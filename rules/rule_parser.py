import re
from typing import List, Dict, Any, Optional

# Abilities normalization
ABILITY_MAP = {
    "strength": "strength", "str": "strength",
    "dexterity": "dexterity", "dex": "dexterity",
    "constitution": "constitution", "con": "constitution",
    "intelligence": "intelligence", "int": "intelligence",
    "wisdom": "wisdom", "wis": "wisdom",
    "charisma": "charisma", "cha": "charisma"
}

# Skill lists (with clear names to match against)
PF_SKILLS_MAP = {
    "acrobatics": "acrobatics",
    "appraise": "appraise",
    "bluff": "bluff",
    "climb": "climb",
    "craft": "craft",
    "diplomacy": "diplomacy",
    "disable device": "disable_device",
    "disguise": "disguise",
    "escape artist": "escape_artist",
    "fly": "fly",
    "handle animal": "handle_animal",
    "heal": "heal",
    "intimidate": "intimidate",
    "linguistics": "linguistics",
    "perception": "perception",
    "perform": "perform",
    "profession": "profession",
    "ride": "ride",
    "sense motive": "sense_motive",
    "sleight of hand": "sleight_of_hand",
    "spellcraft": "spellcraft",
    "stealth": "stealth",
    "survival": "survival",
    "swim": "swim",
    "use magic device": "use_magic_device",
    "knowledge (arcana)": "knowledge_(arcana)",
    "knowledge (dungeoneering)": "knowledge_(dungeoneering)",
    "knowledge (engineering)": "knowledge_(engineering)",
    "knowledge (geography)": "knowledge_(geography)",
    "knowledge (history)": "knowledge_(history)",
    "knowledge (local)": "knowledge_(local)",
    "knowledge (nature)": "knowledge_(nature)",
    "knowledge (nobility)": "knowledge_(nobility)",
    "knowledge (planes)": "knowledge_(planes)",
    "knowledge (religion)": "knowledge_(religion)",
    # Fallback to match plain knowledge
    "knowledge": "knowledge_(arcana)"
}

DND5E_SKILLS_MAP = {
    "acrobatics": "Acrobatics",
    "animal handling": "Animal Handling",
    "arcana": "Arcana",
    "athletics": "Athletics",
    "deception": "Deception",
    "history": "History",
    "insight": "Insight",
    "intimidation": "Intimidation",
    "investigation": "Investigation",
    "medicine": "Medicine",
    "nature": "Nature",
    "perception": "Perception",
    "performance": "Performance",
    "persuasion": "Persuasion",
    "religion": "Religion",
    "sleight of hand": "Sleight of Hand",
    "stealth": "Stealth",
    "survival": "Survival"
}

class RuleParser:
    @staticmethod
    def parse_description(description: str, system: str, source_name: str, source_type: str) -> List[Dict[str, Any]]:
        if not description:
            return []
        
        modifiers = []
        sys_key = system.lower().replace("_", "").replace("-", "")
        is_dnd = "dnd" in sys_key
        
        # Lowercase for uniform scanning
        desc_lower = description.lower()
        
        # Find all numbers with plus/minus
        number_pattern = r'([+-]\d+)'
        
        for match in re.finditer(number_pattern, desc_lower):
            val = int(match.group(1))
            start_pos = match.end()
            # Take a 60 character window after the number
            window = desc_lower[start_pos : start_pos + 60]
            
            matched_targets = set()

            # 1. AC check
            if re.search(r'\b(ac|armor class)\b', window):
                if "ac" not in matched_targets:
                    modifiers.append({
                        "target": "ac",
                        "value": val,
                        "type": source_type,
                        "source": source_name,
                        "description": f"{match.group(0)} to AC ({source_name})"
                    })
                    matched_targets.add("ac")
            
            # 2. Initiative check
            if "initiative" in window or "init " in window:
                if "initiative" not in matched_targets:
                    modifiers.append({
                        "target": "initiative",
                        "value": val,
                        "type": source_type,
                        "source": source_name,
                        "description": f"{match.group(0)} to Initiative ({source_name})"
                    })
                    matched_targets.add("initiative")
            
            # 3. Saves check
            for save_keyword, save_target in [("fortitude", "saving_throws.Fortitude"), 
                                              ("reflex", "saving_throws.Reflex"), 
                                              ("will", "saving_throws.Will")]:
                if save_keyword in window:
                    if save_target not in matched_targets:
                        modifiers.append({
                            "target": save_target,
                            "value": val,
                            "type": source_type,
                            "source": source_name,
                            "description": f"{match.group(0)} to {save_keyword.title()} save ({source_name})"
                        })
                        matched_targets.add(save_target)
            
            # All saves fallback
            if "saving throw" in window or "saves" in window:
                if not any(t.startswith("saving_throws.") for t in matched_targets):
                    if "saving_throws.All" not in matched_targets:
                        modifiers.append({
                            "target": "saving_throws.All",
                            "value": val,
                            "type": source_type,
                            "source": source_name,
                            "description": f"{match.group(0)} to all saving throws ({source_name})"
                        })
                        matched_targets.add("saving_throws.All")

            # 4. Abilities check
            for ab_keyword, ab_target in ABILITY_MAP.items():
                if re.search(rf'\b{ab_keyword}\b', window):
                    if ab_target not in matched_targets:
                        modifiers.append({
                            "target": ab_target,
                            "value": val,
                            "type": source_type,
                            "source": source_name,
                            "description": f"{match.group(0)} to {ab_target.title()} ({source_name})"
                        })
                        matched_targets.add(ab_target)

            # 5. Skills check
            skill_map = DND5E_SKILLS_MAP if is_dnd else PF_SKILLS_MAP
            for skill_keyword, skill_target in skill_map.items():
                pattern = rf'\b{re.escape(skill_keyword)}\b'
                if re.search(pattern, window):
                    target_key = f"skills.{skill_target}"
                    if target_key not in matched_targets:
                        modifiers.append({
                            "target": target_key,
                            "value": val,
                            "type": source_type,
                            "source": source_name,
                            "description": f"{match.group(0)} to {skill_keyword.title()} ({source_name})"
                        })
                        matched_targets.add(target_key)

        return modifiers
