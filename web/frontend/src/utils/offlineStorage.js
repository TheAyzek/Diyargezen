/**
 * Diyargezen IndexedDB Offline Storage Engine
 * 
 * Manages local persistent storage for character sheets, dirty state tracking,
 * and sync metadata when operating offline or with intermittent connectivity.
 */

const DB_NAME = 'DiyargezenDB';
const DB_VERSION = 1;

let dbInstance = null;

export function openOfflineDB() {
  return new Promise((resolve, reject) => {
    if (dbInstance) {
      return resolve(dbInstance);
    }

    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      // Characters Store
      if (!db.objectStoreNames.contains('characters')) {
        const charStore = db.createObjectStore('characters', { keyPath: 'id' });
        charStore.createIndex('is_dirty', 'is_dirty', { unique: false });
        charStore.createIndex('updated_at', 'updated_at', { unique: false });
      }

      // Metadata Store (last_sync_timestamp, user_preferences, etc.)
      if (!db.objectStoreNames.contains('meta')) {
        db.createObjectStore('meta', { keyPath: 'key' });
      }
    };

    request.onsuccess = (event) => {
      dbInstance = event.target.result;
      resolve(dbInstance);
    };

    request.onerror = (event) => {
      console.error('IndexedDB open error:', event.target.error);
      reject(event.target.error);
    };
  });
}

export async function saveLocalCharacter(character, isDirty = true) {
  try {
    const db = await openOfflineDB();
    const tx = db.transaction(['characters'], 'readwrite');
    const store = tx.objectStore('characters');

    const now = new Date().toISOString();
    const record = {
      id: character.id || character.server_id || `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      server_id: character.server_id || character.id || null,
      name: character.name || character.isim || 'İsimsiz Kahraman',
      system: (character.system || 'pathfinder1e').toLowerCase(),
      data: character.data || character,
      is_dirty: isDirty,
      is_deleted: character.is_deleted || False || false,
      created_at: character.created_at || now,
      updated_at: character.updated_at || now
    };

    return new Promise((resolve, reject) => {
      const req = store.put(record);
      req.onsuccess = () => resolve(record);
      req.onerror = (e) => reject(e.target.error);
    });
  } catch (err) {
    console.error('Error saving character to IndexedDB:', err);
    throw err;
  }
}

export async function getAllLocalCharacters() {
  try {
    const db = await openOfflineDB();
    const tx = db.transaction(['characters'], 'readonly');
    const store = tx.objectStore('characters');

    return new Promise((resolve, reject) => {
      const req = store.getAll();
      req.onsuccess = () => {
        const results = req.result || [];
        // Filter out soft-deleted tombstone records
        resolve(results.filter(c => !c.is_deleted));
      };
      req.onerror = (e) => reject(e.target.error);
    });
  } catch (err) {
    console.error('Error fetching local characters from IndexedDB:', err);
    return [];
  }
}

export async function getDirtyCharacters() {
  try {
    const db = await openOfflineDB();
    const tx = db.transaction(['characters'], 'readonly');
    const store = tx.objectStore('characters');
    const index = store.index('is_dirty');

    return new Promise((resolve, reject) => {
      const req = index.getAll(IDBKeyRange.only(1)); // 1 or true
      req.onsuccess = () => {
        const dirtyItems = req.result || [];
        resolve(dirtyItems.map(item => ({
          server_id: item.server_id || item.id,
          name: item.name,
          system: item.system,
          data: item.data,
          updated_at: item.updated_at,
          created_at: item.created_at,
          is_deleted: item.is_deleted || false
        })));
      };
      req.onerror = () => {
        // Fallback: manually filter all records
        const allReq = store.getAll();
        allReq.onsuccess = () => {
          const all = allReq.result || [];
          resolve(all.filter(c => c.is_dirty).map(item => ({
            server_id: item.server_id || item.id,
            name: item.name,
            system: item.system,
            data: item.data,
            updated_at: item.updated_at,
            created_at: item.created_at,
            is_deleted: item.is_deleted || false
          })));
        };
        allReq.onerror = (e) => reject(e.target.error);
      };
    });
  } catch (err) {
    console.error('Error fetching dirty characters from IndexedDB:', err);
    return [];
  }
}

export async function markCharactersSynced(syncedItems, lastSyncTimestamp) {
  try {
    const db = await openOfflineDB();
    const tx = db.transaction(['characters', 'meta'], 'readwrite');
    const charStore = tx.objectStore('characters');
    const metaStore = tx.objectStore('meta');

    if (Array.isArray(syncedItems)) {
      syncedItems.forEach(item => {
        const record = {
          id: item.server_id || item.id,
          server_id: item.server_id || item.id,
          name: item.name,
          system: item.system,
          data: item.data || item,
          is_dirty: false,
          is_deleted: item.is_deleted || false,
          created_at: item.created_at,
          updated_at: item.updated_at
        };
        charStore.put(record);
      });
    }

    if (lastSyncTimestamp) {
      metaStore.put({ key: 'last_sync_timestamp', value: lastSyncTimestamp });
    }

    return new Promise((resolve) => {
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => resolve(false);
    });
  } catch (err) {
    console.error('Error marking characters as synced in IndexedDB:', err);
    return false;
  }
}

export async function getLastSyncTimestamp() {
  try {
    const db = await openOfflineDB();
    const tx = db.transaction(['meta'], 'readonly');
    const store = tx.objectStore('meta');

    return new Promise((resolve) => {
      const req = store.get('last_sync_timestamp');
      req.onsuccess = () => resolve(req.result ? req.result.value : null);
      req.onerror = () => resolve(null);
    });
  } catch (err) {
    return null;
  }
}

export async function deleteLocalCharacter(id) {
  try {
    const db = await openOfflineDB();
    const tx = db.transaction(['characters'], 'readwrite');
    const store = tx.objectStore('characters');

    return new Promise((resolve, reject) => {
      const req = store.delete(id);
      req.onsuccess = () => resolve(true);
      req.onerror = (e) => reject(e.target.error);
    });
  } catch (err) {
    console.error('Error deleting local character from IndexedDB:', err);
    return false;
  }
}
