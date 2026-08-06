# Pixel Shadow — 글자 그림자 두께 (Ruby 1.8.7)
#
# 게임은 글자를 그림자 색으로 세 번(오른쪽·아래·대각) 찍고 그 위에 본 글자를 얹는다.
# 원판 오프셋 2픽셀은 획이 굵은 포켓몬 폰트에 맞춘 값이라, 획이 1픽셀인 픽셀 폰트에서는
# 그림자가 글자보다 두꺼워 보인다.
#
# **픽셀 사이 값은 없다** — draw_text의 좌표는 정수라 1.5픽셀은 그릴 수 없다. 대신 두께는
# 「몇 겹을 어디에 찍는가」와 「얼마나 진하게 찍는가」로 만든다. 아래 넷 중에 고른다.
#
#   :thin   1픽셀 세 겹                      — 가장 얇다
#   :soft   1픽셀 세 겹 + 2픽셀 대각을 옅게   — 1과 2 사이 (1.5쯤)
#   :step   1픽셀 세 겹 + 2픽셀 오른쪽·아래   — 2에 가깝되 대각이 비어 덜 뭉친다 (1.75쯤)
#   :thick  2픽셀 세 겹                      — 원판 그대로
#
# ⚠ :soft는 반투명을 쓰므로 mkxp.json의 solidFonts가 켜져 있으면 효과가 없다
#   (알파 블렌딩을 끄는 옵션이라 옅은 겹이 진하게 찍힌다).

PIXEL_SHADOW_STYLE = :soft
PIXEL_SHADOW_FAINT = 48          # :soft의 바깥 겹 알파 (0~255)

def pixelShadowFaint(color)
  return Color.new(color.red, color.green, color.blue, PIXEL_SHADOW_FAINT)
end

# 그림자 겹을 [dx, dy, 옅음?] 목록으로 돌려준다.
def pixelShadowLayers
  case PIXEL_SHADOW_STYLE
  when :thin  then return [[1, 0, false], [0, 1, false], [1, 1, false]]
  when :soft  then return [[1, 0, false], [0, 1, false], [1, 1, false], [2, 2, true]]
  when :step  then return [[1, 0, false], [0, 1, false], [1, 1, false],
                           [2, 0, true],  [0, 2, true]]
  else             return [[2, 0, false], [0, 2, false], [2, 2, false]]
  end
end

def pbDrawShadowText(bitmap, x, y, width, height, string, baseColor, shadowColor = nil, align = 0)
  return if !bitmap || !string
  width  = (width < 0)  ? bitmap.text_size(string).width + 4  : width
  height = (height < 0) ? bitmap.text_size(string).height + 4 : height
  if shadowColor
    faint = pixelShadowFaint(shadowColor)
    for layer in pixelShadowLayers
      bitmap.font.color = layer[2] ? faint : shadowColor
      bitmap.draw_text(x + layer[0], y + layer[1], width, height, string, align)
    end
  end
  if baseColor
    bitmap.font.color = baseColor
    bitmap.draw_text(x, y, width, height, string, align)
  end
end

def pbDrawOutlineText(bitmap, x, y, width, height, string, baseColor, shadowColor = nil, align = 0)
  return if !bitmap || !string
  d = (PIXEL_SHADOW_STYLE == :thick) ? 2 : 1
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
