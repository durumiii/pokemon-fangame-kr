# 상점 점원 문구의 갈래 조회가 서는가 — 맵26(아크릴리코 구호소) 이벤트4(검은깃털).
#
# 무엇을 재나 (Z-73, 2026-08-18). 점원 문구는 절23 전역 조회라 자리 개념이 없다. 갈래는
# `krmart-at:<맵>:<이벤트>`로 배정하고 값은 `krmart:<갈래>|<원문>`으로 잡는데, **그 맵과
# 이벤트를 어디서 집느냐**가 이 수술의 유일한 미지수다. 설계는 `pbMapInterpreter`가
# 상점을 연 그 이벤트를 들고 있다고 보는데, 루비 1.8의 실행 문맥은 감각으로 단정할
# 자리가 아니라 게임 실행기로 잰다.
#
# arm 넷:
#   A `pbMapInterpreter`가 상점을 연 이벤트의 맵·이벤트 번호를 들고 있나
#   B 수술본의 `_MART`가 배정된 갈래의 문안을 내나 (맵26 이벤트4 → 반말)
#   C 배정이 없는 상점은 기본 갈래(존대) 그대로인가 (회귀)
#   D 인터프리터가 없을 때(메뉴 등) 안 깨지고 기본값으로 떨어지나
#
# 돌리는 법은 qa-mart-runner.rb 머리에.
DATA_DIR = "D:/Game/Pokemon Z/V2.18/Data/"
LIVE = DATA_DIR + "Scripts.rxdata"
MAPNO = 26
EVNO = 4
GREET = "\302\277Te interesa algo de lo que tengo?"   # ¿Te interesa algo de lo que tengo?

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

# ---------------- 스텁 ----------------
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
  attr_accessor :map_id, :need_refresh, :interpreter
  def events; {}; end
end
$game_map = GameMapStub.new
$game_map.map_id = MAPNO
$game_variables = Hash.new(0)
$game_switches = Hash.new(false)
$MapFactory = nil

$mart = nil
def kr_probe_mart(str)
  $mart = _MART(str)
  return true
end
$seen = nil
def kr_probe_who
  it = pbMapInterpreter
  $seen = it ? [it.instance_variable_get("@map_id"),
                it.instance_variable_get("@event_id"),
                it.class.to_s] : nil
  return true
end
# ---------------- 스텁 끝 ----------------

SECS = sections(LIVE)
log "루비 #{RUBY_VERSION}, 절 수=#{SECS.length}"
def head53(src); src[0, src.index("class FaceWindowVX")]; end
eval(SECS[39][1], TOPLEVEL_BINDING, "039_Interpreter")

# 절42 수술본 — krMart를 얹는다(설치본은 안 건드린다).
OLD_HASH = "  def self.getFromHash(type,key)\r\n    @@messages.getFromHash(type,key)\r\n" +
           "  end\r\n\r\n  def self.getFromMapHash(type,key)\r\n"
NEW_HASH = "  def self.getFromHash(type,key)\r\n    @@messages.getFromHash(type,key)\r\n" +
           "  end\r\n\r\n" +
           "  def self.krMart(str)\r\n" +
           "    it=pbMapInterpreter\r\n" +
           "    return nil if !it\r\n" +
           "    mp=it.instance_variable_get(\"@map_id\")\r\n" +
           "    ev=it.instance_variable_get(\"@event_id\")\r\n" +
           "    return nil if !mp || !ev\r\n" +
           "    at=\"krmart-at:\#{mp}:\#{ev}\"\r\n" +
           "    br=@@messages.getFromHash(MessageTypes::ScriptTexts,at)\r\n" +
           "    return nil if br==at\r\n" +
           "    key=\"krmart:\#{br}|\"+Messages.stringToKey(str)\r\n" +
           "    hit=@@messages.getFromHash(MessageTypes::ScriptTexts,key)\r\n" +
           "    return hit==key ? nil : hit\r\n" +
           "  end\r\n\r\n" +
           "  def self.getFromMapHash(type,key)\r\n"
OLD_MART = "  return string\r\nend\r\n\r\ndef _I(str)\r\n"
NEW_MART = "  return string\r\nend\r\n\r\n" +
           "def _MART(*arg)\r\n" +
           "  hit=MessageTypes.krMart(arg[0])\r\n" +
           "  return _INTL(*arg) if !hit\r\n" +
           "  s=hit.clone\r\n" +
           "  for i in 1...arg.length\r\n" +
           "    s.gsub!(/\\{\#{i}\\}/,\"\#{arg[i]}\")\r\n" +
           "  end\r\n" +
           "  return s\r\nend\r\n\r\ndef _I(str)\r\n"

src42 = SECS[42][1]
log "앵커 있나 — getFromHash #{src42.include?(OLD_HASH)} · _MART #{src42.include?(OLD_MART)}"
src42 = src42.gsub(OLD_HASH, NEW_HASH).gsub(OLD_MART, NEW_MART)
eval(src42, TOPLEVEL_BINDING, "042_Intl_Messages_P")
eval(head53(SECS[53][1]), TOPLEVEL_BINDING, "053_Messages"); stub_kernel!
log "eval 통과"

$game_temp = Game_Temp.new
r = MessageTypes.loadMessageFile(DATA_DIR + "korean.dat")
log "korean.dat 적재: #{r.class} (nil이면 실패)"

# ⚠ 깔린 korean.dat에는 아직 갈래 열쇠가 없다 — 빌드는 병합 뒤이므로 여기서 **주입**한다.
# 재는 것은 조회 경로이지 빌드가 아니다. 값은 23-script-texts.add.jsonl과 같은 두 줄.
MessageTypes.getFromHash(MessageTypes::ScriptTexts, "x")   # delayedLoad를 태운다
msgs = MessageTypes.class_eval("@@messages")
hash = msgs.instance_variable_get("@messages")
if hash && hash[MessageTypes::ScriptTexts]
  hash[MessageTypes::ScriptTexts][Messages.stringToKey("krmart-at:#{MAPNO}:#{EVNO}")] = "반말"
  hash[MessageTypes::ScriptTexts][Messages.stringToKey("krmart:반말|" + GREET)] =
    "\353\247\210\354\235\214\354\227\220 \353\223\234\353\212\224 " +
    "\353\254\274\352\261\264\354\235\264\353\235\274\353\217\204 \354\236\210\354\226\264?"
  log "주입 완료 — 배정 1줄 · 값 1줄"
else
  log "!! 주입 실패 — 해시 구조가 다르다: #{hash.class}"
end

# 상점을 연 이벤트를 실제로 세운다 — 맵 데이터 실물.
map = load_data("Data/Map0#{MAPNO}.rxdata")
ev = map.events[EVNO]
list = ev.pages[0].list
log "맵#{MAPNO} 이벤트#{EVNO} 이름=#{ev.name.inspect} 명령 수=#{list.length}"

it = Interpreter.new
it.setup(list, EVNO, MAPNO)
it.instance_variable_set(:@index, 0)
$game_map.interpreter = it     # pbMapInterpreter가 이걸 돌려준다

log "--- A: pbMapInterpreter가 무엇을 들고 있나 ---"
it.instance_variable_set(:@parameters, [12, "kr_probe_who"])
it.command_111
log "[A] #{$seen.inspect}  기대 [#{MAPNO}, #{EVNO}, \"Interpreter\"]"
log "[A] 통과? #{$seen == [MAPNO, EVNO, "Interpreter"]}"

log "--- B: 배정된 갈래의 문안이 나오나 ---"
it.instance_variable_set(:@parameters, [12, "kr_probe_mart(#{GREET.inspect})"])
it.command_111
log "[B] _MART 반환 = #{$mart.inspect}"
log "[B] 기본값(절23) = #{MessageTypes.getFromHash(MessageTypes::ScriptTexts, GREET).inspect}"
log "[B] 배정 = #{MessageTypes.getFromHash(MessageTypes::ScriptTexts, "krmart-at:#{MAPNO}:#{EVNO}").inspect}"
log "[B] 갈렸나? #{$mart != MessageTypes.getFromHash(MessageTypes::ScriptTexts, GREET)}"

log "--- C: 배정 없는 상점은 기본 갈래 그대로인가 ---"
it2 = Interpreter.new
it2.setup(list, 99, MAPNO)      # 배정표에 없는 이벤트 번호
it2.instance_variable_set(:@index, 0)
it2.instance_variable_set(:@parameters, [12, "kr_probe_mart(#{GREET.inspect})"])
$game_map.interpreter = it2
$mart = nil
it2.command_111
log "[C] _MART 반환 = #{$mart.inspect}"
log "[C] 기본값 그대로인가? #{$mart == MessageTypes.getFromHash(MessageTypes::ScriptTexts, GREET)}"

log "--- D: 인터프리터가 없을 때 ---"
$game_map.interpreter = nil
begin
  d = _MART(GREET)
  log "[D] _MART 반환 = #{d.inspect}"
  log "[D] 기본값 그대로인가? #{d == MessageTypes.getFromHash(MessageTypes::ScriptTexts, GREET)}"
rescue Exception => e
  log "[D] 예외 #{e.class}: #{e.message}"
end
