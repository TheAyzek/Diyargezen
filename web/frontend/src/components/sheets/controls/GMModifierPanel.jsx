import React, { useState } from 'react';
import { Plus, Trash2, WandSparkles } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';

const STAT_OPTIONS = [['ac', 'AC'], ['hp', 'HP'], ['bab', 'BAB'], ['fortitude', 'Fortitude'], ['reflex', 'Reflex'], ['will', 'Will']];

export default function GMModifierPanel() {
  const { customModifiers, addCustomModifier, removeCustomModifier } = useCharacterStore();
  const [stat, setStat] = useState('ac');
  const [value, setValue] = useState(1);
  const [name, setName] = useState('GM etkisi');
  const add = () => {
    if (!name.trim() || !Number.isInteger(Number(value)) || Number(value) === 0) return;
    addCustomModifier({ stat, value: Number(value), name: name.trim(), is_active: true });
    setValue(1);
  };
  return <section className="glass-card" aria-label="Game Master değiştiricileri">
    <h3 style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: '1.1rem', marginBottom: 12 }}><WandSparkles size={16} style={{ color: 'var(--accent-gold)' }} /> GM Modifikatörleri</h3>
    <p style={{ color: '#8b949e', fontSize: 12, marginTop: 0 }}>Buff, debuff veya masa kuralını görünür bir +X/−X kaydı olarak ekleyin.</p>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 72px 1.3fr auto', gap: 6 }}>
      <select className="form-select" value={stat} onChange={(e) => setStat(e.target.value)}>{STAT_OPTIONS.map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select>
      <input className="form-input" type="number" value={value} onChange={(e) => setValue(e.target.value)} aria-label="Modifikatör değeri" />
      <input className="form-input" value={name} onChange={(e) => setName(e.target.value)} aria-label="Modifikatör açıklaması" />
      <button type="button" className="btn btn-secondary" onClick={add} title="Modifikatör ekle"><Plus size={15} /></button>
    </div>
    {(customModifiers || []).map((modifier, index) => <div key={`${modifier.name}-${index}`} style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 12 }}>
      <span>{modifier.name}: <b>{modifier.value > 0 ? '+' : ''}{modifier.value} {modifier.stat.toUpperCase()}</b></span>
      <button type="button" onClick={() => removeCustomModifier(index)} style={{ border: 0, background: 'none', color: 'var(--color-ruby)', cursor: 'pointer' }} aria-label={`${modifier.name} sil`}><Trash2 size={14} /></button>
    </div>)}
  </section>;
}
