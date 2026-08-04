# /// script
# requires-python = ">=3.12"
# ///
"""걸음 5 발굴(3단) 러너 — 원문 대조 오역 후보를 3회 통과 합집합으로 캔다.

구성(2026-08-02 사용자 승인): gpt-5.6-luna ×2 + glm-5.2 ×1, 점검표 프롬프트,
행 단위 합집합. 재현율 측정(pilot/recall_probe.py)에서 luna 2회 합집합이
결격 실례 8/10을 잡았고 늘 놓친 둘은 판정 문서의 「경미」 부류였다.
비용 상한 $15 — 넘으면 멈추고 보고한다.

batch.py와 같은 진행 기록 규약: 통과×청크마다 mine/out/<pass>/<cid>.jsonl이 기록,
있으면 건너뛴다. 끊기면 그냥 다시 run.

usage:
  uv run mine.py plan               # 현 정본에서 청크 목록 생성 (mine/chunks.jsonl)
  uv run mine.py run [--workers 4]
  uv run mine.py status
  uv run mine.py merge              # 합집합 → mine/candidates.jsonl
"""
import json
import re
import sys
import threading
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
MINE = HERE / "mine"
OUT = MINE / "out"
URL = "https://api.llmgateway.io/v1/chat/completions"
COST_CAP = 15.0
PASSES = [("luna1", "gpt-5.6-luna"), ("luna2", "gpt-5.6-luna"), ("glm1", "glm-5.2")]

sys.path.insert(0, str(HERE))
from batch import (CHUNK_ROWS, HAN, SPK, frozen_keys, key_of,  # noqa: E402
                   read_jsonl, worth_rewriting)

# 재현율 측정으로 보정된 점검표 프롬프트(pilot/recall_probe.py PROMPT_CHECKLIST와
# 동일 본문). 열린 질문 대비 luna 재현이 4/10 → 7/10.
PROMPT = """스페인어 포켓몬 팬게임의 한국어 번역을 검수한다. 각 행의 es(원문)와
ko(번역)를 대조하되, 행마다 아래 다섯 항목을 **하나씩 순서대로** 점검해라.

1. 추가: ko에 있는 형용사·부사·뉘앙스 중 es에 근거가 없는 것이 있는가?
   (예: 원문 una sorpresa(놀랄 일)를 「엄청나게 놀랄 일」로 부풀림)
2. 누락·왜곡: es의 내용어(명사·동사·수량 표현)가 ko에서 빠지거나 다른 뜻으로 바뀌었는가?
   (예: correr(달리다)를 「걷다」로, semanas(몇 주)를 「며칠」로)
3. 수·성: es의 단수/복수, 남성/여성이 ko에서 유지되는가?
   (지시 대상이 한 명인지 여럿인지, 남성 화법인지 여성 화법인지)
4. 문법: ko 자체가 비문이거나 오타·활용 오류가 있는가?
   (예: 목적어에 피동 활용이 붙는 류의 주술 어긋남)
5. 관례: 포켓몬 시리즈 정식 명칭과 어긋나는 역어가 있는가?
   (게임 용어는 한국어 정식 발매판 명칭이 기준이다)

말투·문체 취향은 결함이 아니다. 마크업(\\c[n], \\PN, <b> 등)은 무시해라.

출력은 JSON 배열만: [{"id": <행 id>, "flag": true/false, "why": "<위반 항목 번호와 요지, 없으면 빈 문자열>"}]
모든 행에 대해 하나씩. 코드펜스·설명 금지."""


def plan():
    """batch.plan과 같은 절·거르기·청크 규칙, 단 현 정본(=apply 이후)을 읽는다."""
    chunks = []

    def push(tag, rows):
        for i in range(0, len(rows), CHUNK_ROWS):
            piece = rows if len(rows) <= 60 and i == 0 else rows[i:i + CHUNK_ROWS]
            chunks.append({"cid": f"{tag}-{i // CHUNK_ROWS}", "rows": piece})
            if len(rows) <= 60:
                break

    cur_map, buf = None, []
    for d in read_jsonl(HERE / "ko" / "00-maps.jsonl"):
        if "map" in d:
            if buf:
                push(f"m{cur_map:04d}", buf)
            cur_map, buf, idx = d["map"], [], 0
            continue
        if HAN.search(d.get("v", "")) and worth_rewriting(d["v"]):
            buf.append({"id": f"{cur_map}:{idx}", "es": d["k"], "ko": d["v"]})
        idx += 1
    if buf:
        push(f"m{cur_map:04d}", buf)

    fro = frozen_keys()
    for sec, fname in ((22, "22-phone.jsonl"), (23, "23-script-texts.jsonl")):
        rows = [{"id": f"s{sec}:{j}", "es": d["k"], "ko": d["v"]}
                for j, d in enumerate(read_jsonl(HERE / "ko" / fname))
                if HAN.search(d.get("v", "")) and worth_rewriting(d["v"])
                and d["k"] not in fro]
        for i in range(0, len(rows), CHUNK_ROWS):
            chunks.append({"cid": f"s{sec}-{i // CHUNK_ROWS:03d}",
                           "rows": rows[i:i + CHUNK_ROWS]})

    MINE.mkdir(exist_ok=True)
    for p, _ in PASSES:
        (OUT / p).mkdir(parents=True, exist_ok=True)
    with open(MINE / "chunks.jsonl", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"청크 {len(chunks)}개 · {sum(len(c['rows']) for c in chunks):,}행"
          f" × {len(PASSES)}통과 → {MINE / 'chunks.jsonl'}")


def spent() -> float:
    return sum(read_jsonl(p)[0].get("cost", 0)
               for p in OUT.glob("*/*.jsonl"))


def ask(key, model, rows, attempt=0):
    payload = {"model": model, "temperature": 0.0,
               "messages": [{"role": "system", "content": PROMPT},
                            {"role": "user", "content": json.dumps(rows, ensure_ascii=False)}]}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            body = json.load(r)
        text = body["choices"][0]["message"]["content"]
        cost = float(body.get("usage", {}).get("cost") or 0)
        m = re.search(r"\[.*\]", text, re.S)
        arr = json.loads(m.group(0))
        return {str(a["id"]): a for a in arr if isinstance(a, dict) and "id" in a}, cost
    except Exception as e:
        if attempt < 2:
            time.sleep(8 * (attempt + 1))
            return ask(key, model, rows, attempt + 1)
        return {"__error__": type(e).__name__}, 0.0


def run(workers=4):
    key = key_of()
    chunks = read_jsonl(MINE / "chunks.jsonl")
    jobs = [(pname, model, c) for pname, model in PASSES for c in chunks
            if not (OUT / pname / (c["cid"] + ".jsonl")).exists()]
    total_rows = sum(len(c["rows"]) for _, _, c in jobs)
    base_cost = spent()
    print(f"대기 {len(jobs)}건 · {total_rows:,}행 (기왕 지출 ${base_cost:.2f} / 상한 ${COST_CAP})")
    if not jobs:
        return
    lock = threading.Lock()
    state = {"rows": 0, "n": 0, "cost": base_cost, "flags": 0, "t0": time.time(),
             "stop": False}
    log = open(MINE / "log.txt", "a", encoding="utf-8")

    def work(job):
        pname, model, c = job
        if state["stop"]:
            return
        got, cost = ask(key, model, c["rows"])
        err = got.pop("__error__", None)
        missing = [r for r in c["rows"] if r["id"] not in got]
        if missing and not err:
            got2, cost2 = ask(key, model, missing)
            got2.pop("__error__", None)
            got.update(got2)
            cost += cost2
        out_rows = []
        flags = 0
        for r in c["rows"]:
            v = got.get(r["id"])
            if v is None:
                out_rows.append({"id": r["id"], "flag": None, "why": err or "미판정"})
            else:
                fl = bool(v.get("flag"))
                flags += fl
                out_rows.append({"id": r["id"], "flag": fl,
                                 "why": str(v.get("why", ""))[:300]})
        tmp = OUT / pname / (c["cid"] + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps({"cid": c["cid"], "model": model, "cost": cost},
                               ensure_ascii=False) + "\n")
            for row in out_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        tmp.rename(OUT / pname / (c["cid"] + ".jsonl"))
        with lock:
            state["rows"] += len(c["rows"])
            state["n"] += 1
            state["cost"] += cost
            state["flags"] += flags
            if state["cost"] >= COST_CAP:
                state["stop"] = True
            el = time.time() - state["t0"]
            rate = state["rows"] / el if el else 0
            eta = (total_rows - state["rows"]) / rate if rate else 0
            line = (f"[{state['n']}/{len(jobs)} {state['rows']:,}/{total_rows:,}행"
                    f" | {rate:.1f}행/s | ETA {int(eta // 60)}m{int(eta % 60):02d}s"
                    f" | ${state['cost']:.2f} | 후보 {state['flags']:,}] {pname}/{c['cid']}")
            print(line, flush=True)
            log.write(line + "\n")
            log.flush()

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, jobs))
    if state["stop"]:
        print(f"상한 ${COST_CAP} 도달 — 멈췄다. 남은 건 run으로 이어 태운다(상한 조정 후).")
    print(f"끝. 후보 {state['flags']:,}행 표시, 누적 실비용 ${state['cost']:.2f}")


def status():
    chunks = read_jsonl(MINE / "chunks.jsonl")
    for pname, model in PASSES:
        done = flags = none = 0
        for c in chunks:
            p = OUT / pname / (c["cid"] + ".jsonl")
            if not p.exists():
                continue
            done += 1
            for r in read_jsonl(p)[1:]:
                if r["flag"] is None:
                    none += 1
                elif r["flag"]:
                    flags += 1
        print(f"{pname}({model}): 청크 {done}/{len(chunks)} · 후보 {flags:,} · 미판정 {none:,}")
    print(f"누적 실비용 ${spent():.2f} / 상한 ${COST_CAP}")


def merge():
    chunks = read_jsonl(MINE / "chunks.jsonl")
    src = {r["id"]: r for c in chunks for r in c["rows"]}
    hits = {}
    for pname, _ in PASSES:
        for p in (OUT / pname).glob("*.jsonl"):
            for r in read_jsonl(p)[1:]:
                if r["flag"]:
                    hits.setdefault(r["id"], []).append(
                        {"pass": pname, "why": r["why"]})
    with open(MINE / "candidates.jsonl", "w", encoding="utf-8") as f:
        for rid, hs in sorted(hits.items()):
            row = src.get(rid, {})
            f.write(json.dumps({"id": rid, "es": row.get("es"), "ko": row.get("ko"),
                                "votes": len(hs), "hits": hs}, ensure_ascii=False) + "\n")
    from collections import Counter
    votes = Counter(len(h) for h in hits.values())
    print(f"후보 합집합 {len(hits):,}행 → {MINE / 'candidates.jsonl'}"
          f" (표수 분포 {dict(sorted(votes.items()))})")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    a = sys.argv[2:]
    if cmd == "plan":
        plan()
    elif cmd == "run":
        run(workers=int(a[a.index("--workers") + 1]) if "--workers" in a else 4)
    elif cmd == "status":
        status()
    elif cmd == "merge":
        merge()
    else:
        print(__doc__)
