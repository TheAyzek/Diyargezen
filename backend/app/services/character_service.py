import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import DB_PATH, SYSTEM_MAPPING
from app.models.user import Character, User
from app.models.progression import LevelProgression
from rules.character_manager import CharacterManager
from rules.dnd5e_rules import DND5EValidator
from rules.pf1e_rules import PF1EValidator
from rules.mnm3e_rules import MM3EValidator

logger = logging.getLogger(__name__)

class CharacterService:
    def __init__(self):
        pass

    def _normalize_system_for_recalc(self, system: str) -> str:
        """Map client keys to keys recognized by calculators/validators."""
        sys_lower = system.lower()
        mapped = SYSTEM_MAPPING.get(sys_lower, sys_lower)
        if mapped == "mm3e":
            return "mm3e"
        if mapped == "pathfinder1e":
            return "pathfinder1e"
        return mapped

    def recalculate(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the TTRPG derived statistics calculator pipeline."""
        system = character_data.get("system", "")
        normalized_system = self._normalize_system_for_recalc(system)
        
        char_copy = character_data.copy()
        char_copy["system"] = normalized_system
        
        # Instantiate local CharacterManager per request for statelessness and thread-safety
        manager = CharacterManager(DB_PATH)
        manager.set_active_character(char_copy)
        recalculated_char = manager.recalculate_character()
        
        recalculated_char["system"] = system
        return recalculated_char

    def validate(self, character_data: Dict[str, Any]) -> List[str]:
        """Runs rule validators for the specific TTRPG system."""
        system = character_data.get("system", "").lower()
        normalized_system = SYSTEM_MAPPING.get(system, system)
        
        if "dnd5e" in normalized_system:
            validator = DND5EValidator()
        elif "pathfinder1e" in normalized_system or "pf1e" in normalized_system:
            validator = PF1EValidator()
        elif "mm3e" in normalized_system or "mnm" in normalized_system:
            validator = MM3EValidator()
        else:
            return [f"Bilinmeyen sistem tipi için doğrulama yapılamadı: {system}"]
            
        try:
            warnings = validator.validate(character_data, {})
            return warnings
        except Exception as exc:
            logger.error("Doğrulama hatası: %s", exc, exc_info=True)
            return [f"Doğrulama işlemi sırasında hata oluştu: {str(exc)}"]

    # ---------------------------------------------------------
    # CRUD Operations using SQLAlchemy Session
    # ---------------------------------------------------------

    def create_character(self, db: Session, system: str, name: str, data: Dict[str, Any], user_id: int) -> Character:
        """Create a new character in the database associated with a user."""
        # Ensure derived statistics are computed before saving
        data_recalced = self.recalculate(data)
        
        db_char = Character(
            user_id=user_id,
            system=system,
            name=name,
            data=json.dumps(data_recalced, ensure_ascii=False),
            created_at=json.dumps(data_recalced.get("created_at") or "") or "",
            updated_at=json.dumps(data_recalced.get("updated_at") or "") or ""
        )
        # Handle created_at/updated_at as standard ISO strings
        now = datetime.now(timezone.utc).isoformat()
        db_char.created_at = now
        db_char.updated_at = now
        
        db.add(db_char)
        db.commit()
        db.refresh(db_char)
        return db_char

    def get_character(self, db: Session, character_id: int) -> Optional[Character]:
        """Retrieve a character by ID."""
        return db.query(Character).filter(Character.id == character_id).first()

    def list_characters(self, db: Session, user_id: int, system: Optional[str] = None) -> List[Character]:
        """List all characters belonging to a specific user, optionally filtered by system."""
        # Also return characters with user_id == None (public/seeded characters)
        query = db.query(Character).filter((Character.user_id == user_id) | (Character.user_id == None))
        if system:
            query = query.filter(Character.system == system)
        return query.order_by(Character.id.desc()).all()

    def update_character(self, db: Session, character_id: int, name: str, data: Dict[str, Any]) -> bool:
        """Update an existing character record."""
        db_char = self.get_character(db, character_id)
        if not db_char:
            return False
            
        data_recalced = self.recalculate(data)

        db_char.name = name
        db_char.data = json.dumps(data_recalced, ensure_ascii=False)
        db_char.updated_at = datetime.now(timezone.utc).isoformat()
        
        db.commit()
        return True

    def delete_character(self, db: Session, character_id: int) -> bool:
        """Delete a character record."""
        db_char = self.get_character(db, character_id)
        if not db_char:
            return False
        db.delete(db_char)
        db.commit()
        return True

    # ---------------------------------------------------------
    # Level-Up & Progression Progression History Engine
    # ---------------------------------------------------------

    def level_up(self, db: Session, character_id: int, class_name: str, choices: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Progress character level by 1, applying custom choices and saving progression history."""
        db_char = self.get_character(db, character_id)
        if not db_char:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Karakter bulunamadı.")
            
        if db_char.user_id and db_char.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu karakter üzerinde işlem yetkiniz yok.")

        char_data = json.loads(db_char.data)
        current_level = int(char_data.get("level", 1))
        target_level = current_level + 1

        # Check if progression history already has this level
        existing_prog = db.query(LevelProgression).filter(
            LevelProgression.character_id == character_id,
            LevelProgression.level == target_level
        ).first()
        if existing_prog:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Karakter zaten seviye {target_level} geçmişine sahip.")

        # Apply choices
        is_mnm = any(s in db_char.system.lower() for s in ["mnm", "mm3e", "mastermind"])

        # 1. Update level
        char_data["level"] = target_level
        char_data["class"] = class_name  # Set current/multiclass name
        if is_mnm:
            char_data["pl_value"] = target_level

        # 2. HP added
        if not is_mnm:
            con_score = int(char_data.get("abilities", {}).get("constitution", 10))
            con_modifier = (con_score - 10) // 2
            hp_base_added = int(choices.get("hp_added", 6))
            total_hp_increase = hp_base_added + con_modifier
            char_data["hit_points"] = int(char_data.get("hit_points", 10)) + total_hp_increase

        # 3. Skills allocated
        skill_ranks = char_data.setdefault("skill_ranks", {})
        for skill, ranks in choices.get("skill_ranks", {}).items():
            skill_ranks[skill] = int(skill_ranks.get(skill, 0)) + int(ranks)

        # 4. Feats selected
        feats = char_data.setdefault("feats", [])
        for feat in choices.get("feats", []):
            if feat not in feats:
                feats.append(feat)

        # 5. Ability score increase
        ability_increase = choices.get("ability_increase")
        if ability_increase:
            abilities = char_data.setdefault("abilities", {})
            abilities[ability_increase] = int(abilities.get(ability_increase, 10)) + 1

        # 6. Spells learned
        spells = char_data.setdefault("spells", [])
        for spell in choices.get("spells_learned", []):
            if spell not in spells:
                spells.append(spell)

        # Recalculate derived statistics
        recalced_data = self.recalculate(char_data)

        # Save progression record
        prog = LevelProgression(
            character_id=character_id,
            level=target_level,
            class_name=class_name,
            choices=json.dumps(choices, ensure_ascii=False),
            created_at=datetime.now(timezone.utc).isoformat()
        )
        db.add(prog)

        # Update character state
        db_char.data = json.dumps(recalced_data, ensure_ascii=False)
        db_char.updated_at = datetime.now(timezone.utc).isoformat()
        db.commit()

        return recalced_data

    def level_undo(self, db: Session, character_id: int, user_id: int) -> Dict[str, Any]:
        """Undo the highest level progression, reverting stats to previous level."""
        db_char = self.get_character(db, character_id)
        if not db_char:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Karakter bulunamadı.")
            
        if db_char.user_id and db_char.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu karakter üzerinde işlem yetkiniz yok.")

        # Find highest progression record
        highest_prog = db.query(LevelProgression).filter(
            LevelProgression.character_id == character_id
        ).order_by(LevelProgression.level.desc()).first()

        if not highest_prog:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Geri alınacak seviye ilerleme geçmişi bulunamadı (Başlangıç Seviye 1 geri alınamaz).")

        choices = json.loads(highest_prog.choices)
        char_data = json.loads(db_char.data)
        
        is_mnm = any(s in db_char.system.lower() for s in ["mnm", "mm3e", "mastermind"])

        # 1. Decrement level
        char_data["level"] = max(1, int(char_data.get("level", 2)) - 1)
        if is_mnm:
            char_data["pl_value"] = char_data["level"]

        # 2. Subtract HP
        if not is_mnm:
            con_score = int(char_data.get("abilities", {}).get("constitution", 10))
            con_modifier = (con_score - 10) // 2
            hp_base_added = int(choices.get("hp_added", 6))
            total_hp_increase = hp_base_added + con_modifier
            char_data["hit_points"] = max(1, int(char_data.get("hit_points", 10)) - total_hp_increase)

        # 3. Revert skills
        skill_ranks = char_data.get("skill_ranks", {})
        for skill, ranks in choices.get("skill_ranks", {}).items():
            skill_ranks[skill] = max(0, int(skill_ranks.get(skill, 0)) - int(ranks))

        # 4. Remove feats
        feats = char_data.get("feats", [])
        for feat in choices.get("feats", []):
            if feat in feats:
                feats.remove(feat)

        # 5. Revert ability score increase
        ability_increase = choices.get("ability_increase")
        if ability_increase:
            abilities = char_data.get("abilities", {})
            abilities[ability_increase] = max(1, int(abilities.get(ability_increase, 11)) - 1)

        # 6. Remove learned spells
        spells = char_data.get("spells", [])
        for spell in choices.get("spells_learned", []):
            if spell in spells:
                spells.remove(spell)

        # Remove the progression record
        db.delete(highest_prog)

        # Recalculate derived statistics
        recalced_data = self.recalculate(char_data)

        # Update character state
        db_char.data = json.dumps(recalced_data, ensure_ascii=False)
        db_char.updated_at = datetime.now(timezone.utc).isoformat()
        db.commit()

        return recalced_data
