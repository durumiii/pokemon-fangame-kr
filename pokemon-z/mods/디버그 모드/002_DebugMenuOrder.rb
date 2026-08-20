# 디버그 메뉴의 순서를 다시 잡고, 덜 쓰는 항목을 묶음으로 접는다.
#
# 원작 `pbDebugMenu`(600줄)는 손대지 않는다. 그 메뉴가 쓰는 `CommandList`가 스무 줄짜리
# 이고 게임 전체에서 디버그 메뉴 한 곳만 쓰므로(실측: `CommandList.new` 호출 1건),
# 그 클래스만 갈아 끼우면 순서·묶음이 다 된다.
#
# 묶음을 고르면 `getCommand`가 그 자리에서 하위 목록을 열고 고른 항목의 열쇠를 돌려준다.
# 취소하면 nil이라 원작 분기가 아무것도 안 타고 메뉴로 돌아간다.
#
# 순서를 바꾸려면 아래 TOP 배열의 줄 차례만 바꾸면 된다.
class CommandList
  # 첫 화면에 그대로 서는 항목 — 이 차례대로 뜬다.
  TOP = [
    "warp", "healparty", "usepc",
    "additem", "addpokemon", "setmoney", "refreshmap",
    "testwildbattle", "testtrainerbattle",
    "testdoublewildbattle", "testdoubletrainerbattle",
    "switches", "variables", "setbadges"
  ]

  # 접어 두는 묶음 — [묶음 이름, 그 안의 항목 차례].
  # 「개발 도구」에는 게임 파일을 쓰는 것과 이 게임이 안 쓰는 기능을 함께 넣었다
  # (렐릭 스톤·정화의 방·미스터리 기프트는 맵 이벤트 전수에서 호출 0건).
  GROUPS = [
    ["플레이어 설정", ["setplayer", "renameplayer", "randomid", "changeoutfit",
                      "toggleshoes", "togglepokegear", "togglepokedex",
                      "dexlists", "setcoins"]],
    ["박스와 가방",   ["fillbag", "clearbag", "fillboxes", "clearboxes", "demoparty"]],
    ["필드와 데이터", ["roamerstatus", "roam", "setencounters", "setmetadata",
                      "terraintags", "resettrainers", "readyrematches",
                      "daycare", "quickhatch"]],
    ["개발 도구",     ["extracttext", "compiletext", "compiledata", "animeditor",
                      "mapconnections", "trainertypes", "debugconsole",
                      "togglelogging", "relicstone", "purifychamber", "mysterygift"]]
  ]

  def initialize
    @keys = []
    @labels = {}
    @top = nil
    @groups = nil
  end

  def add(key, value)
    @keys.push(key) if !@keys.include?(key)
    @labels[key] = value
  end

  # 첫 화면 목록. 표에 이름이 없는 항목(다른 모드가 더한 것)은 잃지 않고 뒤에 붙인다.
  def list
    known = []
    @top = []
    for key in TOP
      known.push(key)
      @top.push(key) if @keys.include?(key)
    end
    for g in GROUPS
      for key in g[1]
        known.push(key)
      end
    end
    for key in @keys
      @top.push(key) if !known.include?(key)
    end
    @groups = []
    for g in GROUPS
      inner = []
      for key in g[1]
        inner.push(key) if @keys.include?(key)
      end
      @groups.push([g[0], inner]) if inner.length > 0
    end
    ret = []
    for key in @top
      ret.push(@labels[key])
    end
    for g in @groups
      ret.push(g[0] + "...")
    end
    return ret
  end

  def getCommand(index)
    return nil if index < 0
    list if !@top
    return @top[index] if index < @top.length
    g = @groups[index - @top.length]
    return nil if !g
    names = []
    for key in g[1]
      names.push(@labels[key])
    end
    sel = Kernel.pbShowCommands(nil, names, -1)
    return nil if !sel || sel < 0
    return g[1][sel]
  end
end
