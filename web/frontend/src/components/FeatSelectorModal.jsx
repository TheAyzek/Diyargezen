import React, { useState, useEffect, useMemo } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Search, X, Swords, Users, Sparkles, Hammer, Star, Shield, Award, Wand2, AlertTriangle, CheckCircle2, ShieldAlert, Music, Zap, Heart, Flame, BookOpen } from 'lucide-react';
import { cleanText } from '../utils/textSanitizer';

const CATEGORY_CONFIG = {
  ClassFeature:  { icon: Wand2,     color: '#f39c12', label: 'Sınıf Özelliği',       short: 'Sınıf' },
  Combat:        { icon: Swords,    color: '#e94560', label: 'Savaş (Combat)',         short: 'Savaş' },
  Teamwork:      { icon: Users,     color: '#4ec9b0', label: 'İşbirliği (Teamwork)',  short: 'Teamwork' },
  Metamagic:     { icon: Sparkles,  color: '#7c6ef7', label: 'Metamagic',             short: 'Metamagic' },
  'Item Creation': { icon: Hammer,  color: '#c9a84c', label: 'Eşya Üretimi',          short: 'Üretim' },
  Racial:        { icon: Star,      color: '#ce9178', label: 'Irk (Racial)',           short: 'Irk' },
  Mythic:        { icon: Award,     color: '#d4af37', label: 'Mythic',                 short: 'Mythic' },
  Performance:   { icon: Music,     color: '#c678dd', label: 'Performans',             short: 'Perf.' },
  Grit:          { icon: Flame,     color: '#e5844a', label: 'Grit (Cesaret)',         short: 'Grit' },
  Panache:       { icon: Zap,       color: '#56b6c2', label: 'Panache (Zarafet)',      short: 'Panache' },
  Social:        { icon: BookOpen,  color: '#98c379', label: 'Sosyal (Social)',        short: 'Sosyal' },
  Faith:         { icon: Heart,     color: '#e06c75', label: 'İnanç (Faith)',          short: 'İnanç' },
  Magic:         { icon: Sparkles,  color: '#a594ff', label: 'Sihir (Magic)',          short: 'Sihir' },
  General:       { icon: Shield,    color: '#9cdcfe', label: 'Genel (General)',        short: 'Genel' },
};

// Frontend prerequisite evaluator helper
function evaluatePrerequisites(feat, character) {
  if (!character) return { valid: true, warnings: [] };

  const warnings = [];
  const sys = feat.sistem_verisi || {};
  let prereqs = sys.prerequisites || sys.prereqs || feat.prerequisites || [];
  if (typeof prereqs === 'string') {
    prereqs = [prereqs];
  } else if (!Array.isArray(prereqs)) {
    prereqs = [];
  }

  const scores = character.abilities || { strength: 10, dexterity: 10, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 };
  const bab = Number(character.bab || 0);
  const totalLevel = Number(character.level || 1);

  const currentFeats = new Set((character.feats || []).map(f => (typeof f === 'object' ? f.isim || f.name : String(f)).toLowerCase()));

  for (const p of prereqs) {
    const pStr = String(p).trim();
    if (!pStr) continue;

    // Ability Score check e.g. "Str 13", "Dex 15"
    const mAb = pStr.match(/(Str|Dex|Con|Int|Wis|Cha)\s*(\d+)/i);
    if (mAb) {
      const statMap = { str: 'strength', dex: 'dexterity', con: 'constitution', int: 'intelligence', wis: 'wisdom', cha: 'charisma' };
      const statKey = statMap[mAb[1].toLowerCase()];
      const reqVal = parseInt(mAb[2], 10);
      const currVal = Number(scores[statKey] || 10);
      if (currVal < reqVal) {
        warnings.push(`${mAb[1].toUpperCase()} >= ${reqVal} gerekli (Mevcut: ${currVal})`);
      }
    }

    // BAB check e.g. "Base attack bonus +1"
    const mBab = pStr.match(/(?:Base attack bonus|BAB)\s*\+?(\d+)/i);
    if (mBab) {
      const reqBab = parseInt(mBab[1], 10);
      if (bab < reqBab) {
        warnings.push(`BAB >= +${reqBab} gerekli (Mevcut: +${bab})`);
      }
    }

    // Level check e.g. "Character level 3rd"
    const mLvl = pStr.match(/(?:Character level|Level)\s*(\d+)/i);
    if (mLvl) {
      const reqLvl = parseInt(mLvl[1], 10);
      if (totalLevel < reqLvl) {
        warnings.push(`Seviye >= ${reqLvl} gerekli (Mevcut: ${totalLevel})`);
      }
    }

    // Common Prerequisite Feat check
    const knownFeats = ["Power Attack", "Dodge", "Point-Blank Shot", "Precise Shot", "Combat Expertise", "Weapon Focus", "Mobility"];
    for (const kf of knownFeats) {
      if (pStr.toLowerCase().includes(kf.toLowerCase()) && !currentFeats.has(kf.toLowerCase())) {
        warnings.push(`Ön Feat Gerekli: ${kf}`);
      }
    }
  }

  return {
    valid: warnings.length === 0,
    warnings
  };
}

export default function FeatSelectorModal({
  isOpen,
  onClose,
  system,
  character,
  className = '',
  initialCategory = 'All',
  selectedFeats = [],
  maxFeats = 1,
  onAddFeat
}) {
  const [feats, setFeats] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState(initialCategory || 'All');
  const [loading, setLoading] = useState(false);
  const [ruleError, setRuleError] = useState(null);
  const [overrideModalTarget, setOverrideModalTarget] = useState(null);

  useEffect(() => {
    if (isOpen && initialCategory) {
      setActiveCategory(initialCategory);
    }
  }, [isOpen, initialCategory]);

  useEffect(() => {
    if (isOpen) {
      fetchFeats();
    }
  }, [isOpen, system, className, activeCategory, searchQuery]);

  const fetchFeats = () => {
    setLoading(true);
    const sys = (system || 'pf1e').toLowerCase();
    axios.get(`/api/rules/${sys}/feats`, {
      params: { query: searchQuery, category: cat }
    })
      .then(res => {
        setFeats(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Feats fetch error:', err);
        setFeats([]);
        setLoading(false);
      });
  };

  // Hook'lar her zaman early return'den ÖNCE çağrılmalı (React Rules of Hooks)
  const categories = ['All', ...Object.keys(CATEGORY_CONFIG)];

  const catCounts = useMemo(() => {
    const counts = { All: feats.length };
    feats.forEach(f => {
      const c = f.sistem_verisi?.feat_category || 'General';
      counts[c] = (counts[c] || 0) + 1;
    });
    return counts;
  }, [feats]);

  if (!isOpen) return null;

  const isSelected = (featName) => selectedFeats.some(f => (f.isim || f.name || f) === featName);

  const canAdd = (featEntity) => {
    if (selectedFeats.length >= maxFeats) {
      return { ok: false, msg: `Bu seviyede en fazla ${maxFeats} feat seçebilirsiniz.` };
    }
    const featName = featEntity.isim || featEntity.name || featEntity;
    if (isSelected(featName)) {
      return { ok: false, msg: 'Bu feat zaten seçili.' };
    }
    return { ok: true, msg: '' };
  };

  const handleSelectClick = (feat) => {
    const check = canAdd(feat);
    if (!check.ok) {
      setRuleError(check.msg);
      setTimeout(() => setRuleError(null), 3000);
      return;
    }
    setRuleError(null);

    // Evaluate prerequisites
    const prereqResult = evaluatePrerequisites(feat, character);
    if (!prereqResult.valid) {
      // Open GM Soft-Block Override Dialog
      setOverrideModalTarget({ feat, warnings: prereqResult.warnings });
    } else {
      // Add directly
      onAddFeat(feat);
    }
  };

  const handleConfirmOverride = () => {
    if (overrideModalTarget) {
      onAddFeat({
        ...overrideModalTarget.feat,
        is_overridden: true,
        override_reason: 'GM İzniyle Ezildi'
      });
      setOverrideModalTarget(null);
    }
  };

  const modal = (
    <div
      style={{
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(7, 6, 15, 0.96)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 99999, padding: '16px', boxSizing: 'border-box'
      }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="glass-card"
        style={{
          width: '100%', maxWidth: '850px', maxHeight: '88vh',
          display: 'flex', flexDirection: 'column', padding: '0',
          border: '1px solid rgba(201,168,76,0.45)',
          boxShadow: '0 0 40px rgba(0,0,0,0.95), 0 0 20px rgba(201,168,76,0.15)',
          boxSizing: 'border-box', overflow: 'hidden'
        }}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px 16px',
          borderBottom: '1px solid rgba(255,255,255,0.07)',
          flexShrink: 0
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ margin: 0, fontSize: '1.4rem', color: '#c9a84c', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'Cinzel, serif' }}>
              <Award size={20} />
              Feat Seçimi (Pathfinder 1e)
            </h3>
            <button
              onClick={onClose}
              style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', padding: '4px' }}
              onMouseOver={e => e.currentTarget.style.color = '#e94560'}
              onMouseOut={e => e.currentTarget.style.color = '#8b949e'}
            >
              <X size={24} />
            </button>
          </div>

          {/* Slots & Rule Hint */}
          <div style={{
            fontSize: '12px', color: '#8b949e', background: 'rgba(255,255,255,0.03)',
            borderRadius: '6px', padding: '8px 12px', marginBottom: '12px',
            border: '1px solid rgba(255,255,255,0.05)',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center'
          }}>
            <span>
              <b style={{ color: '#c9a84c' }}>Feat Motoru:</b> Ön koşullar canlı denetlenir. Uymayan feat'lerde <i>GM Override</i> seçeneği aktiftir.
            </span>
            <span style={{
              fontWeight: 'bold',
              color: selectedFeats.length >= maxFeats ? '#e94560' : '#c9a84c',
              background: 'rgba(201,168,76,0.1)', padding: '2px 10px', borderRadius: '12px',
              border: '1px solid rgba(201,168,76,0.2)'
            }}>
              Seçilen: {selectedFeats.length} / {maxFeats}
            </span>
          </div>

          {/* Selected Feats Chips */}
          {selectedFeats.length > 0 && (
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '10px' }}>
              {selectedFeats.map((f, i) => {
                const fname = f.isim || f.name || f;
                const isOverridden = f.is_overridden;
                return (
                  <span key={i} style={{
                    display: 'inline-flex', alignItems: 'center', gap: '6px',
                    background: isOverridden ? 'rgba(233,69,96,0.15)' : 'rgba(201,168,76,0.15)',
                    border: `1px solid ${isOverridden ? 'rgba(233,69,96,0.4)' : 'rgba(201,168,76,0.4)'}`,
                    borderRadius: '20px', padding: '4px 12px', fontSize: '12px', color: isOverridden ? '#fca5a5' : '#f0e6d2'
                  }}>
                    <Award size={12} style={{ color: isOverridden ? '#e94560' : '#c9a84c' }} />
                    {fname} {isOverridden && <span style={{ fontSize: '10px', color: '#f87171' }}>(GM Override)</span>}
                  </span>
                );
              })}
            </div>
          )}

          {/* Rule Error */}
          {ruleError && (
            <div style={{
              background: 'rgba(233,69,96,0.15)', border: '1px solid rgba(233,69,96,0.4)',
              borderRadius: '6px', padding: '8px 12px', marginBottom: '10px',
              fontSize: '13px', color: '#e94560', fontWeight: '500'
            }}>
              ⚠ {ruleError}
            </div>
          )}

          {/* Search Bar */}
          <div style={{
            background: 'rgba(34,34,59,0.6)', border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px', padding: '8px 14px', display: 'flex', alignItems: 'center', gap: '10px'
          }}>
            <Search size={16} style={{ color: '#8b949e', flexShrink: 0 }} />
            <input
              type="text"
              placeholder="Feat ismi veya açıklama ara (ör. Power Attack, Dodge)..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#f0e6d2', width: '100%', outline: 'none', fontSize: '13px' }}
            />
          </div>
        </div>

        {/* Category Tabs */}
        <div style={{
          display: 'flex', gap: '4px', padding: '12px 24px 0',
          overflowX: 'auto', flexShrink: 0, borderBottom: '1px solid rgba(255,255,255,0.05)'
        }}>
          {categories.map(cat => {
            const cfg = CATEGORY_CONFIG[cat];
            const Icon = cfg?.icon || Award;
            const isActive = activeCategory === cat;
            const count = catCounts[cat] || 0;

            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '5px',
                  padding: '8px 12px 10px', fontSize: '11px', fontWeight: isActive ? 'bold' : 'normal',
                  background: isActive ? `${cfg?.color || '#c9a84c'}18` : 'transparent',
                  border: 'none', borderBottom: isActive ? `2px solid ${cfg?.color || '#c9a84c'}` : '2px solid transparent',
                  color: isActive ? (cfg?.color || '#c9a84c') : '#8b949e',
                  cursor: 'pointer', whiteSpace: 'nowrap', flexShrink: 0, transition: 'all 0.15s',
                  borderRadius: '4px 4px 0 0'
                }}
              >
                {cat !== 'All' && <Icon size={13} style={{ flexShrink: 0 }} />}
                <span>{cat === 'All' ? 'Tümü' : (cfg?.short || cat)}</span>
                {count > 0 && (
                  <span style={{
                    background: isActive ? (cfg?.color || '#c9a84c') : 'rgba(255,255,255,0.1)',
                    color: isActive ? '#0d0d17' : '#8b949e',
                    fontSize: '9px', fontWeight: 'bold',
                    padding: '1px 5px', borderRadius: '8px', minWidth: '16px', textAlign: 'center'
                  }}>{count}</span>
                )}
              </button>
            );
          })}
        </div>

        {/* Feat List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px 24px 24px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#c9a84c' }}>Yükleniyor...</div>
          ) : feats.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#8b949e' }}>
              {searchQuery ? `"${searchQuery}" için feat bulunamadı.` : 'Bu kategoride feat bulunamadı.'}
            </div>
          ) : (
            feats.map((feat, idx) => {
              const featName = feat.isim || feat.name;
              const selected = isSelected(featName);
              const check = canAdd(feat);
              const cat = feat.sistem_verisi?.feat_category || 'General';
              const cfg = CATEGORY_CONFIG[cat] || { color: '#8b949e' };

              const sys = feat.sistem_verisi || {};
              const prereqs = sys.prerequisites || sys.prereqs;
              const isDummy = (str) => !str || ['benefit', 'benefit(s)', 'prerequisites', 'special', 'normal', 'description'].includes(String(str).trim().toLowerCase());
              const rawDesc = feat.aciklama && !isDummy(feat.aciklama) ? feat.aciklama : null;
              const rawSysBenefit = sys.benefit && !isDummy(sys.benefit) ? sys.benefit : null;
              const rawSysDesc = (sys.description?.value || sys.description) && !isDummy(sys.description?.value || sys.description) ? (sys.description?.value || sys.description) : null;
              const benefit = rawDesc || rawSysBenefit || rawSysDesc || feat.aciklama || '';

              const prereqEvaluation = evaluatePrerequisites(feat, character);

              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
                    gap: '12px', padding: '12px 16px',
                    background: selected ? `${cfg.color}18` : 'rgba(255,255,255,0.025)',
                    border: `1px solid ${selected ? cfg.color + '50' : 'rgba(255,255,255,0.05)'}`,
                    borderRadius: '8px',
                    opacity: !selected && !check.ok ? 0.5 : 1,
                    transition: 'all 0.15s'
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 'bold', color: '#f0e6d2', fontSize: '14px' }}>
                        {featName}
                      </span>
                      <span style={{
                        fontSize: '10px', padding: '2px 7px', borderRadius: '10px',
                        background: `${cfg.color}22`, color: cfg.color, border: `1px solid ${cfg.color}44`,
                        fontWeight: 'bold'
                      }}>
                        {cat}
                      </span>

                      {/* Validation Badges */}
                      {prereqEvaluation.valid ? (
                        <span style={{ fontSize: '10px', display: 'inline-flex', alignItems: 'center', gap: '3px', color: '#4ec9b0', background: 'rgba(78,201,176,0.12)', padding: '2px 6px', borderRadius: '4px', border: '1px solid rgba(78,201,176,0.3)' }}>
                          <CheckCircle2 size={10} /> Uygun
                        </span>
                      ) : (
                        <span style={{ fontSize: '10px', display: 'inline-flex', alignItems: 'center', gap: '3px', color: '#f87171', background: 'rgba(248,113,113,0.12)', padding: '2px 6px', borderRadius: '4px', border: '1px solid rgba(248,113,113,0.3)' }}>
                          <AlertTriangle size={10} /> Ön Koşul Eksik
                        </span>
                      )}
                    </div>

                    {/* Prerequisites display & warnings */}
                    {prereqs && (Array.isArray(prereqs) ? prereqs.length > 0 : prereqs !== '[]' && prereqs !== 'null') && (
                      <div style={{
                        fontSize: '11px', color: '#d7ba7d', background: 'rgba(215,186,125,0.08)',
                        borderRadius: '4px', padding: '3px 8px', margin: '4px 0 6px',
                        border: '1px solid rgba(215,186,125,0.2)', display: 'inline-block'
                      }}>
                        <b style={{ color: '#c9a84c' }}>Önkoşul:</b> {Array.isArray(prereqs) ? prereqs.join(', ') : String(prereqs)}
                      </div>
                    )}

                    {!prereqEvaluation.valid && (
                      <div style={{ fontSize: '11px', color: '#fca5a5', margin: '2px 0 6px' }}>
                        ⚠ {prereqEvaluation.warnings.join(' | ')}
                      </div>
                    )}

                    {/* Benefit / Description */}
                    {benefit && (
                      <div style={{ fontSize: '12px', color: '#8b949e', lineHeight: '1.4', maxHeight: '60px', overflow: 'hidden' }}>
                        {cleanText(benefit)}
                      </div>
                    )}
                  </div>

                  <div style={{ flexShrink: 0, display: 'flex', alignItems: 'center' }}>
                    {selected ? (
                      <span style={{
                        display: 'flex', alignItems: 'center', gap: '4px',
                        fontSize: '11px', color: cfg.color, fontWeight: 'bold',
                        padding: '6px 12px', borderRadius: '20px',
                        background: `${cfg.color}20`, border: `1px solid ${cfg.color}40`
                      }}>
                        ✓ Seçildi
                      </span>
                    ) : (
                      <button
                        className="btn btn-secondary"
                        disabled={!check.ok}
                        title={check.ok ? '' : check.msg}
                        style={{ padding: '6px 14px', fontSize: '12px', minHeight: 'unset' }}
                        onClick={() => handleSelectClick(feat)}
                      >
                        {!prereqEvaluation.valid ? '⚠ Seç (GM Override)' : '+ Seç'}
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* GM Soft-Block Override Confirmation Modal */}
        {overrideModalTarget && (
          <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(7, 6, 15, 0.96)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100000, padding: '16px'
          }}>
            <div className="sheet-card" style={{ maxWidth: '480px', width: '100%', padding: '24px', border: '1px solid var(--crimson-bright)', boxShadow: '0 0 30px rgba(233,69,96,0.3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#f87171', marginBottom: '12px' }}>
                <ShieldAlert size={24} />
                <h3 style={{ margin: 0, fontFamily: 'Cinzel, serif', fontSize: '1.2rem' }}>GM Kural Ezme (Override)</h3>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: '1.5' }}>
                <b>"{overrideModalTarget.feat.isim || overrideModalTarget.feat.name}"</b> seçimi için aşağıdaki ön koşullar karşılanmamıştır:
              </p>

              <div style={{ background: 'rgba(233,69,96,0.12)', border: '1px solid rgba(233,69,96,0.3)', padding: '10px 14px', borderRadius: '6px', margin: '12px 0', fontSize: '0.82rem', color: '#fca5a5' }}>
                {overrideModalTarget.warnings.map((w, i) => (
                  <div key={i} style={{ marginBottom: '4px' }}>• {w}</div>
                ))}
              </div>

              <p style={{ fontSize: '0.8rem', color: 'var(--gold-pale)', fontStyle: 'italic' }}>
                Pathfinder 1e GM Kuralları uyarınca hard-block yapılmaz. Game Master izniyle bu kuralı ezerek karaktere ekleyebilirsiniz.
              </p>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
                <button className="gold-btn" onClick={() => setOverrideModalTarget(null)} style={{ padding: '8px 16px', fontSize: '0.8rem' }}>
                  İptal
                </button>
                <button className="crimson-btn" onClick={handleConfirmOverride} style={{ padding: '8px 16px', fontSize: '0.8rem' }}>
                  ⚠ GM İzniyle Ekle (Override)
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );

  return ReactDOM.createPortal(modal, document.body);
}
