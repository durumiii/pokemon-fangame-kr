# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools"]
# ///
"""마스터 폰트 하나를 게임이 요청하는 패밀리명 16벌로 찍어 낸다.

게임은 폰트를 파일 이름이 아니라 **폰트가 자기 안에 들고 있는 패밀리명**으로 찾는다.
원판 pkmn*.ttf 여덟 벌이 그 이름들을 들고 있으면서 한글이 0자라, 같은 이름을 한글 든
마스터가 직접 들게 해 그 자리를 덮는다. 이름과 파일의 짝은 fonts/families.json.

    uv run runa/stamp-fonts.py [--out <모드폴더>/Fonts]

산출물은 저장소에 넣지 않는다(같은 마스터에서 언제든 다시 나온다).
"""
import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
MASTER = HERE / "fonts" / "dppt-kr.ttf"
FAMILIES = HERE / "fonts" / "families.json"
OUT = HERE.parent / "mods" / "DPPT Font" / "Fonts"

# 이름표의 자리 — 1 패밀리, 4 전체 이름, 16 타이포그래픽 패밀리, 6 포스트스크립트.
NAME_IDS = (1, 4, 16)


def stamp(master: Path, family: str) -> TTFont:
    # recalcTimestamp=False가 없으면 저장 시각이 새로 매겨져 같은 재료로 지어도
    # 매번 다른 바이트가 나온다 — 설치 판정이 그것을 「원본이 달라졌다」로 읽는다.
    font = TTFont(master, recalcTimestamp=False)
    for record in font["name"].names:
        if record.nameID in NAME_IDS:
            record.string = family
        elif record.nameID == 6:
            record.string = family.replace(" ", "")
    font["head"].modified = font["head"].created
    return font


def main() -> None:
    ap = argparse.ArgumentParser(description="마스터를 패밀리명 16벌로 찍는다")
    ap.add_argument("--master", type=Path, default=MASTER)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    families = json.loads(FAMILIES.read_text(encoding="utf-8"))["families"]
    args.out.mkdir(parents=True, exist_ok=True)
    for filename, family in families.items():
        stamp(args.master, family).save(args.out / filename)

    made = sorted(args.out.glob("*.ttf"))
    print(f"{args.out} — {len(made)}벌 (기대 {len(families)})")
    for path in made:                       # 찍힌 이름을 되읽어 확인한다
        got = {r.toUnicode() for r in TTFont(path, lazy=True)["name"].names
               if r.nameID == 1}
        want = families[path.name]
        assert got == {want}, f"{path.name}의 패밀리명이 {got} 예요 (기대 {want!r})"
    print("패밀리명 확인 — 16벌 모두 기대한 이름이에요")


if __name__ == "__main__":
    main()
