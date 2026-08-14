"""
Pathfinder 1st Edition Spellbook Scribing & Scroll Crafting Cost Engine
=======================================================================
References:
- PF1e Core Rulebook p. 219 (Writing a New Spell into a Spellbook, Table 9-3)
- PF1e Core Rulebook p. 550 (Scribe Scroll Feat, Scroll Creation Rules)

Formulas:
- Spellbook Pages: 1 page for Level 0, Level pages for Level 1..9 (100 pages per volume)
- Scribing Ink Cost: Level^2 * 10 gp (5 gp for Level 0)
- Decipher Spellcraft DC: 20 + Spell Level (or Read Magic)
- Write Spellcraft DC: 15 + Spell Level (Time: 1 hour per spell level, 30 min for 0)
- Scroll Creation Cost: (Spell Level * Caster Level * 25 gp) / 2
"""

import math
from typing import Dict, Any, List, Optional


SCRIBING_DATA_BY_LEVEL = {
    0: {"pages": 1, "cost_gp": 5.0, "dc_write": 15, "dc_decipher": 20, "time_hours": 0.5},
    1: {"pages": 1, "cost_gp": 10.0, "dc_write": 16, "dc_decipher": 21, "time_hours": 1.0},
    2: {"pages": 2, "cost_gp": 40.0, "dc_write": 17, "dc_decipher": 22, "time_hours": 2.0},
    3: {"pages": 3, "cost_gp": 90.0, "dc_write": 18, "dc_decipher": 23, "time_hours": 3.0},
    4: {"pages": 4, "cost_gp": 160.0, "dc_write": 19, "dc_decipher": 24, "time_hours": 4.0},
    5: {"pages": 5, "cost_gp": 250.0, "dc_write": 20, "dc_decipher": 25, "time_hours": 5.0},
    6: {"pages": 6, "cost_gp": 360.0, "dc_write": 21, "dc_decipher": 26, "time_hours": 6.0},
    7: {"pages": 7, "cost_gp": 490.0, "dc_write": 22, "dc_decipher": 27, "time_hours": 7.0},
    8: {"pages": 8, "cost_gp": 640.0, "dc_write": 23, "dc_decipher": 28, "time_hours": 8.0},
    9: {"pages": 9, "cost_gp": 810.0, "dc_write": 24, "dc_decipher": 29, "time_hours": 9.0},
}


def extract_spell_level(spell_item: Any) -> int:
    """Extracts integer spell level (0..9) from various spell payload formats."""
    if spell_item is None:
        return 1

    if isinstance(spell_item, int):
        return max(0, min(9, spell_item))

    if isinstance(spell_item, dict):
        for k in ("level", "seviye"):
            if k in spell_item and spell_item[k] is not None:
                try:
                    return max(0, min(9, int(spell_item[k])))
                except (ValueError, TypeError):
                    pass
        sv = spell_item.get("sistem_verisi") or spell_item.get("system_data") or {}
        if isinstance(sv, dict):
            for k in ("level", "seviye"):
                if k in sv and sv[k] is not None:
                    try:
                        return max(0, min(9, int(sv[k])))
                    except (ValueError, TypeError):
                        pass
            sys_obj = sv.get("system", {}) if isinstance(sv.get("system"), dict) else {}
            for k in ("level", "spell_level"):
                if k in sys_obj and sys_obj[k] is not None:
                    try:
                        return max(0, min(9, int(sys_obj[k])))
                    except (ValueError, TypeError):
                        pass

    return 1


def calculate_spellbook_pages_and_cost(
    spells_list: List[Any],
    book_size: int = 100
) -> Dict[str, Any]:
    """Calculates total pages used, ink cost in gp, volume count, and per-spell breakdown."""
    total_pages = 0
    total_cost_gp = 0.0
    spells_breakdown = []

    for spell in spells_list or []:
        lvl = extract_spell_level(spell)
        data = SCRIBING_DATA_BY_LEVEL.get(lvl, SCRIBING_DATA_BY_LEVEL[1])

        name = "Bilinmeyen Büyü"
        if isinstance(spell, dict):
            name = spell.get("isim") or spell.get("name") or name
        elif isinstance(spell, str):
            name = spell

        total_pages += data["pages"]
        total_cost_gp += data["cost_gp"]

        spells_breakdown.append({
            "name": name,
            "level": lvl,
            "pages": data["pages"],
            "cost_gp": data["cost_gp"],
            "dc_write": data["dc_write"],
            "dc_decipher": data["dc_decipher"],
            "time_hours": data["time_hours"]
        })

    capacity = max(1, int(book_size or 100))
    books_needed = max(1, math.ceil(total_pages / capacity))
    current_book_pages = total_pages % capacity if total_pages % capacity != 0 or total_pages == 0 else capacity
    percentage = round((total_pages / capacity) * 100, 1)

    return {
        "total_spells": len(spells_list or []),
        "total_pages_used": total_pages,
        "book_capacity": capacity,
        "books_needed": books_needed,
        "current_book_pages": current_book_pages,
        "percentage": percentage,
        "total_cost_gp": total_cost_gp,
        "is_overflow": total_pages > capacity,
        "spells_breakdown": spells_breakdown
    }


def calculate_scroll_crafting_cost(
    spell_level: int,
    caster_level: Optional[int] = None
) -> Dict[str, Any]:
    """Calculates Scribe Scroll market price and crafting cost (CRB p. 550)."""
    lvl = max(0, min(9, int(spell_level or 0)))
    
    # Default minimum caster level for spell level if not provided
    MIN_CL_BY_LEVEL = {0: 1, 1: 1, 2: 3, 3: 5, 4: 7, 5: 9, 6: 11, 7: 13, 8: 15, 9: 17}
    min_cl = MIN_CL_BY_LEVEL.get(lvl, 1)
    cl = max(min_cl, int(caster_level or min_cl))

    if lvl == 0:
        base_market_price = 12.5
    else:
        base_market_price = float(lvl * cl * 25)

    crafting_cost_gp = base_market_price / 2.0
    crafting_days = max(1, math.ceil(base_market_price / 1000.0))

    return {
        "spell_level": lvl,
        "caster_level": cl,
        "min_caster_level": min_cl,
        "market_price_gp": base_market_price,
        "crafting_cost_gp": crafting_cost_gp,
        "crafting_days": crafting_days
    }
