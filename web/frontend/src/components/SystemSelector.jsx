import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Sword, Sparkles, Activity, Lock, CheckCircle2, Shield, Zap, Scroll, ChevronRight, Dices } from 'lucide-react';

const DEFAULT_SYSTEMS = [
  {
    key: 'pf1e',
    name: 'Pathfinder 1st Edition',
    subtitle: 'Core Ruleset & Full Campaign Engine',
    dice_system: 'd20',
    description: 'Efsanevi Pathfinder 1st Edition kural motoru. 77 resmi ırk, 45 temel sınıf ve 23.000+ entite ile eksiksiz karakter oluşturucu.',
    is_active: true,
    badge: 'AKTİF & MÜKEMMEL DESTEK',
    features: [
      '🎲 D20 Sistem & Otomatik Stat Motoru',
      '⚔️ 77 Irk & 45 Sınıf Kataloğu',
      '📜 23.000+ Kural, Büyü & Eşya Veritabanı',
      '📄 Canlı PDF Karakter Kağıdı İhracı'
    ]
  },
  {
    key: 'dnd5e',
    name: 'D&D 5th Edition',
    subtitle: '5e SRD Ruleset Engine',
    dice_system: 'd20',
    description: 'Dungeons & Dragons 5th Edition SRD kuralları ve seviye ilerleme motoru.',
    is_active: false,
    badge: 'YAKINDA GELECEK',
    features: [
      '🎲 D20 Advantage / Disadvantage',
      '🛡️ 5e SRD Irk & Sınıf Seçeneği',
      '⏳ Alt Yapı Hazırlanıyor'
    ]
  },
  {
    key: 'mnm',
    name: 'Mutants & Masterminds 3e',
    subtitle: 'Point-Buy Superhero System',
    dice_system: 'd20',
    description: 'Mutants & Masterminds 3rd Edition puan bazlı süper kahraman oluşturma sistemi.',
    is_active: false,
    badge: 'YAKINDA GELECEK',
    features: [
      '⚡ Puan Bazlı (Point-Buy) Karakter Motoru',
      '🦸 Güç Tasarımı & Süper Kahraman Şablonları',
      '⏳ Alt Yapı Hazırlanıyor'
    ]
  }
];

export default function SystemSelector({ onSelect, onBack }) {
  const [systems, setSystems] = useState(DEFAULT_SYSTEMS);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get('/api/systems')
      .then(res => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          // Merge API data with rich frontend features metadata
          const merged = res.data.map(sys => {
            const match = DEFAULT_SYSTEMS.find(d => d.key === sys.key || d.key === sys.system_key);
            return {
              ...sys,
              subtitle: match?.subtitle || 'Game Engine',
              badge: sys.is_active !== false && (sys.key === 'pf1e' || sys.key === 'pathfinder1e') ? 'AKTİF & MÜKEMMEL DESTEK' : 'YAKINDA GELECEK',
              features: match?.features || [
                `🎲 ${sys.dice_system ? sys.dice_system.toUpperCase() : 'D20'} Motoru`,
                '📜 Kural Kataloğu'
              ]
            };
          });
          setSystems(merged);
        }
      })
      .catch(err => {
        console.warn('Backend systems endpoint fallback:', err);
      });
  }, []);

  const getSystemIcon = (key) => {
    const k = (key || '').toLowerCase();
    if (k.includes('pf1e') || k.includes('pathfinder')) {
      return (
        <div style={{
          width: 52,
          height: 52,
          borderRadius: 12,
          background: 'linear-gradient(135deg, rgba(201,168,76,0.25) 0%, rgba(201,168,76,0.05) 100%)',
          border: '1px solid rgba(201,168,76,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 15px rgba(201,168,76,0.2)'
        }}>
          <Activity className="w-7 h-7 text-amber-300" />
        </div>
      );
    }
    if (k.includes('dnd') || k.includes('5e')) {
      return (
        <div style={{
          width: 52,
          height: 52,
          borderRadius: 12,
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid rgba(255,255,255,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Sword className="w-7 h-7 text-slate-500" />
        </div>
      );
    }
    return (
      <div style={{
        width: 52,
        height: 52,
        borderRadius: 12,
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Sparkles className="w-7 h-7 text-slate-500" />
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center my-24">
        <div className="animate-fade-in text-xl text-amber-400 font-serif">Kural Sistemleri Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: '1100px',
      margin: '2rem auto',
      padding: '0 1.5rem',
      position: 'relative'
    }}>
      {/* Background Ambient Glow */}
      <div style={{
        position: 'absolute',
        top: '-40px',
        left: '50%',
        transform: 'translateX(-50%)',
        width: '600px',
        height: '300px',
        background: 'radial-gradient(circle, rgba(201, 168, 76, 0.12) 0%, rgba(0,0,0,0) 70%)',
        pointerEvents: 'none',
        zIndex: 0
      }} />

      {/* Hero Header */}
      <div style={{ textAlign: 'center', marginBottom: '2.5rem', position: 'relative', zIndex: 1 }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(201, 168, 76, 0.1)',
          border: '1px solid rgba(201, 168, 76, 0.3)',
          padding: '4px 14px',
          borderRadius: '20px',
          fontSize: '0.82rem',
          color: '#c9a84c',
          fontWeight: 'bold',
          marginBottom: '12px',
          letterSpacing: '0.5px'
        }}>
          <Dices size={15} /> OYUN MOTORU KATALOĞU
        </div>

        <h2 style={{
          fontFamily: 'Cinzel, Georgia, serif',
          fontSize: '2.5rem',
          fontWeight: 'bold',
          background: 'linear-gradient(180deg, #fff7d6 0%, #c9a84c 70%, #9e7f30 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '10px',
          letterSpacing: '1px',
          filter: 'drop-shadow(0 2px 8px rgba(201, 168, 76, 0.25))'
        }}>
          OYUN SİSTEMİ SEÇİN
        </h2>
        
        <p style={{ color: '#a0a0b8', fontSize: '1.05rem', maxWidth: '650px', margin: '0 auto', lineHeight: '1.5' }}>
          Diyargezen altyapısı şu anda <strong style={{ color: '#f0e6d2' }}>Pathfinder 1st Edition (PF1e)</strong> kurallarını tam performansla desteklemektedir.
        </p>
      </div>

      {/* Systems Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))',
        gap: '24px',
        marginBottom: '2.5rem',
        position: 'relative',
        zIndex: 1
      }}>
        {systems.map(sys => {
          const isActive = sys.is_active !== false && (sys.key === 'pf1e' || sys.key === 'pathfinder1e');

          return (
            <div
              key={sys.key}
              onClick={() => isActive && onSelect(sys.key)}
              style={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                borderRadius: '16px',
                padding: '24px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                cursor: isActive ? 'pointer' : 'not-allowed',
                background: isActive 
                  ? 'linear-gradient(160deg, rgba(28,24,18,0.92) 0%, rgba(15,17,25,0.95) 100%)' 
                  : 'rgba(20, 22, 32, 0.5)',
                border: isActive 
                  ? '1px solid rgba(201, 168, 76, 0.45)' 
                  : '1px solid rgba(255, 255, 255, 0.07)',
                boxShadow: isActive 
                  ? '0 12px 35px -5px rgba(0,0,0,0.6), 0 0 20px rgba(201, 168, 76, 0.15)' 
                  : 'none',
                opacity: isActive ? 1 : 0.65,
                backdropFilter: 'blur(10px)',
                transform: 'translateY(0)'
              }}
              onMouseOver={(e) => {
                if (isActive) {
                  e.currentTarget.style.transform = 'translateY(-6px)';
                  e.currentTarget.style.borderColor = 'rgba(201, 168, 76, 0.8)';
                  e.currentTarget.style.boxShadow = '0 18px 45px -5px rgba(0,0,0,0.7), 0 0 30px rgba(201, 168, 76, 0.25)';
                }
              }}
              onMouseOut={(e) => {
                if (isActive) {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderColor = 'rgba(201, 168, 76, 0.45)';
                  e.currentTarget.style.boxShadow = '0 12px 35px -5px rgba(0,0,0,0.6), 0 0 20px rgba(201, 168, 76, 0.15)';
                }
              }}
            >
              {/* Status Badge */}
              <div style={{ position: 'absolute', top: '20px', right: '20px' }}>
                {isActive ? (
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 'bold',
                    background: 'rgba(63, 185, 80, 0.15)',
                    color: '#3fb950',
                    border: '1px solid rgba(63, 185, 80, 0.35)',
                    padding: '4px 10px',
                    borderRadius: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    boxShadow: '0 0 10px rgba(63, 185, 80, 0.2)'
                  }}>
                    <CheckCircle2 size={13} /> {sys.badge}
                  </span>
                ) : (
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 'bold',
                    background: 'rgba(255, 255, 255, 0.05)',
                    color: '#8b949e',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    padding: '4px 10px',
                    borderRadius: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px'
                  }}>
                    <Lock size={13} /> YAKINDA GELECEK
                  </span>
                )}
              </div>

              {/* Main Content */}
              <div>
                <div style={{ marginBottom: '16px' }}>
                  {getSystemIcon(sys.key)}
                </div>

                <h3 style={{
                  fontFamily: 'Cinzel, Georgia, serif',
                  fontSize: '1.4rem',
                  fontWeight: 'bold',
                  color: isActive ? '#f0e6d2' : '#768390',
                  marginBottom: '4px'
                }}>
                  {sys.name}
                </h3>

                <div style={{
                  fontSize: '0.75rem',
                  color: isActive ? '#c9a84c' : '#54606e',
                  fontWeight: 'bold',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  marginBottom: '14px'
                }}>
                  {sys.subtitle || 'Game Engine'}
                </div>

                <p style={{
                  fontSize: '0.85rem',
                  color: isActive ? '#c4b59d' : '#6e7681',
                  lineHeight: '1.55',
                  marginBottom: '18px'
                }}>
                  {sys.description}
                </p>

                {/* Features List */}
                <div style={{
                  background: isActive ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.15)',
                  border: isActive ? '1px solid rgba(201, 168, 76, 0.15)' : '1px solid rgba(255,255,255,0.04)',
                  borderRadius: '10px',
                  padding: '12px 14px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  marginBottom: '20px'
                }}>
                  {(sys.features || []).map((feat, idx) => (
                    <div key={idx} style={{
                      fontSize: '0.78rem',
                      color: isActive ? '#e6edf3' : '#6e7681',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}>
                      {feat}
                    </div>
                  ))}
                </div>
              </div>

              {/* Card Footer Button */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                paddingTop: '14px',
                borderTop: isActive ? '1px solid rgba(201, 168, 76, 0.18)' : '1px solid rgba(255,255,255,0.05)'
              }}>
                <span style={{
                  fontSize: '0.75rem',
                  fontFamily: 'monospace',
                  background: 'rgba(0,0,0,0.4)',
                  color: isActive ? '#c9a84c' : '#6e7681',
                  padding: '3px 8px',
                  borderRadius: '4px',
                  border: isActive ? '1px solid rgba(201,168,76,0.25)' : '1px solid rgba(255,255,255,0.05)'
                }}>
                  ZAR: {sys.dice_system ? sys.dice_system.toUpperCase() : 'D20'}
                </span>

                {isActive ? (
                  <button style={{
                    background: 'linear-gradient(135deg, #c9a84c 0%, #9e7f30 100%)',
                    color: '#0d1117',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '6px 14px',
                    fontSize: '0.82rem',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    cursor: 'pointer',
                    boxShadow: '0 4px 12px rgba(201,168,76,0.3)',
                    transition: 'all 0.2s ease'
                  }}>
                    Sistemi Başlat <ChevronRight size={15} />
                  </button>
                ) : (
                  <span style={{ fontSize: '0.78rem', color: '#6e7681', fontStyle: 'italic' }}>
                    Kilitli
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Cancel Button */}
      <div style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
        <button
          onClick={onBack}
          style={{
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            color: '#c9d1d9',
            padding: '8px 24px',
            borderRadius: '8px',
            fontSize: '0.9rem',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
            e.currentTarget.style.color = '#f0e6d2';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
            e.currentTarget.style.color = '#c9d1d9';
          }}
        >
          İptal Et / Geri Dön
        </button>
      </div>
    </div>
  );
}
