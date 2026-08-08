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
]


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
