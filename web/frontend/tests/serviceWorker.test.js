import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

test('HTTP cache never intercepts private APIs or foreign origins', async () => {
  const handlers = {};
  const self = { location: { origin: 'https://diyargezen.test' },
    addEventListener: (event, callback) => { handlers[event] = callback; }, skipWaiting() {}, clients: { claim() {} } };
  vm.runInNewContext(await readFile(new URL('../public/sw.js', import.meta.url), 'utf8'), { self, URL });
  for (const url of ['/api/characters/1', '/api/auth/me', '/api/sync/v2', '/api/health', 'https://other.test/asset.png']) {
    handlers.fetch({ request: { url: new URL(url, self.location.origin).href, method: 'GET' },
      respondWith: () => assert.fail('Private response must never use shared HTTP cache') });
  }
});
