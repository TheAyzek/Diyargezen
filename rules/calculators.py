from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
import re

class BaseCalculator(ABC):
    """Base class for TTRPG derived statistics calculators."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(__file__).resolve().parent.parent / "data" / "characters.db"

    @abstractmethod
    def calculate(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates and returns all derived statistics for the system."""
        pass

    def get_active_mechanics(self, character: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Query SQLite for active entities (Race, Class, Feats, Equipment)
        and fetch their 'standard_mechanics' and 'prerequisites'.
        Checks in-memory entity dicts first.
        """
        import sqlite3
        import json
        
        active_mechanics = []
        active_prerequisites = []
        
        names_to_query = []
        
        def process_entity_dict(entity: Any):
            if isinstance(entity, dict):
                sys_ver = entity.get("sistem_verisi") or entity.get("system") or entity.get("data")
                if isinstance(sys_ver, dict):
                    active_mechanics.extend(sys_ver.get("standard_mechanics", []))
                    active_prerequisites.extend(sys_ver.get("prerequisites", []))
                    return True
            return False

        # Race
        race = character.get("race")
        race_data = character.get("race_data")
        if not process_entity_dict(race_data) and isinstance(race, str) and race:
            names_to_query.append(race)
            
        # Class
        cls = character.get("class")
        class_data = character.get("class_data")
        if not process_entity_dict(class_data) and isinstance(cls, str) and cls:
            names_to_query.append(cls)
            
        # Feats
        raw_feats = character.get("feats", [])
        if isinstance(raw_feats, list):
            for f in raw_feats:
                if not process_entity_dict(f):
                    if isinstance(f, str) and f:
                        names_to_query.append(f)
                    elif isinstance(f, dict) and f.get("name"):
                        names_to_query.append(f["name"])
                        
        # Equipment / Items
        raw_items = character.get("equipment", [])
        if isinstance(raw_items, list):
            for item in raw_items:
                if not process_entity_dict(item):
                    if isinstance(item, str) and item:
                        names_to_query.append(item)
                    elif isinstance(item, dict) and item.get("name"):
                        names_to_query.append(item["name"])
                        
        if names_to_query:
            sys_key = character.get("system", "").lower().replace("_", "").replace("-", "")
            if "pf" in sys_key or "pathfinder" in sys_key:
                sys_db = "pathfinder1e"
            elif "mm" in sys_key:
                sys_db = "mm3e"
            else:
                sys_db = "dnd5e"
                
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                placeholders = ",".join("?" for _ in names_to_query)
                cursor.execute(
                    f"SELECT isim, sistem_verisi FROM entities WHERE sistem = ? AND isim IN ({placeholders})",
                    [sys_db] + names_to_query
                )
                rows = cursor.fetchall()
                for row in rows:
                    try:
                        payload = json.loads(row[1]) if row[1] else {}
                        active_mechanics.extend(payload.get("standard_mechanics", []))
                        active_prerequisites.extend(payload.get("prerequisites", []))
                    except Exception:
                        pass
                conn.close()
            except Exception:
                pass
                
        return {
            "mechanics": active_mechanics,
            "prerequisites": active_prerequisites
        }

    def get_adjusted_abilities(self, character: Dict[str, Any]) -> Dict[str, int]:
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
                     "stamina", "agility", "fighting", "intellect", "awareness", "presence"]
        scores = {}
        is_mm = "mm" in character.get("system", "").lower()
        default_val = 0 if is_mm else 10
        for ab in abilities:
            scores[ab] = get_ability(character, ab, default=default_val)

        # ---------------------------------------------------------------------------
        # RACIAL ABILITY SCORE INCREASES
        # Apply parent race ASI first, then subrace ASI on top.
        # For D&D 5e subraces: their stored ability_score_increase ALREADY INCLUDES
        # the parent bonus (e.g., Wood Elf stores dex+2 AND wis+1). We subtract the
        # parent's contribution to get only the true subrace delta, avoiding double-
        # counting.
        # ---------------------------------------------------------------------------
        sys_key = character.get("system", "").lower().replace("_", "").replace("-", "")
        is_dnd5e = "dnd" in sys_key

        # Determine whether we have a subrace selected
        subrace_data: Dict = character.get("subrace_data") or {}
        has_subrace = bool(character.get("subrace", ""))

        # Helper: extract ASI dict from a data dict (entity.sistem_verisi or similar)
        def extract_asi(data: Any) -> Dict[str, int]:
            if not isinstance(data, dict):
                return {}
            raw = data.get("ability_score_increase") or data.get("modifiers") or {}
            if isinstance(raw, dict):
                result = {}
                for k, v in raw.items():
                    try:
                        result[k.lower()] = int(v)
                    except (ValueError, TypeError):
                        pass
                return result
            return {}

        # --- Parent race ASI ---
        parent_asi: Dict[str, int] = {}
        race_entity = self._get_entity_data(character, "race")
        if race_entity:
            parent_asi = extract_asi(race_entity)

        # If subrace is selected and system is D&D 5e, the subrace entity stores
        # the COMBINED ASI (parent + subrace bonus). Compute net subrace delta.
        if has_subrace and subrace_data:
            subrace_asi = extract_asi(subrace_data)
            if is_dnd5e:
                # subrace_asi may include parent race contributions – subtract them
                net_subrace_delta: Dict[str, int] = {}
                all_keys = set(list(parent_asi.keys()) + list(subrace_asi.keys()))
                for k in all_keys:
                    delta = subrace_asi.get(k, 0) - parent_asi.get(k, 0)
                    if delta != 0:
                        net_subrace_delta[k] = delta
                # Apply parent race ASI + net subrace delta
                for k, v in parent_asi.items():
                    if k in scores:
                        scores[k] += v
                for k, v in net_subrace_delta.items():
                    if k in scores:
                        scores[k] += v
            else:
                # PF1e heritages: apply parent ASI and then the subrace ASI directly on top
                for k, v in parent_asi.items():
                    if k in scores:
                        scores[k] += v
                for k, v in subrace_asi.items():
                    if k in scores:
                        scores[k] += v
        else:
            # No subrace – just apply parent race ASI
            for k, v in parent_asi.items():
                if k in scores:
                    scores[k] += v

        # --- Standard mechanics (feat / item modifiers, NON-ability-score targets) ---
        # NOTE: Ability score bonuses are handled above via ability_score_increase.
        # We skip mechanics targeting base ability score names here to prevent
        # double-counting (race entities store BOTH ability_score_increase AND
        # a matching standard_mechanics entry with the same value).
        ABILITY_SCORE_NAMES = {
            "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
            "stamina", "agility", "fighting", "intellect", "awareness", "presence"
        }
        active = self.get_active_mechanics(character)
        for m in active["mechanics"]:
            target = m.get("target", "")
            if target in ABILITY_SCORE_NAMES:
                # These are handled by ability_score_increase above — skip
                continue
            if target in scores:
                val = m.get("value", 0)
                if isinstance(val, int):
                    scores[target] += val
        return scores

    def _get_entity_data(self, character: Dict[str, Any], field: str) -> Optional[Dict[str, Any]]:
        """Helper: return the sistem_verisi dict for 'race' or 'class' entity
        stored inside the active character, querying the DB if necessary."""
        import sqlite3 as _sqlite3
        import json as _json

        data = character.get(f"{field}_data")
        if isinstance(data, dict) and data:
            return data

        name = character.get(field, "")
        if not name:
            return None

        sys_key = character.get("system", "").lower().replace("_", "").replace("-", "")
        if "pf" in sys_key or "pathfinder" in sys_key:
            sys_db = "pathfinder1e"
        elif "mm" in sys_key:
            sys_db = "mm3e"
        else:
            sys_db = "dnd5e"

        try:
            conn = _sqlite3.connect(str(self.db_path))
            row = conn.execute(
                "SELECT sistem_verisi FROM entities WHERE sistem = ? AND isim = ? LIMIT 1",
                (sys_db, name)
            ).fetchone()
            conn.close()
            if row and row[0]:
                return _json.loads(row[0])
        except Exception:
            pass
        return None



def get_ability(char: dict, name: str, default: int = 10) -> int:
    abilities = char.get("abilities", {})
    for k, v in abilities.items():
        if k.lower() == name.lower():
            try:
                return int(v)
            except:
                pass
    return default


def get_modifier(char: dict, name: str, default: int = 0) -> int:
    modifiers = char.get("modifiers", {})
    for k, v in modifiers.items():
        if k.lower() == name.lower():
            try:
                return int(v)
            except:
                pass
    score = get_ability(char, name, default=10)
    return (score - 10) // 2


def format_mod(val: int) -> str:
    return f"{val:+d}" if val >= 0 else f"{val:d}"


class DND5e_Calculator(BaseCalculator):
    """Calculations engine for D&D 5th Edition."""

    def calculate(self, character: Dict[str, Any]) -> Dict[str, Any]:
        derived = {}
        level = int(character.get("level", 1))

        # Modifiers
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        mods = {ab: (scores.get(ab, 10) - 10) // 2 for ab in abilities}
        derived["ability_modifiers"] = {ab.title(): m for ab, m in mods.items()}

        # Proficiency
        prof = 2 + (level - 1) // 4
        derived["proficiency_bonus"] = prof

        # HP
        raw_hd = str(character.get("class_data", {}).get("hit_die", "8")).lower()
        try:
            hit_die = int(raw_hd.split('d')[-1])
        except ValueError:
            hit_die = 8
        con_mod = mods["constitution"]
        hp = hit_die + con_mod + (level - 1) * (hit_die // 2 + 1 + con_mod)
        derived["hit_points"] = max(1, hp)

        # Initiative
        derived["initiative"] = mods["dexterity"]

        # AC
        derived["armor_class"] = 10 + mods["dexterity"]

        # Saving Throws
        proficient_saves = character.get("class_data", {}).get("saving_throws", [])
        saving_throws = {}
        for ab in abilities:
            is_prof = ab.title() in proficient_saves or ab in proficient_saves
            saving_throws[ab.title()] = mods[ab] + (prof if is_prof else 0)
        derived["saving_throws"] = saving_throws

        # Skills
        skill_map = {
            "Acrobatics": "dexterity", "Animal Handling": "wisdom", "Arcana": "intelligence",
            "Athletics": "strength", "Deception": "charisma", "History": "intelligence",
            "Insight": "wisdom", "Intimidation": "charisma", "Investigation": "intelligence",
            "Medicine": "wisdom", "Nature": "intelligence", "Perception": "wisdom",
            "Performance": "charisma", "Persuasion": "charisma", "Religion": "intelligence",
            "Sleight of Hand": "dexterity", "Stealth": "dexterity", "Survival": "wisdom"
        }
        skills = {}
        proficient_skills = character.get("proficient_skills", [])
        for skill, ab in skill_map.items():
            is_prof = skill in proficient_skills
            skills[skill] = mods[ab] + (prof if is_prof else 0)
        derived["skills"] = skills

        # Spell Save DC
        casting_stat = character.get("class_data", {}).get("spellcasting_ability", "intelligence").lower()
        casting_mod = mods.get(casting_stat, 0)
        derived["spell_save_dc"] = 8 + prof + casting_mod

        # Apply standard mechanics
        self.apply_mechanics(character, derived)

        return derived

    def apply_mechanics(self, character: Dict[str, Any], derived: Dict[str, Any]) -> None:
        active = self.get_active_mechanics(character)
        mechanics = active["mechanics"]
        
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        mods = {ab: (scores.get(ab, 10) - 10) // 2 for ab in abilities}
        
        hp_bonus = 0
        speed_bonus = 0
        init_bonus = 0
        ac_bonus = 0
        
        base_ac = 10
        armor_dex_cap = 999
        armor_adds_dex = True
        has_armor = False
        shield_bonus = 0
        
        for m in mechanics:
            target = m.get("target", "")
            val = m.get("value", 0)
            if isinstance(val, str):
                try:
                    val = int(val.replace("+", "").strip())
                except ValueError:
                    val = 0
                    
            if target == "hp":
                hp_bonus += val
            elif target == "speed":
                speed_bonus += val
            elif target == "initiative":
                init_bonus += val
            elif target == "ac":
                mode = m.get("mode", "add")
                if mode == "armor":
                    base_ac = val
                    has_armor = True
                    dex_max = m.get("dex_max")
                    if dex_max is not None:
                        armor_dex_cap = dex_max
                    else:
                        if val >= 16:
                            armor_dex_cap = 0
                            armor_adds_dex = False
                        elif val >= 12:
                            armor_dex_cap = 2
                            armor_adds_dex = True
                        else:
                            armor_dex_cap = 999
                            armor_adds_dex = True
                elif mode == "shield":
                    shield_bonus += val
                elif mode == "natural_armor":
                    base_ac = max(base_ac, val)
                    has_armor = True
                else:
                    ac_bonus += val
                    
        dex_mod = mods["dexterity"]
        if armor_adds_dex:
            dex_contrib = min(dex_mod, armor_dex_cap)
            if dex_contrib < 0 and armor_dex_cap == 0:
                dex_contrib = 0
        else:
            dex_contrib = 0
            
        if not has_armor:
            base_ac = 10 + dex_mod
            dex_contrib = 0
            
        final_ac = base_ac + dex_contrib + shield_bonus + ac_bonus
        derived["armor_class"] = final_ac
        
        derived["hit_points"] += hp_bonus
        derived["initiative"] += init_bonus
        
        for m in mechanics:
            target = m.get("target", "")
            val = m.get("value", 0)
            if isinstance(val, str):
                try: val = int(val.replace("+", ""))
                except: val = 0
            if target.startswith("saving_throws."):
                parts = target.split('.')
                save_type = parts[1].capitalize()
                if save_type == "All":
                    for s in derived["saving_throws"]:
                        derived["saving_throws"][s] += val
                elif save_type in derived["saving_throws"]:
                    derived["saving_throws"][save_type] += val
                    
        for m in mechanics:
            target = m.get("target", "")
            val = m.get("value", 0)
            if isinstance(val, str):
                try: val = int(val.replace("+", ""))
                except: val = 0
            if target.startswith("skills."):
                parts = target.split('.')
                skill_name = parts[1].title()
                if skill_name in derived["skills"]:
                    derived["skills"][skill_name] += val



class PF1e_Calculator(BaseCalculator):
    """Calculations engine for Pathfinder 1st Edition."""

    def calculate(self, character: Dict[str, Any]) -> Dict[str, Any]:
        derived = {}
        level = int(character.get("level", 1))

        # Modifiers
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        mods = {ab: (scores.get(ab, 10) - 10) // 2 for ab in abilities}
        derived["ability_modifiers"] = {ab.title(): m for ab, m in mods.items()}

        # Initiative
        derived["initiative"] = mods["dexterity"]

        # BAB
        bab_prog = character.get("class_data", {}).get("bab_progression", "medium")
        if bab_prog == "full":
            bab = level
        elif bab_prog == "medium":
            bab = (level * 3) // 4
        else:
            bab = level // 2
        derived["bab"] = bab

        # Melee & Ranged attack bonus
        derived["melee_attack_bonus"] = bab + mods["strength"]
        derived["ranged_attack_bonus"] = bab + mods["dexterity"]

        # CMB & CMD
        size_mod = int(character.get("size_modifier", 0))
        derived["cmb"] = bab + mods["strength"] - size_mod
        derived["cmd"] = 10 + bab + mods["strength"] + mods["dexterity"] - size_mod

        # AC (Touch & Flat-footed)
        armor_bonus = int(character.get("armor_bonus", 0))
        shield_bonus = int(character.get("shield_bonus", 0))
        natural_armor = int(character.get("natural_armor", 0))
        size_modifier_ac = int(character.get("size_modifier_ac", 0))

        derived["armor_class"] = 10 + mods["dexterity"] + armor_bonus + shield_bonus + natural_armor + size_modifier_ac
        derived["touch_ac"] = 10 + mods["dexterity"] + size_modifier_ac
        derived["flat_footed_ac"] = 10 + armor_bonus + shield_bonus + natural_armor + size_modifier_ac

        # Saves
        save_prog = character.get("class_data", {}).get("saving_throws", {})
        saves = {}
        for save_type, ab in [("fortitude", "constitution"), ("reflex", "dexterity"), ("will", "wisdom")]:
            prog = save_prog.get(save_type, "poor")
            base_save = (2 + level // 2) if prog == "good" else (level // 3)
            saves[save_type.title()] = base_save + mods[ab]
        derived["saving_throws"] = saves

        # Skills
        class_skills = character.get("class_data", {}).get("class_skills", [])
        skill_ranks = character.get("skill_ranks", {})
        pf_skills = [
            "Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disable Device",
            "Disguise", "Escape Artist", "Fly", "Handle Animal", "Heal", "Intimidate", "Linguistics",
            "Perception", "Perform", "Profession", "Ride", "Sense Motive", "Sleight of Hand",
            "Spellcraft", "Stealth", "Survival", "Swim", "Use Magic Device"
        ]
        skills = {}
        for sk in pf_skills:
            ranks = int(skill_ranks.get(sk, 0))
            ab_map = {
                "Climb": "strength", "Swim": "strength",
                "Acrobatics": "dexterity", "Disable Device": "dexterity", "Escape Artist": "dexterity", "Fly": "dexterity", "Ride": "dexterity", "Sleight of Hand": "dexterity", "Stealth": "dexterity",
                "Appraise": "intelligence", "Craft": "intelligence", "Linguistics": "intelligence", "Spellcraft": "intelligence",
                "Heal": "wisdom", "Perception": "wisdom", "Profession": "wisdom", "Sense Motive": "wisdom", "Survival": "wisdom",
                "Bluff": "charisma", "Diplomacy": "charisma", "Disguise": "charisma", "Handle Animal": "charisma", "Intimidate": "charisma", "Perform": "charisma", "Use Magic Device": "charisma"
            }
            ab = ab_map.get(sk, "wisdom")
            class_bonus = 3 if (sk in class_skills and ranks > 0) else 0
            skills[sk] = ranks + mods.get(ab, 0) + class_bonus
        derived["skills"] = skills

        # Apply standard mechanics
        self.apply_mechanics(character, derived)

        return derived

    def eval_formula(self, formula: str, character: Dict[str, Any], derived: Dict[str, Any]) -> int:
        if not isinstance(formula, str):
            try: return int(formula)
            except: return 0
            
        f = formula.strip()
        mods = derived.get("ability_modifiers", {})
        f = f.replace("@abilities.str.mod", str(mods.get("Strength", 0)))
        f = f.replace("@abilities.dex.mod", str(mods.get("Dexterity", 0)))
        f = f.replace("@abilities.con.mod", str(mods.get("Constitution", 0)))
        f = f.replace("@abilities.int.mod", str(mods.get("Intelligence", 0)))
        f = f.replace("@abilities.wis.mod", str(mods.get("Wisdom", 0)))
        f = f.replace("@abilities.cha.mod", str(mods.get("Charisma", 0)))
        
        level = character.get("level", 1)
        f = re.sub(r'@classes\.[a-zA-Z0-9_]+\.level', str(level), f)
        
        if "?" in f and ":" in f:
            match = re.match(r'(.*?)\?(.*?):(.*?)$', f)
            if match:
                cond, val_true, val_false = match.groups()
                try:
                    cond_eval = eval(cond, {"__builtins__": None}, {})
                    f = val_true if cond_eval else val_false
                except Exception:
                    f = val_false
                    
        try:
            f_clean = re.sub(r'[^0-9+\-*/\s().]', '', f)
            return int(eval(f_clean, {"__builtins__": None}, {}))
        except Exception:
            try:
                nums = re.findall(r'-?\d+', f)
                return int(nums[0]) if nums else 0
            except Exception:
                return 0

    def apply_mechanics(self, character: Dict[str, Any], derived: Dict[str, Any]) -> None:
        active = self.get_active_mechanics(character)
        mechanics = active["mechanics"]
        
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        mods = {ab: (scores.get(ab, 10) - 10) // 2 for ab in abilities}
        
        armor_bonus = 0
        shield_bonus = 0
        natural_armor = 0
        deflection_bonus = 0
        other_ac_bonus = 0
        dex_max = 999
        
        for m in mechanics:
            target = m.get("target", "")
            val = m.get("value", 0)
            if isinstance(val, str):
                val = self.eval_formula(val, character, derived)
                
            mode = m.get("mode", "add")
            
            m_dex_max = m.get("dex_max")
            if m_dex_max is not None:
                dex_max = min(dex_max, m_dex_max)
                
            if target == "ac":
                if mode == "armor":
                    armor_bonus += val
                elif mode == "shield":
                    shield_bonus += val
                elif mode == "natural_armor":
                    natural_armor += val
                elif mode == "deflection":
                    deflection_bonus += val
                else:
                    other_ac_bonus += val
            elif target == "hp":
                derived["hit_points"] = derived.get("hit_points", 10) + val
            elif target == "initiative":
                derived["initiative"] += val
            elif target == "bab":
                derived["bab"] += val
            elif target == "cmb":
                derived["cmb"] += val
            elif target == "cmd":
                derived["cmd"] += val
            elif target.startswith("saving_throws."):
                parts = target.split('.')
                save_type = parts[1].capitalize()
                if save_type == "All":
                    for s in derived["saving_throws"]:
                        derived["saving_throws"][s] += val
                elif save_type in derived["saving_throws"]:
                    derived["saving_throws"][save_type] += val
            elif target.startswith("skills."):
                parts = target.split('.')
                skill_name = parts[1].title()
                if skill_name in derived["skills"]:
                    derived["skills"][skill_name] += val
                    
        dex_mod = mods["dexterity"]
        dex_contrib = min(dex_mod, dex_max)
        
        size_modifier_ac = int(character.get("size_modifier_ac", 0))
        
        derived["armor_class"] = 10 + dex_contrib + armor_bonus + shield_bonus + natural_armor + deflection_bonus + other_ac_bonus + size_modifier_ac
        derived["touch_ac"] = 10 + dex_contrib + deflection_bonus + size_modifier_ac + other_ac_bonus
        derived["flat_footed_ac"] = 10 + armor_bonus + shield_bonus + natural_armor + deflection_bonus + size_modifier_ac + other_ac_bonus
        
        size_mod = int(character.get("size_modifier", 0))
        str_mod = mods["strength"]
        derived["melee_attack_bonus"] = derived["bab"] + str_mod
        derived["ranged_attack_bonus"] = derived["bab"] + dex_mod
        derived["cmb"] = derived["bab"] + str_mod - size_mod
        derived["cmd"] = 10 + derived["bab"] + str_mod + dex_contrib - size_mod + deflection_bonus



class MnM3e_Calculator(BaseCalculator):
    """Calculations engine for Mutants & Masterminds 3rd Edition."""

    def calculate(self, character: Dict[str, Any]) -> Dict[str, Any]:
        derived = {}
        pl = int(character.get("pl_value", 10))

        # Modifiers (direct ranks in MM3e)
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "stamina", "agility", "dexterity", "fighting", "intellect", "awareness", "presence"]
        mods = {ab: scores.get(ab, 0) for ab in abilities}
        derived["ability_modifiers"] = {ab.title(): m for ab, m in mods.items()}

        # Initiative
        derived["initiative"] = mods["agility"]

        # Defenses
        defense_ranks = character.get("defenses", {})
        defenses = {
            "Dodge": mods["agility"] + int(defense_ranks.get("Dodge", 0)),
            "Parry": mods["fighting"] + int(defense_ranks.get("Parry", 0)),
            "Toughness": mods["stamina"] + int(defense_ranks.get("Toughness", 0)),
            "Fortitude": mods["stamina"] + int(defense_ranks.get("Fortitude", 0)),
            "Will": mods["awareness"] + int(defense_ranks.get("Will", 0)),
        }
        derived["defenses"] = defenses

        # Skills
        skill_ranks = character.get("skill_ranks", {})
        mm_skills = {
            "Acrobatics": "agility", "Athletics": "strength", "Close Combat": "fighting",
            "Deception": "presence", "Expertise": "intellect", "Insight": "awareness",
            "Intimidation": "presence", "Investigation": "intellect", "Perception": "awareness",
            "Persuasion": "presence", "Ranged Combat": "dexterity", "Sleight of Hand": "dexterity",
            "Stealth": "agility", "Technology": "intellect", "Treatment": "intellect", "Vehicles": "dexterity"
        }
        skills = {}
        for sk, ab in mm_skills.items():
            ranks = int(skill_ranks.get(sk, 0))
            skills[sk] = ranks + mods[ab]
        derived["skills"] = skills

        # Apply standard mechanics
        self.apply_mechanics(character, derived)

        return derived

    def apply_mechanics(self, character: Dict[str, Any], derived: Dict[str, Any]) -> None:
        active = self.get_active_mechanics(character)
        mechanics = active["mechanics"]
        
        # 1. Apply additional modifiers to defenses and skills
        for m in mechanics:
            target = m.get("target", "")
            val = m.get("value", 0)
            if isinstance(val, str):
                try: val = int(val.replace("+", ""))
                except: val = 0
            if target == "initiative":
                derived["initiative"] += val
            elif target == "dodge" or target == "dodge_defense":
                derived["defenses"]["Dodge"] += val
            elif target == "parry" or target == "parry_defense":
                derived["defenses"]["Parry"] += val
            elif target == "toughness" or target == "toughness_defense":
                derived["defenses"]["Toughness"] += val
            elif target == "fortitude" or target == "fortitude_defense":
                derived["defenses"]["Fortitude"] += val
            elif target == "will" or target == "will_defense":
                derived["defenses"]["Will"] += val
            elif target.startswith("skills."):
                parts = target.split('.')
                skill_name = parts[1].title()
                if skill_name in derived["skills"]:
                    derived["skills"][skill_name] += val
                    
        # 2. Enforce M&M 3e Power Level defense caps
        pl = int(character.get("pl_value", 10))
        cap = 2 * pl
        
        dodge = derived["defenses"]["Dodge"]
        toughness = derived["defenses"]["Toughness"]
        if dodge + toughness > cap:
            derived["defenses"]["Dodge"] = cap - toughness
            
        parry = derived["defenses"]["Parry"]
        if parry + toughness > cap:
            derived["defenses"]["Parry"] = cap - toughness
            
        fort = derived["defenses"]["Fortitude"]
        will = derived["defenses"]["Will"]
        if fort + will > cap:
            derived["defenses"]["Will"] = cap - fort

