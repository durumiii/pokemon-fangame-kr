# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Dump RPG Maker XP event pages: commands, page conditions, switch/var ops."""
import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "vendor"))
from datread import load

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")


def b2s(v):
    if isinstance(v, (bytes, bytearray)):
        return bytes(v).decode("utf-8", "replace")
    return str(v)


def sysnames():
    sysd = load(open(GAME / "System.rxdata", "rb"))
    a = sysd.attributes
    sw = [b2s(x) for x in a["@switches"]]
    var = [b2s(x) for x in a["@variables"]]
    return sw, var


def loadmap(n):
    return load(open(GAME / f"Map{n:03d}.rxdata", "rb"))


def pagecond(p):
    c = p.attributes["@condition"].attributes
    out = []
    if c["@switch1_valid"]:
        out.append(f"switch1={c['@switch1_id']}")
    if c["@switch2_valid"]:
        out.append(f"switch2={c['@switch2_id']}")
    if c["@variable_valid"]:
        out.append(f"var{c['@variable_id']}>={c['@variable_value']}")
    if c["@self_switch_valid"]:
        out.append(f"selfswitch={b2s(c['@self_switch_ch'])}")
    return ", ".join(out) or "(none)"


def dumppage(p, sw, var, indent=0):
    lines = []
    for cmd in p.attributes["@list"]:
        ca = cmd.attributes
        code, params, ind = ca["@code"], ca["@parameters"], ca["@indent"]
        ps = [b2s(x) if isinstance(x, (bytes, bytearray)) else x for x in params]
        pre = "  " * ind
        if code in (101, 401):
            lines.append(f"{pre}TXT {ps[0]!r}")
        elif code == 102:
            lines.append(f"{pre}CHOICE {[b2s(c) for c in params[0]]}")
        elif code == 121:
            s, e, v = params[0], params[1], params[2]
            names = "; ".join(f"{i}:{sw[i] if i < len(sw) else '?'}" for i in range(s, e + 1))
            lines.append(f"{pre}SWITCH {'ON' if v == 0 else 'OFF'} [{names}]")
        elif code == 122:
            s, e = params[0], params[1]
            names = "; ".join(f"{i}:{var[i] if i < len(var) else '?'}" for i in range(s, e + 1))
            lines.append(f"{pre}VAR {names} op={params[2]} type={params[3]} operand={ps[4:]}")
        elif code == 111:
            t = params[0]
            if t == 0:
                i = params[1]
                lines.append(f"{pre}IF switch {i}:{sw[i] if i<len(sw) else '?'} == {'ON' if params[2]==0 else 'OFF'}")
            elif t == 1:
                i = params[1]
                lines.append(f"{pre}IF var {i}:{var[i] if i<len(var) else '?'} op{params[4]} {ps[2:]}")
            elif t == 2:
                lines.append(f"{pre}IF selfswitch {b2s(params[1])} == {'ON' if params[2]==0 else 'OFF'}")
            elif t == 12:
                lines.append(f"{pre}IF script: {ps[1]}")
            else:
                lines.append(f"{pre}IF type={t} {ps[1:]}")
        elif code == 411:
            lines.append(f"{pre}ELSE")
        elif code == 412:
            lines.append(f"{pre}END")
        elif code == 355 or code == 655:
            lines.append(f"{pre}SCRIPT {ps[0]}")
        elif code == 108 or code == 408:
            lines.append(f"{pre}# {ps[0]}")
        elif code == 126:
            lines.append(f"{pre}ITEM {ps}")
        elif code == 201:
            lines.append(f"{pre}TRANSFER {ps}")
        elif code == 0:
            pass
        else:
            lines.append(f"{pre}[{code}] {ps}")
    return lines


if __name__ == "__main__":
    sw, var = sysnames()
    mapno, evno = int(sys.argv[1]), int(sys.argv[2])
    m = loadmap(mapno)
    events = m.attributes["@events"]
    ev = events[evno]
    print(f"=== Map{mapno} Event{evno} name={b2s(ev.attributes['@name'])} x={ev.attributes['@x']} y={ev.attributes['@y']}")
    for i, p in enumerate(ev.attributes["@pages"]):
        print(f"--- page {i} cond: {pagecond(p)} trigger={p.attributes['@trigger']}")
        for l in dumppage(p, sw, var):
            print("   " + l)
