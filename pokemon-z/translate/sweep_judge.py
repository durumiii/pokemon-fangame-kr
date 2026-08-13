# /// script
# requires-python = ">=3.12"
# ///
"""NPC 재번역 사후 정밀 스윕 — 실변경 행 전수 판정.

두 결함만 찾는다: ① 정보 소실/발명(es 대비), ② 화자 오귀속 의심(페르소나
지침과 문장 속 화자 정체의 모순 — 다화자 이벤트에서 상대 대사가 섞인 경우).

    uv run translate/sweep_judge.py        # → batch/npc-sweep-flags.jsonl
"""

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from batch import URL, key_of, or_extras  # noqa: E402

OUT = HERE / "batch" / "npc-out"
CHUNKS = HERE / "batch" / "npc-chunks.jsonl"
FLAGS = HERE / "batch" / "npc-sweep-flags.jsonl"
MODEL = "gemini-3.6-flash"

PROMPT = """스페인어 포켓몬 팬게임의 한국어 재번역 품질 판정이다. 입력은 JSON 배열,
각 항목은 {"id","npc","es","old","new"} — es가 뜻의 정본, old는 이전 번역,
new는 화자 지침(npc)을 반영한 재번역이다.

다음 두 결함만 찾아라. 그 외(어투 취향, 표현 차이)는 보고하지 마라.

1. "loss": new가 es에 있는 사실·수치·대상·조건을 빠뜨렸거나, es에 없는
   정보를 지어냈다. (예: 「게임에서 승리했다」의 「게임에서」 탈락)
2. "speaker": 문장 내용상 이 대사의 화자가 npc가 지시한 인물일 수 없다.
   (예: 도둑 페르소나가 붙었는데 내용은 도둑을 체포해 포상을 주는 쪽의 대사)
   어투가 npc와 다른 것만으로는 보고하지 말고, 정체가 모순일 때만.

출력은 결함이 있는 항목만 담은 JSON 배열:
[{"id":"...","issue":"loss|speaker","note":"한 줄 근거"}]
결함이 없으면 []. 설명·코드펜스 금지."""


def ask(key, rows, attempt=0):
    payload = {"model": MODEL, "temperature": 0.0, "reasoning_effort": "minimal",
               "messages": [{"role": "system", "content": PROMPT},
                            {"role": "user", "content": json.dumps(rows, ensure_ascii=False)}],
               **or_extras()}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            body = json.load(r)
        text = body["choices"][0]["message"]["content"]
        cost = float(body.get("usage", {}).get("cost") or 0)
        m = re.search(r"\[.*\]", text, re.S)
        return (json.loads(m.group(0)) if m else []), cost
    except Exception:
        if attempt < 2:
            time.sleep(8 * (attempt + 1))
            return ask(key, rows, attempt + 1)
        return None, 0.0


def main():
    id2npc = {}
    for l in CHUNKS.read_text(encoding="utf-8").splitlines():
        for r in json.loads(l)["rows"]:
            id2npc[r["id"]] = r["npc"]
    rows = []
    for p in sorted(OUT.glob("n*.jsonl")):
        for l in p.read_text(encoding="utf-8").splitlines():
            d = json.loads(l)
            if d["ok"] and d["new"] and d["new"] != d["old"]:
                rows.append({"id": d["id"], "npc": id2npc.get(d["id"], ""),
                             "es": d["es"], "old": d["old"], "new": d["new"]})
    key = key_of()
    flags, cost_sum, fails = [], 0.0, 0
    with open(FLAGS, "w", encoding="utf-8") as f:
        for i in range(0, len(rows), 40):
            got, cost = ask(key, rows[i:i + 40])
            cost_sum += cost
            if got is None:
                fails += 1
                continue
            for g in got:
                if isinstance(g, dict) and g.get("id"):
                    flags.append(g)
                    f.write(json.dumps(g, ensure_ascii=False) + "\n")
            if (i // 40) % 20 == 0:
                print(f"{i + 40}/{len(rows)} 지적 {len(flags)} ${cost_sum:.2f}", flush=True)
    print(f"완료: 대상 {len(rows)}행, 지적 {len(flags)}건, 실패 청크 {fails}, ${cost_sum:.2f}")


if __name__ == "__main__":
    main()
