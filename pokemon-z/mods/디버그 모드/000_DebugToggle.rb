# P키로 디버그 모드($DEBUG)를 켜고 끈다 (Ruby 1.8.7 / 3.1+ 공통).
#
# 키 판정은 엔진(mkxp-z)의 확장 `Input.triggerex?`다 — Windows 가상 키 코드를 그대로
# 받고, 눌린 순간에만 참이라 눌림 유지를 따로 셀 필요가 없다. Win32API를 쓰지 않는
# 이유가 둘이다: (1) mkxp-z의 Win32API 대체층에 창 포커스 조회 함수가 없어 비Windows
# 에서는 예외도 없이 조용히 0이 와 토글이 영영 안 먹는다, (2) 창이 포커스를 잃으면
# 엔진이 키 상태를 스스로 비우므로 포커스 확인 자체가 필요 없다.
#
# 훅은 `Events.onMapUpdate`다. `Scene_Map#update` 별칭을 쓰지 않으므로 그 메서드를
# 잡는 다른 모드·원작 코드(따라다니는 포켓몬 등 다섯 자리)와 순서를 다투지 않는다.
module DebugToggleKey
  # 바꾸려면 이 한 줄. Windows 가상 키 코드다(P=0x50, W=0x57, F9=0x78).
  DEBUG_KEY = 0x50

  def self.update
    return if !Input.respond_to?(:triggerex?)
    # 대사창이 떠 있는 동안에는 무시한다 — 메시지가 겹쳐 뜨는 것을 막는다.
    return if $game_temp && $game_temp.message_window_showing
    return if !Input.triggerex?(DEBUG_KEY)
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
