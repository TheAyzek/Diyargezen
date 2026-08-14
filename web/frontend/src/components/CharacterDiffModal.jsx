import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, ArrowRight, Shield, Sword, Sparkles, Scale, Check, AlertCircle, Plus, Minus, Wand2 } from 'lucide-react';

export default function CharacterDiffModal({ isOpen, onClose, initialCharA = null, initialCharB = null, allCharacters = [] }) {
  const [charAId, setCharAId] = useState(initialCharA?.id || '');
  const [charBId, setCharBId] = useState(initialCharB?.id || '');
  const [charA, setCharA] = useState(initialCharA);
  const [charB, setCharB] = useState(initialCharB);
  const [diffData, setDiffData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview'); // overview, combat, skills, feats, spells, wealth

  useEffect(() => {
    if (initialCharA) {
      setCharA(initialCharA);
      setCharAId(initialCharA.id || 'current_a');
    }
    if (initialCharB) {
      setCharB(initialCharB);
      setCharBId(initialCharB.id || 'current_b');
    }
  }, [initialCharA, initialCharB]);

  useEffect(() => {
    if (charA && charB) {
      fetchDiff();
    }
  }, [charA, charB]);

  const handleSelectA = (id) => {
    setCharAId(id);
    const found = allCharacters.find(c => String(c.id) === String(id));
    if (found) setCharA(found.data || found);
  };

  const handleSelectB = (id) => {
    setCharBId(id);
    const found = allCharacters.find(c => String(c.id) === String(id));
    if (found) setCharB(found.data || found);
  };

  const fetchDiff = async () => {
    setLoading(true);
    try {
      const res = await axios.post('/api/rules/character-diff', {
        character_a: charA,
        character_b: charB
      });
      setDiffData(res.data);
    } catch (err) {
      console.error('Error fetching character diff:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const renderDeltaBadge = (delta, isHigherBetter = true) => {
    if (delta === 0 || delta === '0') return <span style={{ color: '#8b949e', fontSize: '11px' }}>±0</span>;
    const isPositive = typeof delta === 'number' ? delta > 0 : String(delta).startsWith('+');
    const isGood = isHigherBetter ? isPositive : !isPositive;
    const color = isGood ? '#3fb950' : '#e94560';
    const bg = isGood ? 'rgba(63, 185, 80, 0.15)' : 'rgba(233, 69, 96, 0.15)';
    const text = typeof delta === 'number' ? (delta > 0 ? `+${delta}` : `${delta}`) : delta;

    return (
      <span style={{
        background: bg,
        color: color,
        border: `1px solid ${color}40`,
        borderRadius: '4px',
        padding: '1px 6px',
        fontSize: '11px',
        fontWeight: 'bold'
      }}>
        {text}
      </span>
    );
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 10000,
      padding: '20px'
    }}>
      <div style={{
        background: '#0d0d1a',
        border: '1px solid var(--border-gold)',
        borderRadius: '12px',
        width: '100%',
        maxWidth: '1050px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 10px 40px rgba(0,0,0,0.8)',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'linear-gradient(90deg, #14142b 0%, #1a1a36 100%)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Scale size={22} style={{ color: 'var(--accent-gold)' }} />
            <div>
              <h3 style={{ margin: 0, color: 'var(--gold-bright)', fontSize: '1.2rem', fontFamily: 'Cinzel, serif' }}>
                Karakter Versiyon & Snapshot Karşılaştırma (Diff)
              </h3>
              <p style={{ margin: '2px 0 0', fontSize: '12px', color: '#8b949e' }}>
                İki karakterin veya seviyenin stat, savaş, yetenek ve envanter değişimlerini yan yana inceleyin.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', padding: '4px' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Character Pickers */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr auto 1fr',
          gap: '16px',
          alignItems: 'center',
          padding: '16px 20px',
          background: '#121124',
          borderBottom: '1px solid rgba(255,255,255,0.05)'
        }}>
          {/* Character A Picker */}
          <div>
            <label style={{ fontSize: '11px', color: '#8b949e', fontWeight: 'bold', display: 'block', marginBottom: '4px' }}>
              🔵 1. KARAKTER (TEMEL / ÖNCEKİ HALİ)
            </label>
            <select
              value={charAId}
              onChange={(e) => handleSelectA(e.target.value)}
              style={{
                width: '100%',
                background: '#1a1a2e',
                color: '#fff',
                border: '1px solid #38bdf8',
                borderRadius: '6px',
                padding: '8px 12px',
                fontSize: '13px'
              }}
            >
              {charA && !allCharacters.some(c => String(c.id) === String(charAId)) && (
                <option value={charAId}>{charA.name} (Mevcut Karakter)</option>
              )}
              {allCharacters.map(c => (
                <option key={c.id} value={c.id}>
                  {c.name} - {c.data?.race || c.race} {c.data?.class || c.class} (Lv {c.data?.level || c.level || 1})
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', color: '#8b949e' }}>
            <ArrowRight size={24} style={{ color: 'var(--accent-gold)' }} />
            <span style={{ fontSize: '10px', marginTop: '2px' }}>FARK</span>
          </div>

          {/* Character B Picker */}
          <div>
            <label style={{ fontSize: '11px', color: '#8b949e', fontWeight: 'bold', display: 'block', marginBottom: '4px' }}>
              🟢 2. KARAKTER (HEDEF / YENİ HALİ)
            </label>
            <select
              value={charBId}
              onChange={(e) => handleSelectB(e.target.value)}
              style={{
                width: '100%',
                background: '#1a1a2e',
                color: '#fff',
                border: '1px solid #3fb950',
                borderRadius: '6px',
                padding: '8px 12px',
                fontSize: '13px'
              }}
            >
              {charB && !allCharacters.some(c => String(c.id) === String(charBId)) && (
                <option value={charBId}>{charB.name} (Hedef Karakter)</option>
              )}
              {allCharacters.map(c => (
                <option key={c.id} value={c.id}>
                  {c.name} - {c.data?.race || c.race} {c.data?.class || c.class} (Lv {c.data?.level || c.level || 1})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Tab Navigation */}
        <div style={{ display: 'flex', gap: '4px', padding: '10px 20px', background: '#0a0914', borderBottom: '1px solid rgba(255,255,255,0.05)', overflowX: 'auto' }}>
          {[
            { id: 'overview', label: '📊 Genel & Nitelikler' },
            { id: 'combat', label: '⚔️ Savaş & Manevralar' },
            { id: 'skills', label: `🎯 Yetenekler (${diffData?.improved_skills?.length || 0})` },
            { id: 'feats', label: `🌟 Feat & Trait (${diffData?.feats?.added?.length || 0} Yeni)` },
            { id: 'spells', label: '✨ Büyücülük' },
            { id: 'wealth', label: '💎 Servet & Envanter' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: activeTab === tab.id ? 'var(--accent-gold)' : 'transparent',
                color: activeTab === tab.id ? '#0f0f1a' : '#8b949e',
                border: 'none',
                padding: '6px 14px',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: 'bold',
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content Body */}
        <div style={{ padding: '20px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--accent-gold)' }}>
              <Sparkles size={32} className="animate-spin" />
              <p style={{ marginTop: '10px', fontSize: '13px' }}>Farklar hesaplanıyor...</p>
            </div>
          ) : !diffData ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#8b949e' }}>
              Karşılaştırmak için lütfen iki karakter seçin.
            </div>
          ) : (
            <>
              {/* TAB 1: OVERVIEW & ABILITIES */}
              {activeTab === 'overview' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {/* Identity Summary Card */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', background: '#141426', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div>
                      <div style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 'bold' }}>1. KARAKTER</div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#fff' }}>{diffData.progression.name_a}</div>
                      <div style={{ fontSize: '12px', color: '#d4c5a9', marginTop: '2px' }}>
                        Seviye {diffData.progression.level_a} • {diffData.progression.race_a} • {diffData.progression.class_a}
                        {diffData.progression.archetype_a && ` (${diffData.progression.archetype_a})`}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '11px', color: '#3fb950', fontWeight: 'bold' }}>2. KARAKTER</div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#fff' }}>
                        {diffData.progression.name_b}
                        <span style={{ marginLeft: '10px' }}>{renderDeltaBadge(diffData.progression.level_delta)}</span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#d4c5a9', marginTop: '2px' }}>
                        Seviye {diffData.progression.level_b} • {diffData.progression.race_b} • {diffData.progression.class_b}
                        {diffData.progression.archetype_b && ` (${diffData.progression.archetype_b})`}
                      </div>
                    </div>
                  </div>

                  {/* Core Stats Overview (HP, BAB, AC, Saves) */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
                    {[
                      { label: 'Can Puanı (HP)', obj: diffData.combat.hit_points },
                      { label: 'Temel Saldırı (BAB)', obj: diffData.combat.bab },
                      { label: 'Zırh Sınıfı (AC)', obj: diffData.combat.armor_class },
                      { label: 'Dokunuş AC (Touch)', obj: diffData.combat.touch_ac },
                      { label: 'İnisiyatif', obj: diffData.combat.initiative },
                      { label: 'Hız (Speed)', obj: diffData.combat.speed }
                    ].map((item, i) => (
                      <div key={i} style={{ background: '#1a1a2e', padding: '10px 12px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <div style={{ fontSize: '10px', color: '#8b949e', fontWeight: 'bold' }}>{item.label}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px' }}>
                          <span style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#f0e6d2' }}>
                            {item.obj.val_a} <span style={{ color: '#8b949e', fontSize: '12px' }}>➔</span> {item.obj.val_b}
                          </span>
                          {renderDeltaBadge(item.obj.delta)}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Ability Scores Grid */}
                  <div style={{ background: '#141426', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-gold)' }}>
                    <h4 style={{ margin: '0 0 12px', color: 'var(--gold-bright)', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Sparkles size={16} /> Temel Nitelik Karşılaştırması (Ability Scores)
                    </h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '10px' }}>
                      {Object.entries(diffData.abilities).map(([abName, abData]) => (
                        <div key={abName} style={{ background: '#1a1a2e', padding: '10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '11px', fontWeight: 'bold', color: '#ffd700' }}>{abName}</span>
                            {renderDeltaBadge(abData.score_delta)}
                          </div>
                          <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#fff', marginTop: '4px' }}>
                            {abData.score_a} <span style={{ color: '#8b949e', fontSize: '12px' }}>➔</span> {abData.score_b}
                          </div>
                          <div style={{ fontSize: '10px', color: '#8b949e', marginTop: '2px' }}>
                            Mod: {abData.mod_a >= 0 ? `+${abData.mod_a}` : abData.mod_a} ➔ {abData.mod_b >= 0 ? `+${abData.mod_b}` : abData.mod_b}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Saving Throws */}
                  <div style={{ background: '#141426', padding: '14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <h4 style={{ margin: '0 0 12px', color: 'var(--accent-gold)', fontSize: '0.95rem' }}>Kurtarma Zarları (Saving Throws)</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                      {Object.entries(diffData.combat.saving_throws).map(([svName, svData]) => (
                        <div key={svName} style={{ background: '#1a1a2e', padding: '10px', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#f0e6d2' }}>{svName}</div>
                            <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--accent-gold)', marginTop: '2px' }}>
                              +{svData.val_a} ➔ +{svData.val_b}
                            </div>
                          </div>
                          {renderDeltaBadge(svData.delta)}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: COMBAT & MANEUVERS */}
              {activeTab === 'combat' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div style={{ background: '#141426', padding: '14px', borderRadius: '8px' }}>
                      <div style={{ fontSize: '11px', color: '#8b949e', fontWeight: 'bold' }}>TEMEL SALDIRI BONUSU (BAB)</div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#7c6ef7', marginTop: '4px' }}>
                        +{diffData.combat.bab.val_a} ➔ +{diffData.combat.bab.val_b}
                        <span style={{ marginLeft: '10px' }}>{renderDeltaBadge(diffData.combat.bab.delta)}</span>
                      </div>
                    </div>
                    <div style={{ background: '#141426', padding: '14px', borderRadius: '8px' }}>
                      <div style={{ fontSize: '11px', color: '#8b949e', fontWeight: 'bold' }}>CMB / CMD SAVUNMASI</div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ffd700', marginTop: '4px' }}>
                        CMB: +{diffData.combat.cmb.val_a} ➔ +{diffData.combat.cmb.val_b} ({renderDeltaBadge(diffData.combat.cmb.delta)})
                        <br />
                        CMD: {diffData.combat.cmd.val_a} ➔ {diffData.combat.cmd.val_b} ({renderDeltaBadge(diffData.combat.cmd.delta)})
                      </div>
                    </div>
                  </div>

                  {/* 10 Maneuvers Diff Matrix */}
                  <div style={{ background: '#141426', padding: '14px', borderRadius: '8px', border: '1px solid rgba(201,168,76,0.3)' }}>
                    <h4 style={{ margin: '0 0 12px', color: 'var(--accent-gold)', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Sword size={16} /> 10 Savaş Manevrası Kıyaslaması (CMB & CMD)
                    </h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '8px' }}>
                      {Object.entries(diffData.combat.maneuvers).map(([mName, mData]) => (
                        <div key={mName} style={{ background: '#1a1a2e', padding: '8px 10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#ffd700' }}>{mName}</div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#8b949e', marginTop: '4px' }}>
                            <span>CMB: +{mData.cmb_a} ➔ +{mData.cmb_b}</span>
                            {renderDeltaBadge(mData.cmb_delta)}
                          </div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#8b949e', marginTop: '2px' }}>
                            <span>CMD: {mData.cmd_a} ➔ {mData.cmd_b}</span>
                            {renderDeltaBadge(mData.cmd_delta)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: SKILLS */}
              {activeTab === 'skills' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div style={{ fontSize: '12px', color: '#8b949e' }}>
                    Değişen veya rank yatırılan yetenekler listelenmektedir ({Object.keys(diffData.skills).length} yetenek):
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '8px' }}>
                    {Object.values(diffData.skills).map((sk, i) => (
                      <div key={i} style={{ background: '#141426', padding: '10px 12px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#f0e6d2' }}>{sk.skill}</div>
                          <div style={{ fontSize: '10px', color: '#8b949e', marginTop: '2px' }}>
                            Rank: {sk.rank_a} ➔ {sk.rank_b} ({renderDeltaBadge(sk.rank_delta)})
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#ffd700' }}>
                            {sk.total_a >= 0 ? `+${sk.total_a}` : sk.total_a} ➔ {sk.total_b >= 0 ? `+${sk.total_b}` : sk.total_b}
                          </div>
                          {renderDeltaBadge(sk.total_delta)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 4: FEATS & TRAITS */}
              {activeTab === 'feats' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {/* Feats Added / Removed */}
                  <div style={{ background: '#141426', padding: '14px', borderRadius: '8px' }}>
                    <h4 style={{ margin: '0 0 10px', color: '#3fb950', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Plus size={16} /> Yeni Eklenen Feat'ler ({diffData.feats.added.length})
                    </h4>
                    {diffData.feats.added.length === 0 ? (
                      <span style={{ fontSize: '12px', color: '#8b949e', fontStyle: 'italic' }}>Yeni eklenen feat yok.</span>
                    ) : (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {diffData.feats.added.map((f, i) => (
                          <span key={i} style={{ background: 'rgba(63,185,80,0.15)', border: '1px solid #3fb950', color: '#3fb950', padding: '4px 10px', borderRadius: '6px', fontSize: '12px', fontWeight: 'bold' }}>
                            +{f}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {diffData.feats.removed.length > 0 && (
                    <div style={{ background: '#141426', padding: '14px', borderRadius: '8px' }}>
                      <h4 style={{ margin: '0 0 10px', color: '#e94560', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Minus size={16} /> Kaldırılan Feat'ler ({diffData.feats.removed.length})
                      </h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {diffData.feats.removed.map((f, i) => (
                          <span key={i} style={{ background: 'rgba(233,69,96,0.15)', border: '1px solid #e94560', color: '#e94560', padding: '4px 10px', borderRadius: '6px', fontSize: '12px' }}>
                            -{f}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Traits Diff */}
                  <div style={{ background: '#141426', padding: '14px', borderRadius: '8px' }}>
                    <h4 style={{ margin: '0 0 10px', color: 'var(--accent-gold)', fontSize: '0.95rem' }}>
                      Karakter Özellikleri (Traits)
                    </h4>
                    <div style={{ fontSize: '12px', color: '#d4c5a9' }}>
                      {diffData.traits.added.length > 0 && (
                        <div>Yeni Trait: <b>{diffData.traits.added.join(', ')}</b></div>
                      )}
                      {diffData.traits.common.length > 0 && (
                        <div style={{ color: '#8b949e', marginTop: '4px' }}>Ortak Trait'ler: {diffData.traits.common.join(', ')}</div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 5: SPELLCASTING */}
              {activeTab === 'spells' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div style={{ background: '#141426', padding: '14px', borderRadius: '8px' }}>
                      <div style={{ fontSize: '11px', color: '#a594ff', fontWeight: 'bold' }}>BÜYÜCÜ SEVİYESİ (CL)</div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#fff', marginTop: '4px' }}>
                        +{diffData.spellcasting.caster_level.val_a} ➔ +{diffData.spellcasting.caster_level.val_b}
                        <span style={{ marginLeft: '10px' }}>{renderDeltaBadge(diffData.spellcasting.caster_level.delta)}</span>
                      </div>
                    </div>
                    <div style={{ background: '#141426', padding: '14px', borderRadius: '8px' }}>
                      <div style={{ fontSize: '11px', color: '#a594ff', fontWeight: 'bold' }}>ODAKLANMA (CONCENTRATION)</div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#38bdf8', marginTop: '4px' }}>
                        +{diffData.spellcasting.concentration.val_a} ➔ +{diffData.spellcasting.concentration.val_b}
                        <span style={{ marginLeft: '10px' }}>{renderDeltaBadge(diffData.spellcasting.concentration.delta)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Spell Slots Progression Grid */}
                  <div style={{ background: '#141426', padding: '14px', borderRadius: '8px', border: '1px solid rgba(124,110,247,0.3)' }}>
                    <h4 style={{ margin: '0 0 12px', color: '#a594ff', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Wand2 size={16} /> Günlük Büyü Yuvaları Değişimi (Spell Slots)
                    </h4>
                    {Object.keys(diffData.spellcasting.spell_slots).length === 0 ? (
                      <span style={{ fontSize: '12px', color: '#8b949e', fontStyle: 'italic' }}>Büyü yuvası bilgisi yok.</span>
                    ) : (
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '8px' }}>
                        {Object.entries(diffData.spellcasting.spell_slots).map(([lvlStr, slotData]) => (
                          <div key={lvlStr} style={{ background: '#1a1a2e', padding: '8px 10px', borderRadius: '6px', textAlign: 'center' }}>
                            <div style={{ fontSize: '10px', color: '#8b949e' }}>{lvlStr === '0' ? 'Cantrip' : `${lvlStr}. Seviye`}</div>
                            <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--gold-bright)', marginTop: '2px' }}>
                              {slotData.slots_a} ➔ {slotData.slots_b}
                            </div>
                            <div style={{ marginTop: '2px' }}>{renderDeltaBadge(slotData.delta)}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 6: WEALTH & GEAR */}
              {activeTab === 'wealth' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div style={{ background: '#141426', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-gold)' }}>
                      <div style={{ fontSize: '11px', color: '#8b949e', fontWeight: 'bold' }}>TOPLAM SERVET DEĞERİ (GP)</div>
                      <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: '#ffd700', marginTop: '4px' }}>
                        {diffData.wealth_and_gear.total_wealth_gp.val_a.toLocaleString()} ➔ {diffData.wealth_and_gear.total_wealth_gp.val_b.toLocaleString()} gp
                        <span style={{ marginLeft: '10px' }}>{renderDeltaBadge(diffData.wealth_and_gear.total_wealth_gp.delta_str)}</span>
                      </div>
                    </div>
                    <div style={{ background: '#141426', padding: '14px', borderRadius: '8px' }}>
                      <div style={{ fontSize: '11px', color: '#8b949e', fontWeight: 'bold' }}>TOPLAM TAŞINAN AĞIRLIK (LBS)</div>
                      <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: '#f0e6d2', marginTop: '4px' }}>
                        {diffData.wealth_and_gear.total_weight_lbs.val_a} ➔ {diffData.wealth_and_gear.total_weight_lbs.val_b} lbs
                        <span style={{ marginLeft: '10px' }}>{renderDeltaBadge(diffData.wealth_and_gear.total_weight_lbs.delta_str, false)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Gear Added / Removed */}
                  {diffData.wealth_and_gear.items_added.length > 0 && (
                    <div style={{ background: '#141426', padding: '14px', borderRadius: '8px' }}>
                      <h4 style={{ margin: '0 0 10px', color: '#3fb950', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Plus size={16} /> Yeni Eklenen Eşyalar ({diffData.wealth_and_gear.items_added.length})
                      </h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {diffData.wealth_and_gear.items_added.map((item, i) => (
                          <span key={i} style={{ background: 'rgba(63,185,80,0.15)', border: '1px solid #3fb950', color: '#3fb950', padding: '4px 10px', borderRadius: '6px', fontSize: '12px' }}>
                            +{item}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
