import React, { useMemo } from 'react';
import { useCharacterStore } from '../../../store/characterStore';

const ABILITY_KEYS = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'];
const ABILITY_LABELS = { strength: 'STR', dexterity: 'DEX', constitution: 'CON', intelligence: 'INT', wisdom: 'WIS', charisma: 'CHA' };

const SKILL_LIST = [
  { name: 'Acrobatics', ability: 'dexterity' },
  { name: 'Appraise', ability: 'intelligence' },
  { name: 'Bluff', ability: 'charisma' },
  { name: 'Climb', ability: 'strength' },
  { name: 'Diplomacy', ability: 'charisma' },
  { name: 'Disable Device', ability: 'dexterity', trained: true },
  { name: 'Disguise', ability: 'charisma' },
  { name: 'Escape Artist', ability: 'dexterity' },
  { name: 'Fly', ability: 'dexterity' },
  { name: 'Handle Animal', ability: 'charisma', trained: true },
  { name: 'Heal', ability: 'wisdom' },
  { name: 'Intimidate', ability: 'charisma' },
  { name: 'Linguistics', ability: 'intelligence', trained: true },
  { name: 'Perception', ability: 'wisdom' },
  { name: 'Perform', ability: 'charisma' },
  { name: 'Ride', ability: 'dexterity' },
  { name: 'Sense Motive', ability: 'wisdom' },
  { name: 'Sleight of Hand', ability: 'dexterity', trained: true },
  { name: 'Spellcraft', ability: 'intelligence', trained: true },
  { name: 'Stealth', ability: 'dexterity' },
  { name: 'Survival', ability: 'wisdom' },
  { name: 'Swim', ability: 'strength' },
  { name: 'Use Magic Device', ability: 'charisma', trained: true },
];

const fmtMod = (n) => (n >= 0 ? `+${n}` : `${n}`);

function PDivider({ label }) {
  return (
    <div className="parchment-divider">
      <div className="line" />
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ color: 'var(--ink-light)', fontSize: '0.6rem' }}>✦</span>
        <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.52rem', letterSpacing: '0.14em', color: 'var(--ink-light)', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>{label}</span>
        <span style={{ color: 'var(--ink-light)', fontSize: '0.6rem' }}>✦</span>
      </div>
      <div className="line" />
    </div>
  );
}

export default function ParchmentSheetDisplay() {
  const store = useCharacterStore();
  const {
    name, level, race, class: charClass, abilities, skills, recalcedData,
    alignment, deity, gender, age, height, weight, homeland, portrait
  } = store;

  const derivedScores = recalcedData.ability_scores || store.abilities || {};
  const derivedMods = recalcedData.ability_modifiers || {};

  const mods = useMemo(() => {
    const r = {};
    ABILITY_KEYS.forEach(k => {
      const normKey = k.charAt(0).toUpperCase() + k.slice(1);
      r[k] = derivedMods[normKey] ?? Math.floor(((derivedScores[normKey] || abilities[k] || 10) - 10) / 2);
    });
    return r;
  }, [derivedMods, derivedScores, abilities]);

  const maxHp = recalcedData.hit_points || 10;
  const currentHp = store.currentHp ?? maxHp;
  const hpPct = Math.max(0, Math.min(100, (currentHp / maxHp) * 100));
  const hpColor = hpPct > 66 ? '#4a7a3a' : hpPct > 33 ? '#8a6020' : '#8b1a1a';

  const classSkills = recalcedData.class_data?.class_skills || [];
  const featsList = store.feats || (store.feat ? [{ isim: store.feat }] : []);
  const traitsList = store.traits || [];

  return (
    <div className="parchment parchment-frame" style={{ width: '100%', minHeight: '100%', padding: '24px 22px 28px', boxSizing: 'border-box' }}>
      
      {/* Corner Flourishes */}
      {['top-left', 'top-right', 'bottom-left', 'bottom-right'].map(pos => (
        <div key={pos} style={{
          position: 'absolute',
          [pos.includes('top') ? 'top' : 'bottom']: 8,
          [pos.includes('left') ? 'left' : 'right']: 8,
          width: 24, height: 24,
          borderTop: pos.includes('top') ? `2px solid var(--ink-light)` : 'none',
          borderBottom: pos.includes('bottom') ? `2px solid var(--ink-light)` : 'none',
          borderLeft: pos.includes('left') ? `2px solid var(--ink-light)` : 'none',
          borderRight: pos.includes('right') ? `2px solid var(--ink-light)` : 'none',
          opacity: 0.7,
        }} />
      ))}

      {/* Header / Title */}
      <div style={{ textAlign: 'center', marginBottom: 16, position: 'relative' }}>
        {portrait && (
          <div style={{
            position: 'absolute', right: 0, top: 0,
            width: 54, height: 54, borderRadius: 2,
            border: '1px solid var(--ink-mid)', overflow: 'hidden',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
          }}>
            <img src={portrait} alt="Portrait" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
        )}
        <div style={{ fontFamily: 'Cinzel Decorative, Cinzel, serif', fontSize: '1.4rem', color: 'var(--ink)', letterSpacing: '0.06em', lineHeight: 1.15 }}>
          {name || 'İsimsiz Kahraman'}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, margin: '6px 0 4px' }}>
          <div style={{ flex: 1, height: 2, background: `linear-gradient(90deg, transparent, var(--ink-light))` }} />
          <span style={{ color: 'var(--ink-light)', fontSize: '0.75rem' }}>⚔</span>
          <div style={{ flex: 1, height: 2, background: `linear-gradient(90deg, var(--ink-light), transparent)` }} />
        </div>
        <div style={{ fontFamily: 'EB Garamond, serif', fontSize: '0.85rem', color: 'var(--ink-mid)', fontStyle: 'italic' }}>
          {race || 'Bilinmeyen Irk'} {charClass || 'Bilinmeyen Sınıf'}, Seviye {level || 1} &nbsp;·&nbsp; {alignment || 'TN'} &nbsp;·&nbsp; {deity || 'İnanç Yok'}
        </div>
      </div>

      {/* Identity Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 5, marginBottom: 12 }}>
        {[
          ['Cinsiyet / Yaş', `${gender || '—'} / ${age || '—'}`],
          ['Boy / Kilo', `${height || '—'} / ${weight || '—'}`],
          ['Memleket', homeland || '—'],
          ['Hız (Speed)', `${recalcedData.speed || 30} ft.`]
        ].map(([l, v]) => (
          <div key={l} style={{ border: '1px solid var(--ink-mid)', borderRadius: 1, padding: '4px 6px', background: 'rgba(42,31,14,0.04)' }}>
            <div style={{ fontFamily: 'Cinzel, serif', fontSize: '0.45rem', letterSpacing: '0.1em', color: 'var(--ink-light)', textTransform: 'uppercase' }}>{l}</div>
            <div style={{ fontFamily: 'EB Garamond, serif', fontSize: '0.78rem', fontWeight: 600, color: 'var(--ink)' }}>{v}</div>
          </div>
        ))}
      </div>

      {/* Ability Scores */}
      <PDivider label="Yetenek Skorları (Ability Scores)" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 5, marginBottom: 12 }}>
        {ABILITY_KEYS.map(k => {
          const normKey = k.charAt(0).toUpperCase() + k.slice(1);
          const score = derivedScores[normKey] || abilities[k] || 10;
          const m = mods[k];
          return (
            <div key={k} style={{ border: '2px solid var(--ink-light)', borderRadius: 1, textAlign: 'center', padding: '4px 2px', background: 'rgba(42,31,14,0.03)' }}>
              <div style={{ fontFamily: 'Cinzel, serif', fontSize: '0.46rem', letterSpacing: '0.1em', color: 'var(--ink-light)', textTransform: 'uppercase' }}>{ABILITY_LABELS[k]}</div>
              <div style={{ fontFamily: 'EB Garamond, serif', fontSize: '1.4rem', fontWeight: 600, color: 'var(--ink)', lineHeight: 1.05 }}>{score}</div>
              <div style={{ background: 'var(--ink-mid)', color: 'var(--parchment)', fontFamily: 'DM Mono, monospace', fontSize: '0.68rem', borderRadius: 1, margin: '2px 3px 1px', padding: '1px 0' }}>{fmtMod(m)}</div>
            </div>
          );
        })}
      </div>

      {/* HP & Combat */}
      <PDivider label="Dövüş & Savunma (Combat Stats)" />
      <div style={{ marginBottom: 10 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 3 }}>
          <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.48rem', letterSpacing: '0.1em', color: 'var(--ink-light)', textTransform: 'uppercase' }}>Can Puanı (Hit Points)</span>
          <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '0.85rem', color: 'var(--ink)', fontWeight: 600 }}>{currentHp} / {maxHp}</span>
        </div>
        <div style={{ height: 9, background: 'rgba(42,31,14,0.12)', border: '1px solid var(--ink-mid)', borderRadius: 1, overflow: 'hidden' }}>
          <div className="hp-bar-fill" style={{ width: `${hpPct}%`, background: `linear-gradient(90deg, ${hpColor}, ${hpColor}cc)` }} />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4, marginBottom: 12 }}>
        {[
          ['AC', recalcedData.armor_class || 10],
          ['Touch', recalcedData.touch_ac || 10],
          ['FF', recalcedData.flat_footed_ac || 10],
          ['Init', fmtMod(recalcedData.initiative || 0)],
          ['BAB', fmtMod(recalcedData.bab || 0)],
          ['CMB', fmtMod(recalcedData.cmb || 0)],
          ['CMD', recalcedData.cmd || 10]
        ].map(([l, v]) => (
          <div key={l} style={{ border: '1px solid var(--ink-light)', borderRadius: 1, textAlign: 'center', padding: '4px 2px', background: 'rgba(42,31,14,0.04)' }}>
            <div style={{ fontFamily: 'Cinzel, serif', fontSize: '0.44rem', letterSpacing: '0.08em', color: 'var(--ink-light)', textTransform: 'uppercase' }}>{l}</div>
            <div style={{ fontFamily: 'DM Mono, monospace', fontSize: '0.95rem', fontWeight: 600, color: 'var(--ink)' }}>{v}</div>
          </div>
        ))}
      </div>

      {/* Saving Throws */}
      <PDivider label="Kurtarma Zarları (Saving Throws)" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 5, marginBottom: 12 }}>
        {[
          ['Fortitude', recalcedData.saving_throws?.Fortitude ?? recalcedData.saving_throws?.fortitude ?? 0],
          ['Reflex', recalcedData.saving_throws?.Reflex ?? recalcedData.saving_throws?.reflex ?? 0],
          ['Will', recalcedData.saving_throws?.Will ?? recalcedData.saving_throws?.will ?? 0]
        ].map(([l, v]) => (
          <div key={l} style={{ border: '1px solid var(--ink-light)', borderRadius: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: 'rgba(42,31,14,0.04)' }}>
            <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.52rem', letterSpacing: '0.06em', color: 'var(--ink-mid)' }}>{l}</span>
            <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '0.98rem', fontWeight: 600, color: 'var(--ink)' }}>{fmtMod(v)}</span>
          </div>
        ))}
      </div>

      {/* Skills Grid */}
      <PDivider label="Beceriler (Skills)" />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1px 12px', marginBottom: 12 }}>
        {SKILL_LIST.map(skill => {
          const ranks = parseInt(skills[skill.name]) || 0;
          const abMod = mods[skill.ability] || 0;
          const isClassSkill = classSkills.includes(skill.name);
          const total = ranks + abMod + (isClassSkill && ranks > 0 ? 3 : 0);
          const active = ranks > 0;
          return (
            <div key={skill.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '2px 0', borderBottom: '1px dotted rgba(42,31,14,0.18)' }}>
              <div style={{ fontFamily: 'EB Garamond, serif', fontSize: '0.72rem', color: active ? 'var(--ink)' : 'var(--ink-light)', display: 'flex', alignItems: 'center', gap: 3 }}>
                {isClassSkill && ranks > 0 && <span style={{ color: '#5a3a1a', fontSize: '0.55rem' }}>★</span>}
                {skill.name}
                <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.42rem', color: 'var(--ink-light)' }}>({ABILITY_LABELS[skill.ability]})</span>
              </div>
              <span style={{ fontFamily: 'DM Mono, monospace', fontSize: '0.68rem', color: 'var(--ink)', fontWeight: active ? 600 : 400 }}>{fmtMod(total)}</span>
            </div>
          );
        })}
      </div>

      {/* Feats & Traits */}
      {(featsList.length > 0 || traitsList.length > 0) && (
        <>
          <PDivider label="Feat & Özellikler (Feats & Traits)" />
          <div style={{ fontFamily: 'EB Garamond, serif', fontSize: '0.78rem', color: 'var(--ink)', lineHeight: 1.5, marginBottom: 10, padding: '5px 8px', border: '1px solid rgba(42,31,14,0.2)', borderRadius: 1, background: 'rgba(42,31,14,0.03)' }}>
            {featsList.map(f => f.isim || f.name || f).concat(traitsList.map(t => t.isim || t.name || t)).join(', ')}
          </div>
        </>
      )}

      {/* Equipment */}
      {recalcedData.equipment?.length > 0 && (
        <>
          <PDivider label="Ekipman & Envanter (Equipment)" />
          <div style={{ fontFamily: 'EB Garamond, serif', fontSize: '0.78rem', color: 'var(--ink)', lineHeight: 1.5, marginBottom: 10, padding: '5px 8px', border: '1px solid rgba(42,31,14,0.2)', borderRadius: 1, background: 'rgba(42,31,14,0.03)' }}>
            {recalcedData.equipment.map(e => e.name).join(', ')}
          </div>
        </>
      )}

      {/* Footer */}
      <div style={{ textAlign: 'center', marginTop: 16, paddingTop: 10, borderTop: '1px solid var(--ink-light)', display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ flex: 1, height: 1, background: `linear-gradient(90deg, transparent, var(--ink-mid))` }} />
        <div style={{ fontFamily: 'Cinzel Decorative, Cinzel, serif', fontSize: '0.48rem', letterSpacing: '0.2em', color: 'var(--ink-light)', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>
          Pathfinder 1e · Diyargezen Character Registry
        </div>
        <div style={{ flex: 1, height: 1, background: `linear-gradient(90deg, var(--ink-mid), transparent)` }} />
      </div>
    </div>
  );
}
