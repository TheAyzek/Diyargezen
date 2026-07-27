import React, { useState } from 'react';
import { Plus, Trash, Search, Shield, X, Award } from 'lucide-react';
import { useCharacterStore, computeFeatSlots } from '../../../store/characterStore';
import EntitySelectorModal from '../../EntitySelectorModal';
import TraitSelectorModal from '../../TraitSelectorModal';
import FeatSelectorModal from '../../FeatSelectorModal';
import PortraitUpload from './PortraitUpload';
import GMModifierPanel from './GMModifierPanel';

export default function PF1eControls() {
  const {
    id, name, level, race, class: charClass, feat, abilities, skills, recalcedData,
    alignment, gender, age, height, weight, deity, homeland, hair, eyes,
    traits, feats,
    updateField, updateAbility, updateSkillRank, addEquipment, removeEquipment,
    addTrait, removeTrait, addFeat, removeFeat
  } = useCharacterStore();

  const [modalOpen, setModalOpen] = useState(false);
  const [modalCategory, setModalCategory] = useState('races');
  const [modalTitle, setModalTitle] = useState('Irk Seçin');
  const [traitModalOpen, setTraitModalOpen] = useState(false);
  const [traitError, setTraitError] = useState(null);
  const [featModalOpen, setFeatModalOpen] = useState(false);
  const [featError, setFeatError] = useState(null);

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
    Object.values(skills).forEach(val => {
      spent += parseInt(val) || 0;
    });
    
    return total - spent;
  };

  const adjustScore = (ab, delta) => {
    const current = abilities[ab] || 10;
    const next = current + delta;
    if (next < 7 || next > 18) return;
    
    const currentCost = costMap[current];
    const nextCost = costMap[next];
    const pointsLeft = getRemainingPoints();
    if (delta > 0 && (nextCost - currentCost) > pointsLeft) return;

    updateAbility(ab, next);
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

  const abilitiesList = [
    { key: 'strength', label: 'Strength' },
    { key: 'dexterity', label: 'Dexterity' },
    { key: 'constitution', label: 'Constitution' },
    { key: 'intelligence', label: 'Intelligence' },
    { key: 'wisdom', label: 'Wisdom' },
    { key: 'charisma', label: 'Charisma' }
  ];

  const pfSkillsList = [
    "Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disable Device",
    "Disguise", "Escape Artist", "Fly", "Handle Animal", "Heal", "Intimidate", "Linguistics",
    "Perception", "Perform", "Profession", "Ride", "Sense Motive", "Sleight of Hand",
    "Spellcraft", "Stealth", "Survival", "Swim", "Use Magic Device",
    "Knowledge (Arcana)", "Knowledge (Dungeoneering)", "Knowledge (Engineering)",
    "Knowledge (Geography)", "Knowledge (History)", "Knowledge (Local)",
    "Knowledge (Nature)", "Knowledge (Nobility)", "Knowledge (Planes)", "Knowledge (Religion)"
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Character Setup Card */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
          Karakter Kurulumu
        </h3>
        
        <PortraitUpload />
        
        <div className="form-group">
          <label htmlFor="pf1e-char-name" className="form-label">Karakter Adı</label>
          <input 
            id="pf1e-char-name"
            name="character_name"
            type="text" 
            value={name || ''} 
            onChange={(e) => updateField('name', e.target.value)} 
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="pf1e-char-level" className="form-label">Seviye (Level)</label>
          <input 
            id="pf1e-char-level"
            name="character_level"
            type="number" 
            min={1} 
            max={20} 
            value={level || 1} 
            onChange={(e) => updateField('level', Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
            className="form-input"
            disabled={id !== null}
          />
          {id !== null && (
            <span style={{ fontSize: '11px', color: 'var(--accent-gold)' }}>
              Seviye için sağ üstteki <b>Seviye Atla</b> veya <b>Geri Al</b> işlemlerini kullanın.
            </span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="pf1e-char-race" className="form-label">Irk (Race)</label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input id="pf1e-char-race" name="character_race" type="text" value={race || ''} readOnly className="form-input" placeholder="Irk seçin" />
            <button className="btn btn-secondary" style={{ padding: '8px 12px' }} onClick={() => handleOpenSelector('races', 'Irk Seçin')}>
              Seç
            </button>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="pf1e-char-class" className="form-label">Sınıf (Class)</label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input id="pf1e-char-class" name="character_class" type="text" value={charClass || ''} readOnly className="form-input" placeholder="Sınıf seçin" />
            <button className="btn btn-secondary" style={{ padding: '8px 12px' }} onClick={() => handleOpenSelector('classes', 'Sınıf Seçin')}>
              Seç
            </button>
          </div>
        </div>
      </div>

      {/* Feats Selection Card */}
      <div className="glass-card" style={{ border: '1px solid rgba(201,168,76,0.2)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '10px' }}>
          <h3 style={{ fontSize: '1.1rem', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Award size={16} style={{ color: '#c9a84c' }} />
            Feat Seçimi & Hücreleri
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{
              fontSize: '11px', padding: '2px 8px', borderRadius: '10px',
              background: (feats?.length || 0) >= maxFeatSlots ? 'rgba(233,69,96,0.15)' : 'rgba(201,168,76,0.1)',
              color: (feats?.length || 0) >= maxFeatSlots ? '#e94560' : '#c9a84c',
              border: `1px solid ${(feats?.length || 0) >= maxFeatSlots ? 'rgba(233,69,96,0.3)' : 'rgba(201,168,76,0.2)'}`,
              fontWeight: 'bold'
            }}>
              {feats?.length || 0} / {maxFeatSlots}
            </span>
            {(feats?.length || 0) < maxFeatSlots && (
              <button
                className="btn btn-primary"
                style={{ padding: '5px 10px', fontSize: '11px', minHeight: 'unset' }}
                onClick={() => setFeatModalOpen(true)}
              >
                <Plus size={12} /> Feat Ekle
              </button>
            )}
          </div>
        </div>

        {/* Rule hint */}
        <div style={{ fontSize: '11px', color: '#8b949e', marginBottom: '12px' }}>
          Mevcut Seviye (<b style={{ color: '#c9a84c' }}>{level}</b>) ve Sınıf/Irk bonuslarına göre toplam <b style={{ color: '#c9a84c' }}>{maxFeatSlots} feat</b> hakkınız var.
        </div>

        {/* Feat Error */}
        {featError && (
          <div style={{
            background: 'rgba(233,69,96,0.12)', border: '1px solid rgba(233,69,96,0.35)',
            borderRadius: '6px', padding: '8px 12px', marginBottom: '10px',
            fontSize: '12px', color: '#e94560'
          }}>
            ⚠ {featError}
          </div>
        )}

        {/* Selected Feats List */}
        {(!feats || feats.length === 0) ? (
          <div style={{ textAlign: 'center', padding: '16px 0', color: '#8b949e', fontSize: '13px' }}>
            Henüz feat seçilmedi. Feat eklemek için yukarıdaki butonu kullanın.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {feats.map((f, idx) => {
              const fname = f.isim || f;
              const cat = f.sistem_verisi?.feat_category || 'General';
              return (
                <div key={idx} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '10px 14px', borderRadius: '8px',
                  background: 'rgba(201,168,76,0.06)',
                  border: '1px solid rgba(201,168,76,0.2)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Award size={14} style={{ color: '#c9a84c' }} />
                    <span style={{ fontWeight: 'bold', color: '#f0e6d2', fontSize: '13px' }}>{fname}</span>
                    <span style={{
                      fontSize: '10px', padding: '1px 6px', borderRadius: '10px',
                      background: 'rgba(201,168,76,0.15)', color: '#c9a84c', fontWeight: 'bold'
                    }}>{cat}</span>
                  </div>
                  <button
                    onClick={() => removeFeat(fname)}
                    style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', padding: '4px' }}
                    onMouseOver={e => e.currentTarget.style.color = '#e94560'}
                    onMouseOut={e => e.currentTarget.style.color = '#8b949e'}
                    title="Feati kaldır"
                  >
                    <X size={14} />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Trait Selection Card */}
      <div className="glass-card" style={{ border: '1px solid rgba(201,168,76,0.2)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '10px' }}>
          <h3 style={{ fontSize: '1.1rem', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={16} style={{ color: '#c9a84c' }} />
            Karakter Traitler (Özellikler)
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{
              fontSize: '11px', padding: '2px 8px', borderRadius: '10px',
              background: (traits?.length || 0) >= 2 ? 'rgba(233,69,96,0.15)' : 'rgba(201,168,76,0.1)',
              color: (traits?.length || 0) >= 2 ? '#e94560' : '#c9a84c',
              border: `1px solid ${(traits?.length || 0) >= 2 ? 'rgba(233,69,96,0.3)' : 'rgba(201,168,76,0.2)'}`,
              fontWeight: 'bold'
            }}>
              {traits?.length || 0} / 2
            </span>
            {(traits?.length || 0) < 2 && (
              <button
                className="btn btn-primary"
                style={{ padding: '5px 10px', fontSize: '11px', minHeight: 'unset' }}
                onClick={() => setTraitModalOpen(true)}
              >
                <Plus size={12} /> Trait Ekle
              </button>
            )}
          </div>
        </div>

        {/* Rule hint */}
        <div style={{ fontSize: '11px', color: '#8b949e', marginBottom: '12px' }}>
          Aynı kategoriden olmamak koşuluyla <b style={{ color: '#c9a84c' }}>en fazla 2</b> trait seçebilirsiniz.
        </div>

        {/* Trait error */}
        {traitError && (
          <div style={{
            background: 'rgba(233,69,96,0.12)', border: '1px solid rgba(233,69,96,0.35)',
            borderRadius: '6px', padding: '8px 12px', marginBottom: '10px',
            fontSize: '12px', color: '#e94560'
          }}>
            ⚠ {traitError}
          </div>
        )}

        {/* Selected traits */}
        {(!traits || traits.length === 0) ? (
          <div style={{ textAlign: 'center', padding: '16px 0', color: '#8b949e', fontSize: '13px' }}>
            Henüz trait seçilmedi. Trait eklemek için yukarıdaki butonu kullanın.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {traits.map((trait, idx) => {
              const cat = trait.sistem_verisi?.trait_category || 'Unknown';
              const catColors = {
                Combat: '#e94560', Faith: '#c9a84c', Magic: '#7c6ef7',
                Social: '#4ec9b0', Race: '#ce9178', Regional: '#6a9955',
                Religion: '#d7ba7d', Campaign: '#9cdcfe'
              };
              const catColor = catColors[cat] || '#8b949e';
              return (
                <div key={idx} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
                  padding: '10px 14px', borderRadius: '8px',
                  background: `${catColor}10`,
                  border: `1px solid ${catColor}35`
                }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
                      <span style={{ fontWeight: 'bold', color: '#f0e6d2', fontSize: '13px' }}>{trait.isim}</span>
                      <span style={{
                        fontSize: '10px', padding: '1px 6px', borderRadius: '10px',
                        background: `${catColor}20`, color: catColor, fontWeight: 'bold'
                      }}>{cat}</span>
                    </div>
                    {trait.aciklama && (
                      <div
                        style={{ fontSize: '11px', color: '#8b949e', lineHeight: '1.4' }}
                        dangerouslySetInnerHTML={{ __html: trait.aciklama }}
                      />
                    )}
                  </div>
                  <button
                    onClick={() => removeTrait(trait.isim)}
                    style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', padding: '4px', marginLeft: '8px', flexShrink: 0 }}
                    onMouseOver={e => e.currentTarget.style.color = '#e94560'}
                    onMouseOut={e => e.currentTarget.style.color = '#8b949e'}
                    title="Traiti kaldır"
                  >
                    <X size={14} />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
      {/* Personal Identity Details Card */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
          Kişisel Bilgiler & Kimlik
        </h3>

        <div className="form-group">
          <label htmlFor="pf1e-char-alignment" className="form-label">Hizalama (Alignment)</label>
          <select
            id="pf1e-char-alignment"
            name="character_alignment"
            value={alignment || 'TN'}
            onChange={(e) => updateField('alignment', e.target.value)}
            className="form-input"
            style={{ background: '#0f0f1a', color: '#f0e6d2' }}
          >
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

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label htmlFor="pf1e-char-gender" className="form-label">Cinsiyet</label>
            <input
              id="pf1e-char-gender"
              name="character_gender"
              type="text"
              placeholder="Örn: Kadın"
              value={gender || ''}
              onChange={(e) => updateField('gender', e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="pf1e-char-age" className="form-label">Yaş</label>
            <input
              id="pf1e-char-age"
              name="character_age"
              type="text"
              placeholder="Örn: 25"
              value={age || ''}
              onChange={(e) => updateField('age', e.target.value)}
              className="form-input"
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label htmlFor="pf1e-char-height" className="form-label">Boy</label>
            <input
              id="pf1e-char-height"
              name="character_height"
              type="text"
              placeholder="Örn: 5'10&quot;"
              value={height || ''}
              onChange={(e) => updateField('height', e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="pf1e-char-weight" className="form-label">Kilo</label>
            <input
              id="pf1e-char-weight"
              name="character_weight"
              type="text"
              placeholder="Örn: 160 lbs"
              value={weight || ''}
              onChange={(e) => updateField('weight', e.target.value)}
              className="form-input"
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label htmlFor="pf1e-char-deity" className="form-label">Tanrı / İnanç</label>
            <input
              id="pf1e-char-deity"
              name="character_deity"
              type="text"
              placeholder="Örn: Sarenrae"
              value={deity || ''}
              onChange={(e) => updateField('deity', e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="pf1e-char-homeland" className="form-label">Memleket</label>
            <input
              id="pf1e-char-homeland"
              name="character_homeland"
              type="text"
              placeholder="Örn: Varisia"
              value={homeland || ''}
              onChange={(e) => updateField('homeland', e.target.value)}
              className="form-input"
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label htmlFor="pf1e-char-hair" className="form-label">Saç</label>
            <input
              id="pf1e-char-hair"
              name="character_hair"
              type="text"
              placeholder="Örn: Siyah"
              value={hair || ''}
              onChange={(e) => updateField('hair', e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="pf1e-char-eyes" className="form-label">Göz</label>
            <input
              id="pf1e-char-eyes"
              name="character_eyes"
              type="text"
              placeholder="Örn: Kehribar"
              value={eyes || ''}
              onChange={(e) => updateField('eyes', e.target.value)}
              className="form-input"
            />
          </div>
        </div>
      </div>

      {/* Point Buy Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1.2rem' }}>Yetenek Puan Satın Alma</h3>
          <span style={{ 
            fontSize: '12px', 
            background: getRemainingPoints() >= 0 ? '#22223b' : 'rgba(233,69,96,0.15)', 
            color: getRemainingPoints() >= 0 ? '#c9a84c' : '#e94560',
            padding: '4px 8px', 
            borderRadius: '4px',
            fontWeight: 'bold'
          }}>
            Kalan Puan: {getRemainingPoints()} / 15
          </span>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {abilitiesList.map(ab => {
            const val = abilities[ab.key] || 10;
            return (
              <div key={ab.key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)', padding: '8px 16px', borderRadius: '8px' }}>
                <span style={{ fontWeight: '600', color: '#d4c5a9' }}>{ab.label}</span>
                <div className="ability-value-row">
                  <button className="ability-btn" style={{ width: '24px', height: '24px' }} onClick={() => adjustScore(ab.key, -1)}>-</button>
                  <span className="ability-score" style={{ fontSize: '1.2rem' }}>{val}</span>
                  <button className="ability-btn" style={{ width: '24px', height: '24px' }} onClick={() => adjustScore(ab.key, 1)}>+</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Skill ranks allocation */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
          <h3 style={{ fontSize: '1.2rem' }}>Beceri Rütbeleri (Skills)</h3>
          <span style={{ fontSize: '12px', background: '#22223b', padding: '3px 8px', borderRadius: '4px', color: '#c9a84c', fontWeight: 'bold' }}>
            Boş Rütbe: {getAvailableSkillRanks()}
          </span>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '250px', overflowY: 'auto', paddingRight: '4px' }}>
          {pfSkillsList.map(skillName => {
            const ranks = skills[skillName] || 0;
            const classSkills = recalcedData.class_data?.class_skills || [];
            const isClassSkill = classSkills.includes(skillName);

            return (
              <div key={skillName} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 12px', background: 'rgba(255,255,255,0.01)', border: '1px solid rgba(255,255,255,0.03)', borderRadius: '6px' }}>
                <span style={{ fontSize: '13px', color: '#d4c5a9', fontWeight: isClassSkill ? 'bold' : 'normal' }}>
                  {skillName} {isClassSkill && <span style={{ color: '#c9a84c', fontSize: '10px' }}>(Sınıf)</span>}
                </span>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button className="ability-btn" style={{ width: '22px', height: '22px', fontSize: '12px' }} onClick={() => handleAdjustSkillRank(skillName, -1)}>-</button>
                  <span style={{ fontSize: '14px', fontWeight: 'bold', minWidth: '16px', textAlign: 'center' }}>{ranks}</span>
                  <button className="ability-btn" style={{ width: '22px', height: '22px', fontSize: '12px' }} onClick={() => handleAdjustSkillRank(skillName, 1)}>+</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Equipment Selection */}
      <GMModifierPanel />
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
          <h3 style={{ fontSize: '1.2rem' }}>Zırh & Ekipman</h3>
          <button className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '11px', minHeight: 'unset' }} onClick={() => handleOpenSelector('equipment', 'Zırh/Ekipman Ekle')}>
            <Plus size={12} /> Ekle
          </button>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '180px', overflowY: 'auto' }}>
          {recalcedData.equipment?.length === 0 ? (
            <div style={{ fontSize: '13px', color: '#8b949e', textAlign: 'center', padding: '12px' }}>Envanter boş.</div>
          ) : (
            recalcedData.equipment?.map((item, index) => (
              <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 12px', background: '#16213e', borderRadius: '6px' }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 'bold' }}>{item.name}</div>
                  <div style={{ fontSize: '11px', color: '#8b949e' }}>{item.type} - {item.sistem_verisi?.weight?.value || 0} lb</div>
                </div>
                <button className="btn btn-secondary" style={{ padding: '4px', minHeight: 'unset', color: '#e94560' }} onClick={() => removeEquipment(index)}>
                  <Trash size={12} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

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
        selectedTraits={traits || []}
        onAddTrait={handleAddTrait}
      />

      <FeatSelectorModal
        isOpen={featModalOpen}
        onClose={() => setFeatModalOpen(false)}
        system="pf1e"
        selectedFeats={feats || []}
        maxFeats={maxFeatSlots}
        onAddFeat={handleAddFeat}
      />
    </div>
  );
}
