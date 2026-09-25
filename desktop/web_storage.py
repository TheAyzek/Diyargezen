"""SQLite persistence for the embedded web client's v2 record contract.

One transaction per bridge command. Old native/IndexedDB stores are left intact;
this table has explicit verified account partitions, never inferred ownership.
"""
import json
import uuid
from datetime import datetime, timezone
from desktop.local_db import _connect


def _new_id():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc).isoformat()


class WebStorage:
    def __init__(self, path):
        self.path = path
        with _connect(path) as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS web_local_records (
                    owner TEXT NOT NULL, id TEXT NOT NULL, body TEXT NOT NULL,
                    PRIMARY KEY(owner,id));
                CREATE TABLE IF NOT EXISTS web_local_archives (
                    owner TEXT NOT NULL, id TEXT NOT NULL, body TEXT NOT NULL,
                    PRIMARY KEY(owner,id));
                CREATE TABLE IF NOT EXISTS web_level_drafts (
                    owner TEXT NOT NULL, id TEXT NOT NULL, body TEXT NOT NULL,
                    PRIMARY KEY(owner,id));
            ''')

    def execute(self, owner, method, args):
        if not owner or method not in {'all', 'get', 'save', 'delete', 'prepare', 'apply', 'resolve', 'archives', 'restore', 'draft_get', 'draft_save'}:
            raise ValueError('Geçersiz yerel işlem')
        with _connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if method == 'draft_get':
                row = db.execute('SELECT body FROM web_level_drafts WHERE owner=? AND id=?', (owner, str(args['id']))).fetchone()
                return json.loads(row[0]) if row else None
            if method == 'draft_save':
                db.execute('INSERT INTO web_level_drafts VALUES(?,?,?) ON CONFLICT(owner,id) DO UPDATE SET body=excluded.body',
                           (owner, str(args['id']), json.dumps(args['value'], ensure_ascii=False, allow_nan=False)))
                return True
            records = {row[0]: json.loads(row[1]) for row in db.execute(
                'SELECT id,body FROM web_local_records WHERE owner=?', (owner,))}

            def put(record):
                records[record['id']] = record
                db.execute('INSERT INTO web_local_records VALUES(?,?,?) ON CONFLICT(owner,id) DO UPDATE SET body=excluded.body',
                           (owner, record['id'], json.dumps(record, ensure_ascii=False, allow_nan=False)))

            def save(character):
                key = str(character.get('server_id') or character.get('id') or _new_id())
                previous = records.get(key, {})
                system = character.get('system', 'pf1e').lower()
                if system not in {'pf1e', 'pathfinder1e'}:
                    raise ValueError('Yalnızca PF1e desteklenir')
                record = {
                    **character, 'id': key, 'server_id': key, 'system': system,
                    'name': character.get('name') or 'İsimsiz Kahraman',
                    'data': character.get('data', character),
                    'created_at': character.get('created_at') or _now(), 'updated_at': _now(),
                    'is_dirty': True, 'is_deleted': bool(character.get('is_deleted')),
                    'revision': character.get('revision', previous.get('revision', 0)),
                    'local_revision': _new_id(),
                    'pending_operation': previous.get('pending_operation'),
                    'conflict': previous.get('conflict'),
                }
                put(record)
                return record

            if method == 'all':
                return list(records.values())
            if method == 'get':
                return records.get(args['id'])
            if method == 'save':
                return save(args['character'])
            if method == 'delete':
                if args['id'] in records:
                    put({**records[args['id']], 'is_deleted': True, 'is_dirty': True,
                         'updated_at': _now(), 'local_revision': _new_id()})
                return True
            if method == 'prepare':
                if owner == 'guest':
                    return []
                operations = []
                for record in records.values():
                    if not record['is_dirty'] or record.get('conflict'):
                        continue
                    if not record.get('pending_operation'):
                        record['pending_operation'] = {
                            'local_revision': record['local_revision'],
                            'payload': {
                                'operation_id': _new_id(), 'server_id': record['server_id'],
                                'base_revision': record['revision'], 'system': record['system'],
                                'name': record['name'], 'data': record['data'], 'is_deleted': record['is_deleted'],
                            },
                        }
                        put(record)
                    operations.append(record['pending_operation']['payload'])
                    if len(operations) == 100:
                        break
                return operations
            if method == 'apply':
                response = args['response']
                if response.get('protocol_version') != 2 or not isinstance(response.get('results'), list) or not isinstance(response.get('characters'), list):
                    raise ValueError('Geçersiz senkronizasyon yanıtı')
                sent = {op['operation_id']: op for op in args['operations']}
                seen = set()
                for result in response['results']:
                    op_id, key = result['operation_id'], result['server_id']
                    if op_id in seen or op_id not in sent or sent[op_id]['server_id'] != key:
                        raise ValueError('Geçersiz işlem onayı')
                    seen.add(op_id)
                    if result['status'] == 'accepted':
                        remote = _remote(result['server_character'])
                        if remote['id'] != key or remote['revision'] != result['revision']:
                            raise ValueError('Geçersiz revizyon')
                    elif result['status'] == 'conflict':
                        remote = result.get('server_character')
                        if not isinstance(result.get('actual_revision'), int) or (remote and remote['server_id'] != key):
                            raise ValueError('Geçersiz çakışma')
                    else:
                        raise ValueError('Geçersiz sonuç')
                    record = records.get(key)
                    pending = (record or {}).get('pending_operation') or {}
                    if pending.get('payload', {}).get('operation_id') != op_id:
                        continue
                    if result['status'] == 'conflict':
                        put({**record, 'conflict': result, 'pending_operation': None})
                    elif pending['local_revision'] == record['local_revision']:
                        put(remote)
                    else:
                        put({**record, 'revision': remote['revision'], 'remote_id': remote['remote_id'], 'pending_operation': None})
                for item in response['characters']:
                    remote = _remote(item)
                    record = records.get(remote['id'])
                    if record and (record['is_dirty'] or record.get('conflict') or record['revision'] > remote['revision']):
                        continue
                    put(remote)
                return True
            if method == 'resolve':
                record = records.get(args['id'])
                if not record or (record.get('conflict') or {}).get('operation_id') != args['operationId'] or record['local_revision'] != args['localRevision']:
                    raise ValueError('Çakışma değişti; yeniden yükleyin')
                if args['choice'] not in {'local', 'server'}:
                    raise ValueError('Geçersiz çözüm')
                db.execute('INSERT INTO web_local_archives VALUES(?,?,?)', (owner, _new_id(), json.dumps(record)))
                remote = record['conflict'].get('server_character')
                if args['choice'] == 'local':
                    put({**record, 'revision': remote['revision'] if remote else 0, 'conflict': None,
                         'pending_operation': None, 'is_dirty': True, 'local_revision': _new_id()})
                elif remote:
                    put(_remote(remote))
                else:
                    put({**record, 'conflict': None, 'pending_operation': None, 'is_deleted': True, 'is_dirty': False})
                return True
            if method == 'archives':
                return [{'key': row[0], 'value': json.loads(row[1])} for row in db.execute(
                    'SELECT id,body FROM web_local_archives WHERE owner=?', (owner,))]
            if method == 'restore':
                row = db.execute('SELECT body FROM web_local_archives WHERE owner=? AND id=?', (owner, args['key'])).fetchone()
                if not row:
                    raise ValueError('Arşiv bulunamadı')
                record = json.loads(row[0])
                key = _new_id()
                name = record['name'] + ' (Kurtarıldı)'
                return save({**record, 'id': key, 'server_id': key, 'remote_id': None,
                             'revision': 0, 'is_deleted': False, 'name': name,
                             'data': {**record['data'], 'id': key, 'server_id': key, 'name': name}})


def _remote(item):
    if not item.get('server_id') or type(item.get('revision')) is not int or item['revision'] < 1:
        raise ValueError('Geçersiz sunucu kaydı')
    return {**item, 'id': str(item['server_id']), 'server_id': str(item['server_id']),
            'remote_id': item['id'], 'is_dirty': False, 'is_deleted': bool(item.get('is_deleted')),
            'pending_operation': None, 'conflict': None, 'local_revision': _new_id()}
