# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""patch_intl의 EDIT 전량 점검 — 적용 가능한가, 멱등한가. 설치본은 안 건드린다.

    uv run share/qa-edits.py

**EDIT을 더하거나 고친 뒤에 돌린다.** patch_file과 같은 셈법으로 절을 고르고 순차
적용을 흉내 내므로, 뒤 EDIT이 앞 EDIT의 산출을 앵커로 삼는 경우도 그대로 잡힌다.

무엇을 잡나:
- **멱등** — 옛 자구가 새 자구의 부분 문자열이면 「이미 얹혔나」 판정이 영영 안 서서
  돌릴 때마다 또 얹힌다(2026-08-17 실사고). 얹기만 하는 수술이 특히 걸린다 — 앵커에
  뒤따르는 줄까지 물리고, 새 코드가 옛 자구로 끝나지 않게 변수 이름까지 달리한다.
- **적용 가능** — 옛/새 자구가 둘 다 없으면 patch_intl은 그 자리에서 멈춘다. 게임 판이
  바뀌었거나 앵커를 잘못 뜬 것이다.

⚠ 절 이름은 부분 일치로 고른다(`hint in name`) — patch_file이 그렇게 하기 때문이다.
「Messages」가 「Intl_Messages」에도 걸리므로 절을 이름으로 직접 찾지 마라.
"""
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "vendor"))
sys.path.insert(0, str(HERE.parent / "translate"))
import patch_intl  # noqa: E402
from outside_scan import load, GAME  # noqa: E402


def main():
    secs = []
    for sec in load(open(GAME / "Data/Scripts.rxdata", "rb")):
        secs.append([bytes(sec[1]).decode("utf-8", "replace"),
                     zlib.decompress(bytes(sec[2])).decode("utf-8")])

    bad = 0
    for i, (hint, old, new) in enumerate(patch_intl.EDITS):
        if old in new:
            print(f"[{i}] {hint}: 멱등 깨짐 — 옛 자구가 새 자구의 부분 문자열")
            bad += 1
        hit = False
        for s in secs:                       # patch_file과 같은 순회
            if hint not in s[0] or s[0].startswith("MOD:"):
                continue
            if new in s[1] and old not in s[1]:
                hit = True                   # 이미 얹힘
                break
            if old in s[1]:
                s[1] = s[1].replace(old, new)
                hit = True
                break
        if not hit:
            print(f"[{i}] {hint}: 옛/새 자구 모두 없음 — patch_intl이 여기서 멈춘다")
            bad += 1

    print(f"EDIT {len(patch_intl.EDITS)}개 · 문제 {bad}개")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
