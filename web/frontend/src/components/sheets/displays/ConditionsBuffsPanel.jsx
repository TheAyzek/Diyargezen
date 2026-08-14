import React, { useState } from 'react';
import { useCharacterStore } from '../../../store/characterStore';
import { 
  Zap, Sparkles, Shield, Flame, Activity, X, Plus, Check, 
  AlertTriangle, EyeOff, Link2, BatteryMedium, BatteryLow, Ghost, Lock, ArrowDownCircle, Frown, Dumbbell, Feather, Heart, Brain, Moon, Crown
} from 'lucide-react';

const CONDITIONS_PRESETS = [
  // Buffs
  { id: 'haste', name: '⚡ Acele (Haste)', category: 'buff', desc: '+1 Saldırı, +1 Dodge AC, +1 Reflex, +30 ft Hız, Ek Saldırı' },
  { id: 'bless', name: '✨ Kutsama (Bless)', category: 'buff', desc: '+1 Moral Saldırı Bonusu, Korkuya karşı +1 Save' },
  { id: 'heroism', name: '🛡️ Kahramanlık (Heroism)', category: 'buff', desc: '+2 Moral Saldırı, Save ve Yetenek Bonusu' },
  { id: 'greater_heroism', name: '👑 Büyük Kahramanlık (Greater Heroism)', category: 'buff', desc: '+4 Moral Saldırı, Save ve Yetenek Bonusu' },
  { id: 'bulls_strength', name: '💪 Boğa Gücü (Bull\'s Strength)', category: 'buff', desc: '+4 Güç Enhancement (+2 Mod)' },
  { id: 'cats_grace', name: '🐾 Kedi Zarafeti (Cat\'s Grace)', category: 'buff', desc: '+4 Çeviklik Enhancement (+2 Mod)' },
  { id: 'bears_endurance', name: '🐻 Ayı Dayanıklılığı (Bear\'s Endurance)', category: 'buff', desc: '+4 Bünye Enhancement (+2 Mod, +2 HP/Lv, +2 Fort)' },
  { id: 'foxs_cunning', name: '🦊 Tilki Kurnazlığı (Fox\'s Cunning)', category: 'buff', desc: '+4 Zeka Enhancement (+2 Mod)' },
  { id: 'owls_wisdom', name: '🦉 Baykuş Bilgeliği (Owl\'s Wisdom)', category: 'buff', desc: '+4 Bilgelik Enhancement (+2 Mod)' },
  { id: 'eagles_splendor', name: '🦅 Kartal Görkemi (Eagle\'s Splendor)', category: 'buff', desc: '+4 Karizma Enhancement (+2 Mod)' },
  { id: 'mage_armor', name: '🔮 Büyücü Zırhı (Mage Armor)', category: 'buff', desc: '+4 Zırh Bonusu (Fiziksel zırhsız)' },
  { id: 'shield_spell', name: '🛡️ Kalkan Büyüsü (Shield Spell)', category: 'buff', desc: '+4 Kalkan Bonusu (Fiziksel kalkansız)' },
  { id: 'barkskin', name: '🌲 Ağaç Kabuğu (Barkskin)', category: 'buff', desc: '+2 Doğal Zırh Enhancement' },
  { id: 'inspire_courage', name: '🎵 Cesaret Verme (Inspire Courage +2)', category: 'buff', desc: '+2 Yetkinlik Saldırı & Hasar' },
  { id: 'barbarian_rage', name: '🔥 Barbar Öfkesi (Rage)', category: 'buff', desc: '+4 STR/CON, +2 Will, -2 AC' },
  { id: 'flanking', name: '⚔️ Kıstırma Avantajı (Flanking)', category: 'buff', desc: 'Yakın dövüş saldırılarına +2 Durumsal Bonus' },

  // Debuffs
  { id: 'fatigued', name: '🥱 Yorgun (Fatigued)', category: 'debuff', desc: '-2 STR/DEX (-1 Saldırı, Hasar, AC, Reflex)' },
  { id: 'exhausted', name: '🔋 Tükenmiş (Exhausted)', category: 'debuff', desc: '-6 STR/DEX (-3 Saldırı, Hasar, AC, Reflex), Yarı Hız' },
  { id: 'sickened', name: '🤢 Midesi Bulanmış (Sickened)', category: 'debuff', desc: 'Tüm Saldırı, Hasar, Save ve Yeteneklere -2 Penaltı' },
  { id: 'shaken', name: '😨 Sarsılmış (Shaken)', category: 'debuff', desc: 'Saldırı, Save ve Yeteneklere -2 Penaltı' },
  { id: 'frightened', name: '😱 Korkmuş (Frightened)', category: 'debuff', desc: 'Saldırı, Save ve Yeteneklere -2 Penaltı (Kaçış)' },
  { id: 'entangled', name: '🕸️ Dolanmış (Entangled)', category: 'debuff', desc: '-2 Saldırı, -4 DEX, Yarı Hız' },
  { id: 'prone', name: '🛌 Yüzüstü / Yerde (Prone)', category: 'debuff', desc: '-4 Yakın Saldırı, -4 Yakın AC, +4 Menzilli AC' },
  { id: 'blinded', name: '🙈 Kör (Blinded)', category: 'debuff', desc: '-2 AC, DEX AC kaybı, -4 STR/DEX Yetenekleri ve Algı' },
  { id: 'dazzled', name: '☀️ Gözü Kamaşmış (Dazzled)', category: 'debuff', desc: '-1 Saldırı ve Algı zarları' },
  { id: 'deafened', name: '🔇 Sağır (Deafened)', category: 'debuff', desc: '-4 İnisiyatif' },
  { id: 'grappled', name: '🤼 Güreşte (Grappled)', category: 'debuff', desc: '-2 Saldırı, -4 DEX, Hareket Edemez' },
  { id: 'pinned', name: '🔒 Çivilenmiş (Pinned)', category: 'debuff', desc: '-4 AC, DEX AC kaybı, Hareket Edemez' },
  { id: 'staggered', name: '😵 Sersemlemiş (Staggered)', category: 'debuff', desc: 'Yalnızca tek standart veya hareket eylemi' },
  { id: 'stunned', name: '⚡ Şok Olmuş (Stunned)', category: 'debuff', desc: '-2 AC, DEX AC kaybı, Eylem yapamaz' }
];

export default function ConditionsBuffsPanel() {
  const store = useCharacterStore();
  const activeConditions = store.active_conditions || store.conditions || [];
  const [filter, setFilter] = useState('all'); // all, buff, debuff

  const isConditionActive = (id) => activeConditions.includes(id);

  const toggleCondition = (id) => {
    let newConds;
    if (activeConditions.includes(id)) {
      newConds = activeConditions.filter(c => c !== id);
    } else {
      newConds = [...activeConditions, id];
    }
    store.updateCharacterField('active_conditions', newConds);
    store.updateCharacterField('conditions', newConds);
  };

  const clearAllConditions = () => {
    store.updateCharacterField('active_conditions', []);
    store.updateCharacterField('conditions', []);
  };

  const filteredPresets = CONDITIONS_PRESETS.filter(p => {
    if (filter === 'buff') return p.category === 'buff';
    if (filter === 'debuff') return p.category === 'debuff';
    return true;
  });

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(20, 20, 38, 0.95) 0%, rgba(15, 15, 26, 0.95) 100%)',
      border: '1px solid var(--border-gold)',
      borderRadius: '8px',
      padding: '14px 18px',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={18} style={{ color: 'var(--accent-gold)' }} />
          <h4 style={{ margin: 0, color: 'var(--gold-bright)', fontSize: '0.95rem', fontFamily: 'Cinzel, serif' }}>
            Canlı Durumlar & Geçici Koşul Modifikatörleri (Conditions & Buffs)
          </h4>
          <span style={{ fontSize: '11px', background: activeConditions.length > 0 ? '#3fb95025' : '#8b949e20', color: activeConditions.length > 0 ? '#3fb950' : '#8b949e', border: `1px solid ${activeConditions.length > 0 ? '#3fb95050' : '#8b949e30'}`, borderRadius: '10px', padding: '1px 8px', fontWeight: 'bold' }}>
            {activeConditions.length} Aktif
          </span>
        </div>

        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          {['all', 'buff', 'debuff'].map(cat => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              style={{
                background: filter === cat ? 'var(--accent-gold)' : 'transparent',
                color: filter === cat ? '#0f0f1a' : '#8b949e',
                border: '1px solid rgba(201,168,76,0.3)',
                borderRadius: '4px',
                padding: '3px 8px',
                fontSize: '11px',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              {cat === 'all' ? 'Tümü' : cat === 'buff' ? '⚡ Buff\'lar' : '🛑 Koşullar'}
            </button>
          ))}
          {activeConditions.length > 0 && (
            <button
              onClick={clearAllConditions}
              style={{
                background: 'rgba(233, 69, 96, 0.15)',
                color: '#e94560',
                border: '1px solid rgba(233, 69, 96, 0.4)',
                borderRadius: '4px',
                padding: '3px 8px',
                fontSize: '11px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              Temizle
            </button>
          )}
        </div>
      </div>

      {/* Active Badges Strip */}
      {activeConditions.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', background: 'rgba(0,0,0,0.3)', padding: '8px 10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <span style={{ fontSize: '11px', color: '#8b949e', alignSelf: 'center', marginRight: '4px' }}>Aktif:</span>
          {activeConditions.map(cId => {
            const found = CONDITIONS_PRESETS.find(p => p.id === cId) || { name: cId, category: 'buff' };
            const isBuff = found.category === 'buff';
            return (
              <span
                key={cId}
                onClick={() => toggleCondition(cId)}
                style={{
                  background: isBuff ? 'rgba(63, 185, 80, 0.2)' : 'rgba(233, 69, 96, 0.2)',
                  color: isBuff ? '#3fb950' : '#e94560',
                  border: `1px solid ${isBuff ? '#3fb95060' : '#e9456060'}`,
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
                title="Kaldırmak için tıklayın"
              >
                {found.name} <X size={12} />
              </span>
            );
          })}
        </div>
      )}

      {/* Grid of Toggleable Conditions */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: '8px',
        maxHeight: '260px',
        overflowY: 'auto',
        paddingRight: '4px'
      }}>
        {filteredPresets.map(preset => {
          const isActive = isConditionActive(preset.id);
          const isBuff = preset.category === 'buff';
          return (
            <div
              key={preset.id}
              onClick={() => toggleCondition(preset.id)}
              style={{
                background: isActive 
                  ? (isBuff ? 'rgba(63, 185, 80, 0.15)' : 'rgba(233, 69, 96, 0.15)')
                  : '#141426',
                border: isActive
                  ? `1px solid ${isBuff ? '#3fb950' : '#e94560'}`
                  : '1px solid rgba(255,255,255,0.06)',
                borderRadius: '6px',
                padding: '8px 10px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: '12px',
                  fontWeight: 'bold',
                  color: isActive ? (isBuff ? '#3fb950' : '#e94560') : '#f0e6d2',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}>
                  {preset.name}
                </div>
                <div style={{ fontSize: '10px', color: '#8b949e', marginTop: '2px', lineHeight: '1.2' }}>
                  {preset.desc}
                </div>
              </div>
              <div style={{
                width: '18px',
                height: '18px',
                borderRadius: '4px',
                background: isActive ? (isBuff ? '#3fb950' : '#e94560') : 'rgba(255,255,255,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: isActive ? '#0f0f1a' : 'transparent',
                flexShrink: 0
              }}>
                <Check size={12} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
