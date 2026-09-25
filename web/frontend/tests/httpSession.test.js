import { beforeEach, test } from 'node:test';
import assert from 'node:assert/strict';
import axios from 'axios';
import { installSessionInterceptors } from '../src/utils/httpSession.js';
import { captureSession, rotateSession } from '../src/utils/sessionScope.js';

const values = new Map();
globalThis.localStorage = {
  getItem: key => values.get(key) ?? null,
  setItem: (key, value) => values.set(key, String(value)),
  removeItem: key => values.delete(key),
};
function login(name) {
  localStorage.setItem('token', `${name}-token`);
  localStorage.setItem('username', name);
  rotateSession();
}
const ok = config => ({ status: 200, data: {}, headers: {}, config });
const unauthorized = config => new axios.AxiosError(
  'Unauthorized', 'ERR_BAD_REQUEST', config, null,
  { status: 401, data: {}, headers: {}, config },
);
beforeEach(() => { values.clear(); });

test('request sends captured JWT without changing explicit authorization', async () => {
  login('alice');
  const session = captureSession();
  const client = axios.create({ adapter: async config => {
    assert.equal(config.headers.get('Authorization'), 'Bearer alice-token');
    assert.equal(config.sessionScope.key, session.key);
    return ok(config);
  } });
  installSessionInterceptors(client);
  await client.post('/api/sync/v2', {}, {
    sessionScope: session, headers: { Authorization: 'Bearer alice-token' },
  });
});

test('old captured request is rejected before adapter, even after same-account login', async () => {
  login('alice');
  const session = captureSession();
  login('alice');
  let sent = false;
  const client = axios.create({ adapter: async config => { sent = true; return ok(config); } });
  installSessionInterceptors(client);
  await assert.rejects(client.post('/api/sync/v2', {}, { sessionScope: session }), /Oturum değişti/);
  assert.equal(sent, false);
});

test('different explicit JWT is rejected, not silently replaced with current account', async () => {
  login('bob');
  let sent = false;
  const client = axios.create({ adapter: async config => { sent = true; return ok(config); } });
  installSessionInterceptors(client);
  await assert.rejects(client.post('/api/sync/v2', {}, {
    headers: { Authorization: 'Bearer alice-token' },
  }), /gönderilmedi/);
  assert.equal(sent, false);
});

for (const sameAccount of [false, true]) {
  test(`late 401 cannot erase or warn a new ${sameAccount ? 'same-account' : 'different-account'} session`, async () => {
    login('alice');
    let rejectResponse;
    let notices = 0;
    const client = axios.create({ adapter: config => new Promise((resolve, reject) => {
      rejectResponse = () => reject(unauthorized(config));
    }) });
    installSessionInterceptors(client, () => { notices++; });
    const pending = client.get('/api/characters');
    login(sameAccount ? 'alice' : 'bob');
    const current = captureSession();
    rejectResponse();
    await assert.rejects(pending, /Oturum değişti/);
    assert.equal(captureSession().key, current.key);
    assert.equal(notices, 0);
  });
}

test('late successful response is rejected instead of reaching new account UI', async () => {
  login('alice');
  let respond;
  const client = axios.create({ adapter: config => new Promise(resolve => {
    respond = () => resolve(ok(config));
  }) });
  installSessionInterceptors(client);
  const pending = client.get('/api/characters');
  login('bob');
  respond();
  await assert.rejects(pending, /Oturum değişti/);
});

test('current 401 reports reauthentication without removing offline account identity', async () => {
  login('alice');
  const session = captureSession();
  let notice;
  const client = axios.create({ adapter: async config => { throw unauthorized(config); } });
  installSessionInterceptors(client, value => { notice = value; });
  await assert.rejects(client.get('/api/characters'), /Unauthorized/);
  assert.equal(notice.key, session.key);
  assert.equal(captureSession().key, session.key);
});

test('guest requests send no synthetic JWT and 401 cannot invalidate guest access', async () => {
  localStorage.setItem('isGuest', 'true');
  let notices = 0;
  const client = axios.create({ adapter: async config => {
    assert.equal(config.headers.has('Authorization'), false);
    throw unauthorized(config);
  } });
  installSessionInterceptors(client, () => { notices++; });
  await assert.rejects(client.get('/api/rules'), /Unauthorized/);
  assert.equal(localStorage.getItem('isGuest'), 'true');
  assert.equal(notices, 0);
});

test('session is captured at invocation, before a subsequent microtask account change', async () => {
  login('alice');
  let sentToken;
  const client = axios.create({ adapter: async config => {
    sentToken = config.headers.get('Authorization');
    return ok(config);
  } });
  installSessionInterceptors(client);
  const pending = client.post('/api/characters', { name: 'Alice character' });
  login('bob');
  await assert.rejects(pending, /Oturum değişti/);
  assert.equal(sentToken, 'Bearer alice-token');
});
