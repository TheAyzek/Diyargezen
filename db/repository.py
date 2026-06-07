"""
EntityRepository — GUI ve creators için SQLite köprüsü.
Mevcut kod self.data dict formatını beklediği için legacy dict üretir.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from db.entity_store import count_entities, init_game_schema, list_entities
from parsers.base import CATEGORY_TO_SECTION

logger = logging.getLogger(__name__)

# data_file → sistem anahtarı
DATA_FILE_TO_SYSTEM: Dict[str, str] = {
    "dnd_data.json": "dnd5e",
    "pathfinder_1e_data.json": "pathfinder1e",
    "mm_data.json": "mm3e",
}

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "characters.db"


class EntityRepository:
    """SQLite entity deposuna okuma/yazma arayüzü."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB
        init_game_schema(self.db_path)

    def has_data(self, sistem: str) -> bool:
        return count_entities(self.db_path, sistem) > 0

    def list_names(self, sistem: str, kategori: str) -> List[str]:
        return [e.isim for e in list_entities(self.db_path, sistem, kategori)]

    def get_entity(self, sistem: str, kategori: str, isim: str) -> Optional[Dict[str, Any]]:
        for ent in list_entities(self.db_path, sistem, kategori):
            if ent.isim == isim:
                return ent.sistem_verisi
        return None

    def to_legacy_dict(self, sistem: str) -> Dict[str, Any]:
        """Creator'ların beklediği {races: {}, classes: {}, ...} yapısını üret."""
        legacy: Dict[str, Any] = {"system": sistem}
        entities = list_entities(self.db_path, sistem)
        for ent in entities:
            section = CATEGORY_TO_SECTION.get(ent.kategori, ent.kategori + "s")
            legacy.setdefault(section, {})
            if isinstance(legacy[section], dict):
                legacy[section][ent.isim] = ent.sistem_verisi
        return legacy

    @classmethod
    def for_data_file(cls, data_file: str, db_path: Optional[Path] = None) -> "EntityRepository":
        return cls(db_path)

    @classmethod
    def system_for_file(cls, data_file: str) -> Optional[str]:
        return DATA_FILE_TO_SYSTEM.get(data_file)
