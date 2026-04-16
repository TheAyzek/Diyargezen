"""
Otomatik Hesaplama Modülü
Kural kitaplarından otomatik hesaplamalar yapar.
"""

from typing import Dict, Any, List, Optional, Tuple


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
    D&D 5e Armor Class hesaplama - İYİLEŞTİRİLDİ (Magic Item Bonuses)
    Zırh tipine göre AC hesaplar + Magic item bonusları
    """
    abilities = character.get("abilities", {})
    dex_modifier = calculate_ability_modifier(abilities.get("Dexterity", 10))

    # Zırh kontrolü
    equipment = character.get("equipment", [])
    armor = None
    for item in equipment:
        # equipment öğeleri bazen string bazen dict olabilir; dict ise kontrol et
        if isinstance(item, dict) and item.get("type") == "armor":
            armor = item
            break

    # Default base AC
    if not armor:
        base_ac = 10 + dex_modifier
    else:
        armor_name = (armor.get("name", "") or "").lower()

        # Zırh tipine göre AC hesaplama
        if ("padded" in armor_name) or ("leather" in armor_name and "studded" not in armor_name):
            base_ac = 11 + dex_modifier
        elif "studded" in armor_name:
            base_ac = 12 + dex_modifier
        elif "hide" in armor_name:
            base_ac = 12 + min(dex_modifier, 2)  # Max +2 DEX
        elif "chain shirt" in armor_name or "scale mail" in armor_name:
            base_ac = 14 + min(dex_modifier, 2)  # Max +2 DEX
        elif "breastplate" in armor_name or "half plate" in armor_name:
            base_ac = 15 + min(dex_modifier, 2)  # Max +2 DEX
        elif "ring mail" in armor_name:
            base_ac = 14  # No DEX modifier
        elif "chain mail" in armor_name or "splint" in armor_name:
            base_ac = 16  # No DEX modifier
        elif "plate" in armor_name:
            base_ac = 18  # No DEX modifier
        else:
            # Bilinmeyen zırh tipi, default
            base_ac = 10 + dex_modifier

        # Magic armor bonus - İYİLEŞTİRİLDİ (Magic Item Bonuses)
        if armor.get("attuned", False):  # Attuned magic item
            ac_bonus = extract_magic_item_ac_bonus(armor)
            base_ac += ac_bonus

    # Diğer attuned magic item'lerden AC bonusu (ring, cloak, vb.) - İYİLEŞTİRİLDİ
    magic_ac_bonus = calculate_magic_item_ac_bonus(character)
    base_ac += magic_ac_bonus

    return base_ac


def extract_magic_item_ac_bonus(item: Dict[str, Any]) -> int:
    """
    Magic item'den AC bonusunu çıkar - İYİLEŞTİRİLDİ (Magic Item Bonuses)
    
    Args:
        item: Equipment item dict
    
    Returns:
        AC bonus (0-5 arası genellikle)
    """
    if not item:
        return 0
    
    # "+1", "+2", "+3" gibi bonusları parse et
    item_name = item.get("name", "").lower()
    description = item.get("description", "").lower()
    
    import re
    
    # Pattern: "+1", "+2", "+3" gibi
    bonus_patterns = [
        r'\+(\d+)\s*(?:armor|ac|armor\s+class)',
        r'armor\s+class\s+(?:\+|\s+)(\d+)',
        r'\+(\d+)\s*$',  # Sadece "+1" gibi
    ]
    
    for pattern in bonus_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            try:
                bonus = int(match.group(1))
                # D&D 5e'de genellikle +1 ila +3 arası magic armor
                return min(bonus, 5)  # Max +5 (very rare)
            except ValueError:
                pass
    
    # Item name'de "+1", "+2" gibi varsa
    name_match = re.search(r'\+(\d+)', item_name)
    if name_match:
        try:
            bonus = int(name_match.group(1))
            return min(bonus, 5)
        except ValueError:
            pass
    
    return 0


def calculate_magic_item_ac_bonus(character: Dict[str, Any]) -> int:
    """
    Attuned magic item'lerden toplam AC bonusunu hesapla - İYİLEŞTİRİLDİ (Magic Item Bonuses)
    (Ring of Protection, Cloak of Protection, vb.)
    
    Args:
        character: Character dict
    
    Returns:
        Toplam AC bonus (genellikle +1 ila +3)
    """
    equipment = character.get("equipment", [])
    attuned_items = character.get("attuned_items", [])  # Attuned item name listesi
    
    total_bonus = 0
    
    # Attuned item'leri kontrol et
    for item in equipment:
        item_name = item.get("name", "")
        
        # Attuned mu kontrol et
        is_attuned = item.get("attuned", False) or item_name in attuned_items
        
        if not is_attuned:
            continue
        
        # AC bonus veren magic item'ler (Ring of Protection, Cloak of Protection, vb.)
        item_name_lower = item_name.lower()
        if any(keyword in item_name_lower for keyword in ["ring of protection", "cloak of protection", "bracers of defense"]):
            total_bonus += extract_magic_item_ac_bonus(item)
    
    return total_bonus


def calculate_magic_weapon_bonus(character: Dict[str, Any], weapon_name: Optional[str] = None) -> Dict[str, int]:
    """
    Magic weapon'den attack ve damage bonusunu hesapla - İYİLEŞTİRİLDİ (Magic Item Bonuses)
    
    Args:
        character: Character dict
        weapon_name: Weapon name (opsiyonel, belirli bir weapon için)
    
    Returns:
        Dict with 'attack_bonus' and 'damage_bonus'
    """
    equipment = character.get("equipment", [])
    attuned_items = character.get("attuned_items", [])
    
    bonuses = {"attack_bonus": 0, "damage_bonus": 0}
    
    # Eğer belirli bir weapon belirtilmişse sadece onu kontrol et
    if weapon_name:
        for item in equipment:
            if item.get("name") == weapon_name and item.get("type") == "weapon":
                if item.get("attuned", False) or item.get("name") in attuned_items:
                    attack_bonus = extract_magic_item_bonus(item, "attack")
                    damage_bonus = extract_magic_item_bonus(item, "damage")
                    bonuses["attack_bonus"] = attack_bonus
                    bonuses["damage_bonus"] = damage_bonus
                break
    else:
        # Equipped weapon'ı bul
        for item in equipment:
            if item.get("type") == "weapon" and item.get("equipped", False):
                if item.get("attuned", False) or item.get("name") in attuned_items:
                    bonuses["attack_bonus"] = extract_magic_item_bonus(item, "attack")
                    bonuses["damage_bonus"] = extract_magic_item_bonus(item, "damage")
                break
    
    return bonuses


def extract_magic_item_bonus(item: Dict[str, Any], bonus_type: str = "attack") -> int:
    """
    Magic item'den attack veya damage bonusunu çıkar - İYİLEŞTİRİLDİ (Magic Item Bonuses)
    
    Args:
        item: Equipment item dict
        bonus_type: "attack" veya "damage"
    
    Returns:
        Bonus değeri (0-5 arası genellikle)
    """
    if not item:
        return 0
    
    item_name = item.get("name", "").lower()
    description = item.get("description", "").lower()
    
    import re
    
    # Pattern: "+1", "+2", "+3" gibi
    if bonus_type == "attack":
        bonus_patterns = [
            r'\+(\d+)\s*(?:to\s+)?(?:attack|attack\s+rolls?)',
            r'(?:attack|attack\s+rolls?)\s+(?:\+|\s+)(\d+)',
        ]
    else:  # damage
        bonus_patterns = [
            r'\+(\d+)\s*(?:to\s+)?(?:damage|damage\s+rolls?)',
            r'(?:damage|damage\s+rolls?)\s+(?:\+|\s+)(\d+)',
        ]
    
    # Description'dan parse et
    for pattern in bonus_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            try:
                bonus = int(match.group(1))
                return min(bonus, 5)  # Max +5
            except ValueError:
                pass
    
    # Item name'de "+1", "+2" gibi varsa (hem attack hem damage için geçerli)
    name_match = re.search(r'\+(\d+)', item_name)
    if name_match:
        try:
            bonus = int(name_match.group(1))
            return min(bonus, 5)
        except ValueError:
            pass
    
    return 0


def check_attunement_limit(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attunement limit kontrolü - İYİLEŞTİRİLDİ (Attunement Tracking)
    D&D 5e'de bir karakter maksimum 3 item attune edebilir
    
    Args:
        character: Character dict
    
    Returns:
        Dict with 'current_attuned', 'max_attuned', 'can_attune_more', 'attuned_items'
    """
    equipment = character.get("equipment", [])
    attuned_items = character.get("attuned_items", [])
    
    # Attuned item'leri say
    current_attuned = 0
    attuned_item_names = []
    
    for item in equipment:
        item_name = item.get("name", "")
        if item.get("attuned", False) or item_name in attuned_items:
            current_attuned += 1
            attuned_item_names.append(item_name)
    
    max_attuned = 3  # D&D 5e standard limit
    can_attune_more = current_attuned < max_attuned
    
    return {
        "current_attuned": current_attuned,
        "max_attuned": max_attuned,
        "can_attune_more": can_attune_more,
        "attuned_items": attuned_item_names,
        "remaining_slots": max_attuned - current_attuned
    }


def can_attune_item(character: Dict[str, Any], item_name: Optional[str] = None) -> Tuple[bool, str]:
    """
    Bir item attune edilebilir mi kontrol et - İYİLEŞTİRİLDİ (Attunement Tracking)
    
    Args:
        character: Character dict
        item_name: Item name (opsiyonel)
    
    Returns:
        Tuple (can_attune: bool, reason: str)
    """
    attunement_info = check_attunement_limit(character)
    
    if not attunement_info["can_attune_more"]:
        return False, f"Maksimum attunement limitine ulaşıldı ({attunement_info['max_attuned']}/3)"
    
    # Eğer item_name belirtilmişse, item'ın zaten attuned olup olmadığını kontrol et
    if item_name:
        attuned_items = attunement_info["attuned_items"]
        if item_name in attuned_items:
            return False, f"{item_name} zaten attuned"
    
    return True, f"Attune edilebilir ({attunement_info['remaining_slots']} slot kaldı)"


def calculate_encumbrance_details(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detaylı encumbrance hesaplama - İYİLEŞTİRİLDİ (Encumbrance Details)
    Variant Encumbrance kuralları: STR × 30 lbs = Encumbered, STR × 45 lbs = Heavily Encumbered
    
    Args:
        character: Character dict
    
    Returns:
        Dict with weight, capacity, encumbered status, movement penalty
    """
    abilities = character.get("abilities", {})
    strength = abilities.get("Strength", 10)
    
    # Carrying capacity: STR × 15 lbs (normal), STR × 30 lbs (encumbered), STR × 45 lbs (heavily encumbered)
    base_capacity = strength * 15  # Normal carrying capacity
    encumbered_threshold = strength * 30  # Encumbered threshold
    heavily_encumbered_threshold = strength * 45  # Heavily encumbered threshold
    
    # Equipment weight topla
    equipment = character.get("equipment", [])
    total_weight = 0.0
    
    import re
    
    for item in equipment:
        weight = item.get("weight", 0)
        quantity = item.get("quantity", 1)
        
        # Weight string veya number olabilir
        if isinstance(weight, str):
            # "5 lbs" gibi string'den sayıyı çıkar
            weight_match = re.search(r'(\d+(?:\.\d+)?)', weight)
            if weight_match:
                try:
                    weight = float(weight_match.group(1))
                except ValueError:
                    weight = 0.0
            else:
                weight = 0.0
        elif isinstance(weight, (int, float)):
            weight = float(weight)
        else:
            weight = 0.0
        
        total_weight += weight * quantity
    
    # Encumbrance status
    encumbrance_status = "unencumbered"
    movement_penalty = 0
    
    if total_weight >= heavily_encumbered_threshold:
        encumbrance_status = "heavily_encumbered"
        movement_penalty = -20  # -20 ft movement
    elif total_weight >= encumbered_threshold:
        encumbrance_status = "encumbered"
        movement_penalty = -10  # -10 ft movement
    elif total_weight >= base_capacity:
        encumbrance_status = "at_capacity"
        movement_penalty = 0  # No penalty but at limit
    else:
        encumbrance_status = "unencumbered"
        movement_penalty = 0
    
    return {
        "total_weight": total_weight,
        "base_capacity": base_capacity,
        "encumbered_threshold": encumbered_threshold,
        "heavily_encumbered_threshold": heavily_encumbered_threshold,
        "encumbrance_status": encumbrance_status,
        "movement_penalty": movement_penalty,
        "remaining_capacity": base_capacity - total_weight,
        "percentage_used": (total_weight / base_capacity * 100) if base_capacity > 0 else 0
    }


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
        hit_dice_value = class_info.get("hit_die", "d8")  # "d8", "d10", "d12" gibi
        
        # Hit die string'ini integer'a çevir - DÜZELTİLDİ (HP Hesaplama)
        if isinstance(hit_dice_value, str):
            # "d8", "d10", "d12" formatını parse et
            hit_dice_str = hit_dice_value.lower().replace("d", "")
            try:
                hit_dice = int(hit_dice_str)
            except ValueError:
                hit_dice = 8  # Default
        elif isinstance(hit_dice_value, int):
            hit_dice = hit_dice_value
        else:
            hit_dice = 8  # Default
    
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
    
    # Spellcasting sınıfları ve slot tabloları - DÜZELTİLDİ (tüm class'lar için)
    # Full caster progression: Wizard, Sorcerer, Bard, Cleric, Druid
    # Half caster progression: Paladin, Ranger
    # 1/3 caster: Eldritch Knight, Arcane Trickster
    
    full_caster_slots = {
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
    
    half_caster_slots = {
        1: {}, 2: {1: 2}, 3: {1: 3}, 4: {}, 5: {1: 4, 2: 2}, 6: {}, 7: {1: 4, 2: 3}, 8: {}, 9: {1: 4, 2: 3, 3: 2},
        10: {}, 11: {1: 4, 2: 3, 3: 3}, 12: {}, 13: {1: 4, 2: 3, 3: 3, 4: 1}, 14: {}, 15: {1: 4, 2: 3, 3: 3, 4: 2},
        16: {}, 17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 18: {}, 19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}, 20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}
    }
    
    spell_slots_table = {
        # Full casters (Wizard, Sorcerer, Bard, Cleric, Druid)
        "Wizard": full_caster_slots,
        "Sorcerer": full_caster_slots,
        "Bard": full_caster_slots,
        "Cleric": full_caster_slots,
        "Druid": full_caster_slots,
        # Half casters (Paladin, Ranger)
        "Paladin": half_caster_slots,
        "Ranger": half_caster_slots,
        # Artificer (unique progression)
        "Artificer": {
            1: {1: 2}, 2: {1: 2}, 3: {1: 3}, 4: {}, 5: {1: 3, 2: 2}, 6: {}, 7: {1: 4, 2: 2},
            8: {}, 9: {1: 4, 2: 3}, 10: {}, 11: {1: 4, 2: 3, 3: 2}, 12: {}, 13: {1: 4, 2: 3, 3: 3},
            14: {}, 15: {1: 4, 2: 3, 3: 3, 4: 1}, 16: {}, 17: {1: 4, 2: 3, 3: 3, 4: 2}, 18: {},
            19: {1: 4, 2: 3, 3: 3, 4: 3}, 20: {1: 4, 2: 3, 3: 3, 4: 3}
        },
        # Warlock (unique progression - Pact Magic)
        "Warlock": {
            1: {1: 1}, 2: {1: 2}, 3: {2: 2}, 4: {2: 2}, 5: {3: 2}, 6: {3: 2}, 7: {4: 2}, 8: {4: 2},
            9: {5: 2}, 10: {5: 2}, 11: {5: 3}, 12: {5: 3}, 13: {5: 3}, 14: {5: 3}, 15: {5: 3},
            16: {5: 3}, 17: {5: 4}, 18: {5: 4}, 19: {5: 4}, 20: {5: 4}
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


def get_spellcasting_ability(char_class: str) -> str:
    """Spellcasting ability'yi döndür"""
    if char_class in ["Cleric", "Druid", "Ranger"]:
        return "Wisdom"
    elif char_class in ["Bard", "Paladin", "Sorcerer", "Warlock"]:
        return "Charisma"
    elif char_class in ["Wizard", "Artificer"]:
        return "Intelligence"
    return "Intelligence"  # Default


def calculate_spell_upcast_damage(spell_name: str, base_level: int, cast_level: int, spell_data: Optional[Dict[str, Any]] = None, dnd_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    D&D 5e Spell Upcasting damage hesaplama
    
    Args:
        spell_name: Spell ismi
        base_level: Spell'in base level'i
        cast_level: Hangi level slot ile cast ediliyor
        spell_data: Spell verisi (opsiyonel, dnd_data'dan da alınabilir)
        dnd_data: D&D verisi (spell_data yoksa kullanılır)
    
    Returns:
        Upcast edilmiş spell bilgisi (damage, description, vb.) veya None
    """
    if cast_level <= base_level:
        return None  # Upcast değil, normal cast
    
    # Spell verisini al
    if not spell_data and dnd_data:
        spells = dnd_data.get('spells', {})
        spell_data = spells.get(spell_name, {})
    
    if not spell_data:
        return None
    
    description = spell_data.get('description', '')
    base_damage = spell_data.get('damage', '')
    
    # Upcast bilgisi description'da olabilir
    # Örnek: "At Higher Levels: For each slot level above 1st, you create one additional dart..."
    # veya "At Higher Levels. When you cast this spell using a spell slot of 3rd level or higher..."
    
    import re
    
    # Upcast damage pattern'lerini ara
    # Pattern 1: "For each slot level above X, the damage increases by Y dice"
    # Pattern 2: "When you cast this spell using a spell slot of Xth level or higher, the damage increases..."
    # Pattern 3: "At Higher Levels: ..."
    
    upcast_info = {
        "base_level": base_level,
        "cast_level": cast_level,
        "base_damage": base_damage,
        "upcast_damage": base_damage,  # Default olarak base damage
        "additional_dice": 0,
        "additional_damage_per_level": 0
    }
    
    # Upcast description'ı parse et
    higher_level_patterns = [
        r'At\s+Higher\s+Levels[:\s]+([^.]+)',
        r'at\s+higher\s+levels[:\s]+([^.]+)',
        r'When\s+you\s+cast\s+this\s+spell\s+using\s+a\s+spell\s+slot\s+of\s+(\d+)(?:st|nd|rd|th)\s+level\s+or\s+higher[^.]*',
    ]
    
    upcast_description = None
    for pattern in higher_level_patterns:
        match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
        if match:
            upcast_description = match.group(1) if match.lastindex >= 1 else match.group(0)
            break
    
    if upcast_description:
        # Damage artışını parse et
        # Örnek: "For each slot level above 1st, the damage increases by 1d4" -> +1d4 per level
        # Örnek: "For each slot level above 2nd, you create one additional dart" -> +1 dart (damage değil, count)
        
        dice_patterns = [
            r'(\d+)d(\d+)\s*(?:additional|extra|more)',
            r'increases?\s+by\s+(\d+)d(\d+)',
            r'(\d+)d(\d+)\s+for\s+each\s+slot',
            r'(\d+)d(\d+)\s+per\s+level',
        ]
        
        for pattern in dice_patterns:
            match = re.search(pattern, upcast_description, re.IGNORECASE)
            if match:
                num_dice = int(match.group(1))
                dice_size = int(match.group(2))
                
                level_diff = cast_level - base_level
                additional_dice = num_dice * level_diff
                upcast_info["additional_dice"] = additional_dice
                upcast_info["additional_damage_per_level"] = f"{num_dice}d{dice_size}"
                break
        
        # Fixed damage artışı (örn: "+2 damage per level")
        fixed_patterns = [
            r'increases?\s+by\s+(\d+)',
            r'\+(\d+)\s+damage',
        ]
        
        for pattern in fixed_patterns:
            match = re.search(pattern, upcast_description, re.IGNORECASE)
            if match:
                fixed_damage = int(match.group(1))
                level_diff = cast_level - base_level
                upcast_info["additional_damage_per_level"] = fixed_damage
                upcast_info["total_additional_damage"] = fixed_damage * level_diff
                break
    
    upcast_info["upcast_description"] = upcast_description if upcast_description else None
    upcast_info["description"] = description
    
    return upcast_info


def is_ritual_spell(spell_name: str, spell_data: Optional[Dict[str, Any]] = None, dnd_data: Optional[Dict[str, Any]] = None) -> bool:
    """
    Spell'in ritual olup olmadığını kontrol et - DÜZELTİLDİ (Ritual Detection Fix)
    
    Args:
        spell_name: Spell ismi
        spell_data: Spell verisi (opsiyonel)
        dnd_data: D&D verisi (spell_data yoksa kullanılır)
    
    Returns:
        True if ritual, False otherwise
    """
    if not spell_data and dnd_data:
        spells = dnd_data.get('spells', {})
        spell_data = spells.get(spell_name, {})
    
    if not spell_data:
        return False
    
    # D&D 5e bilinen ritual spell listesi - DÜZELTİLDİ (Veri eksikliği için)
    known_ritual_spells = {
        # 1st Level
        "Alarm", "Comprehend Languages", "Detect Magic", "Detect Poison and Disease",
        "Find Familiar", "Identify", "Illusory Script", "Purify Food and Drink",
        "Speak with Animals", "Tenser's Floating Disk", "Unseen Servant",
        # 2nd Level
        "Animal Messenger", "Augury", "Beast Sense", "Gentle Repose", "Locate Animals or Plants",
        "Locate Object", "Magic Mouth", "Silence", "Skywrite",
        # 3rd Level
        "Feign Death", "Leomund's Tiny Hut", "Meld into Stone", "Water Breathing", "Water Walk",
        # 4th Level
        "Commune", "Commune with Nature", "Control Water", "Divination", "Locate Creature",
        # 5th Level
        "Contact Other Plane", "Rary's Telepathic Bond",
        # 6th Level
        "Forbiddance", "Instant Summons",
        # 7th Level
        "Mordenkainen's Magnificent Mansion",
        # 8th Level
        "Awaken", "Drawmij's Instant Summons",
        # 9th Level
        None  # 9th level ritual spell yok
    }
    
    # Bilinen ritual spell listesinde var mı kontrol et
    if spell_name in known_ritual_spells:
        return True
    
    # Ritual flag'i varsa kullan (ancak known listesi daha öncelikli)
    if 'ritual' in spell_data:
        ritual_flag = spell_data.get('ritual', False)
        if isinstance(ritual_flag, bool):
            # Eğer False ise ama known listesinde yoksa, False döndür
            # Eğer True ise, True döndür
            if ritual_flag:
                return True
        elif isinstance(ritual_flag, str):
            if ritual_flag.lower() in ['true', 'yes', '1']:
                return True
    
    # Casting time'da "ritual" geçiyorsa veya components'te "R" varsa
    casting_time = spell_data.get('casting_time', '')
    if casting_time and 'ritual' in str(casting_time).lower():
        return True
    
    components = spell_data.get('components', '')
    if components and ('R' in str(components) or 'ritual' in str(components).lower()):
        return True
    
    # Description'da "ritual" geçiyorsa (daha geniş arama) - DÜZELTİLDİ
    description = spell_data.get('description', '')
    if description:
        description_lower = description.lower()
        # "ritual" kelimesi geçiyorsa ve "can be cast as a ritual" veya benzeri pattern varsa
        if 'ritual' in description_lower:
            ritual_patterns = [
                'can be cast as a ritual',
                'cast as a ritual',
                'ritual spell',
                'ritual version',
            ]
            for pattern in ritual_patterns:
                if pattern in description_lower:
                    return True
    
    return False


def is_concentration_spell(spell_name: str, spell_data: Optional[Dict[str, Any]] = None, dnd_data: Optional[Dict[str, Any]] = None) -> bool:
    """
    Spell'in concentration olup olmadığını kontrol et
    
    Args:
        spell_name: Spell ismi
        spell_data: Spell verisi (opsiyonel)
        dnd_data: D&D verisi (spell_data yoksa kullanılır)
    
    Returns:
        True if concentration, False otherwise
    """
    if spell_data:
        # Concentration flag'i varsa kullan
        if 'concentration' in spell_data:
            return bool(spell_data.get('concentration', False))
        
        # Duration'da "concentration" geçiyorsa
        duration = spell_data.get('duration', '')
        if duration and 'concentration' in str(duration).lower():
            return True
    
    # dnd_data'dan al
    if dnd_data:
        spells = dnd_data.get('spells', {})
        spell_data = spells.get(spell_name, {})
        if spell_data:
            if 'concentration' in spell_data:
                return bool(spell_data.get('concentration', False))
            duration = spell_data.get('duration', '')
            if duration and 'concentration' in str(duration).lower():
                return True
    
    return False


def extract_material_components(spell_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Spell'in material component'lerini çıkar
    
    Args:
        spell_data: Spell verisi
    
    Returns:
        Material component bilgisi (component name, cost, consumed, vb.) veya None
    """
    if not spell_data:
        return None
    
    components = spell_data.get('components', '')
    if not components or 'M' not in str(components):
        return None
    
    import re
    
    # Material component açıklamasını çıkar (parantez içinde)
    # Örnek: "M (a pearl worth at least 100 gp and an owl feather)"
    # Örnek: "M (10 gp worth of charcoal, incense, and herbs that must be consumed by fire in a brass brazier)"
    
    material_info = {
        "has_material": True,
        "component": None,
        "cost": None,
        "consumed": False
    }
    
    # Pattern: M (description)
    match = re.search(r'M\s*\(([^)]+)\)', str(components), re.IGNORECASE)
    if match:
        material_desc = match.group(1).strip()
        material_info["component"] = material_desc
        
        # Cost parse et (örn: "100 gp", "10 gp")
        cost_match = re.search(r'(\d+)\s*gp', material_desc, re.IGNORECASE)
        if cost_match:
            material_info["cost"] = int(cost_match.group(1))
        
        # Consumed kontrolü (örn: "consumed", "must be consumed")
        if 'consumed' in material_desc.lower() or 'must be consumed' in material_desc.lower():
            material_info["consumed"] = True
    
    return material_info if material_info["component"] else None


def is_prepared_caster(char_class: str) -> bool:
    """Sınıf prepared caster mı kontrol et"""
    prepared_casters = ["Wizard", "Cleric", "Druid", "Paladin", "Ranger", "Artificer"]
    return char_class in prepared_casters


def is_known_caster(char_class: str) -> bool:
    """Sınıf known caster mı kontrol et"""
    known_casters = ["Sorcerer", "Bard", "Warlock", "Ranger"]
    return char_class in known_casters


def calculate_spells_prepared(character: Dict[str, Any], class_data: Optional[Dict[str, Any]] = None) -> Optional[int]:
    """
    D&D 5e Prepared Spells hesaplama
    
    Prepared Casters (Wizard, Cleric, Druid, Paladin, Ranger, Artificer):
    - Wizard: Level + INT modifier (spellbook'tan hazırlanır)
    - Cleric/Druid/Paladin: Level + spellcasting modifier (tüm listesinden)
    - Ranger: Spells known (prepared değil)
    - Artificer: Level + INT modifier
    
    Known Casters (Sorcerer, Bard, Warlock):
    - None döndür (hazırlanmaz, bilinen spell'ler kullanılır)
    """
    char_class = character.get("class", "")
    level = character.get("level", 1)
    abilities = character.get("abilities", {})
    
    # Known casters hazırlanmaz
    if char_class in ["Sorcerer", "Bard", "Warlock"]:
        return None  # Spells known sistemi kullanılır
    
    # Ranger spells known kullanır, prepared değil
    if char_class == "Ranger":
        return None  # Spells known table'a bakılmalı
    
    # Prepared casters
    if is_prepared_caster(char_class):
        spellcasting_ability = get_spellcasting_ability(char_class)
        ability_modifier = calculate_ability_modifier(abilities.get(spellcasting_ability, 10))
        spells_prepared = level + ability_modifier
        
        # Minimum 1 (modifier negatif olsa bile en az 1 spell hazırlanabilir)
        return max(1, spells_prepared)
    
    return None


def calculate_spells_known(character: Dict[str, Any], class_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, int]]:
    """
    D&D 5e Spells Known hesaplama
    
    Known Casters için bilinen spell sayılarını döndürür:
    - Sorcerer: Level'a göre belirli sayıda spell bilir
    - Bard: Level'a göre belirli sayıda spell bilir
    - Warlock: Patron ve level'a göre
    - Ranger: Level'a göre belirli sayıda spell bilir (prepared değil)
    """
    char_class = character.get("class", "")
    level = character.get("level", 1)
    
    # Sorcerer spells known table
    sorcerer_spells_known = {
        1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11,
        11: 12, 12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 17: 15, 18: 15, 19: 15, 20: 15
    }
    
    # Bard spells known table
    bard_spells_known = {
        1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11, 9: 12, 10: 14,
        11: 15, 12: 15, 13: 16, 14: 18, 15: 19, 16: 19, 17: 20, 18: 22, 19: 22, 20: 22
    }
    
    # Warlock spells known (base, patron ekleyebilir)
    warlock_spells_known = {
        1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 10,
        11: 11, 12: 11, 13: 12, 14: 12, 15: 13, 16: 13, 17: 14, 18: 14, 19: 15, 20: 15
    }
    
    # Ranger spells known
    ranger_spells_known = {
        1: 0, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5, 8: 5, 9: 6, 10: 6,
        11: 7, 12: 7, 13: 8, 14: 8, 15: 9, 16: 9, 17: 10, 18: 10, 19: 11, 20: 11
    }
    
    if char_class == "Sorcerer":
        return {"total": sorcerer_spells_known.get(level, 2)}
    elif char_class == "Bard":
        return {"total": bard_spells_known.get(level, 4)}
    elif char_class == "Warlock":
        return {"total": warlock_spells_known.get(level, 2)}
    elif char_class == "Ranger":
        return {"total": ranger_spells_known.get(level, 0)}
    
    return None  # Prepared caster veya spellcaster değil


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


def calculate_skill_modifier(character: Dict[str, Any], skill_name: str, class_data: Optional[Dict[str, Any]] = None) -> int:
    """
    D&D 5e Skill Modifier hesaplama - İYİLEŞTİRİLDİ (Skill Check Modifiers)
    
    Skill modifier = Ability Modifier + Proficiency Bonus (eğer proficient ise)
    - Expertise: Double proficiency bonus
    - Jack of All Trades (Bard): Half proficiency bonus (rounded down) for non-proficient skills
    
    Args:
        character: Karakter verisi
        skill_name: Skill adı (örn: "Athletics", "Perception")
        class_data: Class data (opsiyonel)
    
    Returns:
        Skill modifier (integer)
    """
    level = character.get("level", 1)
    abilities = character.get("abilities", {})
    char_class = character.get("class", "")
    
    # Skill-to-ability mapping
    skill_abilities_map = {
        "Athletics": "Strength",
        "Acrobatics": "Dexterity", "Sleight of Hand": "Dexterity", "Stealth": "Dexterity",
        "Arcana": "Intelligence", "History": "Intelligence", "Investigation": "Intelligence",
        "Nature": "Intelligence", "Religion": "Intelligence",
        "Animal Handling": "Wisdom", "Insight": "Wisdom", "Medicine": "Wisdom",
        "Perception": "Wisdom", "Survival": "Wisdom",
        "Deception": "Charisma", "Intimidation": "Charisma", "Performance": "Charisma",
        "Persuasion": "Charisma"
    }
    
    # Skill'in ability'sini bul
    ability_name = skill_abilities_map.get(skill_name, "Strength")
    ability_score = abilities.get(ability_name, 10)
    ability_modifier = calculate_ability_modifier(ability_score)
    
    # Proficiency bonus
    prof_bonus = calculate_proficiency_bonus(level)
    
    # Proficient skills kontrolü
    skills = character.get("skills", {})
    proficient_skills = []
    expertise_skills = []
    
    # Skills data yapısı değişken olabilir
    if isinstance(skills, dict):
        # Eğer skills bir dict ise (proficiencies listesi içinde olabilir)
        proficient_skills = skills.get("proficiencies", []) or skills.get("class_skills", [])
        expertise_skills = skills.get("expertise", [])
    elif isinstance(skills, list):
        proficient_skills = skills
    
    # Skill adını normalize et (büyük/küçük harf farkı)
    skill_name_normalized = skill_name.title()
    proficient_skills_normalized = [s.title() for s in proficient_skills]
    expertise_skills_normalized = [s.title() for s in expertise_skills]
    
    is_proficient = skill_name_normalized in proficient_skills_normalized
    is_expertise = skill_name_normalized in expertise_skills_normalized
    
    # Skill modifier hesaplama
    skill_modifier = ability_modifier
    
    if is_proficient:
        if is_expertise:
            # Expertise: Double proficiency bonus
            skill_modifier += prof_bonus * 2
        else:
            # Normal proficiency
            skill_modifier += prof_bonus
    else:
        # Jack of All Trades (Bard 2nd level): Half proficiency bonus (rounded down)
        if char_class == "Bard" and level >= 2:
            jack_bonus = prof_bonus // 2  # Half proficiency, rounded down
            skill_modifier += jack_bonus
    
    return skill_modifier


def calculate_jump_distance(character: Dict[str, Any]) -> Dict[str, int]:
    """
    D&D 5e Jump Distance hesaplama - İYİLEŞTİRİLDİ (Jump Distance)
    
    Long Jump:
    - Running start (10 ft minimum): STR feet
    - Standing: STR / 2 feet
    
    High Jump:
    - Running start (10 ft minimum): 3 + STR modifier feet
    - Standing: 3 + STR modifier feet (minimum 0)
    
    Args:
        character: Karakter verisi
    
    Returns:
        Dict with 'long_jump_running', 'long_jump_standing', 'high_jump_running', 'high_jump_standing'
    """
    abilities = character.get("abilities", {})
    strength = abilities.get("Strength", 10)
    str_modifier = calculate_ability_modifier(strength)
    
    # Long Jump
    long_jump_running = max(10, strength)  # Minimum 10 ft with running start
    long_jump_standing = strength // 2  # Standing: half of STR
    
    # High Jump
    high_jump_running = max(10, 3 + str_modifier)  # Minimum 10 ft with running start
    high_jump_standing = max(0, 3 + str_modifier)  # Standing: 3 + STR modifier (minimum 0)
    
    return {
        "long_jump_running": long_jump_running,
        "long_jump_standing": long_jump_standing,
        "high_jump_running": high_jump_running,
        "high_jump_standing": high_jump_standing
    }


def calculate_initiative(character: Dict[str, Any]) -> int:
    """
    D&D 5e Initiative hesaplama
    Initiative = DEX modifier (proficiency bonus eklenmez)
    """
    abilities = character.get("abilities", {})
    dex_score = abilities.get("Dexterity", 10)
    dex_modifier = calculate_ability_modifier(dex_score)
    return dex_modifier


def calculate_movement_speed(character: Dict[str, Any], race_data: Optional[Dict[str, Any]] = None, class_data: Optional[Dict[str, Any]] = None) -> int:
    """
    D&D 5e Movement Speed hesaplama - DÜZELTİLDİ (Movement Speed Calculation)
    Base speed: Race'den gelir (genellikle 30 ft, Dwarf 25 ft, Wood Elf 35 ft)
    Class modifiers: Monk (+10 ft at level 2), Barbarian (+10 ft at level 5), vb.
    Armor modifiers: Heavy armor speed reduction
    Encumbrance modifiers: Variant encumbrance rules (STR × 30 lbs = Encumbered, STR × 45 lbs = Heavily Encumbered)
    """
    # Base speed: Race'den al (default: 30 ft)
    base_speed = 30
    
    if race_data:
        race_speed = race_data.get("speed")
        if race_speed:
            base_speed = race_speed
    elif character.get("race"):
        # Race data yoksa, character'dan al (eğer race'de speed varsa)
        # Şimdilik default kullan, daha sonra data loader'dan alınabilir
        pass
    
    # Class modifiers
    level = character.get("level", 1)
    char_class = character.get("class", "")
    
    if class_data and char_class:
        class_info = class_data.get("classes", {}).get(char_class, {})
        class_features = class_info.get("features", {})
        
        # Monk: Unarmored Movement - Level 2'de +10 ft, level 6'da +15 ft, level 10'da +20 ft, level 14'da +25 ft
        if char_class == "Monk":
            if level >= 14:
                base_speed += 25
            elif level >= 10:
                base_speed += 20
            elif level >= 6:
                base_speed += 15
            elif level >= 2:
                base_speed += 10
        
        # Barbarian: Fast Movement - Level 5'te +10 ft
        elif char_class == "Barbarian":
            if level >= 5:
                base_speed += 10
    
    # Encumbrance modifiers - İYİLEŞTİRİLDİ (Encumbrance Details)
    encumbrance_info = calculate_encumbrance_details(character)
    movement_penalty = encumbrance_info.get("movement_penalty", 0)
    base_speed += movement_penalty  # Encumbrance penalty (-10 veya -20 ft)
    
    # Armor modifiers (heavy armor -10 ft speed reduction)
    equipment = character.get("equipment", [])
    for item in equipment:
        if item.get("type") == "armor":
            armor_type = item.get("armor_type", "").lower()
            if armor_type == "heavy":
                # Heavy armor: -10 ft speed (eğer strength requirement karşılanmamışsa)
                strength_req = item.get("strength_requirement", 0)
                strength = character.get("abilities", {}).get("Strength", 10)
                
                if strength < strength_req:
                    base_speed -= 10
                    # Minimum 5 ft
                    if base_speed < 5:
                        base_speed = 5
                break
    
    # Encumbrance modifiers (Variant Encumbrance Rule) - DÜZELTİLDİ (Encumbrance System)
    abilities = character.get("abilities", {})
    strength = abilities.get("Strength", 10)
    
    # Total equipment weight hesapla
    total_weight = 0
    for item in equipment:
        weight = item.get("weight", 0)
        quantity = item.get("quantity", 1)
        # Weight sayısal değilse (örn: "5 lb" string), parse et
        if isinstance(weight, str):
            try:
                # "5 lb", "5lbs", "5" gibi formatları parse et
                weight_str = weight.lower().replace("lb", "").replace("lbs", "").strip()
                weight = float(weight_str) if weight_str else 0
            except (ValueError, AttributeError):
                weight = 0
        total_weight += weight * quantity
    
    # Encumbrance thresholds
    carrying_capacity = strength * 15  # Base carrying capacity
    encumbered_threshold = strength * 30  # Encumbered: -10 ft speed
    heavily_encumbered_threshold = strength * 45  # Heavily Encumbered: -20 ft speed
    
    # Encumbrance penalties
    if total_weight >= heavily_encumbered_threshold:
        base_speed -= 20  # Heavily Encumbered: -20 ft
    elif total_weight >= encumbered_threshold:
        base_speed -= 10  # Encumbered: -10 ft
    
    # Feat modifiers - DÜZELTİLDİ (Speed Modifiers - Feats)
    feats = character.get("feats", [])
    if isinstance(feats, list):
        for feat_name in feats:
            feat_lower = feat_name.lower() if isinstance(feat_name, str) else ""
            
            # Mobile feat: +10 ft speed
            if "mobile" in feat_lower:
                base_speed += 10
            
            # Diğer speed modifier feat'leri buraya eklenebilir
            # Örn: Fleet of Foot (various sources)
    
    # Spell modifiers - DÜZELTİLDİ (Speed Modifiers - Spells)
    # Not: Active spells takibi için character data'da "active_spells" veya 
    # "concentrating_spells" field'ı olması gerekir. Eğer bu field'lar yoksa,
    # spell modifier'ları uygulanmaz (sadece known spells aktif değildir).
    
    active_spells = character.get("active_spells", [])  # Aktif spell'ler (Longstrider, Haste, vb.)
    concentrating_spells = character.get("concentrating_spells", [])  # Concentration spell'ler (Haste, vb.)
    
    # Aktif spell'leri birleştir
    if active_spells or concentrating_spells:
        all_active_spells = []
        if active_spells:
            all_active_spells.extend(active_spells)
        if concentrating_spells:
            all_active_spells.extend(concentrating_spells)
        
        # Unique spell names (duplicate'leri temizle)
        active_spell_names = list(set([s.lower() if isinstance(s, str) else "" for s in all_active_spells]))
        
        for spell_name in active_spell_names:
            # Longstrider: +10 ft speed (1 hour, no concentration)
            if "longstrider" in spell_name:
                base_speed += 10
            
            # Haste: Speed doubled (1 minute, concentration)
            elif "haste" in spell_name:
                base_speed = int(base_speed * 2)
            
            # Diğer speed modifier spell'leri buraya eklenebilir
            # Örn: Expeditious Retreat (bonus action dash, speed değil ama hareket bonusu)
    
    # Minimum 5 ft
    if base_speed < 5:
        base_speed = 5
    
    return base_speed


def calculate_hit_dice_display(character: Dict[str, Any], class_data: Optional[Dict[str, Any]] = None) -> str:
    """
    D&D 5e Hit Dice gösterimi - DÜZELTİLDİ (Hit Dice Display)
    Format: "Level × Hit Die Type" (örn: "5 × d10")
    """
    level = character.get("level", 1)
    char_class = character.get("class", "")
    
    # Default hit die: d8
    hit_die = "d8"
    
    if class_data and char_class:
        class_info = class_data.get("classes", {}).get(char_class, {})
        hit_die = class_info.get("hit_die", "d8")
    elif character.get("hit_die"):
        # Character'da direkt hit_die varsa kullan
        hit_die = character.get("hit_die")
    else:
        # Class data yoksa, default class hit dice'leri
        class_hit_dice = {
            "Barbarian": "d12",
            "Fighter": "d10", "Paladin": "d10", "Ranger": "d10",
            "Artificer": "d8", "Bard": "d8", "Cleric": "d8", "Druid": "d8",
            "Monk": "d8", "Rogue": "d8", "Warlock": "d8",
            "Sorcerer": "d6", "Wizard": "d6"
        }
        hit_die = class_hit_dice.get(char_class, "d8")
    
    # Hit die formatını düzelt (eğer sadece sayıysa "d" ekle)
    if isinstance(hit_die, int):
        hit_die = f"d{hit_die}"
    elif isinstance(hit_die, str) and not hit_die.startswith("d") and hit_die.isdigit():
        hit_die = f"d{hit_die}"
    
    # Format: "Level × Hit Die Type"
    return f"{level} × {hit_die}"


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

def calculate_all_dnd_stats(character: Dict[str, Any], class_data: Optional[Dict[str, Any]] = None, race_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Tum D&D istatistiklerini hesapla - IYILESTIRILDI (v3)
    Eklenenler: skills (expertise, jack of all trades), carrying_capacity, encumbrance
    Yeni: Multiclass destegi (spell slots, hit dice, proficiency bonus)
    """
    level = character.get("level", 1)
    abilities = character.get("abilities", {})
    is_multiclass = character.get("is_multiclass", False)
    class_levels = character.get("class_levels", {})

    # Proficiency bonus her zaman TOPLAM seviyeye gore
    proficiency_bonus = calculate_proficiency_bonus(level)

    # Multiclass spell slots
    if is_multiclass and class_levels:
        try:
            from utils.multiclass import calculate_multiclass_spell_slots, calculate_multiclass_hit_dice
            subclasses = character.get("subclasses", {})
            spell_slots = calculate_multiclass_spell_slots(class_levels, subclasses)
            hit_dice_display = calculate_multiclass_hit_dice(class_levels)
        except ImportError:
            spell_slots = calculate_spell_slots(character, class_data)
            hit_dice_display = calculate_hit_dice_display(character, class_data)
    else:
        spell_slots = calculate_spell_slots(character, class_data)
        hit_dice_display = calculate_hit_dice_display(character, class_data)
    
    stats = {
        "proficiency_bonus": proficiency_bonus,
        "ability_modifiers": {
            ability: calculate_ability_modifier(score)
            for ability, score in abilities.items()
        },
        "armor_class": calculate_armor_class(character),
        "hit_points": calculate_hit_points(character, class_data),
        "spell_slots": spell_slots,
        "spell_save_dc": calculate_spell_save_dc(character, class_data),
        "spell_attack_bonus": calculate_spell_attack_bonus(character, class_data),
        "saving_throws": calculate_saving_throws(character, class_data),
        "passive_perception": calculate_passive_perception(character),
        "initiative": calculate_initiative(character),
        "movement_speed": calculate_movement_speed(character, race_data, class_data),
        "hit_dice": hit_dice_display,
        "jump_distance": calculate_jump_distance(character),
        "encumbrance": calculate_encumbrance_details(character),
    }

    # Multiclass bilgilerini koru
    if is_multiclass:
        stats["is_multiclass"] = True
        stats["class_levels"] = class_levels
        class_parts = [f"{c} {l}" for c, l in class_levels.items()]
        stats["class_display"] = " / ".join(class_parts)

    # Carrying capacity
    str_score = abilities.get("Strength", 10)
    stats["carrying_capacity"] = str_score * 15
    stats["push_drag_lift"] = str_score * 30

    # All skills hesaplama (expertise ve jack of all trades dahil)
    all_skill_names = [
        "Athletics",
        "Acrobatics", "Sleight of Hand", "Stealth",
        "Arcana", "History", "Investigation", "Nature", "Religion",
        "Animal Handling", "Insight", "Medicine", "Perception", "Survival",
        "Deception", "Intimidation", "Performance", "Persuasion"
    ]
    skills = {}
    for skill_name in all_skill_names:
        skills[skill_name] = calculate_skill_modifier(character, skill_name, class_data)
    stats["skills"] = skills

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


# ============================================================================
# D&D 5e Spell Sistemi İyileştirmeleri
# ============================================================================

def calculate_spell_upcasting(spell_data: Dict[str, Any], cast_slot_level: int) -> Dict[str, Any]:
    """
    Spell Upcasting hesaplama
    Daha yüksek level slot ile cast edildiğinde etkilerin nasıl değişeceğini hesapla
    
    Args:
        spell_data: Spell bilgileri (level, description, vb)
        cast_slot_level: Kullanılan spell slot'ı seviyesi
    
    Returns:
        Upcasting ile güncellenmiş spell etkileri
    """
    spell_level = spell_data.get("level", 0)
    
    if cast_slot_level <= spell_level:
        # Upcast edilmiyor
        return spell_data
    
    levels_upcasted = cast_slot_level - spell_level
    
    result = dict(spell_data)
    result["actual_cast_level"] = cast_slot_level
    result["upcasted_levels"] = levels_upcasted
    
    # Scaling description ekle
    if "scaling" in spell_data:
        scaling_desc = spell_data["scaling"]
        result["scaling_effect"] = f"Scaling ({levels_upcasted}x): {scaling_desc}"
    else:
        result["scaling_effect"] = f"Spell upcasted by {levels_upcasted} level(s)"
    
    return result


def track_spell_concentration(character: Dict[str, Any], new_spell: str) -> Dict[str, Any]:
    """
    Concentration tracking - Yeni bir spell cast edildiğinde kontrol et
    
    Args:
        character: Character data
        new_spell: Cast edilecek spell ismi
    
    Returns:
        Concentration durumu ve uyarı bilgileri
    """
    current_spells = character.get("active_spells", {})
    concentration_required = current_spells.get("requires_concentration", False)
    current_concentration_spell = current_spells.get("concentration_spell", None)
    
    result = {
        "can_cast": True,
        "warning": None,
        "breaks_current_concentration": False
    }
    
    # Mevcut concentration spell varsa ve yeni spell concentration gerektiriyorsa
    if concentration_required and current_concentration_spell:
        result["breaks_current_concentration"] = True
        result["warning"] = f"Casting {new_spell} will break concentration on {current_concentration_spell}"
    
    return result


def check_ritual_casting(character: Dict[str, Any], spell_data: Dict[str, Any]) -> bool:
    """
    Ritual Casting kontrolü - Spell ritual olarak cast edilebilir mi?
    
    Args:
        character: Character data
        spell_data: Spell bilgileri
    
    Returns:
        Ritual casting mümkün mü?
    """
    # Spell ritual olabilir mi?
    if not spell_data.get("ritual", False):
        return False
    
    char_class = character.get("class", "")
    
    # Ritual casting yetenekleri check et
    ritual_casters = ["Cleric", "Druid", "Wizard"]
    
    # Wizard spellbook kontrolü
    if char_class == "Wizard":
        # Wizard spellbook'da varsa ritual olarak cast edilebilir
        spellbook = character.get("spellbook", [])
        return spell_data.get("name") in spellbook
    elif char_class in ritual_casters:
        # Diğer sınıflar kendi hazırlanan spell'lerini ritual olarak cast edebilir
        return spell_data.get("name") in character.get("prepared_spells", [])
    
    return False


def calculate_material_components_needed(spells_list: list) -> Dict[str, Any]:
    """
    Spell list'i için gerekli material components'ları hesapla
    
    Args:
        spells_list: Cast edilen spell'ler listesi
    
    Returns:
        Gerekli malzemelerin envanteri
    """
    materials_needed = {}
    consumed_items = {}
    
    for spell in spells_list:
        if isinstance(spell, dict):
            materials = spell.get("material_components", [])
            consumed = spell.get("material_consumed", False)
            
            for material in materials:
                if material not in materials_needed:
                    materials_needed[material] = {
                        "count": 0,
                        "consumed": consumed,
                        "spells": []
                    }
                
                materials_needed[material]["count"] += 1
                materials_needed[material]["spells"].append(spell.get("name", "Unknown"))
                
                if consumed:
                    consumed_items[material] = consumed_items.get(material, 0) + 1
    
    return {
        "all_materials": materials_needed,
        "consumed_items": consumed_items
    }


def prepare_spells_for_casting(character: Dict[str, Any], spells_to_prepare: list) -> Dict[str, Any]:
    """
    Cast için spell'leri hazırla - Spell slot'larını ayır, concentration kontrol et
    
    Args:
        character: Character data
        spells_to_prepare: Hazırlanacak spell'ler
    
    Returns:
        Hazırlık sonuçları ve warnings
    """
    char_level = character.get("level", 1)
    spell_slots = calculate_spell_slots(character)
    
    result = {
        "prepared_spells": [],
        "warnings": [],
        "slot_usage": {}
    }
    
    used_slots = {}
    
    for spell in spells_to_prepare:
        spell_level = spell.get("level", 0)
        slot_key = f"level_{spell_level}"
        
        # Slot availability check
        available_slots = spell_slots.get(slot_key, 0)
        used = used_slots.get(slot_key, 0)
        
        if used < available_slots:
            result["prepared_spells"].append(spell.get("name", "Unknown"))
            used_slots[slot_key] = used + 1
        else:
            result["warnings"].append(f"No available {slot_key} slots for {spell.get('name', 'Unknown')}")
    
    result["slot_usage"] = used_slots
    
    return result


# ============================================================================
# Evrensel Etki Motoru (Universal Effect Engine)
# ============================================================================

import re as _re
import logging as _logging
from typing import Union

_effect_logger = _logging.getLogger(__name__ + ".effects")

# ---- Sistem stat haritasi -------------------------------------------------
# Her sistem farkli yetenek isimleri kullanir; bu haritalar target degerlerini
# karakter dict'indeki gercel anahtarlara esler.

_DND_ABILITY_ALIASES: Dict[str, str] = {
    "str": "Strength", "strength": "Strength",
    "dex": "Dexterity", "dexterity": "Dexterity",
    "con": "Constitution", "constitution": "Constitution",
    "int": "Intelligence", "intelligence": "Intelligence",
    "wis": "Wisdom", "wisdom": "Wisdom",
    "cha": "Charisma", "charisma": "Charisma",
}

_PF1E_ABILITY_ALIASES = _DND_ABILITY_ALIASES  # PF1e ve D&D 5e ayni isimleri kullanir

_VTM_ATTRIBUTE_ALIASES: Dict[str, str] = {
    "strength": "Strength", "dexterity": "Dexterity", "stamina": "Stamina",
    "charisma": "Charisma", "manipulation": "Manipulation", "composure": "Composure",
    "intelligence": "Intelligence", "wits": "Wits", "resolve": "Resolve",
}

_MM3E_ABILITY_ALIASES: Dict[str, str] = {
    "str": "Strength", "strength": "Strength",
    "sta": "Stamina", "stamina": "Stamina",
    "agl": "Agility", "agility": "Agility",
    "dex": "Dexterity", "dexterity": "Dexterity",
    "fgt": "Fighting", "fighting": "Fighting",
    "int": "Intellect", "intellect": "Intellect",
    "awe": "Awareness", "awareness": "Awareness",
    "pre": "Presence", "presence": "Presence",
}

_ALIAS_MAP: Dict[str, Dict[str, str]] = {
    "dnd5e":        _DND_ABILITY_ALIASES,
    "pathfinder1e": _PF1E_ABILITY_ALIASES,
    "vtm5e":        _VTM_ATTRIBUTE_ALIASES,
    "mm3e":         _MM3E_ABILITY_ALIASES,
}


def _resolve_target(target: str, system: str) -> str:
    """target degerini sistem icin dogru anahtara cevir."""
    aliases = _ALIAS_MAP.get(system, {})
    return aliases.get(target.lower().replace(" ", "_"), target)


# ---- Efekt Uygulayici (per-effect-type handlers) --------------------------

def _apply_stat_bonus(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Yetenek puanina bonus ekle."""
    key = _resolve_target(target, system)
    abilities = char.setdefault("abilities", {})
    try:
        abilities[key] = abilities.get(key, 10) + int(value)
    except (TypeError, ValueError):
        _effect_logger.warning("stat_bonus icin gecersiz deger: %s", value)


def _apply_save_bonus(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Saving throw bonusu ekle."""
    bonuses = char.setdefault("save_bonuses", {})
    key = _resolve_target(target, system)
    bonuses[key] = bonuses.get(key, 0) + int(value)


def _apply_skill_bonus(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Beceri bonusu ekle."""
    bonuses = char.setdefault("skill_bonuses", {})
    bonuses[target] = bonuses.get(target, 0) + int(value)


def _apply_speed_bonus(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Hareket hizi bonusu ekle."""
    speeds = char.setdefault("speed_bonuses", {})
    key = target if target != "base" else "base"
    speeds[key] = speeds.get(key, 0) + int(value)


def _apply_hp_bonus(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Can puani bonusu ekle."""
    char["hp_bonus"] = char.get("hp_bonus", 0) + int(value)


def _apply_ac_bonus(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Zirh sinifi bonusu ekle."""
    char["ac_bonus"] = char.get("ac_bonus", 0) + int(value)


def _apply_damage_bonus(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Hasar bonusu ekle."""
    bonuses = char.setdefault("damage_bonuses", {})
    bonuses[target] = bonuses.get(target, 0) + int(value)


def _apply_add_proficiency(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Yetkinlik ekle (armor, weapon, skill, tool, save)."""
    profs = char.setdefault("proficiencies", [])
    if target not in profs:
        profs.append(target)


def _apply_resistance(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Hasar direnci ekle."""
    resists = char.setdefault("resistances", [])
    if target not in resists:
        resists.append(target)


def _apply_immunity(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Hasar bagisikligi ekle."""
    immunes = char.setdefault("immunities", [])
    if target not in immunes:
        immunes.append(target)


def _apply_advantage(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Avantaj (D&D) veya extra die (M&M) ekle."""
    advs = char.setdefault("advantages", [])
    if target not in advs:
        advs.append(target)


def _apply_disadvantage(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Dezavantaj ekle."""
    disadvs = char.setdefault("disadvantages", [])
    if target not in disadvs:
        disadvs.append(target)


def _apply_grant_trait(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Irksal/sinifsal ozellik ekle."""
    traits = char.setdefault("granted_traits", [])
    label = f"{target}: {value}" if value else target
    if label not in traits:
        traits.append(label)


def _apply_set_value(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """Belirli bir alani dogrudan ayarla (override)."""
    char[target] = value


# ---- VtM 5e ozel handler'lar ---------------------------------------------

def _apply_add_dot(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """VtM 5e nokta (dot) sistemi icin deger artir."""
    dots = char.setdefault("dots", {})
    dots[target] = dots.get(target, 0) + int(value)


def _apply_discipline_access(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """VtM 5e disiplin erisimi ekle."""
    discs = char.setdefault("discipline_access", [])
    if target not in discs:
        discs.append(target)


def _apply_pool_bonus(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """VtM 5e zar havuzu bonusu."""
    bonuses = char.setdefault("pool_bonuses", {})
    bonuses[target] = bonuses.get(target, 0) + int(value)


# ---- M&M 3e ozel handler'lar ---------------------------------------------

def _apply_defense_bonus(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """M&M 3e savunma bonusu (dodge, parry, fortitude, toughness, will)."""
    defenses = char.setdefault("defense_bonuses", {})
    defenses[target] = defenses.get(target, 0) + int(value)


def _apply_power_rank(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """M&M 3e guc rank'i ekle."""
    powers = char.setdefault("power_ranks", {})
    powers[target] = powers.get(target, 0) + int(value)


def _apply_ability_rank(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """M&M 3e ability rank'i degistir."""
    abilities = char.setdefault("abilities", {})
    key = _resolve_target(target, system)
    abilities[key] = abilities.get(key, 0) + int(value)


def _apply_advantage_grant(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """M&M 3e advantage (feature) ekle."""
    advs = char.setdefault("mm_advantages", [])
    label = f"{target} {value}" if value and str(value) != "1" else target
    if label not in advs:
        advs.append(label)


def _apply_skill_rank(char: Dict[str, Any], target: str, value: Any, system: str) -> None:
    """M&M 3e skill rank ekle."""
    skills = char.setdefault("skill_ranks", {})
    skills[target] = skills.get(target, 0) + int(value)


# ---- Handler registry ------------------------------------------------------

_EFFECT_HANDLERS = {
    "stat_bonus":        _apply_stat_bonus,
    "save_bonus":        _apply_save_bonus,
    "skill_bonus":       _apply_skill_bonus,
    "speed_bonus":       _apply_speed_bonus,
    "hp_bonus":          _apply_hp_bonus,
    "ac_bonus":          _apply_ac_bonus,
    "damage_bonus":      _apply_damage_bonus,
    "add_proficiency":   _apply_add_proficiency,
    "resistance":        _apply_resistance,
    "immunity":          _apply_immunity,
    "advantage":         _apply_advantage,
    "disadvantage":      _apply_disadvantage,
    "grant_trait":       _apply_grant_trait,
    "set_value":         _apply_set_value,
    # VtM 5e
    "add_dot":           _apply_add_dot,
    "discipline_access": _apply_discipline_access,
    "pool_bonus":        _apply_pool_bonus,
    # M&M 3e
    "defense_bonus":     _apply_defense_bonus,
    "power_rank":        _apply_power_rank,
    "ability_rank":      _apply_ability_rank,
    "advantage_grant":   _apply_advantage_grant,
    "skill_rank":        _apply_skill_rank,
}


def apply_effects(
    character: Dict[str, Any],
    effects: list,
    system: str,
    *,
    ignore_conditions: bool = False,
) -> Dict[str, Any]:
    """
    Etki listesini karakter dict'ine uygula.

    Her EffectModel (veya uyumlu dict) icin uygun handler cagirilir.
    Bilinmeyen effect_type'lar loglanir ama program cokmez.

    Args:
        character: Karakter dict'i (in-place degistirilir).
        effects: EffectModel listesi veya dict listesi.
        system: Sistem anahtari ('dnd5e', 'pathfinder1e', 'vtm5e', 'mm3e').
        ignore_conditions: True ise kosullu efektler de uygulanir.

    Returns:
        Guncellenmis karakter dict'i.
    """
    applied_count = 0

    for effect in effects:
        if isinstance(effect, dict):
            target = effect.get("target", "")
            etype = effect.get("effect_type", "")
            value = effect.get("value", 0)
            condition = effect.get("condition", "")
            source = effect.get("source", "")
        else:
            target = getattr(effect, "target", "")
            etype = getattr(effect, "effect_type", "")
            value = getattr(effect, "value", 0)
            condition = getattr(effect, "condition", "")
            source = getattr(effect, "source", "")

        if not target or not etype:
            continue

        if condition and not ignore_conditions:
            conds = character.setdefault("conditional_effects", [])
            conds.append({
                "target": target, "effect_type": etype,
                "value": value, "condition": condition, "source": source,
            })
            continue

        handler = _EFFECT_HANDLERS.get(etype)
        if handler is None:
            _effect_logger.warning("Bilinmeyen effect_type: '%s' (target=%s)", etype, target)
            continue

        try:
            handler(character, target, value, system)
            applied_count += 1
        except Exception as exc:
            _effect_logger.warning(
                "Efekt uygulama hatasi [%s -> %s]: %s", etype, target, exc,
            )

    _effect_logger.debug("%d/%d efekt uygulandi (system=%s)", applied_count, len(effects), system)
    return character


def collect_effects_from_choices(
    choices: Dict[str, Dict[str, Any]],
    system: str,
) -> list:
    """
    Karakter olusturma secimlerinden (irk, sinif, arka plan vb.) tum
    EffectModel'leri topla.

    Args:
        choices: {'race': race_data, 'class': class_data, 'background': bg_data, ...}
        system: Sistem anahtari.

    Returns:
        Birlesmis EffectModel (dict) listesi.
    """
    all_effects: list = []

    for choice_key, data in choices.items():
        if not isinstance(data, dict):
            continue
        effects = data.get("effects", [])
        for eff in effects:
            if isinstance(eff, dict):
                eff.setdefault("source", choice_key)
            all_effects.append(eff)

    return all_effects


# ============================================================================
# Sisteme Ozel Metin Ayristiricilari (Smart Parsers)
# ============================================================================

def parse_dnd5e_effect(text: str, source: str = "") -> Optional[Dict[str, Any]]:
    """
    D&D 5e metin ifadesini EffectModel dict'ine cevir.

    Desteklenen kaliplar:
      "+2 to Strength"             -> stat_bonus, strength, 2
      "+1 to all ability scores"   -> stat_bonus, all_abilities, 1
      "Darkvision 60 ft."          -> grant_trait, darkvision, "60 ft."
      "Proficiency in Perception"  -> add_proficiency, perception, True
      "Resistance to fire damage"  -> resistance, fire, True
      "Advantage on saving throws against poison" -> advantage, save_vs_poison, True
      "+5 ft. speed"               -> speed_bonus, base, 5
    """
    if not text:
        return None
    t = text.strip()

    m = _re.match(
        r"[+](\d+)\s+(?:to\s+)?(?:all\s+ability\s+scores?)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": "all_abilities", "effect_type": "stat_bonus",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"([+-]?\d+)\s+(?:to\s+|bonus\s+to\s+)?(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma|STR|DEX|CON|INT|WIS|CHA)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(2).lower(), "effect_type": "stat_bonus",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"[+](\d+)\s+(?:to\s+)?(?:Armor\s+Class|AC)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": "ac", "effect_type": "ac_bonus",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"[+](\d+)\s*(?:ft\.?|feet)\s*(?:speed|movement)?",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": "base", "effect_type": "speed_bonus",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"Darkvision\s+(\d+)\s*(?:ft\.?|feet)?",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": "darkvision", "effect_type": "grant_trait",
                "value": f"{m.group(1)} ft.", "source": source}

    m = _re.match(
        r"(?:Proficiency|Proficient)\s+(?:in|with)\s+(.+)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(1).strip().lower(), "effect_type": "add_proficiency",
                "value": True, "source": source}

    m = _re.match(
        r"Resistance\s+to\s+(.+?)(?:\s+damage)?$",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(1).strip().lower(), "effect_type": "resistance",
                "value": True, "source": source}

    m = _re.match(
        r"(?:Immunity|Immune)\s+to\s+(.+?)(?:\s+damage)?$",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(1).strip().lower(), "effect_type": "immunity",
                "value": True, "source": source}

    m = _re.match(
        r"Advantage\s+on\s+(.+?)(?:\s+saving\s+throws?\s+against\s+(.+))?$",
        t, _re.IGNORECASE,
    )
    if m:
        target = m.group(2) or m.group(1)
        condition = f"saving throws against {m.group(2)}" if m.group(2) else ""
        return {"target": target.strip().lower().replace(" ", "_"),
                "effect_type": "advantage", "value": True,
                "condition": condition, "source": source}

    m = _re.match(
        r"[+](\d+)\s+(?:to\s+)?(\w[\w\s]*?)\s+(?:checks?|rolls?|bonus)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(2).strip().lower(), "effect_type": "skill_bonus",
                "value": int(m.group(1)), "source": source}

    return None


def parse_pf1e_effect(text: str, source: str = "") -> Optional[Dict[str, Any]]:
    """
    Pathfinder 1e metin ifadesini EffectModel dict'ine cevir.

    Desteklenen kaliplar:
      "+2 to Constitution"        -> stat_bonus, constitution, 2
      "-2 Charisma"               -> stat_bonus, charisma, -2
      "+2 racial bonus on saves against poison" -> save_bonus, poison, 2
      "+2 dodge bonus to AC"      -> ac_bonus, ac, 2
      "Low-Light Vision"          -> grant_trait, low_light_vision, True
    """
    if not text:
        return None
    t = text.strip()

    m = _re.match(
        r"([+-]?\d+)\s+(?:racial\s+bonus\s+)?(?:to\s+|bonus\s+to\s+)?"
        r"(Str|Dex|Con|Int|Wis|Cha|Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)",
        t, _re.IGNORECASE,
    )
    if m:
        raw_name = m.group(2).lower()
        ability_map = {
            "str": "constitution",  # sadece kisaltma haritasi icin
        }
        ability_map = {
            "str": "strength", "dex": "dexterity", "con": "constitution",
            "int": "intelligence", "wis": "wisdom", "cha": "charisma",
            "strength": "strength", "dexterity": "dexterity",
            "constitution": "constitution", "intelligence": "intelligence",
            "wisdom": "wisdom", "charisma": "charisma",
        }
        return {"target": ability_map.get(raw_name, raw_name),
                "effect_type": "stat_bonus", "value": int(m.group(1)),
                "source": source}

    m = _re.match(
        r"[+](\d+)\s+(?:racial\s+)?(?:bonus\s+)?(?:on|to)\s+(?:saving\s+throws?\s+)?(?:against\s+)?(.+)",
        t, _re.IGNORECASE,
    )
    if m:
        target_text = m.group(2).strip().lower()
        if any(kw in target_text for kw in ("save", "poison", "fear", "enchant", "illus", "mind", "spell")):
            return {"target": target_text.replace(" ", "_"), "effect_type": "save_bonus",
                    "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"[+](\d+)\s+(?:dodge\s+|natural\s+|armor\s+)?bonus\s+to\s+(?:Armor\s+Class|AC)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": "ac", "effect_type": "ac_bonus",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"[+](\d+)\s+(?:racial\s+)?bonus\s+(?:on|to)\s+(\w[\w\s]*?)\s+(?:checks?|rolls?)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(2).strip().lower(), "effect_type": "skill_bonus",
                "value": int(m.group(1)), "source": source}

    low_t = t.lower()
    if "darkvision" in low_t:
        dist = _re.search(r"(\d+)", t)
        return {"target": "darkvision", "effect_type": "grant_trait",
                "value": f"{dist.group(1)} ft." if dist else "60 ft.", "source": source}
    if "low-light vision" in low_t or "low light vision" in low_t:
        return {"target": "low_light_vision", "effect_type": "grant_trait",
                "value": True, "source": source}

    return None


def parse_vtm5e_effect(text: str, source: str = "") -> Optional[Dict[str, Any]]:
    """
    VtM 5e metin ifadesini EffectModel dict'ine cevir.

    Desteklenen kaliplar:
      "Gain 1 dot in Potence"      -> add_dot, potence, 1
      "+2 dots in Celerity"        -> add_dot, celerity, 2
      "Access to Dominate"         -> discipline_access, dominate, True
      "+1 to Strength"             -> add_dot, strength, 1
      "+2 dice to Intimidation"    -> pool_bonus, intimidation, 2
      "Compulsion: Rage"           -> grant_trait, compulsion, "Rage"
    """
    if not text:
        return None
    t = text.strip()

    m = _re.match(
        r"(?:Gain\s+)?[+]?(\d+)\s+dots?\s+(?:in|of|to)\s+(\w[\w\s]*)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(2).strip().lower(), "effect_type": "add_dot",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"(?:Access|Gain\s+access)\s+to\s+(\w[\w\s]*)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(1).strip().lower(), "effect_type": "discipline_access",
                "value": True, "source": source}

    m = _re.match(
        r"[+](\d+)\s+(?:to\s+)?(Strength|Dexterity|Stamina|Charisma|Manipulation|Composure|Intelligence|Wits|Resolve)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(2).strip().lower(), "effect_type": "add_dot",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"[+](\d+)\s+(?:dice?\s+)?(?:to|on|for)\s+(\w[\w\s]*?)(?:\s+(?:checks?|rolls?|pool))?$",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(2).strip().lower(), "effect_type": "pool_bonus",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"Compulsion[:\s]+(.+)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": "compulsion", "effect_type": "grant_trait",
                "value": m.group(1).strip(), "source": source}

    m = _re.match(
        r"Bane[:\s]+(.+)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": "bane", "effect_type": "grant_trait",
                "value": m.group(1).strip(), "source": source}

    return None


def parse_mm3e_effect(text: str, source: str = "") -> Optional[Dict[str, Any]]:
    """
    Mutants & Masterminds 3e metin ifadesini EffectModel dict'ine cevir.

    Desteklenen kaliplar:
      "+2 to Dodge"                -> defense_bonus, dodge, 2
      "+3 Toughness"               -> defense_bonus, toughness, 3
      "+2 Strength"                -> ability_rank, strength, 2
      "Rank 5 Blast"               -> power_rank, blast, 5
      "+4 to Stealth"              -> skill_rank, stealth, 4
      "Defensive Roll 3"           -> advantage_grant, defensive_roll, 3
    """
    if not text:
        return None
    t = text.strip()

    _DEFENSES = {"dodge", "parry", "fortitude", "toughness", "will"}

    m = _re.match(
        r"[+](\d+)\s+(?:to\s+)?(Dodge|Parry|Fortitude|Toughness|Will)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(2).strip().lower(), "effect_type": "defense_bonus",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"[+](\d+)\s+(?:to\s+)?(Strength|Stamina|Agility|Dexterity|Fighting|Intellect|Awareness|Presence|STR|STA|AGL|DEX|FGT|INT|AWE|PRE)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(2).strip().lower(), "effect_type": "ability_rank",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"Rank\s+(\d+)\s+(\w[\w\s]*)",
        t, _re.IGNORECASE,
    )
    if m:
        return {"target": m.group(2).strip().lower(), "effect_type": "power_rank",
                "value": int(m.group(1)), "source": source}

    m = _re.match(
        r"(\w[\w\s]*?)\s+(\d+)$",
        t, _re.IGNORECASE,
    )
    if m:
        name = m.group(1).strip().lower()
        val = int(m.group(2))
        if name in _DEFENSES:
            return {"target": name, "effect_type": "defense_bonus",
                    "value": val, "source": source}
        return {"target": name.replace(" ", "_"), "effect_type": "advantage_grant",
                "value": val, "source": source}

    m = _re.match(
        r"[+](\d+)\s+(?:to\s+)?(\w[\w\s]*?)(?:\s+(?:checks?|bonus|ranks?))?$",
        t, _re.IGNORECASE,
    )
    if m:
        target = m.group(2).strip().lower()
        if target not in _DEFENSES and target not in {
            a.lower() for a in _MM3E_ABILITY_ALIASES.values()
        }:
            return {"target": target, "effect_type": "skill_rank",
                    "value": int(m.group(1)), "source": source}

    return None


def parse_effect(text: str, system: str, source: str = "") -> Optional[Dict[str, Any]]:
    """
    Sistem otomatik tespitli parser dispatch.
    Dogru sisteme gore uygun parser'i cagirir.
    """
    _PARSERS = {
        "dnd5e":        parse_dnd5e_effect,
        "pathfinder1e": parse_pf1e_effect,
        "vtm5e":        parse_vtm5e_effect,
        "mm3e":         parse_mm3e_effect,
    }
    parser = _PARSERS.get(system)
    if parser is None:
        _effect_logger.warning("Bilinmeyen sistem: %s, dnd5e parser kullaniliyor", system)
        parser = parse_dnd5e_effect
    return parser(text, source=source)


def parse_effects_batch(
    texts: List[str],
    system: str,
    source: str = "",
) -> List[Dict[str, Any]]:
    """
    Birden fazla metin ifadesini toplu parse et.
    Parse edilemeyen satirlar atlanir.
    """
    results: List[Dict[str, Any]] = []
    for text in texts:
        parsed = parse_effect(text, system, source=source)
        if parsed is not None:
            results.append(parsed)
    return results
