# Ball Shortcut — 볼 단축키가 마지막에 쓴 볼을 낸다 (Z-50 ①)
#
# 원본은 전투 중 볼 단축키가 고정 사슬(집볼 계열 → 울트라볼 → 슈퍼볼 → 몬스터볼)로
# 볼을 골라, 쓰고 싶은 볼이 목록 뒤에 있으면 앞엣것부터 다 떨어져야 나온다.
# 여기서는 마지막으로 전투 가방에서 고른 볼을 기억해 두었다가 그것을 먼저 낸다.
# 갖고 있지 않으면 원본 사슬 그대로다.
#
# 자리 셋이 한 벌이다.
#   · 기억  — `NewBattleBag#intoPocket`(이 파일). 고른 것이 볼일 때만 적는다.
#   · 던지기 — `PokeBattle_Battle#pbAttackPhase`(010_TurnOrder.rb의 사슬 머리).
#   · 아이콘 — `CommandMenuDisplay#update`(이 파일).
#
# ⚠ 전투 가방의 「마지막에 쓴 도구」 빠른 칸을 먹이는 전역 `$lastUsed`는 건드리지
# 않는다. 그것을 볼로 덮으면 상처약을 쓴 뒤에도 빠른 칸이 볼을 가리켜 도구 단축키를
# 잃는다. 그래서 전역을 따로 둔다.
#
# `$lastUsedBall`은 세이브에 안 실린다 — 원작의 `$lastUsed`도 마찬가지로 평범한
# 전역이고 `NewBattleBag#initialize`가 `$lastUsed ||= 0`으로 열어 쓴다(절
# `Objetos Batalla` 22행). 게임을 다시 켜면 사슬이 기본값으로 돌아갈 뿐이라
# 세이브에 실을 값이 아니다.

class NewBattleBag
  alias qol_ball_intoPocket intoPocket
  def intoPocket
    qol_ball_intoPocket
    item=@ret
    $lastUsedBall=item if item && item>0 && pbIsPokeBall?(item)
  end
end

class CommandMenuDisplay
  # 단축키가 실제로 낼 볼. 마지막에 쓴 볼이 없거나 다 떨어졌으면 원본 아이콘 사슬 그대로.
  def qol_ball_iconItem
    return $lastUsedBall if $lastUsedBall && $lastUsedBall>0 &&
                            $PokemonBag.pbHasItem?($lastUsedBall)
    for sym in [:ULTRABALL,:GREATBALL,:POKEBALL,
                :POKEBALLCASERA,:SUPERBALLCASERA,:ULTRABALLCASERA]
      next if !hasConst?(PBItems,sym)
      return getConst(PBItems,sym) if $PokemonBag.pbHasItem?(sym)
    end
    return 0
  end

  alias qol_ball_update update
  def update
    qol_ball_update
    return if !@iconBall
    item=qol_ball_iconItem
    return if item==@qol_ball_icon   # 값이 바뀔 때만 다시 그린다
    @qol_ball_icon=item
    if item>0
      @iconBall.setBitmap(sprintf("Graphics/Icons/item%03d.png",item))
    else
      @iconBall.setBitmap("Graphics/Icons/item000.png")
    end
  end
end
