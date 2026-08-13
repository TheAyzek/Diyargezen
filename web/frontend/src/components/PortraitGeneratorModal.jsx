import React, { useState, useEffect, useRef } from 'react';
import { X, Sparkles, Wand2, Image as ImageIcon, Check, RefreshCw, Sliders, Download, Layers } from 'lucide-react';
import { useCharacterStore } from '../store/characterStore';

const ART_STYLES = [
  { id: 'oil_painting', name: 'Epic High-Fantasy Oil Painting', promptSuffix: 'epic fantasy oil painting, d20 book cover art, highly detailed, dramatic lighting, 8k resolution' },
  { id: 'dark_fantasy', name: 'Dark Fantasy Realism', promptSuffix: 'dark fantasy, realistic texture, cinematic lighting, gritty detail, masterpiece' },
  { id: 'anime_fantasy', name: 'Anime / JRPG Fantasy', promptSuffix: 'vibrant anime fantasy illustration, JRPG character art, clean lines, beautiful lighting' },
  { id: 'parchment_sketch', name: 'Parchment Sketch', promptSuffix: 'vintage parchment paper sketch, ink and watercolor illustration, hand-drawn fantasy art' }
];

export const PRESET_AVATARS = [
  {
    id: 'f_fighter',
    name: 'Valeros (Human Fighter)',
    class: 'Fighter',
    race: 'Human',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#1e1b2e"/><circle cx="50" cy="38" r="20" fill="#d8b48f"/><path d="M 30 75 Q 50 55 70 75 Q 50 95 30 75 Z" fill="#64748b"/><polygon points="40,25 50,15 60,25" fill="#ffd700"/><path d="M 20 85 L 80 85 L 75 100 L 25 100 Z" fill="#334155"/><circle cx="43" cy="36" r="3" fill="#1e293b"/><circle cx="57" cy="36" r="3" fill="#1e293b"/><path d="M 45 45 Q 50 48 55 45" stroke="#9a3412" stroke-width="2" fill="none"/></svg>`
  },
  {
    id: 'f_wizard',
    name: 'Ezren (Human Wizard)',
    class: 'Wizard',
    race: 'Human',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#0f172a"/><circle cx="50" cy="40" r="18" fill="#f5d0a9"/><path d="M 25 90 C 25 60 75 60 75 90 Z" fill="#3b82f6"/><path d="M 30 30 C 30 10 70 10 70 30 Z" fill="#1d4ed8"/><circle cx="44" cy="38" r="2.5" fill="#0f172a"/><circle cx="56" cy="38" r="2.5" fill="#0f172a"/><path d="M 46 48 Q 50 52 54 48" stroke="#9a3412" stroke-width="2" fill="none"/><path d="M 35 48 C 35 68 65 68 65 48 Z" fill="#e2e8f0"/></svg>`
  },
  {
    id: 'f_cleric',
    name: 'Kyra (Human Cleric)',
    class: 'Cleric',
    race: 'Human',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#2d1b00"/><circle cx="50" cy="38" r="19" fill="#e0b894"/><path d="M 20 90 C 20 58 80 58 80 90 Z" fill="#ca8a04"/><circle cx="50" cy="20" r="8" fill="#facc15"/><circle cx="43" cy="36" r="2.5" fill="#1e293b"/><circle cx="57" cy="36" r="2.5" fill="#1e293b"/><path d="M 45 46 Q 50 49 55 46" stroke="#9a3412" stroke-width="2" fill="none"/></svg>`
  },
  {
    id: 'f_rogue',
    name: 'Merisiel (Elf Rogue)',
    class: 'Rogue',
    race: 'Elf',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#064e3b"/><path d="M 30 35 L 20 15 L 40 30 Z" fill="#d97706"/><path d="M 70 35 L 80 15 L 60 30 Z" fill="#d97706"/><circle cx="50" cy="40" r="17" fill="#fef08a"/><path d="M 22 90 C 22 60 78 60 78 90 Z" fill="#047857"/><circle cx="43" cy="38" r="3" fill="#065f46"/><circle cx="57" cy="38" r="3" fill="#065f46"/><path d="M 45 46 Q 50 50 55 46" stroke="#047857" stroke-width="2" fill="none"/></svg>`
  },
  {
    id: 'f_paladin',
    name: 'Seelah (Human Paladin)',
    class: 'Paladin',
    race: 'Human',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#1e293b"/><circle cx="50" cy="38" r="19" fill="#c0a080"/><path d="M 20 90 Q 50 50 80 90 Z" fill="#94a3b8"/><path d="M 40 15 L 60 15 L 50 35 Z" fill="#fbbf24"/><circle cx="43" cy="36" r="2.5" fill="#0f172a"/><circle cx="57" cy="36" r="2.5" fill="#0f172a"/><path d="M 45 46 Q 50 49 55 46" stroke="#78350f" stroke-width="2" fill="none"/></svg>`
  },
  {
    id: 'f_barbarian',
    name: 'Amiri (Human Barbarian)',
    class: 'Barbarian',
    race: 'Human',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#450a0a"/><circle cx="50" cy="38" r="20" fill="#d97706"/><path d="M 20 90 L 80 90 L 70 65 L 30 65 Z" fill="#991b1b"/><path d="M 25 25 L 35 35 L 20 40 Z" fill="#b91c1c"/><circle cx="43" cy="36" r="3" fill="#450a0a"/><circle cx="57" cy="36" r="3" fill="#450a0a"/><path d="M 42 46 L 58 46" stroke="#450a0a" stroke-width="3" fill="none"/></svg>`
  },
  {
    id: 'f_ranger',
    name: 'Harsk (Dwarf Ranger)',
    class: 'Ranger',
    race: 'Dwarf',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#14532d"/><circle cx="50" cy="42" r="22" fill="#eab308"/><path d="M 20 90 Q 50 65 80 90 Z" fill="#166534"/><path d="M 30 50 Q 50 75 70 50 Z" fill="#b45309"/><circle cx="43" cy="38" r="3" fill="#14532d"/><circle cx="57" cy="38" r="3" fill="#14532d"/><path d="M 45 44 L 55 44" stroke="#78350f" stroke-width="2" fill="none"/></svg>`
  },
  {
    id: 'f_druid',
    name: 'Lini (Gnome Druid)',
    class: 'Druid',
    race: 'Gnome',
    svg: `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#15803d"/><circle cx="50" cy="40" r="16" fill="#fef08a"/><path d="M 25 90 C 25 65 75 65 75 90 Z" fill="#16a34a"/><circle cx="50" cy="22" r="14" fill="#a855f7"/><circle cx="44" cy="38" r="2.5" fill="#15803d"/><circle cx="56" cy="38" r="2.5" fill="#15803d"/><path d="M 45 46 Q 50 49 55 46" stroke="#15803d" stroke-width="2" fill="none"/></svg>`
  }
];

export function generatePollinationsImageUrl(prompt, seed = 42) {
  const cleanPrompt = (prompt || 'heroic fantasy character portrait')
    .replace(/[^a-zA-Z0-9, ]/g, '')
    .trim();
  const encoded = encodeURIComponent(cleanPrompt);
  return `https://image.pollinations.ai/prompt/${encoded}?width=512&height=512&seed=${seed}&nologo=true`;
}

export default function PortraitGeneratorModal({ isOpen, onClose }) {
  const store = useCharacterStore();
  const { race, class: charClass, gender, hair, eyes, updateField } = store;

  const [activeTab, setActiveTab] = useState('gallery'); // 'gallery', 'ai', 'filters'
  const [selectedStyle, setSelectedStyle] = useState(ART_STYLES[0].id);
  const [customPrompt, setCustomPrompt] = useState('');
  const [selectedAvatarSvg, setSelectedAvatarSvg] = useState(PRESET_AVATARS[0].svg);
  const [aiImageUrl, setAiImageUrl] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [aiError, setAiError] = useState('');
  const [seed, setSeed] = useState(Math.floor(Math.random() * 10000));

  // Filters
  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const [sepia, setSepia] = useState(0);
  const [grayscale, setGrayscale] = useState(0);

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

  const handleGenerateFreeAi = () => {
    setIsGenerating(true);
    setAiError('');
    const newSeed = Math.floor(Math.random() * 10000);
    setSeed(newSeed);
    const url = generatePollinationsImageUrl(customPrompt, newSeed);
    
    // Preload image
    const img = new Image();
    img.src = url;
    img.onload = () => {
      setAiImageUrl(url);
      setIsGenerating(false);
    };
    img.onerror = () => {
      setAiImageUrl(url);
      setIsGenerating(false);
    };
  };

  const handleApplyPreset = (svgStr) => {
    const svgBlob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' });
    const reader = new FileReader();
    reader.onload = () => {
      updateField('portrait', reader.result);
      onClose();
    };
    reader.readAsDataURL(svgBlob);
  };

  const handleApplyAiImage = () => {
    if (aiImageUrl) {
      updateField('portrait', aiImageUrl);
      onClose();
    }
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(7, 6, 15, 0.96)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: '20px'
    }}>
      <div style={{
        backgroundColor: '#12101f', border: '1px solid var(--border-gold)', borderRadius: '14px',
        width: '100%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto',
        boxShadow: '0 20px 50px rgba(0,0,0,0.85)', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px'
      }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(201,168,76,0.2)', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(201,168,76,0.15)', border: '1px solid var(--gold-bright)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Wand2 size={18} color="var(--gold-bright)" />
            </div>
            <div>
              <h3 style={{ margin: 0, fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', fontSize: '1.2rem' }}>
                High-Fantasy Portre Stüdyosu (%100 Ücretsiz)
              </h3>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Galeri avatarları, sıfır maliyetli canlı AI görsel üretimi ve filtreler
              </div>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div style={{ display: 'flex', gap: '8px', background: 'rgba(10,8,20,0.6)', padding: '4px', borderRadius: '8px', border: '1px solid rgba(201,168,76,0.2)' }}>
          <button
            onClick={() => setActiveTab('gallery')}
            style={{
              flex: 1, padding: '8px', borderRadius: '6px', fontSize: '0.8rem', fontFamily: 'Cinzel, serif', fontWeight: 'bold', cursor: 'pointer',
              background: activeTab === 'gallery' ? 'rgba(201,168,76,0.25)' : 'transparent',
              color: activeTab === 'gallery' ? 'var(--gold-bright)' : '#94a3b8',
              border: activeTab === 'gallery' ? '1px solid var(--gold-bright)' : 'none'
            }}
          >
            🖼️ Galeri Avatarları (Hazır)
          </button>
          <button
            onClick={() => setActiveTab('ai')}
            style={{
              flex: 1, padding: '8px', borderRadius: '6px', fontSize: '0.8rem', fontFamily: 'Cinzel, serif', fontWeight: 'bold', cursor: 'pointer',
              background: activeTab === 'ai' ? 'rgba(124,110,247,0.25)' : 'transparent',
              color: activeTab === 'ai' ? '#c4beff' : '#94a3b8',
              border: activeTab === 'ai' ? '1px solid #7c6ef7' : 'none'
            }}
          >
            🎨 Ücretsiz AI Üret (Pollinations)
          </button>
        </div>

        {/* Tab 1: Gallery */}
        {activeTab === 'gallery' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--gold-pale)' }}>
              Pathfinder 1e standartlarına uygun yüksek kaliteli High-Fantasy karakter avatarları:
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '12px' }}>
              {PRESET_AVATARS.map(av => (
                <div
                  key={av.id}
                  onClick={() => {
                    setSelectedAvatarSvg(av.svg);
                    handleApplyPreset(av.svg);
                  }}
                  style={{
                    backgroundColor: '#1a1829', border: '1px solid rgba(201,168,76,0.25)', borderRadius: '8px',
                    padding: '10px', textAlign: 'center', cursor: 'pointer', transition: 'all 0.2s ease',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.4)'
                  }}
                  className="hover:border-gold"
                >
                  <div
                    style={{ width: '80px', height: '80px', margin: '0 auto 8px', borderRadius: '50%', overflow: 'hidden', border: '1px solid var(--gold-bright)' }}
                    dangerouslySetInnerHTML={{ __html: av.svg }}
                  />
                  <div style={{ fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--gold-bright)' }}>{av.name}</div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{av.race} · {av.class}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 2: Free AI Generator */}
        {activeTab === 'ai' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ fontSize: '0.78rem', color: '#c4beff', background: 'rgba(124,110,247,0.1)', padding: '10px', borderRadius: '6px', border: '1px solid rgba(124,110,247,0.3)' }}>
              ⚡ <b>%100 Ücretsiz & Sınırsız:</b> Pollinations.ai entegrasyonu ile hiçbir API anahtarı veya ödeme yapmadan anında benzersiz portre üretebilirsiniz.
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-pale)', marginBottom: '4px' }}>
                SANAT STİLİ SEÇİMİ
              </label>
              <select
                className="rune-input"
                value={selectedStyle}
                onChange={(e) => setSelectedStyle(e.target.value)}
                style={{ width: '100%', padding: '8px 12px' }}
              >
                {ART_STYLES.map(st => (
                  <option key={st.id} value={st.id}>{st.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-pale)', marginBottom: '4px' }}>
                AI PROMPT (OTOMATİK OLUŞTURULDU)
              </label>
              <textarea
                className="rune-input"
                rows={3}
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                style={{ width: '100%', padding: '8px 12px', resize: 'vertical' }}
              />
            </div>

            <button
              className="gold-btn primary"
              onClick={handleGenerateFreeAi}
              disabled={isGenerating}
              style={{ padding: '10px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            >
              {isGenerating ? (
                <>
                  <RefreshCw size={16} className="animate-spin" /> Portre İşleniyor (İnference)...
                </>
              ) : (
                <>
                  <Sparkles size={16} /> 🎨 Ücretsiz AI Portre Üret
                </>
              )}
            </button>

            {aiImageUrl && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px', marginTop: '10px' }}>
                <div style={{ width: '180px', height: '180px', borderRadius: '12px', overflow: 'hidden', border: '2px solid var(--gold-bright)', boxShadow: '0 0 20px rgba(201,168,76,0.4)' }}>
                  <img src={aiImageUrl} alt="Üretilen Portre" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                </div>
                <button
                  className="gold-btn"
                  onClick={handleApplyAiImage}
                  style={{ padding: '8px 20px', fontSize: '0.82rem', fontWeight: 'bold' }}
                >
                  <Check size={16} /> Karakter Kağıdına Uygula
                </button>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
