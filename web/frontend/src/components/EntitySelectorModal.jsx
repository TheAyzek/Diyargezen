import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Search, X, ChevronDown, ChevronRight, Sparkles } from 'lucide-react';

export default function EntitySelectorModal({ isOpen, onClose, system, category, title, onSelect }) {
  const [entities, setEntities] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedClasses, setExpandedClasses] = useState({});

  useEffect(() => {
    if (isOpen) {
      loadEntities();
    }
  }, [isOpen, category, system]);

  const loadEntities = () => {
    setLoading(true);
    let endpointCategory = category;
    if (category === 'equipment') endpointCategory = 'equipment';
    else if (category === 'feats') endpointCategory = 'feats';
    else if (category === 'races') endpointCategory = 'races';
    else if (category === 'classes') endpointCategory = 'classes';
    else if (category === 'spells') endpointCategory = 'spells';
    else if (category === 'powers') endpointCategory = 'powers';

    axios.get(`/api/rules/${system}/${endpointCategory}`, {
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
    if (isOpen) {
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

  const isClassCategory = category === 'classes';

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

  const modalJSX = (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(15, 15, 26, 0.88)',
        backdropFilter: 'blur(10px)',
        WebkitBackdropFilter: 'blur(10px)',
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

        {/* Entities / Accordion List */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#c9a84c' }}>Aranıyor...</div>
          ) : entities.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#8b949e' }}>Sonuç bulunamadı.</div>
          ) : isClassCategory ? (
            /* Class Category Accordion Grouping */
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
                      {cls.aciklama && (
                        <div 
                          style={{ fontSize: '13px', color: '#8b949e', marginTop: '6px', lineHeight: '1.4' }}
                          dangerouslySetInnerHTML={{ __html: cls.aciklama }}
                        />
                      )}
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
                  {isExpanded && archetypes.length > 0 && (
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
                              <div 
                                style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}
                                dangerouslySetInnerHTML={{ __html: arch.aciklama }}
                              />
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
            entities.map((ent, idx) => (
              <div 
                key={idx}
                onClick={() => {
                  onSelect(ent);
                  onClose();
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.05)',
                  borderRadius: '8px',
                  padding: '14px 18px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = 'rgba(201, 168, 76, 0.05)';
                  e.currentTarget.style.borderColor = 'rgba(201, 168, 76, 0.3)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                }}
              >
                <div style={{ fontWeight: 'bold', color: '#f0e6d2', marginBottom: '6px', fontSize: '15px' }}>
                  {ent.isim}
                </div>
                {ent.aciklama && (
                  <div 
                    style={{ fontSize: '13px', color: '#8b949e', lineHeight: '1.4' }}
                    dangerouslySetInnerHTML={{ __html: ent.aciklama }}
                  />
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalJSX, document.body);
}
