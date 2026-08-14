"""
Pathfinder 1st Edition Conditions & Situational Buffs Engine
============================================================
References:
- PF1e Core Rulebook p. 565-568 (Official Conditions)
- PF1e Core Rulebook Spells (Bless, Haste, Heroism, Bull's Strength, Mage Armor, Shield, etc.)
- PF1e Class Features (Barbarian Rage, Bardic Inspire Courage)

Architecture:
- Defines registry of official conditions and common situational buffs.
- Aggregates stat, combat, AC, saving throws, and skill modifiers with PF1e stacking rules.
"""

from typing import Dict, Any, List, Optional


PF1E_CONDITIONS_AND_BUFFS: Dict[str, Dict[str, Any]] = {
    # ── 1. Resmi Paizo Koşulları (Conditions - CRB p. 565-568) ────────────────
    "blinded": {
        "name": "Kör (Blinded)",
        "type": "condition",
        "category": "debuff",
        "icon": "EyeOff",
        "description": "Zırh Sınıfına -2 penaltı, Çeviklik AC bonusunu kaybeder. STR/DEX yeteneklerine ve Perception'a -4 penaltı.",
        "ac_penalty": 2,
        "loses_dex_ac": True,
        "skill_penalty_str_dex": 4,
        "perception_penalty": 4
    },
    "dazzled": {
        "name": "Gözü Kamaşmış (Dazzled)",
        "type": "condition",
        "category": "debuff",
        "icon": "Sun",
        "description": "Saldırı zarlarına ve görüşe dayalı Perception zarlarına -1 penaltı.",
        "attack_penalty": 1,
        "perception_penalty": 1
    },
    "deafened": {
        "name": "Sağır (Deafened)",
        "type": "condition",
        "category": "debuff",
        "icon": "VolumeX",
        "description": "İnisiyatife -4 penaltı, işitmeye dayalı Perception zarlarında otomatik başarısızlık.",
        "initiative_penalty": 4
    },
    "entangled": {
        "name": "Dolanmış / Sarılmış (Entangled)",
        "type": "condition",
        "category": "debuff",
        "icon": "Link2",
        "description": "Saldırılara -2 penaltı, Çevikliğe -4 penaltı (-2 AC, -2 Reflex, -2 DEX yetenekleri). Hareket hızı yarıya iner.",
        "attack_penalty": 2,
        "dex_penalty": 4,
        "speed_halved": True
    },
    "exhausted": {
        "name": "Tükenmiş (Exhausted)",
        "type": "condition",
        "category": "debuff",
        "icon": "BatteryLow",
        "description": "Güç ve Çevikliğe -6 penaltı (-3 saldırı, hasar, AC, Reflex). Hareket hızı yarıya iner.",
        "str_penalty": 6,
        "dex_penalty": 6,
        "speed_halved": True
    },
    "fatigued": {
        "name": "Yorgun (Fatigued)",
        "type": "condition",
        "category": "debuff",
        "icon": "BatteryMedium",
        "description": "Güç ve Çevikliğe -2 penaltı (-1 saldırı, hasar, AC, Reflex). Koşamaz veya hücum edemez.",
        "str_penalty": 2,
        "dex_penalty": 2
    },
    "frightened": {
        "name": "Korkmuş (Frightened)",
        "type": "condition",
        "category": "debuff",
        "icon": "Ghost",
        "description": "Saldırılara, kurtarma zarlarına, yetenek zarlarına -2 penaltı. Kaçmak zorundadır.",
        "attack_penalty": 2,
        "save_penalty": 2,
        "skill_penalty": 2
    },
    "grappled": {
        "name": "Güreşte (Grappled)",
        "type": "condition",
        "category": "debuff",
        "icon": "Users",
        "description": "Hareket edemez. Çevikliğe -4 penaltı (-2 AC, -2 Reflex). Saldırı ve manevra zarlarına -2 penaltı.",
        "attack_penalty": 2,
        "dex_penalty": 4,
        "cmb_penalty": 2
    },
    "pinned": {
        "name": "Yere Çivilenmiş (Pinned)",
        "type": "condition",
        "category": "debuff",
        "icon": "Lock",
        "description": "AC'ye -4 penaltı, Çeviklik AC bonusunu kaybeder. Hareket edemez.",
        "ac_penalty": 4,
        "loses_dex_ac": True
    },
    "prone": {
        "name": "Yüzüstü / Yerde (Prone)",
        "type": "condition",
        "category": "debuff",
        "icon": "ArrowDownCircle",
        "description": "Yakın dövüş saldırılarına -4 penaltı. Yakın dövüş saldırılarına karşı -4 AC, menzilli saldırılara karşı +4 AC.",
        "melee_attack_penalty": 4,
        "melee_ac_penalty": 4,
        "ranged_ac_bonus": 4
    },
    "shaken": {
        "name": "Sarsılmış (Shaken)",
        "type": "condition",
        "category": "debuff",
        "icon": "AlertTriangle",
        "description": "Saldırı zarlarına, kurtarma zarlarına, yetenek ve nitelik zarlarına -2 penaltı.",
        "attack_penalty": 2,
        "save_penalty": 2,
        "skill_penalty": 2
    },
    "sickened": {
        "name": "Midesi Bulanmış (Sickened)",
        "type": "condition",
        "category": "debuff",
        "icon": "Frown",
        "description": "Tüm saldırı, silah hasarı, kurtarma zarları, yetenek ve nitelik kontrollerine -2 penaltı.",
        "attack_penalty": 2,
        "damage_penalty": 2,
        "save_penalty": 2,
        "skill_penalty": 2
    },
    "staggered": {
        "name": "Sersemlemiş (Staggered)",
        "type": "condition",
        "category": "debuff",
        "icon": "PauseCircle",
        "description": "Her tur yalnızca tek bir standart veya hareket eylemi yapabilir (Tam Saldırı yapamaz).",
        "cannot_full_attack": True
    },
    "stunned": {
        "name": "Şok Olmuş (Stunned)",
        "type": "condition",
        "category": "debuff",
        "icon": "ZapOff",
        "description": "Eylemler yapamaz, elindekileri düşürür. AC'ye -2 penaltı, Çeviklik AC bonusunu kaybeder.",
        "ac_penalty": 2,
        "loses_dex_ac": True
    },

    # ── 2. Popüler Savaş & Büyü Buff'ları (CRB Spells & Features) ─────────────
    "bless": {
        "name": "Kutsama (Bless)",
        "type": "buff",
        "category": "spell",
        "icon": "Sparkles",
        "description": "Saldırı zarlarına ve korkuya karşı kurtarma zarlarına +1 moral bonusu.",
        "morale_attack_bonus": 1,
        "fear_save_bonus": 1
    },
    "haste": {
        "name": "Acele (Haste)",
        "type": "buff",
        "category": "spell",
        "icon": "Zap",
        "description": "Saldırılara +1, Zırh Sınıfına +1 Dodge, Reflex kurtarma zarlarına +1, Temel Hıza +30 ft bonus.",
        "attack_bonus": 1,
        "ac_dodge_bonus": 1,
        "reflex_bonus": 1,
        "speed_bonus": 30,
        "extra_attack": True
    },
    "heroism": {
        "name": "Kahramanlık (Heroism)",
        "type": "buff",
        "category": "spell",
        "icon": "ShieldAlert",
        "description": "Saldırı zarlarına, kurtarma zarlarına ve yetenek kontrollerine +2 moral bonusu.",
        "morale_attack_bonus": 2,
        "morale_save_bonus": 2,
        "morale_skill_bonus": 2
    },
    "greater_heroism": {
        "name": "Büyük Kahramanlık (Greater Heroism)",
        "type": "buff",
        "category": "spell",
        "icon": "ShieldCheck",
        "description": "Saldırı zarlarına, kurtarma zarlarına ve yetenek zarlarına +4 moral bonusu.",
        "morale_attack_bonus": 4,
        "morale_save_bonus": 4,
        "morale_skill_bonus": 4
    },
    "bulls_strength": {
        "name": "Boğa Gücü (Bull's Strength)",
        "type": "buff",
        "category": "spell",
        "icon": "Dumbbell",
        "description": "Güce +4 enhancement bonusu (+2 STR modifikasyonu).",
        "enhancement_str": 4
    },
    "cats_grace": {
        "name": "Kedi Zarafeti (Cat's Grace)",
        "type": "buff",
        "category": "spell",
        "icon": "Feather",
        "description": "Çevikliğe +4 enhancement bonusu (+2 DEX modifikasyonu).",
        "enhancement_dex": 4
    },
    "bears_endurance": {
        "name": "Ayı Dayanıklılığı (Bear's Endurance)",
        "type": "buff",
        "category": "spell",
        "icon": "Heart",
        "description": "Bünyeye +4 enhancement bonusu (+2 CON modifikasyonu, +2 HP/seviye, +2 Fortitude).",
        "enhancement_con": 4
    },
    "foxs_cunning": {
        "name": "Tilki Kurnazlığı (Fox's Cunning)",
        "type": "buff",
        "category": "spell",
        "icon": "Brain",
        "description": "Zekaya +4 enhancement bonusu (+2 INT modifikasyonu).",
        "enhancement_int": 4
    },
    "owls_wisdom": {
        "name": "Baykuş Bilgeliği (Owl's Wisdom)",
        "type": "buff",
        "category": "spell",
        "icon": "Moon",
        "description": "Bilgeliğe +4 enhancement bonusu (+2 WIS modifikasyonu).",
        "enhancement_wis": 4
    },
    "eagles_splendor": {
        "name": "Kartal Görkemi (Eagle's Splendor)",
        "type": "buff",
        "category": "spell",
        "icon": "Crown",
        "description": "Karizmaya +4 enhancement bonusu (+2 CHA modifikasyonu).",
        "enhancement_cha": 4
    },
    "mage_armor": {
        "name": "Büyücü Zırhı (Mage Armor)",
        "type": "buff",
        "category": "spell",
        "icon": "Shield",
        "description": "Zırh Sınıfına +4 zırh bonusu (normal zırhla istiflenmez).",
        "armor_bonus": 4
    },
    "shield_spell": {
        "name": "Kalkan Büyüsü (Shield Spell)",
        "type": "buff",
        "category": "spell",
        "icon": "ShieldPlus",
        "description": "Zırh Sınıfına +4 kalkan bonusu ve Magic Missile bağışıklığı.",
        "shield_bonus": 4
    },
    "barkskin": {
        "name": "Ağaç Kabuğu (Barkskin)",
        "type": "buff",
        "category": "spell",
        "icon": "TreePine",
        "description": "Doğal Zırha +2 enhancement bonusu (+3 CL6, +4 CL9, +5 CL12).",
        "natural_armor_enhancement": 2
    },
    "inspire_courage": {
        "name": "Cesaret Verme (Inspire Courage +2)",
        "type": "buff",
        "category": "class_feature",
        "icon": "Music",
        "description": "Saldırı ve silah hasarına +2 competence bonusu, korkuya karşı +2 moral bonusu.",
        "competence_attack_bonus": 2,
        "competence_damage_bonus": 2,
        "fear_save_bonus": 2
    },
    "barbarian_rage": {
        "name": "Barbar Öfkesi (Barbarian Rage)",
        "type": "buff",
        "category": "class_feature",
        "icon": "Flame",
        "description": "Güç ve Bünyeye +4 moral bonusu, Will kurtarma zarına +2 moral bonusu, AC'ye -2 penaltı.",
        "morale_str": 4,
        "morale_con": 4,
        "morale_will_bonus": 2,
        "ac_penalty": 2
    },
    "flanking": {
        "name": "Kıstırma (Flanking Advantage)",
        "type": "buff",
        "category": "tactical",
        "icon": "Crosshair",
        "description": "Hedefi kıstıran yakın dövüş saldırılarına +2 circumstance saldırı bonusu.",
        "melee_attack_bonus": 2
    }
}


def get_available_conditions_and_buffs() -> List[Dict[str, Any]]:
    """Returns the full list of conditions and situational buffs for UI dropdowns/grids."""
    result = []
    for key, data in PF1E_CONDITIONS_AND_BUFFS.items():
        entry = dict(data)
        entry["id"] = key
        result.append(entry)
    return result


def calculate_conditions_and_buffs_modifiers(
    active_condition_keys: List[str],
    character: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculates all aggregated numerical bonuses, penalties, and flags from active conditions/buffs."""
    mods = {
        "ability_enhancements": {"strength": 0, "dexterity": 0, "constitution": 0, "intelligence": 0, "wisdom": 0, "charisma": 0},
        "ability_morale": {"strength": 0, "dexterity": 0, "constitution": 0, "intelligence": 0, "wisdom": 0, "charisma": 0},
        "ability_penalties": {"strength": 0, "dexterity": 0, "constitution": 0, "intelligence": 0, "wisdom": 0, "charisma": 0},
        "attack_bonus": 0,
        "melee_attack_bonus": 0,
        "ranged_attack_bonus": 0,
        "damage_bonus": 0,
        "ac_dodge_bonus": 0,
        "ac_penalty": 0,
        "ac_armor_bonus": 0,
        "ac_shield_bonus": 0,
        "ac_natural_bonus": 0,
        "save_bonuses": {"Fortitude": 0, "Reflex": 0, "Will": 0},
        "save_penalties": 0,
        "fear_save_bonus": 0,
        "skill_bonus": 0,
        "skill_penalties": 0,
        "speed_bonus": 0,
        "speed_halved": False,
        "initiative_penalty": 0,
        "loses_dex_ac": False,
        "applied_conditions": []
    }

    # Stacking tracking (highest morale/competence bonus wins)
    max_morale_attack = 0
    max_morale_save = 0
    max_morale_skill = 0
    max_competence_attack = 0
    max_competence_damage = 0

    for key in active_condition_keys or []:
        clean_k = str(key).strip().lower().replace(" ", "_").replace("-", "_")
        c_data = PF1E_CONDITIONS_AND_BUFFS.get(clean_k)
        if not c_data:
            # Try fuzzy match
            for reg_k, reg_v in PF1E_CONDITIONS_AND_BUFFS.items():
                if reg_k in clean_k or clean_k in reg_k:
                    c_data = reg_v
                    break
        if not c_data:
            continue

        mods["applied_conditions"].append(c_data["name"])

        # Ability enhancements (highest enhancement bonus applies)
        if "enhancement_str" in c_data: mods["ability_enhancements"]["strength"] = max(mods["ability_enhancements"]["strength"], c_data["enhancement_str"])
        if "enhancement_dex" in c_data: mods["ability_enhancements"]["dexterity"] = max(mods["ability_enhancements"]["dexterity"], c_data["enhancement_dex"])
        if "enhancement_con" in c_data: mods["ability_enhancements"]["constitution"] = max(mods["ability_enhancements"]["constitution"], c_data["enhancement_con"])
        if "enhancement_int" in c_data: mods["ability_enhancements"]["intelligence"] = max(mods["ability_enhancements"]["intelligence"], c_data["enhancement_int"])
        if "enhancement_wis" in c_data: mods["ability_enhancements"]["wisdom"] = max(mods["ability_enhancements"]["wisdom"], c_data["enhancement_wis"])
        if "enhancement_cha" in c_data: mods["ability_enhancements"]["charisma"] = max(mods["ability_enhancements"]["charisma"], c_data["enhancement_cha"])

        # Ability morale (highest morale bonus applies)
        if "morale_str" in c_data: mods["ability_morale"]["strength"] = max(mods["ability_morale"]["strength"], c_data["morale_str"])
        if "morale_con" in c_data: mods["ability_morale"]["constitution"] = max(mods["ability_morale"]["constitution"], c_data["morale_con"])

        # Ability penalties (stack)
        if "str_penalty" in c_data: mods["ability_penalties"]["strength"] += c_data["str_penalty"]
        if "dex_penalty" in c_data: mods["ability_penalties"]["dexterity"] += c_data["dex_penalty"]

        # Attack bonuses
        if "attack_bonus" in c_data: mods["attack_bonus"] += c_data["attack_bonus"]
        if "melee_attack_bonus" in c_data: mods["melee_attack_bonus"] += c_data["melee_attack_bonus"]
        if "attack_penalty" in c_data: mods["attack_bonus"] -= c_data["attack_penalty"]
        if "melee_attack_penalty" in c_data: mods["melee_attack_bonus"] -= c_data["melee_attack_penalty"]

        # Morale / Competence attack tracking
        if "morale_attack_bonus" in c_data: max_morale_attack = max(max_morale_attack, c_data["morale_attack_bonus"])
        if "competence_attack_bonus" in c_data: max_competence_attack = max(max_competence_attack, c_data["competence_attack_bonus"])

        # Damage bonuses / penalties
        if "competence_damage_bonus" in c_data: max_competence_damage = max(max_competence_damage, c_data["competence_damage_bonus"])
        if "damage_penalty" in c_data: mods["damage_bonus"] -= c_data["damage_penalty"]

        # AC Dodge / Penalties / Spells
        if "ac_dodge_bonus" in c_data: mods["ac_dodge_bonus"] += c_data["ac_dodge_bonus"]
        if "ac_penalty" in c_data: mods["ac_penalty"] += c_data["ac_penalty"]
        if "melee_ac_penalty" in c_data: mods["ac_penalty"] += c_data["melee_ac_penalty"]
        if "armor_bonus" in c_data: mods["ac_armor_bonus"] = max(mods["ac_armor_bonus"], c_data["armor_bonus"])
        if "shield_bonus" in c_data: mods["ac_shield_bonus"] = max(mods["ac_shield_bonus"], c_data["shield_bonus"])
        if "natural_armor_enhancement" in c_data: mods["ac_natural_bonus"] = max(mods["ac_natural_bonus"], c_data["natural_armor_enhancement"])
        if c_data.get("loses_dex_ac"): mods["loses_dex_ac"] = True

        # Saves
        if "reflex_bonus" in c_data: mods["save_bonuses"]["Reflex"] += c_data["reflex_bonus"]
        if "morale_will_bonus" in c_data: mods["save_bonuses"]["Will"] += c_data["morale_will_bonus"]
        if "save_penalty" in c_data: mods["save_penalties"] += c_data["save_penalty"]
        if "morale_save_bonus" in c_data: max_morale_save = max(max_morale_save, c_data["morale_save_bonus"])
        if "fear_save_bonus" in c_data: mods["fear_save_bonus"] = max(mods["fear_save_bonus"], c_data["fear_save_bonus"])

        # Skills
        if "skill_penalty" in c_data: mods["skill_penalties"] += c_data["skill_penalty"]
        if "morale_skill_bonus" in c_data: max_morale_skill = max(max_morale_skill, c_data["morale_skill_bonus"])

        # Speed & Initiative
        if "speed_bonus" in c_data: mods["speed_bonus"] += c_data["speed_bonus"]
        if c_data.get("speed_halved"): mods["speed_halved"] = True
        if "initiative_penalty" in c_data: mods["initiative_penalty"] += c_data["initiative_penalty"]

    # Apply highest Morale / Competence bonuses
    mods["attack_bonus"] += max_morale_attack + max_competence_attack
    mods["damage_bonus"] += max_competence_damage
    mods["save_bonuses"]["Fortitude"] += max_morale_save
    mods["save_bonuses"]["Reflex"] += max_morale_save
    mods["save_bonuses"]["Will"] += max_morale_save
    mods["skill_bonus"] += max_morale_skill

    return mods
