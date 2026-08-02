# 프레임 시간 측정 v3 — 단계별로 가르고, 렌더 쪽(gfx)까지 잰다.
# Graphics.update 진입 간격이 곧 실제 프레임 시간이다(프레임 리미터 대기 포함).
#
# 단계:
#   gfx = Graphics.update 자체 (렌더 + 프레임 리미터 대기. 느린 프레임에서
#         gfx가 크면 범인은 스크립트가 아니라 렌더·GC 쪽이다)
#   scn = Scene_Map#update 전체 (아래 넷을 포함하는 바깥 틀)
#   map = Scene_Map#updateMaps      (연결된 맵 전부의 이벤트 갱신)
#   int = Interpreter#update        (이벤트 해석기)
#   pl  = Game_Player#update        (플레이어 이동 — 동행류 알리아스 포함)
#   spr = Scene_Map#updateSpritesets(연결된 맵 전부의 스프라이트셋 + onMapUpdate 훅)
#
# 재진입 가드: 단계 안에서 Graphics.update가 다시 돌아 같은 단계가 겹치면
# (동행 스크립트의 대기 루프 등) 가장 바깥 호출만 잰다 — v2에서 겹쳐 세어져
# pl이 프레임보다 커지는 오염이 있었다.
#
# 걷기 체감을 재려고 프레임을 이동 중(mv)/정지(st)로 갈라 요약에 둘 다 적는다.

module FrameProfiler
  @@buf = []
  @@count = 0
  @@sum = 0.0
  @@max = 0.0
  @@slow = 0
  @@ph = {}
  @@depth = {}
  @@mv = nil
  @@st = nil
  @@gc_last = nil

  PHASES = ["gfx", "scn", "map", "int", "pl", "spr"]

  def self.reset_buckets
    @@mv = { "n" => 0, "sum" => 0.0 }
    @@st = { "n" => 0, "sum" => 0.0 }
  end
  reset_buckets

  def self.ph_add(key, ms)
    @@ph[key] = (@@ph[key] || 0.0) + ms
  end

  # 가장 바깥 호출만 시각을 돌려준다. 안쪽 겹침은 nil — ph_end가 무시한다.
  def self.ph_begin(key)
    @@depth[key] = (@@depth[key] || 0) + 1
    return Time.now if @@depth[key] == 1
    nil
  end

  def self.ph_end(key, t0)
    @@depth[key] -= 1 if (@@depth[key] || 0) > 0
    ph_add(key, (Time.now - t0) * 1000.0) if t0
  end

  def self.context
    parts = []
    parts.push($scene ? $scene.class.to_s : "no-scene")
    parts.push("map" + $game_map.map_id.to_s) if $game_map
    parts.push("evt" + $game_map.events.size.to_s) if $game_map
    parts.push("battle") if $game_temp && $game_temp.in_battle
    parts.push("msg") if $game_temp && $game_temp.message_window_showing
    parts.join(" ")
  end

  def self.fmt_ph(h)
    parts = []
    PHASES.each { |k| parts.push(k + ("%.1f" % (h[k] || 0.0))) }
    parts.join(" ")
  end

  def self.bucket_str(tag, b)
    return tag + " 0f" if b["n"] == 0
    parts = []
    PHASES.each { |k| parts.push(k + ("%.1f" % ((b[k] || 0.0) / b["n"]))) }
    tag + (" %.1fms/%df(" % [b["sum"] / b["n"], b["n"]]) + parts.join(" ") + ")"
  end

  def self.tick(dt)
    ph = @@ph
    @@ph = {}
    moving = false
    begin
      moving = ($game_player and $game_player.moving?)
    rescue
    end
    b = moving ? @@mv : @@st
    b["n"] += 1
    b["sum"] += dt
    ph.each { |k, v| b[k] = (b[k] || 0.0) + v }
    @@count += 1
    @@sum += dt
    @@max = dt if dt > @@max
    if dt >= SLOW_MS
      @@slow += 1
      @@buf.push(Time.now.strftime("%H:%M:%S") + (" slow %dms [" % dt) + fmt_ph(ph) +
                 "]" + (moving ? " mv " : " ") + context)
    end
    if @@count >= SUMMARY_FRAMES
      avg = @@sum / @@count
      fps = 1000.0 / (avg > 0 ? avg : 1.0)
      line = " avg %.1fms (%.1f fps) max %dms slow %d/%d | " %
             [avg, fps, @@max, @@slow, @@count]
      if GC.respond_to?(:count)
        c = GC.count
        line += "gc" + (c - (@@gc_last || c)).to_s + " "
        @@gc_last = c
      end
      line += bucket_str("mv", @@mv) + " " + bucket_str("st", @@st) + " "
      @@buf.push(Time.now.strftime("%H:%M:%S") + line + context)
      flush
      @@count = 0
      @@sum = 0.0
      @@max = 0.0
      @@slow = 0
      reset_buckets
    end
  end

  def self.flush
    return if @@buf.empty?
    begin
      File.open(LOG, "a") { |f| @@buf.each { |l| f.puts(l) } }
    rescue
      # 파일이 잠겨 있어도 게임은 계속 돈다 — 다음 주기에 다시 쓴다
    end
    @@buf.clear
  end

  begin
    File.open(LOG, "a") { |f|
      f.puts("---- " + Time.now.to_s + " boot v3-phases frame_rate=" +
             Graphics.frame_rate.to_s + " slow_ms=" + SLOW_MS.to_s +
             " gc_count=" + (GC.respond_to?(:count) ? "yes" : "no"))
    }
  rescue
  end
end

class Scene_Map
  alias fpz_update update
  def update
    t = FrameProfiler.ph_begin("scn")
    begin
      fpz_update
    ensure
      FrameProfiler.ph_end("scn", t)
    end
  end

  alias fpz_updateMaps updateMaps
  def updateMaps
    t = FrameProfiler.ph_begin("map")
    begin
      fpz_updateMaps
    ensure
      FrameProfiler.ph_end("map", t)
    end
  end

  alias fpz_updateSpritesets updateSpritesets
  def updateSpritesets
    t = FrameProfiler.ph_begin("spr")
    begin
      fpz_updateSpritesets
    ensure
      FrameProfiler.ph_end("spr", t)
    end
  end
end

class Game_Player
  alias fpz_pl_update update
  def update
    t = FrameProfiler.ph_begin("pl")
    begin
      fpz_pl_update
    ensure
      FrameProfiler.ph_end("pl", t)
    end
  end
end

class Interpreter
  alias fpz_int_update update
  def update
    t = FrameProfiler.ph_begin("int")
    begin
      fpz_int_update
    ensure
      FrameProfiler.ph_end("int", t)
    end
  end
end

class << Graphics
  alias fpz_update update

  def update
    now = Time.now
    if defined?(@fpz_last) && @fpz_last
      FrameProfiler.tick((now - @fpz_last) * 1000.0)
    end
    @fpz_last = now
    fpz_update
    FrameProfiler.ph_add("gfx", (Time.now - now) * 1000.0)
  end
end
