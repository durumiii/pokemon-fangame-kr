# 한글에는 합성 굵게를 걸지 않는다 (Ruby 1.8.7)
#
# 폰트에 굵은 판이 없으면 엔진이 글자를 가로로 1픽셀 겹쳐 굵게를 흉내 낸다. 획이 1픽셀인
# 픽셀 폰트에서는 그 겹침이 한글의 속공간을 메워, 「ㅐ」처럼 세로획 둘이 나란한 글자가
# 통째로 검은 사각형이 된다. 라틴 글자는 속공간이 넓어 견딘다.
#
# 그래서 굵게를 **글자별로** 가른다 — 여러 바이트 글자(한글·기호)는 굵게를 끄고, 한 바이트
# 글자(라틴·숫자)는 그대로 둔다. 원본 drawSingleFormattedChar(DrawText 절)에서 그 한 줄만
# 다르고 나머지는 같다. 그림자 겹은 001_Shadow.rb의 pixelShadowLayers를 따른다.

def pixelShadowWide?(ch)
  s = ch[0]
  return false if !s.is_a?(String) || s.length == 0
  b = s.respond_to?(:getbyte) ? s.getbyte(0) : s[0]   # 1.8.7은 Fixnum, 1.9+는 getbyte
  return b >= 0xC0                                    # 여러 바이트 글자
end

def drawSingleFormattedChar(bitmap, ch)
  if ch[5] # If a graphic
    graphic = Bitmap.new(ch[0])
    graphicRect = ch[15]
    bitmap.blt(ch[1], ch[2], graphic, graphicRect, ch[8].alpha)
    graphic.dispose
  else
    if bitmap.font.size != ch[13]
      bitmap.font.size = ch[13]
    end
    if ch[0] != "\n" && ch[0] != "\r" && ch[0] != " " && !isWaitChar(ch[0])
      wantbold = ch[6] && !pixelShadowWide?(ch)
      if bitmap.font.bold != wantbold
        bitmap.font.bold = wantbold
      end
      if bitmap.font.italic != ch[7]
        bitmap.font.italic = ch[7]
      end
      if bitmap.font.name != ch[12]
        bitmap.font.name = ch[12]
      end
      offset = 0
      if ch[9] # shadow
        bitmap.font.color = ch[9]
        if (ch[16] & 1) != 0 # outline
          offset = 1
          for dx in [0, 1, 2]
            for dy in [0, 1, 2]
              next if dx == 1 && dy == 1
              bitmap.draw_text(ch[1] + dx, ch[2] + dy, ch[3] + 2, ch[4], ch[0])
            end
          end
        elsif (ch[16] & 2) != 0 # outline 2
          offset = 2
          for dx in [0, 2, 4]
            for dy in [0, 2, 4]
              next if dx == 2 && dy == 2
              bitmap.draw_text(ch[1] + dx, ch[2] + dy, ch[3] + 4, ch[4], ch[0])
            end
          end
        else
          faint = pixelShadowFaint(ch[9])
          for layer in pixelShadowLayers
            bitmap.font.color = layer[2] ? faint : ch[9]
            bitmap.draw_text(ch[1] + layer[0], ch[2] + layer[1], ch[3] + 2, ch[4], ch[0])
          end
        end
      end
      if bitmap.font.color != ch[8]
        bitmap.font.color = ch[8]
      end
      bitmap.draw_text(ch[1] + offset, ch[2] + offset, ch[3], ch[4], ch[0])
    else
      if bitmap.font.color != ch[8]
        bitmap.font.color = ch[8]
      end
    end
    if ch[10] # underline
      bitmap.fill_rect(ch[1], ch[2] + ch[4] - [(ch[4] - bitmap.font.size) / 2, 0].max - 2,
         ch[3] - 2, 2, ch[8])
    end
    if ch[11] # strikeout
      bitmap.fill_rect(ch[1], ch[2] + (ch[4] / 2), ch[3] - 2, 2, ch[8])
    end
  end
end
