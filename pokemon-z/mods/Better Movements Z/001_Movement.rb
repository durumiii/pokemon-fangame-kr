# Better Movements Z — 훅 두 개. 원본 메서드를 통째로 갈지 않는다:
# Game_Player#update는 Walk_Run(22)·Following(187)이 alias 사슬로 잡고 있어서
# 통째로 다시 정의하면 동행이 부서진다. 사슬 끝에 얹기만 한다.

class Game_Character
  # 속도: Walk_Run이 프레임마다 @move_speed에 바닐라 눈금을 직접 박으므로
  # (setter를 안 지나간다), 실제로 걸음을 미는 update_move 직전에 표로 바꿔치기한다.
  # Game_Player가 아니라 Game_Character에 얹는 이유(2026-08-02 실기 회귀): 동행
  # 속도 동기화(Following의 follow_leader)가 플레이어 update의 super **앞**에서
  # 돌아 바닐라 눈금을 복사해 간다 — 플레이어에만 얹으면 동행이 바닐라 속도로
  # 걷다 반 발짝씩 처져 2칸 점프로 딸려온다. 여기 얹으면 동행 자신의 update_move가
  # 같은 표를 지나 둘의 속도가 맞는다. NPC 이벤트는 정수 눈금이라 표(실수 키)에
  # 안 걸린다.
  alias bmz_update_move update_move
  def update_move
    mapped = BetterMovementsZ::SPEED[@move_speed]
    @move_speed = mapped if mapped
    bmz_update_move
  end
end

class Game_Player < Game_Character
  # 회전 문턱: 코어 update(21)에 `> 2`(프레임) 리터럴로 박혀 있고 값만 바꿀 후크가
  # 없다. 코어는 방향이 바뀐 프레임에만 @lastdirframe에 현재 프레임 번호를 찍는다 —
  # 그 직후 문턱 차이만큼 과거로 밀어, 리터럴을 안 고치고 같은 효과를 낸다.
  alias bmz_update update
  def update
    bmz_update
    if @lastdirframe == Graphics.frame_count
      @lastdirframe -= 2 - BetterMovementsZ::TURN_DELAY_FRAMES
    end
  end
end
