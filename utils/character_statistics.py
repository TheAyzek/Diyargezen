"""
Karakter istatistikleri ve analiz modülü
Karakter güç seviyesi, istatistikler ve analiz
"""
from typing import Dict, Any, Optional
from utils.calculations import (
    calculate_all_dnd_stats,
    calculate_all_mm_stats,
)


def analyze_character(character: dict, class_data: Optional[dict] = None) -> Dict[str, Any]:
    """
    Karakteri analiz et ve istatistikleri hesapla
    
    Args:
        character: Karakter verisi
        class_data: Sınıf verisi (D&D için)
    
    Returns:
        Analiz sonuçları
    """
    system = character.get("system", "UNKNOWN")
    
    if system == "DND5E":
        return _analyze_dnd(character, class_data)
    elif system == "MUTANTS_AND_MASTERMINDS":
        return _analyze_mm(character)
    else:
        return {
            "error": f"Bilinmeyen sistem: {system}",
            "system": system
        }


def _analyze_dnd(character: dict, class_data: Optional[dict] = None) -> Dict[str, Any]:
    """D&D karakteri analizi"""
    # Tüm istatistikleri hesapla
    stats = calculate_all_dnd_stats(character, class_data)
    
    abilities = character.get("abilities", {})
    level = character.get("level", 1)
    
    # Ability score toplamı
    total_ability_score = sum(abilities.values())
    average_ability_score = total_ability_score / len(abilities) if abilities else 0
    
    # Modifier toplamı
    modifiers = stats.get("ability_modifiers", {})
    total_modifier = sum(modifiers.values())
    average_modifier = total_modifier / len(modifiers) if modifiers else 0
    
    # Güç seviyesi skoru (basit hesaplama)
    power_score = (
        level * 10 +  # Seviye katkısı
        total_ability_score * 0.5 +  # Ability score katkısı
        stats.get("armor_class", 10) * 2 +  # AC katkısı
        stats.get("hit_points", 10) * 0.5 +  # HP katkısı
        len(character.get("spells", {}).get("cantrips", [])) * 2 +  # Cantrip sayısı
        sum(len(spells) for spells in character.get("spells", {}).values()) * 3  # Büyü sayısı
    )
    
    # Seviye bazlı değerlendirme
    level_tier = _get_dnd_level_tier(level)
    
    # Güç seviyesi kategorisi
    power_category = _categorize_power_level(power_score, level)
    
    return {
        "system": "DND5E",
        "character_name": character.get("name", "İsimsiz"),
        "level": level,
        "level_tier": level_tier,
        "stats": stats,
        "abilities": {
            "scores": abilities,
            "modifiers": modifiers,
            "total_score": total_ability_score,
            "average_score": round(average_ability_score, 1),
            "total_modifier": total_modifier,
            "average_modifier": round(average_modifier, 1),
        },
        "combat": {
            "armor_class": stats.get("armor_class", 10),
            "hit_points": stats.get("hit_points", 10),
            "proficiency_bonus": stats.get("proficiency_bonus", 2),
        },
        "magic": {
            "spell_slots": stats.get("spell_slots", {}),
            "spell_save_dc": stats.get("spell_save_dc", 0),
            "spell_attack_bonus": stats.get("spell_attack_bonus", 0),
            "total_spells": sum(len(spells) for spells in character.get("spells", {}).values()),
        },
        "power_analysis": {
            "power_score": round(power_score, 1),
            "power_category": power_category,
            "recommendations": _get_dnd_recommendations(character, stats, level)
        }
    }


def _analyze_mm(character: dict) -> Dict[str, Any]:
    """M&M karakteri analizi"""
    stats = calculate_all_mm_stats(character)
    
    abilities = character.get("abilities", {})
    power_level = character.get("power_level", "1")
    try:
        pl = int(power_level)
    except:
        pl = 1
    
    # Ability score toplamı
    total_ability_score = sum(abilities.values())
    average_ability_score = total_ability_score / len(abilities) if abilities else 0
    
    # Modifier toplamı
    modifiers = stats.get("ability_modifiers", {})
    total_modifier = sum(modifiers.values())
    
    # Güç seviyesi skoru
    defenses = character.get("defenses", {})
    power_score = (
        pl * 20 +  # Power Level katkısı
        total_ability_score * 0.3 +  # Ability score katkısı
        character.get("power_points", 0) * 0.5 +  # Power Points katkısı
        defenses.get("defense", 0) * 2 +  # Defense katkısı
        defenses.get("toughness", 0) * 2 +  # Toughness katkısı
        len(character.get("powers", [])) * 5  # Power sayısı
    )
    
    # Güç seviyesi kategorisi
    power_category = _categorize_power_level(power_score, pl)
    
    return {
        "system": "MUTANTS_AND_MASTERMINDS",
        "character_name": character.get("name", "İsimsiz"),
        "power_level": pl,
        "stats": stats,
        "abilities": {
            "scores": abilities,
            "modifiers": modifiers,
            "total_score": total_ability_score,
            "average_score": round(average_ability_score, 1),
            "total_modifier": total_modifier,
        },
        "defenses": {
            "attack_bonus": defenses.get("attack_bonus", 0),
            "effect_rank": defenses.get("effect_rank", 0),
            "defense": defenses.get("defense", 0),
            "toughness": defenses.get("toughness", 0),
        },
        "powers": {
            "power_points": character.get("power_points", 0),
            "total_powers": len(character.get("powers", [])),
            "total_advantages": len(character.get("advantages", [])),
        },
        "power_analysis": {
            "power_score": round(power_score, 1),
            "power_category": power_category,
            "recommendations": _get_mm_recommendations(character, pl)
        }
    }


def _get_dnd_level_tier(level: int) -> str:
    """D&D seviye katmanını döndür"""
    if level <= 4:
        return "Başlangıç (Tier 1)"
    elif level <= 10:
        return "Orta Seviye (Tier 2)"
    elif level <= 16:
        return "Yüksek Seviye (Tier 3)"
    else:
        return "Efsanevi (Tier 4)"


def _categorize_power_level(power_score: float, level: int) -> str:
    """Güç seviyesi kategorisini belirle"""
    # Seviye bazlı beklenen skor
    expected_score = level * 15
    
    if power_score < expected_score * 0.7:
        return "Zayıf"
    elif power_score < expected_score * 0.9:
        return "Orta"
    elif power_score < expected_score * 1.1:
        return "İyi"
    elif power_score < expected_score * 1.3:
        return "Güçlü"
    else:
        return "Çok Güçlü"


def _get_dnd_recommendations(character: dict, stats: dict, level: int) -> list:
    """D&D karakteri için öneriler"""
    recommendations = []
    
    abilities = character.get("abilities", {})
    
    # Ability score önerileri
    for ability, score in abilities.items():
        if score < 10:
            recommendations.append(f"{ability} skoru düşük ({score}). Artırmayı düşünün.")
        elif score >= 18:
            recommendations.append(f"{ability} skoru çok yüksek ({score}). İyi dengelenmiş!")
    
    # AC önerileri
    ac = stats.get("armor_class", 10)
    if ac < 13:
        recommendations.append(f"Zırh Sınıfı düşük ({ac}). Daha iyi zırh veya kalkan düşünün.")
    elif ac >= 18:
        recommendations.append(f"Zırh Sınıfı çok yüksek ({ac}). Mükemmel savunma!")
    
    # HP önerileri
    hp = stats.get("hit_points", 10)
    expected_hp = level * 8  # Basit tahmin
    if hp < expected_hp * 0.8:
        recommendations.append(f"Can Puanı düşük ({hp}). CON artırmayı veya Tough feat düşünün.")
    
    # Büyü önerileri
    total_spells = sum(len(spells) for spells in character.get("spells", {}).values())
    if total_spells == 0 and character.get("class", "").lower() in ["wizard", "sorcerer", "cleric"]:
        recommendations.append("Büyücü sınıfı için büyü sayısı az. Daha fazla büyü öğrenmeyi düşünün.")
    
    return recommendations


def _get_mm_recommendations(character: dict, power_level: int) -> list:
    """M&M karakteri için öneriler"""
    recommendations = []
    
    defenses = character.get("defenses", {})
    pl_limits = {
        1: {"defense": 5, "toughness": 5, "attack": 5, "effect": 5},
        5: {"defense": 10, "toughness": 10, "attack": 10, "effect": 10},
        10: {"defense": 15, "toughness": 15, "attack": 15, "effect": 15},
    }
    
    # PL limit kontrolü
    limit = pl_limits.get(power_level, pl_limits[10])
    if defenses.get("defense", 0) < limit["defense"] * 0.8:
        recommendations.append("Defense düşük. PL limitine yaklaşmayı düşünün.")
    
    if character.get("power_points", 0) < power_level * 15:
        recommendations.append("Power Points az. Daha fazla güç eklemeyi düşünün.")
    
    if len(character.get("powers", [])) == 0:
        recommendations.append("Hiç power yok. Karakterinize güçler ekleyin.")
    
    return recommendations

