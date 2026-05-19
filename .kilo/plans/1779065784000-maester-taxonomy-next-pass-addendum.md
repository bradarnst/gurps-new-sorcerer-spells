# Maester Taxonomy Next Pass Addendum

This document supplements `/home/brad/.local/share/kilo/plans/1779065784000-maester-taxonomy-continuation.md`. It does not replace that plan. It records the clarified decision rules for the next structural taxonomy pass so that the next pass can be executed and reviewed against the same standards.

No `AGENTS.md` or ADRs are present for this work, so this addendum serves as the explicit decision record for the next pass.

## Purpose

The next pass is a structural cleanup and validation pass. It should refine the current `spell_type` taxonomy into a set of in-world, durable disciplines that can survive later Westerosi naming and presentation work.

## Clarified Decisions

### 1. Wizard colleges are a candidate vocabulary, not roots

The original wizard colleges should be treated only as a candidate starting vocabulary for sorcerer `spell_type` names and concepts. They are not authoritative roots, mandatory top-level categories, or a structure that the sorcerer taxonomy must preserve.

Implications:
- Use them where they genuinely fit.
- Reject or depart from them where the sorcerer corpus supports a better discipline boundary.
- Treat them as a useful starting point, not as a constraint.

### 2. A `spell_type` must survive on its own merits

A `spell_type` should persist because it is coherent, useful, and real in-world as a discipline, not merely because a report split happened to expose a cluster.

Implications:
- Report artifacts are prompts for review, not justification.
- Each retained type should be defensible as something practitioners would recognize as a real branch of sorcery.
- A review-bucket label is not automatically a candidate final type.

### 3. Small but strong types may survive

Small size alone is not a reason to merge or delete a `spell_type`. A thin type may survive if it is conceptually strong and clearly distinct.

Examples:
- `Enchantment` is the main positive example of a small but valid surviving type.
- `Radiation` is acceptable to leave alone for now rather than force a premature merge.

Implications:
- Evaluate thin types by coherence first, count second.
- Avoid consolidating away valid disciplines just to reduce category count.
- Counts remain a warning signal, not an automatic ruling.

### 4. Dissolve `Ageing`

`Ageing` should not survive as its own `spell_type`. Its spells should be reassigned individually into more real disciplines.

Agreed reassignment target structure:

**Body Control**
- `Age (Variant)`
- `Animal Ageing`
- `Decrepify`
- `Progeria`
- `Temporary Ageing`

**Healing / Protection**
- `Halt Ageing`
- `Personal Halt Ageing`
- `Protection from Ageing`

**Necromantic**
- `Age`
- `Burden of Time`
- `Reaper’s Embrace`

Implications:
- Reassign spell by spell.
- Do not preserve `Ageing` as a convenience bucket.
- Do not attempt to create a replacement “age-magic” specialty.

### 5. Break apart review buckets into real types

Labels such as `Banishment, Locks, and Instability` are not acceptable `spell_type`s. They are review buckets, not final disciplines.

Implications:
- Break these apart spell by spell.
- Reassign each spell into a real, defensible type.
- Do not preserve multi-topic labels that merely summarize unresolved cleanup.
- If the pieces belong to different real types, move them separately instead of keeping the bucket intact.

### 6. Merge closely related thin types when they are truly one discipline

Closely related small types may be merged, but only when they are genuinely one in-world discipline rather than merely adjacent topics.

Implications:
- Merge on conceptual unity, not just low counts.
- Prefer fewer stronger types when the underlying practice is actually singular.
- Do not merge distinct disciplines just to simplify the report.
- Two coherent thin candidates can become one stronger list if they clearly represent one real kind of sorcery.

### 7. Do not auto-split `Sorcerous Services & Rites`

`Sorcerous Services & Rites` may remain a single `spell_type` if, after review, it is coherent and not too large.

Implications:
- Review it critically.
- Keep it whole if it reads as one real discipline.
- Do not split it automatically just because it appears broad.

### 8. Do not auto-split `Weapon Boons & Retaliations`

`Weapon Boons & Retaliations` may also remain a single `spell_type` if, after review, it is coherent and not too large.

Implications:
- Apply the same standard as above.
- Preserve it if it functions as one real discipline.
- Split only if the review shows it is actually several unrelated practices.

### 9. Remove all Alkahest spells before the next rerun

All `Alkahest` spells should be removed before the next taxonomy rerun.

Spells to remove:
- `Alkahest Jet`
- `Alkahest Sphere`
- `Rain of Alkahest`
- `Spit Alkahest`

Implications:
- Do this before evaluating the next structural readout.
- The next structural report should not be distorted by spells already known to be leaving the corpus.

### 10. Defer `see_also` until after `spell_type` approval

`see_also` should not be part of this structural pass. It should be deferred until after `spell_type` approval.

If later added:
- Use a simple spell-id array.
- Its main purpose should be linking counterpart spells such as `Personal`, `Mass`, and `Permanent` forms.
- Manual additions can be made later where useful.

Implications:
- Do not let cross-link design complicate current taxonomy decisions.
- Finish discipline approval first.
- If retained later, keep it deliberately simple rather than turning it into a full variant/family system.

### 11. No subheadings

There should be no subheadings in the taxonomy. Either something is a `spell_type` or it is not.

Implications:
- Avoid hierarchical presentation that masks weak categories.
- Promote only real disciplines to `spell_type`.
- Handle everything else through reassignment, merging, or later metadata rather than nested structure.

### 12. Next phase after approval

After this next structural pass is completed and approved, the project can move on to:
- Westerosi renaming
- Westerosi descriptions and examples

Implications:
- The immediate goal is structural correctness, not final flavor text.
- Naming and descriptive work should wait until the approved `spell_type` structure is stable.

## Operating Standard For The Next Pass

When reviewing any candidate `spell_type`, apply this test:

1. Is it a real in-world discipline rather than a cleanup artifact?
2. Is it coherent enough that its member spells plausibly belong together?
3. If small, is it still strong and distinct enough to survive?
4. If broad, is it truly one discipline rather than several weakly related ones?
5. If questionable, should its spells be reassigned individually instead of preserving the label?

## Recommended Execution Order

1. Remove all Alkahest spells from the corpus.
2. Rerun the taxonomy outputs.
3. Rework questionable review buckets into real spell types or dissolve them.
4. Apply the agreed `Ageing` redistribution.
5. Review thin-but-strong types for retention.
6. Review broad-but-coherent candidates such as `Sorcerous Services & Rites` and `Weapon Boons & Retaliations` without auto-splitting them.
7. Approve the resulting `spell_type` structure.
8. Only then move on to Westerosi naming and descriptions/examples.

## Practical Outcome Expected From The Next Pass

The next rerun should aim to produce:
- only real, defensible `spell_type`s
- no convenience buckets disguised as disciplines
- no `Ageing`
- no `Alkahest` spells
- no subheading structure
- a stable enough taxonomy to support later Westerosi naming and descriptive work

This addendum is intended to constrain the next pass, not expand scope beyond that structural objective.
