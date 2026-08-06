# 대화창 본문의 그림자도 같은 겹 규칙으로 (Ruby 1.8.7)
#
# 메뉴·라벨은 SpriteWindow 절이, 대화창 본문은 DrawText 절의 이 함수가 그린다.
# 겹 목록은 001_Shadow.rb의 pixelShadowLayers가 정한다 — 두께는 거기서 한 번에 바꾼다.

def renderLineBrokenChunksWithShadow(bitmap, xDst, yDst, normtext, maxheight, baseColor, shadowColor)
  layers = pixelShadowLayers
  faint = pixelShadowFaint(shadowColor)
  for i in 0...normtext.length
    width = normtext[i][3]
    textx = normtext[i][1] + xDst
    texty = normtext[i][2] + yDst
    if maxheight == 0 || normtext[i][2] < maxheight
      height = normtext[i][4]
      text = normtext[i][0]
      for layer in layers
        bitmap.font.color = layer[2] ? faint : shadowColor
        bitmap.draw_text(textx + layer[0], texty + layer[1], width + 2, height, text)
      end
      bitmap.font.color = baseColor
      bitmap.draw_text(textx, texty, width + 2, height, text)
    end
  end
end
