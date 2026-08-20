# 디버그 메뉴의 차례를 다시 잡고, 덜 쓰는 항목을 묶음으로 접고, 우리 토글 둘을 얹는다.
#
# 원작 `pbDebugMenu`(600줄)는 손대지 않는다. 그 메뉴가 쓰는 `CommandList`가 스무 줄짜리
# 이고 게임 전체에서 디버그 메뉴 한 곳만 쓰므로(실측: `CommandList.new` 호출 1건),
# 그 클래스만 갈아 끼우면 차례·묶음·항목 추가가 다 된다.
#
# 묶음을 고르면 `getCommand`가 그 자리에서 하위 목록을 열고 고른 항목의 열쇠를 돌려준다.
# 우리 토글을 고르면 그 자리에서 값을 뒤집고 nil을 돌려준다 — 원작 분기가 아무것도
# 안 타고 메뉴로 돌아오므로 원작 코드에 손댈 일이 없다.
#
# 차례를 바꾸려면 아래 TOP 배열의 줄 차례만 바꾸면 된다.
class CommandList
  # 첫 화면에 그대로 서는 항목 — 이 차례대로 뜬다.
  # `dbgz_`로 시작하는 둘은 원작에 없는 우리 항목이다(004_DebugPerks.rb의 깃발).
  TOP = [
    "warp", "healparty", "usepc",
    "additem", "addpokemon", "setmoney",
    "dbgz_heal", "dbgz_hm",
    "refreshmap",
    "testwildbattle", "testtrainerbattle",
    "testdoublewildbattle", "testdoubletrainerbattle",
    "switches", "variables", "setbadges"
  ]

  # 접어 두는 묶음 — [묶음 이름, 그 안의 항목 차례].
  # 「개발 도구」에는 게임 파일을 쓰는 것과 이 게임이 안 쓰는 기능을 함께 넣었다
  # (렐릭 스톤·정화의 방·이상한 소포는 맵 이벤트 전수에서 호출 0건).
  GROUPS = [
    ["플레이어 설정", ["setplayer", "renameplayer", "randomid", "changeoutfit",
                      "toggleshoes", "togglepokegear", "togglepokedex",
                      "dexlists", "setcoins"]],
    ["박스와 가방",   ["fillbag", "clearbag", "fillboxes", "clearboxes", "demoparty"]],
    ["필드와 데이터", ["roamerstatus", "roam", "setencounters", "setmetadata",
                      "terraintags", "resettrainers", "readyrematches",
                      "daycare", "quickhatch"]],
    ["개발 도구",     ["dbgz_devmode",
                      "extracttext", "compiletext", "compiledata", "animeditor",
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

  # 우리 항목은 라벨에 지금 상태를 싣는다. 메뉴를 열 때마다 다시 셈한다.
  def dbgz_extras
    return if !defined?(DebugPerks)
    add("dbgz_heal", "전투 후 자동 회복: " + DebugPerks.onoff(DebugPerks.heal))
    add("dbgz_hm", "비전기술·라이드 자동 통과: " + DebugPerks.onoff(DebugPerks.hm))
    add("dbgz_devmode", "개발자 모드: " + DebugPerks.onoff(DebugPerks.devmode))
  end

  # 첫 화면 목록. 표에 이름이 없는 항목(다른 모드가 더한 것)은 잃지 않고 뒤에 붙인다.
  def list
    dbgz_extras
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

  # 우리 항목이면 그 자리에서 값을 뒤집고 nil을 돌려준다.
  def dbgz_toggle(key)
    return key if !key
    return key if key != "dbgz_heal" && key != "dbgz_hm" && key != "dbgz_devmode"
    return nil if !defined?(DebugPerks)
    if key == "dbgz_devmode"
      DebugPerks.devmode = !DebugPerks.devmode
      if DebugPerks.devmode
        Kernel.pbMessage("개발자 모드 켬 — 리전 맵이 편집기로 열리고, 중요한 도구도 버릴 수 있고, 알에게 기술을 가르치고, 데이터에 없는 트레이너를 부르면 추가할지 묻습니다.")
        Kernel.pbMessage("리전 맵을 나갈 때 저장에 승낙하면 지도 데이터가 바뀌니 조심하세요.")
      else
        Kernel.pbMessage("개발자 모드 끔 — 그 넷이 평소 규칙대로 돌아갑니다.")
      end
    elsif key == "dbgz_heal"
      DebugPerks.heal = !DebugPerks.heal
      Kernel.pbMessage("전투 후 자동 회복 " + DebugPerks.onoff(DebugPerks.heal) + ".")
    else
      DebugPerks.hm = !DebugPerks.hm
      if DebugPerks.hm
        Kernel.pbMessage("비전기술·라이드를 배지도 기술도 없이 쓸 수 있어요.")
      else
        Kernel.pbMessage("비전기술·라이드가 평소 규칙대로 돌아갑니다.")
      end
    end
    return nil
  end

  def getCommand(index)
    return nil if index < 0
    list if !@top
    return dbgz_toggle(@top[index]) if index < @top.length
    g = @groups[index - @top.length]
    return nil if !g
    names = []
    for key in g[1]
      names.push(@labels[key])
    end
    sel = Kernel.pbShowCommands(nil, names, -1)
    return nil if !sel || sel < 0
    return dbgz_toggle(g[1][sel])
  end
end
