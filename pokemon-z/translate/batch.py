# /// script
# requires-python = ">=3.12"
# ///
"""걸음 5 초벌 배치 러너 — gemini-3.6-flash(llmgateway).

설계 원칙 셋(2026-08-02 사용자):
- **재개 가능**: 조각(청크)마다 out/<cid>.jsonl이 원장이다. 있으면 건너뛴다.
  끊기면 그냥 다시 run — 이미 된 조각은 안 태운다.
- **ETA 인터페이스**: run이 조각마다 진행줄(행 속도·ETA·누적 실비용)을 찍고
  log.txt에 남긴다. `status`는 언제든 그 원장으로 현황을 낸다.
- **수정 요청**: 프롬프트·말투표를 고친 뒤 `redo --map N | --cid 조각 | --all`로
  그 조각의 출력을 지우면 다음 run이 다시 태운다. 출력마다 프롬프트 해시를
  남겨 어느 판으로 구웠는지 추적된다.

대상 범위: 절0(맵 대사)·절22(전화)·절23(시스템 문구)의 한글 행.
설명문 절(도감·기술·도구·특성)은 대사용 프롬프트와 안 맞아 이 배치에서 뺐다.

usage:
  uv run batch.py plan               # 청크 원장 생성 (batch/chunks.jsonl)
  uv run batch.py run [--limit N] [--workers 4]
  uv run batch.py status
  uv run batch.py redo --map 27 | --cid m0027-0 | --all-rejected
  uv run batch.py apply              # 검증 통과 행을 정본 ko/에 반영
"""
import hashlib
import json
import re
import sys
import threading
import time
import unicodedata
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
BATCH = HERE / "batch"
OUT = BATCH / "out"
MODEL = "gemini-3.6-flash"
URL = "https://api.llmgateway.io/v1/chat/completions"
CHUNK_ROWS = 40  # 한 요청의 행 수. 60 이하 맵은 통째로 간다(장면 유지)

sys.path.insert(0, str(HERE))
from validate import check  # noqa: E402  (7종 검사 재사용)


def key_of() -> str:
    for line in (Path.home() / ".hermes" / ".env").read_text().splitlines():
        if line.startswith("LLMGATEWAY_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("LLMGATEWAY_API_KEY 없음 (~/.hermes/.env)")


def read_jsonl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l]


HAN = re.compile(r"[가-힣]")
SPK = re.compile(r"^(?:\\c\[\d+\])?<b>([^:<]{1,20}):")
# 재번역이 필요 없는 행 거르기(2026-08-02 사용자):
# 마크업·구두점을 벗긴 알맹이가 이 길이 이하면 선택지·라벨류다 — 다듬을 게 없다.
CORE_STRIP = re.compile(
    r"\\c\[\d+\]|\\j\[[^\]]*\]|</?[a-z][^>]*>|\{\d+[^}]*\}|\\[A-Za-z]+"
    r"|[\s.·…!?~\-—\"“”‘’'()\[\]]")
CORE_MIN = 9


def worth_rewriting(v: str) -> bool:
    return len(CORE_STRIP.sub("", v)) >= CORE_MIN


def frozen_keys() -> set:
    """걸음 3~4에서 손으로 확정한 절23 키 — 다시 태우면 퇴행 위험이라 동결."""
    led = json.loads((HERE / "battle-expr-replacements.json").read_text(encoding="utf-8"))
    entries = led if isinstance(led, list) else next(
        v for v in led.values() if isinstance(v, list))
    keys = {e["es"] for e in entries if isinstance(e, dict) and "es" in e}
    keys |= {json.loads(l)["k"]
             for l in (HERE / "ko" / "23-script-texts.add.jsonl").read_text(encoding="utf-8").splitlines() if l}
    return keys


def deaccent(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


# ---------- plan ----------

def plan():
    aliases = json.loads((HERE / "speaker-aliases.json").read_text(encoding="utf-8"))
    chunks = []

    def push(sec, tag, rows):
        for i in range(0, len(rows), CHUNK_ROWS):
            piece = rows if len(rows) <= 60 and i == 0 else rows[i:i + CHUNK_ROWS]
            chunks.append({"cid": f"{tag}-{i // CHUNK_ROWS}", "sec": sec, "rows": piece})
            if len(rows) <= 60:
                break

    cur_map, buf = None, []
    for d in read_jsonl(HERE / "ko" / "00-maps.jsonl"):
        if "map" in d:
            if buf:
                push(0, f"m{cur_map:04d}", buf)
            cur_map, buf, idx = d["map"], [], 0
            continue
        if HAN.search(d.get("v", "")) and worth_rewriting(d["v"]):
            m = SPK.match(d["v"])
            spk = m.group(1) if m else None
            spk = aliases.get(spk, spk)
            buf.append({"id": f"{cur_map}:{idx}", "speaker": spk, "es": d["k"], "ko": d["v"]})
        idx += 1
    if buf:
        push(0, f"m{cur_map:04d}", buf)

    fro = frozen_keys()
    for sec, fname in ((22, "22-phone.jsonl"), (23, "23-script-texts.jsonl")):
        rows = [
            {"id": f"s{sec}:{j}", "speaker": None, "es": d["k"], "ko": d["v"]}
            for j, d in enumerate(read_jsonl(HERE / "ko" / fname))
            if HAN.search(d.get("v", "")) and worth_rewriting(d["v"]) and d["k"] not in fro
        ]
        for i in range(0, len(rows), CHUNK_ROWS):
            chunks.append({"cid": f"s{sec}-{i // CHUNK_ROWS:03d}", "sec": sec,
                           "rows": rows[i:i + CHUNK_ROWS]})

    BATCH.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    with open(BATCH / "chunks.jsonl", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    nrows = sum(len(c["rows"]) for c in chunks)
    print(f"청크 {len(chunks)}개 · {nrows:,}행 → {BATCH / 'chunks.jsonl'}")


# ---------- prompt ----------

def voice_table():
    table = {}
    for line in (HERE / "voices.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 5 and cells[1] and cells[1] not in ("인물", "갈래", "태그") \
                and not cells[1].startswith("-"):
            table[cells[1]] = cells[-2]
    return table


def build_prompt(speakers):
    body = (HERE / "prompt.md").read_text(encoding="utf-8")
    body = body.split("## 시스템 프롬프트 본문", 1)[1].split("## 파일럿에서", 1)[0]
    gloss = (HERE / "glossary.md").read_text(encoding="utf-8")
    vt = voice_table()
    lines = [f"- {s}: {vt[s]}" for s in sorted(speakers or []) if s and s in vt]
    common = (HERE / "voices.md").read_text(encoding="utf-8").split("## 배치 프롬프트에 얹을 공통 규칙", 1)[1]
    voices = "말투표 (이 장면의 화자):\n" + ("\n".join(lines) if lines else "- (태그 화자 없음 — 기본값 적용)")
    voices += "\n기본값: 서술문은 간결한 평서(~했다), 일반 NPC는 해요체, 시스템 문구는 합쇼체.\n"
    voices += "공통 규칙:" + common
    body = body.replace("[용어 규칙 — glossary.md 본문 삽입]", gloss)
    body = body.replace("[말투표 발췌 — 이 묶음의 화자들만, voices.md에서]", voices)
    return body


# ---------- run ----------

def ask(key, prompt, rows, attempt=0):
    # reasoning_effort=minimal: gemini-3.6-flash는 씽킹이 모델 강제지만 effort는
    # 조절된다. 실전 프롬프트 A/B(2026-08-02, m0000-1 28행)에서 기본(씽킹 4,589tok)과
    # minimal(0tok)이 검증 반려 0:0, 고유명사 이탈 2:2로 동급이었고 비용만 3.2배
    # 차이였다. 번역엔 씽킹이 값을 안 낸다 — 사용자 직관과 일치.
    payload = {"model": MODEL, "temperature": 0.3, "reasoning_effort": "minimal",
               "messages": [
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(
            [{"id": r["id"], "speaker": r["speaker"], "es": r["es"], "ko": r["ko"]} for r in rows],
            ensure_ascii=False)}]}
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
        return {str(a["id"]): a["ko"] for a in arr
                if isinstance(a, dict) and isinstance(a.get("ko"), str)}, cost
    except Exception as e:
        if attempt < 2:
            time.sleep(8 * (attempt + 1))
            return ask(key, prompt, rows, attempt + 1)
        return {"__error__": type(e).__name__}, 0.0


def run(limit=None, workers=4):
    key = key_of()
    chunks = read_jsonl(BATCH / "chunks.jsonl")
    pending = [c for c in chunks if not (OUT / (c["cid"] + ".jsonl")).exists()]
    if limit:
        pending = pending[:limit]
    total_rows = sum(len(c["rows"]) for c in pending)
    print(f"대기 {len(pending)}청크 · {total_rows:,}행 (전체 {len(chunks)}청크)")
    if not pending:
        return
    lock = threading.Lock()
    state = {"done_rows": 0, "done_chunks": 0, "cost": 0.0, "rej": 0, "t0": time.time()}
    log = open(BATCH / "log.txt", "a", encoding="utf-8")

    def work(c):
        speakers = {r["speaker"] for r in c["rows"] if r["speaker"]}
        prompt = build_prompt(speakers)
        phash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        got, cost = ask(key, prompt, c["rows"])
        out_rows, rej = [], 0
        err = got.pop("__error__", None) if isinstance(got, dict) else "shape"
        # 한 번에 안 온 행만 모아 1회 재시도
        missing = [r for r in c["rows"] if r["id"] not in got]
        if missing and not err:
            got2, cost2 = ask(key, prompt, missing)
            got2.pop("__error__", None)
            got.update(got2)
            cost += cost2
        for r in c["rows"]:
            ko = got.get(r["id"])
            if ko is None:
                out_rows.append({"id": r["id"], "ko": r["ko"], "ok": False, "why": err or "누락"})
                rej += 1
                continue
            bad = check(r["ko"], ko, c["sec"])
            if bad:
                out_rows.append({"id": r["id"], "ko": ko, "ok": False, "why": " | ".join(bad)})
                rej += 1
            else:
                out_rows.append({"id": r["id"], "ko": ko, "ok": True,
                                 "same": ko == r["ko"]})
        tmp = OUT / (c["cid"] + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps({"cid": c["cid"], "prompt": phash, "cost": cost},
                               ensure_ascii=False) + "\n")
            for row in out_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        tmp.rename(OUT / (c["cid"] + ".jsonl"))
        with lock:
            state["done_rows"] += len(c["rows"])
            state["done_chunks"] += 1
            state["cost"] += cost
            state["rej"] += rej
            el = time.time() - state["t0"]
            rate = state["done_rows"] / el if el else 0
            eta = (total_rows - state["done_rows"]) / rate if rate else 0
            line = (f"[{state['done_chunks']}/{len(pending)}청크 {state['done_rows']:,}/"
                    f"{total_rows:,}행 | {rate:.1f}행/s | ETA {int(eta // 60)}m{int(eta % 60):02d}s"
                    f" | ${state['cost']:.2f} | 반려누적 {state['rej']}] {c['cid']}")
            print(line, flush=True)
            log.write(line + "\n")
            log.flush()

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, pending))
    print(f"끝. 반려 {state['rej']}행, 실비용 ${state['cost']:.2f}")


# ---------- status / redo / apply ----------

def status():
    chunks = read_jsonl(BATCH / "chunks.jsonl")
    done = ok = rej = same = 0
    cost = 0.0
    for c in chunks:
        p = OUT / (c["cid"] + ".jsonl")
        if not p.exists():
            continue
        rows = read_jsonl(p)
        cost += rows[0].get("cost", 0)
        done += 1
        for r in rows[1:]:
            if r["ok"]:
                ok += 1
                same += bool(r.get("same"))
            else:
                rej += 1
    total_rows = sum(len(c["rows"]) for c in chunks)
    print(f"청크 {done}/{len(chunks)} · 행 {ok + rej:,}/{total_rows:,}"
          f" (통과 {ok:,} · 그중 무변경 {same:,} · 반려 {rej:,}) · 실비용 ${cost:.2f}")
    why = Counter()
    for c in chunks:
        p = OUT / (c["cid"] + ".jsonl")
        if p.exists():
            for r in read_jsonl(p)[1:]:
                if not r["ok"]:
                    why[r["why"].split(":")[0]] += 1
    if why:
        print("반려 사유:", dict(why.most_common(8)))


def redo(args):
    chunks = read_jsonl(BATCH / "chunks.jsonl")
    targets = []
    if "--all-rejected" in args:
        for c in chunks:
            p = OUT / (c["cid"] + ".jsonl")
            if p.exists() and any(not r["ok"] for r in read_jsonl(p)[1:]):
                targets.append(c["cid"])
    elif "--map" in args:
        m = int(args[args.index("--map") + 1])
        targets = [c["cid"] for c in chunks if c["cid"].startswith(f"m{m:04d}")]
    elif "--cid" in args:
        targets = [args[args.index("--cid") + 1]]
    n = 0
    for cid in targets:
        p = OUT / (cid + ".jsonl")
        if p.exists():
            p.unlink()
            n += 1
    print(f"{n}청크 초기화 — 다음 run이 다시 태운다")


def apply():
    accepted = {}
    for p in sorted(OUT.glob("*.jsonl")):
        for r in read_jsonl(p)[1:]:
            if r["ok"] and not r.get("same"):
                accepted[r["id"]] = r["ko"]
    changed = 0
    # 절0
    path = HERE / "ko" / "00-maps.jsonl"
    out_lines = []
    cur_map = idx = None
    for line in path.read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if "map" in d:
            cur_map, idx = d["map"], 0
        else:
            ko = accepted.get(f"{cur_map}:{idx}")
            if ko is not None and d["v"] != ko:
                d["v"] = ko
                changed += 1
            idx += 1
        out_lines.append(json.dumps(d, ensure_ascii=False))
    path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    for sec, fname in ((22, "22-phone.jsonl"), (23, "23-script-texts.jsonl")):
        path = HERE / "ko" / fname
        rows = read_jsonl(path)
        for j, d in enumerate(rows):
            ko = accepted.get(f"s{sec}:{j}")
            if ko is not None and d["v"] != ko:
                d["v"] = ko
                changed += 1
        path.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in rows) + "\n",
                        encoding="utf-8")
    print(f"정본 반영 {changed:,}행. 다음: uv run build.py")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "plan":
        plan()
    elif cmd == "run":
        a = sys.argv[2:]
        run(limit=int(a[a.index("--limit") + 1]) if "--limit" in a else None,
            workers=int(a[a.index("--workers") + 1]) if "--workers" in a else 4)
    elif cmd == "status":
        status()
    elif cmd == "redo":
        redo(sys.argv[2:])
    elif cmd == "apply":
        apply()
    else:
        print(__doc__)
