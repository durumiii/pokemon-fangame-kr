# 「Controller UX」 자체 점검 — 구판 루비(1.8.7) 실물에서 입력창 가드의 셈을 잰다.
#
# 무엇을 재나 — 가방 검색창(`handle_input`)과 이름 입력(`pbEntry1`)이 가상 B·C를
# **패드에서 왔을 때만** 듣는가. 한글 조합 중에는 입력창 글자가 그 프레임에 안 늘어
# 옛 가드(「글자가 변했으면 무시」)가 헛돌았고, 두벌식 ㅌ(X 글쇠)·ㅊ(C 글쇠)이
# 취소·확정으로 읽혔다(제보 2026-08-21).
#   ⓐ 한글 조합 중(글자 안 늚) X 글쇠 → 검색창이 안 닫힌다
#   ⓑ 한글 조합 중 C 글쇠 → 검색창이 안 닫힌다
#   ⓒ 패드 취소(키보드 무입력 + 가상 B) → 닫히고 검색어가 원래대로 되돌아간다
#   ⓓ 패드 확정(키보드 무입력 + 가상 C) → 닫히고 검색어가 남는다
#   ⓔ 영문 x 타이핑(글자가 실제로 늚) → 안 닫히고 그 글자가 들어간다
#   ⓕ 넘패드0(가상 B에 묶인 또 하나의 글쇠) → 안 닫힌다
#   ⓖ Esc·Enter 직독 경로는 그대로다
#   ⓗ 아무것도 안 눌리면 안 닫힌다
#   ⓘ~ⓝ 이름 입력(`pbEntry1`)에 같은 여섯 갈래 + minlength 지킴
#
# 화면은 못 잰다 — 실제로 한글이 찍히는 모양은 사람 몫이다.
#
# 돌리는 법(시험대는 packaging 지침 「구판 루비에서 한 줄 재는 법」):
#   1. 이 파일을 D:/ztest/ 에, 모드의 004·006 .rb 를 D:/ztest/check/ 에 둔다.
#   2. D:/ztest/rundir/mkxp.json 의 customScript 를 이 파일로 바꾼다.
#   3. rundir 에서 Game.exe 를 돌린다.
#   4. 결과는 D:/ztest/qa-controllerux_out.txt. **customScript 를 syntax.rb 로 되돌린다.**
#
# 신형 루비(3.1) 시험대(`/mnt/d/Game/_probe/z-mkxpz/`)에서도 그대로 돈다 — 아래 CHECK·OUT
# 를 그 폴더로 바꾸고 그쪽 mkxp.json 의 customScript 를 이 파일로 두면 된다.
CHECK = "D:/ztest/check"
OUT   = "D:/ztest/qa-controllerux_out.txt"

$out = []
$bad = 0
def log(s); $out << s.to_s; end
def chk(label, got, want)
  ok = (got == want)
  $bad += 1 if !ok
  log("#{ok ? 'OK ' : 'X  '} #{label} = #{got.inspect}#{ok ? '' : " (기대 #{want.inspect})"}")
end

# ── 엔진 껍데기 ────────────────────────────────────────────────────────────
# 원작 `DP Scripting Utilities`가 두는 상수. handle_input이 이 이름으로 읽는다.
ESCAPE = 0x1B
RETURN = 13

module Graphics
  def self.update; end
end

# 가상 버튼(키보드+패드 합본)과 키보드 전용 조회를 따로 흉내낸다.
# $vbtn = 이 프레임에 트리거된 가상 버튼, $keys = 이 프레임에 눌린 키보드 글쇠.
module Input
  A = 11
  B = 12
  C = 13
  def self.update; end
  def self.text_input=(v); end
  def self.trigger?(b);   return ($vbtn || []).include?(b); end
  def self.pressex?(k);   return ($keys || []).include?(k); end
  def self.triggerex?(k); return ($keys || []).include?(k); end
end

def press(keys, vbtn)
  $keys = keys
  $vbtn = vbtn
end

# 입력창 껍데기 — `update`가 예약한 글자를 그때 집어넣는다(원작의 Input.gets 자리).
class FakeEntry
  attr_accessor :text
  def initialize(text)
    @text = text
    @pending = nil
  end
  def types(ch); @pending = ch; end
  def update
    if @pending
      @text = @text + @pending
      @pending = nil
    end
  end
end

class PokemonEntryScene
  attr_accessor :sprites, :minlength
  def initialize(entry, minlength)
    @sprites = {"entry" => entry, "helpwindow" => FakeEntry.new("")}
    @minlength = minlength
  end
end

# ── 모드 싣기 ──────────────────────────────────────────────────────────────
# read+eval이 아니라 load로 싣는다 — 읽어서 eval하면 신형 루비에서 리터럴이
# ASCII-8BIT가 되어 실물(UTF-8)과 달라진다(packaging 「구판 루비에서 한 줄 재는 법」).
["004_TextEntryPad.rb", "006_TextSearchPad.rb"].each do |f|
  load("#{CHECK}/#{f}")
end

# ── 가방 검색창 ────────────────────────────────────────────────────────────
# 한 프레임을 돌린다. [닫혔나, 창에 남은 글자]를 돌려준다.
def frame(keys, vbtn, typed)
  w = FakeEntry.new("포켓")
  w.types(typed) if typed
  press(keys, vbtn)
  closed = handle_input(w, nil, "포켓")
  return [closed ? true : false, w.text]
end

log("RUBY_VERSION = #{RUBY_VERSION.inspect}")
log("-- 가방 검색창(handle_input)")
chk("ⓐ 한글 조합 중 X 글쇠(ㅌ)",        frame([:X], [Input::B], nil),         [false, "포켓"])
chk("ⓑ 한글 조합 중 C 글쇠(ㅊ)",        frame([:C], [Input::C], nil),         [false, "포켓"])
chk("ⓒ 패드 취소",                      frame([], [Input::B], nil),           [true,  "포켓"])
chk("ⓓ 패드 확정",                      frame([], [Input::C], nil),           [true,  "포켓"])
chk("ⓔ 영문 x 타이핑",                  frame([:X], [Input::B], "x"),         [false, "포켓x"])
chk("ⓕ 넘패드0",                        frame([:KP_0], [Input::B], nil),      [false, "포켓"])
chk("ⓕ' 스페이스",                      frame([:SPACE], [Input::C], " "),     [false, "포켓 "])
chk("ⓖ Esc 직독",                       frame([ESCAPE], [], nil),             [true,  "포켓"])
chk("ⓖ' Enter 직독",                    frame([RETURN], [], nil),             [true,  "포켓"])
chk("ⓗ 무입력",                         frame([], [], nil),                   [false, "포켓"])

# ── 이름 입력 ──────────────────────────────────────────────────────────────
# pbEntry1은 무한 루프라 한 프레임씩 먹인다. 프레임 목록이 다 떨어지면 예외로 끊는다.
class OutOfFrames < StandardError; end
module Input
  def self.update
    if $script
      step = $script.shift
      if step.nil?
        # pbEntry1은 루프를 빠져나온 뒤 Input.update를 한 번 더 부른다. 그 한 번은
        # 빈 프레임으로 넘겨 주고, 그다음에도 부르면 루프가 안 끝난 것이니 끊는다.
        raise OutOfFrames.new("프레임 소진") if $spent
        $spent = true
        $keys = []
        $vbtn = []
        return
      end
      $keys, $vbtn, typed = step
      $entry.types(typed) if typed
    end
  end
end

def entry_run(minlength, frames)
  $entry = FakeEntry.new("이름")
  $script = frames
  $spent = false
  scene = PokemonEntryScene.new($entry, minlength)
  begin
    ret = scene.pbEntry1
  rescue OutOfFrames
    $script = nil
    return [:open, $entry.text]
  end
  $script = nil
  return [ret, $entry.text]
end

log("-- 이름 입력(pbEntry1)")
chk("ⓘ 한글 조합 중 X 글쇠(ㅌ)", entry_run(0, [[[:X], [Input::B], nil]]),   [:open, "이름"])
chk("ⓙ 한글 조합 중 C 글쇠(ㅊ)", entry_run(0, [[[:C], [Input::C], nil]]),   [:open, "이름"])
chk("ⓚ 패드 취소",               entry_run(0, [[[], [Input::B], nil]]),     ["",    "이름"])
chk("ⓛ 패드 확정",               entry_run(0, [[[], [Input::C], nil]]),     ["이름", "이름"])
chk("ⓜ 영문 x 타이핑",           entry_run(0, [[[:X], [Input::B], "x"]]),   [:open, "이름x"])
chk("ⓝ Esc·Enter 직독",          entry_run(0, [[[:ESCAPE], [], nil]]),      ["",    "이름"])
chk("ⓝ' Enter 직독",             entry_run(0, [[[:RETURN], [], nil]]),      ["이름", "이름"])
chk("ⓞ minlength가 패드 확정도 막는다", entry_run(9, [[[], [Input::C], nil]]), [:open, "이름"])
chk("ⓟ minlength가 패드 취소도 막는다", entry_run(9, [[[], [Input::B], nil]]), [:open, "이름"])

log("")
log($bad == 0 ? "전부 통과" : "실패 #{$bad}건")
f = File.open(OUT, "wb"); f.write($out.join("\n") + "\n"); f.flush; f.close
Kernel.exit!
