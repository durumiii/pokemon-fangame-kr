# 전투 호출 대사에 좌표가 닿는가 — 맵25(아크릴리코마을) 이벤트38의 pbTrainerBattle 자리.
#
# 무엇을 재나 (Z-73 잔여, 2026-08-18). 전투 호출 대사는 조건 분기(111)의 스크립트 인자
# 안에 _I("...") 꼴로 박혀 있고, 그 스크립트는 Interpreter#pbExecuteScript의 eval이
# 돌린다. 소스를 읽으면 그때 self가 인터프리터라 @map_id·@event_id·@index가 _I 안에서
# 보여야 하는데, **루비 1.8의 eval 바인딩은 내 언어 감각으로 단정할 자리가 아니다.**
# 그래서 실물로 잰다.
#
# arm 다섯:
#   P 최상위 def가 eval 안에서 인터프리터의 인스턴스 변수를 보는가 (설계의 전제)
#   Q 그때 @index가 정본 자리 목록의 c값(7)과 같은가
#   R 지금 판에서 _I가 실제로 한국어를 내는가 (경로가 살아 있다는 대조)
#   S 수술본에서 좌표 값이 실제로 이긴다 — 이미 깔린 좌표 항목으로 잰다
#   T 좌표가 없는 자리는 옛 값 그대로다 (회귀)
#   U 인터프리터 밖에서 불러도 안 깨진다 (폴백)
# P·Q가 서야 수술이 성립하고, S·T·U가 서야 수술이 옳다.
#
# ⚠ S가 쓰는 맵155 이벤트4 c1은 101 대사 자리다 — 전투 호출 자리가 아니다. 좌표 항목이
# 이미 깔려 있어 조회 승패를 가릴 수 있는 자리라서 고른 것이고, 재는 것은 _I의 조회
# 우선순위이지 그 자리의 동작이 아니다.
#
# 돌리는 법은 qa-trainerloc-runner.rb 머리에.
DATA_DIR = "D:/Game/Pokemon Z/V2.18/Data/"
LIVE = DATA_DIR + "Scripts.rxdata"
MAPNO = 25
EVNO = 38
CMDIDX = 7        # 정본 자리 m25.e38.p0.c7 — 111 명령이 선 자리
SPEECH = "\302\241Mamma mia! \302\241Buen entrenamiento!"   # ¡Mamma mia! ¡Buen entrenamiento!

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
$shown = []
def stub_kernel!
  class << Kernel
    def pbRgssOpen(f, mode = "rb")
      fp = File.open(f, mode)
      begin; return yield(fp); ensure; fp.close; end
    end
    def pbMessage(msg, cmds = nil, cmdIfCancel = 0); $shown << msg; return 0; end
    def pbShowCommands(win, cmds, cancel = 0); return 0; end
  end
end
stub_kernel!
class GameMapStub
  attr_accessor :map_id, :need_refresh
  def events; {}; end
end
$game_map = GameMapStub.new
$game_map.map_id = 25
$game_variables = Hash.new(0)
$game_switches = Hash.new(false)
$MapFactory = nil

# 전제 탐침 — 최상위 def다. _I와 같은 자격으로 놓인다.
$probe = nil
def kr_probe
  $probe = [
    (defined?(@map_id)   ? @map_id   : :undef),
    (defined?(@event_id) ? @event_id : :undef),
    (defined?(@index)    ? @index    : :undef),
    self.class.to_s
  ]
  return true
end

# _I가 무엇을 돌려주는지 그 자리에서 잡는다.
$ires = nil
def kr_probe_i(str)
  $ires = _I(str)
  return true
end
# ---------------- 스텁 끝 ----------------

SECS = sections(LIVE)
log "루비 #{RUBY_VERSION}, 절 수=#{SECS.length}"
log "39/42/53 이름 = #{SECS[39][0].inspect}, #{SECS[42][0].inspect}, #{SECS[53][0].inspect}"

def head53(src); src[0, src.index("class FaceWindowVX")]; end
eval(SECS[39][1], TOPLEVEL_BINDING, "039_Interpreter")
eval(SECS[42][1], TOPLEVEL_BINDING, "042_Intl_Messages")
eval(head53(SECS[53][1]), TOPLEVEL_BINDING, "053_Messages"); stub_kernel!
log "eval 039/042/053 통과"

$game_temp = Game_Temp.new
r = MessageTypes.loadMessageFile(DATA_DIR + "korean.dat")
log "korean.dat 적재: #{r.class} (nil이면 실패)"

map = load_data("Data/Map#{MAPNO.to_s.rjust(3, '0')}.rxdata")
ev = map.events[EVNO]
list = ev.pages[0].list
log "이벤트#{EVNO} 이름=#{ev.name.inspect} 페이지0 명령 수=#{list.length}"
log "c#{CMDIDX} 코드=#{list[CMDIDX].code} 스크립트=#{list[CMDIDX].parameters[1].inspect}"

def run111(name, list, idx, script)
  it = Interpreter.new
  it.setup(list, EVNO, MAPNO)
  it.instance_variable_set(:@index, idx)
  it.instance_variable_set(:@parameters, [12, script])
  begin
    it.command_111
  rescue Exception => e
    log "[#{name}] 예외 #{e.class}: #{e.message}"
  end
end

log "--- P·Q: eval 안에서 인스턴스 변수가 보이나 ---"
run111("P", list, CMDIDX, "kr_probe")
log "[P] @map_id·@event_id·@index·self.class = #{$probe.inspect}"
log "[P] 기대 = [#{MAPNO}, #{EVNO}, #{CMDIDX}, \"Interpreter\"]"
log "[P] 통과? #{$probe == [MAPNO, EVNO, CMDIDX, "Interpreter"]}"

log "--- R: 지금 판의 _I가 한국어를 내나 ---"
run111("R", list, CMDIDX, "kr_probe_i(#{SPEECH.inspect})")
log "[R] _I 반환 = #{$ires.inspect}"
log "[R] 한글 신호(상위바이트) 있나? #{$ires ? $ires.unpack("C*").select { |b| b >= 0xe0 }.length > 0 : false}"

log "--- 대조: 정본에 좌표 열쇠가 이미 있나 ---"
key = "krloc:#{MAPNO}:#{EVNO}:#{CMDIDX}|" + Messages.stringToKey(SPEECH)
log "열쇠 = #{key.inspect}"
log "getFromMapHash = #{MessageTypes.getFromMapHash(MAPNO, key).inspect} (열쇠 그대로면 미등재)"

# ---------------- 수술본 ----------------
# 설치본을 건드리지 않고 절 42의 _I 정의만 메모리에서 갈아 끼운다.
OLD_I = "def _I(str)\r\n  return _MAPINTL($game_map.map_id,str)\r\nend\r\n"
NEW_I = "def _I(str)\r\n" +
        "  if @map_id && @event_id\r\n" +
        "    krHit=MessageTypes.krLoc(@map_id,@event_id,@index,str)\r\n" +
        "    return krHit ? krHit : _MAPINTL(@map_id,str)\r\n" +
        "  end\r\n" +
        "  return _MAPINTL($game_map.map_id,str)\r\n" +
        "end\r\n"
SRC42 = SECS[42][1]
log "--- 수술본 ---"
log "옛 _I 자구 있나? #{SRC42.include?(OLD_I)}"
SRC42_P = SRC42.gsub(OLD_I, NEW_I)
log "갈렸나? #{SRC42_P != SRC42}"
eval(SRC42_P, TOPLEVEL_BINDING, "042_Intl_Messages_P"); stub_kernel!
# ⚠ 절42를 다시 eval하면 MessageTypes가 새로 서면서 @@messages가 빈다 — 다시 싣는다.
r2 = MessageTypes.loadMessageFile(DATA_DIR + "korean.dat")
log "korean.dat 재적재: #{r2.class} (nil이면 실패)"

# S — 이미 깔린 좌표 항목: 맵155(훈련의 집) 이벤트4 c1. 치유사 쪽만 해요체로 갈라 뒀다.
S_MAP = 155; S_EV = 4; S_IDX = 1
S_SRC = "\302\277Quieres iniciar un super-entrenamiento de Puntos de Esfuerzo?"
map155 = load_data("Data/Map155.rxdata")
list155 = map155.events[S_EV].pages[0].list
log "맵#{S_MAP} 이벤트#{S_EV} c#{S_IDX} 코드=#{list155[S_IDX].code}"
$ires = nil
it = Interpreter.new
it.setup(list155, S_EV, S_MAP)
it.instance_variable_set(:@index, S_IDX)
it.instance_variable_set(:@parameters, [12, "kr_probe_i(#{S_SRC.inspect})"])
it.command_111
log "[S] 수술본 _I 반환 = #{$ires.inspect}"
log "[S] 맵 조회(좌표 무시) = #{MessageTypes.getFromMapHash(S_MAP, S_SRC).inspect}"
log "[S] 좌표 조회 = #{MessageTypes.krLoc(S_MAP, S_EV, S_IDX, S_SRC).inspect}"
log "[S] 좌표가 이겼나? #{$ires == MessageTypes.krLoc(S_MAP, S_EV, S_IDX, S_SRC)}"

# T — 좌표가 없는 자리(맵25 전투 호출)는 옛 값 그대로여야 한다.
$ires = nil
run111("T", list, CMDIDX, "kr_probe_i(#{SPEECH.inspect})")
log "[T] 수술본 _I 반환 = #{$ires.inspect}"
log "[T] 옛 값 그대로인가? #{$ires == MessageTypes.getFromMapHash(MAPNO, SPEECH)}"

# U — 인터프리터 밖(최상위)에서 부르면 폴백으로 떨어져야 한다.
$game_map.map_id = MAPNO
begin
  u = _I(SPEECH)
  log "[U] 최상위 _I 반환 = #{u.inspect}"
  log "[U] 안 깨졌나? #{u == MessageTypes.getFromMapHash(MAPNO, SPEECH)}"
rescue Exception => e
  log "[U] 예외 #{e.class}: #{e.message}"
end
