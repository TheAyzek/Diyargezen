import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CharacterRecord:
    id: Optional[int]
    system: str
    name: str
    data: dict


def init_db(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system TEXT NOT NULL,
                name TEXT NOT NULL,
                data TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_character(db_path: Path, record: CharacterRecord) -> int:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO characters (system, name, data) VALUES (?, ?, ?)",
            (record.system, record.name, json.dumps(record.data, ensure_ascii=False)),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def load_character(db_path: Path, record_id: int) -> Optional[CharacterRecord]:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, system, name, data FROM characters WHERE id = ?", (record_id,))
        row = cur.fetchone()
        if not row:
            return None
        return CharacterRecord(id=row[0], system=row[1], name=row[2], data=json.loads(row[3]))
    finally:
        conn.close()


def list_characters(db_path: Path) -> list[CharacterRecord]:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, system, name, data FROM characters ORDER BY id DESC")
        rows = cur.fetchall()
        return [CharacterRecord(id=r[0], system=r[1], name=r[2], data=json.loads(r[3])) for r in rows]
    finally:
        conn.close()


