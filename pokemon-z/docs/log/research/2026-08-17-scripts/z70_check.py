import gzip, json, re
from collections import defaultdict
from pathlib import Path

HERE = Path("translate")

def norm(s):
    s = s.replace("\\n", " ").replace("\\r", " ")
    return re.sub(r"\s+", " ", s).strip()

by = defaultdict(list)
for line in gzip.open(HERE / "canon/messages.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(line)
    by[norm(r["es"])].append(r)
    if r.get("en"):
        by[norm(r["en"])].append(r)

rows = [json.loads(l) for l in Path("docs/log/research/2026-08-17-corpus-divergence.jsonl").read_text(encoding="utf-8").splitlines()]

out = []
multi_items = []
mismatch_items = []

for row in rows:
    src = row["원문"]
    cands = by.get(norm(src), [])
    variants = defaultdict(lambda: {"tags": set(), "count": 0})
    for c in cands:
        ko = norm(c["ko"])
        variants[ko]["tags"].add(c["src"] + ":" + c["file"])
        variants[ko]["count"] += 1
    ko_변형 = [
        {"값": ko, "출처": sorted(v["tags"]), "횟수": v["count"]}
        for ko, v in variants.items()
    ]
    ko_변형.sort(key=lambda x: -x["횟수"])
    유일한가 = len(ko_변형) <= 1
    본가값 = norm(row["본가"])
    최다 = ko_변형[0]["값"] if ko_변형 else None
    목록의_본가값이_최다인가 = (본가값 == 최다) if ko_변형 else None

    out.append({
        "절": row["절"], "i": row["i"], "원문": src,
        "ko_변형": ko_변형,
        "유일한가": 유일한가,
        "목록의_본가값이_최다인가": 목록의_본가값이_최다인가,
    })
    if len(ko_변형) > 1:
        multi_items.append((row["절"], row["i"], src, ko_변형, 목록의_본가값이_최다인가))
        if not 목록의_본가값이_최다인가:
            mismatch_items.append((row["절"], row["i"], src, 본가값, ko_변형))

outpath = "/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/1ccee530-bae2-4a7c-ae3e-e56f04e9fdb0/scratchpad/z70-canon-variants.jsonl"
with open(outpath, "w", encoding="utf-8") as f:
    for item in out:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"총 {len(out)}행, 변형 2개 이상: {len(multi_items)}행, 목록값이 최다 아님: {len(mismatch_items)}행")
print("=== 변형 2개 이상 목록 ===")
for 절, i, src, variants, match in multi_items:
    print(f"{절}#{i} match={match} src={src[:50]!r}")
    for v in variants:
        print(f"    [{v['횟수']}] {v['값'][:70]!r} {v['출처']}")
print("=== 본가칸이 최다 아닌 항목 ===")
for 절, i, src, listed, variants in mismatch_items:
    print(f"{절}#{i} src={src[:60]!r}")
    print(f"    목록의 본가: {listed[:70]!r}")
    for v in variants:
        print(f"    [{v['횟수']}] {v['값'][:70]!r} {v['출처']}")
