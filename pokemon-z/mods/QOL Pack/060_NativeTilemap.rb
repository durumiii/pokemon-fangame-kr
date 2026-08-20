# 맵 렌더러를 엔진 내장(원본) 타일맵으로 되돌린다 — Joiplay에서 커스텀 렌더러가
# 깨지는 문제의 우회(레딧 제보, Z-35). Settings의 MAPVIEWMODE 상수는 그대로 두고
# 유일한 소비처인 PokemonSystem#tilemap이 0을 돌려주게 덮는다.
# TilemapLoader는 0을 받아도 내장 Tilemap을 못 쓰는 환경($ResizeFactor != 1.0 등)
# 이면 스스로 CustomTilemap으로 폴백한다 — 최악이 현행 동작이다.
#
# 다만 다리가 놓인 맵만은 예외로 커스텀 렌더러를 쓴다. 다리 위에 올라섰을 때 다리
# 그림을 캐릭터 아래로 내리는 보정이 CustomTilemap에만 있어서(Tilemap_XP의
# `spriteZ=1 if @priorities[id]==4 && $PokemonGlobal.bridge>0` 두 줄), 내장 렌더러로는
# 다리가 캐릭터 위로 그려진다. 다리 밑을 지나다닐 수 있는 칸이 실제로 있어
# 타일 우선도를 아예 내려 버리는 길은 막혀 있다.
#
# 아래 목록은 `pbBridgeOn`을 부르는 맵 전수다(V2.18 실측 — 맵 이벤트 전수 조회,
# 공용 이벤트·스크립트에는 호출이 없다). 다리 타일이 있어도 이 호출이 없는 맵은
# 두 렌더러의 결과가 같으므로 목록에 넣지 않는다.
#   5번도로(55) · 7번도로 북쪽(76) · 옛 고목내마을(140) ·
#   18번도로(287) · 19번도로(299) · 미르 신시가지 서쪽(391)
# 이 게임은 맵 연결(connections)이 비어 있어 한 번에 한 맵만 그려진다 — 그래서
# 지금 렌더러를 고를 때 보는 맵은 언제나 $game_map이다.
class PokemonSystem
  BRIDGE_MAP_IDS = [55, 76, 140, 287, 299, 391]

  def tilemap
    return 1 if $game_map && BRIDGE_MAP_IDS.include?($game_map.map_id)
    return 0
  end
end
