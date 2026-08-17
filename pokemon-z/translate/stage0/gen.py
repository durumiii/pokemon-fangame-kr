# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Z-53 이행 1단계 — 0단계 정본 파일 다섯을 지금 출처에서 **기계로만** 만든다.

사람 판정은 하나도 넣지 않는다. 지금 값을 그대로 옮긴다. 출처(`translate/ko/`,
`translate/data/`)는 읽기만 한다.

산출: translate/stage0/{sites.jsonl,messages.jsonl,groups.yaml,terms.yaml,axes.yaml}
되돌려 대조하는 쪽은 diff.py.

usage: uv run translate/stage0/gen.py
"""
import json
import sys

import yaml

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA, EMPTY_SECS, HASH_SECS, KO, LIST_SECS, OUT, ROOT,
    apply_overrides, dump_jsonl, h8, ko_file, norm, read_jsonl, read_maps, read_overrides,
)

# 귀속표에서 자리로 옮기는 칸 — (귀속표 이름, 자리 이름)
ATTR_FIELDS = [("sprite", "speaker"), ("cls", "layer"), ("kind", "kind"),
               ("scene", "scene"), ("how", "how"), ("who", "who")]


def load_attr():
    """(맵, norm(원문)) → 귀속표 행들. 이을 때 양쪽 다 norm으로 줄인다."""
    import gzip
    out = {}
    with gzip.open(DATA / "speaker-attr.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            a = json.loads(line)
            out.setdefault((a["map"], norm(a["k"])), []).append(a)
    return out


def load_verdicts():
    """통일·갈림 판정을 (norm 원문 → 판정)으로 편다."""
    unified = {norm(r["es"]): r["ko"] for r in read_jsonl(DATA / "unified-phrases.jsonl")}
    # 갈림: (norm 원문, 맵) → 이유. 갈래의 maps에 든 자리만 붙인다.
    div = {}
    for r in read_jsonl(DATA / "divergence-allowed.jsonl"):
        for branch in r["갈래"]:
            for m in branch.get("maps", ()):
                div[(norm(r["es"]), m)] = (branch["ko"], r["이유"])
    return unified, div


def map_sites(attr):
    """맵 절 — 자리와 값. 한 (맵, norm 원문)에 자리가 여럿이면 값은 공유 항목에 둔다."""
    sites, msgs = [], []
    stats = {"rows": 0, "sites": 0, "shared": 0, "no_attr": 0}
    unified, div = load_verdicts()
    used_unified = {}
    for mi, rows in read_maps():
        for seq, row in enumerate(rows):
            stats["rows"] += 1
            nk = norm(row["k"])
            hits = sorted(attr.get((mi, nk), ()), key=lambda a: (a["event"], a["page"], a["cmd"]))
            if hits:
                ids = [f"m{mi}.e{a['event']}.p{a['page']}.c{a['cmd']}" for a in hits]
                metas = hits
            else:
                # 귀속표가 좌표를 못 잡은 자리 — 원문 해시로 결정적 id를 세운다.
                stats["no_attr"] += 1
                ids, metas = [f"m{mi}.k{h8(nk)}"], [None]
            stats["sites"] += len(ids)

            # 값: 갈림 판정이 있으면 자체 값 + 왜, 통일 목록과 같으면 참조, 아니면 자체 값.
            val, why = row["v"], None
            dv = div.get((nk, mi))
            if dv and dv[0] == row["v"]:
                why = dv[1]
            elif unified.get(nk) == row["v"]:
                slug = f"unified.{h8(nk)}"
                used_unified[slug] = row["v"]
                val = {"ref": slug}

            if len(ids) > 1:
                stats["shared"] += 1
                shared = f"m{mi}.s{seq}"
                msgs.append(_msg(shared, val, why))
                body = [_msg(i, {"ref": shared}, None) for i in ids]
            else:
                body = [_msg(ids[0], val, why)]
            msgs.extend(body)

            for sid, meta in zip(ids, metas):
                s = {"id": sid, "src": row["k"], "apply": "map"}
                if meta:
                    for src_f, dst_f in ATTR_FIELDS:
                        v = meta.get(src_f)
                        if v not in (None, "", []):
                            s[dst_f] = v
                sites.append(s)
    return sites, msgs, used_unified, stats


def _msg(mid, val, why):
    m = {"id": mid, "val": val}
    if why:
        m["why"] = why
    return m


def loc_sites():
    """좌표 열쇠(apply=krloc) — 값과 왜를 그대로 옮긴다."""
    sites, msgs = [], []
    for r in read_jsonl(KO / "00-maps.loc.jsonl"):
        sid = f"loc.m{r['map']}.e{r['event']}.c{r['cmd']}"
        sites.append({"id": sid, "src": r["k"], "apply": "krloc"})
        msgs.append(_msg(sid, r["v"], r.get("왜")))
    return sites, msgs


def ui_sites():
    """런타임 치환표(apply=gsub) — UI Text KR. 값 정본은 data/uitext.jsonl이고
    인명 행({"name": ...})의 표기는 names.json에서 읽는다(생성기 uitext.py와 같은 규칙)."""
    names = json.loads((ROOT / "names.json").read_text(encoding="utf-8"))["names"]
    sites, msgs = [], []
    for r in read_jsonl(DATA / "uitext.jsonl"):
        if "note" in r:
            continue
        if "name" in r:
            src, val = f"\\b{r['name']}\\b", names[r["name"]]
        elif "re" in r:
            src, val = f"\\b{r['re']}\\b", r["ko"]
        else:
            src, val = r["es"], r["ko"]
        sid = f"ui.g{h8(src)}"
        sites.append({"id": sid, "src": src, "apply": "gsub"})
        msgs.append(_msg(sid, val, None))
    return sites, msgs


def section_sites():
    """리스트 절(apply=index)과 해시 절(apply=global)."""
    sites, msgs = [], []
    for sec in LIST_SECS:
        for r in read_jsonl(ko_file(sec)):
            sid = f"s{sec}.i{r['i']}"
            s = {"id": sid, "apply": "index"}
            if "es" in r:
                s["src"] = r["es"]
            sites.append(s)
            msgs.append(_msg(sid, r["v"], None))
    for sec in HASH_SECS:
        for r in read_jsonl(ko_file(sec)):
            sid = f"s{sec}.k{h8(r['k'])}"
            sites.append({"id": sid, "src": r["k"], "apply": "global"})
            msgs.append(_msg(sid, r["v"], None))
    return sites, msgs


def write_yaml(path, obj):
    path.write_text(
        yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=10**6),
        encoding="utf-8",
    )


def main():
    attr = load_attr()
    msites, mmsgs, used_unified, stats = map_sites(attr)
    lsites, lmsgs = loc_sites()
    ssites, smsgs = section_sites()
    usites, umsgs = ui_sites()

    sites = msites + lsites + ssites + usites
    ids = [s["id"] for s in sites]
    assert len(set(ids)) == len(ids), "자리 id가 겹친다"

    msgs = ([{"id": k, "val": v} for k, v in sorted(used_unified.items())]
            + mmsgs + lmsgs + smsgs + umsgs)
    mids = [m["id"] for m in msgs]
    assert len(set(mids)) == len(mids), "값 id가 겹친다"

    # 사람 수정은 재생성을 지우지 않는다 — 마지막에 얹는다(설계 「이행 1단계」 overrides 절).
    ovr = read_overrides()
    sites, msgs = apply_overrides(sites, msgs, ovr)

    dump_jsonl(OUT / "sites.jsonl", sites)
    dump_jsonl(OUT / "messages.jsonl", msgs)

    # groups — 페르소나 표 + 스프라이트 묶음. 기계 이관이라 격 판정을 새로 만들지 않는다.
    sprite_groups = json.loads((ROOT / "sprite-groups.json").read_text(encoding="utf-8"))
    write_yaml(OUT / "groups.yaml", {
        "_source": ["translate/persona-table.jsonl", "translate/sprite-groups.json"],
        "groups": [
            {"group": r["sprite"], "match": {"speaker": r["sprite"]},
             "rows": r["rows"], "bucket": r["버킷"], "persona": r["페르소나"],
             "appearance": r["외형"], "basis": r["근거"], "note": r["비고"],
             "source": "translate/persona-table.jsonl"}
            for r in read_jsonl(ROOT / "persona-table.jsonl")
        ],
        "sprite_groups": sprite_groups,
    })

    # terms — term-pairs만 기계 이관. 코드 하드코딩(CORE_TERMS·UiText TABLE) 이관은
    # 설계가 「설계 뒤」로 미뤄 둔 자리라 여기 담지 않는다.
    write_yaml(OUT / "terms.yaml", {
        "_source": ["translate/term-pairs.jsonl"],
        "terms": [{"term": f"t-{h8(r['es'])}", "ko": r["ko"], "src": r["es"],
                   "source": "translate/term-pairs.jsonl"}
                  for r in read_jsonl(ROOT / "term-pairs.jsonl")],
    })

    # axes — 설계 3절 그대로. layout은 정본 값이 아니라 그릇의 뼈대다(절 종류·맵 수):
    # 값이 하나도 없는 절 셋과 빈 맵 33개가 자리 목록만으로는 안 살아나서 여기 적는다.
    write_yaml(OUT / "axes.yaml", {
        "axes": {"speaker": {"from": "sites.speaker"}, "to": {"from": "sites.to"},
                 "kind": {"values": ["say", "narration", "choice", "system", "ui"]}},
        "precedence": ["site", "speaker", "to", "kind"],
        "layout": {
            "maps": len(read_maps()),
            "sections": {0: "maps", **{s: "list" for s in LIST_SECS},
                         **{s: "hash" for s in HASH_SECS},
                         **{s: "empty" for s in EMPTY_SECS}},
        },
    })

    print(f"sites {len(sites):,} · messages {len(msgs):,}")
    print(f"맵 절: 정본 {stats['rows']:,}줄 → 자리 {stats['sites']:,}개 "
          f"(값 공유 묶음 {stats['shared']:,} · 귀속표 밖 {stats['no_attr']:,})")
    print(f"통일 참조 {len(used_unified):,}건 · overrides {len(ovr):,}줄")


if __name__ == "__main__":
    main()
