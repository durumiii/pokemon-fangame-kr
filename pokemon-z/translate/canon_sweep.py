# /// script
# requires-python = ">=3.12"
# ///
"""정본 절을 본가 문장 코퍼스와 원문 완전 일치로 대조 — 미리보기/반영 (Z-2·Z-3).

원문(es 또는 k)을 코퍼스(messages.jsonl.gz)의 es·en 두 칸과 완전 일치로 맞추고,
값이 본가 자구와 다른 행을 보여 준다. 같은 원문에 세대별 자구가 갈리면 최신
세대를 채택한다. ⚠ 코퍼스의 줄바꿈은 글자 그대로의 백슬래시+n 두 글자다 —
공백으로 펴야 일치가 잡힌다. ⚠ 짧은 낱말은 출처 딴자리 오탐이 흔하다(성격명↔
기술명, 색↔인물명) — 출처 파일 태그를 보고 반영 여부를 갈라라. 자동 전량 반영
금지: --write는 승인 목록(줄 번호 파일)이 있어야 한다.

usage: uv run canon_sweep.py 06-move-descs             # 미리보기 (@번호 붙음)
       uv run canon_sweep.py 23-script-texts --write approved.txt
"""
import gzip
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
SRC_RANK = {"za": 0, "sv": 1, "la": 2, "swsh": 3, "lgpe": 4, "usum": 5, "sm": 6, "oras": 7, "xy": 8}


def norm(s):
    s = s.replace("\\n", " ").replace("\\r", " ")
    return re.sub(r"\s+", " ", s).strip()


def put_lines(edits):
    """0단계 정본에 앉히고 ko를 역생성한다 — 창구는 stage0/edit.py 하나다."""
    sys.path.insert(0, str(HERE / "stage0"))
    from edit import put_lines as _put
    return _put(edits)


def main():
    args = [a for a in sys.argv[1:] if a != "--write"]
    if not args:
        sys.exit(__doc__)
    sec = args[0]
    approved = None
    if "--write" in sys.argv:
        approved = {int(x) for x in Path(args[1]).read_text().split()}

    by = defaultdict(list)
    for line in gzip.open(HERE / "canon/messages.jsonl.gz", "rt", encoding="utf-8"):
        r = json.loads(line)
        by[norm(r["es"])].append(r)
        if r.get("en"):
            by[norm(r["en"])].append(r)

    p = HERE / "ko" / f"{sec}.jsonl"
    if not p.exists():
        # 접두 일치로 아무거나 집으면 00-maps가 00-maps.loc을 물어 온다 — 절 번호로 찾는다.
        sys.path.insert(0, str(HERE / "stage0"))
        from common import ko_file
        p = ko_file(int(sec[:2]))
        if p is None:
            sys.exit(f"중단: 절 파일을 못 찾았다 — {sec}")
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]
    n = applied = 0
    edits = []
    for idx, r in enumerate(rows):
        src = r.get("es") or r.get("k")
        if not src or not by.get(norm(src)):
            continue
        best = min(by[norm(src)], key=lambda c: SRC_RANK.get(c["src"], 99))
        ko = norm(best["ko"])
        if norm(r["v"]) == ko or "[VAR" in ko:
            continue
        n += 1
        if approved is not None:
            if idx in approved:
                edits.append((p.name, idx + 1, ko))
                applied += 1
            continue
        files = sorted({c["src"] + ":" + c["file"] for c in by[norm(src)]})
        print(f"@{idx} es={norm(src)[:64]!r}")
        print(f"    현행 {r['v'][:74]!r}")
        print(f"    본가 {ko[:74]!r} {files[:3]}")
    print(f"== 대상 {n}행" + (f" · 반영 {applied}행" if approved is not None else ""))
    if approved is not None:
        err = put_lines(edits)
        if err:
            print("멈춤 —", err)
            return
        print(f"기록: {p}")


if __name__ == "__main__":
    main()
