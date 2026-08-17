import gzip, json, re, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/durumii/workspace/claude-native/pokemon-fangame-kr/pokemon-z/translate")
KO = ROOT / "ko"
SRC_RANK = {"za": 0, "sv": 1, "la": 2, "swsh": 3, "lgpe": 4, "usum": 5, "sm": 6, "oras": 7, "xy": 8}

def norm(s):
    s = s.replace("\\n", " ").replace("\\r", " ")
    return re.sub(r"\s+", " ", s).strip()

# --- load canon corpus ---
by = defaultdict(list)
with gzip.open(ROOT / "canon/messages.jsonl.gz", "rt", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        by[norm(r["es"])].append(r)
        if r.get("en"):
            by[norm(r["en"])].append(r)

def canon_lookup(r):
    src = r.get("es") or r.get("k")
    if not src:
        return None
    cands = by.get(norm(src))
    if not cands:
        return None
    best = min(cands, key=lambda c: SRC_RANK.get(c["src"], 99))
    return best["src"]

# --- load all ko lines ---
rows = []  # (section, i, v, matched_src)
for p in sorted(KO.glob("*.jsonl")):
    sec = p.stem
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        v = r.get("v")
        if not v:
            continue
        msrc = canon_lookup(r)
        rows.append((sec, i, v, msrc))

print(f"총 ko 줄 수: {len(rows)}", file=sys.stderr)

# --- category 1: compound/aux-verb spacing (word-level dict by space-removed key) ---
single_tokens = defaultdict(list)   # token -> [(sec,i,src)]
bigram_joined = defaultdict(list)   # joined_string -> [(sec,i,spaced_form,src)]

for sec, i, v, msrc in rows:
    toks = v.split()
    for t in toks:
        if len(t) >= 3:
            single_tokens[t].append((sec, i, msrc))
    for a, b in zip(toks, toks[1:]):
        joined = a + b
        if len(joined) >= 3:
            bigram_joined[joined].append((sec, i, f"{a} {b}", msrc))

splits_compound = []
for joined, occs_b in bigram_joined.items():
    if joined not in single_tokens:
        continue
    occs_a = single_tokens[joined]
    a_gens = {m for _, _, m in occs_a if m}
    b_gens = {m for _, _, _, m in occs_b if m}
    both_grounded = bool(a_gens) and bool(b_gens)
    splits_compound.append({
        "표기A": joined,
        "표기B": occs_b[0][2],
        "A출현": [{"절": s, "i": idx, "코퍼스세대": m} for s, idx, m in occs_a],
        "B출현": [{"절": s, "i": idx, "코퍼스세대": m} for s, idx, spaced, m in occs_b],
        "양쪽다_코퍼스근거있음": both_grounded,
    })

# --- category 2: number range connector N~M vs N-M ---
range_re = re.compile(r"(\d+)\s*([~-])\s*(\d+)")
range_occs = defaultdict(list)  # (num1,num2) -> [(sec,i,connector,src)]
for sec, i, v, msrc in rows:
    for m in range_re.finditer(v):
        n1, conn, n2 = m.group(1), m.group(2), m.group(3)
        range_occs[(n1, n2)].append((sec, i, conn, msrc))

splits_range = []
for (n1, n2), occs in range_occs.items():
    conns = {c for _, _, c, _ in occs}
    if len(conns) < 2:
        continue
    a_occs = [(s, idx, m) for s, idx, c, m in occs if c == "~"]
    b_occs = [(s, idx, m) for s, idx, c, m in occs if c == "-"]
    a_gens = {m for _, _, m in a_occs if m}
    b_gens = {m for _, _, m in b_occs if m}
    splits_range.append({
        "표기A": f"{n1}~{n2}",
        "표기B": f"{n1}-{n2}",
        "A출현": [{"절": s, "i": idx, "코퍼스세대": m} for s, idx, m in a_occs],
        "B출현": [{"절": s, "i": idx, "코퍼스세대": m} for s, idx, m in b_occs],
        "양쪽다_코퍼스근거있음": bool(a_gens) and bool(b_gens),
    })

all_splits = splits_compound + splits_range

out_path = Path("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/1ccee530-bae2-4a7c-ae3e-e56f04e9fdb0/scratchpad/z70-notation-splits.jsonl")
with open(out_path, "w", encoding="utf-8") as f:
    for item in all_splits:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

# --- summary ---
n_total = len(all_splits)
n_both = sum(1 for x in all_splits if x["양쪽다_코퍼스근거있음"])
n_onlyone = n_total - n_both

def total_occ(x):
    return len(x["A출현"]) + len(x["B출현"])

top15 = sorted(all_splits, key=total_occ, reverse=True)[:15]

print(f"갈림 항목 총수: {n_total}")
print(f"  compound(공백/보조동사): {len(splits_compound)}")
print(f"  range(수 구간 부호): {len(splits_range)}")
print(f"양쪽 다 코퍼스 근거 있음(본가 세대차): {n_both}")
print(f"한쪽만 근거 있음/근거 없음(고칠 후보): {n_onlyone}")
print()
print("=== 출현 수 상위 15 ===")
for x in top15:
    print(f"{x['표기A']!r} vs {x['표기B']!r}  A={len(x['A출현'])} B={len(x['B출현'])} 양쪽근거={x['양쪽다_코퍼스근거있음']}")
