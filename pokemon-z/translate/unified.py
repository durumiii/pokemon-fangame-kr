# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""통일 정형구 목록 — 여러 맵에 복제된 원문의 통일판을 **원문 키로** 자체 저장한다.

정본(00-maps.jsonl)은 게임 판이 바뀌면 다시 뽑히고, 실수로 한 자리가 고쳐질 수도
있다. 우리가 판정한 통일판은 좌표가 아니라 원문에 묶어 여기 남는다 — 정본이 어떤
모양이 되든 이 목록에서 되살릴 수 있다(고유명의 canon/names.jsonl과 같은 격).

목록 둘을 다룬다:
- translate/data/unified-phrases.jsonl  {"es", "ko", "맵수", "src"} — 전판 통일.
- translate/data/divergence-allowed.jsonl {"es", "이유", "갈래": [{"ko","maps","sprites"}]}
  — 의도된 갈림. **갈래별 값까지 자체 저장**한다(유지자 방침 2026-08-12: 갈랐어도
  갈래 단위로는 하나로 관리·복원 가능해야 한다).

    uv run translate/unified.py check              # 두 목록 대 정본 대조 (verify에도 실림)
    uv run translate/unified.py restore [--write]  # 정본의 어긋난 자리를 목록 값으로 복원
    uv run translate/unified.py sync [--write]     # 의도적 변경·새 통일·갈래 재배정을 목록에 반영

restore와 sync는 방향이 반대다 — 실수로 갈렸으면 restore(목록이 이긴다),
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


def div_ledger():
    if not ALLOWED.exists():
        return {}
    return {r["es"]: r for r in
            (json.loads(l) for l in ALLOWED.read_text(encoding="utf-8").splitlines() if l.strip())}


def div_expected(div):
    """갈림 허용 목록 → es별 {맵: 기대값}."""
    return {es: {m: b["ko"] for b in r.get("갈래", []) for m in b["maps"]}
            for es, r in div.items()}


_ATTR_CACHE = None


def _sprites(m, es):
    """(맵, 원문)의 스프라이트들 — 갈래 기록용(사람이 갈래를 읽을 때의 좌표)."""
    global _ATTR_CACHE
    if _ATTR_CACHE is None:
        import gzip
        _ATTR_CACHE = {}
        p = HERE / "data" / "speaker-attr.jsonl.gz"
        if p.exists():
            with gzip.open(p, "rt", encoding="utf-8") as f:
                for line in f:
                    r = json.loads(line)
                    _ATTR_CACHE.setdefault((r["map"], fold(r["k"])), set()).add(
                        r.get("sprite") or "?")
    return _ATTR_CACHE.get((m, es), set())


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
    """(목록과 어긋난 es 목록, 정본에 없는 es 목록)을 돌려준다."""
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
                print(f"어긋남 {es[:46]!r}\n    목록: {e['ko'][:60]!r}\n    정본: {vals[0][:60]!r}"
                      + (f" 외 {len(vals)-1}판" if len(vals) > 1 else ""))
    dd = 0
    exp = div_expected(div_ledger())
    grp2 = {k: dict(g) for k, g in ((k, {m: v for m, v in g}) for k, g in grp.items())}
    for es, mp in exp.items():
        cur = grp2.get(es, {})
        for m, want in mp.items():
            if m in cur and cur[m] != want:
                dd += 1
                if not quiet:
                    print(f"갈림 어긋남 {es[:40]!r} 맵{m}: {cur[m][:40]!r} ≠ {want[:40]!r}")
        for m in set(cur) - set(mp):
            dd += 1
            if not quiet:
                print(f"갈림 미배정 {es[:40]!r} 맵{m}: {cur[m][:40]!r}")
    if not quiet:
        print(f"통일 목록 {len(led)}건(어긋남 {len(drift)} · 사라짐 {len(gone)}) · 갈림 허용 목록 어긋남·미배정 {dd}")
    return drift, gone


def put_lines(edits):
    """0단계 정본에 앉히고 ko를 역생성한다 — 창구는 stage0/edit.py 하나다."""
    sys.path.insert(0, str(HERE / "stage0"))
    from edit import put_lines as _put
    return _put(edits)


def restore(write=False):
    led = ledger()
    exp = div_expected(div_ledger())
    edits, hit, cur = [], 0, None
    for ln, line in enumerate(MAPS.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        if "map" in r:
            cur = r["map"]
            continue
        kf = fold(r["k"])
        e = led.get(kf)
        want = e["ko"] if e else exp.get(kf, {}).get(cur)
        if want and r["v"] != want:
            hit += 1
            print(f"맵{cur} {r['v'][:40]!r} → {want[:40]!r}")
            edits.append((MAPS.name, ln, want))
    if write:
        err = put_lines(edits)
        if err:
            print("멈춤 —", err)
            return
    print(f"복원 {'반영' if write else '대상'} {hit}행" + ("" if write else " — 반영하려면 --write"))


def sync(write=False):
    """정본의 현 상태를 목록에 반영 — 값이 바뀐 것은 갱신, 새 통일은 등재, 사라진 것은 삭제.

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
    # 갈림 허용 목록 — 갈래(값·맵·스프라이트)를 정본 현 상태로 재배정. es·이유는 보존한다.
    div, dchg = div_ledger(), 0
    for es, r in div.items():
        g = grp.get(es, [])
        buckets = {}
        for m, v in sorted(g):
            buckets.setdefault(v, []).append(m)
        new = [{"ko": v, "maps": ms, "sprites": sorted({s for m in ms for s in _sprites(m, es)})}
               for v, ms in sorted(buckets.items(), key=lambda x: -len(x[1]))]
        old = r.get("갈래", [])
        if [(b["ko"], b["maps"]) for b in new] != [(b["ko"], b["maps"]) for b in old]:
            dchg += 1
            print(f"갈래 재배정 {es[:44]!r}: {len(old)}→{len(new)}갈래")
            r["갈래"] = new
    if write:
        rows = sorted(led.values(), key=lambda r: -r.get("맵수", 0))
        LEDGER.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                          encoding="utf-8")
        ALLOWED.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n"
                                   for r in div.values()), encoding="utf-8")
    print(f"통일 갱신 {upd} · 등재 {add} · 삭제 {drop} · 갈래 재배정 {dchg}"
          + ("" if write else " — 반영하려면 --write"))


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
