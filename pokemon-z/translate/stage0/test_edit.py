# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""edit 공용 한 벌 자체 검사 — 장난감 자료로 네 갈래만 본다.

공유 항목은 그 맵의 전 자리가 함께 바뀌는가 · 통일 참조는 그 맵만 떨어져 나오는가 ·
없는 열쇠는 조용히 0인가. 선택자 트리는 시끄럽게 거부하는가 · 뜬 뒤에 코드가 바뀌면
쓰기를 거부하는가.

usage: uv run translate/stage0/test_edit.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import dump_jsonl  # noqa: E402
import edit  # noqa: E402
from edit import Messages  # noqa: E402

SITES = [
    # 맵1: 같은 원문이 두 자리 — 값은 공유 항목에 있다
    {"id": "m1.e1.p0.c1", "src": "Hola ", "apply": "map"},
    {"id": "m1.e2.p0.c1", "src": "Hola", "apply": "map"},
    # 맵1의 다른 원문 — 통일 참조
    {"id": "m1.e3.p0.c1", "src": "Adios", "apply": "map"},
    # 맵2도 같은 통일 항목을 가리킨다 — 여긴 안 바뀌어야 한다
    {"id": "m2.e1.p0.c1", "src": "Adios", "apply": "map"},
    {"id": "s23.k0", "src": "Fin", "apply": "global"},   # 맵 절이 아니다
]
MSGS = [
    {"id": "unified.x", "val": "잘 가"},
    {"id": "m1.s0", "val": "안녕"},
    {"id": "m1.e1.p0.c1", "val": {"ref": "m1.s0"}},
    {"id": "m1.e2.p0.c1", "val": {"ref": "m1.s0"}},
    {"id": "m1.e3.p0.c1", "val": {"ref": "unified.x"}},
    {"id": "m2.e1.p0.c1", "val": {"ref": "unified.x"}},
    {"id": "s23.k0", "val": {"sel": "mart", "when": {"반말": "끝이야"}, "default": "끝"}},
]


def test_stale_guard():
    """뜬 뒤에 stage0 코드가 바뀌면 쓰기를 거부한다(2026-08-19 옛 스튜디오 사고)."""
    assert edit.stale_reason() is None
    saved = edit._LOADED_STAMP
    try:
        edit._LOADED_STAMP = 0          # 「이 프로세스가 아주 옛날에 떴다」
        why = edit.stale_reason()
        assert why and "다시 켜고" in why, why
        assert edit.put_lines([("00-maps.jsonl", 1, "아무거나")]) == why
    finally:
        edit._LOADED_STAMP = saved
    assert edit.stale_reason() is None


def main():
    test_stale_guard()
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        dump_jsonl(d / "sites.jsonl", SITES)
        dump_jsonl(d / "messages.jsonl", MSGS)
        e = Messages(d)

        assert len(e.groups) == 3, e.groups            # 맵 절만, 공유는 한 항목
        assert e.set(1, "hay", "x") == 0                # 없는 열쇠
        assert e.set(1, "Hola", "반갑다") == 1          # 접힌 원문으로 찾는다
        assert e.value("m1.e1.p0.c1") == "반갑다"       # 공유 항목이 갈려 두 자리가 함께
        assert e.value("m1.e2.p0.c1") == "반갑다"
        assert e.set(1, "Adios", "또 보자") == 1
        assert e.value("m1.e3.p0.c1") == "또 보자"      # 그 맵만 참조에서 떨어졌다
        assert e.value("m2.e1.p0.c1") == "잘 가", "통일 항목을 갈아 다른 맵까지 물들었다"

        assert e.value("s23.k0") == "끝", "선택자 트리는 기본 갈래로 보여야 한다"
        try:
            e.put("s23.k0", "덮어쓰기")
        except ValueError:
            pass
        else:
            raise AssertionError("선택자 트리를 통째로 덮는 것을 안 막았다")

        e.save()
        again = Messages(d)
        assert again.value("m1.e1.p0.c1") == "반갑다"
        assert [m["id"] for m in again.msgs] == [m["id"] for m in MSGS], "줄 순서가 밀렸다"
        assert MSGS[1]["val"] == "안녕", "원본을 건드렸다"
    cache_check()
    print("edit 자체 검사 통과 — 낡은 프로세스 가드 · 공유 항목 · 통일 참조 떼기 · 없는 열쇠 · 선택자 트리 거부 · 순서 보존 · 캐시 무효화")


def cache_check():
    """상주 캐시 — 지문이 그대로면 같은 것을 주고, 밖에서 움직이면 다시 읽는다.

    캐시가 파일보다 오래 살면 딴 도구(fix.py·git 병합)의 수정을 못 보고 덮는다.
    """
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        dump_jsonl(d / "sites.jsonl", [])
        dump_jsonl(d / "messages.jsonl", [{"id": "a", "val": "처음"}])
        (d / "axes.yaml").write_text("axes: {}\n", encoding="utf-8")
        (d / "layout.yaml").write_text("maps: 0\nsections: {}\n", encoding="utf-8")
        edit.invalidate()
        st1 = edit._stamp(d)
        one = Messages(d)
        edit._cache = (st1, one, {}, {})
        assert edit.load(d)[0] is one and edit.load(d)[3], "지문이 같은데 다시 읽었다"
        dump_jsonl(d / "messages.jsonl", [{"id": "a", "val": "밖에서 갈린 값"}])
        ed, _, _, warm = edit.load(d)
        assert not warm, "밖에서 갈렸는데 캐시를 그대로 썼다"
        assert ed.msgs[0]["val"] == "밖에서 갈린 값", ed.msgs
        # 지문은 0단계 파일 여섯을 다 덮는다 — 페이지 판정(pages)과 그릇 뼈대(layout)가
        # 빠져 있으면 층·장면을 고쳐도 상주 창구가 옛 값을 그대로 준다(Z-53 2단계)
        for name, text in (("pages.jsonl", '{"id": "m1.e1.p0", "layer": "N"}\n'),
                           ("layout.yaml", "maps: 12\nsections: {}\n")):
            st = edit._stamp(d)
            (d / name).write_text(text, encoding="utf-8")
            assert edit._stamp(d) != st, f"{name}이 갈렸는데 지문이 그대로다"
        edit.invalidate()


if __name__ == "__main__":
    main()
