"""
SQLite Storage Module
=====================
Karakter verilerinin kalıcı olarak saklanması için SQLite veritabanı
bağlantılarını ve tam CRUD (Create, Read, Update, Delete) işlemlerini
sağlar.

Özellikler:
  - Context manager ile güvenli bağlantı yönetimi (WAL modu, otomatik rollback)
  - created_at / updated_at zaman damgaları
  - Sisteme veya isme göre filtreleme / arama
  - Index destekli hızlı sorgu performansı
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Optional

logger = logging.getLogger(__name__)


# ======================================================================
# Data model
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
        id=row[0],
        system=row[1],
        name=row[2],
        data=json.loads(row[3]),
        created_at=row[4],
        updated_at=row[5],
    )


# ======================================================================
# Schema / Initialization
# ======================================================================

def init_db(db_path: Path) -> None:
    """Veritabanını ve tabloları oluştur (yoksa). İndexleri de ekler."""
    with _connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                system     TEXT    NOT NULL,
                name       TEXT    NOT NULL,
                data       TEXT    NOT NULL,
                created_at TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_characters_system ON characters(system)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name)"
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
        logger.debug("Karakter güncellendi: id=%d", record_id)
    return updated


# ======================================================================
# DELETE
# ======================================================================

def delete_character(db_path: Path, record_id: int) -> bool:
    """Bir karakter kaydını sil. Başarılıysa True döner."""
    with _connect(db_path) as conn:
        cur = conn.execute("DELETE FROM characters WHERE id = ?", (record_id,))
        deleted = cur.rowcount > 0
    if deleted:
        logger.debug("Karakter silindi: id=%d", record_id)
    return deleted
