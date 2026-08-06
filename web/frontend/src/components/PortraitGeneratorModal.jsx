import React, { useState, useEffect } from 'react';
import { X, Sparkles, Wand2, Image as ImageIcon, Check, RefreshCw } from 'lucide-react';
import { useCharacterStore } from '../store/characterStore';

const ART_STYLES = [
  { id: 'oil_painting', name: 'Epic High-Fantasy Oil Painting', promptSuffix: 'epic fantasy oil painting, d20 book cover art, highly detailed, dramatic lighting, 8k resolution' },
  { id: 'dark_fantasy', name: 'Dark Fantasy Realism', promptSuffix: 'dark fantasy, realistic texture, cinematic lighting, gritty detail, masterpiece' },
  { id: 'anime_fantasy', name: 'Anime / JRPG Fantasy', promptSuffix: 'vibrant anime fantasy illustration, JRPG character art, clean lines, beautiful lighting' },
  { id: 'parchment_sketch', name: 'Parchment Sketch', promptSuffix: 'vintage parchment paper sketch, ink and watercolor illustration, hand-drawn fantasy art' }
];

const PRESET_AVATARS = [
  {
    id: 'f_fighter',
    name: 'Valeros Style Fighter',
    class: 'Fighter',
    race: 'Human',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#1e1b2e"/><circle cx="50" cy="38" r="20" fill="#d8b48f"/><path d="M 30 75 Q 50 55 70 75 Q 50 95 30 75 Z" fill="#64748b"/><polygon points="40,25 50,15 60,25" fill="#ffd700"/><path d="M 20 85 L 80 85 L 75 100 L 25 100 Z" fill="#334155"/><circle cx="43" cy="36" r="3" fill="#1e293b"/><circle cx="57" cy="36" r="3" fill="#1e293b"/><path d="M 45 45 Q 50 48 55 45" stroke="#9a3412" stroke-width="2" fill="none"/></svg>`
  },
  {
    id: 'f_wizard',
    name: 'Ezren Style Wizard',
    class: 'Wizard',
    race: 'Human',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#0f172a"/><circle cx="50" cy="40" r="18" fill="#f5d0a9"/><path d="M 25 90 C 25 60 75 60 75 90 Z" fill="#3b82f6"/><path d="M 30 30 C 30 10 70 10 70 30 Z" fill="#1d4ed8"/><circle cx="44" cy="38" r="2.5" fill="#0f172a"/><circle cx="56" cy="38" r="2.5" fill="#0f172a"/><path d="M 46 48 Q 50 52 54 48" stroke="#9a3412" stroke-width="2" fill="none"/><path d="M 35 48 C 35 68 65 68 65 48 Z" fill="#e2e8f0"/></svg>`
  },
  {
    id: 'f_cleric',
    name: 'Kyra Style Cleric',
    class: 'Cleric',
    race: 'Human',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#2d1b00"/><circle cx="50" cy="38" r="19" fill="#e0b894"/><path d="M 20 90 C 20 58 80 58 80 90 Z" fill="#ca8a04"/><circle cx="50" cy="20" r="8" fill="#facc15"/><circle cx="43" cy="36" r="2.5" fill="#1e293b"/><circle cx="57" cy="36" r="2.5" fill="#1e293b"/><path d="M 45 46 Q 50 49 55 46" stroke="#9a3412" stroke-width="2" fill="none"/></svg>`
  },
  {
    id: 'f_rogue',
    name: 'Merisiel Style Rogue',
    class: 'Rogue',
    race: 'Elf',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#064e3b"/><path d="M 30 35 L 20 15 L 40 30 Z" fill="#d97706"/><path d="M 70 35 L 80 15 L 60 30 Z" fill="#d97706"/><circle cx="50" cy="40" r="17" fill="#fef08a"/><path d="M 22 90 C 22 60 78 60 78 90 Z" fill="#047857"/><circle cx="43" cy="38" r="3" fill="#065f46"/><circle cx="57" cy="38" r="3" fill="#065f46"/><path d="M 45 46 Q 50 50 55 46" stroke="#047857" stroke-width="2" fill="none"/></svg>`
  }
];

export default function PortraitGeneratorModal({ isOpen, onClose }) {
  const store = useCharacterStore();
  const { race, class: charClass, gender, hair, eyes, updateField } = store;

  const [selectedStyle, setSelectedStyle] = useState(ART_STYLES[0].id);
  const [customPrompt, setCustomPrompt] = useState('');
  const [selectedAvatarSvg, setSelectedAvatarSvg] = useState(PRESET_AVATARS[0].svg);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    buildAutoPrompt();
  }, [race, charClass, gender, hair, eyes, selectedStyle]);

  const buildAutoPrompt = () => {
    const styleObj = ART_STYLES.find(s => s.id === selectedStyle) || ART_STYLES[0];
    const pGender = gender || 'heroic';
    const pRace = race || 'Human';
    const pClass = charClass || 'Adventurer';
    const pHair = hair ? `, ${hair} hair` : '';
    const pEyes = eyes ? `, ${eyes} eyes` : '';

    const generated = `A portrait of a ${pGender} ${pRace} ${pClass}${pHair}${pEyes}, wearing ornate adventurer gear, ${styleObj.promptSuffix}`;
    setCustomPrompt(generated);
  };

  if (!isOpen) return null;

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
    }, 600);
  };

  const handleApplyPortrait = () => {
    // Generate Data URI from SVG
    const svgBlob = new Blob([selectedAvatarSvg], { type: 'image/svg+xml;charset=utf-8' });
    const reader = new FileReader();
    reader.onload = () => {
      updateField('portrait', reader.result);
      onClose();
    };
    reader.readAsDataURL(svgBlob);
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(7, 6, 15, 0.96)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: '20px'
    }}>
      <div style={{
        backgroundColor: '#12101f', border: '1px solid var(--border-gold)', borderRadius: '14px',
        width: '100%', maxWidth: '750px', maxHeight: '90vh', overflowY: 'auto',
        boxShadow: '0 20px 50px rgba(0,0,0,0.85)', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px'
      }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(201,168,76,0.3)', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Wand2 size={22} color="var(--gold-bright)" />
            <h2 style={{ fontFamily: 'Cinzel Decorative, serif', fontSize: '1.2rem', color: 'var(--gold-bright)', margin: 0 }}>
              Yapay Zeka Karakter Portresi Üreteci
            </h2>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Style Selector */}
        <div>
          <label style={{ fontSize: '0.78rem', color: 'var(--gold-light)', fontWeight: 600, display: 'block', marginBottom: '6px', fontFamily: 'Cinzel, serif' }}>
            🎨 Sanat Stili Seçin (Art Style)
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '8px' }}>
            {ART_STYLES.map(style => (
              <button
                key={style.id}
                onClick={() => setSelectedStyle(style.id)}
                style={{
                  padding: '8px 10px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer',
                  backgroundColor: selectedStyle === style.id ? 'rgba(201,168,76,0.25)' : '#19162a',
                  border: `1px solid ${selectedStyle === style.id ? 'var(--border-gold)' : '#2a2540'}`,
                  color: selectedStyle === style.id ? 'var(--gold-bright)' : '#94a3b8',
                  textAlign: 'left'
                }}
              >
                {style.name}
              </button>
            ))}
          </div>
        </div>

        {/* Prompt Input Box */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
            <label style={{ fontSize: '0.78rem', color: 'var(--gold-light)', fontWeight: 600, fontFamily: 'Cinzel, serif' }}>
              ✨ Oluşturulan İstem (Character Prompt)
            </label>
            <button onClick={buildAutoPrompt} style={{ background: 'none', border: 'none', color: '#4ec9b0', fontSize: '0.7rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
              <RefreshCw size={11} /> İstemi Sıfırla
            </button>
          </div>
          <textarea
            className="rune-input"
            rows={3}
            value={customPrompt}
            onChange={e => setCustomPrompt(e.target.value)}
            style={{ width: '100%', fontSize: '0.82rem', lineHeight: '1.4', fontFamily: 'monospace' }}
          />
        </div>

        {/* Generated Preview & Presets Selection */}
        <div>
          <label style={{ fontSize: '0.78rem', color: 'var(--gold-light)', fontWeight: 600, display: 'block', marginBottom: '8px', fontFamily: 'Cinzel, serif' }}>
            🖼️ Görsel Önizleme & Avatar Şablonu Seçin
          </label>
          <div style={{ display: 'flex', gap: '14px', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0b0914', border: '1px solid #2a2540', borderRadius: '10px', padding: '16px' }}>
            {PRESET_AVATARS.map((avatar) => (
              <div
                key={avatar.id}
                onClick={() => setSelectedAvatarSvg(avatar.svg)}
                style={{
                  width: '80px', height: '80px', borderRadius: '10px', overflow: 'hidden', cursor: 'pointer',
                  border: selectedAvatarSvg === avatar.svg ? '2px solid var(--border-gold)' : '1px solid #334155',
                  boxShadow: selectedAvatarSvg === avatar.svg ? '0 0 12px rgba(201,168,76,0.5)' : 'none',
                  transition: 'all 0.2s ease', position: 'relative'
                }}
              >
                <div dangerouslySetInnerHTML={{ __html: avatar.svg }} style={{ width: '100%', height: '100%' }} />
                {selectedAvatarSvg === avatar.svg && (
                  <div style={{ position: 'absolute', top: 4, right: 4, backgroundColor: 'var(--gold-bright)', borderRadius: '50%', padding: 2 }}>
                    <Check size={12} color="#12101f" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            style={{
              padding: '8px 14px', backgroundColor: 'rgba(78, 201, 176, 0.15)', border: '1px solid #4ec9b0',
              borderRadius: '6px', color: '#4ec9b0', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '6px'
            }}
          >
            <Sparkles size={14} /> {isGenerating ? 'Üretiliyor...' : '🎨 İstem İle Yeniden Üret'}
          </button>

          <button
            onClick={handleApplyPortrait}
            style={{
              padding: '8px 16px', backgroundColor: 'linear-gradient(135deg, #c9a84c 0%, #ffd700 100%)',
              border: '1px solid var(--border-gold)', borderRadius: '6px', color: '#121218',
              fontSize: '0.82rem', fontWeight: 800, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px',
              fontFamily: 'Cinzel, serif'
            }}
          >
            <Check size={16} /> ✨ Bu Portreyi Karakterime Ata
          </button>
        </div>

      </div>
    </div>
  );
}
