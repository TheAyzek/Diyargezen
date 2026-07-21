import { create } from 'zustand';
import axios from 'axios';

export const useCharacterStore = create((set, get) => ({
  id: null,
  name: 'İsimsiz Kahraman',
  system: '',
  level: 1,
  pl_value: 10,
  race: '',
  class: '',
  background: '',
  abilities: {},
  skills: {},
  advantages: [],
  powers: {},
  equipment: [],
  raceData: {},
  classData: {},
  archetype: '',
  portrait: '',
  
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

      set({
        id: char.id,
        name: char.name,
        system: char.system.toLowerCase(),
        level: char.data?.level || 1,
        pl_value: char.data?.pl_value || 10,
        race: char.data?.race || '',
        class: char.data?.class || '',
        background: char.data?.background || '',
        abilities: char.data?.abilities || {},
        skills: char.data?.skill_ranks || {},
        advantages: char.data?.advantages || [],
        powers: char.data?.powers || {},
        equipment: char.data?.equipment || [],
        raceData: char.data?.race_data || {},
        classData: char.data?.class_data || {},
        archetype: char.data?.archetype || '',
        portrait: char.data?.portrait || char.portrait || '',
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
        abilities: defaultAbilities,
        skills: {},
        advantages: [],
        powers: {},
        equipment: [],
        raceData: {},
        classData: {},
        archetype: sys.includes('mm') || sys.includes('mnm') ? 'Özel (Custom)' : '',
        portrait: '',
        defenses: { dodge: 0, parry: 0, fortitude: 0, toughness: 0, will: 0 },
        recalcedData: {},
        warnings: []
      });
    }
    get().recalculate();
  },

  updateField: (field, value) => {
    set({ [field]: value });
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

  addAdvantage: (adv) => {
    set(state => {
      if (!state.advantages.includes(adv)) {
        return { advantages: [...state.advantages, adv] };
      }
      return {};
    });
    get().recalculate();
  },

  removeAdvantage: (advName) => {
    set(state => ({
      advantages: state.advantages.filter(a => a !== advName)
    }));
    get().recalculate();
  },

  addPower: (powerName, powerData) => {
    set(state => ({
      powers: {
        ...state.powers,
        [powerName]: powerData
      }
    }));
    get().recalculate();
  },

  removePower: (powerName) => {
    set(state => {
      const nextPowers = { ...state.powers };
      delete nextPowers[powerName];
      return { powers: nextPowers };
    });
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
      feats: state.feat ? [state.feat] : [],
      proficient_skills: state.recalcedData.proficient_skills || [],
      archetype: state.archetype,
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
      feats: state.feat ? [state.feat] : [],
      proficient_skills: state.recalcedData.proficient_skills || [],
      race_data: state.raceData,
      class_data: state.classData,
      portrait: state.portrait,
      ...state.recalcedData
    };

    try {
      const response = await axios.post('/api/characters/export/pdf', { data: payload }, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `${state.name.replace(/\s+/g, '_')}_sheet.pdf`;
      link.click();
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('PDF dışa aktarılamadı!');
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
