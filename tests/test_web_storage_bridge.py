import pytest
from desktop.web_bridge import BridgeService
from desktop.web_storage import WebStorage


def session(name='alice'):
    return {'authenticated': True, 'token': name + '-token', 'owner': 'account:' + name}


@pytest.fixture
def bridge(tmp_path):
    def verify(token):
        if token not in {'alice-token', 'bob-token'}:
            raise ValueError('invalid token')
        return token.removesuffix('-token')
    return BridgeService(tmp_path / 'client.db', verify)


def save(bridge, name='Local', identity=None):
    return bridge.dispatch(identity or session(), 'save', {'character': {'name': name, 'system': 'pf1e', 'data': {'level': 1}}})


def response(op, *, conflict=False):
    remote = {**op, 'id': 9, 'revision': 3 if conflict else 1, 'name': 'Remote', 'created_at': 'now', 'updated_at': 'now'}
    return {'protocol_version': 2, 'characters': [remote], 'results': [{
        'operation_id': op['operation_id'], 'server_id': op['server_id'],
        'status': 'conflict' if conflict else 'accepted', 'actual_revision': remote['revision'],
        'revision': remote['revision'], 'server_character': remote,
    }]}


def test_verified_identity_cannot_select_another_partition(bridge):
    save(bridge)
    assert bridge.dispatch(session('bob'), 'all', {}) == []
    with pytest.raises(ValueError):
        bridge.dispatch({**session(), 'owner': 'account:bob'}, 'all', {})
    with pytest.raises(ValueError):
        bridge.dispatch({**session(), 'token': 'forged'}, 'all', {})
    assert len(bridge.dispatch(session(), 'all', {})) == 1


def test_guest_is_separate_and_cannot_prepare_uploads(bridge):
    guest = {'authenticated': False, 'token': '', 'owner': 'guest'}
    save(bridge, identity=guest)
    assert bridge.dispatch(session(), 'all', {}) == []
    assert bridge.dispatch(guest, 'prepare', {}) == []


def test_verified_token_hash_allows_offline_restart_without_storing_jwt(bridge):
    save(bridge)
    def offline(token):
        raise ValueError('expired/unavailable')
    restarted = BridgeService(bridge.path, offline)
    assert len(restarted.dispatch(session(), 'all', {})) == 1
    with pytest.raises(ValueError):
        restarted.dispatch(session('bob'), 'all', {})
    from desktop.local_db import _connect
    with _connect(bridge.path) as db:
        digest = db.execute('SELECT token_hash FROM web_verified_sessions').fetchone()[0]
        assert digest != session()['token'] and len(digest) == 64


def test_restart_retries_exact_operation_and_ack_preserves_inflight_edit(bridge):
    record = save(bridge)
    operations = bridge.dispatch(session(), 'prepare', {})
    bridge.dispatch(session(), 'save', {'character': {**record, 'name': 'Later'}})
    restarted = BridgeService(bridge.path, lambda token: 'alice')
    assert restarted.dispatch(session(), 'prepare', {}) == operations
    restarted.dispatch(session(), 'apply', {'operations': operations, 'response': response(operations[0])})
    next_ops = restarted.dispatch(session(), 'prepare', {})
    assert next_ops[0]['name'] == 'Later'
    assert next_ops[0]['base_revision'] == 1
    assert next_ops[0]['operation_id'] != operations[0]['operation_id']
    assert restarted.dispatch(session(), 'get', {'id': record['id']})['remote_id'] == 9


@pytest.mark.parametrize('choice', ['local', 'server'])
def test_conflict_archives_and_restore_makes_a_new_copy(bridge, choice):
    record = save(bridge)
    operations = bridge.dispatch(session(), 'prepare', {})
    bridge.dispatch(session(), 'apply', {'operations': operations, 'response': response(operations[0], conflict=True)})
    assert bridge.dispatch(session(), 'prepare', {}) == []
    bridge.dispatch(session(), 'resolve', {'id': record['id'], 'operationId': operations[0]['operation_id'],
                                         'localRevision': record['local_revision'], 'choice': choice})
    archive = bridge.dispatch(session(), 'archives', {})[0]
    assert bridge.dispatch(session('bob'), 'archives', {}) == []
    restored = bridge.dispatch(session(), 'restore', {'key': archive['key']})
    assert restored['id'] != record['id']
    assert restored['revision'] == 0 and restored['conflict'] is None
    assert restored['name'] == 'Local (Kurtarıldı)'
    assert len(bridge.dispatch(session(), 'archives', {})) == 1


def test_invalid_ack_rolls_back_all_sqlite_changes(bridge):
    record = save(bridge)
    ops = bridge.dispatch(session(), 'prepare', {})
    bad = response(ops[0])
    bad['characters'].append({'server_id': 'bad'})
    with pytest.raises(ValueError):
        bridge.dispatch(session(), 'apply', {'operations': ops, 'response': bad})
    assert bridge.dispatch(session(), 'prepare', {}) == ops
    assert bridge.dispatch(session(), 'get', {'id': record['id']})['is_dirty']


def test_other_system_and_arbitrary_command_rejected(bridge):
    with pytest.raises(ValueError):
        bridge.dispatch(session(), 'save', {'character': {'system': 'dnd5e'}})
    with pytest.raises(ValueError):
        bridge.dispatch(session(), 'sql', {'query': 'DELETE FROM users'})


def test_stale_conflict_resolution_does_not_overwrite_later_edit(bridge):
    record = save(bridge)
    ops = bridge.dispatch(session(), 'prepare', {})
    bridge.dispatch(session(), 'apply', {'operations': ops, 'response': response(ops[0], conflict=True)})
    bridge.dispatch(session(), 'save', {'character': {**record, 'name': 'Later'}})
    with pytest.raises(ValueError):
        bridge.dispatch(session(), 'resolve', {'id': record['id'], 'operationId': ops[0]['operation_id'],
                                             'localRevision': record['local_revision'], 'choice': 'server'})


def test_sqlite_level_draft_is_separate_from_committed_character(bridge):
    record = save(bridge)
    draft = {'version': 1, 'baseLevel': 3, 'step': 2}
    bridge.dispatch(session(), 'draft_save', {'id': record['id'], 'value': draft})
    assert bridge.dispatch(session(), 'draft_get', {'id': record['id']}) == draft
    assert bridge.dispatch(session(), 'get', {'id': record['id']}) == record
    bridge.dispatch(session(), 'draft_save', {'id': record['id'], 'value': None})
    assert bridge.dispatch(session(), 'draft_get', {'id': record['id']}) is None
