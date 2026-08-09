---
name: ruby-mod-hook-validation
description: "Test framework to verify Ruby mod patches target methods actually exist in game scripts"
user-invocable: false
origin: auto-extracted
---

# Ruby Mod Hook Validation: Silent Patch Failure Detection

**Extracted:** 2026-08-09  
**Context:** Pokémon Essentials modding, RPGXP game patching, version compatibility

## Problem

Ruby mods patch game classes via `alias_method`, `define_method`. If target method renamed in game update, patch silently fails — no error message:

```ruby
# my_mod.rb
alias_method :pbGraphicsUpdate_original, :pbGraphicsUpdate
# ↑ If method doesn't exist, fails silently, mod has no effect
```

**User experience:** Mod appears installed and active (mod.json listed), but doesn't work. No error to debug.

## Solution

Validate target method names against actual compiled game scripts using `rubymarshal`:

```python
# test_mod_hooks.py
import zlib
from pathlib import Path
import rubymarshal.reader as R

def extract_method_names(rxdata_path):
    """Extract all class#method names from Scripts.rxdata."""
    data = R.loads(Path(rxdata_path).read_bytes())
    methods = set()
    
    for script_id, script_name, script_code in data:
        class_name = str(script_name)
        src = zlib.decompress(bytes(script_code)).decode("utf-8", "replace")
        
        for line in src.split('\n'):
            line = line.strip()
            if line.startswith('def '):
                # Extract: "def method_name" or "def method_name(args)"
                method = line.split()[1].split('(')[0]
                methods.add(f"{class_name}#{method}")
    
    return methods

def test_battle_scene_speed_hooks():
    """Verify Battle Scene Speed mod targets exist."""
    game_methods = extract_method_names("/mnt/d/Game/Pokemon Z/V2.18/Data/Scripts.rxdata")
    
    required = {
        "PokeBattle_Scene#pbGraphicsUpdate",
        "PokeBattle_Scene#pbWaitMessage",
        "PokeBattle_Scene#pbDisplayMessage",
        "PokeBattle_Scene#pbDisplayPausedMessage",
        "PokeBattle_Scene#pbShowCommands",
        "PokeBattle_Scene#pbCommandMenuEx",
        "PokeBattle_Scene#pbFightMenu",
        "PokeBattle_Scene#pbChooseTarget",
        "PokeBattle_Scene#pbAnimationCore",
    }
    
    missing = required - game_methods
    assert not missing, f"Hooks not found: {missing}"
    
    print(f"✓ All {len(required)} mod targets verified")

if __name__ == "__main__":
    test_battle_scene_speed_hooks()
```

## Automation: Read Target List from mod.json

```python
import json

def test_mod_from_metadata():
    """Auto-read mod.json touches and validate."""
    mod = json.load(open("mod.json"))
    game_methods = extract_method_names("/path/to/Scripts.rxdata")
    
    if "touches" not in mod:
        print("⚠ No 'touches' in mod.json — skipping")
        return
    
    required = mod["touches"].get("methods", [])
    missing = [m for m in required if m not in game_methods]
    
    assert not missing, f"Missing: {missing}"
    print(f"✓ Verified {len(required)} mod touches")
```

**mod.json entry:**
```json
{
  "name": "Battle Scene Speed",
  "touches": {
    "methods": [
      "PokeBattle_Scene#pbGraphicsUpdate",
      "PokeBattle_Scene#pbWaitMessage",
      ...
    ]
  }
}
```

## Implementation Checklist

1. **Add to test suite:**
   ```bash
   pytest mod/tests/test_<mod_name>_hooks.py
   ```

2. **Run after game version update:**
   ```bash
   # Before release: verify all installed mods still compatible
   python mod/tests/validate_all_hooks.py
   ```

3. **CI integration:** Run test on every git push to catch breakage early

## When to Use

- Mod uses `alias_method` or `define_method` to patch classes
- Game version updates happen (risks method renames)
- Want user-facing confidence: "mod is installed and compatible"
- Multiple mods installed (one broken mod can cascade)

## When NOT to Use

- Mod only patches files (no Ruby runtime patching)
- Scripts.rxdata encrypted or inaccessible
- No way to decode game binary format
