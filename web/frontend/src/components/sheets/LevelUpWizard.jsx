import React, { useState, useEffect } from 'react';
import { useCharacterStore } from '../../store/characterStore';
import { ArrowRight, ArrowLeft, Check, Sparkles, AlertCircle, Plus, Minus, Wand2 } from 'lucide-react';
import SpellSelectorModal from '../SpellSelectorModal';

export default function LevelUpWizard({ isOpen, onClose }) {
  const { 
    id, name, level, class: currentClass, abilities, skills, recalcedData, levelUp, system 
  } = useCharacterStore();

  const targetLevel = level + 1;
  const isFighter = currentClass?.toLowerCase() === 'fighter';
  const isOddLevel = targetLevel % 2 !== 0;
  const isFighterBonusFeat = isFighter && (targetLevel % 2 === 0);
  const isAbilityIncreaseLevel = targetLevel % 4 === 0;

  // Spellcaster check for PF1e & fantasy classes
  const isSpellcaster = [
    'wizard', 'sorcerer', 'cleric', 'druid', 'bard', 'paladin',
    'ranger', 'magus', 'alchemist', 'witch', 'oracle', 'inquisitor',
    'summoner', 'arcanist', 'bloodrager', 'shaman'
  ].includes(currentClass?.toLowerCase());

  // Dynamic screens based on TTRPG system
  let screens = [];
  if (system === 'mnm') {
    screens = ['confirm'];
  } else if (system === 'dnd5e') {
    screens = ['hp', 'feat', 'confirm'];
  } else { // pf1e
    screens = ['hp', 'skills', 'feat', 'confirm'];
  }

  // Step state
  const [step, setStep] = useState(1);
  const [error, setError] = useState('');

  // Class configuration mapping
  const hitDieMap = {
    fighter: 10,
    barbarian: 12,
    paladin: 10,
    ranger: 10,
    cleric: 8,
    druid: 8,
    rogue: 8,
    monk: 8,
    bard: 8,
    wizard: 6,
    sorcerer: 6,
    warlock: 8
  };

  const skillBaseMap = {
    fighter: 2,
    wizard: 2,
    sorcerer: 2,
    cleric: 2,
    paladin: 2,
    barbarian: 4,
    druid: 4,
    monk: 4,
    ranger: 6,
    bard: 6,
    rogue: 8
  };

  const classHitDie = hitDieMap[currentClass?.toLowerCase()] || 8;
  const defaultHpRoll = Math.floor(classHitDie / 2) + 1; // Average roll rounded up

  // Choices state
  const [hpAdded, setHpAdded] = useState(defaultHpRoll);
  const [allocatedRanks, setAllocatedRanks] = useState({});
  const [selectedFeats, setSelectedFeats] = useState([]);
  const [customFeatText, setCustomFeatText] = useState('');
  const [abilityIncrease, setAbilityIncrease] = useState('');
  const [spellsLearned, setSpellsLearned] = useState([]);
  const [customSpellText, setCustomSpellText] = useState('');
  const [isSpellModalOpen, setIsSpellModalOpen] = useState(false);
  
  // DND5e specific states
  const [dndChoiceType, setDndChoiceType] = useState('asi'); // 'asi' or 'feat'

  const intScore = abilities.intelligence || 10;
  const intMod = Math.floor((intScore - 10) / 2);
  const classBaseRanks = skillBaseMap[currentClass?.toLowerCase()] || 2;
  const allowedRanksThisLevel = Math.max(1, classBaseRanks + intMod);

  const pfSkillsList = [
    "Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disable Device",
    "Disguise", "Escape Artist", "Fly", "Handle Animal", "Heal", "Intimidate", "Linguistics",
    "Perception", "Perform", "Profession", "Ride", "Sense Motive", "Sleight of Hand",
    "Spellcraft", "Stealth", "Survival", "Swim", "Use Magic Device",
    "Knowledge (Arcana)", "Knowledge (Dungeoneering)", "Knowledge (Engineering)",
    "Knowledge (Geography)", "Knowledge (History)", "Knowledge (Local)",
    "Knowledge (Nature)", "Knowledge (Nobility)", "Knowledge (Planes)", "Knowledge (Religion)"
  ];

  // DND5e ASI level check
  const isDndASILevel = system === 'dnd5e' && (
    [4, 8, 12, 16, 19].includes(targetLevel) ||
    (currentClass?.toLowerCase() === 'fighter' && [6, 14].includes(targetLevel)) ||
    (currentClass?.toLowerCase() === 'rogue' && [10].includes(targetLevel))
  );

  // Recalculate default HP when wizard opens/class changes
  useEffect(() => {
    setHpAdded(defaultHpRoll);
    setAllocatedRanks({});
    setSelectedFeats([]);
    setCustomFeatText('');
    setAbilityIncrease('');
    setSpellsLearned([]);
    setCustomSpellText('');
    setStep(1);
    setError('');
    setDndChoiceType('asi');
  }, [isOpen, level, currentClass, system]);

  if (!isOpen) return null;

  const totalAllocatedRanks = Object.values(allocatedRanks).reduce((sum, val) => sum + val, 0);
  const remainingRanks = allowedRanksThisLevel - totalAllocatedRanks;

  const handleAdjustAllocatedRank = (skillName, delta) => {
    const currentAllocated = allocatedRanks[skillName] || 0;
    const currentBase = skills[skillName] || 0;
    const nextAllocated = currentAllocated + delta;

    if (nextAllocated < 0) return;
    if (delta > 0 && remainingRanks <= 0) return;

    if (currentBase + nextAllocated > targetLevel) {
      setError(`Bir beceriye verilen toplam puan karakter seviyesini (${targetLevel}) aşamaz!`);
      return;
    }

    setError('');
    setAllocatedRanks(prev => ({
      ...prev,
      [skillName]: nextAllocated
    }));
  };

  const handleAddFeat = (featName) => {
    const clean = featName.trim();
    if (!clean) return;
    if (selectedFeats.includes(clean)) return;

    let limit = 0;
    if (system === 'dnd5e') {
      limit = isDndASILevel ? 1 : 0;
    } else { // pf1e
      limit = (isOddLevel ? 1 : 0) + (isFighterBonusFeat ? 1 : 0);
    }

    if (selectedFeats.length >= limit) {
      setError(`Bu seviyede en fazla ${limit} yetenek (feat) seçebilirsiniz.`);
      return;
    }

    setError('');
    setSelectedFeats([...selectedFeats, clean]);
    setCustomFeatText('');
  };

  const handleRemoveFeat = (index) => {
    setSelectedFeats(selectedFeats.filter((_, i) => i !== index));
  };

  const handleAddSpell = () => {
    const clean = customSpellText.trim();
    if (!clean) return;
    if (spellsLearned.includes(clean)) return;

    setSpellsLearned([...spellsLearned, clean]);
    setCustomSpellText('');
  };

  const handleRemoveSpell = (index) => {
    setSpellsLearned(spellsLearned.filter((_, i) => i !== index));
  };

  const handleNext = () => {
    setError('');
    const currentScreen = screens[step - 1];

    if (currentScreen === 'hp') {
      if (hpAdded < 1 || hpAdded > classHitDie) {
        setError(`Lütfen 1 ile ${classHitDie} (Hit Die) arasında geçerli bir HP değeri girin.`);
        return;
      }
      setStep(step + 1);
    } else if (currentScreen === 'skills') {
      if (remainingRanks !== 0) {
        setError(`Lütfen tüm beceri puanlarını dağıtın. Kalan puan: ${remainingRanks}`);
        return;
      }
      setStep(step + 1);
    } else if (currentScreen === 'feat') {
      if (system === 'dnd5e') {
        if (isDndASILevel) {
          if (dndChoiceType === 'asi' && !abilityIncrease) {
            setError('Lütfen geliştirmek istediğiniz yetenek skorunu (Ability Score) seçin.');
            return;
          }
          if (dndChoiceType === 'feat' && selectedFeats.length < 1) {
            setError('Lütfen bir Feat seçin veya ekleyin.');
            return;
          }
        }
      } else { // pf1e
        const requiredFeatsCount = (isOddLevel ? 1 : 0) + (isFighterBonusFeat ? 1 : 0);
        if (selectedFeats.length < requiredFeatsCount) {
          setError(`Bu seviyede ${requiredFeatsCount} adet Feat seçmelisiniz.`);
          return;
        }
        if (isAbilityIncreaseLevel && !abilityIncrease) {
          setError('Lütfen geliştirmek istediğiniz yetenek skorunu (Ability Score) seçin.');
          return;
        }
      }
      setStep(step + 1);
    }
  };

  const handlePrev = () => {
    setError('');
    setStep(prev => prev - 1);
  };

  const handleConfirm = async () => {
    const skillRanksPayload = {};
    Object.entries(allocatedRanks).forEach(([sk, ranks]) => {
      if (ranks > 0) {
        skillRanksPayload[sk] = ranks;
      }
    });

    // For DND5e, if ASI type is selected, we do not send feats. If Feat type is selected, we do not send ability_increase
    const payloadAbilityIncrease = (system === 'dnd5e' && dndChoiceType !== 'asi') ? null : (abilityIncrease || null);
    const payloadFeats = (system === 'dnd5e' && dndChoiceType !== 'feat') ? [] : selectedFeats;

    const success = await levelUp(currentClass || 'Fighter', {
      hp_added: system === 'mnm' ? 0 : hpAdded,
      skill_ranks: system === 'mnm' ? {} : skillRanksPayload,
      feats: system === 'mnm' ? [] : payloadFeats,
      ability_increase: system === 'mnm' ? null : payloadAbilityIncrease,
      spells_learned: system === 'mnm' ? [] : spellsLearned
    });

    if (success) {
      onClose();
    }
  };

  const popularFeats = system === 'dnd5e' ? [
    "Great Weapon Master", "Sharpshooter", "War Caster", "Fey Touched", "Lucky", 
    "Sentinel", "Mobile", "Resilient", "Telekinetic", "Alert", "Actor"
  ] : [
    "Power Attack", "Weapon Focus", "Dodge", "Toughness", "Improved Initiative", 
    "Iron Will", "Great Fortitude", "Lightning Reflexes", "Mobility", "Cleave",
    "Point-Blank Shot", "Precise Shot", "Rapid Shot", "Two-Weapon Fighting"
  ];

  const currentScreen = screens[step - 1];

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.85)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      backdropFilter: 'blur(8px)',
      padding: '20px'
    }}>
      <div className="glass-card animate-fade-in" style={{
        maxWidth: '650px',
        width: '100%',
        backgroundColor: '#0f0f1a',
        border: '2px solid var(--accent-gold)',
        borderRadius: '16px',
        boxShadow: '0 0 30px rgba(201, 168, 76, 0.25)',
        display: 'flex',
        flexDirection: 'column',
        maxHeight: '90vh'
      }}>
        
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid rgba(201,168,76,0.2)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h3 style={{ fontSize: '1.4rem', color: 'var(--accent-gold)', margin: 0 }}>
              🚀 {system === 'mnm' ? 'Güç Seviyesi Yükseltme' : 'Seviye Atlama Sihirbazı'}
            </h3>
            <span style={{ fontSize: '12px', color: '#8b949e' }}>
              {name} • {system === 'mnm' ? `PL ${level}` : `Seviye ${level}`} → <b style={{ color: 'var(--accent-gold)' }}>{system === 'mnm' ? `PL ${targetLevel}` : `Seviye ${targetLevel}`}</b>
            </span>
          </div>
          <button 
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#8b949e',
              fontSize: '20px',
              cursor: 'pointer'
            }}
          >
            &times;
          </button>
        </div>

        {/* Wizard Steps indicator */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          padding: '12px 24px',
          background: 'rgba(255,255,255,0.02)',
          fontSize: '11px',
          textTransform: 'uppercase',
          letterSpacing: '1px',
          color: '#8b949e',
          borderBottom: '1px solid rgba(255,255,255,0.03)'
        }}>
          {screens.map((scr, idx) => {
            let label = '';
            if (scr === 'hp') label = '1. HP & Sınıf';
            if (scr === 'skills') label = '2. Beceriler';
            if (scr === 'feat') label = system === 'dnd5e' ? '2. Yetenek & Feat' : '3. Feat & Yetenek';
            if (scr === 'confirm') label = system === 'mnm' ? 'Seçimleri Onayla' : `${screens.length}. Büyü & Onay`;
            return (
              <span 
                key={scr}
                style={{ 
                  color: step === (idx + 1) ? 'var(--accent-gold)' : 'inherit', 
                  fontWeight: step === (idx + 1) ? 'bold' : 'normal' 
                }}
              >
                {label}
              </span>
            );
          })}
        </div>

        {/* Error panel */}
        {error && (
          <div style={{
            margin: '16px 24px 0 24px',
            background: 'rgba(233, 69, 96, 0.15)',
            border: '1px solid rgba(233, 69, 96, 0.3)',
            color: 'var(--color-ruby)',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Body content (scrollable) */}
        <div style={{
          padding: '24px',
          flex: 1,
          overflowY: 'auto'
        }}>
          
          {/* SCREEN: HP and Class */}
          {currentScreen === 'hp' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div className="form-group">
                <label className="form-label">Seviye Sınıfı (Assumed Class)</label>
                <input 
                  type="text" 
                  value={currentClass || 'Fighter'} 
                  className="form-input" 
                  disabled 
                  style={{ opacity: 0.8 }}
                />
                <span style={{ fontSize: '11px', color: '#8b949e' }}>Multiclassing desteklenmemektedir, mevcut sınıfınız ile devam edersiniz.</span>
              </div>

              <div className="form-group">
                <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Hit Die Roll (Zar Sonucu)</span>
                  <span style={{ color: 'var(--accent-gold)' }}>Sınıf Zarı: d{classHitDie}</span>
                </label>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <input 
                    type="number" 
                    min={1} 
                    max={classHitDie} 
                    value={hpAdded} 
                    onChange={(e) => setHpAdded(Math.max(1, Math.min(classHitDie, parseInt(e.target.value) || 1)))}
                    className="form-input"
                    style={{ maxWidth: '120px', textAlign: 'center', fontSize: '1.2rem', fontWeight: 'bold' }}
                  />
                  <div>
                    <button 
                      type="button" 
                      className="btn btn-secondary" 
                      style={{ padding: '6px 12px', fontSize: '11px', minHeight: 'unset' }}
                      onClick={() => setHpAdded(defaultHpRoll)}
                    >
                      Ortalama Önerilen ({defaultHpRoll})
                    </button>
                    <div style={{ fontSize: '11px', color: '#8b949e', marginTop: '4px' }}>
                      Eklenecek HP: <b>{hpAdded}</b> (Zar sonucu) + <b>{Math.floor(((abilities.constitution || 10) - 10) / 2)}</b> (CON Mod)
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SCREEN: Skill Ranks (PF1e only) */}
          {currentScreen === 'skills' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                padding: '12px 16px', 
                background: 'rgba(201, 168, 76, 0.08)',
                borderRadius: '8px',
                border: '1px solid rgba(201, 168, 76, 0.2)'
              }}>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 'bold', color: 'var(--accent-gold)' }}>Kullanılabilir Beceri Puanları</div>
                  <div style={{ fontSize: '11px', color: '#8b949e' }}>
                    Sınıf Baz ({classBaseRanks}) + INT Mod ({intMod})
                  </div>
                </div>
                <div style={{ fontSize: '1.8rem', fontWeight: '800', color: remainingRanks === 0 ? 'var(--color-emerald)' : 'var(--accent-gold)' }}>
                  {remainingRanks}
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '350px', overflowY: 'auto', paddingRight: '4px' }}>
                {pfSkillsList.map(skillName => {
                  const currentBase = skills[skillName] || 0;
                  const allocated = allocatedRanks[skillName] || 0;
                  const newTotal = currentBase + allocated;
                  const isClassSkill = (recalcedData.class_data?.class_skills || []).includes(skillName);

                  return (
                    <div key={skillName} style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center', 
                      padding: '8px 16px', 
                      background: allocated > 0 ? 'rgba(63, 185, 80, 0.05)' : 'rgba(255,255,255,0.01)', 
                      border: '1px solid rgba(255,255,255,0.03)', 
                      borderRadius: '8px' 
                    }}>
                      <div>
                        <span style={{ fontSize: '13px', fontWeight: isClassSkill ? 'bold' : 'normal', color: '#f0e6d2' }}>
                          {skillName}
                        </span>
                        {isClassSkill && <span style={{ color: 'var(--accent-gold)', fontSize: '10px', marginLeft: '6px' }}>(Sınıf)</span>}
                        <div style={{ fontSize: '10px', color: '#8b949e' }}>Mevcut: {currentBase} Rütbe | Yeni Toplam: {newTotal}</div>
                      </div>
                      
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <button 
                          type="button"
                          className="ability-btn" 
                          style={{ width: '22px', height: '22px', fontSize: '12px' }} 
                          disabled={allocated <= 0}
                          onClick={() => handleAdjustAllocatedRank(skillName, -1)}
                        >
                          <Minus size={10} />
                        </button>
                        <span style={{ fontSize: '14px', fontWeight: 'bold', minWidth: '16px', textAlign: 'center' }}>
                          +{allocated}
                        </span>
                        <button 
                          type="button"
                          className="ability-btn" 
                          style={{ width: '22px', height: '22px', fontSize: '12px' }}
                          disabled={remainingRanks <= 0 || newTotal >= targetLevel}
                          onClick={() => handleAdjustAllocatedRank(skillName, 1)}
                        >
                          <Plus size={10} />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* SCREEN: Feats & Ability Scores */}
          {currentScreen === 'feat' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              
              {/* DND5e ASI Choose Layout */}
              {system === 'dnd5e' && isDndASILevel && (
                <div style={{ 
                  display: 'flex', 
                  gap: '12px', 
                  marginBottom: '16px',
                  padding: '12px',
                  background: 'rgba(255,255,255,0.02)',
                  borderRadius: '8px',
                  border: '1px solid rgba(255,255,255,0.05)'
                }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '13px' }}>
                    <input 
                      type="radio" 
                      name="dndChoice" 
                      value="asi" 
                      checked={dndChoiceType === 'asi'} 
                      onChange={() => {
                        setDndChoiceType('asi');
                        setSelectedFeats([]);
                      }} 
                    />
                    Ability Score Improvement (Yetenek +1)
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '13px' }}>
                    <input 
                      type="radio" 
                      name="dndChoice" 
                      value="feat" 
                      checked={dndChoiceType === 'feat'} 
                      onChange={() => {
                        setDndChoiceType('feat');
                        setAbilityIncrease('');
                      }} 
                    />
                    Feat (Yeni Yetenek Seç)
                  </label>
                </div>
              )}

              {/* Feats Selection */}
              {((system === 'pf1e' && (isOddLevel || isFighterBonusFeat)) || (system === 'dnd5e' && isDndASILevel && dndChoiceType === 'feat')) && (
                <div>
                  <h4 style={{ fontSize: '1.1rem', color: 'var(--accent-gold)', marginBottom: '8px' }}>
                    Feat (Yetenek) Seçimi
                  </h4>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#8b949e' }}>
                      Kazanılan Feat Limitiniz: <b>1</b> adet. 
                    </div>

                    <div style={{ display: 'flex', gap: '8px' }}>
                      <input 
                        type="text" 
                        placeholder="Feat ismi yazın veya önerilerden seçin"
                        value={customFeatText}
                        onChange={(e) => setCustomFeatText(e.target.value)}
                        className="form-input"
                      />
                      <button 
                        type="button" 
                        className="btn btn-primary"
                        onClick={() => handleAddFeat(customFeatText)}
                        style={{ minHeight: 'unset', padding: '8px 16px' }}
                      >
                        Ekle
                      </button>
                    </div>

                    {/* Popular recommendations list */}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
                      {popularFeats.map(f => (
                        <button 
                          key={f}
                          type="button"
                          className="btn btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '11px', minHeight: 'unset', textTransform: 'none' }}
                          onClick={() => handleAddFeat(f)}
                        >
                          +{f}
                        </button>
                      ))}
                    </div>

                    {/* Selected Feats List */}
                    <div style={{ marginTop: '10px' }}>
                      <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '6px' }}>Bu Seviyede Seçilen Feat'ler:</div>
                      {selectedFeats.length === 0 ? (
                        <div style={{ fontStyle: 'italic', fontSize: '12px', color: '#8b949e' }}>Henüz feat seçilmedi.</div>
                      ) : (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                          {selectedFeats.map((f, i) => (
                            <span 
                              key={i} 
                              style={{ 
                                background: '#16213e', 
                                border: '1px solid var(--accent-gold)', 
                                padding: '4px 10px', 
                                borderRadius: '6px',
                                fontSize: '12px',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '6px'
                              }}
                            >
                              {f}
                              <button 
                                type="button" 
                                style={{ background: 'none', border: 'none', color: 'var(--color-ruby)', cursor: 'pointer', fontSize: '12px' }}
                                onClick={() => handleRemoveFeat(i)}
                              >
                                &times;
                              </button>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* DND5e Non-ASI / PF1e Non-Feat levels messages */}
              {system === 'dnd5e' && !isDndASILevel && (
                <p style={{ color: '#8b949e', fontSize: '13px', fontStyle: 'italic' }}>
                  Bu seviyede ({targetLevel}) yetenek puanı artışı (ASI) veya feat kazanmıyorsunuz.
                </p>
              )}

              {system === 'pf1e' && !(isOddLevel || isFighterBonusFeat) && (
                <p style={{ color: '#8b949e', fontSize: '13px', fontStyle: 'italic' }}>
                  Bu seviyede ({targetLevel}) yeni bir feat kazanmıyorsunuz.
                </p>
              )}

              {/* Ability Points Increase */}
              {((system === 'pf1e' && isAbilityIncreaseLevel) || (system === 'dnd5e' && isDndASILevel && dndChoiceType === 'asi')) && (
                <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '16px' }}>
                  <h4 style={{ fontSize: '1.1rem', color: 'var(--accent-gold)', marginBottom: '8px' }}>
                    Ability Score (Yetenek) Artışı
                  </h4>

                  <div className="form-group">
                    <label className="form-label">Geliştirilecek Yetenek (+1)</label>
                    <select 
                      value={abilityIncrease}
                      onChange={(e) => setAbilityIncrease(e.target.value)}
                      className="form-select"
                    >
                      <option value="">-- Yetenek Seçin --</option>
                      <option value="strength">Strength (Güç)</option>
                      <option value="dexterity">Dexterity (Çeviklik)</option>
                      <option value="constitution">Constitution (Dayanıklılık)</option>
                      <option value="intelligence">Intelligence (Zeka)</option>
                      <option value="wisdom">Wisdom (Sezgi)</option>
                      <option value="charisma">Charisma (Karizma)</option>
                    </select>
                  </div>
                </div>
              )}

              {system === 'pf1e' && !isAbilityIncreaseLevel && (
                <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '16px' }}>
                  <p style={{ color: '#8b949e', fontSize: '13px', fontStyle: 'italic' }}>
                    Yetenek skorları sadece 4 ve katları seviyelerde artar.
                  </p>
                </div>
              )}

            </div>
          )}

          {/* SCREEN: Spells & Confirm */}
          {currentScreen === 'confirm' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              
              {/* Spells Selection (only if spellcaster in D&D/PF and not confirm for M&M) */}
              {system !== 'mnm' && isSpellcaster && (
                <div>
                  <h4 style={{ fontSize: '1.1rem', color: 'var(--accent-gold)', marginBottom: '8px' }}>
                    Yeni Öğrenilen Büyüler (Spells learned)
                  </h4>
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
                    <input 
                      type="text" 
                      placeholder="Büyü adı girin veya kataloğdan seçin"
                      value={customSpellText}
                      onChange={(e) => setCustomSpellText(e.target.value)}
                      className="form-input"
                    />
                    <button 
                      type="button" 
                      className="btn btn-primary"
                      onClick={handleAddSpell}
                      style={{ minHeight: 'unset', padding: '8px 16px' }}
                    >
                      Ekle
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-secondary"
                      onClick={() => setIsSpellModalOpen(true)}
                      style={{ minHeight: 'unset', padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '6px' }}
                    >
                      <Wand2 size={16} /> Kataloğdan Seç
                    </button>
                  </div>

                  <SpellSelectorModal
                    isOpen={isSpellModalOpen}
                    onClose={() => setIsSpellModalOpen(false)}
                    system={system || 'pathfinder1e'}
                    characterClass={currentClass}
                    characterLevel={targetLevel}
                    selectedSpells={spellsLearned}
                    onAddSpell={(spellObj) => {
                      const name = spellObj.isim || spellObj.name;
                      if (name && !spellsLearned.includes(name)) {
                        setSpellsLearned([...spellsLearned, name]);
                      }
                    }}
                  />

                  {spellsLearned.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {spellsLearned.map((s, i) => (
                        <span 
                          key={i} 
                          style={{ 
                            background: '#1a1a2e', 
                            border: '1px solid rgba(255,255,255,0.1)', 
                            padding: '4px 10px', 
                            borderRadius: '6px',
                            fontSize: '12px',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px'
                          }}
                        >
                          {s}
                          <button 
                            type="button" 
                            style={{ background: 'none', border: 'none', color: 'var(--color-ruby)', cursor: 'pointer' }}
                            onClick={() => handleRemoveSpell(i)}
                          >
                            &times;
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Summary */}
              <div style={{ 
                background: 'rgba(255, 255, 255, 0.02)', 
                border: '1px solid rgba(255, 255, 255, 0.05)', 
                borderRadius: '8px', 
                padding: '16px' 
              }}>
                <h4 style={{ color: 'var(--accent-gold)', fontSize: '1rem', marginBottom: '12px' }}>Gelişim Özeti:</h4>
                {system === 'mnm' ? (
                  <ul style={{ fontSize: '13px', display: 'flex', flexDirection: 'column', gap: '8px', listStyleType: 'none', paddingLeft: 0 }}>
                    <li>• Yeni Güç Seviyesi (Power Level): <b style={{ color: 'var(--accent-gold)' }}>PL {targetLevel}</b></li>
                    <li>• Toplam Güç Puanı Sınırı: <b>{targetLevel * 15} PP</b> (+15 PP artışı)</li>
                    <li>• Bu yükseltme ile ek 15 Güç Puanı kazanıp, karakter kağıdınızda dilediğiniz gibi dağıtabileceksiniz.</li>
                  </ul>
                ) : (
                  <ul style={{ fontSize: '13px', display: 'flex', flexDirection: 'column', gap: '8px', listStyleType: 'none', paddingLeft: 0 }}>
                    <li>• Hedef Seviye: <b>{targetLevel}</b></li>
                    <li>• Eklenecek Base HP: <b>+{hpAdded}</b> (Toplam HP artışı: {hpAdded + Math.floor(((abilities.constitution || 10) - 10) / 2)})</li>
                    {system === 'pf1e' && (
                      <li>• Dağıtılan Beceri Puanları (Skill Ranks): 
                        <div style={{ paddingLeft: '12px', color: '#8b949e', marginTop: '4px' }}>
                          {Object.entries(allocatedRanks).map(([k, v]) => `${k} (+${v})`).join(', ') || 'Yok'}
                        </div>
                      </li>
                    )}
                    {selectedFeats.length > 0 && (
                      <li>• Seçilen Yeni Yetenekler (Feats): <b>{selectedFeats.join(', ')}</b></li>
                    )}
                    {abilityIncrease && (
                      <li>• Artırılan Yetenek Skoru: <b style={{ textTransform: 'uppercase' }}>{abilityIncrease} +1</b></li>
                    )}
                    {spellsLearned.length > 0 && (
                      <li>• Öğrenilen Büyüler: <b>{spellsLearned.join(', ')}</b></li>
                    )}
                  </ul>
                )}
              </div>
            </div>
          )}

        </div>

        {/* Footer actions */}
        <div style={{
          padding: '20px 24px',
          borderTop: '1px solid rgba(255,255,255,0.05)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          {step > 1 ? (
            <button type="button" className="btn btn-secondary" onClick={handlePrev}>
              <ArrowLeft size={16} /> Geri
            </button>
          ) : (
            <div />
          )}

          {step < screens.length ? (
            <button type="button" className="btn btn-primary" onClick={handleNext}>
              İleri <ArrowRight size={16} />
            </button>
          ) : (
            <button type="button" className="btn btn-primary" onClick={handleConfirm} style={{ borderColor: 'var(--color-emerald)', background: 'rgba(63, 185, 80, 0.1)' }}>
              Onayla ve Seviye Atla <Check size={16} />
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
