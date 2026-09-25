from contextlib import closing
from dataclasses import asdict
import sqlite3
import pytest
from desktop import local_db as db


@pytest.fixture
def path(tmp_path):
    path = tmp_path / "accounts.db"
    db.init_local_db(path)
    return path


def login(path, name):
    db.save_local_auth(path, name, name + "-token")


def save(path, name="Valeros"):
    return db.save_local_character(path, {"name": name, "system": "pf1e"})


def test_accounts_isolate_crud_queue_checkpoint_and_logout(path):
    login(path, "alice")
    alice = save(path)
    db.set_sync_checkpoint(path, "alice-checkpoint")
    login(path, "bob")
    assert db.list_local_characters(path) == []
    assert db.get_dirty_characters(path) == []
    assert db.get_sync_checkpoint(path) is None
    assert db.get_local_character(path, alice.id) is None
    with pytest.raises(ValueError):
        db.save_local_character(path, {"name": "Overwrite"}, alice.id)
    db.delete_local_character(path, alice.id)
    bob = save(path, "Bob")
    db.set_sync_checkpoint(path, "bob-checkpoint")
    login(path, "alice")
    assert [r.id for r in db.list_local_characters(path)] == [alice.id]
    assert not db.get_local_character(path, alice.id).is_deleted
    assert db.get_sync_checkpoint(path) == "alice-checkpoint"
    db.clear_local_auth(path)
    assert db.list_local_characters(path) == []
    assert db.get_sync_checkpoint(path) is None
    login(path, "bob")
    assert [r.id for r in db.get_dirty_characters(path)] == [bob.id]
    assert db.get_sync_checkpoint(path) == "bob-checkpoint"


@pytest.mark.parametrize("change", ["bob", "logout", "alice"])
def test_late_response_is_rejected_after_session_change(path, change):
    login(path, "alice")
    alice = save(path)
    session = db.get_sync_session(path)
    if change == "logout":
        db.clear_local_auth(path)
    else:
        login(path, change)
    with pytest.raises(ValueError):
        db.apply_sync_response(path, [asdict(alice)], [], sent_records=[alice],
                               synced_at="late", expected_session=session)
    assert db.get_sync_checkpoint(path) is None
    login(path, "alice")
    assert db.get_local_character(path, alice.id).is_dirty


def test_remote_id_collision_cannot_overwrite_another_owner(path):
    login(path, "alice")
    alice = save(path)
    db.apply_sync_response(path, [asdict(alice)], [], sent_records=[alice])
    login(path, "bob")
    with pytest.raises(ValueError):
        db.apply_sync_response(path, [{**asdict(alice), "name": "Overwrite"}], [])
    db.apply_sync_response(path, [], [alice.server_id])
    login(path, "alice")
    assert db.get_local_character(path, alice.id).name == "Valeros"


def test_legacy_migration_keeps_unowned_records_and_backs_up(tmp_path):
    path = tmp_path / "legacy.db"
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("""CREATE TABLE local_characters (
            id INTEGER PRIMARY KEY, server_id TEXT UNIQUE NOT NULL, user_id INTEGER,
            system TEXT, name TEXT, data TEXT, is_dirty INTEGER, is_deleted INTEGER,
            created_at TEXT, updated_at TEXT)""")
        conn.execute("INSERT INTO local_characters VALUES (1,'legacy-id',NULL,'pf1e','Legacy','{}',1,0,'before','before')")
    db.init_local_db(path)
    backups = list((tmp_path / "backups").glob("*.db"))
    assert len(backups) == 1
    with closing(sqlite3.connect(backups[0])) as conn:
        assert conn.execute("SELECT name FROM local_characters").fetchone()[0] == "Legacy"
        assert "owner" not in {r[1] for r in conn.execute("PRAGMA table_info(local_characters)")}
    db.init_local_db(path)
    assert list((tmp_path / "backups").glob("*.db")) == backups
    assert db.get_local_character(path, 1).name == "Legacy"
    login(path, "alice")
    assert db.get_dirty_characters(path) == []
    assert db.list_local_characters(path) == []
    db.clear_local_auth(path)
    assert db.get_local_character(path, 1).is_dirty


def test_worker_uses_frozen_credentials_and_discards_late_response(path, monkeypatch):
    from desktop.sync_engine import SyncWorker, ApiClient, api_client
    login(path, "alice")
    alice = save(path)
    db.set_sync_checkpoint(path, "alice-before")
    worker = SyncWorker(path)

    def response(self, operations):
        assert self.username == "alice"
        assert self.token == "alice-token"
        assert [r["server_id"] for r in operations] == [alice.server_id]
        login(path, "bob")
        monkeypatch.setattr(api_client, "token", "bob-token")
        assert self.token == "alice-token"
        return {"protocol_version": 2, "characters": [], "results": []}

    monkeypatch.setattr(ApiClient, "sync_v2", response)
    worker.perform_sync()
    assert db.list_local_characters(path) == []
    assert db.get_sync_checkpoint(path) is None
    login(path, "alice")
    assert db.get_local_character(path, alice.id).is_dirty
    assert db.get_sync_checkpoint(path) == "alice-before"


def test_logged_out_worker_does_not_use_stale_global_token(path, monkeypatch):
    from desktop.sync_engine import SyncWorker, ApiClient, api_client
    save(path)
    monkeypatch.setattr(api_client, "token", "stale-token")

    def unexpected(self, operations):
        pytest.fail("Logged-out worker must not send local-only characters")

    monkeypatch.setattr(ApiClient, "sync_v2", unexpected)
    SyncWorker(path).perform_sync()
    assert len(db.get_dirty_characters(path)) == 1


def test_worker_uses_current_account_instead_of_legacy_checkpoint(path, monkeypatch):
    from desktop.sync_engine import SyncWorker, ApiClient
    login(path, "alice")
    db.set_sync_checkpoint(path, "alice-checkpoint")
    worker = SyncWorker(path)
    login(path, "bob")
    db.set_sync_checkpoint(path, "bob-checkpoint")
    observed = []

    def response(self, operations):
        observed.append((self.username, operations))
        return {"protocol_version": 2, "characters": [], "results": []}

    monkeypatch.setattr(ApiClient, "sync_v2", response)
    worker.perform_sync()
    login(path, "alice")
    worker.perform_sync()
    assert observed == [("bob", []), ("alice", [])]


def test_unscoped_legacy_checkpoint_is_not_reused(path):
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("INSERT INTO sync_state VALUES ('last_sync_timestamp', 'legacy')")
    login(path, "alice")
    assert db.get_sync_checkpoint(path) is None
    db.clear_local_auth(path)
    assert db.get_sync_checkpoint(path) is None
