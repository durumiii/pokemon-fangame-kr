# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow"]
# ///
"""배경·스프라이트가 있는 그림 자산 8장의 한국어판을 만든다 (Z-74).

글자 제거는 승인된 연결 성분 방식(scenelib.strip_text)을 쓰고, 스프라이트에 글자가
붙어 성분이 합쳐진 자리(diploma 계열)만 줄 상자 안에서 얇은 획을 추가로 걷는다.
UI 판(cartaBayas·namingControls·icon_register)은 상자 색이 유채색이라 성분 판정이
안 먹으므로 라벨 자리를 바탕색으로 덮는다.

문안은 translate/data/asset-texts.jsonl 의 ko 칸이 정본이며 이 스크립트는 읽기만 한다.
"""
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SC = Path("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr"
          "/cb96cd66-0e0a-4e10-8e5f-614e8ecfd6a0/scratchpad")
sys.path.insert(0, str(SC))
from scenelib import strip_lines, strip_text, TEXT_W, TEXT_O  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SRC = SC / "scenes-src"
OUT = SC / "cards"
SHEETS = SC / "sheets"
FONTS = SC / "fonts"
GAL = {14: FONTS / "Galmuri14.ttf", 11: REPO / "runa/fonts/src/Galmuri11.ttf",
       9: FONTS / "Galmuri9.ttf", 7: FONTS / "Galmuri7.ttf"}

TEXTS = {}
for line in (REPO / "translate/data/asset-texts.jsonl").read_text(encoding="utf-8").splitlines():
    o = json.loads(line)
    if o.get("file"):
        TEXTS[o["file"]] = o["ko"]


def font(fam, mult):
    return ImageFont.truetype(str(GAL[fam]), fam * mult)


def wrap(draw, text, f, maxw):
    """어절 단위 줄바꿈. 자구는 그대로 두고 자리만 맞춘다."""
    out, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=f) <= maxw or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def modal(im, box):
    return Counter(im.crop(box).convert("RGBA").get_flattened_data()).most_common(1)[0][0]


def fill(im, box, color):
    ImageDraw.Draw(im).rectangle([box[0], box[1], box[2] - 1, box[3] - 1], fill=color)


def repaint(im, box, colors, bg):
    px = im.load()
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if px[x, y] in colors:
                px[x, y] = bg


# ── 1·2. 튜토리얼 판 두 장 ────────────────────────────────────────────────
def tutorial_legendarios():
    n = "tutorialLegendarios.png"
    im = Image.open(SRC / n).convert("RGBA")
    out, bg = strip_text(im)
    d = ImageDraw.Draw(out)
    f = font(14, 2)
    paras = [p.split("\n") for p in TEXTS[n].split("\n\n")]
    tops = [42, 170, 280]          # 원본 문단 첫 줄 위치
    for top, lines in zip(tops, paras):
        y = top - 4
        for ln in lines:
            for sub in wrap(d, ln, f, 428):
                d.text((41, y), sub, font=f, fill=TEXT_W, stroke_width=2, stroke_fill=TEXT_O)
                y += 32
    return n, im, out


def tutorial_random():
    n = "tutorialRandom.png"
    im = Image.open(SRC / n).convert("RGBA")
    out, bg = strip_text(im)
    px = out.load()
    for y in range(im.height):          # 스프라이트가 없는 판이라 남은 색 글자(머리글)도 건다
        for x in range(im.width):
            if px[x, y][3] >= 20 and px[x, y] != bg:
                px[x, y] = bg
    head_c = (255, 192, 48, 255)
    head_o = (96, 66, 0, 255)
    d = ImageDraw.Draw(out)
    f = font(11, 2)
    lines = TEXTS[n].split("\n")
    d.text((43, 28), lines[0], font=f, fill=head_c, stroke_width=2, stroke_fill=head_o)
    y = 62
    for para in "\n".join(lines[1:]).strip("\n").split("\n\n"):
        for ln in para.split("\n"):
            for sub in wrap(d, ln, f, 430):
                d.text((43, y), sub, font=f, fill=TEXT_W, stroke_width=2, stroke_fill=TEXT_O)
                y += 26
        y += 26
    return n, im, out


# ── 3~5. 상장 셋 ─────────────────────────────────────────────────────────
DIPLOMA = {
    # 파일: (줄 상자 [(y, x0, x1)], 첫 줄 y, 줄 간격)
    "diploma.png": ([(86, 100, 409), (129, 100, 413), (172, 180, 319),
                     (215, 196, 301), (258, 86, 423)], 86, 43),
    "diplomaNuz1.png": ([(71, 100, 409), (114, 67, 450), (157, 180, 319),
                         (200, 196, 301), (243, 86, 423)], 71, 43),
    "diplomaNuz2.png": ([(59, 94, 403), (101, 61, 476), (143, 138, 374),
                         (185, 174, 313), (227, 190, 295), (269, 80, 417)], 59, 42),
}


def diploma(n):
    im = Image.open(SRC / n).convert("RGBA")
    lines_box, y0, pitch = DIPLOMA[n]
    out, bg = strip_lines(im, lines_box)
    d = ImageDraw.Draw(out)
    f = font(14, 2)
    ko = TEXTS[n].split("\n")
    rows = []
    for ln in ko:
        rows += wrap(d, ln, f, 430)
    for i, ln in enumerate(rows):
        w = d.textlength(ln, font=f)
        d.text((256 - w / 2, y0 + pitch * i - 3), ln, font=f,
               fill=TEXT_W, stroke_width=2, stroke_fill=TEXT_O)
    return n, im, out


# ── 6. 열매 카드 ─────────────────────────────────────────────────────────
def carta_bayas():
    n = "cartaBayas.PNG"
    im = Image.open(SRC / n).convert("RGBA")
    out = im.copy()
    head_bg, head_o = (80, 133, 224, 255), (40, 87, 168, 255)
    box_bg, box_o = (154, 192, 255, 255), (107, 151, 225, 255)
    rows = [(76, 124), (132, 180), (188, 236), (244, 292), (300, 348)]
    left, right = (100, 292), (288, 482)
    repaint(out, (60, 32, 240, 68), {TEXT_W, head_o}, head_bg)          # 머리글(포켓볼 아이콘 밖)
    for (a, b) in rows:
        for (x0, x1) in (left, right):
            repaint(out, (x0, a, x1, b), {TEXT_W, box_o}, box_bg)
    d = ImageDraw.Draw(out)
    f = font(9, 2)
    ko = [s for s in TEXTS[n].split("\n")]
    head, rest = ko[0], [s for s in ko[1:] if s.strip()]
    w = d.textlength(head, font=f)
    d.text((148 - w / 2, 40), head, font=f, fill=TEXT_W, stroke_width=1, stroke_fill=head_o)
    for i, (a, b) in enumerate(rows):
        name, color, e1, e2 = rest[i * 4:i * 4 + 4]
        for (cx, txts) in ((197, (name, color)), (385, (e1, e2))):
            for j, t in enumerate(txts):
                w = d.textlength(t, font=f)
                d.text((cx - w / 2, a + 5 + j * 22), t, font=f,
                       fill=TEXT_W, stroke_width=1, stroke_fill=box_o)
    return n, im, out


# ── 7. 이름 입력 조작 띠 ─────────────────────────────────────────────────
# 이 자산은 2배 확대된 도트 그림이라 좌표·글자 크기를 모두 짝수로 맞춘다.
# (라벨키, 지울 상자, 그 자리 바탕색, 글자색, 테색, 글꼴족)
# 글꼴족 7=14px·9=18px. 띠는 높이 14px, 금색 버튼은 폭 52px이라 14px까지만 들어간다.
NC_SPOTS = [
    ("f5",  (92, 4, 162, 18),  (80, 176, 200, 255), (240, 240, 224, 255), None, 7),
    ("x",   (300, 4, 372, 18), (208, 136, 192, 255), (240, 240, 224, 255), None, 7),
    ("z",   (382, 4, 452, 18), (184, 144, 224, 255), (240, 240, 224, 255), None, 7),
    ("up",  (36, 28, 88, 64),  (200, 168, 64, 255), (248, 248, 248, 255), (56, 80, 96, 255), 7),
    ("low", (100, 28, 152, 64), (200, 168, 64, 255), (248, 248, 248, 255), (56, 80, 96, 255), 7),
    ("etc", (164, 28, 216, 64), (200, 168, 64, 255), (248, 248, 248, 255), (56, 80, 96, 255), 7),
    ("del", (302, 30, 364, 62), (232, 128, 208, 255), (248, 248, 248, 255), (56, 80, 96, 255), 9),
    ("fin", (382, 30, 444, 62), (200, 144, 248, 255), (248, 248, 248, 255), (56, 80, 96, 255), 9),
]


def naming_controls():
    n = "namingControls.png"
    im = Image.open(SRC / n).convert("RGBA")
    out = im.copy()
    label = dict(zip(["f5", "x", "z", "up", "low", "etc", "del", "fin"], TEXTS[n].split("\n")))
    d = ImageDraw.Draw(out)
    over = []
    for key, box, bgc, fg, stroke, fam in NC_SPOTS:
        f = font(fam, 2)
        fill(out, box, bgc)
        t = label[key]
        w = d.textlength(t, font=f)
        if w > box[2] - box[0]:
            over.append((key, t, round(w), box[2] - box[0]))
        x = box[0] + round((box[2] - box[0] - w) / 2)
        ink = 16 if f.size == 18 else 12
        y = box[1] + (box[3] - box[1] - ink) // 2 - 2
        kw = dict(stroke_width=1, stroke_fill=stroke) if stroke else {}
        d.text((x, y), t, font=f, fill=fg, **kw)
    return n, im, out, over


# ── 8. 등록 버튼 ─────────────────────────────────────────────────────────
def icon_register():
    n = "icon_register.PNG"
    im = Image.open(SRC / n).convert("RGBA")
    out = im.copy()
    d = ImageDraw.Draw(out)
    f = font(7, 2)
    t = TEXTS[n].split("\n")[0]
    over = []
    for box, bgc in (((20, 4, 52, 20), (160, 88, 232, 255)),
                     ((20, 28, 52, 44), (186, 186, 186, 255))):
        fill(out, box, bgc)
        w = d.textlength(t, font=f)
        if w > box[2] - box[0]:
            over.append((t, round(w), box[2] - box[0]))
        d.text((box[0] + round((box[2] - box[0] - w) / 2), box[1] - 2), t,
               font=f, fill=(255, 255, 255, 255))
    return n, im, out, over


def sheet(name, before, after):
    k = 2 if before.width > 200 else 6
    W, H = before.width * k, before.height * k
    canvas = Image.new("RGB", (W * 2 + 24, H + 16), (32, 32, 40))
    for i, im in enumerate((before, after)):
        chk = Image.new("RGBA", im.size, (255, 0, 255, 255))
        chk.alpha_composite(im)
        canvas.paste(chk.convert("RGB").resize((W, H), Image.NEAREST), (8 + i * (W + 8), 8))
    canvas.save(SHEETS / f"{Path(name).stem}_sheet.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    SHEETS.mkdir(parents=True, exist_ok=True)
    jobs = [tutorial_legendarios(), tutorial_random(),
            diploma("diploma.png"), diploma("diplomaNuz1.png"), diploma("diplomaNuz2.png"),
            carta_bayas(), naming_controls(), icon_register()]
    for job in jobs:
        n, before, after = job[0], job[1], job[2]
        after.save(OUT / n)
        sheet(n, before, after)
        note = f"  overflow={job[3]}" if len(job) > 3 and job[3] else ""
        print(f"{n} 저장{note}")


if __name__ == "__main__":
    main()


def check():
    """자구 점검: 그린 줄을 다시 합치면 원장 ko와 (공백만 빼고) 같아야 한다."""
    from PIL import Image as _I
    d = ImageDraw.Draw(_I.new("RGBA", (1, 1)))
    cases = [("tutorialLegendarios.png", font(14, 2), 428),
             ("tutorialRandom.png", font(11, 2), 430),
             ("diploma.png", font(14, 2), 430),
             ("diplomaNuz1.png", font(14, 2), 430),
             ("diplomaNuz2.png", font(14, 2), 430)]
    for name, f, mw in cases:
        drawn = []
        for ln in TEXTS[name].split("\n"):
            drawn += wrap(d, ln, f, mw) if ln.strip() else []
        got = " ".join(" ".join(drawn).split())
        want = " ".join(TEXTS[name].split())
        assert got == want, (name, got, want)
    for name in ("cartaBayas.PNG", "namingControls.png", "icon_register.PNG"):
        assert TEXTS[name].strip(), name
    print("자구 점검 통과")
