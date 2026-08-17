# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
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

**맵 밖 절의 문구도 재료로 낸다.** 상점·창구처럼 이벤트에서 열리는 화면의 문구(절23 등)는
겪는 순서가 없으므로 자리 목록에 `anchor`를 준다 — 그 이벤트의 대사 뒤에 「화면」으로 붙어,
플레이어가 말을 건 뒤 무엇을 어떤 차례로 만나는지가 한 장에 선다.

  {"k":"¿Te interesa algo de lo que tengo?","anchor":"m26.e4","label":"첫 인사","order":1,
   "bucket":"상점 점원 말투"}

자리는 `k`(원문)나 `id`(사이트 id)로 가리키고, 원문 하나에 자리가 여럿이면 `site`로 고른다.
화면 자리의 판정 열쇠는 사이트 id 그대로이고 `apply_verdicts`는 그 줄을 건너뛴다 —
반영 경로가 절마다 달라 사람이 읽고 넣는다.

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

    rows, off = [], []
    for s in sites:
        m = ID_RE.match(s["id"])
        if not m:
            # 맵 밖 자리(절23 스크립트 문구 등)는 겪는 순서가 없다 — 앵커를 받아
            # 그 이벤트의 순서 뒤에 「화면」으로 붙인다(groups_from_ids의 anchor).
            # 좌표 열쇠(`loc.*`)는 맵 자리의 파생값이라 뺀다 — 판정할 자리가 아니다.
            if s.get("src") and s["id"].startswith("s"):
                off.append({**s, "ko": val(s["id"]), "nk": norm(s["src"])})
            continue
        mp, ev, pg, cmd = (int(x) for x in m.groups())
        rows.append({**s, "map": mp, "event": ev, "page": pg, "cmd": cmd,
                     "ko": val(s["id"]), "nk": norm(s.get("src", ""))})
    return rows, who_set, off


def proposals(path):
    """제안 문안 층 — {"id", "new", "why"} 한 줄이 한 자리. 재료와 같은 장에 실린다.

    유지자에게 올리는 것은 「실물 + 제안」 한 장이지, 재료 한 장과 표 한 장이 아니다.

    `bucket`을 적으면 그 묶음에서만 서는 제안이다 — 같은 자리에 갈래별로 다른 문안을
    올릴 때 쓴다(상점 점원 말투의 존대·반말·하게체처럼). 안 적으면 모든 묶음에 선다.
    """
    return {(r.get("bucket") or "", r["id"]): (r.get("why", ""), r["new"])
            for r in read_jsonl(Path(path))} if path else {}


def naming(r):
    """한 줄의 화자 표시 — 이름표가 먼저, 없으면 그림, 둘 다 없으면 표시 없음."""
    return r.get("who") or r.get("speaker") or "(화자 없음)"


def bid_of(g, r):
    """자리 열쇠 — 맵 자리는 배치 꼴(맵:이벤트:페이지:명령), 화면 자리는 사이트 id 그대로.

    apply_verdicts는 배치 꼴만 정본에 반영한다. 화면 자리(절23 등)는 반영 경로가 달라
    id를 그대로 두고, 판정은 사람이 읽어 반영한다.

    ⚠ 화면 자리에는 앵커를 붙인다 — **같은 문구를 갈래별로 여러 이벤트에 걸어 물을 때**
    열쇠가 겹치면 판정이 서로를 덮는다(상점 갈래 셋이 그 꼴이었다). 앵커를 붙여도
    숫자로 시작하지 않으므로 apply_verdicts는 그대로 건너뛴다.
    """
    return (f'{g["map"]}:{g["event"]}:{r["page"]}:{r["cmd"]}'
            if r.get("cmd") is not None else f'{r["id"]}@m{g["map"]}.e{g["event"]}')


def _groups_yaml():
    import yaml
    return yaml.safe_load((OUT / "groups.yaml").read_text(encoding="utf-8"))


def personas():
    """스프라이트 → (버킷, 페르소나 한 줄). 그림 이름만으로는 못 읽는다."""
    return {e["group"]: (e.get("bucket", ""), e.get("persona", ""))
            for e in _groups_yaml()["groups"]}


def sprite_groups():
    g = _groups_yaml()["sprite_groups"]["groups"]
    return {s: grp for grp, ss in g.items() for s in ss}


def marks():
    """fixlog 원문 키 — 유지자 손이 지나간 자리. register-ok는 자리 칸(register_ok)으로
    사이트에 펴져 있어(gen.stamp_register_ok) 따로 안 읽는다."""
    return {norm(r["es"]) for r in read_jsonl(ROOT / "fixlog.jsonl") if r.get("es")}


# ── 재료 조립 ────────────────────────────────────────────────────────────────
class Ctx:
    def __init__(self, prop=None):
        self.rows, self.who_set, self.off = load()
        self.prop = prop or {}
        self.persona = personas()
        self.s2g = sprite_groups()
        self.fix = marks()
        self.by_ev = {}
        self.by_src = {}
        for r in self.rows:
            self.by_ev.setdefault((r["map"], r["event"]), []).append(r)
            self.by_src.setdefault(r["nk"], []).append(r)
        self.by_site = {r["id"]: r for r in self.off}
        self.off_by_src = {}
        for r in self.off:
            self.off_by_src.setdefault(r["nk"], []).append(r)

    def offmap(self, row):
        """자리 목록 한 줄 → 맵 밖 자리 하나. `id`로 집거나 `k`(원문)로 찾는다."""
        if row.get("id"):
            hit = self.by_site.get(row["id"])
            if not hit:
                sys.exit(f"맵 밖 자리를 못 찾았다: {row['id']!r}")
            return hit
        hits = self.off_by_src.get(norm(row["k"]), [])
        if not hits:
            sys.exit(f"그 원문의 맵 밖 자리가 없다: {row['k']!r}")
        if len(hits) > 1 and not row.get("site"):
            ids = ", ".join(h["id"] for h in hits[:5])
            sys.exit(f"원문 하나에 자리가 여럿이다 — `site`로 골라라: {row['k']!r} → {ids}")
        return next((h for h in hits if h["id"] == row.get("site")), hits[0])

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
        if "register_ok" in r:
            why = r["register_ok"]
            f.append(f"기존 판정 register-ok: {why}" if why else "기존 판정 register-ok")
        return f

    def group(self, mp, ev, cand_ids, title=None, note=None, attach=()):
        """한 (맵, 이벤트) 묶음의 재료 — 머리 · 페이지별 시퀀스 · 같은 원문의 다른 자리.

        `attach`는 그 이벤트에서 열리는 **화면**의 문구다(상점·창구 등 맵 밖 절).
        플레이어가 겪는 순서는 「이벤트 대사 → 화면」이므로 시퀀스 꼬리에 붙인다.
        """
        seq = sorted(self.by_ev.get((mp, ev), []), key=lambda r: (r["page"], r["cmd"]))
        if attach:
            pg = seq[-1]["page"] if seq else 0
            for i, (site, label, _ord) in enumerate(sorted(attach, key=lambda x: x[2]), 1):
                seq.append({**site, "map": mp, "event": ev, "page": pg, "cmd": None,
                            "screen": f"{i}. {label}" if label else str(i),
                            "layer": "화면"})
                cand_ids = set(cand_ids) | {site["id"]}
        cands = [r for r in seq if r["id"] in cand_ids] or seq
        # 제안은 묶음별로 갈린다 — 묶음을 안 적은 제안은 어느 묶음에나 선다
        prop = {i: v for (b, i), v in self.prop.items() if not b or b == title}
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
            "prop": prop,
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
    if a.who:
        hits = [r for r in ctx.rows if (r.get("who") or "") == a.who]
        if not hits:
            names = sorted({r["who"] for r in ctx.rows if r.get("who")
                            and a.who in r["who"]})[:8]
            sys.exit(f"그 화자의 자리가 없다: {a.who!r}"
                     + (f" — 비슷한 이름: {', '.join(names)}" if names else ""))
        seen = {}
        for r in hits:
            seen.setdefault((r["map"], r["event"]), set()).add(r["id"])
        return [ctx.group(mp, ev, ids, title=f"화자 {a.who}")
                for (mp, ev), ids in seen.items()]
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


def anchor_of(row):
    """`anchor`는 「이 문구를 어느 이벤트에서 만나나」다 — "m26.e4" 또는 {"map","event"}."""
    a = row["anchor"]
    if isinstance(a, str):
        m = re.match(r"^m(\d+)\.e(\d+)$", a)
        if not m:
            sys.exit(f"앵커 꼴이 아니다(m<맵>.e<이벤트>): {a!r}")
        return int(m.group(1)), int(m.group(2))
    return int(a["map"]), int(a["event"])


def groups_from_ids(ctx, path):
    """자리 목록 jsonl — id 또는 map+event(+cmd). 여분 칸은 제목·메모로 싣는다.

    **맵 밖 자리**(절23 스크립트 문구 등)는 `anchor`를 함께 준다 — 그 이벤트의 겪는
    순서 뒤에 「화면」으로 붙는다. 자리는 `id`(사이트 id)나 `k`(원문)로 가리키고,
    `label`·`order`가 화면에서 만나는 차례를 적는다.
    """
    buckets, attach = {}, {}
    for row in read_jsonl(path):
        if row.get("anchor"):
            mp, ev = anchor_of(row)
            site = ctx.offmap(row)
            key = (row.get("bucket") or "", mp, ev)
            b = buckets.setdefault(key, {"mp": mp, "ev": ev, "ids": set(),
                                         "title": row.get("bucket"),
                                         "note": row.get("note")})
            attach.setdefault(key, []).append(
                (site, row.get("label", ""), row.get("order", len(attach.get(key, ())) + 1)))
            continue
        if "id" in row:
            m = ID_RE.match(row["id"])
            if not m:
                print(f"건너뜀(맵 자리가 아님): {row['id']}", file=sys.stderr)
                continue
            mp, ev, pg, cmd = (int(m.group(1)), int(m.group(2)),
                               int(m.group(3)), int(m.group(4)))
        else:
            mp, ev, pg, cmd = row["map"], row["event"], row.get("page"), row.get("cmd")
        # 묶음 이름은 여러 이벤트에 걸칠 수 있다 — 자리는 (이름, 맵, 이벤트)로 가른다.
        # 이름만으로 묶으면 첫 이벤트의 좌표가 남아 나머지 이벤트의 자리가 조용히 사라진다.
        key = (row.get("bucket") or "", mp, ev)
        b = buckets.setdefault(key, {"mp": mp, "ev": ev, "ids": set(),
                                     "title": row.get("bucket"), "note": row.get("note")})
        for r in ctx.by_ev.get((mp, ev), ()):
            if (cmd is None or r["cmd"] == cmd) and (pg is None or r["page"] == pg):
                b["ids"].add(r["id"])
    return [ctx.group(b["mp"], b["ev"], b["ids"], b["title"], b["note"],
                      attach.get(k, ()))
            for k, b in buckets.items()]


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
        page, on_screen = None, False
        for r, cand, fs in g["seq"]:
            if r.get("screen"):
                if not on_screen:
                    on_screen = True
                    L.append("### 여기서 열리는 화면 — 말을 건 뒤 이 차례로 만난다")
            elif r["page"] != page:
                page = r["page"]
                L.append(f"### 겪는 순서 — 페이지 {page}")
            mark = "»" if cand else " "
            tag = f"{naming(r)}|{r.get('layer', '?')}"
            flag = ("  ⚑ " + " · ".join(fs)) if fs else ""
            L.append(f"{mark} `[{r.get('screen') or r['cmd']}]` **{tag}**{flag}")
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


def write_brief(out_dir, brief_path, groups, nhit):
    """판정 요청 브리핑 — 제목·전반 설명·건마다 「정해 달라는 것·갈림·추천」.

    검수 화면 맨 위에 서고 건 단위로 승인·기각·보류를 받는다. 문안 판정(행 단위)과
    층위가 다르다 — 규칙·표기·수술처럼 문안이 아닌 판정이 갈 자리가 여기다.
    """
    b = json.loads(Path(brief_path).read_text(encoding="utf-8")) if brief_path else {}
    b["scenes"] = len({(g["map"], g["event"]) for g in groups})
    b["hits"] = nhit
    for q in b.get("asks", []):
        if q.get("bucket"):      # 묶음 이름이 같은 자리를 그 건에 묶는다
            q["rows"] = [bid_of(g, r)
                         for g in groups if g["title"] == q["bucket"]
                         for r, cand, _ in g["seq"] if cand or r["id"] in g["prop"]]
    (Path(out_dir) / "brief.json").write_text(
        json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    return len(b.get("asks", []))


def review_out(groups, out_dir):
    """검수 스튜디오(review_gui.py)가 읽는 꼴로 낸다 — 재료를 볼 화면은 그것이다.

    페이지마다 `p<맵>-<이벤트>-<페이지>.jsonl`(id·who·es·old[·new])을 쓰고, 제안이 붙은
    자리의 사유를 `screen-llm.jsonl`에 모은다. 이 도구는 화면을 만들지 않는다 —
    한 저장소에 검수 화면이 둘이면 판정이 어디 쌓였는지부터 갈린다.

    ⚠ 검수 스튜디오의 장면 열쇠는 (맵, 이벤트, 페이지)라 **묶음 이름이 파일에 안 담긴다.**
    `--phrase`·`--ids`처럼 자리를 자유롭게 고른 판정은 여러 장면에 흩어지므로, 묶음 이름과
    메모를 각 줄의 **사유**에 실어 어느 판정에 속한 자리인지 화면에서 읽히게 한다.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    screen, pages = [], {}
    for g in groups:
        for r, cand, _ in g["seq"]:
            # 배치 파이프라인의 자리 열쇠는 맵:이벤트:페이지:명령이다 — apply_verdicts가 그 꼴을 읽는다
            bid = bid_of(g, r)
            row = {"id": bid, "who": naming(r), "es": r.get("src", ""), "old": r["ko"]}
            pr = g["prop"].get(r["id"])
            if pr:
                row["new"] = pr[1]
            elif cand:
                row["new"] = r["ko"]      # 문안 없이 자리만 지목한 판정 — 현행을 그대로 세운다
            if pr or cand:
                why = " · ".join(x for x in (g["title"], g["note"],
                                             pr[0] if pr else "") if x)
                screen.append({"id": bid,
                               "유형": g["title"] or ("제안" if pr else "판정 자리"),
                               "근거": why})
            pages.setdefault((g["map"], g["event"], r["page"]), []).append(row)
    for (mp, ev, pg), rows in sorted(pages.items()):
        # 맵 번호는 세 자리로 채운다 — review_gui의 「이벤트 전체 보기」가 그 꼴로 찾는다
        (out / f"p{mp:03d}-{ev}-{pg}.jsonl").write_text(
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
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ctx2 = Ctx({("", f"m141.e33.p0.c{g['seq'][0][0]['cmd']}"): ("시험", "새 문안")})
        g2 = ctx2.group(141, 33, set())
        npg, nhit = review_out([g2], td)
        rows = [json.loads(x) for x in (Path(td) / "p141-33-0.jsonl").read_text(
            encoding="utf-8").splitlines()]
        scr = [json.loads(x) for x in (Path(td) / "screen-llm.jsonl").read_text(
            encoding="utf-8").splitlines()]
        ids = {r["id"] for r in rows}
        # 배치 꼴(맵:이벤트:페이지:명령)이라야 apply_verdicts가 읽는다
        assert all(i.count(":") == 3 for i in ids), sorted(ids)[:3]
        # 사유의 id가 행의 id와 같은 꼴이라야 검수 화면에 장면이 뜬다(안 그러면 0장면)
        assert all(x["id"] in ids for x in scr), (scr[:2], sorted(ids)[:3])
    # 맵 밖 자리(절23)는 앵커를 받아 그 이벤트의 겪는 순서 뒤에 화면으로 붙는다
    with tempfile.TemporaryDirectory() as td:
        ids = Path(td) / "ids.jsonl"
        ids.write_text(json.dumps(
            {"k": "¡Vuelve cuando quieras!", "anchor": "m26.e4", "label": "작별",
             "order": 1, "bucket": "화면 시험"}, ensure_ascii=False) + "\n",
            encoding="utf-8")
        gs = groups_from_ids(ctx, ids)
        last = gs[0]["seq"][-1][0]
        assert last.get("screen") and last["cmd"] is None, last
        assert last["id"].startswith("s23."), last["id"]
        assert gs[0]["seq"][-1][1], "화면 자리는 판정 자리로 서야 한다"
        # 화면 자리의 열쇠는 사이트 id + 앵커 — 배치 꼴로 위장하면 엉뚱한 맵 자리에 반영되고,
        # 앵커가 없으면 같은 문구를 갈래별로 물을 때 판정이 서로를 덮는다
        bid = bid_of(gs[0], last)
        assert bid == f'{last["id"]}@m26.e4', bid
        assert not bid[0].isdigit()
        npg, nhit = review_out(gs, td)
        assert nhit >= 1, nhit
    print("selftest ok — 맵141 이벤트33 {}행 · 맵63 중복 자리 {}건 · 화면 자리 1건".format(
        len(g["seq"]), len(p["dups"])))


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--ids"), a.add_argument("--phrase")
    a.add_argument("--who", help="화자 한 사람의 자리 전부 — 말투 판정의 단위")
    a.add_argument("--map", type=int), a.add_argument("--event", type=int)
    a.add_argument("--context", type=int, help="후보 앞뒤 N줄만")
    a.add_argument("-o", "--out", help="사람·에이전트가 읽을 md")
    a.add_argument("--review", help="검수 스튜디오가 읽을 폴더로 낸다")
    a.add_argument("--brief", help="판정 요청 브리핑 json — title·note·asks[{id,title,ask,split,rec}]")
    a.add_argument("--serve", type=int, nargs="?", const=8793,
                   help="--review와 함께 — 낸 자리를 검수 스튜디오로 곧바로 띄운다(기본 8793)")
    a.add_argument("--proposals", help="제안 문안 jsonl — {id, new, why}")
    a.add_argument("--selftest", action="store_true")
    a = a.parse_args()
    if a.selftest:
        return selftest()
    if not (a.ids or a.phrase or a.who or (a.map is not None and a.event is not None)):
        sys.exit("--ids · --phrase · --who · (--map과 --event) 중 하나가 필요하다")
    ctx = Ctx(proposals(a.proposals))
    groups = [context_cut(g, a.context) for g in groups_from_args(ctx, a)]
    text = md(groups)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    if a.review:
        if a.context is not None:
            print("⚠ --context는 --review에서 무시한다 — 검수 화면의 문맥은 장면 전문이다")
            groups = groups_from_args(ctx, a)
        npg, nhit = review_out(groups, a.review)
        nask = write_brief(a.review, a.brief, groups, nhit)
        print(f"검수 스튜디오 입력 {npg}장면 · 제안 {nhit}줄"
              + (f" · 판정 요청 {nask}건" if nask else "") + f" → {a.review}")
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
