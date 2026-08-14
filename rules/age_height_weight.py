"""
Pathfinder 1st Edition Age, Height & Weight Engine
===================================================
References:
- PF1e Core Rulebook p. 168-169 (Table 7-1: Random Starting Ages)
- PF1e Core Rulebook p. 169 (Table 7-2: Aging Effects)
- PF1e Core Rulebook p. 169 (Table 7-3: Random Height and Weight)

Aging Effects (Cumulative):
- Middle Age:  -1 Str, -1 Dex, -1 Con | +1 Int, +1 Wis, +1 Cha
- Old:         -3 Str, -3 Dex, -3 Con | +2 Int, +2 Wis, +2 Cha
- Venerable:   -6 Str, -6 Dex, -6 Con | +3 Int, +3 Wis, +3 Cha
"""

import random
from typing import Dict, Any, List, Optional, Tuple


AGE_THRESHOLDS_BY_RACE: Dict[str, Dict[str, Any]] = {
    "human": {
        "adulthood": 15,
        "middle_age": 35,
        "old": 53,
        "venerable": 70,
        "max_age_dice": "2d20",
        "starting_dice": {"intuitive": "1d4", "self_taught": "1d6", "trained": "2d6"}
    },
    "dwarf": {
        "adulthood": 40,
        "middle_age": 125,
        "old": 188,
        "venerable": 250,
        "max_age_dice": "2d100",
        "starting_dice": {"intuitive": "3d6", "self_taught": "5d6", "trained": "7d6"}
    },
    "elf": {
        "adulthood": 110,
        "middle_age": 175,
        "old": 263,
        "venerable": 350,
        "max_age_dice": "4d100",
        "starting_dice": {"intuitive": "4d6", "self_taught": "6d6", "trained": "10d6"}
    },
    "gnome": {
        "adulthood": 40,
        "middle_age": 100,
        "old": 150,
        "venerable": 200,
        "max_age_dice": "3d100",
        "starting_dice": {"intuitive": "4d6", "self_taught": "6d6", "trained": "9d6"}
    },
    "half-elf": {
        "adulthood": 20,
        "middle_age": 62,
        "old": 93,
        "venerable": 125,
        "max_age_dice": "3d20",
        "starting_dice": {"intuitive": "1d6", "self_taught": "2d6", "trained": "3d6"}
    },
    "half-orc": {
        "adulthood": 14,
        "middle_age": 30,
        "old": 45,
        "venerable": 60,
        "max_age_dice": "2d10",
        "starting_dice": {"intuitive": "1d4", "self_taught": "1d6", "trained": "2d6"}
    },
    "halfling": {
        "adulthood": 20,
        "middle_age": 50,
        "old": 75,
        "venerable": 100,
        "max_age_dice": "5d20",
        "starting_dice": {"intuitive": "2d4", "self_taught": "3d6", "trained": "4d6"}
    }
}


HEIGHT_WEIGHT_BY_RACE: Dict[str, Dict[str, Dict[str, Any]]] = {
    "human": {
        "male":   {"base_height_in": 58, "height_dice": "2d10", "base_weight_lb": 120, "weight_mult": 5},
        "female": {"base_height_in": 53, "height_dice": "2d10", "base_weight_lb": 85,  "weight_mult": 5}
    },
    "dwarf": {
        "male":   {"base_height_in": 45, "height_dice": "2d4",  "base_weight_lb": 150, "weight_mult": 7},
        "female": {"base_height_in": 43, "height_dice": "2d4",  "base_weight_lb": 120, "weight_mult": 7}
    },
    "elf": {
        "male":   {"base_height_in": 64, "height_dice": "2d8",  "base_weight_lb": 100, "weight_mult": 3},
        "female": {"base_height_in": 64, "height_dice": "2d6",  "base_weight_lb": 90,  "weight_mult": 3}
    },
    "gnome": {
        "male":   {"base_height_in": 36, "height_dice": "2d4",  "base_weight_lb": 35,  "weight_mult": 1},
        "female": {"base_height_in": 36, "height_dice": "2d4",  "base_weight_lb": 30,  "weight_mult": 1}
    },
    "half-elf": {
        "male":   {"base_height_in": 62, "height_dice": "2d8",  "base_weight_lb": 110, "weight_mult": 5},
        "female": {"base_height_in": 60, "height_dice": "2d8",  "base_weight_lb": 90,  "weight_mult": 5}
    },
    "half-orc": {
        "male":   {"base_height_in": 58, "height_dice": "2d12", "base_weight_lb": 150, "weight_mult": 7},
        "female": {"base_height_in": 53, "height_dice": "2d12", "base_weight_lb": 110, "weight_mult": 7}
    },
    "halfling": {
        "male":   {"base_height_in": 32, "height_dice": "2d4",  "base_weight_lb": 30,  "weight_mult": 1},
        "female": {"base_height_in": 30, "height_dice": "2d4",  "base_weight_lb": 25,  "weight_mult": 1}
    }
}


def normalize_race_key(race: str) -> str:
    """Normalizes race name (handling Turkish and English variants)."""
    r = (race or "").lower().strip().replace(" ", "-").replace("i̇", "i")
    TURKISH_RACE_MAP = {
        "insan": "human", "yarim-elf": "half-elf", "yarım-elf": "half-elf",
        "yarim-ork": "half-orc", "yarım-ork": "half-orc", "cuce": "dwarf", "cüce": "dwarf",
        "bucukluk": "halfling", "buçukluk": "halfling", "gnom": "gnome"
    }
    return TURKISH_RACE_MAP.get(r, r)


def get_class_training_type(char_class: str) -> str:
    """Determines class training category (intuitive, self_taught, or trained)."""
    c = (char_class or "").lower().strip()
    INTUITIVE_CLASSES = {"barbarian", "oracle", "rogue", "sorcerer", "bloodrager"}
    TRAINED_CLASSES = {"alchemist", "cleric", "druid", "inquisitor", "magus", "monk", "wizard", "arcanist", "shaman", "investigator"}
    if c in INTUITIVE_CLASSES:
        return "intuitive"
    if c in TRAINED_CLASSES:
        return "trained"
    return "self_taught"


def get_age_category_and_modifiers(race: str, age: Optional[int]) -> Dict[str, Any]:
    """
    Evaluates character age against racial thresholds and returns category & modifiers.
    """
    r_key = normalize_race_key(race)
    thresholds = AGE_THRESHOLDS_BY_RACE.get(r_key, AGE_THRESHOLDS_BY_RACE["human"])

    if age is None:
        age_val = thresholds["adulthood"]
    else:
        try:
            age_val = max(1, int(age))
        except (ValueError, TypeError):
            age_val = thresholds["adulthood"]

    mid = thresholds["middle_age"]
    old = thresholds["old"]
    ven = thresholds["venerable"]

    # Calculate category and cumulative modifiers
    if age_val >= ven:
        cat_code = "venerable"
        cat_name = "Kadim (Venerable)"
        physical_mod = -6
        mental_mod = +3
        badge_color = "#e94560"
    elif age_val >= old:
        cat_code = "old"
        cat_name = "Yaşlı (Old)"
        physical_mod = -3
        mental_mod = +2
        badge_color = "#ff9f43"
    elif age_val >= mid:
        cat_code = "middle_age"
        cat_name = "Orta Yaş (Middle Age)"
        physical_mod = -1
        mental_mod = +1
        badge_color = "#feca57"
    else:
        cat_code = "adulthood"
        cat_name = "Yetişkin (Adulthood)"
        physical_mod = 0
        mental_mod = 0
        badge_color = "#4ec9b0"

    modifiers = {
        "strength": physical_mod,
        "dexterity": physical_mod,
        "constitution": physical_mod,
        "intelligence": mental_mod,
        "wisdom": mental_mod,
        "charisma": mental_mod
    }

    return {
        "age": age_val,
        "race": race,
        "category_code": cat_code,
        "category_name": cat_name,
        "badge_color": badge_color,
        "physical_modifier": physical_mod,
        "mental_modifier": mental_mod,
        "modifiers": modifiers,
        "thresholds": {
            "adulthood": thresholds["adulthood"],
            "middle_age": thresholds["middle_age"],
            "old": thresholds["old"],
            "venerable": thresholds["venerable"]
        }
    }


def generate_random_starting_age(
    race: str,
    char_class: str,
    roll_override: Optional[int] = None
) -> Dict[str, Any]:
    """Generates random or deterministic starting age based on class training."""
    r_key = normalize_race_key(race)
    thresholds = AGE_THRESHOLDS_BY_RACE.get(r_key, AGE_THRESHOLDS_BY_RACE["human"])
    t_type = get_class_training_type(char_class)

    base_adulthood = thresholds["adulthood"]
    dice_str = thresholds["starting_dice"][t_type]

    # Parse dice formula e.g. "2d6" -> count 2, sides 6
    parts = dice_str.split("d")
    d_count = int(parts[0])
    d_sides = int(parts[1])

    if roll_override is not None:
        bonus_years = int(roll_override)
    else:
        bonus_years = sum(random.randint(1, d_sides) for _ in range(d_count))

    starting_age = base_adulthood + bonus_years

    return {
        "race": race,
        "class": char_class,
        "training_type": t_type,
        "base_adulthood": base_adulthood,
        "dice_formula": dice_str,
        "bonus_years": bonus_years,
        "starting_age": starting_age
    }


def generate_random_height_weight(
    race: str,
    gender: str = "male",
    height_roll_override: Optional[int] = None
) -> Dict[str, Any]:
    """Generates height and weight based on PF1e official Table 7-3."""
    r_key = normalize_race_key(race)
    g_key = "female" if "fem" in (gender or "").lower() or "kadın" in (gender or "").lower() else "male"

    race_hw = HEIGHT_WEIGHT_BY_RACE.get(r_key, HEIGHT_WEIGHT_BY_RACE["human"])
    hw_config = race_hw.get(g_key, race_hw["male"])

    base_h = hw_config["base_height_in"]
    h_dice = hw_config["height_dice"]
    base_w = hw_config["base_weight_lb"]
    w_mult = hw_config["weight_mult"]

    # Parse dice formula e.g. "2d10"
    parts = h_dice.split("d")
    d_count = int(parts[0])
    d_sides = int(parts[1])

    if height_roll_override is not None:
        height_mod = int(height_roll_override)
    else:
        height_mod = sum(random.randint(1, d_sides) for _ in range(d_count))

    total_height_in = base_h + height_mod
    total_weight_lb = base_w + (height_mod * w_mult)

    feet = total_height_in // 12
    inches = total_height_in % 12
    height_formatted_imperial = f"{feet}'{inches}\""
    height_formatted_metric = f"{round(total_height_in * 2.54)} cm"
    weight_formatted_metric = f"{round(total_weight_lb * 0.453592)} kg"

    return {
        "race": race,
        "gender": g_key,
        "height_inches": total_height_in,
        "height_imperial": height_formatted_imperial,
        "height_metric": height_formatted_metric,
        "weight_lbs": total_weight_lb,
        "weight_metric": weight_formatted_metric,
        "base_height_in": base_h,
        "height_mod": height_mod,
        "base_weight_lb": base_w,
        "weight_mult": w_mult
    }


def get_physical_rules_catalog() -> Dict[str, Any]:
    """Returns complete age, height and weight tables."""
    return {
        "age_thresholds": AGE_THRESHOLDS_BY_RACE,
        "height_weight_tables": HEIGHT_WEIGHT_BY_RACE
    }
