import React, { useState } from 'react';
import { Plus, Trash2, WandSparkles, ShieldCheck, ShieldAlert, Sparkles } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';

const STAT_OPTIONS = [
  ['ac', '🛡 Armor Class (AC)'],
  ['hp', '❤️ Hit Points (HP)'],
  ['bab', '⚔ Base Attack Bonus (BAB)'],
  ['fortitude', '🏰 Fortitude Save'],
  ['reflex', '⚡ Reflex Save'],
  ['will', '🔮 Will Save']
];

export default function GMModifierPanel() {
  const store = useCharacterStore();
  const { customModifiers, addCustomModifier, removeCustomModifier, is_overridden, updateField } = store;
  const [stat, setStat] = useState('ac');
  const [value, setValue] = useState(1);
  const [name, setName] = useState('GM Masa Kuralı');

  const add = () => {
    if (!name.trim() || !Number.isInteger(Number(value)) || Number(value) === 0) return;
    addCustomModifier({ stat, value: Number(value), name: name.trim(), is_active: true });
    setValue(1);
    setName('GM Masa Kuralı');
  };

  const toggleOverride = () => {
    updateField('is_overridden', !is_overridden);
  };

  return (
    <section className="glass-card animate-fade-in" style={{
      background: 'rgba(15, 15, 26, 0.95)',
      border: '1px solid var(--accent-gold)',
      boxShadow: '0 0 20px rgba(201, 168, 76, 0.12)',
      borderRadius: '10px',
      padding: '16px 18px',
      marginBottom: '16px'
    }} aria-label="Game Master değiştiricileri">
      
      {/* Header bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', borderBottom: '1px solid rgba(201, 168, 76, 0.2)', paddingBottom: '10px' }}>
        <h3 style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: '1.1rem', color: '#f0e6d2', margin: 0, fontFamily: 'Cinzel, serif' }}>
          <WandSparkles size={18} style={{ color: 'var(--accent-gold)' }} />
          GM Modifikatörleri & Rule Override
        </h3>

        {/* GM Override Switch Button */}
        <button
          type="button"
          onClick={toggleOverride}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 12px',
            fontSize: '0.75rem',
            fontWeight: 'bold',
            borderRadius: '16px',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            background: is_overridden ? 'rgba(82, 183, 136, 0.2)' : 'rgba(201, 168, 76, 0.1)',
            border: `1px solid ${is_overridden ? '#52b788' : 'var(--accent-gold)'}`,
            color: is_overridden ? '#52b788' : '#d4c5a9'
          }}
          title="Tüm soft-validation önkoşul uyarılarını GM izniyle onaylar/ezar"
        >
          {is_overridden ? <ShieldCheck size={14} /> : <ShieldAlert size={14} />}
          {is_overridden ? 'GM İzni Aktif (Overridden)' : 'GM İzniyle Ez (Override)'}
        </button>
      </div>

      <p style={{ color: '#8b949e', fontSize: '0.78rem', marginTop: 0, marginBottom: '12px' }}>
        Masa kuralları, geçici büyü buff/debuff etkileri veya özel stat modifikatörlerini (+X / -X) canlı hesaplamaya ekleyin.
      </p>

      {/* Input controls grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 80px 1.5fr auto', gap: '8px', marginBottom: '14px' }}>
        <select
          className="form-select"
          value={stat}
          onChange={(e) => setStat(e.target.value)}
          style={{ background: '#0f0f1a', color: '#f0e6d2', border: '1px solid rgba(251,241,210,0.2)', fontSize: '0.8rem', borderRadius: '6px' }}
        >
          {STAT_OPTIONS.map(([key, label]) => <option key={key} value={key}>{label}</option>)}
        </select>

        <input
          className="form-input"
          type="number"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          style={{ background: '#0f0f1a', color: '#f0e6d2', border: '1px solid rgba(251,241,210,0.2)', textAlign: 'center', fontSize: '0.85rem', fontWeight: 'bold', borderRadius: '6px' }}
          aria-label="Modifikatör değeri"
        />

        <input
          className="form-input"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Açıklama (örn: Blessing, Curse)..."
          style={{ background: '#0f0f1a', color: '#f0e6d2', border: '1px solid rgba(251,241,210,0.2)', fontSize: '0.8rem', borderRadius: '6px' }}
          aria-label="Modifikatör açıklaması"
        />

        <button
          type="button"
          className="btn btn-secondary"
          onClick={add}
          style={{ background: 'var(--accent-gold)', color: '#0f0f1a', border: 'none', fontWeight: 'bold', padding: '0 12px', borderRadius: '6px', cursor: 'pointer' }}
          title="Modifikatör Ekle"
        >
          <Plus size={16} />
        </button>
      </div>

      {/* Active Modifiers List */}
      {(customModifiers || []).length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {customModifiers.map((modifier, index) => {
            const isPositive = Number(modifier.value) > 0;
            return (
              <div
                key={`${modifier.name}-${index}`}
                style={{
                  display: 'flex',
                  justify: 'space-between',
                  alignItems: 'center',
                  padding: '6px 10px',
                  borderRadius: '6px',
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.07)',
                  fontSize: '0.8rem'
                }}
              >
                <span style={{ color: '#d4c5a9', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Sparkles size={12} style={{ color: 'var(--accent-gold)' }} />
                  {modifier.name}:
                </span>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{
                    padding: '2px 8px',
                    borderRadius: '10px',
                    fontWeight: 'bold',
                    fontSize: '0.75rem',
                    background: isPositive ? 'rgba(82, 183, 136, 0.15)' : 'rgba(232, 112, 112, 0.15)',
                    color: isPositive ? '#52b788' : '#e87070',
                    border: `1px solid ${isPositive ? 'rgba(82, 183, 136, 0.3)' : 'rgba(232, 112, 112, 0.3)'}`
                  }}>
                    {isPositive ? '+' : ''}{modifier.value} {modifier.stat.toUpperCase()}
                  </span>

                  <button
                    type="button"
                    onClick={() => removeCustomModifier(index)}
                    style={{ border: 0, background: 'none', color: '#e87070', cursor: 'pointer', opacity: 0.8, padding: 0 }}
                    aria-label={`${modifier.name} sil`}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

