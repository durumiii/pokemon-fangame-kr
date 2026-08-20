# 리전 맵 커서에 스냅을 붙인다 (Ruby 1.8.7 / 3.1+ 공통).
#
# 커서가 SNAP_DELAY프레임 동안 가만히 있었고, 선 칸에 보이는 장소 지점이 없으면
# 주변 반경 SNAP_RADIUS칸(8방향) 중 가장 가까운 보이는 지점으로 커서를 끌어당긴다.
# 끌림도 기존 이동과 같은 4프레임 슬라이드를 쓴다.
#
# 대기 프레임을 두는 이유 — 손 뗀 즉시 끌어당기면 방향키를 톡톡 두드려 커서를 옮기는
# 동안 매 타건마다 끌려가 조작을 방해한다(유지자 실기 판정 2026-08-20).
#
# PokemonRegionMapScene을 재오픈해 pbMapScene만 다시 정의한다(순정 278-354줄 복사 +
# 스냅 삽입부). 열람(mode 0)·비행(mode 1)이 같은 루프를 쓰므로 양쪽에 함께 걸린다.
# 리전 맵을 만지는 다른 모드가 생기면 로드 순서를 확인할 것.
class PokemonRegionMapScene
  SNAP_RADIUS = 1   # 실기 감으로 조절할 자리 — 칸 단위 반경
  SNAP_DELAY  = 12  # 입력이 끊긴 뒤 이만큼 지나야 끌어당긴다 (기본 40fps 기준 0.3초)

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

  # 반경 안의 보이는 지점 중 가장 가까운 칸 [x,y]. 없으면 nil.
  # 거리는 제곱거리로 재므로 상하좌우(1)가 대각(2)보다 먼저 걸리고, 완전 동점이면
  # 목록 순 첫 지점이 남는다.
  def pbSnapTarget(x,y)
    return nil if !@map || !@map[2]
    best=nil
    bestdist=0
    for loc in @map[2]
      next if !pbSnapVisibleLoc?(loc)
      dx=loc[0]-x
      dy=loc[1]-y
      next if dx==0 && dy==0
      next if dx.abs>SNAP_RADIUS || dy.abs>SNAP_RADIUS
      next if loc[0]<LEFT || loc[0]>RIGHT || loc[1]<TOP || loc[1]>BOTTOM
      dist=dx*dx+dy*dy
      if !best || dist<bestdist
        best=[loc[0],loc[1]]
        bestdist=dist
      end
    end
    return best
  end

  def pbMapScene(mode=0)
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
