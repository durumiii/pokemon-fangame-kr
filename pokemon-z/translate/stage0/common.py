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

OVERRIDES = OUT / "overrides.jsonl"
# overrides의 set이 쓸 수 있는 칸 — 설계 3절 sites·messages 스키마.
SITE_FIELDS = {"src", "apply", "speaker", "to", "layer", "kind", "scene", "how", "who",
               "translate"}
MSG_FIELDS = {"val", "why", "state", "by", "sample"}


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


def read_overrides(path=None):
    """사람 수정 층. 없으면 빈 목록 — gen은 overrides 없이도 돈다."""
    p = path or OVERRIDES
    return read_jsonl(p) if p.exists() else []


def apply_overrides(sites, msgs, ovr):
    """재생성 결과 위에 사람 수정을 얹는다 — gen은 순수 재생성이고 사람 손은 여기서만 든다.

    한 줄이 한 자리(또는 값)의 칸 몇 개를 갈아 끼운다. 같은 id에 여러 줄이면 파일 순서대로
    나중 줄이 이긴다. 칸 이름이 어느 스키마에 있느냐로 자리/값 중 어디에 얹을지 정한다.
    """
    si = {s["id"]: i for i, s in enumerate(sites)}
    mi = {m["id"]: i for i, m in enumerate(msgs)}
    sites, msgs = list(sites), list(msgs)
    for o in ovr:
        oid = o["id"]
        for k, v in o["set"].items():
            if k in SITE_FIELDS:
                tbl, idx = sites, si
            elif k in MSG_FIELDS:
                tbl, idx = msgs, mi
            else:
                raise ValueError(f"overrides: 스키마에 없는 칸 {k!r} (id={oid})")
            if oid not in idx:
                raise ValueError(f"overrides: 실재하지 않는 id {oid!r} (칸 {k})")
            tbl[idx[oid]] = {**tbl[idx[oid]], k: v}
    return sites, msgs


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
