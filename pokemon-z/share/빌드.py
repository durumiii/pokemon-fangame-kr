"""번역표(JSONL) → korean.dat 빌드 — 패키지 동봉 독립판.

번역표의 문장을 고친 뒤 이 스크립트를 돌리면 ../Data/korean.dat가 다시
만들어집니다. 원본은 korean.dat.bak으로 남습니다.

필요한 것: Python 3.10+ 와 rubymarshal 패키지.
    pip install rubymarshal
실행 (번역표 폴더 안에서):
    python 빌드.py                # 패키지의 Data/korean.dat 갱신
    python 빌드.py "C:/게임 폴더"  # 게임의 Data/korean.dat에 바로 쓰기

주의: 원문(k) 줄과 줄 순서는 건드리지 말고 번역(v)만 고치세요 — 골격이
어긋나면 빌드가 그 자리에서 멈춥니다.
"""
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import rubywrite  # noqa: E402  (동봉본)

try:
    from rubymarshal.reader import load
except ImportError:
    sys.exit("rubymarshal 패키지가 필요합니다:  pip install rubymarshal")

HERE = Path(__file__).parent


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def string_to_key(s):
    # 게임이 조회 키를 이렇게 정규화하므로 새 키도 이 모양이어야 한다
    if re.search(r"[\r\n\t\x01]|^\s+|\s+$|\s{2,}", s):
        s = re.sub(r"^\s+", "", s)
        s = re.sub(r"\s+$", "", s)
        s = re.sub(r"\s{2,}", " ", s)
    return s


def main():
    if len(sys.argv) > 1:
        dat = Path(sys.argv[1]) / "Data" / "korean.dat"
    else:
        dat = HERE.parent / "Data" / "korean.dat"
    if not dat.is_file():
        sys.exit(f"korean.dat를 못 찾았습니다: {dat}")

    d = load(open(dat, "rb"))
    files = {int(p.name[:2]): p for p in HERE.glob("*.jsonl")
             if not p.name.endswith(".add.jsonl")}
    adds = {int(p.name[:2]): p for p in HERE.glob("*.add.jsonl")}
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
                assert head["n"] == len(keys), f"맵 {mi}: 줄 수 불일치 — 번역표를 고칠 때 줄을 지우거나 더하지 마세요"
                dirty = False
                for j in range(len(keys)):
                    row = next(it)
                    assert row["k"] == keys[j].decode("utf-8", "replace"), \
                        f"맵 {mi}[{j}]: 원문(k)이 dat와 다릅니다 — k 줄은 고치면 안 됩니다"
                    nv = row["v"].encode("utf-8")
                    if nv != bytes(values[j]):
                        values[j] = nv
                        dirty = True
                        changed += 1
                if dirty:
                    oh._private_data = rubywrite.dumps([keys, values])
            assert next(it, None) is None, f"{path.name}: 남는 줄"
        elif isinstance(obj, list):
            assert len(rows) == len(obj), f"{path.name}: 줄 수 불일치"
            for row in rows:
                nv = row["v"].encode("utf-8")
                if nv != bytes(obj[row["i"]]):
                    obj[row["i"]] = nv
                    changed += 1
        else:
            keys, values = inner_of(obj)
            assert len(rows) == len(keys), f"{path.name}: 줄 수 불일치"
            dirty = False
            for j, row in enumerate(rows):
                assert row["k"] == keys[j].decode("utf-8", "replace"), \
                    f"{path.name}[{j}]: 원문(k)이 dat와 다릅니다"
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

    out = rubywrite.dumps(d)
    r = load(io.BytesIO(out))
    assert len(r) == len(d), "왕복 검증 실패 — 결과를 쓰지 않았습니다"
    print(f"바뀐 문장 {changed}곳, 새 키 {added}개 · 검증 통과 ({len(out):,} bytes)")

    bak = dat.with_suffix(".dat.bak")
    if not bak.exists():
        bak.write_bytes(dat.read_bytes())
        print(f"원본 백업: {bak.name}")
    dat.write_bytes(out)
    print(f"기록 완료: {dat}")


if __name__ == "__main__":
    main()
