# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""korean.dat 용어 수정 — 걸음 3 (2026-08-01 대조 결과 반영).

전수 대조(ES↔공식 KO, Bulbapedia 판정)에서 Z 패치가 고칠 곳은 기술 셋뿐이었다.
나머지 불일치는 전부 대조 기준 쪽이 구명이었다(PokéAPI는 2020년 대개명 이전,
WS 로케일도 일부 구명). 근거: docs/log/research/2026-08-01-z-terminology-audit.md.

+ combate 계열 통일: 스페인어 원문이 combate인 대사에서 시합·대결 → 배틀.

usage: uv run apply_terms.py [--dry-run]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vendor"))
from fanlib import rubywrite  # noqa: E402
from datread import load  # noqa: E402  (딱지를 떼 옛 도구가 그대로 읽는다)

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/korean.dat")
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/korean.dat")

# 절5(기술명) 위치 → (현재값 확인용, 새 값). Bulbapedia 현행 공식명.
MOVE_FIXES = {
    98: ("깨뜨리다", "깨트리기"),   # Brick Break
    296: ("탐내다", "탐내기"),      # Covet
    336: ("프섭정 ", "프레젠트"),   # Present — 패치의 치환 사고('섭정' 오염) 복구
}
BATTLE_SECTIONS = (0, 22, 23)


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def main():
    dry = "--dry-run" in sys.argv
    d = load(open(STORE, "rb"))

    for i, (old, new) in MOVE_FIXES.items():
        got = d[5][i].decode("utf-8")
        if got == new:
            print(f"절5[{i}]: 이미 {new!r}")
            continue
        assert got == old, f"절5[{i}]가 예상과 다르다: {got!r} (기대 {old!r})"
        d[5][i] = new.encode("utf-8")
        print(f"절5[{i}]: {old!r} → {new!r}")

    swapped = 0
    for sec in BATTLE_SECTIONS:
        targets = d[sec] if sec == 0 else [d[sec]]
        for oh in targets:
            keys, values = inner_of(oh)
            dirty = False
            for i, v in enumerate(values):
                if b"ombate" not in bytes(keys[i]):
                    continue
                text = v.decode("utf-8")
                new = text.replace("시합", "배틀").replace("대결", "배틀")
                if new != text:
                    values[i] = new.encode("utf-8")
                    swapped += new.count("배틀") - text.count("배틀")
                    dirty = True
            if dirty:
                oh._private_data = rubywrite.dumps([keys, values])
    print(f"combate 통일: 시합·대결 → 배틀 {swapped}회")

    out = rubywrite.dumps(d)
    r = load(io.BytesIO(out))
    for i, (_, new) in MOVE_FIXES.items():
        assert r[5][i] == new.encode("utf-8"), f"절5[{i}] 왕복 불일치"
    for sec in BATTLE_SECTIONS:
        src = d[sec] if sec == 0 else [d[sec]]
        dst = r[sec] if sec == 0 else [r[sec]]
        for a, b in zip(src, dst):
            assert inner_of(a) == inner_of(b), f"절{sec} 왕복 불일치"
    for sec in (1, 7, 10, 12, 14):
        if isinstance(d[sec], list):
            assert r[sec] == d[sec], f"절{sec}이 변했다"
        else:
            assert inner_of(r[sec]) == inner_of(d[sec]), f"절{sec}이 변했다"
    print(f"왕복 검증 통과 · 산출 {len(out):,} bytes")

    if dry:
        print("dry-run — 파일에 쓰지 않음")
        return
    STORE.write_bytes(out)
    GAME.write_bytes(out)
    print(f"기록 완료: {STORE}\n           {GAME}")


if __name__ == "__main__":
    main()
