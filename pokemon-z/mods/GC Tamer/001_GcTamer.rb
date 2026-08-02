# GC를 평소에 눌러 두고(GC.disable), 전환 순간에 몰아서 돌린다.
#
# 트리거 셋:
#   transfer = 맵 경계 이동 (이미 ~0.58초 얼어 있는 자리라 GC가 그 안에 숨는다)
#   scene    = 장면 바뀜 (메뉴·전투 진입 등 — 어차피 화면 전환 중)
#   timer    = FALLBACK_S초 동안 전환이 없었을 때의 안전판
#
# 함정: 루비 1.8은 GC.disable 상태에서 GC.start를 불러도 수집하지 않는다
# (gc.c의 garbage_collect가 dont_gc면 그냥 돌아간다). 그래서 수동 수집은
# 반드시 enable → start → disable로 감싼다.

module GcTamer
  @@last = Time.now
  @@last_scene = nil
  @@frames = 0

  def self.collect(trigger)
    return unless ENABLED
    return if (Time.now - @@last) < MIN_GAP_S
    t0 = Time.now
    GC.enable
    GC.start
    GC.disable
    ms = (Time.now - t0) * 1000.0
    @@last = Time.now
    if LOG != ""
      begin
        File.open(LOG, "a") { |f|
          f.puts(Time.now.strftime("%H:%M:%S") + (" gc %s %dms" % [trigger, ms]))
        }
      rescue
        # 로그가 안 써져도 게임은 계속 돈다
      end
    end
  end

  # 매 프레임 호출된다. 장면 바뀜은 즉시, 타이머는 60프레임에 한 번만 본다.
  def self.frame_check
    return unless ENABLED
    scn = $scene ? $scene.class : nil
    if scn != @@last_scene
      @@last_scene = scn
      collect("scene")
    end
    @@frames += 1
    if @@frames >= 60
      @@frames = 0
      collect("timer") if (Time.now - @@last) > FALLBACK_S
    end
  end

  if ENABLED
    GC.disable
    if LOG != ""
      begin
        File.open(LOG, "a") { |f|
          f.puts("---- " + Time.now.to_s + " gc-tamer on fallback=" +
                 FALLBACK_S.to_s + "s min_gap=" + MIN_GAP_S.to_s + "s")
        }
      rescue
      end
    end
  end
end

class << Graphics
  alias gct_update update

  def update
    gct_update
    GcTamer.frame_check
  end
end

class Scene_Map
  alias gct_transfer_player transfer_player

  def transfer_player
    gct_transfer_player
    GcTamer.collect("transfer")
  end
end
