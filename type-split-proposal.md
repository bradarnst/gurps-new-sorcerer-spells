# Type Split Proposal — Second Structural Review

## Scope and source of truth
- Source documents:
  - `/home/brad/.local/share/kilo/plans/1779065784000-maester-taxonomy-continuation.md`
  - `/home/brad/.local/share/kilo/plans/1779065784000-maester-taxonomy-next-pass-addendum.md`
- Working corpus references:
  - `spells-raw.json`
  - `processed/full-probe-spells.json`
  - `tools/build_spell_pilot.py`
- No `AGENTS.md` or ADR files are present in this repository.
- This remains a **structural review pass only**. It does **not** do Westerosi spell renaming or Westerosi description/example writing yet.

## Corpus cleanup applied for this pass
### Raw source backup and filter
- Original backup created:
  - `/home/brad/gaming/gurps-new-sorcerer-spells/spells-raw.backup-pre-alkahest-banefire-banestorm-removal-20260518T130905.json`
- Active source file updated:
  - `/home/brad/gaming/gurps-new-sorcerer-spells/spells-raw.json`
- Removed from the raw source list:
  - all `Alkahest` spells
  - all `Banefire` spells
  - all `Banestorm` spells
- Total raw spells:
  - before: **2207**
  - after removal: **2193**

### Spells excluded from this review pass
- `Alkahest Jet`
- `Alkahest Sphere`
- `Rain of Alkahest`
- `Spit Alkahest`
- `Banefire`
- `Banefire Dart`
- `Banefire Jet`
- `Banefire Shield`
- `Banefire Weapon`
- `Personal Banefire Shield`
- `Rain of Banefire`
- `Detect Banestorm`
- `Identify Newcomer`
- `Seek Banestorm`

## Rebuild status
- `tools/build_spell_pilot.py` was updated so manual overrides remain optional and the old first-50 curated-seed gate no longer blocks rebuilds.
- `processed/full-probe-*` was rebuilt successfully from the filtered `spells-raw.json`.
- The counts below are based on that rebuilt processed corpus.

## Structural adjustments applied before splitting
1. **Dissolved `Ageing` entirely**
   - Body Control: `Age (Variant)`, `Animal Ageing`, `Decrepify`, `Progeria`, `Temporary Ageing`
   - Healing: `Halt Ageing`, `Personal Halt Ageing`
   - Protection: `Protection from Ageing`
   - Necromantic: `Age`, `Burden of Time`, `Reaper’s Embrace`

2. **Contracted `Meta` before splitting it**
   - Reassigned **33** `Personal ...` Meta spillover records to clearer disciplines where an exact or manual counterpart exists.
   - Projected result: `Meta` contracts from **257** to **225**.

3. **Contracted `Gate` before judging whether it still needed a split**
   - After Banestorm removal, `Gate` stood at **64**.
   - Removed **32** obvious distance/gravity or threshold-summoning spillover assignments from the Gate type.
   - Projected result: `Gate` contracts from **64** to **32** and no longer needs a child split.

4. **Applied targeted review feedback while preserving multi-type membership**
   - Spells may belong to more than one `spell_type` list when the overlap is real.
   - `Avatar` now sits in both `Communication & Empathy` and `Protection`.
   - `Badger Paws` and `Mass Badger Paws` were removed from `Protection` and treated as `Earth` plus `Transformation` spells.
   - `Keen Taste and Smell`, `Personal Keen Taste and Smell`, `Keen Touch`, and `Personal Keen Touch` were moved from `Protection` into `Knowledge`.
   - `Accelerate Pregnancy` was moved from `Protection` into `Body Control`.
   - `Irresistible Dance` was moved from `Protection` into `Mind Control`.
   - `Mass Coolness` remains in `Protection`, but now sits under `Safeguards & Reliefs` instead of `Battle Blessings & Readiness`.

## Second-pass decision rule
A `spell_type` survives only if it reads as a **real sorcerous discipline**, not just a convenient review bucket.

That means this pass rejects labels such as:
- `Personal Arcana`
- `Banishment, Locks, and Instability`
- `Gravity, Distance, and Other Ways`
- `Threshold Summons & Callings`

These may still be useful during analysis, but they are **not** recommended as final spell types.

## Biggest structural outcomes from this pass
- `Ageing` is gone.
- all `Alkahest`, `Banefire`, and `Banestorm` spells are excluded from the taxonomy pass.
- `Gate` no longer needs splitting after contraction.
- `Sorcerous Services & Rites` is retained as a real candidate type and is **not** auto-split.
- `Weapon Boons & Retaliations` is also retained as a real candidate type and is **not** auto-split.
- no proposed resulting spell type is above the hard ceiling of **60**.

## Contracted types that no longer need a child split
### Gate (64 → projected 32)
**Recommendation:** keep Gate as a single stable spell type after contraction.

**Why**
- once the obvious Movement/Gravity/Space/Summoning spillover is removed, Gate becomes a much cleaner threshold-and-planar discipline
- this is better than preserving artificial child buckets under Gate

**What leaves Gate**
- most distance/gravity travel spillover
- threshold summons better handled by `Summoning`
- several teleport/distance tracing effects that read more naturally outside Gate

## Refined split proposals

### Meta (257 → projected 225)
**Proposed child spell types**
- Lesser Hexes & Afflictions (54)
- Grand Arcana & Constructs (45)
- Sorcerous Services & Rites (45)
- Arcane Utilities & Implements (35)
- Mana, Ley, and Power (18)
- Countermagic & Suppression (17)
- Arcane Siphons & Frailties (11)

**Why this split is better than the first pass**
- it removes `Personal Arcana` as a fake type
- it keeps `Sorcerous Services & Rites` together, as requested
- it replaces the more review-bucketish `Great Works, Constructs, and Oddities` with `Grand Arcana & Constructs`
- it keeps the narrow siphoning-and-frailty seam visible without forcing it into a miscellaneous pile

### Knowledge (projected 258)
**Proposed child spell types**
- Readings & Analysis (57)
- Senses & Perception (52)
- Detection & Appraisal (41)
- Seekers & Trackers (41)
- Divination & Omens (37)
- Thoughts & Memory (30)

**Why this split still holds**
- the Knowledge boundaries remain strong after cleanup
- these remain distinct browse disciplines: sensing, seeking, testing, prophecy, and mental inquiry

### Protection (projected 252)
**Proposed child spell types**
- Safeguards & Reliefs (53)
- Battle Blessings & Readiness (48)
- Resistances & Immunities (49)
- Armor & Battle Shells (43)
- Wards, Shields, and Barriers (30)
- Concealments & Counter-Senses (17)
- Weapon Boons & Retaliations (12)

**Why this split is better than the first pass**
- `Concealments & Counter-Senses` is clearer than `Subtle & Personal Safeguards`
- `Weapon Boons & Retaliations` stays intact, as requested
- `Safeguards & Reliefs` is shorter and cleaner than `Practical Safeguards & Reliefs`
- several obvious non-battle edge cases were moved out of `Battle Blessings & Readiness`, which leaves that label meaningfully cleaner for the MVP pass

### Mind Control (projected 179)
**Proposed child spell types**
- Mental Curses & Counterwill (35)
- Commands & Compulsion (33)
- Memory, Thought, and Will (32)
- Emotion & Morale (22)
- Pain, Stun, and Collapse (21)
- Possession & Identity (18)
- Dreams, Sleep, and Delusion (18)

**Why this split is better than the first pass**
- `Mental Curses & Counterwill` reads more like a real discipline than the earlier wording
- the branch remains one of the cleanest both mechanically and thematically

### Transformation (projected 176)
**Proposed child spell types**
- Alteration, Growth, and Other Transmutations (56)
- Shapeshifting & Polymorph (45)
- Body Forms & Embodiments (42)
- Creation, Shape, and Matter (33)

**Why this split is better than the first pass**
- it merges thin transformation seams into fewer, stronger disciplines
- it avoids creating an extra marginal type just to shave counts

### Movement (projected 152)
**Proposed child spell types**
- Speed, Haste, and Handling (60)
- Ways, Passage, and Travel (53)
- Forced Movement & Restraint (39)

**Why this split is better than the first pass**
- it merges roads, traversal, relocation, teleportation, and related conveyance magic into one stronger movement discipline
- it is a good example of combining closely related thin groups into a better overall list

**Review caution**
- `Speed, Haste, and Handling` lands exactly on the ceiling and should be watched in later growth

### Making & Breaking (projected 143)
**Proposed child spell types**
- Weapons & Battlework (48)
- Breaking, Shattering, and Ruin (39)
- Crafting, Repair, and Reshaping (32)
- Locks, Seals, and Traps (24)

**Why this split is better than the first pass**
- `Crafting, Repair, and Reshaping` is a better consolidated discipline than separate tiny crafting and reshaping branches

### Earth (projected 140)
**Proposed child spell types**
- Stone, Soil, and Sand (58)
- Metal & Glass (49)
- Earthshape, Passage, and Transmutation (33)

### Artillery (projected 132)
**Proposed child spell types**
- Missiles, Jets, and Rays (55)
- Battlefield Zones & Fields (44)
- Bursts, Barrages, and Bombardment (33)

**Why this split is better than the first pass**
- it folds hazards and field-scale effects into one stronger battlefield-control discipline

### Body Control (projected 133)
**Proposed child spell types**
- Internal Ruin, Fatigue, and Decline (54)
- Body Forms, Limbs, and Alteration (53)
- Vital Functions & Augmentation (26)

**Why this split is better than the first pass**
- it absorbs the dissolved `Ageing` spells cleanly
- it avoids preserving age-magic as its own specialty
- it merges the old limbs branch into a broader flesh-working discipline
- it now handles `Accelerate Pregnancy` as bodily process magic instead of forcing it into a protection branch

### Air (projected 125)
**Proposed child spell types**
- Winds, Vapors, and Sky Passage (58)
- Breath & Atmosphere (51)
- Lightning of the Air (16)

**Why this split is better than the first pass**
- it avoids a tiny standalone sky-passage type
- it keeps air- and weather-adjacent seams readable without oversplitting

### Light & Darkness (projected 120)
**Proposed child spell types**
- Radiance, Sight, and Reflection (42)
- Glamour, Color, and Prism (27)
- Lightning & Radiant Assaults (27)
- Shadows & Obscurity (24)

### Plant (projected 119)
**Proposed child spell types**
- Growth, Blessing, and Husbandry (59)
- Wood, Vines, and Plant Forms (43)
- Plant Lore, Speech, and Passage (17)

**Why this split is better than the first pass**
- it merges vine/thorn restraint into the stronger physical-plant branch

### Fire (projected 108)
**Proposed child spell types**
- Flame Assaults & Battlefire (59)
- Heat, Fuel, and Hearthwork (49)

**Why this split changed**
- the former `Banefire & Hellfire` child is gone because all Banefire spells were removed from the corpus
- the remaining fire split is cleaner and still stays below the ceiling

### Necromantic (projected 91)
**Proposed child spell types**
- Death Curses & Withering (60)
- Undead Animation & Command (19)
- Spirits of the Dead (12)

**Why this split changed**
- the dissolved `Ageing` material is gone
- the former deathflame/banefire seam is gone because Banefire was removed
- the remaining necromantic structure is simpler and still fits under the ceiling

### Water (projected 92)
**Proposed child spell types**
- Water Shaping & Passage (35)
- Ice, Snow, and Frost (32)
- Drowning, Dehydration, and Fluid Assaults (25)

### Animal (projected 86)
**Proposed child spell types**
- Animal Command & Repelling (51)
- Beast Forms & Traits (25)
- Animal Companions, Mounts, and Summons (10)

### Weather (projected 82)
**Proposed child spell types**
- Tempests, Lightning, and Winter Weather (44)
- Rain, Wind, and Greater Weather (38)

**Why this split is better than the first pass**
- it merges the earlier lightning and cold-front seams into one stronger severe-weather discipline
- it remains a cleaner example of merging closely related thin types

### Spirit (projected 61)
**Proposed child spell types**
- Spirits, Wards, and the Dead (36)
- Souls, Possession, and Bindings (25)

**Why this split is better than the first pass**
- it keeps Spirit to two stronger disciplines instead of three thinner ones

## Stable existing spell types after cleanup
These do not need a new split in this pass:
- Gate (32 after contraction)
- Healing (52)
- Force (49)
- Communication & Empathy (48)
- Energy (45)
- Food (41)
- Technological (39)
- Poison (38)
- Time (37)
- Summoning (34)
- Gravity (27)
- Stealth (26)
- Acid (24 after Alkahest removal)
- Sound (24)
- Space (24)
- Illusion & Creation (23)
- Holy (18)
- Dream (16)
- Enchantment (11)
- Radiation (8)

## Small spell types intentionally retained
These stay because they still read as real, useful disciplines rather than report debris:
- Enchantment (11)
- Radiation (8)
- Arcane Siphons & Frailties (11)
- Animal Companions, Mounts, and Summons (10)
- Weapon Boons & Retaliations (12)

## Buckets still above 60 after this pass
- None.

## Judgment-call spell membership lists
Exact spell membership for the remaining judgment calls is written to:
- `/home/brad/gaming/gurps-new-sorcerer-spells/type-split-judgment-call-spells.json`

That file now reflects the targeted feedback adjustments above and preserves multi-type membership where applicable.

Included there:
- `Arcane Siphons & Frailties`
- `Safeguards & Reliefs`
- `Battle Blessings & Readiness`
- `Body Forms, Limbs, and Alteration`
- `Tempests, Lightning, and Winter Weather`

Each entry includes:
- `spell_name`
- `current_spell_types`
- `source_spell_types`

## Main review points before Westerosi naming begins
1. **Meta:** whether `Arcane Siphons & Frailties` feels like a true narrow discipline or should be folded elsewhere.
2. **Protection:** whether the boundary between `Safeguards & Reliefs` and `Battle Blessings & Readiness` is convincing.
3. **Body Control:** whether `Body Forms, Limbs, and Alteration` is the right label for that combined branch.
4. **Weather:** whether `Tempests, Lightning, and Winter Weather` is the right severe-weather name.
5. `Sorcerous Services & Rites` and `Weapon Boons & Retaliations` are intentionally retained intact in this pass and should be approved or revised as whole disciplines, not auto-fragmented.

## Recommendation before any Westerosi renaming or description pass
- Approve this structural pass first.
- Resolve the remaining naming and boundary judgments above.
- Then move on to Westerosi spell renaming.
- Only after renaming is stable should the Westerosi description/example pass begin.
