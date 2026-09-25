"""Non-destructive bootstrap of the bundled PF1e catalog.

Existing catalog rows are deliberately preserved. Replacing published content
requires a separate, versioned migration, not a count-based database overwrite.
"""
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import uuid

from db.entity_store import init_game_schema


def import_missing_catalog(target: Path, bundled: Path) -> int:
    if target.resolve() == bundled.resolve():
        raise ValueError("Catalog source and user database must be distinct")
    # Validate/read the source before touching the user's database.
    with closing(sqlite3.connect(bundled.resolve().as_uri() + "?mode=ro", uri=True)) as source:
        rows = source.execute(
            "SELECT isim, sistem, kategori, aciklama, sistem_verisi FROM entities "
            "WHERE lower(sistem) IN ('pf1e', 'pathfinder1e')"
        ).fetchall()
    if not rows:
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        with closing(sqlite3.connect(str(target))) as existing:
            has_catalog = existing.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='entities'"
            ).fetchone()
            keys = set(existing.execute("SELECT isim, sistem, kategori FROM entities")) if has_catalog else set()
            rows = [row for row in rows if row[:3] not in keys]
            if not rows:
                return 0
            backup_dir = target.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = backup_dir / f"{target.stem}-before-catalog-{stamp}-{uuid.uuid4().hex}.db"
            with closing(sqlite3.connect(str(backup))) as destination:
                existing.backup(destination)
    init_game_schema(target)
    with closing(sqlite3.connect(str(target))) as connection, connection:
        before = connection.total_changes
        connection.executemany(
            "INSERT INTO entities (isim, sistem, kategori, aciklama, sistem_verisi) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT(sistem, kategori, isim) DO NOTHING", rows
        )
        return connection.total_changes - before
