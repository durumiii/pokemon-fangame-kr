# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""전 맵 + 공통이벤트의 **모든** 이벤트 페이지를 덤프(스크립트 + 구조 신호).

산출 jsonl 한 줄 = 페이지 하나. 코드 302(상점)·314(전체회복)·102(선택지)·201(전이) 유무 포함.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "vendor"))
from datread import load

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")


def b2s(v):
    return bytes(v).decode("utf-8", "replace") if isinstance(v, (bytes, bytearray)) else str(v)


mapnames = {k: b2s(v.attributes["@name"]) for k, v in load(open(GAME / "MapInfos.rxdata", "rb")).items()}
mapnames[0] = "(공통 이벤트)"


def page_info(lst):
    scripts, buf, codes, txt = [], None, set(), []
    for cmd in lst:
        ca = cmd.attributes
        code, params = ca["@code"], ca["@parameters"]
        codes.add(code)
        if code == 355:
            if buf is not None:
                scripts.append(buf)
            buf = b2s(params[0])
        elif code == 655:
            buf = (buf or "") + "\n" + b2s(params[0])
        else:
            if buf is not None:
                scripts.append(buf)
                buf = None
            if code == 101:
                txt.append(b2s(params[0]))
            elif code == 111 and params[0] == 12:
                scripts.append(b2s(params[1]))
    if buf is not None:
        scripts.append(buf)
    return scripts, codes, txt


out = sys.stdout


def emit(mapno, eid, ename, pi, trigger, lst):
    scripts, codes, txt = page_info(lst)
    out.write(json.dumps({
        "map": mapno, "map_name": mapnames.get(mapno, "?"), "event": eid, "event_name": ename,
        "page": pi, "trigger": trigger, "scripts": scripts,
        "shop": 302 in codes, "recover": 314 in codes, "choice": 102 in codes, "transfer": 201 in codes,
        "n_cmd": len(lst), "txt": txt[:3], "codes": sorted(codes),
    }, ensure_ascii=False) + "\n")


for i, ce in enumerate(load(open(GAME / "CommonEvents.rxdata", "rb"))):
    if ce is None:
        continue
    a = ce.attributes
    emit(0, i, b2s(a["@name"]), 0, a["@trigger"], a["@list"])

for f in sorted(GAME.glob("Map[0-9][0-9][0-9].rxdata")):
    n = int(f.stem[3:])
    m = load(open(f, "rb"))
    for eid, ev in sorted(m.attributes["@events"].items()):
        a = ev.attributes
        for pi, p in enumerate(a["@pages"]):
            emit(n, eid, b2s(a["@name"]), pi, p.attributes["@trigger"], p.attributes["@list"])
