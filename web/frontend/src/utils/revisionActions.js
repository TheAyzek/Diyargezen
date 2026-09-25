import axios from 'axios';
import { captureSession, assertSession } from './sessionScope.js';
import { getLocalCharacter, applySyncV2 } from './offlineStorage.js';

const runtimeKeys = new Set(['loading', 'recalcedData', 'warnings', 'isOnline', 'syncStatus', 'editorBaseline']);
export function editorFingerprint(state) {
  return JSON.stringify(Object.fromEntries(Object.entries(state).filter(
    ([key, value]) => !runtimeKeys.has(key) && typeof value !== 'function',
  )));
}

export async function requestRevisionAction(state, action, payload, getCurrent) {
  const session = captureSession();
  if (!session.authenticated || !state.server_id || !state.revision ||
      state.editorBaseline !== editorFingerprint(state)) {
    throw new Error('Önce karakteri kaydedip senkronize edin ve yeniden açın.');
  }
  const local = await getLocalCharacter(state.server_id, session);
  if (!local || local.is_dirty || local.conflict || local.pending_operation || local.revision !== state.revision) {
    throw new Error('Bekleyen değişiklik veya çakışma var; önce senkronizasyonu tamamlayın.');
  }
  assertSession(session);
  if (editorFingerprint(getCurrent()) !== state.editorBaseline) throw new Error('Karakter işlem öncesinde değişti.');
  const response = await axios.post(`/api/characters/${state.id}/${action}`, payload, {
    sessionScope: session,
    headers: { Authorization: `Bearer ${session.token}`, 'If-Match': String(state.revision) },
  });
  assertSession(session);
  const remote = response.data.character;
  if (!remote || remote.server_id !== state.server_id || !remote.revision) throw new Error('Geçersiz karakter yanıtı; yeniden senkronize edin.');
  await applySyncV2([], { protocol_version: 2, results: [], characters: [remote] }, session);
  if (editorFingerprint(getCurrent()) !== state.editorBaseline) {
    throw new Error('Sunucu işlemi tamamlandı; yeni yerel düzenlemeniz korunuyor. Kaydetmeden önce sürümleri karşılaştırın.');
  }
  return response;
}
