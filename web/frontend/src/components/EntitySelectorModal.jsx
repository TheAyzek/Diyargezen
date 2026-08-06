import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Search, X, ChevronDown, ChevronRight, Sparkles } from 'lucide-react';
import { cleanText, formatTitle, toSentenceCase } from '../utils/textSanitizer';
import { getEquipmentCategory, EQUIPMENT_CATEGORIES, MAIN_EQUIPMENT_CATEGORIES, SUB_EQUIPMENT_CATEGORIES, matchesEquipmentSubfilter } from '../utils/equipmentClassifier';

export default function EntitySelectorModal({ isOpen, onClose, system, category, title, onSelect }) {
  const [entities, setEntities] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [equipmentTypeFilter, setEquipmentTypeFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [expandedClasses, setExpandedClasses] = useState({});

  useEffect(() => {
    if (isOpen) {
      setEntities([]);
      setSearchQuery('');
      setExpandedClasses({});
      loadEntities();
    }
  }, [isOpen, category, system]);

  const loadEntities = () => {
    setLoading(true);
    let endpointCategory = category;
    if (category === 'equipment' || category === 'item') endpointCategory = 'equipment';
    else if (category === 'feats' || category === 'feat') endpointCategory = 'feats';
    else if (category === 'races' || category === 'race') endpointCategory = 'races';
    else if (category === 'classes' || category === 'class') endpointCategory = 'classes';
    else if (category === 'spells' || category === 'spell') endpointCategory = 'spells';
    else if (category === 'powers' || category === 'power') endpointCategory = 'powers';

    const sys = (system || 'pf1e').toLowerCase();
    axios.get(`/api/rules/${sys}/${endpointCategory}`, {
      params: { query: searchQuery }
    })
      .then(res => {
        setEntities(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching entities:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    if (isOpen && searchQuery !== '') {
      const delayDebounce = setTimeout(() => {
        loadEntities();
      }, 300);
      return () => clearTimeout(delayDebounce);
    }
  }, [searchQuery]);

  const toggleExpand = (className) => {
    setExpandedClasses(prev => ({
      ...prev,
      [className]: !prev[className]
    }));
  };

  if (!isOpen) return null;

  const isClassCategory = category === 'classes' || category === 'class';

  // Helper to group classes and archetypes
  const groupClasses = () => {
    const mainClasses = [];
    const archetypesMap = {};

    const baseNames = [
      "Alchemist", "Barbarian", "Bard", "Bloodrager", "Brawler", "Cavalier", "Cleric",
      "Druid", "Fighter", "Gunslinger", "Hunter", "Inquisitor", "Investigator", "Kineticist",
      "Magus", "Medium", "Mesmerist", "Monk", "Ninja", "Occultist", "Oracle", "Paladin",
      "Antipaladin", "Psychic", "Ranger", "Rogue", "Samurai", "Shaman", "Skald", "Slayer",
      "Sorcerer", "Spiritualist", "Summoner", "Swashbuckler", "Vigilante", "Warpriest", "Witch", "Wizard"
    ];

    entities.forEach(ent => {
      const name = ent.isim;
      const sysData = ent.sistem_verisi || {};
      const explicitParent = sysData.parent_class;
      const isArchetype = explicitParent || sysData.is_archetype || name.includes('(') || name.includes('Unchained') || !baseNames.includes(name);

      if (!isArchetype && baseNames.includes(name)) {
        mainClasses.push(ent);
      } else {
        let parentKey = explicitParent || 'Diğer Sınıflar & Archetype\'lar';
        if (!explicitParent) {
          for (const base of baseNames) {
            if (name.toLowerCase().includes(base.toLowerCase())) {
              parentKey = base;
              break;
            }
          }
        }
        if (!archetypesMap[parentKey]) archetypesMap[parentKey] = [];
        archetypesMap[parentKey].push(ent);
      }
    });

    return { mainClasses, archetypesMap };
  };

  const { mainClasses, archetypesMap } = isClassCategory ? groupClasses() : { mainClasses: [], archetypesMap: {} };

  const filteredGenericEntities = entities.filter(ent => {
    if (category === 'equipment' && equipmentTypeFilter !== 'all') {
      const cat = getEquipmentCategory(ent);
      if (!matchesEquipmentSubfilter(cat, equipmentTypeFilter)) return false;
    }
    if (searchQuery) {
      const q = searchQuery.trim().toLowerCase();
      const n = (ent.isim || ent.name || '').toLowerCase();
      const d = (ent.aciklama || ent.description || '').toLowerCase();
      return n.includes(q) || d.includes(q);
    }
    return true;
  });

  const modalJSX = (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(7, 6, 15, 0.96)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 99999,
        padding: '16px',
        boxSizing: 'border-box'
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div 
        className="glass-card animate-fade-in" 
        style={{
          width: '100%',
          maxWidth: '750px',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          padding: '24px',
          border: '1px solid rgba(201, 168, 76, 0.4)',
          boxShadow: '0 0 35px rgba(0, 0, 0, 0.9), 0 0 15px rgba(201, 168, 76, 0.2)',
          boxSizing: 'border-box',
          position: 'relative'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexShrink: 0 }}>
          <h3 style={{ fontSize: '1.4rem', color: '#c9a84c', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={20} /> {title}
          </h3>
          <button 
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '4px' }}
            onMouseOver={(e) => e.target.style.color = '#e94560'}
            onMouseOut={(e) => e.target.style.color = '#8b949e'}
          >
            <X size={24} />
          </button>
        </div>

        {/* Search Bar */}
        <div style={{ 
          background: 'rgba(34, 34, 59, 0.6)', 
          border: '1px solid rgba(255,255,255,0.1)', 
          borderRadius: '8px', 
          padding: '10px 14px', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '10px', 
          marginBottom: '16px',
          flexShrink: 0 
        }}>
          <Search size={18} style={{ color: '#8b949e' }} />
          <input 
            type="text" 
            placeholder={`${title} ara...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: '#f0e6d2', width: '100%', outline: 'none', fontSize: '14px' }}
          />
        </div>

        {/* Equipment Category Filter Pills */}
        {category === 'equipment' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
            {/* Main Categories Row */}
            <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px' }}>
              {(MAIN_EQUIPMENT_CATEGORIES || EQUIPMENT_CATEGORIES).map(cat => {
                const isActive = (equipmentTypeFilter === cat.id) || (equipmentTypeFilter && equipmentTypeFilter.startsWith(cat.id)) || (!equipmentTypeFilter && cat.id === 'all');
                return (
                  <button
                    key={cat.id}
                    onClick={() => setEquipmentTypeFilter(cat.id)}
                    style={{
                      fontSize: '11px',
                      padding: '5px 12px',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                      background: isActive ? 'rgba(201,168,76,0.25)' : 'rgba(255,255,255,0.04)',
                      border: isActive ? '1px solid #c9a84c' : '1px solid rgba(255,255,255,0.1)',
                      color: isActive ? '#ffd700' : '#8b949e',
                      fontWeight: isActive ? 'bold' : 'normal',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    {cat.label}
                  </button>
                );
              })}
            </div>

            {/* Sub-Categories Pills Row */}
            {(() => {
              const currentMainKey = Object.keys(SUB_EQUIPMENT_CATEGORIES).find(k => equipmentTypeFilter && (equipmentTypeFilter === k || equipmentTypeFilter.startsWith(k)));
              const subItems = currentMainKey ? SUB_EQUIPMENT_CATEGORIES[currentMainKey] : null;
              if (!subItems) return null;
              return (
                <div style={{ display: 'flex', gap: '4px', overflowX: 'auto', paddingBottom: '4px', paddingLeft: '6px', borderLeft: '2px solid rgba(201,168,76,0.3)' }}>
                  {subItems.map(sub => (
                    <button
                      key={sub.id}
                      onClick={() => setEquipmentTypeFilter(sub.id)}
                      style={{
                        fontSize: '10px',
                        padding: '3px 8px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                        background: equipmentTypeFilter === sub.id ? 'rgba(78,201,176,0.2)' : 'rgba(255,255,255,0.02)',
                        border: equipmentTypeFilter === sub.id ? '1px solid #4ec9b0' : '1px solid rgba(255,255,255,0.06)',
                        color: equipmentTypeFilter === sub.id ? '#7ee787' : '#8b949e',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      {sub.label}
                    </button>
                  ))}
                </div>
              );
            })()}
          </div>
        )}

        {/* Entities / Accordion List */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#c9a84c' }}>Aranıyor...</div>
          ) : entities.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#8b949e' }}>Sonuç bulunamadı.</div>
          ) : isClassCategory && !searchQuery && mainClasses.length > 0 ? (
            /* Class Category Accordion Grouping when browsing */
            mainClasses.map((cls, idx) => {
              const archetypes = archetypesMap[cls.isim] || [];
              const isExpanded = !!expandedClasses[cls.isim];

              return (
                <div 
                  key={idx}
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(201, 168, 76, 0.15)',
                    borderRadius: '8px',
                    padding: '14px 18px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
                    <div style={{ flex: 1, minWidth: '220px' }}>
                      <div style={{ fontWeight: 'bold', color: '#f0e6d2', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {cls.isim}
                        <span style={{ fontSize: '11px', background: '#22223b', color: '#c9a84c', padding: '2px 8px', borderRadius: '4px' }}>
                          Sınıf
                        </span>
                      </div>
                      {(() => {
                        const cleanDesc = cleanText(cls.aciklama || cls.description);
                        const sys = cls.sistem_verisi || {};
                        return (
                          <div style={{ marginTop: '6px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            <div style={{ fontSize: '13px', color: '#d4c5a9', lineHeight: '1.45' }}>
                              {cleanDesc || `${cls.isim} sınıfı kural detayları ve yetenek şablonu.`}
                            </div>
                            {sys.hit_die && (
                              <div style={{ fontSize: '11px', color: '#c9a84c', fontWeight: 'bold' }}>
                                Can Zarı: {sys.hit_die}
                              </div>
                            )}
                          </div>
                        );
                      })()}
                    </div>

                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexShrink: 0 }}>
                      <button 
                        className="btn btn-primary"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                        onClick={() => {
                          onSelect(cls);
                          onClose();
                        }}
                      >
                        Sınıfı Seç
                      </button>

                      {archetypes.length > 0 && (
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '6px 10px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}
                          onClick={() => toggleExpand(cls.isim)}
                        >
                          {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                          Archetypes ({archetypes.length})
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Expanded Archetypes Section */}
                  {(isExpanded || searchQuery) && archetypes.length > 0 && (
                    <div style={{ 
                      marginTop: '10px', 
                      paddingTop: '10px', 
                      borderTop: '1px dashed rgba(255,255,255,0.1)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px'
                    }}>
                      <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#c9a84c', marginBottom: '4px' }}>
                        {cls.isim} Alt Sınıfları (Archetypes):
                      </div>
                      {archetypes.map((arch, aIdx) => (
                        <div 
                          key={aIdx}
                          style={{
                            background: 'rgba(0, 0, 0, 0.25)',
                            border: '1px solid rgba(255, 255, 255, 0.05)',
                            borderRadius: '6px',
                            padding: '10px 14px',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            gap: '10px'
                          }}
                        >
                          <div style={{ flex: 1 }}>
                            <div style={{ fontWeight: 'bold', color: '#e2e8f0', fontSize: '14px' }}>
                              {arch.isim}
                            </div>
                            {arch.aciklama && (
                              <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>
                                {cleanText(arch.aciklama)}
                              </div>
                            )}
                          </div>
                          <button
                            className="btn btn-secondary"
                            style={{ padding: '4px 10px', fontSize: '11px', flexShrink: 0 }}
                            onClick={() => {
                              onSelect(arch);
                              onClose();
                            }}
                          >
                            Seç
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            /* Generic Categories (Races, Feats, Equipment, Spells) */
            filteredGenericEntities.map((ent, idx) => {
              const isRaceCategory = category === 'races' || category === 'race';
              const sv = ent.sistem_verisi || {};

              // Extract racial ability bonus text
              let racialBonusText = sv.ability_score_increase_text;
              if (!racialBonusText && sv.ability_score_increase && typeof sv.ability_score_increase === 'object') {
                const parts = Object.entries(sv.ability_score_increase).map(([k, v]) => `${v >= 0 ? '+' : ''}${v} ${k.charAt(0).toUpperCase() + k.slice(1)}`);
                if (parts.length > 0) racialBonusText = parts.join(', ');
              }
              const nameL = (ent.isim || ent.name || '').toLowerCase();
              if (!racialBonusText && (nameL.includes('human') || nameL.includes('half-elf') || nameL.includes('half-orc'))) {
                racialBonusText = '+2 Herhangi Bir Yetenek Puanı (Esnek Puan)';
              }

              const sizeText = sv.size || 'Medium';
              const speedText = sv.speed ? `${sv.speed} ft.` : null;
              const visionText = sv.vision ? `${sv.vision} ${sv.vision_range ? sv.vision_range + 'ft' : ''}` : null;
              const traitsList = Array.isArray(sv.traits) ? sv.traits.slice(0, 6) : [];

              return (
                <div 
                  key={idx}
                  onClick={() => {
                    onSelect(ent);
                    onClose();
                  }}
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(201, 168, 76, 0.18)',
                    borderRadius: '8px',
                    padding: '14px 18px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.background = 'rgba(201, 168, 76, 0.06)';
                    e.currentTarget.style.borderColor = 'rgba(201, 168, 76, 0.4)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
                    e.currentTarget.style.borderColor = 'rgba(201, 168, 76, 0.18)';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <div style={{ fontWeight: 'bold', color: '#f0e6d2', fontSize: '16px' }}>
                      {ent.isim}
                    </div>
                    {isRaceCategory && (
                      <div style={{ display: 'flex', gap: '6px' }}>
                        <span style={{ fontSize: '11px', background: 'rgba(201,168,76,0.15)', color: '#c9a84c', border: '1px solid rgba(201,168,76,0.3)', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold' }}>
                          {sizeText}
                        </span>
                        {speedText && (
                          <span style={{ fontSize: '11px', background: 'rgba(56,189,248,0.15)', color: '#38bdf8', border: '1px solid rgba(56,189,248,0.3)', padding: '2px 8px', borderRadius: '4px' }}>
                            {speedText}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Highlighted Racial Bonus Box */}
                  {isRaceCategory && racialBonusText && (
                    <div style={{
                      background: 'linear-gradient(90deg, rgba(201,168,76,0.12) 0%, rgba(63,185,80,0.08) 100%)',
                      border: '1px solid rgba(201,168,76,0.35)',
                      borderRadius: '6px',
                      padding: '6px 12px',
                      marginBottom: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <span style={{ fontSize: '13px', color: '#f0e6d2' }}>✨ <b>Irk Bonusları:</b></span>
                      <span style={{ fontSize: '13px', fontWeight: 'bold', color: '#3fb950' }}>
                        {racialBonusText}
                      </span>
                    </div>
                  )}

                  {/* Racial Traits Chips */}
                  {isRaceCategory && (traitsList.length > 0 || visionText) && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '8px' }}>
                      {visionText && (
                        <span style={{ fontSize: '10px', background: 'rgba(124,110,247,0.15)', color: '#a594ff', border: '1px solid rgba(124,110,247,0.3)', padding: '1px 6px', borderRadius: '3px' }}>
                          👁 {visionText}
                        </span>
                      )}
                      {traitsList.map((t, ti) => (
                        <span key={ti} style={{ fontSize: '10px', background: 'rgba(255,255,255,0.05)', color: '#d4c5a9', border: '1px solid rgba(255,255,255,0.1)', padding: '1px 6px', borderRadius: '3px' }}>
                          ✦ {formatTitle(t)}
                        </span>
                      ))}
                    </div>
                  )}

                  {ent.aciklama && (
                    <div style={{ fontSize: '13px', color: '#8b949e', lineHeight: '1.4' }}>
                      {cleanText(ent.aciklama.slice(0, 220)) + (ent.aciklama.length > 220 ? '...' : '')}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalJSX, document.body);
}
