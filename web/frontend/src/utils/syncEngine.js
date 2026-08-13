/**
 * Diyargezen Offline-First Background Synchronization Engine
 * 
 * Manages bi-directional synchronization between local IndexedDB storage
 * and the FastAPI server `/api/sync` endpoint using Last-Write-Wins (LWW).
 */

import axios from 'axios';
import {
  getDirtyCharacters,
  getLastSyncTimestamp,
  markCharactersSynced,
  saveLocalCharacter,
  deleteLocalCharacter
} from './offlineStorage';
import { useCharacterStore } from '../store/characterStore';

let isSyncing = false;
let syncListenersInitialized = false;

export async function triggerSync(token) {
  if (isSyncing) return;
  if (!navigator.onLine) {
    useCharacterStore.getState().setSyncStatus('offline_pending');
    return;
  }

  // Guest users without authentic token stay local
  if (!token || token === 'offline-guest-token') {
    useCharacterStore.getState().setSyncStatus('synced');
    return;
  }

  isSyncing = true;
  useCharacterStore.getState().setSyncStatus('syncing');

  try {
    const dirtyChars = await getDirtyCharacters();
    const lastSyncTs = await getLastSyncTimestamp();

    const payload = {
      last_sync_timestamp: lastSyncTs || null,
      dirty_characters: dirtyChars
    };

    const response = await axios.post('/api/sync', payload, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (response.data) {
      const { updated_characters, deleted_server_ids, synced_at } = response.data;

      // 1. Mark pushed dirty records as synced
      await markCharactersSynced(dirtyChars, synced_at);

      // 2. Save pulled server updates to local IndexedDB
      if (Array.isArray(updated_characters)) {
        for (const charItem of updated_characters) {
          await saveLocalCharacter(charItem, false);
        }
      }

      // 3. Process deleted tombstones
      if (Array.isArray(deleted_server_ids)) {
        for (const delId of deleted_server_ids) {
          await deleteLocalCharacter(delId);
        }
      }

      useCharacterStore.getState().setSyncStatus('synced');
    }
  } catch (err) {
    console.warn('Background sync warning:', err.message || err);
    useCharacterStore.getState().setSyncStatus('offline_pending');
  } finally {
    isSyncing = false;
  }
}

export function initSyncEngine(getTokenFn) {
  if (syncListenersInitialized) return;
  syncListenersInitialized = true;

  const handleOnline = () => {
    useCharacterStore.getState().setOnlineStatus(true);
    const token = getTokenFn ? getTokenFn() : null;
    if (token) {
      triggerSync(token);
    }
  };

  const handleOffline = () => {
    useCharacterStore.getState().setOnlineStatus(false);
    useCharacterStore.getState().setSyncStatus('offline_pending');
  };

  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);

  // Initial sync check if online
  if (navigator.onLine) {
    setTimeout(() => {
      const token = getTokenFn ? getTokenFn() : null;
      if (token) triggerSync(token);
    }, 1500);
  }
}
