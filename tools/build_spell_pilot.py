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
    "Ageing": "Secondary functional type for spells whose defining mechanic is magical aging or immunity to it.",
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
    ("ageing", ["Ageing", "Necromantic"]),
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
    "Ageing": ("ageing", "aging", "older", "younger", "year older", "senescence"),
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
        "description": "For three minutes, a ranged weapon flies truer than its maker had any right to expect. It grants +1 to hit per spell level, though any sensible lord or GM will set a ceiling according to the campaign's TL.",
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
        "description": "For three minutes, bestow Luck upon a single animal. Kennelmasters, falconers, and fools overfond of warhounds will all find uses for that.",
    },
    "Train Animal": {
        "spell_types": ["Animal", "Knowledge"],
        "keywords": ["Buff", "Leveled", "No-Signature", "Utility"],
        "description": "Raise an animal's effective IQ for training by 1 per level, to no more than IQ 5, and do so in a fashion that truly lasts. Dispel Magic, Remove Curse, and no-mana ground will not unteach the beast.",
    },
    "Age (Variant)": {
        "spell_types": ["Ageing", "Necromantic"],
        "keywords": ["Malediction", "Resisted-HT", "Debuff", "No-Signature"],
        "description": "Should the subject fail HT, it is made one year older at once, with no gaudy display to warn the hall. Time, when summoned so neatly, can be quite rude.",
        "dedupe": {"status": "variant", "group": "ageing-single-year", "reason": "Keep distinct from Temporary Ageing because this version is permanent."},
    },
    "Burden of Time": {
        "spell_types": ["Ageing", "Necromantic"],
        "keywords": ["Area", "Leveled", "Damage", "Persistent", "Unresisted", "No-Signature"],
        "description": "Set a wandering patch of withering years upon the field for 10 seconds. All living creatures within age 1d-1 years each second, though the loss is temporary and may be shed later by successful Original HT rolls made when healing would otherwise be wasted.",
    },
    "Decrepify": {
        "spell_types": ["Ageing", "Necromantic"],
        "keywords": ["Touch", "Melee", "Malediction", "Resisted-HT", "Debuff", "Leveled"],
        "description": "A mere touch, if it lands and the subject fails HT, lays 1d years per spell level upon living flesh forever. It is close work and ugly work, as such arts commonly are.",
    },
    "Progeria": {
        "spell_types": ["Ageing", "Necromantic"],
        "keywords": ["Malediction", "Resisted-HT", "Debuff", "Cyclic", "No-Signature", "Persistent", "Leveled"],
        "description": "Lay a curse that ages a living subject by one year at once and again each day for 9 days more. Each extra level adds 10 further daily cycles, and only Remove Curse or its peers will cut the thread early.",
    },
    "Protection from Ageing": {
        "spell_types": ["Ageing", "Protection"],
        "keywords": ["Buff", "Defense", "No-Signature"],
        "description": "For three minutes, the subject bears Unaging and may meet magical senescence without bowing to it. Useful whenever rival sorcerers grow too fond of the calendar.",
    },
    "Reaper’s Embrace": {
        "spell_types": ["Ageing", "Necromantic"],
        "keywords": ["Buff", "Aura", "Damage", "Unresisted", "No-Signature"],
        "description": "For three minutes, the subject is mantled in a black aura that ages anyone who touches him by one year. It is a persuasive answer to grapplers and all others who mistake proximity for safety.",
    },
    "Temporary Ageing": {
        "spell_types": ["Ageing", "Necromantic"],
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
        "description": "For three minutes, the subject may fly and hover at Basic Speed × 2, provided there is proper air to bear him. In vacuum, trace atmosphere, or water, the spell proves as useful as a maester's chain in a sword fight.",
        "dedupe": {"status": "variant", "group": "aerial-flight", "reason": "Keep distinct from Personal Aerial Flight because this version is ranged and temporary on another subject."},
    },
    "Aerial Servant": {
        "spell_types": ["Air", "Summoning"],
        "keywords": ["Summoning", "Control", "Utility", "Persistent"],
        "description": "After an hour's ritual and a Quick Contest of Will, you may compel an unwilling aerial servant worth up to 150% of your points to appear. It serves for hours equal to your margin of victory, but neglect the spell and the creature will remember precisely why it hates you.",
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
}


TYPE_ORDER = list(CANONICAL_TYPES)
KEYWORD_ORDER = list(KEYWORD_VOCABULARY)


def order_unique(values: list[str], order: list[str]) -> list[str]:
    seen: set[str] = set()
    kept = [value for value in values if value and not (value in seen or seen.add(value))]
    position = {value: index for index, value in enumerate(order)}
    return sorted(kept, key=lambda value: (position.get(value, len(position)), value))


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def trim_period(text: str) -> str:
    return normalize_ws(text).rstrip(".")


def sentence_split(text: str) -> list[str]:
    normalized = normalize_ws(text)
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
            if phrase in name_text:
                scores[spell_type] += 3
            elif phrase in full_text:
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
        ("This spell lets you ", "This working lets you "),
        ("This spell lets the subject ", "This working lets the subject "),
        ("This spell allows you to ", "This working allows you to "),
        ("This spell allows the caster to ", "This working allows the caster to "),
        ("This spell allows ", "This working allows "),
        ("This spell causes ", "This working causes "),
        ("This spell gives ", "This working grants "),
        ("This spell removes ", "This working removes "),
        ("This spell creates ", "This working creates "),
        ("This spell conjures ", "This working conjures "),
        ("You can ", "You may "),
        ("The spell allows ", "The working allows "),
    ]
    for source, target in replacements:
        if text.startswith(source):
            text = target + text[len(source):]
            break
    return text.replace("doesn't", "does not").replace("can't", "cannot")


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
    if "Buff" in keywords and range_text.lower() == "self":
        core = f"For {duration.lower()}, you gain the spell's listed {spell_types[0].lower()} benefits."
    elif "Buff" in keywords:
        core = f"For {duration.lower()}, the subject gains the spell's listed benefits at {range_text.lower()} range."
    elif "Area" in keywords:
        core = f"{raw_spell['spell_name']} lays its effect over an area at {range_text.lower()} for {duration.lower()}."
    elif any(keyword.startswith("Resisted-") for keyword in keywords):
        resistance = next(keyword for keyword in keywords if keyword.startswith("Resisted-"))
        core = f"This working is cast at {range_text.lower()}; should the subject fail {resistance.replace('-', ' ').lower()}, it suffers the spell's listed effect."
    else:
        core = f"{raw_spell['spell_name']} works at {range_text.lower()} for {duration.lower()}, according to the listed mechanics."
    return f"{core} {choose_coda(raw_spell['spell_name'], keywords)}"


def pick_source_prose(raw_spell: dict[str, Any]) -> str:
    description = normalize_ws(raw_spell.get("description", ""))
    if description:
        return description

    duration = normalize_ws(raw_spell.get("duration", ""))
    if len(duration) > 100 and any(mark in duration for mark in [".", ";"]):
        return duration

    return ""


def generate_description(raw_spell: dict[str, Any], spell_types: list[str], keywords: list[str]) -> tuple[str, str]:
    if raw_spell["spell_name"] in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[raw_spell["spell_name"]]["description"].strip(), "curated"

    original = pick_source_prose(raw_spell)
    if not original:
        return fallback_description(raw_spell, spell_types, keywords), "generated-fallback"

    sentences = sentence_split(original)
    lead = []
    current_length = 0
    for sentence in sentences:
        addition = len(sentence) + (1 if lead else 0)
        if lead and (len(lead) >= 2 or current_length + addition > 340):
            break
        lead.append(sentence)
        current_length += addition

    summary = stylize_summary(" ".join(lead))
    if not summary.endswith((".", "!", "?")):
        summary += "."
    coda = choose_coda(raw_spell["spell_name"], keywords)
    if coda not in summary:
        summary = f"{summary} {coda}"
    return summary, "generated-from-source"


def build_record(raw_spell: dict[str, Any], index: int) -> dict[str, Any]:
    name = raw_spell["spell_name"]
    override = MANUAL_OVERRIDES.get(name)
    parsed_source_keywords = parse_raw_keywords(raw_spell["keywords"])

    if override:
        spell_types = order_unique(override["spell_types"], TYPE_ORDER)
        keywords = infer_role_keywords(raw_spell, spell_types, order_unique(override["keywords"], KEYWORD_ORDER))
        description = override["description"].strip()
        description_source = "curated"
        dedupe = override.get("dedupe", {"status": "unique", "group": None, "reason": "No duplicate candidate identified during build."})
    else:
        spell_types = infer_spell_types(raw_spell, parsed_source_keywords)
        keywords = infer_role_keywords(raw_spell, spell_types, parsed_source_keywords)
        description, description_source = generate_description(raw_spell, spell_types, keywords)
        dedupe = infer_dedupe(raw_spell)

    return {
        "record_index": index,
        "spell_id": raw_spell["spell_id"],
        "spell_name": name,
        "spell_types": spell_types,
        "keywords": keywords,
        "full_cost": raw_spell["full_cost"],
        "casting_roll": raw_spell["casting_roll"],
        "range": raw_spell["range"],
        "duration": raw_spell["duration"],
        "description": description,
        "description_source": description_source,
        "statistics": raw_spell["statistics"],
        "use_example": "",
        "aliases": [],
        "dedupe": dedupe,
        "source_lineage": {
            "source_spell_id": raw_spell["spell_id"],
            "source_spell_types": raw_spell["spell_types"],
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
        unknown_types = [spell_type for spell_type in record["spell_types"] if spell_type not in CANONICAL_TYPES]
        if unknown_types:
            errors.append(f"{record['spell_name']}: unknown spell types {unknown_types}")
        if not record["keywords"]:
            errors.append(f"{record['spell_name']}: missing keywords")
        if any(keyword.lower() == "none" for keyword in record["keywords"]):
            errors.append(f"{record['spell_name']}: contains None keyword")
        unknown_keywords = [keyword for keyword in record["keywords"] if keyword not in KEYWORD_VOCABULARY]
        if unknown_keywords:
            errors.append(f"{record['spell_name']}: unknown keywords {unknown_keywords}")
        if not record["description"].strip():
            errors.append(f"{record['spell_name']}: blank description")
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

    records = [build_record(spell, index + 1) for index, spell in enumerate(source_spells)]
    validation = validate(records)
    if not validation["passed"]:
        raise SystemExit("Validation failed:\n" + "\n".join(validation["errors"]))

    report_summary, report_markdown = build_reports(records)
    OUTPUT_DIR.mkdir(exist_ok=True)

    dataset_payload = {
        "metadata": {
            "source_file": str(RAW_PATH.name),
            "source_total_spells": raw_data["metadata"]["totalSpells"],
            "processed_scope": args.label,
            "processed_count": len(records),
            "dedupe_policy": "Option B during build: canonical record with alias capacity.",
            "description_sources": report_summary["description_sources"],
        },
        "spells": records,
    }
    framework_payload = {
        "canonical_spell_types": CANONICAL_TYPES,
        "canonical_keywords": KEYWORD_VOCABULARY,
    }

    (OUTPUT_DIR / f"{args.label}-spells.json").write_text(json.dumps(dataset_payload, indent=2, ensure_ascii=False) + "\n")
    (OUTPUT_DIR / f"{args.label}-framework.json").write_text(json.dumps(framework_payload, indent=2, ensure_ascii=False) + "\n")
    (OUTPUT_DIR / f"{args.label}-report.json").write_text(json.dumps(report_summary, indent=2, ensure_ascii=False) + "\n")
    (OUTPUT_DIR / f"{args.label}-report.md").write_text(report_markdown)
    (OUTPUT_DIR / f"{args.label}-validation.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
