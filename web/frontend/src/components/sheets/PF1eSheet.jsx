import React, { useEffect, useState } from 'react';
import { useCharacterStore } from '../../store/characterStore';
import PF1eControls from './controls/PF1eControls';
import PF1eLiveSheet from './displays/PF1eLiveSheet';
import LevelUpWizard from './LevelUpWizard';
import { AlertTriangle, Sparkles, History, FileDown, Save, ArrowLeft } from 'lucide-react';

export default function PF1eSheet({ character, onSave, onCancel }) {
  const { 
    id, initCharacter, name, system, level, abilities, recalcedData, warnings, loading, levelUndo, exportPdf, portrait 
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
    <div className="tab-content" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* High-Fantasy Top Bar */}
      <div className="dark-panel corner-ornament" style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap',
        gap: '16px', padding: '16px 20px', borderRadius: '4px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {portrait && (
            <div style={{
              width: '52px',
              height: '52px',
              borderRadius: '10px',
              overflow: 'hidden',
              border: '2px solid var(--gold-bright)',
              boxShadow: '0 0 12px rgba(201,168,76,0.35)',
              flexShrink: 0,
              background: '#0a0814'
            }}>
              <img src={portrait} alt="Karakter Portresi" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            </div>
          )}
          <div>
            <h2 className="shimmer-text" style={{ fontSize: '1.4rem', fontFamily: 'Cinzel Decorative, Cinzel, serif', margin: 0 }}>
              {id ? `${name || 'Karakter'} — Düzenle` : 'Yeni Kahraman Yarat'}
            </h2>
            <div style={{ color: 'var(--gold-dim)', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', letterSpacing: '0.08em', marginTop: '2px' }}>
              Pathfinder 1st Edition · Diyargezen Character Forge
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          {id && (
            <>
              <button 
                className="crimson-btn" 
                onClick={handleLevelUndo} 
                disabled={level <= 1 || loading}
                title="Son Seviye Seçimlerini Geri Al"
              >
                <History size={13} /> Geri Al
              </button>
              <button 
                className="gold-btn primary" 
                onClick={() => setWizardOpen(true)}
                disabled={level >= 20 || loading}
              >
                <Sparkles size={13} /> Seviye Atla
              </button>
              <button 
                className="gold-btn"
                onClick={exportPdf}
                disabled={loading}
                title="Karakter sayfasını PDF olarak indir"
              >
                <FileDown size={13} /> PDF İndir
              </button>
            </>
          )}
          <button className="gold-btn" onClick={onCancel}>
            <ArrowLeft size={13} /> Geri Dön
          </button>
          <button className="gold-btn primary" onClick={handleSave} disabled={loading}>
            <Save size={13} /> Karakteri Kaydet
          </button>
        </div>
      </div>

      {/* Warnings Panel */}
      {warnings.length > 0 && (
        <div style={{
          background: 'rgba(110,16,16,0.2)', border: '1px solid var(--border-crimson)',
          borderRadius: '4px', padding: '12px 16px', color: '#e87070'
        }}>
          <h4 style={{ fontSize: '0.9rem', margin: '0 0 6px', display: 'flex', alignItems: 'center', gap: '8px', color: '#e87070' }}>
            <AlertTriangle size={16} /> Kural Uyuşmazlığı Uyarıları ({warnings.length})
          </h4>
          <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.8rem' }}>
            {warnings.map((warn, i) => (
              <li key={i}>{warn}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Split panel grid: left side controls (560px), right side live sheet (1fr) */}
      <div style={{ display: 'grid', gridTemplateColumns: '560px 1fr', gap: '20px', alignItems: 'start' }}>
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
