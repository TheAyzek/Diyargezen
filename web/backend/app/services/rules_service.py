from typing import List, Dict, Any, Optional
from pathlib import Path
from functools import lru_cache
from app.core.config import DB_PATH, SYSTEM_MAPPING
from rules.character_manager import CharacterManager
from models.entity import DiyargezenEntity

# ── IN-MEMORY LRU CACHE HELPERS ─────────────────────────────────────────────
# Accelerates repetitive rules compendium queries (races, classes, feats, spells)
# by caching parsed entity objects in RAM.

@lru_cache(maxsize=128)
def _cached_get_races(db_path_str: str, system: str) -> List[DiyargezenEntity]:
    manager = CharacterManager(Path(db_path_str))
    return manager.get_top_level_races(system)

@lru_cache(maxsize=128)
def _cached_get_subraces(db_path_str: str, system: str, parent_race: str) -> List[DiyargezenEntity]:
    manager = CharacterManager(Path(db_path_str))
    return manager.get_subraces_for_race(system, parent_race)

@lru_cache(maxsize=128)
def _cached_get_classes(db_path_str: str, system: str) -> List[DiyargezenEntity]:
    manager = CharacterManager(Path(db_path_str))
    return manager.get_clean_classes(system)

@lru_cache(maxsize=512)
def _cached_get_feats(db_path_str: str, system: str, query: str, category: str, class_name: str, limit: Optional[int] = None) -> List[DiyargezenEntity]:
    manager = CharacterManager(Path(db_path_str))
    res = manager.get_feats(system, query=query, category=category, className=class_name)
    if limit and limit > 0:
        return res[:limit]
    return res

@lru_cache(maxsize=512)
def _cached_get_spells(db_path_str: str, system: str, query: str, level: Optional[int], caster_class: str, school: str, limit: Optional[int] = None) -> List[DiyargezenEntity]:
    manager = CharacterManager(Path(db_path_str))
    res = manager.get_spells(system, query=query, level=level, caster_class=caster_class, school=school)
    if limit and limit > 0:
        return res[:limit]
    return res

@lru_cache(maxsize=512)
def _cached_get_equipment(db_path_str: str, system: str, query: str, category: str, limit: Optional[int] = None) -> List[DiyargezenEntity]:
    manager = CharacterManager(Path(db_path_str))
    res = manager.get_clean_equipment(system, query=query, category=category)
    if limit and limit > 0:
        return res[:limit]
    return res

@lru_cache(maxsize=512)
def _cached_get_traits(db_path_str: str, system: str, query: str, category: str, limit: Optional[int] = None) -> List[DiyargezenEntity]:
    manager = CharacterManager(Path(db_path_str))
    res = manager.get_traits(system, query=query, category=category)
    if limit and limit > 0:
        return res[:limit]
    return res

@lru_cache(maxsize=512)
def _cached_get_class_features(db_path_str: str, system: str, class_name: str, query: str, limit: Optional[int] = None) -> List[DiyargezenEntity]:
    manager = CharacterManager(Path(db_path_str))
    res = manager.get_class_features(system, class_name=class_name, query=query)
    if limit and limit > 0:
        return res[:limit]
    return res


class RulesService:
    def __init__(self):
        self.db_path_str = str(Path(DB_PATH).resolve())
        self.manager = CharacterManager(DB_PATH)

    def _normalize_system(self, system: str) -> str:
        """Map client keys (e.g., pf1e) to db keys (e.g., pathfinder1e)."""
        sys_lower = system.lower()
        return SYSTEM_MAPPING.get(sys_lower, sys_lower)

    def get_races(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        races = _cached_get_races(self.db_path_str, db_system)
        if query:
            q_lower = query.lower().strip()
            races = [r for r in races if q_lower in r.isim.lower() or q_lower in r.aciklama.lower()]
        return races

    def get_subraces(self, system: str, parent_race: str) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return _cached_get_subraces(self.db_path_str, db_system, parent_race)

    def get_classes(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        classes = _cached_get_classes(self.db_path_str, db_system)
        if query:
            q_lower = query.lower().strip()
            classes = [c for c in classes if q_lower in c.isim.lower() or q_lower in c.aciklama.lower()]
        return classes

    def search_entities(self, system: str, category: str, query: str) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.search_entities(db_system, category, query)

    def get_equipment(self, system: str, query: str = "", category: str = "", limit: Optional[int] = None) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return _cached_get_equipment(self.db_path_str, db_system, query, category, limit)

    def get_feats_or_advantages(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        feats = self.manager.search_entities(db_system, "feat", query)
        if not feats:
            feats = self.manager.search_entities(db_system, "advantage", query)
        return feats

    def get_feats(self, system: str, query: str = "", category: str = "", class_name: str = "", limit: Optional[int] = None) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return _cached_get_feats(self.db_path_str, db_system, query, category, class_name, limit)

    def get_spells(
        self,
        system: str,
        query: str = "",
        level: Optional[int] = None,
        caster_class: str = "",
        school: str = "",
        limit: Optional[int] = None
    ) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return _cached_get_spells(self.db_path_str, db_system, query, level, caster_class, school, limit)

    def get_powers(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return self.manager.search_entities(db_system, "power", query)

    def get_traits(self, system: str, query: str = "", category: str = "", limit: Optional[int] = None) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return _cached_get_traits(self.db_path_str, db_system, query, category, limit)

    def get_class_features(self, system: str, class_name: str = "", query: str = "", limit: Optional[int] = None) -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        return _cached_get_class_features(self.db_path_str, db_system, class_name, query, limit)

    def get_mechanics(self, system: str, query: str = "", category: str = "") -> List[DiyargezenEntity]:
        db_system = self._normalize_system(system)
        mechanics = self.manager.search_entities(db_system, "rule", query)
        if not mechanics:
            mechanics = self.manager.search_entities(db_system, "condition", query)
        return mechanics
