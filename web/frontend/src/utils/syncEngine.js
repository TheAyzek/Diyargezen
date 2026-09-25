import axios from 'axios';
import { getDirtyCharacters, prepareSyncOperations, applySyncV2 } from './offlineStorage.js';
import { captureSession, assertSession, isCurrentSession } from './sessionScope.js';
import { useCharacterStore } from '../store/characterStore.js';

const inFlight = new Map();
let syncListenersInitialized = false;

export function triggerSync(token) {
  const session = captureSession();
  if (!session.authenticated || token !== session.token) return Promise.resolve();
  if (inFlight.has(session.key)) return inFlight.get(session.key);
  const task = sync(session).finally(() => inFlight.delete(session.key));
  inFlight.set(session.key, task);
  return task;
}

async function sync(session) {
  const status = value => {
    if (isCurrentSession(session)) useCharacterStore.getState().setSyncStatus(value);
  };
  if (!navigator.onLine) { status('offline_pending'); return; }
  status('syncing');
  try {
    const operations = await prepareSyncOperations(session);
    assertSession(session);
    const response = await axios.post('/api/sync/v2', {
      operations,
    }, { sessionScope: session, headers: { Authorization: `Bearer ${session.token}` } });
    assertSession(session);
    await applySyncV2(operations, response.data, session);
    const pending = await getDirtyCharacters(session);
    status(pending.length ? 'offline_pending' : 'synced');
    if (isCurrentSession(session) && typeof window !== 'undefined') {
      window.dispatchEvent(new Event('diyargezen-sync-updated'));
    }
  } catch (error) {
    status('offline_pending');
    if (isCurrentSession(session)) console.warn('Background sync:', error.message);
  }
}

export function initSyncEngine(getTokenFn) {
  if (syncListenersInitialized) return;
  syncListenersInitialized = true;
  const run = () => triggerSync(getTokenFn?.());
  window.addEventListener('online', () => {
    useCharacterStore.getState().setOnlineStatus(true);
    run();
  });
  window.addEventListener('offline', () => {
    useCharacterStore.getState().setOnlineStatus(false);
  });
  window.addEventListener('storage', run);
  // Retry queued edits without requiring a connectivity toggle.
  setInterval(run, 15000);
  run();
}
