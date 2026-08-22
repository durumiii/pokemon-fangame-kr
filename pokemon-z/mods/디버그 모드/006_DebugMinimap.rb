# 맵 목록의 축소 지도가 그림을 놓아 주지 않아 「Out of memory」로 튕기던 것을 고친다.
#
# 원작 `createMinimap`은 `TileDrawingHelper.fromTileset`으로 타일셋 그림 한 장과
# 오토타일 일곱 장을 열고 `helper.dispose`를 끝내 안 부른다. 목록에서 커서가 한 칸
# 움직일 때마다 그것이 다시 불리는데, 이 게임 타일셋은 비트맵으로 펴면 한 장 20~30MB이고
# 47종이라 훑는 동안 합계가 1GB를 넘는다. 실행 파일이 32비트라 주소 공간이 2GB뿐이라
# 거기서 엔진 쪽 비트맵 메모리가 마른다(오류 문구가 루비의 「failed to allocate memory」가
# 아니라 「Out of memory」인 것이 그 표시다).
#
# 고친 꼴 — helper를 하나만 살려 두고 타일셋이 바뀔 때 옛 것을 dispose한다. 최대 점유가
# 한두 장으로 떨어지고, 같은 지역을 훑는 동안(같은 타일셋)에는 다시 열지도 않는다.
# 목록 화면을 닫을 때 마지막 하나까지 놓는다.
#
# dispose가 안전한가 — `pbGetTileset`·`pbGetAutotile`이 돌려주는 것은 `BitmapCache`가
# 물고 있는 **같은 객체**다. 다만 `BitmapWrapper`가 참조 수를 세어 부를 때마다 +1,
# dispose마다 -1이고 0에서만 진짜로 놓으므로(절 `BitmapCache`), 우리가 연 몫만 정확히
# 닫는 셈이 된다 — 다른 자리가 쥔 것은 그대로 산다. 구판 루비 실물에서 확인했다.
#
# 원작의 다른 두 자리(`MapSprite`·맵 연결 편집기의 `getMapSprite`)도 같은 함수를 지나
# 함께 고쳐진다. 셋 다 helper를 제 안에 쥐지 않고 그 자리에서 버리므로, 하나를 돌려
# 쓰는 것이 그쪽에서도 안전하다.

module DebugMinimap
  # 지금 쥔 helper. 타일셋 번호가 같으면 그대로 쓰고, 갈리면 옛 것을 놓고 새로 연다.
  def self.helper(tilesetid, tileset)
    if @id != tilesetid || !@helper
      release
      @helper = TileDrawingHelper.fromTileset(tileset)
      @id = tilesetid
    end
    return @helper
  end

  def self.release
    @helper.dispose if @helper
    @helper = nil
    @id = nil
  end
end


def createMinimap(mapid)
  map = load_data(sprintf("Data/Map%03d.rxdata", mapid)) rescue nil
  return BitmapWrapper.new(32, 32) if !map
  bitmap = BitmapWrapper.new(map.width * 4, map.height * 4)
  black = Color.new(0, 0, 0)
  tilesets = load_data("Data/Tilesets.rxdata")
  tileset = tilesets[map.tileset_id]
  return bitmap if !tileset
  helper = DebugMinimap.helper(map.tileset_id, tileset)
  for y in 0...map.height
    for x in 0...map.width
      for z in 0..2
        id = map.data[x, y, z]
        id = 0 if !id
        helper.bltSmallTile(bitmap, x * 4, y * 4, 4, 4, id)
      end
    end
  end
  bitmap.fill_rect(0, 0, bitmap.width, 1, black)
  bitmap.fill_rect(0, bitmap.height - 1, bitmap.width, 1, black)
  bitmap.fill_rect(0, 0, 1, bitmap.height, black)
  bitmap.fill_rect(bitmap.width - 1, 0, 1, bitmap.height, black)
  return bitmap
end


class MapLister
  # 원작 그대로에 helper 놓기만 더한다(원작은 이 두 줄이 전부다).
  def dispose
    @sprite.bitmap.dispose if @sprite.bitmap
    @sprite.dispose
    DebugMinimap.release
  end
end
