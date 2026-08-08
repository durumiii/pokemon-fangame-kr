# 한글 굵게를 엔진과 같은 방식으로, 한 눈금 덜 (Ruby 1.8.7)
#
# 엔진의 굵게는 SDL_ttf가 한다. 글리프의 폭을 **글자 크기의 10분의 1**만큼 늘려 다시
# 래스터화하고 자간도 그만큼 넓힌다(SDL_ttf: `glyph_overhang = y_ppem / 10`,
# `sz_width += overhang`, `advance += overhang`). 그러니 굵어지는 양이 크기에 비례한다 —
# 22픽셀 글자면 2픽셀, 32픽셀이면 3픽셀이다.
#
# 획이 1픽셀인 픽셀 폰트에서는 그 두께가 한글의 세로 틈을 메워 「배」·「대」의 ㅐ가
# 덩어리가 된다. 그래서 **방식은 엔진과 같게 두되 양만 덜어낸다** — 같은 글자를 오른쪽으로
# 1픽셀씩 옮겨 가며 겹쳐 폭을 넓히되, 엔진이 쓰는 폭에서 `PIXEL_BOLD_TRIM`만큼 뺀다.
#
# ⚠ 예전 판은 「오른쪽 1픽셀에 반투명 한 겹」이었다. 그 주석에 「255면 엔진 기본과 같아진다」고
# 적혀 있었으나 **사실이 아니다** — 양(늘 1픽셀 대 크기 비례)·만드는 시점(래스터화 뒤 겹치기
# 대 래스터화 전 폭 넓히기)·자간(우리는 못 건드림)이 모두 다르다(2026-08-07 실기·소스 확인).
#
# PIXEL_BOLD_ENGINE = 참이면 한글도 엔진 기본 굵게를 그대로 쓴다(견주어 보기용).
# PIXEL_BOLD_TRIM   = 엔진 폭에서 뺄 픽셀 수. 1이면 늘 엔진보다 한 눈금 얇다. 0이면 같은 양.
# PIXEL_BOLD_ALPHA  = 덜어낸 자리에 얹는 바깥 한 겹의 진하기 0~255. 0이면 안 얹는다 —
#                     엔진과 우리 사이의 반 눈금을 이걸로 만든다.
# PIXEL_BOLD_SIDE   = :right(가로) 또는 :diag(대각). 대각은 무게가 아래로 쏠린다.
# 라틴·숫자는 속이 넓어 엔진 기본을 그대로 쓴다.

PIXEL_BOLD_SIDE = :right
PIXEL_BOLD_ENGINE = false
PIXEL_BOLD_TRIM = 1
PIXEL_BOLD_ALPHA = 140

def pixelBoldWidth(size)
  # 엔진과 같은 계산(크기/10)에서 한 눈금씩 덜어낸다. 음수는 굵게 없음.
  w = size / 10 - PIXEL_BOLD_TRIM
  w < 0 ? 0 : w
end

def pixelShadowWide?(ch)
  s = ch[0]
  return false if !s.is_a?(String) || s.length == 0
  # 1.8.7은 getbyte가 없고, 어떤 모바일 실행기는 getbyte가 없으면서 s[0]이 String이라
  # (RPG Player 실측, 2026-08-08 제보) 192와의 비교가 ArgumentError로 터졌다.
  # 그래서 s[0]으로는 절대 떨어지지 않게 — 바이트는 getbyte 아니면 unpack으로만 뜬다.
  b = s.respond_to?(:getbyte) ? s.getbyte(0) : s.unpack("C")[0]
  return b >= 0xC0       # 여러 바이트 글자(한글·기호)
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
      fatten = !PIXEL_BOLD_ENGINE && ch[6] && pixelShadowWide?(ch)      # 한글 굵게는 우리가 반겹으로 만든다
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
      if fatten
        wide = pixelBoldWidth(bitmap.font.size)
        dy = (PIXEL_BOLD_SIDE == :diag) ? 1 : 0
        # 엔진처럼 폭을 넓힌다 — 같은 글자를 한 픽셀씩 옮겨 가며 겹친다.
        for dx in 1..wide
          bitmap.draw_text(ch[1] + offset + dx, ch[2] + offset + dy * dx, ch[3], ch[4], ch[0])
        end
        if PIXEL_BOLD_ALPHA > 0
          # 덜어낸 자리에 옅은 한 겹 — 엔진과 우리 사이의 반 눈금.
          bitmap.font.color = Color.new(ch[8].red, ch[8].green, ch[8].blue, PIXEL_BOLD_ALPHA)
          bitmap.draw_text(ch[1] + offset + wide + 1, ch[2] + offset + dy * (wide + 1),
                           ch[3], ch[4], ch[0])
          bitmap.font.color = ch[8]
        end
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
