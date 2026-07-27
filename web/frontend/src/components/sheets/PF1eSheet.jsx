import React, { useEffect, useState } from 'react';
import { useCharacterStore } from '../../store/characterStore';
import PF1eControls from './controls/PF1eControls';
import PF1eLiveSheet from './displays/PF1eLiveSheet';
import LevelUpWizard from './LevelUpWizard';
import { AlertTriangle, Sparkles, History, FileDown } from 'lucide-react';

export default function PF1eSheet({ character, onSave, onCancel }) {
  const { 
    id, initCharacter, name, system, level, abilities, recalcedData, warnings, loading, levelUndo, exportPdf 
  } = useCharacterStore();

  const [wizardOpen, setWizardOpen] = useState(false);

  // Initialize character store on mount
  useEffect(() => {
    initCharacter('pf1e', character);
  }, [character]);

  const handleLevelUndo = async () => {
    if (window.confirm('Son seviye ilerlemesini geri almak istediğinizden emin misiniz? Bu işlem geri alınamaz.')) {
      await levelUndo();
    }
  };

  const handleSave = () => {
    const state = useCharacterStore.getState();
    const fullData = {
      ...state.recalcedData,
      abilities: state.abilities,
      race: state.race,
      class: state.class,
      level: state.level,
      race_data: state.raceData,
      class_data: state.classData,
      skill_ranks: state.skills,
      feat: state.feat,
      equipment: state.equipment,
      custom_modifiers: state.customModifiers,
      portrait: state.portrait
    };
    
    onSave({
      name: state.name,
      system: 'pf1e',
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
          <p style={{ color: '#8b949e', fontSize: '13px' }}>Pathfinder 1st Edition Kuralları</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          {id && (
            <>
              <button 
                className="btn btn-secondary" 
                onClick={handleLevelUndo} 
                style={{ borderColor: 'rgba(233, 69, 96, 0.4)', color: 'var(--color-ruby)', display: 'flex', alignItems: 'center', gap: '4px' }}
                disabled={level <= 1 || loading}
                title="Son Seviye Seçimlerini Geri Al"
              >
                <History size={14} /> Geri Al
              </button>
              <button 
                className="btn btn-primary" 
                onClick={() => setWizardOpen(true)}
                style={{ borderColor: 'var(--accent-gold)', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: '4px' }}
                disabled={level >= 20 || loading}
              >
                <Sparkles size={14} /> Seviye Atla
              </button>
              <button 
                className="btn btn-secondary"
                onClick={exportPdf}
                disabled={loading}
                title="Karakter sayfasını PDF olarak indir"
                style={{ borderColor: 'rgba(63, 185, 80, 0.4)', color: '#3fb950', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                <FileDown size={14} /> PDF İndir
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
          <h4 className="warnings-title"><AlertTriangle size={18} /> Kural Uyuşmazlığı Uyarıları ({warnings.length})</h4>
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
          <PF1eControls />
        </div>
        <div>
          <PF1eLiveSheet />
        </div>
      </div>

      {/* Level Up Wizard Modal */}
      <LevelUpWizard isOpen={wizardOpen} onClose={() => setWizardOpen(false)} />

    </div>
  );
}
