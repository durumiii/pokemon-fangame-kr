# 맹독 칸 판정 자체 점검(Z-64) — 구판 루비(1.8.7) 실물에서 셈을 잰다.
#
# 무엇을 재나 — 소스 수술이 넣은 판정 줄 셋이 상태별로 어느 칸을 고르는가.
#   전투 HUD(절 「Tipos Pokemon」) · 파티 화면(절 「PScreen_Party」) ·
#   요약 화면(절 「PScreen_Summary」).
# 줄은 **설치본 Scripts.rxdata에서 그대로 뽑아** 돌린다 — 여기 옮겨 적지 않는다.
#
# 화면은 못 잰다 — 칸이 예쁘게 나오는지는 미리보기 PNG와 사람 몫이다.
#
# 돌리는 법(시험대는 packaging 지침 「구판 루비에서 한 줄 재는 법」):
#   1. 이 파일을 D:/ztest/ 아래에 둔다.
#   2. D:/ztest/rundir/mkxp.json 의 customScript 를 이 파일로 바꾼다.
#   3. rundir 에서 Game.exe 를 돌린다.
#   4. 결과는 D:/ztest/qa-toxiccell_out.txt. **customScript 를 syntax.rb 로 되돌린다.**
SCRIPTS = "D:/Game/Pokemon Z/V2.18/Data/Scripts.rxdata"
OUT     = "D:/ztest/qa-toxiccell_out.txt"

$out = []
$bad = 0
def log(s); $out << s.to_s; end
def chk(label, got, want)
  ok = (got == want)
  $bad += 1 if !ok
  log("#{ok ? 'OK ' : 'X  '} #{label} = #{got.inspect}#{ok ? '' : " (기대 #{want.inspect})"}")
end

module PBStatuses
  SLEEP=1; POISON=2; BURN=3; PARALYSIS=4; FROZEN=5; CADUCO=6; HEMORRAGIA=7
end

class Poke
  attr_accessor :status, :statusCount, :hp
  def initialize(st, cnt, hp); @status=st; @statusCount=cnt; @hp=hp; end
end

# 판정 줄을 실물 절에서 뽑는다.
begin
src = {}
Marshal.load(File.open(SCRIPTS, "rb")).each do |sec|
  src[sec[1].to_s] = Zlib::Inflate.inflate(sec[2])
end
def pick(text, pat)
  line = text.split(/\r?\n/).find { |l| l =~ pat }
  raise "판정 줄을 못 찾음: #{pat.inspect}" if !line
  return line.strip
end
HUD   = pick(src["Tipos Pokemon"], /^\s*krSt=/)
PARTY = pick(src["PScreen_Party"], /^\s*status=\(@pokemon\.hp==0\)/)
SUMLINES = src["PScreen_Summary"].split(/\r?\n/).map { |l| l.strip }
i = SUMLINES.index { |l| l =~ /^status=8 if pbPokerus/ }
raise "요약 화면 판정 덩어리를 못 찾음" if !i
SUM = SUMLINES[i, 4].join("\n")

class Ctx
  def pbPokerus(pkmn); return @pokerus; end
  def hud(b)
    @battler = b
    return eval(HUD + "\nkrSt")
  end
  def party(p)
    @pokemon = p
    return eval(PARTY + "\nstatus")
  end
  def summary(p, pokerus)
    @pokemon = p
    @pokerus = pokerus
    pokemon = p
    return eval("status=nil\n" + SUM + "\nstatus")
  end
end

log("뽑은 줄 — HUD: #{HUD}")
log("뽑은 줄 — 파티: #{PARTY}")
log("뽑은 줄 — 요약:\n#{SUM}")
log("")

c = Ctx.new
NONE = Poke.new(0, 0, 20)
SLP  = Poke.new(PBStatuses::SLEEP, 3, 20)      # 잠듦은 statusCount가 남는 유일한 딴 상태
PSN  = Poke.new(PBStatuses::POISON, 0, 20)
TOX  = Poke.new(PBStatuses::POISON, 1, 20)
BRN  = Poke.new(PBStatuses::BURN, 0, 20)
HEM  = Poke.new(PBStatuses::HEMORRAGIA, 0, 20)
FNT  = Poke.new(PBStatuses::POISON, 1, 0)      # 기절 + 맹독 — 기절이 이겨야 한다

# 전투 HUD (battleStatuses: 0~6 일곱 상태, 7 = 새 맹독 칸)
chk("HUD 독",     c.hud(PSN), 1)
chk("HUD 맹독",   c.hud(TOX), 7)
chk("HUD 잠듦",   c.hud(SLP), 0)
chk("HUD 화상",   c.hud(BRN), 2)
chk("HUD 출혈",   c.hud(HEM), 6)

# 파티 화면 (statuses: 0~6 상태, 7 = 기절, 8 = 포켓러스, 9 = 새 맹독 칸)
chk("파티 독",     c.party(PSN), 1)
chk("파티 맹독",   c.party(TOX), 9)
chk("파티 잠듦",   c.party(SLP), 0)
chk("파티 출혈",   c.party(HEM), 6)
chk("파티 기절",   c.party(FNT), 7)

# 요약 화면 — 덮어쓰기 차례가 포켓러스 8 → 상태 → 맹독 9 → 기절 7이라야 한다
chk("요약 독",         c.summary(PSN, 0), 1)
chk("요약 맹독",       c.summary(TOX, 0), 9)
chk("요약 잠듦",       c.summary(SLP, 0), 0)
chk("요약 기절+맹독",  c.summary(FNT, 0), 7)
chk("요약 포켓러스",   c.summary(NONE, 1), 8)
chk("요약 포켓러스+맹독", c.summary(TOX, 1), 9)
chk("요약 무상태",     c.summary(NONE, 0), nil)

log("")
rescue Exception
  log("EXC #{$!.class}: #{$!.message}")
  log($!.backtrace ? $!.backtrace[0,6].join("\n") : "(no backtrace)")
  $bad += 1
end
log($bad == 0 ? "전부 통과 (#{$out.length - 5}표본)" : "실패 #{$bad}건")
File.open(OUT, "wb") { |f| f.write($out.join("\n") + "\n") }
Kernel.exit!
