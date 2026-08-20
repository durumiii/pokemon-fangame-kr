# Craft Prompt — 연금술 제작 권유가 이미 가진 도구를 또 권하지 않게 (Z-76 ⑤)
#
# 공통 이벤트 셋이 현장에서 제작을 권하는데 가방에 그 도구가 있는지를 아예 안 본다.
# 「예」를 고르면 재료가 실제로 줄면서 도구가 하나 더 생긴다.
#
#   공통 이벤트 58 `TenerGolpeRoca`  → 폭발가루 POLVOEXPLOSIVO(756)
#   공통 이벤트 59 `TenerCorte`      → 약한손도끼 HACHAENDEBLE(757)
#   공통 이벤트 61 `TenerMercurica`  → 수은열쇠 LLAVEMERCURICA(758)
#
# 셋이 전부고(공통 이벤트 100개 전수 + 맵 486개의 이벤트 페이지 18,740장 전수),
# 호출 117자리가 전부 소지 검사 없이 최상위에서 곧바로 부른다. 그래서 이벤트 데이터를
# 고치는 대신 **부르는 명령의 처리부**를 감싼다 — 표 세 줄로 117자리가 다 덮인다
# (이벤트 파일을 다시 쓰는 길은 다른 공통 이벤트의 이동 명령이 깨질 위험이 있다).
#
# ⚠ 손대지 않는 것(유지자 판정 2026-08-21) — 감옥 볼 제작(맵 228) · 메뉴의 「Crear」
# (절 `Crafteo`) · 두 경로의 잠금 문턱이 어긋나는 것(의도로 본다).

class Interpreter
  # 공통 이벤트 번호 → 그 이벤트가 주는 도구
  QOL_CRAFT_ITEMS = {
    58 => :POLVOEXPLOSIVO,
    59 => :HACHAENDEBLE,
    61 => :LLAVEMERCURICA
  }

  alias qol_craft_command_117 command_117
  def command_117
    item=QOL_CRAFT_ITEMS[@parameters[0]]
    if item && $PokemonBag && hasConst?(PBItems,item) && $PokemonBag.pbHasItem?(item)
      return true   # 이미 갖고 있다 — 권유를 통째로 건너뛴다
    end
    return qol_craft_command_117
  end
end
