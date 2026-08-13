import { create } from 'zustand';
import axios from 'axios';

// ---------------------------------------------------------------------------
// PF1e Feat Slot Calculator
// ---------------------------------------------------------------------------
// PF1e gives 1 feat at every odd level: 1,3,5,7,9,11,13,15,17,19
// Plus class bonus feats at level 1 (and beyond for Fighter etc.)
// Plus +1 if Human race
export function computeFeatSlots(className = '', race = '', level = 1, vmcClass = '') {
  const lvl = parseInt(level) || 1;
  const cls = (className || '').toLowerCase();
  const raceL = (race || '').toLowerCase();

  // Normal feats: 1 at level 1, then every odd level after
  let normalFeats = Math.ceil(lvl / 2);

  // Variant Multiclassing (VMC) deducts general feats at levels 3, 7, 11, 15, 19
  if (vmcClass) {
    const vmcDeductions = [3, 7, 11, 15, 19].filter(l => lvl >= l).length;
    normalFeats = Math.max(1, normalFeats - vmcDeductions);
  }

  // Human racial bonus feat (+1 at level 1)
  const humanBonus = raceL.includes('human') && !raceL.includes('half') ? 1 : 0;

  // Class bonus feats at level 1
  let classBonus = 0;
  if (cls.includes('fighter')) {
    // Fighter: bonus feat at 1, then every even level
    classBonus = 1 + Math.floor(lvl / 2);
  } else if (cls.includes('wizard')) {
    classBonus = 1; // Scribe Scroll at level 1 (always)
  } else if (cls.includes('monk')) {
    // Monk: 2 bonus feats at level 1 (Improved Unarmed Strike + one style)
    classBonus = cls.includes('unchained') ? 1 : 2;
  } else if (cls.includes('gunslinger')) {
    classBonus = 1; // Gunsmithing at level 1
  } else if (cls.includes('cavalier')) {
    classBonus = 1; // Order's Challenge
  } else if (cls.includes('magus')) {
    classBonus = 0; // Arcana, not technically a feat slot
  }

  return normalFeats + humanBonus + classBonus;
}

export const useCharacterStore = create((set, get) => ({
  id: null,
  name: 'İsimsiz Kahraman',
  system: '',
  level: 1,
  pl_value: 10,
  race: '',
  class: '',
  background: '',
  // PF1e feats stored as array of entity objects
  feats: [],
  spells: [],
  abilities: {},
  skills: {},
  advantages: [],
  powers: {},
  equipment: [],
  customModifiers: [],
  raceData: {},
  classData: {},
  archetype: '',
  portrait: '',
  companion: null,
  multiclass: {}, // e.g. {"Fighter": 3, "Rogue": 2}
  variant_multiclass: '',
  pointBuyBudget: 20,
  
  // Custom defenses state for M&M
  defenses: {
    dodge: 0,
    parry: 0,
    fortitude: 0,
    toughness: 0,
    will: 0
  },

  // Derived & validation states from backend
  recalcedData: {},
  warnings: [],
  loading: false,

  alignment: '',
  gender: '',
  age: '',
  height: '',
  weight: '',
  deity: '',
  homeland: '',
  hair: '',
  eyes: '',
  backstory: '',
  personality: '',
  allies: '',
  notes: '',

  traits: [],
  gold: 150,

  deductGold: (amount) => {
    set(state => ({
      gold: Math.max(0, (state.gold || 0) - amount)
    }));
    get().recalculate();
  },

  // Spell slot tracking & rest state
  usedSpellSlots: {},
  usedDailyResources: {},
  preparedSpells: {},

  setPreparedSpell: (spellLevel, slotIndex, spellName) => {
    set(state => {
      const levelSlots = [...(state.preparedSpells[spellLevel] || [])];
      levelSlots[slotIndex] = { name: spellName, cast: false };
      return {
        preparedSpells: {
          ...state.preparedSpells,
          [spellLevel]: levelSlots
        }
      };
    });
    get().recalculate();
  },

  togglePreparedSpellCast: (spellLevel, slotIndex) => {
    set(state => {
      const levelSlots = [...(state.preparedSpells[spellLevel] || [])];
      if (levelSlots[slotIndex]) {
        levelSlots[slotIndex] = {
          ...levelSlots[slotIndex],
          cast: !levelSlots[slotIndex].cast
        };
      }
      return {
        preparedSpells: {
          ...state.preparedSpells,
          [spellLevel]: levelSlots
        }
      };
    });
    get().recalculate();
  },

  toggleSpellSlotUsed: (spellLevel, maxSlots) => {
    set(state => {
      const currentUsed = state.usedSpellSlots[spellLevel] || 0;
      const nextUsed = currentUsed >= maxSlots ? 0 : currentUsed + 1;
      return {
        usedSpellSlots: {
          ...state.usedSpellSlots,
          [spellLevel]: nextUsed
        }
      };
    });
    get().recalculate();
  },

  restCharacter: () => {
    set(state => {
      const resetPrepared = {};
      Object.entries(state.preparedSpells || {}).forEach(([lvl, slots]) => {
        resetPrepared[lvl] = (slots || []).map(s => s ? { ...s, cast: false } : s);
      });
      return {
        usedSpellSlots: {},
        usedDailyResources: {},
        preparedSpells: resetPrepared
      };
    });
    get().recalculate();
  },

  loadPresetCharacter: (preset) => {
    set({
      id: null,
      name: preset.name || 'İsimsiz Kahraman',
      system: 'pf1e',
      level: 1,
      race: preset.race || 'Human',
      class: preset.class || 'Fighter',
      alignment: preset.alignment || 'Neutral Good',
      gender: preset.gender || '',
      age: preset.age || '25',
      height: preset.height || '',
      weight: preset.weight || '',
      deity: preset.deity || '',
      homeland: preset.homeland || '',
      hair: preset.hair || '',
      eyes: preset.eyes || '',
      abilities: preset.abilities || { strength: 10, dexterity: 10, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 },
      skills: preset.skills || {},
      feats: preset.feats || [],
      traits: preset.traits || [],
      equipment: preset.equipment || [],
      spells: preset.spells || [],
      backstory: preset.backstory || '',
      personality: preset.personality || '',
      allies: preset.allies || '',
      notes: preset.notes || '',
      portrait: preset.portrait || '',
      usedSpellSlots: {},
      preparedSpells: {},
      recalcedData: {},
      warnings: []
    });
    get().recalculate();
  },

  // Offline-First & Sync state
  isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
  syncStatus: typeof navigator !== 'undefined' && !navigator.onLine ? 'offline_pending' : 'synced',

  setOnlineStatus: (status) => set({
    isOnline: status,
    syncStatus: status ? 'synced' : 'offline_pending'
  }),

  setSyncStatus: (status) => set({ syncStatus: status }),

  // Actions
  initCharacter: (system, char = null) => {
    const sys = system.toLowerCase();
    
    if (char) {
      // Map defenses title-case keys back to state if M&M
      const savedDefenses = char.data?.defenses || {};
      const defState = {
        dodge: savedDefenses.Dodge || savedDefenses.dodge || 0,
        parry: savedDefenses.Parry || savedDefenses.parry || 0,
        fortitude: savedDefenses.Fortitude || savedDefenses.fortitude || 0,
        toughness: savedDefenses.Toughness || savedDefenses.toughness || 0,
        will: savedDefenses.Will || savedDefenses.will || 0
      };

      let rawAbilities = char.data?.abilities || {};
      if (sys.includes('pf') || sys.includes('pathfinder') || sys.includes('dnd') || sys.includes('dragon')) {
        const coreKeys = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'];
        const cleanAbilities = {};
        coreKeys.forEach(k => {
          cleanAbilities[k] = rawAbilities[k] ?? (sys.includes('dnd') ? 8 : 10);
        });
        rawAbilities = cleanAbilities;
      }

      set({
        id: char.id,
        name: char.name,
        system: char.system.toLowerCase(),
        level: char.data?.level || 1,
        pl_value: char.data?.pl_value || 10,
        race: char.data?.race || '',
        class: char.data?.class || '',
        background: char.data?.background || '',
        alignment: char.data?.alignment || '',
        gender: char.data?.gender || '',
        age: char.data?.age || '',
        height: char.data?.height || '',
        weight: char.data?.weight || '',
        deity: char.data?.deity || '',
        homeland: char.data?.homeland || '',
        hair: char.data?.hair || '',
        eyes: char.data?.eyes || '',
        traits: char.data?.traits || [],
        // Migrate: if saved data has feat (string), convert; else use feats array
        feats: char.data?.feats || (char.data?.feat ? [{ isim: char.data.feat, sistem_verisi: {} }] : []),
        abilities: rawAbilities,
        skills: char.data?.skill_ranks || {},
        advantages: char.data?.advantages || [],
        powers: char.data?.powers || {},
        equipment: char.data?.equipment || [],
        customModifiers: char.data?.custom_modifiers || [],
        raceData: char.data?.race_data || {},
        classData: char.data?.class_data || {},
        archetype: char.data?.archetype || '',
        racialAbilityChoice: char.data?.racial_ability_choice || 'strength',
        secondaryRacialAbilityChoice: char.data?.secondary_racial_ability_choice || 'dexterity',
        selectedRacialTraits: char.data?.selected_racial_traits || [],
        portrait: char.data?.portrait || char.portrait || '',
        companion: char.data?.companion || null,
        backstory: char.data?.backstory || char.backstory || '',
        personality: char.data?.personality || char.personality || '',
        allies: char.data?.allies || char.allies || '',
        notes: char.data?.notes || char.notes || '',
        preparedSpells: char.data?.preparedSpells || char.preparedSpells || {},
        usedSpellSlots: char.data?.usedSpellSlots || {},
        defenses: defState,
        recalcedData: char.data || {},
        warnings: []
      });
    } else {
      // Defaults based on system
      const defaultAbilities = 
        sys.includes('dnd') ? { strength: 8, dexterity: 8, constitution: 8, intelligence: 8, wisdom: 8, charisma: 8 } :
        sys.includes('pf') ? { strength: 10, dexterity: 10, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 } :
        { strength: 0, stamina: 0, agility: 0, dexterity: 0, fighting: 0, intellect: 0, awareness: 0, presence: 0 };
        
      set({
        id: null,
        name: 'İsimsiz Kahraman',
        system: sys,
        level: 1,
        pl_value: 10,
        race: '',
        class: '',
        background: sys.includes('dnd') ? 'Acolyte' : '',
        alignment: 'TN',
        gender: '',
        age: '',
        height: '',
        weight: '',
        deity: '',
        homeland: '',
        hair: '',
        eyes: '',
        traits: [],
        feats: [],
        abilities: defaultAbilities,
        skills: {},
        advantages: [],
        powers: {},
        equipment: [],
        customModifiers: [],
        raceData: {},
        classData: {},
        archetype: sys.includes('mm') || sys.includes('mnm') ? 'Özel (Custom)' : '',
        racialAbilityChoice: 'strength',
        secondaryRacialAbilityChoice: 'dexterity',
        selectedRacialTraits: [],
        portrait: '',
        companion: null,
        defenses: { dodge: 0, parry: 0, fortitude: 0, toughness: 0, will: 0 },
        recalcedData: {},
        warnings: []
      });
    }
    get().recalculate();
  },

  toggleRacialTrait: (traitName) => {
    let traitWarning = null;
    set(state => {
      const current = state.selectedRacialTraits || [];
      const exists = current.includes(traitName);
      if (exists) {
        return { selectedRacialTraits: current.filter(t => t !== traitName) };
      }

      // Check replacement conflict against currently selected alternate traits
      const sv = state.raceData?.sistem_verisi || state.raceData || {};
      const altTraits = Array.isArray(sv.alternate_traits) ? sv.alternate_traits : [];
      const targetObj = altTraits.find(t => (typeof t === 'object' && t ? t.name : t) === traitName);
      const targetReplaces = (targetObj && Array.isArray(targetObj.replaces)) ? targetObj.replaces : [];

      if (targetReplaces.length > 0) {
        const currentlyReplaced = new Map();
        current.forEach(selName => {
          const selObj = altTraits.find(t => (typeof t === 'object' && t ? t.name : t) === selName);
          if (selObj && Array.isArray(selObj.replaces)) {
            selObj.replaces.forEach(rep => {
              if (rep) currentlyReplaced.set(rep.toLowerCase().trim(), { traitName: selName, origReplaced: rep });
            });
          }
        });

        for (const rep of targetReplaces) {
          const repNorm = (rep || '').toLowerCase().trim();
          if (currentlyReplaced.has(repNorm)) {
            const found = currentlyReplaced.get(repNorm);
            traitWarning = `Alternatif özellik çakışması: '${traitName}' ve '${found.traitName}' ikisi de '${found.origReplaced}' varsayılan özelliğinin yerini alamaz.`;
            break;
          }
        }
      }

      if (traitWarning && !state.is_overridden && !state.gm_override) {
        const existingWarnings = state.warnings || [];
        return {
          warnings: [...existingWarnings.filter(w => !w.includes('Alternatif özellik çakışması')), traitWarning]
        };
      }

      return { selectedRacialTraits: [...current, traitName] };
    });
    get().recalculate();
    return traitWarning ? { error: true, message: traitWarning } : { success: true };
  },

  applyLevelUp: async (levelUpData) => {
    const state = get();
    const existingSpells = state.spells || [];
    const incomingSpells = levelUpData.spells_learned || levelUpData.spells || [];

    const spellMap = new Map();
    existingSpells.forEach(s => {
      const name = typeof s === 'object' ? (s.isim || s.name) : s;
      if (name) spellMap.set(name, s);
    });
    incomingSpells.forEach(s => {
      const name = typeof s === 'object' ? (s.isim || s.name) : s;
      if (name && !spellMap.has(name)) spellMap.set(name, s);
    });

    const mergedSpells = Array.from(spellMap.values());

    if (state.id) {
      const payload = {
        class_name: levelUpData.class_name || state.class || 'Fighter',
        hp_added: levelUpData.hp_added || levelUpData.hpGained || 6,
        favored_class_bonus: levelUpData.favored_class_bonus || levelUpData.fcbChoice || 'hp',
        skill_ranks: levelUpData.skill_ranks || levelUpData.skillRanksGained || {},
        feats: levelUpData.feats || (levelUpData.newFeat ? [levelUpData.newFeat.name || levelUpData.newFeat.isim || levelUpData.newFeat] : []),
        ability_increase: levelUpData.ability_increase || levelUpData.abilityIncrease || null,
        spells_learned: mergedSpells,
        spells: mergedSpells
      };
      return await get().levelUp(payload.class_name, payload);
    }

    const { newLevel, hpGained, skillRanksGained, newFeat, abilityIncrease, fcbChoice } = levelUpData;
    set(state => {
      const nextSkills = { ...(state.skills || {}) };
      if (skillRanksGained && typeof skillRanksGained === 'object') {
        Object.entries(skillRanksGained).forEach(([sk, addRanks]) => {
          nextSkills[sk] = (parseInt(nextSkills[sk]) || 0) + (parseInt(addRanks) || 0);
        });
      }

      const nextFeats = [...(state.feats || [])];
      if (newFeat) {
        nextFeats.push(newFeat);
      }

      const nextAbilities = { ...(state.abilities || {}) };
      if (abilityIncrease) {
        const abKey = abilityIncrease.toLowerCase();
        nextAbilities[abKey] = (parseInt(nextAbilities[abKey]) || 10) + 1;
      }

      const fcbHp = fcbChoice === 'hp' ? 1 : 0;
      const currentHp = state.recalcedData?.hit_points || 10;

      return {
        level: newLevel || (parseInt(state.level) || 1) + 1,
        skills: nextSkills,
        feats: nextFeats,
        abilities: nextAbilities,
        spells: mergedSpells,
        hit_points: currentHp + (hpGained || 0) + fcbHp
      };
    });
    get().recalculate();
  },

  updateField: (field, value) => {
    set({ [field]: value });
    get().recalculate();
  },

  updateCompanion: (companionData) => {
    set(state => ({
      companion: companionData ? {
        ...(state.companion || {}),
        ...companionData
      } : null
    }));
    get().recalculate();
  },

  resetCompanion: () => {
    set({ companion: null });
    get().recalculate();
  },

  updateAbility: (ability, value) => {
    set(state => ({
      abilities: {
        ...state.abilities,
        [ability]: value
      }
    }));
    get().recalculate();
  },

  updateDefense: (defense, value) => {
    set(state => ({
      defenses: {
        ...state.defenses,
        [defense]: value
      }
    }));
    get().recalculate();
  },

  updateSkillRank: (skill, value) => {
    set(state => ({
      skills: {
        ...state.skills,
        [skill]: value
      }
    }));
    get().recalculate();
  },

  addEquipment: (item) => {
    set(state => ({
      equipment: [...state.equipment, item]
    }));
    get().recalculate();
  },

  removeEquipment: (index) => {
    set(state => ({
      equipment: state.equipment.filter((_, i) => i !== index)
    }));
    get().recalculate();
  },

  addCustomModifier: (modifier) => {
    set(state => ({ customModifiers: [...state.customModifiers, modifier] }));
    get().recalculate();
  },

  removeCustomModifier: (index) => {
    set(state => ({ customModifiers: state.customModifiers.filter((_, itemIndex) => itemIndex !== index) }));
    get().recalculate();
  },

  // PF1e Feat Actions — enforces slot count based on class+level+race
  addFeat: (featEntity) => {
    const state = get();
    const currentFeats = state.feats || [];
    const maxFeats = computeFeatSlots(state.class, state.race, parseInt(state.level) || 1);

    const featObj = typeof featEntity === 'string' ? { isim: featEntity } : featEntity;
    const featName = featObj.isim || featObj.name || featEntity;

    if (currentFeats.length >= maxFeats) {
      return { error: 'max_feats', message: `Bu seviyede en fazla ${maxFeats} feat seçebilirsiniz.` };
    }
    if (currentFeats.find(f => (f.isim || f.name || f) === featName)) {
      return { error: 'duplicate', message: 'Bu feat zaten seçili.' };
    }
    set(state => ({ feats: [...(state.feats || []), featObj] }));
    get().recalculate();
    return { error: null };
  },

  removeFeat: (featName) => {
    set(state => ({ feats: (state.feats || []).filter(f => f.isim !== featName) }));
    get().recalculate();
  },

  // PF1e Trait Actions — enforces: max 2 traits, no 2 from same category
  addTrait: (traitEntity) => {
    const MAX_TRAITS = 2;
    const state = get();
    const currentTraits = state.traits || [];
    const traitCategory = traitEntity.sistem_verisi?.trait_category || 'Unknown';

    if (currentTraits.length >= MAX_TRAITS) {
      return { error: 'max_traits', message: `Maksimum ${MAX_TRAITS} trait seçebilirsiniz.` };
    }
    const sameCategory = currentTraits.find(
      t => (t.sistem_verisi?.trait_category || 'Unknown') === traitCategory
    );
    if (sameCategory) {
      return { error: 'same_category', message: `"${traitCategory}" kategorisinden zaten bir trait seçtiniz.` };
    }
    if (currentTraits.find(t => t.isim === traitEntity.isim)) {
      return { error: 'duplicate', message: 'Bu trait zaten seçili.' };
    }

    set(state => ({ traits: [...(state.traits || []), traitEntity] }));
    get().recalculate();
    return { error: null };
  },

  removeTrait: (traitName) => {
    set(state => ({
      traits: (state.traits || []).filter(t => t.isim !== traitName)
    }));
    get().recalculate();
  },

  // PF1e Spell Actions
  addSpell: (spellObj) => {
    const state = get();
    const currentSpells = state.spells || [];
    const name = spellObj.isim || spellObj.name;

    if (currentSpells.some(s => (s.isim || s.name || s) === name)) {
      return { error: 'duplicate', message: 'Bu büyü zaten seçili.' };
    }

    set(state => ({ spells: [...(state.spells || []), spellObj] }));
    get().recalculate();
    return { error: null };
  },

  removeSpell: (spellName) => {
    set(state => ({
      spells: (state.spells || []).filter(s => (s.isim || s.name || s) !== spellName)
    }));
    get().recalculate();
  },

  toggleDndSkill: (skill) => {
    set(state => {
      const currentProfs = state.recalcedData.proficient_skills || [];
      const newProfs = currentProfs.includes(skill)
        ? currentProfs.filter(s => s !== skill)
        : [...currentProfs, skill];
      return {
        recalcedData: {
          ...state.recalcedData,
          proficient_skills: newProfs
        }
      };
    });
    get().recalculate();
  },

  recalculate: () => {
    const state = get();
    
    // Calculate remaining points dynamically for M&M
    let remainingPoints = state.pl_value * 15;
    if (state.system.includes('mm') || state.system.includes('mnm')) {
      let spent = 0;
      Object.entries(state.abilities).forEach(([k, v]) => {
        if (k !== 'power_points') spent += v * 2;
      });
      
      const mmDefenses = state.defenses || { dodge: 0, parry: 0, fortitude: 0, toughness: 0, will: 0 };
      Object.values(mmDefenses).forEach(v => spent += parseInt(v) || 0);
      
      let skillRanks = 0;
      Object.values(state.skills).forEach(v => skillRanks += parseInt(v) || 0);
      spent += Math.ceil(skillRanks / 2);
      
      spent += state.advantages.length;
      Object.values(state.powers).forEach(p => spent += p.cost || 0);
      
      remainingPoints = (state.pl_value * 15) - spent;
    }

    // Map client system keys to backend keys
    let backendSystem = state.system;
    if (state.system.includes('dnd')) backendSystem = 'dnd5e';
    else if (state.system.includes('pf') || state.system.includes('pathfinder')) backendSystem = 'pf1e';
    else backendSystem = 'mnm';

    // Build payload matching character_service.py expected payload
    const payload = {
      system: backendSystem,
      name: state.name,
      level: parseInt(state.level),
      race: state.race,
      class: state.class,
      background: state.background,
      abilities: {
        ...state.abilities,
        power_points: remainingPoints
      },
      skill_ranks: state.skills,
      advantages: state.advantages,
      powers: state.powers,
      defenses: (state.system.includes('mm') || state.system.includes('mnm')) ? {
        Dodge: state.defenses.dodge || 0,
        Parry: state.defenses.parry || 0,
        Fortitude: state.defenses.fortitude || 0,
        Toughness: state.defenses.toughness || 0,
        Will: state.defenses.will || 0
      } : undefined,
      equipment: state.equipment,
      custom_modifiers: state.customModifiers,
      multiclass: state.multiclass,
      variant_multiclass: state.variant_multiclass || state.variantMulticlass,
      feats: (state.feats || []).map(f => f.isim || f),
      traits: (state.traits || []).map(t => ({ isim: t.isim, kategori: t.sistem_verisi?.trait_category })),
      proficient_skills: state.recalcedData.proficient_skills || [],
      archetype: state.archetype,
      racial_ability_choice: state.racialAbilityChoice || 'strength',
      secondary_racial_ability_choice: state.secondaryRacialAbilityChoice || 'dexterity',
      selected_racial_traits: state.selectedRacialTraits || [],
      race_data: state.raceData,
      class_data: state.classData,
      pl_value: parseInt(state.pl_value),
      remaining_power_points: remainingPoints,
      portrait: state.portrait
    };

    set({ loading: true });
    axios.post('/api/characters/recalculate', { data: payload })
      .then(res => {
        set({
          recalcedData: res.data.data,
          warnings: res.data.warnings,
          loading: false
        });
      })
      .catch(err => {
        console.error('Recalculation failed:', err);
        set({ loading: false });
      });
  },

  exportPdf: async () => {
    const state = get();
    set({ loading: true });

    try {
      let response;

      if (state.id) {
        // Kayıtlı karakter: sunucu tarafında hesaplama yapılır
        response = await axios.get(`/api/characters/${state.id}/pdf`, { responseType: 'blob' });
      } else {
        // Kaydedilmemiş karakter: stateless export
        let backendSystem = state.system;
        if (state.system.includes('dnd')) backendSystem = 'dnd5e';
        else if (state.system.includes('pf') || state.system.includes('pathfinder')) backendSystem = 'pf1e';
        else backendSystem = 'mnm';

        const payload = {
          system: backendSystem,
          name: state.name,
          level: parseInt(state.level),
          race: state.race,
          class: state.class,
          background: state.background,
          abilities: state.abilities,
          skill_ranks: state.skills,
          advantages: state.advantages,
          powers: state.powers,
          equipment: state.equipment,
          feats: (state.feats || []).map(f => f.isim || f),
          proficient_skills: state.recalcedData.proficient_skills || [],
          race_data: state.raceData,
          class_data: state.classData,
          portrait: state.portrait,
          ...state.recalcedData
        };
        response = await axios.post('/api/characters/export/pdf', { data: payload }, { responseType: 'blob' });
      }

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `${state.name.replace(/\s+/g, '_')}_sheet.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('PDF dışa aktarılamadı! Backend çalışıyor mu kontrol edin.');
    } finally {
      set({ loading: false });
    }
  },


  levelUp: async (className, choices) => {
    const state = get();
    if (!state.id) {
      alert("Seviye atlamak için karakteri önce kaydetmelisiniz!");
      return false;
    }
    set({ loading: true });
    try {
      const response = await axios.post(`/api/characters/${state.id}/level-up`, {
        class_name: className,
        ...choices
      });
      const charData = response.data.data;
      set({
        level: charData.level,
        class: charData.class,
        abilities: charData.abilities || {},
        skills: charData.skill_ranks || {},
        advantages: charData.advantages || [],
        powers: charData.powers || {},
        equipment: charData.equipment || [],
        recalcedData: charData,
        warnings: response.data.warnings || [],
        loading: false
      });
      return true;
    } catch (err) {
      console.error("Level up failed:", err);
      set({ loading: false });
      alert("Seviye atlatma hatası: " + (err.response?.data?.detail || err.message));
      return false;
    }
  },

  levelUndo: async () => {
    const state = get();
    if (!state.id) return false;
    set({ loading: true });
    try {
      const response = await axios.post(`/api/characters/${state.id}/level-undo`);
      const charData = response.data.data;
      set({
        level: charData.level,
        class: charData.class,
        abilities: charData.abilities || {},
        skills: charData.skill_ranks || {},
        advantages: charData.advantages || [],
        powers: charData.powers || {},
        equipment: charData.equipment || [],
        recalcedData: charData,
        warnings: response.data.warnings || [],
        loading: false
      });
      return true;
    } catch (err) {
      console.error("Level undo failed:", err);
      set({ loading: false });
      alert("Seviye geri alma hatası: " + (err.response?.data?.detail || err.message));
      return false;
    }
  }
}));
