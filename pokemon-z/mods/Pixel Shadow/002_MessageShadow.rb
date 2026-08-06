# 대화창 본문의 그림자도 같은 오프셋으로 (Ruby 1.8.7)
#
# 메뉴·라벨은 SpriteWindow 절이 그리고, 대화창 본문은 DrawText 절의 이 함수가 그린다.
# 오프셋만 PIXEL_SHADOW_OFFSET으로 바꾸고 나머지는 원본 그대로다.

def renderLineBrokenChunksWithShadow(bitmap, xDst, yDst, normtext, maxheight, baseColor, shadowColor)
  d = PIXEL_SHADOW_OFFSET
  for i in 0...normtext.length
    width = normtext[i][3]
    textx = normtext[i][1] + xDst
    texty = normtext[i][2] + yDst
    if maxheight == 0 || normtext[i][2] < maxheight
      height = normtext[i][4]
      text = normtext[i][0]
      bitmap.font.color = shadowColor
      bitmap.draw_text(textx + d, texty,     width + 2, height, text)
      bitmap.draw_text(textx,     texty + d, width + 2, height, text)
      bitmap.draw_text(textx + d, texty + d, width + 2, height, text)
      bitmap.font.color = baseColor
      bitmap.draw_text(textx, texty, width + 2, height, text)
    end
  end
end
