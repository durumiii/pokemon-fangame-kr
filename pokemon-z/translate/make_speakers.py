# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""축약 조인표 생성 — webapp/speakers.json.

    uv run translate/make_speakers.py

translate/data/map-speaker-join.jsonl.gz(비공개 조사 산출물)에서 웹앱 찾아보기에
필요한 것만 뽑는다: 맵별로 (원문 k) → [화자 스프라이트, 분류]. 원문 k는 이미
배포 dat에 들어 있는 텍스트라 새로 공개되는 정보가 아니다.

조인표에 없는 자리는 귀속표가 메운다 — 전투 화면 대사(`how="전투호출"`)는 스프라이트가
없는 대신 호출 인자에 트레이너 직함·이름이 실려 있어, 그것을 한국어로 옮겨 화자 칸에 쓴다.

여기에 speaker-attr.jsonl.gz(speaker.py scan 산출)의 **이벤트 자리**를 얹는다 —
행이 어느 이벤트-페이지의 몇 번째 명령에 서 있는지다. 스튜디오가 이것으로
「이 대사가 속한 이벤트 모아 보기」를 그린다. 한 원문이 여러 자리에 걸리면 전부 담는다.

화자·분류·이벤트 이름은 반복이 심해 문자열 테이블(sp/gp/en)에 담고 본문은 색인만 쓴다.
"""

import gzip
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
JOIN = HERE / "data" / "map-speaker-join.jsonl.gz"
ATTR = HERE / "data" / "speaker-attr.jsonl.gz"
GROUPS = HERE / "stage0" / "groups.yaml"   # 스프라이트 묶음 정본(2026-08-18 강등)
KO = HERE / "ko"
TTYPES = Path("/mnt/d/Game/Pokemon Z/V2.18/PBS/trainertypes.txt")   # 직함 상수 → 번호
OUT = HERE.parent / "webapp" / "speakers.json"

# fixgui.py ctx()와 같은 규칙 — 스프라이트 파일명에서 방향·번호 꼬리를 떼면 인물 하나
stem = lambda s: re.sub(r"(ow|OW|TS|w)?\d*$", "", s) or "(없음)"
TRAINER_GP = "트레이너"   # 스프라이트 묶음이 아니라 전투 화면 화자라는 표시


def trainer_ko():
    """전투호출 행의 화자 이름표 재료 — (직함 상수 → 한국어 직함, 이름 → 한국어 이름).

    직함은 게임 설치본의 trainertypes.txt로 번호를 얻어 절13에 잇는다. 설치본이 없으면
    직함 없이 이름만 쓴다.
    """
    jl = lambda p: [json.loads(l) for l in p.open(encoding="utf-8")]
    ko_cls = {d["i"]: d["v"] for d in jl(KO / "13-trainer-classes.jsonl")}
    names = {d["k"]: d["v"] for d in jl(KO / "14-trainer-names.jsonl")}
    cls = {}
    if TTYPES.exists():
        for line in TTYPES.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            p = line.split(",")
            if len(p) > 1 and p[0].strip().isdigit():
                cls[p[1].strip()] = ko_cls.get(int(p[0]), "")
    return cls, names


def main():
    import yaml
    tcls, tnames = trainer_ko()
    s2g = {s: grp for grp, ss in
           yaml.safe_load(GROUPS.read_text(encoding="utf-8"))
           ["sprite_groups"]["groups"].items() for s in ss}
    sp, gp, en, maps = [], [], [], {}   # 문자열 테이블 + 맵별 본문
    idx = lambda tbl, s: tbl.index(s) if s in tbl else (tbl.append(s) or len(tbl) - 1)
    row = lambda m, k: m["rows"].setdefault(k, [None, None])

    for line in gzip.open(JOIN, "rt", encoding="utf-8"):
        d = json.loads(line)
        if "sprite" not in d:
            continue
        m = maps.setdefault(str(d["map"]), {"name": d.get("map_name", ""), "rows": {}})
        if d["k"] in m["rows"]:        # 같은 대사가 여러 이벤트에 걸리면 첫 화자만
            continue
        m["rows"][d["k"]] = [idx(sp, d["sprite"] or "(없음)"),
                             idx(gp, s2g.get(stem(d["sprite"]), "?"))]

    # 이벤트 자리 — 귀속표의 k는 이벤트 원문 그대로라 dat 쪽 모양(공백 한 칸)으로 접어 맞춘다
    for line in gzip.open(ATTR, "rt", encoding="utf-8"):
        d = json.loads(line)
        m = maps.setdefault(str(d["map"]), {"name": d.get("map_name", ""), "rows": {}})
        r = row(m, re.sub(r"\s+", " ", d["k"]).strip())
        if r[0] is None and d.get("how") == "전투호출":   # 조인표에 없는 전투 대사만 메운다
            label = " ".join(filter(None, [tcls.get(d.get("tclass", ""), ""),
                                           tnames.get(d.get("who", ""), d.get("who", ""))]))
            if label:
                r[0], r[1] = idx(sp, label), idx(gp, TRAINER_GP)
        if len(r) == 2:
            r.append([])
        r[2].append([d["event"], d["page"], d["cmd"], idx(en, d["event_name"])])

    for m in maps.values():            # 이벤트 안 차례대로 — 자리 목록·모아 보기가 이 순서를 쓴다
        for r in m["rows"].values():
            if len(r) > 2:
                r[2].sort(key=lambda p: (p[0], p[1], p[2]))

    OUT.write_text(json.dumps({"sp": sp, "gp": gp, "en": en, "maps": maps},
                              ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    rows = sum(len(m["rows"]) for m in maps.values())
    spots = sum(len(r[2]) for m in maps.values() for r in m["rows"].values() if len(r) > 2)
    blank = sum(r[0] is None for m in maps.values() for r in m["rows"].values())
    print(f"{OUT}: 맵 {len(maps)} · 행 {rows} · 화자 {len(sp)} · 분류 {len(gp)} "
          f"· 이벤트 이름 {len(en)} · 자리 {spots} · 화자 없는 행 {blank} "
          f"· {OUT.stat().st_size / 1024:.0f}KB")


if __name__ == "__main__":
    main()
