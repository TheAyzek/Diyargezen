import React, { useState } from 'react';
import { Plus, Trash, Search } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';
import EntitySelectorModal from '../../EntitySelectorModal';
import PortraitUpload from './PortraitUpload';

export default function PF1eControls() {
  const {
    id, name, level, race, class: charClass, feat, abilities, skills, recalcedData,
    updateField, updateAbility, updateSkillRank, addEquipment, removeEquipment
  } = useCharacterStore();

  const [modalOpen, setModalOpen] = useState(false);
  const [modalCategory, setModalCategory] = useState('races');
  const [modalTitle, setModalTitle] = useState('Irk Seçin');

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
      updateField('race', entity.isim);
      updateField('raceData', entity.sistem_verisi || {});
    } else if (modalCategory === 'classes') {
      updateField('class', entity.isim);
      updateField('classData', entity.sistem_verisi || {});
    } else if (modalCategory === 'feats') {
      updateField('feat', entity.isim);
    } else if (modalCategory === 'equipment') {
      addEquipment({
        name: entity.isim,
        type: entity.kategori,
        description: entity.aciklama,
        sistem_verisi: entity.sistem_verisi || {}
      });
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
          <label className="form-label">Karakter Adı</label>
          <input 
            type="text" 
            value={name} 
            onChange={(e) => updateField('name', e.target.value)} 
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Seviye (Level)</label>
          <input 
            type="number" 
            min={1} 
            max={20} 
            value={level} 
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
          <label className="form-label">Irk (Race)</label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input type="text" value={race} readOnly className="form-input" placeholder="Irk seçin" />
            <button className="btn btn-secondary" style={{ padding: '8px 12px' }} onClick={() => handleOpenSelector('races', 'Irk Seçin')}>
              Seç
            </button>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Sınıf (Class)</label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input type="text" value={charClass} readOnly className="form-input" placeholder="Sınıf seçin" />
            <button className="btn btn-secondary" style={{ padding: '8px 12px' }} onClick={() => handleOpenSelector('classes', 'Sınıf Seçin')}>
              Seç
            </button>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Feat Seçimi (Prerequisites Check)</label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input type="text" value={feat} readOnly className="form-input" placeholder="Feat seçin" />
            <button className="btn btn-secondary" style={{ padding: '8px 12px' }} onClick={() => handleOpenSelector('feats', 'Feat Seçin')}>
              Seç
            </button>
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
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>
                    AC: +{item.sistem_verisi?.armor_class?.value || 0} | ACP: {item.sistem_verisi?.check_penalty || 0}
                  </div>
                </div>
                <button 
                  className="btn btn-danger" 
                  style={{ padding: '3px 6px', minHeight: 'unset', border: 'none' }}
                  onClick={() => removeEquipment(index)}
                >
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

    </div>
  );
}
