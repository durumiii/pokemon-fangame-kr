# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools"]
# ///
"""마스터 글꼴의 좌표를 **정수 눈금**에 다시 앉힌다.

    uv run runa/snap-grid.py --font <ttf> [--in-place]

왜 필요한가. 픽셀 글꼴은 좌표가 「1픽셀이 몇 단위인가」의 정수배일 때만 어느 크기에서나
같은 모양으로 떨어진다. 그런데 DPPt 마스터는 em이 1000이고 가로 16픽셀이라 1픽셀이
**62.5단위** — 정수가 아니다. TrueType 좌표는 정수라서 홀수 픽셀 선이 62/63으로
반올림돼 있고, 그 반 단위가 렌더 때 글자마다 다르게 굴러떨어진다.

실측(2026-08-07): 우리 마스터는 좌표의 49~74%가 눈금에서 0.008~0.016픽셀 벗어나 있었고,
게임이 쓰는 크기(24·25·29)에서 같은 높이로 그려져야 할 한글이 두 높이로 갈렸다. 같은
자리에서 원본 Galmuri11은 벗어난 좌표가 **0개**였고 갈라지지도 않았다 — 그 글꼴은
em이 1200이고 1픽셀이 72단위라 처음부터 정수였다.

고치는 법은 em을 키워 1픽셀을 정수로 만드는 것이다. 1024로 올리면 1픽셀이 정확히
64단위가 된다. 좌표는 옛 눈금으로 픽셀 번호를 읽어(round(v / 62.5)) 새 눈금에 다시 앉힌다.
"""
import argparse
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

NEW_UPEM = 1152          # 가로 16픽셀 → 1픽셀 = 72단위. 갈무리(72)·BW(125@2000=72)와 같은 눈금이라
                         # 한글을 옮겨 심을 때 오차가 0이 된다(1024=64로는 갈무리가 안 떨어진다).
GRID = 16                # em이 몇 픽셀인가 — DPPt 계열의 규약


def main() -> None:
    ap = argparse.ArgumentParser(description="좌표를 정수 눈금에 다시 앉힌다")
    ap.add_argument("--font", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()
    out = args.out or (args.font if args.in_place else None)
    if out is None:
        raise SystemExit("--out이나 --in-place 중 하나를 주세요")

    font = TTFont(args.font, recalcTimestamp=False)
    old = font["head"].unitsPerEm
    was, now = old / GRID, NEW_UPEM / GRID          # 62.5 → 64

    def snap(v: float) -> int:
        return int(round(v / was)) * int(now)

    glyphs = font.getGlyphSet()
    glyf, hmtx = font["glyf"], font["hmtx"]
    moved = 0
    for name in font.getGlyphOrder():
        rec = RecordingPen()
        glyphs[name].draw(rec)
        pen = TTGlyphPen(None)
        for op, args_ in rec.value:
            pen.__getattribute__(op)(*[
                tuple(snap(v) for v in pt) if isinstance(pt, tuple) else pt for pt in args_])
        glyf.glyphs[name] = pen.glyph()
        width, lsb = hmtx[name]
        hmtx.metrics[name] = (snap(width), snap(lsb))
        moved += 1

    font["head"].unitsPerEm = NEW_UPEM
    for table, fields in (("hhea", ("ascent", "descent", "lineGap")),
                          ("OS/2", ("sTypoAscender", "sTypoDescender", "sTypoLineGap",
                                    "usWinAscent", "usWinDescent", "sxHeight", "sCapHeight"))):
        if table not in font:
            continue
        for field in fields:
            if hasattr(font[table], field):
                setattr(font[table], field, snap(getattr(font[table], field)))
    font["head"].modified = font["head"].created
    font.save(out)

    # 되읽어 확인 — 눈금에서 벗어난 좌표가 하나도 없어야 한다.
    again = TTFont(out, lazy=True)
    unit = again["head"].unitsPerEm / GRID
    off = 0
    check = again.getGlyphSet()
    for name in again.getGlyphOrder():
        rec = RecordingPen()
        check[name].draw(rec)
        for op, args_ in rec.value:
            for pt in args_:
                if isinstance(pt, tuple):
                    off += sum(1 for v in pt if abs(v / unit - round(v / unit)) > 1e-6)
    print(f"{out} — 글리프 {moved}개를 1픽셀={int(now)}단위 눈금에 다시 앉힘 · "
          f"벗어난 좌표 {off}개 · {out.stat().st_size:,} bytes")
    if off:
        raise SystemExit("눈금에 안 맞는 좌표가 남았어요 — 고치기 전에는 쓰지 마세요")


if __name__ == "__main__":
    main()
