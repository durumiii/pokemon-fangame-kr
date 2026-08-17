import gzip, json, re, sys
from collections import defaultdict
from pathlib import Path

REPO = Path("/home/durumii/workspace/claude-native/pokemon-fangame-kr/pokemon-z/translate")
SRC_RANK = {"za": 0, "sv": 1, "la": 2, "swsh": 3, "lgpe": 4, "usum": 5, "sm": 6, "oras": 7, "xy": 8}

def norm(s):
    s = s.replace("\\n", " ").replace("\\r", " ")
    return re.sub(r"\s+", " ", s).strip()

VAR_RE = re.compile(r"\[VAR [^\]]*\]")
# game-side interpolation tokens
GAME_TOK_RE = re.compile(r"\{[0-9]+\}|\\v\[[0-9A-Za-z]*\]|\\P[NnMm]?|\\[a-zA-Z]+(?![a-zA-Z])")

def varnorm_corpus(s):
    return VAR_RE.sub("@", s)

def varnorm_game(s):
    # {1} {2} -> @ ; \v[123] -> @ ; \c \n \m \b \l \G \j \e \TE \TM \TN \TP \PN etc -> @
    s = re.sub(r"\{[0-9]+\}", "@", s)
    s = re.sub(r"\\v\[[0-9A-Za-z]*\]", "@", s)
    s = re.sub(r"\\(PN|TE|TM|TN|TP|[a-zA-Z])", "@", s)
    return s

def normkey_var(s, is_corpus):
    s = varnorm_corpus(s) if is_corpus else varnorm_game(s)
    return norm(s)

GAME_TOKEN_TEST = re.compile(r"\{[0-9]+\}|\\v\[[0-9A-Za-z]*\]|\\(PN|TE|TM|TN|TP|[a-zA-Z])")

def has_game_token(s):
    return bool(GAME_TOKEN_TEST.search(s))

# --- load corpus ---
by_raw = defaultdict(list)      # literal norm(es/en) -> rows
by_var = defaultdict(list)      # var-normalized -> rows
corpus_rows = []
for line in gzip.open(REPO/"canon/messages.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(line)
    corpus_rows.append(r)
    for key in ("es","en"):
        v = r.get(key)
        if not v: continue
        by_raw[norm(v)].append(r)
        by_var[normkey_var(v, True)].append(r)

sections = sorted((REPO/"ko").glob("*.jsonl"))

results = {}
partA1_rows = []  # skipped due to [VAR in ko, exact src match
partA2_rows = []  # rows with game-side interpolation tokens in src or v
partB_rows = []   # newly matched via var-normalization, ko differs
for p in sections:
    sec = p.stem
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]
    a1 = a2 = b_new = 0
    for idx, r in enumerate(rows):
        src = r.get("es") or r.get("k")
        if not src:
            continue
        v = r.get("v","")
        tok_in_src = has_game_token(src)
        tok_in_v = has_game_token(v)
        if tok_in_src or tok_in_v:
            a2 += 1
            partA2_rows.append((sec, idx, src, v))

        # part A1: canon_sweep's own skip condition
        cands = by_raw.get(norm(src))
        if cands:
            best = min(cands, key=lambda c: SRC_RANK.get(c["src"], 99))
            ko = norm(best["ko"])
            if "[VAR" in ko and norm(v) != ko:
                a1 += 1
                partA1_rows.append((sec, idx, src, v, ko))

        # part B: var-normalized matching (skip if already exact raw match with ko usable, to find "new" matches)
        vkey = normkey_var(src, False)
        vcands = by_var.get(vkey)
        if vcands:
            bestv = min(vcands, key=lambda c: SRC_RANK.get(c["src"], 99))
            kov = normkey_var(bestv["ko"], True)
            # is this "new" vs raw match? new if raw match didn't exist or raw ko had [VAR unusable
            raw_ok = False
            if cands:
                bestr = min(cands, key=lambda c: SRC_RANK.get(c["src"], 99))
                if "[VAR" not in norm(bestr["ko"]):
                    raw_ok = True
            if not raw_ok:
                b_new += 1
                if norm(v) != kov:
                    partB_rows.append((sec, idx, src, v, bestv["ko"], bestv["src"]+":"+bestv["file"]))
    results[sec] = dict(total=len(rows), a1_var_skip=a1, a2_has_token=a2, b_new_match=b_new)

for sec, r in results.items():
    print(sec, r)

print("== totals ==")
print("A1 (var-skip in canon_sweep):", sum(r["a1_var_skip"] for r in results.values()))
print("A2 (rows with interpolation tokens):", sum(r["a2_has_token"] for r in results.values()))
print("B new matches via var-normalization:", sum(r["b_new_match"] for r in results.values()))

with open("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/1ccee530-bae2-4a7c-ae3e-e56f04e9fdb0/scratchpad/partA1.jsonl","w") as f:
    for row in partA1_rows:
        f.write(json.dumps(row, ensure_ascii=False)+"\n")
with open("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/1ccee530-bae2-4a7c-ae3e-e56f04e9fdb0/scratchpad/partB.jsonl","w") as f:
    for row in partB_rows:
        f.write(json.dumps(row, ensure_ascii=False)+"\n")
