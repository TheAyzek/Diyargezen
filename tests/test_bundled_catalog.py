from contextlib import closing
import sqlite3
import pytest
from db.bundled_catalog import import_missing_catalog
from db.entity_store import init_game_schema


def seed(path, rows):
    init_game_schema(path)
    with closing(sqlite3.connect(path)) as db, db:
        db.executemany(
            "INSERT INTO entities (isim,sistem,kategori,aciklama,sistem_verisi) VALUES (?,?,?,?,?)", rows
        )


def test_import_preserves_user_tables_ids_and_existing_content(tmp_path):
    target, source = tmp_path / "user.db", tmp_path / "bundle.db"
    seed(target, [("Fighter", "pathfinder1e", "class", "Local content", "{}")])
    seed(source, [("Fighter", "pathfinder1e", "class", "Bundled content", "{}"),
                  ("Human", "pathfinder1e", "race", "New", "{}"),
                  ("Other", "dnd5e", "race", "Ignored", "{}")])
    for path, name in [(target, "User character"), (source, "Bundled character")]:
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("CREATE TABLE characters (name TEXT)")
            db.execute("INSERT INTO characters VALUES (?)", (name,))
    assert import_missing_catalog(target, source) == 1
    with closing(sqlite3.connect(target)) as db:
        assert db.execute("SELECT * FROM characters").fetchall() == [("User character",)]
        assert db.execute("SELECT id, aciklama FROM entities WHERE isim='Fighter'").fetchone() == (1, "Local content")
        assert db.execute("SELECT count(*) FROM entities").fetchone()[0] == 2
    backups = list((tmp_path / "backups").glob("*.db"))
    assert len(backups) == 1
    with closing(sqlite3.connect(backups[0])) as backup:
        assert backup.execute("SELECT * FROM characters").fetchall() == [("User character",)]
        assert backup.execute("SELECT count(*) FROM entities").fetchone()[0] == 1
    assert import_missing_catalog(target, source) == 0
    assert list((tmp_path / "backups").glob("*.db")) == backups


def test_first_install_imports_only_catalog(tmp_path):
    source, target = tmp_path / "bundle.db", tmp_path / "new.db"
    seed(source, [("Human", "pf1e", "race", "", "{}")])
    assert import_missing_catalog(target, source) == 1
    with closing(sqlite3.connect(target)) as db:
        assert not db.execute("SELECT name FROM sqlite_master WHERE name='characters'").fetchall()


def test_invalid_source_does_not_modify_target(tmp_path):
    source, target = tmp_path / "invalid.db", tmp_path / "user.db"
    seed(target, [("Human", "pf1e", "race", "", "{}")])
    with closing(sqlite3.connect(source)):
        pass
    before = target.read_bytes()
    with pytest.raises(sqlite3.OperationalError):
        import_missing_catalog(target, source)
    assert target.read_bytes() == before
    assert not (tmp_path / "backups").exists()
