import React, { useState, useEffect } from 'react';
import { Sliders, Plus, Minus, RotateCcw, Award, CheckCircle2, AlertCircle } from 'lucide-react';
import { useCharacterStore } from '../store/characterStore';

export const POINT_BUY_COSTS = {
  7: -4,
  8: -2,
  9: -1,
  10: 0,
  11: 1,
  12: 2,
  13: 3,
  14: 5,
  15: 7,
  16: 10,
  17: 13,
  18: 17
};

export const POINT_BUY_PRESETS = [
  { key: 'low', label: 'Low Fantasy', points: 10 },
  { key: 'standard', label: 'Standard Fantasy', points: 15 },
  { key: 'high', label: 'High Fantasy (Varsayılan)', points: 20 },
  { key: 'epic', label: 'Epic Fantasy', points: 25 },
  { key: 'custom', label: 'Özel Puan Havuzu', points: 20 }
];

export function getPointCost(score) {
  const s = Math.min(18, Math.max(7, parseInt(score) || 10));
  return POINT_BUY_COSTS[s] !== undefined ? POINT_BUY_COSTS[s] : 0;
}

export default function PointBuyStudio({ isOpen, onClose }) {
  const store = useCharacterStore();
  const { abilities, updateAbility, updateField, pointBuyBudget } = store;

  const [selectedPreset, setSelectedPreset] = useState('high');
  const [totalBudget, setTotalBudget] = useState(pointBuyBudget || 20);
  const [baseScores, setBaseScores] = useState({
    strength: abilities?.strength || 10,
    dexterity: abilities?.dexterity || 10,
    constitution: abilities?.constitution || 10,
    intelligence: abilities?.intelligence || 10,
    wisdom: abilities?.wisdom || 10,
    charisma: abilities?.charisma || 10
  });

  const coreKeys = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'];

  // Calculate total points spent
  const pointsSpent = coreKeys.reduce((sum, key) => {
    return sum + getPointCost(baseScores[key]);
  }, 0);

  const pointsRemaining = totalBudget - pointsSpent;

  const handlePresetChange = (presetKey) => {
    setSelectedPreset(presetKey);
    const pObj = POINT_BUY_PRESETS.find(p => p.key === presetKey);
    if (pObj && presetKey !== 'custom') {
      setTotalBudget(pObj.points);
      updateField('pointBuyBudget', pObj.points);
    }
  };

  const handleScoreChange = (key, delta) => {
    const current = baseScores[key] || 10;
    const next = Math.min(18, Math.max(7, current + delta));
    const nextCost = getPointCost(next);
    const currentCost = getPointCost(current);
    const costDiff = nextCost - currentCost;

    if (delta > 0 && pointsRemaining < costDiff) return;

    const newScores = { ...baseScores, [key]: next };
    setBaseScores(newScores);
    updateAbility(key, next);
  };

  const handleResetScores = () => {
    const reset = { strength: 10, dexterity: 10, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 };
    setBaseScores(reset);
    coreKeys.forEach(k => updateAbility(k, 10));
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      backgroundColor: 'rgba(7, 6, 15, 0.95)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem'
    }}>
      <div style={{
        backgroundColor: '#12101f', border: '1px solid var(--border-gold)', borderRadius: '14px',
        width: '100%', maxWidth: '750px', maxHeight: '90vh', overflowY: 'auto',
        boxShadow: '0 20px 50px rgba(0,0,0,0.85)', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px'
      }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(201,168,76,0.2)', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(201,168,76,0.15)', border: '1px solid var(--gold-bright)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Sliders size={18} color="var(--gold-bright)" />
            </div>
            <div>
              <h3 style={{ margin: 0, fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', fontSize: '1.2rem' }}>
                PF1e Point Buy & Stat Alım Stüdyosu
              </h3>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Pathfinder 1st Edition resmi puan satın alma standartı (CRB Table 1-1)
              </div>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem' }}>
            ✕
          </button>
        </div>

        {/* Budget Bar */}
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px',
          padding: '14px 18px', background: 'linear-gradient(135deg, rgba(201,168,76,0.12) 0%, rgba(10,8,20,0.9) 100%)',
          border: '1px solid rgba(201,168,76,0.3)', borderRadius: '8px'
        }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.72rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-pale)', marginBottom: '4px' }}>
              KAMPANYA BÜTÇESİ (FANTASY LEVEL)
            </label>
            <select
              className="rune-input"
              value={selectedPreset}
              onChange={(e) => handlePresetChange(e.target.value)}
              style={{ padding: '6px 10px', fontSize: '0.82rem' }}
            >
              {POINT_BUY_PRESETS.map(p => (
                <option key={p.key} value={p.key}>{p.label}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.65rem', color: 'var(--gold-pale)', textTransform: 'uppercase' }}>Harcanan Puan</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: pointsSpent > totalBudget ? '#ef4444' : 'var(--gold-bright)' }}>
                {pointsSpent}
              </div>
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.65rem', color: 'var(--gold-pale)', textTransform: 'uppercase' }}>Kalan Puan</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: pointsRemaining < 0 ? '#ef4444' : '#4ade80' }}>
                {pointsRemaining} / {totalBudget}
              </div>
            </div>

            <button
              onClick={handleResetScores}
              style={{
                padding: '6px 12px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)',
                borderRadius: '6px', color: '#fca5a5', fontSize: '0.75rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px'
              }}
            >
              <RotateCcw size={13} /> Sıfırla
            </button>
          </div>
        </div>

        {/* Ability Score Allocator Grid */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {coreKeys.map(key => {
            const baseVal = baseScores[key] || 10;
            const cost = getPointCost(baseVal);
            const keyCap = key.toUpperCase().slice(0, 3);

            const adjustedAbilities = recalcedData?.ability_scores || {};
            const keyTitle = key.charAt(0).toUpperCase() + key.slice(1);
            const finalVal = adjustedAbilities[keyTitle] || baseVal;
            const modVal = Math.floor((finalVal - 10) / 2);
            const modStr = modVal >= 0 ? `+${modVal}` : `${modVal}`;

            return (
              <div key={key} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px',
                background: 'rgba(15,12,28,0.7)', border: '1px solid rgba(201,168,76,0.2)', borderRadius: '8px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', width: '160px' }}>
                  <div style={{
                    width: '38px', height: '38px', borderRadius: '6px', background: 'rgba(201,168,76,0.15)',
                    border: '1px solid var(--border-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: 'Cinzel, serif', fontWeight: 'bold', color: 'var(--gold-bright)', fontSize: '0.85rem'
                  }}>
                    {keyCap}
                  </div>
                  <div>
                    <div style={{ fontSize: '0.88rem', fontWeight: 'bold', color: 'var(--gold-light)' }}>
                      {keyTitle}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      Maliyet: <b>{cost > 0 ? `+${cost}` : cost} Puan</b>
                    </div>
                  </div>
                </div>

                {/* Counter Control */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <button
                    onClick={() => handleScoreChange(key, -1)}
                    disabled={baseVal <= 7}
                    style={{
                      width: '32px', height: '32px', borderRadius: '6px', border: '1px solid rgba(201,168,76,0.3)',
                      background: baseVal <= 7 ? 'rgba(255,255,255,0.02)' : 'rgba(201,168,76,0.15)',
                      color: baseVal <= 7 ? '#64748b' : 'var(--gold-bright)', cursor: baseVal <= 7 ? 'not-allowed' : 'pointer',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold'
                    }}
                  >
                    <Minus size={14} />
                  </button>

                  <div style={{ width: '45px', textAlign: 'center' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ffffff' }}>
                      {baseVal}
                    </div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--gold-pale)' }}>Taban</div>
                  </div>

                  <button
                    onClick={() => handleScoreChange(key, 1)}
                    disabled={baseVal >= 18 || (pointsRemaining < (getPointCost(baseVal + 1) - cost))}
                    style={{
                      width: '32px', height: '32px', borderRadius: '6px', border: '1px solid rgba(201,168,76,0.3)',
                      background: baseVal >= 18 ? 'rgba(255,255,255,0.02)' : 'rgba(201,168,76,0.15)',
                      color: baseVal >= 18 ? '#64748b' : 'var(--gold-bright)', cursor: baseVal >= 18 ? 'not-allowed' : 'pointer',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold'
                    }}
                  >
                    <Plus size={14} />
                  </button>
                </div>

                {/* Final Score with Race Modifier */}
                <div style={{ textAlign: 'right', width: '120px' }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--gold-bright)' }}>
                    {finalVal} ({modStr})
                  </div>
                  <div style={{ fontSize: '0.68rem', color: '#94a3b8' }}>
                    Irk & Büyülü Eşyalı
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Action */}
        <button
          className="gold-btn primary"
          onClick={onClose}
          style={{ padding: '10px', fontSize: '0.88rem', fontWeight: 'bold', marginTop: '8px' }}
        >
          <CheckCircle2 size={16} /> Puan Satın Alımını Karakter Kağıdına Tamamla
        </button>

      </div>
    </div>
  );
}
