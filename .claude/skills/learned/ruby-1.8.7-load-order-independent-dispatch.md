---
name: ruby-1.8.7-load-order-independent-dispatch
description: "Use runtime hooks instead of compile-time conditions to decouple module initialization from load order"
user-invocable: false
origin: auto-extracted
---

# 루비 1.8.7: 로드 순서 독립적 디스패치

**Extracted:** 2026-08-03
**Context:** Ruby 1.8.7 environments (Pokémon Essentials) where module load order is determined by sort order and cannot be reliably controlled

## Problem

Two issues collide in Ruby 1.8.7 projects:

1. **No trailing comma support** — Ruby 1.8.7 rejects `func(a, b,)` as SyntaxError
   ```ruby
   # This crashes 1.8.7
   @table.unshift(
     ["[A] Curar", "[X] 회복"],
   )  # ← Trailing comma not allowed
   ```

2. **Load order ≠ initialization order** — Scripts are injected alphabetically, but compile-time checks assume a specific order
   ```ruby
   # Controller UX Z loads first (alphabetically)
   # UI Text KR loads second
   # But at time of injection:
   if defined?(UiTextKR)  # Always false at this point!
       # Never runs
   end
   ```

Result: Code compiles without error but silently does nothing (no error message).

## Solution

**Replace compile-time `defined?()` checks with runtime hooks (alias chains):**

**Before (broken):**
```ruby
# mods/Controller UX Z/004_PadLabels.rb
class Scene_Map
  UITEXT_REPLACEMENTS = [
    ["[A] Curar", "[X] 회복"],
  ]

  # This loads before UI Text KR, so defined?(UiTextKR) is false
  if defined?(UiTextKR)  # ← Load-order dependent, silently fails
    UITEXT_REPLACEMENTS.each { |old, new| UiTextKR::TABLE.unshift([old, new]) }
  end
end
```

**After (works regardless of load order):**
```ruby
# mods/Controller UX Z/004_PadLabels.rb
class Scene_Map
  UITEXT_REPLACEMENTS = [
    ["[A] Curar", "[X] 회복"]  # ← No trailing comma
  ]

  # Hook fires once, at runtime, when Scene_Map#main is first called
  alias _orig_main main
  def main
    # By now both modules are defined
    if defined?(UiTextKR) && defined?(UiTextKR::TABLE)
      UITEXT_REPLACEMENTS.each { |old, new| 
        UiTextKR::TABLE.unshift([old, new]) 
      }
    end
    _orig_main
  end
end
```

## How It Works

1. **Compile time:** Both modules are parsed and available in class namespace
2. **Injection time:** Scripts are ordered alphabetically, but no code runs yet
3. **Runtime (Scene_Map#main first call):** 
   - All modules are defined in memory
   - Alias chain fires once
   - Replacements take effect before any game code runs
   - Order of definition no longer matters

## When to Use

- **Load order is determined by sort, not dependency** (e.g., game mod injection, framework plugin loading)
- **Interdependent features need initialization at a specific time** (e.g., game scene setup)
- **You can't control the injection order**
- **Compile-time checks would fail silently** (no error, no effect)

## Tradeoff

| Aspect | Compile-time `defined?()` | Runtime Hook (alias) |
|--------|--------------------------|---------------------|
| Fail mode | Silent no-op (hard to debug) | Works correctly |
| Performance | Negligible (checked once) | Negligible (alias fire once) |
| Clarity | Explicit dependency | Implicit until runtime |
| Compatibility | Load-order dependent | Load-order independent |

**Rule of thumb:** If module order is external to your control, use runtime hooks.

## Example: Pokemon Z Quick Menu Pad Labels

**Setup:**
- Injected scripts sorted alphabetically
- Controller UX Z (C...) loads before UI Text KR (U...)
- UI Text KR defines `UiTextKR::TABLE` 
- Controller UX Z needs to prepend pad labels to that table

**Symptoms of the problem:**
```bash
# Game script loads, no error
# Scene_Map drawn, pad labels still show keyboard ([A], [S], [D])
# Expected: pad labels ([X], [LB], [RB])
```

**Fix applied:**
```ruby
# mods/Controller UX Z/004_PadLabels.rb
class Scene_Map
  REPLACEMENTS = [
    ["[A] Curar", "[X] 회복"],
    ["[S] Viajar", "[LB] 이동"],
    ["[D] Brújula", "[RB] 나침반"]
  ]

  alias _orig_main main
  def main
    # Fires once here, all modules guaranteed to be loaded
    if defined?(UiTextKR) && defined?(UiTextKR::TABLE)
      REPLACEMENTS.each { |old, new| UiTextKR::TABLE.unshift([old, new]) }
    end
    _orig_main
  end
end
```

Verification:
```bash
uv run inject.py  # Rebuild
# Game starts, Scene_Map#main alias fires
# Pad label replacements take effect
# Verify: Game shows [X] 회복 instead of [A] 회복
```

## Debugging Checklist

If replacements still don't appear:

- [ ] Confirm alias fires: add `print()` before/after hook
- [ ] Confirm `UiTextKR::TABLE` exists: check with `defined?()`
- [ ] Confirm execution order: TABLE is read before Scene_Map draws (usually safe)
- [ ] Check for other hooks/overwrites: grep for Scene_Map#main in all injected sections
- [ ] Verify trailing commas removed: `grep ",\s*)" mods/**/*.rb`
