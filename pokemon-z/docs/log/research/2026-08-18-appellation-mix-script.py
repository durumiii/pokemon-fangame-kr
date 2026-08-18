import gzip, json, re, sys
from collections import defaultdict
sys.path.insert(0, "translate")
from reg import clean
from register import is_dual

ko = {}
for line in open("translate/ko/00-maps.jsonl", encoding="utf-8"):
    r = json.loads(line)
    if "map" not in r:
        ko.setdefault(re.sub(r"\s+", " ", r["k"]).strip(), r["v"])

LOW = re.compile(r"(?<![가-힣])(너|넌|널|너희|네가|네게|네겐|니가)(?![가-힣])")
HIGH = {"그대": re.compile(r"(?<![가-힣])그대"), "자네": re.compile(r"(?<![가-힣])자네"),
        "당신": re.compile(r"(?<![가-힣])당신"), "귀하": re.compile(r"(?<![가-힣])귀하(?!다)")}

pages = defaultdict(list)
for l in gzip.open("translate/data/speaker-attr.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(l)
    if r["kind"] not in ("text", "battle") or not r["who"]:
        continue
    v = ko.get(re.sub(r"\s+", " ", r["k"]).strip())
    if not v:
        continue
    t = clean(v)
    cls = set(c for c in ["너"] if LOW.search(t)) | set(n for n, rx in HIGH.items() if rx.search(t))
    pages[(r["map"], r["event"], r["page"], r["who"])].append((r["cmd"], cls, v))

rows = []
for (m, e, p, who), lst in sorted(pages.items()):
    used = defaultdict(int)
    for _, cls, _ in lst:
        for c in cls: used[c] += 1
    if "너" in used and any(k != "너" for k in used):
        rows.append((m, e, p, who, dict(used), lst))

print(f"| 자리 | 화자 | 분포 | 「너」 계열 줄 |")
print(f"|---|---|---|---|")
for m, e, p, who, used, lst in rows:
    lows = "<br>".join(f"c{c}: {v.replace('|','｜').replace(chr(10),' ')[:110]}" for c, cls, v in lst if "너" in cls)
    dual = " (이중)" if is_dual(who) else ""
    dist = " · ".join(f"{k} {v}" for k, v in sorted(used.items()))
    print(f"| m{m}.e{e}.p{p} | {who}{dual} | {dist} | {lows} |")
