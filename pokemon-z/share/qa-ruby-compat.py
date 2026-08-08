"""코어·모드 스크립트를 신형 루비(1.9~3.x) 지뢰 목록으로 정적 훑는다.

    uv run --project ~/workspace/claude-native/sketches/essentials-modkit \
        python qa-ruby-compat.py <Scripts.rxdata나 게임 폴더> [--ruby <루비 실행 파일>]

두 겹으로 본다.
① 패턴 — 1.8 전용 API·관용구가 신형 루비에서 어떻게 죽는지 종류별로 찍는다.
   즉사(NameError·NoMethodError·ArgumentError)와 조용한 오판(== 거짓)을 구분한다.
② 문법 — --ruby로 신형 루비를 주면 섹션마다 `-c`를 돌려 파싱 불통(1.8 전용
   구문: `when 0:` · rescue 밖 `retry` 등)을 찾는다. 없으면 건너뛴다.

한계 — 정적 grep이라 첨자 비교(`x[i] < 정수`)는 받는 쪽이 String인지 모른다.
「의심」 등급으로만 찍으니 눈으로 가려낼 것. 모바일 실행기(Runa·RPG Player)는
1.8 계열이면서 문자열 첨자만 1.9 의미론인 혼종이라(2026-08-08 제보 실측),
거기서는 「String 첨자 바이트」 부류만 실제로 터진다.
"""
import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, "/home/durumii/workspace/claude-native/sketches/essentials-modkit")
from modkit import scripts  # noqa: E402

# (이름, 정규식, 신형 루비에서 무슨 일이 나나)
PATTERNS = [
    ("Fixnum/Bignum", re.compile(r"\b(Fixnum|Bignum)\b"),
     "3.2+에서 NameError 즉사"),
    ("File/Dir.exists?", re.compile(r"\b(File|Dir)\.exists\?"),
     "3.2+에서 NoMethodError 즉사"),
    ("Thread.critical", re.compile(r"\bThread\.critical\b"),
     "1.9+에서 NoMethodError 즉사"),
    ("$KCODE", re.compile(r"\$KCODE\s*="),
     "1.9+에서 경고(무해에 가깝다)"),
    ("Array#nitems", re.compile(r"\.nitems\b"),
     "1.9+에서 NoMethodError 즉사"),
    ("Object#type 클래스비교", re.compile(r"\.type\s*(==|!=)\s*[A-Z]"),
     "1.9+에서 NoMethodError — 단 .type이 그 클래스의 속성이면 무해"),
    ("String#each", re.compile(r"\b(text|str|line|msg|contents)\.each\b(?!_)"),
     "1.9+에서 NoMethodError — 받는 쪽이 String일 때만"),
    ("getbyte", re.compile(r"\.getbyte\b"),
     "모바일 실행기(Runa·RPG Player)에 없다 — respond_to? 분기 말고 unpack을 쓸 것"),
    ("String 첨자 바이트 의심", re.compile(
        r"\[\s*\w{1,6}\s*\]\s*(==|!=|<=|>=|<|>)\s*(0x[0-9a-fA-F]+|\d{2,3})\b"),
     "받는 쪽이 String이면 1.9 의미론에서 부등호는 ArgumentError 즉사, ==는 조용히 거짓"),
]


def iter_sources(target: pathlib.Path):
    if target.is_dir():
        yield from scripts.sources(target)
        return
    # rxdata 파일 하나를 받았으면 임시 game_dir 꼴을 만들어 준다
    with tempfile.TemporaryDirectory() as td:
        data = pathlib.Path(td) / "Data"
        data.mkdir()
        (data / "Scripts.rxdata").write_bytes(target.read_bytes())
        yield from scripts.sources(pathlib.Path(td))


def main() -> int:
    ap = argparse.ArgumentParser(description="신형 루비 호환 정적 감사")
    ap.add_argument("target", type=pathlib.Path,
                    help="Scripts.rxdata 파일이나 게임 폴더")
    ap.add_argument("--ruby", type=pathlib.Path, default=None,
                    help="문법 검사에 쓸 신형 루비 실행 파일 (없으면 문법 검사 생략)")
    args = ap.parse_args()

    hits = []
    syntax_bad = []
    count = 0
    for name, src in iter_sources(args.target):
        count += 1
        for i, ln in enumerate(src.split("\n"), 1):
            body = ln.split("#", 1)[0]
            for label, rx, effect in PATTERNS:
                if rx.search(body):
                    hits.append((label, effect, name, i, ln.strip()[:100]))
        if args.ruby:
            with tempfile.NamedTemporaryFile(
                    "w", suffix=".rb", encoding="utf-8", delete=False) as f:
                f.write(src)
                tmp = pathlib.Path(f.name)
            r = subprocess.run([str(args.ruby), "-c", str(tmp)],
                               capture_output=True, text=True)
            if r.returncode != 0:
                first = (r.stderr.strip().split("\n")[0]
                         .replace(f"{args.ruby}: ", "").replace(str(tmp), ""))
                syntax_bad.append((name, first[:140]))
            tmp.unlink()

    print(f"섹션 {count}개")
    if args.ruby:
        print(f"\n■ 문법 불통 {len(syntax_bad)}개 — 신형 루비는 이 섹션을 읽다 즉사한다")
        for name, err in syntax_bad:
            print(f"  {name}{err}")
    last = None
    print(f"\n■ 패턴 적중 {len(hits)}건")
    for label, effect, name, i, ln in sorted(hits):
        if label != last:
            print(f"\n[{label}] — {effect}")
            last = label
        print(f"  {name}:{i} | {ln}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
