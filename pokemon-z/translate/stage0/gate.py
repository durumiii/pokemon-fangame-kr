# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal", "pyyaml"]
# ///
"""Z-53 검사 게이트 — 자리마다 오라클을 선언하고 검사가 한 자리에서 돈다.

절마다 따로 붙는 검사가 SoT 미완의 증상이었다(Z-69: verify가 24절 중 여덟만 절 지정으로
보고 열셋에는 아무 검사도 없다). 0단계가 섰으니 절 단위가 아니라 여기서 한 번 돈다.

검사 여섯:
  0. overrides — 사람 수정 층이 성립하는가(id 실재 · 칸 이름 · why·by). **FAIL**
  1. refs   — 참조 무결(자리 id 유일 · 값 id 유일 · 모든 ref가 실재 · 고아 값 없음). **FAIL**
  2. src    — 자리의 원문을 오라클(messages.dat)과 대조. 리스트 절은 인덱스별 원문이라
              **번호가 밀리면 여기서 걸린다**(지금 빌드는 길이만 본다) — 이쪽만 **FAIL**.
              해시 절·맵 절은 키 집합을 두 방향으로 세고 집계만 낸다.
  3. pbs    — PBS가 가진 원문이 정본에 다 들어와 있는가(빠진 쪽이 화면에 스페인어로 뜬다).
  4. untr   — 미번역. **기준 둘을 다 센다**(지침 text-pipeline 「미번역 기준 둘」):
              ① 값이 원문과 완전히 같다 ② 한국어가 한 글자도 없다(빈 값 제외).
  6. emit   — 역생성이 지금 translate/ko/와 같은가. overrides 유래가 아닌 차이는 **FAIL** —
              승격 뒤로는 ko가 산출물이라 이 검사가 그 관계를 상시로 지킨다.
  5. div    — 미등재 갈림. 같은 원문인데 통일 참조를 안 가리면서 값이 갈리고 `why`도 없는 자리.
  7. pages  — 페이지 레코드 층의 정합(자리마다 제 페이지가 있고 · 고아 페이지가 없다). **FAIL**
  8. enum   — axes.yaml에 `values`가 선 축의 정본 실물값이 등재 안인가. **FAIL**

종료 코드는 1·2·6·7·8번만 물린다. 4·5번은 묵은 짐이 산더미라 집계만 낸다 — 게이트를 처음부터
빨간불로 만들면 아무도 안 본다.

산출: translate/stage0/findings/*.jsonl (검사별 위반 목록, 재실행 시 덮어씀)

usage: uv run translate/stage0/gate.py [--dir <0단계 디렉터리>] [--quiet] [--selftest]
"""
import contextlib
import io
import json
import re
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    EMPTY_SECS, HASH_SECS, LIST_SECS, MSG_FIELDS, OUT, PAGE_FIELDS, PAGE_ID, ROOT,
    SITE_FIELDS, dump_jsonl, norm, read_jsonl, read_overrides,
)

sys.path.insert(0, str(ROOT.parent / "vendor"))
from datread import load  # noqa: E402

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18")   # probe.py·verify.py와 같은 상수
MSG_DAT = GAME / "Data" / "messages.dat"
PBS = GAME / "PBS"

HANGUL = re.compile(r"[가-힣]")
SEC_ID = re.compile(r"^s(\d+)\.")
MAP_ID = re.compile(r"^m(\d+)\.")
PAGE_OF = re.compile(r"^(m\d+\.e\d+\.p\d+)\.c")     # 자리 id → 그 자리가 놓인 페이지 id

# ── 오라클 선언표 ────────────────────────────────────────────────────────────
# 절마다 (원문 오라클, 값 오라클, 값을 실제로 돌리는 곳). 값 오라클이 없는 절은
# 「사람 몫」으로 이유와 함께 적는다 — 못 보는 것을 못 본다고 적는 것이 게이트의 일부다.
G, V, S, H = "게이트", "verify.py", "canon_sweep.py(수동)", "사람"
ORACLES = {
    0:  ("messages.dat 맵별 키 집합", "사람 몫 — 맵 대사는 기계 오라클이 없다", H),
    1:  ("messages.dat[1] 인덱스", "canon.jsonl(species)", V),
    2:  ("messages.dat[2] 인덱스", "canon/genera.jsonl(종번호)", V),
    3:  ("messages.dat[3] 인덱스", "문장 코퍼스 en 열", S),
    4:  ("messages.dat[4] 인덱스", "사람 몫 — 코퍼스 적중 0/46(팬게임 폼 이름)", H),
    5:  ("messages.dat[5] 인덱스", "canon.jsonl(moves)", V),
    6:  ("messages.dat[6] 인덱스", "문장 코퍼스 es 열", S),
    7:  ("messages.dat[7] 인덱스", "canon.jsonl(items)", V),
    8:  ("messages.dat[8] 인덱스", "사람 몫 — 짧은 낱말이라 코퍼스가 오탐(실측 6건 전부)", H),
    9:  ("messages.dat[9] 인덱스", "문장 코퍼스 es 열", S),
    10: ("messages.dat[10] 인덱스", "canon.jsonl(abilities)", V),
    11: ("messages.dat[11] 인덱스", "문장 코퍼스 es 열", S),
    12: ("messages.dat[12] 인덱스 · PBS/types.txt", "canon.jsonl(types)", V),
    13: ("messages.dat[13] 인덱스 · PBS/trainertypes.txt", "사람 몫 — 클래스명은 창작·음차", H),
    14: ("messages.dat[14] 키 집합 · PBS/trainers.txt", "사람 몫 — 인명 음차", H),
    15: ("대상 없음(0줄) — 전투 대사는 이벤트에 있다", "—", H),
    16: ("대상 없음(0줄)", "—", H),
    17: ("대상 없음(0줄)", "—", H),
    18: ("messages.dat[18] 인덱스", "사람 몫 — 1줄(칼로스), 대조표 밖", H),
    19: ("messages.dat[19] 키 집합 · PBS/townmap.txt", "사람 몫 — 창작 지명", H),
    20: ("messages.dat[20] 키 집합 · PBS/townmap.txt", "사람 몫 — 창작 지명 설명", H),
    21: ("messages.dat[21] 인덱스", "사람 몫 — 창작 지명(맵 이름)", H),
    22: ("messages.dat[22] 키 집합 · PBS/phone.txt", "사람 몫 — 전화 대사", H),
    23: ("messages.dat[23] 키 집합", "리본만 verify.check_ribbons · 나머지 코퍼스 미개척", V),
}
LOC_ORACLE = ("00-maps 정본의 (맵, 원문)", "사람 몫 — 좌표로 가른 맵 대사", V)
UI_ORACLE = ("게임 스크립트 리터럴 — 기계 오라클 없음", "verify.py UI 치환표(오폭 후보)", V)
TOWER_ORACLE = ("게임 TorreBatalla 해시(수술 전 — 값 반영 경로 없음)", "사람 몫 — 음차", H)
SURG_ORACLE = ("게임 스크립트·데이터 리터럴", "patch_intl EDITS(수술 반영)", H)
# 절23 추가분(상점 갈래) — 값은 절23 자리의 선택자 트리라 위 23행이 덮고, 갈래가
# 온전한지(줄 수·배정)는 verify.check_mart가 수술 자리 수를 기준으로 본다.
MART_ORACLE = ("절23 base 키(추가분은 합성 열쇠)", "verify.py check_mart(갈래 줄 수·배정)", V)


def string_to_key(s):
    """게임의 stringToKey 정규화 — build.py 정본(루비 오라클 검증판)과 같은 꼴."""
    if re.search(r"[\r\n\t\x01]|(?m:^\s+|\s+$)|\s{2,}", s):
        s = re.sub(r"(?m)^\s+", "", s)
        s = re.sub(r"(?m)\s+$", "", s)
        s = re.sub(r"\s{2,}", " ", s)
    return s


def dec(b):
    return bytes(b).decode("utf-8", "replace")


def load_oracle():
    """messages.dat → {절: 리스트[원문]} · {절: 키 집합} · {맵: 키 집합}."""
    d = load(open(MSG_DAT, "rb"))

    def inner(oh):
        return load(io.BytesIO(bytes(oh._private_data)))

    lists = {s: [dec(x) for x in d[s]] for s in LIST_SECS}
    hashes = {s: {dec(k) for k in inner(d[s])[0]} for s in HASH_SECS}
    maps = {i: {dec(k) for k in inner(oh)[0]} for i, oh in enumerate(d[0])}
    return lists, hashes, maps


def load_pbs():
    """PBS가 가진 원문 — 절별 집합. 형식이 파일마다 달라 파일마다 한 줄씩 읽는다."""
    out = {}
    tt = (PBS / "trainertypes.txt").read_text(encoding="utf-8-sig").splitlines()
    out[13] = {ln.split(",")[2] for ln in tt if not ln.startswith("#") and ln.count(",") >= 2}
    ty = (PBS / "types.txt").read_text(encoding="utf-8-sig").splitlines()
    out[12] = {ln[5:] for ln in ty if ln.startswith("Name=")}
    tr = (PBS / "trainers.txt").read_text(encoding="utf-8-sig").splitlines()
    # 한 벌은 구분선 뒤로 「내부명 / 이름,번호 / 마릿수 / 포켓몬…」 — 둘째 줄의 앞 칸이 이름.
    # 구분선을 기준으로 세지 않으면 마릿수 줄 뒤의 포켓몬 이름을 이름으로 문다.
    names, n = set(), None
    for ln in tr:
        if ln.startswith("#-"):
            n = 0
        elif n is not None:
            n += 1
            if n == 2:
                names.add(ln.split(",")[0])
    out[14] = names
    pt = re.findall(r'^Point=[^,]*,[^,]*,"([^"]*)","([^"]*)"',
                    (PBS / "townmap.txt").read_text(encoding="utf-8-sig"), re.M)
    out[19] = {a for a, _ in pt if a}
    out[20] = {b for _, b in pt if b}
    ph = (PBS / "phone.txt").read_text(encoding="utf-8-sig").splitlines()
    out[22] = {ln for ln in ph if ln and not ln.startswith("[")}
    return out


# ── 0단계 읽기 ──────────────────────────────────────────────────────────────
def sec_of(sid):
    """자리 id → 절 이름(정렬·집계용)."""
    if sid.startswith("loc."):
        return "loc"
    if sid.startswith("ui."):
        return "ui"
    if sid.startswith("tower."):
        return "tower"
    if sid.startswith("surg."):
        return "surg"
    m = MAP_ID.match(sid)
    if m:
        return "s00"
    m = SEC_ID.match(sid)
    return f"s{int(m.group(1)):02d}" if m else "?"


def resolve(mid, msgs):
    """참조를 따라 (끝 id, 문자열 값, 어느 고리에든 why가 있었나)까지 간다."""
    why, seen = False, []
    while True:
        m = msgs[mid]
        why = why or ("why" in m)
        v = m["val"]
        if isinstance(v, dict) and "sel" in v:
            return mid, v["default"], why   # 갈래 값은 추가분 파일 몫이라 기본 갈래만 본다
        if not (isinstance(v, dict) and "ref" in v):
            return mid, v, why
        assert v["ref"] not in seen, f"참조 순환: {mid}"
        seen.append(mid)
        mid = v["ref"]


# ── 검사 다섯 ───────────────────────────────────────────────────────────────
def check_refs(sites, msgs):
    bad = []
    sids, mids = [s["id"] for s in sites], [m["id"] for m in msgs]
    for label, ids in (("site", sids), ("message", mids)):
        seen = set()
        for i in ids:
            if i in seen:
                bad.append({"kind": f"{label}-id 중복", "id": i})
            seen.add(i)
    mset, sset = set(mids), set(sids)
    by_id = {m["id"]: m for m in msgs}
    for sid in sids:
        if sid not in mset:
            bad.append({"kind": "자리에 값이 없다", "id": sid})
    referenced = set()
    for m in msgs:
        v = m["val"]
        if isinstance(v, dict) and "ref" in v:
            referenced.add(v["ref"])
            if v["ref"] not in mset:
                bad.append({"kind": "ref가 없는 값을 가리킨다", "id": m["id"], "ref": v["ref"]})
    for m in msgs:
        if m["id"] not in sset and m["id"] not in referenced:
            bad.append({"kind": "고아 값(자리도 참조도 없다)", "id": m["id"]})
    for sid in sids:
        if sid in by_id:
            try:
                _, val, _ = resolve(sid, by_id)
            except (AssertionError, KeyError) as e:
                bad.append({"kind": "참조 해소 실패", "id": sid, "detail": str(e)})
                continue
            if not isinstance(val, str):
                bad.append({"kind": "값이 문자열이 아니다", "id": sid})
    return bad


def check_overrides(ovr, sites, msgs, pages):
    """사람 수정 층이 성립하는가 — id 실재 · 칸 이름 · 유래(why·by).

    overrides는 gen이 지우지 않는 유일한 사람 손이라 여기서 안 걸리면 조용히 안 먹는다.
    페이지 id(`m*.e*.p*`)는 페이지 표로 가고 칸도 페이지 스키마로 본다 — layer가 자리
    스키마와 이름이 겹쳐 칸 이름만으로는 못 가른다(common.apply_overrides와 같은 규칙).
    """
    bad = []
    sset, mset = {s["id"] for s in sites}, {m["id"] for m in msgs}
    pset = {p["id"] for p in pages}
    for n, o in enumerate(ovr):
        where = {"줄": n + 1, "id": o.get("id")}
        if not o.get("id"):
            bad.append({**where, "kind": "id가 없다"})
            continue
        st = o.get("set")
        if not isinstance(st, dict) or not st:
            bad.append({**where, "kind": "set이 비었다"})
            continue
        for k in st:
            if PAGE_ID.match(o["id"]):
                if k not in PAGE_FIELDS:
                    bad.append({**where, "kind": "페이지 스키마에 없는 칸", "칸": k})
                elif o["id"] not in pset:
                    bad.append({**where, "kind": "실재하지 않는 페이지 id", "칸": k})
            elif k in SITE_FIELDS:
                if o["id"] not in sset:
                    bad.append({**where, "kind": "실재하지 않는 자리 id", "칸": k})
            elif k in MSG_FIELDS:
                if o["id"] not in mset:
                    bad.append({**where, "kind": "실재하지 않는 값 id", "칸": k})
            else:
                bad.append({**where, "kind": "스키마에 없는 칸", "칸": k})
        for f in ("why", "by"):
            if not o.get(f):
                bad.append({**where, "kind": f"{f}가 없다"})
    return bad


def check_src(sites, lists, hashes, maps):
    """자리의 원문을 오라클과 대조 — 번호 밀림과 키 어긋남이 여기서 걸린다.

    두 방향을 나눠 본다. 정본→오라클(「오라클 밖」)은 정본이 더 담은 자리라 대개 무해하고,
    오라클→정본(`miss`)은 **게임이 찾는 키를 정본이 안 가진 자리**라 화면에 스페인어가
    그대로 뜬다. 뒤쪽이 실제 위험이다(지침 text-pipeline 「미번역이 남았다」).
    """
    bad, stat = [], {}
    have = {}
    for s in sites:
        if s["apply"] == "global":
            have.setdefault(int(SEC_ID.match(s["id"]).group(1)),
                            set()).add(string_to_key(s["src"]))
        elif s["apply"] == "map":
            have.setdefault(f"m{MAP_ID.match(s['id']).group(1)}",
                            set()).add(string_to_key(s["src"]))
    miss = [{"kind": "오라클에만 있는 원문(정본에 없다)", "절": sec, "src": k}
            for sec, ks in sorted(hashes.items())
            for k in sorted(ks) if k not in have.get(sec, ())]
    miss += [{"kind": "오라클에만 있는 원문(정본에 없다)", "맵": mi, "src": k}
             for mi, ks in sorted(maps.items())
             for k in sorted(ks) if k not in have.get(f"m{mi}", ())]
    for s in sites:
        sec = sec_of(s["id"])
        st = stat.setdefault(sec, {"일치": 0, "어긋남": 0, "원문없음": 0, "오라클밖": 0})
        src = s.get("src")
        if s["apply"] == "index":
            i = int(s["id"].split(".i")[1])
            want = lists[int(SEC_ID.match(s["id"]).group(1))]
            if i >= len(want):
                st["어긋남"] += 1
                bad.append({"kind": "인덱스가 오라클 길이를 넘는다", "id": s["id"]})
            elif src is None:
                st["원문없음" if not want[i] else "오라클밖"] += 1
            elif src == want[i]:
                st["일치"] += 1
            else:
                st["어긋남"] += 1
                bad.append({"kind": "번호 밀림(인덱스의 원문이 오라클과 다르다)",
                            "id": s["id"], "정본": src, "오라클": want[i]})
        elif s["apply"] == "global":
            keys = hashes[int(SEC_ID.match(s["id"]).group(1))]
            st["일치" if string_to_key(src) in keys else "오라클밖"] += 1
        elif s["apply"] == "map":
            mi = int(MAP_ID.match(s["id"]).group(1))
            st["일치" if string_to_key(src) in maps.get(mi, ()) else "오라클밖"] += 1
        else:
            st["오라클밖"] += 1
    return bad, miss, stat


def check_pbs(sites, pbs, lists, hashes):
    """PBS에만 있고 정본에도 dat에도 없는 원문 — 그 자리는 화면에 스페인어가 그대로 뜬다.

    정본이 `es`를 안 적어 둔 줄이 있어(절12 i=9 · 절13 i=121) 자리의 src만 보면 오탐이
    난다. dat 오라클의 원문을 함께 친다 — 원문 미기재 자체는 src 검사가 따로 센다.
    """
    have = {s: {string_to_key(x) for x in xs if x} for s, xs in lists.items()}
    for s, ks in hashes.items():
        have.setdefault(s, set()).update(string_to_key(k) for k in ks)
    for s in sites:
        m = SEC_ID.match(s["id"])
        if m and s.get("src"):
            have.setdefault(int(m.group(1)), set()).add(string_to_key(s["src"]))
    bad, stat = [], {}
    for sec, want in sorted(pbs.items()):
        got = have.get(sec, set())
        miss = sorted(w for w in want if string_to_key(w) not in got)
        stat[sec] = (len(want), len(miss))
        bad += [{"kind": "PBS에만 있는 원문", "절": sec, "src": w} for w in miss]
    return bad, stat


def check_untr(sites, msgs):
    """미번역 두 기준 — ① 값=원문 ② 한글 무포함(빈 값 제외). 빈 값은 따로 센다."""
    by_id = {m["id"]: m for m in msgs}
    bad, stat = [], {}
    for s in sites:
        sec = sec_of(s["id"])
        st = stat.setdefault(sec, {"자리": 0, "값=원문": 0, "한글무포함": 0, "빈값": 0})
        st["자리"] += 1
        _, val, _ = resolve(s["id"], by_id)
        src = s.get("src")
        same = src is not None and val == src
        noko = bool(val) and not HANGUL.search(val)
        if not val:
            st["빈값"] += 1
        if same:
            st["값=원문"] += 1
        if noko:
            st["한글무포함"] += 1
        if same or noko:
            bad.append({"id": s["id"], "절": sec, "값=원문": same, "한글무포함": noko,
                        "src": src, "val": val})
    return bad, stat


def check_emit(d):
    """역생성 ↔ 현행 ko — (그 밖 차이 수, overrides 유래 수, 파일별 차이 목록).

    계산은 diff.py 것을 그대로 부른다(대조 로직 두 벌 금지). compare가 절마다
    찍는 것은 게이트 출력에 안 어울려 삼키고 수만 받는다.
    """
    sys.path.insert(0, str(ROOT / "stage0"))
    from diff import compare, rebuild, tainted_ids
    import emit

    built, owner, msgs = rebuild(d)
    tainted = tainted_ids(msgs, read_overrides(d / "overrides.jsonl"))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        from_ovr, other = compare(built, owner, tainted, show=0)
    rows = [{"kind": "emit 차이", "줄": ln} for ln in buf.getvalue().splitlines()
            if ln.startswith("차이")]
    return other, from_ovr, rows, emit


def check_div(sites, msgs):
    """미등재 갈림 — 같은 원문인데 통일 참조를 안 가리면서 값이 갈리고 why도 없다."""
    by_id = {m["id"]: m for m in msgs}
    groups = {}
    for s in sites:
        if s["apply"] != "map":
            continue
        end, val, why = resolve(s["id"], by_id)
        mi = int(MAP_ID.match(s["id"]).group(1))
        groups.setdefault(norm(s["src"]), []).append((mi, val, why, end, s["id"]))
    bad = 0
    rows = []
    for k, g in groups.items():
        maps = sorted({m for m, *_ in g})
        vals = {v for _, v, *_ in g}
        if len(maps) <= 1 or len(vals) <= 1:
            continue
        if any(end.startswith("unified.") for *_, end, _ in g):
            continue          # 통일 참조 — 갈림이 아니다
        if any(why for _, _, why, _, _ in g):
            continue          # 갈림 허용(why가 붙어 있다)
        bad += 1
        rows.append({"kind": "미등재 갈림", "src": k[:120], "maps": maps,
                     "값": sorted(vals)[:6], "자리": sorted(x[4] for x in g)[:6]})
    return rows, bad, len(groups)


def check_pages(sites, pages):
    """페이지 레코드 층의 정합 — 자리마다 제 페이지가 있고, 대응 자리 없는 페이지가 없다.

    층·장면이 페이지로 올라간 뒤로 이 대응이 끊기면 조회가 조용히 빈 값을 준다.
    """
    bad, have, seen = [], set(), set()
    for p in pages:
        if p["id"] in have:
            bad.append({"kind": "page-id 중복", "id": p["id"]})
        have.add(p["id"])
    for s in sites:
        m = PAGE_OF.match(s["id"])
        if not m:
            continue
        seen.add(m.group(1))
        if m.group(1) not in have:
            bad.append({"kind": "자리의 페이지가 pages에 없다", "id": s["id"],
                        "페이지": m.group(1)})
    bad += [{"kind": "고아 페이지(대응 자리가 없다)", "id": p} for p in sorted(have - seen)]
    return bad, len(seen)


def check_enum(axes, tables):
    """등재제 축 — `values`와 `from`이 함께 선 축의 정본 실물값이 등재 안인가.

    선언만 있고 검사가 없어 kind 등재가 실물과 어긋난 채 오래 살았다(Z-53 설계 4절).
    """
    bad = []
    for name, ax in sorted(axes.get("axes", {}).items()):
        vals, frm = ax.get("values"), ax.get("from")
        if not vals or not frm:
            continue
        tbl, _, field = frm.partition(".")
        if tbl not in tables:
            bad.append({"kind": "축이 없는 표를 가리킨다", "축": name, "from": frm})
            continue
        for r in tables[tbl]:
            v = r.get(field)
            if v is not None and v not in vals:
                bad.append({"kind": "등재 밖 값", "축": name, "from": frm,
                            "id": r["id"], "값": v})
    return bad


# ── 보고 ────────────────────────────────────────────────────────────────────
def print_table():
    print("오라클 선언표 — 절마다 「무엇으로 대조하는가」와 「누가 돌리는가」")
    print(f"  {'절':<4} {'원문 오라클':<42} {'값 오라클':<46} 돌리는 곳")
    for sec in range(24):
        so, vo, who = ORACLES[sec]
        print(f"  {sec:02d}   {so:<42} {vo:<46} {who}")
    for label, (so, vo, who) in (("loc", LOC_ORACLE), ("ui", UI_ORACLE),
                                 ("tower", TOWER_ORACLE), ("surg", SURG_ORACLE),
                                 ("mart", MART_ORACLE)):
        print(f"  {label:<6}{so:<40} {vo:<46} {who}")
    human = sorted(s for s in ORACLES if ORACLES[s][2] == H and s not in EMPTY_SECS)
    print(f"\n  값이 사람 몫인 절: {human} (빈 절 {EMPTY_SECS}는 대상 없음)")


def selftest(sites, lists, hashes, maps):
    """번호 밀림 검출이 실제로 도는지 — 자리 셋의 원문을 메모리에서만 돌려 본다.

    실제 위반이 0이라 검사가 도는지 아닌지가 통과만으로는 구분이 안 된다. 정본은
    건드리지 않는다(사본을 만들어 check_src에만 먹인다).
    """
    ids = ["s5.i1", "s5.i2", "s5.i3"]
    by_id = {s["id"]: s for s in sites}
    srcs = [by_id[i]["src"] for i in ids]
    shifted = [dict(s, src=srcs[(ids.index(s["id"]) + 1) % 3]) if s["id"] in ids else s
               for s in sites]
    bad, _, _ = check_src(shifted, lists, hashes, maps)
    assert len(bad) == 3, f"번호를 밀었는데 검출이 {len(bad)}건이다"
    assert all("번호 밀림" in b["kind"] for b in bad), bad
    print(f"selftest: 절05 자리 셋의 원문을 한 칸 밀자 {len(bad)}건 검출 — 번호 밀림 검사가 산다")
    print(f"          {bad[0]['id']}: 정본 {bad[0]['정본']!r} ≠ 오라클 {bad[0]['오라클']!r}")
    selftest_emit()


def selftest_emit():
    """emit 검사가 사는가 — 0단계 사본의 값 하나를 갈아 차이가 잡히는지 본다.

    정본을 건드리지 않으려고 임시 폴더에 sites·messages·axes·overrides를 복사해 돌린다.
    ko는 진짜 자리를 보므로(compare가 KO를 읽는다) 값을 갈면 그 줄만 차이로 선다.
    """
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for n in ("sites.jsonl", "messages.jsonl", "pages.jsonl", "axes.yaml", "layout.yaml"):
            shutil.copy(OUT / n, td / n)
        rows = read_jsonl(td / "messages.jsonl")
        i = next(i for i, m in enumerate(rows) if isinstance(m["val"], str) and m["val"])
        rows[i] = {**rows[i], "val": rows[i]["val"] + "(셀프테스트)"}
        dump_jsonl(td / "messages.jsonl", rows)
        other, from_ovr, _, _ = check_emit(td)
    assert other >= 1, f"값을 갈았는데 emit 차이가 {other}건이다"
    print(f"selftest: 0단계 사본의 값 한 줄을 갈자 emit 차이 {other}건 — emit 검사가 산다")


def main():
    argv = sys.argv[1:]
    d = Path(argv[argv.index("--dir") + 1]) if "--dir" in argv else OUT
    quiet = "--quiet" in argv
    findings = d / "findings"
    findings.mkdir(exist_ok=True)

    sites = read_jsonl(d / "sites.jsonl")
    msgs = read_jsonl(d / "messages.jsonl")
    pages = read_jsonl(d / "pages.jsonl")
    if not quiet:
        print_table()
    print(f"\n0단계: {d} — 자리 {len(sites):,} · 값 {len(msgs):,} · 페이지 {len(pages):,}\n")

    ovr = read_overrides(d / "overrides.jsonl")
    ovr_bad = check_overrides(ovr, sites, msgs, pages)
    dump_jsonl(findings / "overrides.jsonl", ovr_bad)
    print(f"[{'FAIL' if ovr_bad else ' OK '}] 0. overrides 사람 수정 층 — "
          f"{len(ovr):,}줄 중 위반 {len(ovr_bad)}건")
    for r in ovr_bad[:5]:
        print(f"        {r}")

    refs = check_refs(sites, msgs)
    dump_jsonl(findings / "refs.jsonl", refs)
    print(f"[{'FAIL' if refs else ' OK '}] 1. refs 참조 무결 — 위반 {len(refs)}건")
    for r in refs[:5]:
        print(f"        {r}")

    lists, hashes, maps = load_oracle()
    src_bad, src_miss, src_stat = check_src(sites, lists, hashes, maps)
    dump_jsonl(findings / "src.jsonl", src_bad + src_miss)
    print(f"[{'FAIL' if src_bad else ' OK '}] 2. src 오라클 대조 — 번호 밀림 {len(src_bad)}건 · "
          f"오라클에만 있는 원문 {len(src_miss)}건(집계)")
    for r in src_bad[:5]:
        print(f"        {r['kind']} {r['id']}: 정본 {r.get('정본','')!r} ≠ "
              f"오라클 {r.get('오라클','')!r}")
    for r in src_miss[:5]:
        print(f"        {r['kind']} {r.get('절', r.get('맵'))}: {r['src'][:70]!r}")
    if "--selftest" in argv:
        selftest(sites, lists, hashes, maps)
    if not quiet:
        for sec in sorted(src_stat):
            st = src_stat[sec]
            print(f"        {sec}: 일치 {st['일치']:,} · 어긋남 {st['어긋남']} · "
                  f"원문없음(오라클도 빔) {st['원문없음']:,} · 오라클 밖 {st['오라클밖']:,}")

    pbs_bad, pbs_stat = check_pbs(sites, load_pbs(), lists, hashes)
    dump_jsonl(findings / "pbs.jsonl", pbs_bad)
    print(f"[집계] 3. PBS 원문 커버리지 — 정본에 없는 원문 {len(pbs_bad)}건")
    for sec, (n, miss) in sorted(pbs_stat.items()):
        print(f"        절{sec:02d}: PBS {n}개 중 정본에 없음 {miss}")

    untr, untr_stat = check_untr(sites, msgs)
    dump_jsonl(findings / "untranslated.jsonl", untr)
    tot_same = sum(s["값=원문"] for s in untr_stat.values())
    tot_noko = sum(s["한글무포함"] for s in untr_stat.values())
    print(f"[집계] 4. 미번역 — 기준① 값=원문 {tot_same:,} · 기준② 한글 무포함 {tot_noko:,} "
          f"(빈 값 제외)")
    for sec in sorted(untr_stat):
        st = untr_stat[sec]
        if st["값=원문"] or st["한글무포함"] or st["빈값"]:
            print(f"        {sec}: 자리 {st['자리']:,} · 값=원문 {st['값=원문']:,} · "
                  f"한글무포함 {st['한글무포함']:,} · 빈값 {st['빈값']:,}")

    div_rows, div_bad, div_groups = check_div(sites, msgs)
    dump_jsonl(findings / "divergence.jsonl", div_rows)
    print(f"[집계] 5. 미등재 갈림 — {div_bad}건 (맵 절 원문 묶음 {div_groups:,}개 중)")
    for r in div_rows[:5]:
        print(f"        {r['src'][:60]!r} 맵 {r['maps'][:6]} 값 {r['값'][:2]}")

    pg_bad, pg_used = check_pages(sites, pages)
    dump_jsonl(findings / "pages.jsonl", pg_bad)
    print(f"[{'FAIL' if pg_bad else ' OK '}] 7. pages 정합 — 페이지 {len(pages):,} · "
          f"자리가 가리키는 페이지 {pg_used:,} · 위반 {len(pg_bad)}건")
    for r in pg_bad[:5]:
        print(f"        {r}")

    axes = yaml.safe_load((d / "axes.yaml").read_text(encoding="utf-8"))
    enum_bad = check_enum(axes, {"sites": sites, "messages": msgs, "pages": pages})
    dump_jsonl(findings / "enum.jsonl", enum_bad)
    declared = [k for k, v in axes.get("axes", {}).items() if v.get("values")]
    print(f"[{'FAIL' if enum_bad else ' OK '}] 8. 축 등재 — values가 선 축 {declared} · "
          f"등재 밖 값 {len(enum_bad)}건")
    for r in enum_bad[:5]:
        print(f"        {r}")

    t0 = time.time()
    emit_other, emit_ovr, emit_rows, emit_mod = check_emit(d)
    dump_jsonl(findings / "emit.jsonl", emit_rows)
    print(f"[{'FAIL' if emit_other else ' OK '}] 6. emit 차이 — 그 밖 {emit_other}건 · "
          f"overrides 유래 {emit_ovr}건 ({time.time() - t0:.1f}초)")
    for r in emit_rows[:5]:
        print(f"        {r['줄']}")
    if emit_other:
        print(f"        {emit_mod.advice()}")

    print(f"\n산출: {findings}/"
          f"{{overrides,refs,src,pbs,untranslated,divergence,pages,enum,emit}}.jsonl")
    return 1 if (ovr_bad or refs or src_bad or pg_bad or enum_bad or emit_other) else 0


if __name__ == "__main__":
    sys.exit(main())
