import React from 'react';
import { Shield, Sword, Heart, Star, Sparkles, Activity } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';

export default function PF1eLiveSheet() {
  const { name, level, race, class: charClass, feat, recalcedData, exportPdf, portrait } = useCharacterStore();
  const [activeEqTab, setActiveEqTab] = React.useState('weapons');

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

  const pfSkillsList = [
    "Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disable Device",
    "Disguise", "Escape Artist", "Fly", "Handle Animal", "Heal", "Intimidate", "Linguistics",
    "Perception", "Perform", "Profession", "Ride", "Sense Motive", "Sleight of Hand",
    "Spellcraft", "Stealth", "Survival", "Swim", "Use Magic Device",
    "Knowledge (Arcana)", "Knowledge (Dungeoneering)", "Knowledge (Engineering)",
    "Knowledge (Geography)", "Knowledge (History)", "Knowledge (Local)",
    "Knowledge (Nature)", "Knowledge (Nobility)", "Knowledge (Planes)", "Knowledge (Religion)"
  ];

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
      
      {/* Pathfinder Header block */}
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
            <span style={{ fontSize: '12px', color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '1px' }}>Pathfinder Canlı Karakter Kağıdı</span>
            <button className="btn btn-secondary" style={{ marginTop: '4px', padding: '4px 8px', fontSize: '11px', minHeight: 'unset', display: 'flex', alignItems: 'center', gap: '4px', width: 'fit-content' }} onClick={exportPdf}>
              📄 PDF Olarak Dışa Aktar
            </button>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
          <div>Sınıf & Seviye: <b>{charClass || 'Seçilmedi'} (Seviye {level})</b></div>
          <div>Irk: <b>{race || 'Seçilmedi'}</b></div>
          <div>Seçili Feat: <b>{feat || 'Seçilmedi'}</b></div>
          <div>BAB: <b>+{recalcedData.bab || 0}</b></div>
        </div>
      </div>

      {/* Combat Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(90px, 1fr))', gap: '12px' }}>
        
        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
          <Heart size={18} style={{ color: '#e94560', marginBottom: '4px' }} />
          <div style={{ fontSize: '9px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Hit Points</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>{recalcedData.hit_points || 8}</div>
        </div>

        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
          <Shield size={18} style={{ color: '#3fb950', marginBottom: '4px' }} />
          <div style={{ fontSize: '9px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Armor Class</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>
            {recalcedData.armor_class || 10} <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>({recalcedData.touch_ac}/{recalcedData.flat_footed_ac})</span>
          </div>
        </div>

        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
          <Sword size={18} style={{ color: 'var(--accent-gold)', marginBottom: '4px' }} />
          <div style={{ fontSize: '9px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>CMB / CMD</div>
          <div style={{ fontSize: '1.3rem', fontWeight: 'bold' }}>
            {recalcedData.cmb >= 0 ? `+${recalcedData.cmb}` : recalcedData.cmb || 0} / {recalcedData.cmd || 10}
          </div>
        </div>

        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
          <Sparkles size={18} style={{ color: 'var(--accent-gold)', marginBottom: '4px' }} />
          <div style={{ fontSize: '9px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Initiative</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>
            {recalcedData.initiative >= 0 ? `+${recalcedData.initiative}` : recalcedData.initiative || 0}
          </div>
        </div>

        <div style={{ background: '#16213e', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
          <Activity size={18} style={{ color: 'var(--accent-gold)', marginBottom: '4px' }} />
          <div style={{ fontSize: '9px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Armor Penalty</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: recalcedData.armor_check_penalty < 0 ? '#e94560' : 'inherit' }}>
            {recalcedData.armor_check_penalty || 0}
          </div>
        </div>

      </div>

      {/* Carrying Capacity / Encumbrance Bar */}
      {(() => {
        const totalWeight = recalcedData.total_weight || 0;
        const capacity = recalcedData.carrying_capacity || { light: 33, medium: 66, heavy: 100 };
        const loadStatus = recalcedData.encumbrance_status || 'Light';
        const pct = Math.min(100, (totalWeight / (capacity.heavy || 100)) * 100);
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
              <span>Hafif: {capacity.light} lb</span>
              <span>Orta: {capacity.medium} lb</span>
              <span>Ağır: {capacity.heavy} lb</span>
            </div>
          </div>
        );
      })()}

      {/* Melee & Ranged Attack Bonuses */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', fontSize: '13px' }}>
        <div style={{ background: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: '6px', textAlign: 'center', border: '1px solid rgba(255,255,255,0.05)' }}>
          Melee Attack Bonus: <b>{recalcedData.melee_attack_bonus >= 0 ? `+${recalcedData.melee_attack_bonus}` : recalcedData.melee_attack_bonus || 0}</b>
        </div>
        <div style={{ background: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: '6px', textAlign: 'center', border: '1px solid rgba(255,255,255,0.05)' }}>
          Ranged Attack Bonus: <b>{recalcedData.ranged_attack_bonus >= 0 ? `+${recalcedData.ranged_attack_bonus}` : recalcedData.ranged_attack_bonus || 0}</b>
        </div>
      </div>

      {/* Main stats layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
        
        {/* Ability Scores columns */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {abilities.map(ab => {
            const score = derivedScores[ab.name] || 10;
            const mod = derivedMods[ab.name] || 0;
            return (
              <div key={ab.name} style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '8px 12px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <span style={{ fontSize: '10px', color: 'var(--color-text-muted)', fontWeight: 'bold' }}>{ab.label}</span>
                <span style={{ fontSize: '18px', fontWeight: '800', color: 'var(--accent-gold)' }}>{score}</span>
                <span style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>{mod >= 0 ? `+${mod}` : mod}</span>
              </div>
            );
          })}
        </div>

        {/* Saves & Skills Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Saves */}
          <div>
            <h4 style={{ fontSize: '1rem', color: '#f0e6d2', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '4px', marginBottom: '8px' }}>
              Saving Throws (Saves)
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {Object.entries(savingThrows).map(([save, val]) => (
                <div key={save} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 12px', background: '#16213e', borderRadius: '6px', fontSize: '13px' }}>
                  <span style={{ textTransform: 'capitalize' }}>{save}</span>
                  <span style={{ fontWeight: 'bold', color: '#3fb950' }}>{val >= 0 ? `+${val}` : val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Spell Slots */}
          {recalcedData.spell_slots && Object.keys(recalcedData.spell_slots).length > 0 && (
            <div>
              <h4 style={{ fontSize: '1rem', color: '#f0e6d2', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '4px', marginBottom: '8px' }}>
                Günlük Büyü Yuvaları (Spell Slots)
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {Object.entries(recalcedData.spell_slots).map(([lvl, qty]) => (
                  <div key={lvl} style={{ 
                    background: '#16213e', 
                    border: '1px solid rgba(201,168,76,0.3)', 
                    borderRadius: '6px', 
                    padding: '4px 8px', 
                    fontSize: '11px',
                    textAlign: 'center',
                    minWidth: '55px'
                  }}>
                    <div style={{ color: 'var(--accent-gold)', fontWeight: 'bold' }}>Lvl {lvl}</div>
                    <div style={{ fontSize: '14px', fontWeight: '800' }}>{qty}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Skills Grid */}
          <div>
            <h4 style={{ fontSize: '1rem', color: '#f0e6d2', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '4px', marginBottom: '8px' }}>
              Yetenek Becerileri (Skills)
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '6px', maxHeight: '200px', overflowY: 'auto', paddingRight: '4px' }}>
              {pfSkillsList.map(skill => {
                const lowercaseKey = skill.toLowerCase().replace(/ /g, '_');
                const modifier = skills[lowercaseKey] || 0;
                
                return (
                  <div key={skill} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 8px', background: 'rgba(255,255,255,0.01)', borderRadius: '4px', fontSize: '13px' }}>
                    <span style={{ color: 'var(--color-text-secondary)' }}>{skill}</span>
                    <span style={{ fontWeight: 'bold' }}>{modifier >= 0 ? `+${modifier}` : modifier}</span>
                  </div>
                );
              })}
            </div>
          </div>

        </div>

      </div>

      {/* Ekipman ve Envanter Sekmeleri */}
      <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '20px', marginTop: '10px' }}>
        <h4 style={{ fontSize: '1.1rem', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Sword size={16} /> Envanter & Ekipman
        </h4>
        
        {/* Tab Headers */}
        <div style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.2)', padding: '3px', borderRadius: '8px', marginBottom: '16px' }}>
          {[
            { id: 'weapons', label: 'Silahlar', count: (recalcedData.weapons || []).length },
            { id: 'armor_shields', label: 'Zırh & Kalkan', count: (recalcedData.armor_shields || []).length },
            { id: 'consumables', label: 'Tüketilebilirler', count: (recalcedData.consumables || []).length },
            { id: 'gear', label: 'Genel & Büyülü', count: (recalcedData.gear || []).length }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveEqTab(tab.id)}
              style={{
                flex: 1,
                padding: '8px 4px',
                fontSize: '11px',
                fontWeight: '600',
                background: activeEqTab === tab.id ? 'var(--accent-gold)' : 'transparent',
                color: activeEqTab === tab.id ? '#0f0f1a' : '#8b949e',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px'
              }}
            >
              {tab.label} <span style={{ fontSize: '9px', opacity: 0.7 }}>({tab.count})</span>
            </button>
          ))}
        </div>

        {/* Tab Contents */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', minHeight: '100px', maxHeight: '300px', overflowY: 'auto', paddingRight: '4px' }}>
          {activeEqTab === 'weapons' && (
            (recalcedData.weapons || []).length === 0 ? (
              <p style={{ color: '#8b949e', fontSize: '13px', fontStyle: 'italic', textAlign: 'center', padding: '20px 0' }}>Karakterin üzerinde silah bulunmuyor.</p>
            ) : (
              (recalcedData.weapons || []).map((w, idx) => {
                const sys = w.sistem_verisi?.system || {};
                const dmg = sys.actions?.[0]?.damage?.parts?.[0]?.[0] || w.sistem_verisi?.damage?.parts?.[0]?.[0] || '-';
                const critRange = sys.ability?.critRange || w.sistem_verisi?.ability?.critRange || 20;
                const critMult = sys.ability?.critMult || w.sistem_verisi?.ability?.critMult || 2;
                const critStr = critRange < 20 ? `${critRange}-20/x${critMult}` : `x${critMult}`;
                const rangeVal = sys.range?.value || w.sistem_verisi?.range?.value;
                const rangeUnit = sys.range?.units || w.sistem_verisi?.range?.units || 'ft';
                const rangeStr = rangeVal ? `${rangeVal} ${rangeUnit}` : 'Yakın (Melee)';
                const weight = sys.weight?.value ?? w.sistem_verisi?.weight?.value ?? 0;
                const qty = w.quantity ?? sys.quantity ?? w.sistem_verisi?.quantity ?? 1;

                return (
                  <div key={idx} className="inventory-row" style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    borderRadius: '8px',
                    padding: '10px 14px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 'bold', color: '#f0e6d2', fontSize: '13px' }}>{w.name}</span>
                      <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>{qty} Adet | {weight} lb</span>
                    </div>
                    <div style={{ display: 'flex', gap: '16px', fontSize: '11px', color: 'var(--accent-gold)' }}>
                      <span>Hasar: <b>{dmg}</b></span>
                      <span>Kritik: <b>{critStr}</b></span>
                      <span>Menzil: <b>{rangeStr}</b></span>
                    </div>
                  </div>
                );
              })
            )
          )}

          {activeEqTab === 'armor_shields' && (
            (recalcedData.armor_shields || []).length === 0 ? (
              <p style={{ color: '#8b949e', fontSize: '13px', fontStyle: 'italic', textAlign: 'center', padding: '20px 0' }}>Karakterin üzerinde zırh veya kalkan bulunmuyor.</p>
            ) : (
              (recalcedData.armor_shields || []).map((a, idx) => {
                const sys = a.sistem_verisi?.system || {};
                const acBonus = sys.armor?.value || a.sistem_verisi?.armor_class?.value || a.sistem_verisi?.armorClass?.value || 0;
                const maxDex = sys.armor?.dex ?? a.sistem_verisi?.armor_class?.dex ?? a.sistem_verisi?.armorClass?.dex ?? 'Sınırsız';
                const acp = sys.acp ?? sys.armor?.acp ?? a.sistem_verisi?.check_penalty ?? a.sistem_verisi?.armor_check_penalty ?? 0;
                const weight = sys.weight?.value ?? a.sistem_verisi?.weight?.value ?? 0;
                const qty = a.quantity ?? sys.quantity ?? a.sistem_verisi?.quantity ?? 1;

                return (
                  <div key={idx} className="inventory-row" style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    borderRadius: '8px',
                    padding: '10px 14px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 'bold', color: '#f0e6d2', fontSize: '13px' }}>{a.name}</span>
                      <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>{qty} Adet | {weight} lb</span>
                    </div>
                    <div style={{ display: 'flex', gap: '16px', fontSize: '11px', color: 'var(--accent-gold)' }}>
                      <span>Zırh Sınıfı (AC): <b>+{acBonus}</b></span>
                      <span>Maks Dex: <b>{maxDex}</b></span>
                      <span>Zırh Cezası (ACP): <b style={{ color: acp < 0 ? '#e94560' : 'inherit' }}>{acp}</b></span>
                    </div>
                  </div>
                );
              })
            )
          )}

          {activeEqTab === 'consumables' && (
            (recalcedData.consumables || []).length === 0 ? (
              <p style={{ color: '#8b949e', fontSize: '13px', fontStyle: 'italic', textAlign: 'center', padding: '20px 0' }}>Karakterin üzerinde tüketilebilir eşya bulunmuyor.</p>
            ) : (
              (recalcedData.consumables || []).map((c, idx) => {
                const sys = c.sistem_verisi?.system || {};
                const qty = c.quantity ?? sys.quantity ?? c.sistem_verisi?.quantity ?? 1;
                const weight = sys.weight?.value ?? c.sistem_verisi?.weight?.value ?? 0;
                const type = sys.consumableType || c.sistem_verisi?.consumableType || 'İksir/Tüketilebilir';

                return (
                  <div key={idx} className="inventory-row" style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    borderRadius: '8px',
                    padding: '10px 14px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div>
                      <div style={{ fontWeight: 'bold', color: '#f0e6d2', fontSize: '13px' }}>{c.name}</div>
                      <div style={{ fontSize: '11px', color: 'var(--accent-gold)', textTransform: 'capitalize' }}>Tür: <b>{type}</b></div>
                    </div>
                    <div style={{ textAlign: 'right', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      <div><b>{qty} Adet</b></div>
                      <div>{weight} lb</div>
                    </div>
                  </div>
                );
              })
            )
          )}

          {activeEqTab === 'gear' && (
            (recalcedData.gear || []).length === 0 ? (
              <p style={{ color: '#8b949e', fontSize: '13px', fontStyle: 'italic', textAlign: 'center', padding: '20px 0' }}>Karakterin üzerinde genel veya büyülü eşya bulunmuyor.</p>
            ) : (
              (recalcedData.gear || []).map((g, idx) => {
                const sys = g.sistem_verisi?.system || {};
                const qty = g.quantity ?? sys.quantity ?? g.sistem_verisi?.quantity ?? 1;
                const weight = sys.weight?.value ?? g.sistem_verisi?.weight?.value ?? 0;
                const category = sys.flags?.dictionary?.Category || g.sistem_verisi?.flags?.dictionary?.Category || 'Genel Eşya';

                return (
                  <div key={idx} className="inventory-row" style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    borderRadius: '8px',
                    padding: '10px 14px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div>
                      <div style={{ fontWeight: 'bold', color: '#f0e6d2', fontSize: '13px' }}>{g.name}</div>
                      <div style={{ fontSize: '11px', color: 'var(--accent-gold)' }}>Kategori: <b>{category}</b></div>
                    </div>
                    <div style={{ textAlign: 'right', fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      <div><b>{qty} Adet</b></div>
                      <div>{weight} lb</div>
                    </div>
                  </div>
                );
              })
            )
          )}
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
