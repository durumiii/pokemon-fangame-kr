# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""절23 배틀 메시지를 표현집 기준 문안으로 교체한다 — 걸음 4.

입력은 대조 산출 JSON([{i, es, old, new, src}, …]). 각 항목은 적용 전에
현재 값이 old와 정확히 같은지 확인하고, 다르면 그 항목을 건너뛰며 알린다
(이미 바뀐 자리나 어긋난 대조를 조용히 덮지 않기 위해). 플레이스홀더
{n}의 집합이 old와 new에서 같아야 통과한다.

usage: uv run apply_battle_expr.py <replacements.json> [--dry-run]
"""
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vendor"))
from fanlib import rubywrite  # noqa: E402
from rubymarshal.reader import load  # noqa: E402

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/korean.dat")
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/korean.dat")
PLACEHOLDER = re.compile(r"\{\d\}")


def main():
    dry = "--dry-run" in sys.argv
    reps = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    d = load(open(STORE, "rb"))
    inner = load(io.BytesIO(bytes(d[23]._private_data)))
    keys, values = inner

    applied, skipped, bad_ph = 0, [], []
    for r in reps:
        i = r["i"]
        cur = values[i].decode("utf-8")
        if sorted(PLACEHOLDER.findall(r["old"])) != sorted(PLACEHOLDER.findall(r["new"])):
            bad_ph.append((i, r["new"]))
            continue
        if cur != r["old"]:
            if cur == r["new"]:
                continue  # 이미 적용됨
            skipped.append((i, cur[:40], r["old"][:40]))
            continue
        assert keys[i].decode("utf-8") == r["es"], f"[{i}] ES 키 불일치"
        values[i] = r["new"].encode("utf-8")
        applied += 1

    print(f"적용 {applied} · 건너뜀 {len(skipped)} · 플레이스홀더 불일치 {len(bad_ph)}")
    for i, cur, old in skipped[:10]:
        print(f"  건너뜀 [{i}] 현재 {cur!r} ≠ 기대 {old!r}")
    for i, new in bad_ph[:10]:
        print(f"  플레이스홀더 [{i}] {new!r}")
    if bad_ph:
        sys.exit("플레이스홀더가 어긋난 항목이 있다 — 산출을 고쳐 다시.")

    d[23]._private_data = rubywrite.dumps([keys, values])
    out = rubywrite.dumps(d)
    r2 = load(io.BytesIO(out))
    ri = load(io.BytesIO(bytes(r2[23]._private_data)))
    assert ri[0] == keys and ri[1] == values, "절23 왕복 불일치"
    for sec in (1, 5, 7, 14):
        assert r2[sec] == d[sec] if isinstance(d[sec], list) else True, f"절{sec}이 변했다"
    print(f"왕복 검증 통과 · 산출 {len(out):,} bytes")

    if dry:
        print("dry-run — 파일에 쓰지 않음")
        return
    STORE.write_bytes(out)
    GAME.write_bytes(out)
    print(f"기록 완료: {STORE}\n           {GAME}")


if __name__ == "__main__":
    main()
