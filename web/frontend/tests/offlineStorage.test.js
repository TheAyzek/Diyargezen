import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { IDBFactory } from 'fake-indexeddb';
import axios from 'axios';
import * as storage from '../src/utils/offlineStorage.js';
import { captureSession, rotateSession } from '../src/utils/sessionScope.js';
import { editorFingerprint, requestRevisionAction } from '../src/utils/revisionActions.js';

const values = new Map();
globalThis.localStorage = {
  getItem: key => values.get(key) ?? null,
  setItem: (key, value) => values.set(key, String(value)),
  removeItem: key => values.delete(key),
};
Object.defineProperty(globalThis, 'navigator', { value: { onLine: true }, configurable: true });
const { triggerSync } = await import('../src/utils/syncEngine.js');

function login(name) {
  localStorage.setItem('token', name + '-token');
  localStorage.setItem('username', name);
  rotateSession();
}
const save = name => storage.saveLocalCharacter({ name, system: 'pf1e', data: { name } });

test('level-up drafts survive reopening and remain account-scoped without modifying characters', async () => {
  login('alice');
  const character = await save('Valeros');
  const draft = { version: 1, baseLevel: 3, step: 2, allocatedRanks: { Climb: 1 } };
  await storage.saveLevelDraft(character.id, draft);
  assert.deepEqual(await storage.getLevelDraft(character.id), draft);
  assert.deepEqual(await storage.getLocalCharacter(character.id), character);
  login('bob');
  assert.equal(await storage.getLevelDraft(character.id), null);
  login('alice');
  assert.deepEqual(await storage.getLevelDraft(character.id), draft);
  await storage.saveLevelDraft(character.id, null);
  assert.equal(await storage.getLevelDraft(character.id), null);
});

beforeEach(() => {
  delete globalThis.__diyargezenNativeReady;
  values.clear();
  globalThis.indexedDB = new IDBFactory();
  navigator.onLine = true;
});

test('native desktop storage routes exclusively to SQLite bridge', async () => {
  login('alice');
  globalThis.indexedDB = { open() { throw new Error('Must not open IndexedDB'); } };
  const calls = [];
  globalThis.__diyargezenNativeReady = Promise.resolve(async request => {
    calls.push(request);
    return { ok: true, value: request.method === 'all' ? [] : { id: 'native-record' } };
  });
  assert.equal((await save('Native')).id, 'native-record');
  assert.deepEqual(await storage.getAllLocalCharacters(), []);
  assert.equal(calls[0].session.owner, 'account:alice');
  assert.deepEqual(calls.map(call => call.method), ['save', 'all']);
});

test('native failure never falls back to an independent browser write', async () => {
  globalThis.indexedDB = { open() { throw new Error('Fallback forbidden'); } };
  globalThis.__diyargezenNativeReady = Promise.resolve(async () => ({ ok: false, error: 'SQLite failed' }));
  await assert.rejects(save('Native'), /SQLite failed/);
});

test('late native result is rejected after account changes', async () => {
  login('alice');
  globalThis.__diyargezenNativeReady = Promise.resolve(async () => {
    login('bob');
    return { ok: true, value: [] };
  });
  await assert.rejects(storage.getAllLocalCharacters(), /Oturum değişti/);
});

test('accounts and guest isolate records and checkpoints', async () => {
  const guest = await save('Guest');
  login('alice');
  assert.deepEqual(await storage.getAllLocalCharacters(), []);
  const alice = await save('Alice');
  await storage.applySyncResponse([alice], { updated_characters: [alice], synced_at: 'alice-time' });
  login('bob');
  assert.deepEqual(await storage.getAllLocalCharacters(), []);
  assert.equal(await storage.getLocalCharacter(alice.id), null);
  assert.equal(await storage.getLastSyncTimestamp(), null);
  await storage.deleteLocalCharacter(alice.id);
  login('alice');
  assert.equal((await storage.getLocalCharacter(alice.id)).name, 'Alice');
  assert.equal(await storage.getLastSyncTimestamp(), 'alice-time');
  values.clear();
  assert.equal((await storage.getAllLocalCharacters())[0].id, guest.id);
});

test('boolean dirty records are actually queued', async () => {
  await save('Queued');
  assert.equal((await storage.getDirtyCharacters()).length, 1);
});

test('in-flight edit and delete survive old server responses', async () => {
  const original = await save('Original');
  const edit = await storage.saveLocalCharacter({ ...original, name: 'New edit' });
  await storage.applySyncResponse([original], { updated_characters: [original] });
  assert.equal((await storage.getLocalCharacter(original.id)).name, 'New edit');
  await storage.deleteLocalCharacter(original.id);
  await storage.applySyncResponse([edit], { updated_characters: [edit] });
  assert.deepEqual(await storage.getAllLocalCharacters(), []);
  assert.equal((await storage.getDirtyCharacters())[0].is_deleted, true);
});

test('missing acknowledgement never clears dirty state', async () => {
  const original = await save('Queued');
  await storage.applySyncResponse([original], { updated_characters: [], synced_at: 'time' });
  assert.equal((await storage.getDirtyCharacters()).length, 1);
});

test('acknowledged tombstone is removed; retry does not duplicate', async () => {
  const original = await save('Delete');
  await storage.deleteLocalCharacter(original.id);
  const sent = await storage.getDirtyCharacters();
  for (let i = 0; i < 2; i++) {
    await storage.applySyncResponse(sent, { deleted_server_ids: [original.server_id] });
  }
  assert.deepEqual(await storage.getDirtyCharacters(), []);
  assert.equal(await storage.getLocalCharacter(original.id), null);
});

test('old session response is rejected even on same-account re-login', async () => {
  login('alice');
  const original = await save('Alice');
  const session = captureSession();
  login('alice');
  await assert.rejects(storage.applySyncResponse([original], {
    updated_characters: [original], synced_at: 'late',
  }, session));
  assert.equal(await storage.getLastSyncTimestamp(), null);
  assert.equal((await storage.getDirtyCharacters()).length, 1);
});

test('transaction abort rolls back updates and checkpoint', async () => {
  const original = await save('Keep');
  // An uncloneable function causes the whole readwrite transaction to abort.
  await assert.rejects(storage.applySyncResponse([original], {
    updated_characters: [original], synced_at: () => {},
  }));
  assert.equal((await storage.getDirtyCharacters()).length, 1);
  assert.equal(await storage.getLastSyncTimestamp(), null);
});

test('background sync fixes credentials to the captured account', async t => {
  login('alice');
  const original = await save('Alice');
  t.mock.method(axios, 'post', async (url, payload, config) => {
    assert.equal(config.headers.Authorization, 'Bearer alice-token');
    assert.equal(url, '/api/sync/v2');
    assert.equal(payload.operations[0].server_id, original.server_id);
    login('bob');
    return { data: { protocol_version: 2, results: [], characters: [] } };
  });
  await triggerSync('alice-token');
  assert.deepEqual(await storage.getAllLocalCharacters(), []);
  login('alice');
  assert.equal((await storage.getDirtyCharacters()).length, 1);
  assert.equal(await storage.getLastSyncTimestamp(), null);
});

test('successful sync leaves edits made during the request queued', async t => {
  login('alice');
  const original = await save('Old');
  t.mock.method(axios, 'post', async (url, payload) => {
    await storage.saveLocalCharacter({ ...original, name: 'New' });
    return { data: { protocol_version: 2, results: [{
      operation_id: payload.operations[0].operation_id, server_id: original.server_id,
      status: 'accepted', revision: 1, server_character: { ...original, revision: 1 },
    }], characters: [] } };
  });
  await triggerSync('alice-token');
  assert.equal((await storage.getDirtyCharacters())[0].name, 'New');
});

test('legacy unscoped database is not opened or migrated automatically', async () => {
  const opened = [];
  const open = indexedDB.open.bind(indexedDB);
  indexedDB.open = (...args) => { opened.push(args[0]); return open(...args); };
  login('alice');
  await save('New');
  assert.ok(opened.every(name => name.startsWith('DiyargezenScopedDB:')));
});

test('server numeric ID stays separate from the stable sync UUID', async () => {
  const original = await save('Valeros');
  await storage.applySyncResponse([original], {
    updated_characters: [{ ...original, id: 42 }],
  });
  const stored = await storage.getLocalCharacter(original.id);
  assert.equal(stored.remote_id, 42);
  assert.equal(stored.id, original.server_id);
  const clone = await storage.cloneLocalCharacter(stored.id);
  assert.equal(clone.remote_id, null);
  assert.notEqual(clone.server_id, original.server_id);
});

function accepted(operation, revision = 1) {
  const remote = { ...operation, id: 42, revision };
  return { protocol_version: 2, characters: [remote], results: [{
    operation_id: operation.operation_id, server_id: operation.server_id,
    status: 'accepted', revision, server_character: remote,
  }] };
}

function conflicted(operation, deleted = false) {
  const remote = { ...operation, id: 42, revision: 4, name: 'Server copy', is_deleted: deleted };
  return { protocol_version: 2, characters: [remote], results: [{
    operation_id: operation.operation_id, server_id: operation.server_id,
    status: 'conflict', actual_revision: 4, server_character: remote,
  }] };
}

test('persistent v2 operation is immutable across edits and retry', async () => {
  const original = await save('Before');
  const first = await storage.prepareSyncOperations();
  await storage.saveLocalCharacter({ ...original, name: 'After' });
  assert.deepEqual(await storage.prepareSyncOperations(), first);
  assert.equal((await storage.getLocalCharacter(original.id)).pending_operation.payload.name, 'Before');
  await storage.applySyncV2(first, accepted(first[0]));
  const next = await storage.prepareSyncOperations();
  assert.equal(next[0].name, 'After');
  assert.equal(next[0].base_revision, 1);
  assert.notEqual(next[0].operation_id, first[0].operation_id);
});

test('conflict persists and stops sending until explicit local resolution', async () => {
  const original = await save('Local copy');
  const ops = await storage.prepareSyncOperations();
  await storage.applySyncV2(ops, conflicted(ops[0]));
  assert.deepEqual(await storage.prepareSyncOperations(), []);
  const record = (await storage.getSyncConflicts())[0];
  assert.equal(record.name, 'Local copy');
  assert.equal(record.conflict.server_character.name, 'Server copy');
  await storage.resolveSyncConflict(record.id, record.conflict.operation_id, record.local_revision, 'local');
  const resolved = await storage.prepareSyncOperations();
  assert.equal(resolved[0].base_revision, 4);
  assert.equal(resolved[0].name, 'Local copy');
  assert.notEqual(resolved[0].operation_id, ops[0].operation_id);
  assert.equal((await storage.getLocalCharacter(original.id)).conflict, null);
});

test('server deletion requires explicit resolution and archives local copy', async () => {
  await save('Local copy');
  const ops = await storage.prepareSyncOperations();
  await storage.applySyncV2(ops, conflicted(ops[0], true));
  const record = (await storage.getSyncConflicts())[0];
  await storage.resolveSyncConflict(record.id, record.conflict.operation_id, record.local_revision, 'server');
  assert.deepEqual(await storage.getAllLocalCharacters(), []);
  assert.deepEqual(await storage.getDirtyCharacters(), []);
  const database = await storage.openOfflineDB();
  const archive = await new Promise(resolve => {
    const request = database.transaction('meta').objectStore('meta').getAll();
    request.onsuccess = () => resolve(request.result);
  });
  database.close();
  assert.equal(archive[0].value.name, 'Local copy');
});

test('stale conflict dialog cannot overwrite a later edit', async () => {
  const original = await save('Local');
  const ops = await storage.prepareSyncOperations();
  await storage.applySyncV2(ops, conflicted(ops[0]));
  const record = (await storage.getSyncConflicts())[0];
  await storage.saveLocalCharacter({ ...original, name: 'Later edit' });
  await assert.rejects(storage.resolveSyncConflict(record.id, record.conflict.operation_id, record.local_revision, 'server'));
  assert.equal((await storage.getSyncConflicts())[0].name, 'Later edit');
});

test('missing v2 receipt leaves pending operation intact', async () => {
  await save('Pending');
  const ops = await storage.prepareSyncOperations();
  await storage.applySyncV2(ops, { protocol_version: 2, results: [], characters: [] });
  assert.deepEqual(await storage.prepareSyncOperations(), ops);
});

test('late v2 response cannot write into the next account', async () => {
  login('alice');
  await save('Alice');
  const session = captureSession();
  const ops = await storage.prepareSyncOperations(session);
  login('bob');
  await assert.rejects(storage.applySyncV2(ops, accepted(ops[0]), session));
  assert.deepEqual(await storage.getAllLocalCharacters(), []);
});

async function savedActionState() {
  login('alice');
  const record = await save('Valeros');
  const operations = await storage.prepareSyncOperations();
  await storage.applySyncV2(operations, accepted(operations[0]));
  const state = { id: 42, server_id: record.server_id, name: 'Valeros', revision: 1 };
  state.editorBaseline = editorFingerprint(state);
  return state;
}

test('level action sends captured revision and saves returned snapshot', async t => {
  const state = await savedActionState();
  t.mock.method(axios, 'post', async (url, body, config) => {
    assert.equal(url, '/api/characters/42/level-up');
    assert.equal(config.headers['If-Match'], '1');
    assert.equal(config.headers.Authorization, 'Bearer alice-token');
    return { data: { revision: 2, data: { level: 2 }, character: {
      id: 42, server_id: state.server_id, revision: 2, system: 'pf1e', name: 'Valeros', data: { level: 2 },
    } } };
  });
  await requestRevisionAction(state, 'level-up', {}, () => state);
  assert.equal((await storage.getLocalCharacter(state.server_id)).revision, 2);
});

test('unsaved or queued edits block remote progression before sending', async t => {
  const state = await savedActionState();
  const post = t.mock.method(axios, 'post', () => assert.fail('Must not send'));
  state.name = 'Unsaved';
  await assert.rejects(requestRevisionAction(state, 'level-up', {}, () => state));
  state.name = 'Valeros';
  await storage.saveLocalCharacter({ ...state, system: 'pf1e', data: {} });
  await assert.rejects(requestRevisionAction(state, 'level-undo', {}, () => state));
  assert.equal(post.mock.callCount(), 0);
});

test('edit during progression survives and retains its old base revision', async t => {
  const state = await savedActionState();
  t.mock.method(axios, 'post', async () => {
    state.name = 'New local edit';
    return { data: { revision: 2, character: { id: 42, server_id: state.server_id,
      revision: 2, name: 'Valeros', system: 'pf1e', data: { level: 2 } } } };
  });
  await assert.rejects(requestRevisionAction({ ...state }, 'level-up', {}, () => state));
  assert.equal(state.name, 'New local edit');
  await storage.saveLocalCharacter({ ...state, system: 'pf1e', data: {} });
  assert.equal((await storage.prepareSyncOperations())[0].base_revision, 1);
});

test('failed server level-up does not fall back to local level increment', async t => {
  const { useCharacterStore } = await import('../src/store/characterStore.js');
  const before = useCharacterStore.getState();
  t.after(() => useCharacterStore.setState(before, true));
  useCharacterStore.setState({ id: 42, level: 1, levelUp: async () => false });
  assert.equal(await useCharacterStore.getState().applyLevelUp({ newLevel: 2 }), false);
  assert.equal(useCharacterStore.getState().level, 1);
});
