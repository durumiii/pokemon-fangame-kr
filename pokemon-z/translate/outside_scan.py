# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""번역 조회를 안 타는 이름을 translate/data/outside-sites.jsonl로 모은다 (Z-63/Z-53).

담는 것 둘 — 근거는 docs/log/research/2026-08-17-names-outside-translation-table.md:
  tower   배틀 시설(`TorreBatalla` 절 `BT_TRAINERS`)의 트레이너 이름. 해시 문자열이
          `PokeBattle_Trainer.new`로 곧바로 들어가 `pbGetMessageFromHash`를 안 탄다.
          번역값이 없다 — 미번역이 사실이라 `ko`를 안 적는다.
  surgery 소스에 리터럴로 박혀 `_INTL` 포장이 없는 이름 넷. 값은 share/patch_intl.py의
          EDITS가 이미 실어 나르므로 여기서는 그 값을 그대로 옮긴다(대조만 하고
          patch_intl은 고치지 않는다).

미리보기: uv run translate/outside_scan.py   /   반영: uv run translate/outside_scan.py --write
"""
import json
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "vendor"))
from datread import load  # noqa: E402

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18")   # probe.py·verify.py와 같은 상수
OUT = ROOT / "data/outside-sites.jsonl"
PATCH_INTL = ROOT.parent / "share/patch_intl.py"

NAME_RE = re.compile(r':name\s*=>\s*"((?:[^"\\]|\\.)*)"')

# 소스 수술로 옮긴 이름 넷 — 값의 정본은 share/patch_intl.py의 EDITS다.
SURGERY = [
    ("Paulie", "폴리", "Data/trainers.dat 별명"),
    ("ARTIFICIO", "수호장치", "PField_EncounterModifiers:187"),
    ("FLOR", "꽃", "PField_EncounterModifiers:201"),
    ("FLOR", "꽃", "Boss:37"),
]


def tower_names():
    for sec in load(open(GAME / "Data/Scripts.rxdata", "rb")):
        if bytes(sec[1]).decode("utf-8", "replace") == "TorreBatalla":
            src = zlib.decompress(bytes(sec[2])).decode("utf-8")
            return sorted(set(NAME_RE.findall(src)))
    sys.exit("중단: Scripts.rxdata에 TorreBatalla 절이 없다")


def check_patch_intl():
    """수술 넷의 원문·번역이 patch_intl에 실제로 있는지 — 어긋나면 경고만 찍는다."""
    src = PATCH_INTL.read_text(encoding="utf-8")
    for es, ko, where in SURGERY:
        if f'"{es}"' not in src or f'"{ko}"' not in src:
            print(f"경고: patch_intl에 {es}→{ko}({where})가 안 보인다 — 값이 어긋났는지 확인")


def build():
    rows = [{"kind": "surgery", "src": es, "ko": ko, "where": where}
            for es, ko, where in SURGERY]
    rows += [{"kind": "tower", "src": n} for n in tower_names()]
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def main():
    check_patch_intl()
    new = build()
    cur = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if new == cur:
        print("변경 없음 (%d줄)" % new.count("\n"))
        return
    old_set, new_set = set(cur.splitlines()), set(new.splitlines())
    print("현행 %d줄 → 생성 %d줄 (더함 %d · 뺌 %d)"
          % (cur.count("\n"), new.count("\n"),
             len(new_set - old_set), len(old_set - new_set)))
    if "--write" in sys.argv:
        OUT.write_text(new, encoding="utf-8")
        print("반영: %s" % OUT)
    else:
        for line in sorted(new_set - old_set)[:5]:
            print("  + " + line)
        for line in sorted(old_set - new_set)[:5]:
            print("  - " + line)


def demo():
    """자기 점검 — 이름 뽑기와 줄 꼴이 서는가."""
    names = tower_names()
    assert len(names) == len(set(names)) and names == sorted(names)
    assert "Tobal" in names and len(names) > 800, len(names)
    rows = [json.loads(l) for l in build().splitlines()]
    assert [r["kind"] for r in rows[:4]] == ["surgery"] * 4
    assert all(r["kind"] == "tower" and "ko" not in r for r in rows[4:])
    assert len({(r.get("where", ""), r["src"]) for r in rows}) == len(rows), "자리가 겹친다"
    assert build() == build(), "두 번 돌린 결과가 다르다"
    print("demo OK — tower %d개 · 수술 %d개" % (len(names), len(SURGERY)))


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else main()
