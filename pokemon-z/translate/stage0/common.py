"""stage0 공용 — 경로, 정규화, 절 구분, JSONL 입출력.

0단계 정본(Z-53 설계 3절)을 지금 출처에서 기계로 만들고 되돌리는 두 도구가 함께 쓴다.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]      # translate/
KO = ROOT / "ko"
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent           # translate/stage0/

LIST_SECS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 21]
HASH_SECS = [14, 19, 20, 22, 23]
EMPTY_SECS = [15, 16, 17]


def norm(s):
    """귀속표와 정본을 이을 때 쓰는 줄임 — 지침 text-pipeline 「정본과 빌드」."""
    return re.sub(r"\s+", " ", s).strip()


def h8(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:8]


def read_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def dump_jsonl(path, rows):
    """정본과 같은 꼴 — ensure_ascii=False, 기본 구분자, 줄 끝 개행."""
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )


def ko_file(sec):
    """절 번호 → translate/ko/ 안의 파일 (없으면 None)."""
    for p in sorted(KO.glob("*.jsonl")):
        if p.name.endswith((".add.jsonl", ".loc.jsonl")):
            continue
        if int(p.name[:2]) == sec:
            return p
    return None


def read_maps():
    """00-maps.jsonl → [(맵번호, [{"k","v"}, ...]), ...] 파일 순서 그대로."""
    out, cur = [], None
    for r in read_jsonl(KO / "00-maps.jsonl"):
        if "map" in r:
            cur = []
            out.append((r["map"], cur))
            assert r["map"] == len(out) - 1, f"맵 머리 줄이 순서와 다르다: {r}"
        else:
            cur.append(r)
    return out
