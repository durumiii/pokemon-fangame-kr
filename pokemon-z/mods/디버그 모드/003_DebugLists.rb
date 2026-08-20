# 디버그의 목록 화면(맵 이동·도구 추가·포켓몬 추가)을 쓸 만하게 만든다.
#
# 두 가지다.
#
# ① 이름 — 맵 목록은 `MapInfos`를, 도구 목록은 `items.dat`를 직접 읽어 원어(스페인어)를
#    보여 준다. 번역된 이름은 이미 `korean.dat`의 맵 이름 절·도구 이름 절에 있으므로
#    엔진의 조회 함수로 돌린다. 조회가 비면 원래 이름으로 되돌아가므로 한글패치를 안 깐
#    게임에서도 그대로 선다 — 코어 수술에 기대지 않는다.
#
# ② 거르기 — 목록이 수백 줄이라 F키로 좁힌다. 이름 일부는 어디서나, 도구는 주머니,
#    포켓몬은 타입으로도 고른다. 취소하면 전부로 돌아온다.
#
# 포켓몬 고르기는 원래 `pbCommands2`로 뜨는 딴 길이었는데, 목록 화면 하나로 합쳐
# 거르기가 세 화면에서 같게 돌게 했다.

module DebugList
  FILTER_KEY = 0x46   # F. 바꾸려면 이 한 줄(윈도우 가상 키 코드).

  def self.key?
    return false if !Input.respond_to?(:triggerex?)
    begin
      return Input.triggerex?(FILTER_KEY)
    rescue Exception
      return false
    end
  end

  # 이름 일부를 받는다. 비우면 해제.
  def self.ask_name(current)
    begin
      return pbEnterText("찾을 이름의 일부", 0, 20, current.to_s)
    rescue Exception
      return nil
    end
  end

  def self.match?(text, needle)
    return true if !needle || needle == ""
    return false if !text
    return text.downcase.include?(needle.downcase)
  end

  # 맵 이름을 번역 층에서 읽는다. 없으면 준 값 그대로.
  def self.map_name(id, fallback)
    begin
      n = pbGetMessage(MessageTypes::MapNames, id)
      return n if n && n != ""
    rescue Exception
    end
    return fallback
  end

  def self.item_name(id, fallback)
    begin
      n = PBItems.getName(id)
      return n if n && n != ""
    rescue Exception
    end
    return fallback
  end

  # 진짜 타입만 (물음표·다크 같은 가짜 타입은 뺀다)
  def self.type_ids
    ids = []
    begin
      for c in PBTypes.constants
        i = PBTypes.const_get(c)
        next if !i.is_a?(Integer)
        next if PBTypes.respond_to?(:isPseudoType?) && PBTypes.isPseudoType?(i)
        ids.push(i) if !ids.include?(i)
      end
      ids.sort! {|a, b| PBTypes.getName(a) <=> PBTypes.getName(b) }
    rescue Exception
      ids = []
    end
    return ids
  end

  # 종족별 타입 두 칸. 도감 데이터를 한 번만 열고 훑는다.
  def self.species_types
    return @species_types if @species_types
    table = {}
    begin
      dexdata = pbOpenDexData
      for i in 1..PBSpecies.maxValue
        begin
          pbDexDataOffset(dexdata, i, 8)
          table[i] = [dexdata.fgetb, dexdata.fgetb]
        rescue Exception
          table[i] = []
        end
      end
      dexdata.close
    rescue Exception
      table = {}
    end
    @species_types = table
    return table
  end
end


class MapLister
  def commands
    @dbgz_all = @maps.clone if !@dbgz_all
    @maps = []
    for m in @dbgz_all
      name = DebugList.map_name(m[0], m[1])
      next if !DebugList.match?(name, @dbgz_name)
      @maps.push([m[0], name, m[2]])
    end
    @commands = []
    if @addGlobalOffset == 1
      @commands.push(_INTL("[GLOBAL]"))
    end
    for m in @maps
      @commands.push(sprintf("%s%03d %s", ("  " * m[2]), m[0], m[1]))
    end
    @index = 0 if @index >= @commands.length || @dbgz_name
    return @commands
  end

  def dbgz_menu
    sel = Kernel.pbShowCommands(nil, ["이름으로 거르기", "거르기 해제"], -1)
    return false if !sel || sel < 0
    if sel == 1
      return false if !@dbgz_name
      @dbgz_name = nil
      return true
    end
    txt = DebugList.ask_name(@dbgz_name)
    return false if !txt
    @dbgz_name = (txt == "") ? nil : txt
    return true
  end
end


class ItemLister
  def commands
    @itemdata = readItemList("Data/items.dat")
    cmds = []
    for i in 1..PBItems.maxValue
      raw = @itemdata[i][ITEMNAME]
      next if !raw || raw == ""
      next if @itemdata[i][ITEMPOCKET] == 0
      next if @dbgz_pocket && @itemdata[i][ITEMPOCKET] != @dbgz_pocket
      name = DebugList.item_name(i, raw)
      next if !DebugList.match?(name, @dbgz_name)
      cmds.push([i, name])
    end
    cmds.sort! {|a, b| a[1] <=> b[1] }
    @commands = []
    @ids = []
    if @includeNew
      @commands.push(_ISPRINTF("[NEW ITEM]"))
      @ids.push(-1)
    end
    for c in cmds
      @commands.push(_ISPRINTF("{1:03d}: {2:s}", c[0], c[1]))
      @ids.push(c[0])
    end
    @index = @selection
    @index = 0 if @dbgz_name || @dbgz_pocket
    @index = @commands.length - 1 if @index >= @commands.length
    @index = 0 if @index < 0
    return @commands
  end

  def dbgz_menu
    sel = Kernel.pbShowCommands(nil, ["이름으로 거르기", "주머니로 거르기", "거르기 해제"], -1)
    return false if !sel || sel < 0
    if sel == 2
      return false if !@dbgz_name && !@dbgz_pocket
      @dbgz_name = nil
      @dbgz_pocket = nil
      return true
    end
    if sel == 1
      names = pbPocketNames
      picks = []
      labels = []
      for i in 1...names.length
        picks.push(i)
        labels.push(names[i])
      end
      p = Kernel.pbShowCommands(nil, labels, -1)
      return false if !p || p < 0
      @dbgz_pocket = picks[p]
      return true
    end
    txt = DebugList.ask_name(@dbgz_name)
    return false if !txt
    @dbgz_name = (txt == "") ? nil : txt
    return true
  end
end


# 포켓몬 고르기 목록. 원작의 `pbChooseSpeciesOrdered`가 쓰던 자리를 대신한다.
class SpeciesLister
  def initialize(default = 0)
    @sprite = SpriteWrapper.new
    @sprite.bitmap = nil
    @sprite.z = 2
    @default = default
    @ids = []
    @commands = []
    @index = 0
  end

  def setViewport(viewport)
    @sprite.viewport = viewport
  end

  def startIndex
    return @index
  end

  def commands
    types = @dbgz_type ? DebugList.species_types : nil
    cmds = []
    for i in 1..PBSpecies.maxValue
      cname = (getConstantName(PBSpecies, i) rescue nil)
      next if !cname
      if @dbgz_type
        t = types[i]
        next if !t || !t.include?(@dbgz_type)
      end
      name = PBSpecies.getName(i)
      next if !DebugList.match?(name, @dbgz_name)
      cmds.push([i, name])
    end
    cmds.sort! {|a, b| a[1] <=> b[1] }
    @commands = []
    @ids = []
    for c in cmds
      @commands.push(_ISPRINTF("{1:03d} {2:s}", c[0], c[1]))
      @ids.push(c[0])
    end
    @index = 0
    for i in 0...@ids.length
      @index = i if @ids[i] == @default
    end
    return @commands
  end

  def value(index)
    return 0 if index < 0
    return @ids[index] ? @ids[index] : 0
  end

  def refresh(index)
  end

  def dispose
    @sprite.bitmap.dispose if @sprite.bitmap
    @sprite.dispose
  end

  def dbgz_menu
    sel = Kernel.pbShowCommands(nil, ["이름으로 거르기", "타입으로 거르기", "거르기 해제"], -1)
    return false if !sel || sel < 0
    if sel == 2
      return false if !@dbgz_name && !@dbgz_type
      @dbgz_name = nil
      @dbgz_type = nil
      return true
    end
    if sel == 1
      ids = DebugList.type_ids
      return false if ids.length == 0
      labels = []
      for i in ids
        labels.push(PBTypes.getName(i))
      end
      t = Kernel.pbShowCommands(nil, labels, -1)
      return false if !t || t < 0
      @dbgz_type = ids[t]
      return true
    end
    txt = DebugList.ask_name(@dbgz_name)
    return false if !txt
    @dbgz_name = (txt == "") ? nil : txt
    return true
  end
end


def pbChooseSpeciesOrdered(default)
  return pbListScreen("포켓몬 고르기", SpeciesLister.new(default))
end


# 목록 화면에 거르기 키를 더한다. 나머지는 원작 그대로다.
def pbListScreen(title, lister)
  viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
  viewport.z = 99999
  list = pbListWindow([], 256)
  list.viewport = viewport
  list.z = 2
  canfilter = lister.respond_to?(:dbgz_menu)
  titletext = canfilter ? (title.to_s + "\n(F: 거르기)") : title
  title = Window_UnformattedTextPokemon.new(titletext)
  title.x = 256
  title.y = 0
  title.width = Graphics.width - 256
  title.height = canfilter ? 96 : 64
  title.viewport = viewport
  title.z = 2
  lister.setViewport(viewport)
  selected = -1
  commands = lister.commands
  if commands.length == 0 && !canfilter
    value = lister.value(-1)
    lister.dispose
    title.dispose
    list.dispose
    return value
  end
  list.commands = commands
  list.index = lister.startIndex
  loop do
    Graphics.update
    Input.update
    list.update
    if list.index != selected
      lister.refresh(list.index)
      selected = list.index
    end
    if canfilter && DebugList.key?
      if lister.dbgz_menu
        commands = lister.commands
        if commands.length == 0
          Kernel.pbMessage("맞는 것이 없어요.")
          lister.dbgz_menu
          commands = lister.commands
        end
        list.commands = commands
        list.index = lister.startIndex
        selected = -1
      end
      next
    end
    if Input.trigger?(Input::C) || (list.doubleclick? rescue false)
      break if commands.length > 0
    elsif Input.trigger?(Input::B)
      selected = -1
      break
    end
  end
  value = lister.value(selected)
  lister.dispose
  title.dispose
  list.dispose
  Input.update
  return value
end
