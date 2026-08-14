"""
Pathfinder 1st Edition Alchemy & Magic Item Crafting Engine
============================================================
References:
- PF1e Core Rulebook Chapter 15 (Magic Item Creation)
- Advanced Player's Guide (Alchemist Class, Extracts & Mutagens)
- Ultimate Magic (UM)

Mechanics:
- Brew Potion: Max 3rd level spells. Base Price = Spell Level * CL * 50 gp. Raw Cost = 50%.
- Craft Wondrous Item / Arms & Armor: Raw Cost = 50% market price. 1 day per 1,000 gp. DC = 5 + CL (+5 per missing prereq).
- Craft Wand: 50 charges. Base Price = Spell Level * CL * 750 gp. Raw Cost = 50%.
- Alchemist Mutagen: +4 alchemical bonus to physical stat, +2 natural AC, -2 penalty to mental stat. 10 min/lvl.
"""

import math
from typing import Dict, Any, List, Optional


MUTAGEN_REGISTRY: Dict[str, Dict[str, Any]] = {
    "strength": {
        "name": "Kuvvet Mutajeni (Strength Mutagen)",
        "physical_bonus": {"Strength": 4},
        "mental_penalty": {"Intelligence": -2},
        "natural_armor_bonus": 2,
        "description": "+4 Kuvvet, +2 Doğal Zırh, -2 Zeka (Süre: 10 dk / Seviye)"
    },
    "dexterity": {
        "name": "Çeviklik Mutajeni (Dexterity Mutagen)",
        "physical_bonus": {"Dexterity": 4},
        "mental_penalty": {"Wisdom": -2},
        "natural_armor_bonus": 2,
        "description": "+4 Çeviklik, +2 Doğal Zırh, -2 İrade/Bilgelik (Süre: 10 dk / Seviye)"
    },
    "constitution": {
        "name": "Dayanıklılık Mutajeni (Constitution Mutagen)",
        "physical_bonus": {"Constitution": 4},
        "mental_penalty": {"Charisma": -2},
        "natural_armor_bonus": 2,
        "description": "+4 Dayanıklılık, +2 Doğal Zırh, -2 Karizma (Süre: 10 dk / Seviye)"
    },
    "greater_strength": {
        "name": "Büyük Kuvvet Mutajeni (Greater Strength)",
        "physical_bonus": {"Strength": 6, "Dexterity": 4},
        "mental_penalty": {"Intelligence": -2, "Wisdom": -2},
        "natural_armor_bonus": 4,
        "description": "+6 Kuvvet, +4 Çeviklik, +4 Doğal Zırh, -2 Zeka, -2 Bilgelik"
    },
    "greater_dexterity": {
        "name": "Büyük Çeviklik Mutajeni (Greater Dexterity)",
        "physical_bonus": {"Dexterity": 6, "Constitution": 4},
        "mental_penalty": {"Wisdom": -2, "Charisma": -2},
        "natural_armor_bonus": 4,
        "description": "+6 Çeviklik, +4 Dayanıklılık, +4 Doğal Zırh, -2 Bilgelik, -2 Karizma"
    },
    "greater_constitution": {
        "name": "Büyük Dayanıklılık Mutajeni (Greater Constitution)",
        "physical_bonus": {"Constitution": 6, "Strength": 4},
        "mental_penalty": {"Charisma": -2, "Intelligence": -2},
        "natural_armor_bonus": 4,
        "description": "+6 Dayanıklılık, +4 Kuvvet, +4 Doğal Zırh, -2 Karizma, -2 Zeka"
    },
    "grand_mutagen": {
        "name": "Kadim Mutajen (Grand Mutagen)",
        "physical_bonus": {"Strength": 8, "Dexterity": 6, "Constitution": 4},
        "mental_penalty": {"Intelligence": -2, "Wisdom": -2, "Charisma": -2},
        "natural_armor_bonus": 6,
        "description": "+8 Kuvvet, +6 Çeviklik, +4 Dayanıklılık, +6 Doğal Zırh, -2 Zeka, -2 Bilgelik, -2 Karizma"
    }
}


CRAFTING_FEATS_CATALOG: Dict[str, Dict[str, Any]] = {
    "brew_potion": {
        "name": "Brew Potion",
        "isim_tr": "İksir Üretimi",
        "prereq": "Caster level 3rd",
        "max_spell_level": 3,
        "formula": "Büyü Seviyesi * CL * 50 gp",
        "cost_ratio": 0.5
    },
    "craft_wondrous_item": {
        "name": "Craft Wondrous Item",
        "isim_tr": "Harika Eşya Üretimi",
        "prereq": "Caster level 3rd",
        "formula": "Piyasa Fiyatı / 2",
        "cost_ratio": 0.5
    },
    "craft_magic_arms_armor": {
        "name": "Craft Magic Arms and Armor",
        "isim_tr": "Büyülü Silah ve Zırh Üretimi",
        "prereq": "Caster level 5th",
        "formula": "Geliştirme Maliyeti / 2 + Temel Eşya",
        "cost_ratio": 0.5
    },
    "craft_wand": {
        "name": "Craft Wand",
        "isim_tr": "Asa Üretimi (50 Şarj)",
        "prereq": "Caster level 5th",
        "max_spell_level": 4,
        "formula": "Büyü Seviyesi * CL * 750 gp",
        "cost_ratio": 0.5
    },
    "forge_ring": {
        "name": "Forge Ring",
        "isim_tr": "Yüzük Dövme",
        "prereq": "Caster level 7th",
        "formula": "Piyasa Fiyatı / 2",
        "cost_ratio": 0.5
    },
    "craft_rod": {
        "name": "Craft Rod",
        "isim_tr": "Asa/Çubuk Üretimi (Rod)",
        "prereq": "Caster level 9th",
        "formula": "Piyasa Fiyatı / 2",
        "cost_ratio": 0.5
    },
    "craft_staff": {
        "name": "Craft Staff",
        "isim_tr": "Büyücü Asası (Staff)",
        "prereq": "Caster level 11th",
        "formula": "Piyasa Fiyatı / 2",
        "cost_ratio": 0.5
    }
}


def calculate_mutagen_effects(
    mutagen_type: str = "strength",
    alchemist_level: int = 1
) -> Dict[str, Any]:
    """Calculates active mutagen modifiers, duration, and natural armor."""
    clean_type = (mutagen_type or "strength").lower().strip().replace(" ", "_")
    config = MUTAGEN_REGISTRY.get(clean_type, MUTAGEN_REGISTRY["strength"])
    lvl = max(1, int(alchemist_level or 1))

    duration_minutes = lvl * 10

    return {
        "type": clean_type,
        "name": config["name"],
        "duration_minutes": duration_minutes,
        "duration_formatted": f"{duration_minutes} Dakika ({duration_minutes // 60} saat {duration_minutes % 60} dk)" if duration_minutes >= 60 else f"{duration_minutes} Dakika",
        "physical_bonus": config["physical_bonus"],
        "mental_penalty": config["mental_penalty"],
        "natural_armor_bonus": config["natural_armor_bonus"],
        "description": config["description"]
    }


def calculate_potion_crafting(
    spell_name: str = "Cure Light Wounds",
    spell_level: int = 1,
    caster_level: int = 1
) -> Dict[str, Any]:
    """Calculates potion market price, crafting cost, time, and DC."""
    s_lvl = max(0, int(spell_level))
    cl = max(1, int(caster_level))
    warnings = []

    if s_lvl > 3:
        warnings.append(f"İksirler en fazla 3. seviye büyü içerebilir ({s_lvl}. Seviye geçersizdir).")

    # CRB p. 550: 0-level spells count as 1/2 level for price calculation (0.5 * CL * 50 = 25 * CL)
    if s_lvl == 0:
        market_price = 25 * cl
    else:
        market_price = s_lvl * cl * 50

    raw_cost = market_price // 2

    if market_price <= 250:
        crafting_time = "2 Saat"
        crafting_days = 0.25
    else:
        days = math.ceil(market_price / 1000)
        crafting_time = f"{days} Gün"
        crafting_days = days

    spellcraft_dc = 5 + cl

    return {
        "item_name": f"{spell_name} İksiri",
        "spell_level": s_lvl,
        "caster_level": cl,
        "market_price_gp": market_price,
        "raw_cost_gp": raw_cost,
        "crafting_time": crafting_time,
        "crafting_days": crafting_days,
        "spellcraft_dc": spellcraft_dc,
        "warnings": warnings,
        "is_valid": len(warnings) == 0
    }


def calculate_magic_item_crafting(
    item_name: str,
    item_type: str = "wondrous",
    market_price_gp: int = 1000,
    item_cl: int = 1,
    missing_prereqs_count: int = 0
) -> Dict[str, Any]:
    """Calculates crafting raw cost, crafting days, and Spellcraft DC."""
    price = max(1, int(market_price_gp))
    cl = max(1, int(item_cl))
    missing = max(0, int(missing_prereqs_count))

    raw_cost = price // 2
    crafting_days = max(1, math.ceil(price / 1000))
    base_dc = 5 + cl
    final_dc = base_dc + (missing * 5)

    return {
        "item_name": item_name,
        "item_type": item_type,
        "market_price_gp": price,
        "raw_cost_gp": raw_cost,
        "crafting_days": crafting_days,
        "crafting_time_formatted": f"{crafting_days} Gün (8 saat/gün)",
        "base_spellcraft_dc": base_dc,
        "missing_prereqs_count": missing,
        "final_spellcraft_dc": final_dc,
        "is_valid": True
    }


def get_crafting_catalog() -> Dict[str, Any]:
    """Returns complete alchemy & item creation catalog."""
    return {
        "mutagens": MUTAGEN_REGISTRY,
        "crafting_feats": CRAFTING_FEATS_CATALOG
    }
