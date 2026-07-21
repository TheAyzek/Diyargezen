import React, { useState } from 'react';
import { Plus, Trash, Search } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';
import EntitySelectorModal from '../../EntitySelectorModal';
import PortraitUpload from './PortraitUpload';

export default function MM3eControls() {
  const {
    name, pl_value: pl, archetype, abilities, defenses, skills, advantages, powers, recalcedData,
    updateField, updateAbility, updateDefense, updateSkillRank, addAdvantage, removeAdvantage, addPower, removePower, addEquipment, removeEquipment
  } = useCharacterStore();

  const [modalOpen, setModalOpen] = useState(false);
  const [modalCategory, setModalCategory] = useState('feats');
  const [modalTitle, setModalTitle] = useState('Avantaj Seçin');

  const totalPowerPointsAvailable = pl * 15;

  const getPowerPointsSpent = () => {
    let spent = 0;
    
    // Abilities cost (2 PP per rank)
    Object.entries(abilities).forEach(([key, val]) => {
      if (key !== 'power_points') {
        spent += val * 2;
      }
    });

    // Defenses cost (1 PP per rank)
    Object.values(defenses).forEach(val => {
      spent += parseInt(val) || 0;
    });

    // Skills cost (0.5 PP per rank)
    let totalSkillRanks = 0;
    Object.values(skills).forEach(val => {
      totalSkillRanks += parseInt(val) || 0;
    });
    spent += Math.ceil(totalSkillRanks / 2);

    // Advantages cost (1 PP each standard)
    spent += advantages.length;

    // Powers cost (cost sum)
    Object.values(powers).forEach(p => {
      spent += p.cost || 0;
    });

    return spent;
  };

  const remainingPowerPoints = totalPowerPointsAvailable - getPowerPointsSpent();

  const adjustAbilityScore = (ab, delta) => {
    const current = abilities[ab] || 0;
    const next = current + delta;
    if (next < -5 || next > pl + 2) return;
    updateAbility(ab, next);
  };

  const adjustDefenseScore = (def, delta) => {
    const current = defenses[def] || 0;
    const next = current + delta;
    if (next < 0 || next > pl + 2) return;
    updateDefense(def, next);
  };

  const adjustSkillRankScore = (skill, delta) => {
    const current = skills[skill] || 0;
    const next = current + delta;
    if (next < 0 || next > pl + 10) return;
    updateSkillRank(skill, next);
  };

  const handleOpenSelector = (category, title) => {
    setModalCategory(category);
    setModalTitle(title);
    setModalOpen(true);
  };

  const handleSelectEntity = (entity) => {
    if (modalCategory === 'feats') {
      addAdvantage(entity.isim);
    } else if (modalCategory === 'powers') {
      const powerCost = entity.sistem_verisi?.base_cost || 2;
      addPower(entity.isim, {
        name: entity.isim,
        cost: powerCost,
        effects: entity.sistem_verisi?.effects || [],
        description: entity.aciklama
      });
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
    { key: 'strength', label: 'STR (Strength)' },
    { key: 'stamina', label: 'STA (Stamina)' },
    { key: 'agility', label: 'AGI (Agility)' },
    { key: 'dexterity', label: 'DEX (Dexterity)' },
    { key: 'fighting', label: 'FGT (Fighting)' },
    { key: 'intellect', label: 'INT (Intellect)' },
    { key: 'awareness', label: 'AWR (Awareness)' },
    { key: 'presence', label: 'PRE (Presence)' }
  ];

  const defenseList = [
    { key: 'dodge', label: 'Dodge (Agility)' },
    { key: 'parry', label: 'Parry (Fighting)' },
    { key: 'fortitude', label: 'Fortitude (Stamina)' },
    { key: 'toughness', label: 'Toughness (Stamina)' },
    { key: 'will', label: 'Will (Awareness)' }
  ];

  const mmSkillsList = [
    "Acrobatics", "Athletics", "Close Combat", "Deception", "Expertise",
    "Insight", "Intimidation", "Investigation", "Perception", "Persuasion",
    "Ranged Combat", "Sleight of Hand", "Stealth", "Technology", "Treatment", "Vehicles"
  ];

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

        <div className="form-group" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <label className="form-label">Güç Seviyesi (PL)</label>
            <span style={{ fontWeight: 'bold', color: '#c9a84c' }}>PL {pl}</span>
          </div>
          <input 
            type="range" 
            min={1} 
            max={20} 
            value={pl} 
            onChange={(e) => updateField('pl_value', parseInt(e.target.value) || 10)}
            style={{ width: '100%', accentColor: '#c9a84c', cursor: 'pointer' }}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Arketip (Archetype)</label>
          <select value={archetype} onChange={(e) => updateField('archetype', e.target.value)} className="form-select">
            <option value="Özel (Custom)">Özel (Custom)</option>
            <option value="Battlesuit">Battlesuit</option>
            <option value="Crime Fighter">Crime Fighter</option>
            <option value="Speedster">Speedster</option>
            <option value="Powerhouse">Powerhouse</option>
            <option value="Psionic">Psionic</option>
          </select>
        </div>
      </div>

      {/* Power Points Tracker */}
      <div className="glass-card" style={{ textAlign: 'center', border: remainingPowerPoints >= 0 ? '1px solid rgba(201, 168, 76, 0.3)' : '2px solid var(--color-ruby)' }}>
        <div style={{ fontSize: '13px', textTransform: 'uppercase', color: '#8b949e', marginBottom: '8px', fontWeight: 'bold' }}>
          Power Points Dengesi
        </div>
        <div style={{ fontSize: '2.5rem', fontWeight: '800', color: remainingPowerPoints >= 0 ? '#c9a84c' : '#e94560' }}>
          {remainingPowerPoints}
        </div>
        <div style={{ fontSize: '13px', color: '#d4c5a9', marginTop: '4px' }}>
          Harcanan: <b>{getPowerPointsSpent()}</b> / Toplam: <b>{totalPowerPointsAvailable}</b> PP
        </div>
      </div>

      {/* Abilities grid */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.2rem', marginBottom: '16px' }}>Yetenek Seviyeleri (Abilities)</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {abilitiesList.map(ab => {
            const val = abilities[ab.key] || 0;
            return (
              <div key={ab.key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)', padding: '8px 16px', borderRadius: '8px' }}>
                <div>
                  <div className="ability-name" style={{ fontSize: '12px', marginBottom: '0' }}>{ab.label}</div>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>Maliyet: {val * 2} PP</div>
                </div>
                <div className="ability-value-row">
                  <button className="ability-btn" style={{ width: '24px', height: '24px' }} onClick={() => adjustAbilityScore(ab.key, -1)}>-</button>
                  <span className="ability-score" style={{ fontSize: '1.2rem' }}>{val}</span>
                  <button className="ability-btn" style={{ width: '24px', height: '24px' }} onClick={() => adjustAbilityScore(ab.key, 1)}>+</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Defenses buying */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.2rem', marginBottom: '16px' }}>Savunma Rütbeleri (Defenses)</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {defenseList.map(def => {
            const val = defenses[def.key] || 0;
            return (
              <div key={def.key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)', padding: '8px 16px', borderRadius: '8px' }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 'bold' }}>{def.label}</div>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>Maliyet: {val} PP</div>
                </div>
                <div className="ability-value-row">
                  <button className="ability-btn" style={{ width: '22px', height: '22px', fontSize: '12px' }} onClick={() => adjustDefenseScore(def.key, -1)}>-</button>
                  <span className="ability-score" style={{ fontSize: '1.1rem' }}>{val}</span>
                  <button className="ability-btn" style={{ width: '22px', height: '22px', fontSize: '12px' }} onClick={() => adjustDefenseScore(def.key, 1)}>+</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Skills buying */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.2rem', marginBottom: '16px' }}>Beceri Dereceleri (Skills)</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '200px', overflowY: 'auto', paddingRight: '4px' }}>
          {mmSkillsList.map(skill => {
            const val = skills[skill] || 0;
            return (
              <div key={skill} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 12px', background: 'rgba(255,255,255,0.01)', border: '1px solid rgba(255,255,255,0.03)', borderRadius: '6px' }}>
                <div>
                  <span style={{ fontSize: '13px' }}>{skill}</span>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>Mod limit: {pl + 10}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button className="ability-btn" style={{ width: '20px', height: '20px', fontSize: '11px' }} onClick={() => adjustSkillRankScore(skill, -1)}>-</button>
                  <span style={{ fontSize: '13px', fontWeight: 'bold', minWidth: '16px', textAlign: 'center' }}>{val}</span>
                  <button className="ability-btn" style={{ width: '20px', height: '20px', fontSize: '11px' }} onClick={() => adjustSkillRankScore(skill, 1)}>+</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Advantages Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
          <h3 style={{ fontSize: '1.2rem' }}>Avantajlar</h3>
          <button className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '11px', minHeight: 'unset' }} onClick={() => handleOpenSelector('feats', 'Avantaj Ekle')}>
            <Plus size={12} /> Ekle
          </button>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {advantages.length === 0 ? (
            <div style={{ fontSize: '12px', color: '#8b949e', width: '100%', textAlign: 'center', padding: '12px' }}>Avantaj seçilmedi.</div>
          ) : (
            advantages.map(adv => (
              <span key={adv} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '12px', background: '#16213e', border: '1px solid rgba(201,168,76,0.2)', padding: '2px 8px', borderRadius: '4px' }}>
                {adv}
                <button onClick={() => removeAdvantage(adv)} style={{ background: 'transparent', border: 'none', color: '#e94560', cursor: 'pointer', fontSize: '10px', fontWeight: 'bold' }}>×</button>
              </span>
            ))
          )}
        </div>
      </div>

      {/* Powers Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
          <h3 style={{ fontSize: '1.2rem' }}>Özel Güçler</h3>
          <button className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '11px', minHeight: 'unset' }} onClick={() => handleOpenSelector('powers', 'Güç Ekle')}>
            <Plus size={12} /> Ekle
          </button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '180px', overflowY: 'auto' }}>
          {Object.keys(powers).length === 0 ? (
            <div style={{ fontSize: '13px', color: '#8b949e', textAlign: 'center', padding: '12px' }}>Karakterin henüz özel gücü yok.</div>
          ) : (
            Object.entries(powers).map(([pName, pData]) => (
              <div key={pName} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 12px', background: '#16213e', borderRadius: '6px' }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 'bold' }}>{pName}</div>
                  <div style={{ fontSize: '10px', color: '#c9a84c' }}>Maliyet: {pData.cost} PP</div>
                </div>
                <button 
                  className="btn btn-danger" 
                  style={{ padding: '3px 6px', minHeight: 'unset', border: 'none' }}
                  onClick={() => removePower(pName)}
                >
                  <Trash size={12} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Equipment Selection */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
          <h3 style={{ fontSize: '1.2rem' }}>Cihaz & Ekipman</h3>
          <button className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '11px', minHeight: 'unset' }} onClick={() => handleOpenSelector('equipment', 'Cihaz Ekle')}>
            <Plus size={12} /> Ekle
          </button>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '150px', overflowY: 'auto' }}>
          {recalcedData.equipment?.length === 0 ? (
            <div style={{ fontSize: '13px', color: '#8b949e', textAlign: 'center', padding: '12px' }}>Ekipman çantası boş.</div>
          ) : (
            recalcedData.equipment?.map((item, index) => (
              <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 12px', background: '#16213e', borderRadius: '6px' }}>
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 'bold' }}>{item.name}</div>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>
                    Toughness: +{item.sistem_verisi?.toughness || item.sistem_verisi?.armor_toughness || 0}
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
        system="mnm" 
        category={modalCategory} 
        title={modalTitle} 
        onSelect={handleSelectEntity} 
      />

    </div>
  );
}
