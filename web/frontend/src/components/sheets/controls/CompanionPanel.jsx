import React, { useState } from 'react';
import { PawPrint, Shield, Sparkles, Plus, Trash, Info, Check, Zap, Award } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';

const COMPANION_PRESETS = {
  animal_companion: [
    { key: 'wolf', label: 'Kurt (Wolf)', str: 13, dex: 15, con: 15, int: 2, wis: 12, cha: 6, speed: '50 ft.', acBonus: 2, attacks: 'Isırık 1d6 + Trip', notes: 'Scent, Low-light vision' },
    { key: 'bear', label: 'Ayı (Bear)', str: 15, dex: 15, con: 13, int: 2, wis: 12, cha: 6, speed: '40 ft.', acBonus: 2, attacks: 'Pençe 1d4 (2x), Isırık 1d6', notes: 'Scent, Low-light vision' },
    { key: 'big_cat', label: 'Büyük Kedi (Panther/Lion)', str: 13, dex: 17, con: 13, int: 2, wis: 15, cha: 10, speed: '40 ft.', acBonus: 1, attacks: 'Pençe 1d4 (2x), Isırık 1d6', notes: 'Scent, Pounce' },
    { key: 'eagle', label: 'Kartal (Eagle)', str: 10, dex: 15, con: 12, int: 2, wis: 14, cha: 6, speed: '10 ft., Uçma 80 ft.', acBonus: 1, attacks: 'Pençe 1d4 (2x), Gaga 1d4', notes: 'Flyby Attack' },
    { key: 'horse', label: 'At (Horse)', str: 14, dex: 13, con: 15, int: 2, wis: 12, cha: 6, speed: '50 ft.', acBonus: 4, attacks: 'Nal 1d4 (2x)', notes: 'Scent, Low-light vision' }
  ],
  eidolon: [
    { key: 'quadruped', label: 'Dört Ayaklı (Quadruped)', str: 14, dex: 14, con: 13, int: 7, wis: 10, cha: 11, speed: '40 ft.', acBonus: 2, attacks: 'Isırık 1d6', notes: 'Bedava Evrim: Isırık (Bite)' },
    { key: 'biped', label: 'İki Ayaklı (Biped)', str: 16, dex: 12, con: 13, int: 7, wis: 10, cha: 11, speed: '30 ft.', acBonus: 2, attacks: 'Pençe 1d4 (2x)', notes: 'Bedava Evrim: Pençeler (Claws)' },
    { key: 'serpentine', label: 'Yılansı (Serpentine)', str: 12, dex: 16, con: 13, int: 7, wis: 10, cha: 11, speed: '20 ft., Tırmanma 20 ft.', acBonus: 2, attacks: 'Isırık 1d6', notes: 'Bedava Evrim: Reach (Bite)' },
    { key: 'avian', label: 'Kuşumsu (Avian)', str: 12, dex: 16, con: 13, int: 7, wis: 10, cha: 11, speed: '30 ft., Uçma 40 ft.', acBonus: 1, attacks: 'Pençe 1d4 (2x)', notes: 'Bedava Evrim: Flight' }
  ],
  familiar: [
    { key: 'cat', label: 'Kedi (Cat)', str: 3, dex: 15, con: 8, int: 6, wis: 12, cha: 7, masterBonus: '+3 Gizlilik (Stealth)', notes: 'Gece Görüşü' },
    { key: 'raven', label: 'Kuzgun (Raven)', str: 2, dex: 15, con: 8, int: 6, wis: 14, cha: 6, masterBonus: '+3 Değer Biçme (Appraise)', notes: 'Konuşabilir, Uçar' },
    { key: 'bat', label: 'Yarasa (Bat)', str: 1, dex: 15, con: 8, int: 6, wis: 14, cha: 5, masterBonus: '+3 Uçma (Fly)', notes: 'Blindsight 20 ft.' },
    { key: 'viper', label: 'Engerek (Viper)', str: 4, dex: 17, con: 11, int: 6, wis: 12, cha: 2, masterBonus: '+3 Blöf (Bluff)', notes: 'Zehirli Isırık' },
    { key: 'owl', label: 'Baykuş (Owl)', str: 4, dex: 17, con: 11, int: 6, wis: 15, cha: 6, masterBonus: '+3 Algı (Perception Gölgelerde)', notes: 'Sessiz Uçuş' },
    { key: 'toad', label: 'Kurbağa (Toad)', str: 1, dex: 12, con: 12, int: 6, wis: 14, cha: 4, masterBonus: '+3 Can Puanı (HP Efendiye)', notes: 'Amfibi' }
  ],
  mount: [
    { key: 'warhorse', label: 'Savaş Atı (Heavy Warhorse)', str: 16, dex: 13, con: 17, int: 2, wis: 13, cha: 6, speed: '50 ft.', acBonus: 4, attacks: 'Nal 1d4 (2x), Isırık 1d4', notes: 'Savaş eğitimli' },
    { key: 'camel', label: 'Deve (Camel)', str: 18, dex: 14, con: 14, int: 2, wis: 11, cha: 4, speed: '50 ft.', acBonus: 2, attacks: 'Tükürük / Isırık', notes: 'Çöl Dayanıklılığı' }
  ]
};

const TRICKS_LIST = [
  'Attack (Saldır)', 'Come (Gel)', 'Defend (Korun)', 'Down (Yat / Dur)',
  'Fetch (Getir)', 'Guard (Nöbet Tut)', 'Heel (Takip Et)', 'Perform (Gösteri Yap)',
  'Seek (Ara)', 'Track (İz Sür)', 'Stay (Bekle)'
];

const EIDOLON_EVOLUTIONS = [
  'Claws (Pençeler +1d4)', 'Bite (Isırık +1d6)', 'Flight (Kanat Uçuşu)',
  'Reach (Erişim +5ft)', 'Pounce (Atılma Saldırısı)', 'Tail Spike (Kuyruk İğnesi)',
  'Natural Armor (+2 Zırh)', 'Energy Attacks (+1d6 Alev/Buz)', 'Spell Resistance (Büyü Direnci)'
];

export default function CompanionPanel() {
  const { companion, updateCompanion, resetCompanion, level: masterLevel } = useCharacterStore();

  const [companionType, setCompanionType] = useState(companion?.type || 'animal_companion');
  const [name, setName] = useState(companion?.name || '');
  const [selectedPreset, setSelectedPreset] = useState(companion?.presetKey || 'wolf');
  const [tricks, setTricks] = useState(companion?.tricks || ['Attack', 'Defend', 'Heel']);
  const [evolutions, setEvolutions] = useState(companion?.evolutions || ['Claws']);
  const [notes, setNotes] = useState(companion?.notes || '');

  // Calculate scaled companion stats based on master level
  const calcCompanionStats = () => {
    const lvl = masterLevel || 1;
    const presets = COMPANION_PRESETS[companionType] || COMPANION_PRESETS.animal_companion;
    const activePreset = presets.find(p => p.key === selectedPreset) || presets[0];

    let hd = Math.max(1, Math.floor(lvl * 0.8));
    let bonusHp = hd * 4;
    let baseHp = (hd * 5.5) + bonusHp;
    let ac = 10 + (activePreset.acBonus || 1) + Math.floor(lvl / 3) + Math.floor((activePreset.dex - 10) / 2);
    let bab = Math.floor(hd * 0.75);

    return {
      activePreset,
      hd,
      hp: Math.floor(baseHp),
      ac,
      bab: bab >= 0 ? `+${bab}` : `${bab}`,
      str: activePreset.str + Math.floor(lvl / 4),
      dex: activePreset.dex + Math.floor(lvl / 4),
      con: activePreset.con,
      int: activePreset.int,
      wis: activePreset.wis,
      cha: activePreset.cha
    };
  };

  const stats = calcCompanionStats();

  const handleSaveCompanion = () => {
    const data = {
      type: companionType,
      presetKey: selectedPreset,
      name: name || `${stats.activePreset.label.split(' ')[0]} Yoldaşı`,
      species: stats.activePreset.label,
      level: masterLevel,
      hd: stats.hd,
      hp: stats.hp,
      ac: stats.ac,
      bab: stats.bab,
      str: stats.str,
      dex: stats.dex,
      con: stats.con,
      int: stats.int,
      wis: stats.wis,
      cha: stats.cha,
      tricks: companionType === 'animal_companion' ? tricks : [],
      evolutions: companionType === 'eidolon' ? evolutions : [],
      masterBonus: companionType === 'familiar' ? stats.activePreset.masterBonus : null,
      attacks: stats.activePreset.attacks || 'Doğal Saldırı',
      notes
    };

    updateCompanion(data);
  };

  const toggleTrick = (t) => {
    if (tricks.includes(t)) {
      setTricks(tricks.filter(x => x !== t));
    } else {
      setTricks([...tricks, t]);
    }
  };

  const toggleEvolution = (ev) => {
    if (evolutions.includes(ev)) {
      setEvolutions(evolutions.filter(x => x !== ev));
    } else {
      setEvolutions([...evolutions, ev]);
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      
      {/* Header Banner */}
      <div style={{
        padding: '16px 20px',
        background: 'linear-gradient(135deg, rgba(201,168,76,0.12) 0%, rgba(10,8,20,0.85) 100%)',
        border: '1px solid rgba(201,168,76,0.3)',
        borderRadius: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '44px', height: '44px', borderRadius: '50%',
            background: 'rgba(201,168,76,0.2)', border: '1px solid var(--gold-bright)',
            display: 'flex', alignItems: 'center', justify: 'center'
          }}>
            <PawPrint size={22} style={{ color: 'var(--gold-bright)' }} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', fontSize: '1.2rem' }}>
              {companion ? companion.name : 'Yoldaş & Sadık Dost Özelleştirici'}
            </h3>
            <div style={{ fontSize: '0.78rem', color: 'var(--gold-pale)' }}>
              Pathfinder 1e Animal Companion, Eidolon, Familiar ve Binek Motoru
            </div>
          </div>
        </div>

        {companion ? (
          <button className="crimson-btn" onClick={resetCompanion} style={{ padding: '6px 14px', fontSize: '0.78rem' }}>
            <Trash size={14} /> Yoldaşı Kaldır
          </button>
        ) : (
          <button className="gold-btn" onClick={handleSaveCompanion} style={{ padding: '8px 18px', fontSize: '0.82rem' }}>
            <Plus size={15} /> Yoldaşı Karakter Kağıdına Ekle
          </button>
        )}
      </div>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        
        {/* Left Column: Companion Setup */}
        <div className="dark-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '14px', borderRadius: '8px' }}>
          
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-pale)', marginBottom: '6px' }}>
              YOLDAŞ TÜRÜ (TYPE)
            </label>
            <select
              className="rune-input"
              value={companionType}
              onChange={(e) => {
                const t = e.target.value;
                setCompanionType(t);
                setSelectedPreset(COMPANION_PRESETS[t][0].key);
              }}
              style={{ width: '100%', padding: '8px 12px' }}
            >
              <option value="animal_companion">🐾 Hayvan Yoldaş (Animal Companion - Druid/Ranger/Hunter)</option>
              <option value="eidolon">🌌 Eidolon (Summoner Ruh Yoldaşı)</option>
              <option value="familiar">🦉 Sihirli Familiar (Wizard/Witch/Sorcerer)</option>
              <option value="mount">🐎 Binek (Mount - Cavalier/Paladin)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-pale)', marginBottom: '6px' }}>
              YOLDAŞ İSMİ
            </label>
            <input
              className="rune-input"
              type="text"
              placeholder="Örn: Gölge, Boru, Fırtına..."
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{ width: '100%', padding: '8px 12px' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-pale)', marginBottom: '6px' }}>
              TÜR & ŞABLON SEÇİMİ (PRESET)
            </label>
            <select
              className="rune-input"
              value={selectedPreset}
              onChange={(e) => setSelectedPreset(e.target.value)}
              style={{ width: '100%', padding: '8px 12px' }}
            >
              {(COMPANION_PRESETS[companionType] || []).map(p => (
                <option key={p.key} value={p.key}>{p.label}</option>
              ))}
            </select>
          </div>

          {/* Conditional Sub-panels */}
          {companionType === 'animal_companion' && (
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-pale)', marginBottom: '8px' }}>
                HAYVAN NUMARALARI (TRICKS)
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {TRICKS_LIST.map(tr => {
                  const isSel = tricks.includes(tr);
                  return (
                    <span
                      key={tr}
                      onClick={() => toggleTrick(tr)}
                      style={{
                        padding: '4px 10px',
                        borderRadius: '12px',
                        fontSize: '0.72rem',
                        cursor: 'pointer',
                        background: isSel ? 'rgba(201,168,76,0.25)' : 'rgba(255,255,255,0.03)',
                        border: isSel ? '1px solid var(--gold-bright)' : '1px solid rgba(255,255,255,0.1)',
                        color: isSel ? 'var(--gold-light)' : 'var(--text-muted)',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      {isSel ? '✓ ' : '+ '}{tr}
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {companionType === 'eidolon' && (
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-pale)', marginBottom: '8px' }}>
                EIDOLON EVRİMLERİ (EVOLUTIONS)
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {EIDOLON_EVOLUTIONS.map(ev => {
                  const isSel = evolutions.includes(ev);
                  return (
                    <span
                      key={ev}
                      onClick={() => toggleEvolution(ev)}
                      style={{
                        padding: '4px 10px',
                        borderRadius: '12px',
                        fontSize: '0.72rem',
                        cursor: 'pointer',
                        background: isSel ? 'rgba(142,130,255,0.25)' : 'rgba(255,255,255,0.03)',
                        border: isSel ? '1px solid var(--color-violet)' : '1px solid rgba(255,255,255,0.1)',
                        color: isSel ? '#c4beff' : 'var(--text-muted)',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      {isSel ? '⚡ ' : '+ '}{ev}
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {companionType === 'familiar' && (
            <div style={{ padding: '10px 14px', background: 'rgba(142,130,255,0.1)', border: '1px solid rgba(142,130,255,0.3)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.75rem', color: '#c4beff', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Award size={14} /> Efendi Bonusu (Master Bonus)
              </div>
              <div style={{ fontSize: '0.9rem', color: '#ffffff', fontWeight: 'bold', marginTop: '4px' }}>
                {stats.activePreset.masterBonus || '+3 Bonus'}
              </div>
            </div>
          )}

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-pale)', marginBottom: '6px' }}>
              ÖZEL NOTLAR & EKİPMAN
            </label>
            <textarea
              className="rune-input"
              rows={2}
              placeholder="Yoldaşınızın zırhı, renk tonu, özel davranışları..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', resize: 'vertical' }}
            />
          </div>

          <button className="gold-btn" onClick={handleSaveCompanion} style={{ padding: '10px', marginTop: '8px' }}>
            <Check size={16} /> Yoldaş Ayarlarını Kaydet
          </button>
        </div>

        {/* Right Column: Calculated Live Stat Block */}
        <div className="dark-panel" style={{ padding: '16px', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <h4 style={{ margin: 0, fontFamily: 'Cinzel, serif', color: 'var(--gold-bright)', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={18} /> Yoldaş Canlı Stat Bloğu (Calculated)
          </h4>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
            <div style={{ padding: '10px', background: 'rgba(201,168,76,0.08)', border: '1px solid rgba(201,168,76,0.2)', borderRadius: '6px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.65rem', color: 'var(--gold-pale)', textTransform: 'uppercase' }}>Can (HP)</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--gold-bright)' }}>{stats.hp}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>HD: {stats.hd}d8</div>
            </div>

            <div style={{ padding: '10px', background: 'rgba(201,168,76,0.08)', border: '1px solid rgba(201,168,76,0.2)', borderRadius: '6px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.65rem', color: 'var(--gold-pale)', textTransform: 'uppercase' }}>Zırh (AC)</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--gold-bright)' }}>{stats.ac}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Nat. Armor</div>
            </div>

            <div style={{ padding: '10px', background: 'rgba(201,168,76,0.08)', border: '1px solid rgba(201,168,76,0.2)', borderRadius: '6px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.65rem', color: 'var(--gold-pale)', textTransform: 'uppercase' }}>BAB</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--gold-bright)' }}>{stats.bab}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{stats.activePreset.speed}</div>
            </div>
          </div>

          {/* Ability Scores Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '6px', marginTop: '6px' }}>
            {[
              { label: 'STR', val: stats.str },
              { label: 'DEX', val: stats.dex },
              { label: 'CON', val: stats.con },
              { label: 'INT', val: stats.int },
              { label: 'WIS', val: stats.wis },
              { label: 'CHA', val: stats.cha }
            ].map(ab => (
              <div key={ab.label} style={{ padding: '6px 4px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '4px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.62rem', color: 'var(--gold-pale)' }}>{ab.label}</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 'bold', color: '#ffffff' }}>{ab.val}</div>
              </div>
            ))}
          </div>

          {/* Special Attacks & Notes */}
          <div style={{ padding: '10px', background: 'rgba(10,8,20,0.6)', border: '1px solid rgba(201,168,76,0.15)', borderRadius: '6px', marginTop: '6px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--gold-light)', fontWeight: 'bold' }}>⚔️ Saldırı & Özellikler:</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-main)', marginTop: '4px' }}>
              {stats.activePreset.attacks}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px', fontStyle: 'italic' }}>
              {stats.activePreset.notes}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
