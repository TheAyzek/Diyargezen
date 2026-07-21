from typing import List, Dict, Any
from app.core.config import DB_PATH, SYSTEM_MAPPING
from rules.character_manager import CharacterManager
from models.entity import DiyargezenEntity

class RulesService:
    def __init__(self):
        self.manager = CharacterManager(DB_PATH)

    def _normalize_system(self, system: str) -> str:
        """Map client keys (e.g., pf1e) to db keys (e.g., pathfinder1e)."""
        sys_lower = system.lower()
        return SYSTEM_MAPPING.get(sys_lower, sys_lower)

    def get_races(self, system: str) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.get_top_level_races(db_system)

    def get_subraces(self, system: str, parent_race: str) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.get_subraces_for_race(db_system, parent_race)

    def get_classes(self, system: str) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.get_clean_classes(db_system)

    def search_entities(self, system: str, category: str, query: str) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.search_entities(db_system, category, query)

    def get_equipment(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.get_clean_equipment(db_system, query)

    def get_feats_or_advantages(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        # PF1e and D&D 5e use "feat". M&M 3e uses advantages (stored as "feat" or "advantage")
        # Let's search under "feat" or "advantage" category
        feats = self.manager.search_entities(db_system, "feat", query)
        if not feats:
            feats = self.manager.search_entities(db_system, "advantage", query)
        return feats

    def get_spells(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.search_entities(db_system, "spell", query)

    def get_powers(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.search_entities(db_system, "power", query)
