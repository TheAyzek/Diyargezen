"""
Pathfinder 1st Edition Armor & Shield Special Abilities Engine
==============================================================
References:
- PF1e Core Rulebook Chapter 15 (Table 15-4 & 15-5: Armor & Shield Special Abilities, p. 463-466)
- Ultimate Equipment (Magic Armor and Shields)

Rules:
- Base enhancement bonus must be at least +1 before special abilities can be added.
- Total effective bonus (Enhancement + Abilities) cannot exceed +10.
- Price: (Total Effective Bonus)^2 * 1,000 gp + 150 gp (Masterwork) + Base Armor Cost + Sum(Flat GP Costs).
"""

from typing import Dict, Any, List, Optional


ARMOR_SPECIAL_ABILITIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "glamered": {
        "name": "Glamered",
        "name_tr": "Göz Alıcı (Glamered)",
        "bonus_equivalent": 0,
        "flat_cost_gp": 2700,
        "target": "armor",
        "desc": "Komut verildiğinde normal şık bir kıyafet görünümüne bürünür."
    },
    "fortification_light": {
        "name": "Light Fortification",
        "name_tr": "Hafif Tahkimat (Light Fortification)",
        "bonus_equivalent": 1,
        "flat_cost_gp": 0,
        "crit_negation_pct": 25,
        "desc": "%25 ihtimalle kritik vuruş ve Sneak Attack hasarını normal hasara dönüştürür."
    },
    "fortification_medium": {
        "name": "Medium Fortification",
        "name_tr": "Orta Tahkimat (Medium Fortification)",
        "bonus_equivalent": 3,
        "flat_cost_gp": 0,
        "crit_negation_pct": 50,
        "desc": "%50 ihtimalle kritik vuruş ve Sneak Attack hasarını normal hasara dönüştürür."
    },
    "fortification_heavy": {
        "name": "Heavy Fortification",
        "name_tr": "Ağır Tahkimat (Heavy Fortification)",
        "bonus_equivalent": 5,
        "flat_cost_gp": 0,
        "crit_negation_pct": 75,
        "desc": "%75 ihtimalle kritik vuruş ve Sneak Attack hasarını normal hasara dönüştürür."
    },
    "shadow": {
        "name": "Shadow",
        "name_tr": "Gölge (Shadow)",
        "bonus_equivalent": 0,
        "flat_cost_gp": 3750,
        "skill_bonuses": {"Stealth": 5},
        "target": "armor",
        "desc": "Gizlilik (Stealth) kontrollerine +5 yetkinlik bonusu sağlar."
    },
    "improved_shadow": {
        "name": "Improved Shadow",
        "name_tr": "Gelişmiş Gölge (Improved Shadow)",
        "bonus_equivalent": 0,
        "flat_cost_gp": 15000,
        "skill_bonuses": {"Stealth": 10},
        "target": "armor",
        "desc": "Gizlilik (Stealth) kontrollerine +10 yetkinlik bonusu sağlar."
    },
    "greater_shadow": {
        "name": "Greater Shadow",
        "name_tr": "Kadim Gölge (Greater Shadow)",
        "bonus_equivalent": 0,
        "flat_cost_gp": 33750,
        "skill_bonuses": {"Stealth": 15},
        "target": "armor",
        "desc": "Gizlilik (Stealth) kontrollerine +15 yetkinlik bonusu sağlar."
    },
    "slick": {
        "name": "Slick",
        "name_tr": "Kaygan (Slick)",
        "bonus_equivalent": 0,
        "flat_cost_gp": 3750,
        "skill_bonuses": {"Escape Artist": 5},
        "target": "armor",
        "desc": "Kaçış Sanatı (Escape Artist) kontrollerine +5 bonus sağlar."
    },
    "improved_slick": {
        "name": "Improved Slick",
        "name_tr": "Gelişmiş Kaygan (Improved Slick)",
        "bonus_equivalent": 0,
        "flat_cost_gp": 15000,
        "skill_bonuses": {"Escape Artist": 10},
        "target": "armor",
        "desc": "Kaçış Sanatı (Escape Artist) kontrollerine +10 bonus sağlar."
    },
    "spell_resistance_13": {
        "name": "Spell Resistance (13)",
        "name_tr": "Büyü Direnci (SR 13)",
        "bonus_equivalent": 2,
        "flat_cost_gp": 0,
        "sr": 13,
        "desc": "Kullanıcıya 13 Büyü Direnci (Spell Resistance) kazandırır."
    },
    "spell_resistance_15": {
        "name": "Spell Resistance (15)",
        "name_tr": "Büyü Direnci (SR 15)",
        "bonus_equivalent": 3,
        "flat_cost_gp": 0,
        "sr": 15,
        "desc": "Kullanıcıya 15 Büyü Direnci (Spell Resistance) kazandırır."
    },
    "spell_resistance_17": {
        "name": "Spell Resistance (17)",
        "name_tr": "Büyü Direnci (SR 17)",
        "bonus_equivalent": 4,
        "flat_cost_gp": 0,
        "sr": 17,
        "desc": "Kullanıcıya 17 Büyü Direnci (Spell Resistance) kazandırır."
    },
    "spell_resistance_19": {
        "name": "Spell Resistance (19)",
        "name_tr": "Büyü Direnci (SR 19)",
        "bonus_equivalent": 5,
        "flat_cost_gp": 0,
        "sr": 19,
        "desc": "Kullanıcıya 19 Büyü Direnci (Spell Resistance) kazandırır."
    },
    "energy_resistance": {
        "name": "Energy Resistance",
        "name_tr": "Enerji Direnci (Energy Resistance)",
        "bonus_equivalent": 0,
        "flat_cost_gp": 18000,
        "energy_resistance": 10,
        "desc": "Seçilen bir element türüne karşı 10 puan enerji direnci kazandırır."
    },
    "animated": {
        "name": "Animated",
        "name_tr": "Süzülen (Animated)",
        "bonus_equivalent": 2,
        "flat_cost_gp": 0,
        "target": "shield",
        "desc": "Kalkan el kullanılmadan havada süzülerek +2 kalkan AC sağlar (İki el serbest)."
    },
    "arrow_catching": {
        "name": "Arrow Catching",
        "name_tr": "Ok Çeken (Arrow Catching)",
        "bonus_equivalent": 1,
        "flat_cost_gp": 0,
        "target": "shield",
        "desc": "Menzilli saldırılara karşı +1 AC ve yakınındaki dostlarına gelen okları üstüne çeker."
    },
    "arrow_deflection": {
        "name": "Arrow Deflection",
        "name_tr": "Ok Saptıran (Arrow Deflection)",
        "bonus_equivalent": 2,
        "flat_cost_gp": 0,
        "target": "shield",
        "desc": "Turda 1 kez normal menzilli saldırıyı saptırır."
    },
    "bashing": {
        "name": "Bashing",
        "name_tr": "Darbe Kalkanı (Bashing)",
        "bonus_equivalent": 1,
        "flat_cost_gp": 0,
        "target": "shield",
        "desc": "Kalkan darbesi hasarını 2 boy büyük sayar ve +1 büyülü silah kabul edilir."
    }
}


def calculate_armor_magical_properties(
    armor: Dict[str, Any],
    base_enhancement: int = 1,
    applied_abilities: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculates total AC bonus, skill modifiers, SR, crit negations and GP market price for armor/shield.
    """
    applied = applied_abilities or []
    base_enh = max(0, int(base_enhancement or 0))
    armor_name = armor.get("name") or armor.get("isim") or "Büyülü Zırh"
    base_ac = int(armor.get("ac_bonus") or armor.get("ac") or armor.get("zirh_bonusu") or 4)
    base_cost = int(armor.get("cost_gp") or armor.get("fiyat") or 100)
    is_shield = bool(armor.get("is_shield") or "shield" in str(armor.get("type", "")).lower())

    warnings = []

    if base_enh < 1 and len(applied) > 0:
        warnings.append("Özel nitelik eklenebilmesi için zırh/kalkanın en az +1 temel geliştirme bonusuna sahip olması gerekir.")

    total_ability_bonus = 0
    total_flat_cost = 0
    skill_bonuses = {}
    crit_negation_pct = 0
    spell_resistance = 0
    energy_resistance = 0
    is_animated = False

    for ab_key in applied:
        clean_key = ab_key.lower().strip()
        if clean_key in ARMOR_SPECIAL_ABILITIES_REGISTRY:
            data = ARMOR_SPECIAL_ABILITIES_REGISTRY[clean_key]
            total_ability_bonus += data.get("bonus_equivalent", 0)
            total_flat_cost += data.get("flat_cost_gp", 0)

            if "crit_negation_pct" in data:
                crit_negation_pct = max(crit_negation_pct, data["crit_negation_pct"])

            if "sr" in data:
                spell_resistance = max(spell_resistance, data["sr"])

            if "energy_resistance" in data:
                energy_resistance = max(energy_resistance, data["energy_resistance"])

            if "skill_bonuses" in data:
                for sk, val in data["skill_bonuses"].items():
                    skill_bonuses[sk] = skill_bonuses.get(sk, 0) + val

            if clean_key == "animated":
                is_animated = True

    total_effective_bonus = base_enh + total_ability_bonus

    if total_effective_bonus > 10:
        warnings.append(f"Toplam eşdeğer geliştirme bonusu (+{total_effective_bonus}) izin verilen +10 tavanını aşıyor.")

    total_ac_bonus = base_ac + base_enh

    # Market Price in GP (CRB Table 15-4)
    # Masterwork component = 150 gp
    if total_effective_bonus > 0:
        market_price = (total_effective_bonus ** 2) * 1000 + 150 + base_cost + total_flat_cost
    else:
        market_price = base_cost + total_flat_cost

    crafting_cost = market_price // 2

    return {
        "armor_name": armor_name,
        "is_shield": is_shield,
        "base_ac": base_ac,
        "base_enhancement": base_enh,
        "total_effective_bonus": total_effective_bonus,
        "total_ac_bonus": total_ac_bonus,
        "skill_bonuses": skill_bonuses,
        "crit_negation_pct": crit_negation_pct,
        "spell_resistance": spell_resistance,
        "energy_resistance": energy_resistance,
        "is_animated": is_animated,
        "market_price_gp": market_price,
        "crafting_cost_gp": crafting_cost,
        "warnings": warnings,
        "is_valid": len(warnings) == 0
    }


def get_armor_abilities_catalog() -> Dict[str, Any]:
    """Returns complete catalog of armor and shield special abilities."""
    return {
        "abilities": ARMOR_SPECIAL_ABILITIES_REGISTRY
    }
