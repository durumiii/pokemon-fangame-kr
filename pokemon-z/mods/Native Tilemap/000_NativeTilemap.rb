# 맵 렌더러를 엔진 내장(원본) 타일맵으로 되돌린다 — Joiplay에서 커스텀 렌더러가
# 깨지는 문제의 우회(레딧 제보, Z-35). Settings의 MAPVIEWMODE 상수는 그대로 두고
# 유일한 소비처인 PokemonSystem#tilemap이 0을 돌려주게 덮는다.
# TilemapLoader는 0을 받아도 내장 Tilemap을 못 쓰는 환경($ResizeFactor != 1.0 등)
# 이면 스스로 CustomTilemap으로 폴백한다 — 최악이 현행 동작이다.
class PokemonSystem
  def tilemap
    return 0
  end
end
