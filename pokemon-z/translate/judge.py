# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""걸음 5 좁혀진 검토(4단) 러너 — 발굴 후보를 Opus(claude -p --bare, 구독)로 판정.

대상: mine/candidates-triaged.jsonl의 2표 이상 행 + 1표 표본 50행(실결함률 측정용).
행마다 판정 셋 중 하나 — fix(진짜 결함, 수정안 제시) / ok(결함 아님) / minor(결함이나
현행 유지 무방). fix의 수정안은 apply 전에 validate.py 7종 게이트를 다시 지난다.

llmgateway premium 소진으로 API 대신 구독 CLI를 쓴다(2026-08-02 사용자).
진행 기록 규약은 batch.py와 같다 — judge/out/<cid>.jsonl이 있으면 건너뛴다.

usage:
  uv run judge.py plan                # 판정 청크 생성 (judge/in/)
  uv run judge.py run [--workers 3] [--limit N]
  uv run judge.py status
  uv run judge.py apply               # fix 판정을 게이트 통과 후 정본 반영
"""
import json
import random
import re
import subprocess
import sys
import threading
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
JUDGE = HERE / "judge"
IN = JUDGE / "in"
OUT = JUDGE / "out"
ROWS_PER_CHUNK = 40
SAMPLE_1VOTE = 50

sys.path.insert(0, str(HERE))
from batch import read_jsonl  # noqa: E402
from validate import check  # noqa: E402

PROMPT = """포켓몬 팬게임(스페인어 원작) 한국어 번역의 최종 판정관이다. 각 행에
원문(es)·현행 번역(ko)·하급 발굴 모델의 지적(hits)이 있다. 지적을 그대로 믿지 마라 —
발굴 모델은 한국어 감각이 약해서 멀쩡한 관용 표현을 오타로 몰기도 한다(실례:
「노나 더 세게 저으세요」의 '노나'를 '노를'의 오타라고 판정). 원문과 직접 대조해
스스로 판정해라.

판정은 셋 중 하나다:
- "fix": 뜻이 틀렸거나 비문이다. 고친 전문을 "ko"에 담아라. 마크업(\\c[n]·\\PN·<b> 등)과
  자리표({1} 등)는 현행 그대로 보존하고, 화자 말투(반말/해요체/합쇼체)도 현행을 따른다.
- "minor": 결함이긴 한데 뜻 전달에 지장이 없다(뉘앙스 수위, 사소한 수식). 고치지 않는다.
- "ok": 결함이 아니다. 지적이 틀렸다.

무게는 뜻 정확도 > 자연스러움 > 말맛. 원문에 없는 수식이 뜻을 바꾸면 fix, 강도만
보태면 minor다. 프랑스어 구절(monsieur 등)은 캐릭터 장치라 결함이 아니다.

출력은 JSON 배열만. 각 행마다: {"id": "<id>", "verdict": "fix|minor|ok", "ko": "<fix일 때만 수정 전문>", "note": "<한 줄 근거>"}
코드펜스·설명 금지."""


def plan():
    rows = read_jsonl(HERE / "mine" / "candidates-triaged.jsonl")
    multi = [r for r in rows if r["votes"] >= 2]
    single = [r for r in rows if r["votes"] == 1]
    random.seed(42)
    sample = random.sample(single, min(SAMPLE_1VOTE, len(single)))
    IN.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    chunks = 0
    for tag, pool in (("j", multi), ("s1", sample)):
        for i in range(0, len(pool), ROWS_PER_CHUNK):
            cid = f"{tag}{i // ROWS_PER_CHUNK:03d}"
            with open(IN / f"{cid}.jsonl", "w", encoding="utf-8") as f:
                for r in pool[i:i + ROWS_PER_CHUNK]:
                    f.write(json.dumps(
                        {"id": r["id"], "es": r["es"], "ko": r["ko"],
                         "hits": [h["why"] for h in r["hits"]]},
                        ensure_ascii=False) + "\n")
            chunks += 1
    print(f"판정 대상 {len(multi):,}행(2표+) + 표본 {len(sample)}행(1표)"
          f" → {chunks}청크 ({IN})")


def ask(rows):
    # --bare는 로그인 컨텍스트를 안 태워 "Not logged in"이 난다(2026-08-02 실측) — 뺀다.
    user = json.dumps(rows, ensure_ascii=False)
    p = subprocess.run(
        ["claude", "-p", "--model", "opus", "--append-system-prompt", PROMPT],
        input=user, capture_output=True, text=True, timeout=900)
    if p.returncode != 0:
        raise RuntimeError(f"claude -p 실패: {p.stderr[:200]}")
    text = p.stdout
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise ValueError(f"JSON 배열 없음: {text[:200]}")
    arr = json.loads(m.group(0))
    return {str(a["id"]): a for a in arr if isinstance(a, dict) and "id" in a}


def run(workers=3, limit=None):
    pending = sorted(p for p in IN.glob("*.jsonl")
                     if not (OUT / p.name).exists())
    if limit:
        pending = pending[:limit]
    print(f"대기 {len(pending)}청크")
    if not pending:
        return
    lock = threading.Lock()
    state = {"n": 0, "t0": time.time(), "v": Counter()}

    def work(path):
        rows = read_jsonl(path)
        try:
            got = ask(rows)
        except Exception as e:
            with lock:
                print(f"!! {path.name}: {e}")
            return
        out = []
        for r in rows:
            v = got.get(str(r["id"]))
            if v is None:
                out.append({"id": r["id"], "verdict": "missing"})
            else:
                out.append({"id": r["id"], "verdict": v.get("verdict", "?"),
                            "ko": v.get("ko"), "note": str(v.get("note", ""))[:200]})
        tmp = OUT / (path.stem + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            for row in out:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        tmp.rename(OUT / path.name)
        with lock:
            state["n"] += 1
            for row in out:
                state["v"][row["verdict"]] += 1
            el = time.time() - state["t0"]
            eta = el / state["n"] * (len(pending) - state["n"])
            print(f"[{state['n']}/{len(pending)} | ETA {int(eta // 60)}m"
                  f" | {dict(state['v'])}] {path.name}", flush=True)

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, pending))
    print(f"끝. 판정 분포 {dict(state['v'])}")


def status():
    done = sorted(OUT.glob("*.jsonl"))
    v = Counter()
    for p in done:
        for r in read_jsonl(p):
            v[r["verdict"]] += 1
    total = len(list(IN.glob("*.jsonl")))
    print(f"청크 {len(done)}/{total} · 판정 {dict(v.most_common())}")
    s1 = Counter()
    for p in OUT.glob("s1*.jsonl"):
        for r in read_jsonl(p):
            s1[r["verdict"]] += 1
    if s1:
        n = sum(s1.values())
        print(f"1표 표본({n}행): {dict(s1.most_common())}"
              f" → 실결함률(fix) {s1.get('fix', 0) / n:.0%}")


def put_lines(edits):
    """0단계 정본에 앉히고 ko를 역생성한다 — 창구는 stage0/edit.py 하나다."""
    sys.path.insert(0, str(HERE / "stage0"))
    from edit import put_lines as _put
    return _put(edits)


def apply():
    src = {}
    for p in IN.glob("*.jsonl"):
        for r in read_jsonl(p):
            src[str(r["id"])] = r
    fixes = {}
    gate_rej = 0
    for p in OUT.glob("*.jsonl"):
        for r in read_jsonl(p):
            if r["verdict"] != "fix" or not r.get("ko"):
                continue
            cur = src[str(r["id"])]["ko"]
            sec = 0 if ":" in r["id"] and not r["id"].startswith("s") else int(r["id"][1:].split(":")[0])
            bad = check(cur, r["ko"], sec)
            if bad:
                gate_rej += 1
                continue
            if r["ko"] != cur:
                fixes[str(r["id"])] = r["ko"]
    changed = 0
    edits = []
    path = HERE / "ko" / "00-maps.jsonl"
    cur_map = idx = None
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        d = json.loads(line)
        if "map" in d:
            cur_map, idx = d["map"], 0
            continue
        ko = fixes.get(f"{cur_map}:{idx}")
        if ko is not None and d["v"] != ko:
            edits.append((path.name, ln, ko))
            changed += 1
        idx += 1
    for sec, fname in ((22, "22-phone.jsonl"), (23, "23-script-texts.jsonl")):
        for j, d in enumerate(read_jsonl(HERE / "ko" / fname)):
            ko = fixes.get(f"s{sec}:{j}")
            if ko is not None and d["v"] != ko:
                edits.append((fname, j + 1, ko))
                changed += 1
    err = put_lines(edits)
    if err:
        print("멈춤 —", err)
        return
    print(f"정본 반영 {changed:,}행 (게이트 반려 {gate_rej}). 다음: uv run build.py")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    a = sys.argv[2:]
    if cmd == "plan":
        plan()
    elif cmd == "run":
        run(workers=int(a[a.index("--workers") + 1]) if "--workers" in a else 3,
            limit=int(a[a.index("--limit") + 1]) if "--limit" in a else None)
    elif cmd == "status":
        status()
    elif cmd == "apply":
        apply()
    else:
        print(__doc__)
