import React from 'react';
import { Shield, Sword, Sparkles, Activity } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';

export default function MM3eLiveSheet() {
  const { name, pl_value: pl, archetype, advantages, powers, recalcedData, portrait, exportPdf } = useCharacterStore();

  const abilities = [
    { name: 'Strength', label: 'STR' },
    { name: 'Stamina', label: 'STA' },
    { name: 'Agility', label: 'AGI' },
    { name: 'Dexterity', label: 'DEX' },
    { name: 'Fighting', label: 'FGT' },
    { name: 'Intellect', label: 'INT' },
    { name: 'Awareness', label: 'AWR' },
    { name: 'Presence', label: 'PRE' }
  ];

  const derivedMods = recalcedData.ability_modifiers || {};
  const defenses = recalcedData.defenses || {};
  const skills = recalcedData.skills || {};

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
      
      {/* Mutants & Masterminds Header */}
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
            <h2 style={{ fontSize: '1.8rem', color: '#f0e6d2', margin: 0 }}>{name}</h2>
            <span style={{ fontSize: '12px', color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '1px' }}>M&M 3e Canlı Karakter Kağıdı</span>
            <button className="btn btn-secondary" style={{ marginTop: '4px', padding: '4px 8px', fontSize: '11px', minHeight: 'unset', display: 'flex', alignItems: 'center', gap: '4px', width: 'fit-content' }} onClick={exportPdf}>
              📄 PDF Olarak Dışa Aktar
            </button>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '4px', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
          <div>Güç Seviyesi (Power Level): <b>PL {pl}</b></div>
          <div>Arketip: <b>{archetype || 'Özel (Custom)'}</b></div>
        </div>
      </div>

      {/* Combat Bonuses Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '16px' }}>
        
        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
          <Sparkles size={20} style={{ color: 'var(--accent-gold)', marginBottom: '6px' }} />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Initiative</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 'bold' }}>+{recalcedData.initiative || 0}</div>
        </div>

        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
          <Sword size={20} style={{ color: '#e94560', marginBottom: '6px' }} />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Melee Attack</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 'bold' }}>+{recalcedData.melee_attack || 0}</div>
        </div>

        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
          <Activity size={20} style={{ color: '#3fb950', marginBottom: '6px' }} />
          <div style={{ fontSize: '10px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Ranged Attack</div>
          <div style={{ fontSize: '1.6rem', fontWeight: 'bold' }}>+{recalcedData.ranged_attack || 0}</div>
        </div>

      </div>

      {/* Main layout grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
        
        {/* Abilities column (M&M: rank = modifier) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {abilities.map(ab => {
            const score = derivedMods[ab.name] || 0;
            return (
              <div key={ab.name} style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '8px 12px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', fontWeight: 'bold' }}>{ab.label}</span>
                <span style={{ fontSize: '18px', fontWeight: '800', color: 'var(--accent-gold)' }}>{score >= 0 ? `+${score}` : score}</span>
              </div>
            );
          })}
        </div>

        {/* Defenses, Skills, Advantages */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Defenses totals display */}
          <div>
            <h4 style={{ fontSize: '1rem', color: '#f0e6d2', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '4px', marginBottom: '8px' }}>
              Nihai Savunmalar (Defenses Totals)
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              {Object.entries(defenses).map(([def, val]) => (
                <div key={def} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 12px', background: '#16213e', borderRadius: '6px', fontSize: '13px' }}>
                  <span>{def}</span>
                  <span style={{ fontWeight: 'bold', color: 'var(--accent-gold)' }}>{val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Recalculated Skills */}
          <div>
            <h4 style={{ fontSize: '1rem', color: '#f0e6d2', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '4px', marginBottom: '8px' }}>
              Nihai Beceriler (Skills Modifiers)
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', maxHeight: '180px', overflowY: 'auto', paddingRight: '4px' }}>
              {skills && Object.entries(skills).map(([skill, val]) => (
                <div key={skill} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 8px', background: 'rgba(255,255,255,0.01)', borderRadius: '4px', fontSize: '13px' }}>
                  <span style={{ color: 'var(--color-text-secondary)' }}>{skill}</span>
                  <span style={{ fontWeight: 'bold' }}>+{val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Advantages display */}
          {advantages.length > 0 && (
            <div>
              <h4 style={{ fontSize: '1rem', color: '#f0e6d2', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '4px', marginBottom: '8px' }}>
                Seçili Avantajlar (Advantages Ledger)
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {advantages.map(adv => (
                  <span key={adv} style={{ fontSize: '11px', background: 'var(--bg-ink)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    {adv}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Custom Powers display */}
          {Object.keys(powers).length > 0 && (
            <div>
              <h4 style={{ fontSize: '1rem', color: '#f0e6d2', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '4px', marginBottom: '8px' }}>
                Aktif Süper Güçler
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {Object.entries(powers).map(([pName, pData]) => (
                  <div key={pName} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 12px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '6px', fontSize: '13px' }}>
                    <span>{pName}</span>
                    <span style={{ fontWeight: 'bold', color: 'var(--accent-gold)' }}>{pData.cost} PP</span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}
