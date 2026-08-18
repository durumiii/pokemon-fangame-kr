"""stage0 공용 — 경로, 정규화, 절 구분, JSONL 입출력.

0단계 정본(Z-53 설계 3절)을 지금 출처에서 기계로 만들고 되돌리는 두 도구가 함께 쓴다.
"""
import functools
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
# layer는 gen이 안 싣지만 남는다 — 컷신 안 확인창처럼 사람이 **행 하나만** N으로 고쳐 둔
# 자리가 overrides에 9줄 있고(structure.row_layer가 그 값을 페이지 판정보다 먼저 본다),
# 그 갈래가 서려면 자리 스키마에 이름이 있어야 한다. scene은 행 단위 판정이 없어 걷었다.
SITE_FIELDS = {"src", "apply", "speaker", "to", "layer", "kind", "how", "who",
               "translate", "mart"}
MSG_FIELDS = {"val", "why", "state", "by", "sample"}
# 페이지 레코드(pages.jsonl) — 층·장면은 페이지 단위 판정이라 여기 산다(Z-53 설계 2절).
# layer 이름이 SITE_FIELDS와 겹치므로 어느 표에 얹을지는 id 꼴이 가른다.
PAGE_FIELDS = {"layer", "scene", "mixed", "by", "why"}
PAGE_ID = re.compile(r"^m\d+\.e\d+\.p\d+$")

# 등재제 축의 값 목록 — gen이 axes.yaml에 싣고 gate 검사 8이 정본 실물값을 여기 견준다.
PAGE_LAYERS = ["PS", "PC", "N"]         # 앞선 값이 다수결 동점을 이긴다(재생성 결정성)
PAGE_SCENES = ["컷신", "잡담", "대화", "트레이너", "공통"]
KINDS = ["text", "choice", "battle"]


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


@functools.cache
def _ko_files():
    """절 번호 → 파일. 글롭은 한 번만 — 역생성이 이 함수를 수만 번 부른다."""
    return {int(p.name[:2]): p for p in sorted(KO.glob("*.jsonl"))
            if not p.name.endswith((".add.jsonl", ".loc.jsonl"))}


def ko_file(sec):
    """절 번호 → translate/ko/ 안의 파일 (없으면 None)."""
    return _ko_files().get(sec)


def sweep_skip(name):
    """일괄 훑기에서 뺄 파일인가 — 추가분·좌표는 합성 열쇠라 부분 치환 규칙이 안 선다.
    걸린 줄은 사람이 그 파일에서 직접 고친다(조용히 빼지 말고 목록으로 알릴 것)."""
    return name.endswith((".add.jsonl", ".loc.jsonl"))


def read_overrides(path=None):
    """사람 수정 층. 없으면 빈 목록 — gen은 overrides 없이도 돈다."""
    p = path or OVERRIDES
    return read_jsonl(p) if p.exists() else []


def apply_overrides(sites, msgs, ovr):
    """재생성 결과 위에 사람 수정을 얹는다 — gen은 순수 재생성이고 사람 손은 여기서만 든다.

    한 줄이 한 자리(또는 값)의 칸 몇 개를 갈아 끼운다. 같은 id에 여러 줄이면 파일 순서대로
    나중 줄이 이긴다. 칸 이름이 어느 스키마에 있느냐로 자리/값 중 어디에 얹을지 정한다.
    페이지 id(`m*.e*.p*`) 줄은 여기서 건너뛴다 — apply_page_overrides가 받는다.
    """
    si = {s["id"]: i for i, s in enumerate(sites)}
    mi = {m["id"]: i for i, m in enumerate(msgs)}
    sites, msgs = list(sites), list(msgs)
    for o in ovr:
        oid = o["id"]
        if PAGE_ID.match(oid):
            continue
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


def apply_page_overrides(pages, ovr):
    """페이지 층에 사람 수정을 얹는다 — 페이지 id 줄만 본다.

    표를 칸 이름이 아니라 **id 꼴로** 가르는 것은 layer가 자리 스키마와 이름이 겹치기
    때문이다 — 행 단위 사람 판정이 자리 쪽에 계속 얹힌다(Z-53 설계 2절).
    """
    pi = {p["id"]: i for i, p in enumerate(pages)}
    pages = list(pages)
    for o in ovr:
        oid = o["id"]
        if not PAGE_ID.match(oid):
            continue
        for k, v in o["set"].items():
            if k not in PAGE_FIELDS:
                raise ValueError(f"overrides: 페이지 스키마에 없는 칸 {k!r} (id={oid})")
            if oid not in pi:
                raise ValueError(f"overrides: 실재하지 않는 페이지 id {oid!r} (칸 {k})")
            pages[pi[oid]] = {**pages[pi[oid]], k: v}
        if o["set"] and oid in pi and "by" in o:
            # 사람 판정이 얹힌 페이지는 유래도 사람으로 — by가 이 층의 본체다
            pages[pi[oid]] = {**pages[pi[oid]], "by": o["by"]}
    return pages


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
