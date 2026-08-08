# /// script
# requires-python = ">=3.12"
# ///
"""fixgui의 일괄 바꾸기·묶음 되돌리기 규칙 — `uv run translate/test_fixgui.py`.

정본을 건드리지 않도록 KO·FIXLOG를 임시 폴더로 갈아 끼우고 돈다.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fixgui  # noqa: E402

ROWS = [
    {"file": "a.jsonl", "line": 1, "map": 1, "es": "Hola amigo", "v": "안녕 친구"},
    {"file": "a.jsonl", "line": 2, "map": 1, "es": "Hola", "v": "안녕 친구"},
    {"file": "a.jsonl", "line": 3, "map": 1, "es": "Hola", "v": "반가워 친구"},
]


def test_plan():
    # 번역 기준 — 원문 조건 없음
    hits, skipped, err = fixgui.plan_replace(ROWS, "친구", "동무")
    assert err is None and len(hits) == 3 and not skipped
    assert hits[0]["new"] == "안녕 동무"

    # 원문 조건 — 걸려 빠진 행이 목록으로 돌아온다
    hits, skipped, err = fixgui.plan_replace(ROWS, "친구", "동무", src="amigo")
    assert [h["line"] for h in hits] == [1]
    assert [s["line"] for s in skipped] == [2, 3]

    # 원문 기준 — 찾을 문구를 비우면 그 원문의 번역을 통째로 간다
    hits, skipped, err = fixgui.plan_replace(ROWS, "", "안녕하세요", src="Hola")
    assert [h["line"] for h in hits] == [1, 2, 3]
    assert {h["new"] for h in hits} == {"안녕하세요"}

    # 둘 다 비면 거부
    assert fixgui.plan_replace(ROWS, "", "x")[2] is not None

    # 바뀌지 않는 행은 대상에서 빠진다
    assert fixgui.plan_replace(ROWS, "친구", "친구")[0] == []


def test_bulk_and_revert(tmp):
    fixgui.KO = tmp
    fixgui.FIXLOG = tmp / "fixlog.jsonl"
    (tmp / "a.jsonl").write_text(
        "\n".join(json.dumps({"k": r["es"], "v": r["v"]}, ensure_ascii=False)
                  for r in ROWS) + "\n", encoding="utf-8")

    hits, _, _ = fixgui.plan_replace(fixgui.iter_rows(), "친구", "동무")
    done, errs = fixgui.apply_replace(hits, "테스트")
    assert (done, errs) == (3, [])
    assert [r["v"] for r in fixgui.iter_rows()] == ["안녕 동무", "안녕 동무", "반가워 동무"]

    ops = fixgui.history()
    assert len(ops) == 1 and ops[0]["kind"] == "bulk" and len(ops[0]["rows"]) == 3

    # 묶음 뒤에 따로 고쳐진 행은 되돌리기가 건너뛴다
    fixgui.save_row("a.jsonl", 2, "안녕 동지")
    done, skipped, errs = fixgui.revert_op(ops[0]["op"])
    assert (done, skipped, errs) == (2, 1, [])
    assert [r["v"] for r in fixgui.iter_rows()] == ["안녕 친구", "안녕 동지", "반가워 친구"]

    # 되돌리기 자체도 한 묶음으로 쌓인다
    kinds = [o["kind"] for o in fixgui.history()]
    assert kinds == ["revert", "row", "bulk"], kinds


if __name__ == "__main__":
    test_plan()
    with tempfile.TemporaryDirectory() as d:
        test_bulk_and_revert(Path(d))
    print("OK")
