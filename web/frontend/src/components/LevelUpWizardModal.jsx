import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Sparkles, Dices, Shield, Wand2, Award, ArrowRight, ArrowLeft, CheckCircle2, X, Plus, Minus, AlertTriangle } from 'lucide-react';

const CLASS_HIT_DICE = {
  barbarian: 12,
  fighter: 10, paladin: 10, ranger: 10, cavalier: 10, samurai: 10, bloodrager: 10,
  cleric: 8, druid: 8, rogue: 8, monk: 8, bard: 8, magus: 8, alchemist: 8, inquisitor: 8,
  summoner: 8, oracle: 8, witch: 8, hunter: 8, warpriest: 8, skald: 8, investigator: 8,
  wizard: 6, sorcerer: 6, arcanist: 6
};

const CLASS_BASE_SKILLS = {
  rogue: 8, ninja: 8, investigator: 8,
  ranger: 6, bard: 6, alchemist: 6, inquisitor: 6, hunter: 6, skald: 6,
  barbarian: 4, druid: 4, monk: 4, paladin: 2, fighter: 2, wizard: 2, sorcerer: 2, cleric: 2, magus: 2, witch: 2
};

const PF1E_SKILLS = [
  'Acrobatics', 'Appraise', 'Bluff', 'Climb', 'Craft', 'Diplomacy', 'Disable Device',
  'Disguise', 'Escape Artist', 'Fly', 'Handle Animal', 'Heal', 'Intimidate', 'Linguistics',
  'Perception', 'Perform', 'Profession', 'Ride', 'Sense Motive', 'Sleight of Hand',
  'Spellcraft', 'Stealth', 'Survival', 'Swim', 'Use Magic Device',
  'Knowledge (Arcana)', 'Knowledge (Dungeoneering)', 'Knowledge (Engineering)',
  'Knowledge (Geography)', 'Knowledge (History)', 'Knowledge (Local)',
  'Knowledge (Nature)', 'Knowledge (Nobility)', 'Knowledge (Planes)', 'Knowledge (Religion)'
];

export default function LevelUpWizardModal({
  isOpen,
  onClose,
  character = {},
  onApplyLevelUp
}) {
  const [step, setStep] = useState(1);
  const currentLevel = parseInt(character.level) || 1;
  const newLevel = currentLevel + 1;
  const className = (character.class || 'Fighter').toLowerCase();
  
  // Hit Die calculation
  const hitDie = CLASS_HIT_DICE[className] || 8;
  const baseSkillRanks = CLASS_BASE_SKILLS[className] || 4;
  
  const intMod = character.recalcedData?.ability_modifiers?.Intelligence ?? 0;
  const conMod = character.recalcedData?.ability_modifiers?.Constitution ?? 0;

  // Step 1: HP State
  const [hpRoll, setHpRoll] = useState(Math.floor(hitDie / 2) + 1);
  const [isRolling, setIsRolling] = useState(false);
  const [fcbChoice, setFcbChoice] = useState('hp'); // 'hp' or 'skill'

  // Step 2: Skill Ranks State
  const totalSkillRanksAvailable = Math.max(1, baseSkillRanks + intMod + (fcbChoice === 'skill' ? 1 : 0));
  const [spentSkills, setSpentSkills] = useState({});

  // Step 3: Feat State
  const isOddLevelFeat = newLevel % 2 === 1;
  const isFighterBonusFeat = className.includes('fighter') && newLevel % 2 === 0;
  const grantsFeat = isOddLevelFeat || isFighterBonusFeat;
  const [selectedFeat, setSelectedFeat] = useState(null);
  const [featSearch, setFeatSearch] = useState('');
  const [availableFeats, setAvailableFeats] = useState([]);

  // Step 4: Ability Score Increase State
  const grantsAbilityIncrease = newLevel % 4 === 0;
  const [selectedAbility, setSelectedAbility] = useState('Strength');

  useEffect(() => {
    if (isOpen) {
      setStep(1);
      setHpRoll(Math.floor(hitDie / 2) + 1);
      setFcbChoice('hp');
      setSpentSkills({});
      setSelectedFeat(null);
      setSelectedAbility('Strength');
      if (grantsFeat) {
        fetchFeats();
      }
    }
  }, [isOpen, newLevel]);

  const fetchFeats = () => {
    Promise.all([
      axios.get('/api/rules/pf1e/feats').catch(() => ({ data: [] })),
      axios.get(`/api/rules/pf1e/class-features?class_name=${encodeURIComponent(className)}`).catch(() => ({ data: [] }))
    ]).then(([featsRes, classFeaturesRes]) => {
      const featList = (featsRes.data || []).map(f => ({ ...f, type_badge: 'Feat' }));
      const cfList = (classFeaturesRes.data || []).map(c => ({ ...c, type_badge: `${className.toUpperCase()} Yeteneği` }));
      setAvailableFeats([...cfList, ...featList]);
    }).catch(err => console.error('Error fetching features for level up:', err));
  };


  if (!isOpen) return null;

  const handleRollHp = () => {
    setIsRolling(true);
    let count = 0;
    const interval = setInterval(() => {
      setHpRoll(Math.floor(Math.random() * hitDie) + 1);
      count++;
      if (count > 10) {
        clearInterval(interval);
        const finalRoll = Math.floor(Math.random() * hitDie) + 1;
        setHpRoll(finalRoll);
        setIsRolling(false);
      }
    }, 50);
  };

  const totalSpentSkillRanks = Object.values(spentSkills).reduce((a, b) => a + (parseInt(b) || 0), 0);
  const remainingSkillPoints = totalSkillRanksAvailable - totalSpentSkillRanks;

  const handleAddSkillRank = (sk) => {
    if (remainingSkillPoints <= 0) return;
    const currentRank = parseInt(character.skills?.[sk]) || 0;
    const addedRank = parseInt(spentSkills[sk]) || 0;
    if (currentRank + addedRank >= newLevel) return; // Cannot exceed level

    setSpentSkills(prev => ({
      ...prev,
      [sk]: addedRank + 1
    }));
  };

  const handleRemoveSkillRank = (sk) => {
    const addedRank = parseInt(spentSkills[sk]) || 0;
    if (addedRank <= 0) return;

    setSpentSkills(prev => ({
      ...prev,
      [sk]: addedRank - 1
    }));
  };

  const totalHpGain = Math.max(1, hpRoll + conMod + (fcbChoice === 'hp' ? 1 : 0));

  const handleCompleteLevelUp = () => {
    const levelUpPayload = {
      newLevel,
      hpGained: totalHpGain,
      skillRanksGained: spentSkills,
      newFeat: selectedFeat,
      abilityIncrease: grantsAbilityIncrease ? selectedAbility : null,
      fcbChoice,
      class_name: character.class || 'Fighter',
      hp_added: hpRoll,
      favored_class_bonus: fcbChoice,
      skill_ranks: spentSkills,
      feats: selectedFeat ? [selectedFeat.name || selectedFeat.isim || selectedFeat] : [],
      ability_increase: grantsAbilityIncrease ? selectedAbility : null
    };

    onApplyLevelUp(levelUpPayload);
    onClose();
  };

  return ReactDOM.createPortal(
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      backgroundColor: 'rgba(7, 6, 15, 0.96)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem'
    }}>
      <div style={{
        backgroundColor: '#121218', border: '1px solid #c9a84c', borderRadius: '16px',
        width: '100%', maxWidth: '850px', maxHeight: '90vh', display: 'flex', flexDirection: 'column',
        boxShadow: '0 25px 50px -12px rgba(201, 168, 76, 0.25)', overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem', borderBottom: '1px solid #2a2a3a',
          background: 'linear-gradient(135deg, #1f1b2c 0%, #121218 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '42px', height: '42px', borderRadius: '10px',
              backgroundColor: 'rgba(201, 168, 76, 0.15)', border: '1px solid #c9a84c',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Sparkles size={24} color="#ffd700" />
            </div>
            <div>
              <h2 style={{ color: '#fff', fontSize: '1.3rem', fontWeight: 700, margin: 0, fontFamily: 'Cinzel, serif' }}>
                Seviye Atlama Sihirbazı (Level Up)
              </h2>
              <span style={{ color: '#c9a84c', fontSize: '0.85rem', fontWeight: 600 }}>
                {character.name || 'Kahraman'} • Seviye {currentLevel} ➔ <b style={{ color: '#ffd700' }}>Seviye {newLevel}</b>
              </span>
            </div>
          </div>

          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={24} />
          </button>
        </div>

        {/* Step Progress Bar */}
        <div style={{ display: 'flex', borderBottom: '1px solid #2a2a3a', backgroundColor: '#161622' }}>
          {[
            { num: 1, label: '1. HP Zarı' },
            { num: 2, label: '2. Beceriler' },
            { num: 3, label: '3. Feat Seçimi', skip: !grantsFeat },
            { num: 4, label: '4. Stat Artışı', skip: !grantsAbilityIncrease },
            { num: 5, label: '5. Özet & Onay' }
          ].map(s => {
            if (s.skip) return null;
            const isActive = step === s.num;
            const isDone = step > s.num;

            return (
              <div
                key={s.num}
                onClick={() => isDone && setStep(s.num)}
                style={{
                  flex: 1, padding: '0.75rem', textAlign: 'center', fontSize: '0.8rem', fontWeight: 600,
                  color: isActive ? '#ffd700' : isDone ? '#4ec9b0' : '#64748b',
                  borderBottom: isActive ? '3px solid #ffd700' : 'none',
                  backgroundColor: isActive ? 'rgba(255,215,0,0.05)' : 'transparent',
                  cursor: isDone ? 'pointer' : 'default'
                }}
              >
                {s.label}
              </div>
            );
          })}
        </div>

        {/* Content Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', backgroundColor: '#121218' }}>

          {/* STEP 1: HP & FCB */}
          {step === 1 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{ textAlign: 'center' }}>
                <h3 style={{ color: '#fff', fontSize: '1.1rem', margin: '0 0 0.4rem 0', fontFamily: 'Cinzel, serif' }}>
                  Can Puanı (HP) Artışı • Sınıf Zarı (d{hitDie})
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.82rem', margin: 0 }}>
                  Yeni seviye için can puanı zarınızı atın veya sınıfınızın ortalama zar değerini alın.
                </p>
              </div>

              <div style={{
                display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '2rem',
                backgroundColor: '#181824', border: '1px solid #2a2a3a', borderRadius: '14px', padding: '1.5rem'
              }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>Zar Sonucu (d{hitDie})</div>
                  <div style={{
                    fontSize: '2.5rem', fontWeight: 800, color: '#ffd700', fontFamily: 'DM Mono, monospace',
                    minWidth: '70px', height: '60px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: 'rgba(201, 168, 76, 0.1)', border: '1px solid #c9a84c', borderRadius: '12px'
                  }}>
                    {hpRoll}
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  <button
                    onClick={handleRollHp}
                    disabled={isRolling}
                    style={{
                      padding: '0.6rem 1.2rem', backgroundColor: '#7c6ef7', border: 'none', borderRadius: '8px',
                      color: '#fff', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem'
                    }}
                  >
                    <Dices size={18} /> Rastgele Zar At (Roll d{hitDie})
                  </button>

                  <button
                    onClick={() => setHpRoll(Math.floor(hitDie / 2) + 1)}
                    style={{
                      padding: '0.5rem 1.2rem', backgroundColor: '#2a2a3a', border: 'none', borderRadius: '8px',
                      color: '#cbd5e1', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer'
                    }}
                  >
                    ⚖ Ortalama Al ({Math.floor(hitDie / 2) + 1})
                  </button>
                </div>
              </div>

              {/* Favored Class Bonus */}
              <div style={{ backgroundColor: '#181824', border: '1px solid #2a2a3a', borderRadius: '12px', padding: '1rem' }}>
                <div style={{ color: '#ffd700', fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                  Favori Sınıf Bonusu (Favored Class Bonus)
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <label style={{
                    flex: 1, padding: '0.6rem 0.8rem', borderRadius: '8px', border: `1px solid ${fcbChoice === 'hp' ? '#ffd700' : '#2a2a3a'}`,
                    backgroundColor: fcbChoice === 'hp' ? 'rgba(255,215,0,0.1)' : '#121218', cursor: 'pointer',
                    color: fcbChoice === 'hp' ? '#ffd700' : '#94a3b8', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem'
                  }}>
                    <input type="radio" name="fcb" checked={fcbChoice === 'hp'} onChange={() => setFcbChoice('hp')} />
                    +1 Can Puanı (Hit Point)
                  </label>

                  <label style={{
                    flex: 1, padding: '0.6rem 0.8rem', borderRadius: '8px', border: `1px solid ${fcbChoice === 'skill' ? '#ffd700' : '#2a2a3a'}`,
                    backgroundColor: fcbChoice === 'skill' ? 'rgba(255,215,0,0.1)' : '#121218', cursor: 'pointer',
                    color: fcbChoice === 'skill' ? '#ffd700' : '#94a3b8', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem'
                  }}>
                    <input type="radio" name="fcb" checked={fcbChoice === 'skill'} onChange={() => setFcbChoice('skill')} />
                    +1 Beceri Puanı (Skill Rank)
                  </label>
                </div>
              </div>

              <div style={{
                backgroundColor: 'rgba(78, 201, 176, 0.1)', border: '1px solid #4ec9b0', borderRadius: '10px',
                padding: '0.75rem 1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
              }}>
                <span style={{ fontSize: '0.85rem', color: '#4ec9b0' }}>Kazanılacak Toplam HP:</span>
                <b style={{ fontSize: '1.2rem', color: '#4ec9b0', fontFamily: 'DM Mono, monospace' }}>
                  +{totalHpGain} HP <span style={{ fontSize: '0.75rem', fontWeight: 400 }}>(Zar {hpRoll} + Con Mod {conMod >= 0 ? `+${conMod}` : conMod} {fcbChoice === 'hp' ? '+ 1 FCB' : ''})</span>
                </b>
              </div>
            </div>
          )}

          {/* STEP 2: SKILL RANKS */}
          {step === 2 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#181824', padding: '0.8rem 1rem', borderRadius: '10px', border: '1px solid #2a2a3a' }}>
                <div>
                  <h3 style={{ color: '#fff', fontSize: '1rem', margin: 0 }}>Beceri Puanları Dağıtımı</h3>
                  <span style={{ color: '#94a3b8', fontSize: '0.78rem' }}>
                    Sınıf Tabanı ({baseSkillRanks}) + INT Mod ({intMod}) {fcbChoice === 'skill' ? '+ 1 FCB' : ''}
                  </span>
                </div>
                <div style={{
                  fontSize: '1rem', fontWeight: 700, padding: '0.4rem 0.8rem', borderRadius: '8px',
                  backgroundColor: remainingSkillPoints > 0 ? 'rgba(255,215,0,0.15)' : 'rgba(78,201,176,0.15)',
                  color: remainingSkillPoints > 0 ? '#ffd700' : '#4ec9b0', border: `1px solid ${remainingSkillPoints > 0 ? '#ffd700' : '#4ec9b0'}`
                }}>
                  Kalan Puan: {remainingSkillPoints} / {totalSkillRanksAvailable}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '0.6rem', maxHeight: '350px', overflowY: 'auto' }}>
                {PF1E_SKILLS.map(sk => {
                  const currentRanks = parseInt(character.skills?.[sk]) || 0;
                  const addedRanks = parseInt(spentSkills[sk]) || 0;
                  const totalRanks = currentRanks + addedRanks;
                  const isMaxed = totalRanks >= newLevel;

                  return (
                    <div key={sk} style={{
                      backgroundColor: '#161622', border: `1px solid ${addedRanks > 0 ? '#ffd700' : '#2a2a3a'}`,
                      borderRadius: '8px', padding: '0.5rem 0.8rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between'
                    }}>
                      <div>
                        <div style={{ color: '#fff', fontSize: '0.82rem', fontWeight: 600 }}>{sk}</div>
                        <div style={{ color: '#64748b', fontSize: '0.7rem' }}>
                          Mevcut: {currentRanks} ➔ <b style={{ color: isMaxed ? '#ff6b81' : '#ffd700' }}>{totalRanks} / {newLevel}</b>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <button
                          onClick={() => handleRemoveSkillRank(sk)}
                          disabled={addedRanks <= 0}
                          style={{
                            width: '24px', height: '24px', borderRadius: '4px', border: 'none',
                            backgroundColor: addedRanks > 0 ? '#2a2a3a' : '#121218', color: '#fff', cursor: addedRanks > 0 ? 'pointer' : 'default'
                          }}
                        >
                          -
                        </button>
                        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffd700', minWidth: '16px', textAlign: 'center' }}>
                          {addedRanks}
                        </span>
                        <button
                          onClick={() => handleAddSkillRank(sk)}
                          disabled={remainingSkillPoints <= 0 || isMaxed}
                          style={{
                            width: '24px', height: '24px', borderRadius: '4px', border: 'none',
                            backgroundColor: remainingSkillPoints > 0 && !isMaxed ? '#7c6ef7' : '#121218', color: '#fff', cursor: remainingSkillPoints > 0 && !isMaxed ? 'pointer' : 'default'
                          }}
                        >
                          +
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* STEP 3: FEAT SELECTION */}
          {step === 3 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <h3 style={{ color: '#fff', fontSize: '1.1rem', margin: '0 0 0.3rem 0', fontFamily: 'Cinzel, serif' }}>
                  Yeni Feat Seçimi (Level {newLevel})
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.82rem', margin: 0 }}>
                  Karakterinizin yeni seviyede kazandığı Feat yeteneğini seçin.
                </p>
              </div>

              {/* Selected Feat Banner */}
              {selectedFeat ? (
                <div style={{
                  background: 'linear-gradient(135deg, rgba(201,168,76,0.2) 0%, rgba(30,25,12,0.9) 100%)',
                  border: '1px solid #ffd700',
                  borderRadius: '10px',
                  padding: '12px 16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  boxShadow: '0 4px 15px rgba(255,215,0,0.15)'
                }}>
                  <div>
                    <span style={{ fontSize: '0.7rem', color: '#ffd700', fontWeight: 'bold', letterSpacing: '0.5px', textTransform: 'uppercase' }}>✓ SEÇİLEN YETENEK (FEAT):</span>
                    <div style={{ fontSize: '1.1rem', color: '#fff', fontWeight: 'bold', fontFamily: 'Cinzel, serif' }}>
                      {selectedFeat.name || selectedFeat.isim}
                    </div>
                  </div>
                  <span style={{
                    fontSize: '0.75rem',
                    color: '#3fb950',
                    background: 'rgba(63,185,80,0.15)',
                    padding: '5px 12px',
                    borderRadius: '20px',
                    border: '1px solid rgba(63,185,80,0.4)',
                    fontWeight: 'bold'
                  }}>
                    Seçim Onaylandı
                  </span>
                </div>
              ) : (
                <div style={{
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px dashed rgba(201,168,76,0.3)',
                  borderRadius: '10px',
                  padding: '12px 16px',
                  color: '#94a3b8',
                  fontSize: '0.85rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>⚠️ Lütfen aşağıdaki listeden kazanmak istediğiniz Feat yeteneğini tıklayarak seçin.</span>
                </div>
              )}

              <input
                type="text"
                placeholder="Feat ara..."
                value={featSearch}
                onChange={e => setFeatSearch(e.target.value)}
                style={{
                  width: '100%', padding: '0.6rem 0.9rem', backgroundColor: '#181824', border: '1px solid #2a2a3a',
                  borderRadius: '8px', color: '#fff', fontSize: '0.85rem', outline: 'none'
                }}
              />

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '0.75rem', maxHeight: '300px', overflowY: 'auto' }}>
                {availableFeats
                  .filter(f => (f.name || f.isim || '').toLowerCase().includes(featSearch.toLowerCase()))
                  .slice(0, 40)
                  .map((feat, idx) => {
                    const fName = feat.isim || feat.name;
                    const isPicked = selectedFeat?.name === fName || selectedFeat?.isim === fName;

                    const rawDesc = feat.aciklama || feat.sistem_verisi?.description || 'Feat açıklaması.';
                    const cleanDesc = rawDesc.replace(/<[^>]*>?/gm, '').trim();

                    return (
                      <div
                        key={idx}
                        onClick={() => setSelectedFeat(feat)}
                        style={{
                          backgroundColor: isPicked ? 'rgba(201,168,76,0.18)' : '#161622',
                          border: isPicked ? '2px solid #ffd700' : '1px solid #2a2a3a',
                          boxShadow: isPicked ? '0 0 15px rgba(255,215,0,0.3), inset 0 0 10px rgba(255,215,0,0.1)' : 'none',
                          borderRadius: '8px', padding: '0.85rem', cursor: 'pointer', position: 'relative',
                          transition: 'all 0.2s ease'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '6px', marginBottom: '4px' }}>
                          <div style={{ color: isPicked ? '#ffd700' : '#fff', fontWeight: 700, fontSize: '0.9rem' }}>
                            {fName}
                          </div>
                          {isPicked ? (
                            <span style={{
                              fontSize: '0.65rem', fontWeight: 800, padding: '2px 8px', borderRadius: '12px',
                              backgroundColor: '#ffd700', color: '#0d1117', whiteSpace: 'nowrap', boxShadow: '0 2px 6px rgba(255,215,0,0.4)'
                            }}>
                              ✓ SEÇİLDİ
                            </span>
                          ) : feat.type_badge ? (
                            <span style={{
                              fontSize: '0.65rem', fontWeight: 700, padding: '2px 6px', borderRadius: '4px',
                              backgroundColor: feat.type_badge.includes('Feat') ? 'rgba(124,110,247,0.2)' : 'rgba(255,215,0,0.2)',
                              color: feat.type_badge.includes('Feat') ? '#7c6ef7' : '#ffd700',
                              border: `1px solid ${feat.type_badge.includes('Feat') ? 'rgba(124,110,247,0.4)' : 'rgba(255,215,0,0.4)'}`,
                              whiteSpace: 'nowrap'
                            }}>
                              {feat.type_badge}
                            </span>
                          ) : null}
                        </div>
                        <p style={{ color: isPicked ? '#e6edf3' : '#94a3b8', fontSize: '0.75rem', margin: '4px 0 0 0', lineHeight: '1.4', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                          {cleanDesc}
                        </p>
                      </div>
                    );
                  })}
              </div>
            </div>
          )}

          {/* STEP 4: ABILITY INCREASE */}
          {step === 4 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', textAlign: 'center' }}>
              <div>
                <h3 style={{ color: '#fff', fontSize: '1.1rem', margin: '0 0 0.3rem 0', fontFamily: 'Cinzel, serif' }}>
                  Yetenek Skoru Artışı (+1 Ability Increase)
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.82rem', margin: 0 }}>
                  Seviye {newLevel} dönüm noktasında yetenek skorlarınızdan birine +1 kalıcı puan ekleyin.
                </p>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                {['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma'].map(ab => {
                  const isChosen = selectedAbility === ab;
                  const currentVal = character.recalcedData?.ability_scores?.[ab] || 10;

                  return (
                    <div
                      key={ab}
                      onClick={() => setSelectedAbility(ab)}
                      style={{
                        backgroundColor: isChosen ? 'rgba(255,215,0,0.12)' : '#161622',
                        border: `1px solid ${isChosen ? '#ffd700' : '#2a2a3a'}`,
                        borderRadius: '12px', padding: '1.25rem', cursor: 'pointer', transition: 'all 0.2s ease'
                      }}
                    >
                      <div style={{ color: isChosen ? '#ffd700' : '#94a3b8', fontSize: '0.8rem', fontWeight: 700 }}>{ab.toUpperCase()}</div>
                      <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', margin: '6px 0' }}>
                        {currentVal} ➔ <span style={{ color: '#ffd700' }}>{currentVal + 1}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* STEP 5: SUMMARY & CONFIRM */}
          {step === 5 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{ textAlign: 'center' }}>
                <h3 style={{ color: '#ffd700', fontSize: '1.2rem', margin: '0 0 0.3rem 0', fontFamily: 'Cinzel, serif' }}>
                  Seviye Atlama Özeti (Level Up Summary)
                </h3>
                <p style={{ color: '#cbd5e1', fontSize: '0.85rem', margin: 0 }}>
                  Tebrikler! Kahramanınız Seviye {newLevel}'a yükseliyor. Değişiklikleri onaylayın.
                </p>
              </div>

              <div style={{ backgroundColor: '#181824', border: '1px solid #c9a84c', borderRadius: '12px', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #2a2a3a', paddingBottom: '0.5rem' }}>
                  <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Yeni Seviye:</span>
                  <b style={{ color: '#ffd700', fontSize: '0.95rem' }}>Seviye {newLevel}</b>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #2a2a3a', paddingBottom: '0.5rem' }}>
                  <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Kazanılan Can Puanı:</span>
                  <b style={{ color: '#4ec9b0', fontSize: '0.95rem' }}>+{totalHpGain} HP</b>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #2a2a3a', paddingBottom: '0.5rem' }}>
                  <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Dağıtılan Beceri Rütbeleri:</span>
                  <b style={{ color: '#9cdcfe', fontSize: '0.95rem' }}>+{totalSpentSkillRanks} Rütbe</b>
                </div>

                {grantsFeat && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #2a2a3a', paddingBottom: '0.5rem' }}>
                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Yeni Feat:</span>
                    <b style={{ color: '#ce9178', fontSize: '0.95rem' }}>{selectedFeat?.name || selectedFeat?.isim || 'Seçilmedi'}</b>
                  </div>
                )}

                {grantsAbilityIncrease && (
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Yetenek Skoru Artışı:</span>
                    <b style={{ color: '#ffd700', fontSize: '0.95rem' }}>+1 {selectedAbility}</b>
                  </div>
                )}
              </div>
            </div>
          )}

        </div>

        {/* Modal Footer Controls */}
        <div style={{
          padding: '1rem 1.5rem', backgroundColor: '#161622', borderTop: '1px solid #2a2a3a',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between'
        }}>
          {step > 1 ? (
            <button
              onClick={() => {
                let prev = step - 1;
                if (prev === 4 && !grantsAbilityIncrease) prev--;
                if (prev === 3 && !grantsFeat) prev--;
                setStep(prev);
              }}
              style={{
                padding: '0.5rem 1.25rem', backgroundColor: '#2a2a3a', border: 'none', borderRadius: '8px',
                color: '#fff', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem'
              }}
            >
              <ArrowLeft size={16} /> Geri
            </button>
          ) : <div />}

          {step < 5 ? (
            <button
              onClick={() => {
                let next = step + 1;
                if (next === 3 && !grantsFeat) next++;
                if (next === 4 && !grantsAbilityIncrease) next++;
                setStep(next);
              }}
              style={{
                padding: '0.55rem 1.4rem', backgroundColor: '#7c6ef7', border: 'none', borderRadius: '8px',
                color: '#fff', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem'
              }}
            >
              İleri <ArrowRight size={16} />
            </button>
          ) : (
            <button
              onClick={handleCompleteLevelUp}
              style={{
                padding: '0.65rem 1.8rem', background: 'linear-gradient(135deg, #c9a84c 0%, #ffd700 100%)',
                border: 'none', borderRadius: '8px', color: '#121218', fontSize: '0.9rem', fontWeight: 800,
                cursor: 'pointer', boxShadow: '0 0 15px rgba(255,215,0,0.4)', display: 'flex', alignItems: 'center', gap: '0.5rem'
              }}
            >
              <Sparkles size={18} /> SEVİYE ATLAMAYI TAMAMLA
            </button>
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}
