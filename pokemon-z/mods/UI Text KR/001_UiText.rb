# UI Text KR — 번역 테이블을 안 지나는 하드코딩 화면 문자열 교체 (Ruby 1.8.7)
# 대상: 일시정지 메뉴 단축키(206_Menu_Mejorado), 야생 출현 안내판(204_CartelesPokemon),
# 배지 이름(189_Fancy_Badges). korean.dat로 못 고치는 자리만 여기 싣는다.
# 배지 호칭은 본가 존중 판정(2026-08-02)대로 음차+배지다. medalla는 배지.

module UiTextKR
  TABLE = [
    # (generated from translate/data/uitext.jsonl — 직접 고치지 말고 uv run translate/uitext.py --write)
    # 단축키 표기는 키보드 기본 바인딩 기준(기본판 표준 — 2026-08-03 사용자 판정).
    # 컨트롤러 라벨([X]/[LB]/[RB])은 Controller UX Z의 004_PadLabels 오버라이드 몫.
    ["[A] Curar", "[A] 회복"],
    ["[S] Viajar", "[S] 이동"],
    ["[D] Brújula", "[D] 나침반"],
    # 디버그 패치판은 괄호를 벗긴다("A Curar") — 무괄호 짝도 커버
    ["A Curar", "A 회복"],
    ["S Viajar", "S 이동"],
    ["D Brújula", "D 나침반"],
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
    ["Medalla Odonata", "오도나타 배지"],
    # 연금술(Crafteo) 레시피 조합 화면 하단 — 222_Crafteo.rb pbRedrawItem의
    # textpos 리터럴(첫 화면만 한글이고 둘째 화면이 누락돼 있었다)
    ["C: Combinar", "C: 조합"],
    ["Arriba/Abajo: Cantidad", "위/아래: 수량"],
    ["X: Salir", "X: 나가기"],
    # 불러오기 화면(141_PScreen_Load) — 슬롯 라벨 영문 하드코딩.
    # "Partida "는 sprintf("Partida %d") 접두 부분매치(→ 저장 1, 저장 2 …).
    # 번역 정본에 "Partida " 포함 한국어 값 0건 확인(2026-08-02) — gsub 오폭 없음.
    ["Normal Save", "일반 저장"],
    ["Autosave", "자동 저장"],
    [" Auto Save", " (자동 저장)"],
    ["Partida ", "저장 "],
    # 인물 안내(231_Guia Personajes) 인포그래픽 라벨 — names.json 음차 준수.
    # 맨이름 쌍은 단어 경계 정규식 — Auretosk 등 라틴 이스터에그 부분 오폭 방지.
    # AZ·F3은 keep 명단이라 그대로. Hombre del Saco는 대사 정본 「자루 든 남자」.
    ["Áster Zéphir (AZ)", "아스테르 제피르 (AZ)"],
    ["Hombre del Saco", "자루 든 남자"],
    [/\bOlivier\b/, "올리비에"],
    [/\bCrisanto\b/, "크리산토"],
    [/\bMelia\b/, "멜리아"],
    [/\bMerlot\b/, "메를로"],
    [/\bCanola\b/, "카놀라"],
    [/\bMirra\b/, "미라"],
    [/\bNúbila\b/, "누빌라"],
    [/\bHisopo\b/, "히소포"],
    [/\bLanto\b/, "란토"],
    [/\bAlca\b/, "알카"],
    [/\bWolfram\b/, "볼프람"],
    [/\bZafra\b/, "사프라"],
    [/\bLoto\b/, "로토"],
    [/\bGenos\b/, "게노스"],
    [/\bBelladona\b/, "벨라도나"],
    [/\bMalvo\b/, "말보"],
    [/\bAure\b/, "아우레"],
    [/\bRosaleda\b/, "로살레다"],
    [/\bFerrofaz\b/, "페로파스"],
    [/\bPinot\b/, "피노"],
    [/\bHibis\b/, "히비스"],
    [/\bAnturia\b/, "안투리아"],
    [/\bCendera\b/, "센데라"]
  ]

  def self.fix(text)
    return text if !text.is_a?(String)
    TABLE.each do |pair|
      if pair[0].is_a?(Regexp)
        text = text.gsub(pair[0], pair[1])
      elsif text.include?(pair[0])
        text = text.gsub(pair[0], pair[1])
      end
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

# 배지 이름은 Fancy Badges(절 190)가 FANCY_BADGE_NAMES의 원문을 pbDrawOutlineText로
# 바로 그려서 위 세 진입점을 안 지난다. 게임 본체 절은 MOD 절보다 먼저 실리므로
# 상수 재대입 없이 원소만 제자리에서 갈아 끼운다(Z-62 판정: 길 3).
# 값은 위 TABLE 한 곳에만 산다 — 여기서 이름을 다시 적지 않는다.
if defined?(FANCY_BADGE_NAMES) && FANCY_BADGE_NAMES.is_a?(Array)
  if FANCY_BADGE_NAMES.length != 12
    # 이 길의 유일한 약점이 조용한 실패다 — 배지가 늘거나 이름이 바뀌면 원문으로
    # 돌아간다. 그때 시끄럽게 만드는 것이 이 줄의 몫($DEBUG 콘솔).
    echoln("[UI Text KR] FANCY_BADGE_NAMES 길이 #{FANCY_BADGE_NAMES.length} (12 아님) — 배지 이름 치환표를 다시 맞춰라")
  end
  FANCY_BADGE_NAMES.each_with_index do |badge_name, i|
    FANCY_BADGE_NAMES[i] = UiTextKR.fix(badge_name)
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
