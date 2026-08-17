# 조회 기준 맵 판정 — 맵271(몬스터볼 공장) 이벤트4가 맵280으로 전이한 뒤 말하는 자리.
# 게임 실물 코드를 Scripts.rxdata에서 절째로 잘라 와 eval하고, 실제 korean.dat을 싣는다.
#
# 무엇을 재나 — 맵 대사 조회가 이벤트 소속 맵(@map_id)으로 가는지(Z-73 잔여, 2026-08-18).
# arm 셋을 한 판에 돌린다: A 지금 소스 · B 수술 전(pre-intl.bak) · C 지금 소스에서
# @map_id만 $game_map.map_id로 되돌린 것. **A만 한국어가 나와야 판정이 선다** —
# 대조군이 스페인어를 내는 것까지 봐야 시험이 무언가를 재고 있다는 뜻이다.
#
# 돌리는 법은 qa-maplookup-runner.rb 머리에.
DATA_DIR = "D:/Game/Pokemon Z/V2.18/Data/"
LIVE = DATA_DIR + "Scripts.rxdata"
BAK  = DATA_DIR + "Scripts.rxdata.pre-intl.bak"
TARGET = "Todav"   # "Todavía no hemos tenido la oportunidad..."

begin
  require 'zlib'
rescue Exception => e
  log "require zlib: #{e.class}: #{e.message}"
end

def sections(path)
  raw = File.open(path, "rb") { |f| f.read }
  arr = Marshal.load(raw)
  arr.map { |s| [s[1], Zlib::Inflate.inflate(s[2])] }
end

# ---------------- 스텁 (여기부터는 게임 실물 아님) ----------------
$shown = []       # Kernel.pbMessage 로 나간 문자열
$shownCmds = []   # 선택지
# 053 절을 eval하면 진짜 pbMessage(창을 띄우는 쪽)가 덮어쓰므로 매번 다시 건다.
def stub_kernel!
  module_eval_src = nil
  class << Kernel
    def pbRgssOpen(f, mode = "rb")
      fp = File.open(f, mode)
      begin; return yield(fp); ensure; fp.close; end
    end
    def pbMessage(msg, cmds = nil, cmdIfCancel = 0)
      $shown << msg; $shownCmds << cmds; return 0
    end
    def pbShowCommands(win, cmds, cancel = 0)
      $shownCmds << cmds; return 0
    end
    def pbMessageChooseNumber(msg, params); $shown << msg; return 0; end
  end
end
stub_kernel!
class GameMapStub
  attr_accessor :map_id, :need_refresh
end
$game_map = GameMapStub.new
$game_map.map_id = 280   # 전이가 끝나 플레이어는 도착 맵에 서 있다
$game_variables = Hash.new(0)
$MapFactory = nil
# ---------------- 스텁 끝 ----------------

LIVE_SECS = sections(LIVE)
BAK_SECS  = sections(BAK)
log "루비 #{RUBY_VERSION}, 절 수 live=#{LIVE_SECS.length} bak=#{BAK_SECS.length}"
log "39/42/53 이름(live) = #{LIVE_SECS[39][0].inspect}, #{LIVE_SECS[42][0].inspect}, #{LIVE_SECS[53][0].inspect}"

SRC_INTERP = LIVE_SECS[39][1]
SRC_INTL   = LIVE_SECS[42][1]
# 053 절은 필요한 앞부분만 자른다 — 뒤쪽 FaceWindowVX 부터는 RGSS 창 클래스(SpriteWindow_Base)에
# 기대는 죽은 짐이라 스크립트 전체를 안 태우는 이 시험대에서는 못 연다.
def head53(src); src[0, src.index("class FaceWindowVX")]; end
SRC_MSG_A  = head53(LIVE_SECS[53][1])                           # A: 지금 얹힌 판
SRC_MSG_B  = head53(BAK_SECS[53][1])                            # B: 수술 전(pre-intl.bak)
SRC_MSG_C  = SRC_MSG_A.gsub("_MAPINTL(@map_id,", "_MAPINTL($game_map.map_id,").
                       gsub("MessageTypes.getFromMapHash(@map_id,", "MessageTypes.getFromMapHash($game_map ? $game_map.map_id : 0,")
log "C 되돌림 성립? #{(SRC_MSG_C != SRC_MSG_A) && !SRC_MSG_C.include?("_MAPINTL(@map_id,")}"
log "A 안 @map_id 조회 줄 수 = #{SRC_MSG_A.scan(/_MAPINTL\(@map_id,/).length}, B = #{SRC_MSG_B.scan(/_MAPINTL\(@map_id,/).length}"
log "A 안 krLoc 줄 수 = #{SRC_MSG_A.scan(/krLoc/).length}, B = #{SRC_MSG_B.scan(/krLoc/).length}"

eval(SRC_INTERP, TOPLEVEL_BINDING, "039_Interpreter")
eval(SRC_INTL,   TOPLEVEL_BINDING, "042_Intl_Messages")
eval(SRC_MSG_A,  TOPLEVEL_BINDING, "053_Messages"); stub_kernel!
log "eval 039/042/053 통과"

$game_temp = Game_Temp.new

r = MessageTypes.loadMessageFile(DATA_DIR + "korean.dat")
log "korean.dat 적재: #{r.class} (nil이면 실패), 최상위 길이=#{r ? r.length : -1}"

# --- 맵 이벤트 명령 목록: 게임 데이터 실물 ---
map = load_data("Data/Map271.rxdata")
ev = map.events[4]
log "이벤트4 이름=#{ev.name.inspect} 페이지수=#{ev.pages.length}"
list = ev.pages[0].list
log "page0 명령 수=#{list.length}"

# 전이(201)와 목표 대사(101)의 자리
xfer = nil
list.each_index { |i| xfer = i if !xfer && list[i].code == 201 }
log "첫 전이 201 자리=#{xfer} 파라미터=#{list[xfer].parameters.inspect}"
idx = nil
list.each_index { |i|
  next if idx
  idx = i if list[i].code == 101 && list[i].parameters.length == 1 &&
             list[i].parameters[0].index(TARGET) == 0
}
xs = []
list.each_index { |i| xs << [i, list[i].parameters[1]] if list[i].code == 201 }
log "201 전이 전부(자리,도착맵)=#{xs.inspect}"
log "목표 101 자리=#{idx.inspect} 원문=#{idx ? list[idx].parameters[0] : nil}"
log "그다음 명령 코드들=#{(1..4).map { |k| list[idx + k].code }.inspect}"

def run_arm(name, list, idx)
  $shown = []; $shownCmds = []
  it = Interpreter.new
  it.setup(list, 4, 271)
  it.instance_variable_set(:@index, idx)
  ok = it.command_101
  log "[#{name}] command_101 반환=#{ok.inspect} 나간 문자열 수=#{$shown.length}"
  $shown.each { |s| log "[#{name}] pbMessage <- #{s.inspect}" }
  log "[#{name}] 비ASCII 상위바이트(한글 신호) 포함? #{$shown.join.unpack("C*").select{|b| b>=0xe0}.length > 0}"
end

log "--- @map_id(현재 얹힌 판) ---"
run_arm("A-현재", list, idx)

log "--- $game_map.map_id 로 되돌린 사본 (krLoc은 남김) ---"
eval(SRC_MSG_C, TOPLEVEL_BINDING, "053_Messages_C"); stub_kernel!
run_arm("C-되돌림", list, idx)

log "--- 수술 전 원본 (pre-intl.bak, krLoc 없음) ---"
eval(SRC_MSG_B, TOPLEVEL_BINDING, "053_Messages_B"); stub_kernel!
run_arm("B-수술전", list, idx)

# 대조: 정본에 실제로 뭐가 들어 있나 (직접 조회)
log "--- 직접 조회 ---"
eval(SRC_MSG_A, TOPLEVEL_BINDING, "053_Messages_A2"); stub_kernel!
msg = list[idx].parameters[0].clone
msg += " " if msg[msg.length - 1, 1] != " "
n = idx + 1
while n < list.length && list[n].code == 401
  t = list[n].parameters[0].clone
  t += " " if t[t.length - 1, 1] != " "
  msg += t
  n += 1
end
log "조립 원문=#{msg.inspect}"
log "getFromMapHash(271, 원문) = #{MessageTypes.getFromMapHash(271, msg).inspect}"
log "getFromMapHash(280, 원문) = #{MessageTypes.getFromMapHash(280, msg).inspect}"
log "krLoc(271,4,#{idx}) = #{MessageTypes.krLoc(271, 4, idx, msg).inspect}"

# --- 둘째 줄, 그리고 회귀 대조(전이 전 대사는 여전히 한국어인가) ---
def find_101(list, prefix)
  hit = nil
  list.each_index { |i|
    next if hit
    hit = i if list[i].code == 101 && list[i].parameters.length == 1 &&
               list[i].parameters[0].index(prefix) == 0
  }
  hit
end

i2 = find_101(list, "\302\277Vas a negarte")
log "둘째 줄 자리=#{i2.inspect}"
if i2
  $game_map.map_id = 280
  run_arm("A-현재-둘째줄", list, i2)
end

i0 = find_101(list, "La <b>Vasija Castigo</b> empieza")
log "전이 전 대사 자리=#{i0.inspect} (첫 280 전이는 490)"
if i0
  $game_map.map_id = 271   # 아직 제자리 — 두 기준이 같은 값
  run_arm("A-현재-전이전(회귀대조)", list, i0)
end
$game_map.map_id = 280
