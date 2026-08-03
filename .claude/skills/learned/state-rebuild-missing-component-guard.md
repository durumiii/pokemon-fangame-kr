---
name: state-rebuild-missing-component-guard
description: "Detect missing components during state rebuild to prevent silent data loss"
user-invocable: false
origin: auto-extracted
---

# 상태 재구축 시 누락 감지: 안전판 패턴

**Extracted:** 2026-08-03
**Context:** Tools that perform full state rebuild (database migrations, cache rebuilds, game asset reinject) where existing state might disappear silently

## Problem

Full-state rebuild tools (e.g., `inject.py` that rewrites entire Scripts.rxdata) can silently lose data:

```bash
# Game has 6 injected mods currently loaded
$ uv run inject.py  # Rebuild from configuration list
# But config only specifies 5 mods (forgot one, or it's deprecated)
# Result: 6th mod is gone, no warning

# User doesn't notice until mid-game bug appears
```

The rebuild **overwrites the entire state**, replacing it with what the config says should exist. Anything in the old state not in the config disappears.

## Solution

**Compare old state with new config, warn about gaps:**

```python
def inject_game(game_path, config_mods):
    """
    Reinject all mods from config into game Scripts.rxdata.
    
    Safety: Compare config with current game state.
    If game has mods not in config, warn and exit.
    """
    import sys
    
    # 1. Extract current state from game
    game_sections = extract_sections_from_game(game_path)
    game_mods = [m for m in game_sections if m.startswith("MOD:")]
    
    # 2. Extract config list
    config_mods = [parse_mod_card(card) for card in Path("mods").glob("*/mod.json")]
    config_mod_names = [m["name"] for m in config_mods]
    
    # 3. Detect missing (in game, not in config)
    missing = set(game_mods) - set(config_mod_names)
    
    if missing:
        print(f"경고: 게임에 주입돼 있던 {missing}가 이번 나열에 없어요 "
              f"— 전체 재구축이라 결과에서 빠집니다.")
        sys.exit(1)  # Force user to acknowledge
    
    # 4. Proceed with rebuild
    rebuild_scripts_rxdata(game_path, config_mods)
```

## When to Use

- **Full-state replacement operations** (not incremental updates)
  - Database migrations that rewrite tables
  - Cache rebuilds that clear then repopulate
  - Asset reinjection (game mod scripts, app configs)
  
- **Old state can contain important data** not in the rebuild config
  
- **Rebuild failures are costly** (data loss, mid-operation breakage)

## Design Variations

### Variation 1: Warn + Continue
For non-critical data:
```python
if missing:
    print(f"⚠️  Warning: {missing} will be lost")
    if not confirm("Continue?"):
        sys.exit(1)
rebuild_scripts_rxdata(...)
```

### Variation 2: Explicit Deprecation List
For known-safe removals:
```python
DEPRECATED_MODS = {"Josa Select"}  # v5 absorbed into base
safe_missing = missing & DEPRECATED_MODS
unsafe_missing = missing - DEPRECATED_MODS

if unsafe_missing:
    print(f"Error: Unknown mods will be lost: {unsafe_missing}")
    sys.exit(1)

if safe_missing:
    print(f"Info: Deprecated mods removed: {safe_missing}")
```

### Variation 3: Dry-run Mode
Preview changes before applying:
```python
$ inject.py --dry-run
# Output: Would remove: MOD:OldFeature
#         Would add: MOD:NewFeature
#         No changes to: MOD:Battle Speed Z, ...
```

## Example: Pokemon Z inject.py

**Before (silent loss):**
```bash
$ uv run inject.py
# Game loses Josa Select mod, user doesn't know until text rendering breaks
```

**After (explicit guard):**
```bash
$ uv run inject.py
# Warning: 게임에 주입돼 있던 「Josa Select」가 이번 나열에 없어요 — 전체 재구축이라 결과에서 빠집니다.
# (program exits, user acknowledges removal was intentional)

$ uv run inject.py --accept-changes  # After confirming Josa was moved to base
# Proceeds normally
```

**Prompt output shows the issue immediately:**
```ruby
경고: 게임에 주입돼 있던 「Josa Select」가 이번 나열에 없어요 
— 전체 재구축이라 결과에서 빠집니다.
멈춤: Better Movements Z의 기대와 기반이 다르다 — ...
```

User sees both the removal AND validation issues in one run.

## Verification

Test the guard:
```bash
# 1. Start with game that has Mod A
uv run inject.py
# Verifies all mods in config exist in game

# 2. Manually remove Mod A from game via GUI
# 3. Run inject.py again
# Should report: "Mod A missing from config list"

# 4. Remove Mod A from config explicitly
# 5. Re-run
# Should report: "Mod A in game but not in config"
```

## Tradeoff

| Aspect | No Guard | With Guard |
|--------|----------|-----------|
| Silent data loss | Possible | Prevented |
| User awareness | "Why did my game break?" | "Mod removed, confirm intended" |
| Automation friction | None | Requires explicit flag to continue |
| Recovery | Manual | Undo command or restore from backup |

**Rule:** Destructive operations (full rewrites) must be aware of their destructiveness.
