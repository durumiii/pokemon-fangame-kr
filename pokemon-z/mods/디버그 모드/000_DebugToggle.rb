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
# 디버그 **메뉴**를 여는 원작 키(F9)도 패드 배정이 없어서 RB 단독으로 받는다. 필드에서
# 원작이 안 쓰는 가상 버튼이 Y·Z 둘뿐이라 다른 자리가 없다. 우리 훅은 깃발을 세우는
# 것만 되고 원작이 세운 깃발은 못 지우는데, 원작이 메뉴 깃발을 디버그 깃발보다 먼저
# 처리하므로 취소 버튼 계열은 애초에 못 쓴다.
# ⚠ RB를 먼저 누르고 LB를 나중에 누르면 메뉴가 먼저 열린다. 조합은 LB부터 누른다.
#
# 훅은 `Events.onMapUpdate`다. `Scene_Map#update` 별칭을 쓰지 않으므로 그 메서드를
# 잡는 다른 모드·원작 코드(따라다니는 포켓몬 등 다섯 자리)와 순서를 다투지 않는다.
module DebugToggleKey
  # 바꾸려면 이 두 줄. Windows 가상 키 코드다(P=0x50, W=0x57, F9=0x78).
  DEBUG_KEY = 0x50
  # 패드 조합 — 하나가 눌린 채 다른 하나를 누르는 순간에 켜진다.
  PAD_COMBO = [Input::Y, Input::Z]
  # 디버그가 켜져 있을 때 필드에서 박스 PC를 바로 여는 키(B). 기본 조작에 안 걸린
  # 글자다 — 게임이 키보드로 받는 것은 Space·Return·C·Esc·X·A·Z·S·D·Q·W뿐이다.
  PC_KEY = 0x42
  # 패드로 박스 PC를 여는 법 — LB를 이 프레임 수만큼 붙들고 있으면 열린다(약 1초).
  # 필드에서 원작이 안 쓰는 패드 버튼은 LB·RB 둘뿐이고 그 둘을 이미 토글과 메뉴가
  # 쓴다. LB를 그냥 누르고 있는 것은 조합의 대기 상태일 뿐 아무 일도 안 하므로,
  # 그 빈자리를 길게 누르기로 받는다. RB를 더하러 가는 손이 1초를 넘길 일은 없다.
  PAD_PC_HOLD = 40

  def self.keyboard?
    return false if !Input.respond_to?(:triggerex?)
    return Input.triggerex?(DEBUG_KEY)
  end

  def self.pad?
    a, b = PAD_COMBO
    return (Input.trigger?(a) && Input.press?(b)) ||
           (Input.trigger?(b) && Input.press?(a))
  end

  # 디버그 메뉴를 여는 패드 버튼. 원작은 F9인데 패드 배정이 없다.
  # 조합키(LB+RB)와 가르려고 **LB를 함께 누르고 있지 않을 때만** 연다.
  PAD_MENU = Input::Z

  def self.menu?
    return false if !$DEBUG
    return false if !Input.trigger?(PAD_MENU)
    return false if Input.press?(PAD_COMBO[0])
    return true
  end

  # 이 훅이 필드에서만 도는 게 아니다 — 대사창과 일시정지 메뉴도 `pbUpdateSceneMap`을
  # 거쳐 맵을 갱신하므로 그 안에서도 돈다. 그쪽에서는 LB·RB에 이미 임자가 있다
  # (이동·나침반, 가방의 정렬·검색). 그대로 두면 나침반을 열 때마다 디버그 메뉴가
  # 딸려 열린다. 그래서 두 자리를 다 막는다.
  def self.field?
    return false if !$game_temp
    return false if $game_temp.message_window_showing
    return false if $game_temp.in_menu
    return true
  end

  def self.pc?
    return false if !$DEBUG
    return false if !Input.respond_to?(:triggerex?)
    return Input.triggerex?(PC_KEY)
  end

  # LB 길게 누르기. 한 번 열면 손을 뗄 때까지 다시 안 연다.
  def self.pad_pc?
    if !$DEBUG || !Input.press?(PAD_COMBO[0])
      @hold = 0
      @held_done = false
      return false
    end
    @hold = (@hold ? @hold : 0) + 1
    return false if @held_done
    return false if @hold < PAD_PC_HOLD
    @held_done = true
    return true
  end

  def self.update
    return if !field?
    open_pc = pad_pc?   # 길게 누르기는 매 프레임 세어야 하므로 먼저 부른다
    if pc? || open_pc
      pbFadeOutIn(99999) { pbPokeCenterPC }
      return
    end
    if keyboard? || pad?
      # 조합이 섰으면 LB는 그 몫이다 — 손을 떼기 전까지 PC가 딸려 열리지 않게 막는다
      @held_done = true
      $DEBUG = !$DEBUG
      Kernel.pbMessage($DEBUG ? "디버그 모드 ON" : "디버그 모드 OFF")
      return
    end
    # 깃발만 세운다 — 원작 Scene_Map#update가 이 훅 바로 뒤에서 받아 연다.
    $game_temp.debug_calling = true if menu? && $game_temp
  end
end

# 편의 기능이 게임 루프를 막게 두지 않는다 — 맵 갱신 훅에서 예외가 나면 게임이 선다.
Events.onMapUpdate += proc {
  begin
    DebugToggleKey.update
  rescue Exception
  end
}
