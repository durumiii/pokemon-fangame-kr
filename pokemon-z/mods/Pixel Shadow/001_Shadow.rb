# Pixel Shadow — 글자 그림자를 1픽셀로 (Ruby 1.8.7)
#
# 게임은 글자를 그림자 색으로 세 번(오른쪽·아래·대각) 찍고 그 위에 본 글자를 얹는다.
# 오프셋이 2픽셀이라 획이 굵은 원판 포켓몬 폰트에는 맞았지만, 획이 1픽셀인 픽셀 폰트에서는
# 그림자가 글자보다 두꺼워 보인다. 오프셋만 1로 내린다 — 그리는 방식은 원본 그대로다.
#
# 원본: SpriteWindow 절의 pbDrawShadowText·pbDrawOutlineText, DrawText 절의
# renderLineBrokenChunksWithShadow. 나중 정의가 이기므로 같은 이름으로 다시 정의한다.

PIXEL_SHADOW_OFFSET = 1

def pbDrawShadowText(bitmap, x, y, width, height, string, baseColor, shadowColor = nil, align = 0)
  return if !bitmap || !string
  d = PIXEL_SHADOW_OFFSET
  width  = (width < 0)  ? bitmap.text_size(string).width + 4  : width
  height = (height < 0) ? bitmap.text_size(string).height + 4 : height
  if shadowColor
    bitmap.font.color = shadowColor
    bitmap.draw_text(x + d, y,     width, height, string, align)
    bitmap.draw_text(x,     y + d, width, height, string, align)
    bitmap.draw_text(x + d, y + d, width, height, string, align)
  end
  if baseColor
    bitmap.font.color = baseColor
    bitmap.draw_text(x, y, width, height, string, align)
  end
end

def pbDrawOutlineText(bitmap, x, y, width, height, string, baseColor, shadowColor = nil, align = 0)
  return if !bitmap || !string
  d = PIXEL_SHADOW_OFFSET
  width  = (width < 0)  ? bitmap.text_size(string).width + 4  : width
  height = (height < 0) ? bitmap.text_size(string).height + 4 : height
  if shadowColor
    bitmap.font.color = shadowColor
    bitmap.draw_text(x - d, y - d, width, height, string, align)
    bitmap.draw_text(x,     y - d, width, height, string, align)
    bitmap.draw_text(x + d, y - d, width, height, string, align)
    bitmap.draw_text(x - d, y,     width, height, string, align)
    bitmap.draw_text(x + d, y,     width, height, string, align)
    bitmap.draw_text(x - d, y + d, width, height, string, align)
    bitmap.draw_text(x,     y + d, width, height, string, align)
    bitmap.draw_text(x + d, y + d, width, height, string, align)
  end
  if baseColor
    bitmap.font.color = baseColor
    bitmap.draw_text(x, y, width, height, string, align)
  end
end
