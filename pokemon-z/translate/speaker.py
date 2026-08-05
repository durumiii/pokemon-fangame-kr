# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""화자 귀속 — 이벤트 명령 순서로 「이 대사는 누구 말인가」를 계산한다.

이름표(`<b>이름:</b>`)가 붙은 줄은 그대로 읽고, 붙지 않은 줄은 **같은 이벤트 페이지
안에서 분기 깊이가 같은 동안** 앞 이름표를 물려받는다. 답은 원본 이벤트 데이터에
이미 들어 있다 — 명령 순서(cmd)와 조건 분기 깊이(@indent)가 그것이다.

옛 방식(`mapscan.py` 조인표 + 이벤트 스프라이트)은 이 둘을 버려서, 컷신처럼 그림은
하나인데 화자가 여럿인 자리를 통째로 한 사람으로 봤다. 이름표 없는 줄 4,265행 중
4분의 3에서 그림과 실제 화자가 어긋났고, 962행이 그 판정 위에서 다시 쓰였다.

usage:
  uv run translate/speaker.py scan          이벤트를 훑어 귀속표를 만든다
                                            → docs/research/speaker-attr.jsonl.gz
  uv run translate/speaker.py who <검색어>   원문·번역에 그 말이 든 줄의 화자를 보인다
  uv run translate/speaker.py lines <이름>   그 인물의 대사를 전부 뽑는다(어투 감사용)
  uv run translate/speaker.py stats         판정 근거별 집계
  uv run translate/speaker.py selftest      정답을 아는 자리로 채점한다

귀속 근거(`how`)는 다섯이다:
  태그        그 줄에 이름표가 붙어 있다 — 확실
  상속        같은 페이지·같은 분기 깊이에서 앞 이름표를 물려받았다
  분기다름    분기 깊이를 넘어 물려받았다 — 미더운 정도가 떨어진다
  명단1       페이지에 이름표가 한 종뿐이라 그 사람으로 본다
  그림        페이지에 이름표가 하나도 없다 — NPC 혼자 말하는 자리라 이벤트 그림이 화자다
  미상        이름표도 그림도 없다 — 지문이거나 시스템 문구
  선택지      주인공의 선택지. 주인공은 대사를 하지 않아 이름표가 붙지 않는다
"""
import gzip
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from rubymarshal.reader import load  # noqa: E402

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")
OUT = HERE.parent / "docs" / "research" / "speaker-attr.jsonl.gz"
KO_MAPS = HERE / "ko" / "00-maps.jsonl"

TAG = re.compile(r"^(?:\\c\[\d+\])?<b>([^<:]{1,24}):</b>")

# 정답을 아는 자리 — 유지자가 실기·제보로 확정한 것들 (원문 조각, 기대 화자, 출처)
KNOWN = [
    ("Para nosotros, se parecen mucho a las letras", "Mirra", "맵119 손수정"),
    ("En este sorprendente lugar enterraban a los druidas", "Mirra", "맵119 손수정"),
    ("He tratado con esmero de encontrar a un intérprete", "Mirra", "맵119 손수정"),
    ("Los druidas son la primera civilización", "Crisanto", "맵119 손수정"),
    ("Pero... ya nos han engañado antes", "Crisanto", "맵113 제보"),
    ("Un Pokémon estaba vivo y el otro", "Crisanto", "맵111 제보(누빌라 오판)"),
    ("¿Y <b>Lanto</b> es quien ha financiado", "Crisanto", "맵111 제보"),
]


def b2s(v):
    return v.decode("utf-8", errors="replace") if isinstance(v, bytes) else str(v)


def page_messages(cmdlist):
    """(cmd, indent, kind, text) — 101/401은 한 메시지로 잇고 102는 선택지로 편다.

    cmd는 명령 인덱스, indent는 조건 분기 깊이다. 이 둘이 화자 상속의 전부다.
    """
    out, buf, bi, bd = [], None, None, 0
    for i, cmd in enumerate(cmdlist):
        ca = cmd.attributes
        code, params = ca["@code"], ca["@parameters"]
        if code == 101:
            if buf is not None:
                out.append((bi, bd, "text", buf))
            buf, bi, bd = b2s(params[0]), i, ca["@indent"]
        elif code == 401 and buf is not None:
            buf += "\n" + b2s(params[0])
        else:
            if buf is not None:
                out.append((bi, bd, "text", buf))
                buf = None
            if code == 102:
                for j, c in enumerate(params[0]):
                    out.append((i + j / 100, ca["@indent"], "choice", b2s(c)))
    if buf is not None:
        out.append((bi, bd, "text", buf))
    return out


def attribute(msgs, sprite=""):
    """페이지 하나의 메시지 목록에 화자를 붙인다. msgs는 cmd 순으로 정렬돼 있어야 한다.

    이름표가 하나도 없는 페이지는 **NPC 하나가 혼자 말하는 자리**이므로 이벤트
    그림이 곧 화자다 — 옛 방식이 이 구간에서 맞았던 이유이기도 하다. 그림도 없으면
    화자를 못 정한다(대개 지문·시스템 문구).
    """
    cast = {m for _, _, _, t in msgs if (m := (TAG.match(t).group(1) if TAG.match(t) else None))}
    cur = cur_ind = None
    for cmdi, ind, kind, text in msgs:
        m = TAG.match(text)
        if m:
            cur, cur_ind = m.group(1), ind
            who, how = cur, "태그"
        elif kind == "choice":
            who, how = "", "선택지"
        elif cur is not None and ind == cur_ind:
            who, how = cur, "상속"
        elif cur is not None:
            who, how = cur, "분기다름"
        elif len(cast) == 1:
            who, how = next(iter(cast)), "명단1"
        elif not cast and sprite:
            who, how = sprite, "그림"
        else:
            who, how = "", "미상"
        yield cmdi, ind, kind, text, who, how, sorted(cast)


def scan():
    rows = []
    infos = load(open(GAME / "MapInfos.rxdata", "rb"))
    names = {k: b2s(v.attributes["@name"]) for k, v in infos.items()}

    def emit(mid, mname, eid, ename, page, sprite, cmdlist):
        msgs = page_messages(cmdlist)
        for cmdi, ind, kind, text, who, how, cast in attribute(msgs, sprite):
            rows.append({"map": mid, "map_name": mname, "event": eid, "event_name": ename,
                         "page": page, "cmd": cmdi, "ind": ind, "sprite": sprite,
                         "kind": kind, "who": who, "how": how, "cast": cast, "k": text})

    for ce in load(open(GAME / "CommonEvents.rxdata", "rb")):
        if ce is None:
            continue
        ca = ce.attributes
        emit(0, "(공통 이벤트)", ca["@id"], b2s(ca["@name"]), 0, "", ca["@list"])

    for p in sorted(GAME.glob("Map[0-9][0-9][0-9].rxdata")):
        mid = int(p.stem[3:])
        m = load(open(p, "rb"))
        for ev in m.attributes["@events"].values():
            ea = ev.attributes
            for pi, page in enumerate(ea["@pages"]):
                g = page.attributes["@graphic"].attributes
                emit(mid, names.get(mid, ""), ea["@id"], b2s(ea["@name"]), pi,
                     b2s(g["@character_name"]), page.attributes["@list"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT, "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)}행 → {OUT.relative_to(HERE.parent)}")
    return rows


def load_attr():
    if not OUT.exists():
        sys.exit(f"귀속표가 없어요 — 먼저 만드세요: uv run {Path(__file__).name} scan")
    with gzip.open(OUT, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def ko_index():
    """원문 → 현행 한국어. 맵 대사 정본에서 뽑는다."""
    idx = {}
    for line in KO_MAPS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "map" not in r:
            idx.setdefault(r["k"].strip(), r["v"])
    return idx


def show(rows, ko, limit=None):
    for i, r in enumerate(rows):
        if limit and i >= limit:
            print(f"… 그 밖 {len(rows) - limit}행")
            break
        v = ko.get(r["k"].strip(), "")
        print(f"맵{r['map']}:ev{r['event']}:p{r['page']}:cmd{r['cmd']} "
              f"[{r['how']}] {r['who'] or '—'}")
        print(f"    {v or r['k']}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]

    if cmd == "scan":
        scan()
    elif cmd == "stats":
        rows = load_attr()
        import collections
        c = collections.Counter(r["how"] for r in rows)
        print(f"총 {len(rows)}행")
        for k, n in c.most_common():
            print(f"  {k:6s} {n:6d}")
    elif cmd == "who" and len(sys.argv) > 2:
        q = sys.argv[2]
        rows, ko = load_attr(), ko_index()
        hit = [r for r in rows
               if q in r["k"] or q in ko.get(r["k"].strip(), "")]
        print(f"{len(hit)}행")
        show(hit, ko, 40)
    elif cmd == "lines" and len(sys.argv) > 2:
        name = sys.argv[2]
        rows, ko = load_attr(), ko_index()
        hit = [r for r in rows if name.lower() in (r["who"] or "").lower()]
        import collections
        print(f"{name}: {len(hit)}행 · 근거별 "
              f"{dict(collections.Counter(r['how'] for r in hit))}")
        show(hit, ko)
    elif cmd == "selftest":
        rows = load_attr()
        ok = bad = 0
        for frag, want, src in KNOWN:
            hit = next((r for r in rows if frag in r["k"]), None)
            if hit is None:
                print(f"[못찾음] {frag[:40]!r}")
                bad += 1
                continue
            mark = "O" if hit["who"] == want else "X"
            ok += hit["who"] == want
            bad += hit["who"] != want
            print(f"[{mark}] {want:10s} ← {hit['who']:10s} ({hit['how']}) "
                  f"맵{hit['map']} ev{hit['event']} · {src}")
        print(f"\n채점 {ok}/{ok + bad}")
        sys.exit(1 if bad else 0)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
