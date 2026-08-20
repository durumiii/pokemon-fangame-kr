# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""모드 카드의 `expects` 지문 검사 — 순정 기준으로 떠 있나.

    uv run share/qa-expects.py            # 저장소 mods/ + 보관소 둘 다
    uv run share/qa-expects.py --repo     # 저장소만

**모드 카드를 만들거나 고친 뒤, 그리고 배포 zip을 짓기 전에 돌린다.** 문제가 없으면
한 줄로 조용히 지나가고, 있으면 자리와 넣어야 할 값을 찍고 종료 코드 1로 멈춘다.

`mod.json`의 `expects`(절 이름 → 절 전문 md5)는 **순정 기준**으로 떠야 한다. 손 닿는
파일이 한글패치가 얹힌 설치본이라 뼈대 도구의 산출에 설치본 지문이 박히기 쉽고, 그
카드를 재료로 쓰는 통합 모드에까지 번진다.

무엇을 잡나:
- **설치본 지문** — 카드값이 설치본(`Scripts.rxdata`)과 일치한다. 순정에서 받은 사람의
  설치가 어긋난다. 순정 지문은 `Scripts.rxdata.orig`에서 뜬다.
- **어느 쪽도 아닌 지문** — 게임 판이 바뀌었거나 딴 게임의 카드다.
- **순정에 없는 절** — 코어 수술이 만든 절에 기댄다. 게이트의 「모드는 혼자 서야 한다」에
  걸린다.

⚠ 통합 모드(`UI KR`·`Utility Pack`)는 조립기 산출이다 — 카드를 손으로 고치지 말고
재료 모드를 고친 뒤 `uv run runa/make-union-mods.py`로 다시 조립한다.
"""
import importlib.util
import json
import sys
from pathlib import Path

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18")   # probe.py·verify.py와 같은 상수
HERE = Path(__file__).resolve().parent
ROOTS = [("저장소", HERE.parent / "mods"),
         ("보관소", Path("/mnt/d/GameVault/mods/Pokemon Z Fangame"))]
UNION = {"UI KR", "Utility Pack"}            # runa/make-union-mods.py 산출

_spec = importlib.util.spec_from_file_location("qa_sections", HERE / "qa-sections.py")
_qs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_qs)


def fingerprints(path):
    return {n: h for n, h, _l, _s in _qs.sections(path)}


def main():
    orig = fingerprints(GAME / "Data/Scripts.rxdata.orig")
    inst = fingerprints(GAME / "Data/Scripts.rxdata")

    roots = ROOTS[:1] if "--repo" in sys.argv else ROOTS
    checked = bad = 0
    for tag, root in roots:
        if not root.is_dir():
            print(f"! {tag} 모드 폴더가 없다: {root}")
            return 1
        for card in sorted(root.glob("*/mod.json")):
            mod = card.parent.name
            try:
                expects = json.loads(card.read_text(encoding="utf-8")).get("expects") or {}
            except ValueError as e:
                print(f"! {tag} {mod}: 카드를 못 읽는다 — {e}")
                bad += 1
                continue
            for sec, md5 in sorted(expects.items()):
                checked += 1
                if sec not in orig:
                    why, fix = "순정에 없는 절", "코어 수술에 기댄다 — 모드 안에서 전제를 없애라"
                elif md5 == orig[sec]:
                    continue
                elif md5 == inst.get(sec):
                    why, fix = "설치본 지문", f"순정값 {orig[sec]}"
                else:
                    why, fix = "순정에도 설치본에도 없는 지문", f"순정값 {orig[sec]}"
                bad += 1
                print(f"! {tag} {mod} / {sec}\n    {why}: {md5}\n    → {fix}")
                if mod in UNION:
                    print("    ⚠ 조립기 산출이다 — 카드를 손으로 고치지 말고 재료 모드를"
                          " 고친 뒤 `uv run runa/make-union-mods.py`로 다시 조립해라")

    if bad:
        print(f"\n{checked}줄 중 {bad}줄이 어긋난다.")
        return 1
    print(f"expects {checked}줄 모두 순정 지문과 맞다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
