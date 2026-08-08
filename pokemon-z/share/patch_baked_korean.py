# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Scripts.rxdata에 박힌 한국어 문구 수술 (Z-24).

번역표를 안 거치고 스크립트 소스에 직접 박힌 한국어 가운데 유지자가 승인한
치환표(`baked-korean-fixes.jsonl`: 절·줄·옛 문구·새 문구·근거)를 반영한다.
치환은 **절 이름 + 줄 번호 + 옛 문구 일치**로만 한다 — 그 줄에 옛 문구가 없으면
건너뛰고 보고한다(새 문구가 이미 있으면 기적용). 추측 치환은 없다.

멱등: 다시 돌리면 전부 기적용으로 떨어진다.
검증: 수술 뒤 백업(.pre-baked.bak)과 대조해 의도한 절·줄 밖이 안 바뀌었는지 본다
(`--verify`가 그 대조까지 한 번에 한다).

usage: uv run patch_baked_korean.py [--verify] [대상 Scripts.rxdata ...]
  무인자면 보관소 기반판 + 게임 설치본 둘 다.
"""
import json
import os
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from datread import load  # noqa: E402
from fanlib import rubywrite  # noqa: E402

FIXES = HERE / "baked-korean-fixes.jsonl"
DEFAULT_TARGETS = [
    Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/Scripts.rxdata"),
    Path("/mnt/d/Game/Pokemon Z/V2.18/Data/Scripts.rxdata"),
]


def read_fixes() -> list[dict]:
    return [json.loads(l) for l in FIXES.read_text(encoding="utf-8").splitlines() if l.strip()]


def patch_file(path: Path, fixes: list[dict]) -> bool:
    secs = load(open(path, "rb"))
    sources = {}                               # 절 이름 → (섹션, 줄 목록) — 같은 이름은 첫 절
    for sec in secs:
        name = bytes(sec[1]).decode("utf-8", "replace")
        sources.setdefault(name, sec)

    applied, skipped, missed = [], [], []
    dirty = {}                                 # id(sec) → 줄 목록 (한 절에 여러 치환)
    for f in fixes:
        sec = sources.get(f["sec"])
        if sec is None:
            missed.append(f"{f['sec']}:{f['line']} — 절이 없다")
            continue
        key = id(sec)
        if key not in dirty:
            dirty[key] = (sec, zlib.decompress(bytes(sec[2])).decode("utf-8").split("\n"))
        _, lines = dirty[key]
        i = f["line"] - 1
        if i >= len(lines):
            missed.append(f"{f['sec']}:{f['line']} — 줄이 없다({len(lines)}줄)")
        elif f["old"] in lines[i]:
            lines[i] = lines[i].replace(f["old"], f["new"])
            applied.append(f"{f['sec']}:{f['line']}")
        elif f["new"] in lines[i]:
            skipped.append(f"{f['sec']}:{f['line']}")
        else:
            missed.append(f"{f['sec']}:{f['line']} — 옛 문구가 그 줄에 없다: {lines[i].strip()[:60]}")

    if applied:
        for sec, lines in dirty.values():
            sec[2] = zlib.compress("\n".join(lines).encode("utf-8"))
        bak = path.with_suffix(".rxdata.pre-baked.bak")
        if not bak.exists():
            bak.write_bytes(path.read_bytes())
        tmp = path.with_suffix(".rxdata.baked-tmp")
        with open(tmp, "wb") as fd:            # 옆에 쓰고 갈아 끼운다 — 하드링크를 끊는다
            rubywrite.dump(fd, secs)
        os.replace(tmp, path)

    print(f"{path}: 적용 {len(applied)} · 기적용 {len(skipped)} · 불일치 {len(missed)}")
    for m in missed:
        print(f"  ⚠ {m}")
    return not missed


def verify(path: Path, fixes: list[dict]) -> bool:
    """백업 대 현재 — 바뀐 줄이 치환표의 절·줄과 정확히 일치하는지."""
    bak = path.with_suffix(".rxdata.pre-baked.bak")
    if not bak.exists():
        print(f"{path}: 백업이 없어 대조 불가")
        return False
    want = {(f["sec"], f["line"]) for f in fixes}
    got = set()
    old_secs = {bytes(s[1]).decode("utf-8", "replace"): s for s in load(open(bak, "rb"))}
    for sec in load(open(path, "rb")):
        name = bytes(sec[1]).decode("utf-8", "replace")
        old = old_secs.get(name)
        if old is None or bytes(old[2]) == bytes(sec[2]):
            continue
        a = zlib.decompress(bytes(old[2])).decode("utf-8").split("\n")
        b = zlib.decompress(bytes(sec[2])).decode("utf-8").split("\n")
        if len(a) != len(b):
            print(f"  ⚠ {name}: 줄 수가 다르다({len(a)}→{len(b)})")
            return False
        got |= {(name, i + 1) for i, (x, y) in enumerate(zip(a, b)) if x != y}
    extra, absent = got - want, want - got
    for e in sorted(extra):
        print(f"  ⚠ 치환표 밖이 바뀌었다: {e[0]}:{e[1]}")
    print(f"{path}: 바뀐 줄 {len(got)}/{len(want)} 전부 치환표 안" if not extra else "", end="")
    if absent:
        print(f" · 안 바뀐 항목 {len(absent)}(기적용이면 정상)")
    else:
        print()
    return not extra


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--verify"]
    fixes = read_fixes()
    targets = [Path(a) for a in args] or DEFAULT_TARGETS
    ok = True
    for t in targets:
        ok &= patch_file(t, fixes)
        if "--verify" in sys.argv:
            ok &= verify(t, fixes)
    sys.exit(0 if ok else 1)
