# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Z-53 이행 1단계 — 0단계 정본 파일 다섯을 지금 출처에서 **기계로만** 만든다.

사람 판정은 하나도 넣지 않는다. 지금 값을 그대로 옮긴다. 출처(`translate/ko/`,
`translate/data/`)는 읽기만 한다.

산출: translate/stage0/{sites.jsonl,messages.jsonl,pages.jsonl,axes.yaml,layout.yaml}
되돌려 대조하는 쪽은 diff.py. voices.yaml·terms.yaml은 **사람 소유 정본**이라
gen이 만들지도 다시 쓰지도 않는다(2026-08-18 강등).

usage: uv run translate/stage0/gen.py
"""
import json
import re
import sys

import yaml

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA, EMPTY_SECS, HASH_SECS, KINDS, KO, LIST_SECS, OUT, PAGE_LAYERS, PAGE_SCENES, ROOT,
    apply_overrides, apply_page_overrides, dump_jsonl, h8, ko_file, norm, read_jsonl,
    read_maps, read_overrides,
)

# 귀속표에서 자리로 옮기는 칸 — (귀속표 이름, 자리 이름). 행 사실만 여기 있다.
# 층·장면은 페이지 단위 판정이라 자리에 안 싣는다(Z-53 설계 2절, 3단계에서 걷음) —
# 페이지 판정은 pages.jsonl이 정본이고 조회는 structure.row_layer·scene이 받는다.
ATTR_FIELDS = [("sprite", "speaker"), ("kind", "kind"), ("how", "how"), ("who", "who")]
# 귀속표에서 페이지로 올리는 칸 — (귀속표 이름, 페이지 이름, 등재 값 목록).
# 값 목록은 다수결 동점을 가르는 순서이기도 하다(앞선 값이 이긴다 — 재생성 결정성).
PAGE_ATTR = [("cls", "layer", PAGE_LAYERS), ("scene", "scene", PAGE_SCENES)]


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


def load_meta():
    """판정 메타 → 값에 찍을 state·by·sample. 원본 파일들은 주도권 이전까지 배치
    도구의 원천으로 남고, 여기서는 stage0 값에 유래를 함께 찍을 뿐이다.

    승인 줄은 (맵, 원문) 단위라 값 항목에, 승인 이벤트는 이벤트 단위라 자리별 항목에
    찍는다 — 공유 값이 승인 안 된 다른 자리로 새지 않게. 줄 승인이 이벤트 승인보다
    구체적이므로 먼저 찍힌 줄 승인을 이벤트 승인이 덮지 않는다.
    """
    al = {(r["map"], norm(r["es"])): r for r in read_jsonl(DATA / "approved-lines.jsonl")}
    ae = {(r["map"], r["event"]): r for r in read_jsonl(DATA / "approved-events.jsonl")}
    fk = {r["es"] for r in read_jsonl(DATA / "frozen-keys.jsonl")}
    # 행 단위 출처 목록(provenance.py build 산출) — 사람 낱건 이력의 누적.
    pv = {(r["map"], norm(r["es"])): r["by"]
          for r in read_jsonl(DATA / "provenance-lines.jsonl")} \
        if (DATA / "provenance-lines.jsonl").exists() else {}
    return al, ae, fk, pv


def map_sites(attr, al, ae, pv):
    """맵 절 — 자리와 값. 한 (맵, norm 원문)에 자리가 여럿이면 값은 공유 항목에 둔다."""
    sites, msgs = [], []
    pages = {}          # (맵, 이벤트, 페이지) → {페이지 칸: {값: 몇 행}}
    stats = {"rows": 0, "sites": 0, "shared": 0, "no_attr": 0, "line_ok": 0, "ev_ok": 0,
             "prov": 0}
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

            # 승인 줄 — (맵, 원문) 단위 판정이라 값 항목에 찍는다.
            line = al.get((mi, nk))
            if len(ids) > 1:
                stats["shared"] += 1
                shared = f"m{mi}.s{seq}"
                vm = _msg(shared, val, why)
                msgs.append(vm)
                body = [_msg(i, {"ref": shared}, None) for i in ids]
            else:
                body = [_msg(ids[0], val, why)]
                vm = body[0]
            if line:
                stats["line_ok"] += 1
                vm.update(state="reviewed", by=f"human/{line['src']}")
                if "본보기" in line:      # 명시만 옮긴다 — 없음(자동 선별)과 False(명시 제외)는 다르다
                    vm["sample"] = line["본보기"]
            elif (mi, nk) in pv:
                # 출처 목록 — 사람 낱건이 닿은 값. 승인 줄이 더 구체적이라 그쪽이 우선.
                stats["prov"] += 1
                vm.update(state="reviewed", by=pv[(mi, nk)])
            # 승인 이벤트 — 이벤트 단위 판정이라 자리별 항목에 찍는다(공유 값 누출 방지).
            # 줄 승인이 이미 찍힌 값 항목(단독 자리)은 그대로 둔다.
            for bm, meta in zip(body, metas):
                if meta and (mi, meta["event"]) in ae and "state" not in bm:
                    stats["ev_ok"] += 1
                    # src가 없는 행(노트만)은 파일 이름을 유래로 적는다.
                    tag = ae[(mi, meta["event"])].get("src", "approved-events")
                    bm.update(state="reviewed", by=f"human/{tag}")
            msgs.extend(body)

            for sid, meta in zip(ids, metas):
                s = {"id": sid, "src": row["k"], "apply": "map"}
                if meta:
                    for src_f, dst_f in ATTR_FIELDS:
                        v = meta.get(src_f)
                        if v not in (None, "", []):
                            s[dst_f] = v
                    p = pages.setdefault((mi, meta["event"], meta["page"]), {})
                    for src_f, dst_f, _ in PAGE_ATTR:
                        v = meta.get(src_f)
                        if v not in (None, "", []):
                            p.setdefault(dst_f, {})
                            p[dst_f][v] = p[dst_f].get(v, 0) + 1
                sites.append(s)
    return sites, msgs, used_unified, stats, fold_pages(pages)


def fold_pages(counts):
    """행 단위 귀속값을 페이지 한 줄로 접는다 — 다수결, 갈리면 `mixed`를 남긴다.

    귀속표는 행 단위인데 층·장면은 페이지 단위 판정이다(Z-53 설계 2절). 페이지 안에서
    값이 갈리는 자리가 실제로 있어(2026-08-18 실측: 층 21페이지 · 장면 0) 조용히 누르지
    않고 표시를 남긴다 — 사람 판정은 overrides가 그 위에 얹는다.
    """
    rows = []
    for (mi, ev, pg), c in sorted(counts.items()):
        row, mixed = {"id": f"m{mi}.e{ev}.p{pg}"}, False
        for _, f, order in PAGE_ATTR:
            if f not in c:
                continue
            mixed = mixed or len(c[f]) > 1
            rank = {v: i for i, v in enumerate(order)}
            row[f] = max(c[f], key=lambda v: (c[f][v], -rank.get(v, len(order))))
        if mixed:
            row["mixed"] = True
        row["by"] = "machine/gen"
        rows.append(row)
    return rows


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


def outside_sites():
    """번역 조회 밖 자리(apply=surgery) — 정본은 data/outside-sites.jsonl(생성기 outside_scan.py).

    tower는 값이 없어 원문을 그대로 값으로 둔다 — 미번역이 사실이라 집계에 그대로 보인다.
    surgery는 share/patch_intl.py가 소스에 심는 값을 옮긴 것이다.
    """
    sites, msgs = [], []
    for r in read_jsonl(DATA / "outside-sites.jsonl"):
        if r["kind"] == "tower":
            sid, val = f"tower.g{h8(r['src'])}", r["src"]
        else:
            sid, val = f"surg.g{h8(r['where'] + r['src'])}", r["ko"]
        sites.append({"id": sid, "src": r["src"], "apply": "surgery"})
        msgs.append(_msg(sid, val, None))
    return sites, msgs


MART_ADD = KO / "23-script-texts.add.jsonl"


def load_mart():
    """절23 추가분(상점 갈래) → (원문→{갈래: 값}, 차례 목록, 배정 목록, 갈래 목록).

    합성 열쇠라 base에 접히지 않는다(지침 text-pipeline 「접을 것과 남길 것」) — 값은
    base 줄의 선택자 트리로 들어가고, 줄 차례·상점 이름은 파일 모양이라 axes의 layout에
    남는다(빈 절 뼈대와 같은 자리).
    """
    if not MART_ADD.exists():
        return {}, [], [], []
    vals, steps, at, brs = {}, [], [], []
    for r in read_jsonl(MART_ADD):
        k = r["k"]
        if k.startswith("krmart:"):
            br, _, src = k[len("krmart:"):].partition("|")
            if br not in brs:
                brs.append(br)
            # 평문만 받는다 — diff의 역생성이 when 값을 resolve 없이 그대로 꺼낸다.
            assert isinstance(r["v"], str), f"갈래 값이 문자열이 아니다: {k!r}"
            vals.setdefault(src, {})[br] = r["v"]
            seen = [s for s in steps if s["src"] == src]
            if not seen:
                steps.append({"src": src, "차례": r["차례"]})
            else:
                assert seen[0]["차례"] == r["차례"], f"갈래마다 차례가 다르다: {src!r}"
        elif k.startswith("krmart-at:"):
            mi, ev = (int(x) for x in k[len("krmart-at:"):].split(":"))
            at.append({"map": mi, "event": ev, "갈래": r["v"], "상점": r["상점"]})
    return vals, steps, at, brs


def stamp_mart(sites, at):
    """갈래 배정을 (맵, 이벤트) 자리의 축 칸으로 편다 — 간선을 자리 쪽에 둔다.

    ⚠ `mart` 칸은 **그 자리가 속한 이벤트의 상점 화면 갈래**다(이벤트 속성). 그 줄을
    말하는 사람의 말투가 아니므로 줄 말투 배정에 쓰지 마라 — 점원이 아닌 자리에도
    같은 이벤트면 함께 찍힌다.
    """
    want = {(a["map"], a["event"]): a["갈래"] for a in at}
    n = 0
    for s in sites:
        m = re.match(r"^m(\d+)\.e(\d+)\.", s["id"])
        if m and (int(m.group(1)), int(m.group(2))) in want:
            s["mart"] = want[(int(m.group(1)), int(m.group(2)))]
            n += 1
    for pair in want:
        if not any(s.get("mart") and s["id"].startswith(f"m{pair[0]}.e{pair[1]}.") for s in sites):
            print(f"⚠ 상점 배정 자리 없음(좌표 드리프트?): 맵{pair[0]} 이벤트{pair[1]}")
    return n


def section_sites(fk, mart_vals):
    """리스트 절(apply=index)과 해시 절(apply=global). 동결 절23 키는 reviewed로 찍는다.

    절23의 상점 문구는 갈래별 값을 함께 들어 선택자 트리가 된다 — 기본 갈래(존대)가
    base 줄의 값 그대로이고 `when`이 추가분의 갈래다.
    """
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
            branches = mart_vals.get(r["k"]) if sec == 23 else None
            val = {"sel": "mart", "when": branches, "default": r["v"]} if branches else r["v"]
            m = _msg(sid, val, None)
            if sec == 23 and r["k"] in fk:
                m.update(state="reviewed", by="human/frozen-keys")
            msgs.append(m)
    return sites, msgs


def write_yaml(path, obj):
    path.write_text(
        yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=10**6),
        encoding="utf-8",
    )


def stamp_register_ok(sites):
    """register-ok(어긋남 아님 판정)를 자리 칸으로 편다 — 원천은 data/register-ok.jsonl
    (사람 직접 편집), 좌표 조건은 있는 칸만 맞춘다(이벤트·페이지 통째 꼴 허용).
    등재 뒤에는 gen을 다시 돌려야 소비자(register.py scan·materials)가 본다."""
    import re
    oks = read_jsonl(DATA / "register-ok.jsonl")
    if not oks:
        return 0, 0
    idre = re.compile(r"^m(\d+)\.e(\d+)\.p(\d+)\.c(\d+(?:\.\d+)?)$")
    hits = [0] * len(oks)
    stamped = 0
    for s in sites:
        m = idre.match(s["id"])
        if not m:
            continue
        c = m.group(4)
        row = {"map": int(m.group(1)), "event": int(m.group(2)), "page": int(m.group(3)),
               "cmd": float(c) if "." in c else int(c), "who": s.get("who")}
        for i, o in enumerate(oks):
            if all(o.get(f) in (None, row[f]) for f in ("map", "event", "page", "cmd", "who")):
                s["register_ok"] = o.get("이유", "")
                hits[i] += 1
                stamped += 1
                break
    for o, n in zip(oks, hits):
        if n == 0:
            print(f"⚠ register-ok 자리 없음(좌표 드리프트?): {json.dumps(o, ensure_ascii=False)[:120]}")
    return len(oks), stamped


def main():
    attr = load_attr()
    al, ae, fk, pv = load_meta()
    mart_vals, mart_steps, mart_at, mart_brs = load_mart()
    msites, mmsgs, used_unified, stats, pages = map_sites(attr, al, ae, pv)
    lsites, lmsgs = loc_sites()
    ssites, smsgs = section_sites(fk, mart_vals)
    usites, umsgs = ui_sites()
    osites, omsgs = outside_sites()

    sites = msites + lsites + ssites + usites + osites
    ids = [s["id"] for s in sites]
    assert len(set(ids)) == len(ids), "자리 id가 겹친다"

    msgs = ([{"id": k, "val": v} for k, v in sorted(used_unified.items())]
            + mmsgs + lmsgs + smsgs + umsgs + omsgs)
    mids = [m["id"] for m in msgs]
    assert len(set(mids)) == len(mids), "값 id가 겹친다"

    n_ok, n_ok_sites = stamp_register_ok(sites)
    n_mart_sites = stamp_mart(sites, mart_at)

    # 사람 수정은 재생성을 지우지 않는다 — 마지막에 얹는다(설계 「이행 1단계」 overrides 절).
    ovr = read_overrides()
    sites, msgs = apply_overrides(sites, msgs, ovr)
    pages = apply_page_overrides(pages, ovr)

    dump_jsonl(OUT / "sites.jsonl", sites)
    dump_jsonl(OUT / "messages.jsonl", msgs)
    dump_jsonl(OUT / "pages.jsonl", pages)

    # groups.yaml(페르소나·스프라이트 묶음)·voices.yaml·terms.yaml은 사람 소유
    # 정본이라 gen이 쓰지 않는다(2026-08-18 강등 — 사람 소유 YAML을 기계가 다시
    # 쓰면 주석이 죽는다).

    # axes — 축 등재와 우선순위만. `values`가 선 축은 gate 검사 8이 `from`의 실물값을
    # 여기 견준다(등재 밖 값이면 FAIL).
    write_yaml(OUT / "axes.yaml", {
        "axes": {"speaker": {"from": "sites.speaker"}, "to": {"from": "sites.to"},
                 "kind": {"values": KINDS, "from": "sites.kind"},
                 "mart": {"values": mart_brs, "from": "sites.mart"},
                 "layer": {"values": PAGE_LAYERS, "from": "pages.layer"},
                 "scene": {"values": PAGE_SCENES, "from": "pages.scene"}},
        "precedence": ["site", "speaker", "to", "kind"],
    })

    # layout — 축이 아니라 그릇의 뼈대다(절 종류·맵 수): 값이 하나도 없는 절 셋과
    # 빈 맵 33개가 자리 목록만으로는 안 살아나서 여기 적는다. 소비자는 diff의 역생성.
    write_yaml(OUT / "layout.yaml", {
        "maps": len(read_maps()),
        "sections": {0: "maps", **{s: "list" for s in LIST_SECS},
                     **{s: "hash" for s in HASH_SECS},
                     **{s: "empty" for s in EMPTY_SECS}},
        # 절23 추가분의 모양 — 줄 차례와 상점 이름은 값이 아니라 파일 뼈대다.
        "mart": {"steps": mart_steps,
                 "at": [{k: v for k, v in a.items() if k != "갈래"} for a in mart_at]},
    })

    n_mixed = sum(1 for p in pages if p.get("mixed"))
    print(f"sites {len(sites):,} · messages {len(msgs):,} · pages {len(pages):,}"
          f" (페이지 안에서 값이 갈린 곳 {n_mixed})")
    print(f"맵 절: 정본 {stats['rows']:,}줄 → 자리 {stats['sites']:,}개 "
          f"(값 공유 묶음 {stats['shared']:,} · 귀속표 밖 {stats['no_attr']:,})")
    print(f"통일 참조 {len(used_unified):,}건 · overrides {len(ovr):,}줄")
    print(f"절23 추가분: 갈래 {mart_brs} × {len(mart_steps)}줄 · 배정 {len(mart_at)}곳"
          f"(자리 {n_mart_sites}개에 축 칸)")
    n_frozen = sum(1 for m in smsgs if m.get("by") == "human/frozen-keys")
    print(f"판정 메타: 승인 줄 {stats['line_ok']:,}(원본 {len(al):,}) · "
          f"승인 이벤트 자리 {stats['ev_ok']:,} · 동결 {n_frozen}(원본 {len(fk)}) · "
          f"출처 목록 {stats['prov']:,}(원본 {len(pv):,}) · "
          f"register-ok 자리 {n_ok_sites}(원본 {n_ok})")


if __name__ == "__main__":
    main()
