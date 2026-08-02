# UI Text KR — 번역 테이블을 안 지나는 하드코딩 화면 문자열 교체 (Ruby 1.8.7)
# 대상: 일시정지 메뉴 단축키(206_Menu_Mejorado), 야생 출현 안내판(204_CartelesPokemon),
# 배지 이름(189_Fancy_Badges). korean.dat로 못 고치는 자리만 여기 싣는다.
# 배지 호칭은 본가 존중 판정(2026-08-02)대로 음차+배지다. medalla는 배지.

module UiTextKR
  TABLE = [
    # 단축키 표기는 컨트롤러(Xbox 배치) 기준 — 가상 X·Y·Z가 패드 X·LB·RB에 얹혀
    # 있다(F1 기본 바인딩 실측, Controller UX Z 설계 문서 참조)
    ["[A] Curar", "[X] 회복"],
    ["[S] Viajar", "[LB] 이동"],
    ["[D] Brújula", "[RB] 나침반"],
    ["Esta zona no tiene encuentros", "이 지역에는 나오는 포켓몬이 없습니다"],
    ["No hay Pokémon salvajes", "야생 포켓몬이 없습니다"],
    ["Pokémon salvajes en esta zona: ", "이 지역의 야생 포켓몬: "],
    ["Medalla Guardia", "가르디아 배지"],
    ["Medalla Espectro", "에스펙트로 배지"],
    ["Medalla Centella", "센테야 배지"],
    ["Medalla Vital", "비탈 배지"],
    ["Medalla Tifón", "티폰 배지"],
    ["Medalla Aguijón", "아기혼 배지"],
    ["Medalla Visión", "비시온 배지"],
    ["Medalla Pira", "피라 배지"],
    ["Medalla Forja", "포르하 배지"],
    ["Medalla Escarcha", "에스카르차 배지"],
    ["Medalla Luzbel", "루스벨 배지"],
    ["Medalla Odonata", "오도나타 배지"]
  ]

  def self.fix(text)
    return text if !text.is_a?(String)
    TABLE.each do |pair|
      text = text.gsub(pair[0], pair[1]) if text.include?(pair[0])
    end
    text
  end
end

class Window_AdvancedTextPokemon
  alias uitkr_setText setText
  def setText(value)
    uitkr_setText(UiTextKR.fix(value))
  end
end

class Window_UnformattedTextPokemon
  alias_method :uitkr_text_set, :text=
  def text=(value)
    uitkr_text_set(UiTextKR.fix(value))
  end
end

alias uitkr_pbDrawTextPositions pbDrawTextPositions
def pbDrawTextPositions(bitmap, textpos)
  fixed = textpos.map do |t|
    t.is_a?(Array) ? [UiTextKR.fix(t[0])] + t[1..-1] : t
  end
  uitkr_pbDrawTextPositions(bitmap, fixed)
end

# 불러오기(컨티뉴) 화면의 지명 — pbGetBasicMapNameFromId가 번역표를 안 지나고
# MapInfos.rxdata의 원시 이름(영문)을 그대로 돌려준다(PScreen_Load 실측:
# "Pokemon Bastion"). 번역표(절21 MapNames)를 먼저 보고, 없거나 비면 원래
# 동작으로 내려간다. 게임 본편(Game_Map#name)은 이미 번역 경로를 쓴다.
alias uitkr_pbGetBasicMapNameFromId pbGetBasicMapNameFromId
def pbGetBasicMapNameFromId(id)
  begin
    name = pbGetMessage(MessageTypes::MapNames, id)
    return name if name && name != ""
  rescue
  end
  uitkr_pbGetBasicMapNameFromId(id)
end
