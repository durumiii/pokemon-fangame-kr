# 컨트롤러 라벨 오버라이드 — UI Text KR의 키보드 기준 표기를 패드 표기로.
# TABLE 앞머리에 넣어 먼저 매칭시킨다(원문을 선점하면 키보드 항목은 무동작).
# UI Text KR이 없으면 원문 스페인어를 직접 패드 표기로 바꾼다.
if defined?(UiTextKR)
  UiTextKR::TABLE.unshift(
    ["[A] Curar", "[X] 회복"],
    ["[S] Viajar", "[LB] 이동"],
    ["[D] Brújula", "[RB] 나침반"],
    ["A Curar", "X 회복"],
    ["S Viajar", "LB 이동"],
    ["D Brújula", "RB 나침반"]
  )
end
