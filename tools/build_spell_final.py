from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from typing import Any

import build_spell_pilot as pilot


ROOT = pilot.ROOT
RAW_PATH = pilot.RAW_PATH
OUTPUT_DIR = pilot.OUTPUT_DIR

REQUIRED_RECORD_KEYS = {
    "spell_id",
    "spell_name",
    "spell_types",
    "keywords",
    "full_cost",
    "casting_roll",
    "range",
    "duration",
    "description",
    "statistics",
    "archmagisters_counsel",
    "source_lineage",
}
BANNED_RECORD_KEYS = {
    "record_index",
    "spell_type_display_names",
    "description_source",
    "aliases",
    "dedupe",
}
REQUIRED_SOURCE_LINEAGE_KEYS = {
    "source_spell_name",
    "source_spell_types",
}
BANNED_SOURCE_LINEAGE_KEYS = {
    "source_spell_id",
    "source_keywords",
    "parsed_source_keywords",
    "inferred_parent_spell_types",
}
FINAL_SPELL_TYPE_DESCRIPTIONS = {
    "Lesser Hexes & Afflictions": "Spells that inflict minor curses, hindrances, and hostile magical afflictions.",
    "Grand Arcana & Constructs": "Spells that create large arcane workings, supernatural constructs, or especially potent magical feats.",
    "Sorcerous Services & Rites": "Spells for ceremonial workings, magical assistance, and formal sorcerous procedures.",
    "Arcane Utilities & Implements": "Spells that provide practical magical tools, conveniences, and arcane implements.",
    "Mana, Ley, and Power": "Spells that sense, store, shape, or disrupt mana, ley lines, and magical power sources.",
    "Countermagic & Suppression": "Spells that dispel, block, dampen, or negate other magic.",
    "Arcane Siphons & Frailties": "Spells that drain magical strength, impose arcane weakness, or exploit mystical vulnerabilities.",
    "Readings & Analysis": "Spells that examine magical, physical, or situational details to produce specific insight.",
    "Senses & Perception": "Spells that sharpen the senses or grant unusual ways to perceive the world.",
    "Detection & Appraisal": "Spells that detect hidden things and assess the nature, quality, or value of subjects.",
    "Seekers & Trackers": "Spells that locate and follow people, creatures, objects, or places.",
    "Divination & Omens": "Spells that reveal distant knowledge, omens, prophecy, or glimpses of fate.",
    "Thoughts & Memory": "Spells that read, recover, preserve, or inspect thoughts and memories.",
    "Safeguards & Reliefs": "Spells that prevent harm, break harmful conditions, or provide immediate protective relief.",
    "Resistances & Immunities": "Spells that grant resistance or immunity to hazards, energies, or hostile effects.",
    "Battle Blessings & Readiness": "Spells that improve combat readiness, coordination, and battlefield performance.",
    "Armor & Battle Shells": "Spells that wrap the subject in magical armor, hard shells, or reinforced defenses.",
    "Wards, Shields, and Barriers": "Spells that create wards, shields, walls, and other protective barriers.",
    "Concealments & Counter-Senses": "Spells that hide subjects, foil tracking, and mislead hostile senses.",
    "Weapon Boons & Retaliations": "Spells that empower weapons or punish those who strike the protected subject.",
    "Mental Curses & Counterwill": "Spells that weaken judgment, clarity, or mental resistance through hostile enchantment.",
    "Commands & Compulsion": "Spells that force obedience, direct behavior, or compel specific actions.",
    "Memory, Thought, and Will": "Spells that alter, shield, steal, or reshape thinking, memory, and determination.",
    "Emotion & Morale": "Spells that sway fear, courage, attraction, despair, and battlefield morale.",
    "Pain, Stun, and Collapse": "Spells that inflict pain, shock, disorientation, or outright incapacitation.",
    "Dreams, Sleep, and Delusion": "Spells that induce sleep, shape dreams, or trap minds in delusion and hallucination.",
    "Possession & Identity": "Spells involving possession, stolen identity, body takeover, or altered sense of self.",
    "Alteration, Growth, and Other Transmutations": "Spells that broadly transform bodies or things through change, growth, or reduction.",
    "Shapeshifting & Polymorph": "Spells that turn a subject into another form, species, or physical shape.",
    "Body Forms & Embodiments": "Spells that grant distinctive bodies, alternate embodiments, or specialized physical forms.",
    "Creation, Shape, and Matter": "Spells that conjure material, reshape substance, or alter physical composition.",
    "Speed, Haste, and Handling": "Spells that improve quickness, reflexes, precision, and physical handling.",
    "Ways, Passage, and Travel": "Spells that open routes, speed travel, or carry subjects from place to place.",
    "Forced Movement & Restraint": "Spells that push, pull, pin, bind, or otherwise control movement.",
    "Weapons & Battlework": "Spells that conjure, improve, control, or support weapons and battlefield equipment.",
    "Breaking, Shattering, and Ruin": "Spells that destroy, erode, crack, or otherwise ruin objects and structures.",
    "Crafting, Repair, and Reshaping": "Spells that craft, mend, rebuild, or reshape tools, objects, and materials.",
    "Locks, Seals, and Traps": "Spells that secure, unlock, seal, or trap passages, objects, and containers.",
    "Stone, Soil, and Sand": "Spells dealing with earth, stone, soil, sand, and similar groundbound matter.",
    "Metal & Glass": "Spells that work through metal, crystal, glass, and related hard materials.",
    "Earthshape, Passage, and Transmutation": "Spells that tunnel through earth, reshape terrain, or alter earthen matter.",
    "Missiles, Jets, and Rays": "Spells that deliver direct ranged attacks as missiles, jets, or focused beams.",
    "Battlefield Zones & Fields": "Spells that create persistent hazardous or controlling areas on the battlefield.",
    "Bursts, Barrages, and Bombardment": "Spells that hit with explosive bursts, wide-area volleys, or indirect magical fire.",
    "Internal Ruin, Fatigue, and Decline": "Spells that sap endurance, cause wasting, or inflict hidden bodily harm.",
    "Body Forms, Limbs, and Alteration": "Spells that reshape limbs, alter body structure, or change physical capability.",
    "Vital Functions & Augmentation": "Spells that support breathing, circulation, endurance, and other vital bodily functions.",
    "Winds, Vapors, and Sky Passage": "Spells that command winds, clouds, vapors, and movement through the sky.",
    "Breath & Atmosphere": "Spells that manage air supply, gases, breathing, and atmospheric conditions.",
    "Lightning of the Air": "Spells that call down lightning and related electrical force through the air.",
    "Radiance, Sight, and Reflection": "Spells of illumination, vision, mirrors, brilliance, and reflected light.",
    "Glamour, Color, and Prism": "Spells that bend color, appearance, and prismatic visual deception.",
    "Lightning & Radiant Assaults": "Spells that attack with blinding light, radiant force, or luminous energy.",
    "Shadows & Obscurity": "Spells that deepen darkness, cast shadows, and hide things from view.",
    "Growth, Blessing, and Husbandry": "Spells that encourage growth, fertility, health, and abundance in plant life.",
    "Wood, Vines, and Plant Forms": "Spells that shape wood, command vines, or assume plant-like forms.",
    "Plant Lore, Speech, and Passage": "Spells that reveal plant knowledge, allow communion with vegetation, or ease passage through it.",
    "Flame Assaults & Battlefire": "Spells that burn foes with aggressive flame, explosive fire, and battle magic.",
    "Heat, Fuel, and Hearthwork": "Spells that provide warmth, shape combustion, manage fuel, or support domestic fire.",
    "Death Curses & Withering": "Spells that curse with deathly power, aging, decay, or withering blight.",
    "Undead Animation & Command": "Spells that create, direct, or sustain undead servants.",
    "Spirits of the Dead": "Spells that call, question, perceive, or influence the spirits of the dead.",
    "Water Shaping & Passage": "Spells that move, shape, redirect, or travel through water.",
    "Ice, Snow, and Frost": "Spells of freezing cold, ice, snow, and numbing frost.",
    "Drowning, Dehydration, and Fluid Assaults": "Spells that drown, dehydrate, or attack through dangerous liquid force.",
    "Animal Command & Repelling": "Spells that influence, command, calm, or drive away animals.",
    "Beast Forms & Traits": "Spells that grant animal traits or transform the subject into beast-like forms.",
    "Animal Companions, Mounts, and Summons": "Spells that call, befriend, summon, or support animal allies and mounts.",
    "Tempests, Lightning, and Winter Weather": "Spells that unleash violent storms, lightning, snow, sleet, and winter fury.",
    "Rain, Wind, and Greater Weather": "Spells that shape rain, wind, fog, and broad weather conditions.",
    "Spirits, Wards, and the Dead": "Spells that ward against spirits, manage hauntings, or deal safely with the dead.",
    "Souls, Possession, and Bindings": "Spells that affect souls, possession, spiritual bonds, and supernatural bindings.",
    "Healing": "Spells that restore health, cure afflictions, and repair injuries.",
    "Force": "Spells that use telekinetic pressure, kinetic blows, and force barriers.",
    "Communication & Empathy": "Spells that carry messages, strengthen connection, and support understanding between minds.",
    "Energy": "Spells involving plasma, antimatter, raw power, and volatile magical energy.",
    "Food": "Spells that preserve food, create nourishment, or support eating and drinking.",
    "Technological": "Spells that affect machines, devices, gunpowder, and other technological systems.",
    "Poison": "Spells of toxins, contamination, venom, and noxious breathing hazards.",
    "Time": "Spells that accelerate, delay, revisit, or otherwise manipulate time.",
    "Summoning": "Spells that call, bind, or support separate allies, servants, and other beings.",
    "Gate": "Spells that open portals, cross boundaries, and manage interplanar or dimensional passage.",
    "Gravity": "Spells that alter weight, falling, pull, and other gravitic forces.",
    "Stealth": "Spells that conceal presence, hide movement, and help subjects avoid notice.",
    "Acid": "Spells involving corrosive substances, alkahest, and ongoing acid harm.",
    "Sound": "Spells that shape speech, silence, resonance, noise, and sonic effects.",
    "Space": "Spells that deal with vacuum, distance, stars, and other spatial or cosmic phenomena.",
    "Illusion & Creation": "Spells that deceive the senses or conjure convincing magical phenomena.",
    "Holy": "Spells of sacred power, angelic influence, and consecrated utility.",
    "Dream": "Spells involving sleep, dreams, nightmares, and oneiric travel.",
    "Enchantment": "Spells that place lasting magical enhancement on people, objects, or places.",
    "Radiation": "Spells involving irradiation, fallout, and mutagenic exposure.",
}
FRAMEWORK_BANNED_DESCRIPTION_TERMS = (
    "college",
    "child",
    "parent",
)


def build_final_record(raw_spell: dict[str, Any], split_assignments: dict[tuple[str, str], str]) -> dict[str, Any]:
    source_name = raw_spell["spell_name"]
    parent_spell_types, parsed_source_keywords, override, display_name = pilot.build_parent_type_info(raw_spell)
    keyword_seed = pilot.order_unique(override.get("keywords", parsed_source_keywords), pilot.KEYWORD_ORDER)
    keywords = pilot.infer_role_keywords(raw_spell, parent_spell_types, keyword_seed)

    description_override = override.get("description") or pilot.EXACT_DESCRIPTION_OVERRIDES.get(source_name)
    if description_override:
        description = description_override.strip()
    else:
        description, _ = pilot.generate_description(raw_spell, parent_spell_types, keywords)

    spell_types = pilot.finalize_spell_types(raw_spell, parent_spell_types, parsed_source_keywords, display_name, split_assignments)

    return {
        "spell_id": raw_spell["spell_id"],
        "spell_name": display_name,
        "spell_types": spell_types,
        "keywords": keywords,
        "full_cost": raw_spell["full_cost"],
        "casting_roll": raw_spell["casting_roll"],
        "range": raw_spell["range"],
        "duration": raw_spell["duration"],
        "description": description,
        "statistics": raw_spell["statistics"],
        "archmagisters_counsel": "",
        "source_lineage": {
            "source_spell_name": source_name,
            "source_spell_types": raw_spell["spell_types"],
        },
    }



def validate_final_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []

    for record in records:
        record_keys = set(record)
        missing_record_keys = sorted(REQUIRED_RECORD_KEYS - record_keys)
        extra_record_keys = sorted(record_keys - REQUIRED_RECORD_KEYS)
        banned_record_keys = sorted(record_keys & BANNED_RECORD_KEYS)
        if missing_record_keys:
            errors.append(f"{record['spell_name']}: missing record keys {missing_record_keys}")
        if extra_record_keys:
            errors.append(f"{record['spell_name']}: unexpected record keys {extra_record_keys}")
        if banned_record_keys:
            errors.append(f"{record['spell_name']}: banned record keys present {banned_record_keys}")

        if not record["spell_types"]:
            errors.append(f"{record['spell_name']}: missing spell_types")
        if "Individual Spell" in record["spell_types"]:
            errors.append(f"{record['spell_name']}: contains forbidden raw type")
        unknown_types = [spell_type for spell_type in record["spell_types"] if spell_type not in pilot.FINAL_SPELL_TYPES]
        if unknown_types:
            errors.append(f"{record['spell_name']}: unknown spell types {unknown_types}")

        if not record["keywords"]:
            errors.append(f"{record['spell_name']}: missing keywords")
        if any(keyword.lower() == "none" for keyword in record["keywords"]):
            errors.append(f"{record['spell_name']}: contains None keyword")
        unknown_keywords = [keyword for keyword in record["keywords"] if keyword not in pilot.KEYWORD_VOCABULARY]
        if unknown_keywords:
            errors.append(f"{record['spell_name']}: unknown keywords {unknown_keywords}")

        if not record["description"].strip():
            errors.append(f"{record['spell_name']}: blank description")
        if "archmagisters_counsel" not in record or record["archmagisters_counsel"] != "":
            errors.append(f"{record['spell_name']}: archmagisters_counsel missing or not blank")

        source_lineage = record.get("source_lineage", {})
        source_lineage_keys = set(source_lineage)
        missing_lineage_keys = sorted(REQUIRED_SOURCE_LINEAGE_KEYS - source_lineage_keys)
        extra_lineage_keys = sorted(source_lineage_keys - REQUIRED_SOURCE_LINEAGE_KEYS)
        banned_lineage_keys = sorted(source_lineage_keys & BANNED_SOURCE_LINEAGE_KEYS)
        if missing_lineage_keys:
            errors.append(f"{record['spell_name']}: missing source_lineage keys {missing_lineage_keys}")
        if extra_lineage_keys:
            errors.append(f"{record['spell_name']}: unexpected source_lineage keys {extra_lineage_keys}")
        if banned_lineage_keys:
            errors.append(f"{record['spell_name']}: banned source_lineage keys present {banned_lineage_keys}")

    return {
        "record_count": len(records),
        "errors": errors,
        "passed": not errors,
    }



def build_dataset_payload(raw_data: dict[str, Any], records: list[dict[str, Any]], label: str) -> dict[str, Any]:
    return {
        "metadata": {
            "source_file": RAW_PATH.name,
            "source_total_spells": raw_data["metadata"]["totalSpells"],
            "processed_scope": label,
            "processed_count": len(records),
            "build_timestamp_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        },
        "spells": records,
    }



def build_framework_payload() -> dict[str, Any]:
    missing_descriptions = [spell_type for spell_type in pilot.FINAL_TYPE_ORDER if spell_type not in FINAL_SPELL_TYPE_DESCRIPTIONS]
    if missing_descriptions:
        raise ValueError(f"Missing final spell type descriptions for: {missing_descriptions}")

    return {
        "canonical_spell_types": {
            spell_type: FINAL_SPELL_TYPE_DESCRIPTIONS[spell_type]
            for spell_type in pilot.FINAL_TYPE_ORDER
        },
        "canonical_keywords": {
            keyword: pilot.KEYWORD_VOCABULARY[keyword]
            for keyword in pilot.KEYWORD_ORDER
        },
    }


def validate_framework_payload(framework_payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    spell_type_descriptions = framework_payload.get("canonical_spell_types", {})

    missing_spell_types = [spell_type for spell_type in pilot.FINAL_TYPE_ORDER if spell_type not in spell_type_descriptions]
    extra_spell_types = sorted(set(spell_type_descriptions) - set(pilot.FINAL_TYPE_ORDER))
    if missing_spell_types:
        errors.append(f"framework: missing canonical_spell_types entries {missing_spell_types}")
    if extra_spell_types:
        errors.append(f"framework: unexpected canonical_spell_types entries {extra_spell_types}")

    for spell_type, description in spell_type_descriptions.items():
        if not description.strip():
            errors.append(f"framework: blank description for {spell_type}")
            continue

        normalized = description.lower()
        banned_terms = [term for term in FRAMEWORK_BANNED_DESCRIPTION_TERMS if term in normalized]
        if banned_terms:
            errors.append(f"framework: banned wording {banned_terms} in description for {spell_type}")

    return errors



def main() -> None:
    parser = argparse.ArgumentParser(description="Build production-final Sorcery spell datasets.")
    parser.add_argument("--count", type=int, help="Number of source spells to process. Defaults to the full corpus.")
    parser.add_argument("--label", default="final", help="Output file label prefix.")
    args = parser.parse_args()

    raw_data = json.loads(RAW_PATH.read_text())
    total_spells = len(raw_data["spells"])
    count = total_spells if args.count is None else max(1, min(args.count, total_spells))
    source_spells = raw_data["spells"][:count]

    split_assignments = pilot.compute_split_assignments(
        source_spells,
        enforce_target_distribution=count == total_spells,
    )
    records = [build_final_record(spell, split_assignments) for spell in source_spells]
    validation = validate_final_records(records)
    dataset_payload = build_dataset_payload(raw_data, records, args.label)
    framework_payload = build_framework_payload()
    framework_errors = validate_framework_payload(framework_payload)
    validation["framework_errors"] = framework_errors
    validation["framework_passed"] = not framework_errors
    validation["passed"] = validation["passed"] and not framework_errors
    validation["errors"].extend(framework_errors)
    if not validation["passed"]:
        raise SystemExit("Validation failed:\n" + "\n".join(validation["errors"]))

    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / f"{args.label}-spells.json").write_text(json.dumps(dataset_payload, indent=2, ensure_ascii=False) + "\n")
    (OUTPUT_DIR / f"{args.label}-framework.json").write_text(json.dumps(framework_payload, indent=2, ensure_ascii=False) + "\n")
    (OUTPUT_DIR / f"{args.label}-validation.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
