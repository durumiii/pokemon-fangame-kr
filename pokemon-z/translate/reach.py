# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""BFS reachability on an RMXP map, optionally blocking given tiles.

  uv run reach.py <mapno> <sx> <sy> [--block x,y ...]
prints whether each of the map's transfer events is reachable.
"""
import sys, struct
from collections import deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "vendor"))
from rubymarshal.reader import load as rload

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")


def b2s(v):
    return bytes(v).decode("utf-8", "replace") if isinstance(v, (bytes, bytearray)) else str(v)


def table(t):
    """RMXP Table -> (xs, ys, zs, list)"""
    raw = bytes(t._private_data)
    dim, xs, ys, zs, n = struct.unpack("<5i", raw[:20])
    vals = struct.unpack(f"<{n}H", raw[20:20 + n * 2])
    return xs, ys, zs, vals


mapno, sx, sy = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
blocked = set()
for a in sys.argv[4:]:
    x, y = a.split(",")
    blocked.add((int(x), int(y)))

m = rload(open(GAME / f"Map{mapno:03d}.rxdata", "rb"))
tid = m.attributes["@tileset_id"]
ts = rload(open(GAME / "Tilesets.rxdata", "rb"))[tid]
_, _, _, passages = table(ts.attributes["@passages"])
_, _, _, priorities = table(ts.attributes["@priorities"])
xs, ys, zs, data = table(m.attributes["@data"])


def tile(x, y, z):
    return data[x + y * xs + z * xs * ys]


def passable(x, y, bit):
    if not (0 <= x < xs and 0 <= y < ys):
        return False
    for z in (2, 1, 0):
        t = tile(x, y, z)
        p = passages[t] if t < len(passages) else 0
        pr = priorities[t] if t < len(priorities) else 0
        if p & bit != 0:
            return False
        if p & 0x0f == 0x0f:
            return False
        if pr == 0:
            return True
    return True


# events that block movement (priority 0 = same level, through false)
evblock = {}
for eid, ev in m.attributes["@events"].items():
    a = ev.attributes
    p = a["@pages"][0].attributes  # page 0 approximation
    if False:
        evblock[(a["@x"], a["@y"])] = eid

start = (sx, sy)
seen = {start}
q = deque([start])
DIRS = {2: (0, 1), 4: (-1, 0), 6: (1, 0), 8: (0, -1)}
while q:
    x, y = q.popleft()
    for d, (dx, dy) in DIRS.items():
        nx, ny = x + dx, y + dy
        if (nx, ny) in seen or (nx, ny) in blocked:
            continue
        bit_out = 1 << (d // 2 - 1)
        rev = {2: 8, 8: 2, 4: 6, 6: 4}[d]
        bit_in = 1 << (rev // 2 - 1)
        if passable(x, y, bit_out) and passable(nx, ny, bit_in):
            seen.add((nx, ny))
            q.append((nx, ny))

print(f"reachable tiles from {start} (blocking {sorted(blocked)}): {len(seen)}")
for eid, ev in sorted(m.attributes["@events"].items()):
    a = ev.attributes
    for pi, p in enumerate(a["@pages"]):
        for cmd in p.attributes["@list"]:
            ca = cmd.attributes
            if ca["@code"] == 201:
                ps = ca["@parameters"]
                pos = (a["@x"], a["@y"])
                near = any((pos[0]+dx, pos[1]+dy) in seen for dx in range(-2,3) for dy in range(-2,3))
                print(f"  ev{eid}({b2s(a['@name'])}) at {pos} pg{pi} -> map{ps[1]} ({ps[2]},{ps[3]}) : {'REACHABLE' if pos in seen else ('near' if near else 'no')}")
                break
