# Battle Speed Z — 배틀 애니메이션 재생기 배속 (Ruby 1.8.7)
# 기술·공용 애니메이션은 전부 PBAnimationPlayerX를 지난다. 재생 루프(PokeBattle_Scene)가
# 화면 프레임마다 update를 한 번 불러 내부 프레임을 1씩 미는 구조라, update를 배속만큼
# 거듭 부르면 벽시계 시간이 그 배수로 준다. 소리·화면 효과(playTiming)도 내부 프레임에
# 매여 있어 함께 당겨진다. 애니메이션이 끝난 뒤의 추가 호출은 원본이 스스로 무시한다
# (@frame < 0 조기 반환). 필드(맵 이벤트)의 RPG::Sprite 애니메이션은 안 건드린다.
class PBAnimationPlayerX
  alias basz_update update
  def update
    BattleSpeedZ::ANIM_SPEED.times { basz_update }
  end
end
