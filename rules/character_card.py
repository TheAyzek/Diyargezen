"""
Pathfinder 1st Edition Character Showcase Card Engine
=====================================================
Structures and formats character data for high-resolution card exports and social sharing.
"""

from typing import Dict, Any, List, Optional
from rules.calculators import PF1e_Calculator


def generate_character_card_data(character: Dict[str, Any]) -> Dict[str, Any]:
    """Prepares structured summary for character showcase card rendering."""
    calc = PF1e_Calculator()
    recalced = calc.update_all_stats(character)

    name = str(character.get("name") or "İsimsiz Kahraman").strip()
    race = str(character.get("race") or "İnsan").strip()
    char_class = str(character.get("class") or "Savaşçı").strip()
    archetype = str(character.get("archetype") or "").strip()
    level = int(character.get("level") or 1)
    alignment = str(character.get("alignment") or "TN").strip()
    deity = str(character.get("deity") or "Yok").strip()
    portrait = character.get("portrait") or ""

    # Abilities
    scores = recalced.get("ability_scores", {})
    mods = recalced.get("ability_modifiers", {})
    abilities_list = []
    for ab in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
        val = scores.get(ab, 10)
        m = mods.get(ab, 0)
        abilities_list.append({
            "name": ab[:3].upper(),
            "full_name": ab,
            "score": val,
            "modifier": f"+{m}" if m >= 0 else str(m)
        })

    # Saves
    saves = recalced.get("saving_throws", {})
    fort = saves.get("Fortitude", 0)
    ref = saves.get("Reflex", 0)
    will = saves.get("Will", 0)

    # Top Weapons
    weapons = recalced.get("weapons", [])
    top_weapons = []
    for w in weapons[:2]:
        top_weapons.append({
            "name": w.get("name") or w.get("isim") or "Silah",
            "attack": w.get("calculated_attack") or "+0",
            "damage": w.get("calculated_damage") or "1d8"
        })

    # Physical
    physical = recalced.get("physical_traits", {})

    return {
        "identity": {
            "name": name,
            "race": race,
            "class": char_class,
            "archetype": archetype,
            "level": level,
            "alignment": alignment,
            "deity": deity,
            "title": f"{race} {char_class} {f'({archetype})' if archetype else ''} Seviye {level}",
            "portrait": portrait
        },
        "abilities": abilities_list,
        "combat": {
            "hp": recalced.get("hit_points", 10),
            "ac": recalced.get("armor_class", 10),
            "touch_ac": recalced.get("touch_ac", 10),
            "flat_footed_ac": recalced.get("flat_footed_ac", 10),
            "initiative": f"+{recalced.get('initiative', 0)}" if (recalced.get('initiative', 0) >= 0) else str(recalced.get('initiative', 0)),
            "speed": f"{recalced.get('speed', 30)} ft",
            "bab": f"+{recalced.get('bab', 0)}",
            "cmb": f"+{recalced.get('cmb', 0)}",
            "cmd": recalced.get("cmd", 10)
        },
        "saves": {
            "fortitude": f"+{fort}" if fort >= 0 else str(fort),
            "reflex": f"+{ref}" if ref >= 0 else str(ref),
            "will": f"+{will}" if will >= 0 else str(will)
        },
        "weapons": top_weapons,
        "spellcasting": {
            "caster_level": recalced.get("spellcasting", {}).get("caster_level"),
            "concentration": recalced.get("spellcasting", {}).get("concentration_bonus")
        } if recalced.get("spellcasting") else None,
        "physical": physical
    }
