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
  6. 고유명 표기 — canon/names.jsonl에 적어 둔 정본 표기의 「변이」가 번역에
     남아 있지 않은지(같은 인물이 두 표기로 갈리는 사고를 막는다).

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
from datread import load  # noqa: E402  (딱지를 떼 옛 도구가 그대로 읽는다)

STORE_DAT = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/korean.dat")
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


def check_ribbons(strict):
    """절23 리본 이름을 본가 정식명과 대조 — 원문(영어) 키로.

    리본은 이름이지만 이름 절이 아니라 스크립트 문자열 절(23)에 있어서
    canon 대조의 그물 밖이었다(2026-08-06: 16자리가 비공식 조어·일본어
    잔재로 남아 있었다). 문장 코퍼스의 영어 칸을 다리로 삼아 잡는다.
    구세대 콘테스트 리본은 코퍼스(xy 이후)에 없어 대조표 밖으로 센다.
    """
    import gzip
    want_by_en = {}
    # ① PKHeX 리본표(canon.jsonl의 ribbons 도메인) — 3·4세대 콘테스트 리본까지 있다.
    #    게임 쪽 이름은 「Cool Ribbon Super」, PKHeX는 「Cool Super」라 Ribbon을 끼워 맞춘다.
    for r in rows(HERE / "canon" / "canon.jsonl"):
        if r.get("domain") != "ribbons":
            continue
        parts = r["en"].split()
        want_by_en[" ".join(parts[:1] + ["Ribbon"] + parts[1:])] = r["ko"]
        want_by_en[r["en"] + " Ribbon"] = r["ko"]
    # ② 문장 코퍼스 — 게임 안 표기가 PKHeX 목록과 다른 자리를 덮는다(뒤가 이긴다).
    path = HERE / "canon" / "messages.jsonl.gz"
    if path.exists():
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                en = r.get("en") or ""
                if en.endswith("Ribbon") and r["ko"].endswith("리본"):
                    want_by_en[en] = r["ko"]
    mismatch = miss = ok = 0
    for r in rows(HERE / "ko" / "23-script-texts.jsonl"):
        k, ko = r.get("k") or "", r.get("v")
        # 「Cool Ribbon Super」처럼 뒤에 등급이 붙는 이름까지 본다. 설명 문장
        # (「A Ribbon awarded for …」)은 낱말 수로 걸러 낸다.
        if "Ribbon" not in k or not ko or len(k.split()) > 4 or k.endswith("."):
            continue
        want = want_by_en.get(k)
        if want is None:
            miss += 1
        elif ko == want:
            ok += 1
        else:
            mismatch += 1
            report("FAIL" if strict else "WARN",
                   f"리본 불일치 {k!r}: 현행 {ko!r} ≠ 정식 {want!r}")
    print(f"리본: 일치 {ok} · 불일치 {mismatch} · 대조표 밖(구세대 콘테스트 등) {miss}")


def check_kinds(strict):
    """절02 도감 분류를 genera.jsonl(종번호 키, PokeAPI 산·공식 덤프 교차 검증)과 대조.

    분류는 원문이 짧은 낱말이라 문자열 대조는 오탐 천지다(「Seed」=비비용 무늬) —
    종번호로 잇는다. 팬게임 창작종은 종명이 표와 달라서 거른다: 절01의 한국어
    종명이 표를 만든 종과 같은 자리(canon species와 일치)만 본다.
    """
    path = HERE / "canon" / "genera.jsonl"
    if not path.exists():
        return
    genera = {r["i"]: r["ko"] for r in rows(path)}
    canon_sp = {r["i"]: r["ko"] for r in rows(HERE / "canon" / "canon.jsonl")
                if r.get("domain") == "species" and "i" in r}
    species = {r["i"]: r["v"] for r in rows(HERE / "ko" / "01-species.jsonl") if r.get("v")}
    mismatch = skip = ok = 0
    for r in rows(HERE / "ko" / "02-kinds.jsonl"):
        i, ko = r.get("i"), r.get("v")
        if not ko or i not in genera or canon_sp.get(i) != species.get(i):
            skip += 1  # 창작종·리전폼·표 밖 — 대조 불가
            continue
        if ko == genera[i]:
            ok += 1
        else:
            mismatch += 1
            report("FAIL" if strict else "WARN",
                   f"분류 불일치 i={i}({species.get(i)}): 현행 {ko!r} ≠ 본가 {genera[i]!r}")
    print(f"분류: 일치 {ok} · 불일치 {mismatch} · 대조 밖(창작종 등) {skip}")


def check_dat_and_sentinels():
    d = load(open(STORE_DAT, "rb"))
    ks, vs = inner_of(d[23])
    # __kr_patch__는 build.py가 심는 버전 표식 — 정본 미러 대상이 아니다
    pairs = [(k, v) for k, v in zip(ks, vs) if bytes(k) != b"__kr_patch__"]
    ks, vs = [k for k, _ in pairs], [v for _, v in pairs]
    jr = rows(HERE / "ko" / "23-script-texts.jsonl")
    # __kr_patch__ 버전 표식(build.py가 심음)은 정본 밖 — 카운트에서 제외
    n_dat = sum(1 for k in ks if bytes(k) != b"__kr_patch__")
    if len(jr) != n_dat:
        report("FAIL", f"절23 미러 어긋남: jsonl {len(jr)} ≠ dat {n_dat}")
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


def check_names(strict):
    """고유명 표기 원장(canon/names.jsonl)의 변이가 번역에 남았는지.

    변이는 「이 표기는 틀렸다」고 판정이 난 것이라 의역 여지가 없다 —
    canon 불일치와 달리 기본이 FAIL이다.
    """
    path = HERE / "canon" / "names.jsonl"
    if not path.exists():
        return
    ledger = rows(path)
    bad = 0
    for fname in sorted(p.name for p in (HERE / "ko").glob("*.jsonl")):
        for n, r in enumerate(rows(HERE / "ko" / fname), 1):
            v = r.get("v") or ""
            src = (r.get("k") or r.get("es") or "").lower()
            for e in ledger:
                # 원문에 그 이름이 있는 행에서만 잡는다 — 번역 칸만 보면 옛 표기가
                # 묻힌 다른 낱말을 문다(「무사」가 변이일 때 「무사히」·「갑주무사」).
                if e["es"].lower() not in src:
                    continue
                for wrong in e.get("변이", []):
                    if wrong in v:
                        bad += 1
                        report("FAIL" if strict else "WARN",
                               f"표기 변이 {fname}:{n} {wrong!r} → {e['ko']!r}")
    print(f"고유명: 이름 {len(ledger)}개, 변이 잔존 {bad}")


def main():
    strict = "--strict" in sys.argv
    check_canon(strict)
    check_ribbons(strict)
    check_kinds(strict)
    check_names(strict)
    check_dat_and_sentinels()
    check_scripts()
    check_ui_gsub()
    print(f"\n결과: FAIL {fail} · WARN {warn}")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
