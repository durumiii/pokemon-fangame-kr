# /// script
# requires-python = ">=3.12"
# ///
"""배틀 트레이너 대사만 다시 번역한다 — 도전과 패배를 한 벌로 묶어서.

트레이너 이벤트(`Trainer(n)`)의 대사는 이름표 없이 스프라이트로만 화자가 붙어,
주연 재번역 사정권 밖에 있었다(실측 2026-08-06: 544행 중 0행). 그래서 같은 인물의
도전 대사와 패배 대사가 서로 다른 격으로 서 있는 자리가 남았다.

    uv run translate/batch_trainers.py plan
    Z_BACKEND=openrouter uv run translate/batch_trainers.py run [--effort low]

한 이벤트의 모든 줄을 한 요청에 담는다 — 도전과 패배의 격이 서로 맞물려야 한다.
산출은 `batch/trainer-out/<cid>.jsonl`로, 주연 배치와 같은 꼴이라 선별 2층과
검수 스튜디오가 그대로 읽는다.
"""

import concurrent.futures as cf
import gzip
import json
import re
import sys
import threading
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from batch import MODEL  # noqa: E402  (Z_BACKEND 전환을 함께 탄다)
from batch_pages import fold, ko_index  # noqa: E402
from pilot_npc import ask_npc, build_prompt, key_of, load_personas  # noqa: E402
from validate import check  # noqa: E402

ATTR = HERE / "data/speaker-attr.jsonl.gz"
BATCH = HERE / "batch"
CHUNKS = BATCH / "trainer-chunks.jsonl"
OUT = BATCH / "trainer-out"
TRAINER = re.compile(r"^Trainer\(")


def persona_of(sprite, personas):
    p = personas.get(sprite)
    if not p:
        return f"[스프라이트 {sprite}] 말투 지침 없음 — 현행 격을 지킨다"
    return f"{p['페르소나']} [어미: {p['버킷']}]"


def plan():
    personas, ko = load_personas(), ko_index()
    ev = defaultdict(list)
    for line in gzip.open(ATTR, "rt", encoding="utf-8"):
        r = json.loads(line)
        if r.get("kind") != "text" or not TRAINER.match(r.get("event_name") or ""):
            continue
        cur = ko.get((r["map"], fold(r["k"])))
        if cur is None:                      # 정본에 없는 자리
            continue
        ev[(r["map"], r["event"])].append((r, cur))

    BATCH.mkdir(exist_ok=True)
    n = 0
    with CHUNKS.open("w", encoding="utf-8") as f:
        for (m, e), items in sorted(ev.items()):
            items.sort(key=lambda x: (x[0]["page"], x[0]["cmd"]))
            rows = [{"id": f"{m}:{e}:{r['page']}:{r['cmd']}",
                     "npc": persona_of(r.get("sprite", ""), personas),
                     "es": r["k"], "ko": cur}
                    for r, cur in items]
            f.write(json.dumps({"cid": f"t{m:03d}-{e}", "map": m, "event": e,
                                "rows": rows}, ensure_ascii=False) + "\n")
            n += len(rows)
    print(f"트레이너 이벤트 {len(ev)}개 · {n}행 → {CHUNKS}")


def run(workers=4, effort="low"):
    key, prompt = key_of(), build_prompt()
    chunks = [json.loads(l) for l in CHUNKS.read_text(encoding="utf-8").splitlines() if l]
    OUT.mkdir(exist_ok=True)
    pending = [c for c in chunks if not (OUT / (c["cid"] + ".jsonl")).exists()]
    print(f"대기 {len(pending)}/{len(chunks)}이벤트 · {sum(len(c['rows']) for c in pending)}행")
    lock, st = threading.Lock(), {"rows": 0, "n": 0, "cost": 0.0, "rej": 0}

    def work(c):
        got, cost = ask_npc(key, MODEL, prompt, c["rows"], effort=effort)
        out = []
        for r in c["rows"]:
            new = got.get(r["id"])
            why = "누락" if new is None else None
            if new is not None:
                bad = check(r["ko"], new, 0)
                if bad:
                    why = "검증:" + bad[0][:40]
            out.append({"id": r["id"], "who": r["npc"].split("[")[0].strip(),
                        "es": r["es"], "old": r["ko"],
                        "new": new if why is None else None,
                        "ok": why is None, "why": why})
        (OUT / (c["cid"] + ".jsonl")).write_text(
            "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), encoding="utf-8")
        with lock:
            st["rows"] += len(out)
            st["n"] += 1
            st["cost"] += cost
            st["rej"] += sum(1 for x in out if not x["ok"])
            print(f"[{st['n']}/{len(pending)}] {c['cid']} · 누적 {st['rows']}행 "
                  f"반려 {st['rej']} ${st['cost']:.3f}", flush=True)

    with cf.ThreadPoolExecutor(workers) as ex:
        list(ex.map(work, pending))
    print(f"끝. {st['rows']}행 · 반려 {st['rej']} · 실비용 ${st['cost']:.3f}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "plan":
        plan()
    elif a[0] == "run":
        eff = a[a.index("--effort") + 1] if "--effort" in a else "low"
        run(effort=eff)
    else:
        print(__doc__)
