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
from rubymarshal.reader import load  # noqa: E402

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
             if not p.name.endswith(".add.jsonl")}
    # 추가분: 게임 스크립트에는 있는데 korean.dat에 키가 아예 없는 문자열.
    # 해시 절에 새 (키, 값) 쌍으로 덧붙인다. export.py가 본문에 흡수한 뒤에는
    # 이미 있는 키라 건너뛰므로 몇 번을 돌려도 안전하다.
    adds = {int(p.name[:2]): p for p in KO.glob("*.add.jsonl")}
    changed = 0

    for sec, path in sorted(files.items()):
        rows = read_jsonl(path)
        obj = d[sec]
        if sec == 0:
            it = iter(rows)
            for mi, oh in enumerate(obj):
                head = next(it)
                assert head.get("map") == mi, f"{path.name}: 맵 {mi} 헤더가 아니라 {head}"
                keys, values = inner_of(oh)
                assert head["n"] == len(keys), f"맵 {mi}: 줄 수 {head['n']} ≠ dat {len(keys)}"
                dirty = False
                for j in range(len(keys)):
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
            assert len(rows) == len(keys), f"{path.name}: {len(rows)}줄 ≠ dat {len(keys)}"
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
    for sec, path in sorted(adds.items()):
        obj = d[sec]
        assert not isinstance(obj, list) and sec != 0, f"{path.name}: 추가분은 해시 절에만"
        keys, values = inner_of(obj)
        existing = {bytes(k) for k in keys}
        for row in read_jsonl(path):
            kb = string_to_key(row["k"]).encode("utf-8")
            if kb in existing:
                continue
            existing.add(kb)
            keys.append(kb)
            values.append(row["v"].encode("utf-8"))
            added += 1
        obj._private_data = rubywrite.dumps([keys, values])

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
    r = load(io.BytesIO(out))
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
