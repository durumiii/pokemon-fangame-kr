# 리전 맵 커서에 스냅을 붙인다 (Ruby 1.8.7 / 3.1+ 공통).
#
# 커서가 SNAP_DELAY프레임 동안 가만히 있었고, 선 칸에 보이는 장소 지점이 없으면
# 주변 반경 SNAP_RADIUS칸(8방향) 중 가장 가까운 **표지 칸**으로 커서를 끌어당긴다.
# 끌림도 기존 이동과 같은 4프레임 슬라이드를 쓴다.
#
# 끌어당길 자리는 장소 데이터가 아니라 그림에 표지가 그려진 칸이다(유지자 실기 판정
# 2026-08-20). 데이터 칸 175개 중 118개는 길과 여러 칸에 걸친 넓은 지역이라 표지가
# 없는데, 그런 칸까지 목표로 삼으면 커서가 눈에 보이는 표지 대신 옆의 길로 끌렸다.
#
# 대기 프레임을 두는 이유 — 손 뗀 즉시 끌어당기면 방향키를 톡톡 두드려 커서를 옮기는
# 동안 매 타건마다 끌려가 조작을 방해한다(유지자 실기 판정 2026-08-20).
#
# PokemonRegionMapScene을 재오픈해 pbMapScene만 다시 정의한다(순정 278-354줄 복사 +
# 스냅 삽입부). 열람(mode 0)·비행(mode 1)이 같은 루프를 쓰므로 양쪽에 함께 걸린다.
# 리전 맵을 만지는 다른 모드가 생기면 로드 순서를 확인할 것.
#
# 원작 지도에서 빠진 지점(MISSING_POINTS)도 여기서 채운다 — 표지는 그려져 있는데
# 장소 목록에 없어 이름도 스냅도 없던 자리다.
class PokemonRegionMapScene
  SNAP_RADIUS = 1   # 실기 감으로 조절할 자리 — 칸 단위 반경
  SNAP_DELAY  = 12  # 입력이 끊긴 뒤 이만큼 지나야 끌어당긴다 (기본 40fps 기준 0.3초)

  # 원작 지도에서 빠진 지점 — 그림에는 표지가 그려져 있는데 장소 목록에 항목이 없어
  # 커서를 올려도 이름이 안 뜨고 스냅도 안 걸리던 자리다. 화면이 열릴 때 채운다.
  # 서부 카타콤: 삼채시티 오른쪽 위, 포켓몬 요새를 지나 들어간다(맵 401·403). 네 방위
  # 카타콤 중 이것만 목록에 없다(2026-08-21 유지자 실기 확인 + 데이터 대조).
  # 꼴은 [x, y, 원어 이름, 한국어 이름]이다. 게임의 장소 이름이 번역돼 있으면 한국어를,
  # 아니면 원어를 넣는다 — 이 지점은 원작 목록에 없어 번역표에도 열쇠가 없으므로,
  # 모드가 두 이름을 다 들고 있어야 한글패치 위에서도 순정 위에서도 제 이름이 뜬다.
  MISSING_POINTS = [
    [6,9,"Catacumbas Occidentales","서부 카타콤"]
  ]
  KO_PROBE = "Catacumbas Meridionales"   # 번역 여부를 가늠할 이웃 장소(남부 카타콤)

  # 빠진 지점을 장소 목록에 채운다. 이미 있으면(원작이 고쳐지면) 손대지 않는다.
  # 항목 꼴은 순정과 같다 — [x, y, 이름, 설명, 회복맵, 회복x, 회복y, 표시스위치].
  # 회복 칸이 비어 있으므로 비행 목적지로는 서지 않는다(순정 pbGetHealingSpot).
  def pbSnapFillMissing
    return if !@map || !@map[2]
    translated=(pbGetMessageFromHash(MessageTypes::PlaceNames,KO_PROBE)!=KO_PROBE)
    for pt in MISSING_POINTS
      here=false
      for loc in @map[2]
        here=true if loc[0]==pt[0] && loc[1]==pt[1]
      end
      next if here
      @map[2].push([pt[0],pt[1],(translated ? pt[3] : pt[2]),"",nil,nil,nil,nil])
    end
  end

  # 표지가 그려진 칸. 손으로 고치지 마라 — 두 표시 사이는 생성기가 통째로 다시 쓴다
  # (`uv run tools/regionmap_points.py --write`, 그림 정본과 townmap.dat에서 뽑는다).
  # >>> 표지 칸 — 생성기가 채운다 (tools/regionmap_points.py)
  SNAP_POINTS = [
    [23,0],[10,1],[18,1],[26,1],[28,1],[7,2],[13,2],[19,2],
    [22,2],[27,2],[7,3],[17,3],[26,4],[8,5],[14,5],[16,5],
    [20,5],[4,6],[16,6],[18,6],[19,6],[22,6],[26,6],[27,6],
    [14,7],[16,7],[8,8],[10,8],[18,8],[21,8],[28,8],[11,9],
    [25,9],[5,10],[8,10],[11,10],[14,10],[19,10],[23,10],[27,10],
    [12,11],[18,11],[24,11],[13,12],[21,12],[28,12],[18,13],[23,13],
    [27,13],[5,14],[19,14],[5,15],[3,16],[13,16],[4,17],[5,17],
    [13,17],[18,17],[19,17],[25,17],[22,18],[26,18]
  ]
  # <<< 표지 칸

  # 순정 pbGetMapLocation(213줄 부근)의 표시 조건을 그대로 복제한다.
  # loc[7]이 있고 그 스위치가 꺼져 있으면 미공개 지점이라 스냅 대상에서 뺀다.
  def pbSnapVisibleLoc?(loc)
    return !loc[7] || (!@wallmap && $game_switches[loc[7]])
  end

  def pbSnapHasPoint?(x,y)
    return false if !@map || !@map[2]
    for loc in @map[2]
      return true if loc[0]==x && loc[1]==y && pbSnapVisibleLoc?(loc)
    end
    return false
  end

  # 반경 안의 표지 칸 중 가장 가까운 칸 [x,y]. 없으면 nil.
  # 거리는 제곱거리로 재므로 상하좌우(1)가 대각(2)보다 먼저 걸리고, 완전 동점이면
  # 표 순서의 첫 칸이 남는다. 미공개 지점은 pbSnapHasPoint?가 걸러 준다.
  def pbSnapTarget(x,y)
    return nil if !@map || !@map[2]
    best=nil
    bestdist=0
    for pt in SNAP_POINTS+MISSING_POINTS
      dx=pt[0]-x
      dy=pt[1]-y
      next if dx==0 && dy==0
      next if dx.abs>SNAP_RADIUS || dy.abs>SNAP_RADIUS
      next if pt[0]<LEFT || pt[0]>RIGHT || pt[1]<TOP || pt[1]>BOTTOM
      next if !pbSnapHasPoint?(pt[0],pt[1])
      dist=dx*dx+dy*dy
      if !best || dist<bestdist
        best=[pt[0],pt[1]]
        bestdist=dist
      end
    end
    return best
  end

  def pbMapScene(mode=0)
    pbSnapFillMissing
    xOffset=0
    yOffset=0
    newX=0
    newY=0
    snapIdle=0
    @sprites["cursor"].x=-SQUAREWIDTH/2+(@mapX*SQUAREWIDTH)+(Graphics.width-@sprites["map"].bitmap.width)/2
    @sprites["cursor"].y=-SQUAREHEIGHT/2+(@mapY*SQUAREHEIGHT)+(Graphics.height-@sprites["map"].bitmap.height)/2
    loop do
      Graphics.update
      Input.update
      pbUpdate
      if xOffset!=0 || yOffset!=0
        snapIdle=0
        xOffset+=xOffset>0 ? -4 : (xOffset<0 ? 4 : 0)
        yOffset+=yOffset>0 ? -4 : (yOffset<0 ? 4 : 0)
        @sprites["cursor"].x=newX-xOffset
        @sprites["cursor"].y=newY-yOffset
        next
      end
      @sprites["mapbottom"].maplocation=pbGetMapLocation(@mapX,@mapY)
      @sprites["mapbottom"].mapdetails=pbGetMapDetails(@mapX,@mapY)
      ox=0
      oy=0
      case Input.dir8
      when 1 # lower left
        oy=1 if @mapY<BOTTOM
        ox=-1 if @mapX>LEFT
      when 2 # down
        oy=1 if @mapY<BOTTOM
      when 3 # lower right
        oy=1 if @mapY<BOTTOM
        ox=1 if @mapX<RIGHT
      when 4 # left
        ox=-1 if @mapX>LEFT
      when 6 # right
        ox=1 if @mapX<RIGHT
      when 7 # upper left
        oy=-1 if @mapY>TOP
        ox=-1 if @mapX>LEFT
      when 8 # up
        oy=-1 if @mapY>TOP
      when 9 # upper right
        oy=-1 if @mapY>TOP
        ox=1 if @mapX<RIGHT
      end
      # --- 스냅 삽입부 ---
      # 여기 닿았다는 것은 슬라이드 오프셋이 0이라는 뜻이다(위에서 next로 걸러짐).
      # 방향키를 누르고 있으면(가장자리를 밀고 있을 때 포함) 대기 셈이 0으로 돌아간다.
      # 스냅하면 커서가 지점 위에 앉으므로 다음 판에는 pbSnapHasPoint?가 참이 되어
      # 반복 스냅이 구조적으로 안 난다.
      if ox==0 && oy==0 && Input.dir8==0 && !pbSnapHasPoint?(@mapX,@mapY)
        snapIdle+=1
        if snapIdle>=SNAP_DELAY
          snap=pbSnapTarget(@mapX,@mapY)
          if snap
            ox=snap[0]-@mapX
            oy=snap[1]-@mapY
          end
        end
      else
        snapIdle=0
      end
      # --- 스냅 삽입부 끝 ---
      if ox!=0 || oy!=0
        @mapX+=ox
        @mapY+=oy
        xOffset=ox*SQUAREWIDTH
        yOffset=oy*SQUAREHEIGHT
        newX=@sprites["cursor"].x+xOffset
        newY=@sprites["cursor"].y+yOffset
      end
      if Input.trigger?(Input::B)
        if @editor && @changed
          if Kernel.pbConfirmMessage(_INTL("¿Guardar los cambios?")) { pbUpdate }
            pbSaveMapData
          end
          if Kernel.pbConfirmMessage(_INTL("¿Salir del mapa?")) { pbUpdate }
            break
          end
        else
          break
        end
      elsif Input.trigger?(Input::C) && mode==1 # Choosing an area to fly to
        healspot=pbGetHealingSpot(@mapX,@mapY)
        if healspot
          if $PokemonGlobal.visitedMaps[healspot[0]] ||
             ($DEBUG && Input.press?(Input::CTRL))
            return healspot
          end
        end
      elsif Input.trigger?(Input::C) && @editor # Intentionally placed after other C button check
        pbChangeMapLocation(@mapX,@mapY)
      end
    end
    return nil
  end
end
