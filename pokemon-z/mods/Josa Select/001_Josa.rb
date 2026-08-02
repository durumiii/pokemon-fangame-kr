# Josa Select — \j[받침형,무받침형] 조사 자동 선택 (Ruby 1.8.7)
# 예: "\PN\j[은,는] 상쾌한 아침을 맞았다" → 앞 글자 받침을 보고 은/는 선택.
# 첫 인자 = 받침 있을 때, 둘째 = 없을 때. (으)로의 ㄹ 특례를 안다.
# 판정 불가(문장 시작·기호 등)면 무받침형을 쓴다.

module JosaZ
  # 알파벳 낱자 읽기가 받침으로 끝나는 것 (엘·엠·엔)
  LATIN_CLOSED = ["l", "m", "n"]
  # 숫자 읽기: 일·칠·팔은 ㄹ 받침, 영·삼·육은 그 밖의 받침, 이·사·오·구는 무받침
  DIGIT_L = ["1", "7", "8"]
  DIGIT_CLOSED = ["0", "3", "6"]
  # 거슬러 읽을 때 건너뛰는 닫는 기호들
  SKIP_CHARS = [")", "]", "\"", "'", "\xE2\x80\x99", "\xE2\x80\x9D",
                "\xE3\x80\x8D", "\xE3\x80\x8F"]

  # 앞 문자열의 마지막 유효 글자 종성: 0=무받침, 8=ㄹ, 99=그 밖의 받침, -1=판정 불가
  def self.last_jong(str)
    bytes = str.unpack("C*")
    i = bytes.length
    while i > 0
      j = i - 1
      while j > 0 && (bytes[j] & 0xC0) == 0x80
        j -= 1
      end
      ch = bytes[j...i].pack("C*")
      if ch == ">"
        k = j
        while k > 0 && bytes[k].chr != "<"
          k -= 1
        end
        i = k
        next
      end
      if SKIP_CHARS.include?(ch)
        i = j
        next
      end
      if ch.length == 3
        cp = ((bytes[j] & 0x0F) << 12) | ((bytes[j + 1] & 0x3F) << 6) | (bytes[j + 2] & 0x3F)
        if cp >= 0xAC00 && cp <= 0xD7A3
          jong = (cp - 0xAC00) % 28
          return 0 if jong == 0
          return 8 if jong == 8
          return 99
        end
        return -1
      end
      if ch.length == 1
        c = ch.downcase
        if c >= "a" && c <= "z"
          return LATIN_CLOSED.include?(c) ? 99 : 0
        end
        if c >= "0" && c <= "9"
          return 8 if DIGIT_L.include?(c)
          return DIGIT_CLOSED.include?(c) ? 99 : 0
        end
      end
      return -1
    end
    -1
  end

  def self.resolve(text)
    return text if !text.is_a?(String)
    return text if !text.index("\\j[")
    begin
      text.gsub(/\\j\[([^,\]]*),([^\]]*)\]/) do
        md = $~
        closed = md[1]
        open = md[2]
        jong = last_jong(md.pre_match)
        if jong <= 0
          open
        elsif jong == 8 && closed == "\xEC\x9C\xBC\xEB\xA1\x9C" # "으로": ㄹ 뒤는 "로"
          open
        else
          closed
        end
      end
    rescue
      text
    end
  end
end

class Window_AdvancedTextPokemon
  alias josaz_setText setText
  def setText(value)
    josaz_setText(JosaZ.resolve(value))
  end
end

class Window_UnformattedTextPokemon
  alias_method :josaz_text_set, :text=
  def text=(value)
    josaz_text_set(JosaZ.resolve(value))
  end
end

# 창을 안 거치고 비트맵에 직접 그리는 경로 (요약·가방 등 UI 문장)
alias josaz_drawTextEx drawTextEx
def drawTextEx(bitmap, x, y, width, numlines, text, baseColor, shadowColor)
  josaz_drawTextEx(bitmap, x, y, width, numlines, JosaZ.resolve(text), baseColor, shadowColor)
end

alias josaz_drawFormattedTextEx drawFormattedTextEx
def drawFormattedTextEx(bitmap, x, y, width, text, baseColor = nil, shadowColor = nil)
  josaz_drawFormattedTextEx(bitmap, x, y, width, JosaZ.resolve(text), baseColor, shadowColor)
end
