# /// script
# requires-python = ">=3.12"
# ///
"""번역 즉석 수정 GUI — 검색·행 수정·메모·재빌드를 브라우저에서.

    uv run translate/fixgui.py          # http://localhost:8787
    uv run translate/fixgui.py 8899     # 포트 지정

Windows 브라우저에서 localhost로 바로 열린다(WSL 포트 공유).
수정 저장은 jsonl 행 단위 교체이고, [빌드] 버튼이 build.py를 돌려
보관소·게임 양쪽 korean.dat까지 갱신한다. 메모는 fixnotes.jsonl 축적
(fix.py --notes와 같은 파일).
"""

import gzip
import json
import re
import subprocess
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
LEDGER = HERE.parent / "docs" / "ledger"   # 판정 대장 (glossary·voices)
KO = HERE / "ko"
NOTES = HERE / "fixnotes.jsonl"
JOIN = HERE / "data" / "map-speaker-join.jsonl.gz"
ATTR = HERE / "data" / "speaker-attr.jsonl.gz"
GROUPS = HERE / "sprite-groups.json"

_ctx = None  # 조인표·귀속표 지연 로드


def norm(s):
    """정본의 k에는 화면 너비로 접힌 줄바꿈이 박혀 있다 — 표끼리 이을 땐 줄여서 맞춘다."""
    return re.sub(r"\s+", " ", s).strip()


def ctx():
    """(맵,원문)→화자·분류, (맵,원문)→이벤트 자리, (맵,이벤트,페이지)→명령 순서."""
    global _ctx
    if _ctx is None:
        _ctx = {"row": {}, "mapname": {}, "spots": {}, "page": {}}
        try:
            g = json.loads(GROUPS.read_text(encoding="utf-8"))["groups"]
            s2g = {s: grp for grp, ss in g.items() for s in ss}
            stem = lambda s: re.sub(r"(ow|OW|TS|w)?\d*$", "", s) or "(없음)"
            for line in gzip.open(JOIN, "rt", encoding="utf-8"):
                d = json.loads(line)
                if "sprite" not in d:
                    continue
                key = (d["map"], d["k"])
                if key not in _ctx["row"]:
                    _ctx["row"][key] = {"sprite": d["sprite"] or "(없음)",
                                        "group": s2g.get(stem(d["sprite"]), "?")}
                _ctx["mapname"].setdefault(d["map"], d.get("map_name", ""))
        except Exception as e:
            print("조인표 로드 실패(찾아보기 축소):", e)
        try:
            for line in gzip.open(ATTR, "rt", encoding="utf-8"):
                d = json.loads(line)
                k = norm(d["k"])
                spot = [d["event"], d["page"], d["cmd"], d["event_name"]]
                _ctx["spots"].setdefault((d["map"], k), []).append(spot)
                _ctx["page"].setdefault((d["map"], d["event"], d["page"]), []).append(
                    [d["cmd"], k, d["event_name"], d.get("sprite") or ""])
                _ctx["mapname"].setdefault(d["map"], d.get("map_name", ""))
            for v in _ctx["spots"].values():
                v.sort(key=lambda p: (p[0], p[1], p[2]))
        except Exception as e:
            print("귀속표 로드 실패(이벤트 칩 없음):", e)
    return _ctx


def chips(hits):
    """카드 칩에 붙일 것 — 맵 이름 · 이벤트 자리 · 같은 원문이 선 다른 맵 수."""
    c = ctx()
    want = {norm(h["es"]) for h in hits}
    others = {}
    for r in iter_rows():
        k = norm(r["es"])
        if k in want:
            others.setdefault(k, set()).add(r["map"])
    for h in hits:
        k = norm(h["es"])
        h["mapname"] = c["mapname"].get(h["map"], "")
        h["spots"] = c["spots"].get((h["map"], k), [])
        h["omaps"] = len(others.get(k, ())) - 1
    return hits


def event_page(mp, event, page):
    """한 이벤트-페이지의 대사를 명령 순서대로 — 현행 번역을 붙여서."""
    rows = sorted(ctx()["page"].get((mp, event, page), []), key=lambda p: p[0])
    cur = {norm(r["es"]): r for r in iter_rows() if r["map"] == mp}
    out = []
    for cmd, k, name, sprite in rows:
        r = cur.get(k)
        out.append({"cmd": cmd, "es": k, "sprite": sprite, "name": name,
                    "file": r["file"] if r else "", "line": r["line"] if r else 0,
                    "v": r["v"] if r else "(번역표에 없음)"})
    return out


def same_es(es, mp):
    """같은 원문이 선 다른 맵의 자리 — 정본은 (맵,원문)마다 별개 줄이라 값이 갈린다."""
    k = norm(es)
    c = ctx()
    return [{**r, "mapname": c["mapname"].get(r["map"], "")}
            for r in iter_rows() if norm(r["es"]) == k and r["map"] != mp]


def page():
    return (HERE / "fixgui.html").read_text(encoding="utf-8")


def iter_rows(only_file=""):
    """정본 전 행(v를 가진 행만) — {file,line,map,es,v}."""
    for p in sorted(KO.glob("*.jsonl")):
        if only_file and p.name != only_file:
            continue
        cur_map = None
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            d = json.loads(line)
            if "map" in d and "n" in d:
                cur_map = d["map"]
                continue
            v = d.get("v")
            if v is None:
                continue
            yield {"file": p.name, "line": i, "map": cur_map,
                   "es": d.get("k") or d.get("es") or "", "v": v}


# 검색 태그 — 배포판 스튜디오(webapp/app.js)와 같은 문법. 「반영」 상태는 없다:
# 로컬은 저장이 곧 정본이라 「빌드 전/후」 구분이 행에 남지 않는다.
TAGS = {"분류": "sec", "맵": "map", "화자": "spk", "원문": "k", "번역": "v", "상태": "state"}
STATE_VALS = ["수정", "메모"]
TOKEN_RE = re.compile(r'[^\s:"]+:(?:"[^"]*"?|\S*)|"[^"]*"?|\S+')
TAG_RE = re.compile(r"^(%s):(.*)$" % "|".join(TAGS))
UNQ_RE = re.compile(r'^"([^"]*)"?$')
SEC_LABEL = {0: "맵 대사", 1: "포켓몬 이름", 2: "분류", 3: "도감 설명", 4: "폼",
             5: "기술 이름", 6: "기술 설명", 7: "도구 이름", 8: "도구 복수형",
             9: "도구 설명", 10: "특성 이름", 11: "특성 설명", 12: "타입",
             13: "트레이너 직함", 14: "트레이너 이름", 15: "대전 시작 대사",
             16: "승리 대사", 17: "패배 대사", 18: "지방", 19: "장소 이름",
             20: "장소 설명", 21: "맵 이름", 22: "전화", 23: "시스템 문구"}


def sec_of(file):
    return int(file[:2]) if file[:2].isdigit() else -1


_mapko = None


def map_ko():
    """맵 이름 한국어판 — 조인표의 이름은 스페인어라 절21을 얹어야 「마을」로 찾는다."""
    global _mapko
    if _mapko is None:
        _mapko = {}
        for line in (KO / "21-map-names.jsonl").read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            if d.get("v"):
                _mapko[d["i"]] = d["v"]
    return _mapko


def parse_query(q):
    """`분류:도구 맵:12 화자:간호사 상태:수정 자유어` → 갈래별 값 목록."""
    f = {v: [] for v in TAGS.values()} | {"text": []}
    unq = lambda s: (UNQ_RE.match(s).group(1) if UNQ_RE.match(s) else s)
    for part in TOKEN_RE.findall(q):
        m = TAG_RE.match(part)
        if not m:
            t = unq(part)
            if t:
                f["text"].append(t)
            continue
        val = unq(m.group(2))
        if val:
            f[TAGS[m.group(1)]].append(val)
    return f


def row_match(r, f, c, edited, memoed):
    """같은 태그를 여럿 주면 OR, 다른 태그끼리는 AND — 웹과 같은 규칙."""
    if f["sec"]:
        sec, lab = sec_of(r["file"]), SEC_LABEL.get(sec_of(r["file"]), "")
        if not any(s == str(sec) or s in lab or s in r["file"] for s in f["sec"]):
            return False
    if f["map"]:
        names = [c["mapname"].get(r["map"], ""), map_ko().get(r["map"], "")]
        if r["map"] is None or not any(
                str(r["map"]) == m if m.isdigit() else any(n and m in n for n in names)
                for m in f["map"]):
            return False
    if f["spk"]:
        info = c["row"].get((r["map"], r["es"]))
        if not info or not any(x in info["sprite"] or x in info["group"] for x in f["spk"]):
            return False
    if not all(t in r["es"] for t in f["k"]):
        return False
    if not all(t in r["v"] for t in f["v"]):
        return False
    for st in f["state"]:
        if st.startswith("수정") and (r["file"], r["line"]) not in edited:
            return False
        if st.startswith("메모") and not any(m and m in r["v"] for m in memoed):
            return False
    return all(t in r["v"] or t in r["es"] for t in f["text"])


def search(q, only_file=""):
    f = parse_query(q)
    c = ctx() if (f["map"] or f["spk"]) else {"mapname": {}, "row": {}}
    edited = {(x["file"], x["line"]) for x in log_rows()} if f["state"] else set()
    memoed = [n["query"] for n in load_notes() if not n.get("done")] if f["state"] else []
    hits = []
    for r in iter_rows(only_file):
        if row_match(r, f, c, edited, memoed):
            hits.append(r)
            if len(hits) >= 500:
                return hits, True
    return hits, False


def tag_values(tag, part):
    """제안 드롭다운의 값 후보 — 태그마다 나오는 데가 다르다."""
    c = ctx()
    if tag == "분류":
        return [{"v": str(s), "label": f"{s:02d} · {lab}"}
                for s, lab in SEC_LABEL.items() if part in lab or part == str(s)][:12]
    if tag == "상태":
        return [{"v": v, "label": v} for v in STATE_VALS if v.startswith(part)]
    if tag == "맵":
        out = []
        for m, es in sorted(c["mapname"].items()):
            ko = map_ko().get(m, "")
            if str(m) == part if part.isdigit() else (part in ko or part in (es or "")):
                out.append({"v": str(m), "label": f"{m} · {ko or es or '(이름 없음)'}"})
        return out[:12]
    if tag == "화자":
        vals = {i[k] for i in c["row"].values() for k in ("sprite", "group")}
        return [{"v": v, "label": v} for v in sorted(vals) if part in v][:12]
    return []


def plan_replace(rows, find, repl, src=""):
    """세 갈래 일괄 바꾸기의 대상 산정.

    find 있음 → 번역 칸에서 찾는다(src를 주면 그 말이 원문에 있는 행만).
    find 없음 → 원문 기준: src를 가진 행의 번역을 repl로 통째 갈아 끼운다.
    돌려주는 skipped는 **원문 조건에 걸려 빠진 행** — 개수만 알리면 조건이 좁아
    놓친 자리를 확인할 길이 없다.
    """
    if not find and not src:
        return [], [], "찾을 문구나 원문 조건 중 하나는 필요합니다"
    hits, skipped = [], []
    for r in rows:
        if find:
            if find not in r["v"]:
                continue
            if src and src not in r["es"]:
                skipped.append(r)
                continue
            new = r["v"].replace(find, repl)
        else:
            if src not in r["es"]:
                continue
            new = repl
        if new == r["v"]:
            continue
        hits.append({**r, "new": new})
        if len(hits) >= 500:
            break
    return hits, skipped[:200], None


FIXLOG = HERE / "fixlog.jsonl"


def new_op():
    return str(time.time_ns())


def save_row(file, line, new_v, op=None, kind="row", label=""):
    p = KO / file
    if not p.is_file() or p.parent != KO:
        return "잘못된 파일"
    lines = p.read_text(encoding="utf-8").splitlines()
    d = json.loads(lines[line - 1])
    if "v" not in d:
        return "이 행에는 v가 없음"
    old = d["v"]
    if old == new_v:
        return None
    d["v"] = new_v
    lines[line - 1] = json.dumps(d, ensure_ascii=False)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(FIXLOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"file": file, "line": line, "es": d.get("k", ""),
                            "old": old, "new": new_v,
                            "op": op or new_op(), "kind": kind, "label": label},
                           ensure_ascii=False) + "\n")
    return None


def apply_replace(items, label):
    """고른 자리를 한 동작으로 묶어 적용 — (반영 수, 실패 목록)."""
    op, done, errs = new_op(), 0, []
    for it in items:
        err = save_row(it["file"], int(it["line"]), it["new"], op=op,
                       kind="bulk", label=label)
        if err:
            errs.append(f"{it['file']}:{it['line']} {err}")
        else:
            done += 1
    return done, errs


def log_rows():
    if not FIXLOG.exists():
        return []
    return [json.loads(l) for l in FIXLOG.read_text(encoding="utf-8").splitlines() if l]


def history(limit=60):
    """이력을 동작 묶음으로 세운다 — op가 없는 옛 줄은 한 줄이 곧 한 묶음."""
    ops, order = {}, []
    for i, r in enumerate(log_rows()):
        key = r.get("op") or f"legacy{i}"
        if key not in ops:
            ops[key] = {"op": key, "kind": r.get("kind", "row"),
                        "label": r.get("label", ""), "rows": []}
            order.append(key)
        ops[key]["rows"].append(r)
    return [ops[k] for k in order[::-1][:limit]]


def revert_op(opid):
    """묶음째 되돌린다. 그 뒤에 다시 고쳐진 행은 건너뛴다 — 남의 고침을 지우게 된다."""
    rows = next((g["rows"] for g in history(10**9) if g["op"] == opid), [])
    if not rows:
        return 0, 0, ["그 묶음이 이력에 없습니다"]
    cur = {(r["file"], r["line"]): r["v"] for r in iter_rows()}
    op, done, skipped, errs = new_op(), 0, 0, []
    for r in rows[::-1]:
        if cur.get((r["file"], r["line"])) != r["new"]:
            skipped += 1
            continue
        err = save_row(r["file"], r["line"], r["old"], op=op, kind="revert",
                       label=f"{opid} 되돌리기")
        if err:
            errs.append(f"{r['file']}:{r['line']} {err}")
        else:
            done += 1
    return done, skipped, errs


_ref = None  # 참고 자료 지연 로드


def ref_search(q):
    global _ref
    if _ref is None:
        _ref = {"gloss": (LEDGER / "glossary.md").read_text(encoding="utf-8").splitlines(),
                "canon": [], "msgs": []}
        cp = HERE / "canon" / "canon.jsonl"
        if cp.exists():
            _ref["canon"] = [json.loads(l) for l in cp.read_text(encoding="utf-8").splitlines() if l]
        mp = HERE / "canon" / "messages.jsonl.gz"
        if mp.exists():
            _ref["msgs"] = [json.loads(l) for l in gzip.open(mp, "rt", encoding="utf-8")]
    gl = [ln for ln in _ref["gloss"] if q in ln][:20]
    ca = [r for r in _ref["canon"]
          if any(q in str(r.get(k, "")) for k in ("es", "ko", "en"))][:20]
    ms = [r for r in _ref["msgs"] if q in r.get("es", "") or q in r.get("ko", "")][:20]
    return {"glossary": gl, "canon": ca, "messages": ms}


def maps_rows():
    """00-maps 행 전수 — 검색과 같은 형태 + sprite·group 부착."""
    c = ctx()
    p = KO / "00-maps.jsonl"
    cur_map = None
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        d = json.loads(line)
        if "map" in d and "n" in d:
            cur_map = d["map"]
            continue
        info = c["row"].get((cur_map, d.get("k", "")), {})
        yield {"file": p.name, "line": i, "map": cur_map,
               "es": d.get("k", ""), "v": d.get("v", ""),
               "sprite": info.get("sprite", "?"), "group": info.get("group", "?")}


def browse(by):
    from collections import Counter
    c = ctx()
    if by == "file":
        out = []
        for p in sorted(KO.glob("*.jsonl")):
            n = sum(1 for l in p.read_text(encoding="utf-8").splitlines()
                    if l and "\"v\"" in l)
            out.append({"key": p.name, "label": p.name, "count": n})
        return out
    cnt = Counter()
    for r in maps_rows():
        if by == "map":
            cnt[r["map"]] += 1
        elif by == "sprite":
            cnt[r["sprite"]] += 1
        elif by == "group":
            cnt[r["group"]] += 1
    if by == "map":
        return [{"key": str(k), "label": f"맵 {k} · {c['mapname'].get(k, '')}",
                 "count": n} for k, n in sorted(cnt.items(), key=lambda x: x[0] or 0)]
    return [{"key": str(k), "label": str(k), "count": n}
            for k, n in cnt.most_common()]


def listing(by, key):
    if by == "file":
        p = KO / key
        cur_map = None
        out = []
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            d = json.loads(line)
            if "map" in d and "n" in d:
                cur_map = d["map"]
                continue
            if "v" in d:
                out.append({"file": p.name, "line": i, "map": cur_map,
                            "es": d.get("k") or d.get("es") or "", "v": d["v"]})
            if len(out) >= 500:
                break
        return out
    out = []
    for r in maps_rows():
        val = str(r["map"]) if by == "map" else r.get(by, "?")
        if val == key:
            out.append(r)
        if len(out) >= 500:
            break
    return out


def load_notes():
    if not NOTES.exists():
        return []
    return [json.loads(l) for l in NOTES.read_text(encoding="utf-8").splitlines() if l]


def save_notes(notes):
    NOTES.write_text("\n".join(json.dumps(n, ensure_ascii=False) for n in notes) + "\n",
                     encoding="utf-8")


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            body = page().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif u.path == "/search":
            qs = urllib.parse.parse_qs(u.query)
            hits, trunc = search(qs.get("q", [""])[0], qs.get("file", [""])[0])
            self._json({"hits": chips(hits), "truncated": trunc})
        elif u.path == "/tagvals":
            qs = urllib.parse.parse_qs(u.query)
            self._json({"vals": tag_values(qs.get("tag", [""])[0],
                                           qs.get("part", [""])[0])})
        elif u.path == "/event":
            qs = urllib.parse.parse_qs(u.query)
            g = lambda k: int(qs.get(k, ["0"])[0])
            self._json({"rows": event_page(g("map"), g("event"), g("page"))})
        elif u.path == "/line":
            qs = urllib.parse.parse_qs(u.query)
            f, ln = qs.get("file", [""])[0], int(qs.get("line", ["0"])[0])
            hit = next((r for r in iter_rows(f) if r["line"] == ln), None)
            self._json({"hit": chips([hit])[0] if hit else None})
        elif u.path == "/samees":
            qs = urllib.parse.parse_qs(u.query)
            self._json({"hits": chips(same_es(qs.get("es", [""])[0],
                                              int(qs.get("map", ["-1"])[0])))})
        elif u.path == "/notes":
            self._json({"notes": load_notes()})
        elif u.path == "/browse":
            by = urllib.parse.parse_qs(u.query).get("by", ["map"])[0]
            self._json({"groups": browse(by)})
        elif u.path == "/list":
            qs = urllib.parse.parse_qs(u.query)
            self._json({"hits": chips(listing(qs.get("by", ["map"])[0],
                                              qs.get("key", [""])[0]))})
        elif u.path == "/history":
            self._json({"ops": history()})
        elif u.path == "/ref":
            q = urllib.parse.parse_qs(u.query).get("q", [""])[0]
            self._json(ref_search(q))
        else:
            self._json({"err": "?"}, 404)

    def do_POST(self):
        if self.path == "/save":
            b = self._body()
            err = save_row(b["file"], int(b["line"]), b["v"])
            self._json({"ok": err is None, "err": err})
        elif self.path == "/note":
            b = self._body()
            notes = load_notes()
            notes.append({"query": b["query"], "note": b["note"]})
            save_notes(notes)
            self._json({"ok": True})
        elif self.path == "/done":
            b = self._body()
            notes = load_notes()
            notes[int(b["i"]) - 1]["done"] = bool(b.get("done", True))
            save_notes(notes)
            self._json({"ok": True})
        elif self.path == "/notedel":
            b = self._body()
            notes = load_notes()
            del notes[int(b["i"]) - 1]
            save_notes(notes)
            self._json({"ok": True})
        elif self.path == "/replan":
            b = self._body()
            hits, skipped, err = plan_replace(iter_rows(b.get("file", "")),
                                              b.get("find", ""), b.get("repl", ""),
                                              b.get("src", ""))
            self._json({"ok": err is None, "err": err,
                        "hits": hits, "skipped": skipped})
        elif self.path == "/replace":
            b = self._body()
            done, errs = apply_replace(b["items"], b.get("label", ""))
            self._json({"ok": not errs, "done": done, "errs": errs})
        elif self.path == "/revert":
            b = self._body()
            done, skipped, errs = revert_op(b["op"])
            self._json({"ok": not errs, "done": done, "skipped": skipped, "errs": errs})
        elif self.path == "/build":
            r = subprocess.run(["uv", "run", str(HERE / "build.py")],
                               capture_output=True, text=True)
            last = (r.stdout.strip().splitlines() or ["(출력 없음)"])[-1]
            self._json({"ok": r.returncode == 0,
                        "msg": last if r.returncode == 0 else r.stderr[-200:]})
        else:
            self._json({"err": "?"}, 404)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    print(f"http://localhost:{port}  (중지: Ctrl+C)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    main()
