"""
Otomatik Hesaplama Modülü
Kural kitaplarından otomatik hesaplamalar yapar.
"""

from typing import Dict, Any, Optional


# ============================================================================
# D&D 5e Hesaplamaları
# ============================================================================

def calculate_proficiency_bonus(level: int) -> int:
    """
    D&D 5e Proficiency Bonus hesaplama
    Seviyeye göre: 1-4: +2, 5-8: +3, 9-12: +4, 13-16: +5, 17-20: +6
    """
    if level <= 4:
        return 2
    elif level <= 8:
        return 3
    elif level <= 12:
        return 4
    elif level <= 16:
        return 5
    else:  # 17-20
        return 6


def calculate_ability_modifier(ability_score: int) -> int:
    """
    Ability Modifier hesaplama: (score - 10) // 2
    """
    return (ability_score - 10) // 2


def calculate_armor_class(character: Dict[str, Any], armor_data: Optional[Dict[str, Any]] = None) -> int:
    """
    D&D 5e Armor Class hesaplama
    Zırh tipine göre AC hesaplar
    """
    abilities = character.get("abilities", {})
    dex_modifier = calculate_ability_modifier(abilities.get("Dexterity", 10))
    
    # Zırh kontrolü
    equipment = character.get("equipment", [])
    armor = None
    for item in equipment:
        if item.get("type") == "armor":
            armor = item
            break
    
    if not armor:
        # Zırh yoksa: 10 + DEX modifier
        return 10 + dex_modifier
    
    armor_name = armor.get("name", "").lower()
    
    # Zırh tipine göre AC hesaplama
    if "leather" in armor_name or "padded" in armor_name:
        return 11 + dex_modifier
    elif "studded leather" in armor_name:
        return 12 + dex_modifier
    elif "hide" in armor_name:
        return 12 + min(dex_modifier, 2)  # Max +2 DEX
    elif "chain shirt" in armor_name or "scale mail" in armor_name:
        return 14 + min(dex_modifier, 2)  # Max +2 DEX
    elif "breastplate" in armor_name or "half plate" in armor_name:
        return 15 + min(dex_modifier, 2)  # Max +2 DEX
    elif "ring mail" in armor_name:
        return 14  # No DEX modifier
    elif "chain mail" in armor_name or "splint" in armor_name:
        return 16  # No DEX modifier
    elif "plate" in armor_name:
        return 18  # No DEX modifier
    else:
        # Bilinmeyen zırh tipi, default
        return 10 + dex_modifier


def calculate_hit_points(character: Dict[str, Any], class_data: Optional[Dict[str, Any]] = None) -> int:
    """
    D&D 5e Hit Points hesaplama
    Sınıf hit dice + CON modifier (her seviyede)
    """
    level = character.get("level", 1)
    abilities = character.get("abilities", {})
    con_modifier = calculate_ability_modifier(abilities.get("Constitution", 10))
    
    char_class = character.get("class", "")
    if not class_data or not char_class:
        # Default: d8 hit dice
        hit_dice = 8
    else:
        class_info = class_data.get("classes", {}).get(char_class, {})
        hit_dice = class_info.get("hit_dice", 8)
    
    # 1. seviye: max hit dice + CON modifier
    # Sonraki seviyeler: (hit dice / 2 + 1) + CON modifier (ortalama)
    if level == 1:
        hp = hit_dice + con_modifier
    else:
        hp = hit_dice + con_modifier  # 1. seviye
        # 2-20. seviyeler için ortalama
        average_roll = (hit_dice // 2) + 1
        hp += (average_roll + con_modifier) * (level - 1)
    
    return max(1, hp)  # Minimum 1 HP


def calculate_spell_slots(character: Dict[str, Any], class_data: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
    """
    D&D 5e Spell Slots hesaplama
    Sınıf ve seviyeye göre spell slot'ları döndürür
    """
    level = character.get("level", 1)
    char_class = character.get("class", "")
    
    # Spellcasting sınıfları ve slot tabloları
    spell_slots_table = {
        "Wizard": {
            1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}, 4: {1: 4, 2: 3},
            5: {1: 4, 2: 3, 3: 2}, 6: {1: 4, 2: 3, 3: 3}, 7: {1: 4, 2: 3, 3: 3, 4: 1},
            8: {1: 4, 2: 3, 3: 3, 4: 2}, 9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}, 11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
            12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1}, 13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
            14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1}, 15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
            16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, 17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
            18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1}, 19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
            20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1}
        },
        "Sorcerer": {
            1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}, 4: {1: 4, 2: 3},
            5: {1: 4, 2: 3, 3: 2}, 6: {1: 4, 2: 3, 3: 3}, 7: {1: 4, 2: 3, 3: 3, 4: 1},
            8: {1: 4, 2: 3, 3: 3, 4: 2}, 9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}, 11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
            12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1}, 13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
            14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1}, 15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
            16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, 17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
            18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1}, 19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
            20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1}
        }
    }
    
    if char_class in spell_slots_table:
        return spell_slots_table[char_class].get(level, {})
    
    return {}


def calculate_spell_save_dc(character: Dict[str, Any], class_data: Optional[Dict[str, Any]] = None) -> int:
    """
    D&D 5e Spell Save DC hesaplama
    8 + Proficiency Bonus + Spellcasting Ability Modifier
    """
    level = character.get("level", 1)
    abilities = character.get("abilities", {})
    char_class = character.get("class", "")
    
    prof_bonus = calculate_proficiency_bonus(level)
    
    # Spellcasting ability (genelde INT, WIS veya CHA)
    spellcasting_ability = "Intelligence"  # Default
    if char_class in ["Cleric", "Druid", "Ranger"]:
        spellcasting_ability = "Wisdom"
    elif char_class in ["Bard", "Paladin", "Sorcerer", "Warlock"]:
        spellcasting_ability = "Charisma"
    elif char_class in ["Wizard", "Artificer"]:
        spellcasting_ability = "Intelligence"
    
    ability_modifier = calculate_ability_modifier(abilities.get(spellcasting_ability, 10))
    
    return 8 + prof_bonus + ability_modifier


def calculate_spell_attack_bonus(character: Dict[str, Any], class_data: Optional[Dict[str, Any]] = None) -> int:
    """
    D&D 5e Spell Attack Bonus hesaplama
    Proficiency Bonus + Spellcasting Ability Modifier
    """
    level = character.get("level", 1)
    abilities = character.get("abilities", {})
    char_class = character.get("class", "")
    
    prof_bonus = calculate_proficiency_bonus(level)
    
    # Spellcasting ability
    spellcasting_ability = "Intelligence"  # Default
    if char_class in ["Cleric", "Druid", "Ranger"]:
        spellcasting_ability = "Wisdom"
    elif char_class in ["Bard", "Paladin", "Sorcerer", "Warlock"]:
        spellcasting_ability = "Charisma"
    elif char_class in ["Wizard", "Artificer"]:
        spellcasting_ability = "Intelligence"
    
    ability_modifier = calculate_ability_modifier(abilities.get(spellcasting_ability, 10))
    
    return prof_bonus + ability_modifier


def calculate_saving_throws(character: Dict[str, Any], class_data: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
    """
    D&D 5e Saving Throws hesaplama
    Ability Modifier + Proficiency (eğer sınıf saving throw'u ise)
    """
    level = character.get("level", 1)
    abilities = character.get("abilities", {})
    char_class = character.get("class", "")
    
    prof_bonus = calculate_proficiency_bonus(level)
    
    # Sınıf saving throw'ları
    class_saving_throws = {
        "Fighter": ["Strength", "Constitution"],
        "Rogue": ["Dexterity", "Intelligence"],
        "Wizard": ["Intelligence", "Wisdom"],
        "Cleric": ["Wisdom", "Charisma"],
        "Ranger": ["Strength", "Dexterity"],
        "Paladin": ["Wisdom", "Charisma"],
        "Sorcerer": ["Constitution", "Charisma"],
        "Warlock": ["Wisdom", "Charisma"],
        "Bard": ["Dexterity", "Charisma"],
        "Barbarian": ["Strength", "Constitution"],
        "Druid": ["Intelligence", "Wisdom"],
        "Monk": ["Strength", "Dexterity"]
    }
    
    saving_throws = {}
    proficient_saves = class_saving_throws.get(char_class, [])
    
    for ability in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
        ability_modifier = calculate_ability_modifier(abilities.get(ability, 10))
        if ability in proficient_saves:
            saving_throws[ability] = ability_modifier + prof_bonus
        else:
            saving_throws[ability] = ability_modifier
    
    return saving_throws


def calculate_passive_perception(character: Dict[str, Any]) -> int:
    """
    D&D 5e Passive Perception hesaplama
    10 + Perception modifier
    """
    abilities = character.get("abilities", {})
    wis_modifier = calculate_ability_modifier(abilities.get("Wisdom", 10))
    
    # Proficiency bonus (eğer Perception proficient ise)
    level = character.get("level", 1)
    prof_bonus = calculate_proficiency_bonus(level)
    
    # Perception skill kontrolü (basitleştirilmiş)
    skills = character.get("skills", {}).get("class_skills", [])
    perception_bonus = 0
    if "perception" in [s.lower() for s in skills]:
        perception_bonus = prof_bonus
    
    return 10 + wis_modifier + perception_bonus


# ============================================================================
# M&M Hesaplamaları
# ============================================================================

def calculate_mm_power_points(power_level: int) -> int:
    """
    M&M Power Points hesaplama
    PL × 15
    """
    try:
        pl = int(power_level)
        return pl * 15
    except (ValueError, TypeError):
        return 0


def calculate_mm_ability_modifier(ability_score: int) -> int:
    """
    M&M Ability Modifier hesaplama: (Ability - 10) / 2
    """
    return (ability_score - 10) // 2


def calculate_mm_defense_limits(power_level: int) -> Dict[str, int]:
    """
    M&M Defense Limits hesaplama
    Attack Bonus + Effect Rank ≤ PL × 2
    Defense + Toughness ≤ PL × 2
    """
    try:
        pl = int(power_level)
        max_total = pl * 2
        return {
            "attack_effect_max": max_total,
            "defense_toughness_max": max_total
        }
    except (ValueError, TypeError):
        return {
            "attack_effect_max": 0,
            "defense_toughness_max": 0
        }


# ============================================================================
# VtM Hesaplamaları
# ============================================================================

def calculate_vtm_health(character: Dict[str, Any]) -> int:
    """
    VtM Health hesaplama
    3 + Stamina
    """
    attributes = character.get("attributes", {})
    physical = attributes.get("Physical", {})
    stamina = physical.get("Stamina", 0)
    return 3 + stamina


def calculate_vtm_willpower(character: Dict[str, Any]) -> int:
    """
    VtM Willpower hesaplama
    Resolve + Composure
    """
    attributes = character.get("attributes", {})
    mental = attributes.get("Mental", {})
    social = attributes.get("Social", {})
    resolve = mental.get("Resolve", 0)
    composure = social.get("Composure", 0)
    return resolve + composure


def calculate_vtm_dice_pool(character: Dict[str, Any], attribute: str, skill: str, discipline: Optional[str] = None) -> int:
    """
    VtM Dice Pool hesaplama
    Attribute + Skill + Discipline (varsa)
    """
    attributes = character.get("attributes", {})
    skills = character.get("skills", {})
    
    # Attribute değerini bul
    attr_value = 0
    for category, attrs in attributes.items():
        if attribute in attrs:
            attr_value = attrs[attribute]
            break
    
    # Skill değerini bul
    skill_value = 0
    for category, skls in skills.items():
        if skill in skls:
            skill_value = skls[skill]
            break
    
    # Discipline bonus (varsa)
    discipline_bonus = 0
    if discipline:
        disciplines = character.get("disciplines", [])
        if discipline in disciplines:
            # Discipline seviyesi (basitleştirilmiş, varsayılan 1)
            discipline_bonus = 1
    
    return attr_value + skill_value + discipline_bonus


def calculate_vtm_hunger_dice(humanity: int) -> int:
    """
    VtM Hunger Dice hesaplama
    Humanity seviyesine göre (basitleştirilmiş)
    """
    if humanity >= 8:
        return 1
    elif humanity >= 6:
        return 2
    elif humanity >= 4:
        return 3
    elif humanity >= 2:
        return 4
    else:
        return 5


# ============================================================================
# Genel Hesaplama Fonksiyonları
# ============================================================================

def calculate_all_dnd_stats(character: Dict[str, Any], class_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Tüm D&D istatistiklerini hesapla
    """
    level = character.get("level", 1)
    abilities = character.get("abilities", {})
    
    stats = {
        "proficiency_bonus": calculate_proficiency_bonus(level),
        "ability_modifiers": {
            ability: calculate_ability_modifier(score)
            for ability, score in abilities.items()
        },
        "armor_class": calculate_armor_class(character),
        "hit_points": calculate_hit_points(character, class_data),
        "spell_slots": calculate_spell_slots(character, class_data),
        "spell_save_dc": calculate_spell_save_dc(character, class_data),
        "spell_attack_bonus": calculate_spell_attack_bonus(character, class_data),
        "saving_throws": calculate_saving_throws(character, class_data),
        "passive_perception": calculate_passive_perception(character)
    }
    
    return stats


def calculate_all_mm_stats(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tüm M&M istatistiklerini hesapla
    """
    power_level = character.get("power_level", "1")
    abilities = character.get("abilities", {})
    
    stats = {
        "power_points": calculate_mm_power_points(power_level),
        "ability_modifiers": {
            ability: calculate_mm_ability_modifier(score)
            for ability, score in abilities.items()
        },
        "defense_limits": calculate_mm_defense_limits(power_level)
    }
    
    return stats


def calculate_all_vtm_stats(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tüm VtM istatistiklerini hesapla
    """
    stats = {
        "health": calculate_vtm_health(character),
        "willpower": calculate_vtm_willpower(character),
        "hunger_dice": calculate_vtm_hunger_dice(character.get("humanity", 7))
    }
    
    return stats

