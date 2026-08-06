import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Search, X, Shield, Heart, Sparkles, Users, Star, MapPin, BookOpen, Swords, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { cleanText } from '../utils/textSanitizer';

const CATEGORY_CONFIG = {
  Combat:   { icon: Swords,    color: '#e94560', label: 'Savaş (Combat)' },
  Faith:    { icon: Heart,     color: '#c9a84c', label: 'İnanç (Faith)' },
  Magic:    { icon: Sparkles,  color: '#7c6ef7', label: 'Büyü (Magic)' },
  Social:   { icon: Users,     color: '#4ec9b0', label: 'Sosyal (Social)' },
  Race:     { icon: Star,      color: '#ce9178', label: 'Irk (Race)' },
  Regional: { icon: MapPin,    color: '#6a9955', label: 'Bölgesel (Regional)' },
  Religion: { icon: BookOpen,  color: '#d7ba7d', label: 'Din (Religion)' },
  Campaign: { icon: Shield,    color: '#9cdcfe', label: 'Kampanya (Campaign)' },
};

function evaluateTraitPrerequisites(trait, character) {
  if (!character) return { valid: true, warnings: [] };
  const warnings = [];
  const sys = trait.sistem_verisi || {};
  let prereqs = sys.prerequisites || sys.prereqs || trait.prerequisites || [];
  if (typeof prereqs === 'string') prereqs = [prereqs];
  else if (!Array.isArray(prereqs)) prereqs = [];

  const scores = character.abilities || { strength: 10, dexterity: 10, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 };

  for (const p of prereqs) {
    const pStr = String(p).trim();
    if (!pStr) continue;
    const mAb = pStr.match(/(Str|Dex|Con|Int|Wis|Cha)\s*(\d+)/i);
    if (mAb) {
      const statMap = { str: 'strength', dex: 'dexterity', con: 'constitution', int: 'intelligence', wis: 'wisdom', cha: 'charisma' };
      const reqVal = parseInt(mAb[2], 10);
      const currVal = Number(scores[statMap[mAb[1].toLowerCase()]] || 10);
      if (currVal < reqVal) {
        warnings.push(`${mAb[1].toUpperCase()} >= ${reqVal} gerekli (Mevcut: ${currVal})`);
      }
    }
  }

  return { valid: warnings.length === 0, warnings };
}

export default function TraitSelectorModal({ isOpen, onClose, system, character, selectedTraits = [], onAddTrait }) {
  const [allTraits, setAllTraits] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [loading, setLoading] = useState(false);
  const [ruleError, setRuleError] = useState(null);
  const [overrideModalTarget, setOverrideModalTarget] = useState(null);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      axios.get(`/api/rules/${system}/traits`)
        .then(res => {
          setAllTraits(res.data);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }
  }, [isOpen, system]);

  if (!isOpen) return null;

  const categories = ['All', ...Object.keys(CATEGORY_CONFIG)];

  const filteredTraits = allTraits.filter(t => {
    const cat = t.sistem_verisi?.trait_category || 'Unknown';
    const matchCat = activeCategory === 'All' || cat === activeCategory;
    const q = searchQuery.toLowerCase();
    const matchQ = !q || t.isim.toLowerCase().includes(q) || (t.aciklama || '').toLowerCase().includes(q);
    return matchCat && matchQ;
  });

  const isSelected = (traitName) => selectedTraits.some(t => (t.isim || t.name) === traitName);
  
  const canAdd = (traitEntity) => {
    if (selectedTraits.length >= 2) return { ok: false, msg: 'Maksimum 2 trait seçebilirsiniz.' };
    const cat = traitEntity.sistem_verisi?.trait_category || 'Unknown';
    const sameCat = selectedTraits.find(t => (t.sistem_verisi?.trait_category || 'Unknown') === cat);
    if (sameCat) return { ok: false, msg: `"${cat}" kategorisinden zaten bir trait seçtiniz. (PF1e kuralı)` };
    if (isSelected(traitEntity.isim)) return { ok: false, msg: 'Bu trait zaten seçili.' };
    return { ok: true, msg: '' };
  };

  const handleSelectClick = (trait) => {
    const check = canAdd(trait);
    if (!check.ok) {
      setRuleError(check.msg);
      setTimeout(() => setRuleError(null), 3000);
      return;
    }
    setRuleError(null);

    const prereqRes = evaluateTraitPrerequisites(trait, character);
    if (!prereqRes.valid) {
      setOverrideModalTarget({ trait, warnings: prereqRes.warnings });
    } else {
      onAddTrait(trait);
    }
  };

  const handleConfirmOverride = () => {
    if (overrideModalTarget) {
      onAddTrait({
        ...overrideModalTarget.trait,
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
          width: '100%', maxWidth: '820px', maxHeight: '88vh',
          display: 'flex', flexDirection: 'column', padding: '0',
          border: '1px solid rgba(201,168,76,0.45)',
          boxShadow: '0 0 40px rgba(0,0,0,0.95), 0 0 20px rgba(201,168,76,0.15)',
          boxSizing: 'border-box', overflow: 'hidden'
        }}
      >
        {/* Modal Header */}
        <div style={{
          padding: '20px 24px 16px',
          borderBottom: '1px solid rgba(255,255,255,0.07)',
          flexShrink: 0
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ margin: 0, fontSize: '1.4rem', color: '#c9a84c', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'Cinzel, serif' }}>
              <BookOpen size={20} />
              Trait Seçimi (Pathfinder 1e)
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

          <div style={{
            fontSize: '12px', color: '#8b949e', background: 'rgba(255,255,255,0.03)',
            borderRadius: '6px', padding: '8px 12px', marginBottom: '12px',
            border: '1px solid rgba(255,255,255,0.05)',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center'
          }}>
            <span>
              <b style={{ color: '#c9a84c' }}>Kural:</b> En fazla 2 Trait seçilebilir ve her kategoriden sadece 1 Trait alınabilir.
            </span>
            <span style={{
              fontWeight: 'bold',
              color: selectedTraits.length >= 2 ? '#e94560' : '#c9a84c',
              background: 'rgba(201,168,76,0.1)', padding: '2px 10px', borderRadius: '12px',
              border: '1px solid rgba(201,168,76,0.2)'
            }}>
              Seçilen: {selectedTraits.length} / 2
            </span>
          </div>

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
              placeholder="Trait ismi veya açıklama ara..."
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
            const Icon = cfg?.icon || BookOpen;
            const isActive = activeCategory === cat;

            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '5px',
                  padding: '8px 14px', fontSize: '12px', fontWeight: isActive ? 'bold' : 'normal',
                  background: isActive ? 'rgba(201,168,76,0.15)' : 'transparent',
                  border: 'none', borderBottom: isActive ? `2px solid ${cfg?.color || '#c9a84c'}` : '2px solid transparent',
                  color: isActive ? (cfg?.color || '#c9a84c') : '#8b949e',
                  cursor: 'pointer', whiteSpace: 'nowrap', flexShrink: 0, transition: 'all 0.15s',
                  borderRadius: '4px 4px 0 0', paddingBottom: '10px'
                }}
              >
                {cat !== 'All' && <Icon size={14} />}
                {cat === 'All' ? 'Tümü' : (cfg?.label?.split(' ')[0] || cat)}
              </button>
            );
          })}
        </div>

        {/* Trait List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px 24px 24px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#c9a84c' }}>Yükleniyor...</div>
          ) : filteredTraits.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#8b949e' }}>
              {searchQuery ? `"${searchQuery}" için trait bulunamadı.` : 'Bu kategoride trait bulunamadı.'}
            </div>
          ) : (
            filteredTraits.map((trait, idx) => {
              const traitName = trait.isim || trait.name;
              const selected = isSelected(traitName);
              const check = canAdd(trait);
              const cat = trait.sistem_verisi?.trait_category || 'Unknown';
              const cfg = CATEGORY_CONFIG[cat] || { color: '#8b949e' };
              const prereqEvaluation = evaluateTraitPrerequisites(trait, character);

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
                        {traitName}
                      </span>
                      <span style={{
                        fontSize: '10px', padding: '2px 7px', borderRadius: '10px',
                        background: `${cfg.color}22`, color: cfg.color, border: `1px solid ${cfg.color}44`,
                        fontWeight: 'bold'
                      }}>
                        {cat}
                      </span>
                      {prereqEvaluation.valid ? (
                        <span style={{ fontSize: '10px', color: '#4ec9b0' }}>✓ Uygun</span>
                      ) : (
                        <span style={{ fontSize: '10px', color: '#f87171' }}>⚠ Ön Koşul Var</span>
                      )}
                    </div>

                    {!prereqEvaluation.valid && (
                      <div style={{ fontSize: '11px', color: '#fca5a5', margin: '2px 0 4px' }}>
                        ⚠ {prereqEvaluation.warnings.join(' | ')}
                      </div>
                    )}

                    <div style={{ fontSize: '12px', color: '#8b949e', lineHeight: '1.4' }}>
                      {cleanText(trait.aciklama)}
                    </div>
                  </div>

                  <div style={{ flexShrink: 0, display: 'flex', alignItems: 'center' }}>
                    {selected ? (
                      <span style={{
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
                        onClick={() => handleSelectClick(trait)}
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
                <b>"{overrideModalTarget.trait.isim || overrideModalTarget.trait.name}"</b> seçimi için ön koşullar karşılanmamıştır:
              </p>

              <div style={{ background: 'rgba(233,69,96,0.12)', border: '1px solid rgba(233,69,96,0.3)', padding: '10px 14px', borderRadius: '6px', margin: '12px 0', fontSize: '0.82rem', color: '#fca5a5' }}>
                {overrideModalTarget.warnings.map((w, i) => (
                  <div key={i} style={{ marginBottom: '4px' }}>• {w}</div>
                ))}
              </div>

              <p style={{ fontSize: '0.8rem', color: 'var(--gold-pale)', fontStyle: 'italic' }}>
                Pathfinder 1e GM Kuralları uyarınca Game Master izniyle bu kuralı ezerek karaktere ekleyebilirsiniz.
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
