# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow"]
# ///
"""타이틀 카드류 그림 자산 생성기 (Z-74 간단 부류).

문안 원장(translate/data/asset-texts.jsonl)의 ko가 채워진 카드형 파일을,
원본의 글자 자리에 고운바탕 볼드로 조판해 찍는다. 검정 테 3px 여부는 하드코딩이
아니라 원본 글자에 어두운 윤곽이 실재하는지로 파일마다 판별한다(has_outline).
원본(스페인어)은 설치본 `.orig` 또는 설치본 파일이 정본이다.

    uv run translate/assets/gen_cards.py --out <출력 폴더> [--sheets]

--sheets 를 주면 원본과 나란히 놓은 검수 시트도 함께 낸다.
introTexto0·1은 원본이 금색이라 채움색을 원본에서 표집해 따른다.
"""
import argparse, json, re, statistics, sys
from collections import Counter
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "translate/data/asset-texts.jsonl"
INSTALL = Path("/mnt/d/Game/Pokemon Z/V2.18/Graphics/Pictures")
FONT = Path(__file__).parent / "fonts/GowunBatang-Bold.ttf"
CARD_KINDS = ("title-name","title-epithet","title-place")
CARD_FILES_EXTRA = {"cartelActo1.png","cartelActo2.png","cartelActo3.png","cartelFinal1.png",
                    "cartelFinal2.png","introTexto0.png","introTexto1.png","prisionRot.png",
                    "sitioArma1.png","sitioArma2.png","sitioArma3.png"} | \
                   {f"introText{i}.png" for i in range(1,9)} | \
                   {f"rotMazmorra{i}.png" for i in range(1,9)} | \
                   {"rot2F3.png","rot2Lider7.png","rot2Loto.png","rotAZ.png","rotAZ2.png",
                    "rotAlcaFinal2.png","rotAlcafinal.png"}

def src_path(name):
    o = INSTALL / (name + ".orig")
    return o if o.exists() else INSTALL / name

def sample_fill(im, bb):
    """원본 글자 몸통색 표집 — 불투명 픽셀 중 최빈색(테두리 제외를 위해 밝은 쪽 우선)."""
    from collections import Counter
    c = Counter()
    for y in range(bb[1], bb[3], 2):
        for x in range(bb[0], bb[2], 2):
            p = im.getpixel((x, y))
            if p[3] > 200:
                c[p[:3]] += 1
    if not c: return (255,255,255)
    top = c.most_common(6)
    light = [k for k,_ in top if sum(k) > 330]
    return light[0] if light else top[0][0]

def sample_gold(im, bb):
    """강조(«») 색 표집 — 불투명 픽셀 중 노란빛(R·G 높고 B 낮음) 최빈색."""
    from collections import Counter
    c = Counter()
    for y in range(bb[1], bb[3], 2):
        for x in range(bb[0], bb[2], 2):
            p = im.getpixel((x, y))
            if p[3] > 200 and p[0] > 150 and p[1] > 130 and p[2] < 120:
                c[p[:3]] += 1
    return c.most_common(1)[0][0] if c else None

def _gold_fallback():
    """개별 표집이 실패했을 때 쓸 공용 강조색 — introText1 표집값."""
    if not hasattr(_gold_fallback, "_v"):
        im = Image.open(src_path("introText1.png")).convert("RGBA")
        bb = im.getchannel("A").getbbox()
        _gold_fallback._v = sample_gold(im, bb) or (255,216,0)
    return _gold_fallback._v

def ink_of(im):
    """원본에서 글자 자리·바탕판·글자 픽셀을 뽑는다.

    투명 바탕 그림은 알파 bbox가 곧 글자 자리다. cartelActo처럼 판 전체가 불투명한
    그림은 알파 bbox가 그림 전체라 크기 산정이 망가지므로, 최빈색을 바탕으로 보고
    그와 다른 픽셀의 bbox를 글자 자리로 삼는다(그 최빈색이 새로 그릴 바탕판이 된다).
    """
    px = list(im.get_flattened_data())
    modal = Counter(px).most_common(1)[0][0]
    if modal[3] > 200:
        d = ImageChops.difference(im.convert("RGB"), Image.new("RGB", im.size, modal[:3]))
        m = d.convert("L").point(lambda v: 255 if v > 20 else 0)
        bb = m.getbbox()
        ink = [p for p, q in zip(px, m.get_flattened_data()) if q]
        return bb, Image.new("RGBA", im.size, modal), ink
    bb = im.getchannel("A").getbbox()
    return bb, None, [p for p in px if p[3] > 200]

def has_outline(ink):
    """원본 글자에 어두운 테(윤곽)가 실재하는지 — 글자 픽셀 중 어두운 쪽 비율로 판정.

    실측(57장)은 0% 아니면 58~71%로 갈려 중간이 없다. 인트로·cartel 계열은 0%,
    rot 계열은 60% 안팎이다.
    """
    if not ink: return False
    return sum(1 for p in ink if sum(p[:3]) < 200) / len(ink) > 0.2

# 크기는 클래스마다 고정한다 — 원문 줄 수에 따라 글자가 멋대로 커지던 것을 막는다.
# 대표 원본 한 장에서 글줄 한 줄의 픽셀 높이를 실측하고 ×1.15(한글 보정)한 값을 쓴다.
CLASS_REP = {"이름 카드": "rot10Cendera1.png", "칭호 카드": "rot10Cendera2.png",
             "던전 카드": "rotMazmorra1.png",  "소재지": "sitioArma1.png",
             "막 표지": "cartelActo1.png",     "인트로": "introText1.png",
             "지방 표제": "introTexto0.png"}   # KALOS류 — 인트로 본문보다 크다 (유지자 2026-08-19)

def card_class(name, kind):
    if name.startswith("rotMazmorra") or name == "prisionRot.png": return "던전 카드"
    if name.startswith("sitioArma"): return "소재지"
    if name.startswith("cartel"):    return "막 표지"
    if name.startswith("introTexto"): return "지방 표제"
    if name.startswith("introText"): return "인트로"
    return "칭호 카드" if kind == "title-epithet" else "이름 카드"

def line_height(name):
    """원본 글줄 한 줄의 픽셀 높이 — 줄마다 재서 중앙값을 쓴다(강세부호 낀 줄 보정)."""
    im = Image.open(src_path(name)).convert("RGBA")
    bb, plate, _ = ink_of(im)
    m = (ImageChops.difference(im.convert("RGB"),
         Image.new("RGB", im.size, plate.getpixel((0,0))[:3])).convert("L").point(lambda v: 255 if v>20 else 0)
         if plate else im.getchannel("A").point(lambda v: 255 if v>200 else 0))
    ml = m.load()
    bands = []; s = None
    for y in range(bb[1], bb[3]):
        on = any(ml[x,y] for x in range(bb[0], bb[2]))
        if on and s is None: s = y
        if not on and s is not None: bands.append(y-s); s = None
    if s is not None: bands.append(bb[3]-s)
    return statistics.median(bands or [bb[3]-bb[1]])

def class_sizes():
    if not hasattr(class_sizes, "_v"):
        class_sizes._v = {}
        for cls, rep in CLASS_REP.items():
            h = line_height(rep)
            class_sizes._v[cls] = round(h*1.15)
            print(f"클래스 {cls}: 대표 {rep} 글줄 높이 {h:.0f}px → 고정 크기 {class_sizes._v[cls]}px")
    return class_sizes._v

def clean(l):
    """«»는 조판되지 않는 강조 마크업 — 폭 측정·정렬용으로 벗겨낸 텍스트."""
    return l.replace("«","").replace("»","")

def segments(l):
    """줄을 (텍스트, 강조여부) 조각으로 쪼갠다. «» 문자 자체는 버린다."""
    return [(m.group(1), True) if m.group(1) is not None else (m.group(2), False)
            for m in re.finditer(r"«([^»]*)»|([^«»]+)", l)]

def render(name, ko, kind=""):
    im = Image.open(src_path(name)).convert("RGBA")
    W, H = im.size
    bb, plate, ink = ink_of(im)
    if bb is None: raise ValueError(f"{name}: 글자 없음")
    fill = sample_fill(im, bb) + (255,)
    gold = (sample_gold(im, bb) or _gold_fallback()) + (255,)
    outline = has_outline(ink)
    stroke = 3 if outline else 0
    print(f"  {name}: 테 {'있음' if outline else '없음'}"
          f"(어두운 비율 {100*sum(1 for p in ink if sum(p[:3])<200)/max(1,len(ink)):.1f}%)"
          f" · 글자자리 {bb} · 바탕판 {'있음' if plate else '없음'}")
    lines = ko.split("\n")
    cx=(bb[0]+bb[2])//2; cy=(bb[1]+bb[3])//2
    out = plate.copy() if plate else Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(out)
    cls = card_class(name, kind)
    base = size = class_sizes()[cls]
    while size > 8:
        f = ImageFont.truetype(str(FONT), size)
        if max(d.textbbox((0,0),clean(l),font=f,stroke_width=stroke)[2] for l in lines if l.strip()) <= W-30:
            break
        size -= 2
    if size != base:
        print(f"  {name}: 폭 넘쳐 {cls} 고정 {base}px → {size}px로 줄임")
    lh = int(size*1.08)
    total = lh*len(lines)
    y = max(6, min(cy-total//2, H-total-6))
    for l in lines:
        if l.strip():
            b = d.textbbox((0,0),clean(l),font=f,stroke_width=stroke)
            x = cx-(b[2]-b[0])//2-b[0]
            for text, is_gold in segments(l):
                d.text((x, y-b[1]), text, font=f, fill=gold if is_gold else fill,
                       stroke_width=stroke, stroke_fill=(0,0,0,255))
                x += d.textlength(text, font=f)
        y += lh
    return im, out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sheets", action="store_true")
    a = ap.parse_args()
    outd = Path(a.out); outd.mkdir(parents=True, exist_ok=True)
    if a.sheets: (outd/"sheets").mkdir(exist_ok=True)
    n = skip = 0
    for line in LEDGER.open(encoding="utf-8"):
        r = json.loads(line)
        name, ko = r["file"], r.get("ko")
        if not (r.get("kind","").startswith("title") or name in CARD_FILES_EXTRA):
            continue
        if not ko:
            print(f"SKIP {name}: ko 미기입"); skip += 1; continue
        src, out = render(name, ko, r.get("kind",""))
        out.save(outd/name)
        if a.sheets:
            W,H = src.size
            sheet = Image.new("RGB",(W*2,H),(235,235,240))
            sheet.paste(src,(0,0),src); sheet.paste(out,(W,0),out)
            sheet.save(outd/"sheets"/f"{name[:-4]}_sheet.png")
        n += 1
    print(f"생성 {n} · 건너뜀 {skip}")

if __name__ == "__main__":
    main()
