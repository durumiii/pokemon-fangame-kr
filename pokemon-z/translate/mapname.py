#!/usr/bin/env python3
"""맵 번호 → 이름. 문서에 번호만 적으면 읽는 사람이 어디인지 모른다.

맵 이름표(`ko/21-map-names.jsonl`)는 `i`가 맵 번호 그대로다(i=1이 인트로).
스페인어 이름은 귀속표의 `map_name`에 있다.

usage:
  uv run translate/mapname.py 150 214        번호로 찾는다
  uv run translate/mapname.py --tag 문서.md   문서의 「맵150」에 이름을 붙인다
"""
import gzip
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
NAMES = HERE / "ko/21-map-names.jsonl"
ATTR = HERE.parent / "docs/research/speaker-attr.jsonl.gz"

_ko = _es = None


def ko(mid):
    """한국어 맵 이름. 없으면 빈 문자열."""
    global _ko
    if _ko is None:
        _ko = {}
        for line in NAMES.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("v"):
                _ko[r["i"]] = r["v"]
    return _ko.get(mid, "")


def es(mid):
    """스페인어 맵 이름 — 이벤트 이름과 짝지어 볼 때 쓴다."""
    global _es
    if _es is None:
        _es = {}
        with gzip.open(ATTR, "rt", encoding="utf-8") as f:
            for line in f:
                a = json.loads(line)
                _es.setdefault(a["map"], a.get("map_name", ""))
    return _es.get(mid, "")


# 「맵150」·「맵 150」에만 붙인다. 건드리지 않는 자리:
#   자리 표기 「맵150:22:88」 · 구간 「맵 1–58」 · 이미 이름이 뒤따르는 「**맵113**(보데곤마을」
TAG = re.compile(r"맵\s?(\d{1,3})(?![\d:])(?!\s*[-–—~+])(?!\*{0,2}\s*\()")


def tag(text):
    """문서의 맵 번호 뒤에 이름을 괄호로 붙인다."""
    def sub(m):
        n = ko(int(m.group(1)))
        return m.group(0) + (f"({n})" if n else "")
    return TAG.sub(sub, text)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--tag":
        for p in map(Path, args[1:]):
            p.write_text(tag(p.read_text(encoding="utf-8")), encoding="utf-8")
            print(f"이름 붙임: {p}")
        return
    for a in args:
        if a.isdigit():
            print(f"맵 {a}: {ko(int(a)) or '(이름 없음)'}  ·  {es(int(a))}")


if __name__ == "__main__":
    main()
