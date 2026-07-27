import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Search, X, Shield, Heart, Sparkles, Users, Star, MapPin, BookOpen, Swords } from 'lucide-react';

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

export default function TraitSelectorModal({ isOpen, onClose, system, selectedTraits = [], onAddTrait }) {
  const [allTraits, setAllTraits] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [loading, setLoading] = useState(false);
  const [ruleError, setRuleError] = useState(null);

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

  const isSelected = (traitName) => selectedTraits.some(t => t.isim === traitName);
  
  const canAdd = (traitEntity) => {
    if (selectedTraits.length >= 2) return { ok: false, msg: 'Maksimum 2 trait seçebilirsiniz.' };
    const cat = traitEntity.sistem_verisi?.trait_category || 'Unknown';
    const sameCat = selectedTraits.find(t => (t.sistem_verisi?.trait_category || 'Unknown') === cat);
    if (sameCat) return { ok: false, msg: `"${cat}" kategorisinden zaten bir trait seçtiniz.` };
    if (isSelected(traitEntity.isim)) return { ok: false, msg: 'Bu trait zaten seçili.' };
    return { ok: true, msg: '' };
  };

  const handleAddTrait = (trait) => {
    const check = canAdd(trait);
    if (!check.ok) {
      setRuleError(check.msg);
      setTimeout(() => setRuleError(null), 3000);
      return;
    }
    setRuleError(null);
    onAddTrait(trait);
  };

  // Group displayed traits by category
  const grouped = filteredTraits.reduce((acc, t) => {
    const cat = t.sistem_verisi?.trait_category || 'Diğer';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(t);
    return acc;
  }, {});

  const modal = (
    <div
      style={{
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(10,10,20,0.90)',
        backdropFilter: 'blur(10px)',
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
            <h3 style={{ margin: 0, fontSize: '1.4rem', color: '#c9a84c', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Shield size={20} />
              Trait Seçimi (Pathfinder 1e)
            </h3>
            <button onClick={onClose}
              style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', padding: '4px' }}
              onMouseOver={e => e.currentTarget.style.color = '#e94560'}
              onMouseOut={e => e.currentTarget.style.color = '#8b949e'}
            >
              <X size={24} />
            </button>
          </div>

          {/* Rule hint */}
          <div style={{
            fontSize: '12px', color: '#8b949e', background: 'rgba(255,255,255,0.03)',
            borderRadius: '6px', padding: '8px 12px', marginBottom: '12px',
            border: '1px solid rgba(255,255,255,0.05)'
          }}>
            <span style={{ color: '#c9a84c', fontWeight: 'bold' }}>PF1e Kuralı:</span>{' '}
            Aynı kategoriden olmamak koşuluyla en fazla <b style={{ color: '#f0e6d2' }}>2 adet</b> trait seçebilirsiniz.
            Şu an seçili: <b style={{ color: selectedTraits.length === 2 ? '#e94560' : '#c9a84c' }}>{selectedTraits.length} / 2</b>
          </div>

          {/* Selected traits preview */}
          {selectedTraits.length > 0 && (
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '10px' }}>
              {selectedTraits.map(t => {
                const cat = t.sistem_verisi?.trait_category || 'Unknown';
                const cfg = CATEGORY_CONFIG[cat] || {};
                return (
                  <span key={t.isim} style={{
                    display: 'inline-flex', alignItems: 'center', gap: '6px',
                    background: 'rgba(201,168,76,0.12)', border: `1px solid ${cfg.color || '#c9a84c'}50`,
                    borderRadius: '20px', padding: '4px 12px', fontSize: '12px', color: '#f0e6d2'
                  }}>
                    <span style={{ color: cfg.color || '#c9a84c', fontWeight: 'bold', fontSize: '11px' }}>{cat}</span>
                    {t.isim}
                  </span>
                );
              })}
            </div>
          )}

          {/* Rule error */}
          {ruleError && (
            <div style={{
              background: 'rgba(233,69,96,0.15)', border: '1px solid rgba(233,69,96,0.4)',
              borderRadius: '6px', padding: '8px 12px', marginBottom: '10px',
              fontSize: '13px', color: '#e94560', fontWeight: '500'
            }}>
              ⚠ {ruleError}
            </div>
          )}

          {/* Search bar */}
          <div style={{
            background: 'rgba(34,34,59,0.6)', border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px', padding: '8px 14px', display: 'flex', alignItems: 'center', gap: '10px'
          }}>
            <Search size={16} style={{ color: '#8b949e', flexShrink: 0 }} />
            <input
              type="text"
              placeholder="Trait ara..."
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
            const Icon = cfg?.icon;
            const isActive = activeCategory === cat;
            // Count how many selected traits are from this category
            const selCount = cat === 'All' ? selectedTraits.length : 
              selectedTraits.filter(t => (t.sistem_verisi?.trait_category || '') === cat).length;
            const isBlocked = cat !== 'All' && selCount > 0 && selectedTraits.length > 0;

            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '5px',
                  padding: '8px 14px', fontSize: '12px', fontWeight: isActive ? 'bold' : 'normal',
                  background: isActive ? 'rgba(201,168,76,0.15)' : 'transparent',
                  border: 'none', borderBottom: isActive ? `2px solid ${cfg?.color || '#c9a84c'}` : '2px solid transparent',
                  color: isActive ? (cfg?.color || '#c9a84c') : (isBlocked ? '#555' : '#8b949e'),
                  cursor: 'pointer', whiteSpace: 'nowrap', flexShrink: 0, transition: 'all 0.15s',
                  borderRadius: '4px 4px 0 0',
                  paddingBottom: '10px',
                }}
              >
                {Icon && <Icon size={14} />}
                {cat === 'All' ? 'Tümü' : (cfg?.label?.split(' ')[0] || cat)}
                {selCount > 0 && (
                  <span style={{
                    background: cfg?.color || '#c9a84c', color: '#0f0f1a',
                    borderRadius: '10px', padding: '1px 6px', fontSize: '10px', fontWeight: 'bold'
                  }}>{selCount}</span>
                )}
              </button>
            );
          })}
        </div>

        {/* Trait List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px 24px 24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#c9a84c' }}>Yükleniyor...</div>
          ) : filteredTraits.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#8b949e' }}>
              {searchQuery ? `"${searchQuery}" için sonuç bulunamadı.` : 'Bu kategoride trait bulunamadı.'}
            </div>
          ) : (
            Object.entries(grouped).map(([cat, traits]) => {
              const cfg = CATEGORY_CONFIG[cat] || { color: '#8b949e', label: cat };
              const Icon = cfg.icon || Shield;
              return (
                <div key={cat}>
                  {activeCategory === 'All' && (
                    <div style={{
                      display: 'flex', alignItems: 'center', gap: '8px',
                      marginBottom: '8px', paddingBottom: '6px',
                      borderBottom: `1px solid ${cfg.color}30`
                    }}>
                      <Icon size={16} style={{ color: cfg.color }} />
                      <span style={{ color: cfg.color, fontSize: '13px', fontWeight: 'bold', letterSpacing: '0.05em' }}>
                        {cfg.label || cat}
                      </span>
                    </div>
                  )}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {traits.map((trait, idx) => {
                      const selected = isSelected(trait.isim);
                      const check = canAdd(trait);
                      const bonuses = trait.sistem_verisi?.bonuses || [];

                      return (
                        <div
                          key={idx}
                          style={{
                            display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
                            gap: '12px', padding: '12px 16px',
                            background: selected
                              ? `${cfg.color}18`
                              : 'rgba(255,255,255,0.025)',
                            border: `1px solid ${selected ? cfg.color + '50' : 'rgba(255,255,255,0.05)'}`,
                            borderRadius: '8px',
                            opacity: !selected && !check.ok ? 0.5 : 1,
                            transition: 'all 0.15s'
                          }}
                        >
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '4px' }}>
                              <span style={{ fontWeight: 'bold', color: '#f0e6d2', fontSize: '14px' }}>
                                {trait.isim}
                              </span>
                              <span style={{
                                fontSize: '10px', padding: '2px 7px', borderRadius: '10px',
                                background: `${cfg.color}22`, color: cfg.color, border: `1px solid ${cfg.color}44`,
                                fontWeight: 'bold'
                              }}>
                                {cat}
                              </span>
                            </div>
                            {/* Clean description (strip HTML for the modal) */}
                            <div style={{ fontSize: '12px', color: '#8b949e', lineHeight: '1.5' }}
                              dangerouslySetInnerHTML={{ __html: trait.aciklama || '' }}
                            />
                            {/* Bonus chips */}
                            {bonuses.length > 0 && (
                              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                                {bonuses.map((b, bi) => (
                                  <span key={bi} style={{
                                    fontSize: '10px', padding: '2px 8px', borderRadius: '10px',
                                    background: 'rgba(76,201,176,0.1)', color: '#4ec9b0',
                                    border: '1px solid rgba(76,201,176,0.25)', fontWeight: 'bold'
                                  }}>
                                    {b.type === 'skill'
                                      ? `+${b.value} ${b.skill}${b.makes_class_skill ? ' (Sınıf Becerisi)' : ''}`
                                      : b.type === 'save_will' ? `+${b.value} Will`
                                      : b.type === 'save_fortitude' ? `+${b.value} Fortitude`
                                      : b.type === 'save_reflex' ? `+${b.value} Reflex`
                                      : b.type === 'save_all' ? `+${b.value} Tüm Kurtarma Zarları`
                                      : b.type === 'initiative' ? `+${b.value} Initiative`
                                      : b.type === 'concentration' ? `+${b.value} Konsantrasyon`
                                      : b.type === 'armor_class' ? `+${b.value} Zırh Sınıfı`
                                      : b.type === 'starting_gold' ? `${b.value} GP Başlangıç`
                                      : b.type === 'caster_level' ? `+${b.value} Caster Level`
                                      : `${b.type}: +${b.value}`}
                                  </span>
                                ))}
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
                                onClick={() => handleAddTrait(trait)}
                              >
                                + Seç
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modal, document.body);
}
