---
name: game-translation-csv-validation-workflow
description: "Validate multilingual game translations against official CSV sources, classify mismatches, apply bulk fixes"
user-invocable: false
origin: auto-extracted
---

# Game Translation CSV Validation Workflow

**Extracted:** 2026-08-02  
**Context:** Pokémon Z (spanish fangame) — validating JSONL translation sets against PokeAPI official CSV exports (ES ↔ KO pairs)

## Problem

Game translation files (items, moves, battle text) in JSONL format may contain:
- Mismatches with official names (custom items, renamed NPC moves)
- Stale terminology (outdated official localization, API version drift)
- Hard-coded Latin remnants when should be transliterated (NPC names, proper nouns)
- Inconsistencies in term families (Poké- vs 포켓몬- prefix handling, status effect names)

Spot-checking finds these too late; bulk application of wrong fixes breaks everything.

## Solution

### Step 1: Download official CSV from PokeAPI

```bash
curl -sL -o item_names.csv https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/item_names.csv
curl -sL -o move_names.csv https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/move_names.csv
```

### Step 2: Build official ES ↔ KO dictionary

```python
import csv

es_to_ko = {}
for row in csv.DictReader(open("item_names.csv")):
    item_id = row["item_id"]
    lang_id = row["local_language_id"]
    name = row["name"]
    
    # lang_id: 7=Spanish, 3=Korean (PokeAPI standard)
    if lang_id == "7":
        if item_id not in es_to_ko:
            es_to_ko[item_id] = {}
        es_to_ko[item_id]["es"] = name
    elif lang_id == "3":
        if item_id not in es_to_ko:
            es_to_ko[item_id] = {}
        es_to_ko[item_id]["ko"] = name

# Flatten to {es_name.lower(): ko_name}
official_map = {}
for item_id, names in es_to_ko.items():
    if "es" in names and "ko" in names:
        official_map[names["es"].lower()] = names["ko"]

print(f"Official ES→KO pairs: {len(official_map)}")
```

### Step 3: Load game JSONL and classify all rows

```python
import json

items = [json.loads(line) for line in open("translate/ko/07-items.jsonl")]

matches = []
mismatches = []
not_official = []

for item in items:
    es_name = (item.get("es") or "").strip()
    ko_current = (item.get("v") or "").strip()
    
    if not es_name:
        not_official.append(item)
        continue
    
    official_ko = official_map.get(es_name.lower())
    
    if official_ko is None:
        # Not in PokeAPI — custom/created item
        not_official.append(item)
    elif official_ko.replace(" ", "") == ko_current.replace(" ", ""):
        matches.append(item)
    else:
        mismatches.append((item["i"], es_name, ko_current, official_ko))

print(f"Total: {len(items)}")
print(f"  Matches: {len(matches)}")
print(f"  Mismatches: {len(mismatches)}")
print(f"  Not in PokeAPI (custom): {len(not_official)}")

# Inspect mismatches
for item_id, es, current, official in mismatches:
    print(f"  {item_id}: ES='{es}' → current='{current}' | official='{official}'")
```

### Step 4: Validate before bulk apply

Before auto-replacing, **manually inspect**:
- All mismatches (may indicate real bugs in official API or intentional localization choices)
- Cardinality of not-official items (custom/fan creations should be in a separate category)
- Edge cases (names with accents, spaces, punctuation normalization)

**Example red flags**:
- Mismatch count is 0 for entire category (suspicious — all official names match?) → verify a few samples in-game
- Not-official count is 95% of total → source CSV likely outdated
- Mismatches cluster in one subsection (e.g., all Poké- prefixed items) → likely systematic terminology shift

### Step 5: Apply with audit trail

```python
import json, glob

changes = {}

for path in sorted(glob.glob("translate/ko/*.jsonl")):
    out = []
    count = 0
    
    for line in open(path):
        item = json.loads(line)
        es_name = (item.get("es") or "").strip()
        
        if es_name and es_name.lower() in official_map:
            old_ko = item.get("v", "")
            new_ko = official_map[es_name.lower()]
            
            if new_ko != old_ko:
                item["v"] = new_ko
                count += 1
        
        out.append(json.dumps(item, ensure_ascii=False))
    
    if count > 0:
        open(path, "w").write("\n".join(out) + "\n")
        changes[path] = count

print("Applied changes:", changes)
print("Total rows updated:", sum(changes.values()))
```

### Step 6: Validate result round-trip

```bash
# Rebuild game data (build.py includes round-trip validation)
python3 build.py

# Grep for any remaining unmatched terms
grep -rn "^[A-Z]" translate/ko/*.jsonl | head -20
```

## When to Use

- Validating game translations against official API/source datasets
- Before bulk terminology swaps (e.g., renaming all instances of a term family)
- Detecting stale official names (API version mismatch)
- Auditing custom/fan-created item/move/character names
- CI/CD gate: fail if mismatch count exceeds threshold after update

## Common Pitfalls

1. **API versioning**: Official CSV may lag behind game patches. Cross-check with secondary source (e.g., Bulbapedia, Wishing Star dialogue)
2. **Whitespace normalization**: `.replace(" ", "")` before comparison, but preserve in output
3. **Encoding**: PokeAPI CSV is UTF-8 with BOM — use `encoding="utf-8-sig"` when reading
4. **Terminology drift**: One mismatch (e.g., "Poké-" prefix inconsistency) can cascade. Classify before auto-fix
5. **Custom items**: Not-in-official items may be intentional fan creations. Don't assume they're bugs

## Post-Application Checklist

- [ ] Round-trip build succeeds (korean.dat regenerated, no parse errors)
- [ ] In-game item names/move names display correctly (screenshot verification)
- [ ] No regressions in other JSONL sections (grep for inadvertent replacements)
- [ ] Commit message includes classification summary (X matches, Y mismatches, Z not-official)
