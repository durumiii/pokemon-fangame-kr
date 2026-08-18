# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow"]
# ///
"""양피지·본문 부류 그림 자산 생성기 (Z-74 어려운 부류 6장).

alquimia1~4·helpbg는 원본에서 글자를 지울 수 없어(무늬 위에 직접 그려져 있다)
양피지 무늬를 조각보처럼 다시 짜 덮은 뒤 그 위에 조판한다. tutorialBat은 바탕이
단색이라 연결 성분으로 글자만 걷어낸다(색 있는 성분 = 스프라이트, 무채색 = 글자).

문안은 원장 translate/data/asset-texts.jsonl의 ko에서 읽는다(읽기 전용).
파일별 좌표·색·글꼴은 아래 LAYOUT 표가 정본이다.

    uv run translate/assets/gen_parchment.py --out <출력 폴더> [--sheets]
"""
import argparse, json, random, re
from collections import Counter, deque
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "translate/data/asset-texts.jsonl"
INSTALL = Path("/mnt/d/Game/Pokemon Z/V2.18/Graphics/Pictures")
FONTS = Path(__file__).parent / "fonts"
GALMURI14 = str(FONTS / "Galmuri14.ttf")
GALMURI11 = str(ROOT / "runa/fonts/src/Galmuri11.ttf")

CREAM = (250, 240, 220, 255)   # 양피지 위 글자의 밝은 테
INK = (70, 50, 30, 255)        # 양피지 위 본문 잉크
BAT_FILL = (248, 248, 248, 255)
BAT_STROKE = (72, 80, 88, 255)

TYPES = {"노말":(200,60,40),"벌레":(110,140,30),"비행":(90,120,200),"바위":(150,90,50),
         "땅":(170,120,60),"전기":(200,160,30),"불꽃":(220,90,30),"물":(50,110,210),
         "풀":(60,150,50),"독":(140,70,180),"얼음":(80,180,200),"격투":(180,50,50),
         "에스퍼":(220,90,140),"고스트":(100,70,160),"악":(80,70,70),"강철":(130,140,150),
         "드래곤":(80,70,200),"페어리":(230,130,180)}

# 파일별 레이아웃 — 시제(proto_parchment.py·proto_body.py)에서 승인된 값 그대로.
LAYOUT = {
    "alquimia1.png": dict(mode="rows", y0=30, lh=25, gap=30),
    "alquimia2.png": dict(mode="rows", y0=30, lh=25, gap=30),
    "alquimia3.png": dict(mode="rows", y0=30, lh=25, gap=30),
    # alquimia4는 타입 라벨이 아니라 소재 이름이라 색을 표로 준다.
    "alquimia4.png": dict(mode="rows", y0=60, lh=26, gap=60,
                          label_colors={"목재":(150,90,50), "조약돌":(130,120,110),
                                        "뼛가루":(200,180,140)}),
    # helpbg는 키 아이콘 상자를 원본에서 오려 새 양피지 위에 되붙인다.
    "helpbg.png": dict(mode="help", seed=11, strip=(20,340,120,368), margin=16,
                       keys=[(60,96,240,140),(60,150,100,192),(60,204,100,246),
                             (60,258,100,300),(60,312,100,354)],
                       title_at=(100,44),
                       entry_at=[(256,108),(116,158),(116,212),(116,266),(116,320)]),
    "tutorialBat.png": dict(mode="body",
                            at=[(20,26),(20,58),(20,146),(20,178),(20,271),(20,303)]),
}


def src_path(name):
    """원본(스페인어)은 설치본 `.orig`가 있으면 그것, 없으면 아직 안 덮은 설치본 파일."""
    o = INSTALL / (name + ".orig")
    return o if o.exists() else INSTALL / name


def requilt(im, src_strip, inner, patch=8, seed=7):
    """무늬 있는 바탕을 조각보로 다시 짠다 — 글자 없는 띠에서 8px 조각을 표집해 덮는다."""
    random.seed(seed)
    px = im.load(); out = im.copy(); op = out.load()
    x0, y0, x1, y1 = inner; sx0, sy0, sx1, sy1 = src_strip
    for y in range(y0, y1, patch):
        for x in range(x0, x1, patch):
            sy = random.randint(sy0, sy1-patch); sx = random.randint(sx0, sx1-patch)
            fx = random.choice((False, True))
            for dy in range(min(patch, y1-y)):
                for dx in range(min(patch, x1-x)):
                    sxx = sx + (patch-1-dx if fx else dx)
                    op[x+dx, y+dy] = px[sxx, sy+dy]
    return out


def parse_rows(ko, label_colors=None):
    """원장 ko를 (라벨, 색, 본문줄들) 행으로 쪼갠다.

    「이름: 설명」 줄이 새 행을 열고, 콜론 없는 줄은 직전 행의 다음 줄로 붙는다.
    색은 설명 첫 낱말이 타입이면 타입색, 아니면 label_colors 표에서 찾는다.
    """
    rows = []
    for line in ko.split("\n"):
        if not line.strip():
            continue
        m = re.match(r"^(.+?):\s*(.*)$", line)
        if not m:
            if not rows:
                raise ValueError(f"라벨 없이 시작하는 줄: {line!r}")
            rows[-1][2].append(line)
            continue
        label, rest = m.group(1), m.group(2)
        first = rest.split()[0] if rest.split() else ""
        col = TYPES.get(first) or (label_colors or {}).get(label)
        if col is None:
            raise ValueError(f"라벨 색을 못 정함: {label!r} (설명 {rest!r})")
        rows.append([label + ":", col, [rest]])
    return rows


def draw_rows(out, rows, y0, lh, gap, f, x=28):
    d = ImageDraw.Draw(out)
    y = y0
    for label, col, lines in rows:
        d.text((x, y), label, font=f, fill=col+(255,), stroke_width=2, stroke_fill=CREAM)
        lw = d.textlength(label, font=f)
        d.text((x+lw+10, y), lines[0], font=f, fill=INK, stroke_width=2, stroke_fill=CREAM)
        for l in lines[1:]:
            y += lh
            d.text((x, y), l, font=f, fill=INK, stroke_width=2, stroke_fill=CREAM)
        y += lh + gap


def strip_glyphs(im):
    """연결 성분으로 글자만 걷어낸다 — 색 있는 성분은 스프라이트라 통째로 남긴다.

    눈 흰자처럼 스프라이트 속 흰 픽셀은 색 픽셀과 한 성분이라 함께 살아남는다.
    """
    W, H = im.size
    op = im.load()
    bg = Counter(im.get_flattened_data()).most_common(1)[0][0]
    textish = lambda p: max(p[:3]) - min(p[:3]) < 18   # 무채색 = 글자
    seen = [[False]*W for _ in range(H)]
    out = Image.new("RGBA", (W, H), bg); np_ = out.load()
    for y0 in range(H):
        for x0 in range(W):
            if seen[y0][x0]:
                continue
            p = op[x0, y0]
            if p[3] < 20 or p == bg:
                seen[y0][x0] = True; continue
            comp = []; colored = False
            q = deque([(x0, y0)]); seen[y0][x0] = True
            while q:
                x, y = q.popleft(); pp = op[x, y]
                comp.append((x, y, pp))
                if not textish(pp):
                    colored = True
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < W and 0 <= ny < H and not seen[ny][nx]:
                        p2 = op[nx, ny]
                        if p2[3] >= 20 and p2 != bg:
                            seen[ny][nx] = True; q.append((nx, ny))
            if colored:
                for x, y, pp in comp:
                    np_[x, y] = pp
    return out


def render(name, ko):
    lay = LAYOUT[name]
    im = Image.open(src_path(name)).convert("RGBA")
    W, H = im.size
    if lay["mode"] == "rows":
        out = requilt(im, (15, 15, 29, H-15), (13, 13, W-13, H-13))
        f = ImageFont.truetype(GALMURI11, 22)
        draw_rows(out, parse_rows(ko, lay.get("label_colors")),
                  lay["y0"], lay["lh"], lay["gap"], f)
    elif lay["mode"] == "help":
        m = lay["margin"]
        out = requilt(im, lay["strip"], (m, m, W-m, H-m), seed=lay["seed"])
        for b in lay["keys"]:
            out.paste(im.crop(b), b[:2])
        f = ImageFont.truetype(GALMURI14, 28)
        d = ImageDraw.Draw(out)
        title, *entries = [l for l in ko.split("\n") if l.strip()]
        tx, ty = lay["title_at"]
        d.text((tx, ty), title, font=f, fill=INK, stroke_width=2, stroke_fill=CREAM)
        d.line((tx, ty+32, tx+d.textlength(title, font=f), ty+32), fill=INK, width=2)
        for (x, y), t in zip(lay["entry_at"], entries):
            d.text((x, y), t, font=f, fill=INK, stroke_width=2, stroke_fill=CREAM)
    else:
        out = strip_glyphs(im)
        f = ImageFont.truetype(GALMURI14, 28)
        d = ImageDraw.Draw(out)
        for xy, t in zip(lay["at"], [l for l in ko.split("\n") if l.strip()]):
            d.text(xy, t, font=f, fill=BAT_FILL, stroke_width=2, stroke_fill=BAT_STROKE)
    return im, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sheets", action="store_true")
    a = ap.parse_args()
    outd = Path(a.out); outd.mkdir(parents=True, exist_ok=True)
    if a.sheets:
        (outd/"sheets").mkdir(exist_ok=True)
    todo = {json.loads(l)["file"]: json.loads(l).get("ko")
            for l in LEDGER.open(encoding="utf-8")}
    for name in LAYOUT:
        ko = todo.get(name)
        if not ko:
            print(f"SKIP {name}: 원장에 ko 없음"); continue
        src, out = render(name, ko)
        out.save(outd/name)
        print(f"  {name}: {out.size[0]}x{out.size[1]} · {LAYOUT[name]['mode']}")
        if a.sheets:
            W, H = src.size
            sheet = Image.new("RGB", (W*2, H), (235, 235, 240))
            sheet.paste(src, (0, 0), src); sheet.paste(out, (W, 0), out)
            sheet.save(outd/"sheets"/f"{name[:-4]}_sheet.png")
    print(f"생성 {len(LAYOUT)}")


if __name__ == "__main__":
    main()
