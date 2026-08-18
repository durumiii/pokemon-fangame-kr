# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""overrides 층 자체 검사 — 장난감 자료로 네 성질만 본다.

큰 산출물 없이도 깨지면 여기서 걸린다: 칸이 어느 표에 얹히는가 · 페이지 id가 페이지 표로
가는가 · 나중 줄이 이기는가 · 참조를 거꾸로 타고 물드는가.

usage: uv run translate/stage0/test_overrides.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import apply_overrides, apply_page_overrides  # noqa: E402
from diff import tainted_ids  # noqa: E402

SITES = [{"id": "a", "src": "A", "apply": "map", "layer": "N"},
         {"id": "b", "src": "B", "apply": "map"}]
MSGS = [{"id": "a", "val": {"ref": "sh"}}, {"id": "b", "val": {"ref": "sh"}},
        {"id": "sh", "val": "공유"}]
PAGES = [{"id": "m1.e2.p0", "layer": "N", "by": "machine/gen"}]


def main():
    ovr = [
        {"id": "a", "set": {"layer": "PC"}, "why": "w", "by": "t"},
        {"id": "sh", "set": {"val": "갈아 낀 값"}, "why": "w", "by": "t"},
        {"id": "a", "set": {"layer": "PS"}, "why": "나중 줄이 이긴다", "by": "t"},
        {"id": "m1.e2.p0", "set": {"layer": "PS"}, "why": "w", "by": "human/t"},
    ]
    s, m = apply_overrides(SITES, MSGS, ovr)
    assert s[0]["layer"] == "PS", s[0]          # 칸은 자리 쪽에, 나중 줄이 이긴다
    assert m[2]["val"] == "갈아 낀 값", m[2]     # 값 칸은 값 쪽에
    assert SITES[0]["layer"] == "N", "원본을 건드렸다"
    assert len(s) == 2, "페이지 줄이 자리 표로 샜다"
    # 같은 칸 이름이라도 페이지 id면 페이지 표로 간다
    p = apply_page_overrides(PAGES, ovr)
    assert p[0]["layer"] == "PS" and PAGES[0]["layer"] == "N", (p, PAGES)

    hit = tainted_ids({x["id"]: x for x in m}, [{"id": "sh"}])
    assert hit == {"sh", "a", "b"}, hit          # 공유 값을 갈면 가리키는 자리가 다 물든다

    for fn, bad, why in (
            (lambda o: apply_overrides(SITES, MSGS, o),
             {"id": "없다", "set": {"layer": "PC"}}, "없는 id"),
            (lambda o: apply_overrides(SITES, MSGS, o),
             {"id": "a", "set": {"없는칸": 1}}, "없는 칸"),
            (lambda o: apply_page_overrides(PAGES, o),
             {"id": "m9.e9.p9", "set": {"layer": "PC"}}, "없는 페이지 id"),
            (lambda o: apply_page_overrides(PAGES, o),
             {"id": "m1.e2.p0", "set": {"val": "x"}}, "페이지에 없는 칸")):
        try:
            fn([bad])
        except ValueError:
            continue
        raise AssertionError(f"{why}를 안 막았다")
    print("overrides 자체 검사 통과 — 칸 배정 · 페이지 표 · 나중 줄 우선 · 참조 역전파 · 거부 넷")


if __name__ == "__main__":
    main()
