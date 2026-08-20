# 「QOL Pack」 자체 점검 — 구판 루비(1.8.7) 실물에서 모드 조각의 셈을 잰다.
#
# 무엇을 재나 — Z-42(pbSpeed 수술) · Z-50 ①(볼 단축키) · Z-50 ②(포획 후 자동 보관) ·
# 리전 맵 커서 스냅이 하는 일이 그대로인가.
#   ⓐ 등장 턴에 pbSpeed를 여러 번 불러도 치료·문구가 0번 돈다
#   ⓑ pbAbilitiesOnSwitchIn 한 번에 치료·문구가 정확히 1번 돈다
#   ⓒ 쇠약·출혈 걸린 아군이 있어도 예외가 안 난다(원본은 여기서 NameError)
#   ⓓ 위장이 SLOWSTART·ACOMETIDA 배율을 안 바꾼다
#   ⓔ 마지막에 쓴 볼이 있고 갖고 있으면 그것이, 없으면 옛 사슬이 골라진다
#   ⓕ $lastUsed(도구 빠른 칸)가 볼 사용에 안 물든다
#   ⓖ 스냅이 대각 칸을 안 고르고 상하좌우만 고른다
#   ⓗ 자동 보관이면 파티가 만석이어도 안 묻고 박스로 내려간다
#   ⓘ 물어보기면 원본과 같이 묻는다
#   ⓙ 파티에 자리가 있으면 어느 값이든 안 묻는다
#   ⓚ 옛 세이브 꼴(값이 없는 $PokemonSystem)에서 기본값이 자동 보관으로 읽힌다
#   ⓛ 옵션 항목 둘이 이름·값 차례대로 서고, 골라 두면 각자 설명이 뜬다
#   ⓜ 「별명 물음」이 끄기면 전투 포획도 필드 부화도 안 묻고, 켜기면 묻는다
#   ⓝ 파티·박스가 다 차면 볼 단축키가 볼을 안 쓰고 안내만 낸다
#   ⓞ 박스가 꽉 차 저장에 실패해도 peer가 예외 없이 안내를 낸다
#   ⓟ 이미 가진 도구를 주는 공통 이벤트는 안 불리고, 나머지는 그대로 불린다
#
# 화면은 못 잰다 — 커맨드 창에 아이콘이 실제로 그려지는 모양은 사람 몫이다.
#
# 돌리는 법(시험대는 packaging 지침 「구판 루비에서 한 줄 재는 법」):
#   1. 이 파일을 D:/ztest/ 에, 모드의 .rb 를 D:/ztest/check/ 에 둔다.
#   2. D:/ztest/rundir/mkxp.json 의 customScript 를 이 파일로 바꾼다.
#   3. rundir 에서 Game.exe 를 돌린다.
#   4. 결과는 D:/ztest/qa-qolpack_out.txt. **customScript 를 syntax.rb 로 되돌린다.**
CHECK = "D:/ztest/check"
OUT   = "D:/ztest/qa-qolpack_out.txt"

$out = []
$bad = 0
def log(s); $out << s.to_s; end
def chk(label, got, want)
  ok = (got == want)
  $bad += 1 if !ok
  log("#{ok ? 'OK ' : 'X  '} #{label} = #{got.inspect}#{ok ? '' : " (기대 #{want.inspect})"}")
end

def _INTL(str, *args)
  args.each_with_index {|a, i| str = str.gsub("{#{i + 1}}", a.to_s) }
  return str
end

# ── 도구 껍데기 ────────────────────────────────────────────────────────────
module PBItems
  ULTRABALL       = 265
  GREATBALL       = 266
  POKEBALL        = 267
  POKEBALLCASERA  = 822
  SUPERBALLCASERA = 823
  ULTRABALLCASERA = 824
  POTION          = 19
  POLVOEXPLOSIVO  = 756
  HACHAENDEBLE    = 757
  LLAVEMERCURICA  = 758
end
BALLS = [265, 266, 267, 822, 823, 824]
def hasConst?(mod, sym); return mod.const_defined?(sym.to_s); end
def getConst(mod, sym); return mod.const_get(sym.to_s); end
def pbIsPokeBall?(item); return BALLS.include?(item); end

class FakeBag
  def initialize(counts); @counts = counts; end
  def id(item); return item.is_a?(Integer) ? item : getConst(PBItems, item); end
  def pbQuantity(item); return @counts[id(item)] || 0; end
  def pbHasItem?(item); return pbQuantity(item) > 0; end
  def pbDeleteItem(item, qty = 1)
    n = id(item)
    @counts[n] = pbQuantity(n) - qty
    @counts.delete(n) if @counts[n] <= 0
    return true
  end
end

# ── 배틀 껍데기 — 원작 pbSpeed의 turncount 분기를 그대로 흉내낸다 ──────────
module PBStatuses
  PARALYSIS = 1; SLEEP = 2; POISON = 3; BURN = 4; FROZEN = 5
  CADUCO = 6; HEMORRAGIA = 7
end

class FakeMon
  attr_accessor :name, :status, :statusCount, :hp
  def initialize(name, status = 0); @name = name; @status = status; @statusCount = 0; @hp = 10; end
  def isEgg?; return false; end
end

class FakeBattle
  attr_accessor :battlers, :party, :msgs
  def initialize; @battlers = []; @party = []; @msgs = []; end
  def pbDisplay(t); @msgs.push(t); end
  def pbDisplayPaused(t); @msgs.push(t); end
  def pbParty(index); return @party; end
end

class PokeBattle_Battler
  attr_accessor :turncount, :index, :status, :pokemonIndex, :abilities, :battle
  def initialize(battle, index, abilities = [])
    @battle = battle; @index = index; @abilities = abilities
    @turncount = 0; @status = 0; @pokemonIndex = index
  end
  def hasWorkingAbility(sym); return @abilities.include?(sym); end
  def isFainted?; return false; end
  def pbIsOpposing?(i); return i >= 2; end
  def pbThis(lower = false); return "포켓몬#{@index}"; end
  def pbCureStatus(showmsg = true); @status = 0; end

  # 원작 pbSpeed의 요지 — turncount를 보는 네 자리만 남겼다. 배율을 돌려준다.
  def pbSpeed
    speedmult = 0x1000
    if hasWorkingAbility(:SLOWSTART) && self.turncount <= 5
      speedmult = (speedmult / 2).round
    end
    if hasWorkingAbility(:TINTINEO) && self.turncount == 0
      $fired[:tintineo] += 1
      @battle.pbDisplayPaused(_INTL("¡{1} tintinea como una campana!", pbThis))
    end
    if hasWorkingAbility(:ACOMETIDA) && self.turncount == 0
      $fired[:acometida] += 1
      @battle.pbDisplayPaused(_INTL("¡{1} entra a combatir con furia desmedida!", pbThis))
    end
    if hasWorkingAbility(:ACOMETIDA) && self.turncount == 1
      speedmult = (speedmult * 1.5).round
    end
    return speedmult
  end

  def pbInitEffects(batonpass); @turncount = 0; end
  def pbAbilitiesOnSwitchIn(onactive); $fired[:orig_switchin] += 1; end
end

class NewBattleBag
  attr_reader :ret
  attr_accessor :pocket, :item
  def initialize; @pocket = []; @item = 0; @lastUsed = 0; end
  def intoPocket   # 원작 그대로 — $lastUsed는 도구 빠른 칸이다
    @lastUsed = 0
    @lastUsed = @pocket[@item][0] if @pocket[@item][1] > 1
    $lastUsed = @lastUsed
    @ret = @pocket[@item][0]
  end
end

class FakeIcon
  attr_reader :file
  def setBitmap(f); @file = f; end
  def update; end
end

class CommandMenuDisplay
  attr_reader :iconBall
  def initialize; @iconBall = FakeIcon.new; end
  def update; end
end

# ── 리전 맵 껍데기 — 좌표 상수는 원작 그대로다(절 PScreen_RegionMap 71-76줄) ──
class PokemonRegionMapScene
  LEFT   = 0
  TOP    = 0
  RIGHT  = 29
  BOTTOM = 19
  SQUAREWIDTH  = 16
  SQUAREHEIGHT = 16
end

# ── 옵션 화면 껍데기 — 별칭이 걸릴 원작 메서드만 세운다 ────────────────────
class EnumOption
  attr_reader :name, :values
  def initialize(name, options, getProc, setProc)
    @name = name; @values = options; @getProc = getProc; @setProc = setProc
  end
  def get; return @getProc.call; end
  def set(value); @setProc.call(value); end
end

class FakeTextbox
  attr_accessor :text
end

class Window_PokemonOption
  attr_accessor :index
  def initialize(options); @options = options; @index = 0; end
  def mustUpdateOptions; return false; end
end

class PokemonOptionScene
  def pbAddOnOptions(options); return options; end   # 원작은 받은 것을 그대로 돌려준다
  def pbUpdate; end
end

# ── 포획 껍데기 ───────────────────────────────────────────────────────────
module PokeBattle_BattleCommon; end   # 모드가 이것을 다시 열어 pbStorePokemon을 넣는다

def Kernel.pbConfirmMessage(text)
  $confirmed.push(text)
  return $answer_party
end

module PBSpecies
  def self.getName(species); return "이브이"; end
end

class FakeCatch
  attr_accessor :name, :species
  def initialize(name); @name = name; @species = 1; end
  def isEgg?; return false; end
end

class FakeTrainer
  attr_accessor :party
  def initialize(n)
    @party = []
    n.times {|i| @party.push(FakeCatch.new("파티#{i}")) }
  end
end

class FakePeer
  attr_reader :stored
  def initialize; @stored = []; end
  def pbCurrentBox; return 0; end
  def pbStorePokemon(player, pkmn); @stored.push(pkmn); return 0; end
  def pbGetStorageCreator; return nil; end
  def pbBoxName(box); return "상자#{box + 1}"; end
end

# 전투 씬 껍데기 — 원작 pbDisplayConfirmMessage(절 PokeBattle_Scene 1484줄)를 그대로
# 세워 두고, 명령 창에 무엇이 어떤 차례로 넘어갔는지 적어 둔다.
class FakeBattleScene
  attr_reader :shown
  def initialize; @shown = []; @named = false; end
  def pbShowCommands(msg, commands, defaultValue)
    @shown.push([msg, commands, defaultValue])
    return $answer_command   # 커서가 어디 서든 고르는 값은 시험이 정한다
  end
  def pbDisplayConfirmMessage(msg)
    return pbShowCommands(msg, ["Si", "No"], 1) == 0
  end
  def pbNameEntry(title, pkmn); @named = true; return ""; end
  def named?; return @named; end
end

class Catcher
  include PokeBattle_BattleCommon
  attr_reader :peer, :asked, :msgs
  attr_reader :scene
  def initialize
    @peer = FakePeer.new; @scene = FakeBattleScene.new; @asked = []; @msgs = []
  end
  def pbPlayer; return $Trainer; end
  def pbDisplayConfirm(msg)   # 원작 그대로(절 PokeBattle_Battle 2725줄)
    @asked.push(msg)
    return @scene.pbDisplayConfirmMessage(msg)
  end
  def pbShowCommands(msg, commands, cancancel = true)   # 원작 그대로(같은 절 2729줄)
    return @scene.pbShowCommands(msg, commands, cancancel)
  end
  def pbDisplayPaused(text); @msgs.push(text); end
  def pbChoosePokemon(a, b, c = nil); end
end

# ── 저장·필드 별명·공통 이벤트 껍데기 ─────────────────────────────────────
class FakeStorage
  attr_accessor :isfull
  def initialize(full); @isfull = full; end
  def full?; return @isfull; end
end

def Kernel.pbMessage(text)
  $kernel_msgs.push(text)
  return true
end

# 원작 최상위 pbNickname(절 PSystem_Utilities NUEVO 1699줄)의 요지 — 물어서 이름을 바꾼다.
def pbNickname(pokemon)
  $confirmed.push(_INTL("¿Quieres ponerle un mote a {1}?", "이브이"))
  pokemon.name = "새이름" if $answer_party
end

# 원작 Interpreter#command_117(절 Interpreter 899줄)의 요지 — 자식 인터프리터를 세운다.
class Interpreter
  attr_accessor :parameters, :called
  def initialize; @called = []; end
  def command_117
    @called.push(@parameters[0])
    return true
  end
end

# 볼 단축키 갈래의 껍데기 — pickBall 안에서 불린다
def pbPlayer; return $Trainer; end
def pbDisplay(msg); $battle_msgs.push(msg); end

begin
  log("RUBY_VERSION = #{RUBY_VERSION.inspect}")
  ["010_TurnOrder.rb", "050_MapCursorSnap.rb",
   "070_BallShortcut.rb", "080_AutoBox.rb", "090_CraftPrompt.rb"].each do |f|
    eval(File.open("#{CHECK}/#{f}", "rb") {|fp| fp.read }, TOPLEVEL_BINDING, f)
  end

  # 볼 고르는 사슬은 pbAttackPhase 안에 있어 통째로는 못 돌린다 — 그 대목만
  # 소스에서 오려 메서드로 세운다(자구가 바뀌면 여기서 멈춘다).
  src = File.open("#{CHECK}/010_TurnOrder.rb", "rb") {|fp| fp.read }
  a = src.index("        if pbPlayer.party.length>=6")
  b = src.index("        end  \n          if pokeBall")
  raise "볼 사슬을 못 찾았다" if !a || !b || b <= a
  # 오린 대목에 `next`(만석이면 그 포켓몬의 행동을 넘긴다)가 들어 있으므로 한 바퀴짜리
  # for로 감싼다 — for는 스코프를 새로 만들지 않아 pokeBall이 밖에서도 보인다.
  eval("def pickBall\n  pokeBall=nil\n  for _qa in [0]\n" + src[a...b] +
       "        end\n  end\n  return pokeBall\nend", TOPLEVEL_BINDING, "chain")

  $fired = {:tintineo => 0, :acometida => 0, :orig_switchin => 0}

  # ⓐ 등장 턴에 pbSpeed를 여러 번 불러도 부수효과가 0번
  battle = FakeBattle.new
  bell = PokeBattle_Battler.new(battle, 0, [:TINTINEO, :ACOMETIDA])
  battle.battlers = [bell]
  battle.party = [FakeMon.new("이브이", PBStatuses::PARALYSIS)]
  8.times { bell.pbSpeed }
  chk("ⓐ pbSpeed 8회 — 종소리 발동", $fired[:tintineo], 0)
  chk("ⓐ pbSpeed 8회 — 분노 문구", $fired[:acometida], 0)
  chk("ⓐ pbSpeed 8회 — 문구 없음", battle.msgs.length, 0)
  chk("ⓐ turncount 원복", bell.turncount, 0)

  # ⓓ 위장이 배율을 안 바꾼다
  slow = PokeBattle_Battler.new(battle, 1, [:SLOWSTART])
  chk("ⓓ SLOWSTART turncount 0", slow.pbSpeed, 0x800)
  slow.turncount = 3
  chk("ⓓ SLOWSTART turncount 3", slow.pbSpeed, 0x800)
  slow.turncount = 6
  chk("ⓓ SLOWSTART turncount 6", slow.pbSpeed, 0x1000)
  rage = PokeBattle_Battler.new(battle, 1, [:ACOMETIDA])
  chk("ⓓ ACOMETIDA turncount 0(배율 없음)", rage.pbSpeed, 0x1000)
  rage.turncount = 1
  chk("ⓓ ACOMETIDA turncount 1(1.5배)", rage.pbSpeed, (0x1000 * 1.5).round)
  chk("ⓓ turncount 1은 위장 안 함 — 분노 문구", $fired[:acometida], 0)

  # ⓑ 등장 특성 자리에서 정확히 한 번
  battle2 = FakeBattle.new
  bell2 = PokeBattle_Battler.new(battle2, 0, [:TINTINEO, :ACOMETIDA])
  mate = PokeBattle_Battler.new(battle2, 1, [])
  mate.status = PBStatuses::SLEEP
  battle2.battlers = [bell2, mate]
  # 필드에 선 둘(파티 자리 0·1)은 아래 파티 루프에서 건너뛴다 — 뒤에 둘을 더 둔다.
  battle2.party = [FakeMon.new("나옹"), FakeMon.new("고라파덕"),
                   FakeMon.new("이브이", PBStatuses::PARALYSIS),
                   FakeMon.new("피카츄", PBStatuses::BURN)]
  bell2.pbAbilitiesOnSwitchIn(true)
  chk("ⓑ 원작 몸통도 불린다", $fired[:orig_switchin], 1)
  chk("ⓑ 종소리 문구 1회",
      battle2.msgs.grep(/tintinea como una campana/).length, 1)
  chk("ⓑ 분노 문구 1회",
      battle2.msgs.grep(/furia desmedida/).length, 1)
  chk("ⓑ 필드 아군이 깼다", battle2.msgs.grep(/se despertó/).length, 1)
  chk("ⓑ 필드 아군 상태이상 해제", mate.status, 0)
  chk("ⓑ 파티 아군 치료 문구 2건",
      battle2.msgs.grep(/se curó de la parálisis|se curó de la quemadura/).length, 2)
  chk("ⓑ 파티 상태 0", battle2.party.map {|m| m.status }, [0, 0, 0, 0])
  before = battle2.msgs.length
  bell2.pbAbilitiesOnSwitchIn(true)   # 메가진화 등으로 같은 등장에서 또 불려도
  chk("ⓑ 두 번째 호출은 조용", battle2.msgs.length, before)
  bell2.pbInitEffects(false)          # 교체로 다시 들어오면 다시 돈다
  bell2.pbAbilitiesOnSwitchIn(true)
  chk("ⓑ 재등장하면 다시 1회",
      battle2.msgs.grep(/tintinea como una campana/).length, 2)

  # ⓒ 쇠약·출혈 — 원본이 party[i].name으로 NameError를 내던 자리
  battle3 = FakeBattle.new
  bell3 = PokeBattle_Battler.new(battle3, 0, [:TINTINEO])
  sick = PokeBattle_Battler.new(battle3, 1, [])
  sick.status = PBStatuses::CADUCO
  bleed = PokeBattle_Battler.new(battle3, 2, [])   # index>=2 라 상대편
  battle3.battlers = [bell3, sick, bleed]
  battle3.party = [FakeMon.new("나옹"), FakeMon.new("고라파덕"),
                   FakeMon.new("이브이", PBStatuses::HEMORRAGIA)]
  err = nil
  begin
    bell3.pbAbilitiesOnSwitchIn(true)
  rescue Exception => e
    err = "#{e.class}: #{e.message}"
  end
  chk("ⓒ 예외 없음", err, nil)
  chk("ⓒ 필드 쇠약 문구가 포켓몬 이름으로",
      battle3.msgs.grep(/se curó del estado Caduco/), ["¡포켓몬1 se curó del estado Caduco!"])
  chk("ⓒ 파티 출혈 문구",
      battle3.msgs.grep(/se curó de la Hemorragia/), ["¡이브이 se curó de la Hemorragia!"])

  # ⓔ 볼 고르기 — 만석 가드를 지나야 사슬에 닿으므로 파티는 셋, 박스는 여유로 둔다
  $Trainer = FakeTrainer.new(3)
  $PokemonStorage = FakeStorage.new(false)
  $battle_msgs = []
  $kernel_msgs = []
  $lastUsedBall = nil
  $PokemonBag = FakeBag.new({265 => 3, 266 => 2, 267 => 5, 822 => 1})
  chk("ⓔ 기억이 없으면 옛 사슬(집볼 계열이 먼저)", pickBall, 822)
  chk("ⓔ 옛 사슬은 그 볼을 덜어낸다", $PokemonBag.pbQuantity(822), 0)
  $lastUsedBall = 267
  chk("ⓔ 기억한 볼이 나간다", pickBall, 267)
  chk("ⓔ 기억한 볼을 덜어낸다", $PokemonBag.pbQuantity(267), 4)
  $lastUsedBall = 823   # 갖고 있지 않은 볼
  chk("ⓔ 없는 볼이면 옛 사슬로", pickBall, 265)
  $PokemonBag = FakeBag.new({})
  $lastUsedBall = 267
  chk("ⓔ 볼이 하나도 없으면 nil", pickBall, nil)

  # ⓕ 기억하는 자리 — 볼만 적고 도구 빠른 칸은 안 물든다
  $lastUsed = 0
  $lastUsedBall = nil
  bag = NewBattleBag.new
  bag.pocket = [[267, 5], [PBItems::POTION, 3], [822, 1]]
  bag.item = 0
  bag.intoPocket
  chk("ⓕ 볼을 골랐다 — 기억", $lastUsedBall, 267)
  chk("ⓕ 볼을 골랐다 — 반환", bag.ret, 267)
  bag.item = 1
  bag.intoPocket
  chk("ⓕ 상처약을 골랐다 — 도구 빠른 칸", $lastUsed, PBItems::POTION)
  chk("ⓕ 상처약은 볼 기억을 안 건드린다", $lastUsedBall, 267)
  bag.item = 2
  bag.intoPocket
  chk("ⓕ 한 개뿐인 볼도 기억한다", $lastUsedBall, 822)
  chk("ⓕ 한 개뿐이면 도구 빠른 칸은 0(원작 그대로)", $lastUsed, 0)

  # 아이콘 — 값이 바뀔 때만 다시 그린다
  $PokemonBag = FakeBag.new({265 => 3, 267 => 5})
  $lastUsedBall = 267
  disp = CommandMenuDisplay.new
  disp.update
  chk("아이콘이 기억한 볼", disp.iconBall.file, "Graphics/Icons/item267.png")
  $lastUsedBall = nil
  disp.update
  chk("기억이 없으면 옛 아이콘 사슬", disp.iconBall.file, "Graphics/Icons/item265.png")
  $PokemonBag = FakeBag.new({})
  disp.update
  chk("볼이 없으면 빈 아이콘", disp.iconBall.file, "Graphics/Icons/item000.png")

  # ⓖ 스냅 — 맨해튼 거리라 대각은 후보에 안 든다.
  # (8,2) 둘레의 표지 칸은 [7,2](왼쪽, 거리 1)와 [7,3](왼쪽 아래, 대각)뿐이다.
  scene = PokemonRegionMapScene.new
  $game_switches = {}
  scene.instance_variable_set("@wallmap", false)
  def scene.setlocs(list)   # [x,y] 목록을 순정 항목 꼴로 앉힌다
    @map = [nil, nil, list.map {|xy| [xy[0], xy[1], "곳", "", nil, nil, nil, nil] }]
  end
  scene.setlocs([[7, 2], [7, 3]])
  chk("ⓖ 상하좌우가 있으면 그쪽", scene.pbSnapTarget(8, 2), [7, 2])
  scene.setlocs([[7, 3]])
  chk("ⓖ 대각뿐이면 안 끌린다", scene.pbSnapTarget(8, 2), nil)
  scene.setlocs([[18, 1], [19, 2]])
  chk("ⓖ 동점이면 표 순서의 첫 칸", scene.pbSnapTarget(18, 2), [18, 1])
  scene.setlocs([[7, 2]])
  chk("ⓖ 두 칸 떨어진 곳은 안 끌린다", scene.pbSnapTarget(9, 2), nil)
  chk("ⓖ 반경은 1 그대로", PokemonRegionMapScene::SNAP_RADIUS, 1)

  # ⓚ 옛 세이브 꼴 — 인스턴스 변수가 아예 없는 $PokemonSystem
  $PokemonSystem = PokemonSystem.new
  chk("ⓚ 값이 없으면 자동 보관(0)", $PokemonSystem.qol_autobox, 0)
  $PokemonSystem.qol_autobox = 1
  chk("ⓚ 넣은 값은 그대로", $PokemonSystem.qol_autobox, 1)
  $PokemonSystem.qol_autobox = 0
  chk("ⓚ 0도 그대로", $PokemonSystem.qol_autobox, 0)

  # ⓛ 옵션 항목 — 원작 훅에 하나가 얹히고, 이름·값 차례가 요구대로다
  optscene = PokemonOptionScene.new
  opts = optscene.pbAddOnOptions([])
  chk("ⓛ 항목 둘이 얹힌다", opts.length, 2)
  chk("ⓛ 첫 항목 이름", opts[0].name, "파티가 꽉 찼을 때")
  chk("ⓛ 첫 항목 값 차례", opts[0].values, ["자동 보관", "물어보기"])
  chk("ⓛ 첫 항목 기본값은 자동 보관", opts[0].get, 0)
  opts[0].set(1)
  chk("ⓛ 고른 값이 $PokemonSystem에 실린다", $PokemonSystem.qol_autobox, 1)
  opts[0].set(0)
  chk("ⓛ 둘째 항목 이름", opts[1].name, "별명 물음")
  chk("ⓛ 둘째 항목 값 차례", opts[1].values, ["켜기", "끄기"])
  chk("ⓛ 둘째 항목 기본값은 켜기", opts[1].get, 0)
  opts[1].set(1)
  chk("ⓛ 둘째 항목 값도 $PokemonSystem에", $PokemonSystem.qol_nickname, 1)
  opts[1].set(0)
  # 설명 — 우리 항목에 서 있을 때만 뜬다
  win = Window_PokemonOption.new(opts)
  box = FakeTextbox.new
  optscene.instance_variable_set("@sprites", {"option" => win, "textbox" => box})
  win.index = 0
  optscene.pbUpdate
  chk("ⓛ 항목에 서면 설명이 뜬다", box.text,
      "포켓몬을 잡았을 때 파티가 꽉 차 있으면 어떻게 할지 정한다.")
  win.index = 1
  optscene.pbUpdate
  chk("ⓛ 둘째 항목에 서면 그 설명이 뜬다", box.text,
      "포켓몬을 잡거나 알을 깼을 때 별명을 붙일지 물어본다.")
  box.text = "딴 설명"
  win.index = 2   # 「Salir」 줄 — 우리 항목이 아니다
  optscene.pbUpdate
  chk("ⓛ 딴 줄에서는 안 건드린다", box.text, "딴 설명")
  win.index = 0
  win.mustUpdateOptions   # 원작 pbOptions가 case 뒤에 읽는 자리
  chk("ⓛ case 뒤 자리에서도 뜬다", box.text,
      "포켓몬을 잡았을 때 파티가 꽉 차 있으면 어떻게 할지 정한다.")

  # ⓜ 별명 물음 — 옵션 「별명 물음」이 전투 포획과 필드 부화 양쪽에 걸린다
  caught = FakeCatch.new("이브이")
  $PokemonSystem.qol_autobox = 0
  $Trainer = FakeTrainer.new(3)
  $game_variables = {1 => -1}
  $confirmed = []
  $answer_command = 1   # 둘째 칸 = 「No」 (원작 차례는 [Si, No])

  chk("ⓜ 값이 없으면 켜기(0)", $PokemonSystem.qol_nickname, 0)

  # 켜기 — 원작 그대로 묻고, 명령 차례도 원작 그대로 「예 · 아니요」다
  catn = Catcher.new
  catn.pbStorePokemon(caught)
  chk("ⓜ 켜기 — 전투 포획에서 묻는다", catn.scene.shown.length, 1)
  chk("ⓜ 켜기 — 명령 차례는 원작 그대로", catn.scene.shown[0][1], ["Si", "No"])
  chk("ⓜ 켜기 — B키 기본값도 원작 그대로", catn.scene.shown[0][2], 1)
  chk("ⓜ 「아니요」를 고르면 이름짓기로 안 간다", catn.scene.named?, false)

  $answer_command = 0   # 첫 칸 = 「Si」
  $Trainer = FakeTrainer.new(3)
  catn2 = Catcher.new
  catn2.pbStorePokemon(caught)
  chk("ⓜ 켜기 — 「예」를 고르면 이름짓기로 간다", catn2.scene.named?, true)

  # 끄기 — 묻지도 않는다
  $PokemonSystem.qol_nickname = 1
  $Trainer = FakeTrainer.new(3)
  $answer_command = 0
  catn3 = Catcher.new
  catn3.pbStorePokemon(caught)
  chk("ⓜ 끄기 — 전투 포획에서 안 묻는다", catn3.scene.shown.length, 0)
  chk("ⓜ 끄기 — 이름짓기로 안 간다", catn3.scene.named?, false)
  chk("ⓜ 끄기 — 그래도 peer로 넘어간다", catn3.peer.stored, [caught])

  # 필드 경로(알 부화·선물)의 pbNickname도 같은 값에 걸린다
  $confirmed = []
  $answer_party = true
  egg = FakeCatch.new("이브이")
  pbNickname(egg)
  chk("ⓜ 끄기 — 필드 별명 물음도 안 묻는다", $confirmed.length, 0)
  chk("ⓜ 끄기 — 원래 이름 그대로", egg.name, "이브이")
  $PokemonSystem.qol_nickname = 0
  pbNickname(egg)
  chk("ⓜ 켜기 — 필드 별명 물음은 묻는다", $confirmed.length, 1)
  chk("ⓜ 켜기 — 이름이 바뀐다", egg.name, "새이름")

  # 다른 확인창은 원작 차례 그대로 — 전투 쪽 나머지 여덟 자리가 쓰는 길이다
  $answer_command = 0
  cato = Catcher.new
  chk("ⓜ 다른 확인창은 「예」가 먼저", cato.pbDisplayConfirm("¿Cambiar de Pokémon?"), true)
  chk("ⓜ 다른 확인창의 명령 차례", cato.scene.shown[0][1], ["Si", "No"])
  chk("ⓜ 다른 확인창의 B키 기본값", cato.scene.shown[0][2], 1)
  # 셋째 인자로 불리언을 넘기는 호출(원작 PokeBattle_Battle#pbShowCommands)도 그대로다
  catb = Catcher.new
  boolerr = nil
  begin
    catb.pbShowCommands("¿Qué hacer?", ["Luchar", "Huir"], true)
  rescue Exception => e
    boolerr = "#{e.class}: #{e.message}"
  end
  chk("ⓜ 불리언을 넘기는 호출은 안 깨진다", boolerr, nil)
  chk("ⓜ 불리언이 그대로 넘어간다", catb.scene.shown[0][2], true)

  # ⓗⓘⓙ 포획 — 파티 만석 × 옵션 값, 그리고 자리가 있을 때

  $PokemonSystem.qol_autobox = 0
  $Trainer = FakeTrainer.new(6)
  $game_variables = {1 => -1}
  $confirmed = []
  cat = Catcher.new
  cat.pbStorePokemon(caught)
  chk("ⓗ 자동 보관 — 파티에 넣을지 안 묻는다", $confirmed.length, 0)
  chk("ⓗ 자동 보관 — peer로 넘어갔다(박스 배정은 peer 몫)", cat.peer.stored, [caught])
  chk("ⓗ 자동 보관 — 파티는 그대로 여섯", $Trainer.party.length, 6)
  chk("ⓗ 별명은 그래도 묻는다", cat.scene.shown.length, 1)

  $PokemonSystem.qol_autobox = 1
  $Trainer = FakeTrainer.new(6)
  $confirmed = []
  $answer_party = false
  cat2 = Catcher.new
  cat2.pbStorePokemon(caught)
  chk("ⓘ 물어보기 — 파티에 넣을지 묻는다",
      $confirmed, ["¿Quieres añadir a 이브이 a tu equipo?"])
  chk("ⓘ 거절하면 peer로", cat2.peer.stored, [caught])
  chk("ⓘ 별명도 묻는다", cat2.scene.shown.length, 1)

  $Trainer = FakeTrainer.new(6)
  $confirmed = []
  $answer_party = true
  $game_variables = {1 => 0}
  cat3 = Catcher.new
  def cat3.pbGet(n); return n == 1 ? 0 : @swapped; end
  def cat3.pbSet(n, v); @swapped = v; end
  cat3.pbStorePokemon(caught)
  chk("ⓘ 받아들이면 파티에 들어간다", $Trainer.party[0], caught)
  chk("ⓘ 밀려난 쪽이 peer로", cat3.peer.stored.length, 1)
  chk("ⓘ 밀려난 쪽은 잡은 놈이 아니다", cat3.peer.stored[0] == caught, false)

  $confirmed = []
  [0, 1].each do |val|
    $PokemonSystem.qol_autobox = val
    $Trainer = FakeTrainer.new(3)
    cat4 = Catcher.new
    cat4.pbStorePokemon(caught)
    chk("ⓙ 자리가 있으면 안 묻는다(값 #{val})", $confirmed.length, 0)
    chk("ⓙ 자리가 있으면 그대로 peer로(원본과 같다, 값 #{val})", cat4.peer.stored, [caught])
  end

  # ⓝ 볼 단축키의 박스 만석 가드
  $battle_msgs = []
  $PokemonBag = FakeBag.new({267 => 5})
  $lastUsedBall = 267
  $Trainer = FakeTrainer.new(6)
  $PokemonStorage = FakeStorage.new(true)
  chk("ⓝ 만석이면 볼을 안 낸다", pickBall, nil)
  chk("ⓝ 만석이면 볼이 안 줄어든다", $PokemonBag.pbQuantity(267), 5)
  chk("ⓝ 만석 안내가 뜬다", $battle_msgs, ["¡No hay espacio en la PC!"])
  $battle_msgs = []
  $PokemonStorage = FakeStorage.new(false)
  chk("ⓝ 박스에 자리가 있으면 던진다", pickBall, 267)
  chk("ⓝ 그때는 안내가 없다", $battle_msgs.length, 0)
  $PokemonStorage = FakeStorage.new(true)
  $Trainer = FakeTrainer.new(5)
  $battle_msgs = []
  chk("ⓝ 파티에 자리가 있으면 박스가 차도 던진다", pickBall, 267)
  chk("ⓝ 그때도 안내가 없다", $battle_msgs.length, 0)

  # ⓞ 마지막 그물 — 원작 peer가 부르는 pbDisplayPaused가 살아 있다
  $kernel_msgs = []
  peer = PokeBattle_RealBattlePeer.new
  neterr = nil
  begin
    peer.pbDisplayPaused("No se puede seguir capturando...")
  rescue Exception => e
    neterr = "#{e.class}: #{e.message}"
  end
  chk("ⓞ 예외 없음", neterr, nil)
  chk("ⓞ 안내가 Kernel.pbMessage로 나간다", $kernel_msgs,
      ["No se puede seguir capturando..."])

  # ⓟ 제작 권유 — 이미 가진 도구면 공통 이벤트를 안 부른다
  $PokemonBag = FakeBag.new({756 => 1})
  intp = Interpreter.new
  [58, 59, 61, 60, 12].each do |n|
    intp.parameters = [n]
    intp.command_117
  end
  chk("ⓟ 가진 것(58)만 빠지고 나머지는 불린다", intp.called, [59, 61, 60, 12])
  $PokemonBag = FakeBag.new({756 => 1, 757 => 2, 758 => 1})
  intp2 = Interpreter.new
  [58, 59, 61, 60].each do |n|
    intp2.parameters = [n]
    intp2.command_117
  end
  chk("ⓟ 셋 다 가졌으면 셋 다 빠진다", intp2.called, [60])
  $PokemonBag = FakeBag.new({})
  intp3 = Interpreter.new
  [58, 59, 61].each do |n|
    intp3.parameters = [n]
    intp3.command_117
  end
  chk("ⓟ 하나도 없으면 셋 다 불린다", intp3.called, [58, 59, 61])

  log($bad == 0 ? "판정: 통과" : "판정: 실패 #{$bad}건")
rescue Exception => e
  log("터짐: #{e.class}: #{e.message}")
  log(e.backtrace.join("\n")) if e.backtrace
end
fp = File.open(OUT, "wb"); fp.write($out.join("\n") + "\n"); fp.flush; fp.close
Kernel.exit!
