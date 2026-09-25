"""Add revision tracking without replacing existing character data."""
from contextlib import closing
from pathlib import Path
import sqlite3
import uuid


def migrate_character_revision(path: Path):
    with closing(sqlite3.connect(str(path))) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(characters)")}
        missing_ids = conn.execute(
            "SELECT id FROM characters WHERE server_id IS NULL OR server_id=''"
        ).fetchall() if "server_id" in columns else []
        if not columns or ("revision" in columns and not missing_ids):
            return
        backup_dir = path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        with closing(sqlite3.connect(str(backup_dir / f"{path.stem}-before-revision-{uuid.uuid4().hex}.db"))) as backup:
            conn.backup(backup)
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            if "revision" not in columns:
                conn.execute("ALTER TABLE characters ADD COLUMN revision INTEGER NOT NULL DEFAULT 1")
            for (record_id,) in missing_ids:
                conn.execute("UPDATE characters SET server_id=? WHERE id=?", (str(uuid.uuid4()), record_id))
