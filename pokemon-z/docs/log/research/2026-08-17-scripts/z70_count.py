import gzip, json, time
from pathlib import Path

REPO = Path("/home/durumii/workspace/claude-native/pokemon-fangame-kr/pokemon-z")
SRC_RANK = {"za": 0, "sv": 1, "la": 2, "swsh": 3, "lgpe": 4, "usum": 5, "sm": 6, "oras": 7, "xy": 8}

t0 = time.time()
corpus = []  # (ko, src)
with gzip.open(REPO / "translate/canon/messages.jsonl.gz", "rt", encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        ko = d.get("ko") or ""
        if ko:
            corpus.append((ko, d.get("src")))
print("loaded", len(corpus), time.time() - t0)

pairs = [json.loads(l) for l in open(REPO / "docs/log/research/2026-08-17-notation-splits.jsonl")]

def gen_counts_for(needle):
    counts = {}
    for ko, src in corpus:
        if needle in ko:
            counts[src] = counts.get(src, 0) + 1
    return counts

t0 = time.time()
results = []
for p in pairs:
    a, b = p["표기A"], p["표기B"]
    ca = gen_counts_for(a)
    cb = gen_counts_for(b)
    results.append({"표기A": a, "표기B": b, "A_세대별횟수": ca, "B_세대별횟수": cb,
                     "A출현": p["A출현"], "B출현": p["B출현"]})
print("counted", time.time() - t0)

Path("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/1ccee530-bae2-4a7c-ae3e-e56f04e9fdb0/scratchpad/z70_raw_counts.jsonl").write_text(
    "\n".join(json.dumps(r, ensure_ascii=False) for r in results), encoding="utf-8"
)
print("done")
