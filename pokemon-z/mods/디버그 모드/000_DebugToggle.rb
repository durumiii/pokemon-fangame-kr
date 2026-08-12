# P키(또는 패드 LB+RB)로 디버그 모드($DEBUG)를 켜고 끈다 (Ruby 1.8.7 / 3.1+ 공통).
#
# 키 판정은 엔진(mkxp-z)의 확장 `Input.triggerex?`다 — Windows 가상 키 코드를 그대로
# 받고, 눌린 순간에만 참이라 눌림 유지를 따로 셀 필요가 없다. Win32API를 쓰지 않는
# 이유가 둘이다: (1) mkxp-z의 Win32API 대체층에 창 포커스 조회 함수가 없어 비Windows
# 에서는 예외도 없이 조용히 0이 와 토글이 영영 안 먹는다, (2) 창이 포커스를 잃으면
# 엔진이 키 상태를 스스로 비우므로 포커스 확인 자체가 필요 없다.
#
# 패드는 이 확장으로 못 읽는다(키보드 전용) — 가상 버튼으로만 들어온다. 그래서 패드
# 쪽은 가상 Y+Z 동시 누름으로 받는다. F1 기본 배치에서 그 둘이 LB·RB이고, 맵에서는
# 아무 기능도 안 걸려 있다(실측: `Scene_Map` 섹션에 `Input::Y`·`Input::Z` 호출 0 —
# 둘은 가방·일시정지 메뉴·전투 화면에서만 쓰인다).
#
# 훅은 `Events.onMapUpdate`다. `Scene_Map#update` 별칭을 쓰지 않으므로 그 메서드를
# 잡는 다른 모드·원작 코드(따라다니는 포켓몬 등 다섯 자리)와 순서를 다투지 않는다.
module DebugToggleKey
  # 바꾸려면 이 두 줄. Windows 가상 키 코드다(P=0x50, W=0x57, F9=0x78).
  DEBUG_KEY = 0x50
  # 패드 조합 — 하나가 눌린 채 다른 하나를 누르는 순간에 켜진다.
  PAD_COMBO = [Input::Y, Input::Z]

  def self.keyboard?
    return false if !Input.respond_to?(:triggerex?)
    return Input.triggerex?(DEBUG_KEY)
  end

  def self.pad?
    a, b = PAD_COMBO
    return (Input.trigger?(a) && Input.press?(b)) ||
           (Input.trigger?(b) && Input.press?(a))
  end

  def self.update
    # 대사창이 떠 있는 동안에는 무시한다 — 메시지가 겹쳐 뜨는 것을 막는다.
    return if $game_temp && $game_temp.message_window_showing
    return if !keyboard? && !pad?
    $DEBUG = !$DEBUG
    Kernel.pbMessage($DEBUG ? "디버그 모드 ON" : "디버그 모드 OFF")
  end
end

# 편의 기능이 게임 루프를 막게 두지 않는다 — 맵 갱신 훅에서 예외가 나면 게임이 선다.
Events.onMapUpdate += proc {
  begin
    DebugToggleKey.update
  rescue Exception
  end
}
