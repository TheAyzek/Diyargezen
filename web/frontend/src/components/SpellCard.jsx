import React, { useState } from 'react';
import { Wand2, Zap, Shield, Clock, Target, Sparkles, X, ChevronDown, ChevronUp, Flame, Heart, BookOpen, AlertCircle, Dices } from 'lucide-react';
import { cleanText } from '../utils/textSanitizer';

const SCHOOL_THEMES = {
  evocation:     { color: '#e94560', bg: 'rgba(233, 69, 96, 0.12)',  border: 'rgba(233, 69, 96, 0.35)',  icon: Flame,  label: 'Evocation (Yıkım)' },
  abjuration:    { color: '#4ec9b0', bg: 'rgba(78, 201, 176, 0.12)', border: 'rgba(78, 201, 176, 0.35)', icon: Shield, label: 'Abjuration (Koruma)' },
  transmutation: { color: '#c9a84c', bg: 'rgba(201, 168, 76, 0.12)', border: 'rgba(201, 168, 76, 0.35)', icon: Zap,    label: 'Transmutation (Dönüşüm)' },
  conjuration:   { color: '#7c6ef7', bg: 'rgba(124, 110, 247, 0.12)',border: 'rgba(124, 110, 247, 0.35)',icon: Wand2,  label: 'Conjuration (Çağrı)' },
  enchantment:   { color: '#ce9178', bg: 'rgba(206, 145, 120, 0.12)',border: 'rgba(206, 145, 120, 0.35)',icon: Sparkles,label: 'Enchantment (Efsun)' },
  illusion:      { color: '#9cdcfe', bg: 'rgba(156, 220, 254, 0.12)',border: 'rgba(156, 220, 254, 0.35)',icon: BookOpen,label: 'Illusion (İllüzyon)' },
  divination:    { color: '#4caf50', bg: 'rgba(76, 175, 80, 0.12)',  border: 'rgba(76, 175, 80, 0.35)', icon: Target,  label: 'Divination (Kehanet)' },
  necromancy:    { color: '#a5d6a7', bg: 'rgba(165, 214, 167, 0.12)',border: 'rgba(165, 214, 167, 0.35)',icon: AlertCircle,label: 'Necromancy (Ölüm)' },
  universal:     { color: '#d7ba7d', bg: 'rgba(215, 186, 125, 0.12)',border: 'rgba(215, 186, 125, 0.35)',icon: Wand2,  label: 'Universal (Genel)' }
};

/**
 * Calculates level-scaled damage, healing, or spell mechanics based on Pathfinder 1e Caster Level rules.
 */
export function getSpellFormula(spellObj, characterLevel = 1) {
  const name = (spellObj.isim || spellObj.name || String(spellObj)).trim();
  const nameLower = name.toLowerCase();
  const sv = spellObj.sistem_verisi || spellObj.system || {};
  const desc = (sv.description || spellObj.aciklama || '').toLowerCase();
  const cl = Math.max(1, parseInt(characterLevel) || 1);

  // 1. Iconics
  if (nameLower.includes('fireball')) {
    const dice = Math.min(10, cl);
    return { type: 'damage', formula: `${dice}d6 Alev Hasarı`, diceCount: dice, dieSides: 6, maxCap: '10d6 Max', desc: `Caster Level ${cl} → ${dice}d6 Alev Hasarı` };
  }
  if (nameLower.includes('cure light wounds')) {
    const bonus = Math.min(5, cl);
    return { type: 'healing', formula: `1d8+${bonus} İyileştirme`, diceCount: 1, dieSides: 8, flatBonus: bonus, maxCap: '+5 Max', desc: `Caster Level ${cl} → 1d8+${bonus} İyileştirme` };
  }
  if (nameLower.includes('cure moderate wounds')) {
    const bonus = Math.min(10, cl);
    return { type: 'healing', formula: `2d8+${bonus} İyileştirme`, diceCount: 2, dieSides: 8, flatBonus: bonus, maxCap: '+10 Max', desc: `Caster Level ${cl} → 2d8+${bonus} İyileştirme` };
  }
  if (nameLower.includes('cure serious wounds')) {
    const bonus = Math.min(15, cl);
    return { type: 'healing', formula: `3d8+${bonus} İyileştirme`, diceCount: 3, dieSides: 8, flatBonus: bonus, maxCap: '+15 Max', desc: `Caster Level ${cl} → 3d8+${bonus} İyileştirme` };
  }
  if (nameLower.includes('cure critical wounds')) {
    const bonus = Math.min(20, cl);
    return { type: 'healing', formula: `4d8+${bonus} İyileştirme`, diceCount: 4, dieSides: 8, flatBonus: bonus, maxCap: '+20 Max', desc: `Caster Level ${cl} → 4d8+${bonus} İyileştirme` };
  }
  if (nameLower.includes('magic missile')) {
    const missiles = Math.min(5, 1 + Math.floor((cl - 1) / 2));
    return { type: 'damage', formula: `${missiles} Füze x (1d4+1)`, missiles, diceCount: missiles, dieSides: 4, flatBonus: missiles, maxCap: '5 Füze Max', desc: `Caster Level ${cl} → ${missiles} Füze` };
  }
  if (nameLower.includes('lightning bolt')) {
    const dice = Math.min(10, cl);
    return { type: 'damage', formula: `${dice}d6 Elektrik Hasarı`, diceCount: dice, dieSides: 6, maxCap: '10d6 Max', desc: `Caster Level ${cl} → ${dice}d6 Elektrik` };
  }
  if (nameLower.includes('cone of cold')) {
    const dice = Math.min(15, cl);
    return { type: 'damage', formula: `${dice}d6 Soğuk Hasarı`, diceCount: dice, dieSides: 6, maxCap: '15d6 Max', desc: `Caster Level ${cl} → ${dice}d6 Soğuk` };
  }
  if (nameLower.includes('scorching ray')) {
    const rays = cl >= 11 ? 3 : (cl >= 7 ? 2 : 1);
    return { type: 'damage', formula: `${rays} Işın x (4d6 Alev)`, rays, diceCount: rays * 4, dieSides: 6, maxCap: '3 Işın Max', desc: `Caster Level ${cl} → ${rays} Işın` };
  }
  if (nameLower.includes('shocking grasp') || nameLower.includes('burning hands')) {
    const dice = Math.min(5, cl);
    const side = nameLower.includes('burning') ? 4 : 6;
    return { type: 'damage', formula: `${dice}d${side} Hasar`, diceCount: dice, dieSides: side, maxCap: '5d Max', desc: `Caster Level ${cl} → ${dice}d${side} Hasar` };
  }

  // 2. Generic Regex Match: "X1dY per caster level (maximum Z1dY)"
  const perLevelMatch = desc.match(/(\d+)d(\d+)(?:\s*\+\s*(\d+))?\s*(?:points of\s*\w+\s*damage\s*)?per\s*(?:caster\s*)?level(?:\s*\(maximum\s*(\d+)d\d+\))?/i);
  if (perLevelMatch) {
    const dicePerLvl = parseInt(perLevelMatch[1]) || 1;
    const dieSides = parseInt(perLevelMatch[2]) || 6;
    const maxDice = perLevelMatch[4] ? parseInt(perLevelMatch[4]) : 20;
    const numDice = Math.min(maxDice, cl * dicePerLvl);
    return { type: 'damage', formula: `${numDice}d${dieSides} Hasar`, diceCount: numDice, dieSides, maxCap: `${maxDice}d${dieSides} Max`, desc: `Caster Level ${cl} → ${numDice}d${dieSides}` };
  }

  // 3. Fixed Dice Match: "3d6 points of damage"
  const fixedDiceMatch = desc.match(/(\d+)d(\d+)(?:\s*\+\s*(\d+))?/i);
  if (fixedDiceMatch) {
    const numDice = parseInt(fixedDiceMatch[1]) || 1;
    const dieSides = parseInt(fixedDiceMatch[2]) || 6;
    const flatBonus = parseInt(fixedDiceMatch[3]) || 0;
    return { type: 'effect', formula: `${numDice}d${dieSides}${flatBonus ? '+' + flatBonus : ''}`, diceCount: numDice, dieSides, flatBonus, desc: `${numDice}d${dieSides}${flatBonus ? '+' + flatBonus : ''}` };
  }

  return { type: 'utility', formula: 'Statü / Etki Büyüsü', desc: `Caster Level ${cl} → Yardımcı Büyü` };
}

export default function SpellCard({
  spell,
  characterLevel = 1,
  characterClass = '',
  onCastSpell,
  onRemoveSpell,
  compact = false
}) {
  const [expanded, setExpanded] = useState(false);
  const [castCount, setCastCount] = useState(0);
  const [lastCastResult, setLastCastResult] = useState(null);
  const [showMetamagic, setShowMetamagic] = useState(false);
  const [activeMetamagics, setActiveMetamagics] = useState([]);

  const spellObj = typeof spell === 'object' && spell !== null ? spell : { isim: String(spell) };
  const name = spellObj.isim || spellObj.name || 'Büyü';
  const sv = spellObj.sistem_verisi || spellObj.system || {};

  const level = spellObj.level ?? sv.level ?? 0;
  const schoolKey = (spellObj.school || sv.school || 'universal').toLowerCase().trim();
  const theme = SCHOOL_THEMES[schoolKey] || SCHOOL_THEMES.universal;
  const Icon = theme.icon;

  const castingTime = sv.casting_time || '1 standart eylem';
  const range = sv.range || 'Kişisel / Temas';
  const components = sv.components || 'V, S';
  const savingThrow = sv.saving_throw || 'Yok';
  const description = sv.description || spellObj.aciklama || 'Büyü açıklaması bulunmuyor.';

  // Metamagic definitions
  const METAMAGIC_OPTIONS = [
    { key: 'empower', name: 'Empower', slot: 2, label: '+2 Empower (+%50)' },
    { key: 'maximize', name: 'Maximize', slot: 3, label: '+3 Maximize (Max Zar)' },
    { key: 'quicken', name: 'Quicken', slot: 4, label: '+4 Quicken (Swift)' },
    { key: 'extend', name: 'Extend', slot: 1, label: '+1 Extend (2x Süre)' },
    { key: 'enlarge', name: 'Enlarge', slot: 1, label: '+1 Enlarge (2x Menzil)' },
    { key: 'silent', name: 'Silent', slot: 1, label: '+1 Silent (Sözsüz)' },
    { key: 'still', name: 'Still', slot: 1, label: '+1 Still (Hareketsiz)' },
    { key: 'intensified', name: 'Intensified', slot: 1, label: '+1 Intensified (+5 CL)' },
    { key: 'persistent', name: 'Persistent', slot: 2, label: '+2 Persistent' },
  ];

  const totalSlotAdj = activeMetamagics.reduce((acc, mKey) => {
    const meta = METAMAGIC_OPTIONS.find(o => o.key === mKey);
    return acc + (meta ? meta.slot : 0);
  }, 0);

  const effectiveSlotLevel = Math.min(9, level + totalSlotAdj);
  const isSpontaneous = ['sorcerer', 'oracle', 'bard', 'inquisitor', 'bloodrager'].includes((characterClass || '').toLowerCase());
  const effectiveCastingTime = activeMetamagics.includes('quicken')
    ? 'Swift Action (Hızlı Eylem)'
    : (isSpontaneous && activeMetamagics.length > 0)
      ? 'Full-Round Action (Tam Tur)'
      : castingTime;

  const toggleMetamagic = (mKey) => {
    if (activeMetamagics.includes(mKey)) {
      setActiveMetamagics(activeMetamagics.filter(k => k !== mKey));
    } else {
      setActiveMetamagics([...activeMetamagics, mKey]);
    }
  };

  const effectiveCL = activeMetamagics.includes('intensified') ? characterLevel + 5 : characterLevel;
  const formulaInfo = getSpellFormula({ ...spellObj, sistem_verisi: { ...sv, description } }, effectiveCL);

  const handleCast = () => {
    setCastCount(prev => prev + 1);

    const cl = Math.max(1, parseInt(effectiveCL) || 1);
    let total = 0;
    const rolls = [];

    if (formulaInfo.diceCount > 0) {
      if (activeMetamagics.includes('maximize')) {
        for (let i = 0; i < formulaInfo.diceCount; i++) {
          const maxVal = formulaInfo.dieSides || 6;
          rolls.push(maxVal);
          total += maxVal;
        }
      } else {
        for (let i = 0; i < formulaInfo.diceCount; i++) {
          const r = Math.floor(Math.random() * (formulaInfo.dieSides || 6)) + 1;
          rolls.push(r);
          total += r;
        }
      }
      if (formulaInfo.flatBonus) {
        total += formulaInfo.flatBonus;
      }

      if (activeMetamagics.includes('empower')) {
        const bonusHalf = Math.floor(total * 0.5);
        const empoweredTotal = total + bonusHalf;
        setLastCastResult({
          msg: `✨ Güçlendirilmiş Zarlar: [${rolls.join(', ')}] = ${total} + %50 (${bonusHalf}) = ${empoweredTotal} ${formulaInfo.type === 'healing' ? 'Can Yenilendi' : 'Hasar Verildi'} (Slot: Lv ${effectiveSlotLevel})`,
          total: empoweredTotal,
          rolls,
          formula: formulaInfo.formula
        });
      } else {
        let msg = `✨ ${name} kullanıldı! (Slot Lv ${effectiveSlotLevel}, ${formulaInfo.desc})`;
        if (formulaInfo.type === 'damage') {
          msg = `🔥 ${name} kullanıldı! (${formulaInfo.formula}): ${total} HASAR VERİLDİ! [${rolls.join(', ')}] (Slot Lv ${effectiveSlotLevel})`;
        } else if (formulaInfo.type === 'healing') {
          msg = `✨ ${name} kullanıldı! (${formulaInfo.formula}): ${total} CAN YENİLENDİ! [${rolls.join(', ')}] (Slot Lv ${effectiveSlotLevel})`;
        } else {
          msg = `⚡ ${name} kullanıldı! (${formulaInfo.formula}): ${total} Toplam Değer! [${rolls.join(', ')}] (Slot Lv ${effectiveSlotLevel})`;
        }
        setLastCastResult({
          msg,
          total,
          rolls,
          formula: formulaInfo.formula
        });
      }
    } else {
      setLastCastResult({
        msg: `✨ ${name} büyüsü döküldü! (Gereken Slot: Lv ${effectiveSlotLevel}, Süre: ${effectiveCastingTime})`,
        total: 0,
        rolls: [],
        formula: formulaInfo.formula
      });
    }

    setTimeout(() => setLastCastResult(null), 6000);

    if (onCastSpell) {
      onCastSpell({ spell: name, level: effectiveSlotLevel, total, rolls, formula: formulaInfo.formula });
    }
  };

  return (
    <div
      style={{
        background: theme.bg,
        border: `1px solid ${theme.border}`,
        borderRadius: '10px',
        padding: compact ? '10px 14px' : '14px 18px',
        boxShadow: `0 4px 20px rgba(0,0,0,0.35), 0 0 15px ${theme.color}15`,
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        transition: 'all 0.2s ease-in-out',
        backdropFilter: 'blur(8px)',
        boxSizing: 'border-box'
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '10px' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <Icon size={18} style={{ color: theme.color, flexShrink: 0 }} />
            <h4 style={{ margin: 0, fontSize: compact ? '14px' : '16px', fontWeight: 'bold', color: '#f0e6d2' }}>
              {name}
            </h4>
            <span
              style={{
                fontSize: '10px',
                padding: '2px 8px',
                borderRadius: '12px',
                background: `${theme.color}25`,
                color: theme.color,
                border: `1px solid ${theme.color}45`,
                fontWeight: 'bold'
              }}
            >
              Seviye {level} • {theme.label.split(' ')[0]}
            </span>
          </div>

          {/* Spell Quick Info Bar */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', marginTop: '6px', fontSize: '11px', color: '#8b949e' }}>
            <span>⏱️ <b>Süre:</b> {castingTime}</span>
            <span>🎯 <b>Menzil:</b> {range}</span>
            <span>⚡ <b>Bileşen:</b> {components}</span>
            <span>🛡️ <b>Kurtulma Zarı:</b> {savingThrow}</span>
          </div>
        </div>

        {/* Top Right Badges & Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }}>
          {castCount > 0 && (
            <span
              style={{
                fontSize: '10px',
                background: 'rgba(201,168,76,0.15)',
                color: 'var(--accent-gold)',
                border: '1px solid rgba(201,168,76,0.3)',
                borderRadius: '10px',
                padding: '2px 8px',
                fontWeight: 'bold'
              }}
            >
              Kullanıldı: {castCount}
            </span>
          )}

          {onRemoveSpell && (
            <button
              type="button"
              onClick={() => onRemoveSpell(name)}
              style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', padding: '4px' }}
              onMouseOver={e => e.currentTarget.style.color = '#e94560'}
              onMouseOut={e => e.currentTarget.style.color = '#8b949e'}
              title="Büyüyü Defterden Çıkar"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Level-Scaled Formula Badge */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justify: 'space-between',
          background: 'rgba(0,0,0,0.3)',
          border: `1px solid ${theme.color}30`,
          borderRadius: '6px',
          padding: '6px 10px',
          fontSize: '12px'
        }}
      >
        <span style={{ color: '#8b949e', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Dices size={14} style={{ color: theme.color }} />
          Seviyeye Göre Hasar / Etki:
        </span>
        <span style={{ fontWeight: 'bold', color: theme.color, fontSize: '13px' }}>
          {formulaInfo.formula} {formulaInfo.maxCap ? `(${formulaInfo.maxCap})` : ''}
        </span>
      </div>

      {/* Cast Result Notification */}
      {lastCastResult && (
        <div
          style={{
            background: formulaInfo.type === 'healing' ? 'rgba(63, 185, 80, 0.18)' : 'rgba(233, 69, 96, 0.18)',
            border: `1px solid ${formulaInfo.type === 'healing' ? 'rgba(63, 185, 80, 0.5)' : 'rgba(233, 69, 96, 0.5)'}`,
            borderRadius: '6px',
            padding: '10px 14px',
            fontSize: '13px',
            color: formulaInfo.type === 'healing' ? '#3fb950' : '#ff6b81',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            boxShadow: '0 0 15px rgba(0,0,0,0.5)'
          }}
        >
          <Sparkles size={16} />
          {lastCastResult.msg}
        </div>
      )}

      {/* Expanded Description */}
      {(expanded || !compact) && (
        <div
          style={{
            fontSize: '12px',
            color: '#c9d1d9',
            lineHeight: '1.5',
            background: 'rgba(0,0,0,0.25)',
            borderRadius: '6px',
            padding: '10px 12px',
            border: '1px solid rgba(255,255,255,0.05)',
            marginTop: '4px'
          }}
        >
          {cleanText(description)}
        </div>
      )}

      {/* Metamagic Controls & Simulator Panel */}
      <div style={{ marginTop: '6px', background: 'rgba(124, 110, 247, 0.06)', border: '1px solid rgba(124, 110, 247, 0.25)', borderRadius: '6px', padding: '8px 10px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button
            type="button"
            onClick={() => setShowMetamagic(!showMetamagic)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#a594ff',
              fontSize: '11px',
              fontWeight: 'bold',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: 0
            }}
          >
            <Sparkles size={13} /> 🔮 Metamagic (Metabüyü) {activeMetamagics.length > 0 && `(${activeMetamagics.length} Seçili)`}
          </button>

          {activeMetamagics.length > 0 && (
            <span style={{ fontSize: '11px', color: '#ffd700', fontWeight: 'bold' }}>
              ⚡ Gerekli Slot: Seviye {effectiveSlotLevel} ({effectiveCastingTime})
            </span>
          )}
        </div>

        {showMetamagic && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px' }}>
            {METAMAGIC_OPTIONS.map(opt => {
              const isSelected = activeMetamagics.includes(opt.key);
              return (
                <button
                  key={opt.key}
                  type="button"
                  onClick={() => toggleMetamagic(opt.key)}
                  style={{
                    fontSize: '10px',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    border: isSelected ? '1px solid #d4af37' : '1px solid rgba(255,255,255,0.1)',
                    background: isSelected ? 'rgba(212,175,55,0.2)' : 'rgba(0,0,0,0.3)',
                    color: isSelected ? '#ffd700' : '#8b949e',
                    fontWeight: isSelected ? 'bold' : 'normal',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Card Action Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px', paddingTop: '6px', borderTop: `1px solid ${theme.color}20` }}>
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#8b949e',
            fontSize: '11px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          {expanded ? 'Açıklamayı Gizle' : 'Açıklamayı Göster'}
        </button>

        <button
          type="button"
          className="btn btn-primary"
          style={{
            padding: '6px 14px',
            fontSize: '12px',
            minHeight: 'unset',
            background: `linear-gradient(135deg, ${theme.color} 0%, #1a1a2e 100%)`,
            borderColor: theme.color,
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            boxShadow: `0 0 10px ${theme.color}40`
          }}
          onClick={handleCast}
        >
          <Wand2 size={14} />
          Büyüyü Kullan / At ({formulaInfo.formula})
        </button>
      </div>
    </div>
  );
}
