"""절23 행별 판정 반영 — 아직 정본에 안 앉은 것만. 자리는 내용(원문+직전 현행값)으로 찾는다.

usage: uv run --with pyyaml python z71_apply23.py [--write]
"""
import json, sys
from pathlib import Path

WRITE = "--write" in sys.argv
sys.path.insert(0, "translate/stage0")
S = Path("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/e744c036-4496-412f-a1f6-af69b24a4da5/scratchpad")
EXCLUDE = {"23-script-texts#3454", "23-script-texts#3399"}
SEC = "23-script-texts"

data = {r["id"]: r for r in map(json.loads, open(S/"full-23.jsonl", encoding="utf-8"))}

byid = {}
for l in open("translate/batch/verdicts-z71-canon-review.jsonl", encoding="utf-8"):
    l = l.strip()
    if not l: continue
    try: r = json.loads(l)
    except Exception: continue
    if r.get("id"): byid[r["id"]] = r

lines = open(f"translate/ko/{SEC}.jsonl", encoding="utf-8").read().splitlines()
rows = [(i, json.loads(l)) for i, l in enumerate(lines)]
rows = [(i, r) for i, r in rows if "k" in r or "es" in r]
sp = lambda s: "".join((s or "").split())

edits, fails, already, drift = [], [], [], []
for rid, v in sorted(byid.items()):
    if not rid.startswith(SEC + "#") or rid in EXCLUDE: continue
    if v.get("판정") not in ("B새번역", "직접"): continue
    val = (v.get("텍스트") or "").strip()
    if not val: continue
    exp = data.get(rid)
    if not exp:
        fails.append((rid, "원자료 없음")); continue
    same = [(i, r) for i, r in rows if (r.get("es") or r.get("k")) == exp["es"]]
    hits = [(i, r) for i, r in same if r.get("v") == exp["old"]]
    if not hits:
        hits = [(i, r) for i, r in same if sp(r.get("v")) == sp(exp["old"])]
        if hits: drift.append((rid, exp["old"], hits[0][1].get("v")))
    if not hits:
        # 이미 반영돼 현행값이 판정 문안으로 바뀐 자리
        if any(r.get("v") == val for _, r in same):
            already.append(rid); continue
        fails.append((rid, "내용 미발견")); continue
    for i, r in hits:
        if r.get("v") == val: already.append(rid); continue
        edits.append((SEC + ".jsonl", i + 1, val))

print(f"쓰기 대상 {len(edits)} · 이미 반영 {len(already)} · 보류 {len(fails)} · 공백 드리프트 {len(drift)}")
for d in drift: print("  드리프트:", d[0], "|판정화면:", d[1], "|파일:", d[2])
for f in fails: print("  보류:", f)
if WRITE and edits and not fails:
    from edit import put_lines
    print("결과:", put_lines(edits) or "OK")
elif WRITE:
    print("보류가 있어 쓰지 않았다")
