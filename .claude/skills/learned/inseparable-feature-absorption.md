---
name: inseparable-feature-absorption
description: "Absorb inseparable module dependencies into base to eliminate implicit coupling"
user-invocable: false
origin: auto-extracted
---

# 분리 불가능한 기능 흡수: 모드 → 본문 통합

**Extracted:** 2026-08-03
**Context:** Game mod architecture where a feature is tightly coupled to another system

## Problem

Module A (e.g., Josa Select) is designed as a separate plugin but:
- Downstream code assumes Module A's behavior or format
- Module A must load before/after other modules in a specific order
- Module A becomes a **hidden dependency** rather than explicit requirement
- Installation becomes complex: "X requires Y" vs just distributing X

Example: Josa Select mod interprets `\j[받침형,무받침형]` syntax in translations. Translations *cannot* be distributed or used without the Josa Select interpreter, making them inseparable.

## Solution

**Move the inseparable module into the base system as a built-in section:**

1. **Identify the inseparable feature**  
   Audit downstream code for implicit assumptions:
   ```bash
   grep -r "Josa Select\|\j\[" translate/ docs/ pokemon-z/
   ```

2. **Extract source to a canonical location**  
   Move from `mods/Josa Select/001_Josa.rb` → `share/josa.rb`

3. **Create a build-time integration script**  
   ```python
   # share/bake_josa.py - idempotent injection
   def inject_into_scripts(src_rb, target_rxdata):
       """Inject josa.rb into base Scripts.rxdata as a regular section"""
       # Read base (surgery version + backup)
       # Compress & add to section list
       # Overwrite both copies
   ```

4. **Update documentation & cards**  
   - Remove mod card from registry
   - Update base asset description: "Contains Josa interpreter as built-in section"
   - Document source location (`share/josa.rb`) and build tool (`bake_josa.py`)

5. **Verify idempotence**  
   Run integration script twice, confirm same output checksum

## When to Use

- **Feature is required by another system** (e.g., translation syntax relies on interpreter)
- **Load order is fragile** (module A only works if B is installed + loads first)
- **Distribution is simpler as one unit** (game + translation always travel together)
- **Decoupling would add version complexity** (supporting both "with interpreter" and "without" variants)

## Tradeoff

| Aspect | Separate Mod | Absorbed into Base |
|--------|-------------|------------------|
| Distribution | "Install A, then B" | One package |
| Version sync | A version ≠ B version | Always synced |
| Configurability | Swap mod versions freely | Part of base release cycle |
| Dependency clarity | Explicit in mod list | Implicit in base |

**Decision rule:** If you can't use one without the other, they aren't separate systems.

## Example: Pokemon Z Josa Select

**Before (inseparable coupling, modeled as separate):**
- `mods/Josa Select/` — interpreter plugin
- `translate/apply_josa.py` — generates `\j[...]` syntax
- **Hidden assumption:** Both must exist, mod must load before UI text

**After (integrated into base):**
- `share/josa.rb` — canonical source
- `share/bake_josa.py` — injection (rebuild scripts both directions)
- `pokemon-z/mods/.../*.rxdata` — all contain josa as built-in section
- mod registry: 7 mods → 6 mods (Josa Select removed)

Verification:
```bash
uv run --with rubymarshal python - <<'EOF'
from rubymarshal.reader import load
import zlib
arr = load(open("Data/Scripts.rxdata", "rb"))
sections = [bytes(e[1]).decode("utf-8") for e in arr]
print("Josa Select in base:", "Josa Select" in sections)
EOF
```

Output: `Josa Select in base: True`
