# 전투가 끝나면 파티 전원을 회복한다 (HP·상태이상·PP).
# 단, $DEBUG가 켜져 있을 때만 작동한다.
#
# 원본 디버그 배포판은 PokeBattle_Battle#pbEndOfBattle 꼬리의
# `for i in $Trainer.party` 루프에 `i.heal` 한 줄을 끼워 넣었다. 여기서는
# 코어 섹션을 통째로 덮는 대신 alias로 같은 자리에 한 번 더 돈다 — heal은
# 지닌 물건·폼 되돌리기와 겹치지 않아 최종 상태가 같다.
class PokeBattle_Battle
  alias dbgz_pbEndOfBattle pbEndOfBattle
  def pbEndOfBattle(canlose=false)
    ret = dbgz_pbEndOfBattle(canlose)
    if $DEBUG
      for i in $Trainer.party
        i.heal
      end
    end
    return ret
  end
end