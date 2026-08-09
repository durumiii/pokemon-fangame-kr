# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Scripts.rxdata 신형 루비 호환 수술 (Z-32) — 심 섹션 + 문법 불통 2곳.

① `share/ruby-compat.rb`를 「Z-32 Ruby Compat」 섹션으로 코어 맨 앞에 넣는다.
   이미 있으면 내용만 갈아 끼운다(심을 고치고 다시 돌리면 된다).
② 신형 루비가 파싱조차 못 하는 1.8 전용 구문 두 곳을 소스 수술한다:
   - AudioUtilities의 `when N:` 콜론 23곳 → `when N then`
   - PScreen_Load의 rescue 밖 `retry` → `next` (loop do 블록 안이라 1.8에서도
     관측 동작이 같다 — 블록 retry는 loop 재시작, next는 다음 회차)
   둘 다 1.8.7에서도 그대로 유효한 문법이다.

멱등: 심은 갈아 끼우고, 수술은 이미 적용돼 있으면 건너뛴다.
검증: 수술 뒤 `qa-ruby-compat.py <대상> --ruby <신형 루비>`로 문법 불통 0을 확인.

usage: uv run patch_ruby_compat.py [대상 Scripts.rxdata ...]
  무인자면 보관소 기반판 + 게임 설치본 둘 다.
"""
import os
import re
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from datread import load  # noqa: E402
from fanlib import rubywrite  # noqa: E402

SECTION_ID = 20260809                      # RMXP 섹션 id는 임의 정수 — 눈에 띄는 값으로
SECTION_NAME = b"Z-32 Ruby Compat"
SHIM = HERE / "ruby-compat.rb"

DEFAULT_TARGETS = [
    Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/Scripts.rxdata"),
    Path("/mnt/d/Game/Pokemon Z/V2.18/Data/Scripts.rxdata"),
]

# (섹션명, 정규식, 치환) — 정규식이 안 걸리면 이미 수술된 것으로 본다.
REGEX_EDITS = [
    ("AudioUtilities", re.compile(r"when (\d+):"), r"when \1 then"),
    ("PScreen_Load", re.compile(r"\bretry if deleting==false"), "next if deleting==false"),
    # 정규식 리터럴 안의 `\x7f`~`\x9f`는 루비 3.x가 파싱에서 거부한다("invalid multibyte
    # escape") — 그 바이트 하나로는 올바른 UTF-8 글자가 못 되기 때문이다. POSIX 문자
    # 클래스로 바꾼다: 1.8·3.x 양쪽이 알아듣고, 제어문자를 거른다는 뜻도 그대로다.
    ("PSystem_Utilities NUEVO", re.compile(r"\\x00-\\x1f\\x7f-\\x9f"), "[:cntrl:]"),
    # 바이트를 `문자열[i]`로 읽는 1.8 관용구 — 1.9+에서는 String이 나와, 비교는 즉사하고
    # 산술은 NoMethodError다. `unpack`은 양쪽에서 같은 정수를 준다.
    ("AudioUtilities", re.compile(r"file\.read\(1\)\[0\] rescue 0"),
     'file.read(1).unpack("C")[0] rescue 0'),
    ("AudioUtilities", re.compile(r"\brstr\[0\]==0xFB"), 'rstr.unpack("C3")[0]==0xFB'),
    ("AudioUtilities", re.compile(r"\brstr\[1\]"), 'rstr.unpack("C3")[1]'),
    # `LargePlane < Plane`이 initialize에서 super를 안 불러 네이티브 Plane이 안 선다.
    # 구판 mkxp-z는 넘어갔지만 신판은 dispose의 super에서 MKXPError로 죽는다
    # (「No instance data for variable」). 초기화에서 부모를 세워 준다 — 구판에서도
    # 평범한 Plane 생성이라 동작이 같다.
    ("SpriteWindow",
     re.compile(r"(def initialize\(viewport=nil\)\r?\n)(\s+)(@__sprite=Sprite\.new\(viewport\))"),
     r"\1\2super(viewport)\n\2\3"),
    # 빈 이름의 오토타일을 열면 경로가 폴더가 된다. 1.8은 그냥 넘어갔지만 3.x는
    # `Errno::EISDIR`을 던지는데 이 rescue 목록에 그것이 없다 — 목록에 더한다.
    ("SpriteWindow",
     re.compile(r"rescue Errno::ENOENT, Errno::EINVAL, Errno::EACCES(?!, Errno::EISDIR)"),
     "rescue Errno::ENOENT, Errno::EINVAL, Errno::EACCES, Errno::EISDIR"),
    # 그림자 스프라이트의 `@map.id==$game_map.id`. 1.8에서 `id`는 Object#id(옛 object_id)라
    # 이 비교는 사실 「같은 Game_Map 객체인가」였다 — Game_Map에는 `id`가 없다. 3.x에는
    # 그 메서드가 사라져 즉사하므로 같은 뜻인 `equal?`로 적는다(양쪽 동작 동일).
    ("Sombras",
     re.compile(r"!\((?:!@map\.nil\? && )?@map\.id==\$game_map\.id\)"),
     "!(!@map.nil? && @map.equal?($game_map))"),
    # KleinBitmap 보조 코드가 String에 `getbyte`·`setbyte`·`bytesize`를 무조건 별칭으로
    # 건다. 1.8에서는 그게 없는 API를 채우는 것이었지만 3.x에서는 **있는 것을 덮어써서**
    # 바이트 대신 글자를 돌려준다 — 이 게임의 다른 코드가 getbyte로 바이트를 재다 죽는
    # 뿌리다(2026-08-09 시험대 실측: 글꼴 굵게 판정이 「String과 192 비교」로 즉사).
    # 없을 때만 걸도록 감싼다 — 1.8에서는 지금과 똑같이 걸린다.
    ("Map - Klein",
     re.compile(r"class String\r?\n  alias getbyte  \[\]\r?\n  alias setbyte  \[\]=\r?\n"
                r"  alias bytesize size\r?\nend"),
     'class String\n'
     '  if !"".respond_to?(:getbyte)\n'
     '    alias getbyte  []\n'
     '    alias setbyte  []=\n'
     '  end\n'
     '  if !"".respond_to?(:bytesize)\n'
     '    alias bytesize size\n'
     '  end\n'
     'end'),
    # StringInput#getc이 `@string[@pos]`로 한 바이트를 뜬다 — 1.8은 정수, 3.x는 String.
    # 이 스트림을 읽는 코드(dex 데이터의 `fgetb` 등)는 전부 정수를 전제로 짜여 있어,
    # 3.x에서는 성장 속도 같은 값이 String으로 흘러 비교에서 즉사한다(시험대 실측:
    # 스타팅 포켓몬 지급). 정수로 되돌린다 — 1.8에서는 이 줄이 아무 일도 안 한다.
    ("SpriteWindow",
     re.compile(r"(    ch = @string\[@pos\]\r?\n)(?!    ch = ch\.unpack)"),
     '\\1    ch = ch.unpack("C")[0] if ch.is_a?(String)\\n'),
    # 이름 입력창의 글자·숫자 키가 윈도 가상키 번호(65~90·48~57)로만 물어본다. 신판
    # mkxp-z는 그 번호를 다르게 읽어(SDL 스캔코드) 글자가 하나도 안 들어온다 —
    # 시험대 실측. 같은 화면이 이미 `:BACKSPACE` 꼴 기호를 쓰므로 기호도 함께 묻는다
    # (지원 안 하는 엔진에서는 그냥 거짓이라 옛 판 동작이 그대로다).
    ("TextEntry",
     re.compile(r"if Input\.repeatex\?\(i\)(?! \|\|)"),
     "if Input.repeatex?(i) || Input.repeatex?(i.chr.to_sym)"),
    # 이름·별명 입력창은 `Input.gets`로 글자를 받는데, 신판 mkxp-z는 문자 입력 모드가
    # 기본으로 꺼져 있어 아무것도 안 들어온다(시험대 실측: `Input.text_input`이 false).
    # 창을 열 때 켜고 닫을 때 끈다. 그 API가 없는 옛 실행기에서는 한 줄도 안 걸린다.
    ("TextEntry",
     re.compile(r"    @initial = true(\r?\n)  end\1(?!\1?  def dispose)"),
     "    @initial = true\\1"
     "    Input.text_input = true if Input.respond_to?(:text_input=)\\1"
     "  end\\1"
     "\\1"
     "  def dispose\\1"
     "    Input.text_input = false if Input.respond_to?(:text_input=)\\1"
     "    super\\1"
     "  end\\1"),
]


def _proc_return_to_next(src: str) -> tuple[str, int]:
    """최상위 `proc { ... }` 안의 `return`을 `next`로 바꾼다.

    1.8의 `proc`은 `lambda`와 같은 물건이라 블록 안 `return`이 그 블록에서 돌아왔다.
    1.9+에서는 `proc`이 비-lambda라 같은 자리가 LocalJumpError(unexpected return)다 —
    이벤트 핸들러가 대부분 `Events.onXxx+=proc{...}` 꼴이라 배틀 종료 같은 자리에서
    통째로 터진다. `next`는 1.8·3.x 양쪽에서 「이 블록에서 값을 들고 나간다」로 같다.
    (중첩 `def`가 든 proc 블록은 이 코어에 없다 — 2026-08-09 전수 확인.)
    """
    out = []
    pos = 0
    changed = 0
    for m in re.finditer(r"proc\s*\{", src):
        if m.start() < pos:
            continue
        i = m.end() - 1
        depth = 0
        while i < len(src):
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        block = src[m.start():i]
        new_block, n = re.subn(r"(?m)^(\s*)return\b", r"\1next", block)
        if n:
            out.append(src[pos:m.start()])
            out.append(new_block)
            pos = i
            changed += n
    if not changed:
        return src, 0
    out.append(src[pos:])
    return "".join(out), changed


def patch_file(path: Path) -> None:
    secs = load(open(path, "rb"))
    changed = []

    # ① 심 섹션 — 있으면 갈아 끼우고 없으면 맨 앞에 넣는다
    shim = zlib.compress(SHIM.read_bytes())
    hit = [s for s in secs if bytes(s[1]) == SECTION_NAME]
    if hit:
        if bytes(hit[0][2]) != shim:
            hit[0][2] = shim
            changed.append("심 갱신")
    else:
        secs.insert(0, [SECTION_ID, SECTION_NAME, shim])
        changed.append("심 삽입(맨 앞)")

    # ② 문법 수술
    for hint, rx, repl in REGEX_EDITS:
        for sec in secs:
            name = bytes(sec[1]).decode("utf-8", "replace")
            if name != hint:
                continue
            src = zlib.decompress(bytes(sec[2])).decode("utf-8")
            src2, n = rx.subn(repl, src)
            if n:
                sec[2] = zlib.compress(src2.encode("utf-8"))
                changed.append(f"{name}: {n}곳")
            break
        else:
            sys.exit(f"중단: {path}에 '{hint}' 섹션이 없다 — 코어 구성이 바뀌었는지 확인")

    # ③ proc 안의 return → next (전 절)
    n_pr = 0
    for sec in secs:
        if bytes(sec[1]) == SECTION_NAME:
            continue
        src = zlib.decompress(bytes(sec[2])).decode("utf-8")
        src2, n = _proc_return_to_next(src)
        if n:
            sec[2] = zlib.compress(src2.encode("utf-8"))
            n_pr += n
    if n_pr:
        changed.append(f"proc 안 return→next: {n_pr}곳")

    if changed:
        bak = path.with_suffix(".rxdata.pre-compat.bak")
        if not bak.exists():
            bak.write_bytes(path.read_bytes())
        tmp = path.with_suffix(".rxdata.compat-tmp")
        with open(tmp, "wb") as fd:            # 옆에 쓰고 갈아 끼운다 — 하드링크를 끊는다
            rubywrite.dump(fd, secs)
        os.replace(tmp, path)
    print(f"{path}: " + (", ".join(changed) if changed else "손댈 것 없음(기적용)"))


if __name__ == "__main__":
    targets = [Path(a) for a in sys.argv[1:]] or DEFAULT_TARGETS
    for t in targets:
        patch_file(t)
