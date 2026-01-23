"""
Kural Önizleme Modülü
Yüklenen kuralları okunabilir formatta gösterir.
"""

from typing import Dict, Any


def format_rule_preview(rules: Dict[str, Any]) -> str:
    """
    Kuralları okunabilir formatta formatla
    
    Returns:
        Formatlanmış kural metni
    """
    if not rules:
        return "❌ Kural yüklenmemiş."
    
    lines = []
    lines.append("=" * 60)
    lines.append("📚 KURAL ÖNİZLEME")
    lines.append("=" * 60)
    lines.append("")
    
    # Sistem bilgisi
    system = rules.get("system", "Bilinmeyen")
    lines.append(f"🎲 Sistem: {system}")
    lines.append("")
    
    rules_dict = rules.get("rules", {})
    if not rules_dict:
        lines.append("ℹ️ Hiçbir özel kural tanımlanmamış.")
        lines.append("   Varsayılan hesaplamalar kullanılacak.")
        return "\n".join(lines)
    
    lines.append(f"📋 Tanımlı Kurallar ({len(rules_dict)} adet):")
    lines.append("")
    
    # D&D kuralları
    if system == "DND5E":
        lines.extend(_format_dnd_rules(rules_dict))
    
    # M&M kuralları
    elif system == "MUTANTS_AND_MASTERMINDS":
        lines.extend(_format_mm_rules(rules_dict))
    
    # VtM kuralları
    elif system == "VTM5E":
        lines.extend(_format_vtm_rules(rules_dict))
    
    # Genel format (bilinmeyen sistem)
    else:
        lines.extend(_format_generic_rules(rules_dict))
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def _format_dnd_rules(rules_dict: Dict[str, Any]) -> list[str]:
    """D&D kurallarını formatla"""
    lines = []
    
    # Proficiency Bonus
    if "proficiency_bonus" in rules_dict:
        prof_rule = rules_dict["proficiency_bonus"]
        lines.append("🎯 Proficiency Bonus:")
        if prof_rule.get("type") == "table":
            data = prof_rule.get("data", {})
            if data:
                lines.append("   Seviye Aralığı → Bonus")
                for level_range, bonus in sorted(data.items(), key=lambda x: _parse_range(x[0])):
                    lines.append(f"   • {level_range:15} → +{bonus}")
            else:
                lines.append("   (Tablo boş)")
        lines.append("")
    
    # Armor Class
    if "armor_class" in rules_dict:
        armor_rule = rules_dict["armor_class"]
        lines.append("🛡️ Armor Class:")
        if armor_rule.get("type") == "armor_table":
            data = armor_rule.get("data", {})
            if data:
                lines.append("   Zırh Türü → AC Hesaplama")
                for armor_name, armor_info in data.items():
                    base = armor_info.get("base", "?")
                    max_dex = armor_info.get("max_dex")
                    allows_dex = armor_info.get("allows_dex", True)
                    
                    if allows_dex:
                        if max_dex is not None:
                            ac_desc = f"AC {base} + Dex (max +{max_dex})"
                        else:
                            ac_desc = f"AC {base} + Dex"
                    else:
                        ac_desc = f"AC {base} (Dex yok)"
                    
                    lines.append(f"   • {armor_name:20} → {ac_desc}")
            else:
                lines.append("   (Tablo boş)")
        lines.append("")
    
    # Hit Dice
    if "hit_dice" in rules_dict:
        hit_dice_rule = rules_dict["hit_dice"]
        lines.append("❤️ Hit Dice:")
        if hit_dice_rule.get("type") == "table":
            data = hit_dice_rule.get("data", {})
            if data:
                lines.append("   Sınıf → Hit Dice")
                for class_name, dice_value in sorted(data.items()):
                    lines.append(f"   • {class_name:20} → d{dice_value}")
            else:
                lines.append("   (Tablo boş)")
        lines.append("")
    
    return lines


def _format_mm_rules(rules_dict: Dict[str, Any]) -> list[str]:
    """M&M kurallarını formatla"""
    lines = []
    
    # Power Levels
    if "power_levels" in rules_dict:
        pl_rule = rules_dict["power_levels"]
        lines.append("⚡ Power Levels:")
        if pl_rule.get("type") == "table":
            data = pl_rule.get("data", {})
            if data:
                lines.append("   Power Level → Power Points")
                for pl_key, pl_info in sorted(data.items(), key=lambda x: _parse_pl_key(x[0])):
                    if isinstance(pl_info, dict):
                        pp = pl_info.get("power_points", "?")
                        lines.append(f"   • {pl_key:20} → {pp} Power Points")
                    else:
                        lines.append(f"   • {pl_key:20} → {pl_info}")
            else:
                lines.append("   (Tablo boş)")
        lines.append("")
    
    return lines


def _format_vtm_rules(rules_dict: Dict[str, Any]) -> list[str]:
    """VtM kurallarını formatla"""
    lines = []
    
    # Health
    if "health" in rules_dict:
        health_rule = rules_dict["health"]
        lines.append("❤️ Health:")
        base = health_rule.get("base", "?")
        attribute = health_rule.get("attribute", "?")
        lines.append(f"   Health = {base} + {attribute}")
        lines.append("")
    
    # Willpower
    if "willpower" in rules_dict:
        willpower_rule = rules_dict["willpower"]
        lines.append("🧠 Willpower:")
        attributes = willpower_rule.get("attributes", [])
        if len(attributes) == 2:
            lines.append(f"   Willpower = {attributes[0]} + {attributes[1]}")
        else:
            lines.append(f"   Willpower = {', '.join(attributes)}")
        lines.append("")
    
    return lines


def _format_generic_rules(rules_dict: Dict[str, Any]) -> list[str]:
    """Genel kural formatı (bilinmeyen sistem)"""
    lines = []
    
    for rule_name, rule_data in rules_dict.items():
        lines.append(f"📌 {rule_name}:")
        if isinstance(rule_data, dict):
            rule_type = rule_data.get("type", "bilinmeyen")
            lines.append(f"   Tip: {rule_type}")
            
            if "data" in rule_data:
                data = rule_data["data"]
                if isinstance(data, dict):
                    lines.append("   Veriler:")
                    for key, value in list(data.items())[:10]:  # İlk 10 öğe
                        lines.append(f"   • {key}: {value}")
                    if len(data) > 10:
                        lines.append(f"   ... ve {len(data) - 10} öğe daha")
                else:
                    lines.append(f"   Veri: {data}")
        else:
            lines.append(f"   Değer: {rule_data}")
        lines.append("")
    
    return lines


def _parse_range(range_str: str) -> tuple[int, int]:
    """Aralık string'ini parse et (sıralama için)"""
    try:
        if '-' in range_str:
            start, end = map(int, range_str.split('-'))
            return (start, end)
        else:
            val = int(range_str)
            return (val, val)
    except (ValueError, AttributeError):
        return (0, 0)


def _parse_pl_key(pl_key: str) -> int:
    """Power Level key'ini parse et (sıralama için)"""
    try:
        # "PL10" -> 10
        if pl_key.startswith("PL"):
            return int(pl_key[2:])
        return int(pl_key)
    except (ValueError, AttributeError):
        return 0

