# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow", "rubymarshal"]
# ///
"""리전 맵에서 「표지가 그려진 칸」을 뽑아 QOL Pack의 커서 스냅 소스에 박는다.

커서 스냅이 끌어당길 자리는 장소 데이터(`townmap.dat`)가 아니라 **그림에 표지가 그려진
칸**이다. 데이터 칸 175개 중 118개는 길과 여러 칸에 걸친 넓은 지역이라 표지가 없는데,
그런 칸까지 목표로 삼으면 커서가 눈에 보이는 표지 대신 엉뚱한 빈 자리로 끌린다.

판정은 픽셀로 한다 — 칸 안에 표지 색(장소 표지의 초록 셋, 도시 표지의 파랑)이 몇 개나
있는지 세면 실측 분포가 **40 이상 아니면 8 이하**로 갈려 중간이 없다. 그림이 정본이라
길 위에 선 표지(25번도로의 것)도 이름 규칙 없이 그대로 걸린다.

산출은 모드 소스의 표시 두 줄 사이를 통째로 다시 쓴다.

    uv run tools/regionmap_points.py            # 표만 찍는다
    uv run tools/regionmap_points.py --write    # 모드 소스에 박는다
"""
import argparse
from pathlib import Path

from PIL import Image
from rubymarshal.reader import load

ROOT = Path(__file__).resolve().parents[1]
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18")
ART = ROOT / "mods/Z-GUI/Graphics/Pictures/mapRegion0.png"   # 자리를 맞춘 정본
TOWNMAP = GAME / "Data/townmap.dat"
MOD = ROOT / "mods/QOL Pack/050_MapCursorSnap.rb"

SQUARE = 16
ICON_RGB = {(0, 132, 66), (148, 198, 33), (74, 165, 49), (33, 132, 165)}
ICON_MIN = 40      # 실측 분포의 빈 곳 — 표지가 있으면 40~176, 없으면 0~8
BEGIN = "  # >>> 표지 칸 — 생성기가 채운다 (tools/regionmap_points.py)"
END = "  # <<< 표지 칸"


def icon_pixels(px, size, x, y):
    """칸 하나 안의 표지 색 픽셀 수."""
    cx, cy = x * SQUARE + SQUARE // 2, y * SQUARE + SQUARE // 2
    n = 0
    for dy in range(-SQUARE // 2, SQUARE // 2):
        for dx in range(-SQUARE // 2, SQUARE // 2):
            a, b = cx + dx, cy + dy
            if 0 <= a < size[0] and 0 <= b < size[1] and px[a, b] in ICON_RGB:
                n += 1
    return n


def marked_cells():
    """표지가 그려진 장소 칸 [(x, y, 이름), ...] — 위에서 아래, 왼쪽에서 오른쪽."""
    locs = load(TOWNMAP.open("rb"))[0][2]
    im = Image.open(ART).convert("RGB")
    px = im.load()
    found = {}
    for loc in locs:
        cell = (loc[0], loc[1])
        if icon_pixels(px, im.size, *cell) >= ICON_MIN:
            found[cell] = str(loc[2])[2:-1]
    return [(x, y, found[(x, y)]) for x, y in sorted(found, key=lambda c: (c[1], c[0]))]


def ruby_table(cells):
    """여덟 칸씩 끊어 적은 루비 배열 — 1.8.7과 3.x 공통 문법."""
    lines = []
    for i in range(0, len(cells), 8):
        row = ",".join(f"[{x},{y}]" for x, y, _ in cells[i:i + 8])
        lines.append(f"    {row}," if i + 8 < len(cells) else f"    {row}")
    return "  SNAP_POINTS = [\n" + "\n".join(lines) + "\n  ]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="모드 소스에 박는다")
    a = ap.parse_args()

    cells = marked_cells()
    print(f"표지가 그려진 칸 {len(cells)}개")
    for x, y, name in cells:
        print(f"  ({x:>2},{y:>2})  {name}")

    src = MOD.read_text(encoding="utf-8")
    if BEGIN not in src or END not in src:
        raise SystemExit(f"모드 소스에 표시 두 줄이 없다: {MOD}")
    head, rest = src.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    fresh = f"{head}{BEGIN}\n{ruby_table(cells)}\n{END}{tail}"

    if not a.write:
        print("\n--write 없이는 모드 소스를 고치지 않았다.")
        return
    if fresh == src:
        print(f"\n{MOD.name}: 이미 같은 표다.")
        return
    MOD.write_text(fresh, encoding="utf-8")
    print(f"\n{MOD.name}에 표를 박았다.")


if __name__ == "__main__":
    main()
