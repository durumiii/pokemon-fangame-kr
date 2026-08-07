# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools"]
# ///
"""마스터 폰트 fonts/dppt-kr.ttf 를 만든 절차.

평소에는 돌릴 일이 없다 — 산출물이 저장소에 들어 있고, 모드 조립기는 그것을 쓴다.
dppt 원본이 바뀌거나 들여올 글자를 더할 때만 다시 돌린다.

바탕은 조이플레이 수정판 v3에 실려 온 픽셀 폰트 pokemon-dppt.ttf 다. 한글 음절은
손대지 않는다 — 글자의 얼굴이 바뀌기 때문이다. 손보는 것은 두 가지뿐이다.

  갈아 끼우기 — dppt에 있기는 한데 화면에서 찌그러지던 도형 15자(●■▲♥ 등).
  들여오기   — dppt에 아예 없던 91자. 대괄호·따옴표·낱자모(ㄱ~ㅣ)·문장부호가 여기 든다.
                낱자모가 없어 「ㅐ」가 빈칸으로 떨어지던 자리가 이걸로 메워졌다.

둘 다 갈무리(Galmuri11)에서 가져온다. 자간 규격(unitsPerEm)이 달라 먼저 dppt에 맞춘 뒤
윤곽선만 옮겨 심는다.

    uv run runa/make-font.py --dppt <원본.ttf> --galmuri <Galmuri11.ttf>
"""
import argparse
from pathlib import Path

from fontTools.misc.transform import Identity
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem

HERE = Path(__file__).resolve().parent
OUT = HERE / "fonts" / "dppt-kr.ttf"
GALMURI = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Fonts/Galmuri11.ttf")

REPLACE = "●■▲♥○□△♡◆◇★☆♦♣♠"                        # 있지만 찌그러지는 것
ADD = list('"\'<>[\\]^`{|}') + list("–—─⇒π¨‥▽▼▶§®¯´¼¾¢£¤¦©«¬±µ¶¸½") \
    + [chr(c) for c in range(0x3131, 0x3164)]         # 낱자모 ㄱ~ㅣ


def main() -> None:
    ap = argparse.ArgumentParser(description="dppt에 갈무리 글자를 들여 마스터를 만든다")
    ap.add_argument("--dppt", type=Path, required=True, help="바탕이 될 pokemon-dppt.ttf")
    ap.add_argument("--galmuri", type=Path, default=GALMURI, help="들여올 글자의 출처")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    base = TTFont(args.dppt)
    base_map = {}
    for table in base["cmap"].tables:
        base_map.update(table.cmap)

    donor = TTFont(args.galmuri)
    scale_upem(donor, base["head"].unitsPerEm)
    want = sorted({ord(c) for c in REPLACE + "".join(ADD)})
    trim = Subsetter()
    trim.populate(unicodes=want)
    trim.subset(donor)
    donor_map = {}
    for table in donor["cmap"].tables:
        donor_map.update(table.cmap)
    donor_glyphs = donor.getGlyphSet()

    glyf, hmtx = base["glyf"], base["hmtx"]
    replaced = added = missing = 0
    for code in want:
        source = donor_map.get(code)
        if not source:
            missing += 1
            continue
        target = base_map.get(code)
        if target is None:
            target = "kr%04X" % code
            base.setGlyphOrder(base.getGlyphOrder() + [target])
            for table in base["cmap"].tables:
                if table.isUnicode():
                    table.cmap[code] = target
            added += 1
        else:
            replaced += 1
        pen = TTGlyphPen(base.getGlyphSet())
        donor_glyphs[source].draw(TransformPen(pen, Identity))
        glyf.glyphs[target] = pen.glyph()
        hmtx.metrics[target] = donor["hmtx"][source]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    base.save(args.out)

    covered = set()
    for table in TTFont(args.out)["cmap"].tables:
        covered.update(table.cmap)
    print(f"갈아 끼움 {replaced} · 들여옴 {added} · 갈무리에도 없어 못 넣음 {missing}")
    print(f"{args.out} — {len(covered)}자 · {args.out.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
