# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""번역 정본(ko/) → korean.dat 빌드.

구조(절 수·UserDef 골격·맵 수·목록 길이·키)는 보관소의 현행 korean.dat에서
가져오고, **값만** 정본으로 갈아 끼운다. 정본과 dat의 골격이 어긋나면
(줄 수·키 불일치) 그 자리에서 멈춘다 — 게임 업데이트로 원문이 바뀌면
export.py로 재동기화부터 한다.

왕복 검증 통과 후 보관소·게임 양쪽에 쓴다.

usage: uv run build.py [--dry-run]
"""
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vendor"))
from fanlib import rubywrite  # noqa: E402
from datread import load  # noqa: E402  (딱지를 떼 옛 도구가 그대로 읽는다)
from rubymarshal.reader import load as raw_load  # noqa: E402  왕복 검증은 쓴 모양 그대로 견준다

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/korean.dat")
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/korean.dat")
KO = Path(__file__).with_name("ko")


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def tag_utf8(o):
    """모든 문자열에 UTF-8 인코딩 딱지를 붙인다(마샬 ivar `:E`).

    딱지가 없으면 루비 1.9+ 는 dat의 문자열을 ASCII-8BIT로 읽는다. 그러면
    UTF-8 리터럴과 만나는 자리마다 Encoding::CompatibilityError가 나고,
    번역표 조회는 **비ASCII 표제만** 빗나간다 — ASCII만으로 된 표제는 인코딩이
    달라도 같은 것으로 쳐서 그대로 맞는다. 절23으로 실측하면 표제 6,819개 중
    2,451개(36%)가 빗나가고, 딱지를 붙이면 0개다(루비 3.1.7, 2026-08-07).
    루비 1.8.7 은 딱지를 무시하므로 데스크톱 mkxp-z 구판은 영향이 없다
    — 양쪽 실런타임으로 실측(2026-08-06).
    """
    if isinstance(o, (bytes, bytearray)):
        return bytes(o).decode("utf-8")
    if isinstance(o, list):
        return [tag_utf8(x) for x in o]
    if hasattr(o, "_private_data"):
        inner = load(io.BytesIO(bytes(o._private_data)))
        o._private_data = rubywrite.dumps(tag_utf8(inner))
    return o


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def string_to_key(s):
    """게임의 Messages.stringToKey(041_Intl_Messages.rb:367) 재현.

    루비의 ^/$는 줄 앵커다 — 그래서 \s+$가 \n 앞의 \r만 먹고 \n은 남는다.
    즉 "a\r\nb" → "a\nb"이지 "a b"가 아니다(2026-08-02 밤, 포터블 루비로
    게임 코드 그대로 돌려 실측 — 이전 판의 「공백 하나로 뭉개진다」 가정은
    문자열 앵커로 잘못 읽은 것). 이 구현은 루비 오라클과 실전 키 20,715개
    전량 일치를 확인했다. 값은 건드리지 않는다."""
    if re.search(r"[\r\n\t\x01]|(?m:^\s+|\s+$)|\s{2,}", s):
        s = re.sub(r"(?m)^\s+", "", s)
        s = re.sub(r"(?m)\s+$", "", s)
        s = re.sub(r"\s{2,}", " ", s)
    return s


def main():
    dry = "--dry-run" in sys.argv
    d = load(open(STORE, "rb"))
    # 지난 빌드가 남긴 __kr_patch__ 표식을 떼고 시작한다 — 안 떼면 다음 빌드의
    # 줄 수 검증이 1개 차이로 죽는다(2026-08-04 실사고). 끝에서 다시 심는다.
    keys, values = inner_of(d[23])
    kidx = next((i for i, k in enumerate(keys) if bytes(k) == b"__kr_patch__"), None)
    if kidx is not None:
        keys.pop(kidx); values.pop(kidx)
        d[23]._private_data = rubywrite.dumps([keys, values])
    files = {int(p.name[:2]): p for p in KO.glob("*.jsonl")
             if not p.name.endswith((".add.jsonl", ".loc.jsonl"))}
    # 추가분: 게임 스크립트에는 있는데 korean.dat에 키가 아예 없는 문자열.
    # 해시 절에 새 (키, 값) 쌍으로 덧붙인다. export.py가 본문에 흡수한 뒤에는
    # 이미 있는 키라 건너뛰므로 몇 번을 돌려도 안전하다.
    adds = {int(p.name[:2]): p for p in KO.glob("*.add.jsonl")}
    changed = 0

    # 맵 절 추가분은 줄마다 어느 맵에 붙는지를 `map`으로 들고 다닌다. 전이 뒤 대사가
    # 도착 맵 열쇠로 조회되는 자리(Z-61)를 맵0(전역 폴백)에 얹는 데 쓴다.
    map_adds = {}
    if 0 in adds:
        for r in read_jsonl(adds[0]):
            map_adds.setdefault(r["map"], []).append(r)

    # 좌표 열쇠(Z-73 1단) — 같은 맵 안에서 같은 원문이 자리마다 다른 번역을 받아야 하는
    # 줄을 여기 적는다. 줄 꼴은 {"map","event","cmd","k","v"}이고 k는 00-maps.jsonl의
    # 원문 그대로다. **맵 절의 같은 해시에 열쇠 꼴만 달리해 얹는다** — 새 절을 만들면 절
    # 수가 게임의 MessageTypes 상수와 어긋나고, 절0의 (맵 → 해시) 구조는 그대로 쓸 수
    # 있기 때문이다. 게임 쪽 조립은 share/patch_intl.py의 MessageTypes.krLoc이고,
    # 두 자리의 열쇠 꼴이 한 글자라도 어긋나면 조용히 안 맞는다.
    map_locs = {}
    loc_path = KO / "00-maps.loc.jsonl"
    if loc_path.exists():
        for r in read_jsonl(loc_path):
            key = f"krloc:{r['map']}:{r['event']}:{r['cmd']}|" + string_to_key(r["k"])
            map_locs.setdefault(r["map"], []).append({"k": key, "v": r["v"]})

    for sec, path in sorted(files.items()):
        rows = read_jsonl(path)
        obj = d[sec]
        if sec == 0:
            it = iter(rows)
            for mi, oh in enumerate(obj):
                head = next(it)
                assert head.get("map") == mi, f"{path.name}: 맵 {mi} 헤더가 아니라 {head}"
                keys, values = inner_of(oh)
                # 지난 빌드가 덧붙인 추가분 키는 꼬리에 남는다 — 해시 절의 tail_ok와 같은 꼴.
                tail_ok = {string_to_key(r["k"]).encode("utf-8")
                           for r in map_adds.get(mi, ())}
                tail_ok |= {r["k"].encode("utf-8") for r in map_locs.get(mi, ())}
                strays = [k for k in keys[head["n"]:] if bytes(k) not in tail_ok]
                assert len(keys) >= head["n"] and not strays, \
                    f"맵 {mi}: 줄 수 {head['n']} ≠ dat {len(keys)} (추가분 밖 꼬리 {len(strays)}개)"
                dirty = False
                for j in range(head["n"]):
                    row = next(it)
                    assert row["k"] == keys[j].decode("utf-8", "replace"), \
                        f"맵 {mi}[{j}]: 키 불일치"
                    nv = row["v"].encode("utf-8")
                    if nv != bytes(values[j]):
                        values[j] = nv
                        dirty = True
                        changed += 1
                if dirty:
                    oh._private_data = rubywrite.dumps([keys, values])
            assert next(it, None) is None, f"{path.name}: 남는 줄"
        elif isinstance(obj, list):
            assert len(rows) == len(obj), f"{path.name}: {len(rows)}줄 ≠ dat {len(obj)}"
            for row in rows:
                nv = row["v"].encode("utf-8")
                if nv != bytes(obj[row["i"]]):
                    obj[row["i"]] = nv
                    changed += 1
        else:
            keys, values = inner_of(obj)
            # 지난 빌드가 덧붙인 추가분 키는 꼬리에 남아 있다 — 전부 추가분 소속이면
            # 정상이다(아니면 구조가 어긋난 것). 이 허용이 없으면 제 산출물로 두 번째
            # 빌드가 죽는다(2026-08-09 실사고).
            tail_ok = set()
            if sec in adds:
                tail_ok = {string_to_key(r["k"]).encode("utf-8") for r in read_jsonl(adds[sec])}
            strays = [k for k in keys[len(rows):] if bytes(k) not in tail_ok]
            assert len(keys) >= len(rows) and not strays, \
                f"{path.name}: {len(rows)}줄 ≠ dat {len(keys)} (추가분 밖 꼬리 {len(strays)}개)"
            dirty = False
            for j, row in enumerate(rows):
                assert row["k"] == keys[j].decode("utf-8", "replace"), f"{path.name}[{j}]: 키 불일치"
                nv = row["v"].encode("utf-8")
                if nv != bytes(values[j]):
                    values[j] = nv
                    dirty = True
                    changed += 1
            if dirty:
                obj._private_data = rubywrite.dumps([keys, values])

    added = 0

    def append_rows(oh, rows, folded):
        """해시 껍데기 하나에 (키, 값) 쌍을 덧붙인다. 이미 접힌 키는 base가 이긴다."""
        nonlocal added
        keys, values = inner_of(oh)
        index = {bytes(k): i for i, k in enumerate(keys)}
        for row in rows:
            kb = string_to_key(row["k"]).encode("utf-8")
            nv = row["v"].encode("utf-8")
            if kb in folded:                   # 이미 접힌 키 — base가 이긴다
                continue
            if kb in index:                    # 지난 빌드가 넣은 키 — 값만 따라간다
                if bytes(values[index[kb]]) != nv:
                    values[index[kb]] = nv
                    added += 1
                continue
            index[kb] = len(keys)
            keys.append(kb)
            values.append(nv)
            added += 1
        oh._private_data = rubywrite.dumps([keys, values])

    def map_base_keys():
        """맵마다 정본에 이미 있는 키 — 맵 절 추가분의 folded 몫."""
        it = iter(read_jsonl(files[0]))
        out = {}
        for mi in range(len(d[0])):
            head = next(it)
            out[mi] = {string_to_key(next(it)["k"]).encode("utf-8") for _ in range(head["n"])}
        return out

    for sec, path in sorted(adds.items()):
        # export.py가 base jsonl로 접어 넣은 키는 base가 정본이다 — 추가분은 그 뒤로
        # 손이 안 가 낡으므로, 여기서 값을 따라가면 매 빌드가 정본을 옛 값으로 되돌린다
        # (2026-08-16 실사고: 트레이너 메모 성격 줄이 그렇게 콜론형으로 되살아났다).
        if sec == 0:
            base = map_base_keys()
            for mi, rows in sorted(map_adds.items()):
                append_rows(d[0][mi], rows, base.get(mi, set()))
            continue
        obj = d[sec]
        assert not isinstance(obj, list), f"{path.name}: 추가분은 해시 절에만"
        folded = {string_to_key(r["k"]).encode("utf-8")
                  for r in read_jsonl(files[sec])} if sec in files else set()
        append_rows(obj, read_jsonl(path), folded)

    # 좌표 열쇠는 원문 열쇠와 이름이 겹치지 않으므로 folded가 없다 — 늘 얹는다.
    for mi, loc_rows in sorted(map_locs.items()):
        append_rows(d[0][mi], loc_rows, set())

    # 웹 스튜디오 제보용 버전 표식 — 게임은 이 키를 조회하지 않는다
    from datetime import date
    ver = Path(__file__).with_name("VERSION").read_text(encoding="utf-8").strip()
    stamp = f"{ver}|{date.today()}".encode()
    obj = d[23]
    keys, values = inner_of(obj)
    kb = b"__kr_patch__"
    kidx = next((i for i, k in enumerate(keys) if bytes(k) == kb), None)
    if kidx is None:
        keys.append(kb)
        values.append(stamp)
    else:
        values[kidx] = stamp
    obj._private_data = rubywrite.dumps([keys, values])

    print(f"정본과 dat의 값 차이: {changed}곳, 새 키 추가: {added}개")
    d = tag_utf8(d)
    out = rubywrite.dumps(d)
    r = raw_load(io.BytesIO(out))   # 딱지째 읽는다 — d도 방금 tag_utf8을 거쳤다
    assert len(r) == len(d), "절 수 불일치"
    for sec in range(len(d)):
        if isinstance(d[sec], list):
            assert r[sec] == d[sec], f"절{sec} 왕복 불일치"
        elif hasattr(d[sec], "_private_data"):
            if sec == 0:
                for a, b in zip(r[sec], d[sec]):
                    assert inner_of(a) == inner_of(b), "절0 왕복 불일치"
            else:
                assert inner_of(r[sec]) == inner_of(d[sec]), f"절{sec} 왕복 불일치"
    print(f"왕복 검증 통과 · 산출 {len(out):,} bytes")

    if dry:
        print("dry-run — 파일에 쓰지 않음")
        return
    only = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--out=")), None)
    if only:  # 시험판 — 보관소·게임을 건드리지 않고 한 곳에만 쓴다
        Path(only).write_bytes(out)
        print(f"기록 완료(시험판): {only}")
        return
    STORE.write_bytes(out)
    GAME.write_bytes(out)
    print(f"기록 완료: {STORE}\n           {GAME}")


if __name__ == "__main__":
    main()
