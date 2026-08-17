import gzip, json, re, sys, difflib
from collections import defaultdict
from pathlib import Path

REPO = Path("/home/durumii/workspace/claude-native/pokemon-fangame-kr/pokemon-z/translate")
SRC_RANK = {"za": 0, "sv": 1, "la": 2, "swsh": 3, "lgpe": 4, "usum": 5, "sm": 6, "oras": 7, "xy": 8}

def norm(s):
    s = s.replace("\\n", " ").replace("\\r", " ")
    return re.sub(r"\s+", " ", s).strip()

def norm2(s):
    # punctuation/case-insensitive normalization for fuzzy blocking
    s = norm(s).lower()
    s = re.sub(r"[¡!¿?.,;:\"'\u201c\u201d\u2018\u2019()\\-]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

VAR_RE = re.compile(r"\[VAR [^\]]*\]")
def varnorm_corpus(s): return VAR_RE.sub("@", s)
def varnorm_game(s):
    s = re.sub(r"\{[0-9]+\}", "@", s)
    s = re.sub(r"\\v\[[0-9A-Za-z]*\]", "@", s)
    s = re.sub(r"\\(PN|TE|TM|TN|TP|[a-zA-Z])", "@", s)
    return s

by_raw = defaultdict(list)
by_var = defaultdict(list)
by_norm2 = defaultdict(list)  # blocking key: first 3 words of norm2 text -> rows (for fuzzy)
corpus_rows=[]
for line in gzip.open(REPO/"canon/messages.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(line)
    corpus_rows.append(r)
    for key in ("es","en"):
        v = r.get(key)
        if not v: continue
        by_raw[norm(v)].append(r)
        by_var[norm(varnorm_corpus(v))].append(r)
        n2 = norm2(v)
        if n2:
            blockkey = " ".join(n2.split()[:2])
            by_norm2[blockkey].append((n2, r))

# ponytail: drop oversized blocks (generic first-2-words, e.g. empty/"el "/"¡"-only) —
# fuzzy matching against them is unreliable anyway and they dominate runtime.
by_norm2 = {k: v for k, v in by_norm2.items() if len(v) <= 200}


sections = sorted((REPO/"ko").glob("*.jsonl"))
fuzzy_rows = []
counts = {}
for p in sections:
    sec = p.stem
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]
    c_total_unmatched = 0
    c_fuzzy_hit = 0
    for idx, r in enumerate(rows):
        src = r.get("es") or r.get("k")
        if not src: continue
        # already matched by raw or var? skip those
        if by_raw.get(norm(src)):
            continue
        if by_var.get(norm(varnorm_game(src))):
            continue
        c_total_unmatched += 1
        n2 = norm2(src)
        if not n2 or len(n2) < 6:
            continue
        blockkey = " ".join(n2.split()[:2])
        cands = by_norm2.get(blockkey)
        if not cands:
            continue
        best = None
        bestratio = 0.0
        sm = difflib.SequenceMatcher(None)
        sm.set_seq2(n2)
        for n2c, cr in cands:
            if abs(len(n2c) - len(n2)) > len(n2) * 0.3:
                continue
            sm.set_seq1(n2c)
            if sm.real_quick_ratio() < 0.85 or sm.quick_ratio() < 0.85:
                continue
            ratio = sm.ratio()
            if ratio > bestratio:
                bestratio = ratio
                best = cr
        if best and bestratio >= 0.85 and norm2(src) != norm2(best.get("es") or best.get("en") or ""):
            c_fuzzy_hit += 1
            v = r.get("v","")
            ko = best["ko"]
            if norm(v) != norm(ko):
                fuzzy_rows.append((sec, idx, src, v, ko, bestratio, best["src"]+":"+best["file"]))
        elif best and bestratio >= 0.85:
            c_fuzzy_hit += 1
    counts[sec] = dict(unmatched=c_total_unmatched, fuzzy_hit=c_fuzzy_hit)

for sec, c in counts.items():
    if c["unmatched"] or c["fuzzy_hit"]:
        print(sec, c)
print("== totals ==")
print("unmatched (no raw, no var match):", sum(c["unmatched"] for c in counts.values()))
print("fuzzy hit (ratio>=0.85):", sum(c["fuzzy_hit"] for c in counts.values()))
print("fuzzy hit with differing ko:", len(fuzzy_rows))

with open("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/1ccee530-bae2-4a7c-ae3e-e56f04e9fdb0/scratchpad/partC.jsonl","w") as f:
    for row in fuzzy_rows:
        f.write(json.dumps(row, ensure_ascii=False)+"\n")
