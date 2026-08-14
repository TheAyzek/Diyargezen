"""
Pathfinder 1st Edition Official Paizo Statblock & JSON Portability Engine
========================================================================
References:
- Paizo PF1e Core Rulebook Appendix (Official Monster & NPC Stat Block Format)
- Paizo Adventure Paths & Bestiaries (Statblock Standards)

Sections:
1. Header & Identity
2. DEFENSE (AC, hp, Fort/Ref/Will, Defensive Abilities, DR, Immune, SR)
3. OFFENSE (Speed, Melee, Ranged, Special Attacks, Spells)
4. STATISTICS (Abilities, BAB, CMB, CMD, Feats, Skills, Languages, Gear)
5. SPECIAL ABILITIES
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional


def format_mod(val: int) -> str:
    """Formats numeric modifier with explicit + or - sign."""
    return f"+{val}" if val >= 0 else str(val)


def generate_paizo_statblock(
    character_data: Dict[str, Any],
    recalced_data: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Generates standard Paizo statblock in Plain Text, Markdown, and BBCode formats.
    """
    c = character_data or {}
    r = recalced_data or c.get("recalcedData") or c.get("derived") or {}

    name = c.get("name") or "İsimsiz Kahraman"
    char_class = c.get("class") or "Fighter"
    level = c.get("level") or 1
    race = c.get("race") or "Human"
    alignment = c.get("alignment") or "TN"
    size = c.get("size") or "Medium"
    deity = c.get("deity") or ""

    # Abilities & Mods
    scores = c.get("scores") or c.get("abilities") or {
        "Strength": 10, "Dexterity": 10, "Constitution": 10,
        "Intelligence": 10, "Wisdom": 10, "Charisma": 10
    }
    
    # Calculate modifiers
    mods = {}
    for ab, score in scores.items():
        mods[ab] = (int(score) - 10) // 2

    # Derived Combat Stats
    hp = r.get("hit_points") or r.get("hp") or (10 + (int(level) - 1) * 6 + mods.get("Constitution", 0) * int(level))
    ac_dict = r.get("armor_class") or {}
    ac_total = ac_dict.get("total") or 10 + mods.get("Dexterity", 0)
    ac_touch = ac_dict.get("touch") or 10 + mods.get("Dexterity", 0)
    ac_ff = ac_dict.get("flat_footed") or 10

    saves_dict = r.get("saving_throws") or {}
    fort = saves_dict.get("fortitude") or saves_dict.get("fort") or (mods.get("Constitution", 0) + 2)
    ref = saves_dict.get("reflex") or saves_dict.get("ref") or (mods.get("Dexterity", 0))
    will = saves_dict.get("will") or (mods.get("Wisdom", 0))

    init_val = r.get("initiative") or mods.get("Dexterity", 0)
    speed = r.get("speed") or 30
    bab = r.get("base_attack_bonus") or r.get("bab") or 1
    cmb = r.get("cmb") or (bab + mods.get("Strength", 0))
    cmd = r.get("cmd") or (10 + bab + mods.get("Strength", 0) + mods.get("Dexterity", 0))

    # Senses & Perception
    perception_rank = c.get("skills", {}).get("Perception", 0)
    perception_total = perception_rank + mods.get("Wisdom", 0) + (3 if perception_rank > 0 else 0)
    senses_str = "Normal Vision"
    if "elf" in race.lower() or "gnome" in race.lower():
        senses_str = "Low-Light Vision"
    elif "dwarf" in race.lower() or "half-orc" in race.lower() or "orc" in race.lower():
        senses_str = "Darkvision 60 ft."

    # Feats List
    feats = c.get("feats") or []
    feat_names = [f.get("isim") or f.get("name") if isinstance(f, dict) else str(f) for f in feats]
    feats_str = ", ".join(feat_names) if feat_names else "None"

    # Trained Skills List
    skills_obj = c.get("skills") or {}
    skill_parts = []
    for sk_name, rank in skills_obj.items():
        if int(rank) > 0:
            sk_total = int(rank) + 3 # assume class skill
            skill_parts.append(f"{sk_name} {format_mod(sk_total)}")
    skills_str = ", ".join(skill_parts) if skill_parts else f"Perception {format_mod(perception_total)}"

    # Languages
    languages = c.get("languages") or ["Common"]
    lang_str = ", ".join(languages)

    # Equipment / Gear
    inventory = c.get("inventory") or []
    gear_names = [item.get("name") or item.get("isim") if isinstance(item, dict) else str(item) for item in inventory]
    gear_str = ", ".join(gear_names) if gear_names else "Adventurer's Standard Outfit"

    # Weapons & Attacks
    weapons = c.get("weapons") or [{"name": "Longsword", "damage": "1d8", "crit": "19-20/x2"}]
    melee_attacks = []
    for w in weapons:
        w_name = w.get("name") or w.get("isim") or "Weapon"
        w_dmg = w.get("damage") or "1d8"
        w_crit = w.get("crit") or "20/x2"
        w_atk = bab + mods.get("Strength", 0)
        melee_attacks.append(f"{w_name} {format_mod(w_atk)} ({w_dmg}+{mods.get('Strength', 0)}/{w_crit})")
    melee_str = ", ".join(melee_attacks) if melee_attacks else f"Unarmed Strike {format_mod(bab + mods.get('Strength', 0))} (1d3+{mods.get('Strength', 0)})"

    # Assemble Plain Text Statblock
    lines = [
        f"{name.upper()} CR {max(1, int(level))}",
        f"XP {int(level) * 400}",
        f"{alignment} {size} Humanoid ({race.lower()}) {char_class} {level}",
        f"Init {format_mod(init_val)}; Senses {senses_str}; Perception {format_mod(perception_total)}",
        "----------------------------------------------------------------------",
        "DEFENSE",
        "----------------------------------------------------------------------",
        f"AC {ac_total}, touch {ac_touch}, flat-footed {ac_ff}",
        f"hp {hp} ({level}d{r.get('hit_die', 10)}{format_mod(mods.get('Constitution', 0) * int(level))})",
        f"Fort {format_mod(fort)}, Ref {format_mod(ref)}, Will {format_mod(will)}",
        "----------------------------------------------------------------------",
        "OFFENSE",
        "----------------------------------------------------------------------",
        f"Speed {speed} ft.",
        f"Melee {melee_str}",
        "----------------------------------------------------------------------",
        "STATISTICS",
        "----------------------------------------------------------------------",
        f"Str {scores.get('Strength', 10)} ({format_mod(mods.get('Strength', 0))}), "
        f"Dex {scores.get('Dexterity', 10)} ({format_mod(mods.get('Dexterity', 0))}), "
        f"Con {scores.get('Constitution', 10)} ({format_mod(mods.get('Constitution', 0))}), "
        f"Int {scores.get('Intelligence', 10)} ({format_mod(mods.get('Intelligence', 0))}), "
        f"Wis {scores.get('Wisdom', 10)} ({format_mod(mods.get('Wisdom', 0))}), "
        f"Cha {scores.get('Charisma', 10)} ({format_mod(mods.get('Charisma', 0))})",
        f"Base Atk {format_mod(bab)}; CMB {format_mod(cmb)}; CMD {cmd}",
        f"Feats {feats_str}",
        f"Skills {skills_str}",
        f"Languages {lang_str}",
        f"Gear {gear_str}"
    ]

    plain_text = "\n".join(lines)

    # Markdown format
    md_lines = [
        f"### **{name.upper()}** (CR {max(1, int(level))})",
        f"*{alignment} {size} Humanoid ({race}) {char_class} {level}*",
        f"**Init** {format_mod(init_val)}; **Senses** {senses_str}; **Perception** {format_mod(perception_total)}",
        "",
        "#### **DEFENSE**",
        f"- **AC:** {ac_total}, touch {ac_touch}, flat-footed {ac_ff}",
        f"- **HP:** {hp}",
        f"- **Fort:** {format_mod(fort)}, **Ref:** {format_mod(ref)}, **Will:** {format_mod(will)}",
        "",
        "#### **OFFENSE**",
        f"- **Speed:** {speed} ft.",
        f"- **Melee:** {melee_str}",
        "",
        "#### **STATISTICS**",
        f"- **Str** {scores.get('Strength', 10)}, **Dex** {scores.get('Dexterity', 10)}, **Con** {scores.get('Constitution', 10)}, **Int** {scores.get('Intelligence', 10)}, **Wis** {scores.get('Wisdom', 10)}, **Cha** {scores.get('Charisma', 10)}",
        f"- **Base Atk:** {format_mod(bab)}; **CMB:** {format_mod(cmb)}; **CMD:** {cmd}",
        f"- **Feats:** {feats_str}",
        f"- **Skills:** {skills_str}",
        f"- **Languages:** {lang_str}",
        f"- **Gear:** {gear_str}"
    ]
    markdown = "\n".join(md_lines)

    return {
        "plain_text": plain_text,
        "markdown": markdown
    }


def export_character_json(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepares structured, portable JSON format for character export."""
    return {
        "app": "Diyargezen Pathfinder 1e Character Creator",
        "schema_version": "2.0",
        "export_date": datetime.now().isoformat(),
        "character": character_data
    }


def validate_imported_character_json(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validates structure and integrity of an imported character JSON."""
    warnings = []
    
    char_obj = json_data.get("character") if "character" in json_data else json_data
    
    if not isinstance(char_obj, dict):
        return {"is_valid": False, "warnings": ["Geçersiz JSON yapısı: Karakter nesnesi bulunamadı."]}

    if not char_obj.get("name") and not char_obj.get("isim"):
        warnings.append("Karakter ismi eksik.")

    if not char_obj.get("race") and not char_obj.get("irk"):
        warnings.append("Karakter ırkı eksik.")

    if not char_obj.get("class") and not char_obj.get("sinif"):
        warnings.append("Karakter sınıfı eksik.")

    return {
        "is_valid": len(warnings) == 0,
        "warnings": warnings,
        "character": char_obj
    }
