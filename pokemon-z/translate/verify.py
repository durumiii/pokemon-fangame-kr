# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""재배포 전 검증 게이트 — 한 번에 전부.

검사 항목:
  1. canon 정합 — 이름 절(종·기술·특성·성격·타입·아이템)을 본가 정식명
     대조표(canon/canon.jsonl, PKHeX 산)와 원문(es) 키로 전수 대조.
     구세대 스페인어명은 canon/aliases.jsonl({"es_old","domain","es"})로 흡수.
  2. dat 미러 — 절23 jsonl과 보관소 korean.dat의 키 1:1 일치(개수+표본).
  3. 조회 표본 — 파수 키 몇 개를 stringToKey(루비 오라클 검증판)로 조회.
  4. 게임 Scripts.rxdata — MOD 절 중복 없음 + 보간 수술·부적 수술 잔존.
  5. UI Text KR gsub 오폭 — 치환표 원문이 번역 정본의 한국어 값에 부분
     일치하는 행이 없는지(있으면 화면에서 한국어가 이중 치환된다).

경고(exit 0)와 실패(exit 1)를 구분한다. canon 불일치는 기본 경고 —
의도적 의역(glossary 판정)이 있을 수 있어서다. --strict면 실패로 격상.

usage: uv run verify.py [--strict]
"""
import io
import json
import re
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from rubymarshal.reader import load  # noqa: E402

STORE_DAT = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/korean.dat")
GAME_RX = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/Scripts.rxdata")
UI_MOD = HERE.parent / "mods" / "UI Text KR" / "001_UiText.rb"

# 이름 절 → canon 도메인
NAME_SECTIONS = {
    "01-species.jsonl": "species",
    "05-moves.jsonl": "moves",
    "07-items.jsonl": "items",
    "10-abilities.jsonl": "abilities",
    "12-types.jsonl": "types",
}
SENTINELS = [  # (절23 키, 기대 부분 문자열)
    ("Fuerte", "노력"),
    ("¡{1} ha perdido energía!", "체력을 흡수"),
    ("¡{1} alteró las dimensiones!", "시공"),
]

warn = fail = 0


def report(level, msg):
    global warn, fail
    if level == "FAIL":
        fail += 1
    else:
        warn += 1
    print(f"[{level}] {msg}")


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def string_to_key(s):
    if re.search(r"[\r\n\t\x01]|(?m:^\s+|\s+$)|\s{2,}", s):
        s = re.sub(r"(?m)^\s+", "", s)
        s = re.sub(r"(?m)\s+$", "", s)
        s = re.sub(r"\s{2,}", " ", s)
    return s


def rows(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l]


def check_canon(strict):
    canon = {}
    for r in rows(HERE / "canon" / "canon.jsonl"):
        canon[(r["domain"], r["es"])] = r["ko"]
    alias_path = HERE / "canon" / "aliases.jsonl"
    if alias_path.exists():
        for a in rows(alias_path):
            ko = canon.get((a["domain"], a["es"]))
            if ko:
                canon[(a["domain"], a["es_old"])] = ko
    exc_path = HERE / "canon" / "exceptions.jsonl"
    exceptions = {}
    if exc_path.exists():
        exceptions = {(e["domain"], e["es"]): e["keep_ko"] for e in rows(exc_path)}
    mismatch = miss = ok = 0
    for fname, domain in NAME_SECTIONS.items():
        for r in rows(HERE / "ko" / fname):
            es, ko = r.get("es"), r.get("v")
            if not es or not ko:
                continue
            if exceptions.get((domain, es)) == ko:
                ok += 1
                continue
            want = canon.get((domain, es))
            if want is None:
                miss += 1  # 팬게임 창작이거나 구세대명 — 별칭/용어집 몫
            elif ko == want:
                ok += 1
            else:
                mismatch += 1
                report("FAIL" if strict else "WARN",
                       f"canon 불일치 {fname} {es!r}: 현행 {ko!r} ≠ 정식 {want!r}")
    print(f"canon: 일치 {ok} · 불일치 {mismatch} · 대조표 밖(창작/구세대명) {miss}")


def check_dat_and_sentinels():
    d = load(open(STORE_DAT, "rb"))
    ks, vs = inner_of(d[23])
    jr = rows(HERE / "ko" / "23-script-texts.jsonl")
    if len(jr) != len(ks):
        report("FAIL", f"절23 미러 어긋남: jsonl {len(jr)} ≠ dat {len(ks)}")
    sec = {bytes(k).decode("utf-8", "replace"): bytes(v).decode("utf-8", "replace")
           for k, v in zip(ks, vs)}
    for key, expect in SENTINELS:
        got = sec.get(string_to_key(key))
        if got is None:
            report("FAIL", f"파수 키 MISS: {key!r}")
        elif expect not in got:
            report("FAIL", f"파수 키 값 이상: {key!r} → {got[:40]!r} (기대 부분: {expect})")
    print(f"dat: 절23 {len(ks)}키, 파수 {len(SENTINELS)}종 조회")


def check_scripts():
    secs = load(open(GAME_RX, "rb"))
    names = [bytes(s[1]).decode("utf-8", "replace") for s in secs]
    mods = [n for n in names if n.startswith("MOD:")]
    if len(mods) != len(set(mods)):
        report("FAIL", f"MOD 절 중복: {sorted(set(m for m in mods if mods.count(m) > 1))}")
    marks = {  # 소스 수술 잔존 확인
        "PokeBattle_Battler": '_INTL("¡{1} alteró las dimensiones!",pbThis)',
        "PItem_ItemEffects": "isConst?(item,PBItems,:AMULETODRAGON)",
    }
    for hint, needle in marks.items():
        found = False
        for s in secs:
            n = bytes(s[1]).decode("utf-8", "replace")
            if hint in n and not n.startswith("MOD:"):
                src = zlib.decompress(bytes(s[2])).decode("utf-8")
                found = needle in src
                break
        if not found:
            report("FAIL", f"소스 수술 실종: {hint} — patch_intl.py 재실행 필요")
    print(f"scripts: 절 {len(secs)}, MOD {len(mods)}")


def check_ui_gsub():
    src = UI_MOD.read_text(encoding="utf-8")
    pairs = re.findall(r'\["((?:[^"\\]|\\.)+)",\s*"(?:[^"\\]|\\.)+"\]', src)
    kos = []
    for f in (HERE / "ko").glob("*.jsonl"):
        for r in rows(f):
            v = r.get("v")
            if v:
                kos.append(v)
    hits = 0
    for p in pairs:
        if re.search(r"[가-힣]", p):
            continue  # 원문이 한글인 쌍은 대상 아님
        c = sum(1 for v in kos if p in v)
        if c:
            hits += 1
            report("WARN", f"UI gsub 오폭 후보: {p!r} 가 번역 값 {c}행에 부분 일치")
    print(f"UI 치환표: {len(pairs)}쌍, 오폭 후보 {hits}")


def main():
    strict = "--strict" in sys.argv
    check_canon(strict)
    check_dat_and_sentinels()
    check_scripts()
    check_ui_gsub()
    print(f"\n결과: FAIL {fail} · WARN {warn}")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
