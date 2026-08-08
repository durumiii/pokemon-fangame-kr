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


def test_chips_and_event(tmp):
    """이벤트·맵 칩 — 원문의 줄바꿈을 접어 귀속표와 잇고, 명령 순서를 지킨다."""
    fixgui.KO = tmp
    fixgui.FIXLOG = tmp / "fixlog.jsonl"
    rows = [{"map": 1, "n": 2}, {"k": "Hola\namigo", "v": "안녕 친구"},
            {"k": "Adios", "v": "잘 가"},
            {"map": 2, "n": 1}, {"k": "Hola amigo", "v": "안녕 동무"}]
    (tmp / "a.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    fixgui._ctx = {
        "row": {}, "mapname": {1: "마을", 2: "동굴"},
        "spots": {(1, "Hola amigo"): [[7, 0, 3, "촌장"], [9, 0, 1, "경비"]]},
        "page": {(1, 7, 0): [[3, "Hola amigo", "촌장", "npc"], [1, "Adios", "촌장", "npc"]]},
    }

    h = fixgui.chips([r for r in fixgui.iter_rows() if r["line"] == 2])[0]
    assert h["mapname"] == "마을"
    assert len(h["spots"]) == 2          # 한 대사가 이벤트 둘에 걸린 자리
    assert h["omaps"] == 1               # 같은 원문이 맵 2에도 선다

    ev = fixgui.event_page(1, 7, 0)
    assert [r["cmd"] for r in ev] == [1, 3]          # 명령 순서대로
    assert [r["v"] for r in ev] == ["잘 가", "안녕 친구"]

    other = fixgui.same_es("Hola\namigo", 1)
    assert [(r["map"], r["v"]) for r in other] == [(2, "안녕 동무")]


def test_tags():
    """태그 문법 — 같은 태그는 OR, 다른 태그끼리는 AND(배포판 스튜디오와 같은 규칙)."""
    f = fixgui.parse_query('분류:도구 맵:12 화자:간호사 상태:수정 "두 낱말" 자유어')
    assert f["sec"] == ["도구"] and f["map"] == ["12"] and f["spk"] == ["간호사"]
    assert f["state"] == ["수정"] and f["text"] == ["두 낱말", "자유어"]
    assert fixgui.parse_query("맵:1 맵:2")["map"] == ["1", "2"]      # 같은 태그 누적
    assert fixgui.parse_query("그냥말")["text"] == ["그냥말"]

    c = {"mapname": {12: "고목내마을"}, "row": {(12, "Hola"): {"sprite": "nurse", "group": "간호사"}}}
    row = {"file": "09-item-descs.jsonl", "line": 3, "map": 12, "es": "Hola", "v": "안녕"}
    go = lambda q, **kw: fixgui.row_match(row, fixgui.parse_query(q), c,
                                          kw.get("edited", set()), kw.get("memoed", []))
    assert go("분류:도구")                  # 09 → 「도구 설명」 절 이름에 걸린다
    assert go("분류:9") and go("분류:item")  # 번호·파일명으로도
    assert not go("분류:기술")
    assert go("맵:12") and go("맵:고목") and not go("맵:1")   # 숫자는 정확, 이름은 부분
    assert go("화자:간호사") and go("화자:nurse") and not go("화자:점원")
    assert go("원문:Hola 번역:안녕") and not go("원문:Adios")
    assert go("맵:12 안녕") and not go("맵:12 없는말")        # 태그 + 자유어는 AND
    assert not go("상태:수정")
    assert go("상태:수정", edited={("09-item-descs.jsonl", 3)})
    assert go("상태:메모", memoed=["안녕"]) and not go("상태:메모", memoed=["딴말"])


if __name__ == "__main__":
    test_plan()
    test_tags()
    with tempfile.TemporaryDirectory() as d:
        test_bulk_and_revert(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_chips_and_event(Path(d))
    print("OK")
