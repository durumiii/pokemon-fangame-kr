# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Scan all maps + common events for every use of given switch/variable ids."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "vendor"))
from datread import load

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")
SW = set(int(x) for x in sys.argv[1].split(",")) if len(sys.argv) > 1 else set()
VARS = set(int(x) for x in sys.argv[2].split(",")) if len(sys.argv) > 2 else set()


def b2s(v):
    if isinstance(v, (bytes, bytearray)):
        return bytes(v).decode("utf-8", "replace")
    return str(v)


def scan_list(lst, where, out):
    for cmd in lst:
        ca = cmd.attributes
        code, params = ca["@code"], ca["@parameters"]
        if code == 121 and any(i in SW for i in range(params[0], params[1] + 1)):
            out.append({"where": where, "kind": "set_switch", "range": [params[0], params[1]], "value": "ON" if params[2] == 0 else "OFF"})
        elif code == 122 and any(i in VARS for i in range(params[0], params[1] + 1)):
            out.append({"where": where, "kind": "set_var", "range": [params[0], params[1]], "params": [b2s(p) for p in params[2:]]})
        elif code == 111:
            t = params[0]
            if t == 0 and params[1] in SW:
                out.append({"where": where, "kind": "if_switch", "id": params[1], "want": "ON" if params[2] == 0 else "OFF"})
            elif t == 1 and params[1] in VARS:
                out.append({"where": where, "kind": "if_var", "id": params[1], "params": [b2s(p) for p in params[2:]]})
        elif code in (355, 655, 111) :
            s = b2s(params[-1]) if params else ""
            for i in SW:
                if f"switches[{i}]" in s:
                    out.append({"where": where, "kind": "script_switch", "id": i, "text": s})
            for i in VARS:
                if f"variables[{i}]" in s:
                    out.append({"where": where, "kind": "script_var", "id": i, "text": s})


out = []
# common events
ces = load(open(GAME / "CommonEvents.rxdata", "rb"))
for i, ce in enumerate(ces):
    if ce is None:
        continue
    a = ce.attributes
    name = b2s(a["@name"])
    trig = a["@trigger"]
    cond_sw = a["@switch_id"]
    if cond_sw in SW and trig != 0:
        out.append({"where": f"CommonEvent{i}:{name}", "kind": "ce_condition_switch", "id": cond_sw, "trigger": trig})
    scan_list(a["@list"], f"CommonEvent{i}:{name}", out)

for f in sorted(GAME.glob("Map[0-9][0-9][0-9].rxdata")):
    n = int(f.stem[3:])
    try:
        m = load(open(f, "rb"))
    except Exception as e:
        out.append({"where": f"Map{n}", "kind": "ERROR", "text": str(e)})
        continue
    for eid, ev in m.attributes["@events"].items():
        a = ev.attributes
        ename = b2s(a["@name"])
        for pi, p in enumerate(a["@pages"]):
            c = p.attributes["@condition"].attributes
            w = f"Map{n}/ev{eid}({ename})/pg{pi}"
            if c["@switch1_valid"] and c["@switch1_id"] in SW:
                out.append({"where": w, "kind": "page_cond_switch", "id": c["@switch1_id"]})
            if c["@switch2_valid"] and c["@switch2_id"] in SW:
                out.append({"where": w, "kind": "page_cond_switch2", "id": c["@switch2_id"]})
            if c["@variable_valid"] and c["@variable_id"] in VARS:
                out.append({"where": w, "kind": "page_cond_var", "id": c["@variable_id"], "value": c["@variable_value"]})
            scan_list(p.attributes["@list"], w, out)

for o in out:
    print(json.dumps(o, ensure_ascii=False))
