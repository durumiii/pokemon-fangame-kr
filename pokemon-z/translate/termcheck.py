# /// script
# requires-python = ">=3.12"
# ///
"""용어 잔존 전 절 검사 — 옛 표기가 번역 정본 어디에 남았나.

전수 치환 뒤 절 스물다섯 개(`ko/*.jsonl`)의 번역 값(`v`)에서 옛 표기를 찾아
자리와 전후 문맥을 뽑는다. 맵 대사는 `맵번호:순번`(00-maps.jsonl의 블록 구조),
그 밖의 절은 줄 번호로 가리킨다. 새 표기를 함께 주면 그 등장 수도 센다.

⚠ 매칭은 단순 부분 문자열이라 조사·합성어가 섞인다 — 문맥을 보고 사람이 거른다.
잔존이 있으면 종료 코드 1(후속 스크립트·CI 게이트용).

usage: uv run translate/termcheck.py 궁극병기 [최종병기]
       uv run translate/termcheck.py --selftest
"""
import json
import sys
from pathlib import Path

import mapname

HERE = Path(__file__).parent
PAD = 18  # 발췌 좌우 문맥 글자 수


def spots(path):
    """(자리표, 행) 차례로. 00-maps.jsonl은 {"map","n"} 헤더 뒤 블록."""
    cur_map = idx = None
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        if "map" in r and "v" not in r:
            cur_map, idx = r["map"], 0
            continue
        if cur_map is None:
            yield str(ln), r
        else:
            yield f"맵{cur_map}:{idx}", r
            idx += 1


def excerpt(v, term):
    i = v.find(term)
    lo, hi = max(0, i - PAD), min(len(v), i + len(term) + PAD)
    return ("…" if lo else "") + v[lo:hi] + ("…" if hi < len(v) else "")


def scan(old, new):
    hits = new_count = 0
    for path in sorted((HERE / "ko").glob("*.jsonl")):
        for at, r in spots(path):
            v = r.get("v") or ""
            if new:
                new_count += v.count(new)
            if old not in v:
                continue
            hits += 1
            where = at
            if at.startswith("맵"):
                nm = mapname.ko(int(at[1:].split(":")[0]))
                where = f"{at}({nm})" if nm else at
            print(f"{path.name} {where}  {excerpt(v, old)!r}")
    return hits, new_count


def selftest():
    p = HERE / "ko" / "00-maps.jsonl"
    first = next(spots(p))
    assert first[0] == "맵0:0", first[0]
    assert "v" in first[1], first[1]
    assert excerpt("가나다라마바사", "다라") == "가나다라마바사"
    print("selftest OK")


def main():
    args = sys.argv[1:]
    if args == ["--selftest"]:
        return selftest()
    if not args:
        sys.exit(__doc__)
    old, new = args[0], (args[1] if len(args) > 1 else None)
    hits, new_count = scan(old, new)
    print(f"== {old!r} 잔존 {hits}곳" + (f" · {new!r} {new_count}회" if new else ""))
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
