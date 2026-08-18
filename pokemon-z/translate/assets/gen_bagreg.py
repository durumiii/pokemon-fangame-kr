# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow"]
# ///
"""bagReg.PNG(가방 등록 표시) 생성기 — F5 → 등록.

Controller UX 모드 소유 자산이라 gen_cards.py의 카드형 부류에 안 낀다. 원본은
설치본의 `bagReg.PNG.orig`(F5판 백업) — 본 파일은 이미 등록판으로 덮여 있다.

x<18의 가방 아이콘은 그대로 두고, x>=18의 밝은 픽셀(r+g+b>300, 곧 "F5" 글자)만
몸통색 (87,24,156)으로 지운 뒤 갈무리9 9px을 안티에일리어싱 없이(mode "1") 흰색으로
(21,7)에 "등록"을 찍는다.

    uv run translate/assets/gen_bagreg.py --out <출력 폴더>
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

INSTALL = Path("/mnt/d/Game/Pokemon Z/V2.18/Graphics/Pictures")
FONT = Path(__file__).parent / "fonts/Galmuri9.ttf"
BODY = (87, 24, 156, 255)


def render():
    im = Image.open(INSTALL / "bagReg.PNG.orig").convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(18, im.width):
            r, g, b, a = px[x, y]
            if r + g + b > 300:
                px[x, y] = BODY
    font = ImageFont.truetype(str(FONT), 9)
    draw = ImageDraw.Draw(im)
    draw.fontmode = "1"  # 안티에일리어싱 없이 — 9px 비트맵 폰트에 필요
    draw.text((21, 7), "등록", font=font, fill=(255, 255, 255, 255))
    return im


def demo():
    """자체 검증: 렌더 결과가 보관소 Controller UX의 bagReg.PNG와 픽셀 단위로 같은지."""
    vault = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/Controller UX/Graphics/Pictures/bagReg.PNG")
    got = render().tobytes()
    want = Image.open(vault).convert("RGBA").tobytes()
    assert got == want, "렌더 결과가 보관소 bagReg.PNG와 다르다"
    print("OK: 픽셀 단위로 보관소 bagReg.PNG와 일치")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="출력 폴더 (미지정 시 자체 검증만)")
    a = ap.parse_args()
    if not a.out:
        demo()
        return
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    render().save(out / "bagReg.PNG")
    print(f"썼다: {out / 'bagReg.PNG'}")


if __name__ == "__main__":
    main()
