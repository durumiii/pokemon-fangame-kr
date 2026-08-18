# 파도타기로 다리 밑 물길을 지나갈 수 있게 고친다 — 원작 엔진의 통행 판정 결함.
#
# Game_Map#playerPassable?는 위 레이어부터 내려오며 통행 여부를 따지는데, 다리
# 타일(지형태그 15)을 만났을 때 「다리 위가 아니면 건너뛴다」는 줄이 $PokemonGlobal.bridge
# 가 0일 때만 걸린다. bridge는 다리에 올라설 때 켜지고 맵 이동·세이브 로드에서
# 리셋되지 않으므로, 한 번 다리를 건넌 뒤에는 켜진 채 남는다. 그 상태로 물에 들어가면
# 다리 타일의 통행 비트로 즉시 판정이 끝나 아래 물 레이어까지 못 내려가고, 다리 밑
# 물길이 벽처럼 막힌다.
#
# 수술은 건너뛰기 조건에 파도타기를 더하는 한 줄이다. 다리 위에서 파도타기는 애초에
# 불가능하므로 surfing 중에는 다리 타일을 언제나 건너뛰어도 안전하다. 원본의
# `$PokemonGlobal &&` nil 가드는 그대로 둔다. 나머지 줄은 원본 그대로다.
#
# 경위와 판독: docs/log/research/2026-08-19-surf-under-bridge.md
class Game_Map
  def playerPassable?(x, y, d, self_event = nil)
    bit = (1 << (d / 2 - 1)) & 0x0f
    for i in [2, 1, 0]
      tile_id = data[x, y, i]
      # Ignore bridge tiles if not on a bridge
      next if $PokemonGlobal && tile_id &&
         PBTerrain.isBridge?(@terrain_tags[tile_id]) &&
         ($PokemonGlobal.bridge==0 || $PokemonGlobal.surfing)
      if tile_id == nil
        return false
      # Make water tiles passable if player is surfing
      elsif $PokemonGlobal.surfing &&
         PBTerrain.isPassableWater?(@terrain_tags[tile_id])
        return true
      # Prevent cycling in really tall grass/on ice
      elsif $PokemonGlobal.bicycle &&
         PBTerrain.onlyWalk?(@terrain_tags[tile_id])
        return false
      # Depend on passability of bridge tile if on bridge
      elsif $PokemonGlobal && $PokemonGlobal.bridge>0 &&
         PBTerrain.isBridge?(@terrain_tags[tile_id])
        if @passages[tile_id] & bit != 0 ||
           @passages[tile_id] & 0x0f == 0x0f
          return false
        else
          return true
        end
      # Regular passability checks
      else #if @terrain_tags[tile_id]!=PBTerrain::Neutral
        if @passages[tile_id] & bit != 0 ||
           @passages[tile_id] & 0x0f == 0x0f
          return false
        elsif @priorities[tile_id] == 0
          return true
        end
      end
    end
    return true
  end

  # 같은 결함의 남은 반쪽 — pbEndSurf(103_PField_HiddenMoves.rb)가 부르는 지형 조회다.
  # 여기도 다리 건너뛰기가 bridge==0일 때만 걸려서, 표시가 켜진 채 다리 밑에 들어가면
  # 데크의 지형 15가 나와 「물 위가 아니다」로 읽히고 그 자리에서 하선당한다.
  # 통행 판정만 고쳐서는 다리 밑을 지나갈 수 없어 이쪽도 같은 꼴로 고친다.
  # surfing 추가는 !countBridge 갈래 안에서만 — 진짜 다리 태그가 필요해 countBridge=true로
  # 부르는 호출들은 원래대로 다리 태그를 받는다.
  def terrain_tag(x, y, countBridge=false)
    if @map_id != 0
      for i in [2, 1, 0]
        tile_id = data[x, y, i]
        next if tile_id && PBTerrain.isBridge?(@terrain_tags[tile_id]) &&
                !countBridge && $PokemonGlobal &&
                ($PokemonGlobal.bridge==0 || $PokemonGlobal.surfing)
        if tile_id == nil
          return 0
        elsif @terrain_tags[tile_id] && @terrain_tags[tile_id] > 0 &&
           @terrain_tags[tile_id]!=PBTerrain::Neutral
          return @terrain_tags[tile_id]
        end
      end
    end
    return 0
  end
end
