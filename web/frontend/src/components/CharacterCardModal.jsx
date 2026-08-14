import React, { useRef, useState } from 'react';
import { X, Download, Share2, Sparkles, Shield, Heart, Sword, Zap, Check } from 'lucide-react';

export default function CharacterCardModal({ character, recalcedData, onClose }) {
  const cardRef = useRef(null);
  const [downloading, setDownloading] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!character && !recalcedData) return null;

  const name = character?.name || 'İsimsiz Kahraman';
  const race = character?.race || 'İnsan';
  const charClass = character?.class || 'Savaşçı';
  const archetype = character?.archetype || '';
  const level = character?.level || 1;
  const alignment = character?.alignment || 'TN';
  const deity = character?.deity || 'Yok';
  const portrait = character?.portrait || '';

  const scores = recalcedData?.ability_scores || character?.abilities || {};
  const mods = recalcedData?.ability_modifiers || {};

  const abilities = [
    { key: 'STR', full: 'Strength', val: scores.Strength || 10, mod: mods.Strength ?? 0 },
    { key: 'DEX', full: 'Dexterity', val: scores.Dexterity || 10, mod: mods.Dexterity ?? 0 },
    { key: 'CON', full: 'Constitution', val: scores.Constitution || 10, mod: mods.Constitution ?? 0 },
    { key: 'INT', full: 'Intelligence', val: scores.Intelligence || 10, mod: mods.Intelligence ?? 0 },
    { key: 'WIS', full: 'Wisdom', val: scores.Wisdom || 10, mod: mods.Wisdom ?? 0 },
    { key: 'CHA', full: 'Charisma', val: scores.Charisma || 10, mod: mods.Charisma ?? 0 },
  ];

  const hp = recalcedData?.hit_points || 10;
  const ac = recalcedData?.armor_class || 10;
  const touch = recalcedData?.touch_ac || 10;
  const flat = recalcedData?.flat_footed_ac || 10;
  const init = recalcedData?.initiative ?? 0;
  const speed = recalcedData?.speed || 30;
  const bab = recalcedData?.bab ?? 0;
  const cmb = recalcedData?.cmb ?? 0;
  const cmd = recalcedData?.cmd ?? 10;

  const fort = recalcedData?.saving_throws?.Fortitude ?? 0;
  const ref = recalcedData?.saving_throws?.Reflex ?? 0;
  const will = recalcedData?.saving_throws?.Will ?? 0;

  const topWeapons = (recalcedData?.weapons || []).slice(0, 2);

  // Pure Client-side PNG Generation via Canvas Drawing
  const handleDownloadPNG = async () => {
    setDownloading(true);
    try {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const width = 600;
      const height = 820;
      canvas.width = width;
      canvas.height = height;

      // Background Gradient
      const grad = ctx.createLinearGradient(0, 0, width, height);
      grad.addColorStop(0, '#0f0e1a');
      grad.addColorStop(0.5, '#161426');
      grad.addColorStop(1, '#0a0914');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      // Gold Outer Border
      ctx.strokeStyle = '#d4af37';
      ctx.lineWidth = 4;
      ctx.strokeRect(12, 12, width - 24, height - 24);

      // Inner Accent Border
      ctx.strokeStyle = 'rgba(212, 175, 55, 0.3)';
      ctx.lineWidth = 1;
      ctx.strokeRect(18, 18, width - 36, height - 36);

      // Header Banner
      ctx.fillStyle = '#d4af37';
      ctx.font = 'bold 26px "Cinzel", "Times New Roman", serif';
      ctx.textAlign = 'center';
      ctx.fillText(name.toUpperCase(), width / 2, 58);

      ctx.fillStyle = '#a594ff';
      ctx.font = '14px "Inter", sans-serif';
      const subTitle = `${race} • ${charClass} ${archetype ? `(${archetype}) ` : ''}Seviye ${level} • ${alignment}`;
      ctx.fillText(subTitle, width / 2, 85);

      // Horizontal Divider
      ctx.strokeStyle = 'rgba(212, 175, 55, 0.4)';
      ctx.beginPath();
      ctx.moveTo(35, 100);
      ctx.lineTo(width - 35, 100);
      ctx.stroke();

      // Portrait or Crest
      const portraitBoxX = 35;
      const portraitBoxY = 115;
      const portraitSize = 130;

      ctx.fillStyle = '#141426';
      ctx.fillRect(portraitBoxX, portraitBoxY, portraitSize, portraitSize);
      ctx.strokeStyle = '#d4af37';
      ctx.lineWidth = 2;
      ctx.strokeRect(portraitBoxX, portraitBoxY, portraitSize, portraitSize);

      ctx.fillStyle = '#d4af37';
      ctx.font = '40px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('⚔️', portraitBoxX + portraitSize / 2, portraitBoxY + portraitSize / 2 + 15);

      // Combat Core Stats Next to Portrait
      const statStartX = 185;
      const statColW = 95;

      const combatItems = [
        { label: 'CAN (HP)', val: `${hp}`, color: '#ff6b81' },
        { label: 'ZIRH (AC)', val: `${ac}`, color: '#ffd700' },
        { label: 'TOUCH', val: `${touch}`, color: '#f0e6d2' },
        { label: 'FLAT-FOOT', val: `${flat}`, color: '#f0e6d2' },
        { label: 'INITIATIVE', val: `${init >= 0 ? '+' : ''}${init}`, color: '#38bdf8' },
        { label: 'HIZ (SPEED)', val: `${speed} ft`, color: '#4ec9b0' },
        { label: 'BAB', val: `+${bab}`, color: '#a594ff' },
        { label: 'CMB / CMD', val: `+${cmb}/${cmd}`, color: '#f0e6d2' },
      ];

      combatItems.forEach((it, idx) => {
        const col = idx % 4;
        const row = Math.floor(idx / 4);
        const boxX = statStartX + (col * statColW);
        const boxY = portraitBoxY + (row * 65);

        ctx.fillStyle = 'rgba(255, 255, 255, 0.04)';
        ctx.fillRect(boxX, boxY, statColW - 6, 58);
        ctx.strokeStyle = 'rgba(212, 175, 55, 0.2)';
        ctx.lineWidth = 1;
        ctx.strokeRect(boxX, boxY, statColW - 6, 58);

        ctx.fillStyle = '#8b949e';
        ctx.font = 'bold 9px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(it.label, boxX + (statColW - 6) / 2, boxY + 18);

        ctx.fillStyle = it.color;
        ctx.font = 'bold 18px "Cinzel", sans-serif';
        ctx.fillText(it.val, boxX + (statColW - 6) / 2, boxY + 44);
      });

      // Ability Scores Grid
      const abBoxY = 265;
      ctx.fillStyle = '#d4af37';
      ctx.font = 'bold 13px "Cinzel", serif';
      ctx.textAlign = 'left';
      ctx.fillText('YETENEK PUANLARI (ABILITY SCORES)', 35, abBoxY);

      abilities.forEach((ab, idx) => {
        const abW = (width - 70 - 25) / 6;
        const abX = 35 + (idx * (abW + 5));
        const abCardY = abBoxY + 12;

        ctx.fillStyle = '#121124';
        ctx.fillRect(abX, abCardY, abW, 70);
        ctx.strokeStyle = 'rgba(212, 175, 55, 0.3)';
        ctx.lineWidth = 1;
        ctx.strokeRect(abX, abCardY, abW, 70);

        ctx.fillStyle = '#a594ff';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(ab.key, abX + abW / 2, abCardY + 20);

        ctx.fillStyle = '#ffd700';
        ctx.font = 'bold 20px "Cinzel", serif';
        ctx.fillText(`${ab.val}`, abX + abW / 2, abCardY + 46);

        ctx.fillStyle = '#3fb950';
        ctx.font = 'bold 11px sans-serif';
        ctx.fillText(`(${ab.mod >= 0 ? '+' : ''}${ab.mod})`, abX + abW / 2, abCardY + 62);
      });

      // Saving Throws
      const saveY = 370;
      ctx.fillStyle = '#d4af37';
      ctx.font = 'bold 13px "Cinzel", serif';
      ctx.textAlign = 'left';
      ctx.fillText('KURTARMA ZARLARI (SAVING THROWS)', 35, saveY);

      const saveItems = [
        { label: 'FORTITUDE (CON)', val: `${fort >= 0 ? '+' : ''}${fort}`, color: '#ff6b81' },
        { label: 'REFLEX (DEX)', val: `${ref >= 0 ? '+' : ''}${ref}`, color: '#4ec9b0' },
        { label: 'WILL (WIS)', val: `${will >= 0 ? '+' : ''}${will}`, color: '#38bdf8' },
      ];

      saveItems.forEach((sv, idx) => {
        const svW = (width - 70 - 20) / 3;
        const svX = 35 + (idx * (svW + 10));
        const svCardY = saveY + 12;

        ctx.fillStyle = '#121124';
        ctx.fillRect(svX, svCardY, svW, 50);
        ctx.strokeStyle = 'rgba(212, 175, 55, 0.2)';
        ctx.strokeRect(svX, svCardY, svW, 50);

        ctx.fillStyle = '#8b949e';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(sv.label, svX + svW / 2, svCardY + 20);

        ctx.fillStyle = sv.color;
        ctx.font = 'bold 18px "Cinzel", serif';
        ctx.fillText(sv.val, svX + svW / 2, svCardY + 42);
      });

      // Weapons Section
      const wpnY = 460;
      ctx.fillStyle = '#d4af37';
      ctx.font = 'bold 13px "Cinzel", serif';
      ctx.textAlign = 'left';
      ctx.fillText('ÖNE ÇIKAN SİLAHLAR (WEAPONS)', 35, wpnY);

      if (topWeapons.length === 0) {
        ctx.fillStyle = '#8b949e';
        ctx.font = 'italic 12px sans-serif';
        ctx.fillText('Silah donanımı eklenmedi.', 35, wpnY + 30);
      } else {
        topWeapons.forEach((wpn, idx) => {
          const wBoxY = wpnY + 12 + (idx * 55);
          ctx.fillStyle = '#121124';
          ctx.fillRect(35, wBoxY, width - 70, 46);
          ctx.strokeStyle = 'rgba(212, 175, 55, 0.2)';
          ctx.strokeRect(35, wBoxY, width - 70, 46);

          ctx.fillStyle = '#f0e6d2';
          ctx.font = 'bold 13px sans-serif';
          ctx.textAlign = 'left';
          ctx.fillText(wpn.name || 'Silah', 48, wBoxY + 28);

          ctx.fillStyle = '#38bdf8';
          ctx.font = 'bold 12px sans-serif';
          ctx.textAlign = 'right';
          ctx.fillText(`Saldırı: ${wpn.calculated_attack || '+0'}  |  Hasar: ${wpn.calculated_damage || '1d8'}`, width - 48, wBoxY + 28);
        });
      }

      // Footer Watermark
      ctx.fillStyle = 'rgba(212, 175, 55, 0.6)';
      ctx.font = '11px "Cinzel", serif';
      ctx.textAlign = 'center';
      ctx.fillText('DİYARGEZEN • PATHFINDER 1E CHARACTER CREATOR', width / 2, height - 32);

      // Download
      const dataUrl = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = dataUrl;
      a.download = `${name.replace(/\s+/g, '_')}_vitrin_karti.png`;
      a.click();
    } catch (err) {
      console.error('PNG export failed:', err);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(5, 5, 10, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        background: '#0d0c18',
        border: '2px solid var(--accent-gold)',
        borderRadius: '12px',
        width: '100%',
        maxWidth: '680px',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 10px 40px rgba(0,0,0,0.8), 0 0 20px rgba(201,168,76,0.2)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Modal Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 20px',
          borderBottom: '1px solid rgba(201,168,76,0.3)',
          background: 'linear-gradient(90deg, rgba(201,168,76,0.15) 0%, transparent 100%)'
        }}>
          <h3 style={{ margin: 0, color: 'var(--accent-gold)', fontSize: '1.2rem', fontFamily: 'Cinzel, serif', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={18} /> Karakter Vitrin Kartı (Showcase Card)
          </h3>
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Card Canvas Visualizer Container */}
        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
          <div
            ref={cardRef}
            style={{
              width: '100%',
              maxWidth: '560px',
              background: 'linear-gradient(145deg, #141324 0%, #0a0914 100%)',
              border: '2px solid var(--accent-gold)',
              borderRadius: '10px',
              padding: '20px',
              boxShadow: '0 8px 30px rgba(0,0,0,0.6)',
              position: 'relative'
            }}
          >
            {/* Header */}
            <div style={{ textAlign: 'center', borderBottom: '1px solid rgba(201,168,76,0.3)', paddingBottom: '12px', marginBottom: '14px' }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: 'var(--accent-gold)', fontFamily: 'Cinzel, serif' }}>
                {name}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#a594ff', marginTop: '2px' }}>
                {race} • {charClass} {archetype ? `(${archetype}) ` : ''}Seviye {level} • {alignment}
              </div>
            </div>

            {/* Core Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', marginBottom: '14px' }}>
              <div style={{ background: '#121124', border: '1px solid rgba(233,69,96,0.3)', padding: '8px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '9px', color: '#8b949e', fontWeight: 'bold' }}>CAN (HP)</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ff6b81' }}>{hp}</div>
              </div>
              <div style={{ background: '#121124', border: '1px solid rgba(212,175,55,0.3)', padding: '8px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '9px', color: '#8b949e', fontWeight: 'bold' }}>ZIRH (AC)</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ffd700' }}>{ac}</div>
              </div>
              <div style={{ background: '#121124', border: '1px solid rgba(56,189,248,0.3)', padding: '8px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '9px', color: '#8b949e', fontWeight: 'bold' }}>INITIATIVE</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#38bdf8' }}>{init >= 0 ? `+${init}` : init}</div>
              </div>
              <div style={{ background: '#121124', border: '1px solid rgba(78,201,176,0.3)', padding: '8px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '9px', color: '#8b949e', fontWeight: 'bold' }}>HIZ</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#4ec9b0' }}>{speed} ft</div>
              </div>
            </div>

            {/* Abilities Matrix */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '6px', marginBottom: '14px' }}>
              {abilities.map(ab => (
                <div key={ab.key} style={{ background: '#0a0914', border: '1px solid rgba(201,168,76,0.2)', padding: '6px 2px', borderRadius: '6px', textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: '#a594ff', fontWeight: 'bold' }}>{ab.key}</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#ffd700' }}>{ab.val}</div>
                  <div style={{ fontSize: '10px', color: '#3fb950', fontWeight: 'bold' }}>({ab.mod >= 0 ? `+${ab.mod}` : ab.mod})</div>
                </div>
              ))}
            </div>

            {/* Saves */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginBottom: '14px' }}>
              <div style={{ background: '#121124', padding: '6px 10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '11px', color: '#8b949e' }}>Fortitude:</span>
                <span style={{ fontSize: '11px', fontWeight: 'bold', color: '#ff6b81' }}>{fort >= 0 ? `+${fort}` : fort}</span>
              </div>
              <div style={{ background: '#121124', padding: '6px 10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '11px', color: '#8b949e' }}>Reflex:</span>
                <span style={{ fontSize: '11px', fontWeight: 'bold', color: '#4ec9b0' }}>{ref >= 0 ? `+${ref}` : ref}</span>
              </div>
              <div style={{ background: '#121124', padding: '6px 10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '11px', color: '#8b949e' }}>Will:</span>
                <span style={{ fontSize: '11px', fontWeight: 'bold', color: '#38bdf8' }}>{will >= 0 ? `+${will}` : will}</span>
              </div>
            </div>

            {/* Footer Tag */}
            <div style={{ textAlign: 'center', fontSize: '10px', color: 'rgba(212,175,55,0.6)', fontFamily: 'Cinzel, serif', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '8px' }}>
              DİYARGEZEN • PATHFINDER 1E
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '12px', width: '100%', maxWidth: '560px' }}>
            <button
              onClick={handleDownloadPNG}
              disabled={downloading}
              style={{
                flex: 1,
                padding: '10px 16px',
                background: 'linear-gradient(135deg, #d4af37 0%, #aa8010 100%)',
                color: '#0f0f1a',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 'bold',
                fontSize: '13px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                cursor: downloading ? 'wait' : 'pointer',
                boxShadow: '0 4px 15px rgba(212,175,55,0.3)'
              }}
            >
              <Download size={16} />
              {downloading ? 'Görsel Üretiliyor...' : 'PNG Olarak İndir'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
