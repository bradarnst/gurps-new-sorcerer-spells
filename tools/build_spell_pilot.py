from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "spells-raw.json"
OUTPUT_DIR = ROOT / "processed"


CANONICAL_TYPES = {
    "Acid": "Secondary functional type for alkahest and other persistent corrosive attack families.",
    "Air": "Core college for atmosphere, wind, gas, lightning-in-air, and aerial movement.",
    "Animal": "Core college for beasts, animal minds, and animal enhancement.",
    "Artillery": "Secondary functional type for large-area bombardment, battlefields, mines, and indirect magical fire.",
    "Body Control": "Core college for respiration, internal physiology, and bodily alteration.",
    "Communication & Empathy": "Core college for signaling, perception, and social connection.",
    "Dream": "Secondary thematic type for sleep, dreams, nightmares, and oneiric travel.",
    "Earth": "Core college for stone, soil, and mineral effects.",
    "Energy": "Secondary thematic type for antimatter, plasma, raw power, and surge-heavy effects.",
    "Enchantment": "Core college for lasting magical augmentation.",
    "Fire": "Core college for heat and flame.",
    "Food": "Core college for preservation and nourishment.",
    "Force": "Secondary functional type for telekinetic pressure, force shields, and kinetic blows.",
    "Gate": "Core college for interplanar movement, barriers, and dimensional contact.",
    "Gravity": "Secondary thematic type for weight, falling, and altered gravitic pull.",
    "Healing": "Core college for restoration, curing, and recovery.",
    "Holy": "Secondary thematic type for angelic miracles and explicitly sacred utility.",
    "Illusion & Creation": "Core college for sensory deception and conjured phenomena.",
    "Knowledge": "Core college for detection, analysis, and information gathering.",
    "Light & Darkness": "Core college for illumination, obscurity, and visual conditions.",
    "Making & Breaking": "Core college for reshaping, storing, and altering objects or materials.",
    "Meta": "Core college for magic about magic.",
    "Mind Control": "Core college for imposed behavior and direct mental control.",
    "Movement": "Core college for locomotion and forced repositioning.",
    "Necromantic": "Core college for deathly, aging-adjacent, and life-draining themes.",
    "Plant": "Core college for vines, wood, and plant growth.",
    "Poison": "Secondary functional type for toxic clouds, contamination, and breathing hazards.",
    "Protection": "Core college for wards, resistances, and defensive shells.",
    "Radiation": "Secondary thematic type for irradiation, fallout, and mutagenic energy.",
    "Sound": "Core college for speech, noise, and sonic manipulation.",
    "Space": "Secondary thematic type for cosmic, vacuum, and starward effects.",
    "Spirit": "Secondary thematic type for souls, ghosts, spirit traffic, and the dead who still answer.",
    "Stealth": "Secondary functional type for concealment, hidden carry, and detection avoidance.",
    "Summoning": "Secondary functional type for called allies, servants, and outsider assistance.",
    "Technological": "Core college for machinery and devices.",
    "Time": "Secondary thematic type for temporal displacement, history, and accelerated or stolen time.",
    "Transformation": "Secondary functional type for alternate forms, shapechange, growth, and reduction.",
    "Water": "Core college for liquids, breathing in water, and aquatic adaptation.",
    "Weather": "Core college for storms and large-scale atmospheric violence.",
}


KEYWORD_VOCABULARY = {
    "Area": "Affects a placed area instead of a single target.",
    "Aura": "Centered on the subject's body and dangerous on contact.",
    "Buff": "Improves the subject instead of harming a foe.",
    "Control": "Restrains, repositions, shapes, or otherwise controls the battlefield.",
    "Cyclic": "Repeats automatically over later turns, minutes, or days.",
    "Damage": "Primarily inflicts HP, FP, or equivalent attack consequences.",
    "Debuff": "Imposes a lasting disadvantage or harmful condition.",
    "Defense": "Provides DR, resistance, immunity, or protective cover.",
    "Healing": "Restores, cures, or accelerates recovery.",
    "Information": "Detects, analyzes, or reveals facts.",
    "Jet": "Jet delivery or jet-like attack handling.",
    "Leveled": "Uses leveled scaling as a notable gameplay hook.",
    "Malediction": "Ignores ordinary range penalties and resolves as a resisted supernatural attack.",
    "Melee": "Requires close combat contact or a melee hit.",
    "Missile": "Projectile-style ranged attack.",
    "No-Signature": "Little or no visible magical tell when cast.",
    "Obvious": "Visible or otherwise conspicuous at the table.",
    "Persistent": "Sticks around after casting instead of resolving instantly.",
    "Resisted-DX": "Resisted primarily by DX.",
    "Resisted-HT": "Resisted primarily by HT.",
    "Resisted-HT-or-DX": "Resisted by whichever is better, HT or DX.",
    "Resisted-IQ": "Resisted primarily by IQ.",
    "Resisted-Variable": "Resisted by a special or mixed rule that needs reference to the spell text.",
    "Resisted-Will": "Resisted primarily by Will.",
    "Stealth": "Supports hidden action, quiet movement, or concealment.",
    "Summoning": "Calls or binds a separate creature or ally.",
    "Touch": "Requires touch or direct contact.",
    "Travel": "Moves the subject or enables meaningful repositioning.",
    "Unresisted": "Delivers its main effect without a normal resistance roll.",
    "Utility": "Primarily practical support instead of offense or defense.",
}


RAW_KEYWORD_MAP = {
    "None.": ["Utility"],
    "Obvious.": ["Obvious"],
    "Weapon Buff.": ["Buff"],
    "Armor Buff.": ["Buff", "Defense"],
    "Buff.": ["Buff"],
    "Buff, Incarnum.": ["Buff", "Utility"],
    "Resisted (HT).": ["Resisted-HT", "Malediction", "Debuff"],
    "Resisted (Will).": ["Resisted-Will", "Malediction", "Debuff"],
    "Resisted (IQ).": ["Resisted-IQ", "Debuff"],
    "Area (Leveled).": ["Area", "Leveled"],
    "Area (Fixed).": ["Area"],
    "Area (Special).": ["Area"],
    "Jet, Obvious.": ["Jet", "Damage", "Obvious"],
    "Missile, Obvious.": ["Missile", "Damage", "Obvious"],
    "Missile.": ["Missile", "Damage"],
    "Information.": ["Information"],
    "None or Buff.": ["Utility", "Buff"],
    "Area (Leveled), Buff.": ["Area", "Leveled", "Buff"],
    "Area (Leveled), Obvious.": ["Area", "Leveled", "Obvious"],
    "Area (Leveled), Resisted (the higher of HT or DX).": ["Area", "Leveled", "Resisted-HT-or-DX", "Control"],
}


RAW_LABEL_HINTS: list[tuple[str, list[str]]] = [
    ("communication and empathy", ["Communication & Empathy"]),
    ("movement and communication", ["Movement", "Communication & Empathy"]),
    ("illusion and creation", ["Illusion & Creation"]),
    ("light & darkness", ["Light & Darkness"]),
    ("light and darkness", ["Light & Darkness"]),
    ("making & breaking", ["Making & Breaking"]),
    ("body control", ["Body Control"]),
    ("mind control", ["Mind Control"]),
    ("elemental weapon transformation", ["Transformation", "Making & Breaking"]),
    ("elemental body", ["Transformation"]),
    ("boost attribute", ["Body Control"]),
    ("personal gate and gravity", ["Gate", "Gravity"]),
    ("personal food, force, fungus", ["Food", "Force", "Plant"]),
    ("em and weather", ["Weather", "Technological"]),
    ("essential earth", ["Earth", "Making & Breaking"]),
    ("psychic", ["Mind Control", "Knowledge"]),
    ("communication", ["Communication & Empathy"]),
    ("alkahest", ["Acid"]),
    ("acid", ["Acid"]),
    ("air", ["Air"]),
    ("angelic", ["Holy"]),
    ("animal", ["Animal"]),
    ("antimagic", ["Meta", "Protection"]),
    ("antimatter", ["Energy", "Space"]),
    ("artillery", ["Artillery"]),
    ("banefire", ["Fire", "Necromantic"]),
    ("banestorm", ["Gate", "Weather"]),
    ("bio-tech", ["Technological", "Body Control"]),
    ("blasting", ["Artillery"]),
    ("book", ["Knowledge"]),
    ("creation", ["Illusion & Creation"]),
    ("cyclic elemental", ["Weather"]),
    ("death", ["Necromantic"]),
    ("divination", ["Knowledge"]),
    ("dream", ["Dream", "Mind Control"]),
    ("earth", ["Earth"]),
    ("energy", ["Energy"]),
    ("enchantment", ["Enchantment"]),
    ("ethical", ["Holy"]),
    ("fire", ["Fire"]),
    ("flight", ["Movement"]),
    ("fluid", ["Water"]),
    ("food", ["Food"]),
    ("force", ["Force"]),
    ("fuel", ["Fire", "Technological"]),
    ("fungus", ["Plant"]),
    ("gate", ["Gate"]),
    ("glass", ["Earth", "Making & Breaking"]),
    ("gravity", ["Gravity", "Movement"]),
    ("gunman", ["Technological"]),
    ("healing", ["Healing"]),
    ("hellfire", ["Fire", "Necromantic"]),
    ("ice", ["Water", "Weather"]),
    ("incarnum", ["Meta"]),
    ("infravision", ["Knowledge", "Light & Darkness"]),
    ("knowledge", ["Knowledge"]),
    ("lava", ["Earth", "Fire"]),
    ("lightning", ["Air", "Weather", "Energy"]),
    ("light", ["Light & Darkness"]),
    ("limb", ["Body Control"]),
    ("machine", ["Technological"]),
    ("memory", ["Knowledge", "Mind Control"]),
    ("metal", ["Earth", "Making & Breaking"]),
    ("meta", ["Meta"]),
    ("monster", ["Animal"]),
    ("moon", ["Light & Darkness"]),
    ("movement", ["Movement"]),
    ("necromantic", ["Necromantic"]),
    ("new poison", ["Poison"]),
    ("new prismatic", ["Light & Darkness"]),
    ("plant", ["Plant"]),
    ("plasma", ["Energy", "Fire"]),
    ("poison", ["Poison"]),
    ("possession", ["Mind Control", "Spirit"]),
    ("power", ["Meta"]),
    ("radiation", ["Radiation"]),
    ("raw magic", ["Meta"]),
    ("revised elemental", ["Weather"]),
    ("serpentine", ["Animal"]),
    ("sound", ["Sound"]),
    ("space", ["Space", "Gate"]),
    ("spells of the past", ["Time"]),
    ("spirit", ["Spirit", "Necromantic"]),
    ("stealth", ["Stealth"]),
    ("steam", ["Water", "Fire"]),
    ("technological", ["Technological"]),
    ("time", ["Time"]),
    ("transformation", ["Transformation"]),
    ("water", ["Water"]),
    ("weather", ["Weather"]),
    ("winged folk", ["Animal", "Movement"]),
    ("yellow", ["Light & Darkness"]),
    ("zombie", ["Necromantic", "Spirit"]),
]


TEXT_TYPE_HINTS: dict[str, tuple[str, ...]] = {
    "Acid": ("acid", "alkahest", "corrosion"),
    "Air": ("air", "wind", "aerial", "cloud", "breath", "smoke", "fog", "gas", "odor", "scent", "oxygen", "vortex"),
    "Animal": ("animal", "beast", "hybrid", "hound", "horse", "falcon", "spider", "serpent", "snake", "egg", "mount"),
    "Artillery": ("barrage", "blast", "mine", "minefield", "bombardment", "dome", "circle", "swarm", "field", "towering inferno", "cone"),
    "Body Control": ("body", "blood", "lung", "respiratory", "breathing", "heart", "fatigue", "limb", "crippling injury", "fit"),
    "Communication & Empathy": ("message", "messenger", "speech", "speak", "language", "empathy", "emotion", "attraction", "friend"),
    "Dream": ("dream", "nightmare", "sleep"),
    "Earth": ("earth", "stone", "boulder", "sand", "glass", "metal", "lava", "seismic", "mud", "gem"),
    "Energy": ("energy", "plasma", "antimatter", "surge", "powerstone", "mana storm"),
    "Enchantment": ("enchant", "imbue", "charged", "charge powerstone"),
    "Fire": ("fire", "flame", "burn", "inferno", "heat", "scald", "hellfire", "banefire"),
    "Food": ("food", "drink", "feast", "hunger", "meal"),
    "Force": ("force", "telekin", "ram", "knockback", "bullet shield", "bullet protection", "deflect missile"),
    "Gate": ("gate", "portal", "plane", "world", "dimension", "dimensional", "astral", "phase", "banish"),
    "Gravity": ("gravity", "weightless", "heavy", "falling"),
    "Healing": ("heal", "healing", "cure", "restoration", "recover", "disease", "regeneration"),
    "Holy": ("angel", "celestial", "divine", "faith", "holy"),
    "Illusion & Creation": ("illusion", "mirage", "invisible", "disguise", "mansion", "blacksphere"),
    "Knowledge": ("seek", "detect", "know", "vision", "monitor", "test", "probe", "divination", "analysis", "analyzing"),
    "Light & Darkness": ("light", "dark", "shadow", "glow", "illumination", "invisible", "black"),
    "Making & Breaking": ("lock", "seal", "weapon", "book", "shards", "repair", "gunpowder", "trap", "create air", "purify air"),
    "Meta": ("dispel", "counterspell", "magic zone", "arcane suppression", "powerstone", "lend spell"),
    "Mind Control": ("dominate", "command", "emotion", "behavior", "master", "possession", "terror", "stun", "censure", "fright"),
    "Movement": ("flight", "fly", "move", "jump", "step", "travel", "speed", "teleport", "ride", "shift"),
    "Necromantic": ("death", "dead", "undead", "corpse", "grave", "reaper", "wither", "wilting", "mutilation"),
    "Plant": ("plant", "vine", "tree", "fungus", "weed", "thorn", "wood"),
    "Poison": ("poison", "toxic", "venom", "plague", "disease", "noxious", "brimstone"),
    "Protection": ("protection", "resist", "ward", "shield", "armor", "guard", "invulnerability", "block"),
    "Radiation": ("radiation", "irradiate", "fallout"),
    "Sound": ("sound", "voice", "word", "scream", "song", "silence"),
    "Space": ("space", "void", "star", "cosmic"),
    "Spirit": ("spirit", "ghost", "soul", "ethereal", "astral", "undead"),
    "Stealth": ("stealth", "silent", "hide", "hidden", "cloak", "unseen", "invisible"),
    "Summoning": ("summon", "servant", "ally", "call"),
    "Technological": ("bullet", "gun", "machine", "powder", "technological", "bio-tech", "electromagnetic", "radio"),
    "Time": ("time", "future", "past", "history", "temporal"),
    "Transformation": ("form", "shape", "transform", "change", "grow", "reduce", "body of", "dragon", "giant"),
    "Water": ("water", "ice", "steam", "liquid", "fluid", "aquatic", "drown", "scald"),
    "Weather": ("storm", "lightning", "rain", "snow", "thunder", "weather", "windstorm"),
}


ROLE_CODAS: dict[str, tuple[str, ...]] = {
    "control": (
        "Used well, it governs the field more than any single foe.",
        "The wise cast it to dictate terms, not merely to make a mess.",
    ),
    "damage": (
        "One does not cast it for subtlety, only for results.",
        "No maester would call it gentle, but gentleness is seldom the point.",
    ),
    "defense": (
        "Prudent folk invoke it before steel starts talking.",
        "It is the sort of precaution that seems excessive until the arrows arrive.",
    ),
    "healing": (
        "Any healer worth his chain will see the use of that at once.",
        "It is a merciful working, which is not the same thing as a cheap one.",
    ),
    "information": (
        "Better to know such things beforehand than bleed for ignorance after.",
        "Learning first and regretting later remains the sounder order of operations.",
    ),
    "summoning": (
        "As ever with called servants, the casting is often the easiest part.",
        "The bargain begins once the creature arrives, not before.",
    ),
    "travel": (
        "Distance is less impressive once one learns how to insult it properly.",
        "It is chiefly valued by those who dislike the road, the climb, or both.",
    ),
    "utility": (
        "Plainly put, it is a useful working when circumstances sour.",
        "No grand spectacle, but practical magic seldom apologizes for itself.",
    ),
}


VARIANT_MARKERS = ("personal ", "mass ", "improved ", "lesser ", "greater ", "permanent ")


MANUAL_OVERRIDES: dict[str, dict[str, Any]] = {
    "Absorb Weapon": {
        "spell_types": ["Making & Breaking", "Stealth"],
        "keywords": ["Touch", "Utility", "Stealth", "Persistent"],
        "description": "Lay a hand upon an unattended weapon and tuck it away within the flesh, though in truth it rests elsewhere entirely. The arm bears only a faint blotch, the weapon may weigh no more than spell level × Basic Lift / 10 lbs., and it may be drawn in a second or with Fast-Draw until the spell ends.",
    },
    "Entangling Staff": {
        "spell_types": ["Plant", "Body Control"],
        "keywords": ["Melee", "Control", "Damage", "Obvious", "Persistent", "Leveled"],
        "description": "Strike with a quarterstaff or long staff and have living vines answer the blow. The victim suffers the staff's usual damage, is grappled at ST equal to spell level, may be further bound by recasting, and remains at the mercy of the constricting growth so long as you keep it readied.",
    },
    "Exacting Shot": {
        "spell_types": ["Knowledge"],
        "keywords": ["Buff", "Leveled", "No-Signature", "Utility"],
        "description": "For three minutes, a ranged weapon flies truer than its maker had any right to expect. It grants +1 to hit per spell level, though prudent keepers of the rules may still cap the bonus by the setting's TL.",
    },
    "Healthful Rest": {
        "spell_types": ["Healing"],
        "keywords": ["Buff", "Healing", "No-Signature", "Utility"],
        "description": "Grant the subject a day's rest of uncommon virtue: all rolls to recover HP or overcome crippling injury are made at +5 HT. In the dearer version, each successful HP recovery roll restores 2 HP instead of the customary 1.",
    },
    "Iron Silence": {
        "spell_types": ["Protection", "Stealth"],
        "keywords": ["Buff", "No-Signature", "Stealth", "Utility"],
        "description": "For 30 minutes, the subject moves as quietly under burden as a lightly clad thief. The boon ignores Stealth penalties from encumbrance of any sort, not merely noisy harness.",
    },
    "Nature’s Favor": {
        "spell_types": ["Animal"],
        "keywords": ["Buff", "No-Signature", "Utility"],
        "description": "For three minutes, bestow Luck upon a single animal. Kennelmasters, falconers, and huntsmen alike will find the use of it plain enough.",
    },
    "Train Animal": {
        "spell_types": ["Animal", "Knowledge"],
        "keywords": ["Buff", "Leveled", "No-Signature", "Utility"],
        "description": "Raise an animal's effective IQ for training by 1 per level, to no more than IQ 5, and do so in a fashion that truly lasts. Dispel Magic, Remove Curse, and no-mana ground will not unteach the beast.",
    },
    "Age (Variant)": {
        "spell_types": ["Body Control"],
        "keywords": ["Malediction", "Resisted-HT", "Debuff", "No-Signature"],
        "description": "Should the subject fail HT, it is made one year older at once, with no gaudy display to warn the hall. Time, when summoned so neatly, can be quite rude.",
        "dedupe": {"status": "variant", "group": "ageing-single-year", "reason": "Keep distinct from Temporary Ageing because this version is permanent."},
    },
    "Burden of Time": {
        "spell_types": ["Necromantic"],
        "keywords": ["Area", "Leveled", "Damage", "Persistent", "Unresisted", "No-Signature"],
        "description": "Set a wandering patch of withering years upon the field for 10 seconds. All living creatures within age 1d-1 years each second, though the loss is temporary and may be shed later by successful Original HT rolls made when healing would otherwise be wasted.",
    },
    "Decrepify": {
        "spell_types": ["Body Control"],
        "keywords": ["Touch", "Melee", "Malediction", "Resisted-HT", "Debuff", "Leveled"],
        "description": "A mere touch, if it lands and the subject fails HT, lays 1d years per spell level upon living flesh forever. It is close work and ugly work, as such arts commonly are.",
    },
    "Progeria": {
        "spell_types": ["Body Control"],
        "display_name": "Premature Ageing",
        "keywords": ["Malediction", "Resisted-HT", "Debuff", "Cyclic", "No-Signature", "Persistent", "Leveled"],
        "description": "Lay a curse that ages a living subject by one year at once and again each day for 9 days more. Each extra level adds 10 further daily cycles, and only Remove Curse or its peers will cut the thread early.",
    },
    "Protection from Ageing": {
        "spell_types": ["Protection"],
        "display_name": "Ward Against Ageing",
        "keywords": ["Buff", "Defense", "No-Signature"],
        "description": "For three minutes, the subject bears Unaging and may meet magical senescence without bowing to it. Useful whenever rival sorcerers grow too fond of the calendar.",
    },
    "Reaper’s Embrace": {
        "spell_types": ["Necromantic"],
        "keywords": ["Buff", "Aura", "Damage", "Unresisted", "No-Signature"],
        "description": "For three minutes, the subject is mantled in a black aura that ages anyone who touches him by one year. It is a persuasive answer to grapplers and all others who mistake proximity for safety.",
    },
    "Temporary Ageing": {
        "spell_types": ["Body Control"],
        "keywords": ["Malediction", "Resisted-HT", "Debuff", "No-Signature"],
        "description": "Should the subject fail HT, one year is laid upon him for a time only. The stolen year returns later, one by one, through successful Original HT rolls made when healing would otherwise avail nothing.",
        "dedupe": {"status": "variant", "group": "ageing-single-year", "reason": "Keep distinct from Age (Variant) because this version is temporary and self-correcting."},
    },
    "Aerial Entombment": {
        "spell_types": ["Air", "Gate"],
        "keywords": ["Malediction", "Resisted-HT", "Control", "Persistent", "No-Signature"],
        "description": "Outdoors, a failed HT roll consigns the subject to a prison in the clouds and to suspended animation besides. There he neither ages nor hungers nor thirsts nor breathes, and he remains so until someone has the wit and altitude to free him.",
    },
    "Aerial Flight": {
        "spell_types": ["Air", "Movement"],
        "keywords": ["Buff", "Travel", "No-Signature"],
        "description": "For three minutes, the subject may fly and hover at Basic Speed × 2, provided there is proper air to bear him. In vacuum, trace atmosphere, or water, the working affords no help at all.",
        "dedupe": {"status": "variant", "group": "aerial-flight", "reason": "Keep distinct from Personal Aerial Flight because this version is ranged and temporary on another subject."},
    },
    "Aerial Servant": {
        "spell_types": ["Air", "Summoning"],
        "keywords": ["Summoning", "Control", "Utility", "Persistent"],
        "description": "After an hour's ritual and a Quick Contest of Will, you may compel an unwilling aerial servant of considerable potency to appear. It serves for hours equal to your margin of victory, but neglect the spell and the creature will remember precisely why it hates you.",
    },
    "Air Vision": {
        "spell_types": ["Air", "Knowledge"],
        "keywords": ["Buff", "Information", "Leveled", "No-Signature"],
        "description": "For three minutes, the subject sees through smoke, fog, dust, sand, and like obscurants to a depth of six inches per spell level. The benefit stacks amiably with other vision gifts.",
    },
    "Air Vortex": {
        "spell_types": ["Air", "Movement"],
        "keywords": ["Area", "Leveled", "Control", "Travel", "Resisted-HT-or-DX", "No-Signature"],
        "description": "Raise a swirling vortex that seizes all within its area, turns them vaporous, and carries them about at Move 8 for 9 seconds. Victims may resist with the better of HT or DX; those restored to flesh return stunned until they recover.",
    },
    "Airtight": {
        "spell_types": ["Air", "Food"],
        "keywords": ["Buff", "Utility", "Persistent", "No-Signature"],
        "description": "Seal a reasonably sound bottle, box, jar, or similar vessel for one week against dust, foul air, and other airborne intrusions. It preserves contents well enough, though it does not perform the courtesy of sterilizing them.",
    },
    "Breathe Air": {
        "spell_types": ["Air", "Water"],
        "keywords": ["Buff", "Utility", "No-Signature"],
        "description": "For 30 minutes, a creature accustomed to water may breathe common air without surrendering its gift for water-breathing. Plain, practical, and much admired by those who dislike drowning on land.",
    },
    "Change Air": {
        "spell_types": ["Air", "Making & Breaking"],
        "keywords": ["Touch", "Control", "Utility"],
        "description": "Touch a mass of gas and, on a successful IQ roll, transmute it permanently into another gas within a radius up to spell level in yards. Even good air may be made from bad, though a critical failure invites the sort of lesson apprentices remember.",
    },
    "Clean Breath": {
        "spell_types": ["Air", "Body Control"],
        "keywords": ["Buff", "Defense", "No-Signature"],
        "description": "For 30 minutes, the subject's lungs sift dust, smoke, pollen, and even tear gas from the air. Do not expect the spell to save him from contact agents or subtler poisons beyond the reach of ordinary filter lungs.",
    },
    "Create Air": {
        "spell_types": ["Air"],
        "keywords": ["Touch", "Utility"],
        "description": "On a successful IQ roll, conjure breathable air within arm's reach in a radius of one yard per spell level. Each cubic foot will sustain one person for a minute, which is often all the mercy a sealed chamber affords.",
        "dedupe": {"status": "variant", "group": "air-creation", "reason": "Keep distinct from Essential Air because the created substance and secondary combustion effects differ."},
    },
    "Destroy Air": {
        "spell_types": ["Air"],
        "keywords": ["Touch", "Control", "Utility"],
        "description": "On a successful IQ roll, unmake the air around your touch point in a radius of one yard per spell level. It affects only inanimate air, but that is scant comfort to anyone who meant to breathe it.",
    },
    "Devitalize Air": {
        "spell_types": ["Air", "Poison"],
        "keywords": ["Area", "Leveled", "Damage", "Persistent"],
        "description": "Set a drifting two-yard radius of dead air upon a place, so that any who inhale it suffer 1d-2 FP as from suffocation. The blight endures until sound air diffuses back, or indefinitely in a chamber sealed too well for its own good.",
    },
    "Embolism": {
        "spell_types": ["Air", "Body Control"],
        "keywords": ["Malediction", "Resisted-HT", "Damage", "No-Signature"],
        "description": "Should the subject fail HT, a bubble of air in the blood fells him as a mortal stroke: unconscious at once, with death checks each 30 minutes until treated or absurdly fortunate. It troubles only living breathing creatures with blood and brains.",
    },
    "Essential Air": {
        "spell_types": ["Air"],
        "keywords": ["Touch", "Utility", "Buff"],
        "description": "On a successful IQ roll, create essential air rather than the common sort in a radius of one yard per spell level. Each cubic foot supports breathing for three times as long, and fires within it burn hotter by +1 damage per die.",
        "dedupe": {"status": "variant", "group": "air-creation", "reason": "Keep distinct from Create Air because essential air lasts differently and boosts fire damage."},
    },
    "Haze": {
        "spell_types": ["Air", "Light & Darkness"],
        "keywords": ["Area", "Leveled", "Control", "Obvious"],
        "description": "Lay a shimmer of muggy air, dust, or mist across an area and impose -1 to vision rolls through it, Infravision included. It muddles sight without fully closing the world to the eye.",
    },
    "Monitor Air": {
        "spell_types": ["Air", "Knowledge"],
        "keywords": ["Buff", "Information", "No-Signature"],
        "description": "For 30 minutes, the subject gains an instinctive sense of whether the air about him is safe to breathe. If the follow-up IQ roll succeeds, he may also discern what impurity has spoiled it.",
        "dedupe": {"status": "variant", "group": "air-analysis", "reason": "Keep distinct from Test Air and Seek Air because this is an ongoing subject buff rather than a one-shot scan."},
    },
    "Odor": {
        "spell_types": ["Air", "Communication & Empathy"],
        "keywords": ["Area", "Control", "Utility", "Persistent"],
        "description": "Compel the air in an area to carry any scent you know, across a radius governed by spell level. The smell abides while you concentrate and lingers about an hour afterward, which is longer than some reputations deserve.",
    },
    "Personal Aerial Flight": {
        "spell_types": ["Air", "Movement"],
        "keywords": ["Buff", "Travel", "Persistent"],
        "description": "You yourself may fly and hover at Basic Speed × 2 for as long as you maintain the spell, provided proper air remains to hold you aloft. In water or vacuum, pride must suffice.",
        "dedupe": {"status": "variant", "group": "aerial-flight", "reason": "Keep distinct from Aerial Flight because this version is self-only and indefinite."},
    },
    "Purify Air": {
        "spell_types": ["Air", "Making & Breaking"],
        "keywords": ["Touch", "Utility", "Control"],
        "description": "Touch fouled air and, on a successful IQ roll, strip away its impurities in a radius of one yard per spell level. It is the honest remedy for smoke, taint, and poison when the air can still be made fit to breathe.",
    },
    "Resist Air": {
        "spell_types": ["Air", "Protection"],
        "keywords": ["Buff", "Defense", "Leveled", "No-Signature"],
        "description": "For 30 minutes, the subject gains heavy protection against air and wind: DR equal to spell level × 10 against both outward and inward harm, plus immunity to resisted air effects. Few answers are so firm, save not standing in the storm at all.",
    },
    "Seek Air": {
        "spell_types": ["Air", "Knowledge"],
        "keywords": ["Information", "Utility"],
        "description": "On a successful Per roll, learn the exact direction and distance to the nearest meaningful source of air. A follow-up IQ roll tells what sort of source it is, and the improved version extends the search by long-distance modifiers.",
        "dedupe": {"status": "variant", "group": "air-analysis", "reason": "Keep distinct from Test Air and Monitor Air because this spell locates external sources instead of judging current air quality."},
    },
    "Shape Air": {
        "spell_types": ["Air"],
        "keywords": ["Area", "Leveled", "Control", "Utility", "Persistent"],
        "description": "Take hold of a connected mass of air within a radius up to spell level in yards and shape or move it at Move equal to spell level. Concentration is needed to work it, though not merely to keep it in being.",
    },
    "Shimmering Fields": {
        "spell_types": ["Air", "Weather"],
        "keywords": ["Area", "Leveled", "Damage", "Persistent", "Obvious"],
        "description": "Set a crackling field of discharges over an area, where each turn brings 1d burning surge damage to all within. Any who suffer penetrating damage must make HT or be physically stunned, which tends to improve their respect for weather.",
    },
    "Sparks": {
        "spell_types": ["Air", "Weather"],
        "keywords": ["Area", "Leveled", "Damage", "Obvious"],
        "description": "Loose a ring of erratic sparks about yourself that attacks all nearby at skill 12. Hits inflict 1d burning surge damage and may stun, while metal conductors make the display still more unruly.",
    },
    "Steal Breath": {
        "spell_types": ["Air", "Body Control"],
        "keywords": ["Malediction", "Resisted-HT", "Damage", "No-Signature"],
        "description": "A failed HT roll brings respiratory collapse little kinder than a heart attack: the victim falls to -FP, loses consciousness, and dies in HT/3 minutes without aid. Air elementals and those in Body of Air are destroyed outright, which is one way to settle an argument.",
    },
    "Stench": {
        "spell_types": ["Air", "Poison"],
        "keywords": ["Area", "Leveled", "Damage", "Persistent", "Resisted-HT", "Obvious"],
        "description": "Raise a drifting brimstone cloud that forces all within to resist HT-1 or suffer 1d toxic damage. Those laid low enough by it begin choking, then suffocating, then recovering from stun if fortune has not already lost interest.",
    },
    "Test Air": {
        "spell_types": ["Air", "Knowledge"],
        "keywords": ["Information", "Utility"],
        "description": "Judge at once whether the air about a seen or touched subject is fit to breathe. A successful IQ roll further reveals poison or other impurities, which is often preferable to finding out the vulgar way.",
        "dedupe": {"status": "variant", "group": "air-analysis", "reason": "Keep distinct from Seek Air and Monitor Air because this is a one-shot quality test on a specific subject or location."},
    },
    "Wall of Wind": {
        "spell_types": ["Air", "Protection"],
        "keywords": ["Area", "Leveled", "Control", "Defense", "Persistent", "Obvious"],
        "description": "Conjure a shapeable wall of wind for five minutes and need not tend it further once cast. Missiles are spoiled, those who cross it are hurled about, and loose debris may blind them besides.",
    },
    "Windstorm": {
        "spell_types": ["Air", "Weather"],
        "keywords": ["Area", "Leveled", "Control", "Defense", "Persistent", "Obvious"],
        "description": "Raise a mobile circular storm with a calm eye, one that hurls creatures sideways with doubled knockback while granting +2 Dodge against projectiles to all within. It is less a killing stroke than a thorough rearrangement of the battlefield.",
    },
    "Alkahest Jet": {
        "spell_types": ["Acid"],
        "keywords": ["Jet", "Damage", "Obvious", "Leveled"],
        "description": "Send forth a hand-cast jet of alkahest 10 yards long, dealing 1d corrosion per spell level and continuing to gnaw for one point per second per die. The stream lasts long enough to parry, and a good parry punishes the offending weapon or limb as well.",
        "dedupe": {"status": "variant", "group": "alkahest-jets", "reason": "Keep distinct from Spit Alkahest because this hand-cast jet can parry and uses different attack handling."},
    },
    "Alkahest Sphere": {
        "spell_types": ["Acid"],
        "keywords": ["Missile", "Damage", "Obvious", "Leveled"],
        "description": "Launch a dodgeable sphere of alkahest that deals 1d corrosion per spell level, then continues to eat away for one point per second per die. Only Essential Water washes the lingering harm clean, and Resist Acid merely halves the misery.",
    },
    "Rain of Alkahest": {
        "spell_types": ["Acid"],
        "keywords": ["Area", "Leveled", "Damage", "Persistent", "Obvious"],
        "description": "Summon a corrosive rain over an area for 30 seconds; any who spend part of their turn beneath it are attacked at skill 12. A hit deals 1d-1 corrosion and the usual lingering alkahest burn, while shields may serve as cover at regrettable cost.",
    },
    "Spit Alkahest": {
        "spell_types": ["Acid"],
        "keywords": ["Jet", "Damage", "Obvious", "Leveled"],
        "description": "Spew a 10-yard breath jet of alkahest that strikes like a long melee attack and ignores range penalties. It deals 1d corrosion per spell level and leaves the same lingering burn that only Essential Water can conveniently settle.",
        "dedupe": {"status": "variant", "group": "alkahest-jets", "reason": "Keep distinct from Alkahest Jet because this breath weapon cannot fill the defensive parry role."},
    },
    "Celestial Aid": {
        "spell_types": ["Protection", "Holy"],
        "keywords": ["Buff", "Defense", "No-Signature"],
        "description": "For three minutes, grant the subject DR 4 as an ablative force field and +1 against fear and intimidation. It is a modest grace, but modest graces often keep people alive.",
    },
    "Continual Flame": {
        "spell_types": ["Light & Darkness", "Holy"],
        "keywords": ["Buff", "Utility", "Persistent", "No-Signature"],
        "description": "Set a touched object to shedding torchlight forever, though without heat, smoke, or any need for air. It may be covered and hidden, but not smothered or quenched like an honest flame.",
    },
    "Cure Disease": {
        "spell_types": ["Healing", "Holy"],
        "keywords": ["Touch", "Healing", "Utility"],
        "description": "By touch and a successful IQ roll, cure one disease in a living subject. Repeated attempts on the same patient grow harder, failure costs 1d FP, and success costs FP according to the severity of the illness, as every healer eventually learns to his annoyance.",
    },
    "Age": {
        "spell_types": ["Necromantic"],
    },
    "Accelerate Pregnancy": {
        "spell_types": ["Body Control"],
        "display_name": "Quicken Pregnancy",
    },
    "Animal Ageing": {
        "spell_types": ["Body Control"],
    },
    "Avatar": {
        "spell_types": ["Communication & Empathy", "Protection"],
    },
    "Badger Paws": {
        "spell_types": ["Earth", "Transformation"],
    },
    "Create Implausible Material": {
        "display_name": "Conjure Unlikely Matter",
        "description": "Conjure solid but unnatural matter from the proper raw conditions: lightning from a storm, screams from a living throat, and the like. Such matter is unstable and vanishes after 10 seconds unless further effort is spent to make it endure.",
    },
    "Halt Ageing": {
        "spell_types": ["Healing"],
        "description": "For one month, the subject does not age.",
    },
    "I decided to go with the following two:Blessing of Magic": {
        "spell_types": ["Protection", "Holy"],
        "display_name": "Blessing of Magic",
    },
    "Irresistible Dance": {
        "spell_types": ["Mind Control"],
    },
    "Keen Taste and Smell": {
        "spell_types": ["Knowledge"],
    },
    "Keen Touch": {
        "spell_types": ["Knowledge"],
    },
    "Mass Badger Paws": {
        "spell_types": ["Earth", "Transformation"],
    },
    "My suggestion is to rework Cold as follows: Cold (Unofficial Sorcery Errata)": {
        "display_name": "Cold",
    },
    "My suggestion is to rework Heat as follows: Heat (Unofficial Sorcery Errata)": {
        "display_name": "Heat",
    },
    "Personal Halt Ageing": {
        "spell_types": ["Healing"],
        "description": "You do not age while this spell endures. Unlike most indefinite workings, it costs 1 FP per hour rather than per minute to maintain.",
    },
    "Personal Keen Taste and Smell": {
        "spell_types": ["Knowledge"],
    },
    "Personal Keen Touch": {
        "spell_types": ["Knowledge"],
    },
    "Personal Protection from Force": {
        "spell_types": ["Force", "Protection"],
        "display_name": "Personal Ward Against Force",
    },
    "Personal Protection from Incarnum": {
        "display_name": "Personal Ward Against Incarnum",
        "description": "You gain a +3 bonus on HT rolls made to resist incarnum abilities, including soulmeld effects.",
    },
    "Personal Protection from Magic": {
        "spell_types": ["Meta", "Protection"],
        "display_name": "Personal Ward Against Magic",
    },
    "Protection from (Ethical Category)": {
        "display_name": "Ward Against the Chosen Ethic",
    },
    "Protection from Force": {
        "display_name": "Ward Against Force",
    },
    "Protection from Incarnum": {
        "display_name": "Ward Against Incarnum",
        "description": "For three minutes, the subject gains a +3 bonus on HT rolls made to resist incarnum abilities, including soulmeld effects.",
    },
    "Protection from Magic": {
        "display_name": "Ward Against Magic",
    },
    "Protection from Nuclear Explosions": {
        "display_name": "Ward Against Nuclear Explosions",
    },
    "SAMPLE SPELL Detect Magic": {
        "display_name": "Detect Magic",
        "description": "Discern nearby magic at once by the ordinary principles of sight- or touch-borne detection.",
    },
    "SAMPLE SPELLS Explosive Runes": {
        "display_name": "Explosive Runes",
    },
    "Stop Bleeding": {
        "display_name": "Staunch Bleeding",
    },
    "The resulting spell looks like the following: Resist Cold": {
        "display_name": "Resist Cold",
    },
    "The resulting spell looks like the following: Resist Fire (Unofficial Sorcery Errata)": {
        "display_name": "Resist Fire",
    },
    "To make the spell scale and be closer to what is found in other books, replace it with the following: Fast Fire (Unofficial Sorcery Errata)": {
        "display_name": "Fast Fire",
    },
    "To make the spell scale and be closer to what is found in other books, replace it with the following: Slow Fire (Unofficial Sorcery Errata)": {
        "display_name": "Slow Fire",
    },
}


EDITORIAL_NAME_PREFIXES = (
    "I decided to go with the following two:",
    "My suggestion is to rework Cold as follows:",
    "My suggestion is to rework Heat as follows:",
    "The resulting spell looks like the following:",
    "To make the spell scale and be closer to what is found in other books, replace it with the following:",
    "SAMPLE SPELL ",
    "SAMPLE SPELLS ",
)

EXACT_DISPLAY_NAME_OVERRIDES: dict[str, str] = {
    "Age (Variant)": "One-Year Ageing",
    "All-Eater": "Universal Appetite",
    "Bedtime Reading": "Reading in Sleep",
    "Beast-Rouser": "Rouse Beast",
    "Beast-Soother": "Soothe Beast",
    "Bind Spirit (Type)": "Bind Spirit of a Chosen Kind",
    "Blessing of Freedom (2)": "Blessing of Freedom",
    "Bender Defender": "Drunkard’s Ease",
    "Command Spirit (Type)": "Command Spirit of a Chosen Kind",
    "Dispel (Ethical Category)": "Dispelling of the Chosen Ethic",
    "Exclude (Ethical Category)": "Exclusion of the Chosen Ethic",
    "File Transfer": "Transfer of Records",
    "Loyalty of (Ethical Category)": "Loyalty of the Chosen Ethic",
    "Magic Manager": "Arcane Quickening",
    "Magic Missile": "Arcane Dart",
    "Melee Manager": "Battle Quickening",
    "Mouth-Goes-Away": "Sealed Mouth",
    "No-Taste": "Tastelessness",
    "Numerology/Arithmancy": "Numerology",
    "Personal All-Eater": "Personal Universal Appetite",
    "Personal Bender Defender": "Personal Drunkard’s Ease",
    "Personal Melee Manager": "Personal Battle Quickening",
    "Personal No-Smell": "Personal Scentlessness",
    "Personal No-Taste": "Personal Tastelessness",
    "Quick-Aim": "Swift Aim",
    "Quick-Draw": "Swift Draw",
    "Rail Communication": "Messages Along the Rail",
    "Rail Teleport": "Passage Along the Rail",
    "Rail Teleport Other": "Send Another Along the Rail",
    "Rebuke (Ethical Category)": "Rebuke of the Chosen Ethic",
    "Repel (Ethical Category)": "Repulsion of the Chosen Ethic",
    "See Invisible": "See the Unseen",
    "Seek (Ethical Category)": "Seeking of the Chosen Ethic",
    "Sense (Ethical Category)": "Sensing of the Chosen Ethic",
    "Self-Destruct": "Self-Detonation",
    "Shadow Magic (Spell)": "Shadow of a Chosen Spell",
    "Snekrobolt": "Necrotic Serpent Bolt",
    "Sorcerer’s Stand-In": "Sorcerous Proxy",
    "Sorcerous Screwdriver": "Turning Finger",
    "Sorcerous Silencer": "Silencing Weapon",
    "Speak with Dead": "Speak with the Dead",
    "Sunburst (2)": "Blinding Sunburst",
    "System Switch": "Passage Between Rail Lines",
    "Train Teleport": "Passage of the Train",
    "Ubiquitous Touchscreen": "Touch Upon Glass",
}

POWER_WORD_DISPLAY_NAMES: dict[str, str] = {
    "Blind": "Word of Blindness",
    "Deafen": "Word of Deafness",
    "Disable": "Word of Disablement",
    "Distract": "Word of Distraction",
    "Fatigue": "Word of Fatigue",
    "Kill": "Word of Slaying",
    "Maladroit": "Word of Clumsiness",
    "Nauseate": "Word of Nausea",
    "Pain": "Word of Pain",
    "Petrify": "Word of Petrification",
    "Sicken": "Word of Sickness",
    "Stun": "Word of Stunning",
    "Weaken": "Word of Weakness",
}

CURSE_MISSILE_DISPLAY_TAILS: dict[str, str] = {
    "Clumsiness": "Clumsiness",
    "Curse": "Curses",
    "Frailty": "Frailty",
    "Hunger": "Hunger",
    "Itch": "Itching",
    "Pain": "Pain",
    "Perfume": "Perfume",
    "Retch": "Retching",
    "Spasm": "Spasm",
    "Strike Anosmic": "Scentlessness",
    "Strike Barren": "Barrenness",
    "Strike Blind": "Blindness",
    "Strike Deaf": "Deafness",
    "Strike Dumb": "Muteness",
    "Strike Numb": "Numbness",
    "Thirst": "Thirst",
}

EXACT_DESCRIPTION_OVERRIDES: dict[str, str] = {
    "Ambidexterity": "For three minutes, the subject gains Ambidexterity.",
    "Balance": "For three minutes, the subject gains Perfect Balance.",
    "Beast Summoning": "Seek out the nearest animal, learn its direction and distance, and call it to you for three minutes. If it reaches you, it remains nearby and docile unless you or your companions strike first.",
    "Bedtime Reading": "For a single period of sleep, the caster reads a dreamed copy of a touched book, scroll, or like text and may count that sleep as study.",
    "Call Monster": "Seek out the nearest non-sapient monster, learn its direction and distance, and call it to you for three minutes. It comes as swiftly as it can until it arrives or the spell ends.",
    "Cloud-Walking": "For three minutes, clouds bear the subject as solid ground at his ordinary Move. If he slips or is knocked down, a DX roll may let him catch himself upon the clouds again before he falls in earnest.",
    "Hold Breath": "For one minute, the subject gains Doesn’t Breathe. It does not provide air, but only delays suffocation long enough to reach safer conditions.",
    "Instant Regeneration": "By touch, restore one lost limb or organ at once. It mends living flesh only and must be laid upon the subject directly.",
    "Measure Gravity": "The caster instantly learns the local strength of gravity in the measure he best understands.",
    "Null Sphere": "The caster hurls a small sphere of black nothingness, a momentary gate to a realm hostile to common matter. All within six yards of impact must resist with HT, and those nearest the center suffer the harshest ruin.",
    "Personal Cloud-Walking": "So long as the spell is maintained, clouds bear the caster as solid ground at his ordinary Move. If he slips or is knocked down, a DX roll may let him catch himself upon the clouds again before he falls in earnest.",
    "Personal Hide Thoughts": "So long as the spell is maintained, the caster’s thoughts cannot be read or bent by workings of mind and will.",
    "Personal Hold Breath": "So long as the spell is maintained, the caster does not breathe. It does not provide air, but only delays suffocation long enough to reach safer conditions.",
    "Reflexes": "For three minutes, the subject gains Combat Reflexes.",
    "See Plant Health": "So long as the spell is maintained, sick or damaged plants stand out plainly in the caster’s sight.",
    "Simple Illusion": "Lay a visual illusion over an area for so long as it is maintained. It deceives sight alone, unlike the fuller and dearer Complex Illusion.",
    "Sorcerer’s Stand-In": "For one day, the subject may stand in an assistant’s place during a slow enchantment and may also bear the burden of Personal Sacrifice in the sorcerous method. The proxy contributes no mage-days of his own, and the replaced worker cannot labor elsewhere without breaking the original effort.",
    "Spatial Stability": "For three minutes, the subject is anchored in space and cannot be moved or harmed by teleportation and like spatial workings.",
    "Tell Weight": "With a touch, the caster instantly learns the weight of the subject.",
    "Zombie Summoning": "Seek out the nearest zombie, learn its direction and distance, and call it to you for three minutes. If it reaches you, it lingers nearby and does not attack unless you or your companions strike first.",
}


TYPE_DISPLAY_NAMES: dict[str, str] = {
    "Acid": "Acid",
    "Air": "Air",
    "Animal": "Animal",
    "Artillery": "Artillery",
    "Body Control": "Body Control",
    "Communication & Empathy": "Messages, Persuasion, and Fellow Feeling",
    "Dream": "Dream",
    "Earth": "Earth",
    "Energy": "Energy",
    "Enchantment": "Enchantment",
    "Fire": "Fire",
    "Food": "Victuals, Preservation, and Plenty",
    "Force": "Force",
    "Gate": "Gate",
    "Gravity": "Gravity",
    "Healing": "Healing",
    "Holy": "Holy",
    "Illusion & Creation": "Glamours, Phantoms, and Conjurings",
    "Knowledge": "Knowledge",
    "Light & Darkness": "Light, Shadow, and Radiance",
    "Making & Breaking": "Making & Breaking",
    "Meta": "The Higher Mysteries",
    "Mind Control": "Command, Influence, and Subjugation",
    "Movement": "Movement",
    "Necromantic": "Necromantic",
    "Plant": "Plant",
    "Poison": "Poison",
    "Protection": "Protection",
    "Radiation": "Radiation",
    "Sound": "Sound",
    "Space": "Space",
    "Spirit": "Spirit",
    "Stealth": "Stealth",
    "Summoning": "Summoning",
    "Technological": "Engines, Powder, and Devices",
    "Time": "Time",
    "Transformation": "Transformation",
    "Water": "Water",
    "Weather": "Weather",
}


APPROVED_CHILD_TYPE_DISPLAY_NAMES: dict[str, str] = {
    "Lesser Hexes & Afflictions": "Lesser Hexes & Afflictions",
    "Grand Arcana & Constructs": "Grand Arcana & Constructs",
    "Sorcerous Services & Rites": "Sorcerous Services & Rites",
    "Arcane Utilities & Implements": "Arcane Utilities & Implements",
    "Mana, Ley, and Power": "Mana, Leys, and Power",
    "Countermagic & Suppression": "Countermagic & Suppression",
    "Arcane Siphons & Frailties": "Arcane Siphons & Frailties",
    "Readings & Analysis": "Readings & Examinations",
    "Senses & Perception": "Senses & Perception",
    "Detection & Appraisal": "Detection & Appraisal",
    "Seekers & Trackers": "Seekers & Trackers",
    "Divination & Omens": "Divination & Omens",
    "Thoughts & Memory": "Thoughts & Memory",
    "Safeguards & Reliefs": "Safeguards & Reliefs",
    "Resistances & Immunities": "Resistances & Immunities",
    "Battle Blessings & Readiness": "Battle Blessings & Readiness",
    "Armor & Battle Shells": "Armor & Battle Shells",
    "Wards, Shields, and Barriers": "Wards, Shields, and Barriers",
    "Concealments & Counter-Senses": "Concealments & Counter-Senses",
    "Weapon Boons & Retaliations": "Weapon Boons & Retaliations",
    "Mental Curses & Counterwill": "Mental Curses & Counterwill",
    "Commands & Compulsion": "Commands & Compulsion",
    "Memory, Thought, and Will": "Memory, Thought, and Will",
    "Emotion & Morale": "Emotion & Morale",
    "Pain, Stun, and Collapse": "Pain, Stun, and Collapse",
    "Dreams, Sleep, and Delusion": "Dreams, Sleep, and Delusion",
    "Possession & Identity": "Possession & Identity",
    "Alteration, Growth, and Other Transmutations": "Alteration, Growth, and Other Transmutations",
    "Shapeshifting & Polymorph": "Shapeshifting & Polymorph",
    "Body Forms & Embodiments": "Body Forms & Embodiments",
    "Creation, Shape, and Matter": "Creation, Shape, and Matter",
    "Speed, Haste, and Handling": "Speed, Haste, and Handling",
    "Ways, Passage, and Travel": "Ways, Passage, and Travel",
    "Forced Movement & Restraint": "Forced Movement & Restraint",
    "Weapons & Battlework": "Weapons & Battlework",
    "Breaking, Shattering, and Ruin": "Breaking, Shattering, and Ruin",
    "Crafting, Repair, and Reshaping": "Crafting, Repair, and Reshaping",
    "Locks, Seals, and Traps": "Locks, Seals, and Traps",
    "Stone, Soil, and Sand": "Stone, Soil, and Sand",
    "Metal & Glass": "Metal & Glass",
    "Earthshape, Passage, and Transmutation": "Earthshape, Passage, and Transmutation",
    "Missiles, Jets, and Rays": "Missiles, Jets, and Rays",
    "Battlefield Zones & Fields": "Battlefield Zones & Fields",
    "Bursts, Barrages, and Bombardment": "Bursts, Barrages, and Bombardment",
    "Internal Ruin, Fatigue, and Decline": "Internal Ruin, Fatigue, and Decline",
    "Body Forms, Limbs, and Alteration": "Body Forms, Limbs, and Alteration",
    "Vital Functions & Augmentation": "Vital Functions & Augmentation",
    "Winds, Vapors, and Sky Passage": "Winds, Vapors, and Sky Passage",
    "Breath & Atmosphere": "Breath & Atmosphere",
    "Lightning of the Air": "Lightning of the Air",
    "Radiance, Sight, and Reflection": "Radiance, Sight, and Reflection",
    "Glamour, Color, and Prism": "Glamour, Color, and Prism",
    "Lightning & Radiant Assaults": "Lightning & Radiant Assaults",
    "Shadows & Obscurity": "Shadows & Obscurity",
    "Growth, Blessing, and Husbandry": "Growth, Blessing, and Husbandry",
    "Wood, Vines, and Plant Forms": "Wood, Vines, and Plant Forms",
    "Plant Lore, Speech, and Passage": "Plant Lore, Speech, and Passage",
    "Flame Assaults & Battlefire": "Flame Assaults & Battlefire",
    "Heat, Fuel, and Hearthwork": "Heat, Fuel, and Hearthwork",
    "Death Curses & Withering": "Death Curses & Withering",
    "Undead Animation & Command": "Undead Animation & Command",
    "Spirits of the Dead": "Spirits of the Dead",
    "Water Shaping & Passage": "Water Shaping & Passage",
    "Ice, Snow, and Frost": "Ice, Snow, and Frost",
    "Drowning, Dehydration, and Fluid Assaults": "Drowning, Dehydration, and Fluid Assaults",
    "Animal Command & Repelling": "Animal Command & Repelling",
    "Beast Forms & Traits": "Beast Forms & Traits",
    "Animal Companions, Mounts, and Summons": "Animal Companions, Mounts, and Summons",
    "Tempests, Lightning, and Winter Weather": "Tempests, Lightning, and Winter Weather",
    "Rain, Wind, and Greater Weather": "Rain, Wind, and Greater Weather",
    "Spirits, Wards, and the Dead": "Spirits, Wards, and the Dead",
    "Souls, Possession, and Bindings": "Souls, Possession, and Bindings",
}


APPROVED_SPLIT_CHILD_TYPES: dict[str, list[str]] = {
    "Meta": [
        "Lesser Hexes & Afflictions",
        "Grand Arcana & Constructs",
        "Sorcerous Services & Rites",
        "Arcane Utilities & Implements",
        "Mana, Ley, and Power",
        "Countermagic & Suppression",
        "Arcane Siphons & Frailties",
    ],
    "Knowledge": [
        "Readings & Analysis",
        "Senses & Perception",
        "Detection & Appraisal",
        "Seekers & Trackers",
        "Divination & Omens",
        "Thoughts & Memory",
    ],
    "Protection": [
        "Safeguards & Reliefs",
        "Resistances & Immunities",
        "Battle Blessings & Readiness",
        "Armor & Battle Shells",
        "Wards, Shields, and Barriers",
        "Concealments & Counter-Senses",
        "Weapon Boons & Retaliations",
    ],
    "Mind Control": [
        "Mental Curses & Counterwill",
        "Commands & Compulsion",
        "Memory, Thought, and Will",
        "Emotion & Morale",
        "Pain, Stun, and Collapse",
        "Dreams, Sleep, and Delusion",
        "Possession & Identity",
    ],
    "Transformation": [
        "Alteration, Growth, and Other Transmutations",
        "Shapeshifting & Polymorph",
        "Body Forms & Embodiments",
        "Creation, Shape, and Matter",
    ],
    "Movement": [
        "Speed, Haste, and Handling",
        "Ways, Passage, and Travel",
        "Forced Movement & Restraint",
    ],
    "Making & Breaking": [
        "Weapons & Battlework",
        "Breaking, Shattering, and Ruin",
        "Crafting, Repair, and Reshaping",
        "Locks, Seals, and Traps",
    ],
    "Earth": [
        "Stone, Soil, and Sand",
        "Metal & Glass",
        "Earthshape, Passage, and Transmutation",
    ],
    "Artillery": [
        "Missiles, Jets, and Rays",
        "Battlefield Zones & Fields",
        "Bursts, Barrages, and Bombardment",
    ],
    "Body Control": [
        "Internal Ruin, Fatigue, and Decline",
        "Body Forms, Limbs, and Alteration",
        "Vital Functions & Augmentation",
    ],
    "Air": [
        "Winds, Vapors, and Sky Passage",
        "Breath & Atmosphere",
        "Lightning of the Air",
    ],
    "Light & Darkness": [
        "Radiance, Sight, and Reflection",
        "Glamour, Color, and Prism",
        "Lightning & Radiant Assaults",
        "Shadows & Obscurity",
    ],
    "Plant": [
        "Growth, Blessing, and Husbandry",
        "Wood, Vines, and Plant Forms",
        "Plant Lore, Speech, and Passage",
    ],
    "Fire": [
        "Flame Assaults & Battlefire",
        "Heat, Fuel, and Hearthwork",
    ],
    "Necromantic": [
        "Death Curses & Withering",
        "Undead Animation & Command",
        "Spirits of the Dead",
    ],
    "Water": [
        "Water Shaping & Passage",
        "Ice, Snow, and Frost",
        "Drowning, Dehydration, and Fluid Assaults",
    ],
    "Animal": [
        "Animal Command & Repelling",
        "Beast Forms & Traits",
        "Animal Companions, Mounts, and Summons",
    ],
    "Weather": [
        "Tempests, Lightning, and Winter Weather",
        "Rain, Wind, and Greater Weather",
    ],
    "Spirit": [
        "Spirits, Wards, and the Dead",
        "Souls, Possession, and Bindings",
    ],
}

STABLE_FINAL_TYPES = [
    "Healing",
    "Force",
    "Communication & Empathy",
    "Energy",
    "Food",
    "Technological",
    "Poison",
    "Time",
    "Summoning",
    "Gate",
    "Gravity",
    "Stealth",
    "Acid",
    "Sound",
    "Space",
    "Illusion & Creation",
    "Holy",
    "Dream",
    "Enchantment",
    "Radiation",
]

FINAL_SPELL_TYPE_OVERRIDES: dict[str, list[str]] = {
    "Accelerate Pregnancy": ["Vital Functions & Augmentation"],
    "Age": ["Death Curses & Withering"],
    "Age (Variant)": ["Internal Ruin, Fatigue, and Decline"],
    "Animal Ageing": ["Internal Ruin, Fatigue, and Decline"],
    "Avatar": ["Communication & Empathy", "Safeguards & Reliefs"],
    "Badger Paws": ["Earthshape, Passage, and Transmutation", "Body Forms & Embodiments"],
    "Burden of Time": ["Death Curses & Withering"],
    "Decrepify": ["Internal Ruin, Fatigue, and Decline"],
    "Halt Ageing": ["Healing"],
    "Irresistible Dance": ["Commands & Compulsion"],
    "Keen Taste and Smell": ["Senses & Perception"],
    "Keen Touch": ["Senses & Perception"],
    "Mass Badger Paws": ["Earthshape, Passage, and Transmutation", "Body Forms & Embodiments"],
    "Personal Halt Ageing": ["Healing"],
    "Personal Keen Taste and Smell": ["Senses & Perception"],
    "Personal Keen Touch": ["Senses & Perception"],
    "Premature Ageing": ["Internal Ruin, Fatigue, and Decline"],
    "Protection from Ageing": ["Safeguards & Reliefs"],
    "Reaper’s Embrace": ["Death Curses & Withering"],
    "Temporary Ageing": ["Internal Ruin, Fatigue, and Decline"],
    "Ward Against Ageing": ["Safeguards & Reliefs"],
}

SPLIT_CHILD_DESCRIPTIONS: dict[str, str] = {
    child_type: f"Approved finalized child spell type under {parent_type}."
    for parent_type, child_types in APPROVED_SPLIT_CHILD_TYPES.items()
    for child_type in child_types
}

FINAL_SPELL_TYPES: dict[str, str] = {
    **{spell_type: description for spell_type, description in CANONICAL_TYPES.items() if spell_type in STABLE_FINAL_TYPES},
    **SPLIT_CHILD_DESCRIPTIONS,
}

FINAL_TYPE_ORDER = [
    child_type
    for parent_type in APPROVED_SPLIT_CHILD_TYPES
    for child_type in APPROVED_SPLIT_CHILD_TYPES[parent_type]
] + STABLE_FINAL_TYPES


TYPE_ORDER = list(CANONICAL_TYPES)
KEYWORD_ORDER = list(KEYWORD_VOCABULARY)


def order_unique(values: list[str], order: list[str]) -> list[str]:
    seen: set[str] = set()
    kept = [value for value in values if value and not (value in seen or seen.add(value))]
    position = {value: index for index, value in enumerate(order)}
    return sorted(kept, key=lambda value: (position.get(value, len(position)), value))


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def repair_sentence_spacing(text: str) -> str:
    return re.sub(r"([.!?])([A-Z“\"])", r"\1 \2", text or "")


def trim_period(text: str) -> str:
    return normalize_ws(text).rstrip(".")


def sentence_split(text: str) -> list[str]:
    normalized = normalize_ws(repair_sentence_spacing(text))
    if not normalized:
        return []
    protected = normalized
    for source, target in {
        "vs.": "vs§",
        "p.": "p§",
        "pp.": "pp§",
        "e.g.": "e§g§",
        "i.e.": "i§e§",
    }.items():
        protected = protected.replace(source, target)
    parts = re.split(r"(?<=[.!?])\s+", protected)
    repaired = [part.replace("§", ".") for part in parts]
    return [part.strip() for part in repaired if part.strip()]


def clean_source_prose(text: str) -> str:
    cleaned = repair_sentence_spacing(text)
    cleaned = re.sub(r"\([^)]*(?:GURPS|p\.\s*|pp\.\s*|GM['’]s call)[^)]*\)", "", cleaned)
    cleaned = re.sub(r"\bsee [A-Z][A-Za-z'’\- ]+,\s*p+\.\s*[A-Z]?\d+(?:-\d+)?", "", cleaned)
    cleaned = re.sub(r"\bp+\.\s*[A-Z]?\d+(?:-\d+)?\b", "", cleaned)
    cleaned = re.sub(r"\bpp+\.\s*[A-Z]?\d+(?:-\d+)?\b", "", cleaned)
    cleaned = cleaned.replace("“", "").replace("”", "")
    cleaned = cleaned.replace("…", "...")
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)
    return normalize_ws(cleaned)


def is_duration_stub(sentence: str) -> bool:
    lowered = trim_period(sentence).lower()
    duration_markers = ("instantaneous", "permanent", "indefinite", "special", "second", "minute", "hour", "day", "week", "month", "year")
    return len(lowered.split()) <= 4 and any(marker in lowered for marker in duration_markers)


def should_skip_summary_sentence(sentence: str, source_field: str) -> bool:
    lowered = sentence.lower()
    if source_field == "duration" and (is_duration_stub(sentence) or lowered.startswith(("as ", "like in ", "as per "))):
        return True

    editorial_markers = (
        "the gm",
        "campaign",
        "this changes the full cost",
        "setting's tl",
        "setting’s tl",
        "hour of play",
        "game time",
        "see p.",
        "see pp.",
        "gurps ",
        "pyramid #",
    )
    if any(marker in lowered for marker in editorial_markers):
        return True

    return lowered.startswith((
        "failure means",
        "critical failure means",
        "for example,",
        "to do so,",
    ))


def rewrite_summary_sentence(sentence: str) -> str:
    rewritten = normalize_ws(sentence)
    rewrites = (
        (r"^The (basic|improved) \([^)]*\) version of this spell ", "This spell "),
        (r"^The (basic|improved) version of this spell ", "This spell "),
        (r"^The (basic|improved) \([^)]*\) spell ", "This spell "),
        (r"^The (basic|improved) spell ", "This spell "),
        (r"^With the (basic|improved) \([^)]*\) version of this spell,\s*", ""),
        (r"^With the (basic|improved) version of this spell,\s*", ""),
    )
    for pattern, replacement in rewrites:
        updated = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
        if updated != rewritten:
            return normalize_ws(updated)
    return rewritten


def summarize_source_prose(text: str, source_field: str) -> str:
    sentences = sentence_split(clean_source_prose(text))
    chosen: list[str] = []
    current_length = 0
    for raw_sentence in sentences:
        sentence = rewrite_summary_sentence(raw_sentence)
        if should_skip_summary_sentence(sentence, source_field):
            continue
        addition = len(sentence) + (1 if chosen else 0)
        if chosen and (len(chosen) >= 2 or current_length + addition > 320):
            break
        chosen.append(sentence)
        current_length += addition

    if not chosen:
        for raw_sentence in sentences:
            sentence = rewrite_summary_sentence(raw_sentence)
            if source_field == "duration" and is_duration_stub(sentence):
                continue
            chosen.append(sentence)
            if len(chosen) >= 2:
                break

    return " ".join(chosen)


def stable_index(seed: str, size: int) -> int:
    if size <= 0:
        return 0
    return sum(ord(char) for char in seed) % size


def concise_field(text: str, max_chars: int = 80) -> str:
    normalized = trim_period(text)
    if not normalized:
        return "Special"
    first_clause = re.split(r"[.;]", normalized, maxsplit=1)[0].strip()
    if len(first_clause) > max_chars:
        first_clause = first_clause[: max_chars - 1].rstrip() + "…"
    return first_clause or normalized[: max_chars]


def canonical_resistance(fragment: str) -> list[str]:
    lowered = fragment.lower()
    if "ht" in lowered and "dx" in lowered:
        return ["Resisted-HT-or-DX", "Debuff"]
    if "ht" in lowered and "will" in lowered:
        return ["Resisted-Variable", "Debuff"]
    if "will" in lowered and "spell" in lowered:
        return ["Resisted-Variable", "Debuff"]
    if "ht" in lowered:
        return ["Resisted-HT", "Debuff"]
    if "will" in lowered:
        return ["Resisted-Will", "Debuff"]
    if "iq" in lowered:
        return ["Resisted-IQ", "Debuff"]
    if "dx" in lowered:
        return ["Resisted-DX", "Debuff"]
    return ["Resisted-Variable", "Debuff"]


def parse_raw_keywords(raw: str) -> list[str]:
    normalized_raw = normalize_ws(raw)
    if normalized_raw in RAW_KEYWORD_MAP:
        return order_unique(RAW_KEYWORD_MAP[normalized_raw], KEYWORD_ORDER)

    tokens: list[str] = []
    lowered = normalized_raw.lower()
    if "none" in lowered:
        tokens.append("Utility")
    if "buff" in lowered:
        tokens.append("Buff")
    if "armor buff" in lowered:
        tokens.append("Defense")
    if "information" in lowered:
        tokens.append("Information")
    if "obvious" in lowered:
        tokens.append("Obvious")
    if "missile" in lowered:
        tokens.extend(["Missile", "Damage"])
    if "jet" in lowered:
        tokens.extend(["Jet", "Damage"])
    if "area" in lowered:
        tokens.append("Area")
    if "leveled" in lowered:
        tokens.append("Leveled")

    for fragment in re.findall(r"Resisted \((.*?)\)", normalized_raw, flags=re.IGNORECASE):
        tokens.extend(canonical_resistance(fragment))

    if not tokens:
        tokens = ["Utility"]
    return order_unique(tokens, KEYWORD_ORDER)


def infer_types_from_raw_label(raw_label: str) -> list[str]:
    lowered = raw_label.lower()
    inferred: list[str] = []
    for phrase, types in RAW_LABEL_HINTS:
        if phrase in lowered:
            inferred.extend(types)
    return order_unique(inferred, TYPE_ORDER)


def infer_text_type_scores(spell: dict[str, Any]) -> Counter[str]:
    name_text = normalize_ws(spell["spell_name"]).lower()
    description_text = normalize_ws(spell.get("description", "")).lower()
    statistics_text = normalize_ws(spell.get("statistics", "")).lower()
    full_text = " ".join(part for part in [name_text, description_text, statistics_text] if part)
    scores: Counter[str] = Counter()

    for spell_type, phrases in TEXT_TYPE_HINTS.items():
        for phrase in phrases:
            if scored_text_contains(name_text, phrase):
                scores[spell_type] += 3
            elif scored_text_contains(full_text, phrase):
                scores[spell_type] += 1
    return scores


def fallback_types_from_keywords(parsed_keywords: list[str]) -> list[str]:
    if "Information" in parsed_keywords:
        return ["Knowledge"]
    if "Healing" in parsed_keywords:
        return ["Healing"]
    if any(keyword in parsed_keywords for keyword in ["Missile", "Jet"]):
        return ["Artillery"]
    if any(keyword in parsed_keywords for keyword in ["Resisted-Will", "Resisted-IQ", "Resisted-Variable"]):
        return ["Mind Control"]
    if "Buff" in parsed_keywords:
        return ["Protection"]
    if "Area" in parsed_keywords:
        return ["Artillery"]
    return ["Meta"]


def infer_spell_types(raw_spell: dict[str, Any], parsed_keywords: list[str]) -> list[str]:
    primary = infer_types_from_raw_label(raw_spell["spell_types"][0])
    scores = infer_text_type_scores(raw_spell)

    inferred = list(primary)
    for keyword, mapped_types in {
        "Information": ["Knowledge"],
        "Healing": ["Healing"],
        "Summoning": ["Summoning", "Gate"],
        "Travel": ["Movement"],
        "Defense": ["Protection"],
    }.items():
        if keyword in parsed_keywords:
            inferred.extend(mapped_types)

    extras = [spell_type for spell_type, score in scores.most_common() if score >= 3 and spell_type not in inferred]
    inferred.extend(extras[:2])

    if not inferred:
        inferred.extend(fallback_types_from_keywords(parsed_keywords))

    return order_unique(inferred, TYPE_ORDER)


def spell_text_blob(raw_spell: dict[str, Any]) -> str:
    return " ".join(
        normalize_ws(str(part)).lower()
        for part in [
            raw_spell.get("spell_name", ""),
            " ".join(raw_spell.get("spell_types", [])),
            raw_spell.get("keywords", ""),
            raw_spell.get("range", ""),
            raw_spell.get("duration", ""),
            raw_spell.get("casting_roll", ""),
            raw_spell.get("description", ""),
            raw_spell.get("statistics", ""),
        ]
        if part
    )


def scored_text_contains(text: str, term: str) -> bool:
    normalized_term = normalize_ws(term).lower()
    if not normalized_term:
        return False
    if len(normalized_term) <= 4 or " " in normalized_term:
        return re.search(rf"(?<!\w){re.escape(normalized_term)}(?!\w)", text) is not None
    return normalized_term in text


def name_term_matches(name_text: str, term: str) -> bool:
    return scored_text_contains(name_text, term)


def score_child_type(text: str, parsed_keywords: list[str], *, name_text: str, raw_terms: tuple[str, ...] = (), name_terms: tuple[str, ...] = (), text_terms: tuple[str, ...] = (), keyword_terms: tuple[str, ...] = (), require_keywords: tuple[str, ...] = (), require_absent_keywords: tuple[str, ...] = ()) -> int:
    if require_keywords and not all(keyword in parsed_keywords for keyword in require_keywords):
        return 0
    if require_absent_keywords and any(keyword in parsed_keywords for keyword in require_absent_keywords):
        return 0

    score = 0
    for term in raw_terms:
        if scored_text_contains(text, term):
            score += 6
    for term in name_terms:
        if name_term_matches(name_text, term):
            score += 4
    for term in text_terms:
        if scored_text_contains(text, term):
            score += 2
    for keyword in keyword_terms:
        if keyword in parsed_keywords:
            score += 3
    return score


def score_split_child_types(parent_type: str, raw_spell: dict[str, Any], parsed_keywords: list[str]) -> dict[str, int]:
    spell_name = raw_spell["spell_name"]
    if spell_name in FINAL_SPELL_TYPE_OVERRIDES:
        override_types = FINAL_SPELL_TYPE_OVERRIDES[spell_name]
        matching = [spell_type for spell_type in override_types if spell_type in APPROVED_SPLIT_CHILD_TYPES.get(parent_type, [])]
        if matching:
            return {child_type: (10_000 if child_type == matching[0] else -10_000) for child_type in APPROVED_SPLIT_CHILD_TYPES[parent_type]}

    text = spell_text_blob(raw_spell)
    name_text = normalize_ws(raw_spell["spell_name"]).lower()

    def score(**kwargs: Any) -> int:
        return score_child_type(text, parsed_keywords, name_text=name_text, **kwargs)

    if parent_type == "Meta":
        return {
            "Countermagic & Suppression": score(raw_terms=("antimagic",), name_terms=("dispel", "countermagic", "suppression", "protection from magic", "ward against magic", "suspend magic", "suspend spell", "globe of invulnerability"), text_terms=("negates magic", "interferes with magic", "suppresses", "counterspell")),
            "Mana, Ley, and Power": score(raw_terms=("power spells", "raw magic", "incarnum"), name_terms=("ley ", "mana", "powerstone", "essentia", "mishtai", "tap", "supply", "running"), text_terms=("ley line", "energy reserve", "mana")),
            "Arcane Siphons & Frailties": score(name_terms=("vulnerability", "steal ", "thirst", "frailty", "debility", "agonize", "pain", "choke", "nauseate", "retch"), text_terms=("temporary st loss", "temporary dx loss", "temporary per loss", "temporary ht loss", "more vulnerable")),
            "Grand Arcana & Constructs": score(name_terms=("create ", "conjure ", "construct", "chimera", "create life", "mirror duplicate", "spell phylactery", "portrait", "skyhook", "helping hands", "bilocation", "lesser wish", "paradox"), text_terms=("creates an invisible force", "conjure", "create a living being")),
            "Sorcerous Services & Rites": score(raw_terms=("least spells",), name_terms=("alarm", "prepare game", "telecast", "rail communication", "green telurgy", "grind meat", "hammerhands", "knifehand", "cornucopia", "peacebond"), text_terms=("slow, repetitive actions", "two-way conversation")),
            "Arcane Utilities & Implements": score(name_terms=("detect magic", "reveal magic", "mind-sending", "projection", "far-feeling", "far-tasting", "file transfer", "ripple sense", "gift of letters", "gift of tongues"), keyword_terms=("Information", "Utility")),
            "Lesser Hexes & Afflictions": score(name_terms=("curse", "doom", "itch", "numbness", "blistering", "brittle", "cold", "corrode", "fungal", "glitch", "hinder", "leak", "malfunction", "roundabout"), text_terms=("wracked with pain", "fails to resist")),
        }

    if parent_type == "Knowledge":
        return {
            "Senses & Perception": score(raw_terms=("infravision",), name_terms=("vision", "hearing", "taste", "smell", "touch", "blindsight", "tremorsense", "hypervision", "sense emotion"), text_terms=("see through", "bonus to hearing", "bonus to touch", "bonus to taste and smell")),
            "Thoughts & Memory": score(raw_terms=("memory spells",), name_terms=("memory", "mind-", "thought", "impression", "recall", "memorize"), text_terms=("surface thoughts", "restore subject’s memory")),
            "Divination & Omens": score(raw_terms=("divination spells", "spells of the past"), name_terms=("mancy", "augury", "astrology", "foretell", "scrying", "predict ", "crystal-gazing", "daybook reading", "extispicy", "geomancy", "hydromancy")),
            "Seekers & Trackers": score(name_terms=("seek ", "trace ", "find direction", "seeker", "tracker", "remember path"), text_terms=("exact direction and distance", "homes in")),
            "Detection & Appraisal": score(name_terms=("detect ", "identify ", "reveal ", "know illusion", "test ", "divine purpose"), text_terms=("determine its functions", "identify all currently active")),
            "Readings & Analysis": score(name_terms=("analyze ", "monitor ", "reading", "body-reading", "appraisal"), keyword_terms=("Information",)),
        }

    if parent_type == "Protection":
        return {
            "Wards, Shields, and Barriers": score(name_terms=("ward", "shield", "barrier", "block", "wall", "globe", "sphere", "dome", "sanctuary"), text_terms=("active defense", "shapeable wall")),
            "Resistances & Immunities": score(name_terms=("resist ", "immune", "immunity", "endure", "protection from", "ward against", "fireproof", "insulated", "hearing protection"), text_terms=("virtually immune", "protected from")),
            "Armor & Battle Shells": score(raw_terms=("armor buff",), name_terms=(" armor", "skin", "hide", "shell", "fur", "feathers"), text_terms=("gains dr", "ablative")),
            "Weapon Boons & Retaliations": score(raw_terms=("weapon buff",), name_terms=("weapon", "fang", "retribution", "icy rune"), text_terms=("the next time the subject is struck",)),
            "Concealments & Counter-Senses": score(name_terms=("invisibility", "invisible", "conceal", "blur", "blocker", "remove reflection", "remove shadow", "fate of oedipus", "sonar invisibility"), text_terms=("protected from scrying", "difficult to spot", "nearly impossible to detect")),
            "Battle Blessings & Readiness": score(name_terms=("accuracy", "alertness", "balance", "bless", "bravery", "cadence", "grace", "light step", "melee manager", "presence", "strengthen will", "tongues"), text_terms=("bonus to skill rolls to hit", "becomes braver"), keyword_terms=("Buff",)),
            "Safeguards & Reliefs": score(name_terms=("cleanliness", "analgesic", "antiemetic", "birth control", "preservation", "gentle repose", "diver’s blessing", "eat crow", "guardian spirit"), text_terms=("prevents the subject from rotting", "sanitized waste")),
        }

    if parent_type == "Mind Control":
        return {
            "Dreams, Sleep, and Delusion": score(raw_terms=("dream spells",), name_terms=("dream", "sleep", "nightmare", "hallucination", "delusion", "morphean")),
            "Possession & Identity": score(raw_terms=("possession spells",), name_terms=("possession", "avatar", "identity", "machine possession", "beast possession", "projection"), text_terms=("moves his consciousness", "permanent machine possession")),
            "Emotion & Morale": score(name_terms=("emotion", "terror", "awe", "bravery", "euphoria", "vexation", "hell", "fear", "volatility"), text_terms=("fright check", "undeniable urge")),
            "Commands & Compulsion": score(name_terms=("command", "dominate", "master", "geas", "hypnotize", "avoid", "dance", "control "), text_terms=("mentally dominate", "strong compulsion", "feels an undeniable urge")),
            "Pain, Stun, and Collapse": score(name_terms=("stun", "knockout", "daze", "tickle", "pain", "collapse", "touch of idiocy"), text_terms=("physically stunned", "helpless with laughter", "knocked unconscious")),
            "Memory, Thought, and Will": score(raw_terms=("memory spells", "psychic spells as normal spells"), name_terms=("memory", "mind-reading", "mind-search", "forbidden wisdom", "restore memory", "steal skill", "steal wisdom", "false memory", "recall"), text_terms=("surface thoughts", "temporary iq loss", "knowledge")),
            "Mental Curses & Counterwill": score(name_terms=("curse", "censure", "suspend ", "destabilize", "foolishness", "dread curse", "sever fate line", "shared doom"), text_terms=("fails to resist",)),
        }

    if parent_type == "Transformation":
        return {
            "Shapeshifting & Polymorph": score(raw_terms=("transformation spells",), name_terms=("shapeshift", "polymorph", "morph", "great shapeshift", "permanent shapeshifting", "shapeshifting")),
            "Body Forms & Embodiments": score(raw_terms=("more body of (element) spells", "elemental body spells"), name_terms=("body of", "embodiment", "partial shapeshifting", "paws", "tail", "trunk", "jaws", "arms"), text_terms=("meta-trait", "gains the")),
            "Creation, Shape, and Matter": score(raw_terms=("creation spells", "elemental weapon transformation spells"), name_terms=("create ", "shape ", "matter", "material", "chimera"), text_terms=("transforms matter", "solid but unnatural matter")),
            "Alteration, Growth, and Other Transmutations": score(name_terms=("alter ", "grow", "shrink", "change", "everchanging", "great haste"), text_terms=("temporarily change", "becomes")),
        }

    if parent_type == "Movement":
        return {
            "Ways, Passage, and Travel": score(raw_terms=("movement spells", "flight spells", "gate spells", "personal gate and gravity spells"), name_terms=("flight", "teleport", "jump", "travel", "timeport", "plane shift", "walk", "journey", "rider", "transfer water", "sanctuary"), keyword_terms=("Travel",)),
            "Forced Movement & Restraint": score(name_terms=("push", "pull", "cage", "sphere", "root", "vortex", "levitation", "move terrain", "gravity crush", "gravity push"), text_terms=("move distant creatures", "encloses a creature", "move 0"), keyword_terms=("Control",)),
            "Speed, Haste, and Handling": score(name_terms=("haste", "speed", "step", "fall", "ice movement", "sandstrider", "tolerance", "reading"), text_terms=("basic speed", "basic move", "glide"), keyword_terms=("Buff",)),
        }

    if parent_type == "Making & Breaking":
        return {
            "Locks, Seals, and Traps": score(name_terms=("lock", "seal", "trap", "rune", "block", "binding"), text_terms=("cannot be opened", "triggering conditions")),
            "Weapons & Battlework": score(raw_terms=("gunman spells",), name_terms=("weapon", "blade", "arrow", "bullet", "gun", "armor", "shield", "battle"), text_terms=("manufactured weapon", "skill rolls to hit")),
            "Breaking, Shattering, and Ruin": score(name_terms=("break", "shatter", "ruin", "destroy", "corrode", "disintegr", "annihilation"), text_terms=("devour anything", "temporarily corrodes")),
            "Crafting, Repair, and Reshaping": score(name_terms=("create ", "make ", "repair", "reshape", "shape", "craft", "paper", "glass", "metal"), text_terms=("turn paper", "repair", "conjure")),
        }

    if parent_type == "Earth":
        return {
            "Metal & Glass": score(raw_terms=("metal spells", "glass spells"), name_terms=("metal", "iron", "steel", "silver", "gold", "glass", "crystal", "gem")),
            "Earthshape, Passage, and Transmutation": score(raw_terms=("essential earth spells",), name_terms=("shape", "pass", "tunnel", "walk", "badger paws", "earth to", "move terrain"), text_terms=("dig", "transmute", "earth")),
            "Stone, Soil, and Sand": score(name_terms=("stone", "earth", "sand", "mud", "rock", "lava"), text_terms=("solid earth", "stone surface")),
        }

    if parent_type == "Artillery":
        return {
            "Missiles, Jets, and Rays": score(name_terms=("ray", "bolt", "shot", "missile", "jet", "orb", "sphere", "spray", "lance", "touch"), keyword_terms=("Missile", "Jet")),
            "Battlefield Zones & Fields": score(name_terms=("field", "zone", "wall", "cloud", "rain", "storm", "cage", "circle", "dome", "aura"), text_terms=("area of effect", "mobile circular storm", "lasting duration"), require_keywords=("Area",)),
            "Bursts, Barrages, and Bombardment": score(name_terms=("burst", "barrage", "bombardment", "blast", "swarm", "explosion", "shards"), keyword_terms=("Area", "Damage")),
        }

    if parent_type == "Body Control":
        return {
            "Vital Functions & Augmentation": score(raw_terms=("boost attribute spells",), name_terms=("pregnancy", "breath", "lungs", "respiration", "vigor", "strength", "intelligence", "health", "resist pain"), text_terms=("raise", "bonus", "breathe", "safe development"), keyword_terms=("Buff",)),
            "Body Forms, Limbs, and Alteration": score(raw_terms=("limb spells",), name_terms=("limb", "paws", "tail", "claws", "body of", "branch fingers", "slimy skin", "skin"), text_terms=("meta-trait", "grows", "transforms")),
            "Internal Ruin, Fatigue, and Decline": score(name_terms=("age", "ageing", "fatigue", "decrepify", "embolism", "steal breath", "burden", "progeria", "cold vulnerability"), text_terms=("internal organs", "suffers", "temporary fp", "older at once")),
        }

    if parent_type == "Air":
        return {
            "Lightning of the Air": score(raw_terms=("lightning spells",), name_terms=("lightning", "spark", "shimmering", "storm", "ride the lightning")),
            "Breath & Atmosphere": score(name_terms=("air", "breath", "odor", "stench", "smoke", "fog", "gas", "vapor"), text_terms=("safe to breathe", "create breathable air", "purify air", "change air", "scent")),
            "Winds, Vapors, and Sky Passage": score(name_terms=("flight", "wind", "vortex", "cloud", "aerial", "wall of wind"), text_terms=("fly", "hover", "hurls creatures"), keyword_terms=("Travel",)),
        }

    if parent_type == "Light & Darkness":
        return {
            "Shadows & Obscurity": score(name_terms=("shadow", "dark", "obscur", "invisible", "black", "night")),
            "Glamour, Color, and Prism": score(raw_terms=("yellow spells", "new prismatic spells"), name_terms=("color", "prism", "rainbow", "glamour", "yellow", "illusion")),
            "Lightning & Radiant Assaults": score(raw_terms=("lightning spells",), name_terms=("lightning", "radiant", "sunbolt", "laser", "flash"), keyword_terms=("Damage",)),
            "Radiance, Sight, and Reflection": score(name_terms=("light", "vision", "sight", "reflection", "mirror", "true seeing", "radiance"), text_terms=("see through", "shed light")),
        }

    if parent_type == "Plant":
        return {
            "Plant Lore, Speech, and Passage": score(name_terms=("speak", "lore", "identify", "detect", "seek", "passage", "green telurgy"), text_terms=("two-way conversation", "sapient plant")),
            "Wood, Vines, and Plant Forms": score(raw_terms=("fungus spells",), name_terms=("wood", "vine", "thorn", "root", "branch", "tree", "forest", "entangling", "leaves"), text_terms=("animates plants", "grappled", "living vines")),
            "Growth, Blessing, and Husbandry": score(name_terms=("grow", "bless", "husbandry", "harvest", "animal spirit", "nature’s favor", "train animal"), text_terms=("plant growth", "animal"), keyword_terms=("Buff",)),
        }

    if parent_type == "Fire":
        return {
            "Heat, Fuel, and Hearthwork": score(raw_terms=("fuel spells", "steam spells"), name_terms=("heat", "warm", "fuel", "hearth", "cook", "cold", "slow fire", "fast fire"), text_terms=("ambient temperature", "burn hotter")),
            "Flame Assaults & Battlefire": score(name_terms=("fire", "flame", "burn", "inferno", "hellfire", "plasma", "blast", "corona"), keyword_terms=("Damage",)),
        }

    if parent_type == "Necromantic":
        return {
            "Undead Animation & Command": score(raw_terms=("zombie spells",), name_terms=("undead", "zombie", "skeleton", "lich", "animate", "command")),
            "Spirits of the Dead": score(raw_terms=("spirit spells",), name_terms=("spirit", "ghost", "soul", "dead"), text_terms=("speak with dead", "spirit")),
            "Death Curses & Withering": score(raw_terms=("death spells",), name_terms=("death", "curse", "wither", "reaper", "age", "doom", "grave", "ghoul", "hellspawn"), keyword_terms=("Damage", "Debuff")),
        }

    if parent_type == "Water":
        return {
            "Ice, Snow, and Frost": score(raw_terms=("ice spells",), name_terms=("ice", "snow", "frost", "cold", "blizzard")),
            "Drowning, Dehydration, and Fluid Assaults": score(name_terms=("drown", "dehydr", "thirst", "steam", "scald", "fluid assault", "water jet"), keyword_terms=("Damage",)),
            "Water Shaping & Passage": score(raw_terms=("fluid spells",), name_terms=("water", "wave", "shape", "breathe", "passage", "transfer water", "ice movement"), text_terms=("breathe common air", "aquatic")),
        }

    if parent_type == "Animal":
        return {
            "Animal Companions, Mounts, and Summons": score(name_terms=("summon", "companion", "mount", "rider", "servant"), keyword_terms=("Summoning",)),
            "Beast Forms & Traits": score(name_terms=("claws", "fur", "tail", "feathers", "paws", "trunk", "jaws", "spider", "serpent", "hawk", "beast form"), text_terms=("meta-trait", "animal")),
            "Animal Command & Repelling": score(name_terms=("command", "repel", "control", "master", "dominate", "tame", "train animal"), text_terms=("animal behaves", "mentally dominate an animal")),
        }

    if parent_type == "Weather":
        return {
            "Tempests, Lightning, and Winter Weather": score(raw_terms=("lightning spells", "ice spells"), name_terms=("tempest", "lightning", "thunder", "snow", "winter", "storm", "blizzard"), keyword_terms=("Damage",)),
            "Rain, Wind, and Greater Weather": score(name_terms=("rain", "wind", "weather", "eclipse", "cloud"), text_terms=("forecasts", "weather")),
        }

    if parent_type == "Spirit":
        return {
            "Souls, Possession, and Bindings": score(raw_terms=("possession spells",), name_terms=("soul", "possess", "binding", "bind", "incarnum"), text_terms=("moves his consciousness", "true name")),
            "Spirits, Wards, and the Dead": score(name_terms=("spirit", "ghost", "dead", "ward"), text_terms=("restless dead", "spirit traffic")),
        }

    return {child_type: 0 for child_type in APPROVED_SPLIT_CHILD_TYPES.get(parent_type, [])}


def choose_split_child_type(parent_type: str, raw_spell: dict[str, Any], parsed_keywords: list[str]) -> str:
    scores = score_split_child_types(parent_type, raw_spell, parsed_keywords)
    return max(APPROVED_SPLIT_CHILD_TYPES[parent_type], key=lambda child_type: (scores.get(child_type, 0), -APPROVED_SPLIT_CHILD_TYPES[parent_type].index(child_type)))


def load_split_target_counts() -> dict[str, dict[str, int]]:
    distribution = json.loads((ROOT / "type-split-distribution.json").read_text())
    return {
        item["parent_type"]: {child["type"]: child["count"] for child in item["child_types"]}
        for item in distribution["split_proposals"]
    }


def scale_split_target_counts(targets: dict[str, int], actual_total: int, child_types: list[str]) -> dict[str, int]:
    if actual_total <= 0:
        return {child_type: 0 for child_type in child_types}

    source_total = sum(targets.values())
    if source_total <= 0:
        raise ValueError("Split target counts must sum to a positive total.")

    if source_total == actual_total:
        return {child_type: targets.get(child_type, 0) for child_type in child_types}

    positions = {child_type: index for index, child_type in enumerate(child_types)}
    exact = {
        child_type: (targets.get(child_type, 0) * actual_total) / source_total
        for child_type in child_types
    }
    scaled = {child_type: int(exact[child_type]) for child_type in child_types}
    remainder = actual_total - sum(scaled.values())
    ranked = sorted(
        child_types,
        key=lambda child_type: (exact[child_type] - scaled[child_type], targets.get(child_type, 0), -positions[child_type]),
        reverse=True,
    )
    for child_type in ranked[:remainder]:
        scaled[child_type] += 1
    return scaled


def fit_split_targets_to_locked_counts(targets: dict[str, int], locked_counts: Counter[str], child_types: list[str]) -> dict[str, int]:
    adjusted = {child_type: targets.get(child_type, 0) for child_type in child_types}
    positions = {child_type: index for index, child_type in enumerate(child_types)}

    for child_type in child_types:
        locked_count = locked_counts[child_type]
        if adjusted[child_type] >= locked_count:
            continue

        deficit = locked_count - adjusted[child_type]
        adjusted[child_type] = locked_count
        for _ in range(deficit):
            donors = [
                candidate
                for candidate in child_types
                if candidate != child_type and adjusted[candidate] > locked_counts[candidate]
            ]
            if not donors:
                raise ValueError(f"Unable to fit split targets for locked child type '{child_type}'.")
            donor = max(
                donors,
                key=lambda candidate: (adjusted[candidate] - locked_counts[candidate], adjusted[candidate], -positions[candidate]),
            )
            adjusted[donor] -= 1

    return adjusted


def contract_gate_parent_types(raw_spell: dict[str, Any], parent_spell_types: list[str]) -> list[str]:
    if "Gate" not in parent_spell_types or len(parent_spell_types) == 1:
        return parent_spell_types

    source_label = raw_spell["spell_types"][0]
    if source_label == "Gate Spells":
        return parent_spell_types

    explicit_gate_keepers = {
        "Aerial Entombment",
        "Astral Projection",
        "Banish",
        "Dimensional Lock",
        "Gate Seal",
        "Phase Trap",
        "Planar Portal",
        "Plane Shift",
        "Plane Shift Other",
        "Portal",
        "Portal Architecture",
        "Sanctuary",
        "Town Portal",
        "Underworld Imprisonment",
    }
    if raw_spell["spell_name"] in explicit_gate_keepers:
        return parent_spell_types

    removable_overlap_types = {"Air", "Gravity", "Knowledge", "Movement", "Necromantic", "Space", "Spirit", "Summoning", "Time", "Weather"}
    if any(spell_type in removable_overlap_types for spell_type in parent_spell_types if spell_type != "Gate"):
        return [spell_type for spell_type in parent_spell_types if spell_type != "Gate"]

    return parent_spell_types


def normalize_source_spell_name(name: str) -> str:
    cleaned = normalize_ws(name)
    for prefix in EDITORIAL_NAME_PREFIXES:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    cleaned = re.sub(r"\s*\(Unofficial Sorcery Errata\)$", "", cleaned).strip()
    return normalize_ws(cleaned)


def review_display_name(raw_spell: dict[str, Any], override: dict[str, Any]) -> str:
    source_name = raw_spell["spell_name"]
    if "display_name" in override:
        return override["display_name"]

    if source_name in EXACT_DISPLAY_NAME_OVERRIDES:
        return EXACT_DISPLAY_NAME_OVERRIDES[source_name]

    normalized = normalize_source_spell_name(source_name)
    if normalized in EXACT_DISPLAY_NAME_OVERRIDES:
        return EXACT_DISPLAY_NAME_OVERRIDES[normalized]

    if normalized.startswith("Power Word: "):
        tail = normalized.removeprefix("Power Word: ").strip()
        return POWER_WORD_DISPLAY_NAMES.get(tail, f"Word of {tail}")

    if normalized.startswith("Curse-Missile: "):
        tail = normalized.removeprefix("Curse-Missile: ").strip()
        return f"Missile of {CURSE_MISSILE_DISPLAY_TAILS.get(tail, tail)}"

    if normalized == "Stop Bleeding":
        return "Staunch Bleeding"
    if normalized.startswith("Stop "):
        return f"Halt {normalized.removeprefix('Stop ').strip()}"

    return normalized


def build_parent_type_info(raw_spell: dict[str, Any]) -> tuple[list[str], list[str], dict[str, Any], str]:
    source_name = raw_spell["spell_name"]
    override = MANUAL_OVERRIDES.get(source_name, {})
    parsed_source_keywords = parse_raw_keywords(raw_spell["keywords"])
    parent_spell_types = order_unique(override.get("spell_types", infer_spell_types(raw_spell, parsed_source_keywords)), TYPE_ORDER)
    parent_spell_types = contract_gate_parent_types(raw_spell, parent_spell_types)
    return parent_spell_types, parsed_source_keywords, override, review_display_name(raw_spell, override)


def compute_split_assignments(source_spells: list[dict[str, Any]], *, enforce_target_distribution: bool = False) -> dict[tuple[str, str], str]:
    target_counts = load_split_target_counts()
    parent_entries: dict[str, list[dict[str, Any]]] = defaultdict(list)
    assignments: dict[tuple[str, str], str] = {}

    for raw_spell in source_spells:
        parent_spell_types, parsed_source_keywords, override, display_name = build_parent_type_info(raw_spell)
        override_key = display_name if display_name in FINAL_SPELL_TYPE_OVERRIDES else raw_spell["spell_name"]
        for parent_type in parent_spell_types:
            if parent_type not in APPROVED_SPLIT_CHILD_TYPES:
                continue
            locked_child = None
            if override_key in FINAL_SPELL_TYPE_OVERRIDES:
                locked = [spell_type for spell_type in FINAL_SPELL_TYPE_OVERRIDES[override_key] if spell_type in APPROVED_SPLIT_CHILD_TYPES[parent_type]]
                locked_child = locked[0] if locked else None
            parent_entries[parent_type].append(
                {
                    "spell_id": raw_spell["spell_id"],
                    "spell_name": raw_spell["spell_name"],
                    "display_name": display_name,
                    "parsed_keywords": parsed_source_keywords,
                    "scores": score_split_child_types(parent_type, raw_spell, parsed_source_keywords),
                    "locked_child": locked_child,
                }
            )

    for parent_type, entries in parent_entries.items():
        child_types = APPROVED_SPLIT_CHILD_TYPES[parent_type]
        if not enforce_target_distribution:
            for entry in entries:
                locked_child = entry["locked_child"]
                if locked_child:
                    assignments[(entry["spell_id"], parent_type)] = locked_child
                    continue
                ranked = sorted(child_types, key=lambda child_type: (entry["scores"].get(child_type, 0), -child_types.index(child_type)), reverse=True)
                assignments[(entry["spell_id"], parent_type)] = ranked[0]
            continue

        mutable_entries: list[dict[str, Any]] = []
        counts = Counter()

        for entry in entries:
            spell_id = entry["spell_id"]
            locked_child = entry["locked_child"]
            if locked_child:
                assignments[(spell_id, parent_type)] = locked_child
                counts[locked_child] += 1
            else:
                mutable_entries.append(entry)

        targets = scale_split_target_counts(target_counts[parent_type], len(entries), child_types)
        targets = fit_split_targets_to_locked_counts(targets, counts, child_types)
        current_assignment: dict[str, str] = {}
        for entry in mutable_entries:
            ranked = sorted(child_types, key=lambda child_type: (entry["scores"].get(child_type, 0), -child_types.index(child_type)), reverse=True)
            current_assignment[entry["spell_id"]] = ranked[0]
            counts[ranked[0]] += 1

        desired_totals = Counter(targets)
        while any(counts[child_type] != desired_totals[child_type] for child_type in child_types):
            overfull = [child_type for child_type in child_types if counts[child_type] > desired_totals[child_type]]
            underfull = [child_type for child_type in child_types if counts[child_type] < desired_totals[child_type]]
            if not overfull or not underfull:
                break

            best_move: tuple[float, str, str, str] | None = None
            for entry in mutable_entries:
                spell_id = entry["spell_id"]
                from_child = current_assignment[spell_id]
                if from_child not in overfull:
                    continue
                from_score = entry["scores"].get(from_child, 0)
                for to_child in underfull:
                    penalty = from_score - entry["scores"].get(to_child, 0)
                    candidate = (penalty, spell_id, from_child, to_child)
                    if best_move is None or candidate < best_move:
                        best_move = candidate

            if best_move is None:
                break

            _, spell_id, from_child, to_child = best_move
            current_assignment[spell_id] = to_child
            counts[from_child] -= 1
            counts[to_child] += 1

        for entry in mutable_entries:
            assignments[(entry["spell_id"], parent_type)] = current_assignment[entry["spell_id"]]

    return assignments


def finalize_spell_types(raw_spell: dict[str, Any], parent_types: list[str], parsed_keywords: list[str], display_name: str, split_assignments: dict[tuple[str, str], str]) -> list[str]:
    override_key = display_name if display_name in FINAL_SPELL_TYPE_OVERRIDES else raw_spell["spell_name"]
    if override_key in FINAL_SPELL_TYPE_OVERRIDES:
        return order_unique(FINAL_SPELL_TYPE_OVERRIDES[override_key], FINAL_TYPE_ORDER)

    finalized: list[str] = []
    for spell_type in parent_types:
        if spell_type in APPROVED_SPLIT_CHILD_TYPES:
            finalized.append(split_assignments.get((raw_spell["spell_id"], spell_type), choose_split_child_type(spell_type, raw_spell, parsed_keywords)))
        elif spell_type in STABLE_FINAL_TYPES:
            finalized.append(spell_type)
    return order_unique(finalized, FINAL_TYPE_ORDER)


def infer_role_keywords(raw_spell: dict[str, Any], spell_types: list[str], keywords: list[str]) -> list[str]:
    description_text = normalize_ws(raw_spell.get("description", "")).lower()
    statistics_text = normalize_ws(raw_spell.get("statistics", "")).lower()
    range_text = normalize_ws(raw_spell.get("range", "")).lower()
    duration_text = normalize_ws(raw_spell.get("duration", "")).lower()
    casting_text = normalize_ws(raw_spell.get("casting_roll", "")).lower()
    text = " ".join(part for part in [description_text, statistics_text] if part)

    enriched = list(keywords)

    if "malediction" in statistics_text or (range_text.startswith("unlimited") and casting_text.startswith("will") and any(keyword.startswith("Resisted-") for keyword in enriched)):
        enriched.append("Malediction")
    if "aura" in statistics_text:
        enriched.append("Aura")
    if "cyclic" in statistics_text or "each day after" in description_text:
        enriched.append("Cyclic")
    if "persistent" in statistics_text or any(term in duration_text for term in ["permanent", "indefinite", "truly permanent"]):
        enriched.append("Persistent")
    if "no signature" in statistics_text:
        enriched.append("No-Signature")
    if range_text.startswith("touch"):
        enriched.append("Touch")
    if any(term in range_text for term in ["reach", "staff’s reach"]) or "use staff to hit" in casting_text or "unarmed combat skills" in casting_text or "melee attack" in statistics_text:
        enriched.append("Melee")
    if "summon" in text or "ally" in statistics_text or "Summoning" in spell_types:
        enriched.append("Summoning")
    if any(term in text for term in ["damage", "attack", "burning", "corrosion", "crushing", "toxic", "fatigue damage", "aging attack"]) or any(keyword in enriched for keyword in ["Missile", "Jet"]):
        enriched.append("Damage")
    if any(term in text for term in ["heal", "cure", "restore", "recovery", "rapid healing"]) or "Healing" in spell_types:
        enriched.append("Healing")
    if any(term in text for term in ["protect", "dr ", "shield", "ward", "immune", "resist"]) or "Protection" in spell_types:
        enriched.append("Defense")
    if any(term in text for term in ["seek", "detect", "know", "vision", "probe", "monitor", "analysis"]) or "Knowledge" in spell_types:
        enriched.append("Information")
    if any(term in text for term in ["control", "grapple", "bind", "stun", "paralysis", "vortex", "sleep", "dominate", "knockback"]) or any(spell_type in spell_types for spell_type in ["Mind Control", "Artillery", "Force"]):
        enriched.append("Control")
    if any(spell_type in spell_types for spell_type in ["Movement", "Gate", "Space", "Time"]) or any(term in text for term in ["flight", "jump", "teleport", "portal", "travel", "plane shift"]):
        enriched.append("Travel")
    if any(keyword.startswith("Resisted-") for keyword in enriched) and "Buff" not in enriched and "Healing" not in enriched and "Information" not in enriched:
        enriched.append("Debuff")

    role_keywords = {"Buff", "Damage", "Control", "Defense", "Healing", "Information", "Summoning", "Travel", "Debuff"}
    if not any(keyword in role_keywords for keyword in enriched):
        enriched.append("Utility")

    return order_unique(enriched, KEYWORD_ORDER)


def infer_dedupe(raw_spell: dict[str, Any]) -> dict[str, Any]:
    name = raw_spell["spell_name"]
    lowered = name.lower()
    if "(" in name and ")" in name:
        group = re.sub(r"\s*\([^)]*\)", "", lowered).strip().replace(" ", "-")
        return {"status": "variant", "group": group or None, "reason": "Name carries an explicit variant marker and should be reviewed against similarly named records."}

    for marker in VARIANT_MARKERS:
        if lowered.startswith(marker):
            group = lowered[len(marker):].strip().replace(" ", "-")
            return {"status": "variant", "group": group or None, "reason": f"Name begins with '{marker.strip()}' and likely belongs to a variant family."}

    return {"status": "unique", "group": None, "reason": "No duplicate candidate identified by the current heuristic pass."}


def stylize_summary(summary: str) -> str:
    text = normalize_ws(summary)
    replacements = [
        ("This spell lets you ", "The caster may "),
        ("This spell lets the user ", "The caster may "),
        ("This spell lets the subject ", "The subject may "),
        ("This spell lets the caster ", "The caster may "),
        ("This spell allows you to ", "The caster may "),
        ("This spell allows the caster to ", "The caster may "),
        ("This spell allows the subject to ", "The subject may "),
        ("This spell allows ", "This working allows "),
        ("This spell causes ", "This working causes "),
        ("This spell gives the subject ", "The subject gains "),
        ("This spell gives you ", "The caster gains "),
        ("This spell gives ", "This working grants "),
        ("This spell removes ", "This working removes "),
        ("This spell creates ", "This working creates "),
        ("This spell conjures ", "This working conjures "),
        ("This spell makes the subject ", "The subject becomes "),
        ("This spell makes you ", "The caster becomes "),
        ("This spell ", "This working "),
        ("The spell allows ", "The working allows "),
        ("This working lets you ", "The caster may "),
        ("This working lets the user ", "The caster may "),
        ("This working lets the subject ", "The subject may "),
        ("This working lets the caster ", "The caster may "),
        ("This working allows you to ", "The caster may "),
        ("This working allows the caster to ", "The caster may "),
        ("This working allows the subject to ", "The subject may "),
        ("This working gives the subject ", "The subject gains "),
        ("This working grants the subject ", "The subject gains "),
        ("This working makes the subject ", "The subject becomes "),
        ("This working makes you ", "The caster becomes "),
    ]
    for source, target in replacements:
        if text.startswith(source):
            text = target + text[len(source):]
            break

    regex_replacements = [
        (r"^You subject gains\b", "The subject gains"),
        (r"^You subject of this spell becomes\b", "The subject becomes"),
        (r"^You subject becomes\b", "The subject becomes"),
        (r"^You and all of your carried equipment\b", "The caster and all carried equipment"),
        (r"^You gain\b", "The caster gains"),
        (r"^You become\b", "The caster becomes"),
        (r"^You do not breathe\b", "The caster does not breathe"),
        (r"^You touch\b", "The caster touches"),
        (r"^You throw sphere\b", "The caster throws a sphere"),
        (r"^You throw\b", "The caster throws"),
        (r"^You shoot\b", "The caster looses"),
        (r"^You utter\b", "The caster utters"),
        (r"^You can\b", "The caster may"),
        (r"^You may\b", "The caster may"),
        (r"^Your touch\b", "A touch"),
        (r"^Lets a caster\b", "The spell lets a caster"),
        (r"^Subject can\b", "The subject may"),
    ]
    for pattern, replacement in regex_replacements:
        text = re.sub(pattern, replacement, text)

    text = text.replace("doesn't", "does not").replace("can't", "cannot")
    text = text.replace("does not actually provides", "does not actually provide")
    text = text.replace("may fist make", "may first make")
    text = text.replace("  ", " ")
    return normalize_ws(text)


def choose_coda(spell_name: str, keywords: list[str]) -> str:
    if "Information" in keywords:
        role = "information"
    elif "Healing" in keywords:
        role = "healing"
    elif "Summoning" in keywords:
        role = "summoning"
    elif "Travel" in keywords:
        role = "travel"
    elif "Defense" in keywords:
        role = "defense"
    elif "Control" in keywords and "Damage" not in keywords:
        role = "control"
    elif "Damage" in keywords:
        role = "damage"
    else:
        role = "utility"
    options = ROLE_CODAS[role]
    return options[stable_index(spell_name, len(options))]


def fallback_description(raw_spell: dict[str, Any], spell_types: list[str], keywords: list[str]) -> str:
    duration = concise_field(raw_spell.get("duration", "Special"))
    range_text = concise_field(raw_spell.get("range", "Special range"))
    duration_lower = duration.lower()
    range_lower = range_text.lower()
    duration_clause = {
        "instantaneous": "At once",
        "instantly": "At once",
        "indefinite": "So long as the spell is maintained",
        "permanent": "Permanently",
    }.get(duration_lower, f"For {duration_lower}")

    if "Information" in keywords and range_lower == "self":
        if duration_clause == "At once":
            return "The caster instantly learns the spell's listed information."
        return f"{duration_clause}, the caster gains the spell's listed information."
    if "Information" in keywords and "Touch" in keywords:
        return "With a touch, the caster instantly learns the spell's listed information."
    if "Buff" in keywords and range_lower == "self":
        if duration_clause == "At once":
            return "The caster gains the spell's listed benefits at once."
        return f"{duration_clause}, the caster gains the spell's listed benefits."
    if "Buff" in keywords:
        if duration_clause == "At once":
            if range_lower == "touch":
                return "With a touch, the subject gains the spell's listed benefits at once."
            return "The subject gains the spell's listed benefits at once."
        return f"{duration_clause}, the subject gains the spell's listed benefits."
    if "Area" in keywords:
        if duration_clause == "So long as the spell is maintained":
            return f"This working lays its effect over an area at {range_lower} for so long as it is maintained."
        return f"This working lays its effect over an area at {range_lower} for {duration_lower}."
    if any(keyword.startswith("Resisted-") for keyword in keywords):
        resistance = next(keyword for keyword in keywords if keyword.startswith("Resisted-"))
        return f"Cast at {range_lower}, this working brings its listed effect upon a subject that fails {resistance.replace('-', ' ').lower()}."
    if duration_clause == "At once":
        return f"This working has its listed effect at {range_lower} at once."
    return f"This working has its listed effect at {range_lower} for {duration_lower}."


def pick_source_prose(raw_spell: dict[str, Any]) -> tuple[str, str]:
    description = normalize_ws(raw_spell.get("description", ""))
    if description:
        return description, "description"

    duration = normalize_ws(raw_spell.get("duration", ""))
    if len(duration) > 100 and any(mark in duration for mark in [".", ";"]):
        return duration, "duration"

    return "", ""


def generate_description(raw_spell: dict[str, Any], spell_types: list[str], keywords: list[str]) -> tuple[str, str]:
    original, source_field = pick_source_prose(raw_spell)
    if not original:
        return fallback_description(raw_spell, spell_types, keywords), "generated-fallback"

    summary = stylize_summary(summarize_source_prose(original, source_field))
    if not summary:
        return fallback_description(raw_spell, spell_types, keywords), "generated-fallback"
    if not summary.endswith((".", "!", "?")):
        summary += "."
    return summary, "generated-from-source"


def build_record(raw_spell: dict[str, Any], index: int, split_assignments: dict[tuple[str, str], str]) -> dict[str, Any]:
    source_name = raw_spell["spell_name"]
    parent_spell_types, parsed_source_keywords, override, display_name = build_parent_type_info(raw_spell)
    keyword_seed = order_unique(override.get("keywords", parsed_source_keywords), KEYWORD_ORDER)
    keywords = infer_role_keywords(raw_spell, parent_spell_types, keyword_seed)
    description_override = override.get("description") or EXACT_DESCRIPTION_OVERRIDES.get(source_name)

    if description_override:
        description = description_override.strip()
        description_source = "curated"
        dedupe = override.get("dedupe", {"status": "unique", "group": None, "reason": "No duplicate candidate identified during build."})
    else:
        description, description_source = generate_description(raw_spell, parent_spell_types, keywords)
        dedupe = override.get("dedupe", infer_dedupe(raw_spell))

    spell_types = finalize_spell_types(raw_spell, parent_spell_types, parsed_source_keywords, display_name, split_assignments)
    aliases = [source_name] if display_name != source_name else []
    spell_type_display_names = [APPROVED_CHILD_TYPE_DISPLAY_NAMES.get(spell_type, TYPE_DISPLAY_NAMES.get(spell_type, spell_type)) for spell_type in spell_types]

    return {
        "record_index": index,
        "spell_id": raw_spell["spell_id"],
        "spell_name": display_name,
        "spell_types": spell_types,
        "spell_type_display_names": spell_type_display_names,
        "keywords": keywords,
        "full_cost": raw_spell["full_cost"],
        "casting_roll": raw_spell["casting_roll"],
        "range": raw_spell["range"],
        "duration": raw_spell["duration"],
        "description": description,
        "description_source": description_source,
        "statistics": raw_spell["statistics"],
        "use_example": "",
        "aliases": aliases,
        "dedupe": dedupe,
        "source_lineage": {
            "source_spell_id": raw_spell["spell_id"],
            "source_spell_name": source_name,
            "source_spell_types": raw_spell["spell_types"],
            "inferred_parent_spell_types": parent_spell_types,
            "source_keywords": raw_spell["keywords"],
            "parsed_source_keywords": parsed_source_keywords,
        },
    }


def validate(records: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    for record in records:
        if not record["spell_types"]:
            errors.append(f"{record['spell_name']}: missing spell_types")
        if "Individual Spell" in record["spell_types"]:
            errors.append(f"{record['spell_name']}: contains forbidden raw type")
        unknown_types = [spell_type for spell_type in record["spell_types"] if spell_type not in FINAL_SPELL_TYPES]
        if unknown_types:
            errors.append(f"{record['spell_name']}: unknown spell types {unknown_types}")
        if len(record.get("spell_type_display_names", [])) != len(record["spell_types"]):
            errors.append(f"{record['spell_name']}: spell_type_display_names length mismatch")
        if not record["keywords"]:
            errors.append(f"{record['spell_name']}: missing keywords")
        if any(keyword.lower() == "none" for keyword in record["keywords"]):
            errors.append(f"{record['spell_name']}: contains None keyword")
        unknown_keywords = [keyword for keyword in record["keywords"] if keyword not in KEYWORD_VOCABULARY]
        if unknown_keywords:
            errors.append(f"{record['spell_name']}: unknown keywords {unknown_keywords}")
        if not record["description"].strip():
            errors.append(f"{record['spell_name']}: blank description")
        if "source_spell_name" not in record.get("source_lineage", {}):
            errors.append(f"{record['spell_name']}: source_spell_name missing from source_lineage")
        if "use_example" not in record or record["use_example"] != "":
            errors.append(f"{record['spell_name']}: use_example missing or not blank")
    return {
        "record_count": len(records),
        "errors": errors,
        "passed": not errors,
    }


def build_reports(records: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    type_counts = Counter()
    keyword_counts = Counter()
    description_sources = Counter()
    multi_type_counts = Counter()
    dedupe_groups: dict[str, list[dict[str, str]]] = defaultdict(list)

    for record in records:
        type_counts.update(record["spell_types"])
        keyword_counts.update(record["keywords"])
        description_sources.update([record.get("description_source", "unknown")])
        multi_type_counts.update([len(record["spell_types"])])
        if record["dedupe"]["group"]:
            dedupe_groups[record["dedupe"]["group"]].append(
                {
                    "spell_name": record["spell_name"],
                    "status": record["dedupe"]["status"],
                    "reason": record["dedupe"]["reason"],
                }
            )

    distribution = {
        "spell_types": [
            {
                "spell_type": spell_type,
                "count": count,
                "candidate_action": "defer-pilot-scale" if count < 8 else "stable-for-now",
                "note": "Below the long-run target floor and may want merging unless later waves change the shape." if count < 8 else "Healthy working count for the current pass.",
            }
            for spell_type, count in sorted(type_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "keywords": [
            {"keyword": keyword, "count": count}
            for keyword, count in sorted(keyword_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
    }

    split_candidates = [
        {"spell_type": spell_type, "count": count}
        for spell_type, count in sorted(type_counts.items(), key=lambda item: (-item[1], item[0]))
        if count > 60
    ]
    merge_candidates = [
        {"spell_type": spell_type, "count": count}
        for spell_type, count in sorted(type_counts.items(), key=lambda item: (item[1], item[0]))
        if count < 8
    ]

    summary = {
        "scope": f"batch-{len(records)}",
        "spell_count": len(records),
        "type_count": len(type_counts),
        "keyword_count": len(keyword_counts),
        "description_sources": dict(description_sources),
        "multi_type_distribution": dict(sorted(multi_type_counts.items())),
        "duplicate_groups": [
            {"group": group, "entries": entries}
            for group, entries in sorted(dedupe_groups.items())
        ],
        "type_distribution": distribution["spell_types"],
        "keyword_distribution": distribution["keywords"],
        "split_candidates": split_candidates,
        "merge_candidates": merge_candidates,
        "keyword_outliers": [
            keyword for keyword, count in keyword_counts.items() if count == 1
        ],
    }

    report_lines = [
        "# Spell Dataset Report",
        "",
        "## Scope",
        f"- Batch size: {len(records)} source spells",
        f"- Canonical types used: {len(type_counts)}",
        f"- Canonical keywords used: {len(keyword_counts)}",
        "- Deduplication policy: Option B (canonical record plus alias capacity)",
        f"- Description sources: {', '.join(f'{key}={value}' for key, value in sorted(description_sources.items()))}",
        "",
        "## Multi-Type Distribution",
    ]
    for count, amount in sorted(multi_type_counts.items()):
        report_lines.append(f"- {count} types: {amount} spells")

    report_lines.extend(["", "## Type Distribution"])
    for item in summary["type_distribution"]:
        report_lines.append(f"- {item['spell_type']}: {item['count']} — {item['note']}")

    report_lines.extend(["", "## Candidate Splits (>60)"])
    if split_candidates:
        for item in split_candidates:
            report_lines.append(f"- {item['spell_type']}: {item['count']}")
    else:
        report_lines.append("- None in this batch.")

    report_lines.extend(["", "## Candidate Merges (<8)"])
    if merge_candidates:
        for item in merge_candidates:
            report_lines.append(f"- {item['spell_type']}: {item['count']}")
    else:
        report_lines.append("- None in this batch.")

    report_lines.extend(["", "## Keyword Distribution"])
    for item in summary["keyword_distribution"]:
        report_lines.append(f"- {item['keyword']}: {item['count']}")

    report_lines.extend(["", "## Duplicate / Variant Log"])
    if summary["duplicate_groups"]:
        for group in summary["duplicate_groups"][:40]:
            report_lines.append(f"- {group['group']}")
            for entry in group["entries"]:
                report_lines.append(f"  - {entry['spell_name']}: {entry['reason']}")
        if len(summary["duplicate_groups"]) > 40:
            report_lines.append(f"- ... {len(summary['duplicate_groups']) - 40} additional groups omitted from markdown report; see JSON report for full detail.")
    else:
        report_lines.append("- No duplicate candidates were flagged in this pass.")

    report_lines.extend(["", "## Keyword Outliers"])
    for keyword in sorted(summary["keyword_outliers"]):
        report_lines.append(f"- {keyword}")

    return summary, "\n".join(report_lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Sorcery spell datasets from manual overrides and heuristics.")
    parser.add_argument("--count", type=int, default=50, help="Number of source spells to process.")
    parser.add_argument("--label", default="pilot", help="Output file label prefix.")
    args = parser.parse_args()

    raw_data = json.loads(RAW_PATH.read_text())
    count = max(1, min(args.count, len(raw_data["spells"])))
    source_spells = raw_data["spells"][:count]

    split_assignments = compute_split_assignments(source_spells, enforce_target_distribution=count == len(raw_data["spells"]))
    records = [build_record(spell, index + 1, split_assignments) for index, spell in enumerate(source_spells)]
    validation = validate(records)
    if not validation["passed"]:
        raise SystemExit("Validation failed:\n" + "\n".join(validation["errors"]))

    report_summary, report_markdown = build_reports(records)
    OUTPUT_DIR.mkdir(exist_ok=True)

    spell_name_display_overrides = {
        record["source_lineage"]["source_spell_name"]: record["spell_name"]
        for record in records
        if record["spell_name"] != record["source_lineage"]["source_spell_name"]
    }
    changed_name_count = len(spell_name_display_overrides)

    dataset_payload = {
        "metadata": {
            "source_file": str(RAW_PATH.name),
            "source_total_spells": raw_data["metadata"]["totalSpells"],
            "processed_scope": args.label,
            "processed_count": len(records),
            "taxonomy_mode": "approved-finalized-child-types",
            "taxonomy_plan_sources": [
                str(ROOT / ".kilo/plans/1779065784000-maester-taxonomy-continuation.md"),
                str(ROOT / ".kilo/plans/1779065784000-maester-taxonomy-next-pass-addendum.md"),
                str(ROOT / ".kilo/plans/1779065784000-maester-taxonomy-finalization.md"),
            ],
            "dedupe_policy": "Option B during build: canonical record with alias capacity.",
            "description_sources": report_summary["description_sources"],
            "voice_register": "restrained Westerosi maester",
            "spell_name_reviewed_count": len(records),
            "spell_name_changed_count": changed_name_count,
            "spell_name_kept_count": len(records) - changed_name_count,
            "spell_name_display_override_count": changed_name_count,
            "description_reviewed_count": len(records),
            "description_manual_override_count": report_summary["description_sources"].get("curated", 0),
            "description_generated_from_source_count": report_summary["description_sources"].get("generated-from-source", 0),
            "description_generated_fallback_count": report_summary["description_sources"].get("generated-fallback", 0),
            "spell_type_display_change_count": sum(1 for spell_type, display_name in TYPE_DISPLAY_NAMES.items() if spell_type != display_name),
            "approved_child_type_display_change_count": sum(1 for spell_type, display_name in APPROVED_CHILD_TYPE_DISPLAY_NAMES.items() if spell_type != display_name),
        },
        "spells": records,
    }
    framework_payload = {
        "canonical_spell_types": FINAL_SPELL_TYPES,
        "canonical_spell_type_display_names": {
            spell_type: APPROVED_CHILD_TYPE_DISPLAY_NAMES.get(spell_type, TYPE_DISPLAY_NAMES.get(spell_type, spell_type))
            for spell_type in FINAL_TYPE_ORDER
        },
        "approved_split_child_types": APPROVED_SPLIT_CHILD_TYPES,
        "stable_existing_final_types": STABLE_FINAL_TYPES,
        "approved_child_type_display_names": APPROVED_CHILD_TYPE_DISPLAY_NAMES,
        "spell_name_display_overrides": spell_name_display_overrides,
        "canonical_keywords": KEYWORD_VOCABULARY,
    }

    (OUTPUT_DIR / f"{args.label}-spells.json").write_text(json.dumps(dataset_payload, indent=2, ensure_ascii=False) + "\n")
    (OUTPUT_DIR / f"{args.label}-framework.json").write_text(json.dumps(framework_payload, indent=2, ensure_ascii=False) + "\n")
    (OUTPUT_DIR / f"{args.label}-report.json").write_text(json.dumps(report_summary, indent=2, ensure_ascii=False) + "\n")
    (OUTPUT_DIR / f"{args.label}-report.md").write_text(report_markdown)
    (OUTPUT_DIR / f"{args.label}-validation.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
