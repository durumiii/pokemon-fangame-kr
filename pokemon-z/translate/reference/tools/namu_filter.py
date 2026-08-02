# /// script
# dependencies = ["pyarrow"]
# ///
"""Stream the namuwiki parquet, keep only articles whose title matches a species name."""
import json, sys, pyarrow.parquet as pq

SPECIES = "/home/durumii/workspace/claude-native/sketches/poke-essentials/mod/z/translate/ko/01-species.jsonl"
PARQUET = sys.argv[1]
OUT = sys.argv[2]

byname = {}
for line in open(SPECIES):
    r = json.loads(line)
    if r["i"] > 0:
        byname.setdefault(r["v"], r["i"])

pf = pq.ParquetFile(PARQUET)
print("row groups:", pf.num_row_groups, "rows:", pf.metadata.num_rows, flush=True)
hits = 0
with open(OUT, "w") as out:
    for batch in pf.iter_batches(batch_size=20000, columns=["title", "text"]):
        titles = batch.column("title").to_pylist()
        for i, t in enumerate(titles):
            # namuwiki titles may carry a disambiguator: "리자드(포켓몬스터)"
            base = t.split("(")[0].strip()
            if t in byname or base in byname:
                out.write(json.dumps({"title": t, "dex": byname.get(t) or byname[base],
                                      "text": batch.column("text")[i].as_py()}, ensure_ascii=False) + "\n")
                hits += 1
print("hits:", hits)
