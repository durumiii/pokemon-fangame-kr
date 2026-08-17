# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""All map-transfer commands (code 201) whose destination is in TARGETS, across all maps."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "vendor"))
from datread import load

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")
TARGETS = set(int(x) for x in sys.argv[1].split(","))
sysd = load(open(GAME / "System.rxdata", "rb")).attributes
SW = [bytes(x).decode("utf-8", "replace") if isinstance(x, (bytes, bytearray)) else str(x) for x in sysd["@switches"]]


def b2s(v):
    return bytes(v).decode("utf-8", "replace") if isinstance(v, (bytes, bytearray)) else str(v)


for f in sorted(GAME.glob("Map[0-9][0-9][0-9].rxdata")):
    n = int(f.stem[3:])
    m = load(open(f, "rb"))
    for eid, ev in m.attributes["@events"].items():
        a = ev.attributes
        for pi, p in enumerate(a["@pages"]):
            c = p.attributes["@condition"].attributes
            cond = []
            if c["@switch1_valid"]:
                i = c["@switch1_id"]; cond.append(f"sw{i}:{SW[i] if i < len(SW) else '?'}")
            if c["@switch2_valid"]:
                i = c["@switch2_id"]; cond.append(f"sw{i}:{SW[i] if i < len(SW) else '?'}")
            if c["@variable_valid"]:
                cond.append(f"var{c['@variable_id']}>={c['@variable_value']}")
            if c["@self_switch_valid"]:
                cond.append("self" + b2s(c["@self_switch_ch"]))
            for cmd in p.attributes["@list"]:
                ca = cmd.attributes
                if ca["@code"] == 201 and ca["@parameters"][1] in TARGETS:
                    ps = ca["@parameters"]
                    print(f"Map{n}/ev{eid}({b2s(a['@name'])})/pg{pi} cond=[{'&'.join(cond) or '-'}] -> map{ps[1]} ({ps[2]},{ps[3]})")
