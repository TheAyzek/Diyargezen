"""
Karakter karşılaştırma modülü
İki karakteri karşılaştırır ve farkları tespit eder
"""
from typing import Dict, Any


def compare_characters(char1: Dict[str, Any], char2: Dict[str, Any]) -> Dict[str, Any]:
    """
    İki karakteri karşılaştır ve farkları döndür
    
    Args:
        char1: İlk karakter verisi
        char2: İkinci karakter verisi
    
    Returns:
        Karşılaştırma sonuçları (farklar, benzerlikler, özet)
    """
    system = char1.get("system")
    
    if system != char2.get("system"):
        return {
            "error": "Farklı sistemler karşılaştırılamaz",
            "system1": system,
            "system2": char2.get("system")
        }
    
    if system == "DND5E":
        return _compare_dnd(char1, char2)
    elif system == "MUTANTS_AND_MASTERMINDS":
        return _compare_mm(char1, char2)
    elif system == "VTM5E":
        return _compare_vtm(char1, char2)
    else:
        return {
            "error": f"Bilinmeyen sistem: {system}",
            "system": system
        }


def _compare_dnd(char1: Dict[str, Any], char2: Dict[str, Any]) -> Dict[str, Any]:
    """D&D 5e karakterlerini karşılaştır"""
    differences = []
    similarities = []
    
    # Temel bilgiler
    basic_fields = ["name", "race", "class", "background", "level"]
    for field in basic_fields:
        val1 = char1.get(field, "")
        val2 = char2.get(field, "")
        if val1 != val2:
            differences.append({
                "field": field,
                "char1": val1,
                "char2": val2,
                "type": "basic"
            })
        else:
            similarities.append({
                "field": field,
                "value": val1,
                "type": "basic"
            })
    
    # Ability scores
    abilities1 = char1.get("abilities", {})
    abilities2 = char2.get("abilities", {})
    ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    for ability in ability_names:
        val1 = abilities1.get(ability, 0)
        val2 = abilities2.get(ability, 0)
        diff = val1 - val2
        if diff != 0:
            differences.append({
                "field": f"ability_{ability}",
                "char1": val1,
                "char2": val2,
                "difference": diff,
                "type": "ability"
            })
        else:
            similarities.append({
                "field": f"ability_{ability}",
                "value": val1,
                "type": "ability"
            })
    
    # Level farkı
    level1 = char1.get("level", 1)
    level2 = char2.get("level", 1)
    level_diff = level1 - level2
    
    # Skills
    skills1 = char1.get("skills", {})
    skills2 = char2.get("skills", {})
    prof1 = skills1.get("proficiencies", {})
    prof2 = skills2.get("proficiencies", {})
    
    all_skills = set(prof1.keys()) | set(prof2.keys())
    skill_diffs = []
    for skill in all_skills:
        val1 = prof1.get(skill, False)
        val2 = prof2.get(skill, False)
        if val1 != val2:
            skill_diffs.append({
                "skill": skill,
                "char1": val1,
                "char2": val2
            })
    
    if skill_diffs:
        differences.append({
            "field": "skills",
            "differences": skill_diffs,
            "type": "skills"
        })
    
    # Spells
    spells1 = char1.get("spells", {})
    spells2 = char2.get("spells", {})
    all_spell_keys = set(spells1.keys()) | set(spells2.keys())
    spell_diffs = []
    for key in all_spell_keys:
        spells_list1 = spells1.get(key, [])
        spells_list2 = spells2.get(key, [])
        if spells_list1 != spells_list2:
            spell_diffs.append({
                "level": key,
                "char1": spells_list1,
                "char2": spells_list2
            })
    
    if spell_diffs:
        differences.append({
            "field": "spells",
            "differences": spell_diffs,
            "type": "spells"
        })
    
    # Feats
    feats1 = set(char1.get("feats", []))
    feats2 = set(char2.get("feats", []))
    feat_diff = {
        "only_char1": list(feats1 - feats2),
        "only_char2": list(feats2 - feats1),
        "common": list(feats1 & feats2)
    }
    
    if feat_diff["only_char1"] or feat_diff["only_char2"]:
        differences.append({
            "field": "feats",
            "differences": feat_diff,
            "type": "feats"
        })
    
    return {
        "system": "DND5E",
        "char1_name": char1.get("name", "Unknown"),
        "char2_name": char2.get("name", "Unknown"),
        "differences": differences,
        "similarities": similarities,
        "level_difference": level_diff,
        "summary": {
            "total_differences": len(differences),
            "total_similarities": len(similarities),
            "level_diff": level_diff
        }
    }


def _compare_mm(char1: Dict[str, Any], char2: Dict[str, Any]) -> Dict[str, Any]:
    """M&M karakterlerini karşılaştır"""
    differences = []
    similarities = []
    
    # Temel bilgiler
    basic_fields = ["name", "codename", "power_level", "archetype"]
    for field in basic_fields:
        val1 = char1.get(field, "")
        val2 = char2.get(field, "")
        if val1 != val2:
            differences.append({
                "field": field,
                "char1": val1,
                "char2": val2,
                "type": "basic"
            })
        else:
            similarities.append({
                "field": field,
                "value": val1,
                "type": "basic"
            })
    
    # Abilities
    abilities1 = char1.get("abilities", {})
    abilities2 = char2.get("abilities", {})
    all_abilities = set(abilities1.keys()) | set(abilities2.keys())
    
    for ability in all_abilities:
        val1 = abilities1.get(ability, 0)
        val2 = abilities2.get(ability, 0)
        diff = val1 - val2
        if diff != 0:
            differences.append({
                "field": f"ability_{ability}",
                "char1": val1,
                "char2": val2,
                "difference": diff,
                "type": "ability"
            })
        else:
            similarities.append({
                "field": f"ability_{ability}",
                "value": val1,
                "type": "ability"
            })
    
    # Defenses
    defenses1 = char1.get("defenses", {})
    defenses2 = char2.get("defenses", {})
    all_defenses = set(defenses1.keys()) | set(defenses2.keys())
    
    for defense in all_defenses:
        val1 = defenses1.get(defense, 0)
        val2 = defenses2.get(defense, 0)
        diff = val1 - val2
        if diff != 0:
            differences.append({
                "field": f"defense_{defense}",
                "char1": val1,
                "char2": val2,
                "difference": diff,
                "type": "defense"
            })
    
    # Power Points
    pp1 = char1.get("power_points", 0)
    pp2 = char2.get("power_points", 0)
    if pp1 != pp2:
        differences.append({
            "field": "power_points",
            "char1": pp1,
            "char2": pp2,
            "difference": pp1 - pp2,
            "type": "power_points"
        })
    
    # Powers
    powers1 = set(char1.get("powers", []))
    powers2 = set(char2.get("powers", []))
    power_diff = {
        "only_char1": list(powers1 - powers2),
        "only_char2": list(powers2 - powers1),
        "common": list(powers1 & powers2)
    }
    
    if power_diff["only_char1"] or power_diff["only_char2"]:
        differences.append({
            "field": "powers",
            "differences": power_diff,
            "type": "powers"
        })
    
    return {
        "system": "MUTANTS_AND_MASTERMINDS",
        "char1_name": char1.get("name", "Unknown"),
        "char2_name": char2.get("name", "Unknown"),
        "differences": differences,
        "similarities": similarities,
        "summary": {
            "total_differences": len(differences),
            "total_similarities": len(similarities)
        }
    }


def _compare_vtm(char1: Dict[str, Any], char2: Dict[str, Any]) -> Dict[str, Any]:
    """VtM karakterlerini karşılaştır"""
    differences = []
    similarities = []
    
    # Temel bilgiler
    basic_fields = ["name", "player", "chronicle", "concept", "clan"]
    for field in basic_fields:
        val1 = char1.get(field, "")
        val2 = char2.get(field, "")
        if val1 != val2:
            differences.append({
                "field": field,
                "char1": val1,
                "char2": val2,
                "type": "basic"
            })
        else:
            similarities.append({
                "field": field,
                "value": val1,
                "type": "basic"
            })
    
    # Attributes
    attrs1 = char1.get("attributes", {})
    attrs2 = char2.get("attributes", {})
    all_attrs = set(attrs1.keys()) | set(attrs2.keys())
    
    for attr in all_attrs:
        val1 = attrs1.get(attr, 0)
        val2 = attrs2.get(attr, 0)
        diff = val1 - val2
        if diff != 0:
            differences.append({
                "field": f"attribute_{attr}",
                "char1": val1,
                "char2": val2,
                "difference": diff,
                "type": "attribute"
            })
    
    # Skills
    skills1 = char1.get("skills", {})
    skills2 = char2.get("skills", {})
    all_skill_cats = set(skills1.keys()) | set(skills2.keys())
    
    for cat in all_skill_cats:
        skills_cat1 = skills1.get(cat, {})
        skills_cat2 = skills2.get(cat, {})
        all_skills = set(skills_cat1.keys()) | set(skills_cat2.keys())
        
        for skill in all_skills:
            val1 = skills_cat1.get(skill, 0)
            val2 = skills_cat2.get(skill, 0)
            diff = val1 - val2
            if diff != 0:
                differences.append({
                    "field": f"skill_{cat}_{skill}",
                    "char1": val1,
                    "char2": val2,
                    "difference": diff,
                    "type": "skill"
                })
    
    # Disciplines
    disc1 = set(char1.get("disciplines", []))
    disc2 = set(char2.get("disciplines", []))
    disc_diff = {
        "only_char1": list(disc1 - disc2),
        "only_char2": list(disc2 - disc1),
        "common": list(disc1 & disc2)
    }
    
    if disc_diff["only_char1"] or disc_diff["only_char2"]:
        differences.append({
            "field": "disciplines",
            "differences": disc_diff,
            "type": "disciplines"
        })
    
    # Humanity, Health, Willpower
    for field in ["humanity", "health", "willpower"]:
        val1 = char1.get(field, 0)
        val2 = char2.get(field, 0)
        if val1 != val2:
            differences.append({
                "field": field,
                "char1": val1,
                "char2": val2,
                "difference": val1 - val2,
                "type": field
            })
    
    return {
        "system": "VTM5E",
        "char1_name": char1.get("name", "Unknown"),
        "char2_name": char2.get("name", "Unknown"),
        "differences": differences,
        "similarities": similarities,
        "summary": {
            "total_differences": len(differences),
            "total_similarities": len(similarities)
        }
    }

