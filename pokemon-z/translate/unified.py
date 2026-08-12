# /// script
# requires-python = ">=3.12"
# ///
"""통일 정형구 원장 — 여러 맵에 복제된 원문의 통일판을 **원문 키로** 자체 저장한다.

정본(00-maps.jsonl)은 게임 판이 바뀌면 다시 뽑히고, 실수로 한 자리가 고쳐질 수도
있다. 우리가 판정한 통일판은 좌표가 아니라 원문에 묶어 여기 남는다 — 정본이 어떤
모양이 되든 원장에서 되살릴 수 있다(고유명의 canon/names.jsonl과 같은 격).

원장: translate/data/unified-phrases.jsonl  {"es": 접은 원문, "ko": 통일판, "맵수", "src"}
의도된 갈림은 data/divergence-allowed.jsonl — 그쪽 원문은 이 원장에 안 올린다.

    uv run translate/unified.py check              # 원장 대 정본 대조 (verify에도 실림)
    uv run translate/unified.py restore [--write]  # 정본의 어긋난 자리를 원장 값으로 복원
    uv run translate/unified.py sync [--write]     # 의도적 변경·새 통일을 원장에 반영

restore와 sync는 방향이 반대다 — 실수로 갈렸으면 restore(원장이 이긴다),
판정으로 바꿨으면 sync(정본이 이긴다). 어느 쪽인지는 사람이 정한다.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
MAPS = HERE / "ko" / "00-maps.jsonl"
LEDGER = HERE / "data" / "unified-phrases.jsonl"
ALLOWED = HERE / "data" / "divergence-allowed.jsonl"


def fold(s):
    return re.sub(r"\s+", " ", s or "").strip()


def ledger():
    if not LEDGER.exists():
        return {}
    return {r["es"]: r for r in
            (json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip())}


def canon_groups():
    """정본에서 fold(원문) → {맵: [값들]}."""
    out, cur = {}, None
    for line in MAPS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "map" in r:
            cur = r["map"]
            continue
        out.setdefault(fold(r["k"]), []).append((cur, r["v"]))
    return out


def check(quiet=False):
    """(원장과 어긋난 es 목록, 정본에 없는 es 목록)을 돌려준다."""
    led, grp = ledger(), canon_groups()
    drift, gone = [], []
    for es, e in led.items():
        g = grp.get(es)
        if not g:
            gone.append(es)
            continue
        if {v for _, v in g} != {e["ko"]}:
            drift.append(es)
            if not quiet:
                vals = sorted({v for _, v in g} - {e["ko"]})
                print(f"어긋남 {es[:46]!r}\n    원장: {e['ko'][:60]!r}\n    정본: {vals[0][:60]!r}"
                      + (f" 외 {len(vals)-1}판" if len(vals) > 1 else ""))
    if not quiet:
        print(f"원장 {len(led)}건 · 어긋남 {len(drift)} · 정본에서 사라짐 {len(gone)}")
    return drift, gone


def restore(write=False):
    led = ledger()
    out, hit, cur = [], 0, None
    for line in MAPS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            out.append(line)
            continue
        r = json.loads(line)
        if "map" in r:
            cur = r["map"]
        else:
            e = led.get(fold(r["k"]))
            if e and r["v"] != e["ko"]:
                hit += 1
                print(f"맵{cur} {r['v'][:40]!r} → {e['ko'][:40]!r}")
                if write:
                    r["v"] = e["ko"]
        out.append(json.dumps(r, ensure_ascii=False))
    if write:
        MAPS.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"복원 {'반영' if write else '대상'} {hit}행" + ("" if write else " — 반영하려면 --write"))


def sync(write=False):
    """정본의 현 상태를 원장에 반영 — 값이 바뀐 것은 갱신, 새 통일은 등재, 사라진 것은 삭제.

    갈려 있는 원문은 통일이 아니므로 여기서 등재하지 않는다(verify가 따로 문다).
    """
    led, grp = ledger(), canon_groups()
    allowed = {json.loads(l)["es"] for l in ALLOWED.read_text(encoding="utf-8").splitlines()
               if l.strip()} if ALLOWED.exists() else set()
    upd = add = drop = 0
    for es, g in grp.items():
        maps, vals = {m for m, _ in g}, {v for _, v in g}
        if len(maps) <= 1 or len(vals) != 1 or es in allowed:
            continue
        ko = next(iter(vals))
        if es in led:
            if led[es]["ko"] != ko:
                print(f"갱신 {es[:40]!r}: {led[es]['ko'][:30]!r} → {ko[:30]!r}")
                led[es]["ko"] = ko
                upd += 1
            led[es]["맵수"] = len(maps)
        else:
            print(f"등재 {es[:40]!r} → {ko[:40]!r} ({len(maps)}맵)")
            led[es] = {"es": es, "ko": ko, "맵수": len(maps), "src": "sync"}
            add += 1
    for es in list(led):
        if es not in grp:
            print(f"삭제 {es[:50]!r} — 정본에서 사라짐")
            del led[es]
            drop += 1
    if write:
        rows = sorted(led.values(), key=lambda r: -r.get("맵수", 0))
        LEDGER.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                          encoding="utf-8")
    print(f"갱신 {upd} · 등재 {add} · 삭제 {drop}" + ("" if write else " — 반영하려면 --write"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    w = "--write" in sys.argv
    if cmd == "check":
        check()
    elif cmd == "restore":
        restore(w)
    elif cmd == "sync":
        sync(w)
    else:
        print(__doc__)
