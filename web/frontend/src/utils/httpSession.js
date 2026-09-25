import { AxiosHeaders } from 'axios';
import { captureSession, assertSession } from './sessionScope.js';

// Install once at startup. Capturing synchronously matters: an account change
// in the next microtask must not retarget an already-created write request.
export function installSessionInterceptors(client, onUnauthorized = () => {}) {
  const requestId = client.interceptors.request.use(config => {
    const session = config.sessionScope || captureSession();
    assertSession(session);
    const headers = AxiosHeaders.from(config.headers);
    const expected = session.authenticated ? `Bearer ${session.token}` : null;
    const supplied = headers.get('Authorization');
    if (supplied && supplied !== expected) {
      throw new Error('İsteğin oturumu değişti; işlem gönderilmedi.');
    }
    if (expected) headers.set('Authorization', expected);
    else headers.delete('Authorization');
    config.headers = headers;
    config.sessionScope = session;
    return config;
  }, error => { throw error; }, { synchronous: true });

  const responseId = client.interceptors.response.use(response => {
    assertSession(response.config.sessionScope);
    return response;
  }, error => {
    const session = error.config?.sessionScope;
    if (session) {
      assertSession(session);
      if (session.authenticated && error.response?.status === 401) {
        // Keep the account partition and offline queue accessible. Only an
        // explicit logout may clear the local session; never a late response.
        onUnauthorized(session);
      }
    }
    return Promise.reject(error);
  });

  return () => {
    client.interceptors.request.eject(requestId);
    client.interceptors.response.eject(responseId);
  };
}
