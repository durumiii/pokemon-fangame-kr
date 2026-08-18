"""「지닌 도구」→「지닌 물건」 전수 치환(유지자 판정 2026-08-19). usage: [--write]"""
import json, sys, glob
sys.path.insert(0, "translate/stage0")
WRITE = "--write" in sys.argv
OLD, NEW = "지닌 도구", "지닌 물건"
# 「도구」는 받침이 없고 「물건」은 있다 — 뒤따르는 조사를 함께 간다
JOSA = {"를": "을", "는": "은", "가": "이", "와": "과", "로": "으로", "라": "이라"}

def swap(v):
    out = ""
    while True:
        i = v.find(OLD)
        if i < 0: return out + v
        j = i + len(OLD)
        nxt = v[j:j+1]
        out += v[:i] + NEW + JOSA.get(nxt, nxt)
        v = v[j + len(nxt):]

assert swap("지닌 도구를 쓴다") == "지닌 물건을 쓴다"
assert swap("지닌 도구의 효과") == "지닌 물건의 효과"
assert swap("포켓몬이 지닌 도구.") == "포켓몬이 지닌 물건."
assert swap("지닌 도구로 지닌 도구가") == "지닌 물건으로 지닌 물건이"
assert swap("도구를 찾을") == "도구를 찾을"

edits = []
for p in sorted(glob.glob("translate/ko/*.jsonl")):
    for i, l in enumerate(open(p, encoding="utf-8")):
        r = json.loads(l)
        v = r.get("v") or ""
        if OLD in v:
            edits.append((p.split("/")[-1], i + 1, swap(v)))

print(f"치환 대상 {len(edits)}곳")
for f, n, v in edits: print(f"  {f}:{n}  {v}")
if WRITE:
    from edit import put_lines
    print("결과:", put_lines(edits) or "OK")
