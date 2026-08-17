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
    # 추가분(`23-script-texts.add.jsonl`)은 base에 없는 키를 dat 꼬리에 얹는다 —
    # build.py가 그 꼬리를 허용하므로(tail_ok) 미러 셈에도 함께 넣는다. 이걸 빼먹으면
    # 추가분을 늘릴 때마다 미러가 어긋난 것처럼 잡힌다.
    add_path = HERE / "ko" / "23-script-texts.add.jsonl"
    n_add = len({string_to_key(r["k"]) for r in rows(add_path) if "k" in r}) \
        if add_path.exists() else 0
    # __kr_patch__ 버전 표식(build.py가 심음)은 정본 밖 — 카운트에서 제외
    n_dat = sum(1 for k in ks if bytes(k) != b"__kr_patch__")
    if len(jr) + n_add != n_dat:
        report("FAIL", f"절23 미러 어긋남: jsonl {len(jr)}+추가분 {n_add} ≠ dat {n_dat}")
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
    # 표는 문자열 쌍과 **정규식 쌍** 둘로 돼 있다. 문자열만 세면 인명 정규식
    # 스물셋이 통째로 검사 밖에 남는다(2026-08-17 실측·수선).
    lits = re.findall(r'\["((?:[^"\\]|\\.)+)",\s*"(?:[^"\\]|\\.)+"\]', src)
    rxs = re.findall(r'\[/((?:[^/\\]|\\.)+)/,\s*"(?:[^"\\]|\\.)+"\]', src)
    # 루비 리터럴의 몸통을 그대로 파이썬 re로 읽는다 — 표가 쓰는 것은 `\b`와
    # 문자뿐이고, 루비도 파이썬도 UTF-8에서 한글을 낱말 문자로 쳐 경계가 같다.
    probes = [(p, re.compile(re.escape(p))) for p in lits]
    probes += [(f"/{p}/", re.compile(p)) for p in rxs]
    kos = []
    for f in (HERE / "ko").glob("*.jsonl"):
        for r in rows(f):
            v = r.get("v")
            if v:
                kos.append(v)
    hits = 0
    for label, rx in probes:
        if re.search(r"[가-힣]", label):
            continue  # 원문이 한글인 쌍은 대상 아님
        c = sum(1 for v in kos if rx.search(v))
        if c:
            hits += 1
            report("WARN", f"UI gsub 오폭 후보: {label!r} 가 번역 값 {c}행에 부분 일치")
    print(f"UI 치환표: {len(probes)}쌍(문자열 {len(lits)} · 정규식 {len(rxs)}), 오폭 후보 {hits}")


def check_names(strict):
    """고유명 표기 목록(canon/names.jsonl)의 변이가 번역에 남았는지.

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


def check_unified(strict):
    """여러 맵에 복제된 같은 원문은 한 판이어야 한다 — 통일은 관리 단위 선언이다.

    Z-28(2026-08-10)이 통일한 상태를 지키는 게이트. 의도된 갈림(화자별 유지·손수정)만
    `data/divergence-allowed.jsonl`에 근거와 함께 등재돼 있고, 그 밖의 갈림은 배치·손질이
    통일을 도로 가른 것이므로 FAIL이다. 갈림을 새로 허용하려면 판정을 갈림 허용 목록에 등재한다.
    """
    # 갈림 허용 목록 — 갈래별 값(ko)·자리(maps)·화자(sprites)를 자체 저장한다. 맵별 기대값을
    # 펴서 값까지 대조한다 — 갈림이 허용됐어도 갈래 안 표류는 훼손이다.
    allowed = {}
    p = HERE / "data" / "divergence-allowed.jsonl"
    if p.exists():
        for r in rows(p):
            allowed[r["es"]] = {m: b["ko"] for b in r.get("갈래", []) for m in b["maps"]}
    led = {r["es"]: r["ko"] for r in rows(HERE / "data" / "unified-phrases.jsonl")} \
        if (HERE / "data" / "unified-phrases.jsonl").exists() else {}
    groups = {}
    cur = None
    for n, r in enumerate(rows(HERE / "ko" / "00-maps.jsonl"), 1):
        if "map" in r:
            cur = r["map"]
            continue
        k = re.sub(r"\s+", " ", r.get("k") or "").strip()
        groups.setdefault(k, []).append((cur, r.get("v"), n))
    bad = drift = 0
    for k, g in groups.items():
        maps = sorted({m for m, _, _ in g})
        # 목록 등재분 — 통일판 자체가 저장돼 있으니 값까지 대조한다. 어긋나면
        # unified.py restore(실수 복원) 또는 sync --write(의도적 변경 등재)로 푼다.
        if k in led:
            if {v for _, v, _ in g} != {led[k]}:
                drift += 1
                report("FAIL" if strict else "WARN",
                       f"통일 목록 불일치 {k[:50]!r} — 맵 {maps} (unified.py restore/sync)")
            continue
        if k in allowed:
            exp = allowed[k]
            for m, v, _ in g:
                if m not in exp:
                    drift += 1
                    report("FAIL" if strict else "WARN",
                           f"갈림 허용 목록 미배정 자리 {k[:44]!r} — 맵 {m} (unified.py sync로 갈래 배정)")
                elif v != exp[m]:
                    drift += 1
                    report("FAIL" if strict else "WARN",
                           f"갈림 허용 목록 불일치 {k[:44]!r} — 맵 {m} (unified.py restore/sync)")
            continue
        if len(maps) <= 1 or len({v for _, v, _ in g}) <= 1:
            continue
        bad += 1
        report("FAIL" if strict else "WARN",
               f"통일 원문 갈림 (미허용·미등재) {k[:50]!r} — 맵 {maps}")
    print(f"통일 원문: 통일 목록 {len(led)}건 · 갈림 허용 {len(allowed)}건 · 불일치 {drift} · 미등재 갈림 {bad}")


def check_loc():
    """좌표 열쇠(Z-73)가 가리키는 자리가 실재하는가.

    좌표 항목의 원문이 그 맵의 정본에 없으면 게임에서 **조용히** 안 맞는다 —
    조회가 미스로 떨어져 옛 값이 그대로 뜨므로 화면만 봐서는 오타인지 판정대로인지
    구분이 안 된다. 그래서 여기서 잡는다. 자리 자체(이벤트·명령 인덱스)가 맞는지는
    실기에서만 갈리므로 이 검사 밖이다.
    """
    path = HERE / "ko" / "00-maps.loc.jsonl"
    if not path.exists():
        return
    base, cur = set(), None
    for r in rows(HERE / "ko" / "00-maps.jsonl"):
        if "map" in r:
            cur = r["map"]
        else:
            base.add((cur, string_to_key(r["k"])))
    bad = 0
    for n, r in enumerate(rows(path), 1):
        if (r["map"], string_to_key(r["k"])) not in base:
            bad += 1
            report("FAIL", f"좌표 열쇠의 원문이 맵 {r['map']} 정본에 없음 — 00-maps.loc.jsonl:{n}")
    print(f"좌표 열쇠: {len(rows(path))}줄 · 원문 미발견 {bad}")


def check_natures():
    """성격 활용형 25종이 명사형 정본과 짝을 유지하는가.

    요약 화면만 「얌전」 대신 「얌전한」을 쓰므로 활용형이 코드 수술로 들어간다
    (`share/patch_intl.py`). 값은 `data/nature-adj.jsonl`이 정본이고 명사형은 절23이라
    **두 곳이 갈릴 수 있다** — 성격 표기 판정이 바뀌면 절23만 고쳐지고 활용형은 조용히
    낡는다. 각 줄이 적어 둔 명사형 사본 `n`을 절23 현행값과 견줘 그때 알린다.
    """
    path = HERE / "data" / "nature-adj.jsonl"
    if not path.exists():
        return
    nat = [r for r in rows(path) if "adj" in r]
    if [r["i"] for r in sorted(nat, key=lambda r: r["i"])] != list(range(25)):
        report("FAIL", f"성격 활용형의 자리가 0~24로 서지 않는다 — {path.name}")
        return
    sec23 = {}
    for r in rows(HERE / "ko" / "23-script-texts.jsonl"):
        if "k" in r and r["k"] not in sec23:
            sec23[r["k"]] = r["v"]
    drift = 0
    for r in nat:
        cur = sec23.get(r["es"])
        if cur is None:
            drift += 1
            report("FAIL", f"성격 명사형이 절23에 없다 — {r['es']} (nature-adj.jsonl i={r['i']})")
        elif cur != r["n"]:
            drift += 1
            report("FAIL", f"성격 명사형이 바뀌었다 {r['es']}: {r['n']!r} → {cur!r} — "
                           f"활용형 {r['adj']!r}도 함께 고치고 nature-adj.jsonl의 n을 맞춰라")
    print(f"성격 활용형: 25종 · 명사형 어긋남 {drift}")


def mart_sites():
    """수술이 갈래 조회를 거는 점원 문구가 몇 종인가 — `share/patch_intl.py`가 정본이다."""
    src = (HERE.parent / "share" / "patch_intl.py").read_text(encoding="utf-8")
    return len(re.findall(r'"PScreen_Mart",\n\s*\'[^\']*_INTL\(', src))


def check_mart():
    """상점 점원 문구의 갈래가 온전한가 (Z-73).

    갈래에 줄이 빠지면 게임이 **조용히** 기본 갈래(존대)로 떨어진다 — 화면만 봐서는
    빠뜨린 것인지 그렇게 정한 것인지 구분이 안 되므로 여기서 센다. 원문은 base 정본의
    키와 글자까지 같아야 하고(다르면 조회가 미스), 배정이 가리키는 갈래는 실재해야 한다.
    """
    path = HERE / "ko" / "23-script-texts.add.jsonl"
    if not path.exists():
        return
    base = {r["k"] for r in rows(HERE / "ko" / "23-script-texts.jsonl") if "k" in r}
    vals, at, bad = {}, {}, 0
    for r in rows(path):
        k = r.get("k", "")
        if k.startswith("krmart:"):
            br, _, src = k[len("krmart:"):].partition("|")
            vals.setdefault(br, set()).add(src)
            if src not in base:
                bad += 1
                report("FAIL", f"상점 갈래 「{br}」의 원문이 절23 정본에 없다 — {src[:40]!r}")
        elif k.startswith("krmart-at:"):
            at[k] = r["v"]
    if not vals and not at:
        return
    # 기대 줄 수는 수술 쪽이 정본이다 — 게임이 갈래 조회를 거는 자리가 곧 그 수다.
    # 갈래끼리만 견주면 **모든 갈래에서 같이 빠진 줄**을 못 잡는다.
    want = mart_sites()
    for br, srcs in sorted(vals.items()):
        if want and len(srcs) != want:
            bad += 1
            report("FAIL", f"상점 갈래 「{br}」가 {len(srcs)}줄 — 수술이 거는 자리는 {want}줄이다"
                           " (빠진 줄은 조용히 기본 갈래로 떨어진다)")
    for k, br in sorted(at.items()):
        if br not in vals:
            bad += 1
            report("FAIL", f"상점 배정 {k}가 없는 갈래 「{br}」를 가리킨다")
    print(f"상점 갈래: {len(vals)}갈래 × {want}줄(수술 자리 기준) · 배정 {len(at)}곳 · 어긋남 {bad}")


def main():
    strict = "--strict" in sys.argv
    check_canon(strict)
    check_ribbons(strict)
    check_kinds(strict)
    check_names(strict)
    check_unified(strict)
    check_loc()
    check_natures()
    check_mart()
    check_dat_and_sentinels()
    check_scripts()
    check_ui_gsub()
    print(f"\n결과: FAIL {fail} · WARN {warn}")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
