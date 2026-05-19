# GURPS Sorcerer Spells — Maester Naming and Taxonomy Continuation Plan

## Purpose
Carry the dataset work into the next session with a clear, reviewable direction for:
- Westerosi maester-style **spell descriptions** in the final pass,
- Westerosi-aware **spell and spell-type naming**,
- a **taxonomy-first** review before any full rename sweep,
- a **mapping file only for the 24 original colleges/spell types** the user cares about.

This document supersedes the broader naming discussion where raw/noisy source labels were considered separately. For naming purposes, the only college-level mapping the user wants is for these originals:
- Air
- Animal
- Body Control
- Communication & Empathy
- Earth
- Enchantment
- Fire
- Food
- Gate
- Healing
- Illusion & Creation
- Knowledge
- Light
- Making & Breaking
- Meta
- Mind Control
- Movement
- Necromantic
- Plant
- Protection
- Sound
- Technological
- Water
- Weather

## Confirmed Decisions
- The **Westerosi maester voice** is now the preferred style direction for the **final-final description pass**.
- Spell names and spell-type names should also be reviewed through that lens.
- **Not every spell or spell type must be renamed.** If a name already fits the tone, keep it.
- The separate mapping file should cover **only the 24 original colleges/spell types listed above**.
- We should **not** do a single do-it-all-at-once rename/taxonomy run.
- The next meaningful checkpoint is a **type distribution / split proposal review**, not a final rename pass.

## Planning Constraint
At planning time, no `AGENTS.md` or ADR files were present in the repository.

## Current Probe Snapshot
Reference file:
- `/home/brad/gaming/gurps-new-sorcerer-spells/processed/full-probe-report.md`

Headline numbers from the full heuristic probe:
- Source spells: **2207**
- Canonical types currently used in probe: **40**
- Canonical keywords currently used in probe: **30**
- Multi-type distribution:
  - 1 type: **1333** spells
  - 2 types: **651** spells
  - 3 types: **181** spells
  - 4 types: **33** spells
  - 5 types: **9** spells
- Total type assignments implied by the above: **3355**

Largest current buckets in the probe report:
- Meta: **257**
- Knowledge: **255**
- Protection: **250**
- Mind Control: **176**
- Transformation: **174**
- Movement: **150**
- Making & Breaking: **144**
- Earth: **138**
- Artillery: **132**
- Body Control: **126**
- Air: **125**
- Light & Darkness: **119**
- Plant: **117**
- Fire: **115**
- Necromantic: **100**
- Water: **90**
- Animal: **86**
- Weather: **86**
- Gate: **67**
- Spirit: **61**

## Recommendation on Bucket Size
### Recommendation
- **Hard ceiling now:** `60`
- **Soft target now:** `25-40`
- **Preferred rule:** split anything above 60 immediately if the split is natural and table-useful.
- **Do not force** every bucket under 40 in the first structural pass.

### Why
With 2207 spells and 3355 current type assignments, forcing a strict sub-40 target immediately would likely produce too many artificial micro-types. A better sequence is:
1. get the taxonomy into a sane shape with **no buckets above 60**,
2. review the resulting split logic,
3. then tighten broad but acceptable 40-60 groups only where the split is clearly useful.

### Practical interpretation
- If a bucket lands around **42-55** but has a coherent table identity, it can survive the first structural pass.
- If a bucket is **55-60+** and clearly contains multiple modes of play, it should be split.
- If a split would create contrived fragments just to win the number game, postpone it.

## Recommended Next Session Order
### Phase 1 — Original-College Name Mapping Only
Create a mapping file for the 24 original colleges only.

Suggested file:
- `/home/brad/gaming/gurps-new-sorcerer-spells/original-college-name-map.json`

Suggested schema:
```json
[
  {
    "original_name": "Air",
    "recommended_display_name": "Air",
    "alternate_display_name": "Winds, Vapors, and Breath",
    "status": "keep-for-now",
    "notes": "Short original already fits the setting tolerably well; longer option exists if stronger flavor is desired."
  }
]
```

Important:
- This file is **not** for noisy raw source labels.
- It is **not** the full final taxonomy file.
- It is specifically a **display-name mapping for the 24 original colleges**.

### Phase 2 — Taxonomy Split Proposal
Build a structural split proposal that answers:
- which buckets above 60 should split,
- what the candidate child types are,
- what their approximate counts would be,
- which splits are rooted in gameplay function rather than mere aesthetics.

This pass should produce a reviewable report before any mass spell renaming.

### Phase 3 — Review and Adjust
User reviews:
- original-college display names,
- proposed split names,
- counts per split,
- any buckets that still feel too broad or too ornate.

### Phase 4 — Spell Renaming Pass
Only after taxonomy review is stable:
- rename spells in batches,
- keep some names unchanged where appropriate,
- use the maester tone consistently but not flamboyantly.

### Phase 5 — Final Description Pass
After naming and taxonomy are stable:
- finalize the Westerosi maester-style description field across the intended corpus,
- preserving table utility first.

## Suggested Original-College Display Name Directions
These are **suggestions**, not locked decisions. The point is to arrive in the next session with something concrete enough to review.

| Original college | Recommended now | Alternate stronger-maester option | Current suggestion |
|---|---|---|---|
| Air | Air | Winds, Vapors, and Breath | keep short for now; rename only if the surrounding taxonomy becomes more literary |
| Animal | Animal | Beasts, Vermin, and Their Masters | likely rename later |
| Body Control | Body Control | Flesh, Blood, and Bone | likely rename |
| Communication & Empathy | Communication & Empathy | Messages, Persuasions, and Fellow Feeling | likely rename |
| Earth | Earth | Stone, Soil, and Metal | keep short for now or use the longer version if sibling colleges also lengthen |
| Enchantment | Enchantment | Forged Charms and Lasting Works | likely rename |
| Fire | Fire | Flame, Ember, and Heat | keep short for now; longer option is good if the set becomes more literary overall |
| Food | Food | Victuals, Preservation, and Plenty | likely rename |
| Gate | Gate | Gates, Thresholds, and Far Ways | borderline; either works |
| Healing | Healing | Healing and Restoration | light rename candidate |
| Illusion & Creation | Illusion & Creation | Glamours, Phantoms, and Conjurings | likely rename |
| Knowledge | Knowledge | Signs, Revelations, and Knowing | likely rename |
| Light | Light | Light, Shadow, and Radiance | likely rename |
| Making & Breaking | Making & Breaking | Making, Breaking, and Severing | likely rename |
| Meta | Meta | The Higher Mysteries | likely rename |
| Mind Control | Mind Control | Command, Influence, and Subjugation | likely rename |
| Movement | Movement | Roads, Flight, and Swift Passage | likely rename |
| Necromantic | Necromantic | Death, Dust, and the Restless | likely rename |
| Plant | Plant | Roots, Vines, and Growing Things | likely rename |
| Protection | Protection | Wards, Safeguards, and Defenses | likely rename |
| Sound | Sound | Voices, Echoes, and Song | likely rename |
| Technological | Technological | Engines, Powder, and Devices | likely rename |
| Water | Water | Waters, Ice, and Mists | keep short for now or use longer version if the family goes literary |
| Weather | Weather | Storm, Rain, and Thunder | borderline; strong rename candidate |

## Naming Guidance
### For original colleges
- Treat the 24 original colleges as **root display categories**, not as a complete final flat taxonomy.
- Keep names understandable at a glance.
- Favor names that sound like something a learned maester would catalog, not something a bard would shout.

### For split child types
- These may be more functional and less poetic than the root names.
- They still need flavor, but structure comes first.
- Example principle: `Wards, Safeguards, and Defenses` is a fine root display name; child types under it may still be blunt and searchable.

### For spell names
- Delay large-scale renaming until the type structure is stable.
- Keep strong names that already fit.
- Rename bland/mechanical names later in controlled batches.

## Immediate Structural Priority List
In the next session, the first split review should focus on these oversized probe buckets:
- Meta
- Knowledge
- Protection
- Mind Control
- Transformation
- Movement
- Making & Breaking
- Earth
- Artillery
- Body Control
- Air
- Light & Darkness
- Plant
- Fire
- Necromantic
- Water
- Animal
- Weather
- Gate
- Spirit

These are the groups most likely to benefit from a first-pass division under the **hard ceiling of 60**.

## Suggested Deliverables for the Next Session
1. `original-college-name-map.json`
   - only the 24 original colleges
   - recommended display names, alternates, keep/rename status, notes

2. `type-split-proposal.md`
   - proposed split tree for oversized buckets
   - rationale for each split
   - whether the split is thematic, mechanical, or both

3. `type-split-distribution.json`
   - counts for proposed post-split buckets
   - flags for anything still above 60
   - flags for anything suspiciously tiny

4. optional `type-split-distribution.md`
   - human-readable review report derived from the JSON

## Acceptance Criteria for the Next Structural Pass
- The 24 original colleges have a dedicated mapping file with suggested display names.
- Oversized buckets are split to **60 or below**, unless a documented exception is consciously accepted.
- Most new buckets ideally land in the **25-40** range.
- No obviously artificial micro-types are created purely to satisfy a count target.
- No mass spell renaming is attempted before the split proposal is reviewed.

## Explicit Non-Goals for the Next Session
- Do **not** rename every spell.
- Do **not** finalize every final display name everywhere.
- Do **not** treat noisy raw source labels as the naming layer that matters.
- Do **not** force every bucket below 40 if the split would be contrived.

## Handover Summary
The current direction is:
- keep the **Westerosi maester voice** for final descriptions,
- create an **original-college mapping file only for the 24 user-approved root colleges**,
- do a **taxonomy-first structural split review** before a mass rename pass,
- use **60 as the immediate hard ceiling**,
- use **25-40 as the preferred target where natural**,
- refine names after the split report is reviewed.
