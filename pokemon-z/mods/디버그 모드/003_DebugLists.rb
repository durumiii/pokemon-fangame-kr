# 디버그의 목록 화면(맵 이동·도구 추가·포켓몬 추가)을 쓸 만하게 만든다.
#
# ① 이름 — 맵 목록은 `MapInfos`를, 도구 목록은 `items.dat`를 직접 읽어 원어(스페인어)를
#    보여 준다. 번역된 이름은 이미 `korean.dat`의 맵 이름 절·도구 이름 절에 있으므로
#    엔진의 조회 함수로 돌린다. 조회가 비면 원래 이름으로 되돌아가므로 한글패치를 안 깐
#    게임에서도 그대로 선다 — 코어 수술에 기대지 않는다.
#
# ② 필터 — 목록이 수백 줄이라 F키(패드는 X)로 좁힌다. **타이핑에 기대지 않는다** —
#    초성(ㄱ·ㄴ·ㄷ…)은 목록에서 뽑아 고르게 하고, 도구는 주머니, 포켓몬은 타입으로
#    좁힌다. 실행기가 한글 입력을 받아 주면 이름 일부로도 좁힐 수 있게 그 갈래를 함께
#    두되, 없어도 나머지가 다 돈다.
#    ⚠ 걸러 낸 것이 0줄이면 목록 창에 빈 배열을 넣지 않는다 — 넣으면 커서가 없는 줄을
#    그리다 게임이 죽는다(2026-08-21 실기 제보). 그 자리에서 필터를 풀고 전부로 돌아간다.
#
# 포켓몬 고르기는 원래 `pbCommands2`로 뜨는 딴 길이었는데, 목록 화면 하나로 합쳐
# 필터가 세 화면에서 같게 돌게 했다.

module DebugList
  FILTER_KEY = 0x46      # 키보드 F. 바꾸려면 이 줄(윈도우 가상 키 코드).
  FILTER_PAD = Input::X  # 패드 X 버튼. 목록 화면에서는 확인·취소 말고 임자가 없다.

  CHOSEONG = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
              "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

  def self.key?
    return true if Input.trigger?(FILTER_PAD)
    return false if !Input.respond_to?(:triggerex?)
    begin
      return Input.triggerex?(FILTER_KEY)
    rescue Exception
      return false
    end
  end

  # 이름의 초성. 한글이면 ㄱ~ㅎ, 로마자·숫자면 그 글자, 그 밖은 「기타」.
  # 바이트를 첨자로 읽지 않고 unpack으로 푼다 — 구판·신형 루비에서 뜻이 갈리는 자리다.
  def self.head(name)
    return "기타" if !name || name == ""
    b = name.unpack("C*")
    return "기타" if b.length == 0
    if b[0] < 0x80
      c = ("" << b[0]).upcase
      return c
    end
    return "기타" if b.length < 3 || b[0] < 0xE0
    cp = ((b[0] & 0x0F) << 12) | ((b[1] & 0x3F) << 6) | (b[2] & 0x3F)
    return "기타" if cp < 0xAC00 || cp > 0xD7A3
    return CHOSEONG[(cp - 0xAC00) / 588]
  end

  # 이름 차례대로 훑어 초성을 겹치지 않게 모은다(목록이 이미 이름순이라 차례가 맞다).
  def self.heads(names)
    ret = []
    for n in names
      h = head(n)
      ret.push(h) if !ret.include?(h)
    end
    return ret
  end

  # 실행기가 한글 입력을 받아 주는지는 게임마다 다르다. 못 받으면 빈 값이 와서
  # 필터가 안 걸릴 뿐, 다른 갈래는 그대로 돈다.
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

  # 초성 고르기 — 지금 목록에 실제로 있는 초성만 보여 준다.
  # 되돌리는 값: 고른 초성, 또는 취소면 nil.
  def self.pick_head(names)
    hs = heads(names)
    return nil if hs.length == 0
    sel = Kernel.pbShowCommands(nil, hs, -1)
    return nil if !sel || sel < 0
    return hs[sel]
  end

  # 초성을 모을 때는 초성 필터를 뺀 목록을 본다.
  #
  # ⚠ `commands`는 화면 뒤의 배열(@maps·@ids·@commands)을 그 자리에서 갈아 끼운다.
  # 그래서 다 모은 뒤 **원래 필터로 한 번 더 돌려 되돌려 놓는다.** 안 되돌리면 이어지는
  # 초성 고르기를 취소했을 때 `dbgz_menu`가 false를 주고 `pbListScreen`이 목록을 다시
  # 안 그리는데, 화면에는 걸러진 목록이 떠 있고 속은 전체라 커서 자리가 어긋난다 —
  # 맵 목록에서는 엉뚱한 맵으로 워프한다(2026-08-22 제보).
  # 커서(@index)는 두 번째 `commands`가 필터 때문에 0으로 되돌리므로 따로 되살린다.
  module Pool
    def dbgz_pool
      keep = @dbgz_head
      keepindex = @index
      @dbgz_head = nil
      commands
      names = @dbgz_names.clone
      @dbgz_head = keep
      commands
      @index = keepindex
      return names
    end
  end
end


class MapLister
  include DebugList::Pool

  def dbgz_clear
    @dbgz_head = nil
    @dbgz_name = nil
  end

  def commands
    @dbgz_all = @maps.clone if !@dbgz_all
    @maps = []
    @dbgz_names = []
    for m in @dbgz_all
      name = DebugList.map_name(m[0], m[1])
      next if !DebugList.match?(name, @dbgz_name)
      next if @dbgz_head && DebugList.head(name) != @dbgz_head
      @maps.push([m[0], name, m[2]])
      @dbgz_names.push(name)
    end
    @commands = []
    if @addGlobalOffset == 1
      @commands.push(_INTL("[GLOBAL]"))
    end
    for m in @maps
      @commands.push(sprintf("%s%03d %s", ("  " * m[2]), m[0], m[1]))
    end
    @index = 0 if @index >= @commands.length || @dbgz_name || @dbgz_head
    return @commands
  end

  def dbgz_menu
    sel = Kernel.pbShowCommands(nil, ["초성으로 필터", "이름으로 필터", "필터 해제"], -1)
    return false if !sel || sel < 0
    if sel == 2
      return false if !@dbgz_name && !@dbgz_head
      dbgz_clear
      return true
    end
    if sel == 0
      h = DebugList.pick_head(dbgz_pool)
      return false if !h
      @dbgz_head = h
      return true
    end
    txt = DebugList.ask_name(@dbgz_name)
    return false if !txt
    @dbgz_name = (txt == "") ? nil : txt
    return true
  end
end


class ItemLister
  include DebugList::Pool

  def dbgz_clear
    @dbgz_head = nil
    @dbgz_name = nil
    @dbgz_pocket = nil
  end

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
      next if @dbgz_head && DebugList.head(name) != @dbgz_head
      cmds.push([i, name])
    end
    cmds.sort! {|a, b| a[1] <=> b[1] }
    @commands = []
    @ids = []
    @dbgz_names = []
    if @includeNew
      @commands.push(_ISPRINTF("[NEW ITEM]"))
      @ids.push(-1)
    end
    for c in cmds
      @commands.push(_ISPRINTF("{1:03d}: {2:s}", c[0], c[1]))
      @ids.push(c[0])
      @dbgz_names.push(c[1])
    end
    @index = @selection
    @index = 0 if @dbgz_name || @dbgz_pocket || @dbgz_head
    @index = @commands.length - 1 if @index >= @commands.length
    @index = 0 if @index < 0
    return @commands
  end

  def dbgz_menu
    sel = Kernel.pbShowCommands(nil,
       ["초성으로 필터", "주머니로 필터", "이름으로 필터", "필터 해제"], -1)
    return false if !sel || sel < 0
    if sel == 3
      return false if !@dbgz_name && !@dbgz_pocket && !@dbgz_head
      dbgz_clear
      return true
    end
    if sel == 0
      h = DebugList.pick_head(dbgz_pool)
      return false if !h
      @dbgz_head = h
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
      @dbgz_head = nil   # 주머니를 새로 고르면 초성은 그 주머니 것으로 다시 고른다
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
  include DebugList::Pool

  def initialize(default = 0)
    @sprite = SpriteWrapper.new
    @sprite.bitmap = nil
    @sprite.z = 2
    @default = default
    @ids = []
    @commands = []
    @dbgz_names = []
    @index = 0
  end

  def setViewport(viewport)
    @sprite.viewport = viewport
  end

  def startIndex
    return @index
  end

  def dbgz_clear
    @dbgz_head = nil
    @dbgz_name = nil
    @dbgz_type = nil
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
      next if @dbgz_head && DebugList.head(name) != @dbgz_head
      cmds.push([i, name])
    end
    cmds.sort! {|a, b| a[1] <=> b[1] }
    @commands = []
    @ids = []
    @dbgz_names = []
    for c in cmds
      @commands.push(_ISPRINTF("{1:03d} {2:s}", c[0], c[1]))
      @ids.push(c[0])
      @dbgz_names.push(c[1])
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
    sel = Kernel.pbShowCommands(nil,
       ["초성으로 필터", "타입으로 필터", "이름으로 필터", "필터 해제"], -1)
    return false if !sel || sel < 0
    if sel == 3
      return false if !@dbgz_name && !@dbgz_type && !@dbgz_head
      dbgz_clear
      return true
    end
    if sel == 0
      h = DebugList.pick_head(dbgz_pool)
      return false if !h
      @dbgz_head = h
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
      @dbgz_head = nil   # 타입을 새로 고르면 초성은 그 타입 것으로 다시 고른다
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


# 목록 화면에 필터 키를 더한다. 나머지는 원작 그대로다.
def pbListScreen(title, lister)
  viewport = Viewport.new(0, 0, Graphics.width, Graphics.height)
  viewport.z = 99999
  list = pbListWindow([], 256)
  list.viewport = viewport
  list.z = 2
  canfilter = lister.respond_to?(:dbgz_menu)
  # 단축키 표기는 **키보드 기준으로만** 적는다. 패드 표기는 Controller UX가 UiTextKR의
  # 치환표에 쌍을 얹어 덮으므로, 우리는 그 훅이 걸린 `text=`로 넣기만 하면 된다
  # (`new(문자열)`은 @text에 바로 넣어 훅을 안 지난다 — 실측). 저쪽 모드가 없으면
  # 키보드 표기가 그대로 남는다.
  titletext = canfilter ? (title.to_s + "\n필터: F") : title.to_s
  title = Window_UnformattedTextPokemon.new("")
  title.x = 256
  title.y = 0
  title.width = Graphics.width - 256
  title.height = canfilter ? 96 : 64
  title.viewport = viewport
  title.z = 2
  title.text = titletext
  lister.setViewport(viewport)
  selected = -1
  commands = lister.commands
  if commands.length == 0
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
        fresh = lister.commands
        if fresh.length == 0
          # 빈 목록은 창에 넣지 않는다 — 넣으면 커서가 없는 줄을 그리다 죽는다.
          Kernel.pbMessage("맞는 것이 없어요. 필터를 풀게요.")
          lister.dbgz_clear if lister.respond_to?(:dbgz_clear)
          fresh = lister.commands
        end
        if fresh.length > 0
          commands = fresh
          list.commands = commands
          list.index = lister.startIndex
          selected = -1
        end
      end
      next
    end
    if Input.trigger?(Input::C) || (list.doubleclick? rescue false)
      break
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
