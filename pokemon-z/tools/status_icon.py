#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow"]
# ///
"""상태이상 아이콘 그림의 글자를 갈아 끼운다 (statuses.PNG · battleStatuses.png).

두 그림은 44px 폭에 16px 높이의 칸을 세로로 쌓은 띠고, 칸 하나가 상태이상 하나다.
글자는 그림에 그려져 있어 번역표로는 못 고친다 — 상태 이름을 바꾸면 여기도 고쳐야 한다.

글자체는 이 그림을 만든 외부 한글패치의 것이라 폰트 파일이 없다(갈무리 3종과
대조해 최대 IoU 0.57 — 다른 폰트다). 그래서 같은 결의 비트맵을 손으로 떠서 쓴다:
가로획 1px · 세로획 3px · 받침 없는 글자는 2~12행 · 받침 있는 글자는 2~7행 + 9~13행,
흰 글자에 오른쪽·아래 1px 그림자(칸마다 어두운 색이 다르다).

  uv run tools/status_icon.py <칸 번호> <글자 이름>   # 미리보기만(scratch에 PNG)
  uv run tools/status_icon.py <칸 번호> <글자 이름> --write
  uv run tools/status_icon.py new 맹독 --write        # 칸을 하나 덧붙인다

칸 번호는 0부터. 쇠약(옛 쇠락·부패)은 두 그림 모두 5번 칸이다.

칸 번호 자리에 `new`를 주면 **띠 끝에 칸을 하나 덧붙인다**(Z-64 맹독). 끝 칸 번호는
그림마다 다르므로(battleStatuses 7 · statuses 9) 도구가 파일별로 잡는다. 새 칸은
독 칸(1번)을 픽셀째 복사해 만들어 바탕·테두리·그림자 색이 본가 독 칸과 같고, 글자만
갈린다 — 유지자 판정(2026-08-21)이 「색은 독과 똑같이, 글자만으로 가른다」다.
멱등이다: 이미 늘어 있으면 그 칸을 다시 그린다.

⚠ 그림 로더가 프레임을 쪼개는 것은 파일 이름이 대괄호 숫자로 시작할 때뿐이라
(`AnimatedBitmap#initialize`) 이 둘은 통짜다 — 높이를 늘려도 다른 코드가 안 깨진다.
새 칸을 그리는 쪽 분기는 `share/patch_intl.py`의 소스 수술이다.
"""
import os, sys

from PIL import Image

GAME = "/mnt/d/Game/Pokemon Z/V2.18/Graphics/Pictures"
ZGUI = "/mnt/d/GameVault/mods/Pokemon Z Fangame/Z-GUI/Graphics/Pictures"
# v6부터 배포에 실리는 것은 통합 모드 `UI KR`의 사본이다(Z-GUI는 보관소에만 남는다 —
# make_package.py의 RUNA_INJECT). 둘 다 있으면 둘 다 쓴다.
UIKR = "/mnt/d/GameVault/mods/Pokemon Z Fangame/UI KR/Graphics/Pictures"
TARGETS = ["statuses.PNG", "battleStatuses.png"]
CELL = 16
# 원본 칸 수 — 지금 높이가 이보다 크면 새 칸이 이미 붙어 있다는 뜻이다(멱등 판정).
BASE_CELLS = {"statuses.PNG": 9, "battleStatuses.png": 7}
POISON_CELL = 1                 # 새 칸의 바탕이 되는 칸(독)

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
    "약": (22, 2, [                # ㅇ + ㅑ + 받침 ㄱ — 받침이 있어 윗머리를 2~7행으로 줄인다
        ".#######..###.",
        "###...###.####",
        "###...###.###.",
        "###...###.####",
        "###...###.###.",
        ".#######..###.",
        "..............",
        "##############",
        "...........###",
        "...........###",
        "...........###",
    ]),
    # Z-64 「맹독」. 「독」은 손으로 뜨지 않고 **독 칸(1번)의 픽셀을 그대로 옮겨 적었다** —
    # 두 그림의 1번 칸이 글자자리에서 같은 모양이라 그대로 쓴다(x15부터 2행부터, 13폭).
    # 자리만 두 글자 배치로 옮겼다.
    "맹": (5, 2, [                 # ㅁ + ㅐ + 받침 ㅇ — 받침이 있어 윗머리를 2~7행으로 줄인다
        "########.###..###",
        "###..###.###..###",
        "###..###.###..###",
        "###..###.########",
        "###..###.###..###",
        "########.###..###",
        ".................",
        "....#########....",
        "...###.....###...",
        "...###.....###...",
        "....#########....",
    ]),
    "독": (24, 2, [                # ㄷ + ㅗ + 받침 ㄱ — 독 칸 실물에서 뜬 그대로
        "#############",
        "###..........",
        "###..........",
        "#############",
        ".....###.....",
        "#############",
        ".............",
        "#############",
        "..........###",
        "..........###",
        "..........###",
    ]),
}
WORDS = {"쇠약": ["쇠", "약"], "맹독": ["맹", "독"]}


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
    # 옛 글자 지우기 — 글자띠(2~13행 × x4~폭-5) 안에서 바탕 아닌 것을 전부 되돌린다.
    # 흰색을 콕 집지 않는 이유: 독 칸의 글자는 순백이 아니라 (255,254,254)다.
    # 이 띠 안에 테두리·명암 무늬가 없는 것은 두 그림 열여섯 칸 전수로 확인했다.
    for y in range(y0 + 2, y0 + 14):
        for x in range(4, im.width - 4):
            if px[x, y] != base:
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


def append_cell(im, fn):
    """띠 끝에 독 칸 사본을 붙이고 그 칸 번호를 돌려준다. 이미 붙어 있으면 그 칸을 다시 쓴다."""
    n = BASE_CELLS[fn]
    if im.height // CELL > n:
        return im, n
    out = Image.new("RGBA", (im.width, im.height + CELL))
    out.paste(im, (0, 0))
    out.paste(im.crop((0, POISON_CELL * CELL, im.width, (POISON_CELL + 1) * CELL)),
              (0, n * CELL))
    return out, n


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    arg, name = sys.argv[1], sys.argv[2]
    # 낡음 검사 — 상태이상 표기 정본은 절23(caduco)이다. 재판정되면 그림만 낡으므로
    # (실제로 쇠락→쇠약 재판정이 있었다) 정본과 어긋난 채 그리기 전에 여기서 멈춘다.
    import json
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caduco = next((json.loads(l)["v"] for l in open(
        os.path.join(repo, "translate", "ko", "23-script-texts.jsonl"), encoding="utf-8")
        if l.strip() and json.loads(l).get("k") == "caduco"), None)
    if caduco and caduco not in WORDS:
        sys.exit(f"정본 표기가 「{caduco}」로 바뀌었다 — WORDS 글자 비트맵을 새 표기로 "
                 f"다시 만들어라 (지금 비트맵: {list(WORDS)})")
    write = "--write" in sys.argv
    scratch = os.environ.get("SCRATCH", "/tmp")
    for fn in TARGETS:
        src = os.path.join(GAME, fn)
        im = Image.open(src).convert("RGBA")
        if arg == "new":
            im, cell = append_cell(im, fn)
        else:
            cell = int(arg)
        out = repaint(im, cell, name)
        prev = os.path.join(scratch, f"{fn}.{name}.png")
        out.crop((0, cell * CELL, out.width, (cell + 1) * CELL)) \
           .resize((out.width * 10, CELL * 10), Image.NEAREST).save(prev)
        print("미리보기", prev)
        if write:
            for d in (GAME, ZGUI, UIKR):
                p = os.path.join(d, fn)
                if os.path.exists(p):
                    out.save(p)
                    print("씀", p)


if __name__ == "__main__":
    main()
