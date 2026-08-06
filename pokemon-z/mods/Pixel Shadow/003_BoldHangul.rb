# 한글 굵게를 세로로 겹친다 (Ruby 1.8.7)
#
# 폰트에 굵은 판이 없으면 엔진은 글자를 **가로로** 1픽셀 겹쳐 굵게를 흉내 낸다. 획이
# 1픽셀인 픽셀 폰트에서는 그 겹침이 한글의 세로 틈을 메워, 「배」·「대」처럼 ㅐ가 든 글자가
# 통째로 덩어리가 된다. 굵게를 끄는 대신 **겹치는 방향을 세로로 돌린다** — 굵기는 그대로
# 얻고 세로 틈은 살아남는다.
#
# 실측(번역문에서 자주 쓰는 한글 300자, 2026-08-07):
#   24px  가로 겹침: 세로 틈이 사라진 글자 43 · 가로 틈 0
#         세로 겹침: 세로 틈이 사라진 글자  0 · 가로 틈 8
#   22px  가로 겹침: 47 · 37      세로 겹침: 34 · 129
# 게임이 지정하는 크기는 24가 가장 많다. 가로 틈은 받침 있는 글자에서 조금 좁아지지만
# 세로 틈이 메워질 때처럼 글자가 뭉개지지는 않는다.
#
# 라틴·숫자는 속이 넓어 엔진 기본(가로 겹침)으로 둔다.

PIXEL_BOLD_VERTICAL = true      # false면 엔진 기본 그대로

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
      fatten = PIXEL_BOLD_VERTICAL && ch[6] && pixelShadowWide?(ch)
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
            bitmap.draw_text(ch[1] + layer[0], ch[2] + layer[1] + 1, ch[3] + 2, ch[4], ch[0]) if fatten
          end
        end
      end
      if bitmap.font.color != ch[8]
        bitmap.font.color = ch[8]
      end
      bitmap.draw_text(ch[1] + offset, ch[2] + offset, ch[3], ch[4], ch[0])
      bitmap.draw_text(ch[1] + offset, ch[2] + offset + 1, ch[3], ch[4], ch[0]) if fatten
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
