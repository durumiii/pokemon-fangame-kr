# 컨트롤러 라벨 오버라이드 — UI Text KR의 키보드 기준 표기를 패드 표기로.
# 주입 섹션은 모드명 정렬 순이라 이 섹션이 UI Text KR보다 먼저 실린다 — 로드
# 시점엔 UiTextKR가 없으므로, 맵 씬 진입 때 한 번 치환표 앞머리에 얹는다
# (앞머리가 먼저 매칭돼 키보드 항목을 선점한다). UI Text KR이 없으면 무동작.
class Scene_Map
  alias padlbl_main main
  def main
    if !$padlbl_done && defined?(UiTextKR)
      [
        ["D Brújula", "RB 나침반"],
        ["S Viajar", "LB 이동"],
        ["A Curar", "X 회복"],
        ["[D] Brújula", "[RB] 나침반"],
        ["[S] Viajar", "[LB] 이동"],
        ["[A] Curar", "[X] 회복"]
      ].each do |pair|
        UiTextKR::TABLE.unshift(pair)
      end
      $padlbl_done = true
    end
    padlbl_main
  end
end
