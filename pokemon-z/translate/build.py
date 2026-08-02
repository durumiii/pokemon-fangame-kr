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

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/korean.dat")
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/korean.dat")
KO = Path(__file__).with_name("ko")


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def string_to_key(s):
    """게임의 Messages.stringToKey(041_Intl_Messages.rb:367) 재현.

    게임은 조회할 때마다 키를 이렇게 정규화하므로, dat에 담기는 키도 이 모양이
    아니면 영원히 안 맞는다(\r\n 두 글자는 공백 하나로 뭉개진다 — 2026-08-02
    구조 조사 §4-3·4-6). 값은 건드리지 않는다."""
    if re.search(r"[\r\n\t\x01]|^\s+|\s+$|\s{2,}", s):
        s = re.sub(r"^\s+", "", s)
        s = re.sub(r"\s+$", "", s)
        s = re.sub(r"\s{2,}", " ", s)
    return s


def main():
    dry = "--dry-run" in sys.argv
    d = load(open(STORE, "rb"))
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

    print(f"정본과 dat의 값 차이: {changed}곳, 새 키 추가: {added}개")
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
    STORE.write_bytes(out)
    GAME.write_bytes(out)
    print(f"기록 완료: {STORE}\n           {GAME}")


if __name__ == "__main__":
    main()
