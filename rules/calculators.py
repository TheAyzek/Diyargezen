from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
import re

def extract_weight_and_qty(item: Dict[str, Any]) -> tuple[float, int]:
    # Quantity extraction
    qty = item.get("quantity")
    if qty is None:
        sv = item.get("sistem_verisi") or item.get("system_data") or {}
        if isinstance(sv, dict):
            qty = sv.get("quantity")
            if qty is None:
                qty = sv.get("system", {}).get("quantity") if isinstance(sv.get("system"), dict) else None
    try:
        qty = int(qty) if qty is not None else 1
    except:
        qty = 1

    # Weight extraction
    weight_val = 0.0
    sv = item.get("sistem_verisi") or item.get("system_data") or {}
    if isinstance(sv, dict):
        w_obj = sv.get("weight")
        if w_obj is None:
            w_obj = sv.get("system", {}).get("weight") if isinstance(sv.get("system"), dict) else None
        
        if isinstance(w_obj, dict):
            weight_val = w_obj.get("value", 0.0)
        elif isinstance(w_obj, (int, float)):
            weight_val = w_obj
        elif isinstance(w_obj, str):
            try:
                weight_val = float(w_obj)
            except:
                weight_val = 0.0
    try:
        weight_val = float(weight_val)
    except:
        weight_val = 0.0
        
    return weight_val, qty

def categorize_items(equipment_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    categories = {
        "weapons": [],
        "armor_shields": [],
        "consumables": [],
        "gear": []
    }
    for item in equipment_list:
        if not isinstance(item, dict):
            continue
        sv = item.get("sistem_verisi") or item.get("system_data") or {}
        if not isinstance(sv, dict):
            sv = {}
        sys_obj = sv.get("system", {}) if isinstance(sv.get("system"), dict) else {}
        
        itype = str(item.get("type", sv.get("type", sys_obj.get("type", "")))).lower()
        name_lower = str(item.get("name", "")).lower()
        
        if itype == "weapon" or "weapon" in name_lower or "sword" in name_lower or "dagger" in name_lower or "mace" in name_lower or "bow" in name_lower or "hammer" in name_lower or "axe" in name_lower:
            categories["weapons"].append(item)
        elif itype in ("armor", "shield") or "armor" in name_lower or "shield" in name_lower or "mail" in name_lower or "plate" in name_lower:
            categories["armor_shields"].append(item)
        elif itype == "consumable" or "potion" in name_lower or "scroll" in name_lower or "wand" in name_lower or "elixir" in name_lower or "oil" in name_lower:
            categories["consumables"].append(item)
        else:
            categories["gear"].append(item)
            
    return categories

def _extract_mechanics_from_payload(sys_ver: Dict[str, Any]) -> List[Dict[str, Any]]:
    mechs = list(sys_ver.get("standard_mechanics", []))
    bonuses = sys_ver.get("bonuses", [])
    if isinstance(bonuses, list):
        for b in bonuses:
            if not isinstance(b, dict):
                continue
            b_type = b.get("type")
            val = b.get("value", 0)
            try:
                val = int(val)
            except (ValueError, TypeError):
                val = 0

            if b_type == "initiative":
                mechs.append({"target": "initiative", "value": val})
            elif b_type == "save_fortitude":
                mechs.append({"target": "saving_throws.Fortitude", "value": val})
            elif b_type == "save_reflex":
                mechs.append({"target": "saving_throws.Reflex", "value": val})
            elif b_type == "save_will":
                mechs.append({"target": "saving_throws.Will", "value": val})
            elif b_type == "save_all":
                mechs.append({"target": "saving_throws.All", "value": val})
            elif b_type == "skill":
                sk = b.get("skill")
                if sk:
                    m = {"target": f"skills.{sk}", "value": val}
                    if b.get("makes_class_skill"):
                        m["makes_class_skill"] = True
                        m["skill_name"] = sk
                    mechs.append(m)
            elif b_type == "armor_check_penalty":
                mechs.append({"target": "armor_check_penalty", "value": val})
            elif b_type in ("armor_class", "ac"):
                mechs.append({"target": "ac", "value": val})
            elif b_type == "hp":
                mechs.append({"target": "hp", "value": val})
            elif b_type == "bab":
                mechs.append({"target": "bab", "value": val})
    return mechs

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
        Query SQLite for active entities (Race, Class, Feats, Equipment, Traits)
        and fetch their 'standard_mechanics', 'bonuses', 'prerequisites', or parse descriptions.
        Checks in-memory entity dicts first.
        """
        import sqlite3
        import json
        from rules.rule_parser import RuleParser
        
        sys_key = character.get("system", "").lower().replace("_", "").replace("-", "")
        if "pf" in sys_key or "pathfinder" in sys_key:
            sys_db = "pathfinder1e"
        elif "mm" in sys_key:
            sys_db = "mm3e"
        else:
            sys_db = "dnd5e"

        active_mechanics = []
        active_prerequisites = []
        applied_modifiers = []
        
        # Helper to process in-memory dictionaries
        def process_entity(name: str, data: Any, category: str):
            if not isinstance(data, dict):
                return False
            
            desc = data.get("aciklama") or data.get("description") or ""
            sys_ver = data.get("sistem_verisi") or data.get("system") or data.get("data") or {}
            if not isinstance(sys_ver, dict):
                sys_ver = {}
                
            active_prerequisites.extend(sys_ver.get("prerequisites", []))
            
            explicit_mechs = _extract_mechanics_from_payload(sys_ver)
            explicit_targets = set()
            for m in explicit_mechs:
                m_copy = m.copy()
                m_copy["source"] = name
                m_copy["type"] = category
                active_mechanics.append(m_copy)
                
                val = m.get("value", 0)
                try:
                    val = int(str(val).replace("+", ""))
                except:
                    val = 0
                applied_modifiers.append({
                    "target": m.get("target", ""),
                    "value": val,
                    "type": category,
                    "source": name,
                    "description": m.get("description") or f"+{val} bonus ({name})"
                })
                explicit_targets.add(m.get("target", ""))

            # Process ability score increases (e.g. for races)
            asi = sys_ver.get("ability_score_increase") or sys_ver.get("modifiers")
            if isinstance(asi, dict):
                for ab_name, b_val in asi.items():
                    try:
                        val_int = int(b_val)
                        if val_int != 0:
                            applied_modifiers.append({
                                "target": f"abilities.{ab_name.title()}",
                                "value": val_int,
                                "type": category,
                                "source": name,
                                "description": f"+{val_int} {ab_name.title()} ({name})"
                            })
                    except (ValueError, TypeError):
                        pass
            
            # Dynamic parsing for missing targets
            parsed = RuleParser.parse_description(desc, sys_db, name, category)
            for p in parsed:
                if p["target"] not in explicit_targets:
                    active_mechanics.append(p)
                    applied_modifiers.append(p)
            return True

        names_to_query = []
        
        # 1. Race
        race = character.get("race")
        race_data = character.get("race_data")
        if not process_entity(race, race_data, "race") and isinstance(race, str) and race:
            names_to_query.append((race, "race"))
            
        # 2. Class
        cls = character.get("class")
        class_data = character.get("class_data")
        if not process_entity(cls, class_data, "class") and isinstance(cls, str) and cls:
            names_to_query.append((cls, "class"))
            
        # 3. Feats
        raw_feats = character.get("feats", [])
        if isinstance(raw_feats, list):
            for f in raw_feats:
                if isinstance(f, dict):
                    f_name = f.get("name") or f.get("isim")
                    if not process_entity(f_name, f, "feat") and f_name:
                        names_to_query.append((f_name, "feat"))
                elif isinstance(f, str) and f:
                    names_to_query.append((f, "feat"))
                    
        # 4. Equipment
        raw_items = character.get("equipment", [])
        if isinstance(raw_items, list):
            for item in raw_items:
                if isinstance(item, dict):
                    i_name = item.get("name") or item.get("isim")
                    if not process_entity(i_name, item, "equipment") and i_name:
                        names_to_query.append((i_name, "equipment"))
                elif isinstance(item, str) and item:
                    names_to_query.append((item, "equipment"))

        # 5. Traits
        raw_traits = character.get("traits", [])
        if isinstance(raw_traits, list):
            for t in raw_traits:
                if isinstance(t, dict):
                    t_name = t.get("name") or t.get("isim")
                    if not process_entity(t_name, t, "trait") and t_name:
                        names_to_query.append((t_name, "trait"))
                elif isinstance(t, str) and t:
                    names_to_query.append((t, "trait"))

        # Query database for entities without in-memory detailed data
        if names_to_query:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                placeholders = ",".join("?" for _ in names_to_query)
                query_names = [n[0] for n in names_to_query]
                cursor.execute(
                    f"SELECT isim, aciklama, sistem_verisi FROM entities WHERE sistem = ? AND isim IN ({placeholders})",
                    [sys_db] + query_names
                )
                
                rows = cursor.fetchall()
                db_entities = {row[0]: (row[1] or "", json.loads(row[2]) if row[2] else {}) for row in rows}
                
                for name, category in names_to_query:
                    if name in db_entities:
                        desc, payload = db_entities[name]
                        
                        active_prerequisites.extend(payload.get("prerequisites", []))
                        
                        explicit_mechs = _extract_mechanics_from_payload(payload)
                        explicit_targets = set()
                        for m in explicit_mechs:
                            m_copy = m.copy()
                            m_copy["source"] = name
                            m_copy["type"] = category
                            active_mechanics.append(m_copy)
                            
                            val = m.get("value", 0)
                            try:
                                val = int(str(val).replace("+", ""))
                            except:
                                val = 0
                            applied_modifiers.append({
                                "target": m.get("target", ""),
                                "value": val,
                                "type": category,
                                "source": name,
                                "description": m.get("description") or f"+{val} bonus ({name})"
                            })
                            explicit_targets.add(m.get("target", ""))
                        
                        parsed = RuleParser.parse_description(desc, sys_db, name, category)
                        for p in parsed:
                            if p["target"] not in explicit_targets:
                                active_mechanics.append(p)
                                applied_modifiers.append(p)
                                
                conn.close()
            except Exception:
                pass
                
        return {
            "mechanics": active_mechanics,
            "prerequisites": active_prerequisites,
            "applied_modifiers": applied_modifiers
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
        derived["ability_scores"] = {ab.title(): scores.get(ab, 10) for ab in abilities}
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

        # Spell Save DC & Spellcasting Ability
        class_name = str(character.get("class", "")).lower()
        casting_stat = character.get("class_data", {}).get("spellcasting_ability", "")
        if not casting_stat:
            if any(c in class_name for c in ("wizard", "artificer")):
                casting_stat = "intelligence"
            elif any(c in class_name for c in ("sorcerer", "bard", "warlock", "paladin")):
                casting_stat = "charisma"
            elif any(c in class_name for c in ("cleric", "druid", "ranger")):
                casting_stat = "wisdom"
            else:
                if character.get("class_data", {}).get("spellcasting"):
                    casting_stat = "intelligence"
                else:
                    casting_stat = ""

        if casting_stat:
            derived["spellcasting_ability"] = casting_stat.title()
            casting_mod = mods.get(casting_stat.lower(), 0)
            derived["spell_save_dc"] = 8 + prof + casting_mod
        else:
            derived["spell_save_dc"] = 0

        # Envanter Ağırlık Hesabı
        total_weight = 0.0
        for item in character.get("equipment", []):
            if isinstance(item, dict):
                w_val, qty = extract_weight_and_qty(item)
                total_weight += w_val * qty
        if total_weight == 0.0:
            for cat in ("weapons", "armor_shields", "consumables", "gear"):
                for item in character.get(cat, []):
                    if isinstance(item, dict):
                        w_val, qty = extract_weight_and_qty(item)
                        total_weight += w_val * qty
        derived["total_weight"] = round(total_weight, 2)

        # Categorize equipment lists for display
        categorized = categorize_items(character.get("equipment", []))
        derived["weapons"] = categorized["weapons"]
        derived["armor_shields"] = categorized["armor_shields"]
        derived["consumables"] = categorized["consumables"]
        derived["gear"] = categorized["gear"]
        
        str_score = scores.get("strength", 10)
        carrying_cap = str_score * 15
        enc_limit = str_score * 5
        heavy_enc_limit = str_score * 10
        
        derived["carrying_capacity"] = {
            "light": enc_limit,
            "medium": heavy_enc_limit,
            "heavy": carrying_cap
        }
        
        if total_weight <= enc_limit:
            derived["encumbrance_status"] = "Light"
        elif total_weight <= heavy_enc_limit:
            derived["encumbrance_status"] = "Medium"
        elif total_weight <= carrying_cap:
            derived["encumbrance_status"] = "Heavy"
        else:
            derived["encumbrance_status"] = "Overloaded"

        # DND 5e Büyü Slotları
        spell_slots = {}
        casting_ability = derived.get("spellcasting_ability", "")
        if casting_ability:
            casting_stat = casting_ability.lower()
            
            DND_FULL_CASTER_SLOTS = {
                1: (2, 0, 0, 0, 0, 0, 0, 0, 0), 2: (3, 0, 0, 0, 0, 0, 0, 0, 0),
                3: (4, 2, 0, 0, 0, 0, 0, 0, 0), 4: (4, 3, 0, 0, 0, 0, 0, 0, 0),
                5: (4, 3, 2, 0, 0, 0, 0, 0, 0), 6: (4, 3, 3, 0, 0, 0, 0, 0, 0),
                7: (4, 3, 3, 1, 0, 0, 0, 0, 0), 8: (4, 3, 3, 2, 0, 0, 0, 0, 0),
                9: (4, 3, 3, 3, 1, 0, 0, 0, 0), 10: (4, 3, 3, 3, 2, 0, 0, 0, 0),
                11: (4, 3, 3, 3, 2, 1, 0, 0, 0), 12: (4, 3, 3, 3, 2, 1, 0, 0, 0),
                13: (4, 3, 3, 3, 2, 1, 1, 0, 0), 14: (4, 3, 3, 3, 2, 1, 1, 0, 0),
                15: (4, 3, 3, 3, 2, 1, 1, 1, 0), 16: (4, 3, 3, 3, 2, 1, 1, 1, 0),
                17: (4, 3, 3, 3, 2, 1, 1, 1, 1), 18: (4, 3, 3, 3, 3, 1, 1, 1, 1),
                19: (4, 3, 3, 3, 3, 2, 1, 1, 1), 20: (4, 3, 3, 3, 3, 2, 2, 1, 1)
            }
            DND_HALF_CASTER_SLOTS = {
                1: (0, 0, 0, 0, 0), 2: (2, 0, 0, 0, 0), 3: (3, 0, 0, 0, 0), 4: (3, 0, 0, 0, 0),
                5: (4, 2, 0, 0, 0), 6: (4, 2, 0, 0, 0), 7: (4, 3, 0, 0, 0), 8: (4, 3, 0, 0, 0),
                9: (4, 3, 2, 0, 0), 10: (4, 3, 2, 0, 0), 11: (4, 3, 3, 0, 0), 12: (4, 3, 3, 0, 0),
                13: (4, 3, 3, 1, 0), 14: (4, 3, 3, 1, 0), 15: (4, 3, 3, 2, 0), 16: (4, 3, 3, 2, 0),
                17: (4, 3, 3, 3, 1), 18: (4, 3, 3, 3, 1), 19: (4, 3, 3, 3, 2), 20: (4, 3, 3, 3, 2)
            }
            DND_THIRD_CASTER_SLOTS = {
                1: (0, 0, 0, 0), 2: (0, 0, 0, 0), 3: (2, 0, 0, 0), 4: (3, 0, 0, 0),
                5: (3, 0, 0, 0), 6: (3, 0, 0, 0), 7: (4, 2, 0, 0), 8: (4, 2, 0, 0),
                9: (4, 2, 0, 0), 10: (4, 3, 0, 0), 11: (4, 3, 0, 0), 12: (4, 3, 0, 0),
                13: (4, 3, 2, 0), 14: (4, 3, 2, 0), 15: (4, 3, 2, 0), 16: (4, 3, 3, 0),
                17: (4, 3, 3, 0), 18: (4, 3, 3, 0), 19: (4, 3, 3, 1), 20: (4, 3, 3, 1)
            }
            
            is_low = any(c in class_name for c in ("paladin", "ranger"))
            is_mid = any(c in class_name for c in ("knight", "trickster", "arcane"))
            
            if is_low:
                slots = DND_HALF_CASTER_SLOTS.get(level, (0, 0, 0, 0, 0))
            elif is_mid:
                slots = DND_THIRD_CASTER_SLOTS.get(level, (0, 0, 0, 0))
            else:
                slots = DND_FULL_CASTER_SLOTS.get(level, (0, 0, 0, 0, 0, 0, 0, 0, 0))
                
            for spell_lvl, val in enumerate(slots, 1):
                if val > 0:
                    spell_slots[str(spell_lvl)] = val
                    
        derived["spell_slots"] = spell_slots

        # Apply standard mechanics
        self.apply_mechanics(character, derived)
        derived["applied_modifiers"] = self.get_active_mechanics(character).get("applied_modifiers", [])

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
    """Calculations engine for Pathfinder 1st Edition ONLY.
    PF2e is explicitly NOT supported — all rules follow PF1e (d20 PFRPG).
    """

    # ------------------------------------------------------------------ #
    # Armor Check Penalty applies to these skills (PF1e Core Rulebook)   #
    # ------------------------------------------------------------------ #
    ACP_SKILLS = {
        "Acrobatics", "Climb", "Disable Device", "Escape Artist",
        "Fly", "Ride", "Sleight of Hand", "Stealth", "Swim"
    }

    PF_SKILL_AB: Dict[str, str] = {
        "Climb": "strength", "Swim": "strength",
        "Acrobatics": "dexterity", "Disable Device": "dexterity",
        "Escape Artist": "dexterity", "Fly": "dexterity",
        "Ride": "dexterity", "Sleight of Hand": "dexterity", "Stealth": "dexterity",
        "Appraise": "intelligence", "Craft": "intelligence",
        "Linguistics": "intelligence", "Spellcraft": "intelligence",
        "Heal": "wisdom", "Perception": "wisdom", "Profession": "wisdom",
        "Sense Motive": "wisdom", "Survival": "wisdom",
        "Bluff": "charisma", "Diplomacy": "charisma", "Disguise": "charisma",
        "Handle Animal": "charisma", "Intimidate": "charisma",
        "Perform": "charisma", "Use Magic Device": "charisma",
        "Knowledge (Arcana)": "intelligence", "Knowledge (Dungeoneering)": "intelligence",
        "Knowledge (Engineering)": "intelligence", "Knowledge (Geography)": "intelligence",
        "Knowledge (History)": "intelligence", "Knowledge (Local)": "intelligence",
        "Knowledge (Nature)": "intelligence", "Knowledge (Nobility)": "intelligence",
        "Knowledge (Planes)": "intelligence", "Knowledge (Religion)": "intelligence",
    }

    PF_SKILL_LIST = [
        "Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disable Device",
        "Disguise", "Escape Artist", "Fly", "Handle Animal", "Heal", "Intimidate", "Linguistics",
        "Perception", "Perform", "Profession", "Ride", "Sense Motive", "Sleight of Hand",
        "Spellcraft", "Stealth", "Survival", "Swim", "Use Magic Device",
        "Knowledge (Arcana)", "Knowledge (Dungeoneering)", "Knowledge (Engineering)",
        "Knowledge (Geography)", "Knowledge (History)", "Knowledge (Local)",
        "Knowledge (Nature)", "Knowledge (Nobility)", "Knowledge (Planes)", "Knowledge (Religion)",
    ]

    # ------------------------------------------------------------------ #
    # MAIN PIPELINE — update_all_stats()                                   #
    # UI calls manager.recalculate_character() → this method             #
    # ------------------------------------------------------------------ #

    def update_all_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """PF1e 1st Edition — 5-step dependency-ordered calculation pipeline.

        ADIM 1: Ham Statlar + Irk Bonuslari → Stat Degistiriciler (Modifiers)
        ADIM 2: Sinif verisi → BAB progression, Base Saves, Skill Ranks/Class Skills
        ADIM 3: Feat/Trait mekanikleri → AC, saves, skills'e dogrudan etki
        ADIM 4: Envanter tarama → Armor Check Penalty, Max Dex siniri, AC bilesenler
        ADIM 5: Nihai CMB, CMD, Inisiyatif, HP → character_state'e yaz
        """
        derived: Dict[str, Any] = {}
        level = max(1, int(character.get("level", 1)))

        # ── ADIM 1: Stat skorlari + irk bonuslari → modifierlar ─────────────────
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        mods = {ab: (scores.get(ab, 10) - 10) // 2 for ab in abilities}
        derived["ability_scores"]    = {ab.title(): scores.get(ab, 10) for ab in abilities}
        derived["ability_modifiers"] = {ab.title(): mods[ab] for ab in abilities}

        # ── ADIM 2: Sinif → BAB, Base Saves, Class Skills, HP die ───────────────
        class_data   = character.get("class_data", {}) or {}
        bab_prog     = str(class_data.get("bab_progression", "medium")).lower()
        class_skills = class_data.get("class_skills", []) or []

        # ── ADIM 3 Pre-fetch: Fetch mechanics early to find extra class skills ──
        active    = self.get_active_mechanics(character)
        mechanics = active.get("mechanics", [])

        class_skills_set = set(class_skills)
        for m in mechanics:
            if m.get("makes_class_skill") and m.get("skill_name"):
                class_skills_set.add(m.get("skill_name"))

        # BAB (PF1e Core: Full=level, Medium=3/4*level, Poor=1/2*level)
        if bab_prog == "full":
            bab = level
        elif bab_prog == "medium":
            bab = (level * 3) // 4
        else:
            bab = level // 2
        derived["bab"] = bab

        # Base Saves (Good: 2 + level/2, Poor: level/3)
        save_prog = class_data.get("saving_throws", {}) or {}
        saves: Dict[str, int] = {}
        for save_type, ab in [("fortitude", "constitution"), ("reflex", "dexterity"), ("will", "wisdom")]:
            prog      = str(save_prog.get(save_type, "poor")).lower()
            base_save = (2 + level // 2) if prog == "good" else (level // 3)
            saves[save_type.title()] = base_save + mods[ab]
        derived["saving_throws"] = saves

        # HP (PF1e: Max at 1st, average+1 thereafter)
        hit_die_raw = str(class_data.get("hit_die", "8")).lower()
        try:
            hit_die = int(hit_die_raw.split("d")[-1])
        except ValueError:
            hit_die = 8
        con_mod = mods["constitution"]
        hp = hit_die + con_mod + (level - 1) * (hit_die // 2 + 1 + con_mod)
        derived["hit_points"] = max(1, hp)

        # Skill Ranks (each level: class_int_modifier + int_mod ranks; default rank source = character)
        skill_ranks = character.get("skill_ranks") or character.get("skills") or {}

        # ── ADIM 2b: Skill base values (Rank + Ability Mod + Class Skill +3) ────
        # PF1e Class Skill rule: +3 bonus ONLY if rank >= 1 AND skill is a class skill
        raw_skills: Dict[str, int] = {}
        for sk in self.PF_SKILL_LIST:
            ranks      = max(0, int(skill_ranks.get(sk, 0)))
            ab         = self.PF_SKILL_AB.get(sk, "intelligence")
            class_bonus = 3 if (sk in class_skills_set and ranks > 0) else 0
            raw_skills[sk] = ranks + mods.get(ab, 0) + class_bonus
        derived["skills"] = raw_skills

        # ── ADIM 3: Feat/Trait/Race mekanikleri uygula ──────────────────────────
        # (standard_mechanics JSON'dan ve traits'den gelen dogrudan bonus'lar)
        misc_ac_bonus  = 0
        deflect_bonus  = 0
        feat_bab_bonus = 0
        acp_reduction  = 0
        for m in mechanics:
            target = m.get("target", "")
            try:
                val = self.eval_formula(str(m.get("value", 0)), character, derived)
            except Exception:
                val = 0
            if target == "initiative":
                derived["initiative"] = derived.get("initiative", mods["dexterity"]) + val
            elif target == "hp":
                derived["hit_points"] += val
            elif target == "bab":
                feat_bab_bonus += val
            elif target == "ac":
                mode = m.get("mode", "add")
                if mode == "deflection":
                    deflect_bonus += val
                elif mode not in ("armor", "shield", "natural_armor"):
                    misc_ac_bonus += val
            elif target == "armor_check_penalty":
                acp_reduction += val
            elif target.startswith("saving_throws."):
                save_type = target.split(".")[1].capitalize()
                if save_type == "All":
                    for s in derived["saving_throws"]:
                        derived["saving_throws"][s] += val
                elif save_type in derived["saving_throws"]:
                    derived["saving_throws"][save_type] += val
            elif target.startswith("skills."):
                sk_name = target[len("skills."):]
                if sk_name in derived["skills"]:
                    derived["skills"][sk_name] += val

        derived["bab"] += feat_bab_bonus

        # ── ADIM 4: Envanter → Armor bilesenler + ACP + Max Dex siniri ──────────
        armor_bonus, shield_bonus, natural_armor, acp, dex_max = self._extract_armor(character)

        # Character-level overrides (dogrudan set edilmis degerler her zaman kazanir)
        armor_bonus   = max(armor_bonus, int(character.get("armor_bonus", 0)))
        shield_bonus  = max(shield_bonus, int(character.get("shield_bonus", 0)))
        natural_armor = int(character.get("natural_armor", 0))
        size_ac       = int(character.get("size_modifier_ac", 0))

        # Max Dex kısıtlamasını uygula
        dex_contrib = min(mods["dexterity"], dex_max) if dex_max < 999 else mods["dexterity"]

        # Armor Check Penalty → fiziksel becerilere uygula (sadece rank>0 olanlar)
        if acp < 0:
            if acp_reduction != 0:
                acp_adj = abs(acp_reduction) if acp_reduction < 0 else acp_reduction
                acp = min(0, acp + acp_adj)
            for sk in self.ACP_SKILLS:
                if sk in derived["skills"]:
                    ranks = max(0, int(skill_ranks.get(sk, 0)))
                    if ranks > 0:
                        derived["skills"][sk] += acp  # acp zaten negatif veya 0

        derived["armor_check_penalty"] = acp

        # ── ADIM 5: Nihai AC, CMB, CMD, Inisiyatif ──────────────────────────────
        size_cmb = int(character.get("size_modifier", 0))

        derived["armor_class"]    = 10 + dex_contrib + armor_bonus + shield_bonus + natural_armor + deflect_bonus + misc_ac_bonus + size_ac
        derived["touch_ac"]       = 10 + dex_contrib + deflect_bonus + misc_ac_bonus + size_ac
        derived["flat_footed_ac"] = 10 + armor_bonus + shield_bonus + natural_armor + deflect_bonus + misc_ac_bonus + size_ac
        derived["cmb"]            = derived["bab"] + mods["strength"] - size_cmb
        derived["cmd"]            = 10 + derived["bab"] + mods["strength"] + dex_contrib - size_cmb + deflect_bonus
        derived["melee_attack_bonus"]  = derived["bab"] + mods["strength"]
        derived["ranged_attack_bonus"] = derived["bab"] + mods["dexterity"]
        derived.setdefault("initiative", mods["dexterity"])

        # Envanter Ağırlık Hesabı
        total_weight = 0.0
        for item in character.get("equipment", []):
            if isinstance(item, dict):
                w_val, qty = extract_weight_and_qty(item)
                total_weight += w_val * qty
        if total_weight == 0.0:
            for cat in ("weapons", "armor_shields", "consumables", "gear"):
                for item in character.get(cat, []):
                    if isinstance(item, dict):
                        w_val, qty = extract_weight_and_qty(item)
                        total_weight += w_val * qty
        derived["total_weight"] = round(total_weight, 2)

        # Categorize equipment lists for display
        categorized = categorize_items(character.get("equipment", []))
        derived["weapons"] = categorized["weapons"]
        derived["armor_shields"] = categorized["armor_shields"]
        derived["consumables"] = categorized["consumables"]
        derived["gear"] = categorized["gear"]
        
        # Strength'e göre PF1e Carrying Capacity limitleri
        str_score = derived["ability_scores"].get("Strength", 10)
        
        PF_STR_LOADS = {
            1: (3, 6, 10), 2: (6, 13, 20), 3: (10, 20, 30), 4: (13, 26, 40), 5: (16, 33, 50),
            6: (20, 40, 60), 7: (23, 46, 70), 8: (26, 53, 80), 9: (30, 60, 90), 10: (33, 66, 100),
            11: (38, 76, 115), 12: (43, 86, 130), 13: (50, 100, 150), 14: (58, 116, 175), 15: (66, 133, 200),
            16: (76, 153, 230), 17: (86, 173, 260), 18: (100, 200, 300), 19: (116, 233, 350), 20: (133, 266, 400),
            21: (153, 306, 460), 22: (173, 346, 520), 23: (200, 400, 600), 24: (233, 466, 700), 25: (266, 533, 800),
            26: (306, 613, 920), 27: (346, 693, 1040), 28: (400, 800, 1200), 29: (466, 933, 1400)
        }
        
        if str_score <= 29:
            light, med, heavy = PF_STR_LOADS.get(max(1, str_score), (33, 66, 100))
        else:
            factor = 4 ** ((str_score - 20) // 10)
            base_str = (str_score - 20) % 10 + 20
            base_light, base_med, base_heavy = PF_STR_LOADS[base_str]
            light, med, heavy = base_light * factor, base_med * factor, base_heavy * factor
            
        derived["carrying_capacity"] = {
            "light": light,
            "medium": med,
            "heavy": heavy
        }
        
        if total_weight <= light:
            derived["encumbrance_status"] = "Light"
        elif total_weight <= med:
            derived["encumbrance_status"] = "Medium"
        elif total_weight <= heavy:
            derived["encumbrance_status"] = "Heavy"
        else:
            derived["encumbrance_status"] = "Overloaded"

        # PF1e Büyü Slotları
        spell_slots = {}
        casting_ability = class_data.get("spellcasting_ability", "")
        class_name_lower = str(character.get("class", "")).lower()
        if not casting_ability:
            if any(c in class_name_lower for c in ("wizard", "arcanist", "witch", "alchemist", "magus", "investigator")):
                casting_ability = "intelligence"
            elif any(c in class_name_lower for c in ("sorcerer", "bard", "summoner", "oracle", "bloodrager", "skald", "paladin", "mesmerist")):
                casting_ability = "charisma"
            elif any(c in class_name_lower for c in ("cleric", "druid", "ranger", "inquisitor", "shaman", "warpriest", "hunter", "spiritualist", "adept")):
                casting_ability = "wisdom"
                
        if casting_ability:
            casting_stat = casting_ability.lower()
            casting_mod = mods.get(casting_stat, 0)
            
            PF_FULL_CASTER_SLOTS = {
                1: (3, 1, 0, 0, 0, 0, 0, 0, 0, 0), 2: (4, 2, 0, 0, 0, 0, 0, 0, 0, 0),
                3: (4, 2, 1, 0, 0, 0, 0, 0, 0, 0), 4: (4, 3, 2, 0, 0, 0, 0, 0, 0, 0),
                5: (4, 3, 2, 1, 0, 0, 0, 0, 0, 0), 6: (4, 3, 3, 2, 0, 0, 0, 0, 0, 0),
                7: (4, 4, 3, 2, 1, 0, 0, 0, 0, 0), 8: (4, 4, 3, 3, 2, 0, 0, 0, 0, 0),
                9: (4, 4, 4, 3, 2, 1, 0, 0, 0, 0), 10: (4, 4, 4, 3, 3, 2, 0, 0, 0, 0),
                11: (4, 4, 4, 4, 3, 2, 1, 0, 0, 0), 12: (4, 4, 4, 4, 3, 3, 2, 0, 0, 0),
                13: (4, 4, 4, 4, 4, 3, 2, 1, 0, 0), 14: (4, 4, 4, 4, 4, 3, 3, 2, 0, 0),
                15: (4, 4, 4, 4, 4, 4, 3, 2, 1, 0), 16: (4, 4, 4, 4, 4, 4, 3, 3, 2, 0),
                17: (4, 4, 4, 4, 4, 4, 4, 3, 2, 1), 18: (4, 4, 4, 4, 4, 4, 4, 3, 3, 2),
                19: (4, 4, 4, 4, 4, 4, 4, 4, 3, 3), 20: (4, 4, 4, 4, 4, 4, 4, 4, 4, 4)
            }
            PF_MID_CASTER_SLOTS = {
                1: (4, 1, 0, 0, 0, 0, 0), 2: (5, 2, 0, 0, 0, 0, 0), 3: (6, 3, 0, 0, 0, 0, 0),
                4: (6, 3, 1, 0, 0, 0, 0), 5: (6, 4, 2, 0, 0, 0, 0), 6: (6, 4, 3, 0, 0, 0, 0),
                7: (6, 4, 3, 1, 0, 0, 0), 8: (6, 4, 4, 2, 0, 0, 0), 9: (6, 5, 4, 3, 0, 0, 0),
                10: (6, 5, 4, 3, 1, 0, 0), 11: (6, 5, 4, 4, 2, 0, 0), 12: (6, 5, 5, 4, 3, 0, 0),
                13: (6, 5, 5, 4, 3, 1, 0), 14: (6, 5, 5, 4, 4, 2, 0), 15: (6, 5, 5, 5, 4, 3, 0),
                16: (6, 5, 5, 5, 4, 3, 1), 17: (6, 5, 5, 5, 4, 4, 2), 18: (6, 5, 5, 5, 5, 4, 3),
                19: (6, 5, 5, 5, 5, 5, 4), 20: (6, 5, 5, 5, 5, 5, 5)
            }
            PF_LOW_CASTER_SLOTS = {
                1: (0, 0, 0, 0, 0), 2: (0, 0, 0, 0, 0), 3: (0, 0, 0, 0, 0), 4: (0, 0, 0, 0, 0),
                5: (0, 1, 0, 0, 0), 6: (0, 1, 0, 0, 0), 7: (0, 1, 1, 0, 0), 8: (0, 1, 1, 0, 0),
                9: (0, 2, 1, 0, 0), 10: (0, 2, 1, 1, 0), 11: (0, 2, 1, 1, 0), 12: (0, 2, 2, 1, 1),
                13: (0, 3, 2, 1, 1), 14: (0, 3, 2, 2, 1), 15: (0, 3, 2, 2, 1), 16: (0, 3, 3, 2, 2),
                17: (0, 4, 3, 2, 2), 18: (0, 4, 3, 3, 2), 19: (0, 4, 3, 3, 3), 20: (0, 4, 4, 3, 3)
            }
            
            is_low = any(c in class_name_lower for c in ("paladin", "ranger"))
            is_mid = any(c in class_name_lower for c in ("bard", "skald", "inquisitor", "alchemist"))
            
            if is_low:
                slots = list(PF_LOW_CASTER_SLOTS.get(level, (0, 0, 0, 0, 0)))
            elif is_mid:
                slots = list(PF_MID_CASTER_SLOTS.get(level, (0, 0, 0, 0, 0, 0, 0)))
            else:
                slots = list(PF_FULL_CASTER_SLOTS.get(level, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)))
                
            for spell_lvl in range(1, len(slots)):
                if slots[spell_lvl] > 0 or (is_low and level >= 5 and spell_lvl <= 4):
                    if casting_mod >= spell_lvl:
                        bonus = (casting_mod - spell_lvl) // 4 + 1
                        slots[spell_lvl] += bonus
                        
            for spell_lvl, val in enumerate(slots):
                if val > 0:
                    spell_slots[str(spell_lvl)] = val
                    
        derived["spell_slots"] = spell_slots

        # snake_case aliases (PDF export bunları kullanır)
        derived["skills"] = {
            k.lower().replace(" ", "_"): v
            for k, v in derived["skills"].items()
        }

        derived["applied_modifiers"] = self.get_active_mechanics(character).get("applied_modifiers", [])

        return derived

    def _extract_armor(self, character: Dict[str, Any]):
        armor_bonus, shield_bonus, natural_armor, acp, dex_max = 0, 0, 0, 0, 999
        for item in character.get("equipment", []):
            if not isinstance(item, dict): continue
            sv = item.get("sistem_verisi") or item.get("system_data") or {}
            if not isinstance(sv, dict): sv = {}
            sys_obj = sv.get("system", {}) if isinstance(sv.get("system"), dict) else {}
            
            itype = str(item.get("type", sv.get("type", sys_obj.get("type", "")))).lower()
            
            # Check for armor
            if itype in ("armor", "equipment") or "armor" in str(item.get("name", "")).lower() or "mail" in str(item.get("name", "")).lower() or "plate" in str(item.get("name", "")).lower():
                ac_data = sv.get("armor_class") or sv.get("armorClass") or sys_obj.get("armor") or {}
                if isinstance(ac_data, dict):
                    ab_val = ac_data.get("value") or ac_data.get("base") or 0
                    dm_val = ac_data.get("dex")
                else:
                    try: ab_val = int(ac_data)
                    except: ab_val = 0
                    dm_val = None
                
                try: ab_val = int(ab_val)
                except: ab_val = 0
                
                if ab_val > 0:
                    armor_bonus = max(armor_bonus, ab_val)
                    if dm_val is not None:
                        try: dex_max = min(dex_max, int(dm_val))
                        except: pass
                    
                    acp_val = sv.get("check_penalty") or sv.get("armor_check_penalty") or sys_obj.get("acp") or sys_obj.get("armor", {}).get("acp")
                    if acp_val is None:
                        acp_val = sys_obj.get("check_penalty") or sys_obj.get("armor_check_penalty") or 0
                    try: acp_val = int(acp_val)
                    except: acp_val = 0
                    
                    if acp_val == 0 and ab_val >= 6:
                        acp_val = -(ab_val - 3)
                    acp = min(acp, acp_val)
            
            # Check for shield
            if "shield" in str(item.get("name", "")).lower() or itype == "shield":
                sb_data = sv.get("armor_class") or sv.get("shield_bonus") or sys_obj.get("armor") or {}
                if isinstance(sb_data, dict):
                    sb_val = sb_data.get("value") or sb_data.get("base") or 0
                else:
                    try: sb_val = int(sb_data)
                    except: sb_val = 2
                
                try: sb_val = int(sb_val)
                except: sb_val = 2
                
                shield_bonus = max(shield_bonus, sb_val)
                
                acp_val = sv.get("check_penalty") or sys_obj.get("check_penalty") or sys_obj.get("acp") or 0
                try: acp_val = int(acp_val)
                except: acp_val = 0
                acp += acp_val
        return armor_bonus, shield_bonus, natural_armor, acp, dex_max

    def calculate(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Mevcut arayüz ile uyumluluk için — update_all_stats'a delege eder."""
        return self.update_all_stats(character)

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
    """Calculations engine for Mutants & Masterminds 3rd Edition.

    M&M 3e notu: Ability skorları DOĞRUDAN modifier olarak kullanılır
    (10 çıkarıp 2'ye bölme YOK — D&D/PF1e'den farklı).
    """

    MM_SKILLS: Dict[str, str] = {
        "Acrobatics":    "agility",
        "Athletics":     "strength",
        "Close Combat":  "fighting",
        "Deception":     "presence",
        "Expertise":     "intellect",
        "Insight":       "awareness",
        "Intimidation":  "presence",
        "Investigation": "intellect",
        "Perception":    "awareness",
        "Persuasion":    "presence",
        "Ranged Combat": "dexterity",
        "Sleight of Hand": "dexterity",
        "Stealth":       "agility",
        "Technology":    "intellect",
        "Treatment":     "intellect",
        "Vehicles":      "dexterity",
    }

    # ------------------------------------------------------------------ #
    # MAIN PIPELINE — update_all_stats()                                   #
    # ------------------------------------------------------------------ #

    def calculate(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Mevcut arayüz ile uyumluluk için — update_all_stats'a delege eder."""
        return self.update_all_stats(character)

    def update_all_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """M&M 3e — 5-step dependency-ordered calculation pipeline.

        ADIM 1: Ability Ranks → doğrudan modifier (M&M3e'de rank = modifier)
        ADIM 2: Archetype ve Power Level verisi → base defense ranks
        ADIM 3: Advantage mekanikleri → defense/skill/initiative bonusları
        ADIM 4: Ekipman/Device tarama → Toughness ve özel bonuslar
        ADIM 5: PL Defense Cap uygula (Dodge+Tough ≤ 2×PL vb.) → final yaz
        """
        derived: Dict[str, Any] = {}

        # ── ADIM 1: Ability Ranks (M&M3e: rank = modifier, 0 = normal) ─────────
        scores = self.get_adjusted_abilities(character)
        abilities = ["strength", "stamina", "agility", "dexterity",
                     "fighting", "intellect", "awareness", "presence"]
        mods = {ab: int(scores.get(ab, 0)) for ab in abilities}
        derived["ability_modifiers"] = {ab.title(): mods[ab] for ab in abilities}

        # Initiative = Agility rank (M&M3e Core, p.36)
        derived["initiative"] = mods["agility"]

        # ── ADIM 2: Power Level → base defense ranks ─────────────────────────
        pl = max(1, int(character.get("pl_value", 10)))
        derived["pl_value"] = pl
        # Archetype verisi (opsiyonel — base defense rank override)
        arch_data = character.get("class_data", {}) or character.get("archetype_data", {}) or {}

        defense_ranks = character.get("defenses", {}) or {}

        # ── ADIM 2b: Skills = Rank + Ability Modifier ──────────────────────────
        skill_ranks = character.get("skill_ranks", {}) or {}
        skills: Dict[str, int] = {}
        for sk, ab in self.MM_SKILLS.items():
            ranks = max(0, int(skill_ranks.get(sk, 0)))
            skills[sk] = ranks + mods[ab]
        derived["skills"] = skills

        # ── ADIM 3: Advantage/Power mekanikleri ─────────────────────────────
        active    = self.get_active_mechanics(character)
        mechanics = active.get("mechanics", [])

        init_bonus    = 0
        dodge_bonus   = 0
        parry_bonus   = 0
        tough_bonus   = 0
        fort_bonus    = 0
        will_bonus    = 0

        for m in mechanics:
            target = m.get("target", "")
            try:
                val = int(str(m.get("value", 0)).replace("+", "").strip())
            except (ValueError, TypeError):
                val = 0

            if target == "initiative":
                init_bonus += val
            elif target in ("dodge", "dodge_defense"):
                dodge_bonus += val
            elif target in ("parry", "parry_defense"):
                parry_bonus += val
            elif target in ("toughness", "toughness_defense"):
                tough_bonus += val
            elif target in ("fortitude", "fortitude_defense"):
                fort_bonus += val
            elif target in ("will", "will_defense"):
                will_bonus += val
            elif target.startswith("skills."):
                sk_name = target.split(".")[1].title()
                if sk_name in derived["skills"]:
                    derived["skills"][sk_name] += val

        derived["initiative"] += init_bonus

        # ── ADIM 4: Ekipman / Device tarama → Toughness bonus ────────────────
        equip_tough = 0
        for item in character.get("equipment", []):
            if not isinstance(item, dict):
                continue
            sv = item.get("sistem_verisi") or {}
            if not isinstance(sv, dict):
                sv = {}
            # Zırh / Toughness veren cihazlar
            tb = sv.get("toughness", sv.get("armor_toughness", 0))
            try:
                equip_tough += int(tb)
            except (ValueError, TypeError):
                pass

        # ── ADIM 5: Final defenses + PL cap uygula ───────────────────────────
        defenses = {
            "Dodge":      mods["agility"]  + int(defense_ranks.get("Dodge", 0))     + dodge_bonus,
            "Parry":      mods["fighting"] + int(defense_ranks.get("Parry", 0))     + parry_bonus,
            "Toughness":  mods["stamina"]  + int(defense_ranks.get("Toughness", 0)) + tough_bonus + equip_tough,
            "Fortitude":  mods["stamina"]  + int(defense_ranks.get("Fortitude", 0)) + fort_bonus,
            "Will":       mods["awareness"]+ int(defense_ranks.get("Will", 0))      + will_bonus,
        }

        # M&M 3e Power Level Defense Caps (Core Rulebook p.18)
        #   Dodge + Toughness  ≤ 2 × PL
        #   Parry + Toughness  ≤ 2 × PL
        #   Fortitude + Will   ≤ 2 × PL
        cap = 2 * pl

        toughness = defenses["Toughness"]
        if defenses["Dodge"] + toughness > cap:
            defenses["Dodge"] = max(0, cap - toughness)
        if defenses["Parry"] + toughness > cap:
            defenses["Parry"] = max(0, cap - toughness)

        fort = defenses["Fortitude"]
        will = defenses["Will"]
        if fort + will > cap:
            defenses["Will"] = max(0, cap - fort)

        derived["defenses"] = defenses
        return derived


# ===========================================================================
# ADIM 2 — BÜYÜ HESAPLAMA MOTORU (calculate_spells)
# Açık/Kapalı Prensibi: Aşağıdaki metodlar mevcut sınıflara EKLENTI olarak
# monkey-patch edilir. Hiçbir mevcut metod değiştirilmemiştir.
# ===========================================================================

def _dnd5e_calculate_spells(self, character: Dict[str, Any]) -> Dict[str, Any]:
    """D&D 5e Büyü Sistemi Hesaplayıcı (Plugin Metod).

    Döndürür:
        is_spellcaster     : bool   — karakter büyücü mü?
        spellcasting_ability: str   — INT / WIS / CHA
        spell_save_dc      : int    — 8 + prof + ability_mod
        spell_attack_bonus : int    — prof + ability_mod
        caster_type        : str    — "full" / "half" / "third" / "warlock" / "none"
        slots              : dict   — {"1": n, "2": n, ..., "9": n}  (Warlock: {"pact": n, "slot_level": k})
        known_spells       : list   — DB'den çekilen sınıf büyü listesi (ilk 30)
    """
    import sqlite3
    import json as _json

    result: Dict[str, Any] = {
        "is_spellcaster": False,
        "spellcasting_ability": "",
        "spell_save_dc": 0,
        "spell_attack_bonus": 0,
        "caster_type": "none",
        "slots": {},
        "known_spells": [],
    }

    # -- Sınıf verisi kontrolü --
    class_data = character.get("class_data") or {}
    casting_ability_raw = class_data.get("spellcasting_ability", "")
    class_name = (character.get("class", "") or "").lower()

    if not casting_ability_raw:
        # Fallback for DND5e classes without explicit spellcasting_ability
        SPELLCASTING_ABILITIES = {
            "wizard": "intelligence", "cleric": "wisdom", "druid": "wisdom",
            "bard": "charisma", "paladin": "charisma", "ranger": "wisdom",
            "sorcerer": "charisma", "warlock": "charisma", "artificer": "intelligence",
            "blood hunter": "intelligence", "eldritch knight": "intelligence",
            "arcane trickster": "intelligence"
        }
        for k, v in SPELLCASTING_ABILITIES.items():
            if k in class_name:
                casting_ability_raw = v
                break

    if not casting_ability_raw:
        return result  # Büyücü değil

    casting_ability = casting_ability_raw.lower().strip()
    result["is_spellcaster"] = True
    result["spellcasting_ability"] = casting_ability.title()

    # -- Temel hesaplar --
    level = max(1, int(character.get("level", 1)))
    scores = self.get_adjusted_abilities(character)
    ab_score = scores.get(casting_ability, 10)
    ab_mod = (ab_score - 10) // 2
    prof = 2 + (level - 1) // 4

    result["spell_save_dc"] = 8 + prof + ab_mod
    result["spell_attack_bonus"] = prof + ab_mod

    # -- Sınıf adından büyü tipi belirle --
    class_name = (character.get("class", "") or "").lower()
    WARLOCK_NAMES = {"warlock", "efendi pakti"}
    HALF_CASTERS = {"paladin", "ranger", "şövalye", "izci"}
    THIRD_CASTERS = {"eldritch knight", "arcane trickster", "büyülü şövalye", "arkan hilekâr"}

    if class_name in WARLOCK_NAMES:
        caster_type = "warlock"
    elif any(n in class_name for n in HALF_CASTERS):
        caster_type = "half"
    elif any(n in class_name for n in THIRD_CASTERS):
        caster_type = "third"
    else:
        caster_type = "full"

    result["caster_type"] = caster_type

    # -- Slot tabloları (PHB, p. 114) --
    # Tam büyücü (Wizard, Cleric, Druid, Bard, Sorcerer, vb.)
    FULL_SLOTS = {
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
    # Yarı büyücü (Paladin, Ranger — PHB p. 84, 92)
    HALF_SLOTS = {
        2:  {1: 2},
        3:  {1: 3},
        5:  {1: 4, 2: 2},
        7:  {1: 4, 2: 3},
        9:  {1: 4, 2: 3, 3: 2},
        11: {1: 4, 2: 3, 3: 3},
        13: {1: 4, 2: 3, 3: 3, 4: 1},
        15: {1: 4, 2: 3, 3: 3, 4: 2},
        17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
        19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    }
    # Üçte bir büyücü (EK / AT)
    THIRD_SLOTS = {
        3:  {1: 2},
        7:  {1: 3},
        13: {1: 3, 2: 2},
        19: {1: 3, 2: 3, 3: 3},
    }
    # Warlock Pact Magic (PHB p. 108)
    WARLOCK_PACT = {
        1:  {"slots": 1, "level": 1},
        2:  {"slots": 2, "level": 1},
        3:  {"slots": 2, "level": 2},
        4:  {"slots": 2, "level": 2},
        5:  {"slots": 2, "level": 3},
        6:  {"slots": 2, "level": 3},
        7:  {"slots": 2, "level": 4},
        8:  {"slots": 2, "level": 4},
        9:  {"slots": 2, "level": 5},
        10: {"slots": 2, "level": 5},
        11: {"slots": 3, "level": 5},
        12: {"slots": 3, "level": 5},
        13: {"slots": 3, "level": 5},
        14: {"slots": 3, "level": 5},
        15: {"slots": 3, "level": 5},
        16: {"slots": 3, "level": 5},
        17: {"slots": 4, "level": 5},
        18: {"slots": 4, "level": 5},
        19: {"slots": 4, "level": 5},
        20: {"slots": 4, "level": 5},
    }

    if caster_type == "warlock":
        pact = WARLOCK_PACT.get(level, WARLOCK_PACT[20])
        result["slots"] = {"pact_slots": pact["slots"], "pact_slot_level": pact["level"]}
    elif caster_type == "half":
        eff_level = level // 2
        slot_table = {}
        for threshold in sorted(HALF_SLOTS.keys()):
            if level >= threshold:
                slot_table = HALF_SLOTS[threshold]
        result["slots"] = {str(k): v for k, v in slot_table.items()}
    elif caster_type == "third":
        slot_table = {}
        for threshold in sorted(THIRD_SLOTS.keys()):
            if level >= threshold:
                slot_table = THIRD_SLOTS[threshold]
        result["slots"] = {str(k): v for k, v in slot_table.items()}
    else:
        effective = min(level, 20)
        result["slots"] = {str(k): v for k, v in FULL_SLOTS.get(effective, FULL_SLOTS[20]).items()}

    # -- DB'den büyü listesi (izole spells tablosu) --
    try:
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        # Sınıf adını büyü listesiyle eşleştir (siniflar sütununda arama)
        cur.execute(
            "SELECT isim, seviye, aciklama FROM spells WHERE sistem = 'dnd5e' "
            "AND siniflar LIKE ? ORDER BY seviye, isim LIMIT 30",
            (f"%{class_name}%",)
        )
        rows = cur.fetchall()
        conn.close()
        result["known_spells"] = [
            {"name": r[0], "level": r[1], "description": r[2] or ""}
            for r in rows
        ]
    except Exception:
        result["known_spells"] = []

    return result


def _pf1e_calculate_spells(self, character: Dict[str, Any]) -> Dict[str, Any]:
    """PF1e 1st Edition Büyü Sistemi Hesaplayıcı (Plugin Metod).

    PF2e KESİNLİKLE desteklenmez. Tüm kurallar PF1e Core Rulebook'a göredir.

    Döndürür:
        is_spellcaster        : bool
        spellcasting_ability  : str   — "Intelligence" / "Wisdom" / "Charisma"
        caster_level          : int   — CL = karakter seviyesi (prestige sınıflar hariç)
        concentration_bonus   : int   — CL + ability_mod (PF1e CRB p. 206)
        spell_save_dc_base    : int   — 10 + spell_level + ability_mod (PF1e CRB p. 218)
        casting_type          : str   — "prepared_arcane" / "prepared_divine" / "spontaneous" / "none"
        bonus_slots           : dict  — Yüksek ability'den gelen ekstra slot sayıları
                                         {1: n, 2: n, 3: n, 4: n} (PF1e CRB Table 1-3)
        known_spells          : list  — DB'den sınıf büyü listesi (ilk 30)
    """
    import sqlite3

    result: Dict[str, Any] = {
        "is_spellcaster": False,
        "spellcasting_ability": "",
        "caster_level": 0,
        "concentration_bonus": 0,
        "spell_save_dc_base": 0,
        "casting_type": "none",
        "bonus_slots": {},
        "known_spells": [],
    }

    class_data = character.get("class_data") or {}
    casting_ability_raw = class_data.get("spellcasting_ability", "")
    if not casting_ability_raw:
        return result

    casting_ability = casting_ability_raw.lower().strip()
    result["is_spellcaster"] = True
    result["spellcasting_ability"] = casting_ability.title()

    level = max(1, int(character.get("level", 1)))
    scores = self.get_adjusted_abilities(character)
    ab_score = scores.get(casting_ability, 10)
    ab_mod = (ab_score - 10) // 2

    # CL = sınıf seviyesi (PF1e CRB: prestige ve multiclass durumları ayrı)
    caster_level = level
    result["caster_level"] = caster_level

    # Concentration = CL + casting ability modifier (PF1e CRB p. 206)
    result["concentration_bonus"] = caster_level + ab_mod

    # Temel DC = 10 + büyü seviyesi + ability mod (PF1e CRB p. 218)
    # (Büyü seviyesi arayüzde dinamik olarak eklenir; burada 0 seviye için baz)
    result["spell_save_dc_base"] = 10 + ab_mod

    # Yayınlama tipi
    class_name_raw = (character.get("class", "") or "").lower()
    PREPARED_ARCANE = {"wizard", "büyücü", "arcanist", "arkanik"}
    PREPARED_DIVINE = {"cleric", "rahip", "druid", "dürüst", "oracle"}
    if any(n in class_name_raw for n in PREPARED_ARCANE):
        casting_type = "prepared_arcane"
    elif any(n in class_name_raw for n in PREPARED_DIVINE):
        casting_type = "prepared_divine"
    else:
        casting_type = "spontaneous"
    result["casting_type"] = casting_type

    # ── Bonus Slotlar: Yüksek Ability Skoru (PF1e CRB Table 1-3) ──────────
    # Bir büyücünün ability skoru ≥ 12 ise o seviyede 1 ek slot alır.
    # ability mod 1 → bonus_slot seviye 1; mod 2 → seviye 1-2; vs.
    # Resmi formül: ability_mod >= spell_level → o seviyeye +1 slot
    bonus_slots: Dict[int, int] = {}
    max_spell_level = min(9, (caster_level + 1) // 2)  # erişilebilir max büyü seviyesi
    for sp_lv in range(1, max_spell_level + 1):
        if ab_mod >= sp_lv:
            bonus_slots[sp_lv] = 1
    result["bonus_slots"] = {str(k): v for k, v in bonus_slots.items()}

    # -- DB'den büyü listesi (izole spells tablosu) --
    try:
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute(
            "SELECT isim, seviye, aciklama FROM spells WHERE sistem = 'pathfinder1e' "
            "AND siniflar LIKE ? ORDER BY seviye, isim LIMIT 30",
            (f"%{class_name_raw}%",)
        )
        rows = cur.fetchall()
        conn.close()
        result["known_spells"] = [
            {"name": r[0], "level": r[1], "description": r[2] or ""}
            for r in rows
        ]
    except Exception:
        result["known_spells"] = []

    return result


# -- Metodları sınıflara bağla (monkey-patch — hiçbir sınıf gövdesi değişmez) --
DND5e_Calculator.calculate_spells = _dnd5e_calculate_spells
PF1e_Calculator.calculate_spells  = _pf1e_calculate_spells

