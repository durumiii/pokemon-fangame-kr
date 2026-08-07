# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools"]
# ///
"""마스터 폰트의 **한글 음절만** 다른 폰트 것으로 갈아 끼운 변형을 만든다.

라틴·숫자·부호·낱자모는 마스터(DPPt)의 것을 그대로 둔다 — 갈아 끼우는 것은
한글 음절 2,355자뿐이다. 그래서 어느 변형을 골라도 화면의 영문·부호는 같다.

    uv run runa/make-hangul-variant.py --donor <폰트> --pixel <픽셀당 단위> --out <ttf>

**픽셀 격자를 맞추는 것이 핵심이다.** 픽셀 폰트는 글자 크기가 격자의 정수배일 때만
선이 안 흐려진다. 마스터는 1픽셀이 62.5 단위(upem 1000)인데 갈무리11은 72(upem 1200),
BW는 125(upem 2000)라, upem 비율로 줄이면 격자가 어긋난다. 그래서 upem이 아니라
**픽셀 크기를 기준으로** 윤곽선을 줄인다.

세로 자리도 맞춘다 — DPPt는 글자 전체가 기준선보다 1픽셀 위에 앉아 있다(A는 y=62부터).
받아 오는 폰트는 기준선이 0이라 그대로 심으면 한글만 1픽셀 내려앉는다.

자간은 한글끼리 붙지 않도록 **획이 가장 넓은 글자보다 1픽셀 넓게** 잡고, 모든 음절에
같은 값을 준다(DPPt의 한글도 고정폭이다).
"""
import argparse
from pathlib import Path

from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
MASTER = HERE / "fonts" / "dppt-kr.ttf"
SYLLABLES = range(0xAC00, 0xD7A4)


def cmap_of(font: TTFont) -> dict:
    out = {}
    for table in font["cmap"].tables:
        out.update(table.cmap)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="한글 음절만 다른 폰트 것으로 바꾼 마스터를 만든다")
    ap.add_argument("--donor", type=Path, required=True, help="한글을 가져올 폰트")
    ap.add_argument("--pixel", type=float, required=True, help="받아 올 폰트의 1픽셀이 몇 단위인지")
    ap.add_argument("--master", type=Path, default=MASTER)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    base = TTFont(args.master, recalcTimestamp=False)
    base_map = cmap_of(base)
    unit = base["head"].unitsPerEm / 16          # 마스터의 1픽셀 — DPPt는 em의 16분의 1(62.5)

    donor = TTFont(args.donor)
    donor_map = cmap_of(donor)
    donor_glyphs = donor.getGlyphSet()

    # 갈아 낄 자리 — 마스터에 있고 받아 올 폰트에도 있는 음절만.
    targets = [c for c in SYLLABLES if c in base_map and c in donor_map]
    if not targets:
        raise SystemExit("갈아 낄 음절이 없어요 — 받아 올 폰트에 한글이 있는지 봐요")

    scale = unit / args.pixel
    shift = Transform().scale(scale)

    # 마스터의 한글이 앉은 자리(왼쪽 끝·아래 끝)를 재서 받아 오는 글자를 거기 맞춘다.
    box = BoundsPen(base.getGlyphSet())
    base.getGlyphSet()[base_map[targets[0]]].draw(box)
    want_x, want_y = box.bounds[0], box.bounds[1]

    # 받아 오는 쪽의 왼쪽·아래 끝과 가장 넓은 획을 한 번에 잰다.
    src_x, src_y, widest = None, None, 0
    for code in targets:
        bp = BoundsPen(donor_glyphs)
        donor_glyphs[donor_map[code]].draw(bp)
        if bp.bounds is None:
            continue
        x0, y0, x1, _ = bp.bounds
        src_x = x0 if src_x is None else min(src_x, x0)
        src_y = y0 if src_y is None else min(src_y, y0)
        widest = max(widest, x1 - x0)

    dx = want_x - src_x * scale
    dy = want_y - src_y * scale
    place = Transform(scale, 0, 0, scale, dx, dy)

    # 자간 — 획 폭보다 1픽셀 넓게, 다만 마스터보다 좁히지는 않는다(글자가 붙는다).
    master_adv = base["hmtx"][base_map[targets[0]]][0]
    advance = max(master_adv, round((widest * scale + unit) / unit) * unit)

    glyf, hmtx = base["glyf"], base["hmtx"]
    for code in targets:
        name = base_map[code]
        pen = TTGlyphPen(base.getGlyphSet())
        donor_glyphs[donor_map[code]].draw(TransformPen(pen, place))
        glyf.glyphs[name] = pen.glyph()
        hmtx.metrics[name] = (int(round(advance)), 0)

    base["head"].modified = base["head"].created
    args.out.parent.mkdir(parents=True, exist_ok=True)
    base.save(args.out)

    px = lambda v: round(v / unit, 2)            # 눈으로 읽을 수 있게 픽셀로
    print(f"{args.out} — 음절 {len(targets)}자 교체 · 획 폭 {px(widest * scale)}px · "
          f"자간 {px(advance)}px (마스터 {px(master_adv)}px) · {args.out.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
