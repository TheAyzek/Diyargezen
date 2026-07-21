"""
Masaüstü Yerel SQLite Veritabanı Modülü (Offline-First)
======================================================
İnternet olsun ya da olmasın masaüstü uygulamasının yerelde anında
çalışmasını ve arka planda `is_dirty` kuyruğu yönetmesini sağlar.
"""

from __future__ import annotations

import json
import uuid
import sqlite3
import logging
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LocalCharacterRecord:
    """Yerel SQLite veritabanındaki karakter kaydı."""
    id: Optional[int]
    server_id: str
    user_id: Optional[int]
    system: str
    name: str
    data: dict
    is_dirty: bool = False
    is_deleted: bool = False
    created_at: str = ""
    updated_at: str = ""


@contextmanager
def _connect(db_path: Path) -> Iterator[sqlite3.Connection]:
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


def init_local_db(db_path: Path) -> None:
    """Yerel veritabanı tablolarını ve indekslerini oluşturur."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS local_characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            system TEXT NOT NULL,
            name TEXT NOT NULL,
            data TEXT NOT NULL,
            is_dirty INTEGER DEFAULT 1,
            is_deleted INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS local_auth (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            username TEXT NOT NULL,
            access_token TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_local_chars_server_id ON local_characters(server_id);
        CREATE INDEX IF NOT EXISTS idx_local_chars_is_dirty  ON local_characters(is_dirty);
        """)


def save_local_auth(db_path: Path, username: str, token: str) -> None:
    """JWT Token ve kullanıcı bilgisini yerelde saklar."""
    now_str = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        conn.execute("""
        INSERT INTO local_auth (id, username, access_token, updated_at)
        VALUES (1, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            username=excluded.username,
            access_token=excluded.access_token,
            updated_at=excluded.updated_at
        """, (username, token, now_str))


def get_local_auth(db_path: Path) -> Optional[tuple[str, str]]:
    """Yerel oturum bilgilerini döner: (username, token)."""
    with _connect(db_path) as conn:
        row = conn.execute("SELECT username, access_token FROM local_auth WHERE id=1").fetchone()
        if row:
            return row[0], row[1]
    return None


def clear_local_auth(db_path: Path) -> None:
    """Yerel oturum bilgilerini siler."""
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM local_auth WHERE id=1")


def list_local_characters(db_path: Path, system: Optional[str] = None) -> List[LocalCharacterRecord]:
    """Silinmemiş yerel karakterleri listeler."""
    with _connect(db_path) as conn:
        query = "SELECT id, server_id, user_id, system, name, data, is_dirty, is_deleted, created_at, updated_at FROM local_characters WHERE is_deleted=0"
        params = []
        if system:
            query += " AND system=?"
            params.append(system)
        query += " ORDER BY id DESC"
        
        rows = conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            result.append(LocalCharacterRecord(
                id=r[0], server_id=r[1], user_id=r[2], system=r[3], name=r[4],
                data=json.loads(r[5]), is_dirty=bool(r[6]), is_deleted=bool(r[7]),
                created_at=r[8], updated_at=r[9]
            ))
        return result


def get_local_character(db_path: Path, record_id: int) -> Optional[LocalCharacterRecord]:
    """ID'ye göre yerel karakter kaydını döner."""
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, server_id, user_id, system, name, data, is_dirty, is_deleted, created_at, updated_at FROM local_characters WHERE id=?",
            (record_id,)
        ).fetchone()
        if row:
            return LocalCharacterRecord(
                id=row[0], server_id=row[1], user_id=row[2], system=row[3], name=row[4],
                data=json.loads(row[5]), is_dirty=bool(row[6]), is_deleted=bool(row[7]),
                created_at=row[8], updated_at=row[9]
            )
    return None


def save_local_character(db_path: Path, character_data: dict, record_id: Optional[int] = None) -> LocalCharacterRecord:
    """Karakteri yerel veritabanına kaydeder (Offline-First, is_dirty=1)."""
    now_str = datetime.now(timezone.utc).isoformat()
    name = character_data.get("name", "İsimsiz Kahraman")
    system = character_data.get("system", "pathfinder1e")

    with _connect(db_path) as conn:
        if record_id:
            row = conn.execute("SELECT server_id, created_at FROM local_characters WHERE id=?", (record_id,)).fetchone()
            server_id = row[0] if row else str(uuid.uuid4())
            created_at = row[1] if row else now_str

            conn.execute("""
            UPDATE local_characters
            SET name=?, system=?, data=?, is_dirty=1, updated_at=?
            WHERE id=?
            """, (name, system, json.dumps(character_data, ensure_ascii=False), now_str, record_id))
            rec_id = record_id
        else:
            server_id = str(uuid.uuid4())
            created_at = now_str
            cursor = conn.execute("""
            INSERT INTO local_characters (server_id, user_id, system, name, data, is_dirty, is_deleted, created_at, updated_at)
            VALUES (?, NULL, ?, ?, ?, 1, 0, ?, ?)
            """, (server_id, system, name, json.dumps(character_data, ensure_ascii=False), created_at, now_str))
            rec_id = cursor.lastrowid

    return LocalCharacterRecord(
        id=rec_id, server_id=server_id, user_id=None, system=system, name=name,
        data=character_data, is_dirty=True, is_deleted=False,
        created_at=created_at, updated_at=now_str
    )


def delete_local_character(db_path: Path, record_id: int) -> None:
    """Karakteri yerelde soft-delete (is_deleted=1, is_dirty=1) işaretler."""
    now_str = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        conn.execute("""
        UPDATE local_characters
        SET is_deleted=1, is_dirty=1, updated_at=?
        WHERE id=?
        """, (now_str, record_id))


def get_dirty_characters(db_path: Path) -> List[LocalCharacterRecord]:
    """Sunucuya iletilmeyi bekleyen (`is_dirty=1`) karakterleri döner."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, server_id, user_id, system, name, data, is_dirty, is_deleted, created_at, updated_at FROM local_characters WHERE is_dirty=1"
        ).fetchall()
        result = []
        for r in rows:
            result.append(LocalCharacterRecord(
                id=r[0], server_id=r[1], user_id=r[2], system=r[3], name=r[4],
                data=json.loads(r[5]), is_dirty=bool(r[6]), is_deleted=bool(r[7]),
                created_at=r[8], updated_at=r[9]
            ))
        return result


def apply_sync_response(db_path: Path, updated_characters: List[dict], deleted_server_ids: List[str]) -> None:
    """FastAPI sunucusundan gelen senkronizasyon paketini yerel veritabanına uygular."""
    now_str = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        # 1. Silinen kayıtları temizle
        for s_id in deleted_server_ids:
            conn.execute("DELETE FROM local_characters WHERE server_id=?", (s_id,))

        # 2. Güncellenen karakterleri yaz (is_dirty=0 yap)
        for char in updated_characters:
            s_id = char.get("server_id") or str(uuid.uuid4())
            sys_code = char.get("system", "")
            name = char.get("name", "")
            c_data = char.get("data") or {}
            data_str = json.dumps(c_data, ensure_ascii=False) if isinstance(c_data, dict) else c_data
            created_at = char.get("created_at") or now_str
            updated_at = char.get("updated_at") or now_str

            conn.execute("""
            INSERT INTO local_characters (server_id, user_id, system, name, data, is_dirty, is_deleted, created_at, updated_at)
            VALUES (?, NULL, ?, ?, ?, 0, 0, ?, ?)
            ON CONFLICT(server_id) DO UPDATE SET
                system=excluded.system,
                name=excluded.name,
                data=excluded.data,
                is_dirty=0,
                is_deleted=0,
                updated_at=excluded.updated_at
            """, (s_id, sys_code, name, data_str, created_at, updated_at))

        # 3. PUSH edilen dirty kayıtların dirty bayrağını indir
        conn.execute("UPDATE local_characters SET is_dirty=0 WHERE is_deleted=0")
        conn.execute("DELETE FROM local_characters WHERE is_deleted=1")
