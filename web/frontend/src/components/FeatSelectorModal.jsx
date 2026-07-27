import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Search, X, Swords, Users, Sparkles, Hammer, Star, Shield, Award, HelpCircle } from 'lucide-react';

const CATEGORY_CONFIG = {
  Combat:        { icon: Swords,    color: '#e94560', label: 'Savaş (Combat)' },
  Teamwork:      { icon: Users,     color: '#4ec9b0', label: 'İşbirliği (Teamwork)' },
  Metamagic:     { icon: Sparkles,  color: '#7c6ef7', label: 'Metamagic' },
  'Item Creation': { icon: Hammer,  color: '#c9a84c', label: 'Eşya Üretimi (Item Creation)' },
  Racial:        { icon: Star,      color: '#ce9178', label: 'Irk (Racial)' },
  Mythic:        { icon: Award,     color: '#f39c12', label: 'Mythic' },
  General:       { icon: Shield,    color: '#9cdcfe', label: 'Genel (General)' },
};

export default function FeatSelectorModal({
  isOpen,
  onClose,
  system,
  selectedFeats = [],
  maxFeats = 1,
  onAddFeat
}) {
  const [feats, setFeats] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [loading, setLoading] = useState(false);
  const [ruleError, setRuleError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchFeats();
    }
  }, [isOpen, system, activeCategory, searchQuery]);

  const fetchFeats = () => {
    setLoading(true);
    const cat = activeCategory === 'All' ? '' : activeCategory;
    axios.get(`/api/rules/${system}/feats`, {
      params: { query: searchQuery, category: cat }
    })
      .then(res => {
        setFeats(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Feats fetch error:', err);
        setLoading(false);
      });
  };

  if (!isOpen) return null;

  const categories = ['All', ...Object.keys(CATEGORY_CONFIG)];

  const isSelected = (featName) => selectedFeats.some(f => (f.isim || f) === featName);

  const canAdd = (featEntity) => {
    if (selectedFeats.length >= maxFeats) {
      return { ok: false, msg: `Bu seviyede en fazla ${maxFeats} feat seçebilirsiniz.` };
    }
    const featName = featEntity.isim || featEntity;
    if (isSelected(featName)) {
      return { ok: false, msg: 'Bu feat zaten seçili.' };
    }
    return { ok: true, msg: '' };
  };

  const handleAddFeat = (feat) => {
    const check = canAdd(feat);
    if (!check.ok) {
      setRuleError(check.msg);
      setTimeout(() => setRuleError(null), 3000);
      return;
    }
    setRuleError(null);
    onAddFeat(feat);
  };

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
            <h3 style={{ margin: 0, fontSize: '1.4rem', color: '#c9a84c', display: 'flex', alignItems: 'center', gap: '8px' }}>
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
              <b style={{ color: '#c9a84c' }}>Feat Kotası:</b> Karakter seviyesi, ırkı ve sınıf bonuslarına göre hesaplanmıştır.
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
                const fname = f.isim || f;
                return (
                  <span key={i} style={{
                    display: 'inline-flex', alignItems: 'center', gap: '6px',
                    background: 'rgba(201,168,76,0.15)', border: '1px solid rgba(201,168,76,0.4)',
                    borderRadius: '20px', padding: '4px 12px', fontSize: '12px', color: '#f0e6d2'
                  }}>
                    <Award size={12} style={{ color: '#c9a84c' }} />
                    {fname}
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
              placeholder="Feat ismi ara (ör. Power Attack, Dodge)..."
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
              const benefit = sys.benefit || feat.aciklama;

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
                    </div>

                    {/* Prerequisites badge */}
                    {prereqs && (Array.isArray(prereqs) ? prereqs.length > 0 : prereqs !== '[]' && prereqs !== 'null') && (
                      <div style={{
                        fontSize: '11px', color: '#d7ba7d', background: 'rgba(215,186,125,0.08)',
                        borderRadius: '4px', padding: '3px 8px', margin: '4px 0 6px',
                        border: '1px solid rgba(215,186,125,0.2)', display: 'inline-block'
                      }}>
                        <b style={{ color: '#c9a84c' }}>Önkoşul:</b> {Array.isArray(prereqs) ? prereqs.join(', ') : String(prereqs)}
                      </div>
                    )}

                    {/* Benefit / Description */}
                    {benefit && (
                      <div
                        style={{ fontSize: '12px', color: '#8b949e', lineHeight: '1.4', maxHeight: '60px', overflow: 'hidden' }}
                        dangerouslySetInnerHTML={{ __html: String(benefit) }}
                      />
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
                        onClick={() => handleAddFeat(feat)}
                      >
                        + Seç
                      </button>
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

  return ReactDOM.createPortal(modal, document.body);
}
