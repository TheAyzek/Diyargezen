"""
Equipment Comparison Modülü - İYİLEŞTİRİLDİ (Equipment Comparison)
İki equipment item'ını karşılaştırma fonksiyonları
"""

from typing import Dict, Any, Optional, List, Tuple


def compare_equipment_items(item1: Dict[str, Any], item2: Dict[str, Any], item_type: str = "auto") -> Dict[str, Any]:
    """
    İki equipment item'ını karşılaştır - İYİLEŞTİRİLDİ (Equipment Comparison)
    
    Args:
        item1: İlk item dict
        item2: İkinci item dict
        item_type: Item tipi ("weapon", "armor", "gear", "auto" - otomatik tespit)
    
    Returns:
        Comparison dict with differences and recommendations
    """
    if not item1 or not item2:
        return {
            "error": "Item bulunamadı",
            "item1": item1,
            "item2": item2
        }
    
    # Item tipini tespit et
    if item_type == "auto":
        item_type = item1.get("type", "gear")
        if item_type != item2.get("type", "gear"):
            # Farklı tipler karşılaştırılamaz
            return {
                "error": "Farklı item tipleri karşılaştırılamaz",
                "item1_type": item_type,
                "item2_type": item2.get("type", "gear")
            }
    
    comparison = {
        "item1_name": item1.get("name", "İsimsiz Eşya"),
        "item2_name": item2.get("name", "İsimsiz Eşya"),
        "item_type": item_type,
        "differences": [],
        "advantages_item1": [],
        "advantages_item2": [],
        "recommendation": None
    }
    
    # Item type'a göre karşılaştır
    if item_type == "weapon":
        comparison = _compare_weapons(item1, item2, comparison)
    elif item_type == "armor":
        comparison = _compare_armor(item1, item2, comparison)
    else:
        comparison = _compare_generic(item1, item2, comparison)
    
    # Recommendation hesapla
    comparison["recommendation"] = _calculate_recommendation(comparison)
    
    return comparison


def _compare_weapons(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Weapon karşılaştırması"""
    # Damage
    damage1 = item1.get("damage", "")
    damage2 = item2.get("damage", "")
    if damage1 != damage2:
        comparison["differences"].append({
            "field": "damage",
            "item1_value": damage1,
            "item2_value": damage2,
            "item1_better": _compare_damage(damage1, damage2) > 0,
            "item2_better": _compare_damage(damage1, damage2) < 0
        })
        if _compare_damage(damage1, damage2) > 0:
            comparison["advantages_item1"].append(f"Daha yüksek damage: {damage1}")
        else:
            comparison["advantages_item2"].append(f"Daha yüksek damage: {damage2}")
    
    # Properties
    properties1 = item1.get("properties", [])
    properties2 = item2.get("properties", [])
    if properties1 != properties2:
        unique1 = set(properties1) - set(properties2)
        unique2 = set(properties2) - set(properties1)
        if unique1:
            comparison["advantages_item1"].append(f"Ek özellikler: {', '.join(unique1)}")
        if unique2:
            comparison["advantages_item2"].append(f"Ek özellikler: {', '.join(unique2)}")
    
    # Range
    range1 = item1.get("range", "")
    range2 = item2.get("range", "")
    if range1 != range2:
        comparison["differences"].append({
            "field": "range",
            "item1_value": range1,
            "item2_value": range2
        })
    
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,  # Daha hafif = daha iyi
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,  # Daha ucuz = daha iyi
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Magic bonuses
    bonus1 = _extract_magic_bonus_from_item(item1)
    bonus2 = _extract_magic_bonus_from_item(item2)
    if bonus1 != bonus2:
        comparison["differences"].append({
            "field": "magic_bonus",
            "item1_value": bonus1,
            "item2_value": bonus2,
            "item1_better": bonus1 > bonus2,
            "item2_better": bonus2 > bonus1
        })
        if bonus1 > bonus2:
            comparison["advantages_item1"].append(f"Magic bonus: +{bonus1}")
        else:
            comparison["advantages_item2"].append(f"Magic bonus: +{bonus2}")
    
    return comparison


def _compare_armor(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Armor karşılaştırması"""
    # AC (Armor Class)
    ac1 = item1.get("ac", "")
    ac2 = item2.get("ac", "")
    if ac1 != ac2:
        ac1_val = _parse_ac_value(ac1)
        ac2_val = _parse_ac_value(ac2)
        comparison["differences"].append({
            "field": "ac",
            "item1_value": ac1,
            "item2_value": ac2,
            "item1_better": ac1_val > ac2_val,  # Daha yüksek AC = daha iyi
            "item2_better": ac2_val > ac1_val
        })
        if ac1_val > ac2_val:
            comparison["advantages_item1"].append(f"Daha yüksek AC: {ac1}")
        else:
            comparison["advantages_item2"].append(f"Daha yüksek AC: {ac2}")
    
    # Armor Type
    armor_type1 = item1.get("armor_type", "")
    armor_type2 = item2.get("armor_type", "")
    if armor_type1 != armor_type2:
        comparison["differences"].append({
            "field": "armor_type",
            "item1_value": armor_type1,
            "item2_value": armor_type2
        })
    
    # Stealth Disadvantage
    stealth1 = item1.get("stealth_disadvantage", False)
    stealth2 = item2.get("stealth_disadvantage", False)
    if stealth1 != stealth2:
        comparison["differences"].append({
            "field": "stealth",
            "item1_value": "Disadvantage" if stealth1 else "Normal",
            "item2_value": "Disadvantage" if stealth2 else "Normal",
            "item1_better": not stealth1,  # Disadvantage yok = daha iyi
            "item2_better": not stealth2
        })
    
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Magic bonuses
    bonus1 = _extract_magic_bonus_from_item(item1)
    bonus2 = _extract_magic_bonus_from_item(item2)
    if bonus1 != bonus2:
        comparison["differences"].append({
            "field": "magic_bonus",
            "item1_value": bonus1,
            "item2_value": bonus2,
            "item1_better": bonus1 > bonus2,
            "item2_better": bonus2 > bonus1
        })
        if bonus1 > bonus2:
            comparison["advantages_item1"].append(f"Magic AC bonus: +{bonus1}")
        else:
            comparison["advantages_item2"].append(f"Magic AC bonus: +{bonus2}")
    
    return comparison


def _compare_generic(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Generic item karşılaştırması"""
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Description differences
    desc1 = item1.get("description", "")
    desc2 = item2.get("description", "")
    if desc1 != desc2:
        comparison["differences"].append({
            "field": "description",
            "item1_value": desc1[:100] + "..." if len(desc1) > 100 else desc1,
            "item2_value": desc2[:100] + "..." if len(desc2) > 100 else desc2
        })
    
    return comparison


def _compare_damage(damage1: str, damage2: str) -> int:
    """Damage karşılaştırması (-1: item2 better, 0: equal, 1: item1 better)"""
    import re
    
    # "1d8" formatını parse et
    def parse_damage(dmg_str):
        if not dmg_str:
            return 0, 0
        match = re.search(r'(\d+)d(\d+)', dmg_str)
        if match:
            dice_count = int(match.group(1))
            dice_size = int(match.group(2))
            # Ortalama damage: dice_count * (dice_size + 1) / 2
            avg_damage = dice_count * (dice_size + 1) / 2
            return avg_damage, dice_size
        # Fixed damage
        match = re.search(r'(\d+)', dmg_str)
        if match:
            return float(match.group(1)), 0
        return 0, 0
    
    avg1, size1 = parse_damage(damage1)
    avg2, size2 = parse_damage(damage2)
    
    if avg1 > avg2:
        return 1
    elif avg1 < avg2:
        return -1
    elif size1 > size2:
        return 1  # Daha büyük dice = daha iyi (crit için)
    elif size1 < size2:
        return -1
    return 0


def _parse_gp_cost(cost_str: str) -> float:
    """Cost string'den gp değerini parse et"""
    import re
    if not cost_str:
        return 0.0
    
    # "10 gp", "1 sp", "5 cp" gibi formatları parse et
    match = re.search(r'(\d+(?:\.\d+)?)\s*(gp|sp|cp|pp)', cost_str.lower())
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        # Conversion: 1 gp = 10 sp = 100 cp = 0.1 pp
        if unit == "gp":
            return value
        elif unit == "sp":
            return value / 10
        elif unit == "cp":
            return value / 100
        elif unit == "pp":
            return value * 10
    
    # Sadece sayı varsa gp olarak kabul et
    match = re.search(r'(\d+(?:\.\d+)?)', cost_str)
    if match:
        return float(match.group(1))
    
    return 0.0


def _parse_ac_value(ac_str: Any) -> int:
    """AC string'den integer değerini parse et"""
    if isinstance(ac_str, int):
        return ac_str
    if isinstance(ac_str, str):
        import re
        match = re.search(r'(\d+)', str(ac_str))
        if match:
            return int(match.group(1))
    return 0


def _extract_magic_bonus_from_item(item: Dict[str, Any]) -> int:
    """Item'dan magic bonus çıkar"""
    item_name = item.get("name", "").lower()
    description = item.get("description", "").lower()
    
    import re
    
    # "+1", "+2" gibi pattern
    name_match = re.search(r'\+(\d+)', item_name)
    if name_match:
        try:
            return int(name_match.group(1))
        except ValueError:
            pass
    
    # Description'da "+1 to AC" veya "+2 to attack" gibi
    desc_match = re.search(r'\+(\d+)\s*(?:to|armor|ac|attack|damage)', description)
    if desc_match:
        try:
            return int(desc_match.group(1))
        except ValueError:
            pass
    
    return 0


def _calculate_recommendation(comparison: Dict[str, Any]) -> Optional[str]:
    """Karşılaştırmaya göre recommendation hesapla"""
    advantages1 = len(comparison.get("advantages_item1", []))
    advantages2 = len(comparison.get("advantages_item2", []))
    
    if advantages1 > advantages2:
        return f"{comparison['item1_name']} daha avantajlı görünüyor ({advantages1} avantaj)"
    elif advantages2 > advantages1:
        return f"{comparison['item2_name']} daha avantajlı görünüyor ({advantages2} avantaj)"
    elif advantages1 == advantages2 and advantages1 > 0:
        return "İki item da benzer avantajlara sahip, tercih karakterinize bağlı"
    else:
        return "İki item benzer özelliklere sahip"


Equipment Comparison Modülü - İYİLEŞTİRİLDİ (Equipment Comparison)
İki equipment item'ını karşılaştırma fonksiyonları
"""

from typing import Dict, Any, Optional, List, Tuple


def compare_equipment_items(item1: Dict[str, Any], item2: Dict[str, Any], item_type: str = "auto") -> Dict[str, Any]:
    """
    İki equipment item'ını karşılaştır - İYİLEŞTİRİLDİ (Equipment Comparison)
    
    Args:
        item1: İlk item dict
        item2: İkinci item dict
        item_type: Item tipi ("weapon", "armor", "gear", "auto" - otomatik tespit)
    
    Returns:
        Comparison dict with differences and recommendations
    """
    if not item1 or not item2:
        return {
            "error": "Item bulunamadı",
            "item1": item1,
            "item2": item2
        }
    
    # Item tipini tespit et
    if item_type == "auto":
        item_type = item1.get("type", "gear")
        if item_type != item2.get("type", "gear"):
            # Farklı tipler karşılaştırılamaz
            return {
                "error": "Farklı item tipleri karşılaştırılamaz",
                "item1_type": item_type,
                "item2_type": item2.get("type", "gear")
            }
    
    comparison = {
        "item1_name": item1.get("name", "İsimsiz Eşya"),
        "item2_name": item2.get("name", "İsimsiz Eşya"),
        "item_type": item_type,
        "differences": [],
        "advantages_item1": [],
        "advantages_item2": [],
        "recommendation": None
    }
    
    # Item type'a göre karşılaştır
    if item_type == "weapon":
        comparison = _compare_weapons(item1, item2, comparison)
    elif item_type == "armor":
        comparison = _compare_armor(item1, item2, comparison)
    else:
        comparison = _compare_generic(item1, item2, comparison)
    
    # Recommendation hesapla
    comparison["recommendation"] = _calculate_recommendation(comparison)
    
    return comparison


def _compare_weapons(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Weapon karşılaştırması"""
    # Damage
    damage1 = item1.get("damage", "")
    damage2 = item2.get("damage", "")
    if damage1 != damage2:
        comparison["differences"].append({
            "field": "damage",
            "item1_value": damage1,
            "item2_value": damage2,
            "item1_better": _compare_damage(damage1, damage2) > 0,
            "item2_better": _compare_damage(damage1, damage2) < 0
        })
        if _compare_damage(damage1, damage2) > 0:
            comparison["advantages_item1"].append(f"Daha yüksek damage: {damage1}")
        else:
            comparison["advantages_item2"].append(f"Daha yüksek damage: {damage2}")
    
    # Properties
    properties1 = item1.get("properties", [])
    properties2 = item2.get("properties", [])
    if properties1 != properties2:
        unique1 = set(properties1) - set(properties2)
        unique2 = set(properties2) - set(properties1)
        if unique1:
            comparison["advantages_item1"].append(f"Ek özellikler: {', '.join(unique1)}")
        if unique2:
            comparison["advantages_item2"].append(f"Ek özellikler: {', '.join(unique2)}")
    
    # Range
    range1 = item1.get("range", "")
    range2 = item2.get("range", "")
    if range1 != range2:
        comparison["differences"].append({
            "field": "range",
            "item1_value": range1,
            "item2_value": range2
        })
    
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,  # Daha hafif = daha iyi
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,  # Daha ucuz = daha iyi
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Magic bonuses
    bonus1 = _extract_magic_bonus_from_item(item1)
    bonus2 = _extract_magic_bonus_from_item(item2)
    if bonus1 != bonus2:
        comparison["differences"].append({
            "field": "magic_bonus",
            "item1_value": bonus1,
            "item2_value": bonus2,
            "item1_better": bonus1 > bonus2,
            "item2_better": bonus2 > bonus1
        })
        if bonus1 > bonus2:
            comparison["advantages_item1"].append(f"Magic bonus: +{bonus1}")
        else:
            comparison["advantages_item2"].append(f"Magic bonus: +{bonus2}")
    
    return comparison


def _compare_armor(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Armor karşılaştırması"""
    # AC (Armor Class)
    ac1 = item1.get("ac", "")
    ac2 = item2.get("ac", "")
    if ac1 != ac2:
        ac1_val = _parse_ac_value(ac1)
        ac2_val = _parse_ac_value(ac2)
        comparison["differences"].append({
            "field": "ac",
            "item1_value": ac1,
            "item2_value": ac2,
            "item1_better": ac1_val > ac2_val,  # Daha yüksek AC = daha iyi
            "item2_better": ac2_val > ac1_val
        })
        if ac1_val > ac2_val:
            comparison["advantages_item1"].append(f"Daha yüksek AC: {ac1}")
        else:
            comparison["advantages_item2"].append(f"Daha yüksek AC: {ac2}")
    
    # Armor Type
    armor_type1 = item1.get("armor_type", "")
    armor_type2 = item2.get("armor_type", "")
    if armor_type1 != armor_type2:
        comparison["differences"].append({
            "field": "armor_type",
            "item1_value": armor_type1,
            "item2_value": armor_type2
        })
    
    # Stealth Disadvantage
    stealth1 = item1.get("stealth_disadvantage", False)
    stealth2 = item2.get("stealth_disadvantage", False)
    if stealth1 != stealth2:
        comparison["differences"].append({
            "field": "stealth",
            "item1_value": "Disadvantage" if stealth1 else "Normal",
            "item2_value": "Disadvantage" if stealth2 else "Normal",
            "item1_better": not stealth1,  # Disadvantage yok = daha iyi
            "item2_better": not stealth2
        })
    
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Magic bonuses
    bonus1 = _extract_magic_bonus_from_item(item1)
    bonus2 = _extract_magic_bonus_from_item(item2)
    if bonus1 != bonus2:
        comparison["differences"].append({
            "field": "magic_bonus",
            "item1_value": bonus1,
            "item2_value": bonus2,
            "item1_better": bonus1 > bonus2,
            "item2_better": bonus2 > bonus1
        })
        if bonus1 > bonus2:
            comparison["advantages_item1"].append(f"Magic AC bonus: +{bonus1}")
        else:
            comparison["advantages_item2"].append(f"Magic AC bonus: +{bonus2}")
    
    return comparison


def _compare_generic(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Generic item karşılaştırması"""
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Description differences
    desc1 = item1.get("description", "")
    desc2 = item2.get("description", "")
    if desc1 != desc2:
        comparison["differences"].append({
            "field": "description",
            "item1_value": desc1[:100] + "..." if len(desc1) > 100 else desc1,
            "item2_value": desc2[:100] + "..." if len(desc2) > 100 else desc2
        })
    
    return comparison


def _compare_damage(damage1: str, damage2: str) -> int:
    """Damage karşılaştırması (-1: item2 better, 0: equal, 1: item1 better)"""
    import re
    
    # "1d8" formatını parse et
    def parse_damage(dmg_str):
        if not dmg_str:
            return 0, 0
        match = re.search(r'(\d+)d(\d+)', dmg_str)
        if match:
            dice_count = int(match.group(1))
            dice_size = int(match.group(2))
            # Ortalama damage: dice_count * (dice_size + 1) / 2
            avg_damage = dice_count * (dice_size + 1) / 2
            return avg_damage, dice_size
        # Fixed damage
        match = re.search(r'(\d+)', dmg_str)
        if match:
            return float(match.group(1)), 0
        return 0, 0
    
    avg1, size1 = parse_damage(damage1)
    avg2, size2 = parse_damage(damage2)
    
    if avg1 > avg2:
        return 1
    elif avg1 < avg2:
        return -1
    elif size1 > size2:
        return 1  # Daha büyük dice = daha iyi (crit için)
    elif size1 < size2:
        return -1
    return 0


def _parse_gp_cost(cost_str: str) -> float:
    """Cost string'den gp değerini parse et"""
    import re
    if not cost_str:
        return 0.0
    
    # "10 gp", "1 sp", "5 cp" gibi formatları parse et
    match = re.search(r'(\d+(?:\.\d+)?)\s*(gp|sp|cp|pp)', cost_str.lower())
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        # Conversion: 1 gp = 10 sp = 100 cp = 0.1 pp
        if unit == "gp":
            return value
        elif unit == "sp":
            return value / 10
        elif unit == "cp":
            return value / 100
        elif unit == "pp":
            return value * 10
    
    # Sadece sayı varsa gp olarak kabul et
    match = re.search(r'(\d+(?:\.\d+)?)', cost_str)
    if match:
        return float(match.group(1))
    
    return 0.0


def _parse_ac_value(ac_str: Any) -> int:
    """AC string'den integer değerini parse et"""
    if isinstance(ac_str, int):
        return ac_str
    if isinstance(ac_str, str):
        import re
        match = re.search(r'(\d+)', str(ac_str))
        if match:
            return int(match.group(1))
    return 0


def _extract_magic_bonus_from_item(item: Dict[str, Any]) -> int:
    """Item'dan magic bonus çıkar"""
    item_name = item.get("name", "").lower()
    description = item.get("description", "").lower()
    
    import re
    
    # "+1", "+2" gibi pattern
    name_match = re.search(r'\+(\d+)', item_name)
    if name_match:
        try:
            return int(name_match.group(1))
        except ValueError:
            pass
    
    # Description'da "+1 to AC" veya "+2 to attack" gibi
    desc_match = re.search(r'\+(\d+)\s*(?:to|armor|ac|attack|damage)', description)
    if desc_match:
        try:
            return int(desc_match.group(1))
        except ValueError:
            pass
    
    return 0


def _calculate_recommendation(comparison: Dict[str, Any]) -> Optional[str]:
    """Karşılaştırmaya göre recommendation hesapla"""
    advantages1 = len(comparison.get("advantages_item1", []))
    advantages2 = len(comparison.get("advantages_item2", []))
    
    if advantages1 > advantages2:
        return f"{comparison['item1_name']} daha avantajlı görünüyor ({advantages1} avantaj)"
    elif advantages2 > advantages1:
        return f"{comparison['item2_name']} daha avantajlı görünüyor ({advantages2} avantaj)"
    elif advantages1 == advantages2 and advantages1 > 0:
        return "İki item da benzer avantajlara sahip, tercih karakterinize bağlı"
    else:
        return "İki item benzer özelliklere sahip"




Equipment Comparison Modülü - İYİLEŞTİRİLDİ (Equipment Comparison)
İki equipment item'ını karşılaştırma fonksiyonları
"""

from typing import Dict, Any, Optional, List, Tuple


def compare_equipment_items(item1: Dict[str, Any], item2: Dict[str, Any], item_type: str = "auto") -> Dict[str, Any]:
    """
    İki equipment item'ını karşılaştır - İYİLEŞTİRİLDİ (Equipment Comparison)
    
    Args:
        item1: İlk item dict
        item2: İkinci item dict
        item_type: Item tipi ("weapon", "armor", "gear", "auto" - otomatik tespit)
    
    Returns:
        Comparison dict with differences and recommendations
    """
    if not item1 or not item2:
        return {
            "error": "Item bulunamadı",
            "item1": item1,
            "item2": item2
        }
    
    # Item tipini tespit et
    if item_type == "auto":
        item_type = item1.get("type", "gear")
        if item_type != item2.get("type", "gear"):
            # Farklı tipler karşılaştırılamaz
            return {
                "error": "Farklı item tipleri karşılaştırılamaz",
                "item1_type": item_type,
                "item2_type": item2.get("type", "gear")
            }
    
    comparison = {
        "item1_name": item1.get("name", "İsimsiz Eşya"),
        "item2_name": item2.get("name", "İsimsiz Eşya"),
        "item_type": item_type,
        "differences": [],
        "advantages_item1": [],
        "advantages_item2": [],
        "recommendation": None
    }
    
    # Item type'a göre karşılaştır
    if item_type == "weapon":
        comparison = _compare_weapons(item1, item2, comparison)
    elif item_type == "armor":
        comparison = _compare_armor(item1, item2, comparison)
    else:
        comparison = _compare_generic(item1, item2, comparison)
    
    # Recommendation hesapla
    comparison["recommendation"] = _calculate_recommendation(comparison)
    
    return comparison


def _compare_weapons(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Weapon karşılaştırması"""
    # Damage
    damage1 = item1.get("damage", "")
    damage2 = item2.get("damage", "")
    if damage1 != damage2:
        comparison["differences"].append({
            "field": "damage",
            "item1_value": damage1,
            "item2_value": damage2,
            "item1_better": _compare_damage(damage1, damage2) > 0,
            "item2_better": _compare_damage(damage1, damage2) < 0
        })
        if _compare_damage(damage1, damage2) > 0:
            comparison["advantages_item1"].append(f"Daha yüksek damage: {damage1}")
        else:
            comparison["advantages_item2"].append(f"Daha yüksek damage: {damage2}")
    
    # Properties
    properties1 = item1.get("properties", [])
    properties2 = item2.get("properties", [])
    if properties1 != properties2:
        unique1 = set(properties1) - set(properties2)
        unique2 = set(properties2) - set(properties1)
        if unique1:
            comparison["advantages_item1"].append(f"Ek özellikler: {', '.join(unique1)}")
        if unique2:
            comparison["advantages_item2"].append(f"Ek özellikler: {', '.join(unique2)}")
    
    # Range
    range1 = item1.get("range", "")
    range2 = item2.get("range", "")
    if range1 != range2:
        comparison["differences"].append({
            "field": "range",
            "item1_value": range1,
            "item2_value": range2
        })
    
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,  # Daha hafif = daha iyi
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,  # Daha ucuz = daha iyi
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Magic bonuses
    bonus1 = _extract_magic_bonus_from_item(item1)
    bonus2 = _extract_magic_bonus_from_item(item2)
    if bonus1 != bonus2:
        comparison["differences"].append({
            "field": "magic_bonus",
            "item1_value": bonus1,
            "item2_value": bonus2,
            "item1_better": bonus1 > bonus2,
            "item2_better": bonus2 > bonus1
        })
        if bonus1 > bonus2:
            comparison["advantages_item1"].append(f"Magic bonus: +{bonus1}")
        else:
            comparison["advantages_item2"].append(f"Magic bonus: +{bonus2}")
    
    return comparison


def _compare_armor(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Armor karşılaştırması"""
    # AC (Armor Class)
    ac1 = item1.get("ac", "")
    ac2 = item2.get("ac", "")
    if ac1 != ac2:
        ac1_val = _parse_ac_value(ac1)
        ac2_val = _parse_ac_value(ac2)
        comparison["differences"].append({
            "field": "ac",
            "item1_value": ac1,
            "item2_value": ac2,
            "item1_better": ac1_val > ac2_val,  # Daha yüksek AC = daha iyi
            "item2_better": ac2_val > ac1_val
        })
        if ac1_val > ac2_val:
            comparison["advantages_item1"].append(f"Daha yüksek AC: {ac1}")
        else:
            comparison["advantages_item2"].append(f"Daha yüksek AC: {ac2}")
    
    # Armor Type
    armor_type1 = item1.get("armor_type", "")
    armor_type2 = item2.get("armor_type", "")
    if armor_type1 != armor_type2:
        comparison["differences"].append({
            "field": "armor_type",
            "item1_value": armor_type1,
            "item2_value": armor_type2
        })
    
    # Stealth Disadvantage
    stealth1 = item1.get("stealth_disadvantage", False)
    stealth2 = item2.get("stealth_disadvantage", False)
    if stealth1 != stealth2:
        comparison["differences"].append({
            "field": "stealth",
            "item1_value": "Disadvantage" if stealth1 else "Normal",
            "item2_value": "Disadvantage" if stealth2 else "Normal",
            "item1_better": not stealth1,  # Disadvantage yok = daha iyi
            "item2_better": not stealth2
        })
    
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Magic bonuses
    bonus1 = _extract_magic_bonus_from_item(item1)
    bonus2 = _extract_magic_bonus_from_item(item2)
    if bonus1 != bonus2:
        comparison["differences"].append({
            "field": "magic_bonus",
            "item1_value": bonus1,
            "item2_value": bonus2,
            "item1_better": bonus1 > bonus2,
            "item2_better": bonus2 > bonus1
        })
        if bonus1 > bonus2:
            comparison["advantages_item1"].append(f"Magic AC bonus: +{bonus1}")
        else:
            comparison["advantages_item2"].append(f"Magic AC bonus: +{bonus2}")
    
    return comparison


def _compare_generic(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Generic item karşılaştırması"""
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Description differences
    desc1 = item1.get("description", "")
    desc2 = item2.get("description", "")
    if desc1 != desc2:
        comparison["differences"].append({
            "field": "description",
            "item1_value": desc1[:100] + "..." if len(desc1) > 100 else desc1,
            "item2_value": desc2[:100] + "..." if len(desc2) > 100 else desc2
        })
    
    return comparison


def _compare_damage(damage1: str, damage2: str) -> int:
    """Damage karşılaştırması (-1: item2 better, 0: equal, 1: item1 better)"""
    import re
    
    # "1d8" formatını parse et
    def parse_damage(dmg_str):
        if not dmg_str:
            return 0, 0
        match = re.search(r'(\d+)d(\d+)', dmg_str)
        if match:
            dice_count = int(match.group(1))
            dice_size = int(match.group(2))
            # Ortalama damage: dice_count * (dice_size + 1) / 2
            avg_damage = dice_count * (dice_size + 1) / 2
            return avg_damage, dice_size
        # Fixed damage
        match = re.search(r'(\d+)', dmg_str)
        if match:
            return float(match.group(1)), 0
        return 0, 0
    
    avg1, size1 = parse_damage(damage1)
    avg2, size2 = parse_damage(damage2)
    
    if avg1 > avg2:
        return 1
    elif avg1 < avg2:
        return -1
    elif size1 > size2:
        return 1  # Daha büyük dice = daha iyi (crit için)
    elif size1 < size2:
        return -1
    return 0


def _parse_gp_cost(cost_str: str) -> float:
    """Cost string'den gp değerini parse et"""
    import re
    if not cost_str:
        return 0.0
    
    # "10 gp", "1 sp", "5 cp" gibi formatları parse et
    match = re.search(r'(\d+(?:\.\d+)?)\s*(gp|sp|cp|pp)', cost_str.lower())
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        # Conversion: 1 gp = 10 sp = 100 cp = 0.1 pp
        if unit == "gp":
            return value
        elif unit == "sp":
            return value / 10
        elif unit == "cp":
            return value / 100
        elif unit == "pp":
            return value * 10
    
    # Sadece sayı varsa gp olarak kabul et
    match = re.search(r'(\d+(?:\.\d+)?)', cost_str)
    if match:
        return float(match.group(1))
    
    return 0.0


def _parse_ac_value(ac_str: Any) -> int:
    """AC string'den integer değerini parse et"""
    if isinstance(ac_str, int):
        return ac_str
    if isinstance(ac_str, str):
        import re
        match = re.search(r'(\d+)', str(ac_str))
        if match:
            return int(match.group(1))
    return 0


def _extract_magic_bonus_from_item(item: Dict[str, Any]) -> int:
    """Item'dan magic bonus çıkar"""
    item_name = item.get("name", "").lower()
    description = item.get("description", "").lower()
    
    import re
    
    # "+1", "+2" gibi pattern
    name_match = re.search(r'\+(\d+)', item_name)
    if name_match:
        try:
            return int(name_match.group(1))
        except ValueError:
            pass
    
    # Description'da "+1 to AC" veya "+2 to attack" gibi
    desc_match = re.search(r'\+(\d+)\s*(?:to|armor|ac|attack|damage)', description)
    if desc_match:
        try:
            return int(desc_match.group(1))
        except ValueError:
            pass
    
    return 0


def _calculate_recommendation(comparison: Dict[str, Any]) -> Optional[str]:
    """Karşılaştırmaya göre recommendation hesapla"""
    advantages1 = len(comparison.get("advantages_item1", []))
    advantages2 = len(comparison.get("advantages_item2", []))
    
    if advantages1 > advantages2:
        return f"{comparison['item1_name']} daha avantajlı görünüyor ({advantages1} avantaj)"
    elif advantages2 > advantages1:
        return f"{comparison['item2_name']} daha avantajlı görünüyor ({advantages2} avantaj)"
    elif advantages1 == advantages2 and advantages1 > 0:
        return "İki item da benzer avantajlara sahip, tercih karakterinize bağlı"
    else:
        return "İki item benzer özelliklere sahip"


Equipment Comparison Modülü - İYİLEŞTİRİLDİ (Equipment Comparison)
İki equipment item'ını karşılaştırma fonksiyonları
"""

from typing import Dict, Any, Optional, List, Tuple


def compare_equipment_items(item1: Dict[str, Any], item2: Dict[str, Any], item_type: str = "auto") -> Dict[str, Any]:
    """
    İki equipment item'ını karşılaştır - İYİLEŞTİRİLDİ (Equipment Comparison)
    
    Args:
        item1: İlk item dict
        item2: İkinci item dict
        item_type: Item tipi ("weapon", "armor", "gear", "auto" - otomatik tespit)
    
    Returns:
        Comparison dict with differences and recommendations
    """
    if not item1 or not item2:
        return {
            "error": "Item bulunamadı",
            "item1": item1,
            "item2": item2
        }
    
    # Item tipini tespit et
    if item_type == "auto":
        item_type = item1.get("type", "gear")
        if item_type != item2.get("type", "gear"):
            # Farklı tipler karşılaştırılamaz
            return {
                "error": "Farklı item tipleri karşılaştırılamaz",
                "item1_type": item_type,
                "item2_type": item2.get("type", "gear")
            }
    
    comparison = {
        "item1_name": item1.get("name", "İsimsiz Eşya"),
        "item2_name": item2.get("name", "İsimsiz Eşya"),
        "item_type": item_type,
        "differences": [],
        "advantages_item1": [],
        "advantages_item2": [],
        "recommendation": None
    }
    
    # Item type'a göre karşılaştır
    if item_type == "weapon":
        comparison = _compare_weapons(item1, item2, comparison)
    elif item_type == "armor":
        comparison = _compare_armor(item1, item2, comparison)
    else:
        comparison = _compare_generic(item1, item2, comparison)
    
    # Recommendation hesapla
    comparison["recommendation"] = _calculate_recommendation(comparison)
    
    return comparison


def _compare_weapons(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Weapon karşılaştırması"""
    # Damage
    damage1 = item1.get("damage", "")
    damage2 = item2.get("damage", "")
    if damage1 != damage2:
        comparison["differences"].append({
            "field": "damage",
            "item1_value": damage1,
            "item2_value": damage2,
            "item1_better": _compare_damage(damage1, damage2) > 0,
            "item2_better": _compare_damage(damage1, damage2) < 0
        })
        if _compare_damage(damage1, damage2) > 0:
            comparison["advantages_item1"].append(f"Daha yüksek damage: {damage1}")
        else:
            comparison["advantages_item2"].append(f"Daha yüksek damage: {damage2}")
    
    # Properties
    properties1 = item1.get("properties", [])
    properties2 = item2.get("properties", [])
    if properties1 != properties2:
        unique1 = set(properties1) - set(properties2)
        unique2 = set(properties2) - set(properties1)
        if unique1:
            comparison["advantages_item1"].append(f"Ek özellikler: {', '.join(unique1)}")
        if unique2:
            comparison["advantages_item2"].append(f"Ek özellikler: {', '.join(unique2)}")
    
    # Range
    range1 = item1.get("range", "")
    range2 = item2.get("range", "")
    if range1 != range2:
        comparison["differences"].append({
            "field": "range",
            "item1_value": range1,
            "item2_value": range2
        })
    
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,  # Daha hafif = daha iyi
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,  # Daha ucuz = daha iyi
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Magic bonuses
    bonus1 = _extract_magic_bonus_from_item(item1)
    bonus2 = _extract_magic_bonus_from_item(item2)
    if bonus1 != bonus2:
        comparison["differences"].append({
            "field": "magic_bonus",
            "item1_value": bonus1,
            "item2_value": bonus2,
            "item1_better": bonus1 > bonus2,
            "item2_better": bonus2 > bonus1
        })
        if bonus1 > bonus2:
            comparison["advantages_item1"].append(f"Magic bonus: +{bonus1}")
        else:
            comparison["advantages_item2"].append(f"Magic bonus: +{bonus2}")
    
    return comparison


def _compare_armor(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Armor karşılaştırması"""
    # AC (Armor Class)
    ac1 = item1.get("ac", "")
    ac2 = item2.get("ac", "")
    if ac1 != ac2:
        ac1_val = _parse_ac_value(ac1)
        ac2_val = _parse_ac_value(ac2)
        comparison["differences"].append({
            "field": "ac",
            "item1_value": ac1,
            "item2_value": ac2,
            "item1_better": ac1_val > ac2_val,  # Daha yüksek AC = daha iyi
            "item2_better": ac2_val > ac1_val
        })
        if ac1_val > ac2_val:
            comparison["advantages_item1"].append(f"Daha yüksek AC: {ac1}")
        else:
            comparison["advantages_item2"].append(f"Daha yüksek AC: {ac2}")
    
    # Armor Type
    armor_type1 = item1.get("armor_type", "")
    armor_type2 = item2.get("armor_type", "")
    if armor_type1 != armor_type2:
        comparison["differences"].append({
            "field": "armor_type",
            "item1_value": armor_type1,
            "item2_value": armor_type2
        })
    
    # Stealth Disadvantage
    stealth1 = item1.get("stealth_disadvantage", False)
    stealth2 = item2.get("stealth_disadvantage", False)
    if stealth1 != stealth2:
        comparison["differences"].append({
            "field": "stealth",
            "item1_value": "Disadvantage" if stealth1 else "Normal",
            "item2_value": "Disadvantage" if stealth2 else "Normal",
            "item1_better": not stealth1,  # Disadvantage yok = daha iyi
            "item2_better": not stealth2
        })
    
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Magic bonuses
    bonus1 = _extract_magic_bonus_from_item(item1)
    bonus2 = _extract_magic_bonus_from_item(item2)
    if bonus1 != bonus2:
        comparison["differences"].append({
            "field": "magic_bonus",
            "item1_value": bonus1,
            "item2_value": bonus2,
            "item1_better": bonus1 > bonus2,
            "item2_better": bonus2 > bonus1
        })
        if bonus1 > bonus2:
            comparison["advantages_item1"].append(f"Magic AC bonus: +{bonus1}")
        else:
            comparison["advantages_item2"].append(f"Magic AC bonus: +{bonus2}")
    
    return comparison


def _compare_generic(item1: Dict[str, Any], item2: Dict[str, Any], comparison: Dict[str, Any]) -> Dict[str, Any]:
    """Generic item karşılaştırması"""
    # Weight
    weight1 = item1.get("weight", 0)
    weight2 = item2.get("weight", 0)
    if weight1 != weight2:
        comparison["differences"].append({
            "field": "weight",
            "item1_value": weight1,
            "item2_value": weight2,
            "item1_better": weight1 < weight2,
            "item2_better": weight2 < weight1
        })
    
    # Cost
    cost1 = item1.get("cost", "0 gp")
    cost2 = item2.get("cost", "0 gp")
    if cost1 != cost2:
        cost1_gp = _parse_gp_cost(cost1)
        cost2_gp = _parse_gp_cost(cost2)
        comparison["differences"].append({
            "field": "cost",
            "item1_value": cost1,
            "item2_value": cost2,
            "item1_better": cost1_gp < cost2_gp,
            "item2_better": cost2_gp < cost1_gp
        })
    
    # Description differences
    desc1 = item1.get("description", "")
    desc2 = item2.get("description", "")
    if desc1 != desc2:
        comparison["differences"].append({
            "field": "description",
            "item1_value": desc1[:100] + "..." if len(desc1) > 100 else desc1,
            "item2_value": desc2[:100] + "..." if len(desc2) > 100 else desc2
        })
    
    return comparison


def _compare_damage(damage1: str, damage2: str) -> int:
    """Damage karşılaştırması (-1: item2 better, 0: equal, 1: item1 better)"""
    import re
    
    # "1d8" formatını parse et
    def parse_damage(dmg_str):
        if not dmg_str:
            return 0, 0
        match = re.search(r'(\d+)d(\d+)', dmg_str)
        if match:
            dice_count = int(match.group(1))
            dice_size = int(match.group(2))
            # Ortalama damage: dice_count * (dice_size + 1) / 2
            avg_damage = dice_count * (dice_size + 1) / 2
            return avg_damage, dice_size
        # Fixed damage
        match = re.search(r'(\d+)', dmg_str)
        if match:
            return float(match.group(1)), 0
        return 0, 0
    
    avg1, size1 = parse_damage(damage1)
    avg2, size2 = parse_damage(damage2)
    
    if avg1 > avg2:
        return 1
    elif avg1 < avg2:
        return -1
    elif size1 > size2:
        return 1  # Daha büyük dice = daha iyi (crit için)
    elif size1 < size2:
        return -1
    return 0


def _parse_gp_cost(cost_str: str) -> float:
    """Cost string'den gp değerini parse et"""
    import re
    if not cost_str:
        return 0.0
    
    # "10 gp", "1 sp", "5 cp" gibi formatları parse et
    match = re.search(r'(\d+(?:\.\d+)?)\s*(gp|sp|cp|pp)', cost_str.lower())
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        # Conversion: 1 gp = 10 sp = 100 cp = 0.1 pp
        if unit == "gp":
            return value
        elif unit == "sp":
            return value / 10
        elif unit == "cp":
            return value / 100
        elif unit == "pp":
            return value * 10
    
    # Sadece sayı varsa gp olarak kabul et
    match = re.search(r'(\d+(?:\.\d+)?)', cost_str)
    if match:
        return float(match.group(1))
    
    return 0.0


def _parse_ac_value(ac_str: Any) -> int:
    """AC string'den integer değerini parse et"""
    if isinstance(ac_str, int):
        return ac_str
    if isinstance(ac_str, str):
        import re
        match = re.search(r'(\d+)', str(ac_str))
        if match:
            return int(match.group(1))
    return 0


def _extract_magic_bonus_from_item(item: Dict[str, Any]) -> int:
    """Item'dan magic bonus çıkar"""
    item_name = item.get("name", "").lower()
    description = item.get("description", "").lower()
    
    import re
    
    # "+1", "+2" gibi pattern
    name_match = re.search(r'\+(\d+)', item_name)
    if name_match:
        try:
            return int(name_match.group(1))
        except ValueError:
            pass
    
    # Description'da "+1 to AC" veya "+2 to attack" gibi
    desc_match = re.search(r'\+(\d+)\s*(?:to|armor|ac|attack|damage)', description)
    if desc_match:
        try:
            return int(desc_match.group(1))
        except ValueError:
            pass
    
    return 0


def _calculate_recommendation(comparison: Dict[str, Any]) -> Optional[str]:
    """Karşılaştırmaya göre recommendation hesapla"""
    advantages1 = len(comparison.get("advantages_item1", []))
    advantages2 = len(comparison.get("advantages_item2", []))
    
    if advantages1 > advantages2:
        return f"{comparison['item1_name']} daha avantajlı görünüyor ({advantages1} avantaj)"
    elif advantages2 > advantages1:
        return f"{comparison['item2_name']} daha avantajlı görünüyor ({advantages2} avantaj)"
    elif advantages1 == advantages2 and advantages1 > 0:
        return "İki item da benzer avantajlara sahip, tercih karakterinize bağlı"
    else:
        return "İki item benzer özelliklere sahip"





