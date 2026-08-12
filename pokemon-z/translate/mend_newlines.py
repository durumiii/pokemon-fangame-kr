# /// script
# requires-python = ">=3.12"
# ///
"""새 번역이 지어 넣은 줄바꿈을 지워 「직접」 판정으로 미리 채운다.

기계 검증 반려 가운데 가장 흔한 것이 개행 수 어긋남이다 — 원문 스페인어에는 줄바꿈이
있어도 한국어 정본은 안 쓰는 자리인데, 새 번역이 원문을 따라 넣는다. 현행 번역의
줄바꿈 수에 맞춰 여분을 공백으로 되돌리면 나머지 검사는 그대로 통과한다
(실측 2026-08-06: 104행 중 104행).

    uv run translate/mend_newlines.py <out-dir>          # 미리보기
    uv run translate/mend_newlines.py <out-dir> --write  # 판정 기록에 「직접」으로 채움

채워 넣을 뿐 감추지 않는다 — 검수 화면에 그대로 서고, 고쳐 누르면 그쪽이 이긴다.
이미 판정이 있는 자리는 건드리지 않는다.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from review_page import collect  # noqa: E402  (화면에 실제로 서는 행만 채운다)
from validate import check  # noqa: E402


def mend(base, cand):
    """현행이 안 쓰는 줄바꿈만 지운다. 현행에 줄바꿈이 있으면 손대지 않는다."""
    if base.count("\n") or cand.count("\n") == 0:
        return None
    return re.sub(r"[ \t]+", " ", cand.replace("\n", " ")).strip()


def run(out_dir, write=False):
    d = Path(out_dir)
    ledger = d.parent / f"verdicts-{d.name}.jsonl"
    have = {json.loads(l)["id"] for l in ledger.read_text(encoding="utf-8").splitlines()
            if l.strip() and json.loads(l).get("id")} if ledger.exists() else set()
    shown = {r["id"] for sc in collect(d) for r in sc["rows"]}

    fixed, skipped = [], 0
    for fp in sorted(d.glob("p*.jsonl")):
        for line in fp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("ok") or r["id"] in have or r["id"] not in shown:
                continue
            new = mend(r["old"], r.get("new") or "")
            if new is None:
                continue
            if check(r["old"], new, 0):
                skipped += 1              # 줄바꿈 말고 다른 것도 어긋난 자리
                continue
            fixed.append({"id": r["id"], "판정": "직접", "텍스트": new,
                          "메모": "개행 기계 수선 — 확인 바람", "ts": "auto"})

    print(f"수선 가능 {len(fixed)}행 · 다른 검사도 걸린 자리 {skipped}행 · "
          f"이미 판정된 자리 제외 {len(have)}건")
    for r in fixed[:3]:
        print("  ", r["id"], r["텍스트"][:70])
    if not write:
        print("미리보기만 — 채우려면 --write")
        return
    with ledger.open("a", encoding="utf-8") as f:
        for r in fixed:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{ledger.name}에 {len(fixed)}행 채움 — 화면을 새로고침하면 「직접」으로 서 있다")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        print(__doc__)
        sys.exit()
    run(a[0], write="--write" in sys.argv)
