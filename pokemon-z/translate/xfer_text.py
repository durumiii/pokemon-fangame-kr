# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""전이 뒤에 뜨는 대사를 전수로 캔다 — Z-61의 재료, 지금은 회귀 시험대.

⚠ **이 도구가 세는 「도착 맵 정본 없음」은 2026-08-18부터 결함이 아니다.** 그때 조회
기준이 이벤트 소속 맵(`@map_id`)으로 바뀌어 이 줄들은 제 맵에서 찾아진다(Z-73 잔여,
`share/patch_intl.py`). 지금 이 수는 「전이 뒤에 말하는 자리가 몇이나 되나」를 재는
것이고, 고칠 자리의 수가 아니다. 값이 실제로 닿는지는 `정본_출발`이 답한다 — 그 칸이
거짓인 줄이 생기면 그것이 결함이다.

옛 병이 무엇이었나: 게임이 맵 대사를 **그 순간 플레이어가 서 있는 맵 id**로 조회하는데
정본은 그 대사가 적힌 이벤트가 놓인 맵에 등재돼 있어, 이벤트가 플레이어를 다른 맵으로
옮긴 뒤 말을 걸면 두 맵이 갈려 열쇠가 없고 원문이 그대로 화면에 떴다.

전 맵의 이벤트 페이지를 명령 순서대로 훑어, 다른 맵으로 가는 전이(코드 201) 뒤에 오는
대사·선택지(코드 101·401·102)를 모아 도착 맵에 정본 줄이 있는지 대조한다.

usage: uv run translate/xfer_text.py [산출.json]

⚠ 조건 분기를 모델에 안 넣었다 — 분기 한쪽에만 있는 전이도 그 뒤 전부를 도착 맵으로
세므로 결과는 **후보의 상한**이다. 자리마다 `evdump.py`로 페이지를 열어 확인해야 한다.
공통 이벤트(`CommonEvents.rxdata`)는 안 훑는다.

조사 경위: docs/log/research/2026-08-16-transfer-then-text.md
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from datread import load  # noqa: E402

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")
KO = HERE / "ko" / "00-maps.jsonl"

norm = lambda s: re.sub(r"\s+", " ", s).strip()  # noqa: E731


def b2s(v):
    return bytes(v).decode("utf-8", "replace") if isinstance(v, (bytes, bytearray)) else str(v)


def canon_keys():
    """(맵, 원문) 등재 집합."""
    keys, cur = set(), None
    for line in KO.open(encoding="utf-8"):
        d = json.loads(line)
        if "map" in d:
            cur = d["map"]
            continue
        keys.add((cur, norm(d["k"])))
    return keys


def main():
    canon = canon_keys()
    out = []
    for n in range(0, 600):
        f = GAME / f"Map{n:03d}.rxdata"
        if not f.exists():
            continue
        m = load(open(f, "rb"))
        for ev in m.attributes["@events"].values():
            ea = ev.attributes
            for pi, page in enumerate(ea["@pages"]):
                dest = None
                for cmd in page.attributes["@list"]:
                    ca = cmd.attributes
                    code, ps = ca["@code"], ca["@parameters"]
                    if code == 201:                      # 장소 이동
                        d = ps[1] if ps[0] == 0 else None
                        dest = d if (d is not None and d != n) else None
                    elif code in (101, 401, 102) and dest is not None:
                        texts = [b2s(ps[0])] if code in (101, 401) else [b2s(c) for c in ps[0]]
                        for t in texts:
                            k = norm(t)
                            if not k:
                                continue
                            out.append({"src_map": n, "dest_map": dest, "event": ea["@id"],
                                        "page": pi, "es": t,
                                        "정본_출발": (n, k) in canon,
                                        "정본_도착": (dest, k) in canon})
    miss = [r for r in out if r["정본_출발"] and not r["정본_도착"]]
    pages = {(r["src_map"], r["event"], r["page"]) for r in miss}
    orphan = [r for r in out if not r["정본_출발"]]
    print(f"전이 뒤 대사 {len(out)}행 · 도착 맵 정본 없음 {len(miss)}행(결함 아님, 머리말 참조)"
          f" · 이벤트 페이지 {len(pages)}개")
    print(f"⚠ 출발 맵에도 정본이 없는 줄: {len(orphan)}행 — 이 수가 0이 아니면 결함이다")
    for s, d, e, p in sorted({(r["src_map"], r["dest_map"], r["event"], r["page"]) for r in miss}):
        cnt = sum(1 for r in miss
                  if (r["src_map"], r["dest_map"], r["event"], r["page"]) == (s, d, e, p))
        print(f"  맵{s} ev{e} p{p} → 맵{d} : {cnt}행")
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"산출: {sys.argv[1]}")


if __name__ == "__main__":
    main()
