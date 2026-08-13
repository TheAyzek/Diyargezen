import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Search, X, Wand2, BookOpen, Shield, Flame, Zap, AlertTriangle, CheckCircle2, Sparkles, Plus } from 'lucide-react';
import { getMaxSpellLevel, getMaxSpellsAllowed } from '../utils/spellLimitCalculator';
import { useDebounce } from '../utils/useDebounce';

const SCHOOL_COLORS = {
  evocation: '#e94560',
  abjuration: '#4ec9b0',
  transmutation: '#c9a84c',
  conjuration: '#7c6ef7',
  enchantment: '#ce9178',
  illusion: '#9cdcfe',
  divination: '#4caf50',
  necromancy: '#a5d6a7',
};

const CASTER_CLASSES = [
  'Wizard', 'Sorcerer', 'Cleric', 'Druid', 'Bard', 'Paladin',
  'Ranger', 'Magus', 'Witch', 'Oracle', 'Inquisitor', 'Alchemist'
];

export default function SpellSelectorModal({
  isOpen,
  onClose,
  system = 'pathfinder1e',
  characterClass = '',
  characterLevel = 1,
  selectedSpells = [],
  maxSpells = 99,
  onAddSpell
}) {
  const [spells, setSpells] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeLevel, setActiveLevel] = useState('All');
  const [selectedClass, setSelectedClass] = useState(characterClass || 'All');
  const [selectedSchool, setSelectedSchool] = useState('All');
  const [loading, setLoading] = useState(false);
  const [isOverridden, setIsOverridden] = useState(false);
  const [customSpellText, setCustomSpellText] = useState('');

  const maxSpellLevel = getMaxSpellLevel(characterClass || selectedClass, characterLevel);
  const maxAllowedSpells = Math.min(maxSpells, getMaxSpellsAllowed(characterClass || selectedClass, characterLevel));
  const isLimitReached = selectedSpells.length >= maxAllowedSpells;

  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const clientCache = useRef(new Map());

  useEffect(() => {
    if (isOpen) {
      if (characterClass && selectedClass === 'All') {
        setSelectedClass(characterClass);
      }
      fetchSpells();
    }
  }, [isOpen, system, activeLevel, selectedClass, selectedSchool, debouncedSearchQuery]);

  const NON_SPELL_REGEX = /^\s*[\#\*\+]|\b(scrolls?|wands?|potions?|oils?)\b|\bspecial abilities\b|\bmagic items?\b|\bspells\s*&\s*scrolls\b|\bcommon level\b|\buncommon level\b|\bgreater major\b|\blesser minor\b|\blesser medium\b|\bgreater medium\b|\bmajor potion\b|\bmedium potion\b|\bminor potion\b/i;

  const fetchSpells = () => {
    const lvlParam = activeLevel === 'All' ? '' : activeLevel;
    const classParam = selectedClass === 'All' ? '' : selectedClass;
    const schoolParam = selectedSchool === 'All' ? '' : selectedSchool;

    const sys = (system || 'pf1e').toLowerCase();
    const cacheKey = `${sys}_${lvlParam}_${classParam}_${schoolParam}_${debouncedSearchQuery}`;

    if (clientCache.current.has(cacheKey)) {
      setSpells(clientCache.current.get(cacheKey));
      setLoading(false);
      return;
    }

    setLoading(true);
    const queryParams = { query: debouncedSearchQuery };
    if (lvlParam !== '' && lvlParam !== null && lvlParam !== undefined) queryParams.level = lvlParam;
    if (classParam) queryParams.caster_class = classParam;
    if (schoolParam) queryParams.school = schoolParam;

    axios.get(`/api/rules/${sys}/spells`, { params: queryParams })
      .then(res => {
        const raw = res.data || [];
        const clean = raw.filter(sp => {
          const name = sp.isim || sp.name || '';
          return name && !NON_SPELL_REGEX.test(name);
        });
        clientCache.current.set(cacheKey, clean);
        setSpells(clean);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching spells:', err);
        setSpells([]);
        setLoading(false);
      });
  };


  if (!isOpen) return null;

  const isSelected = (spellName) => selectedSpells.some(s => (s.name || s.isim || s) === spellName);

  const handleSelectSpell = (spellEntity) => {
    const spellName = spellEntity.isim || spellEntity.name;
    if (isSelected(spellName)) return;

    const payload = {
      isim: spellName,
      name: spellName,
      level: spellEntity.sistem_verisi?.level ?? 0,
      school: spellEntity.sistem_verisi?.school || 'Universal',
      sistem_verisi: spellEntity.sistem_verisi || {},
      is_overridden: isOverridden
    };

    onAddSpell(payload);
  };

  const handleAddCustomSpell = () => {
    const name = customSpellText.trim();
    if (!name) return;

    onAddSpell({
      isim: name,
      name: name,
      level: activeLevel === 'All' ? 1 : Number(activeLevel),
      school: 'Custom',
      sistem_verisi: { description: 'Özel Eklenen Büyü' },
      is_overridden: true
    });
    setCustomSpellText('');
  };

  const levelTabs = ['All', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

  const modalContent = (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      backgroundColor: 'rgba(7, 6, 15, 0.96)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem'
    }}>
      <div style={{
        backgroundColor: '#121218', border: '1px solid #2a2a3a', borderRadius: '16px',
        width: '100%', maxWidth: '1000px', maxHeight: '90vh', display: 'flex', flexDirection: 'column',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)', overflow: 'hidden'
      }}>

        {/* Modal Header */}
        <div style={{
          padding: '1.25rem 1.5rem', borderBottom: '1px solid #2a2a3a',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: 'linear-gradient(135deg, #1a1a24 0%, #121218 100%)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '40px', height: '40px', borderRadius: '10px',
              backgroundColor: 'rgba(124, 110, 247, 0.15)', border: '1px solid #7c6ef7',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Wand2 size={22} color="#7c6ef7" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h2 style={{ color: '#fff', fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>
                  Büyü Seçimi (PF1e Spells)
                </h2>
                <span style={{ fontSize: '0.72rem', background: 'rgba(201,168,76,0.15)', color: 'var(--gold-bright)', border: '1px solid rgba(201,168,76,0.3)', padding: '2px 8px', borderRadius: '10px', fontWeight: 'bold' }}>
                  Kural Limiti: {selectedSpells.length} / {maxAllowedSpells} Büyü (Max Lv {maxSpellLevel})
                </span>
              </div>
              <p style={{ color: '#94a3b8', fontSize: '0.8rem', margin: '2px 0 0 0' }}>
                {characterClass || 'Büyücü'} Sınıfı için Seviye {characterLevel} büyü sınırı ve bilinen büyü kontrolleri.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {/* GM Override Checkbox */}
            <label style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              backgroundColor: isOverridden ? 'rgba(233, 69, 96, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${isOverridden ? '#e94560' : '#334155'}`,
              padding: '0.4rem 0.8rem', borderRadius: '8px', cursor: 'pointer',
              fontSize: '0.8rem', color: isOverridden ? '#ff6b81' : '#94a3b8'
            }}>
              <input
                type="checkbox"
                checked={isOverridden}
                onChange={(e) => setIsOverridden(e.target.checked)}
                style={{ cursor: 'pointer' }}
              />
              GM İzniyle Ez (Override)
            </label>

            <button
              onClick={onClose}
              style={{
                backgroundColor: 'transparent', border: 'none', color: '#94a3b8',
                cursor: 'pointer', padding: '0.5rem', borderRadius: '8px', display: 'flex'
              }}
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Filter Controls Bar */}
        <div style={{
          padding: '1rem 1.5rem', backgroundColor: '#181824', borderBottom: '1px solid #2a2a3a',
          display: 'flex', flexDirection: 'column', gap: '0.75rem'
        }}>
          {/* Search & Selectors */}
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: '220px', position: 'relative' }}>
              <Search size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                placeholder="Büyü adı ara..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: '100%', padding: '0.55rem 0.75rem 0.55rem 2.4rem',
                  backgroundColor: '#0f0f15', border: '1px solid #2a2a3a', borderRadius: '8px',
                  color: '#fff', fontSize: '0.85rem', outline: 'none'
                }}
              />
            </div>

            {/* Caster Class Selector */}
            <select
              value={selectedClass}
              onChange={(e) => setSelectedClass(e.target.value)}
              style={{
                padding: '0.55rem 0.75rem', backgroundColor: '#0f0f15', border: '1px solid #2a2a3a',
                borderRadius: '8px', color: '#fff', fontSize: '0.85rem', outline: 'none'
              }}
            >
              <option value="All">Tüm Sınıflar (All Classes)</option>
              {CASTER_CLASSES.map(cls => (
                <option key={cls} value={cls}>{cls}</option>
              ))}
            </select>

            {/* School Selector */}
            <select
              value={selectedSchool}
              onChange={(e) => setSelectedSchool(e.target.value)}
              style={{
                padding: '0.55rem 0.75rem', backgroundColor: '#0f0f15', border: '1px solid #2a2a3a',
                borderRadius: '8px', color: '#fff', fontSize: '0.85rem', outline: 'none'
              }}
            >
              <option value="All">Tüm Okullar (All Schools)</option>
              {Object.keys(SCHOOL_COLORS).map(s => (
                <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
              ))}
            </select>
          </div>

          {/* Level Tabs */}
          <div style={{ display: 'flex', items: 'center', gap: '0.4rem', overflowX: 'auto', paddingBottom: '0.2rem' }}>
            <span style={{ fontSize: '0.75rem', color: '#64748b', alignSelf: 'center', marginRight: '0.2rem' }}>Seviye:</span>
            {levelTabs.map(lvl => {
              const active = activeLevel === lvl;
              return (
                <button
                  key={lvl}
                  onClick={() => setActiveLevel(lvl)}
                  style={{
                    padding: '0.35rem 0.75rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 600,
                    cursor: 'pointer', border: '1px solid',
                    backgroundColor: active ? 'rgba(124, 110, 247, 0.25)' : 'rgba(255, 255, 255, 0.03)',
                    borderColor: active ? '#7c6ef7' : '#2a2a3a',
                    color: active ? '#a594ff' : '#94a3b8'
                  }}
                >
                  {lvl === 'All' ? 'Tümü' : `Lvl ${lvl}`}
                </button>
              );
            })}
          </div>
        </div>

        {/* Custom Spell Input Bar */}
        <div style={{
          padding: '0.75rem 1.5rem', backgroundColor: '#14141e', borderBottom: '1px solid #2a2a3a',
          display: 'flex', alignItems: 'center', gap: '0.75rem'
        }}>
          <input
            type="text"
            placeholder="Veritabanında bulunmayan özel büyü adı yazıp ekleyebilirsiniz..."
            value={customSpellText}
            onChange={(e) => setCustomSpellText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAddCustomSpell()}
            style={{
              flex: 1, padding: '0.45rem 0.75rem', backgroundColor: '#0f0f15',
              border: '1px solid #2a2a3a', borderRadius: '6px', color: '#fff', fontSize: '0.8rem'
            }}
          />
          <button
            onClick={handleAddCustomSpell}
            disabled={!customSpellText.trim()}
            style={{
              padding: '0.45rem 0.9rem', backgroundColor: '#7c6ef7', border: 'none',
              borderRadius: '6px', color: '#fff', fontSize: '0.8rem', fontWeight: 600,
              cursor: customSpellText.trim() ? 'pointer' : 'not-allowed', opacity: customSpellText.trim() ? 1 : 0.5,
              display: 'flex', alignItems: 'center', gap: '0.3rem'
            }}
          >
            <Plus size={14} /> Özel Büyü Ekle
          </button>
        </div>

        {/* Spells Grid List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem 1.5rem' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
              <Sparkles className="animate-spin" size={32} color="#7c6ef7" style={{ margin: '0 auto 1rem auto' }} />
              <div style={{ color: '#a594ff', fontWeight: 600, fontSize: '0.9rem' }}>Kadim Büyü Tomarları Açılıyor...</div>
              <div style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '4px' }}>Pathfinder 1e grimoire veritabanı taranıyor</div>
            </div>
          ) : spells.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
              Arama kriterlerine uygun büyü bulunamadı.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))', gap: '1rem' }}>
              {spells.map((spell, idx) => {
                const sv = spell.sistem_verisi || {};
                const name = spell.isim || spell.name;
                const level = sv.level ?? 0;
                const school = (sv.school || 'Universal').toLowerCase();
                const schoolColor = SCHOOL_COLORS[school] || '#9cdcfe';
                const alreadySelected = isSelected(name);

                return (
                  <div
                    key={spell.id || name || idx}
                    style={{
                      backgroundColor: '#161622', border: `1px solid ${alreadySelected ? '#4ec9b0' : '#2a2a3a'}`,
                      borderRadius: '12px', padding: '1rem', display: 'flex', flexDirection: 'column',
                      justify: 'space-between', gap: '0.75rem', transition: 'all 0.2s ease',
                      boxShadow: alreadySelected ? '0 0 12px rgba(78, 201, 176, 0.15)' : 'none'
                    }}
                  >
                    <div>
                      {/* Top Badges */}
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                        <span style={{
                          fontSize: '0.7rem', fontWeight: 700, padding: '0.2rem 0.5rem',
                          borderRadius: '4px', backgroundColor: `${schoolColor}20`, color: schoolColor,
                          border: `1px solid ${schoolColor}40`
                        }}>
                          Level {level} • {sv.school || 'Universal'}
                        </span>
                        {sv.casting_time && (
                          <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                            {sv.casting_time}
                          </span>
                        )}
                      </div>

                      {/* Title */}
                      <h3 style={{ color: '#fff', fontSize: '0.95rem', fontWeight: 700, margin: '0 0 0.4rem 0' }}>
                        {name}
                      </h3>

                      {/* Spell Properties */}
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', fontSize: '0.72rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
                        {sv.components && <span style={{ background: '#0f0f15', padding: '2px 6px', borderRadius: '4px' }}>Comp: {sv.components}</span>}
                        {sv.range && <span style={{ background: '#0f0f15', padding: '2px 6px', borderRadius: '4px' }}>Menzil: {sv.range}</span>}
                        {sv.saving_throw && <span style={{ background: '#0f0f15', padding: '2px 6px', borderRadius: '4px' }}>Save: {sv.saving_throw}</span>}
                      </div>

                      {/* Description Excerpt */}
                      <p style={{
                        color: '#cbd5e1', fontSize: '0.78rem', lineHeight: '1.4', margin: 0,
                        display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden'
                      }}>
                        {spell.aciklama || sv.description || 'Açıklama mevcut değil.'}
                      </p>
                    </div>

                    {/* Action Button */}
                    {(() => {
                      const isLevelTooHigh = level > maxSpellLevel;
                      const isRuleBlocked = (isLimitReached || isLevelTooHigh) && !isOverridden && !alreadySelected;

                      return (
                        <button
                          onClick={() => {
                            if (isRuleBlocked) {
                              if (window.confirm(`⚠️ Kural Uyarısı: ${isLevelTooHigh ? `Karakteriniz için Max Büyü Seviyesi ${maxSpellLevel}.` : `Büyü hakkı limiti (${maxAllowedSpells}) doldu.`}\n\nGM izniyle kuralı ezerek (Override) eklemek istiyor musunuz?`)) {
                                setIsOverridden(true);
                                handleSelectSpell(spell);
                              }
                            } else {
                              handleSelectSpell(spell);
                            }
                          }}
                          disabled={alreadySelected}
                          style={{
                            width: '100%', padding: '0.5rem', borderRadius: '8px',
                            backgroundColor: alreadySelected ? '#1e293b' : isRuleBlocked ? 'rgba(233,69,96,0.2)' : '#7c6ef7',
                            border: isRuleBlocked ? '1px solid #e94560' : 'none',
                            color: alreadySelected ? '#64748b' : isRuleBlocked ? '#ff6b81' : '#fff',
                            fontSize: '0.8rem', fontWeight: 600, cursor: alreadySelected ? 'default' : 'pointer',
                            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem',
                            transition: 'all 0.2s ease'
                          }}
                        >
                          {alreadySelected ? (
                            <>
                              <CheckCircle2 size={15} color="#4ec9b0" /> Seçildi
                            </>
                          ) : isRuleBlocked ? (
                            <>
                              <AlertTriangle size={15} color="#e94560" /> ⚠️ {isLevelTooHigh ? `Seviye Lv ${level} High` : 'Limit Doldu'} (Override)
                            </>
                          ) : (
                            <>
                              <Plus size={15} /> Büyü Defterine Ekle
                            </>
                          )}
                        </button>
                      );
                    })()}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '1rem 1.5rem', backgroundColor: '#121218', borderTop: '1px solid #2a2a3a',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between'
        }}>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
            Seçilen Büyüler: <b style={{ color: '#fff' }}>{selectedSpells.length}</b>
          </span>

          <button
            onClick={onClose}
            style={{
              padding: '0.5rem 1.25rem', backgroundColor: '#2a2a3a', border: 'none',
              borderRadius: '8px', color: '#fff', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer'
            }}
          >
            Tamam (Kapat)
          </button>
        </div>

      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
}
