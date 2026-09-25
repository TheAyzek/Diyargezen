import sys
from pathlib import Path
from contextlib import closing
import sqlite3

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm.exc import StaleDataError
from app.main import app
from app.core.database import Base, get_db
from app.core.sync_migration import migrate_character_revision
from app.models.user import Character


@pytest.fixture
def api():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    def dependency():
        with factory() as session:
            yield session
    previous = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = dependency
    client = TestClient(app)
    registration = client.post('/api/auth/register', json={'username': 'revision_user', 'password': 'Password123!'})
    assert registration.status_code == 201
    headers = {'Authorization': 'Bearer ' + registration.json()['access_token']}
    try:
        yield client, headers, factory
    finally:
        if previous is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous
        client.close()
        engine.dispose()


def op(operation_id='create', base=0, **changes):
    return dict(operation_id=operation_id, server_id='stable-uuid', base_revision=base,
                system='pf1e', name='Valeros', data={'level': 1}, **changes)


def push(api, *operations):
    client, headers, _ = api
    return client.post('/api/sync/v2', headers=headers, json={'operations': list(operations)})


def test_two_embedded_sqlite_clients_conflict_and_recover_through_real_api(api, tmp_path):
    from desktop.web_storage import WebStorage
    a, b = WebStorage(tmp_path / 'a.db'), WebStorage(tmp_path / 'b.db')
    owner = 'account:revision_user'
    def sync(store):
        operations = store.execute(owner, 'prepare', {})
        response = push(api, *operations)
        assert response.status_code == 200
        store.execute(owner, 'apply', {'operations': operations, 'response': response.json()})
    saved = a.execute(owner, 'save', {'character': {'name': 'Valeros', 'system': 'pf1e', 'data': {'level': 1}}})
    sync(a)
    sync(b)
    first = a.execute(owner, 'get', {'id': saved['id']})
    second = b.execute(owner, 'get', {'id': saved['id']})
    a.execute(owner, 'save', {'character': {**first, 'name': 'Device A'}})
    b.execute(owner, 'save', {'character': {**second, 'name': 'Device B'}})
    sync(a)
    sync(b)
    conflicted = b.execute(owner, 'get', {'id': saved['id']})
    assert conflicted['name'] == 'Device B'
    assert conflicted['conflict']['server_character']['name'] == 'Device A'
    b.execute(owner, 'resolve', {'id': saved['id'], 'operationId': conflicted['conflict']['operation_id'],
                               'localRevision': conflicted['local_revision'], 'choice': 'server'})
    assert b.execute(owner, 'get', {'id': saved['id']})['name'] == 'Device A'
    assert len(b.execute(owner, 'archives', {})) == 1


def test_stale_device_cannot_overwrite_latest_revision(api):
    first = push(api, op()).json()
    assert first['results'][0]['revision'] == 1
    edited = op('edit-a', 1)
    edited['name'] = 'Device A'
    assert push(api, edited).json()['results'][0]['revision'] == 2
    stale = op('edit-b', 1)
    stale['name'] = 'Device B'
    response = push(api, stale)
    assert response.status_code == 200
    conflict = response.json()['results'][0]
    assert conflict['status'] == 'conflict'
    assert conflict['actual_revision'] == 2
    assert conflict['server_character']['name'] == 'Device A'
    assert response.json()['characters'][0]['name'] == 'Device A'


def test_retry_returns_original_receipt_without_reapplying(api):
    original = push(api, op()).json()['results'][0]
    push(api, op('edit', 1))
    replay = push(api, op()).json()
    assert replay['results'][0] == original
    assert replay['characters'][0]['revision'] == 2
    assert len(replay['characters']) == 1


def test_operation_id_payload_mismatch_rolls_back_whole_batch(api):
    push(api, op())
    changed = op()
    changed['name'] = 'Different payload'
    assert push(api, op('would-change', 1), changed).status_code == 409
    assert push(api).json()['characters'][0]['revision'] == 1
    assert push(api, op('would-change', 1)).json()['results'][0]['status'] == 'accepted'


def test_tombstone_conflicts_with_stale_update_and_remains_in_pull(api):
    push(api, op())
    deleted = push(api, op('delete', 1, is_deleted=True)).json()['results'][0]
    assert deleted['revision'] == 2
    assert deleted['server_character']['is_deleted']
    assert push(api, op('stale', 1)).json()['results'][0]['status'] == 'conflict'
    assert push(api).json()['characters'][0]['is_deleted']


def test_conflict_resolution_requires_new_operation_and_current_base(api):
    push(api, op())
    old = op('conflicting', 0)
    assert push(api, old).json()['results'][0]['status'] == 'conflict'
    old['base_revision'] = 1
    assert push(api, old).status_code == 409
    assert push(api, op('resolved', 1)).json()['results'][0]['revision'] == 2


def test_other_user_cannot_read_or_mutate_account_records(api):
    push(api, op())
    client, _, _ = api
    registered = client.post('/api/auth/register', json={'username': 'other_user', 'password': 'Password123!'})
    other_headers = {'Authorization': 'Bearer ' + registered.json()['access_token']}
    assert client.post('/api/sync/v2', headers=other_headers, json={}).json()['characters'] == []
    assert client.post('/api/sync/v2', headers=other_headers, json={'operations': [op()]}).status_code == 409
    assert push(api).json()['characters'][0]['revision'] == 1


def test_orm_stale_writer_is_rejected_even_outside_sync(api):
    push(api, op())
    _, _, factory = api
    with factory() as first, factory() as second:
        a = first.query(Character).first()
        b = second.query(Character).first()
        a.name = 'First writer'
        first.commit()
        b.name = 'Stale writer'
        with pytest.raises(StaleDataError):
            second.commit()
        second.rollback()
    assert push(api).json()['characters'][0]['name'] == 'First writer'


def test_client_clock_does_not_control_revision_order(api):
    initial = op()
    initial['updated_at'] = '2099-01-01T00:00:00Z'
    push(api, initial)
    later = op('next', 1)
    later['updated_at'] = '1900-01-01T00:00:00Z'
    assert push(api, later).json()['results'][0]['revision'] == 2


def test_migration_preserves_rows_and_takes_one_backup(tmp_path):
    path = tmp_path / 'legacy.db'
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute('CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT)')
        conn.execute("INSERT INTO characters VALUES (7, 'Preserve me')")
    migrate_character_revision(path)
    migrate_character_revision(path)
    with closing(sqlite3.connect(path)) as conn:
        assert conn.execute('SELECT * FROM characters').fetchall() == [(7, 'Preserve me', 1)]
    backups = list((tmp_path / 'backups').glob('*.db'))
    assert len(backups) == 1
    with closing(sqlite3.connect(backups[0])) as conn:
        assert conn.execute('SELECT * FROM characters').fetchall() == [(7, 'Preserve me')]


def test_migration_assigns_stable_ids_to_legacy_characters(tmp_path):
    path = tmp_path / 'legacy.db'
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute('CREATE TABLE characters (id INTEGER PRIMARY KEY, server_id TEXT)')
        conn.execute('INSERT INTO characters VALUES (1, NULL)')
    migrate_character_revision(path)
    with closing(sqlite3.connect(path)) as conn:
        before = conn.execute('SELECT server_id FROM characters').fetchone()[0]
    assert before
    migrate_character_revision(path)
    with closing(sqlite3.connect(path)) as conn:
        assert conn.execute('SELECT server_id FROM characters').fetchone()[0] == before


def test_seed_never_overwrites_small_existing_user_database(tmp_path, monkeypatch):
    import gzip
    from app.core import database
    path = tmp_path / 'characters.db'
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute('CREATE TABLE characters (name TEXT)')
        conn.execute("INSERT INTO characters VALUES ('User data')")
    with gzip.open(tmp_path / 'seed_characters.db.gz', 'wb') as output:
        output.write(b'Not the user database')
    monkeypatch.setattr(database, 'DB_PATH', path)
    database.check_db_exists()
    with closing(sqlite3.connect(path)) as conn:
        assert conn.execute('SELECT name FROM characters').fetchone()[0] == 'User data'


def test_two_sqlite_clients_conflict_and_explicit_resolution(api, tmp_path):
    from desktop import local_db as local, sync_v2_store as client_sync
    a, b = tmp_path / 'a.db', tmp_path / 'b.db'
    for path in (a, b):
        local.init_local_db(path)
        local.save_local_auth(path, 'revision_user', 'test-token')
    first = local.save_local_character(a, {'name': 'Initial', 'system': 'pf1e'})

    def exchange(path):
        session = local.get_sync_session(path)
        operations = client_sync.prepare_operations(path, session)
        response = push(api, *operations)
        assert response.status_code == 200
        client_sync.apply_response(path, operations, response.json(), session)
        return response.json()

    exchange(a)
    exchange(b)
    second = local.list_local_characters(b)[0]
    local.save_local_character(a, {'name': 'Device A', 'system': 'pf1e'}, first.id)
    local.save_local_character(b, {'name': 'Device B', 'system': 'pf1e'}, second.id)
    assert exchange(a)['results'][0]['revision'] == 2
    assert exchange(b)['results'][0]['status'] == 'conflict'
    assert local.get_local_character(b, second.id).name == 'Device B'
    conflict = client_sync.list_conflicts(b)[0]
    client_sync.resolve_conflict(b, second.server_id, conflict['conflict']['operation_id'],
                                conflict['fingerprint'], 'local', local.get_sync_session(b))
    assert exchange(b)['results'][0]['revision'] == 3
    exchange(a)
    assert local.get_local_character(a, first.id).name == 'Device B'
    assert not local.get_dirty_characters(a)
    assert not local.get_dirty_characters(b)


def test_lost_reply_retries_same_operation_after_client_restart(api, tmp_path):
    from desktop import local_db as local, sync_v2_store as client_sync
    path = tmp_path / 'client.db'
    local.init_local_db(path)
    local.save_local_auth(path, 'revision_user', 'test-token')
    record = local.save_local_character(path, {'name': 'Before', 'system': 'pf1e'})
    session = local.get_sync_session(path)
    operations = client_sync.prepare_operations(path, session)
    assert push(api, *operations).status_code == 200  # Server committed; reply lost.
    local.save_local_character(path, {'name': 'After', 'system': 'pf1e'}, record.id)
    local.init_local_db(path)
    retry = client_sync.prepare_operations(path, session)
    assert retry == operations
    client_sync.apply_response(path, retry, push(api, *retry).json(), session)
    next_ops = client_sync.prepare_operations(path, session)
    assert next_ops[0]['base_revision'] == 1
    assert next_ops[0]['name'] == 'After'
    client_sync.apply_response(path, next_ops, push(api, *next_ops).json(), session)
    assert local.get_local_character(path, record.id).name == 'After'
    assert not local.get_dirty_characters(path)


@pytest.mark.parametrize('method,suffix,payload', [
    ('put', '', {'system': 'pf1e', 'name': 'Edit', 'data': {}}),
    ('delete', '', None),
    ('post', '/level-up', {'class_name': 'Fighter'}),
    ('post', '/level-undo', None),
    ('post', '/gm/modifiers', {'stat': 'ac', 'value': 1, 'name': 'Buff'}),
    ('post', '/gm/overrides', {'selection_type': 'feat', 'selection_key': 'Power Attack', 'reason': 'GM approval'}),
    ('put', '/level-up-session', {'target_level': 2, 'state': 'started'}),
])
def test_all_legacy_mutations_require_matching_revision(api, method, suffix, payload):
    record = push(api, op()).json()['characters'][0]
    client, headers, _ = api
    url = f"/api/characters/{record['id']}{suffix}"
    assert client.request(method, url, headers=headers, json=payload).status_code == 428
    assert client.request(method, url, headers={**headers, 'If-Match': '999'}, json=payload).status_code == 409
    assert push(api).json()['characters'][0]['revision'] == 1


def test_portrait_requires_revision_before_any_write(api):
    record = push(api, op()).json()['characters'][0]
    client, headers, _ = api
    response = client.post(f"/api/characters/{record['id']}/portrait", headers=headers,
                           files={'file': ('portrait.png', b'png', 'image/png')})
    assert response.status_code == 428


def test_update_then_soft_delete_preserves_history_and_sync_tombstone(api, monkeypatch):
    from app.routers.characters import service
    from app.models.progression import LevelProgression
    monkeypatch.setattr(service, 'recalculate', lambda data: data)
    record = push(api, op()).json()['characters'][0]
    client, headers, factory = api
    url = f"/api/characters/{record['id']}"
    with factory() as session:
        session.add(LevelProgression(character_id=record['id'], level=2, class_name='Fighter', choices='{}', created_at='now'))
        session.commit()
    updated = client.put(url, headers={**headers, 'If-Match': '"1"'}, json={'system': 'pf1e', 'name': 'Updated', 'data': {}})
    assert updated.status_code == 200
    assert updated.json()['revision'] == 2
    assert client.delete(url, headers={**headers, 'If-Match': '1'}).status_code == 409
    assert client.delete(url, headers={**headers, 'If-Match': '2'}).status_code == 204
    tombstone = push(api).json()['characters'][0]
    assert tombstone['is_deleted'] and tombstone['revision'] == 3
    assert client.get(url, headers=headers).status_code == 404
    assert client.get('/api/characters', headers=headers).json() == []
    with factory() as session:
        assert session.query(LevelProgression).count() == 1


def test_auxiliary_override_write_advances_revision(api):
    record = push(api, op()).json()['characters'][0]
    client, headers, _ = api
    url = f"/api/characters/{record['id']}/gm/overrides"
    response = client.post(url, headers={**headers, 'If-Match': '1'}, json={
        'selection_type': 'feat', 'selection_key': 'Power Attack', 'reason': 'GM approval',
    })
    assert response.status_code == 201
    assert response.json()['revision'] == 2
    assert push(api, op('stale-after-override', 1)).json()['results'][0]['status'] == 'conflict'


def test_put_race_returns_409_and_rolls_back(api, monkeypatch):
    from app.routers.characters import service
    record = push(api, op()).json()['characters'][0]
    client, headers, factory = api
    def concurrent_recalculation(data):
        with factory() as session:
            other = session.get(Character, record['id'])
            other.name = 'Concurrent winner'
            session.commit()
        return data
    monkeypatch.setattr(service, 'recalculate', concurrent_recalculation)
    response = client.put(f"/api/characters/{record['id']}", headers={**headers, 'If-Match': '1'},
                          json={'system': 'pf1e', 'name': 'Stale loser', 'data': {}})
    assert response.status_code == 409
    assert push(api).json()['characters'][0]['name'] == 'Concurrent winner'
