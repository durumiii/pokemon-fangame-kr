# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""dat에 손으로 넣은 수정을 정본(ko/)으로 회수한다 — 손댄 자리만 골라서.

    uv run translate/harvest.py                 # 무엇이 돌아오는지 보여만 준다
    uv run translate/harvest.py --write         # 정본에 반영
    uv run translate/harvest.py --from <dat>    # 회수할 dat (기본: 게임 폴더)
    uv run translate/harvest.py --base <dat>    # 기준선 (기본: 모드 폴더 = 마지막 배포본)

⚠ **`export.py`와 다르다.** export는 dat를 통째로 정본에 덮는 재동기화 도구라,
회수 대상 dat가 마지막 빌드 시점에 멈춰 있으면 그 뒤 정본이 받은 수정을 되돌린다
(2026-08-08 실측: 282행이 옛 값으로 돌아갔다).

이 도구는 **기준선·dat·정본 셋을 함께 본다**:

| 기준선 → dat | 정본 | 판정 |
|---|---|---|
| 바뀜 | 기준선 그대로 | **회수** — dat에서만 고친 자리다 |
| 바뀜 | dat와 같음 | 이미 반영 |
| 바뀜 | 둘 다와 다름 | **충돌** — 정본이 그 뒤 따로 움직였다. 손대지 않고 알린다 |

기준선은 「그 dat를 만들어 낸 배포본」이다. 게임 폴더의 dat를 회수한다면 그것을
설치한 모드 폴더의 dat가 기준선이다.

빈 값으로 바뀐 자리는 실수일 수 있어 건드리지 않고 알린다.
"""
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from datread import load  # noqa: E402

KO = HERE / "ko"
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/korean.dat")
STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/korean.dat")

# 정본 파일 이름 앞 두 자리가 절 번호다
SEC_FILE = {int(p.name[:2]): p for p in sorted(KO.glob("*.jsonl"))
            if p.name[:2].isdigit() and not p.name.endswith(".add.jsonl")}


def decide(was, got, canon):
    """기준선·dat·정본 셋을 견주어 이 자리를 어떻게 할지 — 이 도구의 전부다."""
    if got == was:      return "무변"      # dat에서 손대지 않았다
    if canon == got:    return "이미"      # 정본에 벌써 들어와 있다
    if canon != was:    return "충돌"      # 정본이 그 뒤 따로 움직였다
    if not got.strip(): return "빈값"      # 지운 것은 실수일 수 있다
    return "회수"


def selftest():
    assert decide("옛", "옛", "옛") == "무변"
    assert decide("옛", "새", "옛") == "회수"
    assert decide("옛", "새", "새") == "이미"
    assert decide("옛", "새", "딴것") == "충돌"      # 정본이 먼저 움직였으면 손대지 않는다
    assert decide("옛", "", "옛") == "빈값"
    assert decide("옛", "  ", "옛") == "빈값"
    assert decide("옛", "새", "새") == "이미"
    print("selftest OK")


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def dat_values(path):
    """dat → {(절, 맵, 자리): 값}. 맵 대사가 아니면 맵은 None."""
    d = load(open(path, "rb"))
    out = {}
    for sec in range(len(d)):
        obj = d[sec]
        if sec == 0:
            for mi, oh in enumerate(obj):
                _, values = inner_of(oh)
                for j, v in enumerate(values):
                    out[(0, mi, j)] = bytes(v).decode("utf-8", "replace")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                out[(sec, None, i)] = bytes(v).decode("utf-8", "replace")
        elif hasattr(obj, "_private_data"):
            keys, values = inner_of(obj)
            for j, (k, v) in enumerate(zip(keys, values)):
                if bytes(k) == b"__kr_patch__":      # build.py가 심는 판 표식
                    continue
                out[(sec, None, j)] = bytes(v).decode("utf-8", "replace")
    return out


def canon_rows(sec):
    """정본 파일의 (자리 → 줄 번호). 맵 대사는 (맵, 자리)."""
    path = SEC_FILE.get(sec)
    if not path:
        return None, None
    lines = path.read_text(encoding="utf-8").splitlines()
    pos, cur, i = {}, None, 0
    for ln, line in enumerate(lines):
        r = json.loads(line)
        if sec == 0 and "map" in r and "n" in r:
            cur = r["map"]; i = 0; continue
        pos[(cur, i) if sec == 0 else (None, r["i"] if "i" in r else i)] = ln
        i += 1
    return lines, pos


def put_lines(edits):
    """0단계 정본에 앉히고 ko를 역생성한다 — 창구는 stage0/edit.py 하나다."""
    sys.path.insert(0, str(HERE / "stage0"))
    from edit import put_lines as _put
    return _put(edits)


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest()
    opt = lambda name, default: Path(args[args.index(name) + 1]) if name in args else default
    src, base = opt("--from", GAME), opt("--base", STORE)
    write = "--write" in args

    got, ref = dat_values(src), dat_values(base)
    touched = {k: v for k, v in got.items() if k in ref and ref[k] != v}
    print(f"회수 대상 {src}\n기준선   {base}\n손댄 자리 {len(touched)}개")

    by_sec, blank, clash = {}, [], []
    for (sec, mi, j), v in touched.items():
        by_sec.setdefault(sec, []).append(((mi, j), v))

    total, already, edits = 0, 0, []
    for sec, items in sorted(by_sec.items()):
        lines, pos = canon_rows(sec)
        if lines is None:
            print(f"  ⚠ 절{sec}: 정본 파일이 없어 건너뜀 ({len(items)}자리)")
            continue
        n = 0
        for key, v in items:
            ln = pos.get(key)
            if ln is None:
                print(f"  ⚠ 절{sec} {key}: 정본에서 자리를 못 찾음")
                continue
            r = json.loads(lines[ln])
            was = ref[(sec, key[0], key[1])]
            verdict = decide(was, v, r["v"])
            if verdict == "이미":
                already += 1
                continue
            if verdict == "충돌":
                clash.append((sec, key, was, v, r["v"]))
                continue
            if verdict == "빈값":
                blank.append((sec, key, r["v"]))
                continue
            edits.append((SEC_FILE[sec].name, ln + 1, v))
            n += 1
        if n:
            print(f"  {SEC_FILE[sec].name}: {n}행")
        total += n

    if write:
        err = put_lines(edits)
        if err:
            print("멈춤 —", err)
            return
    print(f"\n회수 {total}행 · 이미 정본에 있던 것 {already}행 · 충돌 {len(clash)}행")
    for sec, key, was, v, cur in clash:
        print(f"  ⚠ 충돌 절{sec} {key} — 손대지 않았어요\n"
              f"      기준선: {was!r}\n      dat:    {v!r}\n      정본:   {cur!r}")
    for sec, key, old in blank:
        print(f"  ⚠ 빈 값이라 건드리지 않음 — 절{sec} {key} (정본: {old!r})")
    if not write:
        print("\n(미리보기입니다 — 반영하려면 --write)")


if __name__ == "__main__":
    main()
