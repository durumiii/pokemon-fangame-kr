# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Map*.rxdata 이벤트 판독 → 대사-화자 조인표.

무태그 대사 행(00-maps.jsonl)의 화자를 이벤트(이름·스프라이트·좌표)로 역추적한다.
어투 배정(일회용 NPC 「~다」 번역투 교정)의 조사 도구.

    uv run translate/mapscan.py [--game "/mnt/d/Game/Pokemon Z/V2.18"]

산출: docs/research/map-speaker-join.jsonl (한 줄 = 대사 하나, 이벤트 문맥 포함)
stdout: 조인율·스프라이트 분포·어미 분포 리포트.
"""

import argparse
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from datread import load  # 딱지를 떼 옛 도구가 그대로 읽는다

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME = "/mnt/d/Game/Pokemon Z/V2.18"


def b2s(v):
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="replace")
    return str(v)


def norm(s):
    # dat 추출기가 401 연속행을 공백으로 이었으므로(실측: Modo Heroico 행)
    # 공백류 전체를 한 칸으로 눌러 맞춘다.
    return re.sub(r"\s+", " ", s).strip()


def page_messages(page):
    """한 이벤트 페이지의 (유형, 문자열) 목록. 101+401 병합, 102 선택지는 개별."""
    out = []
    buf = None
    for cmd in page.attributes["@list"]:
        ca = cmd.attributes
        code, params = ca["@code"], ca["@parameters"]
        if code == 101:
            if buf is not None:
                out.append(("text", buf))
            buf = b2s(params[0])
        elif code == 401 and buf is not None:
            buf += "\n" + b2s(params[0])
        else:
            if buf is not None:
                out.append(("text", buf))
                buf = None
            if code == 102:
                out.extend(("choice", b2s(c)) for c in params[0])
    if buf is not None:
        out.append(("text", buf))
    return out


def scan_maps(game_dir):
    data = Path(game_dir) / "Data"
    infos = load(open(data / "MapInfos.rxdata", "rb"))
    map_names = {k: b2s(v.attributes["@name"]) for k, v in infos.items()}
    rows = []
    # 맵 0 = CommonEvents (스프라이트 없음, 이벤트명만)
    for ce in load(open(data / "CommonEvents.rxdata", "rb")):
        if ce is None:
            continue
        ca = ce.attributes
        fake_page = type("P", (), {"attributes": {"@list": ca["@list"]}})()
        for kind, text in page_messages(fake_page):
            rows.append({
                "map": 0, "map_name": "(common)", "event": ca["@id"],
                "event_name": b2s(ca["@name"]), "page": 0,
                "sprite": "", "x": -1, "y": -1, "kind": kind, "text": text,
            })
    for p in sorted(data.glob("Map[0-9][0-9][0-9].rxdata")):
        mid = int(p.stem[3:])
        m = load(open(p, "rb"))
        for eid, ev in m.attributes["@events"].items():
            ea = ev.attributes
            for pi, page in enumerate(ea["@pages"]):
                g = page.attributes["@graphic"].attributes
                sprite = b2s(g["@character_name"])
                for kind, text in page_messages(page):
                    rows.append({
                        "map": mid,
                        "map_name": map_names.get(mid, ""),
                        "event": ea["@id"],
                        "event_name": b2s(ea["@name"]),
                        "page": pi,
                        "sprite": sprite,
                        "x": ea["@x"], "y": ea["@y"],
                        "kind": kind, "text": text,
                    })
    return rows


def load_jsonl_rows(path):
    """00-maps.jsonl → {map: [(k, v), ...]}"""
    per_map = defaultdict(list)
    cur = None
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if "map" in r and "n" in r:
            cur = r["map"]
            continue
        per_map[cur].append((r["k"], r["v"]))
    return per_map


SPEAKER_TAG = re.compile(r"^<b>([^<:]{1,40}):</b>")
ENDING = re.compile(r"(다|요|죠|까|니|네|라|자|해|어|아|지|오|소|세)\s*[.!?…]*\s*$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default=DEFAULT_GAME)
    ap.add_argument("--out", default=str(ROOT / "docs/research/map-speaker-join.jsonl.gz"))
    args = ap.parse_args()

    ev_rows = scan_maps(args.game)
    per_map = load_jsonl_rows(ROOT / "translate/ko/00-maps.jsonl")

    # 이벤트 텍스트 색인: (map, norm(text)) → 이벤트 문맥 목록
    idx = defaultdict(list)
    for r in ev_rows:
        idx[(r["map"], norm(r["text"]))].append(r)

    joined, missed = [], []
    for mid, pairs in per_map.items():
        for k, v in pairs:
            hits = idx.get((mid, norm(k)), [])
            row = {"map": mid, "k": k, "v": v}
            if hits:
                h = hits[0]
                row.update({
                    "map_name": h["map_name"], "event": h["event"],
                    "event_name": h["event_name"], "sprite": h["sprite"],
                    "x": h["x"], "y": h["y"], "kind": h["kind"],
                    "n_hits": len(hits),
                })
                joined.append(row)
            else:
                missed.append(row)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if out.suffix == ".gz" else open
    with opener(out, "wt", encoding="utf-8") as f:
        for r in joined + missed:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    total = len(joined) + len(missed)
    print(f"이벤트에서 뽑은 표시 문자열: {len(ev_rows)}")
    print(f"jsonl 대사 행: {total} / 조인 {len(joined)} ({len(joined)/total:.1%}) / 미조인 {len(missed)}")

    untag = [r for r in joined if not SPEAKER_TAG.match(r["k"])]
    print(f"조인된 무태그: {len(untag)}")
    print("\n[스프라이트 상위 30 (무태그 조인분)]")
    for s, c in Counter(r["sprite"] for r in untag).most_common(30):
        print(f"  {c:5}  {s or '(없음)'}")
    print("\n[무태그 한국어 어미 분포]")
    for e, c in Counter(
        (ENDING.search(r["v"].strip()) or [None]) and (m.group(1) if (m := ENDING.search(r["v"].strip())) else "(기타)")
        for r in untag
    ).most_common(15):
        print(f"  {c:5}  {e}")
    print("\n[미조인 표본 10]")
    for r in missed[:10]:
        print(f"  map{r['map']:>3} | {r['k'][:70]!r}")


if __name__ == "__main__":
    main()
