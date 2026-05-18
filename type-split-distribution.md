# Type Split Distribution Report — Second Structural Review

## Pre-pass assumptions used for this report
- Backed up the original raw source to `spells-raw.backup-pre-alkahest-banefire-banestorm-removal-20260518T130905.json`.
- Updated `spells-raw.json` to remove all Alkahest, Banefire, and Banestorm spells.
- Removed **14** spells from this review pass.
- Dissolved `Ageing` entirely.
- Reassigned **33** `Personal ...` Meta spillover records to clearer counterpart disciplines where possible.
- Contracted `Gate` by removing **32** distance/gravity or threshold-summoning spillover assignments.
- Applied targeted feedback adjustments for `Avatar`, `Badger Paws`, `Mass Badger Paws`, `Keen Taste and Smell`, `Personal Keen Taste and Smell`, `Keen Touch`, `Personal Keen Touch`, `Accelerate Pregnancy`, and `Irresistible Dance`.

## Rebuild status
- `tools/build_spell_pilot.py` was updated so manual overrides remain optional and the old first-50 curated-seed gate no longer blocks rebuilds.
- `processed/full-probe-*` was rebuilt successfully from the filtered `spells-raw.json`.
- The counts below are based on that rebuilt processed corpus.

## Result summary
- Proposed resulting spell types above the hard ceiling of 60: **0**
- `Ageing` is no longer retained as a spell type.
- `Gate` no longer needs child splitting after contraction: **64 → 32**
- `Meta` is reviewed after contraction rather than with the old personal spillover intact: **257 → 225**
- all `Alkahest`, `Banefire`, and `Banestorm` spells are excluded from this pass

## Largest resulting spell types
| Spell type | Count | Source |
|---|---:|---|
| Speed, Haste, and Handling | 60 | split: Movement |
| Growth, Blessing, and Husbandry | 59 | split: Plant |
| Flame Assaults & Battlefire | 59 | split: Fire |
| Winds, Vapors, and Sky Passage | 58 | split: Air |
| Readings & Analysis | 57 | split: Knowledge |
| Stone, Soil, and Sand | 58 | split: Earth |
| Safeguards & Reliefs | 53 | split: Protection |
| Internal Ruin, Fatigue, and Decline | 54 | split: Body Control |
| Missiles, Jets, and Rays | 55 | split: Artillery |
| Death Curses & Withering | 60 | split: Necromantic |
| Battle Blessings & Readiness | 48 | split: Protection |
| Alteration, Growth, and Other Transmutations | 56 | split: Transformation |
| Lesser Hexes & Afflictions | 54 | split: Meta |
| Body Forms, Limbs, and Alteration | 53 | split: Body Control |
| Ways, Passage, and Travel | 53 | split: Movement |
| Healing | 52 | stable existing type |
| Breath & Atmosphere | 51 | split: Air |
| Animal Command & Repelling | 51 | split: Animal |

## Stable existing spell types worth preserving as-is in this pass
| Spell type | Count |
|---|---:|
| Healing | 52 |
| Force | 49 |
| Communication & Empathy | 48 |
| Energy | 45 |
| Food | 41 |
| Technological | 39 |
| Poison | 38 |
| Time | 37 |
| Summoning | 34 |
| Gate | 32 |
| Gravity | 27 |
| Stealth | 26 |
| Acid | 24 |
| Sound | 24 |
| Space | 24 |
| Illusion & Creation | 23 |
| Holy | 18 |
| Dream | 16 |
| Enchantment | 11 |
| Radiation | 8 |

## Small but intentionally retained spell types
| Spell type | Count | Why retain it |
|---|---:|---|
| Arcane Siphons & Frailties | 11 | Narrow, but still reads as a coherent siphoning-and-weakening discipline. |
| Enchantment | 11 | Explicitly approved as a small but worthwhile discipline. |
| Animal Companions, Mounts, and Summons | 10 | Clear table-facing niche and likely to grow later. |
| Radiation | 8 | Approved to leave alone for now. |

## Structural improvements over the previous pass
- `Ageing` is gone instead of surviving as a tiny specialty.
- `Gate` is now a single clean threshold-and-planar type rather than a bad review split.
- `Sorcerous Services & Rites` is preserved as one broad type rather than fragmented automatically.
- `Weapon Boons & Retaliations` is preserved as one broad type rather than fragmented automatically.
- the removal of Banefire simplifies both `Fire` and `Necromantic`
- spells continue to support multi-type membership where the overlap is real, such as `Avatar` belonging to both `Communication & Empathy` and `Protection`
- several obvious non-battle outliers were removed from `Battle Blessings & Readiness`, which leaves that bucket more coherent
- several previously thin child types were merged into stronger disciplines:
  - Movement travel branches → `Ways, Passage, and Travel`
  - Weather severe-storm branches → `Tempests, Lightning, and Winter Weather`
  - Spirit branches → two stronger Spirit disciplines instead of three thinner ones

## Main review cautions
- `Arcane Siphons & Frailties` is still the most arguable small new type.
- `Safeguards & Reliefs` versus `Battle Blessings & Readiness` should be sanity-checked for overlap.
- `Body Forms, Limbs, and Alteration` may still want a cleaner final label.
- `Tempests, Lightning, and Winter Weather` may still want a shorter final name.

## Judgment-call spell membership
Exact spell membership for the current judgment calls is written to:
- `type-split-judgment-call-spells.json`

That file reflects the targeted feedback adjustments above.

## Bottom line
This pass produces a taxonomy with:
- no resulting spell type above 60,
- no `Ageing`,
- no `Alkahest`, `Banefire`, or `Banestorm` spells in the review corpus,
- no review-bucket child names like `Banishment, Locks, and Instability`,
- and a cleaner platform for the later Westerosi naming and description passes.
