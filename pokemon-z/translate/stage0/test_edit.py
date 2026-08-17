# /// script
# requires-python = ">=3.12"
# ///
"""edit 공용 한 벌 자체 검사 — 장난감 자료로 세 갈래만 본다.

공유 항목은 그 맵의 전 자리가 함께 바뀌는가 · 통일 참조는 그 맵만 떨어져 나오는가 ·
없는 열쇠는 조용히 0인가.

usage: uv run translate/stage0/test_edit.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import dump_jsonl  # noqa: E402
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
    {"id": "s23.k0", "val": "끝"},
]


def main():
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

        e.save()
        again = Messages(d)
        assert again.value("m1.e1.p0.c1") == "반갑다"
        assert [m["id"] for m in again.msgs] == [m["id"] for m in MSGS], "줄 순서가 밀렸다"
        assert MSGS[1]["val"] == "안녕", "원본을 건드렸다"
    print("edit 자체 검사 통과 — 공유 항목 · 통일 참조 떼기 · 없는 열쇠 · 순서 보존")


if __name__ == "__main__":
    main()
