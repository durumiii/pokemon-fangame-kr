# /// script
# requires-python = ">=3.12"
# ///
"""걸음 5 기계 검증기 — 재번역 후보를 행 단위로 통과/반려 가른다.

방법론 보고서(docs/design/z-retranslation-methodology.md)의 2단이다.
근거는 구조 조사 §5-1: 조용한 실패 성격상 사전 검증이 유일한 방어선이다.

usage:
  uv run validate.py <후보.jsonl> [--section 0]
후보 파일 형식: 한 행에 {"id": n, "ko": "..."} (파일럿 out-*.jsonl과 같음).
기준(현행)은 pilot/sample-200.jsonl이 아니라 --base로 준 jsonl의 같은 id 행이다
(기본: pilot/sample-200.jsonl — 파일럿 검산용).

검사 7종: 자리표 집합(서식 지시자 포함) · 제어 코드/태그(인자 포함) ·
\\x01 · 길이 1.4배 · <<n>> 금지 · 개행 수 · 절0의 \\j 신규 금지.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

# 인자까지 통째로 보존을 요구하는 것들. <c3=..>·<icon=..>은 인자가 뜻을 갖는다.
EXACT = re.compile(
    r"\\c\[\d+\]|\\v\[\d+\]|\\se\[[^\]]*\]|\\wt(?:np)?\[\d+\]"
    r"|\\PN|\\TP|\\TE|\\TM|\\m\b|\\x01"
    r"|</?b>|</?i>|</?ac>|</?ar>|<r>|<br>"
    r"|<c[23]=[^>]*>|<icon=[^>]*>"
    r"|\{\d+(?::[^}]*)?\}"
)
JOSA = re.compile(r"\\j\[[^\]]*\]")


def marks(s: str) -> Counter:
    return Counter(EXACT.findall(s))


def check(base: str, cand: str, sec: int) -> list[str]:
    bad = []
    if marks(base) != marks(cand):
        diff = (marks(base) - marks(cand)) + (marks(cand) - marks(base))
        bad.append("마크업: " + ", ".join(sorted(diff)))
    if len(cand) > len(base) * 1.4 + 6:
        bad.append(f"길이: {len(base)}→{len(cand)}")
    if "<<" in cand and re.search(r"<<\d+>>", cand):
        bad.append("<<n>> 표기(마셜 경로에서 안 풀림)")
    if base.count("\n") != cand.count("\n"):
        bad.append(f"개행 수: {base.count(chr(10))}→{cand.count(chr(10))}")
    if sec == 0 and len(JOSA.findall(cand)) > len(JOSA.findall(base)):
        bad.append("절0에 \\j 신규 삽입")
    return bad


def main() -> int:
    args = sys.argv[1:]
    base_path = Path(__file__).with_name("pilot") / "sample-200.jsonl"
    sec = 0
    cand_path = None
    it = iter(args)
    for a in it:
        if a == "--base":
            base_path = Path(next(it))
        elif a == "--section":
            sec = int(next(it))
        else:
            cand_path = Path(a)
    if cand_path is None:
        print(__doc__)
        return 2

    base = {}
    for line in base_path.read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if "id" in d and "ko" in d:
            base[d["id"]] = d["ko"]

    rejected = 0
    total = 0
    for line in cand_path.read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if d.get("got") is False or d["id"] not in base:
            continue
        total += 1
        bad = check(base[d["id"]], d["ko"], sec)
        if bad:
            rejected += 1
            print(f"반려 #{d['id']}: " + " | ".join(bad))
    print(f"\n{cand_path.name}: {total}행 중 반려 {rejected}행")
    return 0


if __name__ == "__main__":
    main()
