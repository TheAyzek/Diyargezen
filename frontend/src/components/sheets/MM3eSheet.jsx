import React, { useEffect, useState } from 'react';
import { useCharacterStore } from '../../store/characterStore';
import MM3eControls from './controls/MM3eControls';
import MM3eLiveSheet from './displays/MM3eLiveSheet';
import LevelUpWizard from './LevelUpWizard';
import { AlertTriangle, Sparkles, History } from 'lucide-react';

export default function MM3eSheet({ character, onSave, onCancel }) {
  const { id, initCharacter, name, level, pl_value, abilities, defenses, recalcedData, warnings, loading, levelUndo } = useCharacterStore();
  const [wizardOpen, setWizardOpen] = useState(false);

  // Initialize character store on mount
  useEffect(() => {
    initCharacter('mnm', character);
  }, [character]);

  const handleLevelUndo = async () => {
    if (window.confirm('Son Güç Seviyesi artışını geri almak istediğinizden emin misiniz? Bu işlem geri alınamaz.')) {
      await levelUndo();
    }
  };

  const handleSave = () => {
    const state = useCharacterStore.getState();
    const fullData = {
      ...state.recalcedData,
      abilities: state.abilities,
      defenses: {
        Dodge: state.defenses.dodge || 0,
        Parry: state.defenses.parry || 0,
        Fortitude: state.defenses.fortitude || 0,
        Toughness: state.defenses.toughness || 0,
        Will: state.defenses.will || 0
      },
      skill_ranks: state.skills,
      advantages: state.advantages,
      powers: state.powers,
      pl_value: state.pl_value,
      remaining_power_points: state.recalcedData.remaining_power_points,
      archetype: state.archetype,
      equipment: state.equipment,
      portrait: state.portrait
    };
    
    onSave({
      name: state.name,
      system: 'mnm',
      data: fullData
    });
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Header Save Bar */}
      <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', borderRadius: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', color: 'var(--accent-gold)' }}>
            {id ? 'Karakteri Düzenle' : 'Yeni Karakter Yarat'}
          </h2>
          <p style={{ color: '#8b949e', fontSize: '13px' }}>Mutants & Masterminds 3rd Edition Kuralları</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {id && (
            <>
              <button 
                className="btn btn-secondary" 
                onClick={handleLevelUndo} 
                style={{ borderColor: 'rgba(233, 69, 96, 0.4)', color: 'var(--color-ruby)', display: 'flex', alignItems: 'center', gap: '4px' }}
                disabled={level <= 1 || loading}
                title="Son Güç Seviyesi İlerlemesini Geri Al"
              >
                <History size={14} /> Geri Al
              </button>
              <button 
                className="btn btn-primary" 
                onClick={() => setWizardOpen(true)}
                style={{ borderColor: 'var(--accent-gold)', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: '4px' }}
                disabled={level >= 20 || loading}
              >
                <Sparkles size={14} /> PL Yükselt
              </button>
            </>
          )}
          <button className="btn btn-secondary" onClick={onCancel}>İptal</button>
          <button className="btn btn-primary" onClick={handleSave} disabled={loading}>Kaydet</button>
        </div>
      </div>

      {/* Warnings Panel */}
      {warnings.length > 0 && (
        <div className="warnings-panel">
          <h4 className="warnings-title"><AlertTriangle size={18} /> Güç Seviyesi ve PP Sınırı İhlalleri ({warnings.length})</h4>
          <ul>
            {warnings.map((warn, i) => (
              <li key={i} className="warning-item">{warn}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Split panel grid: left side controls, right side live sheet */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', alignItems: 'start' }}>
        <div>
          <MM3eControls />
        </div>
        <div>
          <MM3eLiveSheet />
        </div>
      </div>

      {/* Level Up Wizard Modal */}
      <LevelUpWizard isOpen={wizardOpen} onClose={() => setWizardOpen(false)} />

    </div>
  );
}
