# /// script
# requires-python = ">=3.12"
# ///
"""검수 판정을 번역 정본에 반영한다 — 선별분은 판정대로, 나머지는 새 번역으로.

    uv run translate/apply_verdicts.py <out-dir>          # 미리보기(쓰지 않는다)
    uv run translate/apply_verdicts.py <out-dir> --write  # 정본에 반영

판정 원장은 `<out-dir>`의 짝인 `verdicts-<out이름>.jsonl`. 자리마다 최종 한 줄이다.

반영 규칙 — **판정이 없으면 새 번역을 채택한다**(유지자 판정 2026-08-06: 선별 화면에서
고르지 않은 행은 새 번역으로 간다). 그 위에 안전판 셋:

- 기계 검증 반려(`ok:false`) 행은 현행을 지킨다. 판정으로 명시하면 그것이 이긴다.
- 승인 줄은 현행을 지킨다 — 이미 판정이 끝난 자리라 자동 채택 대상이 아니다.
- 「보류」와 「현행」은 손대지 않는다.

같은 (맵, 접힌 원문)이 여러 자리에 서면 정본은 한 줄뿐이다 — 그 열쇠에 판정이 둘 이상
엇갈리면 반영하지 않고 목록으로 보여 준다.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from batch_pages import BATCH, MAPS, fold  # noqa: E402

CHUNKS = BATCH / "page-chunks.jsonl"


def approved_ids():
    """이미 판정이 끝난 줄 — 자동 채택에서 뺀다."""
    out = set()
    if CHUNKS.exists():
        for line in CHUNKS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                for r in json.loads(line)["rows"]:
                    if r.get("approved"):
                        out.add(r["id"])
    return out


def verdicts(path):
    """행 판정만 추린다 — 이벤트 승인 줄(`event` 열쇠)은 환류 몫이라 여기서 안 쓴다."""
    out = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("id"):
                    out[r["id"]] = r
    return out


def decide(row, v, approved):
    """(새 번역문 또는 None, 사유) — None이면 현행 유지."""
    if v:
        j = (v.get("판정") or "").strip()
        if j == "B새번역":
            return row.get("new"), "판정:새번역"
        if j == "직접":
            t = (v.get("텍스트") or "").strip()
            return (t, "판정:직접") if t else (None, "판정:직접(빈칸)")
        if j == "현행":
            return None, "판정:현행"
        if j == "보류":
            return None, "판정:보류"
        # 고르지 않은 자리 — 메모를 남겼으면 물음이 걸려 있는 것이니 현행을 지킨다.
        # 메모도 없으면 고른 것을 도로 끈 자리라 무판정과 같게 본다.
        if (v.get("메모") or "").strip():
            return None, "메모만(물음 걸림)"
    if row["id"] in approved:
        return None, "승인 줄"
    if not row.get("ok"):
        return None, "기계 반려"
    if not row.get("new"):
        return None, "새 번역 없음"
    return row["new"], "무판정→새번역"


APPROVED_EV = HERE / "data/approved-events.jsonl"


def done_events(d, vs):
    """판정이 끝난 이벤트 — 화면에 걸린 행이 전부 판정됐거나 이벤트째 승인된 것."""
    sys.path.insert(0, str(HERE))
    from review_page import collect  # 화면에 실제로 실리는 행과 같은 셈법을 쓴다

    ev_rows = {}
    for sc in collect(d):
        ev_rows.setdefault((sc["map"], int(sc["event"])), []).extend(
            r["id"] for r in sc["rows"])
    # 완료 표시는 장면(이벤트-페이지) 단위다. 이벤트가 끝났다고 보려면 화면에 선
    # 그 이벤트의 페이지가 모두 표시돼야 한다 — 7-0만 눌렀는데 7-1이 딸려가면 안 된다.
    marked = set()
    for r in _ledger_rows(d):
        e = r.get("event")
        if e and (r.get("판정") or "").strip() in ("완료", "승인"):
            m, _, rest = e.partition(":")
            ev, _, pg = rest.partition("-")
            marked.add((int(m), int(ev), pg))
    pages = {}
    for sc in collect(d):
        pages.setdefault((sc["map"], int(sc["event"])), set()).add(str(sc["page"]))

    def flagged(ev):
        got = {p for (m, e, p) in marked if (m, e) == ev}
        return "" in got or (pages.get(ev, set()) and pages[ev] <= got)

    return {ev for ev, ids in ev_rows.items()
            if flagged(ev) or all(i in vs for i in ids)}


def _ledger_rows(d):
    p = Path(d).parent / f"verdicts-{Path(d).name}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip()] if p.exists() else []


PROTECTED = HERE / "data/protected.jsonl"


def record_applied(evs):
    """반영이 끝난 이벤트를 승인 이벤트로 올리고 **보호로 고정한다**.

    유지자 판정 2026-08-06: 검수를 마친 이벤트는 승인일 뿐 아니라 고정이다 —
    다음 배치가 다시 건드리지 않게 보호 층(page 단위)에도 함께 올린다.
    """
    have = {(json.loads(l)["map"], json.loads(l)["event"])
            for l in APPROVED_EV.read_text(encoding="utf-8").splitlines() if l.strip()}
    new = [e for e in sorted(evs) if e not in have]
    with APPROVED_EV.open("a", encoding="utf-8") as f:
        for m, e in new:
            f.write(json.dumps({"map": m, "event": e, "src": "검수 반영"},
                               ensure_ascii=False) + "\n")
    lock_pages(new)
    return new


def lock_pages(evs):
    """이벤트의 모든 페이지를 보호에 올린다 — 사정권에서 아예 뺀다."""
    pages = set()
    for line in CHUNKS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            c = json.loads(line)
            if (c["map"], c["event"]) in set(evs):
                pages.add((c["map"], c["event"], c["page"]))
    have = {(r["map"], r["event"], r["page"]) for r in
            (json.loads(l) for l in PROTECTED.read_text(encoding="utf-8").splitlines()
             if l.strip())}
    with PROTECTED.open("a", encoding="utf-8") as f:
        for m, e, p in sorted(pages - have):
            f.write(json.dumps({"map": m, "event": e, "page": p},
                               ensure_ascii=False) + "\n")
    return pages - have


MEND_MEMO = "개행 기계 수선 — 확인 바람"
APPLIED_ROWS = BATCH / "applied-rows.jsonl"


def mend_rows(d, vs):
    """기계 수선 행 중 **그 이벤트의 유일한 선별이 아닌 것** — 먼저 반영하고 화면에서 지운다.

    유일한 선별이면 남긴다. 그 행을 지우면 이벤트가 목록에서 통째로 사라져,
    장면을 열어 볼 길이 막힌다(유지자 판정 2026-08-06).
    """
    sys.path.insert(0, str(HERE))
    from review_page import collect

    out = set()
    for sc in collect(d):
        ids = [r["id"] for r in sc["rows"]]
        mend = {i for i in ids if (vs.get(i) or {}).get("메모") == MEND_MEMO}
        if len(mend) < len(ids):      # 사람이 볼 행이 남아야 이벤트가 목록에 선다
            out |= mend
    return out


def record_rows(ids):
    have = {json.loads(l)["id"] for l in APPLIED_ROWS.read_text(encoding="utf-8").splitlines()
            if l.strip()} if APPLIED_ROWS.exists() else set()
    new = sorted(ids - have)
    with APPLIED_ROWS.open("a", encoding="utf-8") as f:
        for i in new:
            f.write(json.dumps({"id": i, "src": "개행 기계 수선"}, ensure_ascii=False) + "\n")
    return new


def run(out_dir, write=False, events_only=False):
    d = Path(out_dir)
    ledger = d.parent / f"verdicts-{d.name}.jsonl"
    vs, appr = verdicts(ledger), approved_ids()
    keep = done_events(d, vs) if events_only else None
    rows_ok = mend_rows(d, vs) if events_only else set()
    if events_only:
        print(f"판정 끝난 이벤트 {len(keep)}개 · 먼저 반영할 수선 행 {len(rows_ok)}개")

    # 접힌 복제 자리(covers) — 같은 화자의 같은 원문은 한 번만 번역되고, 판정은
    # 접힌 전 맵에 함께 반영된다(batch_pages.dedupe가 대표 행에 맵 목록을 남긴다).
    covers = {}
    stem = d.name.replace("-fresh", "")
    chunks_name = {"page-out": "page-chunks", "page-out-pilot": "pilot-chunks",
                   "npc-out": "npc-chunks", "npc-out-pilot": "npc-pilot-chunks"}.get(stem)
    cf = d.parent / (chunks_name + ".jsonl") if chunks_name else None
    if cf and cf.exists():
        for line in cf.read_text(encoding="utf-8").splitlines():
            if line.strip():
                for r in json.loads(line)["rows"]:
                    if r.get("covers"):
                        covers[r["id"]] = r["covers"]

    plan, why, olds = {}, {}, {}
    clash, stat = [], {}
    for fp in sorted(d.glob("*.jsonl")):
        if fp.name.startswith("screen"):     # 산출 파일 이름은 p…(주연)·t…(트레이너)
            continue
        for line in fp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            m, e = (int(x) for x in r["id"].split(":")[:2])
            if keep is not None and (m, e) not in keep and r["id"] not in rows_ok:
                continue
            new, tag = decide(r, vs.get(r["id"]), appr)
            stat[tag] = stat.get(tag, 0) + 1
            if new is None:
                continue
            key = (int(r["id"].split(":")[0]), fold(r["es"]))
            if key in plan and plan[key] != new:
                clash.append((key, why[key], plan[key], tag, new))
                continue
            plan[key], why[key] = new, tag
            olds[key] = r.get("old") or ""
            for m2 in covers.get(r["id"], []):    # 접힌 복제 맵에도 같은 판이 간다
                k2 = (m2, key[1])
                if plan.get(k2, new) != new:
                    clash.append((k2, why.get(k2), plan[k2], tag + "(covers)", new))
                    continue
                plan[k2], why[k2] = new, tag + "(covers)"

    for tag, n in sorted(stat.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {n}행")
    print(f"판정 원장 {len(vs)}건 · 반영 대상 {len(plan)}자리 · 열쇠 충돌 {len(clash)}")
    for key, t1, v1, t2, v2 in clash[:10]:
        print(f"  충돌 맵{key[0]} 「{key[1][:30]}」: {t1}={v1[:25]} / {t2}={v2[:25]}")

    # 통일 전파 — 같은 원문이 다른 맵에서 **같은 현행**으로 서 있으면 함께 간다.
    # 통일 원문은 한 자리만 번역되므로(batch_pages.dedupe) 여기서 안 퍼지면 대표
    # 자리만 새 판이 되어 통일이 도로 갈라진다(verify check_unified가 문다).
    # 값 일치 조건이 안전판이다 — 의도된 갈림(현행이 다른 자리)은 절대 안 건드린다.
    spread = {}
    for key, new in plan.items():
        es, old = key[1], olds.get(key, "")
        if not old or new == old:
            continue
        if es in spread and spread[es] != (old, new):
            spread.pop(es)                    # 맵마다 딴 판정 — 퍼뜨리지 않는다
            continue
        spread[es] = (old, new)

    if not write:
        print("미리보기만 — 반영하려면 --write")
        return

    out, hit, sp_hit, cur = [], 0, 0, None
    for line in MAPS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            out.append(line)
            continue
        r = json.loads(line)
        if "map" in r:
            cur = r["map"]
        else:
            kf = fold(r["k"])
            new = plan.get((cur, kf))
            if new and new != r["v"]:
                r["v"], hit = new, hit + 1
            elif not new and kf in spread and r["v"] == spread[kf][0]:
                r["v"], sp_hit = spread[kf][1], sp_hit + 1
        out.append(json.dumps(r, ensure_ascii=False))
    MAPS.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"정본 {MAPS.name}: {hit}행 고침 · 통일 전파 {sp_hit}행")
    if events_only and keep:
        print(f"승인 이벤트 등재: {len(record_applied(keep))}개 새로 올림")
    if events_only and rows_ok:
        print(f"수선 행 등재: {len(record_rows(rows_ok))}개 — 화면에서 빠진다")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        print(__doc__)
        sys.exit()
    run(a[0], write="--write" in sys.argv, events_only="--events" in sys.argv)
