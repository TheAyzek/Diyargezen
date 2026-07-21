import React from 'react';
import { Shield, Sword, Heart, Star, Sparkles } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';

export default function DND5eLiveSheet() {
  const { name, level, race, class: charClass, background, recalcedData, exportPdf, portrait } = useCharacterStore();

  const abilities = [
    { name: 'Strength', label: 'STR' },
    { name: 'Dexterity', label: 'DEX' },
    { name: 'Constitution', label: 'CON' },
    { name: 'Intelligence', label: 'INT' },
    { name: 'Wisdom', label: 'WIS' },
    { name: 'Charisma', label: 'CHA' }
  ];

  const derivedScores = recalcedData.ability_scores || {};
  const derivedMods = recalcedData.ability_modifiers || {};
  const savingThrows = recalcedData.saving_throws || {};
  const skills = recalcedData.skills || {};
  const proficientSkills = recalcedData.proficient_skills || [];

  return (
    <div className="glass-card" style={{ 
      borderColor: 'var(--accent-gold)', 
      background: 'rgba(15, 15, 26, 0.85)',
      boxShadow: '0 0 25px rgba(201, 168, 76, 0.15)',
      padding: '30px',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      borderRadius: '12px'
    }}>
      
      {/* Official RPG Sheet Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        borderBottom: '2px solid var(--accent-gold)', 
        paddingBottom: '16px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          {portrait && (
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '8px',
              border: '2px solid var(--accent-gold)',
              overflow: 'hidden',
              boxShadow: '0 0 10px rgba(201, 168, 76, 0.3)',
              background: '#0f0f1a'
            }}>
              <img src={portrait} alt="Portrait" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            </div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <h2 style={{ fontSize: '1.8rem', color: '#f0e6d2', textShadow: '0 0 8px rgba(240, 230, 210, 0.2)', margin: 0 }}>{name}</h2>
            <span style={{ fontSize: '12px', color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '1px' }}>Karakter Canlı Kağıdı</span>
            <button className="btn btn-secondary" style={{ marginTop: '4px', padding: '4px 8px', fontSize: '11px', minHeight: 'unset', display: 'flex', alignItems: 'center', gap: '4px', width: 'fit-content' }} onClick={exportPdf}>
              📄 PDF Olarak Dışa Aktar
            </button>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
          <div>Sınıf & Seviye: <b>{charClass || 'Seçilmedi'} (Seviye {level})</b></div>
          <div>Irk: <b>{race || 'Seçilmedi'}</b></div>
          <div>Arka Plan: <b>{background || 'Seçilmedi'}</b></div>
          <div>Deneyim: <b>0 XP</b></div>
        </div>
      </div>

      {/* Derived Stat Shields Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '16px' }}>
        
        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
          <Heart size={20} style={{ color: '#e94560', marginBottom: '6px' }} />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Hit Points</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 'bold' }}>{recalcedData.hit_points || 10}</div>
        </div>

        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
          <Shield size={20} style={{ color: '#3fb950', marginBottom: '6px' }} />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Armor Class</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 'bold' }}>{recalcedData.armor_class || 10}</div>
        </div>

        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
          <Sword size={20} style={{ color: 'var(--accent-gold)', marginBottom: '6px' }} />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Initiative</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 'bold' }}>
            {recalcedData.initiative >= 0 ? `+${recalcedData.initiative}` : recalcedData.initiative || 0}
          </div>
        </div>

        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
          <Star size={20} style={{ color: 'var(--accent-gold)', marginBottom: '6px' }} />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Proficiency</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 'bold' }}>+{recalcedData.proficiency_bonus || 2}</div>
        </div>

      </div>

      {/* Carrying Capacity / Encumbrance Bar */}
      {(() => {
        const totalWeight = recalcedData.total_weight || 0;
        const capacity = recalcedData.carrying_capacity || { light: 50, medium: 100, heavy: 150 };
        const loadStatus = recalcedData.encumbrance_status || 'Light';
        const pct = Math.min(100, (totalWeight / (capacity.heavy || 150)) * 100);
        return (
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '6px' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>Taşıma Yükü: <b>{totalWeight} / {capacity.heavy} lb</b></span>
              <span style={{ 
                fontWeight: 'bold', 
                color: loadStatus === 'Light' ? '#3fb950' : loadStatus === 'Medium' ? '#e9c46a' : '#e94560' 
              }}>{loadStatus.toUpperCase()} LOAD</span>
            </div>
            <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
              <div style={{ 
                width: `${pct}%`, 
                height: '100%', 
                background: loadStatus === 'Light' ? '#3fb950' : loadStatus === 'Medium' ? '#e9c46a' : '#e94560',
                transition: 'width 0.3s ease' 
              }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
              <span>Hafif Yük limit: {capacity.light} lb</span>
              <span>Ağır Yük limit: {capacity.medium} lb</span>
              <span>Kapasite: {capacity.heavy} lb</span>
            </div>
          </div>
        );
      })()}

      {/* Main Stats layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
        
        {/* Ability boxes column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {abilities.map(ab => {
            const score = derivedScores[ab.name] || 10;
            const mod = derivedMods[ab.name] || 0;
            return (
              <div 
                key={ab.name} 
                style={{ 
                  background: 'rgba(255,255,255,0.02)', 
                  border: '1px solid rgba(255,255,255,0.05)', 
                  borderRadius: '10px', 
                  padding: '10px 16px',
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  position: 'relative'
                }}
              >
                <span style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 'bold', textTransform: 'uppercase' }}>{ab.label}</span>
                <span style={{ fontSize: '20px', fontWeight: '800', color: 'var(--accent-gold)' }}>{score}</span>
                <div style={{ 
                  background: 'var(--bg-ink)', 
                  padding: '2px 8px', 
                  borderRadius: '10px', 
                  fontSize: '12px', 
                  fontWeight: 'bold', 
                  marginTop: '4px',
                  border: '1px solid rgba(255,255,255,0.05)'
                }}>
                  {mod >= 0 ? `+${mod}` : mod}
                </div>
              </div>
            );
          })}
        </div>

        {/* Saves & Skills Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Saving Throws */}
          <div>
            <h4 style={{ fontSize: '1.1rem', color: '#f0e6d2', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '6px', marginBottom: '10px' }}>
              Saving Throws
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              {abilities.map(ab => {
                const modifier = savingThrows[ab.name] || 0;
                return (
                  <div key={ab.name} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 12px', background: 'rgba(255,255,255,0.01)', border: '1px solid rgba(255,255,255,0.03)', borderRadius: '6px' }}>
                    <span style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>{ab.name}</span>
                    <span style={{ fontSize: '13px', fontWeight: 'bold' }}>{modifier >= 0 ? `+${modifier}` : modifier}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recalculated Skills lists */}
          <div>
            <h4 style={{ fontSize: '1.1rem', color: '#f0e6d2', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '6px', marginBottom: '10px' }}>
              Beceriler (Skills)
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', maxHeight: '250px', overflowY: 'auto', paddingRight: '4px' }}>
              {skills && Object.entries(skills).map(([skill, val]) => {
                const isProf = proficientSkills.includes(skill);
                return (
                  <div key={skill} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 10px', background: isProf ? 'rgba(201,168,76,0.03)' : 'transparent', borderRadius: '4px' }}>
                    <span style={{ fontSize: '13px', color: isProf ? 'var(--accent-gold)' : 'var(--color-text-secondary)' }}>
                      {isProf ? '●' : '○'} {skill}
                    </span>
                    <span style={{ fontSize: '13px', fontWeight: 'bold' }}>
                      {val >= 0 ? `+${val}` : val}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Spellcasting block */}
          {recalcedData.spell_save_dc ? (
            <div style={{ background: 'rgba(201, 168, 76, 0.05)', border: '1px solid rgba(201,168,76,0.2)', padding: '16px', borderRadius: '10px' }}>
              <h4 style={{ fontSize: '1.1rem', color: 'var(--accent-gold)', marginBottom: '10px' }}>Spellcasting Matrix</h4>
              <div style={{ display: 'flex', gap: '24px', fontSize: '13px' }}>
                <div>Spell Save DC: <b>{recalcedData.spell_save_dc}</b></div>
                <div>Spell Attack Mod: <b>+{recalcedData.proficiency_bonus + (derivedMods[recalcedData.spellcasting_ability] || 0)}</b></div>
              </div>
              {recalcedData.spell_slots && Object.keys(recalcedData.spell_slots).length > 0 && (
                <div style={{ marginTop: '12px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Mevcut Büyü Slotları</div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {Object.entries(recalcedData.spell_slots).map(([lvl, qty]) => (
                      <span key={lvl} style={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.05)', padding: '2px 6px', borderRadius: '4px', fontSize: '12px' }}>
                        Lvl {lvl}: <b>{qty}</b>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>

      </div>

      {/* Active Modifiers Engine Display */}
      <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '20px', marginTop: '10px' }}>
        <h4 style={{ fontSize: '1.1rem', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Sparkles size={16} /> Aktif Karakter Modifikatörleri
        </h4>
        
        {(!recalcedData.applied_modifiers || recalcedData.applied_modifiers.length === 0) ? (
          <p style={{ color: '#8b949e', fontSize: '13px', fontStyle: 'italic' }}>Aktif bir modifikatör bulunmamaktadır.</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px' }}>
            {recalcedData.applied_modifiers.map((mod, idx) => {
              let badgeBg = '#475569';
              if (mod.type === 'race') badgeBg = '#854d0e';
              else if (mod.type === 'feat') badgeBg = '#0369a1';
              else if (mod.type === 'trait') badgeBg = '#701a75';
              else if (mod.type === 'equipment') badgeBg = '#166534';
              
              return (
                <div key={idx} style={{ 
                  background: 'rgba(255, 255, 255, 0.02)', 
                  border: '1px solid rgba(255, 255, 255, 0.05)', 
                  borderRadius: '6px', 
                  padding: '8px 12px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ 
                      fontSize: '9px', 
                      background: badgeBg, 
                      color: '#fff', 
                      padding: '2px 6px', 
                      borderRadius: '4px',
                      textTransform: 'uppercase',
                      fontWeight: 'bold'
                    }}>{mod.type}</span>
                    <span style={{ 
                      fontWeight: 'bold', 
                      color: mod.value >= 0 ? '#3fb950' : '#f85149',
                      fontSize: '14px' 
                    }}>{mod.value >= 0 ? `+${mod.value}` : mod.value}</span>
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: '600', color: '#f0e6d2' }}>
                    {mod.source}
                  </div>
                  <div style={{ fontSize: '11px', color: '#8b949e' }}>
                    Hedef: <b>{mod.target.replace('skills.', 'Beceri: ').replace('saving_throws.', 'Kurtarma: ').toUpperCase()}</b>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
}
