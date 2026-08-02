# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""디버그 패치 3편집 — 커뮤니티 배포 Scripts (1).rxdata의 변경분을 이식.

원본 파일을 통째로 쓰면 우리 수술·주입이 날아가므로, 실측으로 격리한
변경 3건만 지정 Scripts.rxdata에 얹는다(2026-08-03, 수술 전 원본 대비 diff):
  1) Main 머리에 `$DEBUG = true` — 디버그 모드 본체
  2) PokeBattle_Battle 전투 종료부에 `i.heal` — 전투 후 파티 전원 회복
  3) Menu Mejorado 퀵메뉴 라벨의 [A]/[D]/[S] 괄호 제거

멱등: 이미 적용된 파일에 다시 돌려도 무해(각 편집이 적용 여부를 검사).

usage: uv run patch_debug.py <Scripts.rxdata 경로>
"""
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from rubymarshal.reader import load  # noqa: E402
from fanlib import rubywrite  # noqa: E402


EDITS = {
    "Main": [("__PREPEND__", "$DEBUG = true\n\n")],
    "PokeBattle_Battle": [(
        "      i.itemInitial=i.itemRecycle=0\n      i.belch=false\n    end",
        "      i.itemInitial=i.itemRecycle=0\n      i.belch=false\n      i.heal\n    end",
    )],
    "Menu Mejorado": [
        ('["[A] Curar"', '["A Curar"'),
        ('["[D] Brújula"', '["D Brújula"'),
        ('["[S] Viajar"', '["S Viajar"'),
    ],
}


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: patch_debug.py <Scripts.rxdata>")
    p = Path(sys.argv[1])
    arr = load(open(p, "rb"))
    changed = 0
    for s in arr:
        name = s[1].decode("utf-8", errors="replace") if isinstance(s[1], bytes) else str(s[1])
        if name not in EDITS:
            continue
        body = zlib.decompress(bytes(s[2])).decode("utf-8")
        orig = body
        for old, new in EDITS[name]:
            if old == "__PREPEND__":
                if not body.startswith(new.split("\n", 1)[0]):
                    body = new + body
            elif old in body:
                body = body.replace(old, new)
            elif old.replace("\n", "\r\n") in body:  # CRLF 절(실측: PokeBattle_Battle)
                body = body.replace(old.replace("\n", "\r\n"), new.replace("\n", "\r\n"))
            # old도 new도 없으면 앵커 소실 — 사후 검증에서 잡힌다
        if body != orig:
            s[2] = zlib.compress(body.encode("utf-8"))
            changed += 1
            print(f"편집: {name}")
    if changed:
        with open(p, "wb") as f:
            rubywrite.dump(f, arr)
    # 사후 검증: 세 편집 전부 존재해야 성공
    arr2 = load(open(p, "rb"))
    ok = {"Main": False, "PokeBattle_Battle": False, "Menu Mejorado": False}
    for s in arr2:
        name = s[1].decode("utf-8", errors="replace") if isinstance(s[1], bytes) else str(s[1])
        if name in ok:
            body = zlib.decompress(bytes(s[2])).decode("utf-8")
            if name == "Main":
                ok[name] = body.startswith("$DEBUG = true")
            elif name == "PokeBattle_Battle":
                ok[name] = "i.belch=false\n      i.heal" in body.replace("\r\n", "\n")
            else:
                ok[name] = '["A Curar"' in body and "[A] Curar" not in body
    if not all(ok.values()):
        sys.exit(f"검증 실패: {ok}")
    print(f"디버그 3편집 확인 완료: {p}")


if __name__ == "__main__":
    main()
