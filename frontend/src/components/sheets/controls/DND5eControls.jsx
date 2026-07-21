import React, { useState } from 'react';
import { Plus, Trash, Search, Shield, Sword } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';
import EntitySelectorModal from '../../EntitySelectorModal';
import PortraitUpload from './PortraitUpload';

export default function DND5eControls() {
  const {
    name, level, race, class: charClass, background, abilities, recalcedData,
    updateField, updateAbility, addEquipment, removeEquipment, toggleDndSkill
  } = useCharacterStore();

  const [modalOpen, setModalOpen] = useState(false);
  const [modalCategory, setModalCategory] = useState('races');
  const [modalTitle, setModalTitle] = useState('Irk Seçin');

  const costMap = { 8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9 };
  
  const getRemainingPoints = () => {
    let spent = 0;
    Object.entries(abilities).forEach(([k, v]) => {
      if (k !== 'power_points') spent += costMap[v] || 0;
    });
    return 27 - spent;
  };

  const adjustScore = (ab, delta) => {
    const current = abilities[ab] || 8;
    const next = current + delta;
    if (next < 8 || next > 15) return;
    
    const currentCost = costMap[current];
    const nextCost = costMap[next];
    const pointsLeft = getRemainingPoints();
    if (delta > 0 && (nextCost - currentCost) > pointsLeft) return;

    updateAbility(ab, next);
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

  const skillList = [
    "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History",
    "Insight", "Intimidation", "Investigation", "Medicine", "Nature", "Perception",
    "Performance", "Persuasion", "Religion", "Sleight of Hand", "Stealth", "Survival"
  ];

  const currentProfs = recalcedData.proficient_skills || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Basic Setup Card */}
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
          />
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
          <label className="form-label">Arka Plan (Background)</label>
          <select value={background} onChange={(e) => updateField('background', e.target.value)} className="form-select">
            <option value="Acolyte">Acolyte</option>
            <option value="Criminal">Criminal</option>
            <option value="Folk Hero">Folk Hero</option>
            <option value="Noble">Noble</option>
            <option value="Sage">Sage</option>
            <option value="Soldier">Soldier</option>
          </select>
        </div>
      </div>

      {/* Point Buy Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1.2rem' }}>Yetenek Puan Dağıtımı</h3>
          <span style={{ 
            fontSize: '12px', 
            background: getRemainingPoints() >= 0 ? '#22223b' : 'rgba(233,69,96,0.15)', 
            color: getRemainingPoints() >= 0 ? '#c9a84c' : '#e94560',
            padding: '4px 8px', 
            borderRadius: '4px',
            fontWeight: 'bold'
          }}>
            Kalan Puan: {getRemainingPoints()} / 27
          </span>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {abilitiesList.map(ab => {
            const val = abilities[ab.key] || 8;
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

      {/* Skill Proficiency Checkboxes */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
          Beceri Uzmanlıkları (Proficiencies)
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', maxHeight: '200px', overflowY: 'auto' }}>
          {skillList.map(skill => {
            const isProf = currentProfs.includes(skill);
            return (
              <div 
                key={skill} 
                onClick={() => toggleDndSkill(skill)}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '8px', 
                  cursor: 'pointer',
                  padding: '6px 8px',
                  borderRadius: '4px',
                  background: isProf ? 'rgba(201,168,76,0.05)' : 'transparent',
                  border: `1px solid ${isProf ? 'rgba(201,168,76,0.2)' : 'transparent'}`
                }}
              >
                <input type="checkbox" checked={isProf} onChange={() => {}} style={{ pointerEvents: 'none' }} />
                <span style={{ fontSize: '13px', color: isProf ? '#c9a84c' : '#d4c5a9' }}>{skill}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Starting Equipment Selection */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
          <h3 style={{ fontSize: '1.2rem' }}>Ekipman Listesi</h3>
          <button className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '11px', minHeight: 'unset' }} onClick={() => handleOpenSelector('equipment', 'Eşya Ekle')}>
            <Plus size={12} /> Eşya Ekle
          </button>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '180px', overflowY: 'auto' }}>
          {recalcedData.equipment?.length === 0 ? (
            <div style={{ fontSize: '13px', color: '#8b949e', textAlign: 'center', padding: '12px' }}>Ekipman çantası boş.</div>
          ) : (
            recalcedData.equipment?.map((item, index) => (
              <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 12px', background: '#16213e', borderRadius: '6px' }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 'bold' }}>{item.name}</div>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>{item.type || 'item'}</div>
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
        system="dnd5e" 
        category={modalCategory} 
        title={modalTitle} 
        onSelect={handleSelectEntity} 
      />

    </div>
  );
}
