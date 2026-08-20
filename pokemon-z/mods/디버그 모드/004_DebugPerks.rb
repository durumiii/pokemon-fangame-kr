# 디버그를 켜면 딸려 오던 편의 둘을 떼어 내 각각 토글로 만든다. 둘 다 기본은 꺼짐.
#
# ① 비전기술·라이드 자동 통과.
#    원작 `PField_HiddenMoves`가 `$DEBUG` 하나만 보고 배지도 기술 보유도 안 따지고
#    통과시킨다 — 거합베기·박치기·바위깨기·괴력·파도타기·폭포오르기·잠수, 그리고
#    파도타기라이드 아이템을 보는 자리까지 스물두 줄이 그 꼴이다(실측). 그래서 디버그를
#    켜는 순간 온 지도가 열려 정상 진행 확인이 안 됐다.
#    끄는 법은 그 판정만 속이는 것이다 — 진입점에서 `$DEBUG`를 잠깐 내렸다가 되돌린다.
#    원본 코드를 베껴 오지 않으므로 원작 판정이 바뀌어도 따라간다.
#
# ② 전투 후 자동 회복. `001_HealAfterBattle.rb`가 이 깃발을 본다.
#
# 값은 게임을 껐다 켜면 꺼진 상태로 돌아간다 — 세이브에 아무것도 안 남긴다.

module DebugPerks
  def self.hm;    return @hm ? true : false; end
  def self.heal;  return @heal ? true : false; end
  def self.hm=(v);   @hm = v ? true : false; end
  def self.heal=(v); @heal = v ? true : false; end

  def self.onoff(v)
    return v ? "켬" : "끔"
  end

  # 원작 판정이 $DEBUG 하나만 보므로 그 값을 잠깐 내려 평소 규칙으로 되돌린다.
  def self.as_player
    old = $DEBUG
    $DEBUG = false
    begin
      return yield
    ensure
      $DEBUG = old
    end
  end
end


# 필드에서 지형을 넘는 진입점 여덟. `proc` 안에서는 `return`이 신형 루비에서 죽으므로
# 값을 돌려줄 때 `next`를 쓴다.
class << Kernel
  ["pbCut", "pbHeadbutt", "pbRockSmash", "pbStrength",
   "pbSurf", "pbWaterfall", "pbDive", "pbSurfacing"].each {|m|
    next if !Kernel.respond_to?(m)
    old = "dbgz_perk_" + m
    alias_method(old, m)
    define_method(m) {|*args|
      next send(old, *args) if DebugPerks.hm
      next DebugPerks.as_player { send(old, *args) }
    }
  }
end


# 파티 화면에서 기술을 골라 쓰는 길. 판정이 한 자리로 모여 있다.
if defined?(HiddenMoveHandlers) && HiddenMoveHandlers.respond_to?(:triggerCanUseMove)
  class << HiddenMoveHandlers
    alias_method :dbgz_perk_triggerCanUseMove, :triggerCanUseMove
    def triggerCanUseMove(item, pokemon)
      return dbgz_perk_triggerCanUseMove(item, pokemon) if DebugPerks.hm
      return DebugPerks.as_player { dbgz_perk_triggerCanUseMove(item, pokemon) }
    end
  end
end
