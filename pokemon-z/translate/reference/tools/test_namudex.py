"""Self-check: the shipped namudex.jsonl still holds the reference rows."""
import json, pathlib

ROWS = [json.loads(l) for l in (pathlib.Path(__file__).parent.parent / "namudex.jsonl").open()]


def test_casey_emerald():
    r = next(r for r in ROWS if r["species"] == 63 and r["version"] == "emerald" and "note" not in r)
    assert r["ko"].startswith("하루에 18시간 잠들어 있는 포켓몬이다.")
    assert "1시간마다 순간이동으로 장소를 이동한다" in r["ko"]


def test_shape():
    assert len({r["species"] for r in ROWS}) > 880
    assert all(r["species"] > 0 and r["ko"] and r["version"] for r in ROWS)
    # merged labels must be expanded, never left as raw Korean
    assert not any("/" in r["version"] for r in ROWS)


if __name__ == "__main__":
    test_casey_emerald(); test_shape(); print("ok", len(ROWS), "rows")
