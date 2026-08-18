# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal", "pyyaml"]
# ///
"""페이지 층 자체 검사 — 장난감 자료로 세 성질만 본다.

접기가 다수결인가(동점은 등재 순서로 갈라 재생성이 흔들리지 않는가) · 갈린 페이지에
표시가 남는가 · 정합·등재 검사가 실제로 잡는가.

usage: uv run translate/stage0/test_pages.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate import check_enum, check_pages  # noqa: E402
from gen import fold_pages  # noqa: E402


def main():
    rows = fold_pages({
        (1, 2, 0): {"layer": {"PC": 9, "N": 4}, "scene": {"잡담": 13}},
        (1, 3, 0): {"layer": {"N": 1, "PC": 1}},                    # 동점
        (2, 1, 0): {"layer": {"PS": 3}, "scene": {"컷신": 3}},
    })
    assert [r["id"] for r in rows] == ["m1.e2.p0", "m1.e3.p0", "m2.e1.p0"], rows
    assert rows[0]["layer"] == "PC" and rows[0]["mixed"], rows[0]      # 다수결
    assert rows[1]["layer"] == "PC" and rows[1]["mixed"], rows[1]      # 동점은 등재 순서
    assert "mixed" not in rows[2] and "scene" not in rows[1], rows     # 안 갈리면 표시 없음
    assert all(r["by"] == "machine/gen" for r in rows), rows

    sites = [{"id": "m1.e2.p0.c1"}, {"id": "m1.e3.p0.c1"}, {"id": "s23.k0"}]
    bad, used = check_pages(sites, rows)
    assert used == 2, used
    assert len(bad) == 1 and "고아" in bad[0]["kind"], bad          # m2.e1.p0에 자리가 없다
    bad, _ = check_pages(sites + [{"id": "m9.e9.p9.c1"}], rows)
    assert any("pages에 없다" in b["kind"] for b in bad), bad
    assert not check_pages([{"id": s["id"]} for s in sites] + [{"id": "m2.e1.p0.c1"}], rows)[0]

    axes = {"axes": {"layer": {"values": ["PS", "PC", "N"], "from": "pages.layer"},
                     "speaker": {"from": "sites.speaker"}}}
    assert not check_enum(axes, {"sites": sites, "pages": rows})
    bent = [*rows[:1], {**rows[1], "layer": "없는층"}, *rows[2:]]
    hit = check_enum(axes, {"sites": sites, "pages": bent})
    assert len(hit) == 1 and hit[0]["값"] == "없는층", hit
    print("페이지 층 자체 검사 통과 — 다수결 · 동점 갈이 · mixed 표시 · 정합 둘 · 등재 밖 값")


if __name__ == "__main__":
    main()
