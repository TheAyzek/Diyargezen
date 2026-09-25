import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'vite';
import React from 'react';
import { renderToString } from 'react-dom/server';

test('canonical level-up wizard renders the open HP step', async () => {
  const server = await createServer({ server: { middlewareMode: true }, appType: 'custom' });
  try {
    const { useCharacterStore } = await server.ssrLoadModule('/src/store/characterStore.js');
    useCharacterStore.setState({ name: 'Valeros', race: 'Human', class: 'Fighter', level: 1 });
    // React server rendering reads Zustand's server snapshot, not live state.
    Object.assign(useCharacterStore.getInitialState(), { name: 'Valeros', race: 'Human', class: 'Fighter', level: 1 });
    const { default: Wizard } = await server.ssrLoadModule('/src/components/sheets/LevelUpWizard.jsx');
    const html = renderToString(React.createElement(Wizard, { isOpen: true, onClose() {} }));
    assert.match(html, /Hit Die Roll/);
    assert.match(html, /Taslağı sakla ve kapat/);
  } finally { await server.close(); }
});
