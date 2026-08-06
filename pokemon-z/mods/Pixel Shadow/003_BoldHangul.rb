# 한글 굵게를 「반 픽셀」만큼만 (Ruby 1.8.7)
#
# 폰트에 굵은 판이 없으면 엔진은 글자를 가로로 1픽셀 겹쳐 굵게를 흉내 낸다. 획이 1픽셀인
# 픽셀 폰트에서는 그 겹침이 한글의 세로 틈을 그대로 메워, 「배」·「대」의 ㅐ가 덩어리가 된다.
#
# 픽셀 사이 값은 그릴 수 없으니 **옅게 겹쳐서** 만든다 — 오른쪽 1픽셀 자리에 같은 글자를
# 반투명으로 한 겹 얹는다. 획은 굵어 보이고, 틈은 메워지는 대신 반톤으로 남아 글자 모양이
# 살아 있다. 세로로 겹치는 방식도 재 봤지만(세로 틈은 완벽히 남는다) 획의 무게가 아래로
# 쏠려 어색해 버렸다(2026-08-07 유지자 판정).
#
# PIXEL_BOLD_SIDE  = 겹치는 자리 :right(가로) 또는 :diag(대각)
# PIXEL_BOLD_ALPHA = 그 겹의 진하기 0~255. 0이면 굵게를 아예 걸지 않는다(=포기).
#                    80 옅게 · 110 보통 · 150 진하게 · 255면 엔진 기본과 같아진다.
# 라틴·숫자는 속이 넓어 엔진 기본(가로 1픽셀)을 그대로 쓴다.

PIXEL_BOLD_SIDE = :right
PIXEL_BOLD_ALPHA = 110

def pixelShadowWide?(ch)
  s = ch[0]
  return false if !s.is_a?(String) || s.length == 0
  b = s.respond_to?(:getbyte) ? s.getbyte(0) : s[0]   # 1.8.7은 Fixnum, 1.9+는 getbyte
  return b >= 0xC0                                    # 여러 바이트 글자(한글·기호)
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
      # 한글 굵게는 우리가 세로로 겹쳐 만든다 — 엔진의 가로 겹침은 끈다
      fatten = ch[6] && pixelShadowWide?(ch)      # 한글 굵게는 우리가 반겹으로 만든다
      wantbold = fatten ? false : ch[6]
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
      if fatten && PIXEL_BOLD_ALPHA > 0
        half = Color.new(ch[8].red, ch[8].green, ch[8].blue, PIXEL_BOLD_ALPHA)
        dx = 1
        dy = (PIXEL_BOLD_SIDE == :diag) ? 1 : 0
        bitmap.font.color = half
        bitmap.draw_text(ch[1] + offset + dx, ch[2] + offset + dy, ch[3], ch[4], ch[0])
        bitmap.font.color = ch[8]
      end
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
