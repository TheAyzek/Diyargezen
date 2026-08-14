import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Sparkles, Sword, Shield, Wand2, Star, Zap, ChevronRight, Check } from 'lucide-react';

export default function ProgressionPlannerModal({ character, onClose }) {
  const [matrix, setMatrix] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterMode, setFilterMode] = useState('all'); // 'all', 'milestones', 'future'

  const charClass = character?.class || 'Fighter';
  const race = character?.race || 'Human';
  const currentLevel = parseInt(character?.level) || 1;

  useEffect(() => {
    setLoading(true);
    axios.get(`/api/rules/progression-matrix?char_class=${encodeURIComponent(charClass)}&race=${encodeURIComponent(race)}`)
      .then(res => {
        setMatrix(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching progression matrix:', err);
        setLoading(false);
      });
  }, [charClass, race]);

  const filteredMatrix = matrix.filter(row => {
    if (filterMode === 'future') {
      return row.level >= currentLevel;
    }
    if (filterMode === 'milestones') {
      return row.has_general_feat || row.has_ability_boost || row.bonus_feats?.length > 0 || row.class_features?.length > 0;
    }
    return true;
  });

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(5, 5, 10, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        background: '#0d0c18',
        border: '2px solid var(--accent-gold)',
        borderRadius: '12px',
        width: '100%',
        maxWidth: '900px',
        maxHeight: '90vh',
        boxShadow: '0 10px 40px rgba(0,0,0,0.8), 0 0 20px rgba(201,168,76,0.2)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Modal Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 22px',
          borderBottom: '1px solid rgba(201,168,76,0.3)',
          background: 'linear-gradient(90deg, rgba(201,168,76,0.15) 0%, transparent 100%)'
        }}>
          <div>
            <h3 style={{ margin: 0, color: 'var(--accent-gold)', fontSize: '1.25rem', fontFamily: 'Cinzel, serif', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={20} /> 1-20 Seviye İlerleme Yol Haritası
            </h3>
            <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#a594ff' }}>
              {race} • {charClass} • Şu Anki Seviye: <b>{currentLevel}</b>
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.3)', padding: '2px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <button
                type="button"
                onClick={() => setFilterMode('all')}
                style={{
                  fontSize: '11px',
                  padding: '4px 10px',
                  borderRadius: '4px',
                  border: 'none',
                  background: filterMode === 'all' ? 'var(--accent-gold)' : 'transparent',
                  color: filterMode === 'all' ? '#0f0f1a' : '#8b949e',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                Tümü (1-20)
              </button>
              <button
                type="button"
                onClick={() => setFilterMode('future')}
                style={{
                  fontSize: '11px',
                  padding: '4px 10px',
                  borderRadius: '4px',
                  border: 'none',
                  background: filterMode === 'future' ? 'var(--accent-gold)' : 'transparent',
                  color: filterMode === 'future' ? '#0f0f1a' : '#8b949e',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                Gelecek ({currentLevel}-20)
              </button>
              <button
                type="button"
                onClick={() => setFilterMode('milestones')}
                style={{
                  fontSize: '11px',
                  padding: '4px 10px',
                  borderRadius: '4px',
                  border: 'none',
                  background: filterMode === 'milestones' ? 'var(--accent-gold)' : 'transparent',
                  color: filterMode === 'milestones' ? '#0f0f1a' : '#8b949e',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                ⭐ Dönüm Noktaları
              </button>
            </div>

            <button
              onClick={onClose}
              style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Timeline Content */}
        <div style={{ padding: '20px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#ffd700' }}>İlerleme matrisi yükleniyor...</div>
          ) : (
            filteredMatrix.map(row => {
              const isCurrent = row.level === currentLevel;
              const isPast = row.level < currentLevel;

              return (
                <div
                  key={row.level}
                  style={{
                    background: isCurrent ? 'rgba(212,175,55,0.12)' : isPast ? 'rgba(255,255,255,0.02)' : 'rgba(20,20,38,0.7)',
                    border: isCurrent ? '2px solid var(--accent-gold)' : '1px solid rgba(255,255,255,0.06)',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: '12px',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {/* Left: Level Badge & BAB/Saves */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px', minWidth: '220px' }}>
                    <div style={{
                      width: '42px',
                      height: '42px',
                      borderRadius: '8px',
                      background: isCurrent ? 'linear-gradient(135deg, #d4af37 0%, #aa8010 100%)' : '#141426',
                      color: isCurrent ? '#0f0f1a' : '#ffd700',
                      border: isCurrent ? 'none' : '1px solid rgba(212,175,55,0.4)',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 'bold',
                      flexShrink: 0
                    }}>
                      <span style={{ fontSize: '9px', opacity: 0.8 }}>LVL</span>
                      <span style={{ fontSize: '16px', lineHeight: 1 }}>{row.level}</span>
                    </div>

                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#f0e6d2', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Sword size={13} style={{ color: '#38bdf8' }} /> BAB: <b style={{ color: '#38bdf8' }}>{row.bab_formatted}</b>
                        {isCurrent && (
                          <span style={{ fontSize: '10px', background: '#3fb950', color: '#000', padding: '1px 6px', borderRadius: '4px', fontWeight: 'bold' }}>
                            ŞU ANKİ SEVİYE
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '11px', color: '#8b949e', marginTop: '2px', display: 'flex', gap: '8px' }}>
                        <span>Fort: <b style={{ color: '#ff6b81' }}>+{row.fort_save}</b></span>
                        <span>Ref: <b style={{ color: '#4ec9b0' }}>+{row.ref_save}</b></span>
                        <span>Will: <b style={{ color: '#38bdf8' }}>+{row.will_save}</b></span>
                      </div>
                    </div>
                  </div>

                  {/* Middle: Feat & Stat Badges */}
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', flex: 1, minWidth: '220px' }}>
                    {row.has_general_feat && (
                      <span style={{ fontSize: '11px', background: 'rgba(212,175,55,0.18)', color: '#ffd700', border: '1px solid rgba(212,175,55,0.4)', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        ⭐ Genel Feat
                      </span>
                    )}
                    {row.is_human_bonus_feat && (
                      <span style={{ fontSize: '11px', background: 'rgba(56,189,248,0.18)', color: '#38bdf8', border: '1px solid rgba(56,189,248,0.4)', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold' }}>
                        👤 Human Bonus Feat
                      </span>
                    )}
                    {row.has_ability_boost && (
                      <span style={{ fontSize: '11px', background: 'rgba(63,185,80,0.18)', color: '#3fb950', border: '1px solid rgba(63,185,80,0.4)', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        💪 +1 Yetenek Skoru Artışı
                      </span>
                    )}
                    {(row.bonus_feats || []).map((bf, idx) => (
                      <span key={idx} style={{ fontSize: '11px', background: 'rgba(233,69,96,0.18)', color: '#ff6b81', border: '1px solid rgba(233,69,96,0.4)', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold' }}>
                        ⚔️ {bf}
                      </span>
                    ))}
                    {row.max_spell_level > 0 && (
                      <span style={{ fontSize: '11px', background: 'rgba(124,110,247,0.18)', color: '#a594ff', border: '1px solid rgba(124,110,247,0.4)', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        🔮 Seviye {row.max_spell_level} Büyüler
                      </span>
                    )}
                  </div>

                  {/* Right: Unlocked Class Features */}
                  <div style={{ minWidth: '180px', textAlign: 'right' }}>
                    {row.class_features?.length > 0 ? (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', justifyContent: 'flex-end' }}>
                        {row.class_features.map((featName, fIdx) => (
                          <span key={fIdx} style={{ fontSize: '11px', color: '#f0e6d2', background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)' }}>
                            ✦ {featName}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span style={{ fontSize: '11px', color: '#6e7681', fontStyle: 'italic' }}>
                        Standart Gelişim
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
