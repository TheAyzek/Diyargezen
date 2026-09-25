from dataclasses import asdict
import pytest
from desktop import local_db


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "offline.db"
    local_db.init_local_db(path)
    return path


def create(path, name="Valeros"):
    return local_db.save_local_character(path, {"system": "pf1e", "name": name})


@pytest.mark.parametrize("delete", [False, True])
def test_edit_during_request_is_not_overwritten(db_path, delete):
    sent = create(db_path)
    if delete:
        local_db.delete_local_character(db_path, sent.id)
    else:
        local_db.save_local_character(db_path, {"system": "pf1e", "name": "New edit"}, sent.id)
    local_db.apply_sync_response(db_path, [asdict(sent)], [], sent_records=[sent], synced_at="checkpoint")
    current = local_db.get_local_character(db_path, sent.id)
    assert current.is_dirty
    assert current.is_deleted == delete
    assert current.name == ("Valeros" if delete else "New edit")
    assert local_db.get_sync_checkpoint(db_path) == "checkpoint"


def test_missing_ack_and_new_records_remain_dirty(db_path):
    sent = create(db_path)
    new = create(db_path, "New during request")
    local_db.apply_sync_response(db_path, [], [], sent_records=[sent])
    assert {r.id for r in local_db.get_dirty_characters(db_path)} == {sent.id, new.id}


def test_remote_delete_preserves_later_edit(db_path):
    sent = create(db_path)
    local_db.save_local_character(db_path, {"system": "pf1e", "name": "New edit"}, sent.id)
    local_db.apply_sync_response(db_path, [], [sent.server_id], sent_records=[sent])
    assert local_db.get_local_character(db_path, sent.id).is_dirty


def test_pull_without_sent_snapshot_does_not_ack_dirty_record(db_path):
    sent = create(db_path)
    local_db.apply_sync_response(db_path, [asdict(sent)], [])
    assert local_db.get_local_character(db_path, sent.id).is_dirty


def test_response_failure_rolls_back_ack_and_checkpoint(db_path):
    sent = create(db_path)
    local_db.set_sync_checkpoint(db_path, "before")
    with pytest.raises(ValueError):
        local_db.apply_sync_response(db_path, [asdict(sent), {}], [],
                                     sent_records=[sent], synced_at="after")
    assert local_db.get_local_character(db_path, sent.id).is_dirty
    assert local_db.get_sync_checkpoint(db_path) == "before"


def test_repeat_response_and_clean_pull(db_path):
    sent = create(db_path)
    for _ in range(2):
        local_db.apply_sync_response(db_path, [asdict(sent)], [], sent_records=[sent])
    assert len(local_db.list_local_characters(db_path)) == 1
    assert not local_db.get_dirty_characters(db_path)
    remote = {**asdict(sent), "name": "Remote edit"}
    local_db.apply_sync_response(db_path, [remote], [])
    assert local_db.get_local_character(db_path, sent.id).name == "Remote edit"
    local_db.apply_sync_response(db_path, [], [sent.server_id])
    assert not local_db.list_local_characters(db_path)


def test_worker_passes_request_snapshot_and_keeps_inflight_edit(db_path, monkeypatch):
    from desktop.sync_engine import SyncWorker, ApiClient
    local_db.save_local_auth(db_path, "alice", "test-token")
    sent = create(db_path)

    def response(self, operations):
        assert operations[0]["name"] == "Valeros"
        local_db.save_local_character(db_path, {"system": "pf1e", "name": "While syncing"}, sent.id)
        remote = {**asdict(sent), "revision": 1}
        return {"protocol_version": 2, "characters": [remote], "results": [{
            "operation_id": operations[0]["operation_id"], "server_id": sent.server_id,
            "status": "accepted", "revision": 1, "server_character": remote}]}

    monkeypatch.setattr(ApiClient, "sync_v2", response)
    worker = SyncWorker(db_path)
    worker.perform_sync()
    current = local_db.get_local_character(db_path, sent.id)
    assert current.name == "While syncing"
    assert current.is_dirty
    from desktop.sync_v2_store import prepare_operations
    assert prepare_operations(db_path, local_db.get_sync_session(db_path))[0]['base_revision'] == 1


def test_worker_network_failure_preserves_queue_and_checkpoint(db_path, monkeypatch):
    from desktop.sync_engine import SyncWorker, ApiClient
    local_db.save_local_auth(db_path, "alice", "test-token")
    sent = create(db_path)
    local_db.set_sync_checkpoint(db_path, "before")

    def failure(self, operations):
        raise ConnectionError("offline")

    monkeypatch.setattr(ApiClient, "sync_v2", failure)
    worker = SyncWorker(db_path)
    worker.perform_sync()
    assert local_db.get_local_character(db_path, sent.id).is_dirty
    assert worker._last_sync_timestamp == "before"
    assert local_db.get_sync_checkpoint(db_path) == "before"
