# Type Split Proposal

## Scope and method
- Source of truth for this pass: `/home/brad/.local/share/kilo/plans/1779065784000-maester-taxonomy-continuation.md`.
- Corpus and reports inspected: `processed/full-probe-report.md`, `processed/full-probe-spells.json`, and `tools/build_spell_pilot.py`.
- `build_spell_pilot.py` currently infers the 40 working canonical types and reports only which current buckets exceed 60; it does not yet model post-split child taxonomy.
- This proposal is a **review pass only**. It partitions oversized current buckets by the current spell names, secondary types, and keywords, but it does **not** mass-rename spells and it does **not** do the final prose pass.
- Constraints used here:
  - hard ceiling: **60**
  - soft target: **25-40 where natural**
  - avoid artificial micro-types unless a small bucket exposes a real mechanical seam worth reviewing on its own.

## Split-first priority order
### First review tier
These are the largest and noisiest buckets and should be reviewed first even if the rest of the proposal is accepted provisionally:
1. **Meta (257)**
2. **Knowledge (255)**
3. **Protection (250)**
4. **Mind Control (176)**

### Second review tier
These are structurally important but cleaner once the first tier is settled:
- **Transformation (174)**
- **Movement (150)**
- **Making & Breaking (144)**
- **Earth (138)**
- **Artillery (132)**
- **Body Control (126)**
- **Air (125)**

### Third review tier
These still need first-pass splitting, but their seams are more legible already:
- **Light & Darkness (119)**
- **Plant (117)**
- **Fire (115)**
- **Necromantic (100)**
- **Water (90)**
- **Animal (86)**
- **Weather (86)**
- **Gate (67)**
- **Spirit (61)**

## Proposed first-pass splits

### Meta (257)
**Roll-up root original college:** `Meta`

**Proposed child types**
- Lesser Hexes & Afflictions (53)
- Great Works, Constructs, and Oddities (45)
- Sorcerous Services & Rites (44)
- Arcane Utilities & Implements (35)
- Personal Arcana (33)
- Mana, Ley, and Power (18)
- Countermagic & Suppression (17)
- Thefts, Vulnerabilities, and Doom (12)

**Why this split is mechanically useful**
- This is the noisiest bucket in the whole corpus.
- It separates countermagic, mana economy, personal upkeep workings, and nuisance hexes into reviewable queues instead of leaving everything magic-adjacent in one bucket.
- The split also exposes where the current probe is using `Meta` as a catch-all, which is valuable before any naming pass.

**Naming confidence**
- Medium.
- `Sorcerous Services & Rites` and `Great Works, Constructs, and Oddities` are useful placeholders but worth user review.

### Knowledge (255)
**Roll-up root original college:** `Knowledge`

**Proposed child types**
- Readings & Analysis (57)
- Senses & Vision (46)
- Seekers & Trackers (43)
- Detection & Appraisal (42)
- Divination & Omens (37)
- Thoughts & Memory (30)

**Why this split is mechanically useful**
- It cleanly separates passive sensory buffs, active seeking magic, omen/divination rituals, and mind-reading or memory work.
- At the table, these are different use cases: scouting, diagnosis, tracking, prophecy, and mental inquiry do not want to live in the same lookup bucket.

**Naming confidence**
- High on the split seams, medium on the exact names.
- `Readings & Analysis` versus `Detection & Appraisal` is the main wording seam to review.

### Protection (250)
**Roll-up root original college:** `Protection`

**Proposed child types**
- Battle Blessings & Readiness (54)
- Resistances & Immunities (49)
- Practical Safeguards & Reliefs (45)
- Armor & Battle Shells (41)
- Wards, Shields, and Barriers (32)
- Subtle & Personal Safeguards (17)
- Weapon Boons & Retaliations (12)

**Why this split is mechanically useful**
- The current bucket mixes armor, elemental resistance, defensive blessings, stealthy screening, battlefield wards, and retaliatory weapon-side defenses.
- Those are distinct shopping lists for players: “make me harder to hit,” “let me ignore fire,” “stop scrying,” and “prepare for travel or illness” should not all be the same type.

**Naming confidence**
- Medium.
- `Battle Blessings & Readiness` and `Practical Safeguards & Reliefs` are accurate but may want shorter final labels.

### Mind Control (176)
**Roll-up root original college:** `Mind Control`

**Proposed child types**
- Curses, Counterwill, and Ruin (35)
- Memory, Thought, and Will (34)
- Commands & Compulsion (32)
- Pain, Stun, and Collapse (21)
- Emotion & Morale (21)
- Dreams, Sleep, and Delusion (18)
- Possession & Identity (15)

**Why this split is mechanically useful**
- This separates command spells, morale/emotion effects, dream or sleep effects, memory/will manipulation, and hard mental shutdown effects.
- Players and GMs usually search these by consequence: obedience, terror, sleep, confusion, or possession.

**Naming confidence**
- High on the mechanical split.
- `Curses, Counterwill, and Ruin` is the label most likely to need a second wording pass.

### Transformation (174)
**Roll-up root original college:** none; this remains a cross-college functional family.

**Proposed child types**
- Shapeshifting & Polymorph (45)
- Body Forms & Embodiments (42)
- Creation, Shape, and Matter (33)
- Transmutations & Other Forms (31)
- Alteration, Growth, and Reduction (23)

**Why this split is mechanically useful**
- It separates identity-changing form magic from elemental body states, matter-shaping magic, and size/alteration effects.
- That distinction matters because those spells solve very different problems in play.

**Naming confidence**
- High.

### Movement (150)
**Roll-up root original college:** `Movement`

**Proposed child types**
- Speed, Haste, and Handling (58)
- Forced Movement & Restraint (35)
- Steps, Strides, and Passage (23)
- Flight & Falling (18)
- Teleportation & Long Passage (16)

**Why this split is mechanically useful**
- It isolates speed buffs from repositioning control, terrain-passage magic, flight, and true relocation magic.
- A character looking for haste, teleportation, or battlefield drag effects should not have to search the same flat bucket.

**Naming confidence**
- High on the seams.
- `Steps, Strides, and Passage` is the main wording choice to review.

### Making & Breaking (144)
**Roll-up root original college:** `Making & Breaking`

**Proposed child types**
- Weapons & Battlework (49)
- Breaking, Shattering, and Ruin (39)
- Locks, Seals, and Traps (24)
- Crafting, Repair, and Stores (19)
- Reshaping & Transmutation (13)

**Why this split is mechanically useful**
- It pulls apart weapon enhancement, destructive object magic, lock/trap work, repair/crafting, and object reshaping.
- Those are natural shopping categories for both players and worldbuilding notes.

**Naming confidence**
- High.

### Earth (138)
**Roll-up root original college:** `Earth`

**Proposed child types**
- Stone, Soil, and Sand (56)
- Metal & Glass (49)
- Earthshape, Passage, and Transmutation (33)

**Why this split is mechanically useful**
- The material seam is clean: raw earth/stone/sand behaves differently from metal and glass magic.
- The remaining shape, travel, and transmutation effects form a coherent utility group instead of producing tiny artificial slices.

**Naming confidence**
- High.

### Artillery (132)
**Roll-up root original college:** none; this remains a cross-college functional family.

**Proposed child types**
- Missiles, Jets, and Rays (55)
- Bursts, Barrages, and Bombardment (33)
- Hazards, Mines, and Persistent Zones (26)
- Battlefield Fields & Wards (18)

**Why this split is mechanically useful**
- It separates direct ranged attacks from area barrages, placed hazards, and battlefield-scale field effects.
- Those distinctions matter immediately in encounter prep and in player browsing.

**Naming confidence**
- High.

### Body Control (126)
**Roll-up root original college:** `Body Control`

**Proposed child types**
- Vital Functions, Fatigue, and Internal Ruin (59)
- Body Forms & Alteration (37)
- Bodily Enhancements (16)
- Limbs, Flesh, and Reach (14)

**Why this split is mechanically useful**
- It separates body-form magic from stat and mobility enhancement, limb-specific manipulation, and harsh internal afflictions.
- Combining breath and other internal-function magic with fatigue and ruin keeps this pass from creating a contrived micro-type.

**Naming confidence**
- High.

### Air (125)
**Roll-up root original college:** `Air`

**Proposed child types**
- Breath & Atmosphere (49)
- Wind, Pressure, and Shaping (26)
- Clouds, Vapors, and Smells (23)
- Lightning of the Air (16)
- Flight & Sky Passage (11)

**Why this split is mechanically useful**
- It cleanly distinguishes respiration/air-quality effects, wind control, cloud or vapor hazards, lightning, and airborne travel.
- That is a practical table split and also keeps the air/weather boundary readable.

**Naming confidence**
- High on the structure, medium on whether `Lightning of the Air` should stay under Air versus leaning harder into Weather.

### Light & Darkness (119)
**Roll-up root original college:** `Light`

**Proposed child types**
- Color, Prism, and Other Glamour (27)
- Lightning & Radiant Assaults (27)
- Light, Seeing, and Reflection (25)
- Shadows & Obscurity (24)
- Lightborne Passage (16)

**Why this split is mechanically useful**
- It separates sensory/illumination play, shadow play, lightning attacks, and light-based movement tricks.
- The current mixed bucket is especially hard to search because it contains both visibility tools and aggressive storm-lightning effects.

**Naming confidence**
- Medium.
- `Color, Prism, and Other Glamour` is a useful provisional name but not yet elegant.

### Plant (117)
**Roll-up root original college:** `Plant`

**Proposed child types**
- Growth, Blessing, and Husbandry (57)
- Fungus, Wood, and Plant Forms (29)
- Plant Lore, Speech, and Passage (17)
- Vines, Thorns, and Restraint (14)

**Why this split is mechanically useful**
- It separates agrarian growth magic from combat entanglement, plant communication/knowledge, and fungal or wooden form magic.
- Those are distinct enough in play that a single plant bucket is doing too much work.

**Naming confidence**
- High.

### Fire (115)
**Roll-up root original college:** `Fire`

**Proposed child types**
- Heat, Fuel, and Hearthwork (49)
- Firebolts, Jets, and Strikes (31)
- Battlefield Fire & Walls (23)
- Banefire & Hellfire (12)

**Why this split is mechanically useful**
- It separates practical heat/fuel manipulation, direct fire attacks, battlefield fire zones, and cursed/deathly flame.
- The banefire/hellfire seam is mechanically real and worth isolating before naming review.

**Naming confidence**
- High.

### Necromantic (100)
**Roll-up root original college:** `Necromantic`

**Proposed child types**
- Death Curses & Withering (51)
- Undead Animation & Command (19)
- Spirits of the Dead (12)
- Deathflame & Banefire (10)
- Ageing & Life-Draining (8)

**Why this split is mechanically useful**
- It separates generic deathly afflictions from undead command, spirit dealings, cursed flame, and explicit ageing effects.
- `Ageing & Life-Draining` is small, but it exposes a real mechanical seam that already overlaps with the existing Ageing type.

**Naming confidence**
- High on the split seam, medium on whether the ageing child should remain distinct this early.

### Water (90)
**Roll-up root original college:** `Water`

**Proposed child types**
- Ice, Snow, and Frost (30)
- Drowning, Dehydration, and Fluid Assaults (25)
- Water Shaping & Stores (20)
- Aquatic Passage & Breathing (15)

**Why this split is mechanically useful**
- It separates cold/ice effects, fluid attack magic, matter-shaping water utility, and aquatic adaptation.
- Those are distinct enough in use that they should not remain a single 90-spell bucket.

**Naming confidence**
- High.

### Animal (86)
**Roll-up root original college:** `Animal`

**Proposed child types**
- Animal Command & Repelling (51)
- Beast Forms & Traits (25)
- Animal Summons, Mounts, and Bonds (10)

**Why this split is mechanically useful**
- It separates commanding or repelling creatures from trait grafting/shapeshifting and from companion or mount creation/bonding.
- That is a natural player-facing distinction even if the last child stays small.

**Naming confidence**
- High.

### Weather (86)
**Roll-up root original college:** `Weather`

**Proposed child types**
- Rain, Wind, and Greater Weather (40)
- Lightning Storms (32)
- Snow, Ice, and Cold Fronts (14)

**Why this split is mechanically useful**
- It cleanly separates storm-lightning from broad weather shaping and from cold-front magic.
- The resulting three-way split is strong enough to use at the table without manufacturing niche subfamilies.

**Naming confidence**
- High.

### Gate (67)
**Roll-up root original college:** `Gate`

**Proposed child types**
- Gates, Portals, and Planar Passage (29)
- Gravity, Distance, and Other Ways (28)
- Banishment, Locks, and Instability (10)

**Why this split is mechanically useful**
- It isolates actual gate/portal travel from the current gravity-distance subfamily and from hostile lock/banishment magic.
- That makes the current mixed gate bucket much easier to browse.

**Naming confidence**
- Medium.
- `Gravity, Distance, and Other Ways` is a holding name for the current personal gravity/distance seam and should be reviewed.

### Spirit (61)
**Roll-up root original college:** none; this remains a cross-college thematic family.

**Proposed child types**
- Possession, Souls, and Bindings (25)
- Spirit Sight, Wards, and the Undead (20)
- Spirit Allies & Summons (16)

**Why this split is mechanically useful**
- It separates soul/possession play, spirit detection or warding, and actual spirit allies or summoned dead.
- The parent bucket is only barely over the line, so a three-way split is enough.

**Naming confidence**
- Medium.
- `Spirit Sight, Wards, and the Undead` is clear but a bit composite.

## Buckets still above 60 after the first pass
- None.

## Buckets intentionally left small enough to review, not auto-merged away
- `Ageing & Life-Draining` under Necromantic (8): small, but it exposes a real mechanical seam shared with the existing Ageing family.
- `Radiation` (8): unchanged pre-existing type; still small, but not part of this split pass.
- `Animal Summons, Mounts, and Bonds` (10): small, but it is a practical table-facing subfamily if the user wants companions and mount magic isolated.
- `Banishment, Locks, and Instability` (10): small, but it is clearer than burying those spells back inside generic gate travel.

## Naming choices that need explicit review
- **Meta:** `Sorcerous Services & Rites` and `Great Works, Constructs, and Oddities` are functional but not final-grade names.
- **Protection:** `Battle Blessings & Readiness` and `Practical Safeguards & Reliefs` may want a shorter final phrasing.
- **Light & Darkness:** `Color, Prism, and Other Glamour` is the least settled child label in that branch.
- **Gate:** `Gravity, Distance, and Other Ways` is a placeholder-quality name for a real subfamily.
- **Spirit:** `Spirit Sight, Wards, and the Undead` may be too composite for the final taxonomy.

## Recommendation before any spell renaming
- Review and approve the **first-tier splits** first: Meta, Knowledge, Protection, and Mind Control.
- Then review the naming uncertainty list above.
- Only after that should any large spell-name pass begin.
