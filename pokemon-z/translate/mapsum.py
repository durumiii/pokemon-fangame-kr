# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Per-map event summary: page conditions, switch ops, transfers, battles, first texts."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "vendor"))
from datread import load

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")
sysd = load(open(GAME / "System.rxdata", "rb")).attributes
SW = [x.decode("utf-8", "replace") if isinstance(x, (bytes, bytearray)) else str(x) for x in sysd["@switches"]]
VAR = [x.decode("utf-8", "replace") if isinstance(x, (bytes, bytearray)) else str(x) for x in sysd["@variables"]]


def b2s(v):
    return bytes(v).decode("utf-8", "replace") if isinstance(v, (bytes, bytearray)) else str(v)


def swn(i):
    return f"{i}:{SW[i] if 0 <= i < len(SW) else '?'}"


def varn(i):
    return f"{i}:{VAR[i] if 0 <= i < len(VAR) else '?'}"


for mapno in [int(x) for x in sys.argv[1:]]:
    m = load(open(GAME / f"Map{mapno:03d}.rxdata", "rb"))
    print(f"##### Map{mapno}")
    for eid, ev in sorted(m.attributes["@events"].items()):
        a = ev.attributes
        print(f"-- ev{eid} '{b2s(a['@name'])}' @({a['@x']},{a['@y']})")
        for pi, p in enumerate(a["@pages"]):
            c = p.attributes["@condition"].attributes
            cond = []
            if c["@switch1_valid"]: cond.append(swn(c["@switch1_id"]))
            if c["@switch2_valid"]: cond.append(swn(c["@switch2_id"]))
            if c["@variable_valid"]: cond.append(f"{varn(c['@variable_id'])}>={c['@variable_value']}")
            if c["@self_switch_valid"]: cond.append(f"self{b2s(c['@self_switch_ch'])}")
            notes = []
            txt = []
            for cmd in p.attributes["@list"]:
                ca = cmd.attributes
                code, params = ca["@code"], ca["@parameters"]
                if code == 101:
                    txt.append(b2s(params[0]))
                elif code == 121:
                    notes.append(f"SET[{','.join(swn(i) for i in range(params[0], params[1]+1))}]={'ON' if params[2]==0 else 'OFF'}")
                elif code == 122:
                    notes.append(f"VAR[{','.join(varn(i) for i in range(params[0], params[1]+1))}] op{params[2]} {[b2s(x) for x in params[4:]]}")
                elif code == 111 and params[0] == 0:
                    notes.append(f"IFSW {swn(params[1])}=={'ON' if params[2]==0 else 'OFF'}")
                elif code == 111 and params[0] == 1:
                    notes.append(f"IFVAR {varn(params[1])} {[b2s(x) for x in params[2:]]}")
                elif code == 111 and params[0] == 12:
                    notes.append(f"IFSCRIPT {b2s(params[1])[:120]}")
                elif code in (355, 655):
                    s = b2s(params[0])
                    if any(k in s for k in ("pbTrainerBattle", "Item", "switches", "variables", "pbWildBattle", "Ending", "credit")):
                        notes.append(f"SCRIPT {s[:140]}")
                elif code == 201:
                    notes.append(f"TRANSFER map{params[1]} ({params[2]},{params[3]})")
                elif code == 103:
                    notes.append(f"NUMINPUT {varn(params[0])} digits={params[1]}")
                elif code == 126:
                    notes.append(f"GIVEITEM {params}")
            print(f"   pg{pi} cond=[{' & '.join(cond) or '-'}] trig={p.attributes['@trigger']}")
            for n in notes:
                print(f"      {n}")
            for t in txt[:3]:
                print(f"      TXT {t[:110]}")
