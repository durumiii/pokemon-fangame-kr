# Controller UX Z — 커서 자동 숨김 (Ruby 1.8.7)
# 마우스가 움직이면 보여 주고, IDLE_FRAMES 동안 쉬면 숨긴다(사용자 요구 2026-08-02 —
# 무조건 숨김에서 변경). 「마지막 입력이 패드인가」는 못 가린다 — 가상 버튼 층이
# 키보드와 패드를 합쳐서 출처가 스크립트에 안 내려온다. 마우스 유휴가 그 대용이다.
#
# 이 빌드(mkxp-z 구판)는 show_cursor=·mouse_x·mouse_y를 루비에 노출한다(심볼 실측).
# 수신자가 판본마다 달라 Graphics·Input 순으로 더듬고, 좌표를 못 읽는 판본이면
# 이전 동작(상시 숨김)으로 물러난다. 마우스 UI($mouse/Game_Mouse)는 죽은 코드다.
module CursorAutoHide
  IDLE_FRAMES = 120  # 60fps 기준 2초

  @owner = nil
  @last = nil
  @idle = IDLE_FRAMES  # 부팅 직후에는 숨긴 채 시작
  @shown = nil

  def self.owner
    if @owner.nil?
      @owner = false
      [Graphics, Input].each do |mod|
        if mod.respond_to?(:show_cursor=)
          @owner = mod
          break
        end
      end
    end
    @owner
  end

  def self.mouse_pos
    [Input, Graphics].each do |mod|
      if mod.respond_to?(:mouse_x)
        return [mod.mouse_x, mod.mouse_y]
      end
    end
    nil
  end

  def self.tick
    return if !owner
    pos = mouse_pos
    if pos && pos != @last
      @idle = 0
      @last = pos
    elsif @idle < IDLE_FRAMES
      @idle += 1
    end
    want = pos ? (@idle < IDLE_FRAMES) : false
    if want != @shown
      @shown = want
      owner.show_cursor = want
    end
  end
end

module Input
  class << self
    alias_method :cux_cursor_update, :update
    def update
      cux_cursor_update
      begin
        CursorAutoHide.tick
      rescue Exception
        # 커서는 편의 기능이다 — 실패가 게임 루프를 막게 두지 않는다
      end
    end
  end
end
