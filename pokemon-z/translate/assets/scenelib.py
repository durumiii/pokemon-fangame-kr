"""글자 제거 공용부: 연결 성분 판정(승인된 proto_body 방식) + 보조 도구."""
from PIL import Image
from collections import Counter, deque

TEXT_W = (248, 248, 248, 255)
TEXT_O = (72, 80, 88, 255)

def achromatic(p, thr=18):
    r, g, b, a = p
    return max(r, g, b) - min(r, g, b) < thr

def strip_text(im, bg=None, protect=(), force_boxes=None):
    """bg/투명이 아닌 픽셀을 8방향 성분으로 묶어 전부 무채색이면 제거.
    protect: 통째 보존할 사각형 목록. force_boxes: 이 안에서는 무채색 픽셀을 성분과
    무관하게 제거(글자가 스프라이트에 붙은 자리)."""
    W, H = im.size
    op = im.load()
    if bg is None:
        bg = Counter(im.get_flattened_data()).most_common(1)[0][0]
    out = Image.new("RGBA", (W, H), bg)
    np_ = out.load()
    for y in range(H):          # 원본의 투명 영역(판 바깥 테두리)은 투명 그대로 둔다
        for x in range(W):
            if op[x, y][3] < 20:
                np_[x, y] = op[x, y]
    seen = bytearray(W * H)
    for y0 in range(H):
        for x0 in range(W):
            if seen[y0 * W + x0]:
                continue
            p = op[x0, y0]
            if p[3] < 20 or p == bg:
                seen[y0 * W + x0] = 1
                continue
            comp = []
            colored = False
            q = deque([(x0, y0)])
            seen[y0 * W + x0] = 1
            while q:
                x, y = q.popleft()
                pp = op[x, y]
                comp.append((x, y, pp))
                if not achromatic(pp):
                    colored = True
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx]:
                        p2 = op[nx, ny]
                        if p2[3] >= 20 and p2 != bg:
                            seen[ny * W + nx] = 1
                            q.append((nx, ny))
            if colored:
                for x, y, pp in comp:
                    np_[x, y] = pp
    for (x0, y0, x1, y1) in protect:
        for y in range(y0, y1):
            for x in range(x0, x1):
                np_[x, y] = op[x, y]
    if force_boxes:
        for (x0, y0, x1, y1) in force_boxes:
            for y in range(y0, y1):
                for x in range(x0, x1):
                    if np_[x, y] in (TEXT_W, TEXT_O):
                        np_[x, y] = bg
    return out, bg


def thick_mask(im, size=9):
    """글자 색 픽셀 중 굵은 덩어리(스프라이트 몸통)만 남긴 마스크."""
    from PIL import Image, ImageFilter
    W, H = im.size
    px = im.load()
    m = Image.new("L", (W, H), 0)
    mp = m.load()
    for y in range(H):
        for x in range(W):
            if px[x, y] in (TEXT_W, TEXT_O):
                mp[x, y] = 255
    return m.filter(ImageFilter.MinFilter(size)).filter(ImageFilter.MaxFilter(size)).load()


def despeckle(out, bg, boxes, max_area=200):
    """상자 안에 남은 작은 글자 조각(스프라이트에 안 붙은 섬)을 지운다."""
    W, H = out.size
    op = out.load()
    seen = bytearray(W * H)
    for (a, b, c, d) in boxes:
        for y0 in range(b, d):
            for x0 in range(a, c):
                if seen[y0 * W + x0] or op[x0, y0] == bg or op[x0, y0][3] < 20:
                    continue
                comp = []
                q = deque([(x0, y0)])
                seen[y0 * W + x0] = 1
                while q and len(comp) <= max_area:
                    x, y = q.popleft()
                    comp.append((x, y))
                    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx]:
                            p2 = op[nx, ny]
                            if p2 != bg and p2[3] >= 20:
                                seen[ny * W + nx] = 1
                                q.append((nx, ny))
                if len(comp) <= max_area:
                    for x, y in comp:
                        op[x, y] = bg


def strip_lines(im, lines, h=28, pad=2, thick=9, speck=200):
    """대각선 셋(diploma 계열): 성분 판정 + 줄 상자 안 얇은 글자 제거 + 조각 청소."""
    out, bg = strip_text(im)
    tk = thick_mask(im, thick)
    op = out.load()
    boxes = [(x0 - pad, y, x1 + pad + 1, y + h) for (y, x0, x1) in lines]
    for (a, b, c, d) in boxes:
        for y in range(b, d):
            for x in range(a, c):
                if op[x, y] in (TEXT_W, TEXT_O) and not tk[x, y]:
                    op[x, y] = bg
    despeckle(out, bg, boxes, speck)
    return out, bg
