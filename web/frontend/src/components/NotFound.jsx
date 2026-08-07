import React from 'react';
import { Compass, Home } from 'lucide-react';

export default function NotFound({ onGoHome }) {
  return (
    <div style={{
      minHeight: '70vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 20px',
      textAlign: 'center',
      color: 'var(--text-light, #e0e0e0)'
    }}>
      <div style={{
        width: 80,
        height: 80,
        borderRadius: '50%',
        background: 'rgba(201,168,76,0.1)',
        border: '1px solid var(--border-gold, #c9a84c)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 24
      }}>
        <Compass size={40} color="var(--gold-bright, #ffd700)" />
      </div>

      <h1 style={{
        fontFamily: 'Cinzel Decorative, Cinzel, serif',
        fontSize: '2.5rem',
        margin: '0 0 12px 0',
        color: 'var(--gold-bright, #ffd700)',
        letterSpacing: '0.05em'
      }}>
        404 — Diyar Bulunamadı
      </h1>

      <p style={{
        fontFamily: 'Outfit, sans-serif',
        fontSize: '1.1rem',
        maxWidth: 500,
        margin: '0 0 32px 0',
        color: 'var(--text-muted, #94a3b8)',
        lineHeight: 1.6
      }}>
        Aradığınız yol veya mekan sisler arasında kaybolmuş. Pathfinder rehberiniz sizi ana karargaha geri çağırmaktadır.
      </p>

      <button
        onClick={onGoHome}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          padding: '12px 24px',
          background: 'linear-gradient(135deg, rgba(201,168,76,0.2) 0%, rgba(201,168,76,0.05) 100%)',
          border: '1px solid var(--border-gold, #c9a84c)',
          borderRadius: 6,
          color: 'var(--gold-bright, #ffd700)',
          fontFamily: 'Cinzel, serif',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}
      >
        <Home size={18} /> Ana Sayfaya Dön
      </button>
    </div>
  );
}
