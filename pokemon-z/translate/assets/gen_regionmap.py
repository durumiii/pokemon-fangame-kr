# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow", "rubymarshal"]
# ///
"""리전 맵 그림의 장소 표지를 데이터 칸 중심에 맞춘다 (Z-GUI 자산).

원판 mapRegion0.png은 장소 표지 37개 중 14개가 격자에서 2~8px 밀려 있다. 커서는
16px 격자의 칸 중앙에 서고 이름 조회도 칸으로 하므로(townmap.dat), 밀린 표지는
커서가 제 칸에 서도 그림 위에 얹히지 않는다. 여기서 그 표지들을 제 칸 중앙으로
옮긴다 — 데이터는 그대로 두고 그림만 고친다.

옮길 자리는 하드코딩하지 않는다. 표지 하나(정렬된 (19,17))를 본으로 삼아 그림
전체에서 정확 일치로 찾고, townmap.dat에서 가장 가까운 장소 칸을 짝지어 그 칸
중앙까지의 차이를 옮김량으로 쓴다. 표지는 12x12 몸통과 바로 밑 12x4 그림자로
이뤄지고 둘을 함께 옮긴다. 비운 자리는 가장 가까운 배경 픽셀로 메운다.

장소 칸이 짝지어지지 않는 표지(원판 (2,5) 근처 하나)는 건드리지 않는다 — 이름
항목도 게임 맵도 없어 칸 중앙으로 옮기면 「눌러도 아무것도 안 뜨는 표지」가
된다. 그 자리의 처분은 유지자 판정 몫이다.

    uv run translate/assets/gen_regionmap.py            # 표만 찍는다
    uv run translate/assets/gen_regionmap.py --write    # 정본 폴더에 png를 낸다
    uv run translate/assets/gen_regionmap.py --sheets   # 전후 비교 시트도 낸다
"""
import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw
from rubymarshal.reader import load

ROOT = Path(__file__).resolve().parents[2]
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18")
SRC = GAME / "Graphics/Pictures/mapRegion0.png"
TOWNMAP = GAME / "Data/townmap.dat"
OUT = ROOT / "mods/Z-GUI/Graphics/Pictures/mapRegion0.png"
SHEETS = ROOT / "share/review-cards"

SQUARE = 16          # 커서 격자 한 칸
MARK = 12            # 표지 몸통 한 변
SHADOW = 4           # 몸통 바로 밑 그림자 높이
TEMPLATE_CELL = (19, 17)   # 본으로 쓸 정렬된 표지 — 남쪽 감시탑
SHADOW_RGB = (41, 41, 41)


def src_path():
    """원판 — 다른 모드가 덮었으면 그 백업이 원판이다."""
    o = SRC.with_name(SRC.name + ".orig")
    return o if o.exists() else SRC


def load_cells():
    """townmap.dat의 장소 칸 목록 — (x, y) → 이름."""
    locs = load(TOWNMAP.open("rb"))[0][2]
    return dict(((l[0], l[1]), str(l[2])[2:-1]) for l in locs)


def find_marks(px, size):
    """표지 몸통의 좌상 좌표 목록 — 본과 12x12가 정확히 같은 자리."""
    W, H = size
    tx, ty = TEMPLATE_CELL[0] * SQUARE + 2, TEMPLATE_CELL[1] * SQUARE + 2
    tmpl = [(dx, dy, px[tx + dx, ty + dy]) for dy in range(MARK) for dx in range(MARK)]
    corner = tmpl[0][2]
    hits = []
    for y in range(H - MARK):
        for x in range(W - MARK):
            if px[x, y] != corner:
                continue
            if all(px[x + dx, y + dy] == c for dx, dy, c in tmpl):
                hits.append((x, y))
    return hits, tmpl


def nearest_cell(cx, cy, cells):
    """표지 중심에서 가장 가까운 장소 칸 — 한 칸(16px) 밖이면 짝이 없는 것으로 본다."""
    best, bestd = None, None
    for (gx, gy) in cells:
        d = (gx * SQUARE + 8 - cx) ** 2 + (gy * SQUARE + 8 - cy) ** 2
        if bestd is None or d < bestd:
            best, bestd = (gx, gy), d
    return (best, bestd) if bestd is not None and bestd <= SQUARE * SQUARE else (None, bestd)


def footprint(x, y):
    """표지 하나가 차지하는 픽셀 — 몸통 12x12 + 바로 밑 그림자 12x4."""
    body = [(x + dx, y + dy) for dy in range(MARK) for dx in range(MARK)]
    shade = [(x + dx, y + MARK + dy) for dy in range(SHADOW) for dx in range(MARK)]
    return body, shade


def fill_background(im, holes):
    """비운 자리를 가장 가까운 배경 픽셀로 메운다 (BFS 거리 순으로 번짐)."""
    px = im.load()
    W, H = im.size
    hole = set(holes)
    q = deque()
    seed = {}
    for (x, y) in hole:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in hole:
                seed[(x, y)] = px[n]
                q.append((x, y))
                break
    done = set(seed)
    for (x, y), c in seed.items():
        px[x, y] = c
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in hole and n not in done:
                done.add(n)
                px[n] = px[x, y]
                q.append(n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="정본 폴더에 png를 낸다")
    ap.add_argument("--sheets", action="store_true", help="전후 비교 시트도 낸다")
    a = ap.parse_args()

    src = Image.open(src_path()).convert("RGBA")
    px = src.load()
    cells = load_cells()
    marks, _ = find_marks(px, src.size)

    moves, orphans = [], []
    for (x, y) in marks:
        cx, cy = x + MARK // 2, y + MARK // 2
        cell, _ = nearest_cell(cx, cy, cells)
        if cell is None:
            orphans.append((x, y))
            continue
        sx = cell[0] * SQUARE + 8 - cx
        sy = cell[1] * SQUARE + 8 - cy
        if sx or sy:
            moves.append((x, y, sx, sy, cell))

    print(f"표지 {len(marks)}개 · 옮길 것 {len(moves)}개 · 짝 없는 표지 {len(orphans)}개")
    for x, y, sx, sy, cell in sorted(moves, key=lambda m: (m[4][1], m[4][0])):
        print(f"  칸 {cell} {cells[cell]:<26} 옮김 {sx:+d},{sy:+d}")
    for x, y in orphans:
        print(f"  ⚠ 짝 없는 표지 좌상({x},{y}) — 손대지 않는다(장소 데이터·게임 맵 없음)")

    out = src.copy()
    for x, y, sx, sy, cell in moves:
        body, shade = footprint(x, y)
        patch = dict((p, px[p]) for p in body + shade)
        # 옛 자리를 통째로 지운 다음 새 자리에 찍는다 — 일부만 지우면 남은 표지
        # 픽셀이 배경으로 오인돼 메움에 번진다.
        fill_background(out, list(patch))
        o = out.load()
        for (a_, b_), c in patch.items():
            o[a_ + sx, b_ + sy] = c

    if a.sheets:
        SHEETS.mkdir(parents=True, exist_ok=True)
        S = 6
        tiles = []
        for x, y, sx, sy, cell in sorted(moves, key=lambda m: (m[4][1], m[4][0])):
            box = (cell[0] * SQUARE - 16, cell[1] * SQUARE - 16,
                   cell[0] * SQUARE + 32, cell[1] * SQUARE + 32)
            pair = Image.new("RGB", (96 * S, 48 * S), (25, 25, 25))
            for i, img in enumerate((src, out)):
                c = img.convert("RGB").crop(box).resize((48 * S, 48 * S), Image.NEAREST)
                d = ImageDraw.Draw(c)
                d.rectangle([16 * S, 16 * S, 32 * S - 1, 32 * S - 1], outline=(255, 0, 0), width=2)
                d.text((4, 4), ("전 " if i == 0 else "후 ") + cells[cell][:16], fill=(255, 255, 0))
                pair.paste(c, (i * 48 * S, 0))
            tiles.append(pair)
        cols = 2
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tiles[0].width, rows * tiles[0].height), (15, 15, 15))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % cols) * t.width, (i // cols) * t.height))
        p = SHEETS / "regionmap-marks.png"
        sheet.save(p)
        print(f"시트: {p}")

    if a.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        out.save(OUT)
        print(f"저장: {OUT}")
    else:
        print("--write 없이는 png를 쓰지 않았다.")


if __name__ == "__main__":
    main()
