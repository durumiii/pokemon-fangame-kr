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
    EMPTY_SECS, KO, OUT, dump_jsonl, ko_file, read_jsonl, read_overrides,
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


def rebuild(d=OUT):
    """다섯 파일 → ({파일 이름: [레코드, ...]}, {파일 이름: [그 줄을 낸 자리 id, ...]}, 값 표)

    자리 id를 줄마다 함께 내는 것은 차이가 났을 때 「어느 자리가 냈나」를 되짚기 위해서다.
    맵 머리 줄처럼 자리가 없는 줄은 None.
    """
    sites = read_jsonl(d / "sites.jsonl")
    msgs = {m["id"]: m for m in read_jsonl(d / "messages.jsonl")}
    layout = yaml.safe_load((d / "axes.yaml").read_text(encoding="utf-8"))["layout"]

    out, owner = {}, {}

    # 맵 절 — 자리 순서가 곧 줄 순서이고, 같은 공유 항목을 가리키는 자리들이 한 줄이다.
    by_map = {}
    for s in sites:
        if s["apply"] != "map":
            continue
        mi = int(MAP_ID_RE.match(s["id"]).group(1))
        by_map.setdefault(mi, []).append(s)
    rows, rids = [], []
    for mi in range(layout["maps"]):
        body, bids, done = [], [], set()
        for s in by_map.get(mi, ()):
            v = msgs[s["id"]]["val"]
            if isinstance(v, dict) and SHARED_RE.match(v.get("ref", "")):
                if v["ref"] in done:
                    continue
                done.add(v["ref"])
            body.append({"k": s["src"], "v": resolve(v, msgs)})
            bids.append(s["id"])
        rows.append({"map": mi, "n": len(body)})
        rids.append(None)
        rows.extend(body)
        rids.extend(bids)
    out["00-maps.jsonl"] = rows
    owner["00-maps.jsonl"] = rids

    # 좌표 열쇠
    loc, locids = [], []
    for s in sites:
        if s["apply"] != "krloc":
            continue
        mi, ev, cmd = map(int, re.match(r"^loc\.m(\d+)\.e(\d+)\.c(\d+)$", s["id"]).groups())
        m = msgs[s["id"]]
        r = {"map": mi, "event": ev, "cmd": cmd, "k": s["src"], "v": resolve(m["val"], msgs)}
        if "why" in m:
            r["왜"] = m["why"]
        loc.append(r)
        locids.append(s["id"])
    out["00-maps.loc.jsonl"] = loc
    owner["00-maps.loc.jsonl"] = locids

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
        owner.setdefault(name, []).append(s["id"])
    for sec in EMPTY_SECS:
        out.setdefault(ko_file(sec).name, [])
        owner.setdefault(ko_file(sec).name, [])
    return out, owner, msgs


def tainted_ids(msgs, ovr):
    """overrides가 건드린 id 하나가 실제로 물들이는 자리 id 집합.

    값을 공유 항목이나 통일 참조에서 갈면 그것을 가리키는 자리가 전부 달라진다 —
    참조를 거꾸로 타고 번져 나간다.
    """
    hit = {o["id"] for o in ovr}
    if not hit:
        return hit
    back = {}
    for m in msgs.values():
        v = m["val"]
        if isinstance(v, dict) and "ref" in v:
            back.setdefault(v["ref"], []).append(m["id"])
    out, todo = set(hit), list(hit)
    while todo:
        cur = todo.pop()
        for src in back.get(cur, ()):
            if src not in out:
                out.add(src)
                todo.append(src)
    return out


def compare(built, owner, tainted=frozenset(), write_to=None, show=5):
    """역생성 결과를 현행 정본과 대조. 반환 (overrides 유래 건수, 그 밖의 건수).

    overrides가 값을 갈면 역생성이 ko와 달라지는데 그건 결함이 아니라 정본이 ko보다
    앞선 상태다. 그 밖의 차이(M)만 0이어야 한다.
    """
    from_ovr = other = 0
    for name, rows in sorted(built.items()):
        ids = owner.get(name, [])
        cur = read_jsonl(KO / name)
        diffs = []
        for i in range(max(len(rows), len(cur))):
            a = rows[i] if i < len(rows) else None
            b = cur[i] if i < len(cur) else None
            if a != b:
                sid = ids[i] if i < len(ids) else None
                diffs.append((i, a, b, sid in tainted))
        # 바이트까지 같은지도 본다 — 레코드가 같아도 직렬화 꼴이 다를 수 있다.
        made = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
        same_bytes = made == (KO / name).read_text(encoding="utf-8")
        n_ovr = sum(1 for *_, o in diffs if o)
        from_ovr += n_ovr
        other += len(diffs) - n_ovr
        mark = "OK " if not diffs and same_bytes else "차이"
        note = "" if same_bytes else "  (레코드는 같으나 바이트가 다름)" if not diffs else ""
        tail = f" (overrides 유래 {n_ovr} · 그 밖 {len(diffs) - n_ovr})" if n_ovr else ""
        print(f"{mark} {name}: 레코드 {len(rows):,}줄 · 차이 {len(diffs)}건{tail}{note}")
        for i, a, b, o in diffs[:show]:
            print(f"     [{i}]{' [overrides 유래]' if o else ''} "
                  f"자리={ids[i] if i < len(ids) else '—'}")
            print(f"          역생성={json.dumps(a, ensure_ascii=False)[:160]}")
            print(f"          현행  ={json.dumps(b, ensure_ascii=False)[:160]}")
        # 쓰기는 대조 뒤에 — 먼저 쓰면 제 산출과 대조해 「차이 0」으로 찍힌다
        # (2026-08-18 emit --write 첫 실전에서 실측). 정본 자리에 바이트가 같은 것을
        # 다시 앉히지는 않는다 — 손 안 댄 절까지 매번 재작성되는 것을 없앤다.
        # 다른 디렉터리로 낼 때는 그 디렉터리가 온전해야 하므로 전부 쓴다.
        if write_to and not (same_bytes and write_to == KO):
            (write_to / name).write_text(made, encoding="utf-8")
    return from_ovr, other


def main():
    built, owner, msgs = rebuild()
    write_to = None
    if "--write" in sys.argv:
        write_to = Path(sys.argv[sys.argv.index("--write") + 1])
        write_to.mkdir(parents=True, exist_ok=True)

    tainted = tainted_ids(msgs, read_overrides())
    from_ovr, other = compare(built, owner, tainted, write_to)
    print(f"\n합계 차이 {from_ovr + other}건 — overrides 유래 {from_ovr}건 · 그 밖 {other}건")
    return 1 if other else 0


if __name__ == "__main__":
    sys.exit(main())
