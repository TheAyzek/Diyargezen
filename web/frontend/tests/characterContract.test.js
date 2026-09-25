import { test } from 'node:test';
import assert from 'node:assert/strict';
import axios from 'axios';
import { characterPayload, normalizeCharacterRecord } from '../src/utils/characterContract.js';
import { useCharacterStore } from '../src/store/characterStore.js';

test('local level-up uses canonical choice fields and records GM reason', async t => {
  const recalculate = useCharacterStore.getState().recalculate;
  t.after(() => useCharacterStore.setState({ recalculate }));
  useCharacterStore.setState({ recalculate: () => {}, id: null, level: 1,
    abilities: { constitution: 14, strength: 16 }, hit_points: 12, max_hp: 12,
    skills: { Climb: 1 }, feats: [], spells: [], traits: [], override_history: [] });
  assert.equal(await useCharacterStore.getState().applyLevelUp({ hp_added: 6, favored_class_bonus: 'hp',
    skill_ranks: { Climb: 1 }, feats: ['Power Attack'], traits_learned: ['Custom'],
    is_overridden: true, override_reason: 'Campaign exception' }), true);
  const state = useCharacterStore.getState();
  assert.equal(state.level, 2);
  assert.equal(state.max_hp, 21);
  assert.equal(state.skills.Climb, 2);
  assert.deepEqual(state.feats, ['Power Attack']);
  assert.equal(state.override_history[0].reason, 'Campaign exception');
});

test('offline save takes current editable values, not stale calculated data', () => {
  const data = characterPayload({ recalcedData: { feats: ['Old'], spells: ['Old'], notes: 'Old' },
    name: 'Hero', feats: [{ isim: 'Dodge', is_overridden: true, override_reason: 'GM' }],
    spells: [{ isim: 'Light' }], notes: 'Offline edit', skills: { Stealth: 2 },
    preparedSpells: { 0: ['Light'] }, customModifiers: [{ stat: 'ac', value: 2 }], hit_points: null });
  assert.equal(data.notes, 'Offline edit');
  assert.equal(data.feats[0].override_reason, 'GM');
  assert.equal(data.spells[0].isim, 'Light');
  assert.deepEqual(data.skill_ranks, { Stealth: 2 });
  assert.equal(data.hit_points, undefined);
});

test('preset and saved record preserve the same race, class and skills', t => {
  const oldPost = axios.post;
  const oldState = useCharacterStore.getState();
  axios.post = () => new Promise(() => {});
  t.after(() => { axios.post = oldPost; useCharacterStore.setState(oldState, true); });
  const preset = { name: 'Valeros', system: 'pf1e', level: 3, race: 'Human', class: 'Fighter',
    abilities: { strength: 16 }, skills: { Climb: 3 }, spells: [], notes: 'Test', gold: 40 };
  useCharacterStore.getState().loadPresetCharacter(preset);
  assert.equal(useCharacterStore.getState().class, 'Fighter');
  assert.equal(useCharacterStore.getState().level, 3);
  const saved = characterPayload(useCharacterStore.getState());
  useCharacterStore.getState().initCharacter('pf1e', { id: 12, name: preset.name, system: 'pf1e', data: saved });
  assert.equal(useCharacterStore.getState().race, 'Human');
  assert.deepEqual(useCharacterStore.getState().skills, { Climb: 3 });
  assert.equal(useCharacterStore.getState().gold, 40);
});

test('switching characters clears spell resources, conditions and GM decisions', t => {
  const oldPost = axios.post;
  const oldState = useCharacterStore.getState();
  axios.post = () => new Promise(() => {});
  t.after(() => { axios.post = oldPost; useCharacterStore.setState(oldState, true); });
  useCharacterStore.getState().initCharacter('pf1e', normalizeCharacterRecord({ name: 'Mage',
    spells: ['Light'], used_spell_slots: { 1: 2 }, active_conditions: ['sickened'], override_history: [{ reason: 'GM' }] }));
  useCharacterStore.getState().initCharacter('pf1e');
  const current = useCharacterStore.getState();
  assert.deepEqual(current.spells, []);
  assert.deepEqual(current.active_conditions, []);
  assert.deepEqual(current.override_history, []);
  assert.deepEqual(current.usedSpellSlots, {});
});
