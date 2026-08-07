# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools"]
# ///
"""마스터에 **CJK 기준선용 글자**를 심는다 — 한글이 크기마다 다른 높이로 갈리지 않게.

    uv run runa/add-blue-zone.py --font <ttf> [--out <ttf>]

FreeType의 자동 힌팅은 CJK 글자를 그릴 때 **한자 몇 자의 윤곽선을 재서** 위·아래
기준선(blue zone)을 잡고, 그 선에 맞춰 획을 픽셀에 붙인다. 한자가 한 자도 없는 글꼴은
그 기준선을 못 잡아, 같은 높이로 그려져야 할 한글이 크기에 따라 두세 무리로 갈린다
(2026-08-07 실측: DPPt·BW 마스터가 24·25·28·29·31픽셀에서 거의 반반으로 갈렸다).

그래서 그 한자 자리에 **한글과 똑같은 높이의 속 빈 네모**를 심는다. 힌터는 그것을 재서
한글에 딱 맞는 기준선을 잡고, 혹 진짜 한자가 화면에 나오더라도 「없는 글자」로 읽히는
네모가 보일 뿐이다(글자 하나를 베껴 심으면 엉뚱한 한글이 보인다).

심은 뒤 일곱 크기(24·25·26·28·29·31·32)에서 한글 높이가 두 무리로만 떨어지는 것을
확인하고 끝낸다 — 안 되면 저장하지 않는다.
"""
import argparse
from collections import Counter
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

# FreeType이 CJK 기준선의 표본으로 삼는 한자들. 판마다 목록이 달라 넉넉히 잡는다 —
# 이분 탐색으로는 「他」 하나로도 충분했다(2026-08-07).
BLUE_ZONE_HANJA = "他們你來個到和地大不了在人有我一是中為上國會可以這下事出時就都能第自年過發後方定"
MODEL = "각"        # 한글의 위·아래 끝을 다 쓰는 글자 — 여기서 기준선의 높이를 딴다
SIZES = (24, 25, 26, 28, 29, 31, 32)      # 게임이 실제로 쓰는 글자 크기
SAMPLE = ("가나다라마바사아자차카타파하각간갈감갑강개거건걸검게겨결경고곡곤골공과관교"
          "구국군권그근글금급기긴길김")


def cmap_of(font: TTFont) -> dict:
    out = {}
    for table in font["cmap"].tables:
        if table.isUnicode():
            out.update(table.cmap)
    return out


def hollow_box(x0: int, y0: int, x1: int, y1: int, thick: int):
    """속이 빈 네모 하나. 바깥은 시계 반대, 안쪽은 반대로 돌려 구멍이 되게."""
    pen = TTGlyphPen(None)
    for points in ([(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                   [(x0 + thick, y0 + thick), (x0 + thick, y1 - thick),
                    (x1 - thick, y1 - thick), (x1 - thick, y0 + thick)]):
        pen.moveTo(points[0])
        for point in points[1:]:
            pen.lineTo(point)
        pen.closePath()
    return pen.glyph()


def spread(path: Path) -> dict:
    """크기마다 한글이 몇 가지 높이로 그려지는가 — {크기: {높이: 자 수}}."""
    from PIL import Image, ImageDraw, ImageFont

    out = {}
    for size in SIZES:
        face = ImageFont.truetype(str(path), size)
        seen = Counter()
        for ch in SAMPLE:
            card = Image.new("L", (size * 2, size * 2), 255)
            ImageDraw.Draw(card).text((size // 2, size // 4), ch, font=face, fill=0)
            box = card.point(lambda v: 255 if v < 200 else 0).getbbox()
            if box:
                seen[box[3] - box[1]] += 1
        out[size] = dict(sorted(seen.items()))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="CJK 기준선용 글자를 심는다")
    ap.add_argument("--font", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    out = args.out or args.font

    font = TTFont(args.font, recalcTimestamp=False)
    chart = cmap_of(font)
    model = chart.get(ord(MODEL))
    if model is None:
        raise SystemExit(f"기준으로 삼을 `{MODEL}`이 글꼴에 없어요")
    bounds = BoundsPen(font.getGlyphSet())
    font.getGlyphSet()[model].draw(bounds)
    x0, y0, x1, y1 = (int(v) for v in bounds.bounds)
    thick = int(font["head"].unitsPerEm / 16)          # 테두리는 1픽셀

    glyf, hmtx = font["glyf"], font["hmtx"]
    put = 0
    for ch in BLUE_ZONE_HANJA:
        code = ord(ch)
        name = "bluezone%04X" % code
        font.setGlyphOrder(font.getGlyphOrder() + [name])
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap[code] = name
        glyf.glyphs[name] = hollow_box(x0, y0, x1, y1, thick)
        hmtx.metrics[name] = hmtx[model]
        put += 1

    font["head"].modified = font["head"].created
    font.save(out)

    after = spread(out)
    split = {size: rows for size, rows in after.items() if len(rows) > 2}
    print(f"{out} — 기준선용 글자 {put}자 심음 · {out.stat().st_size:,} bytes")
    for size, rows in after.items():
        print(f"   {size}pt {' '.join(f'{h}px×{n}' for h, n in rows.items())}")
    if split:
        raise SystemExit(f"아직 갈려요: {split} — 이대로는 쓰지 마세요")
    print("일곱 크기 모두 두 무리로만 떨어져요(받침 있음·없음).")


if __name__ == "__main__":
    main()
