"""
SQLite Storage Module
=====================
Karakter verilerinin kalıcı olarak saklanması için SQLite veritabanı
bağlantılarını ve tam CRUD (Create, Read, Update, Delete) işlemlerini
sağlar.

Şema:
  - systems             : Desteklenen TTRPG sistemleri
  - characters          : Karakter ana bilgileri + JSON data blob
  - character_stats     : Normalize edilmiş stat key/value çiftleri
  - character_inventory : Envanter kalemleri

Özellikler:
  - Context manager ile güvenli bağlantı yönetimi (WAL modu, otomatik rollback)
  - created_at / updated_at zaman damgaları
  - Sisteme veya isme göre filtreleme / arama
  - Index destekli hızlı sorgu performansı
  - Foreign key CASCADE ile referans bütünlüğü
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


# ======================================================================
# Data models
# ======================================================================

@dataclass
class CharacterRecord:
    """Veritabanında saklanan bir karakter kaydı."""
    id: Optional[int]
    system: str
    name: str
    data: dict
    created_at: Optional[str] = field(default=None)
    updated_at: Optional[str] = field(default=None)


@dataclass
class InventoryItem:
    """Envanter kalemi."""
    id: Optional[int]
    character_id: int
    item_name: str
    item_type: str = "misc"
    quantity: int = 1
    weight: float = 0.0
    description: str = ""
    equipped: bool = False


# ======================================================================
# Connection helper
# ======================================================================

@contextmanager
def _connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Thread-safe SQLite bağlantısı (WAL + auto-commit/rollback)."""
    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _row_to_record(row: tuple) -> CharacterRecord:
    """Tek bir DB satırını CharacterRecord'a dönüştür."""
    return CharacterRecord(
        id=row[0], system=row[1], name=row[2],
        data=json.loads(row[3]), created_at=row[4], updated_at=row[5],
    )


# ======================================================================
# Schema / Initialization
# ======================================================================

_SCHEMA_SQL = """
-- Desteklenen TTRPG sistemleri
CREATE TABLE IF NOT EXISTS systems (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT    UNIQUE NOT NULL,
    name        TEXT    NOT NULL,
    dice_system TEXT    NOT NULL DEFAULT 'd20',
    description TEXT    DEFAULT ''
);

-- Karakter ana tablosu
CREATE TABLE IF NOT EXISTS characters (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    system     TEXT    NOT NULL,
    name       TEXT    NOT NULL,
    data       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Normalize edilmiş stat çiftleri (karakter başına)
CREATE TABLE IF NOT EXISTS character_stats (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    stat_key     TEXT    NOT NULL,
    stat_value   REAL    NOT NULL DEFAULT 0,
    UNIQUE(character_id, stat_key)
);

-- Envanter kalemleri
CREATE TABLE IF NOT EXISTS character_inventory (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    item_name    TEXT    NOT NULL,
    item_type    TEXT    DEFAULT 'misc',
    quantity     INTEGER DEFAULT 1,
    weight       REAL    DEFAULT 0,
    description  TEXT    DEFAULT '',
    equipped     INTEGER DEFAULT 0
);

-- İndexler
CREATE INDEX IF NOT EXISTS idx_characters_system   ON characters(system);
CREATE INDEX IF NOT EXISTS idx_characters_name     ON characters(name);
CREATE INDEX IF NOT EXISTS idx_charstats_charid    ON character_stats(character_id);
CREATE INDEX IF NOT EXISTS idx_charinv_charid      ON character_inventory(character_id);
"""

_SEED_SYSTEMS = [
    ("dnd5e",        "D&D 5th Edition",               "d20",      "Dungeons & Dragons 5e SRD"),
    ("pathfinder1e", "Pathfinder 1st Edition",         "d20",      "Pathfinder 1e Core Rulebook"),
    ("mm3e",         "Mutants & Masterminds 3e",       "d20",      "M&M 3rd Edition"),
]


def init_db(db_path: Path) -> None:
    """Veritabanını, tabloları ve seed verilerini oluştur."""
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA_SQL)
        for key, name, dice, desc in _SEED_SYSTEMS:
            conn.execute(
                "INSERT OR IGNORE INTO systems (key, name, dice_system, description) "
                "VALUES (?, ?, ?, ?)",
                (key, name, dice, desc),
            )


# ======================================================================
# CREATE
# ======================================================================

def save_character(db_path: Path, record: CharacterRecord) -> int:
    """Yeni karakter kaydı oluştur. Dönen değer: yeni kaydın id'si."""
    with _connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO characters (system, name, data) VALUES (?, ?, ?)",
            (record.system, record.name, json.dumps(record.data, ensure_ascii=False)),
        )
        new_id = int(cur.lastrowid)

        _sync_stats(conn, new_id, record.data)
        _sync_inventory(conn, new_id, record.data)

        logger.debug("Karakter oluşturuldu: id=%d, name=%s", new_id, record.name)
        return new_id


# ======================================================================
# READ
# ======================================================================

def load_character(db_path: Path, record_id: int) -> Optional[CharacterRecord]:
    """Tek bir karakteri id'ye göre yükle. Bulunamazsa None döner."""
    with _connect(db_path) as conn:
        cur = conn.execute(
            "SELECT id, system, name, data, created_at, updated_at "
            "FROM characters WHERE id = ?",
            (record_id,),
        )
        row = cur.fetchone()
    return _row_to_record(row) if row else None


def list_characters(
    db_path: Path,
    system: Optional[str] = None,
) -> List[CharacterRecord]:
    """Tüm karakterleri listele. İsteğe bağlı sisteme göre filtrele."""
    query = "SELECT id, system, name, data, created_at, updated_at FROM characters"
    params: tuple = ()
    if system:
        query += " WHERE system = ?"
        params = (system,)
    query += " ORDER BY updated_at DESC"

    with _connect(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_record(r) for r in rows]


def search_characters(
    db_path: Path,
    name_query: str,
    system: Optional[str] = None,
) -> List[CharacterRecord]:
    """Karakter adına göre arama (LIKE, case-insensitive)."""
    query = (
        "SELECT id, system, name, data, created_at, updated_at "
        "FROM characters WHERE name LIKE ?"
    )
    params: list = [f"%{name_query}%"]
    if system:
        query += " AND system = ?"
        params.append(system)
    query += " ORDER BY updated_at DESC"

    with _connect(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_record(r) for r in rows]


def count_characters(db_path: Path, system: Optional[str] = None) -> int:
    """Toplam karakter sayısını döndür (opsiyonel sistem filtresi)."""
    query = "SELECT COUNT(*) FROM characters"
    params: tuple = ()
    if system:
        query += " WHERE system = ?"
        params = (system,)

    with _connect(db_path) as conn:
        row = conn.execute(query, params).fetchone()
    return row[0] if row else 0


def get_character_stats(db_path: Path, character_id: int) -> Dict[str, float]:
    """Bir karakterin normalize edilmiş stat'larını döndür."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT stat_key, stat_value FROM character_stats WHERE character_id = ?",
            (character_id,),
        ).fetchall()
    return {key: val for key, val in rows}


def get_character_inventory(db_path: Path, character_id: int) -> List[InventoryItem]:
    """Bir karakterin envanter kalemlerini döndür."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, character_id, item_name, item_type, quantity, weight, "
            "description, equipped FROM character_inventory WHERE character_id = ?",
            (character_id,),
        ).fetchall()
    return [
        InventoryItem(
            id=r[0], character_id=r[1], item_name=r[2], item_type=r[3],
            quantity=r[4], weight=r[5], description=r[6], equipped=bool(r[7]),
        )
        for r in rows
    ]


def list_systems(db_path: Path) -> List[dict]:
    """Kayıtlı sistemleri döndür."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT key, name, dice_system, description FROM systems ORDER BY id"
        ).fetchall()
    return [
        {"key": r[0], "name": r[1], "dice_system": r[2], "description": r[3]}
        for r in rows
    ]


# ======================================================================
# UPDATE
# ======================================================================

def update_character(db_path: Path, record_id: int, record: CharacterRecord) -> bool:
    """Mevcut bir karakter kaydını güncelle. Başarılıysa True döner."""
    now = datetime.now().isoformat()
    with _connect(db_path) as conn:
        cur = conn.execute(
            "UPDATE characters SET system = ?, name = ?, data = ?, updated_at = ? "
            "WHERE id = ?",
            (
                record.system,
                record.name,
                json.dumps(record.data, ensure_ascii=False),
                now,
                record_id,
            ),
        )
        updated = cur.rowcount > 0
        if updated:
            _sync_stats(conn, record_id, record.data)
            _sync_inventory(conn, record_id, record.data)
    if updated:
        logger.debug("Karakter güncellendi: id=%d", record_id)
    return updated


# ======================================================================
# DELETE
# ======================================================================

def delete_character(db_path: Path, record_id: int) -> bool:
    """Bir karakter kaydını sil (CASCADE ile stats/inventory de silinir)."""
    with _connect(db_path) as conn:
        cur = conn.execute("DELETE FROM characters WHERE id = ?", (record_id,))
        deleted = cur.rowcount > 0
    if deleted:
        logger.debug("Karakter silindi: id=%d", record_id)
    return deleted


# ======================================================================
# Internal sync helpers
# ======================================================================

def _sync_stats(conn: sqlite3.Connection, char_id: int, data: dict) -> None:
    """JSON data blob'undaki stat'ları character_stats tablosuna yansıt."""
    abilities = data.get("abilities", {})
    if not abilities:
        return
    conn.execute("DELETE FROM character_stats WHERE character_id = ?", (char_id,))
    for key, val in abilities.items():
        if isinstance(val, (int, float)):
            conn.execute(
                "INSERT INTO character_stats (character_id, stat_key, stat_value) "
                "VALUES (?, ?, ?)",
                (char_id, key, float(val)),
            )
    for extra_key in ("hit_points", "armor_class", "initiative", "proficiency_bonus"):
        val = data.get(extra_key)
        if isinstance(val, (int, float)):
            conn.execute(
                "INSERT OR REPLACE INTO character_stats (character_id, stat_key, stat_value) "
                "VALUES (?, ?, ?)",
                (char_id, extra_key, float(val)),
            )


def _sync_inventory(conn: sqlite3.Connection, char_id: int, data: dict) -> None:
    """JSON data blob'undaki envanter kalemlerini character_inventory tablosuna yansıt."""
    equipment = data.get("equipment", [])
    if not equipment:
        return
    conn.execute("DELETE FROM character_inventory WHERE character_id = ?", (char_id,))
    for item in equipment:
        if isinstance(item, str):
            conn.execute(
                "INSERT INTO character_inventory (character_id, item_name) VALUES (?, ?)",
                (char_id, item),
            )
        elif isinstance(item, dict):
            conn.execute(
                "INSERT INTO character_inventory "
                "(character_id, item_name, item_type, quantity, weight, description, equipped) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    char_id,
                    item.get("name", "Unknown"),
                    item.get("type", "misc"),
                    item.get("quantity", 1),
                    item.get("weight", 0),
                    item.get("description", ""),
                    1 if item.get("equipped") else 0,
                ),
            )
