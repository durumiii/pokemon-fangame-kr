#!/usr/bin/env python3
"""상태이상 아이콘 그림의 글자를 갈아 끼운다 (statuses.PNG · battleStatuses.png).

두 그림은 44px 폭에 16px 높이의 칸을 세로로 쌓은 띠고, 칸 하나가 상태이상 하나다.
글자는 그림에 구워져 있어 번역표로는 못 고친다 — 상태 이름을 바꾸면 여기도 고쳐야 한다.

글자체는 이 그림을 만든 외부 한글패치의 것이라 폰트 파일이 없다(갈무리 3종과
대조해 최대 IoU 0.57 — 다른 폰트다). 그래서 같은 결의 비트맵을 손으로 떠서 쓴다:
가로획 1px · 세로획 3px · 받침 없는 글자는 2~12행 · 받침 있는 글자는 2~7행 + 9~13행,
흰 글자에 오른쪽·아래 1px 그림자(칸마다 어두운 색이 다르다).

  uv run tools/status_icon.py <칸 번호> <글자 이름>   # 미리보기만(scratch에 PNG)
  uv run tools/status_icon.py <칸 번호> <글자 이름> --write

칸 번호는 0부터. 쇠락(옛 부패)은 두 그림 모두 5번 칸이다.
"""
import os, sys

from PIL import Image

GAME = "/mnt/d/Game/Pokemon Z/V2.18/Graphics/Pictures"
ZGUI = "/mnt/d/GameVault/mods/Pokemon Z Fangame/Z-GUI/Graphics/Pictures"
TARGETS = ["statuses.PNG", "battleStatuses.png"]
CELL = 16

# 손으로 뜬 글자꼴. 한 줄 = 한 픽셀 행, '#'이 글자. 좌표는 칸 왼쪽 위 기준.
# 받침 있는 글자(락)는 2~13행, 없는 글자(쇠)는 2~12행을 쓴다.
# 낱자꼴 — 옛 「부패」와 같은 자리(x8부터, 2행부터)에 앉는다.
GLYPHS = {
    "쇠": (8, 2, [                 # ㅅ + ㅚ (ㅗ 아래, ㅣ 오른쪽) — 「화」의 짜임을 본떴다
        "...###....###",
        "...###....###",
        "...###....###",
        "..#####...###",
        ".###.###..###",
        "###...###.###",
        "..........###",
        "...###....###",
        "...###....###",
        "#########.###",
        "..........###",
    ]),
    "락": (22, 2, [                # ㄹ + ㅏ + 받침 ㄱ — 받침이 있어 윗머리를 2~7행으로 줄인다
        "#########.###.",
        "......###.###.",
        "#########.####",
        "###.......###.",
        "###.......###.",
        "#########.###.",
        "..............",
        "##############",
        "...........###",
        "...........###",
        "...........###",
    ]),
}
WORDS = {"쇠락": ["쇠", "락"]}


def cell_colors(im, cell):
    """칸의 바탕·글자·그림자 색을 실물에서 읽는다 — 칸마다 색이 다르다."""
    px = im.load()
    y0 = cell * CELL
    counts = {}
    for y in range(y0, y0 + CELL):
        for x in range(im.width):
            counts[px[x, y]] = counts.get(px[x, y], 0) + 1
    base = max(counts, key=counts.get)                       # 가장 넓은 색 = 바탕
    white = (255, 255, 255, 255)
    dark = min((c for c in counts if c[3] == 255 and c != white),
               key=lambda c: sum(c[:3]))                     # 가장 어두운 색 = 그림자
    return base, white, dark


def repaint(im, cell, word):
    base, white, dark = cell_colors(im, cell)
    px = im.load()
    y0 = cell * CELL
    # 옛 글자 지우기 — 글자·그림자 픽셀만 바탕색으로 되돌린다(테두리·명암 줄은 건드리지 않는다)
    for y in range(y0 + 2, y0 + 14):
        for x in range(4, im.width - 4):
            if px[x, y] in (white, dark):
                px[x, y] = base
    plan = [(x0, top, rows) for x0, top, rows in (GLYPHS[g] for g in WORDS[word])]
    for x0, top, rows in plan:          # 그림자 먼저 — 옆 글자가 위를 덮는다
        for dy, line in enumerate(rows):
            for dx, c in enumerate(line):
                if c == "#":
                    px[x0 + dx + 1, y0 + top + dy + 1] = dark
    for x0, top, rows in plan:
        for dy, line in enumerate(rows):
            for dx, c in enumerate(line):
                if c == "#":
                    px[x0 + dx, y0 + top + dy] = white
    return im


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cell, name = int(sys.argv[1]), sys.argv[2]
    write = "--write" in sys.argv
    scratch = os.environ.get("SCRATCH", "/tmp")
    for fn in TARGETS:
        src = os.path.join(GAME, fn)
        im = Image.open(src).convert("RGBA")
        out = repaint(im, cell, name)
        prev = os.path.join(scratch, f"{fn}.{name}.png")
        out.crop((0, cell * CELL, out.width, (cell + 1) * CELL)) \
           .resize((out.width * 10, CELL * 10), Image.NEAREST).save(prev)
        print("미리보기", prev)
        if write:
            for d in (GAME, ZGUI):
                p = os.path.join(d, fn)
                if os.path.exists(p):
                    out.save(p)
                    print("씀", p)


if __name__ == "__main__":
    main()
