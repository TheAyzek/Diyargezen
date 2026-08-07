import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { Search, X, Wand2, Shield, Zap, AlertTriangle, CheckCircle2, Award, BookOpen } from 'lucide-react';
import { cleanText } from '../utils/textSanitizer';

function evaluatePrerequisites(feature, character) {
  if (!character) return { valid: true, warnings: [] };

  const warnings = [];
  const sys = feature.sistem_verisi || {};
  let prereqs = sys.prerequisites || sys.prereqs || feature.prerequisites || [];
  if (typeof prereqs === 'string') prereqs = [prereqs];
  else if (!Array.isArray(prereqs)) prereqs = [];

  const charLevel = Number(character.level || character.characterLevel || 1);

  // Level requirement check e.g. "Barbarian level 6th", "Rogue level 4"
  for (const p of prereqs) {
    const pStr = String(p).trim();
    if (!pStr) continue;

    const mLvl = pStr.match(/(?:level|lvl)\s*(\d+)/i);
    if (mLvl) {
      const reqLvl = parseInt(mLvl[1], 10);
      if (charLevel < reqLvl) {
        warnings.push(`Seviye ${reqLvl} gerekli (Mevcut Seviye: ${charLevel})`);
      }
    }
  }

  return { valid: warnings.length === 0, warnings };
}

export default function ClassFeatureSelectorModal({
  isOpen,
  onClose,
  system = 'pf1e',
  characterClass = '',
  characterLevel = 1,
  character = {},
  selectedFeatures = [],
  onAddFeature
}) {
  const [features, setFeatures] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [overrideModalTarget, setOverrideModalTarget] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchFeatures();
    }
  }, [isOpen, system, characterClass, searchQuery]);

  const fetchFeatures = () => {
    setLoading(true);
    const sys = (system || 'pf1e').toLowerCase();
    const cls = characterClass || character?.class || character?.className || '';
    axios.get(`/api/rules/${sys}/class-features`, {
      params: {
        class_name: cls,
        query: searchQuery
      }
    })
      .then(res => {
        setFeatures(res.data || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching class features:', err);
        setFeatures([]);
        setLoading(false);
      });
  };

  if (!isOpen) return null;

  const isSelected = (featureName) => selectedFeatures.some(f => (f.isim || f.name || f) === featureName);

  const handleSelectFeature = (featEntity) => {
    const featureName = featEntity.isim || featEntity.name;
    if (isSelected(featureName)) return;

    const prereqsEval = evaluatePrerequisites(featEntity, { ...character, level: characterLevel });
    if (!prereqsEval.valid) {
      setOverrideModalTarget({ feature: featEntity, warnings: prereqsEval.warnings });
    } else {
      onAddFeature(featEntity);
    }
  };

  const handleConfirmOverride = () => {
    if (overrideModalTarget) {
      onAddFeature({
        ...overrideModalTarget.feature,
        is_overridden: true,
        override_reason: 'GM İzniyle Ezildi'
      });
      setOverrideModalTarget(null);
    }
  };

  const modalContent = (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 9999,
        background: 'rgba(5, 5, 12, 0.85)', backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px'
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%', maxWidth: '780px', maxHeight: '85vh',
          background: 'linear-gradient(180deg, #161426 0%, #0d0b18 100%)',
          border: '1px solid var(--accent-gold, #c9a84c)', borderRadius: '12px',
          boxShadow: '0 20px 50px rgba(0,0,0,0.8), 0 0 30px rgba(201,168,76,0.15)',
          display: 'flex', flexDirection: 'column', overflow: 'hidden'
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: '16px 24px', borderBottom: '1px solid rgba(201,168,76,0.2)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          background: 'rgba(255,255,255,0.02)'
        }}>
          <div>
            <h3 style={{ margin: 0, color: 'var(--accent-gold, #c9a84c)', fontFamily: 'Cinzel, serif', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Wand2 size={20} /> {characterClass || 'Sınıf'} Özel Yetenekleri (Class Features)
            </h3>
            <span style={{ fontSize: '0.78rem', color: '#8b949e' }}>
              Rage Powers, Rogue Talents, Discoveries, Hexes, Arcana, Revelations vb.
            </span>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#8b949e', cursor: 'pointer', padding: '4px' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Search Filter */}
        <div style={{ padding: '16px 24px 0' }}>
          <div style={{
            background: 'rgba(34,34,59,0.6)', border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px', padding: '8px 14px', display: 'flex', alignItems: 'center', gap: '10px'
          }}>
            <Search size={16} style={{ color: '#8b949e', flexShrink: 0 }} />
            <input
              type="text"
              placeholder={`${characterClass} yeteneği ismi veya açıklama ara...`}
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#f0e6d2', width: '100%', outline: 'none', fontSize: '13px' }}
            />
          </div>
        </div>

        {/* List Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px 24px 24px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#c9a84c' }}>Yetenekler Yükleniyor...</div>
          ) : features.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#8b949e' }}>
              {searchQuery ? `"${searchQuery}" aramanıza uygun yetenek bulunamadı.` : `${characterClass} için özel yetenek bulunamadı.`}
            </div>
          ) : (
            features.map((feat, idx) => {
              const featName = feat.isim || feat.name;
              const selected = isSelected(featName);
              const prereqsEval = evaluatePrerequisites(feat, { ...character, level: characterLevel });

              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
                    gap: '12px', padding: '12px 16px',
                    background: selected ? 'rgba(243,156,18,0.15)' : 'rgba(255,255,255,0.025)',
                    border: `1px solid ${selected ? 'rgba(243,156,18,0.4)' : 'rgba(255,255,255,0.05)'}`,
                    borderRadius: '8px',
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
                        background: 'rgba(243,156,18,0.2)', color: '#f39c12', border: '1px solid rgba(243,156,18,0.4)',
                        fontWeight: 'bold'
                      }}>
                        {characterClass} Yeteneği
                      </span>
                      {prereqsEval.valid ? (
                        <span style={{ fontSize: '10px', color: '#4ec9b0' }}>✓ Uygun</span>
                      ) : (
                        <span style={{ fontSize: '10px', color: '#f87171' }}>⚠ Şart Eksik</span>
                      )}
                    </div>

                    {!prereqsEval.valid && (
                      <div style={{ fontSize: '11px', color: '#fca5a5', margin: '2px 0 4px' }}>
                        ⚠ {prereqsEval.warnings.join(' | ')}
                      </div>
                    )}

                    <div style={{ fontSize: '12px', color: '#8b949e', lineHeight: '1.4' }}>
                      {cleanText(feat.aciklama)}
                    </div>
                  </div>

                  <div style={{ flexShrink: 0, display: 'flex', alignItems: 'center' }}>
                    {selected ? (
                      <span style={{
                        fontSize: '11px', color: '#f39c12', fontWeight: 'bold',
                        padding: '6px 12px', borderRadius: '20px',
                        background: 'rgba(243,156,18,0.2)', border: '1px solid rgba(243,156,18,0.4)'
                      }}>
                        ✓ Seçildi
                      </span>
                    ) : (
                      <button
                        onClick={() => handleSelectFeature(feat)}
                        className="gold-btn primary"
                        style={{ padding: '6px 14px', fontSize: '12px' }}
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

        {/* Override Modal Overlay */}
        {overrideModalTarget && (
          <div style={{
            position: 'absolute', inset: 0, background: 'rgba(10,8,20,0.92)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            padding: '24px', zIndex: 10, textAlign: 'center'
          }}>
            <AlertTriangle size={42} style={{ color: '#f39c12', marginBottom: '12px' }} />
            <h4 style={{ color: '#f0e6d2', margin: '0 0 8px 0', fontSize: '1.1rem' }}>
              Şartlar Sağlanamadı: {overrideModalTarget.feature.isim || overrideModalTarget.feature.name}
            </h4>
            <div style={{ color: '#fca5a5', fontSize: '0.85rem', marginBottom: '16px', maxWidth: '480px' }}>
              {overrideModalTarget.warnings.join(', ')}
            </div>
            <p style={{ color: '#8b949e', fontSize: '0.8rem', marginBottom: '20px' }}>
              Game Master izni ile ön koşulları görmezden gelerek bu yeteneği eklemek istiyor musunuz?
            </p>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button className="gold-btn primary" onClick={handleConfirmOverride} style={{ padding: '8px 16px' }}>
                Evet, GM İzniyle Ekle
              </button>
              <button className="gold-btn" onClick={() => setOverrideModalTarget(null)} style={{ padding: '8px 16px' }}>
                Vazgeç
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
}
