import { assertSession } from './sessionScope.js';

export function hasNativeStorage() {
  return !!globalThis.__diyargezenNativeReady;
}

export async function nativeStorage(method, args, session) {
  assertSession(session);
  const bridge = await globalThis.__diyargezenNativeReady;
  assertSession(session);
  // A failed native call must never silently fall back to a second database.
  const result = await bridge({ method, args, session });
  assertSession(session);
  if (!result.ok) throw new Error(result.error || 'SQLite işlemi başarısız.');
  return result.value;
}
