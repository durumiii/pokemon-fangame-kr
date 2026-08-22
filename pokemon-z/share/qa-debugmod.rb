# 「디버그 모드」 자체 점검 — 구판 루비(1.8.7) 실물에서 모드 조각의 셈을 잰다.
#
# 무엇을 재나 — 모드가 원작에 손대지 않고 하는 것들의 셈이 그대로인가.
#   ① 초성 뽑기가 한글·로마자·숫자·그 밖을 제대로 가르는가 (목록 필터의 뼈대)
#   ② 메뉴를 갈아 끼워도 원작 열쇠 48개가 하나도 안 사라지는가
#   ③ 편의 토글이 꺼지면 원작 판정이 평소대로 돌아가고 $DEBUG가 원복되는가
#   ④ 초성 고르기를 취소해도 화면 뒤의 목록이 걸러진 채로 남는가 (커서 어긋남)
#   ⑤ 축소 지도 helper를 하나만 쥐고 타일셋이 갈릴 때 옛 것을 놓는가 (메모리 누수)
#
# 화면은 못 잰다 — 창이 뜨는 모양·눌러 보는 흐름은 사람 몫이다.
#
# 돌리는 법(시험대는 packaging 지침 「구판 루비에서 한 줄 재는 법」):
#   1. 이 파일과 모드의 .rb 를 D:/ztest/ 아래에 둔다 — 모드 쪽은 D:/ztest/check/ 로.
#   2. D:/ztest/rundir/mkxp.json 의 customScript 를 이 파일로 바꾼다.
#   3. rundir 에서 Game.exe 를 돌린다.
#   4. 결과는 D:/ztest/qa-debugmod_out.txt. **customScript 를 syntax.rb 로 되돌린다.**
CHECK = "D:/ztest/check"
OUT   = "D:/ztest/qa-debugmod_out.txt"

$out = []
$bad = 0
def log(s); $out << s.to_s; end
def chk(label, got, want)
  ok = (got == want)
  $bad += 1 if !ok
  log("#{ok ? 'OK ' : 'X  '} #{label} = #{got.inspect}#{ok ? '' : " (기대 #{want.inspect})"}")
end

# 게임 절이 안 실린 자리라 모드가 부르는 것들을 껍데기로 세운다.
$msgs = []
def Kernel.pbMessage(t); $msgs.push(t); end
# 고를 답을 $answers 에 미리 넣어 둔다. 비면 취소(-1).
$answers = []
def Kernel.pbShowCommands(a, b, c, d = 0)
  return $answers.length > 0 ? $answers.shift : -1
end
# 원작 판정 흉내 — 넷 다 $DEBUG 하나만 본다(실물이 그 꼴이다).
def Kernel.pbSurf; return $DEBUG ? "통과" : "막힘"; end
def Kernel.pbHeadbutt(event); return $DEBUG ? "통과:#{event}" : "막힘"; end
class PokemonRegionMap
  def initialize; @scene = self; end
  def pbStartScene(editor); $editor = editor; end
  def pbMapScene; end
  def pbEndScene; end
  def pbStartScreen; @scene.pbStartScene($DEBUG); @scene.pbMapScene; @scene.pbEndScene; end
end
class PokemonBagScreen
  def pbStartScreen; return $DEBUG ? "중요 도구도 버리기" : "평소대로"; end
end
def pbLearnMove(pokemon, move, ignoreifknown = false, bymachine = false, &block)
  return "알은 못 배운다" if pokemon == :egg && !$DEBUG
  r = "가르쳤다:#{move}"
  r = block.call(r) if block
  return r
end
def pbTrainerCheck(a, b, c, d = 0); return $DEBUG ? "추가할까 물음" : "조용"; end

# 맵 목록 껍데기 — 원작 MapLister 에서 목록 필터가 보는 것만 세운다.
module MessageTypes; MapNames = 1; end
$mapnames = {}
def pbGetMessage(type, id); return $mapnames[id]; end
class MapLister
  def initialize(maps); @maps = maps; @addGlobalOffset = 0; @index = 0; end
  def startIndex; return @index; end
  def value(index)
    return -1 if index < 0
    return @maps[index - @addGlobalOffset][0]
  end
end

# 축소 지도 helper 껍데기 — 몇 장 열리고 몇 장 놓이는지만 센다.
$opened = 0
$disposed = 0
class TileDrawingHelper
  def self.fromTileset(tileset); $opened += 1; return self.new(tileset); end
  def initialize(tileset); @tileset = tileset; end
  attr_reader :tileset
  def dispose; $disposed += 1; end
end

# 원작 pbDebugMenu가 세우는 열쇠 48개 — 순서까지 실물 그대로.
KEYS = ["switches", "variables", "refreshmap", "warp", "healparty", "additem",
  "fillbag", "clearbag", "addpokemon", "fillboxes", "clearboxes", "usepc",
  "setplayer", "renameplayer", "randomid", "changeoutfit", "setmoney", "setcoins",
  "setbadges", "demoparty", "toggleshoes", "togglepokegear", "togglepokedex",
  "dexlists", "readyrematches", "mysterygift", "daycare", "quickhatch",
  "roamerstatus", "roam", "setencounters", "setmetadata", "terraintags",
  "trainertypes", "resettrainers", "testwildbattle", "testdoublewildbattle",
  "testtrainerbattle", "testdoubletrainerbattle", "relicstone", "purifychamber",
  "extracttext", "compiletext", "compiledata", "mapconnections", "animeditor",
  "debugconsole", "togglelogging"]

begin
  log("RUBY_VERSION = #{RUBY_VERSION.inspect}")
  ["003_DebugLists.rb", "004_DebugPerks.rb", "005_DebugSideEffects.rb",
   "002_DebugMenuOrder.rb", "006_DebugMinimap.rb"].each do |f|
    load "#{CHECK}/#{f}"
  end

  # ① 초성
  [["칼로스 피레네", "ㅋ"], ["리펠꽃", "ㄹ"], ["따라큐", "ㄸ"], ["쁘사이저", "ㅃ"],
   ["힘의모래", "ㅎ"], ["Poke Ball", "P"], ["poke", "P"], ["3번도로", "3"],
   ["", "기타"], ["♂표시", "기타"]].each do |c|
    chk("초성 #{c[0].inspect}", DebugList.head(c[0]), c[1])
  end
  chk("초성 모으기(차례 유지·중복 없음)",
      DebugList.heads(["가부리아스", "괴력몬", "나옹", "리자몽", "리아코", "Poke Ball"]),
      ["ㄱ", "ㄴ", "ㄹ", "P"])

  # ③ 토글 — 기본값과 양방향
  $DEBUG = true
  chk("기본값 hm", DebugPerks.hm, true)
  chk("기본값 heal", DebugPerks.heal, true)
  chk("기본값 devmode", DebugPerks.devmode, false)
  chk("devmode 꺼짐: 리전 맵 편집기 인자", (PokemonRegionMap.new.pbStartScreen; $editor), false)
  chk("devmode 꺼짐: 가방", PokemonBagScreen.new.pbStartScreen, "평소대로")
  chk("devmode 꺼짐: 알에 기술", pbLearnMove(:egg, "파도타기"), "알은 못 배운다")
  chk("블록이 그대로 흐른다", pbLearnMove(:pikachu, "번개") {|r| r + "!" }, "가르쳤다:번개!")
  chk("devmode 꺼짐: 트레이너 확인창", pbTrainerCheck(1, "철수", 1), "조용")
  DebugPerks.hm = false
  chk("hm 꺼짐: pbSurf", Kernel.pbSurf, "막힘")
  chk("hm 꺼짐: 인자 전달", Kernel.pbHeadbutt(7), "막힘")
  chk("감싼 뒤 $DEBUG 원복", $DEBUG, true)
  DebugPerks.hm = true
  chk("hm 켜짐: pbSurf", Kernel.pbSurf, "통과")
  DebugPerks.devmode = true
  chk("devmode 켜짐: 리전 맵", (PokemonRegionMap.new.pbStartScreen; $editor), true)
  chk("devmode 켜짐: 가방", PokemonBagScreen.new.pbStartScreen, "중요 도구도 버리기")
  chk("devmode 켜짐: 알에 기술", pbLearnMove(:egg, "파도타기"), "가르쳤다:파도타기")
  chk("devmode 켜짐: 트레이너 확인창", pbTrainerCheck(1, "철수", 1), "추가할까 물음")
  DebugPerks.devmode = false

  # ② 메뉴 — 열쇠 보존과 자리
  c = CommandList.new
  KEYS.each {|k| c.add(k, "라벨:" + k) }
  shown = c.list
  i = shown.index("전투 후 자동 회복: 켬")
  chk("전투 후 회복이 소지금 설정 뒤", shown[i - 1], "라벨:setmoney")
  chk("그다음이 비전기술", shown[i + 1], "비전기술·라이드 자동 통과: 켬")
  chk("그 뒤가 맵 새로고침", shown[i + 2], "라벨:refreshmap")
  chk("개발자 모드는 첫 화면에 없다", shown.grep(/개발자 모드/).length, 0)
  chk("묶음 넷이 끝에 선다", shown[-4..-1],
      ["플레이어 설정...", "박스와 가방...", "필드와 데이터...", "개발 도구..."])
  chk("토글을 고르면 원작 분기로 안 넘어간다", c.getCommand(i), nil)
  chk("골랐더니 뒤집혔다", DebugPerks.heal, false)
  chk("라벨이 상태를 따라간다", c.list.include?("전투 후 자동 회복: 끔"), true)
  chk("원작 항목은 열쇠를 그대로 준다", c.getCommand(c.list.index("라벨:warp")), "warp")

  grouped = []
  CommandList::GROUPS.each {|g| g[1].each {|k| grouped.push(k) if KEYS.include?(k) } }
  top = []
  n = 0
  while n < c.list.length && !c.list[n].index("...")
    top.push(c.getCommand(n)); n += 1
  end
  chk("닿지 않는 원작 열쇠", KEYS.reject {|k| (top + grouped).compact.include?(k) }, [])

  # 모르는 열쇠(다른 모드가 더한 것)를 잃지 않는가
  c2 = CommandList.new
  KEYS.each {|k| c2.add(k, "라벨:" + k) }
  c2.add("newthing", "새 항목")
  j = c2.list.index("새 항목")
  chk("모르는 열쇠를 되찾는다", j.nil? ? nil : c2.getCommand(j), "newthing")

  # ④ 필터 취소 뒤 화면과 속이 어긋나지 않는가
  $mapnames = {1 => "관동", 2 => "나비마을", 3 => "낙엽시티", 4 => "단풍시티"}
  ml = MapLister.new([[1, "Kanto", 0], [2, "Napo", 0], [3, "Nak", 0], [4, "Dan", 0]])
  chk("거르기 전에는 네 줄", ml.commands.length, 4)
  chk("초성 모으기는 초성 필터를 뺀 전체를 본다",
      DebugList.heads(ml.dbgz_pool), ["ㄱ", "ㄴ", "ㄷ"])
  ml.instance_variable_set("@dbgz_head", "ㄴ")
  chk("ㄴ으로 두 줄", ml.commands.length, 2)
  ml.instance_variable_set("@index", 1)
  $answers = [0, -1]   # 「초성으로 필터」를 골랐다가 초성 고르기에서 취소
  chk("취소면 목록을 다시 안 그린다(false)", ml.dbgz_menu, false)
  chk("취소 뒤에도 커서 자리가 그대로", ml.startIndex, 1)
  chk("취소 뒤 커서가 가리키는 맵", ml.value(1), 3)     # 낙엽시티. 어긋나면 2가 나온다
  chk("취소 뒤에도 목록은 걸러진 두 줄", ml.commands.length, 2)
  $answers = [0, 2]    # 이번엔 ㄷ — 모은 초성은 ["ㄱ", "ㄴ", "ㄷ"]이니 셋째
  chk("초성을 고르면 다시 그리라고 한다(true)", ml.dbgz_menu, true)
  chk("고른 초성으로 다시 좁힌다", ml.commands.length, 1)
  chk("좁힌 목록의 첫 줄", ml.value(0), 4)

  # ⑤ 축소 지도 helper — 하나만 쥐고 갈릴 때 옛 것을 놓는다
  h1 = DebugMinimap.helper(3, "타일셋3")
  chk("첫 요청에 한 장 연다", $opened, 1)
  h2 = DebugMinimap.helper(3, "타일셋3")
  chk("같은 타일셋이면 다시 안 연다", $opened, 1)
  chk("같은 helper를 돌려준다", h2.equal?(h1), true)
  chk("아직 아무것도 안 놓았다", $disposed, 0)
  h3 = DebugMinimap.helper(7, "타일셋7")
  chk("타일셋이 갈리면 새로 연다", $opened, 2)
  chk("갈릴 때 옛 것을 놓는다", $disposed, 1)
  chk("새 helper가 새 타일셋을 쥔다", h3.tileset, "타일셋7")
  DebugMinimap.release
  chk("목록을 닫으면 마지막 하나도 놓는다", $disposed, 2)
  DebugMinimap.release
  chk("두 번 놓아도 셈이 안 어긋난다", $disposed, 2)
  chk("놓은 뒤 요청하면 새로 연다", (DebugMinimap.helper(7, "타일셋7"); $opened), 3)
  DebugMinimap.release

  log($bad == 0 ? "판정: 통과" : "판정: 실패 #{$bad}건")
rescue Exception => e
  log("터짐: #{e.class}: #{e.message}")
  log(e.backtrace.join("\n")) if e.backtrace
end
fp = File.open(OUT, "wb"); fp.write($out.join("\n") + "\n"); fp.flush; fp.close
Kernel.exit!
