# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools"]
# ///
"""갈무리 마스터를 만든다 — **원본 갈무리 통짜**를 우리가 쓰는 글자 수만큼 줄인 것.

    uv run runa/make-galmuri-master.py

DPPt에 갈무리 한글만 옮겨 심은 판은 게임이 쓰는 크기(25·26·28·31픽셀)에서 글자마다
높이가 갈렸다 — 원본 갈무리는 어느 크기에서도 두 무리(받침 있음·없음)로만 떨어진다
(2026-08-07 실측). 그래서 갈래는 **옮겨 심기를 그만두고 원본을 그대로 쓴다.**

원본은 20,999자라 16벌로 찍으면 56MB가 된다. DPPt 마스터가 들고 있는 글자
(2,995자)만 남기면 그 십분의 일로 준다. 갈무리에 없는 글자 57자(옛 낱자모·별자리
기호 따위)는 DPPt에서 가져와 갈무리 눈금에 다시 앉힌다.
"""
import argparse
from pathlib import Path

from fontTools.misc.transform import Transform
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
GALMURI = HERE / "fonts" / "src" / "Galmuri11.ttf"
DPPT = HERE / "fonts" / "dppt-kr.ttf"
OUT = HERE / "fonts" / "galmuri-kr.ttf"
GRID = 16                       # em이 몇 픽셀인가 — DPPt 계열의 규약

# **한자를 남겨야 한다.** FreeType의 자동 힌팅은 한자 몇 자의 윤곽선을 재서 CJK 글자의
# 위·아래 기준선(blue zone)을 잡는다. 줄이면서 한자를 다 버리면 그 기준선이 사라져,
# 같은 높이로 그려져야 할 한글이 크기에 따라 세 무리로 갈린다(2026-08-07 실측:
# 25·26·28·31픽셀에서 갈렸고, 한자를 되돌리자 원본과 완전히 같아졌다. 이분 탐색으로
# 「他」 한 글자만 있어도 해결되는 것을 확인했다).
# 판마다 표본이 다를 수 있어 넉넉히 남긴다 — 41자라 크기는 6KB쯤 는다.
BLUE_ZONE_HANJA = "他們你來個到和地大不了在人有我一是中為上國會可以這下事出時就都能第自年過發後方定"


def cmap_of(font: TTFont) -> dict:
    """유니코드 표만 읽는다.

    DPPt에는 옛 맥 로만 표가 남아 있어 U+0080~009F(제어 문자 자리)에 `Adieresis`
    같은 글리프가 걸려 있다. 그것까지 「우리가 쓰는 글자」로 세면 갈무리에 없는
    글자로 잡혀 헛되이 32자를 옮기게 된다 — 진짜 자리(U+00C4 …)에는 이미 있다.
    """
    out = {}
    for table in font["cmap"].tables:
        if table.isUnicode():
            out.update(table.cmap)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="갈무리 통짜를 우리 글자 수만큼 줄인다")
    ap.add_argument("--galmuri", type=Path, default=GALMURI)
    ap.add_argument("--like", type=Path, default=DPPT, help="글자 목록을 가져올 글꼴")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    like = TTFont(args.like)
    wanted = set(cmap_of(like))

    base = TTFont(args.galmuri, recalcTimestamp=False)
    had = set(cmap_of(base))
    hanja = {ord(ch) for ch in BLUE_ZONE_HANJA} & had
    keep = sorted((wanted & had) | hanja)
    missing = sorted(wanted - had)

    trim = Subsetter()
    trim.populate(unicodes=keep)
    trim.subset(base)

    # 갈무리에 없는 글자는 DPPt에서 가져온다. 1픽셀이 62.5단위인 자리에서 읽어
    # 72단위 자리에 다시 앉힌다 — 픽셀 번호로 옮기므로 눈금이 어긋나지 않는다.
    src_unit = like["head"].unitsPerEm / GRID
    dst_unit = base["head"].unitsPerEm / GRID
    like_map, like_glyphs = cmap_of(like), like.getGlyphSet()
    base_map = cmap_of(base)
    glyf, hmtx = base["glyf"], base["hmtx"]
    brought = 0
    for code in missing:
        source = like_map.get(code)
        if source is None:
            continue
        rec = RecordingPen()
        like_glyphs[source].draw(rec)
        pen = TTGlyphPen(None)
        for op, args_ in rec.value:
            getattr(pen, op)(*[
                tuple(int(round(v / src_unit)) * int(dst_unit) for v in pt)
                if isinstance(pt, tuple) else pt for pt in args_])
        name = "kr%04X" % code
        base.setGlyphOrder(base.getGlyphOrder() + [name])
        for table in base["cmap"].tables:
            if table.isUnicode():
                table.cmap[code] = name
        glyf.glyphs[name] = pen.glyph()
        width = like["hmtx"][source][0]
        hmtx.metrics[name] = (int(round(width / src_unit)) * int(dst_unit), 0)
        base_map[code] = name
        brought += 1

    base["head"].modified = base["head"].created
    base.save(args.out)

    again = TTFont(args.out, lazy=True)
    covered = set(cmap_of(again))
    print(f"{args.out} — {len(covered)}자 (원본에서 남긴 {len(keep)} · 그중 힌팅 기준선용 "
          f"한자 {len(hanja)} + DPPt에서 들여온 {brought}) · {args.out.stat().st_size:,} bytes")
    still = sorted(wanted - covered)
    if still:
        print(f"⚠ 아직 없는 글자 {len(still)}자: {''.join(chr(c) for c in still[:40])}")


if __name__ == "__main__":
    main()
