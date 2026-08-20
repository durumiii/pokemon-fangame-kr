# 디버그를 켜면 딸려 오던 나머지 곁가지 넷을 한 토글 뒤로 넣는다. 기본은 꺼짐.
#
# 원작이 `$DEBUG` 하나로 열어 두는 자리가 비전기술 말고도 남아 있었다(전수 조사
# 2026-08-21 — 게임 스크립트의 `$DEBUG` 98곳 중 키 조건부 26곳과 비전기술 22곳을
# 뺀 나머지에서 골랐다).
#
#   ① 리전 맵이 편집기로 열린다 — 확인 버튼이 지점 이름 편집이 되고, 나갈 때
#      「변경을 저장할까?」에 승낙하면 `townmap.dat`를 덮어쓴다. 실수 한 번에 원본이
#      바뀌는 자리라 이 넷 중 가장 위험하다.
#   ② 가방에서 중요한 도구도 「버리기」가 뜨고, 「이상한 소포 만들기」 항목이 붙는다.
#   ③ 알에게 기술을 가르칠 수 있다.
#   ④ 데이터에 없는 트레이너를 부르면 「새 트레이너를 추가할까?」를 묻는다.
#      같은 일을 디버그 메뉴의 트레이너 편집이 이미 하므로 평소에는 방해일 뿐이다.
#
# 고치는 법은 004와 같다 — 원본 판정이 `$DEBUG` 하나만 보므로 그 자리에서만 값을
# 내렸다 되돌린다. 원본 코드를 베끼지 않으므로 원작이 바뀌어도 따라간다.
# 리전 맵만 예외로 인자를 직접 넘긴다 — 그쪽은 `$DEBUG`를 판정이 아니라 값으로 쓴다.

module DebugPerks
  def self.side;    return @side ? true : false; end
  def self.side=(v); @side = v ? true : false; end
end


# ① 리전 맵. 편집기 여부를 인자로 받으므로 그 인자만 갈아 끼운다.
# 인자를 그대로 두면 미방문 지점 이동(CTRL) 같은 딴 디버그 기능까지 함께 죽는다.
if defined?(PokemonRegionMap)
  class PokemonRegionMap
    def pbStartScreen
      @scene.pbStartScene(DebugPerks.side)
      @scene.pbMapScene
      @scene.pbEndScene
    end
  end
end


# ② 가방 화면.
if defined?(PokemonBagScreen)
  class PokemonBagScreen
    alias dbgz_side_pbStartScreen pbStartScreen
    def pbStartScreen
      return dbgz_side_pbStartScreen if DebugPerks.side
      return DebugPerks.as_player { dbgz_side_pbStartScreen }
    end
  end
end


# ③ 알에게 기술 가르치기. 블록을 받는 메서드라 인자를 그대로 적어 넘긴다.
# 두 전역 메서드는 `defined?`로 막아 둔다 — 실을 때 없으면 파일이 거기서 멎는다.
if defined?(pbLearnMove)
alias dbgz_side_pbLearnMove pbLearnMove
def pbLearnMove(pokemon, move, ignoreifknown = false, bymachine = false, &block)
  if DebugPerks.side
    return dbgz_side_pbLearnMove(pokemon, move, ignoreifknown, bymachine, &block)
  end
  return DebugPerks.as_player {
    dbgz_side_pbLearnMove(pokemon, move, ignoreifknown, bymachine, &block)
  }
end
end


# ④ 없는 트레이너를 부를 때 뜨는 「새 트레이너를 추가할까?」 확인창.
if defined?(pbTrainerCheck)
alias dbgz_side_pbTrainerCheck pbTrainerCheck
def pbTrainerCheck(trainerid, trainername, maxbattles, startBattleId = 0)
  if DebugPerks.side
    return dbgz_side_pbTrainerCheck(trainerid, trainername, maxbattles, startBattleId)
  end
  return DebugPerks.as_player {
    dbgz_side_pbTrainerCheck(trainerid, trainername, maxbattles, startBattleId)
  }
end
end
