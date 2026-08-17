# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""apply_verdicts의 낡은 스냅숏 가드(Z-54 ③) — `uv run translate/test_apply_verdicts.py`.

정본을 건드리지 않도록 MAPS를 임시 폴더로 갈아 끼우고 돈다. 산출의 old(배치 시점
현행)가 지금 정본과 다르면 그 행은 반영되지 않고, 같으면 반영된다.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import apply_verdicts as av  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        maps = td / "00-maps.jsonl"
        maps.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in [
            {"map": 1, "n": 2},
            {"k": "Hola", "v": "유지자가 방금 고친 값"},   # 배치 뒤 손댄 자리 — 낡음
            {"k": "Adiós", "v": "옛 값"},                  # 그대로인 자리 — 반영돼야
        ]) + "\n", encoding="utf-8")
        out = td / "page-out"
        out.mkdir()
        (out / "p001.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in [
            {"id": "1:0", "es": "Hola", "old": "배치 시점 값", "new": "새 번역A", "ok": True},
            {"id": "1:1", "es": "Adiós", "old": "옛 값", "new": "새 번역B", "ok": True},
        ]) + "\n", encoding="utf-8")

        orig = av.MAPS
        av.MAPS = maps
        try:
            av.run(str(out), write=True)
        finally:
            av.MAPS = orig

        got = {json.loads(l)["k"]: json.loads(l)["v"]
               for l in maps.read_text(encoding="utf-8").splitlines() if '"k"' in l}
        assert got["Hola"] == "유지자가 방금 고친 값", got   # 낡은 스냅숏 — 안 덮는다
        assert got["Adiós"] == "새 번역B", got               # 신선 — 반영된다
    print("OK")


if __name__ == "__main__":
    main()
