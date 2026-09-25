from desktop import local_db as db, sync_v2_store as sync
import pytest


@pytest.fixture
def context(tmp_path):
    path = tmp_path / 'client.db'
    db.init_local_db(path)
    db.save_local_auth(path, 'alice', 'token')
    record = db.save_local_character(path, {'name': 'Local', 'system': 'pf1e'})
    return path, db.get_sync_session(path), record


def reply(op, conflict=False):
    remote = {**op, 'id': 1, 'revision': 3 if conflict else 1,
              'name': 'Remote', 'created_at': 'now', 'updated_at': 'now'}
    result = {'operation_id': op['operation_id'], 'server_id': op['server_id'],
              'status': 'conflict' if conflict else 'accepted', 'revision': remote['revision'],
              'actual_revision': remote['revision'], 'server_character': remote}
    return {'protocol_version': 2, 'characters': [remote], 'results': [result]}


def test_persistent_retry_after_edit_and_ack(context):
    path, session, record = context
    sent = sync.prepare_operations(path, session)
    db.save_local_character(path, {'name': 'Later', 'system': 'pf1e'}, record.id)
    db.init_local_db(path)
    assert sync.prepare_operations(path, session) == sent
    sync.apply_response(path, sent, reply(sent[0]), session)
    assert db.get_local_character(path, record.id).name == 'Later'
    next_ops = sync.prepare_operations(path, session)
    assert next_ops[0]['base_revision'] == 1
    assert next_ops[0]['operation_id'] != sent[0]['operation_id']


@pytest.mark.parametrize('choice', ['local', 'server'])
def test_conflict_preserves_both_copies_and_requires_resolution(context, choice):
    path, session, record = context
    sent = sync.prepare_operations(path, session)
    sync.apply_response(path, sent, reply(sent[0], conflict=True), session)
    assert sync.prepare_operations(path, session) == []
    conflict = sync.list_conflicts(path)[0]
    assert conflict['local']['name'] == 'Local'
    assert conflict['conflict']['server_character']['name'] == 'Remote'
    sync.resolve_conflict(path, record.server_id, sent[0]['operation_id'], conflict['fingerprint'], choice, session)
    assert sync.list_conflicts(path) == []
    if choice == 'local':
        next_ops = sync.prepare_operations(path, session)
        assert next_ops[0]['base_revision'] == 3
        assert next_ops[0]['operation_id'] != sent[0]['operation_id']
    else:
        assert db.get_local_character(path, record.id).name == 'Remote'
        assert sync.prepare_operations(path, session) == []
    with db._connect(path) as conn:
        assert conn.execute("SELECT count(*) FROM sync_state WHERE key LIKE 'conflict_archive:%'").fetchone()[0] == 1


def test_missing_ack_and_invalid_response_preserve_queue(context):
    path, session, _ = context
    sent = sync.prepare_operations(path, session)
    sync.apply_response(path, sent, {'protocol_version': 2, 'results': [], 'characters': []}, session)
    assert sync.prepare_operations(path, session) == sent
    invalid = reply(sent[0])
    invalid['characters'].append({'server_id': 'broken'})
    with pytest.raises(KeyError):
        sync.apply_response(path, sent, invalid, session)
    assert sync.prepare_operations(path, session) == sent


def test_late_response_is_rejected(context):
    path, session, record = context
    sent = sync.prepare_operations(path, session)
    db.save_local_auth(path, 'bob', 'token-b')
    with pytest.raises(ValueError):
        sync.apply_response(path, sent, reply(sent[0]), session)
    assert db.list_local_characters(path) == []
    db.save_local_auth(path, 'alice', 'token')
    assert db.get_local_character(path, record.id).is_dirty
