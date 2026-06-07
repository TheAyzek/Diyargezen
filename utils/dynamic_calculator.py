"""
Dinamik Hesaplama Motoru
JSON'dan yüklenen kurallara göre hesaplama yapar.
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path
from utils.rule_storage import load_rules
from utils.calculations import (
    calculate_proficiency_bonus,
    calculate_armor_class,
    calculate_hit_points,
    calculate_mm_power_points,
)


def get_table_value(table_data: Dict[str, Any], key: Union[int, str]) -> Optional[Any]:
    """
    Tablo verisinden değer al
    Örnek: {"1-4": 2, "5-8": 3} tablosundan level 3 için 2 döndürür
    """
    if isinstance(key, int):
        # Aralık kontrolü
        for range_str, value in table_data.items():
            if '-' in range_str:
                start, end = map(int, range_str.split('-'))
                if start <= key <= end:
                    return value
            elif range_str == str(key):
                return value
    else:
        return table_data.get(str(key))
    
    return None


def calculate_dynamic_proficiency_bonus(level: int, rules: Optional[Dict[str, Any]] = None) -> int:
    """
    Dinamik Proficiency Bonus hesaplama
    Önce özel kurallardan, yoksa varsayılan hesaplamadan
    """
    if rules and 'rules' in rules:
        prof_rule = rules['rules'].get('proficiency_bonus')
        if prof_rule and prof_rule.get('type') == 'table':
            value = get_table_value(prof_rule.get('data', {}), level)
            if value is not None:
                return value
    
    # Varsayılan hesaplama
    return calculate_proficiency_bonus(level)


def calculate_dynamic_armor_class(character: Dict[str, Any], rules: Optional[Dict[str, Any]] = None, default_data: Optional[Dict[str, Any]] = None) -> int:
    """
    Dinamik AC hesaplama
    Önce özel kurallardan, yoksa varsayılan hesaplamadan
    """
    if rules and 'rules' in rules:
        armor_rule = rules['rules'].get('armor_class')
        if armor_rule and armor_rule.get('type') == 'armor_table':
            # Zırh kurallarını kullan
            armor_data = armor_rule.get('data', {})
            equipment = character.get("equipment", [])
            
            for item in equipment:
                if item.get("type") == "armor":
                    armor_name = item.get("name", "").lower()
                    for armor_key, armor_info in armor_data.items():
                        if armor_key in armor_name:
                            base_ac = armor_info.get('base', 10)
                            max_dex = armor_info.get('max_dex')
                            allows_dex = armor_info.get('allows_dex', True)
                            
                            abilities = character.get("abilities", {})
                            dex_modifier = (abilities.get("Dexterity", 10) - 10) // 2
                            
                            if allows_dex:
                                if max_dex is not None:
                                    dex_modifier = min(dex_modifier, max_dex)
                                return base_ac + dex_modifier
                            else:
                                return base_ac
    
    # Varsayılan hesaplama
    return calculate_armor_class(character, default_data)


def calculate_dynamic_hit_points(character: Dict[str, Any], rules: Optional[Dict[str, Any]] = None, default_data: Optional[Dict[str, Any]] = None) -> int:
    """
    Dinamik HP hesaplama
    Önce özel kurallardan, yoksa varsayılan hesaplamadan
    """
    if rules and 'rules' in rules:
        hit_dice_rule = rules['rules'].get('hit_dice')
        if hit_dice_rule and hit_dice_rule.get('type') == 'table':
            # Hit dice tablosunu kullan
            hit_dice_data = hit_dice_rule.get('data', {})
            char_class = character.get("class", "")
            if char_class in hit_dice_data:
                # Özel hit dice kullan
                hit_dice = hit_dice_data[char_class]
                level = character.get("level", 1)
                abilities = character.get("abilities", {})
                con_modifier = (abilities.get("Constitution", 10) - 10) // 2
                
                if level == 1:
                    return hit_dice + con_modifier
                else:
                    hp = hit_dice + con_modifier
                    average_roll = (hit_dice // 2) + 1
                    hp += (average_roll + con_modifier) * (level - 1)
                    return max(1, hp)
    
    # Varsayılan hesaplama
    return calculate_hit_points(character, default_data)


def calculate_dynamic_power_points(power_level: Union[int, str], rules: Optional[Dict[str, Any]] = None) -> int:
    """
    Dinamik Power Points hesaplama (M&M)
    """
    if rules and 'rules' in rules:
        pl_rule = rules['rules'].get('power_levels')
        if pl_rule and pl_rule.get('type') == 'table':
            pl_data = pl_rule.get('data', {})
            pl_key = f"PL{power_level}" if isinstance(power_level, int) else str(power_level)
            if pl_key in pl_data:
                return pl_data[pl_key].get('power_points', 0)
    
    # Varsayılan hesaplama
    try:
        pl = int(power_level) if isinstance(power_level, str) else power_level
        return calculate_mm_power_points(pl)
    except (ValueError, TypeError):
        return 0


def load_rules_for_system(base_dir: Path, system: str) -> Optional[Dict[str, Any]]:
    """
    Sistem için kuralları yükle
    """
    return load_rules(base_dir, system)

