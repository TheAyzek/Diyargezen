import React, { useState, useRef, useEffect } from 'react';
import { Plus, Trash, Shield, X, Award, Wand2, Sparkles, User, Activity, Sword, BookOpen, Package, FileText, Download, Copy, AlertTriangle } from 'lucide-react';
import { useCharacterStore, computeFeatSlots } from '../../../store/characterStore';
import { exportCharacterPDF } from '../../../utils/pdfExportUtil';
import { exportCharacterJSON, copyCharacterJSONToClipboard } from '../../../utils/jsonExportUtil';
import EntitySelectorModal from '../../EntitySelectorModal';
import TraitSelectorModal from '../../TraitSelectorModal';
import FeatSelectorModal from '../../FeatSelectorModal';
import SpellSelectorModal from '../../SpellSelectorModal';
import LevelUpWizardModal from '../../LevelUpWizardModal';
import SpellCard from '../../SpellCard';
import PortraitUpload from './PortraitUpload';
import CompanionPanel from './CompanionPanel';
import GMModifierPanel from './GMModifierPanel';
import RuneField from '../../common/RuneField';
import { getEquipmentCategory, EQUIPMENT_CATEGORIES } from '../../../utils/equipmentClassifier';
import { cleanText } from '../../../utils/textSanitizer';


const ABILITY_KEYS = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'];
const ABILITY_LABELS = { strength: 'STR', dexterity: 'DEX', constitution: 'CON', intelligence: 'INT', wisdom: 'WIS', charisma: 'CHA' };
const ABILITY_FULL = { strength: 'Strength', dexterity: 'Dexterity', constitution: 'Constitution', intelligence: 'Intelligence', wisdom: 'Wisdom', charisma: 'Charisma' };
const ABILITY_RUNES = { strength: 'ᚠ', dexterity: 'ᚢ', constitution: 'ᚦ', intelligence: 'ᚨ', wisdom: 'ᚱ', charisma: 'ᚲ' };

const TABS = [
  { id: 'identity', icon: '⚜', label: 'Kimlik' },
  { id: 'abilities', icon: 'ᛟ', label: 'Skorlar' },
  { id: 'combat', icon: '⚔', label: 'Dövüş' },
  { id: 'skills', icon: '✦', label: 'Beceriler' },
  { id: 'gear', icon: '⚗', label: 'Ekipman' },
  { id: 'backstory', icon: '📜', label: 'Hikaye' },
  { id: 'companion', icon: '🐾', label: 'Yoldaş' },
];

function FieldLabel({ children }) {
  return (
    <div style={{ fontFamily: 'Cinzel, serif', fontSize: '0.52rem', letterSpacing: '0.13em', color: 'var(--gold-pale)', textTransform: 'uppercase', marginBottom: 4, fontWeight: 600 }}>
      {children}
    </div>
  );
}

function SectionHeader({ icon, title }) {
  return (
    <div className="section-header">
      <div className="line" />
      <div style={{ display: 'flex', alignItems: 'center', gap: 7, whiteSpace: 'nowrap' }}>
        <span style={{ color: 'var(--gold)', fontSize: '0.75rem' }}>{icon}</span>
        <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.52rem', letterSpacing: '0.18em', color: 'var(--gold-pale)', textTransform: 'uppercase' }}>{title}</span>
      </div>
      <div className="line" />
    </div>
  );
}

const fmtMod = (n) => (n >= 0 ? `+${n}` : `${n}`);

export default function PF1eControls() {
  const store = useCharacterStore();
  const {
    id, name, level, race, class: charClass, feat, abilities, skills, recalcedData,
    alignment, gender, age, height, weight, deity, homeland, hair, eyes,
    backstory = '', personality = '', allies = '',
    traits, feats, spells = [], usedSpellSlots = {},
    racialAbilityChoice = 'strength', secondaryRacialAbilityChoice = 'dexterity', selectedRacialTraits = [],
    updateField, updateAbility, updateSkillRank, addEquipment, removeEquipment,
    addTrait, removeTrait, addFeat, removeFeat, addSpell, removeSpell, toggleRacialTrait, applyLevelUp,
    toggleSpellSlotUsed, setPreparedSpell, togglePreparedSpellCast, restCharacter, deductGold
  } = store;

  const raceData = store.raceData || store.recalcedData?.race_data || {};
  const classData = store.classData || store.recalcedData?.class_data || {};

  const [tab, setTab] = useState('identity');
  const scrollRef = useRef(null);

  const SPELLCASTING_CLASSES = [
    'wizard', 'sorcerer', 'cleric', 'druid', 'bard', 'paladin',
    'ranger', 'magus', 'alchemist', 'witch', 'oracle', 'inquisitor',
    'summoner', 'arcanist', 'bloodrager', 'hunter', 'investigator',
    'shaman', 'warpriest', 'medium', 'mesmerist', 'occultist', 'spiritualist'
  ];

  const PREPARED_SPELLCASTERS = ['wizard', 'cleric', 'druid', 'paladin', 'ranger', 'magus', 'witch', 'inquisitor', 'warpriest', 'shaman', 'alchemist'];
  const isPreparedSpellcaster = PREPARED_SPELLCASTERS.includes((charClass || '').toLowerCase());

  const COMPANION_CLASSES = [
    'druid', 'ranger', 'hunter', 'summoner', 'wizard', 'witch',
    'sorcerer', 'cavalier', 'paladin', 'samurai', 'arcanist',
    'magus', 'cleric', 'oracle', 'inquisitor', 'spiritualist', 'alchemist'
  ];

  const clsLower = (charClass || '').toLowerCase().trim();
  const hasSpellcasting = SPELLCASTING_CLASSES.some(c => clsLower.includes(c));
  const hasCompanion = COMPANION_CLASSES.some(c => clsLower.includes(c));

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = 0;
  }, [tab]);

  useEffect(() => {
    if (tab === 'companion' && !hasCompanion) {
      setTab('identity');
    }
  }, [charClass, hasCompanion, tab]);

  const normRace = (r) => {
    const str = (r || '').toLowerCase().trim();
    const map = {
      'insan': 'human', 'i̇nsan': 'human', 'human': 'human',
      'yarım-elf': 'half-elf', 'yarim-elf': 'half-elf', 'yarım elf': 'half-elf', 'yarim elf': 'half-elf', 'half-elf': 'half-elf', 'halfelf': 'half-elf',
      'yarım-ork': 'half-orc', 'yarim-ork': 'half-orc', 'yarım ork': 'half-orc', 'yarim ork': 'half-orc', 'half-orc': 'half-orc', 'halforc': 'half-orc',
      'cüce': 'dwarf', 'cuce': 'dwarf', 'dwarf': 'dwarf',
      'elf': 'elf',
      'gnom': 'gnome', 'gnome': 'gnome',
      'buçukluk': 'halfling', 'bucukluk': 'halfling', 'halfling': 'halfling',
      'ork': 'orc', 'orc': 'orc',
      'goblin': 'goblin', 'hobgoblin': 'hobgoblin',
      'kobold': 'kobold', 'tiefling': 'tiefling', 'aasimar': 'aasimar'
    };
    return map[str] || str;
  };

  const canonRace = normRace(race);
  const isFlexibleRace = ['human', 'half-elf', 'half-orc', 'primitive human'].includes(canonRace) ||
    JSON.stringify(raceData.sistem_verisi || {}).toLowerCase().includes('any');

  const svData = raceData.sistem_verisi || raceData || {};
  const rawRacialTraits = Array.isArray(svData.alternate_traits) ? svData.alternate_traits : [];
  const availableRacialTraits = rawRacialTraits;

  const [modalOpen, setModalOpen] = useState(false);
  const [modalCategory, setModalCategory] = useState('races');
  const [modalTitle, setModalTitle] = useState('Irk Seçin');
  const [traitModalOpen, setTraitModalOpen] = useState(false);
  const [traitError, setTraitError] = useState(null);
  const [featModalOpen, setFeatModalOpen] = useState(false);
  const [featError, setFeatError] = useState(null);
  const [spellModalOpen, setSpellModalOpen] = useState(false);
  const [levelUpModalOpen, setLevelUpModalOpen] = useState(false);

  const maxFeatSlots = computeFeatSlots(charClass, race, level);
  const costMap = { 7: -4, 8: -2, 9: -1, 10: 0, 11: 1, 12: 2, 13: 3, 14: 5, 15: 7, 16: 10, 17: 13, 18: 17 };

  const getRemainingPoints = () => {
    let spent = 0;
    Object.entries(abilities).forEach(([k, v]) => {
      if (k !== 'power_points') spent += costMap[v] || 0;
    });
    return 15 - spent;
  };

  const getAvailableSkillRanks = () => {
    const intMod = Math.floor(((abilities.intelligence || 10) - 10) / 2);
    const ranksPerLevel = recalcedData.class_data?.skill_ranks_per_level || 2;
    const total = Math.max(1, ranksPerLevel + intMod) * level;
    let spent = 0;
    Object.values(skills).forEach(val => { spent += parseInt(val) || 0; });
    return total - spent;
  };

  const handleAdjustSkillRank = (skillName, delta) => {
    const current = skills[skillName] || 0;
    const next = current + delta;
    if (next < 0 || next > level) return;
    if (delta > 0 && getAvailableSkillRanks() <= 0) return;
    updateSkillRank(skillName, next);
  };

  const handleOpenSelector = (category, title) => {
    setModalCategory(category);
    setModalTitle(title);
    setModalOpen(true);
  };

  const handleSelectEntity = (entity) => {
    if (modalCategory === 'races') {
      updateField('race', entity.isim || entity.name);
      updateField('raceData', entity);
    } else if (modalCategory === 'classes') {
      updateField('class', entity.isim || entity.name);
      updateField('classData', entity);
    } else if (modalCategory === 'feats') {
      updateField('feat', entity.isim || entity.name);
    } else if (modalCategory === 'equipment') {
      addEquipment({
        name: entity.isim || entity.name,
        type: entity.kategori,
        description: entity.aciklama,
        sistem_verisi: entity.sistem_verisi || {}
      });
    }
  };

  const handleAddTrait = (traitEntity) => {
    const result = addTrait(traitEntity);
    if (result?.error) {
      setTraitError(result.message);
      setTimeout(() => setTraitError(null), 3500);
    }
  };

  const handleAddFeat = (featEntity) => {
    const result = addFeat(featEntity);
    if (result?.error) {
      setFeatError(result.message);
      setTimeout(() => setFeatError(null), 3500);
    }
  };

  const pfSkillsList = [
    "Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disable Device",
    "Disguise", "Escape Artist", "Fly", "Handle Animal", "Heal", "Intimidate", "Linguistics",
    "Perception", "Perform", "Profession", "Ride", "Sense Motive", "Sleight of Hand",
    "Spellcraft", "Stealth", "Survival", "Swim", "Use Magic Device",
    "Knowledge (arcana)", "Knowledge (dungeoneering)", "Knowledge (engineering)",
    "Knowledge (geography)", "Knowledge (history)", "Knowledge (local)",
    "Knowledge (nature)", "Knowledge (nobility)", "Knowledge (planes)", "Knowledge (religion)"
  ];

  return (
    <div style={{
      background: 'var(--obsidian-mid)',
      border: '1px solid rgba(201,168,76,0.25)',
      borderRadius: '8px',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      position: 'relative',
      boxShadow: '0 8px 32px rgba(0,0,0,0.6)'
    }}>
      {/* Floating Rune Background */}
      <RuneField />

      {/* Hero Header Card */}
      <div style={{
        position: 'relative', zIndex: 2, padding: '16px 20px 14px',
        borderBottom: '1px solid rgba(201,168,76,0.18)',
        background: 'linear-gradient(180deg, rgba(16,14,28,0.97) 0%, rgba(10,8,20,0.93) 100%)',
        flexShrink: 0,
        display: 'flex',
        flexDirection: 'column',
        gap: 12
      }}>
        <div style={{ position: 'absolute', top: 0, left: 0, width: 14, height: 14, borderTop: '1px solid var(--gold)', borderLeft: '1px solid var(--gold)', opacity: 0.6 }} />
        <div style={{ position: 'absolute', top: 0, right: 0, width: 14, height: 14, borderTop: '1px solid var(--gold)', borderRight: '1px solid var(--gold)', opacity: 0.6 }} />

        {/* Row 1: Left Identity Controls (Name, Race, Class) + Right Compact Portrait */}
        <div style={{ display: 'flex', gap: 16, alignItems: 'stretch', flexWrap: 'wrap' }}>
          {/* Left Block: Name, Race, Class */}
          <div style={{ flex: '1 1 360px', display: 'flex', flexDirection: 'column', gap: 10, justifyContent: 'center' }}>
            <div>
              <FieldLabel>Karakter İsmi</FieldLabel>
              <input className="rune-input" value={name || ''} onChange={e => updateField('name', e.target.value)}
                placeholder="Kahramanınızın ismi..."
                style={{ fontSize: '1.05rem', fontFamily: 'Cinzel, serif', letterSpacing: '0.04em', padding: '8px 12px', width: '100%' }} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <FieldLabel>Irk (Race)</FieldLabel>
                <div style={{ display: 'flex', gap: 4 }}>
                  <input className="rune-input" value={race || ''} readOnly placeholder="Irk..." style={{ padding: '7px 10px', width: '100%' }} />
                  <button className="gold-btn" style={{ padding: '6px 14px', flexShrink: 0 }} onClick={() => handleOpenSelector('races', 'Irk Seçin')}>
                    Seç
                  </button>
                </div>
              </div>

              <div>
                <FieldLabel>Sınıf (Class)</FieldLabel>
                <div style={{ display: 'flex', gap: 4 }}>
                  <input className="rune-input" value={charClass || ''} readOnly placeholder="Sınıf..." style={{ padding: '7px 10px', width: '100%' }} />
                  <button className="gold-btn" style={{ padding: '6px 14px', flexShrink: 0 }} onClick={() => handleOpenSelector('classes', 'Sınıf Seçin')}>
                    Seç
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Block: Portrait Upload */}
          <div style={{ flexShrink: 0, minWidth: 260 }}>
            <PortraitUpload />
          </div>
        </div>

        {/* Row 2: Seviye & Dışa Aktarım İşlem Butonları */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center', background: 'rgba(0,0,0,0.25)', padding: '8px 12px', borderRadius: 6, border: '1px solid rgba(255,255,255,0.06)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.75rem', color: 'var(--gold-pale)', textTransform: 'uppercase', fontWeight: 600 }}>Seviye:</span>
            <input type="number" min={1} max={20} className="stat-input" value={level || 1}
              onChange={e => updateField('level', Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
              style={{ fontSize: '0.95rem', height: 32, width: 46, textAlign: 'center' }}
              disabled={id !== null} />
          </div>

          <button
            className="gold-btn primary"
            onClick={() => setLevelUpModalOpen(true)}
            style={{ padding: '0 12px', height: 32, whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 4, background: 'linear-gradient(135deg, #c9a84c 0%, #ffd700 100%)', color: '#121218', fontWeight: 800, fontSize: '0.8rem' }}
          >
            <Sparkles size={14} /> ⬆ Seviye Atla
          </button>

          <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
            <button
              className="gold-btn"
              onClick={() => exportCharacterPDF(store)}
              style={{ padding: '0 10px', height: 32, whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(201,168,76,0.15)', border: '1px solid var(--border-gold)', color: 'var(--gold-bright)', fontWeight: 700, fontSize: '0.78rem' }}
            >
              <FileText size={14} /> 📄 PDF
            </button>

            <button
              className="gold-btn"
              onClick={() => exportCharacterJSON(store)}
              style={{ padding: '0 10px', height: 32, whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(78, 201, 176, 0.15)', border: '1px solid #4ec9b0', color: '#4ec9b0', fontWeight: 700, fontSize: '0.78rem' }}
            >
              <Download size={14} /> 📤 JSON
            </button>

            <button
              className="gold-btn"
              onClick={() => copyCharacterJSONToClipboard(store)}
              style={{ padding: '0 10px', height: 32, whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(165, 148, 255, 0.15)', border: '1px solid #a594ff', color: '#a594ff', fontWeight: 700, fontSize: '0.78rem' }}
            >
              <Copy size={14} /> 📋 Kopyala
            </button>
          </div>
        </div>

        {/* Selected Class Description Banner */}
        {charClass && (
          <div style={{
            marginTop: '10px',
            padding: '10px 14px',
            borderRadius: '6px',
            background: 'rgba(201, 168, 76, 0.08)',
            border: '1px solid rgba(201, 168, 76, 0.25)',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontFamily: 'Cinzel, serif', fontWeight: 'bold', color: 'var(--accent-gold)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={14} /> {charClass} Sınıf Tanımı & Kuralları
              </span>
              {classData?.sistem_verisi?.hit_die && (
                <span style={{ fontSize: '0.72rem', background: 'rgba(15,15,26,0.8)', padding: '2px 8px', borderRadius: '4px', border: '1px solid var(--accent-gold)', color: '#f0e6d2', fontWeight: 'bold' }}>
                  Can Zarı: {classData.sistem_verisi.hit_die}
                </span>
              )}
            </div>
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#d4c5a9', lineHeight: '1.45' }}>
              {cleanText(classData?.aciklama || classData?.description) || `${charClass} sınıfı Pathfinder 1e yetenek ve kural şablonu.`}
            </p>
          </div>
        )}
      </div>

      {/* Tabs Header */}
      <div style={{ position: 'relative', zIndex: 2, display: 'flex', borderBottom: '1px solid rgba(201,168,76,0.18)', background: 'rgba(4,3,10,0.6)', flexShrink: 0 }}>
        {TABS.filter(t => (t.id === 'companion' ? hasCompanion : true)).map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`epic-tab ${tab === t.id ? 'active' : ''}`}
            style={{ flex: 1 }}>
            <span style={{ fontSize: '0.85rem', color: tab === t.id ? 'var(--gold-light)' : 'var(--gold-dim)', fontFamily: 'Cinzel, serif' }}>{t.icon}</span>
            <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.45rem', letterSpacing: '0.1em', textTransform: 'uppercase', color: tab === t.id ? 'var(--gold)' : 'var(--gold-dim)' }}>{t.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content Area */}
      <div ref={scrollRef} key={tab}
        style={{ position: 'relative', zIndex: 2, flex: 1, minHeight: 480, maxHeight: 680, overflowY: 'auto', padding: '16px 18px 22px', background: 'rgba(10,8,18,0.55)' }}>

        {/* ── TAB 1: IDENTITY ── */}
        {tab === 'identity' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <SectionHeader icon="⚜" title="Karakter Kimliği & Detayları" />

            {/* Selected Race Summary & Ability Bonus Display */}
            {race && (
              <div style={{
                background: 'linear-gradient(135deg, rgba(201,168,76,0.12) 0%, rgba(63,185,80,0.08) 100%)',
                border: '1px solid var(--border-gold)',
                borderRadius: '4px',
                padding: '10px 14px',
                marginBottom: '4px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.55rem', letterSpacing: '0.12em', color: 'var(--gold-bright)', textTransform: 'uppercase' }}>
                    👑 {race} Irk Bonusları & Özellikleri
                  </span>
                  <span style={{ fontSize: '0.7rem', color: '#38bdf8', fontFamily: 'DM Mono, monospace' }}>
                    {raceData.sistem_verisi?.size || 'Medium'} · {raceData.sistem_verisi?.speed || 30} ft.
                  </span>
                </div>

                {/* Bonus text display */}
                <div style={{ fontSize: '0.82rem', fontWeight: 'bold', fontFamily: 'DM Mono, monospace', marginBottom: 6, display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                  <span style={{ color: '#c9a84c' }}>✨ Status Bonusu:</span>
                  {(() => {
                    const sv = raceData.sistem_verisi || {};
                    const rLower = (race || '').toLowerCase().trim();
                    
                    if (isFlexibleRace) {
                      const primary = (racialAbilityChoice || 'strength').toUpperCase();
                      const secondary = (secondaryRacialAbilityChoice || 'dexterity').toUpperCase();
                      const hasDual = selectedRacialTraits.includes('Dual Talent');
                      return (
                        <span>
                          <span style={{ color: '#3fb950', background: 'rgba(63,185,80,0.12)', padding: '1px 6px', borderRadius: '4px', border: '1px solid rgba(63,185,80,0.3)' }}>
                            +2 {primary} (Esnek Puan)
                          </span>
                          {hasDual && (
                            <span style={{ color: '#3fb950', background: 'rgba(63,185,80,0.12)', padding: '1px 6px', borderRadius: '4px', border: '1px solid rgba(63,185,80,0.3)', marginLeft: '4px' }}>
                              & +2 {secondary} (Dual Talent)
                            </span>
                          )}
                        </span>
                      );
                    }

                    // Check sistem_verisi or fallback to canonical PF1E_RACE_ASI map
                    const PF1E_RACE_ASI_MAP = {
                      "dwarf": { constitution: 2, wisdom: 2, charisma: -2 },
                      "elf": { dexterity: 2, intelligence: 2, constitution: -2 },
                      "gnome": { constitution: 2, charisma: 2, strength: -2 },
                      "halfling": { dexterity: 2, charisma: 2, strength: -2 },
                      "aasimar": { wisdom: 2, charisma: 2 },
                      "android": { dexterity: 2, intelligence: 2, charisma: -2 },
                      "catfolk": { dexterity: 2, charisma: 2, wisdom: -2 },
                      "changeling": { wisdom: 2, charisma: 2, constitution: -2 },
                      "deep one hybrid": { constitution: 2, wisdom: 2, dexterity: -2 },
                      "dhampir": { dexterity: 2, charisma: 2, constitution: -2 },
                      "drow": { dexterity: 2, charisma: 2, constitution: -2 },
                      "drow noble": { dexterity: 4, intelligence: 2, wisdom: 2, charisma: 2, constitution: -2 },
                      "duergar": { constitution: 2, wisdom: 2, charisma: -4 },
                      "fetchling": { dexterity: 2, charisma: 2, wisdom: -2 },
                      "goblin": { dexterity: 4, strength: -2, charisma: -2 },
                      "grippli": { dexterity: 2, wisdom: 2, strength: -2 },
                      "hobgoblin": { dexterity: 2, constitution: 2 },
                      "ifrit": { dexterity: 2, charisma: 2, wisdom: -2 },
                      "kitsune": { dexterity: 2, charisma: 2, strength: -2 },
                      "kobold": { dexterity: 2, strength: -4, constitution: -2 },
                      "merfolk": { dexterity: 2, constitution: 2, charisma: 2 },
                      "nagaji": { strength: 2, charisma: 2, intelligence: -2 },
                      "orc": { strength: 4, intelligence: -2, wisdom: -2, charisma: -2 },
                      "oread": { strength: 2, wisdom: 2, charisma: -2 },
                      "ratfolk": { dexterity: 2, intelligence: 2, strength: -2 },
                      "skinwalker": { wisdom: 2, intelligence: -2 },
                      "suli": { strength: 2, charisma: 2, intelligence: -2 },
                      "svirfneblin": { dexterity: 2, wisdom: 2, strength: -2, charisma: -4 },
                      "sylph": { dexterity: 2, intelligence: 2, constitution: -2 },
                      "tengu": { dexterity: 2, wisdom: 2, constitution: -2 },
                      "tiefling": { dexterity: 2, intelligence: 2, charisma: -2 },
                      "trox": { strength: 6, dexterity: -2, intelligence: -2, wisdom: -2, charisma: -2 },
                      "undine": { dexterity: 2, wisdom: 2, charisma: -2 },
                      "vanara": { dexterity: 2, wisdom: 2, charisma: -2 },
                      "vishkanya": { dexterity: 2, charisma: 2, wisdom: -2 },
                      "wayang": { dexterity: 2, intelligence: 2, wisdom: -2 },
                      "wyrwood": { dexterity: 2, intelligence: 2, constitution: -2 }
                    };

                    let asiObj = (sv.ability_score_increase && typeof sv.ability_score_increase === 'object' && Object.keys(sv.ability_score_increase).length > 0)
                      ? sv.ability_score_increase
                      : (PF1E_RACE_ASI_MAP[canonRace] || PF1E_RACE_ASI_MAP[rLower] || {});

                    const entries = Object.entries(asiObj);
                    if (entries.length > 0) {
                      return (
                        <span>
                          {entries.map(([k, v], i) => {
                            const statName = k.slice(0, 3).toUpperCase();
                            const valText = v >= 0 ? `+${v}` : `${v}`;
                            const isNeg = v < 0;
                            return (
                              <span key={k} style={{
                                color: isNeg ? '#f87171' : '#3fb950',
                                background: isNeg ? 'rgba(248,113,113,0.12)' : 'rgba(63,185,80,0.12)',
                                border: `1px solid ${isNeg ? 'rgba(248,113,113,0.3)' : 'rgba(63,185,80,0.3)'}`,
                                padding: '1px 6px',
                                borderRadius: '4px',
                                marginRight: i < entries.length - 1 ? '4px' : '0'
                              }}>
                                {valText} {statName}
                              </span>
                            );
                          })}
                        </span>
                      );
                    }

                    if (sv.ability_score_increase_text) {
                      return <span style={{ color: '#3fb950' }}>{sv.ability_score_increase_text}</span>;
                    }

                    return <span style={{ color: '#8b949e' }}>Standart Irksal Skorlar</span>;
                  })()}
                </div>

                {/* Core Racial Vision / Features */}
                {raceData.sistem_verisi?.vision && (
                  <div style={{ fontSize: '0.72rem', color: '#a594ff', fontFamily: 'EB Garamond, serif' }}>
                    👁 Görüş: {raceData.sistem_verisi.vision} {raceData.sistem_verisi.vision_range ? `(${raceData.sistem_verisi.vision_range} ft)` : ''}
                  </div>
                )}
              </div>
            )}

            {/* Flexible Racial Bonuses */}
            {isFlexibleRace && (
              <div style={{ background: 'rgba(201,168,76,0.08)', border: '1px solid rgba(201,168,76,0.3)', borderRadius: 2, padding: 10, marginBottom: 6 }}>
                <FieldLabel>Irksal +2 Puan Seçimi (Floating Bonus)</FieldLabel>
                <select className="rune-select" value={racialAbilityChoice} onChange={e => updateField('racialAbilityChoice', e.target.value)}>
                  <option value="strength">💪 Strength (+2)</option>
                  <option value="dexterity">⚡ Dexterity (+2)</option>
                  <option value="constitution">🛡️ Constitution (+2)</option>
                  <option value="intelligence">🧠 Intelligence (+2)</option>
                  <option value="wisdom">👁️ Wisdom (+2)</option>
                  <option value="charisma">✨ Charisma (+2)</option>
                </select>

                {selectedRacialTraits.includes('Dual Talent') && (
                  <div style={{ marginTop: 8 }}>
                    <FieldLabel>Dual Talent İkinci +2 Puan Seçimi</FieldLabel>
                    <select className="rune-select" value={secondaryRacialAbilityChoice} onChange={e => updateField('secondaryRacialAbilityChoice', e.target.value)}>
                      <option value="strength">💪 Strength (+2)</option>
                      <option value="dexterity">⚡ Dexterity (+2)</option>
                      <option value="constitution">🛡️ Constitution (+2)</option>
                      <option value="intelligence">🧠 Intelligence (+2)</option>
                      <option value="wisdom">👁️ Wisdom (+2)</option>
                      <option value="charisma">✨ Charisma (+2)</option>
                    </select>
                  </div>
                )}
              </div>
            )}

            {/* Optional Alternate Racial Traits */}
            {race && availableRacialTraits.length > 0 && (() => {
              const currentlyReplaced = new Map();
              availableRacialTraits.forEach(item => {
                const name = typeof item === 'string' ? item : item?.name;
                if (selectedRacialTraits.includes(name)) {
                  const replaces = Array.isArray(item?.replaces) ? item.replaces : [];
                  replaces.forEach(r => {
                    if (r) currentlyReplaced.set(r.toLowerCase().trim(), { traitName: name, origReplaced: r });
                  });
                }
              });

              return (
                <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(201,168,76,0.15)', borderRadius: 2, padding: 10, marginBottom: 6 }}>
                  <FieldLabel>Alternatif Irksal Özellikler ({race})</FieldLabel>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 160, overflowY: 'auto' }}>
                    {availableRacialTraits.map((item, tIdx) => {
                      const tName = typeof item === 'string' ? item : item?.name || '';
                      const replaces = Array.isArray(item?.replaces) ? item.replaces : [];
                      const isChecked = selectedRacialTraits.includes(tName);
                      
                      let conflictingWith = null;
                      if (!isChecked && replaces.length > 0) {
                        for (const r of replaces) {
                          const rNorm = (r || '').toLowerCase().trim();
                          if (currentlyReplaced.has(rNorm)) {
                            const found = currentlyReplaced.get(rNorm);
                            conflictingWith = { replacedTrait: found.origReplaced || r, chosenTrait: found.traitName };
                            break;
                          }
                        }
                      }

                      return (
                        <label key={tIdx} style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: 8,
                          fontSize: '0.78rem',
                          color: isChecked ? 'var(--gold-bright)' : conflictingWith ? '#888' : 'var(--gold-light)',
                          opacity: conflictingWith ? 0.6 : 1,
                          cursor: conflictingWith ? 'not-allowed' : 'pointer'
                        }} title={conflictingWith ? `'${conflictingWith.replacedTrait}' varsayılan özelliği '${conflictingWith.chosenTrait}' tarafından değiştirildiği için seçilemez.` : ''}>
                          <input
                            type="checkbox"
                            checked={isChecked}
                            disabled={Boolean(conflictingWith)}
                            onChange={() => {
                              if (conflictingWith) return;
                              const res = toggleRacialTrait(tName);
                              if (res?.error) {
                                setTraitError(res.message);
                                setTimeout(() => setTraitError(null), 3500);
                              }
                            }}
                            style={{ accentColor: 'var(--gold)', marginTop: 2 }}
                          />
                          <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span>
                              <b>{tName}</b>
                              {replaces.length > 0 && (
                                <span style={{ fontSize: '0.7rem', color: '#8888a0', marginLeft: 6 }}>
                                  (Değiştirir: {replaces.join(', ')})
                                </span>
                              )}
                            </span>
                            {conflictingWith && (
                              <span style={{ fontSize: '0.68rem', color: '#f87171', fontStyle: 'italic' }}>
                                ⚠️ Çakışma: '{conflictingWith.replacedTrait}' özelliği '{conflictingWith.chosenTrait}' tarafından zaten değiştirilmiş
                              </span>
                            )}
                          </div>
                        </label>
                      );
                    })}
                  </div>
                </div>
              );
            })()}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              <div>
                <FieldLabel>Hizalama (Alignment)</FieldLabel>
                <select className="rune-select" value={alignment || 'TN'} onChange={e => updateField('alignment', e.target.value)}>
                  <option value="LG">Lawful Good (LG)</option>
                  <option value="NG">Neutral Good (NG)</option>
                  <option value="CG">Chaotic Good (CG)</option>
                  <option value="LN">Lawful Neutral (LN)</option>
                  <option value="TN">True Neutral (TN)</option>
                  <option value="CN">Chaotic Neutral (CN)</option>
                  <option value="LE">Lawful Evil (LE)</option>
                  <option value="NE">Neutral Evil (NE)</option>
                  <option value="CE">Chaotic Evil (CE)</option>
                </select>
              </div>

              <div>
                <FieldLabel>Tanrı / İnanç</FieldLabel>
                <input className="rune-input" value={deity || ''} onChange={e => updateField('deity', e.target.value)} placeholder="Iomedae, Sarenrae..." />
              </div>

              <div>
                <FieldLabel>Cinsiyet</FieldLabel>
                <input className="rune-input" value={gender || ''} onChange={e => updateField('gender', e.target.value)} placeholder="Kadın, Erkek..." />
              </div>

              <div>
                <FieldLabel>Yaş</FieldLabel>
                <input className="rune-input" value={age || ''} onChange={e => updateField('age', e.target.value)} placeholder="25..." />
              </div>

              <div>
                <FieldLabel>Boy</FieldLabel>
                <input className="rune-input" value={height || ''} onChange={e => updateField('height', e.target.value)} placeholder="5'10&quot;..." />
              </div>

              <div>
                <FieldLabel>Kilo</FieldLabel>
                <input className="rune-input" value={weight || ''} onChange={e => updateField('weight', e.target.value)} placeholder="160 lbs..." />
              </div>

              <div>
                <FieldLabel>Saç</FieldLabel>
                <input className="rune-input" value={hair || ''} onChange={e => updateField('hair', e.target.value)} placeholder="Siyah..." />
              </div>

              <div>
                <FieldLabel>Göz</FieldLabel>
                <input className="rune-input" value={eyes || ''} onChange={e => updateField('eyes', e.target.value)} placeholder="Kehribar..." />
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <FieldLabel>Memleket</FieldLabel>
                <input className="rune-input" value={homeland || ''} onChange={e => updateField('homeland', e.target.value)} placeholder="Varisia..." />
              </div>
            </div>
          </div>
        )}

        {/* ── TAB 2: ABILITIES ── */}
        {tab === 'abilities' && (
          <div>
            <SectionHeader icon="ᛟ" title="Yetenek Skorları & Point Buy" />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, padding: '6px 10px', background: 'rgba(201,168,76,0.06)', border: '1px solid var(--border-gold)' }}>
              <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.52rem', color: 'var(--gold-pale)', textTransform: 'uppercase' }}>Kalan Satın Alma Puanı</span>
              <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '1rem', color: getRemainingPoints() >= 0 ? 'var(--gold-bright)' : '#e87070', fontWeight: 600 }}>
                {getRemainingPoints()} / 15
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 18 }}>
              {ABILITY_KEYS.map(k => {
                const normKey = k.charAt(0).toUpperCase() + k.slice(1);
                const derivedVal = recalcedData.ability_scores?.[normKey] || abilities[k] || 10;
                const m = recalcedData.ability_modifiers?.[normKey] ?? Math.floor((derivedVal - 10) / 2);
                return (
                  <div key={k} className="ability-box corner-ornament corner-ornament-bottom">
                    <div style={{ position: 'absolute', top: 2, right: 4, fontSize: '1rem', color: 'var(--gold)', opacity: 0.12, fontFamily: 'Cinzel, serif' }}>{ABILITY_RUNES[k]}</div>
                    <div style={{ fontFamily: 'Cinzel, serif', fontSize: '0.48rem', letterSpacing: '0.14em', color: 'var(--gold-pale)', textTransform: 'uppercase' }}>
                      {ABILITY_LABELS[k]}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <button className="gold-btn" style={{ padding: '2px 6px', fontSize: '0.8rem' }} onClick={() => updateAbility(k, Math.max(7, (abilities[k] || 10) - 1))}>-</button>
                      <input className="stat-input" style={{ width: 44, fontSize: '1.4rem', border: 'none', background: 'transparent' }} value={abilities[k] || 10} readOnly />
                      <button className="gold-btn" style={{ padding: '2px 6px', fontSize: '0.8rem' }} onClick={() => updateAbility(k, Math.min(18, (abilities[k] || 10) + 1))}>+</button>
                    </div>
                    <div style={{ fontFamily: 'DM Mono, monospace', fontSize: '0.75rem', color: m >= 0 ? 'var(--gold-light)' : '#d46060', background: 'rgba(201,168,76,0.12)', border: '1px solid rgba(201,168,76,0.3)', borderRadius: 1, padding: '1px 8px', minWidth: 36, textAlign: 'center' }}>
                      {fmtMod(m)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── TAB 3: COMBAT ── */}
        {tab === 'combat' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <GMModifierPanel />
            <SectionHeader icon="⚔" title="Hit Points & AC" />

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
              <div className="dark-panel corner-ornament" style={{ padding: 8, textAlign: 'center' }}>
                <FieldLabel>Zırh Sınıfı (AC)</FieldLabel>
                <div style={{ fontFamily: 'DM Mono, monospace', fontSize: '1.4rem', color: 'var(--gold-bright)', fontWeight: 600 }}>{recalcedData.armor_class || 10}</div>
              </div>
              <div className="dark-panel corner-ornament" style={{ padding: 8, textAlign: 'center' }}>
                <FieldLabel>Touch AC</FieldLabel>
                <div style={{ fontFamily: 'DM Mono, monospace', fontSize: '1.4rem', color: 'var(--gold-bright)', fontWeight: 600 }}>{recalcedData.touch_ac || 10}</div>
              </div>
              <div className="dark-panel corner-ornament" style={{ padding: 8, textAlign: 'center' }}>
                <FieldLabel>Flat-Footed</FieldLabel>
                <div style={{ fontFamily: 'DM Mono, monospace', fontSize: '1.4rem', color: 'var(--gold-bright)', fontWeight: 600 }}>{recalcedData.flat_footed_ac || 10}</div>
              </div>
            </div>

            <SectionHeader icon="⚔" title="Kuşanılan Silahlar & Saldırı Zarları" />
            {recalcedData.weapons && recalcedData.weapons.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {recalcedData.weapons.map((w, idx) => (
                  <div key={idx} className="dark-panel corner-ornament" style={{ padding: '8px 12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontFamily: 'EB Garamond, serif', fontSize: '0.95rem', fontWeight: 600, color: 'var(--gold-bright)' }}>
                        {w.name || w.isim}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                        Kritik: {w.crit_range || '20/x2'}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                      <div style={{ textAlign: 'center' }}>
                        <span style={{ fontSize: '0.6rem', color: 'var(--gold-dim)', display: 'block' }}>ATAK</span>
                        <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '1.1rem', fontWeight: 'bold', color: '#4ec9b0' }}>
                          {w.calculated_attack || '+0'}
                        </span>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                        <span style={{ fontSize: '0.6rem', color: 'var(--gold-dim)', display: 'block' }}>HASAR</span>
                        <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '1rem', fontWeight: 'bold', color: '#ff6b81' }}>
                          {w.calculated_damage || '1d6'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ fontSize: '0.75rem', color: '#64748b', fontStyle: 'italic', textAlign: 'center', padding: '8px' }}>
                Envanterinizde henüz silah bulunmuyor (Ekipman sekmesinden ekleyebilirsiniz).
              </div>
            )}

            <SectionHeader icon="🛡" title="Saldırı & Kurtarma Zarları" />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6 }}>
              {[
                ['BAB', fmtMod(recalcedData.bab || 0)],
                ['İnisiyatif', fmtMod(recalcedData.initiative || 0)],
                ['CMB', fmtMod(recalcedData.cmb || 0)],
                ['CMD', recalcedData.cmd || 10]
              ].map(([l, v]) => (
                <div key={l} className="dark-panel" style={{ padding: '6px 4px', textAlign: 'center' }}>
                  <FieldLabel>{l}</FieldLabel>
                  <div style={{ fontFamily: 'DM Mono, monospace', fontSize: '1.1rem', color: 'var(--gold-bright)' }}>{v}</div>
                </div>
              ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, marginTop: 4 }}>
              <div className="dark-panel" style={{ padding: 6, textAlign: 'center' }}>
                <FieldLabel>Hareket Hızı</FieldLabel>
                <div style={{ fontFamily: 'DM Mono, monospace', fontSize: '1.1rem', color: '#9cdcfe' }}>{recalcedData.speed || 30} ft</div>
              </div>
              <div className="dark-panel" style={{ padding: 6, textAlign: 'center' }}>
                <FieldLabel>Yakın Atak</FieldLabel>
                <div style={{ fontFamily: 'DM Mono, monospace', fontSize: '1.1rem', color: 'var(--gold-bright)' }}>{fmtMod(recalcedData.melee_attack_bonus || 0)}</div>
              </div>
              <div className="dark-panel" style={{ padding: 6, textAlign: 'center' }}>
                <FieldLabel>Menzilli Atak</FieldLabel>
                <div style={{ fontFamily: 'DM Mono, monospace', fontSize: '1.1rem', color: 'var(--gold-bright)' }}>{fmtMod(recalcedData.ranged_attack_bonus || 0)}</div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 4 }}>
              {[
                ['Fortitude', recalcedData.saving_throws?.Fortitude ?? recalcedData.saving_throws?.fortitude ?? 0],
                ['Reflex', recalcedData.saving_throws?.Reflex ?? recalcedData.saving_throws?.reflex ?? 0],
                ['Will', recalcedData.saving_throws?.Will ?? recalcedData.saving_throws?.will ?? 0]
              ].map(([label, val]) => (
                <div key={label} className="dark-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 12px' }}>
                  <span style={{ fontFamily: 'EB Garamond, serif', fontSize: '0.88rem', color: 'var(--gold-light)' }}>{label}</span>
                  <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '1rem', color: 'var(--gold-bright)', fontWeight: 600 }}>{fmtMod(val)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── TAB 4: SKILLS ── */}
        {tab === 'skills' && (
          <div>
            <SectionHeader icon="✦" title="Beceri Rütbeleri (Skills)" />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10, padding: '5px 10px', background: 'rgba(201,168,76,0.06)', border: '1px solid var(--border-gold)' }}>
              <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.5rem', color: 'var(--gold-pale)', textTransform: 'uppercase' }}>Kullanılabilir Rütbe</span>
              <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '0.95rem', color: 'var(--gold-bright)', fontWeight: 600 }}>{getAvailableSkillRanks()}</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 24px 42px 36px', gap: 4, padding: '4px 8px 6px', fontFamily: 'Cinzel, serif', fontSize: '0.42rem', letterSpacing: '0.1em', color: 'var(--gold-dim)', textTransform: 'uppercase', borderBottom: '1px solid rgba(201,168,76,0.12)', marginBottom: 4 }}>
              <span>Skill</span><span style={{ textAlign: 'center' }}>CS</span><span style={{ textAlign: 'center' }}>Ranks</span><span style={{ textAlign: 'center' }}>Total</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 2, maxHeight: 440, overflowY: 'auto' }}>
              {pfSkillsList.map(skillName => {
                const ranks = skills[skillName] || 0;
                const skillDetail = recalcedData.skills_detail?.[skillName] || {};
                const activeClassSkills = (recalcedData.class_skills_active || []).map(s => String(s).toLowerCase());
                const rawClassSkills = (recalcedData.class_data?.class_skills || classData.class_skills || []).map(s => String(s).toLowerCase());
                const hasKnowledgeAll = rawClassSkills.some(s => s.includes('knowledge') && s.includes('all'));
                
                const isClassSkill = skillDetail.is_class_skill !== undefined
                  ? skillDetail.is_class_skill
                  : (activeClassSkills.includes(skillName.toLowerCase()) || rawClassSkills.includes(skillName.toLowerCase()) || (hasKnowledgeAll && skillName.toLowerCase().startsWith('knowledge')));

                const classBonus = skillDetail.class_bonus !== undefined
                  ? skillDetail.class_bonus
                  : (isClassSkill && ranks > 0 ? 3 : 0);

                const total = skillDetail.total !== undefined
                  ? skillDetail.total
                  : (recalcedData.skills?.[skillName] !== undefined ? recalcedData.skills[skillName] : ranks + classBonus);

                const abMod = skillDetail.ability_modifier !== undefined ? skillDetail.ability_modifier : 0;

                return (
                  <div key={skillName} className="skill-row" title={`${ranks} Rank + ${abMod} Mod ${classBonus > 0 ? '+ 3 Sınıf Bonusu' : ''}`}>
                    <div style={{ fontFamily: 'EB Garamond, serif', fontSize: '0.82rem', color: ranks > 0 ? 'var(--gold-light)' : 'var(--gold-dim)', display: 'flex', alignItems: 'center', gap: 5 }}>
                      {skillName} {isClassSkill && (
                        <span style={{ 
                          fontFamily: 'Cinzel, serif', 
                          fontSize: '0.42rem', 
                          color: ranks > 0 ? '#4cd964' : 'var(--gold-bright)',
                          background: ranks > 0 ? 'rgba(76,217,100,0.12)' : 'rgba(201,168,76,0.15)',
                          padding: '1px 4px',
                          borderRadius: '3px',
                          border: ranks > 0 ? '1px solid rgba(76,217,100,0.3)' : '1px solid rgba(201,168,76,0.3)'
                        }}>
                          {ranks > 0 ? '★ Sınıf (+3)' : '★ Sınıf'}
                        </span>
                      )}
                    </div>
                    <input type="checkbox" checked={isClassSkill} readOnly style={{ accentColor: 'var(--gold)', justifySelf: 'center' }} />
                    <div style={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <button className="gold-btn" style={{ padding: '1px 4px', fontSize: '0.65rem' }} onClick={() => handleAdjustSkillRank(skillName, -1)}>-</button>
                      <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '0.8rem', width: 16, textAlign: 'center' }}>{ranks}</span>
                      <button className="gold-btn" style={{ padding: '1px 4px', fontSize: '0.65rem' }} onClick={() => handleAdjustSkillRank(skillName, 1)}>+</button>
                    </div>
                    <div style={{ fontFamily: 'DM Mono, monospace', fontSize: '0.8rem', textAlign: 'center', color: total > 0 ? 'var(--gold-bright)' : 'var(--gold-dim)' }}>
                      {fmtMod(total)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── TAB 5: GEAR, FEATS, TRAITS & SPELLS ── */}
        {tab === 'gear' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            
            {/* Feats Section */}
            <SectionHeader icon="✧" title="Feat & Hücre Seçimi" />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.52rem', color: 'var(--gold-dim)' }}>{feats?.length || 0} / {maxFeatSlots} Feat Seçildi</span>
              <button className="gold-btn primary" style={{ padding: '4px 10px' }} onClick={() => setFeatModalOpen(true)}>
                + Feat Ekle
              </button>
            </div>
            {featError && <div style={{ color: '#e87070', fontSize: '0.75rem' }}>{featError}</div>}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 8 }}>
              {(feats || []).map((f, i) => (
                <span key={i} style={{ border: '1px solid var(--border-gold)', background: 'rgba(201,168,76,0.08)', padding: '3px 8px', borderRadius: 1, fontSize: '0.75rem', color: 'var(--gold-light)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                  {f.isim || f} <X size={10} style={{ cursor: 'pointer' }} onClick={() => removeFeat(f.isim || f)} />
                </span>
              ))}
            </div>

            {/* Traits Section */}
            <SectionHeader icon="🛡" title="Traitler (Karakter Özellikleri)" />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.52rem', color: 'var(--gold-dim)' }}>{traits?.length || 0} / 2 Trait Seçildi</span>
              <button className="gold-btn" style={{ padding: '4px 10px' }} onClick={() => setTraitModalOpen(true)}>
                + Trait Ekle
              </button>
            </div>
            {traitError && <div style={{ color: '#e87070', fontSize: '0.75rem' }}>{traitError}</div>}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 8 }}>
              {(traits || []).map((t, i) => (
                <span key={i} style={{ border: '1px solid rgba(63,185,80,0.3)', background: 'rgba(63,185,80,0.08)', padding: '3px 8px', borderRadius: 1, fontSize: '0.75rem', color: '#3fb950', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                  {t.isim || t} <X size={10} style={{ cursor: 'pointer' }} onClick={() => removeTrait(t.isim || t)} />
                </span>
              ))}
            </div>

            {/* Equipment Section */}
            <SectionHeader icon="⚗" title="Zırh & Ekipman" />

            {/* Encumbrance & Carrying Capacity Meter */}
            {(() => {
              const enc = recalcedData.encumbrance || {};
              const cap = recalcedData.carrying_capacity || enc.carrying_capacity || {};
              const totalW = recalcedData.total_weight ?? enc.total_weight ?? 0;
              const lightMax = cap.light_max ?? cap.light ?? 33;
              const mediumMax = cap.medium_max ?? cap.medium ?? 66;
              const heavyMax = cap.heavy_max ?? cap.heavy ?? 100;
              
              const statusRaw = enc.status || recalcedData.encumbrance_status || 'Light Load';
              const status = statusRaw.includes('Light') ? 'Light' : statusRaw.includes('Medium') ? 'Medium' : statusRaw.includes('Heavy') ? 'Heavy' : 'Overloaded';

              const percent = Math.min(100, Math.round((totalW / (heavyMax || 100)) * 100));
              const statusColor = status === 'Light' ? '#4ec9b0' : status === 'Medium' ? '#ffd700' : status === 'Heavy' ? '#ff9f43' : '#e94560';

              return (
                <div style={{ backgroundColor: '#161622', border: `1px solid ${statusColor}`, borderRadius: '10px', padding: '10px', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#fff' }}>
                      📦 Taşıma Kapasitesi: <b style={{ color: statusColor }}>{totalW} lbs</b> ({statusRaw})
                    </span>
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                      Max: {heavyMax} lbs
                    </span>
                  </div>

                  {/* Progress Meter Bar */}
                  <div style={{ height: '8px', backgroundColor: '#0f0f15', borderRadius: '4px', overflow: 'hidden', border: '1px solid #2a2a3a' }}>
                    <div style={{ width: `${percent}%`, height: '100%', backgroundColor: statusColor, transition: 'width 0.3s ease' }} />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#64748b', marginTop: '4px' }}>
                    <span>Hafif: {lightMax} lbs</span>
                    <span>Orta: {mediumMax} lbs</span>
                    <span>Ağır: {heavyMax} lbs</span>
                  </div>

                  {/* Encumbrance Warning Banner */}
                  {status !== 'Light' && (
                    <div style={{
                      marginTop: '8px', padding: '6px 10px', borderRadius: '6px', fontSize: '0.75rem',
                      backgroundColor: `${statusColor}15`, border: `1px solid ${statusColor}40`, color: statusColor,
                      display: 'flex', alignItems: 'center', gap: '6px'
                    }}>
                      <AlertTriangle size={14} />
                      {status === 'Medium' && '⚠️ Orta Yük Uyarısı: Hareket hızı 20 ft\'e düşer, Max DEX sınırı +3, ACP -3.'}
                      {status === 'Heavy' && '⚠️ Ağır Yük Uyarısı: Hareket hızı 20 ft\'e düşer, Max DEX sınırı +1, ACP -6.'}
                      {status === 'Overloaded' && '🚨 KRİTİK AŞIRI YÜK: Karakter eşyaları taşıyamıyor! Hareket engellenir.'}
                    </div>
                  )}
                </div>
              );
            })()}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.52rem', color: 'var(--gold-dim)' }}>Kategorize Envanter Listesi</span>
              <button className="gold-btn" style={{ padding: '4px 10px' }} onClick={() => handleOpenSelector('equipment', 'Ekipman Ekle')}>
                + Ekle
              </button>
            </div>

            {/* Grouped Equipment Inventory */}
            {(() => {
              const eqList = recalcedData.equipment || [];
              if (eqList.length === 0) {
                return (
                  <div style={{ fontSize: '0.8rem', color: 'var(--gold-dim)', fontStyle: 'italic', padding: '8px 0', marginBottom: 8 }}>
                    Henüz envanterinize ekipman eklenmedi. Eşya eklemek için yukarıdaki "+ Ekle" butonunu kullanın.
                  </div>
                );
              }

              const grouped = {};
              eqList.forEach((item, index) => {
                const catId = getEquipmentCategory(item);
                if (!grouped[catId]) grouped[catId] = [];
                grouped[catId].push({ item, index });
              });

              return (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 12 }}>
                  {EQUIPMENT_CATEGORIES.filter(c => c.id !== 'all' && grouped[c.id]?.length > 0).map(cat => (
                    <div key={cat.id} style={{ background: 'rgba(15,12,28,0.6)', border: '1px solid rgba(201,168,76,0.18)', borderRadius: 6, padding: '8px 10px' }}>
                      <div style={{ fontSize: '0.72rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-bright)', fontWeight: 'bold', marginBottom: 6 }}>
                        {cat.label} ({grouped[cat.id].length})
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        {grouped[cat.id].map(({ item, index }) => (
                          <div key={index} className="dark-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 10px' }}>
                            <span style={{ fontFamily: 'EB Garamond, serif', fontSize: '0.88rem', color: 'var(--gold-light)' }}>{item.name || item.isim}</span>
                            <Trash size={13} style={{ color: '#e87070', cursor: 'pointer', opacity: 0.8 }} onClick={() => removeEquipment(index)} />
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}

            {/* Spells & Spell Slots Section */}
            {hasSpellcasting && (
              <>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <SectionHeader icon="✦" title="Günlük Büyü Slotları & Defter" />
                  <button
                    className="gold-btn"
                    onClick={() => restCharacter()}
                    style={{ padding: '3px 8px', fontSize: '0.72rem', display: 'flex', alignItems: 'center', gap: 4, background: 'rgba(124,110,247,0.15)', border: '1px solid #7c6ef7', color: '#a594ff' }}
                  >
                    🌙 Uzun Dinlenme Yap
                  </button>
                </div>

                {/* Spell Slots per Day Tracker */}
                {recalcedData.spell_slots && Object.keys(recalcedData.spell_slots).length > 0 && (
                  <div style={{ backgroundColor: '#161622', border: '1px solid var(--border-gold)', borderRadius: '8px', padding: '10px', marginBottom: '10px' }}>
                    <FieldLabel>Günlük Büyü Hakkı Takibi (Tıklayarak Harcayın)</FieldLabel>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '6px' }}>
                      {Object.entries(recalcedData.spell_slots).map(([lvlStr, totalSlots]) => {
                        const lvl = parseInt(lvlStr);
                        const usedCount = usedSpellSlots[lvlStr] || 0;
                        const remaining = Math.max(0, totalSlots - usedCount);

                        return (
                          <div key={lvlStr} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.8rem', backgroundColor: '#0f0f15', padding: '4px 8px', borderRadius: '6px' }}>
                            <span style={{ color: 'var(--gold-bright)', fontWeight: 600 }}>
                              {lvl === 0 ? 'Cantrips (0. Seviye)' : `Seviye ${lvl} Büyüler`}
                            </span>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                                {remaining} / {totalSlots} Kalan
                              </span>
                              <div style={{ display: 'flex', gap: '3px' }}>
                                {Array.from({ length: totalSlots }).map((_, i) => {
                                  const isUsed = i < usedCount;
                                  return (
                                    <div
                                      key={i}
                                      onClick={() => toggleSpellSlotUsed(lvlStr, totalSlots)}
                                      style={{
                                        width: '16px', height: '16px', borderRadius: '4px', cursor: 'pointer',
                                        backgroundColor: isUsed ? '#e94560' : 'rgba(78, 201, 176, 0.2)',
                                        border: `1px solid ${isUsed ? '#ff6b81' : '#4ec9b0'}`,
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        fontSize: '0.6rem', color: isUsed ? '#fff' : '#4ec9b0', fontWeight: 'bold'
                                      }}
                                    >
                                      {isUsed ? '✕' : '✓'}
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Prepared Spells Manager for Prepared Spellcasters */}
                {isPreparedSpellcaster && recalcedData.spell_slots && (
                  <div style={{ backgroundColor: '#161622', border: '1px solid #7c6ef7', borderRadius: '8px', padding: '10px', marginBottom: '10px' }}>
                    <FieldLabel>🔮 Günlük Büyü Hazırlama Paneli (Prepared Spells)</FieldLabel>
                    <div style={{ fontSize: '0.7rem', color: '#a594ff', marginBottom: '8px' }}>
                      {charClass} sınıfı hazırlamalı büyücüdür. Günlük slotlarınıza defterinizdeki büyüleri seçip bağlayabilirsiniz:
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {Object.entries(recalcedData.spell_slots).map(([lvlStr, totalSlots]) => {
                        const lvl = parseInt(lvlStr);
                        if (lvl === 0) return null;

                        const currentPrepared = preparedSpells[lvlStr] || [];

                        return (
                          <div key={lvlStr} style={{ backgroundColor: '#0f0f15', border: '1px solid #2a2a3a', borderRadius: '6px', padding: '8px' }}>
                            <div style={{ fontSize: '0.78rem', color: 'var(--gold-bright)', fontWeight: 700, marginBottom: '6px' }}>
                              Seviye {lvl} Büyü Slotları ({totalSlots} Slot Hak)
                            </div>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                              {Array.from({ length: totalSlots }).map((_, slotIdx) => {
                                const preparedItem = currentPrepared[slotIdx] || { name: '', cast: false };
                                const isCast = preparedItem.cast;

                                return (
                                  <div key={slotIdx} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <span style={{ fontSize: '0.7rem', color: '#64748b', width: '42px', flexShrink: 0 }}>
                                      Slot #{slotIdx + 1}:
                                    </span>
                                    <select
                                      className="rune-input"
                                      value={preparedItem.name || ''}
                                      onChange={e => setPreparedSpell(lvlStr, slotIdx, e.target.value)}
                                      style={{ flex: 1, padding: '4px 6px', fontSize: '0.78rem' }}
                                    >
                                      <option value="">-- Büyü Hazırla --</option>
                                      {spells.map((sp, sIdx) => {
                                        const spName = sp.isim || sp.name;
                                        return <option key={sIdx} value={spName}>{spName}</option>;
                                      })}
                                    </select>
                                    <button
                                      onClick={() => togglePreparedSpellCast(lvlStr, slotIdx)}
                                      style={{
                                        padding: '3px 8px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold', cursor: 'pointer',
                                        backgroundColor: isCast ? '#e94560' : 'rgba(78, 201, 176, 0.2)',
                                        border: `1px solid ${isCast ? '#ff6b81' : '#4ec9b0'}`,
                                        color: isCast ? '#fff' : '#4ec9b0'
                                      }}
                                    >
                                      {isCast ? '✕ Atıldı' : '✓ Hazır'}
                                    </button>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.52rem', color: 'var(--gold-dim)' }}>{spells?.length || 0} Büyü Seçildi</span>
                  <button className="gold-btn primary" style={{ padding: '4px 10px' }} onClick={() => setSpellModalOpen(true)}>
                    + Büyü Ekle
                  </button>
                </div>

                {/* Spell Components & Focus Equipment Tracker */}
                {(() => {
                  const equipNames = (recalcedData.equipment || []).map(e => (e.name || e.isim || '').toLowerCase());
                  const hasPouch = equipNames.some(e => e.includes('pouch') || e.includes('torba') || e.includes('component'));
                  const hasHolySymbol = equipNames.some(e => e.includes('holy') || e.includes('symbol') || e.includes('sembol') || e.includes('mistletoe'));

                  return (
                    <div style={{ backgroundColor: '#161622', border: '1px solid var(--border-gold)', borderRadius: '8px', padding: '10px', marginBottom: '10px' }}>
                      <FieldLabel>💎 Büyü Malzemesi & Kutsal Odak Ekipmanı</FieldLabel>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '6px', fontSize: '0.72rem' }}>
                        <span style={{
                          padding: '3px 8px', borderRadius: '4px', fontWeight: 600,
                          backgroundColor: hasPouch ? 'rgba(78, 201, 176, 0.15)' : 'rgba(233, 69, 96, 0.15)',
                          border: `1px solid ${hasPouch ? '#4ec9b0' : '#e94560'}`,
                          color: hasPouch ? '#4ec9b0' : '#ff6b81'
                        }}>
                          {hasPouch ? '✓ Büyü Torbası Var (Pouch)' : '⚠️ Büyü Torbası Eksik'}
                        </span>

                        <span style={{
                          padding: '3px 8px', borderRadius: '4px', fontWeight: 600,
                          backgroundColor: hasHolySymbol ? 'rgba(78, 201, 176, 0.15)' : 'rgba(201, 168, 76, 0.15)',
                          border: `1px solid ${hasHolySymbol ? '#4ec9b0' : 'var(--border-gold)'}`,
                          color: hasHolySymbol ? '#4ec9b0' : 'var(--gold-bright)'
                        }}>
                          {hasHolySymbol ? '✓ Kutsal Sembol Var (Holy Symbol)' : '⚜ Kutsal Odak (Divine Focus)'}
                        </span>

                        <span style={{
                          padding: '3px 8px', borderRadius: '4px', fontWeight: 600,
                          backgroundColor: 'rgba(255, 215, 0, 0.15)', border: '1px solid #ffd700', color: '#ffd700'
                        }}>
                          💰 Altın Stok: {gold} gp
                        </span>
                      </div>
                    </div>
                  );
                })()}

                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {spells.map((sp, idx) => {
                    const sName = sp.isim || sp.name || '';
                    let costInfo = null;
                    if (sName.includes('Stoneskin')) costInfo = { cost: 250, item: '250 gp Elmas Tozu' };
                    else if (sName.includes('Identify')) costInfo = { cost: 100, item: '100 gp İnci' };
                    else if (sName.includes('Raise Dead')) costInfo = { cost: 5000, item: '5,000 gp Elmas' };
                    else if (sName.includes('Resurrection')) costInfo = { cost: 10000, item: '10,000 gp Elmas' };
                    else if (sName.includes('Animate Dead')) costInfo = { cost: 25, item: '25 gp Oniks' };

                    const canAfford = costInfo ? gold >= costInfo.cost : true;

                    return (
                      <div key={idx} className="dark-panel" style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: '6px 10px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontFamily: 'EB Garamond, serif', fontSize: '0.85rem', color: 'var(--gold-bright)' }}>{sName}</span>
                          <X size={12} style={{ color: '#e87070', cursor: 'pointer' }} onClick={() => removeSpell(sName)} />
                        </div>

                        {costInfo && (
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '2px', backgroundColor: '#0f0f15', padding: '4px 6px', borderRadius: '4px' }}>
                            <span style={{ fontSize: '0.68rem', color: canAfford ? '#ffd700' : '#ff6b81' }}>
                              💎 Malzeme: {costInfo.item}
                            </span>
                            <button
                              onClick={() => deductGold(costInfo.cost)}
                              disabled={!canAfford}
                              style={{
                                padding: '2px 8px', fontSize: '0.65rem', borderRadius: '4px', cursor: canAfford ? 'pointer' : 'not-allowed',
                                backgroundColor: canAfford ? 'rgba(255, 215, 0, 0.2)' : 'rgba(100,100,100,0.2)',
                                border: `1px solid ${canAfford ? '#ffd700' : '#555'}`, color: canAfford ? '#ffd700' : '#888', fontWeight: 'bold'
                              }}
                            >
                              ⚡ Malzemeyi Tüket (-{costInfo.cost} gp)
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </>
            )}

          </div>
        )}

        {/* ── TAB 6: BACKSTORY ── */}
        {tab === 'backstory' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <SectionHeader icon="📜" title="Arka Plan & Köken Hikayesi" />
            <div>
              <FieldLabel>Köken & Arka Plan Hikayesi (Backstory & Origin)</FieldLabel>
              <textarea
                className="rune-input"
                rows={6}
                value={backstory || ''}
                onChange={e => updateField('backstory', e.target.value)}
                placeholder="Kahramanınızın nerede doğduğu, maceracı olma nedeni, geçmişteki dönüm noktaları..."
                style={{ width: '100%', resize: 'vertical', lineHeight: '1.5', fontFamily: 'EB Garamond, serif', fontSize: '0.95rem' }}
              />
            </div>

            <SectionHeader icon="🎭" title="Kişilik & Görünüş Notları" />
            <div>
              <FieldLabel>Kişilik Özellikleri, Mizaç & Zaaflar</FieldLabel>
              <textarea
                className="rune-input"
                rows={4}
                value={personality || ''}
                onChange={e => updateField('personality', e.target.value)}
                placeholder="Dış görünüş notları (dövmeler, yara izleri), davranış biçimleri, idealleri..."
                style={{ width: '100%', resize: 'vertical', lineHeight: '1.5', fontFamily: 'EB Garamond, serif', fontSize: '0.95rem' }}
              />
            </div>

            <SectionHeader icon="⚜" title="Müttefikler & Teşkilatlar" />
            <div>
              <FieldLabel>Bağlı Olduğu Loncalar, Klanlar & Müttefikler</FieldLabel>
              <textarea
                className="rune-input"
                rows={3}
                value={allies || ''}
                onChange={e => updateField('allies', e.target.value)}
                placeholder="Üye olduğu lonca, klan, müttefik NPC'ler ve düşmanlar..."
                style={{ width: '100%', resize: 'vertical', lineHeight: '1.5', fontFamily: 'EB Garamond, serif', fontSize: '0.95rem' }}
              />
            </div>

            <SectionHeader icon="📖" title="Macera & Oturum Notları" />
            <div>
              <FieldLabel>Oturum Notları & Görev Günlüğü</FieldLabel>
              <textarea
                className="rune-input"
                rows={4}
                value={notes || ''}
                onChange={e => updateField('notes', e.target.value)}
                placeholder="Oturum sırasında tutulan notlar, keşfedilen gizemler, görev günlüğü..."
                style={{ width: '100%', resize: 'vertical', lineHeight: '1.5', fontFamily: 'EB Garamond, serif', fontSize: '0.95rem' }}
              />
            </div>
          </div>
        )}

        {tab === 'companion' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <CompanionPanel />
          </div>
        )}

      </div>

      {/* Selector Modals */}
      <EntitySelectorModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        system="pf1e"
        category={modalCategory}
        title={modalTitle}
        onSelect={handleSelectEntity}
      />

      <TraitSelectorModal
        isOpen={traitModalOpen}
        onClose={() => setTraitModalOpen(false)}
        system="pf1e"
        character={store}
        selectedTraits={traits || []}
        onAddTrait={handleAddTrait}
      />

      <FeatSelectorModal
        isOpen={featModalOpen}
        onClose={() => setFeatModalOpen(false)}
        system="pf1e"
        character={store}
        selectedFeats={feats || []}
        maxFeats={maxFeatSlots}
        onAddFeat={handleAddFeat}
      />

      <SpellSelectorModal
        isOpen={spellModalOpen}
        onClose={() => setSpellModalOpen(false)}
        system="pf1e"
        characterClass={charClass}
        characterLevel={level}
        selectedSpells={spells || []}
        onAddSpell={(sp) => addSpell(sp)}
      />

      <LevelUpWizardModal
        isOpen={levelUpModalOpen}
        onClose={() => setLevelUpModalOpen(false)}
        character={store}
        onApplyLevelUp={(payload) => applyLevelUp(payload)}
      />
    </div>
  );
}
