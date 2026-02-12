"""
D&D 5e Multiclassing Modulu
Cok sinifli karakter olusturma kurallari ve hesaplamalari
"""

from typing import Dict, Any, List, Optional, Tuple


# ============================================================================
# Multiclass Prerequisite (Onkosul) Tablosu
# Her sinifa giris icin gereken minimum ability score'lar
# ============================================================================
MULTICLASS_PREREQUISITES: Dict[str, Dict[str, int]] = {
    "Barbarian":  {"Strength": 13},
    "Bard":       {"Charisma": 13},
    "Cleric":     {"Wisdom": 13},
    "Druid":      {"Wisdom": 13},
    "Fighter":    {"Strength": 13},  # veya Dexterity 13
    "Monk":       {"Dexterity": 13, "Wisdom": 13},
    "Paladin":    {"Strength": 13, "Charisma": 13},
    "Ranger":     {"Dexterity": 13, "Wisdom": 13},
    "Rogue":      {"Dexterity": 13},
    "Sorcerer":   {"Charisma": 13},
    "Warlock":    {"Charisma": 13},
    "Wizard":     {"Intelligence": 13},
    "Artificer":  {"Intelligence": 13},
    "Blood Hunter": {"Strength": 13},  # veya Dexterity 13
}

# Fighter ve Blood Hunter icin alternatif prerequisite (STR veya DEX)
MULTICLASS_ALTERNATIVE_PREREQS: Dict[str, List[Dict[str, int]]] = {
    "Fighter": [{"Strength": 13}, {"Dexterity": 13}],
    "Blood Hunter": [{"Strength": 13}, {"Dexterity": 13}],
}

# ============================================================================
# Multiclass Proficiency Tablosu
# Yeni sinifa geciste kazanilan proficiency'ler
# (1. siniftan farkli - daha kisitli)
# ============================================================================
MULTICLASS_PROFICIENCIES: Dict[str, Dict[str, List[str]]] = {
    "Barbarian":  {"armor": ["Shields"], "weapons": ["Simple weapons", "Martial weapons"]},
    "Bard":       {"armor": ["Light armor"], "weapons": [], "skills": ["Any one skill"]},
    "Cleric":     {"armor": ["Light armor", "Medium armor", "Shields"], "weapons": []},
    "Druid":      {"armor": ["Light armor", "Medium armor", "Shields (no metal)"], "weapons": []},
    "Fighter":    {"armor": ["Light armor", "Medium armor", "Shields"], "weapons": ["Simple weapons", "Martial weapons"]},
    "Monk":       {"armor": [], "weapons": ["Simple weapons", "Shortswords"]},
    "Paladin":    {"armor": ["Light armor", "Medium armor", "Shields"], "weapons": ["Simple weapons", "Martial weapons"]},
    "Ranger":     {"armor": ["Light armor", "Medium armor", "Shields"], "weapons": ["Simple weapons", "Martial weapons"], "skills": ["One skill from class list"]},
    "Rogue":      {"armor": ["Light armor"], "weapons": [], "skills": ["One skill from class list"]},
    "Sorcerer":   {"armor": [], "weapons": []},
    "Warlock":    {"armor": ["Light armor"], "weapons": ["Simple weapons"]},
    "Wizard":     {"armor": [], "weapons": []},
    "Artificer":  {"armor": ["Light armor", "Medium armor", "Shields"], "weapons": []},
}

# ============================================================================
# Spellcaster Level Tablosu (Multiclass Spell Slot hesaplama)
# Full caster = 1, Half caster = 0.5, Third caster = 0.33
# ============================================================================
SPELLCASTER_LEVEL_MULTIPLIER: Dict[str, float] = {
    "Bard":       1.0,
    "Cleric":     1.0,
    "Druid":      1.0,
    "Sorcerer":   1.0,
    "Wizard":     1.0,
    "Artificer":  0.5,  # Round up
    "Paladin":    0.5,
    "Ranger":     0.5,
    "Fighter":    0.33,  # Eldritch Knight (sadece belirli subclass)
    "Rogue":      0.33,  # Arcane Trickster (sadece belirli subclass)
}

# Spellcaster subclass'lar (Fighter ve Rogue icin)
THIRD_CASTER_SUBCLASSES = {
    "Fighter": ["Eldritch Knight"],
    "Rogue": ["Arcane Trickster"],
}

# ============================================================================
# Multiclass Spell Slot Tablosu
# Toplam caster level'a gore spell slot sayisi
# ============================================================================
MULTICLASS_SPELL_SLOTS: Dict[int, Dict[int, int]] = {
    1:  {1: 2},
    2:  {1: 3},
    3:  {1: 4, 2: 2},
    4:  {1: 4, 2: 3},
    5:  {1: 4, 2: 3, 3: 2},
    6:  {1: 4, 2: 3, 3: 3},
    7:  {1: 4, 2: 3, 3: 3, 4: 1},
    8:  {1: 4, 2: 3, 3: 3, 4: 2},
    9:  {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
}

# Hit Dice tablosu
CLASS_HIT_DICE: Dict[str, int] = {
    "Barbarian": 12, "Bard": 8, "Cleric": 8, "Druid": 8,
    "Fighter": 10, "Monk": 8, "Paladin": 10, "Ranger": 10,
    "Rogue": 8, "Sorcerer": 6, "Warlock": 8, "Wizard": 6,
    "Artificer": 8, "Blood Hunter": 10,
}


def check_multiclass_prerequisites(
    character: Dict[str, Any],
    target_class: str
) -> Tuple[bool, List[str]]:
    """
    Bir karakterin belirli bir sinifa multiclass yapip yapamayacagini kontrol et.

    D&D 5e kurali: Hem mevcut sinifin hem de hedef sinifin prerequisite'lerini
    karsilamak gerekir.

    Returns:
        (can_multiclass, reasons)
    """
    abilities = character.get("abilities", {})
    current_class = character.get("class", "")
    reasons = []

    # Mevcut sinifin prerequisite'lerini kontrol et
    for cls in [current_class, target_class]:
        if not cls:
            continue

        # Alternatif prerequisite var mi?
        if cls in MULTICLASS_ALTERNATIVE_PREREQS:
            alternatives = MULTICLASS_ALTERNATIVE_PREREQS[cls]
            any_met = False
            for alt in alternatives:
                if all(abilities.get(ab, 0) >= req for ab, req in alt.items()):
                    any_met = True
                    break
            if not any_met:
                alt_strs = [" veya ".join(f"{ab} >= {req}" for ab, req in alt.items()) for alt in alternatives]
                reasons.append(f"{cls} icin gerekli: {' VEYA '.join(alt_strs)}")
        else:
            prereqs = MULTICLASS_PREREQUISITES.get(cls, {})
            for ability, min_score in prereqs.items():
                current_score = abilities.get(ability, 0)
                if current_score < min_score:
                    reasons.append(f"{cls} icin {ability} >= {min_score} gerekli (mevcut: {current_score})")

    can_multiclass = len(reasons) == 0
    return can_multiclass, reasons


def get_multiclass_proficiencies(target_class: str) -> Dict[str, List[str]]:
    """Yeni sinifa geciste kazanilan proficiency'leri dondur"""
    return MULTICLASS_PROFICIENCIES.get(target_class, {})


def calculate_multiclass_spell_slots(class_levels: Dict[str, int], subclasses: Optional[Dict[str, str]] = None) -> Dict[int, int]:
    """
    Multiclass spell slot hesaplama.
    
    Args:
        class_levels: {"Wizard": 5, "Fighter": 3} gibi sinif/seviye dict'i
        subclasses: {"Fighter": "Eldritch Knight"} gibi subclass bilgisi
    
    Returns:
        {1: 4, 2: 3, 3: 2} gibi spell slot dict'i
    """
    if subclasses is None:
        subclasses = {}

    # Toplam caster level hesapla
    total_caster_level = 0.0

    for cls, level in class_levels.items():
        multiplier = SPELLCASTER_LEVEL_MULTIPLIER.get(cls, 0)

        # Third casters icin subclass kontrolu
        if multiplier == 0.33:
            subclass = subclasses.get(cls, "")
            valid_subclasses = THIRD_CASTER_SUBCLASSES.get(cls, [])
            if subclass not in valid_subclasses:
                multiplier = 0  # Spellcaster subclass degilse spell slot yok

        # Artificer round up, digerleri round down
        if cls == "Artificer":
            import math
            total_caster_level += math.ceil(level * multiplier)
        else:
            total_caster_level += int(level * multiplier)

    caster_level = int(total_caster_level)
    if caster_level < 1:
        return {}

    caster_level = min(caster_level, 20)
    return MULTICLASS_SPELL_SLOTS.get(caster_level, {})


def calculate_multiclass_hp(
    class_levels: Dict[str, int],
    con_modifier: int
) -> int:
    """
    Multiclass HP hesaplama.
    
    Ilk sinifin 1. seviyesi: max hit die + CON mod
    Sonraki tum seviyeler: (hit die / 2 + 1) + CON mod
    """
    total_hp = 0
    first_class = True

    for cls, level in class_levels.items():
        hit_die = CLASS_HIT_DICE.get(cls, 8)

        if first_class:
            # 1. sinifin 1. seviyesi max hit die
            total_hp += hit_die + con_modifier
            # Kalan seviyeler ortalama
            for _ in range(1, level):
                total_hp += (hit_die // 2 + 1) + con_modifier
            first_class = False
        else:
            # Diger siniflarin tum seviyeleri ortalama
            for _ in range(level):
                total_hp += (hit_die // 2 + 1) + con_modifier

    return max(1, total_hp)


def calculate_multiclass_hit_dice(class_levels: Dict[str, int]) -> str:
    """
    Multiclass hit dice gosterimi.
    Ornek: "5d8 + 3d10"
    """
    parts = []
    for cls, level in class_levels.items():
        hit_die = CLASS_HIT_DICE.get(cls, 8)
        parts.append(f"{level}d{hit_die}")
    return " + ".join(parts)


def get_total_character_level(character: Dict[str, Any]) -> int:
    """Toplam karakter seviyesini hesapla (multiclass dahil)"""
    class_levels = character.get("class_levels", {})
    if class_levels:
        return sum(class_levels.values())
    return character.get("level", 1)


def get_available_multiclass_options(character: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Karakter icin mevcut multiclass seceneklerini listele.
    Her secenek icin prerequisite kontrolu yapar.
    """
    current_class = character.get("class", "")
    all_classes = list(MULTICLASS_PREREQUISITES.keys())
    options = []

    for cls in all_classes:
        if cls == current_class:
            continue  # Zaten bu sinifta

        can_mc, reasons = check_multiclass_prerequisites(character, cls)
        hit_die = CLASS_HIT_DICE.get(cls, 8)
        profs = get_multiclass_proficiencies(cls)
        prereqs = MULTICLASS_PREREQUISITES.get(cls, {})

        options.append({
            "class": cls,
            "can_multiclass": can_mc,
            "reasons": reasons,
            "hit_die": f"d{hit_die}",
            "prerequisites": prereqs,
            "proficiencies": profs,
            "is_spellcaster": cls in SPELLCASTER_LEVEL_MULTIPLIER and SPELLCASTER_LEVEL_MULTIPLIER[cls] > 0,
        })

    return options


def apply_multiclass_level(character: Dict[str, Any], new_class: str) -> Dict[str, Any]:
    """
    Karaktere yeni bir sinif seviyesi ekle.
    
    Returns:
        Guncellenmis karakter verisi
    """
    from utils.calculations import calculate_ability_modifier, calculate_proficiency_bonus

    # class_levels dict'i olustur/guncelle
    class_levels = character.get("class_levels", {})
    if not class_levels:
        # Ilk kez multiclass - mevcut sinif seviyesini ekle
        current_class = character.get("class", "Fighter")
        current_level = character.get("level", 1)
        class_levels[current_class] = current_level

    # Yeni sinifa 1 seviye ekle
    if new_class in class_levels:
        class_levels[new_class] += 1
    else:
        class_levels[new_class] = 1

    character["class_levels"] = class_levels
    character["is_multiclass"] = True

    # Toplam level guncelle
    total_level = sum(class_levels.values())
    character["level"] = total_level

    # Display class string
    class_parts = [f"{cls} {lvl}" for cls, lvl in class_levels.items()]
    character["class_display"] = " / ".join(class_parts)

    # Proficiency bonus (toplam seviyeye gore)
    character["proficiency_bonus"] = calculate_proficiency_bonus(total_level)

    # HP hesapla
    con_mod = calculate_ability_modifier(character.get("abilities", {}).get("Constitution", 10))
    character["hit_points"] = calculate_multiclass_hp(class_levels, con_mod)

    # Hit dice display
    character["hit_dice"] = calculate_multiclass_hit_dice(class_levels)

    # Multiclass spell slots
    subclasses = character.get("subclasses", {})
    mc_slots = calculate_multiclass_spell_slots(class_levels, subclasses)
    if mc_slots:
        character["spell_slots"] = mc_slots

    # Yeni sinif proficiency'lerini ekle
    new_profs = get_multiclass_proficiencies(new_class)
    existing_profs = character.get("proficiencies", {})
    for prof_type, items in new_profs.items():
        if prof_type not in existing_profs:
            existing_profs[prof_type] = []
        for item in items:
            if item not in existing_profs[prof_type]:
                existing_profs[prof_type].append(item)
    character["proficiencies"] = existing_profs

    return character
