# /// script
# requires-python = ">=3.12"
# ///
"""고유명 표기 목록 — 흩어진 표기를 한 곳에서 관리한다.

같은 인물·조직·용어가 번역 정본 곳곳에서 다르게 적히는 사고가 반복됐다
(아스터/아스테르 · 샤핀/사핀 · 프리물라/프리뮬라 · 팀 아조스/아조스단).
사람 눈으로 잡으면 늘 늦으니, 정본 표기를 표기 목록에 적어 두고 기계가 훑는다.

목록: translate/canon/names.jsonl — 한 줄이 이름 하나다.
    {"es": 원문, "ko": 정본 표기, "변이": [틀린 표기…], "쪽지": 판정 근거,
     "생략허용": true}   # 원문에 있어도 번역에서 이름을 안 쓸 수 있는 자리

usage:
  uv run tools/names.py check              변이 잔존과 표기 빠짐을 훑는다
  uv run tools/names.py rename <es> <새표기>  정본을 훑어 바꾸고 목록을 고친다
                                            (옛 표기는 변이 목록으로 내려간다)
  uv run tools/names.py add <es> <ko> [쪽지]  표기 목록에 새 이름을 올린다
  uv run tools/names.py sweep [--all] [--tsv]  목록을 안 보고 정본에서 갈림을 캐낸다

`check`는 verify.py에도 같은 검사가 들어 있다(재배포 게이트). 이 도구는 작업
중에 바로 돌려 보는 쪽이다.

`check`가 아는 것은 표기 목록에 적힌 변이뿐이라, 모르는 갈림은 애초에 검사 대상이
아니었다. `sweep`은 반대로 간다 — 정본에서 원문↔번역 쌍을 직접 캐서 한 원문이
여러 한국어로 적힌 자리를 찾아낸다. 규칙과 한계는
docs/log/research/2026-08-06-names-sweep.md.
"""
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent.parent
LEDGER = HERE / "translate" / "canon" / "names.jsonl"
KO_DIR = HERE / "translate" / "ko"

FINAL_CONSONANT = set()  # 받침 있는 한글 음절은 코드로 판별한다


def put_lines(edits):
    """0단계 정본에 앉히고 ko를 역생성한다 — 창구는 stage0/edit.py 하나다."""
    sys.path.insert(0, str(HERE / "translate" / "stage0"))
    from edit import put_lines as _put
    return _put(edits)


def sweep_skip(name):
    sys.path.insert(0, str(HERE / "translate" / "stage0"))
    from common import sweep_skip as _s
    return _s(name)

def has_batchim(word):
    """마지막 한글 음절에 받침이 있는가 — 조사 선택이 이걸로 갈린다."""
    for ch in reversed(word):
        if "가" <= ch <= "힣":
            return (ord(ch) - 0xAC00) % 28 != 0
    return None  # 한글이 아니면 판단하지 않는다


def load_ledger():
    if not LEDGER.exists():
        return []
    return [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]


def save_ledger(rows):
    LEDGER.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def ko_files():
    return sorted(KO_DIR.glob("*.jsonl"))


def each_row():
    """(파일, 줄번호, 엔트리) — 원문은 절마다 `k` 또는 `es`에 들어 있다."""
    for f in ko_files():
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                yield f, n, json.loads(line)


def src_of(entry):
    return entry.get("k") or entry.get("es") or ""


def cmd_check():
    ledger = load_ledger()
    bad = missing = 0
    for f, n, e in each_row():
        v = e.get("v", "")
        if not v:
            continue
        src = src_of(entry=e)
        for r in ledger:
            # 변이도 **원문에 그 이름이 있는 행에서만** 잡는다. 번역 칸만 보면
            # 옛 표기가 묻힌 다른 낱말을 잘못 문다(「무사」가 변이일 때 「무사히」·
            # 「갑주무사」·「무사태평」 88행이 걸렸다 — 2026-08-06).
            # 원문 대조는 **낱말 경계**로 — 부분 문자열은 「Alca」가 「Alcaide(소장)」에,
            # 「Mimi」가 「Mimikyu」에 걸린다(2026-08-06 실측 29건 중 24건이 이 오탐).
            # 대소문자도 지킨다 — 「Mujer(이름표)」를 소문자 mujer(보통명사)에 물리면 안 된다
            here = re.search(r"\b" + re.escape(r["es"]) + r"\b", src)
            for wrong in r.get("변이", []):
                if wrong in v and here:
                    bad += 1
                    print(f"[변이] {f.name}:{n} {wrong!r} → {r['ko']!r}  | {v[:70]}")
            if f.name in r.get("생략자리", ()):   # 의도된 자리(절13·14 어순 스왑 따위)
                continue
            if here and r["ko"] not in v and not r.get("생략허용"):
                missing += 1
                print(f"[빠짐] {f.name}:{n} 원문에 {r['es']!r} 있는데 {r['ko']!r} 없음 | {v[:70]}")
    print(f"\n이름 {len(ledger)}개 · 변이 잔존 {bad} · 표기 빠짐 {missing}")
    return 1 if bad else 0


def cmd_rename(es, new):
    ledger = load_ledger()
    row = next((r for r in ledger if r["es"] == es), None)
    if row is None:
        sys.exit(f"표기 목록에 없는 이름이에요: {es} — 먼저 add로 올려주세요")
    old = row["ko"]
    if old == new:
        sys.exit(f"이미 {new!r}예요")
    if old in new or new in old:
        print(f"⚠ 옛 표기와 새 표기가 서로를 품어요({old!r} / {new!r}) — "
              f"부분 치환이 겹칠 수 있으니 결과를 꼭 확인하세요")
    ob, nb = has_batchim(old), has_batchim(new)
    if ob is not None and nb is not None and ob != nb:
        print(f"⚠ 받침이 달라져요({old!r} {'있음' if ob else '없음'} → "
              f"{new!r} {'있음' if nb else '없음'}) — 뒤따르는 조사를 확인하세요")

    # ⚠ 번역 칸만 보고 바꾸면 안 된다 — 옛 표기가 다른 낱말에 묻혀 있는 자리를 함께 부순다
    # (2026-08-06 실사고: 「무사」→「총사」가 「무사히」·「갑주무사」(포켓몬 종명)·
    #  「무사 병영」까지 44행 갈아엎었다). **원문 칸에 그 이름이 있는 행만** 고친다.
    key = es.lower()
    changed, skipped = 0, []
    edits, left = [], []
    for f in ko_files():
        lines = f.read_text(encoding="utf-8").split("\n")
        hit = 0
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            e = json.loads(line)
            if old not in e.get("v", ""):
                continue
            if key not in src_of(entry=e).lower():   # 절에 따라 원문 칸이 k 또는 es다
                skipped.append((f.name, (e.get("k") or "")[:40], e["v"][:40]))
                continue
            if sweep_skip(f.name):        # 합성 열쇠 파일 — 사람이 직접 고칠 자리
                left.append(f"{f.name}:{i + 1} {e['v'][:60]}")
                continue
            edits.append((f.name, i + 1, e["v"].replace(old, new)))
            hit += 1
        if hit:
            print(f"  {f.name} {hit}행")
            changed += hit
    for ln in left:
        print(f"  건너뜀(추가분·좌표는 직접 고친다) {ln}")
    err = put_lines(edits)
    if err:
        print("멈춤 —", err)
        return
    if skipped:
        print(f"  건너뜀 {len(skipped)}행 — 번역엔 옛 표기가 있으나 원문에 {es!r}가 없어요:")
        for name, k, v in skipped[:8]:
            print(f"    {name} | {k} | {v}")
        if len(skipped) > 8:
            print(f"    … 그 밖 {len(skipped) - 8}행")

    row["ko"] = new
    row["변이"] = sorted(set(row.get("변이", [])) | {old})
    save_ledger(ledger)
    print(f"{changed}행을 {old!r} → {new!r}로 고치고 표기 목록을 갱신했어요 "
          f"(옛 표기는 변이 목록으로 내려갔어요)")
    print("빌드해서 게임에 반영하세요: uv run translate/build.py")


def cmd_add(es, ko, note=""):
    ledger = load_ledger()
    if any(r["es"] == es for r in ledger):
        sys.exit(f"이미 표기 목록에 있어요: {es}")
    ledger.append({"es": es, "ko": ko, "변이": [], "쪽지": note})
    save_ledger(ledger)
    print(f"표기 목록에 올렸어요: {es} → {ko}")


# ── sweep — 표기 목록을 안 보고 정본에서 갈림을 캐낸다 ──────────────────────────
EMPH = re.compile(r"<b>(.*?)</b>", re.S)
TRIM = " \t　.,!?¡¿…·:;~\"'“”‘’「」『』()[]{}*<>/\\"
# 원문 칸이 통째로 이름인 절들 (도구·도구 복수형·트레이너 직함·트레이너 이름·지명·맵 이름)
TABLE_SECTIONS = ("07-items", "08-item-plurals", "13-trainer-classes",
                  "14-trainer-names", "19-place-names", "21-map-names")
MAPS = "00-maps.jsonl"


def norm(s):
    return re.sub(r"\s+", " ", s.strip(TRIM)).strip(TRIM).strip()


def is_name_candidate(es):
    """강조 안 원문이 고유명 후보인가 — 첫 글자가 대문자인 짧은 어구만 본다.

    `<b>` 강조는 이름 말고 문장 강조에도 쓰인다(`<b>no</b>`, `<b>mucho</b>`).
    소문자로 시작하는 것과 긴 어구를 버리면 그 잡음이 대부분 빠진다.
    놓치는 것: 소문자로 시작하는 고유명(목록의 `maese`·`chateau`가 그렇다).
    """
    m = re.search(r"[^\W\d_]", es, re.UNICODE)
    return bool(m) and m.group().isupper() and len(es) <= 30


def _rows(fname):
    f = KO_DIR / fname
    for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            yield n, json.loads(line)


def _best_perm(ks, vs, known):
    """어순이 뒤집힌 자리를 찾는다 — 아는 짝에 덜 어긋나는 배치가 있으면 그것."""
    def bad(order):
        return sum(1 for i, j in enumerate(order)
                   if ks[i] in known and vs[j] not in known[ks[i]])
    ident = tuple(range(len(ks)))
    base = bad(ident)
    if base == 0 or len(ks) > 6:      # 6!=720 — 그 위는 세지 않는다
        return ident, base, base
    best = min(itertools.permutations(ident), key=bad)
    return best, bad(best), base


def sweep_collect():
    """정본에서 (원문, 한국어, 자리) 짝을 캔다. → (짝 목록, 통계, 뒤집힘 후보)"""
    pairs, stats, flipped = [], Counter(), []
    known = defaultdict(set)

    def emit(es, ko, loc, kind):
        pairs.append((es, ko, loc))
        stats[kind] += 1

    for stem in TABLE_SECTIONS:                       # ① 표 절 — 칸 하나가 이름 하나
        for n, e in _rows(stem + ".jsonl"):
            es, ko = norm(src_of(e)), norm(e.get("v", ""))
            if es and ko:
                emit(es, ko, f"{stem}.jsonl:{n}", "표")
                known[es].add(ko)

    rows, mapid = [], None                            # ② 맵 대사의 <b> 강조
    for n, e in _rows(MAPS):
        if "map" in e:
            mapid = e["map"]
            continue
        ks = [norm(x) for x in EMPH.findall(e.get("k", ""))]
        vs = [norm(x) for x in EMPH.findall(e.get("v", ""))]
        if ks or vs:
            rows.append((f"{MAPS}:{n}(맵{mapid})", ks, vs))

    for loc, ks, vs in rows:                          # 강조 하나 = 짝짓기가 자명하다
        if len(ks) == len(vs) == 1 and ks[0] and vs[0]:
            if is_name_candidate(ks[0]):
                emit(ks[0], vs[0], loc, "강조1")
                known[ks[0]].add(vs[0])

    for loc, ks, vs in rows:                          # 강조 여럿 = 순서대로 대응
        if len(ks) < 2:
            continue
        if len(ks) != len(vs):
            stats["짝수 어긋남"] += 1
            flipped.append(("개수", loc, ks, vs, None))
            continue
        order, nbad, base = _best_perm(ks, vs, known)
        if nbad < base:
            stats["어순 뒤집힘"] += 1
            flipped.append(("어순", loc, ks, vs, [vs[j] for j in order]))
        for i, j in enumerate(order):
            if ks[i] and vs[j] and is_name_candidate(ks[i]):
                emit(ks[i], vs[j], loc, "강조N")
    return pairs, stats, flipped


def classify(forms):
    """갈림인가 아닌가 — 짧은 쪽이 긴 쪽들에 통째로 들어 있으면 갈림이 아니다.

    「아조스단/아조스단원」, 「올리비에/올리비에 교수」, 조사가 붙은 「미라가」가
    이 규칙으로 빠진다. 놓치는 것: 접두가 붙은 자리(「옛 바니타스」/「바니타스」는
    포함으로 빠진다)와 어간이 달라진 축약형.
    """
    base = min(forms, key=len)
    return "포함" if all(base in f for f in forms) else "갈림"


def cmd_sweep(argv):
    show_all = "--all" in argv
    tsv = "--tsv" in argv
    pairs, stats, flipped = sweep_collect()
    ledger = {r["es"] for r in load_ledger()}

    by_es = defaultdict(Counter)
    where = {}
    for es, ko, loc in pairs:
        by_es[es][ko] += 1
        where.setdefault((es, ko), loc)

    split = {es: c for es, c in by_es.items() if len(c) > 1}
    buckets = defaultdict(list)
    for es, c in split.items():
        buckets[classify(list(c))].append(es)

    if tsv:
        for es in sorted(split, key=lambda e: -sum(split[e].values())):
            for ko, n in split[es].most_common():
                print(f"{classify(list(split[es]))}\t{es}\t{ko}\t{n}\t{where[(es, ko)]}")
        return 0

    for kind in ("갈림", "포함") if show_all else ("갈림",):
        print(f"\n=== {kind} {len(buckets[kind])}개 " +
              ("(사람이 판정할 자리)" if kind == "갈림" else "(오탐 — 포함관계)"))
        for es in sorted(buckets[kind], key=lambda e: -sum(by_es[e].values())):
            mark = "목록" if es in ledger else "밖"
            print(f"\n[{mark}] {es}")
            for ko, n in by_es[es].most_common():
                print(f"    {n:5d}  {ko:<24} {where[(es, ko)]}")

    if flipped:
        print(f"\n=== 짝짓기 의심 {len(flipped)}자리 (사람이 볼 것)")
        for why, loc, ks, vs, fixed in flipped[:60]:
            print(f"  [{why}] {loc}  {ks} ↔ {vs}" + (f"  ⇒ {fixed}" if fixed else ""))

    print(f"\n원문 {len(by_es)}종 · 짝 {len(pairs)}개 "
          f"({' · '.join(f'{k} {v}' for k, v in sorted(stats.items()))})")
    print(f"갈린 원문 {len(split)}종 — 갈림 {len(buckets['갈림'])} · "
          f"포함(오탐) {len(buckets['포함'])} · "
          f"목록 밖 {sum(1 for e in split if e not in ledger)}")
    return 0


def selftest():
    assert has_batchim("아조스단") is True          # ㄴ 받침
    assert has_batchim("아스테르") is False          # 르 — 받침 없음
    assert has_batchim("사프라") is False
    assert has_batchim("선생") is True
    assert has_batchim("AZ") is None                # 한글이 아니면 판단 보류
    assert has_batchim("로시욘 저택") is True        # 마지막 한글 음절만 본다
    assert has_batchim("아스터 왕") is True

    # sweep 판정 규칙 — 작은 표본으로
    assert EMPH.findall("가 <b>Mirra</b>를") == ["Mirra"]
    assert norm("  Bosque   Errante. ") == "Bosque Errante"
    assert norm("「미라」!") == "미라"
    assert is_name_candidate("Bosque Errante") is True
    assert is_name_candidate("Ruta 2") is True
    assert is_name_candidate("Áster") is True
    assert is_name_candidate("no") is False              # 문장 강조는 소문자
    assert is_name_candidate("2") is False               # 숫자만
    assert is_name_candidate("A" * 31) is False          # 긴 어구는 이름이 아니다
    assert classify(["아조스단", "아조스단원"]) == "포함"
    assert classify(["올리비에", "올리비에 교수"]) == "포함"
    assert classify(["미라", "미라가"]) == "포함"          # 조사
    assert classify(["무사", "총사"]) == "갈림"
    assert classify(["미라", "미르라"]) == "갈림"
    known = {"Mirra": {"미라"}, "Zafra": {"사프라"}}
    assert _best_perm(["Mirra", "Zafra"], ["미라", "사프라"], known)[1:] == (0, 0)
    order, nbad, base = _best_perm(["Mirra", "Zafra"], ["사프라", "미라"], known)
    assert order == (1, 0) and nbad == 0 and base == 2   # 어순 뒤집힘을 잡는다
    print("selftest 통과")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "selftest":
        selftest()
    elif cmd == "sweep":
        sys.exit(cmd_sweep(sys.argv[2:]))
    elif cmd == "check":
        sys.exit(cmd_check())
    elif cmd == "rename" and len(sys.argv) == 4:
        cmd_rename(sys.argv[2], sys.argv[3])
    elif cmd == "add" and len(sys.argv) >= 4:
        cmd_add(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
