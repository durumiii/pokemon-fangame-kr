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

라틴·숫자는 갈무리 것을 버리고 **BW에서 통째로 이식**한다(Z-21, 유지자 2026-08-09).
갈무리 원본이 악센트 라틴을 한글 눈금(792), 악센트 대문자는 그보다 크게(1008)
그려 놓아 é·í·á가 주변 글자보다 크게 보였다 — 악센트만 갈면 옆의 기본 라틴과
스타일이 섞이므로 영어·숫자까지 한 소스로 통일한다.
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
BW = HERE / "fonts" / "bw-kr.ttf"
OUT = HERE / "fonts" / "galmuri-kr.ttf"
GRID = 16                       # em이 몇 픽셀인가 — DPPt 계열의 규약


def latin_codes(cmap: dict) -> set:
    """BW에서 통일 이식하는 자리 — 숫자·영문자와 라틴 확장 글자(악센트 포함).

    문장부호·기호는 갈무리 것을 지킨다(한글 문장 속 출현이 대부분이라 스타일을
    한글에 맞춘다). ×(0xD7)·÷(0xF7)는 글자가 아니라 뺀다.
    """
    ranges = [(0x30, 0x39), (0x41, 0x5A), (0x61, 0x7A),      # 숫자·영문
              (0xC0, 0xD6), (0xD8, 0xF6), (0xF8, 0x17F)]    # 라틴-1 보충·확장-A 글자
    return {c for lo, hi in ranges for c in range(lo, hi + 1) if c in cmap}

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


def transplant(base: TTFont, src: TTFont, codes: set) -> int:
    """src의 글리프를 base 눈금에 다시 앉힌다 — 픽셀 번호로 옮기므로 어긋나지 않는다.

    이미 있는 자리는 cmap을 새 글리프로 돌려 덮는다(옛 글리프는 미참조로 남는다).
    """
    src_unit = src["head"].unitsPerEm / GRID
    dst_unit = base["head"].unitsPerEm / GRID
    src_map, src_glyphs = cmap_of(src), src.getGlyphSet()
    glyf, hmtx = base["glyf"], base["hmtx"]
    done = 0
    for code in sorted(codes):
        source = src_map.get(code)
        if source is None:
            continue
        rec = RecordingPen()
        src_glyphs[source].draw(rec)
        pen = TTGlyphPen(None)
        for op, args_ in rec.value:
            getattr(pen, op)(*[
                tuple(int(round(v / src_unit)) * int(dst_unit) for v in pt)
                if isinstance(pt, tuple) else pt for pt in args_])
        name = "kr%04X" % code
        if name not in glyf.glyphs:
            base.setGlyphOrder(base.getGlyphOrder() + [name])
        for table in base["cmap"].tables:
            if table.isUnicode():
                table.cmap[code] = name
        glyf.glyphs[name] = pen.glyph()
        width = src["hmtx"][source][0]
        hmtx.metrics[name] = (int(round(width / src_unit)) * int(dst_unit), 0)
        done += 1
    return done


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

    # 라틴·숫자는 BW에서 통째로(악센트 눈금 사고 수리 + 스타일 통일),
    # 그 밖에 갈무리에 없는 글자는 DPPt에서 가져온다.
    bw = TTFont(BW)
    latin = latin_codes(cmap_of(bw)) & (wanted | had)
    replaced = transplant(base, bw, latin)
    brought = transplant(base, like, set(missing) - latin)

    base["head"].modified = base["head"].created
    base.save(args.out)

    again = TTFont(args.out, lazy=True)
    covered = set(cmap_of(again))
    print(f"{args.out} — {len(covered)}자 (원본에서 남긴 {len(keep)} · 그중 힌팅 기준선용 "
          f"한자 {len(hanja)} + BW 라틴·숫자 {replaced} + DPPt에서 들여온 {brought}) · "
          f"{args.out.stat().st_size:,} bytes")
    still = sorted(wanted - covered)
    if still:
        print(f"⚠ 아직 없는 글자 {len(still)}자: {''.join(chr(c) for c in still[:40])}")


if __name__ == "__main__":
    main()
