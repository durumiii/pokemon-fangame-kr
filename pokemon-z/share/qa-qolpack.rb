# 「QOL Pack」 자체 점검 — 구판 루비(1.8.7) 실물에서 모드 조각의 셈을 잰다.
#
# 무엇을 재나 — Z-42(pbSpeed 수술)와 Z-50 ①(볼 단축키)이 하는 일이 그대로인가.
#   ⓐ 등장 턴에 pbSpeed를 여러 번 불러도 치료·문구가 0번 돈다
#   ⓑ pbAbilitiesOnSwitchIn 한 번에 치료·문구가 정확히 1번 돈다
#   ⓒ 쇠약·출혈 걸린 아군이 있어도 예외가 안 난다(원본은 여기서 NameError)
#   ⓓ 위장이 SLOWSTART·ACOMETIDA 배율을 안 바꾼다
#   ⓔ 마지막에 쓴 볼이 있고 갖고 있으면 그것이, 없으면 옛 사슬이 골라진다
#   ⓕ $lastUsed(도구 빠른 칸)가 볼 사용에 안 물든다
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

begin
  log("RUBY_VERSION = #{RUBY_VERSION.inspect}")
  ["010_TurnOrder.rb", "070_BallShortcut.rb"].each do |f|
    eval(File.open("#{CHECK}/#{f}", "rb") {|fp| fp.read }, TOPLEVEL_BINDING, f)
  end

  # 볼 고르는 사슬은 pbAttackPhase 안에 있어 통째로는 못 돌린다 — 그 대목만
  # 소스에서 오려 메서드로 세운다(자구가 바뀌면 여기서 멈춘다).
  src = File.open("#{CHECK}/010_TurnOrder.rb", "rb") {|fp| fp.read }
  a = src.index("        pokeBall=nil")
  b = src.index("        end  \n          if pokeBall")
  raise "볼 사슬을 못 찾았다" if !a || !b || b <= a
  eval("def pickBall\n" + src[a...b] + "        end\n  return pokeBall\nend",
       TOPLEVEL_BINDING, "chain")

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

  # ⓔ 볼 고르기
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

  log($bad == 0 ? "판정: 통과" : "판정: 실패 #{$bad}건")
rescue Exception => e
  log("터짐: #{e.class}: #{e.message}")
  log(e.backtrace.join("\n")) if e.backtrace
end
fp = File.open(OUT, "wb"); fp.write($out.join("\n") + "\n"); fp.flush; fp.close
Kernel.exit!
