# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Z-53 이행 1단계 채점표 — 0단계 파일 다섯에서 번역표 24절을 역생성해 현행 정본과 대조한다.

목표는 차이 0. 차이가 있으면 절별 건수와 예시 다섯을 낸다.

usage: uv run translate/stage0/diff.py [--write <디렉터리>]
"""
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    EMPTY_SECS, KO, OUT, dump_jsonl, ko_file, read_jsonl,
)

SHARED_RE = re.compile(r"^m\d+\.s\d+$")
MAP_ID_RE = re.compile(r"^m(\d+)\.")


def resolve(val, msgs, seen=()):
    """참조를 따라 실제 문자열까지 간다."""
    while isinstance(val, dict) and "ref" in val:
        r = val["ref"]
        assert r not in seen, f"참조 순환: {r}"
        seen = (*seen, r)
        val = msgs[r]["val"]
    assert isinstance(val, str), f"값이 문자열이 아니다: {val!r}"
    return val


def rebuild():
    """다섯 파일 → {파일 이름: [레코드, ...]}"""
    sites = read_jsonl(OUT / "sites.jsonl")
    msgs = {m["id"]: m for m in read_jsonl(OUT / "messages.jsonl")}
    layout = yaml.safe_load((OUT / "axes.yaml").read_text(encoding="utf-8"))["layout"]

    out = {}

    # 맵 절 — 자리 순서가 곧 줄 순서이고, 같은 공유 항목을 가리키는 자리들이 한 줄이다.
    by_map = {}
    for s in sites:
        if s["apply"] != "map":
            continue
        mi = int(MAP_ID_RE.match(s["id"]).group(1))
        by_map.setdefault(mi, []).append(s)
    rows = []
    for mi in range(layout["maps"]):
        body, done = [], set()
        for s in by_map.get(mi, ()):
            v = msgs[s["id"]]["val"]
            if isinstance(v, dict) and SHARED_RE.match(v.get("ref", "")):
                if v["ref"] in done:
                    continue
                done.add(v["ref"])
            body.append({"k": s["src"], "v": resolve(v, msgs)})
        rows.append({"map": mi, "n": len(body)})
        rows.extend(body)
    out["00-maps.jsonl"] = rows

    # 좌표 열쇠
    loc = []
    for s in sites:
        if s["apply"] != "krloc":
            continue
        mi, ev, cmd = map(int, re.match(r"^loc\.m(\d+)\.e(\d+)\.c(\d+)$", s["id"]).groups())
        m = msgs[s["id"]]
        r = {"map": mi, "event": ev, "cmd": cmd, "k": s["src"], "v": resolve(m["val"], msgs)}
        if "why" in m:
            r["왜"] = m["why"]
        loc.append(r)
    out["00-maps.loc.jsonl"] = loc

    # 번호로 서는 절 · 원문 키로 서는 절
    for s in sites:
        m = re.match(r"^s(\d+)\.(i|k)", s["id"])
        if not m:
            continue
        sec = int(m.group(1))
        name = ko_file(sec).name
        v = resolve(msgs[s["id"]]["val"], msgs)
        if m.group(2) == "i":
            r = {"i": int(s["id"].split(".i")[1]), "v": v}
            if "src" in s:
                r["es"] = s["src"]
        else:
            r = {"k": s["src"], "v": v}
        out.setdefault(name, []).append(r)
    for sec in EMPTY_SECS:
        out.setdefault(ko_file(sec).name, [])
    return out


def main():
    built = rebuild()
    write_to = None
    if "--write" in sys.argv:
        write_to = Path(sys.argv[sys.argv.index("--write") + 1])
        write_to.mkdir(parents=True, exist_ok=True)

    total = 0
    for name, rows in sorted(built.items()):
        if write_to:
            dump_jsonl(write_to / name, rows)
        cur = read_jsonl(KO / name)
        diffs = []
        for i in range(max(len(rows), len(cur))):
            a = rows[i] if i < len(rows) else None
            b = cur[i] if i < len(cur) else None
            if a != b:
                diffs.append((i, a, b))
        # 바이트까지 같은지도 본다 — 레코드가 같아도 직렬화 꼴이 다를 수 있다.
        made = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
        same_bytes = made == (KO / name).read_text(encoding="utf-8")
        total += len(diffs)
        mark = "OK " if not diffs and same_bytes else "차이"
        note = "" if same_bytes else "  (레코드는 같으나 바이트가 다름)" if not diffs else ""
        print(f"{mark} {name}: 레코드 {len(rows):,}줄 · 차이 {len(diffs)}건{note}")
        for i, a, b in diffs[:5]:
            print(f"     [{i}] 역생성={json.dumps(a, ensure_ascii=False)[:160]}")
            print(f"          현행  ={json.dumps(b, ensure_ascii=False)[:160]}")
    print(f"\n합계 차이 {total}건")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
