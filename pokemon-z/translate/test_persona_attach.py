# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""attach_personas의 안전장치 하나만 지킨다 — `uv run translate/test_persona_attach.py`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from batch_pages import attach_personas, personas  # noqa: E402


def row(sprite):
    return ({"sprite": sprite}, "who", "", "")


def go(cast, take):
    attach_personas(cast, take, {})
    return {x["name"]: x.get("persona") for x in cast}


per = personas()
assert "burguesow" in per and "flecha" not in per, "표가 사람 스프라이트만 담는다는 전제가 깨졌다"

# 혼자 쓰는 사람 스프라이트 → 붙는다
got = go([{"name": "A", "voice": ""}], [(*row("burguesow")[:1], "A", "", "")])
assert got["A"] and "신사" in got["A"], got

# 두 화자가 한 스프라이트를 나눠 쓰면 둘 다 안 붙는다 (p331-7-0 사례)
got = go([{"name": "A", "voice": ""}, {"name": "B", "voice": ""}],
         [({"sprite": "burguesow"}, "A", "", ""), ({"sprite": "burguesow"}, "B", "", "")])
assert got == {"A": None, "B": None}, got

# 사람이 아닌 연출용 스프라이트는 표에 없어 안 붙는다 (Bruja ← flecha 사례)
got = go([{"name": "A", "voice": ""}], [({"sprite": "flecha"}, "A", "", "")])
assert got == {"A": None}, got

# 이미 말투 지시가 있으면 건드리지 않는다
got = go([{"name": "A", "voice": "해요체"}], [({"sprite": "burguesow"}, "A", "", "")])
assert got == {"A": None}, got

print("ok")
