import { captureSession, assertSession } from './sessionScope.js';
import { hasNativeStorage, nativeStorage } from './nativeStorage.js';

// Leave the unscoped legacy DiyargezenDB untouched; ownership is unknown.
export function databaseName(session) {
  return 'DiyargezenScopedDB:' + encodeURIComponent(session.owner);
}

export function openOfflineDB(session = captureSession()) {
  assertSession(session);
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(databaseName(session), 1);
    request.onupgradeneeded = () => {
      const db = request.result;
      db.createObjectStore('characters', { keyPath: 'id' });
      db.createObjectStore('meta', { keyPath: 'key' });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

// Resolve only after commit, never on the success of an individual request.
async function transaction(session, stores, mode, action) {
  const db = await openOfflineDB(session);
  try {
    assertSession(session);
    return await new Promise((resolve, reject) => {
      const tx = db.transaction(stores, mode);
      let result;
      tx.oncomplete = () => {
        try { assertSession(session); resolve(result); } catch (error) { reject(error); }
      };
      tx.onabort = () => reject(tx.error || new Error('Yerel işlem iptal edildi.'));
      tx.onerror = () => {}; // onabort owns error reporting.
      try { action(tx, value => { result = value; }); }
      catch (error) { tx.abort(); reject(error); }
    });
  } finally { db.close(); }
}

function allRecords(session) {
  if (hasNativeStorage()) return nativeStorage('all', {}, session);
  return transaction(session, ['characters'], 'readonly', (tx, done) => {
    const request = tx.objectStore('characters').getAll();
    request.onsuccess = () => done(request.result);
  });
}

export async function saveLocalCharacter(character, isDirty = true, session = captureSession()) {
  if (hasNativeStorage()) {
    if (!isDirty) throw new Error('Temiz kayıtlar yalnızca sunucu onayıyla uygulanır.');
    return nativeStorage('save', { character }, session);
  }
  const now = new Date().toISOString();
  const id = String(character.server_id || character.id || crypto.randomUUID());
  const record = {
    ...character, id, server_id: String(character.server_id || id),
    name: character.name || character.isim || 'İsimsiz Kahraman',
    system: (character.system || 'pathfinder1e').toLowerCase(),
    data: character.data || character,
    is_dirty: isDirty, is_deleted: !!character.is_deleted,
    created_at: character.created_at || now,
    updated_at: isDirty ? now : (character.updated_at || now),
    local_revision: crypto.randomUUID(),
  };
  return transaction(session, ['characters'], 'readwrite', (tx, done) => {
    const store = tx.objectStore('characters');
    const request = store.get(id);
    request.onsuccess = () => {
      const previous = request.result;
      const saved = { ...record, revision: character.revision ?? previous?.revision ?? 0,
        pending_operation: previous?.pending_operation || null,
        conflict: previous?.conflict || null };
      store.put(saved);
      done(saved);
    };
  });
}

export async function getAllLocalCharacters(session = captureSession()) {
  return (await allRecords(session)).filter(record => !record.is_deleted);
}

export async function getDirtyCharacters(session = captureSession()) {
  // IndexedDB keys cannot be booleans; do not query a boolean dirty index.
  return (await allRecords(session)).filter(record => record.is_dirty);
}

export function getLocalCharacter(id, session = captureSession()) {
  if (hasNativeStorage()) return nativeStorage('get', { id }, session);
  return transaction(session, ['characters'], 'readonly', (tx, done) => {
    const request = tx.objectStore('characters').get(id);
    request.onsuccess = () => done(request.result || null);
  });
}

export function getLastSyncTimestamp(session = captureSession()) {
  return transaction(session, ['meta'], 'readonly', (tx, done) => {
    const request = tx.objectStore('meta').get('last_sync_timestamp');
    request.onsuccess = () => done(request.result?.value || null);
  });
}

// Drafts are account- and character-scoped, independent of the character revision.
// They never upload unfinished level-up decisions or dirty the committed sheet.
export function getLevelDraft(id, session = captureSession()) {
  if (hasNativeStorage()) return nativeStorage('draft_get', { id }, session);
  return transaction(session, ['meta'], 'readonly', (tx, done) => {
    const request = tx.objectStore('meta').get('level_draft:' + id);
    request.onsuccess = () => done(request.result?.value || null);
  });
}

export function saveLevelDraft(id, value, session = captureSession()) {
  if (hasNativeStorage()) return nativeStorage('draft_save', { id, value }, session);
  return transaction(session, ['meta'], 'readwrite', (tx, done) => {
    tx.objectStore('meta').put({ key: 'level_draft:' + id, value });
    done(true);
  });
}

export function deleteLocalCharacter(id, session = captureSession()) {
  if (hasNativeStorage()) return nativeStorage('delete', { id }, session);
  return transaction(session, ['characters'], 'readwrite', (tx, done) => {
    const store = tx.objectStore('characters');
    const request = store.get(id);
    request.onsuccess = () => {
      if (request.result) store.put({
        ...request.result, is_deleted: true, is_dirty: true,
        updated_at: new Date().toISOString(), local_revision: crypto.randomUUID(),
      });
      done(true);
    };
  });
}

export async function cloneLocalCharacter(id, session = captureSession()) {
  const record = await getLocalCharacter(id, session);
  if (!record) throw new Error('Klonlanacak karakter bulunamadı.');
  const newId = crypto.randomUUID();
  const name = record.name + ' (Kopya)';
  return saveLocalCharacter({
    ...record, id: newId, server_id: newId, remote_id: null, revision: 0, name,
    data: { ...record.data, id: newId, server_id: newId, name },
  }, true, session);
}

// A durable, immutable request survives reloads and ambiguous network failures.
export function prepareSyncOperations(session = captureSession()) {
  if (hasNativeStorage()) return nativeStorage('prepare', {}, session);
  return transaction(session, ['characters'], 'readwrite', (tx, done) => {
    const store = tx.objectStore('characters');
    const request = store.getAll();
    request.onsuccess = () => {
      const operations = [];
      for (const record of request.result) {
        if (operations.length >= 100) break;
        if (!record.is_dirty || record.conflict) continue;
        if (!record.pending_operation) {
          record.pending_operation = {
            local_revision: record.local_revision,
            payload: {
              operation_id: crypto.randomUUID(), server_id: record.server_id,
              base_revision: record.revision || 0, system: record.system,
              name: record.name, data: record.data, is_deleted: record.is_deleted,
            },
          };
          store.put(record);
        }
        operations.push(record.pending_operation.payload);
      }
      done(operations);
    };
  });
}

function fromRemote(remote) {
  return { ...remote, id: String(remote.server_id), server_id: String(remote.server_id),
    remote_id: remote.id, is_dirty: false, is_deleted: !!remote.is_deleted,
    pending_operation: null, conflict: null, local_revision: crypto.randomUUID() };
}

export function applySyncV2(operations, response, session = captureSession()) {
  if (hasNativeStorage()) return nativeStorage('apply', { operations, response }, session);
  if (response?.protocol_version !== 2 || !Array.isArray(response.results) || !Array.isArray(response.characters)) {
    throw new Error('Geçersiz v2 senkronizasyon yanıtı');
  }
  const sent = new Map(operations.map(op => [op.operation_id, op]));
  const seen = new Set();
  for (const result of response.results) {
    const op = sent.get(result.operation_id);
    if (!op || seen.has(result.operation_id) || result.server_id !== op.server_id ||
        !['accepted', 'conflict'].includes(result.status)) throw new Error('Geçersiz işlem onayı');
    seen.add(result.operation_id);
    if (result.status === 'accepted' && (!Number.isInteger(result.revision) || result.revision < 1 ||
        result.server_character?.server_id !== op.server_id || result.server_character?.revision !== result.revision)) {
      throw new Error('Eksik sunucu revizyonu');
    }
    if (result.status === 'conflict' && (!Number.isInteger(result.actual_revision) ||
        (result.server_character && result.server_character.server_id !== op.server_id))) {
      throw new Error('Geçersiz çakışma kaydı');
    }
  }
  return transaction(session, ['characters'], 'readwrite', (tx, done) => {
    const store = tx.objectStore('characters');
    const request = store.getAll();
    request.onsuccess = () => {
      const records = new Map(request.result.map(record => [record.id, record]));
      for (const result of response.results) {
        const record = records.get(result.server_id);
        if (record?.pending_operation?.payload.operation_id !== result.operation_id) continue;
        if (result.status === 'conflict') {
          records.set(record.id, { ...record, pending_operation: null, conflict: result });
        } else if (record.local_revision === record.pending_operation.local_revision) {
          records.set(record.id, fromRemote(result.server_character));
        } else {
          records.set(record.id, { ...record, revision: result.revision,
            remote_id: result.server_character.id, pending_operation: null });
        }
      }
      for (const remote of response.characters) {
        const record = records.get(String(remote.server_id));
        if (!remote.server_id || !Number.isInteger(remote.revision)) { tx.abort(); return; }
        if (record?.is_dirty || record?.conflict) continue;
        if (record && record.revision > remote.revision) continue;
        records.set(String(remote.server_id), fromRemote(remote));
      }
      for (const record of records.values()) store.put(record);
      done(true);
    };
  });
}

export async function getSyncConflicts(session = captureSession()) {
  return (await allRecords(session)).filter(record => record.conflict);
}

// Explicit recovery only: the old browser partition is never auto-merged.
export function getBrowserLocalCharacters(session = captureSession()) {
  return transaction(session, ['characters'], 'readonly', (tx, done) => {
    const request = tx.objectStore('characters').getAll();
    request.onsuccess = () => done(request.result);
  });
}

export function getConflictArchives(session = captureSession()) {
  if (hasNativeStorage()) return nativeStorage('archives', {}, session);
  return transaction(session, ['meta'], 'readonly', (tx, done) => {
    const request = tx.objectStore('meta').getAll();
    request.onsuccess = () => done(request.result.filter(item => item.key.startsWith('conflict_archive:')));
  });
}

export async function restoreConflictArchive(key, session = captureSession()) {
  if (hasNativeStorage()) return nativeStorage('restore', { key }, session);
  const archive = (await getConflictArchives(session)).find(item => item.key === key);
  if (!archive) throw new Error('Arşiv bulunamadı.');
  const record = archive.value;
  const id = crypto.randomUUID();
  const name = record.name + ' (Kurtarıldı)';
  return saveLocalCharacter({ ...record, id, server_id: id, remote_id: null,
    revision: 0, is_deleted: false, name,
    data: { ...record.data, id, server_id: id, name },
  }, true, session);
}

export function resolveSyncConflict(id, operationId, localRevision, choice, session = captureSession()) {
  if (hasNativeStorage()) return nativeStorage('resolve', { id, operationId, localRevision, choice }, session);
  if (!['local', 'server'].includes(choice)) throw new Error('Geçersiz çözüm seçimi');
  return transaction(session, ['characters', 'meta'], 'readwrite', (tx, done) => {
    const store = tx.objectStore('characters');
    const request = store.get(id);
    request.onsuccess = () => {
      const record = request.result;
      if (record?.conflict?.operation_id !== operationId || record.local_revision !== localRevision) {
        tx.abort(); return;
      }
      // Preserve both copies before an explicit user decision replaces anything.
      tx.objectStore('meta').put({ key: 'conflict_archive:' + crypto.randomUUID(), value: record });
      const remote = record.conflict.server_character;
      if (choice === 'local') store.put({ ...record, revision: remote?.revision || 0,
        conflict: null, pending_operation: null, is_dirty: true, local_revision: crypto.randomUUID() });
      else if (remote) store.put(fromRemote(remote));
      else store.put({ ...record, conflict: null, pending_operation: null, is_dirty: false, is_deleted: true });
      done(true);
    };
  });
}

export function applySyncResponse(sent, response, session = captureSession()) {
  const updates = response.updated_characters || [];
  const deleted = response.deleted_server_ids || [];
  if (!Array.isArray(updates) || !Array.isArray(deleted) || updates.some(item => !item.server_id)) {
    throw new Error('Geçersiz senkronizasyon yanıtı');
  }
  const snapshots = new Map(sent.map(item => [String(item.server_id), item]));
  return transaction(session, ['characters', 'meta'], 'readwrite', (tx, done) => {
    const store = tx.objectStore('characters');
    const process = (serverId, remote) => {
      const id = String(serverId);
      const request = store.get(id);
      request.onsuccess = () => {
        const local = request.result;
        const snapshot = snapshots.get(id);
        if (local?.is_dirty && (!snapshot || local.local_revision !== snapshot.local_revision)) return;
        if (!remote) store.delete(id);
        else store.put({
          ...remote, id, server_id: id, remote_id: typeof remote.id === 'number' ? remote.id : null,
          is_dirty: false, is_deleted: false,
          local_revision: crypto.randomUUID(),
        });
      };
    };
    for (const item of updates) process(item.server_id, item);
    for (const id of deleted) process(id, null);
    if (response.synced_at) tx.objectStore('meta').put({
      key: 'last_sync_timestamp', value: response.synced_at,
    });
    done(true);
  });
}
