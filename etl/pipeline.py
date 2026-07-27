"""
ETL Pipeline
============
data/ klasöründeki JSON dosyalarını tarar, parser'larla DiyargezenEntity
üretir ve SQLite entities tablosuna yazar.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from db.entity_store import (
    bulk_upsert_entities,
    count_entities,
    init_game_schema,
    needs_rebuild,
    set_etl_meta,
    _source_fingerprint,
)
from parsers import PARSERS

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = BASE_DIR / "data" / "characters.db"
DATA_DIR = BASE_DIR / "data"

SYSTEM_FILES: Dict[str, List[str]] = {
    "pathfinder1e": ["pathfinder_1e_data.json"],
}


def _fingerprint(data_dir: Path) -> str:
    """entity_store._source_fingerprint ile aynı mantığı kullan — tutarlılık için."""
    all_files = []
    for files in SYSTEM_FILES.values():
        all_files.extend(files)
    return _source_fingerprint(data_dir, all_files)


def run_etl(
    db_path: Optional[Path] = None,
    systems: Optional[List[str]] = None,
    force: bool = False,
) -> Dict[str, int]:
    """
    ETL çalıştır. Dönen dict: {sistem: entity_sayısı}.
    """
    db_path = db_path or DEFAULT_DB
    data_dir = db_path.parent
    systems = systems or list(PARSERS.keys())

    init_game_schema(db_path)

    if not force and not needs_rebuild(db_path, data_dir, systems):
        logger.info("ETL atlandı — veritabanı güncel")
        return {s: count_entities(db_path, s) for s in systems}

    totals: Dict[str, int] = {}
    for sistem in systems:
        parser = PARSERS.get(sistem)
        if not parser:
            logger.warning("Parser yok: %s", sistem)
            continue
        try:
            entities = parser(base_dir=BASE_DIR)
            totals[sistem] = bulk_upsert_entities(db_path, entities, sistem)
        except Exception as exc:
            logger.exception("%s ETL hatası: %s", sistem, exc)
            totals[sistem] = 0

    set_etl_meta(db_path, "source_fingerprint", _fingerprint(data_dir))
    set_etl_meta(db_path, "last_etl_systems", ",".join(systems))
    logger.info("ETL tamamlandı: %s", totals)
    return totals


def run_etl_if_needed(db_path: Optional[Path] = None) -> Dict[str, int]:
    """Uygulama açılışında çağrılır — yalnızca gerekirse ETL yapar."""
    return run_etl(db_path=db_path, force=False)
