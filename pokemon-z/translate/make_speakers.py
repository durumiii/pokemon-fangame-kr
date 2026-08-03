# /// script
# requires-python = ">=3.12"
# ///
"""축약 조인표 생성 — webapp/speakers.json.

    uv run translate/make_speakers.py

docs/research/map-speaker-join.jsonl.gz(비공개 조사 산출물)에서 웹앱 찾아보기에
필요한 것만 뽑는다: 맵별로 (원문 k) → [화자 스프라이트, 분류]. 원문 k는 이미
배포 dat에 들어 있는 텍스트라 새로 공개되는 정보가 아니다.

화자·분류·맵이름은 반복이 심해 문자열 테이블(sp/gp)에 담고 본문은 색인만 쓴다.
"""

import gzip
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
JOIN = HERE.parent / "docs" / "research" / "map-speaker-join.jsonl.gz"
GROUPS = HERE / "sprite-groups.json"
OUT = HERE.parent / "webapp" / "speakers.json"

# fixgui.py ctx()와 같은 규칙 — 스프라이트 파일명에서 방향·번호 꼬리를 떼면 인물 하나
stem = lambda s: re.sub(r"(ow|OW|TS|w)?\d*$", "", s) or "(없음)"


def main():
    s2g = {s: grp for grp, ss in
           json.loads(GROUPS.read_text(encoding="utf-8"))["groups"].items() for s in ss}
    sp, gp, maps = [], [], {}          # 문자열 테이블 + 맵별 본문
    idx = lambda tbl, s: tbl.index(s) if s in tbl else (tbl.append(s) or len(tbl) - 1)

    for line in gzip.open(JOIN, "rt", encoding="utf-8"):
        d = json.loads(line)
        if "sprite" not in d:
            continue
        m = maps.setdefault(str(d["map"]), {"name": d.get("map_name", ""), "rows": {}})
        if d["k"] in m["rows"]:        # 같은 대사가 여러 이벤트에 걸리면 첫 화자만
            continue
        m["rows"][d["k"]] = [idx(sp, d["sprite"] or "(없음)"),
                             idx(gp, s2g.get(stem(d["sprite"]), "?"))]

    OUT.write_text(json.dumps({"sp": sp, "gp": gp, "maps": maps},
                              ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    rows = sum(len(m["rows"]) for m in maps.values())
    print(f"{OUT}: 맵 {len(maps)} · 행 {rows} · 화자 {len(sp)} · 분류 {len(gp)} "
          f"· {OUT.stat().st_size / 1024:.0f}KB")


if __name__ == "__main__":
    main()
