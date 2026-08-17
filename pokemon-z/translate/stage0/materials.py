# /// script
# requires-python = ">=3.12"
# ///
"""판정 재료 생성 — 자리 목록을 받아 유지자에게 올릴 재료를 기계로 갖춘다.

싣는 것: 맵 이름 · 화자(이름표+그림+페르소나+버킷+그룹) · 층 · 겪는 순서의 전 대사
(원문·번역 병기, cmd 오름차순) · 같은 원문의 다른 자리 · 유지자 손이 지나간 표시
(fixlog·register-ok). 한국어 문안은 만들지 않는다 — 실물만 나른다.

화자는 **이름표(`who`)가 먼저이고 그림은 그다음이다** — 그림은 이벤트에 하나뿐이라
스토리 장면처럼 화자가 여럿인 자리를 한 이름으로 뭉갠다.

⚠ 이름표 상속도 틀리는 자리가 있다(장면 끝의 내레이션을 앞 화자가 물고 가는 꼴).
**틀린 자리는 `translate/stage0/overrides.jsonl`에 한 줄로 고친다** — 이 도구는
overrides를 얹어 읽으므로 gen 재생성 없이 곧바로 반영되고, 고친 줄에는 표시가 붙는다.

  {"id":"m213.e4.p0.c88","set":{"who":""},"why":"장면 끝 내레이션","by":"사람/2026-08-18"}

usage:
  uv run translate/stage0/materials.py --map 141 --event 33
  uv run translate/stage0/materials.py --phrase "Bueno, otra vez será." --map 63
  uv run translate/stage0/materials.py --map 305 --event 2 --proposals p.jsonl \\
      --review translate/batch/page-out-m305 → 검수 스튜디오로 본다
  uv run translate/stage0/materials.py --selftest
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DATA, OUT, ROOT, apply_overrides, norm, read_jsonl,  # noqa: E402
                    read_overrides)

sys.path.insert(0, str(ROOT))
import mapname  # noqa: E402

DUP_CAP = 12          # 「...」류 정형구는 수백 자리에 서므로 자르고 수만 알린다
ID_RE = re.compile(r"^m(\d+)\.e(\d+)\.p(\d+)\.c(\d+)$")
STEM_RE = re.compile(r"(ow|OW|TS|w)?\d*$")


# ── 실물 로드 ────────────────────────────────────────────────────────────────
def load():
    """sites·messages를 읽고 **사람 수정(overrides)을 얹어** 돌려준다.

    gen을 다시 돌리지 않아도 화자 손지정이 곧바로 재료에 반영되게 하려는 것이다.
    함께 돌려주는 집합은 화자 칸을 사람이 지정한 자리 — 출력에 표시가 붙는다.
    """
    sites = read_jsonl(OUT / "sites.jsonl")
    msg_rows = read_jsonl(OUT / "messages.jsonl")
    ovr = read_overrides()
    sites, msg_rows = apply_overrides(sites, msg_rows, ovr)
    who_set = {o["id"] for o in ovr if {"who", "speaker"} & set(o["set"])}
    msgs = {m["id"]: m["val"] for m in msg_rows}

    def val(sid):
        v, seen = msgs.get(sid), set()
        while isinstance(v, dict) and "ref" in v and v["ref"] not in seen:
            seen.add(v["ref"])
            v = msgs.get(v["ref"])
        return v if isinstance(v, str) else ""

    rows = []
    for s in sites:
        m = ID_RE.match(s["id"])
        if not m:
            continue                      # 맵 밖 절·좌표 열쇠는 시퀀스가 없다
        mp, ev, pg, cmd = (int(x) for x in m.groups())
        rows.append({**s, "map": mp, "event": ev, "page": pg, "cmd": cmd,
                     "ko": val(s["id"]), "nk": norm(s.get("src", ""))})
    return rows, who_set


def proposals(path):
    """제안 문안 층 — {"id", "new", "why"} 한 줄이 한 자리. 재료와 같은 장에 실린다.

    유지자에게 올리는 것은 「실물 + 제안」 한 장이지, 재료 한 장과 표 한 장이 아니다.
    """
    return {r["id"]: (r.get("why", ""), r["new"]) for r in read_jsonl(Path(path))} if path else {}


def naming(r):
    """한 줄의 화자 표시 — 이름표가 먼저, 없으면 그림, 둘 다 없으면 표시 없음."""
    return r.get("who") or r.get("speaker") or "(화자 없음)"


def personas():
    """스프라이트 → (버킷, 페르소나 한 줄). 그림 이름만으로는 못 읽는다."""
    p = ROOT / "persona-table.jsonl"
    return {r["sprite"]: (r.get("버킷", ""), r.get("페르소나", ""))
            for r in read_jsonl(p)} if p.exists() else {}


def sprite_groups():
    g = json.loads((ROOT / "sprite-groups.json").read_text(encoding="utf-8"))["groups"]
    return {s: grp for grp, ss in g.items() for s in ss}


def marks():
    """(fixlog 원문 키, register-ok 좌표 조건들) — 사람 판정이 지나간 자리."""
    fix = {norm(r["es"]) for r in read_jsonl(ROOT / "fixlog.jsonl") if r.get("es")}
    ok_path = DATA / "register-ok.jsonl"
    ok = read_jsonl(ok_path) if ok_path.exists() else []
    return fix, ok


def ok_hit(ok, row):
    """register-ok 한 줄은 있는 좌표 칸만으로 맞춘다(page·cmd가 없는 줄이 있다)."""
    out = []
    for r in ok:
        if all(r.get(k) == row[k] for k in ("map", "event", "page", "cmd") if k in r):
            out.append(r.get("이유", ""))
    return out


# ── 재료 조립 ────────────────────────────────────────────────────────────────
class Ctx:
    def __init__(self, prop=None):
        self.rows, self.who_set = load()
        self.prop = prop or {}
        self.persona = personas()
        self.s2g = sprite_groups()
        self.fix, self.ok = marks()
        self.by_ev = {}
        self.by_src = {}
        for r in self.rows:
            self.by_ev.setdefault((r["map"], r["event"]), []).append(r)
            self.by_src.setdefault(r["nk"], []).append(r)

    def speaker(self, who, sprite):
        """머리에 서는 화자 한 줄 — 이름표가 이름이고, 그림은 페르소나를 여는 열쇠다."""
        bucket, per = self.persona.get(sprite, ("", "")) if sprite else ("", "")
        grp = self.s2g.get(STEM_RE.sub("", sprite) or "(없음)", "?") if sprite else "?"
        return who or "(이름표 없음)", sprite, grp, bucket, per

    def flags(self, r):
        f = []
        if r["id"] in self.who_set:
            f.append("화자 손지정(overrides)")
        if r["nk"] in self.fix:
            f.append("유지자 손수정(fixlog)")
        for why in ok_hit(self.ok, r):
            f.append(f"기존 판정 register-ok: {why}" if why else "기존 판정 register-ok")
        return f

    def group(self, mp, ev, cand_ids, title=None, note=None):
        """한 (맵, 이벤트) 묶음의 재료 — 머리 · 페이지별 시퀀스 · 같은 원문의 다른 자리."""
        seq = sorted(self.by_ev.get((mp, ev), []), key=lambda r: (r["page"], r["cmd"]))
        cands = [r for r in seq if r["id"] in cand_ids] or seq
        casts, layers = {}, {}
        for r in seq:
            casts[(r.get("who", ""), r.get("speaker", ""))] = None
            layers[r.get("layer", "")] = None
        # 같은 원문의 다른 자리 — 원문마다 한 번, 흔한 정형구는 잘라서 수만 알린다
        dups, seen_nk = [], set()
        for r in cands:
            if r["nk"] in seen_nk:
                continue
            seen_nk.add(r["nk"])
            spots, seen_spot = [], set()
            for o in self.by_src.get(r["nk"], ()):
                key = (o["map"], o["event"], o["cmd"], o.get("speaker", ""))
                if (o["map"], o["event"]) != (mp, ev) and key not in seen_spot:
                    seen_spot.add(key)
                    spots.append(o)
            if spots:
                dups.append((r, spots[:DUP_CAP], len(spots)))
        return {
            "map": mp, "event": ev, "map_ko": mapname.ko(mp) or "(이름 없음)",
            "title": title, "note": note,
            "speakers": [self.speaker(w, s) for w, s in casts],
            "layers": [l for l in layers if l],
            "seq": [(r, r["id"] in cand_ids, self.flags(r)) for r in seq],
            "prop": self.prop,
            "dups": dups,
        }


def context_cut(g, n):
    """--context N — 후보 앞뒤 N줄만 남긴다(페이지 경계는 안 넘는다)."""
    seq, keep = g["seq"], set()
    if n is None or not any(cand for _, cand, _ in seq):
        return g                          # 이벤트 통째 모드는 자를 후보가 없다
    for i, (r, cand, _) in enumerate(seq):
        if not cand:
            continue
        for j in range(max(0, i - n), min(len(seq), i + n + 1)):
            if seq[j][0]["page"] == r["page"]:
                keep.add(j)
    return {**g, "seq": [x for i, x in enumerate(seq) if i in keep]}


# ── 입력 ─────────────────────────────────────────────────────────────────────
def groups_from_args(ctx, a):
    if a.map is not None and a.event is not None:
        return [ctx.group(a.map, a.event, set())]
    if a.phrase:
        nk = norm(a.phrase)
        hits = [r for r in ctx.by_src.get(nk, ())
                if a.map is None or r["map"] == a.map]
        if not hits:
            sys.exit(f"그 원문의 자리가 없다: {a.phrase!r}"
                     + (f" (맵{a.map})" if a.map is not None else ""))
        out, seen = [], {}
        for r in hits:
            seen.setdefault((r["map"], r["event"]), set()).add(r["id"])
        for (mp, ev), ids in seen.items():
            out.append(ctx.group(mp, ev, ids, title=f"「{a.phrase}」"))
        return out
    return groups_from_ids(ctx, Path(a.ids))


def groups_from_ids(ctx, path):
    """자리 목록 jsonl — id 또는 map+event(+cmd). 여분 칸은 제목·메모로 싣는다."""
    buckets = {}
    for row in read_jsonl(path):
        if "id" in row:
            m = ID_RE.match(row["id"])
            if not m:
                print(f"건너뜀(맵 자리가 아님): {row['id']}", file=sys.stderr)
                continue
            mp, ev, cmd = int(m.group(1)), int(m.group(2)), int(m.group(4))
        else:
            mp, ev, cmd = row["map"], row["event"], row.get("cmd")
        key = row.get("bucket") or f"{mp}.{ev}"
        b = buckets.setdefault(key, {"mp": mp, "ev": ev, "ids": set(),
                                     "title": row.get("bucket"), "note": row.get("note")})
        for r in ctx.by_ev.get((mp, ev), ()):
            if cmd is None or r["cmd"] == cmd:
                b["ids"].add(r["id"])
    return [ctx.group(b["mp"], b["ev"], b["ids"], b["title"], b["note"])
            for b in buckets.values()]


# ── 출력 ─────────────────────────────────────────────────────────────────────
def head_lines(g):
    out = []
    for who, sprite, grp, bucket, per in g["speakers"]:
        bits = [who]
        if sprite:
            bits.append(f"그림 {sprite}")
        if grp and grp != "?":
            bits.append(f"그룹 {grp}")
        if bucket:
            bits.append(f"등재 {bucket}")
        line = " · ".join(bits)
        out.append(f"{line} — {per}" if per else line)
    return out


def md(groups):
    L = []
    for g in groups:
        L.append(f"## 맵{g['map']} {g['map_ko']} · 이벤트{g['event']}"
                 + (f" — {g['title']}" if g["title"] else ""))
        if g["note"]:
            L.append(f"> {g['note']}")
        L.append("")
        for h in head_lines(g):
            L.append(f"- 화자: {h}")
        L.append(f"- 층: {' / '.join(g['layers']) or '(없음)'}")
        allf = sorted({f for _, _, fs in g["seq"] for f in fs})
        if allf:
            L.append("- 사람 손이 지나간 자리: " + " · ".join(allf))
        L.append("")
        page = None
        for r, cand, fs in g["seq"]:
            if r["page"] != page:
                page = r["page"]
                L.append(f"### 겪는 순서 — 페이지 {page}")
            mark = "»" if cand else " "
            tag = f"{naming(r)}|{r.get('layer', '?')}"
            flag = ("  ⚑ " + " · ".join(fs)) if fs else ""
            L.append(f"{mark} `[{r['cmd']}]` **{tag}**{flag}")
            L.append(f"    - ES: {r.get('src', '')}")
            L.append(f"    - KO: {r['ko']}")
            if r["id"] in g["prop"]:
                why, new = g["prop"][r["id"]]
                L.append(f"    - 제안: {new}" + (f"  ({why})" if why else ""))
        if g["dups"]:
            L.append("")
            L.append("### 같은 원문의 다른 자리")
            L.append("| 원문 | 자리 | 화자 | 층 | 현행 번역 |")
            L.append("|---|---|---|---|---|")
            for r, spots, total in g["dups"]:
                for o in spots:
                    L.append(f"| {esc_cell(r.get('src', ''))} | 맵{o['map']} "
                             f"{mapname.ko(o['map'])} {o['event']}·{o['cmd']} | "
                             f"{naming(o)} | {o.get('layer', '?')} | "
                             f"{esc_cell(o['ko'])} |")
                if total > len(spots):
                    L.append(f"| {esc_cell(r.get('src', ''))} | …외 {total - len(spots)}자리 "
                             f"(전체 {total}) | | | |")
        L.append("")
    return "\n".join(L)


def esc_cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def review_out(groups, out_dir):
    """검수 스튜디오(review_gui.py)가 읽는 꼴로 낸다 — 재료를 볼 화면은 그것이다.

    페이지마다 `p<맵>-<이벤트>-<페이지>.jsonl`(id·who·es·old[·new])을 쓰고, 제안이 붙은
    자리의 사유를 `screen-llm.jsonl`에 모은다. 이 도구는 화면을 만들지 않는다 —
    한 저장소에 검수 화면이 둘이면 판정이 어디 쌓였는지부터 갈린다.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    screen, pages = [], {}
    for g in groups:
        for r, _, _ in g["seq"]:
            # 배치 파이프라인의 자리 열쇠는 맵:이벤트:페이지:명령이다 — apply_verdicts가 그 꼴을 읽는다
            bid = f'{g["map"]}:{g["event"]}:{r["page"]}:{r["cmd"]}'
            row = {"id": bid, "who": naming(r), "es": r.get("src", ""), "old": r["ko"]}
            pr = g["prop"].get(r["id"])
            if pr:
                row["new"] = pr[1]
                screen.append({"id": r["id"], "유형": "말투", "근거": pr[0]})
            pages.setdefault((g["map"], g["event"], r["page"]), []).append(row)
    for (mp, ev, pg), rows in sorted(pages.items()):
        (out / f"p{mp}-{ev}-{pg}.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    (out / "screen-llm.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in screen), encoding="utf-8")
    return len(pages), len(screen)


def selftest():
    ctx = Ctx()
    g = ctx.group(141, 33, set())
    kos = [r["ko"] for r, _, _ in g["seq"]]
    assert g["map_ko"], "맵 이름이 안 붙었다"
    assert any("후보생" in k for k in kos), kos[:5]
    order = [(r["page"], r["cmd"]) for r, _, _ in g["seq"]]
    assert order == sorted(order), "겪는 순서가 아니다"
    # 원문 조인은 양쪽 norm — 줄바꿈이 박힌 원문도 붙어야 한다
    # 원문에는 줄바꿈이 박힌 자리가 있다 — 조인 열쇠는 양쪽 다 norm이어야 한다
    assert norm("a\n b") == "a b"
    assert all(r["nk"] == norm(r.get("src", "")) for r in ctx.rows)
    p = ctx.group(63, 4, {r["id"] for r in ctx.by_src[norm("Bueno, otra vez será.")]
                          if r["map"] == 63 and r["event"] == 4})
    assert p["dups"], "같은 원문의 다른 자리가 안 잡혔다"
    # 화자는 이름표가 먼저다 — 그림 하나에 화자 둘인 장면에서 갈려야 한다
    assert naming({"who": "Olivier", "speaker": "rupicow2"}) == "Olivier"
    assert naming({"who": "", "speaker": "rupicow2"}) == "rupicow2"
    two = ctx.group(305, 2, set())
    whos = {naming(r) for r, _, _ in two["seq"]}
    assert {"Rúpico", "Olivier"} <= whos, whos
    assert len(two["speakers"]) >= 2, two["speakers"]
    # 사람 손지정은 gen 재생성 없이 곧바로 얹힌다
    sid = "m305.e2.p1.c58"
    s2, _ = apply_overrides([{"id": sid, "who": "Rúpico"}], [],
                            [{"id": sid, "set": {"who": "올리비에"}}])
    assert s2[0]["who"] == "올리비에", s2
    print("selftest ok — 맵141 이벤트33 {}행 · 맵63 중복 자리 {}건".format(
        len(g["seq"]), len(p["dups"])))


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--ids"), a.add_argument("--phrase")
    a.add_argument("--map", type=int), a.add_argument("--event", type=int)
    a.add_argument("--context", type=int, help="후보 앞뒤 N줄만")
    a.add_argument("-o", "--out", help="사람·에이전트가 읽을 md")
    a.add_argument("--review", help="검수 스튜디오가 읽을 폴더로 낸다")
    a.add_argument("--serve", type=int, nargs="?", const=8793,
                   help="--review와 함께 — 낸 자리를 검수 스튜디오로 곧바로 띄운다(기본 8793)")
    a.add_argument("--proposals", help="제안 문안 jsonl — {id, new, why}")
    a.add_argument("--selftest", action="store_true")
    a = a.parse_args()
    if a.selftest:
        return selftest()
    if not (a.ids or a.phrase or (a.map is not None and a.event is not None)):
        sys.exit("--ids · --phrase · (--map과 --event) 중 하나가 필요하다")
    ctx = Ctx(proposals(a.proposals))
    groups = [context_cut(g, a.context) for g in groups_from_args(ctx, a)]
    text = md(groups)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    if a.review:
        npg, nhit = review_out(groups, a.review)
        print(f"검수 스튜디오 입력 {npg}장면 · 제안 {nhit}줄 → {a.review}")
        if a.serve:
            # 이미 승인된 이벤트도 다시 보는 자리라 --no-skip이 기본이다
            import subprocess
            cmd = [sys.executable, str(ROOT / "review_gui.py"), "--out", a.review,
                   "--port", str(a.serve), "--no-skip"]
            return subprocess.call(cmd)
        print(f"  uv run translate/review_gui.py --out {a.review} --port 8793 --no-skip")
    if not (a.out or a.review):
        print(text)


if __name__ == "__main__":
    main()
