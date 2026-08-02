# /// script
# dependencies = []
# ///
"""Parse namuwiki 도감 설명 tables into (dex, version, ko) rows."""
import json, re, sys, collections

SPECIES = "/home/durumii/workspace/claude-native/sketches/poke-essentials/mod/z/translate/ko/01-species.jsonl"
BYNAME, NAMEOF = {}, {}
for line in open(SPECIES):
    r = json.loads(line)
    if r["i"] > 0:
        BYNAME.setdefault(r["v"], r["i"])
        NAMEOF[r["i"]] = r["v"]

CELLOPT = re.compile(r"^(<[^>]*>)+")
ROWSPAN = re.compile(r"<\|(\d+)>")


def clean(s: str) -> str:
    s = re.sub(r"\[\[파일:[^\]]*\]\]", "", s)               # images
    s = re.sub(r"\[\*[^\]]*\]", "", s)                      # footnotes (non-nested)
    s = re.sub(r"\[\[([^\]|]*)\|([^\]]*)\]\]", r"\2", s)     # piped links
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)                # plain links
    s = re.sub(r"\[include\([^)]*\)\]", "", s)
    s = re.sub(r"\[anchor\([^)]*\)\]", "", s)
    s = re.sub(r"\{\{\{[^ ]*\s?", "", s).replace("}}}", "")  # color/size spans
    s = re.sub(r"<[^<>]*>", "", s)                           # leftover cell opts
    s = s.replace("[br]", "\n").replace("'''", "").replace("''", "")
    s = re.sub(r"[ \t]+", " ", s)
    return "\n".join(p.strip() for p in s.split("\n")).strip()


def cells(line: str):
    """Split a namuwiki table row into cells; returns None if not a row."""
    if not line.startswith("||"):
        return None
    body = line.strip()
    if body.endswith("||"):
        body = body[:-2]
    return body[2:].split("||")


def parse_all(path):
    rows, bads = [], []
    labels = collections.Counter()
    for line in open(path):
        r = json.loads(line)
        t = r["text"]
        i = t.find("[anchor(앵커-도감 설명)]")
        if i < 0:
            continue
        # single-species articles carry no section header: fall back to the title.
        # Multi-species articles must not, or a headerless first block would be
        # attributed to the article's own species (투구푸스 vs 투구).
        seg = t[i:]
        headed = re.search(r"^\|\|<-\d.*?(\d{1,4})\s+[가-힣]", seg, re.M)
        cur = None if headed else BYNAME.get(r["title"].split("(")[0].strip())
        form = None
        span_left, span_body = 0, None
        for line in t[i:].split("\n")[1:]:
            cs = cells(line)
            if cs is None:
                if line.strip() == "":
                    continue
                break
            if "[anchor(앵커-도감설명 스킵)]" in line:
                break
            is_header = bool(re.match(r"^<-\d", cs[0])) and len(cs) == 1
            if is_header:
                h = clean(cs[0])
                if "도감 설명" in h or not h:
                    continue
                m = re.search(r"(\d{1,4})\s+([가-힣].*)$", h)
                if m:
                    cur, nm = int(m.group(1)), m.group(2).strip()
                    form = None if NAMEOF.get(cur) == nm else nm
                else:
                    cur, form = BYNAME.get(h.strip()), None
                if cur is None:
                    bads.append((r["title"], "header", h[:40]))
                span_left = 0
                continue
            label = clean(cs[0])
            if not label:
                continue
            if len(cs) >= 2 and cs[1].strip() != "":
                sp = ROWSPAN.search(cs[1])
                body = clean(cs[1])
                span_left = (int(sp.group(1)) - 1) if sp else 0
                span_body = body
            elif span_left > 0:
                body = span_body
                span_left -= 1
            else:
                body = ""
            if not body:
                bads.append((r["title"], "empty", label[:30]))
                continue
            if cur is None:
                bads.append((r["title"], "no-species", label[:30]))
                continue
            labels[label] += 1
            rows.append({"species": cur, "raw_label": label, "ko": body,
                         "title": r["title"], "form": form})
    return rows, bads, labels


if __name__ == "__main__":
    rows, bads, labels = parse_all(sys.argv[1])
    print("rows", len(rows), "species", len({r['species'] for r in rows}), "bad", len(bads))
    json.dump(rows, open(sys.argv[2], "w"), ensure_ascii=False)
    for k, v in labels.most_common(200):
        print(v, repr(k))
    print("--- bad sample")
    for b in bads[:20]:
        print(b)
