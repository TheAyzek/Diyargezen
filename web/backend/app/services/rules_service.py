from typing import List, Dict, Any, Optional
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

    def get_races(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        races = self.manager.get_top_level_races(db_system)
        if query:
            q_lower = query.lower().strip()
            races = [r for r in races if q_lower in r.isim.lower() or q_lower in r.aciklama.lower()]
        return races

    def get_subraces(self, system: str, parent_race: str) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.get_subraces_for_race(db_system, parent_race)

    def get_classes(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        classes = self.manager.get_clean_classes(db_system)
        if query:
            q_lower = query.lower().strip()
            classes = [c for c in classes if q_lower in c.isim.lower() or q_lower in c.aciklama.lower()]
        return classes

    def search_entities(self, system: str, category: str, query: str) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.search_entities(db_system, category, query)

    def get_equipment(self, system: str, query: str = "", category: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.get_clean_equipment(db_system, query=query, category=category)


    def get_feats_or_advantages(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        # PF1e and D&D 5e use "feat". M&M 3e uses advantages (stored as "feat" or "advantage")
        # Let's search under "feat" or "advantage" category
        feats = self.manager.search_entities(db_system, "feat", query)
        if not feats:
            feats = self.manager.search_entities(db_system, "advantage", query)
        return feats

    def get_feats(self, system: str, query: str = "", category: str = "", class_name: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.get_feats(db_system, query=query, category=category, className=class_name)

    def get_spells(
        self,
        system: str,
        query: str = "",
        level: Optional[int] = None,
        caster_class: str = "",
        school: str = ""
    ) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.get_spells(
            db_system, query=query, level=level, caster_class=caster_class, school=school
        )

    def get_powers(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.search_entities(db_system, "power", query)

    def get_traits(self, system: str, query: str = "", category: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.get_traits(db_system, query, category)

    def get_class_features(self, system: str, class_name: str = "", query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.get_class_features(db_system, class_name=class_name, query=query)

    def get_mechanics(self, system: str, query: str = "", category: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        # Search for rules, mechanics, or conditions in db, or return curated mechanics if query matches
        mechanics = self.manager.search_entities(db_system, "rule", query)
        if not mechanics:
            mechanics = self.manager.search_entities(db_system, "condition", query)
        return mechanics

