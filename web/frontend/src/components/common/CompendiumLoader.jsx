import React, { useState, useEffect } from 'react';
import { BookOpen, Sparkles, Server } from 'lucide-react';

const ATMOSPHERIC_QUOTES = [
  "Pathfinder 1st Edition SRD kural kadim arşivleri taranıyor...",
  "Büyü Grimoire sayfaları ve gizemli efsunlar sıralanıyor...",
  "Sınıf yetenekleri, hünerler ve dövüş manevraları hazırlanıyor...",
  "Maceracı teçhizatları ve simya eşyaları indeksleniyor...",
  "Diyargezen Kural Motoru bilgi kasasını doğruluyor..."
];

export default function CompendiumLoader({ activeCategory = 'Kural Kütüphanesi', coldStartMsg = '' }) {
  const [quoteIndex, setQuoteIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setQuoteIndex(prev => (prev + 1) % ATMOSPHERIC_QUOTES.length);
    }, 3500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Central High-Fantasy Animated Loader Banner */}
      <div 
        className="sheet-card"
        style={{
          padding: '40px 24px',
          textAlign: 'center',
          background: 'linear-gradient(135deg, rgba(16,14,28,0.95) 0%, rgba(8,6,16,0.98) 100%)',
          border: '1px solid var(--border-gold, #c9a84c)',
          borderRadius: '10px',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: '0 0 30px rgba(0,0,0,0.8), 0 0 15px rgba(201,168,76,0.15)'
        }}
      >
        {/* Ambient Top Glow Line */}
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: '2px',
          background: 'linear-gradient(90deg, transparent 0%, var(--gold-bright, #ffd700) 50%, transparent 100%)'
        }} />

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          
          {/* Animated Rune Circle Container */}
          <div style={{ position: 'relative', width: 90, height: 90, marginBottom: 20 }}>
            
            {/* Outer Spinning Rune Ring */}
            <div style={{
              position: 'absolute', inset: 0,
              borderRadius: '50%',
              border: '2px dashed rgba(201, 168, 76, 0.4)',
              borderTopColor: 'var(--gold-bright, #ffd700)',
              borderBottomColor: 'var(--gold-bright, #ffd700)',
              animation: 'rune-rotate 6s linear infinite'
            }} />

            {/* Inner Pulsing Orb */}
            <div style={{
              position: 'absolute', inset: 12,
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(201,168,76,0.25) 0%, rgba(20,16,35,0.8) 100%)',
              border: '1px solid rgba(201,168,76,0.5)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              animation: 'pulse-glow 2.5s infinite ease-in-out'
            }}>
              <BookOpen size={30} style={{ color: 'var(--gold-bright, #ffd700)', filter: 'drop-shadow(0 0 8px rgba(255,215,0,0.6))' }} />
            </div>

            {/* Sparkle Accent */}
            <Sparkles size={18} style={{
              position: 'absolute', top: 0, right: 0,
              color: 'var(--gold-bright, #ffd700)',
              animation: 'spin 4s linear infinite'
            }} />
          </div>

          {/* Heading */}
          <h3 style={{
            margin: '0 0 8px 0',
            fontFamily: 'Cinzel Decorative, Cinzel, serif',
            fontSize: '1.25rem',
            color: 'var(--gold-bright, #ffd700)',
            letterSpacing: '0.08em'
          }}>
            {activeCategory.toUpperCase()} YÜKLENİYOR...
          </h3>

          {/* Dynamic Fantasy Quote */}
          <p style={{
            margin: '0 0 14px 0',
            fontFamily: 'Outfit, sans-serif',
            fontSize: '0.9rem',
            color: 'var(--gold-light, #f7df94)',
            transition: 'opacity 0.5s ease',
            minHeight: '1.4em'
          }}>
            {ATMOSPHERIC_QUOTES[quoteIndex]}
          </p>

          {/* Cold Start Banner (Render.com free-tier wake up) */}
          {coldStartMsg && (
            <div style={{
              marginTop: 12,
              padding: '10px 16px',
              borderRadius: 6,
              background: 'rgba(201,168,76,0.12)',
              border: '1px solid rgba(201,168,76,0.35)',
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              maxWidth: 540
            }}>
              <Server size={18} color="#ffd700" className="animate-spin" />
              <span style={{ fontSize: '0.82rem', color: '#fff', fontFamily: 'Outfit, sans-serif', textAlign: 'left' }}>
                {coldStartMsg}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Skeleton Card Grid Shimmer */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
        gap: '16px'
      }}>
        {[1, 2, 3, 4, 5, 6].map(i => (
          <div
            key={i}
            className="sheet-card"
            style={{
              padding: '18px',
              border: '1px solid rgba(201,168,76,0.15)',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px'
            }}
          >
            {/* Title & Chevron Skeleton */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="skeleton-box" style={{ width: '60%', height: 20 }} />
              <div className="skeleton-box" style={{ width: 16, height: 16, borderRadius: '50%' }} />
            </div>

            {/* Badges Skeleton */}
            <div style={{ display: 'flex', gap: 6 }}>
              <div className="skeleton-box" style={{ width: 70, height: 16 }} />
              <div className="skeleton-box" style={{ width: 90, height: 16 }} />
            </div>

            {/* Text Paragraph Lines Skeleton */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 4 }}>
              <div className="skeleton-box" style={{ width: '100%', height: 12 }} />
              <div className="skeleton-box" style={{ width: '92%', height: 12 }} />
              <div className="skeleton-box" style={{ width: '75%', height: 12 }} />
            </div>

            {/* Footer Line Skeleton */}
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 8, borderTop: '1px dashed rgba(201,168,76,0.1)' }}>
              <div className="skeleton-box" style={{ width: 80, height: 12 }} />
              <div className="skeleton-box" style={{ width: 50, height: 12 }} />
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
