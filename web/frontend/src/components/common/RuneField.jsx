import React, { useMemo } from 'react';

const RUNE_CHARS = ['ᚠ','ᚢ','ᚦ','ᚨ','ᚱ','ᚲ','ᚷ','ᚹ','ᚺ','ᚾ','ᛁ','ᛃ','ᛇ','ᛈ','ᛉ','ᛊ','ᛏ','ᛒ','ᛖ','ᛗ','ᛚ','ᛜ','ᛞ','ᛟ'];

export default function RuneField() {
  const runes = useMemo(() => Array.from({ length: 28 }, (_, i) => ({
    id: i,
    char: RUNE_CHARS[i % RUNE_CHARS.length],
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: 14 + Math.random() * 22,
    delay: Math.random() * 5,
    duration: 6 + Math.random() * 8,
    tx: (Math.random() - 0.5) * 40,
    ty: -(30 + Math.random() * 50),
  })), []);

  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none', zIndex: 0 }}>
      {runes.map(r => (
        <div key={r.id} style={{
          position: 'absolute',
          left: `${r.x}%`,
          top: `${r.y}%`,
          fontSize: r.size,
          color: 'var(--gold)',
          opacity: 0,
          fontFamily: 'Cinzel, serif',
          animation: `particleDrift ${r.duration}s ${r.delay}s ease-in-out infinite`,
          '--tx': `${r.tx}px`,
          '--ty': `${r.ty}px`,
          willChange: 'transform, opacity',
        }}>
          {r.char}
        </div>
      ))}
    </div>
  );
}
