# Maester Taxonomy Finalization Record

This document supplements:
- `/home/brad/.local/share/kilo/plans/1779065784000-maester-taxonomy-continuation.md`
- `/home/brad/.local/share/kilo/plans/1779065784000-maester-taxonomy-next-pass-addendum.md`

## Finalized Status
The structural taxonomy phase is now **finalized for MVP purposes**.

The next session should treat the taxonomy as approved and move on to the Westerosi maester voice phase rather than reopening structural classification work.

## Approved Working State
### Corpus and build state
- Raw source backup created:
  - `/home/brad/gaming/gurps-new-sorcerer-spells/spells-raw.backup-pre-alkahest-banefire-banestorm-removal-20260518T130905.json`
- Active raw corpus:
  - `/home/brad/gaming/gurps-new-sorcerer-spells/spells-raw.json`
- `spells-raw.json` has had all `Alkahest`, `Banefire`, and `Banestorm` spells removed.
- `tools/build_spell_pilot.py` was updated so manual overrides remain optional and the old first-50 curated-seed gate no longer blocks rebuilds.
- `processed/full-probe-*` was rebuilt successfully from the filtered raw corpus.

### Approved taxonomy artifacts
Use these as the current accepted MVP structural outputs:
- `/home/brad/gaming/gurps-new-sorcerer-spells/type-split-proposal.md`
- `/home/brad/gaming/gurps-new-sorcerer-spells/type-split-distribution.json`
- `/home/brad/gaming/gurps-new-sorcerer-spells/type-split-distribution.md`
- `/home/brad/gaming/gurps-new-sorcerer-spells/type-split-judgment-call-spells.json`
- `/home/brad/gaming/gurps-new-sorcerer-spells/original-college-name-map.json`

## Approved structural decisions
- The wizard colleges are only a candidate starting vocabulary for sorcerer `spell_type` naming, not roots.
- `spell_type` structure is approved enough for the project to move on.
- Spells may belong to more than one `spell_type` list when the overlap is real.
- `Ageing` is dissolved.
- `Gate` remains a single stable type after contraction.
- `Sorcerous Services & Rites` remains intact.
- `Weapon Boons & Retaliations` remains intact.
- No subheading structure is desired.
- `see_also` remains deferred.
- Spell examples are deferred to a later phase.

## Approved targeted spell placement adjustments
These specific review outcomes should be treated as settled for MVP:
- `Avatar` belongs to both `Communication & Empathy` and `Protection`.
- `Badger Paws` and `Mass Badger Paws` are not in `Protection`; they belong in `Earth` and `Transformation`.
- `Keen Taste and Smell`, `Personal Keen Taste and Smell`, `Keen Touch`, and `Personal Keen Touch` belong in `Knowledge`, not `Protection`.
- `Accelerate Pregnancy` belongs in `Body Control`, not in `Battle Blessings & Readiness`.
- `Irresistible Dance` belongs in `Mind Control`, not in `Battle Blessings & Readiness`.
- The movement child type name is `Ways, Passage, and Travel`.
- The knowledge child type name is `Senses & Perception`.

## Finalized-for-now interpretation
“Finalized” here means:
- good enough to move into the next project phase,
- not blocked on further taxonomy debate,
- still open to later refinement if new spells are added or future worldbuilding needs justify it.

The next session should not spend its time re-litigating the taxonomy unless a truly blocking issue is discovered during the naming/description work.

## Next Phase
The next phase is:
- Westerosi maester voice phrasing for **spell names**,
- Westerosi maester voice phrasing for **spell type names**,
- Westerosi maester voice phrasing for **spell descriptions**.

The next phase does **not** include:
- example/use-case writing,
- `see_also` implementation,
- another structural taxonomy pass unless a blocking issue appears.
