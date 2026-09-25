"""Durable v2 outbox and conflicts, partitioned by the current SQLite account."""
import hashlib
import json
import sqlite3
import uuid
from desktop import local_db


def _fingerprint(record):
    values = [record[k] for k in ('name', 'system', 'data', 'is_deleted', 'updated_at')]
    return hashlib.sha256(json.dumps(values, ensure_ascii=False).encode()).hexdigest()


def _state(conn, owner, server_id):
    row = conn.execute('SELECT state FROM sync_v2_records WHERE owner=? AND server_id=?', (owner, server_id)).fetchone()
    return json.loads(row[0]) if row else {'revision': 0}


def _put_state(conn, owner, server_id, state):
    conn.execute('INSERT INTO sync_v2_records VALUES (?,?,?) ON CONFLICT(owner,server_id) DO UPDATE SET state=excluded.state',
                 (owner, server_id, json.dumps(state, ensure_ascii=False)))


def _record(conn, owner, server_id):
    return conn.execute('SELECT * FROM local_characters WHERE owner=? AND server_id=?', (owner, server_id)).fetchone()


def prepare_operations(path, session):
    with local_db._connect(path) as conn:
        conn.execute('BEGIN IMMEDIATE')
        owner = local_db._owner(conn, session)
        if not owner:
            return []
        conn.row_factory = sqlite3.Row
        records = conn.execute('SELECT * FROM local_characters WHERE owner=? AND is_dirty=1 ORDER BY id', (owner,)).fetchall()
        operations = []
        for record in records:
            if len(operations) == 100:
                break
            if record['system'].lower() not in {'pf1e', 'pathfinder1e'}:
                continue
            state = _state(conn, owner, record['server_id'])
            if state.get('conflict'):
                continue
            if not state.get('pending'):
                state['pending'] = {
                    'fingerprint': _fingerprint(record),
                    'payload': {
                        'operation_id': str(uuid.uuid4()), 'server_id': record['server_id'],
                        'base_revision': state['revision'], 'system': record['system'].lower(),
                        'name': record['name'], 'data': json.loads(record['data']),
                        'is_deleted': bool(record['is_deleted']),
                    },
                }
                _put_state(conn, owner, record['server_id'], state)
            operations.append(state['pending']['payload'])
        return operations


def _write_remote(conn, owner, remote):
    server_id = remote['server_id']
    existing = conn.execute('SELECT owner FROM local_characters WHERE server_id=?', (server_id,)).fetchone()
    if existing and existing[0] != owner:
        raise ValueError('Kayıt kimliği başka yerel hesaba ait')
    conn.execute('''INSERT INTO local_characters
        (server_id,owner,system,name,data,is_dirty,is_deleted,created_at,updated_at)
        VALUES (?,?,?,?,?,0,?,?,?) ON CONFLICT(server_id) DO UPDATE SET
        system=excluded.system,name=excluded.name,data=excluded.data,is_dirty=0,
        is_deleted=excluded.is_deleted,updated_at=excluded.updated_at''',
        (server_id, owner, remote['system'], remote['name'], json.dumps(remote['data'], ensure_ascii=False),
         int(remote['is_deleted']), remote['created_at'], remote['updated_at']))


def apply_response(path, operations, response, session):
    if response.get('protocol_version') != 2 or not isinstance(response.get('results'), list) or not isinstance(response.get('characters'), list):
        raise ValueError('Geçersiz v2 yanıtı')
    sent = {op['operation_id']: op for op in operations}
    seen = set()
    with local_db._connect(path) as conn:
        conn.execute('BEGIN IMMEDIATE')
        owner = local_db._owner(conn, session)
        conn.row_factory = sqlite3.Row
        for result in response['results']:
            op_id = result['operation_id']
            server_id = result['server_id']
            if op_id not in sent or op_id in seen or sent[op_id]['server_id'] != server_id:
                raise ValueError('Geçersiz işlem onayı')
            seen.add(op_id)
            state = _state(conn, owner, server_id)
            record = _record(conn, owner, server_id)
            if not record or state.get('pending', {}).get('payload', {}).get('operation_id') != op_id:
                continue
            if result['status'] == 'conflict':
                state['conflict'] = result
            elif result['status'] == 'accepted':
                remote = result['server_character']
                if remote['server_id'] != server_id or remote['revision'] != result['revision']:
                    raise ValueError('Geçersiz sunucu revizyonu')
                if _fingerprint(record) == state['pending']['fingerprint']:
                    _write_remote(conn, owner, remote)
                state['revision'] = result['revision']
            else:
                raise ValueError('Bilinmeyen işlem sonucu')
            state.pop('pending', None)
            _put_state(conn, owner, server_id, state)

        for remote in response['characters']:
            server_id = remote['server_id']
            if not server_id or not isinstance(remote['revision'], int):
                raise ValueError('Geçersiz karakter revizyonu')
            state = _state(conn, owner, server_id)
            record = _record(conn, owner, server_id)
            if (record and record['is_dirty']) or state.get('conflict') or state['revision'] > remote['revision']:
                continue
            _write_remote(conn, owner, remote)
            _put_state(conn, owner, server_id, {'revision': remote['revision']})


def list_conflicts(path):
    with local_db._connect(path) as conn:
        conn.execute('BEGIN')
        owner = local_db._owner(conn)
        conn.row_factory = sqlite3.Row
        conflicts = []
        for row in conn.execute('SELECT server_id,state FROM sync_v2_records WHERE owner=?', (owner,)):
            state = json.loads(row['state'])
            record = _record(conn, owner, row['server_id'])
            if state.get('conflict') and record:
                conflicts.append({'local': dict(record), 'conflict': state['conflict'], 'fingerprint': _fingerprint(record)})
        return conflicts


def resolve_conflict(path, server_id, operation_id, fingerprint, choice, session):
    if choice not in {'local', 'server'}:
        raise ValueError('Geçersiz çözüm')
    with local_db._connect(path) as conn:
        conn.execute('BEGIN IMMEDIATE')
        owner = local_db._owner(conn, session)
        conn.row_factory = sqlite3.Row
        state = _state(conn, owner, server_id)
        record = _record(conn, owner, server_id)
        if not record or state.get('conflict', {}).get('operation_id') != operation_id or _fingerprint(record) != fingerprint:
            raise ValueError('Çakışma değişti; yeniden yükleyin')
        conn.execute('INSERT INTO sync_state VALUES (?,?)',
                     ('conflict_archive:' + str(uuid.uuid4()), json.dumps({'owner': owner, 'local': dict(record), 'state': state})))
        remote = state['conflict']['server_character']
        if choice == 'server':
            if remote:
                _write_remote(conn, owner, remote)
            else:
                conn.execute('UPDATE local_characters SET is_dirty=0,is_deleted=1 WHERE owner=? AND server_id=?', (owner, server_id))
        _put_state(conn, owner, server_id, {'revision': remote['revision'] if remote else 0})
