// One PF1e payload for saving and calculation. Never rely on the last network
// response for editable fields: offline edits must survive save/reopen.
export function characterPayload(state) {
  const data = { ...state.recalcedData, system: 'pf1e' };
  for (const key of ['name', 'level', 'race', 'class', 'alignment', 'gender', 'age', 'height', 'weight',
    'deity', 'homeland', 'hair', 'eyes', 'backstory', 'personality', 'allies', 'notes', 'portrait',
    'abilities', 'feats', 'traits', 'spells', 'equipment', 'companion', 'multiclass', 'archetype',
    'archetypes', 'variant_multiclass', 'gold', 'pointBuyBudget', 'hit_points', 'max_hp',
    'favored_class', 'secondary_favored_class', 'favored_class_bonuses', 'selections', 'override_history']) {
    if (['hit_points', 'max_hp'].includes(key) && state[key] == null) { delete data[key]; continue; }
    if (state[key] !== undefined) data[key] = state[key];
  }
  Object.assign(data, {
    skill_ranks: state.skills || {}, race_data: state.raceData || {}, class_data: state.classData || {},
    custom_modifiers: state.customModifiers || [], prepared_spells: state.preparedSpells || {},
    used_spell_slots: state.usedSpellSlots || {}, used_daily_resources: state.usedDailyResources || {},
    racial_ability_choice: state.racialAbilityChoice || 'strength',
    secondary_racial_ability_choice: state.secondaryRacialAbilityChoice || 'dexterity',
    selected_racial_traits: state.selectedRacialTraits || [],
    conditions: state.active_conditions || state.conditions || [],
    active_conditions: state.active_conditions || state.conditions || [],
  });
  return data;
}

export function normalizeCharacterRecord(record) {
  const data = record.data || record;
  return { ...record, name: record.name || data.name || 'İsimsiz Kahraman',
    system: 'pf1e', data: { ...data, skill_ranks: data.skill_ranks || data.skills || {},
      prepared_spells: data.prepared_spells || data.preparedSpells || {},
      used_spell_slots: data.used_spell_slots || data.usedSpellSlots || {},
    } };
}
