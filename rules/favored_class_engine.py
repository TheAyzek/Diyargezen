"""
Pathfinder 1st Edition Favored Class Bonus (FCB) & Racial Options Engine
========================================================================
References:
- PF1e Core Rulebook p. 31 (Favored Class Rules)
- PF1e Advanced Player's Guide (APG) & Advanced Race Guide (ARG) (Racial Alternate FCBs)

Core Mechanics:
- When a character gains a level in their favored class, they choose either:
  1. +1 Hit Point (HP)
  2. +1 Skill Rank
  3. A racial favored class bonus specific to their race and class
- Half-Elves have the Multitalented trait, allowing them to choose two favored classes.
"""

from typing import Dict, Any, List, Optional


# Registry of Paizo official racial favored class options
RACIAL_FCB_REGISTRY: Dict[str, Dict[str, Dict[str, Any]]] = {
    "human": {
        "fighter": {
            "key": "human_fighter_cmd",
            "name": "+1 CMD vs Bull Rush / Trip",
            "description": "+1 to the fighter's CMD when resisting a bull rush or trip combat maneuver.",
            "fraction": 1.0,
            "target": "cmd_special"
        },
        "wizard": {
            "key": "human_wizard_spell",
            "name": "+1/6 Ekstra Büyü (Spell Known)",
            "description": "Add one spell from the wizard spell list to the spellbook (must be at least 1 level below highest).",
            "fraction": 1/6,
            "target": "bonus_spells_known"
        },
        "sorcerer": {
            "key": "human_sorcerer_spell",
            "name": "+1/6 Ekstra Büyü (Spell Known)",
            "description": "Add one spell known from the sorcerer spell list (at least 1 level below highest).",
            "fraction": 1/6,
            "target": "bonus_spells_known"
        },
        "rogue": {
            "key": "human_rogue_talent",
            "name": "+1/6 Rogue Talent",
            "description": "Gain +1/6 of a new rogue talent.",
            "fraction": 1/6,
            "target": "bonus_talents"
        },
        "cleric": {
            "key": "human_cleric_spell",
            "name": "+1/6 Ekstra Büyü",
            "description": "Add one spell from the cleric spell list to the list of known spells (or domain slots).",
            "fraction": 1/6,
            "target": "bonus_spells_known"
        },
        "bard": {
            "key": "human_bard_spell",
            "name": "+1/6 Ekstra Büyü",
            "description": "Add one spell known from the bard spell list.",
            "fraction": 1/6,
            "target": "bonus_spells_known"
        },
        "paladin": {
            "key": "human_paladin_energy",
            "name": "+1/2 Energy Resistance",
            "description": "Add +1 to the paladin's energy resistance to one energy type (max 10).",
            "fraction": 0.5,
            "target": "energy_resistance"
        }
    },
    "dwarf": {
        "fighter": {
            "key": "dwarf_fighter_cmd",
            "name": "+1 CMD vs Bull Rush / Trip",
            "description": "+1 to CMD when resisting a bull rush or trip maneuver while standing on ground.",
            "fraction": 1.0,
            "target": "cmd_special"
        },
        "barbarian": {
            "key": "dwarf_barbarian_spell_save",
            "name": "+1/3 Save vs Spells (Rage)",
            "description": "Add +1/3 to the barbarian's saving throws against spells while raging.",
            "fraction": 1/3,
            "target": "saves_vs_spells"
        },
        "cleric": {
            "key": "dwarf_cleric_channel",
            "name": "+1/2 Channel Damage/Heal (Undead)",
            "description": "Add +1/2 to the cleric's channeled energy damage against undead.",
            "fraction": 0.5,
            "target": "channel_energy_bonus"
        }
    },
    "elf": {
        "wizard": {
            "key": "elf_wizard_sr",
            "name": "+1/2 CL to Overcome Spell Resistance",
            "description": "Add +1/2 to caster level checks made to overcome spell resistance.",
            "fraction": 0.5,
            "target": "spell_penetration"
        },
        "rogue": {
            "key": "elf_rogue_talent",
            "name": "+1/6 Rogue Talent",
            "description": "Gain +1/6 of a new rogue talent.",
            "fraction": 1/6,
            "target": "bonus_talents"
        },
        "ranger": {
            "key": "elf_ranger_favored_enemy",
            "name": "+1/2 Favored Enemy Damage",
            "description": "Add +1/2 to weapon damage rolls against the ranger's favored enemies.",
            "fraction": 0.5,
            "target": "favored_enemy_damage"
        }
    },
    "half-elf": {
        "ranger": {
            "key": "half_elf_ranger_hp",
            "name": "+1/4 Companion HP",
            "description": "Add +1 hit point to the ranger's animal companion.",
            "fraction": 0.25,
            "target": "companion_hp"
        },
        "summoner": {
            "key": "half_elf_summoner_points",
            "name": "+1/4 Evolution Point",
            "description": "Add +1/4 to the summoner's eidolon evolution pool.",
            "fraction": 0.25,
            "target": "evolution_points"
        }
    },
    "half-orc": {
        "inquisitor": {
            "key": "half_orc_inquisitor_intimidate",
            "name": "+1/2 Intimidate & Knowledge",
            "description": "Add +1/2 on Intimidate checks and Knowledge checks to identify creatures.",
            "fraction": 0.5,
            "target": "skill:intimidate"
        },
        "barbarian": {
            "key": "half_orc_barbarian_rounds",
            "name": "+1 Round of Rage",
            "description": "Add +1 to the barbarian's total number of rage rounds per day.",
            "fraction": 1.0,
            "target": "rage_rounds"
        },
        "fighter": {
            "key": "half_orc_fighter_crit",
            "name": "+1/2 to Critical Confirmation Rolls",
            "description": "Add +1/2 to critical hit confirmation rolls (max +4).",
            "fraction": 0.5,
            "target": "crit_confirmation"
        }
    },
    "gnome": {
        "bard": {
            "key": "gnome_bard_illusion_dc",
            "name": "+1/6 Illusion DC",
            "description": "Add +1/6 to the DC of all illusion spells cast by the bard.",
            "fraction": 1/6,
            "target": "illusion_dc"
        },
        "alchemist": {
            "key": "gnome_alchemist_bomb",
            "name": "+1/2 Bomb per Day",
            "description": "Add +1/2 to the number of bombs per day the alchemist can create.",
            "fraction": 0.5,
            "target": "bombs_per_day"
        }
    },
    "halfling": {
        "rogue": {
            "key": "halfling_rogue_acro_stealth",
            "name": "+1/2 Acrobatics & Stealth",
            "description": "Add +1/2 bonus on Acrobatics and Stealth skill checks.",
            "fraction": 0.5,
            "target": "skill_bonus"
        },
        "paladin": {
            "key": "halfling_paladin_saves",
            "name": "+1/2 to Halfling Luck Saves",
            "description": "Add +1/2 to the paladin's racial saving throw bonus (Fear & all saves).",
            "fraction": 0.5,
            "target": "saving_throws.all"
        }
    }
}


def get_racial_fcb_options(race: str, char_class: str) -> List[Dict[str, Any]]:
    """Returns available racial FCB options for a given race and class combination."""
    r_key = (race or "").lower().strip().replace(" ", "-").replace("i̇", "i")
    # Normalize Turkish race names
    TURKISH_RACE_MAP = {
        "insan": "human", "yarim-elf": "half-elf", "yarım-elf": "half-elf",
        "yarim-ork": "half-orc", "yarım-ork": "half-orc", "cuce": "dwarf", "cüce": "dwarf",
        "bucukluk": "halfling", "buçukluk": "halfling", "gnom": "gnome"
    }
    r_key = TURKISH_RACE_MAP.get(r_key, r_key)

    c_key = (char_class or "").lower().strip()

    race_data = RACIAL_FCB_REGISTRY.get(r_key, {})
    options = []

    # Check specific class
    if c_key in race_data:
        options.append(race_data[c_key])

    # Add standard HP and Skill options
    standard_options = [
        {
            "key": "hp",
            "name": "+1 Can Puanı (+1 HP)",
            "description": "Karakterin toplam can puanı havuzuna +1 HP ekler.",
            "fraction": 1.0,
            "target": "hp"
        },
        {
            "key": "skill",
            "name": "+1 Yetenek Puanı (+1 Skill Rank)",
            "description": "Karakterin dağıtabileceği toplam yetenek puanı havuzuna +1 Rank ekler.",
            "fraction": 1.0,
            "target": "skill_points"
        }
    ]

    return standard_options + options


def evaluate_favored_class_bonuses(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates character's favored class bonus allocation.
    Returns aggregated HP, Skill Ranks, Racial bonuses and allocation status.
    """
    char_class = str(character.get("class", "Fighter")).strip()
    char_race = str(character.get("race", "Human")).strip()
    total_level = int(character.get("level", 1))

    favored_class = str(character.get("favored_class") or char_class).strip()
    sec_favored_class = str(character.get("secondary_favored_class") or "").strip()

    is_half_elf = "half-elf" in char_race.lower() or "yarım-elf" in char_race.lower() or "yarim-elf" in char_race.lower()

    # Calculate total eligible levels (levels in primary class + multiclass if in favored classes)
    eligible_levels = 0
    multiclass_data = character.get("multiclass")
    if isinstance(multiclass_data, dict) and multiclass_data:
        for c_name, c_lvl in multiclass_data.items():
            c_name_clean = str(c_name).strip()
            if c_name_clean.lower() == favored_class.lower() or (is_half_elf and sec_favored_class and c_name_clean.lower() == sec_favored_class.lower()):
                eligible_levels += int(c_lvl)
    else:
        eligible_levels = total_level

    # Parse FCB choices
    raw_fcb = character.get("favored_class_bonuses") or character.get("fcb_choices") or []
    hp_count = 0
    skill_count = 0
    racial_counts: Dict[str, int] = {}
    choices_by_level = []

    if isinstance(raw_fcb, list):
        for idx, item in enumerate(raw_fcb, 1):
            choice = "hp"
            if isinstance(item, dict):
                choice = str(item.get("choice", "hp")).lower().strip()
            elif isinstance(item, str):
                choice = item.lower().strip()

            if choice == "hp":
                hp_count += 1
            elif choice in ("skill", "skill_rank", "skill_point"):
                skill_count += 1
            else:
                # Racial choice
                racial_counts[choice] = racial_counts.get(choice, 0) + 1

            choices_by_level.append({"level": idx, "choice": choice})

    elif isinstance(raw_fcb, dict):
        hp_count = int(raw_fcb.get("hp", 0))
        skill_count = int(raw_fcb.get("skill", 0))
        r_key = raw_fcb.get("racial_key")
        r_val = int(raw_fcb.get("racial", 0))
        if r_key and r_val > 0:
            racial_counts[r_key] = r_val

        # Synthesize choices list
        lvl = 1
        for _ in range(hp_count):
            choices_by_level.append({"level": lvl, "choice": "hp"})
            lvl += 1
        for _ in range(skill_count):
            choices_by_level.append({"level": lvl, "choice": "skill"})
            lvl += 1
        if r_key:
            for _ in range(r_val):
                choices_by_level.append({"level": lvl, "choice": r_key})
                lvl += 1

    allocated_count = hp_count + skill_count + sum(racial_counts.values())
    unallocated_count = max(0, eligible_levels - allocated_count)

    # Compute effective racial bonus values (floored fractions)
    racial_bonuses = []
    available_racial_options = {
        opt["key"]: opt for opt in get_racial_fcb_options(char_race, favored_class)
    }

    for r_key, count in racial_counts.items():
        opt = available_racial_options.get(r_key)
        fraction = opt.get("fraction", 1.0) if opt else 1.0
        effective_val = int(count * fraction)
        racial_bonuses.append({
            "key": r_key,
            "name": opt.get("name", r_key) if opt else r_key,
            "allocated_ranks": count,
            "fraction": fraction,
            "effective_value": effective_val,
            "target": opt.get("target") if opt else None
        })

    return {
        "favored_class": favored_class,
        "secondary_favored_class": sec_favored_class if is_half_elf else None,
        "total_eligible_levels": eligible_levels,
        "allocated_count": allocated_count,
        "unallocated_count": unallocated_count,
        "hp_bonus": hp_count,
        "skill_bonus": skill_count,
        "racial_counts": racial_counts,
        "racial_bonuses": racial_bonuses,
        "choices_by_level": choices_by_level,
        "is_complete": unallocated_count == 0
    }
