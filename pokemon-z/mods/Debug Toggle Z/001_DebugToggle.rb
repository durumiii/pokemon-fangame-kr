# W키로 디버그 모드($DEBUG)를 켜고 끈다 (Ruby 1.8.7 / 3.1+ 공통).
# 출처: 디시 레쿠쟈 갤 228378 배포판의 Db 섹션 — 우리 모드 형식으로 이식.
#
# 키 폴링은 Win32API의 GetAsyncKeyState다. mkxp-z·Joiplay에서 이 API가 실제로 키를
# 읽는지는 실기 확인 전이라(Z-36), 못 쓰는 환경에서는 조용히 무동작으로 내려간다 —
# 토글이 안 될 뿐 게임은 그대로 돈다. 실기에서 안 먹는 것으로 확인되면 폴링을
# 엔진 Input으로 갈아야 한다.
module DebugToggleKey
  W_KEYCODE = 0x57

  begin
    GetKeyState = Win32API.new("user32", "GetAsyncKeyState", 'i', 'i')
  rescue Exception
    GetKeyState = nil
  end

  def self.wPressed?
    return false if !GetKeyState
    begin
      return (GetKeyState.call(W_KEYCODE) & 0x8000) != 0
    rescue Exception
      return false
    end
  end
end

class Scene_Map
  alias debugtoggle_update update
  def update
    if DebugToggleKey.wPressed?
      if !@wKeyHeld
        $DEBUG = !$DEBUG
        Kernel.pbMessage($DEBUG ? "디버그 모드 ON" : "디버그 모드 OFF")
        @wKeyHeld = true
      end
    else
      @wKeyHeld = false
    end
    debugtoggle_update
  end
end
