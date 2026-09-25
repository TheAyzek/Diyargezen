/**
 * Diyargezen Pathfinder 1st Edition Live PDF View & Form Synchronizer
 * 
 * Architecture & Performance Design:
 * ----------------------------------
 * This component handles real-time rendering of active Pathfinder 1e character sheets using `pdf-lib`.
 * It embeds an interactive `<iframe src={pdfDataUri}>` container alongside tabbed HTML displays
 * for parchment sheet summary and spellbook management.
 * 
 * Performance Loop:
 * 1. Debounced Re-render (300ms): Reacts to Zustand store mutations (attributes, equipment, skills, feats, traits)
 *    and throttles PDF generation to prevent main thread rendering bottlenecks.
 * 2. Embedded Font Stream: Embeds standard Helvetica typefaces for AcroForm field appearance generation.
 * 3. Reactive Data URI Streaming: Encodes filled PDF bytes into Base64 Data URI streams for instant `<iframe />` rendering.
 * 4. Image Canvas Embedding: Scales character portraits into PDF canvas coordinate space if portrait Data URI exists.
 */

import React, { useEffect, useState } from 'react';
import { FileText, RefreshCw, Download, Shield, Heart, Sword, Sparkles, Activity, Wand2, Scroll, Scale, Zap, Coins } from 'lucide-react';

import { useCharacterStore } from '../../../store/characterStore';
import SpellCard from '../../SpellCard';
import ParchmentSheetDisplay from './ParchmentSheetDisplay';
import CharacterDiffModal from '../../CharacterDiffModal';
import CharacterCardModal from '../../CharacterCardModal';
import ProgressionPlannerModal from '../../ProgressionPlannerModal';
import StatblockModal from '../../StatblockModal';
import PartyLootModal from '../../PartyLootModal';
import ConditionsBuffsPanel from './ConditionsBuffsPanel';

export default function PF1eLiveSheet() {
  const store = useCharacterStore();
  const { name, level, race, class: charClass, feat, recalcedData, portrait, raceData, skills } = store;
  const traits = store.traits || [];
  const feats = store.feats || (feat ? [{ isim: feat }] : []);
  
  const [pdfUrl, setPdfUrl] = useState(null);
  const [rendering, setRendering] = useState(false);
  const [viewMode, setViewMode] = useState('pdf'); // 'pdf', 'summary', 'spells'
  const [activeEqTab, setActiveEqTab] = useState('weapons');
  const [spellLevelFilter, setSpellLevelFilter] = useState('all');
  const [spellSchoolFilter, setSpellSchoolFilter] = useState('all');
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);
  const [showCardModal, setShowCardModal] = useState(false);
  const [showProgressionModal, setShowProgressionModal] = useState(false);
  const [showStatblockModal, setShowStatblockModal] = useState(false);
  const [showPartyLootModal, setShowPartyLootModal] = useState(false);
  const [pdfError, setPdfError] = useState('');
  const pdfSnapshot = JSON.stringify(Object.fromEntries(Object.entries(store).filter(
    ([key, value]) => typeof value !== 'function' && !['loading', 'warnings', 'syncStatus', 'isOnline', 'editorBaseline'].includes(key),
  )));
  useEffect(() => {
    if (viewMode !== 'pdf') return;
    let cancelled = false;
    const timer = setTimeout(async () => {
      setRendering(true);
      setPdfError('');
      try {
        const { generateCharacterPDFBlobUrl } = await import('../../../utils/pdfExportUtil.js');
        const url = await generateCharacterPDFBlobUrl(JSON.parse(pdfSnapshot));
        if (cancelled) URL.revokeObjectURL(url);
        else setPdfUrl(url);
      } catch (error) {
        if (!cancelled) setPdfError(error.message);
      } finally {
        if (!cancelled) setRendering(false);
      }
    }, 300);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [pdfSnapshot, viewMode]);
  useEffect(() => () => { if (pdfUrl) URL.revokeObjectURL(pdfUrl); }, [pdfUrl]);

  const handleDownloadPdf = () => {
    if (!pdfUrl) return;
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = `${name || 'Diyargezen_Karakter'}_PF1e_Sheet.pdf`;
    link.click();
  };

  return (
    <div className="glass-card" style={{ 
      borderColor: 'var(--accent-gold)', 
      background: 'rgba(15, 15, 26, 0.9)',
      boxShadow: '0 0 25px rgba(201, 168, 76, 0.15)',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      borderRadius: '12px',
      maxWidth: '100%',
      overflow: 'hidden'
    }}>
      
      {/* Header bar with controls and view mode toggles */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        borderBottom: '2px solid var(--accent-gold)', 
        paddingBottom: '14px',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {portrait && (
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '8px',
              border: '2px solid var(--accent-gold)',
              overflow: 'hidden',
              background: '#0f0f1a'
            }}>
              <img src={portrait} alt="Portrait" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            </div>
          )}
          <div>
            <h3 style={{ fontSize: '1.4rem', color: '#f0e6d2', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={20} style={{ color: 'var(--accent-gold)' }} />
              Canlı Karakter Kağıdı (PDF AcroForm)
              {rendering ? (
                <span style={{ fontSize: '11px', background: 'rgba(201,168,76,0.2)', color: 'var(--accent-gold)', padding: '2px 8px', borderRadius: '10px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <RefreshCw size={10} className="animate-spin" /> Güncelleniyor...
                </span>
              ) : (
                <span style={{ fontSize: '11px', background: 'rgba(63,185,80,0.15)', color: '#3fb950', border: '1px solid rgba(63,185,80,0.3)', padding: '2px 8px', borderRadius: '10px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  ● Canlı Senkronize
                </span>
              )}
            </h3>
            <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
              Reaktif `pdf-lib` Form Görselleştirici
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap', maxWidth: '100%' }}>
          <button 
            onClick={() => setViewMode('pdf')}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '6px',
              border: '1px solid var(--accent-gold)',
              background: viewMode === 'pdf' ? 'var(--accent-gold)' : 'transparent',
              color: viewMode === 'pdf' ? '#0f0f1a' : 'var(--accent-gold)',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            📄 Canlı PDF
          </button>
          <button 
            onClick={() => setViewMode('summary')}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '6px',
              border: '1px solid var(--accent-gold)',
              background: viewMode === 'summary' ? 'var(--accent-gold)' : 'transparent',
              color: viewMode === 'summary' ? '#0f0f1a' : 'var(--accent-gold)',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            📊 Midnight Obsidian
          </button>
          <button 
            onClick={() => setViewMode('parchment')}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '6px',
              border: '1px solid #d4c5a9',
              background: viewMode === 'parchment' ? '#d4c5a9' : 'transparent',
              color: viewMode === 'parchment' ? '#2a1f0e' : '#d4c5a9',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <Scroll size={13} /> 📜 Eskiz Parşömen
          </button>

          <button 
            onClick={() => setViewMode('spells')}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '6px',
              border: '1px solid #7c6ef7',
              background: viewMode === 'spells' ? '#7c6ef7' : 'transparent',
              color: viewMode === 'spells' ? '#ffffff' : '#a594ff',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <Wand2 size={13} /> Büyü Kitabı ({(store.spells || []).length})
          </button>
          <button 
            onClick={() => setViewMode('feats')}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '6px',
              border: '1px solid #c9a84c',
              background: viewMode === 'feats' ? '#c9a84c' : 'transparent',
              color: viewMode === 'feats' ? '#0f0f1a' : '#c9a84c',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <Sparkles size={13} /> Feat & Trait Kartları ({feats.length + traits.length})
          </button>
          <button 
            onClick={handleDownloadPdf}
            className="btn btn-secondary"
            style={{ padding: '6px 10px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}
            disabled={!pdfUrl}
            title="Doldurulmuş PDF'i İndir"
          >
            <Download size={14} /> İndir
          </button>
          <button 
            onClick={() => setIsDiffModalOpen(true)}
            className="btn btn-secondary"
            style={{ padding: '6px 10px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', border: '1px solid #7c6ef7', color: '#d8b4fe' }}
            title="Bu karakteri başka bir karakterle veya snapshot ile kıyasla"
          >
            <Scale size={14} /> Karşılaştır
          </button>
          <button 
            onClick={() => setShowCardModal(true)}
            className="btn btn-secondary"
            style={{ padding: '6px 10px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', border: '1px solid #d4af37', color: '#ffd700' }}
            title="Karakteri şık sosyal medya / vitrin kartı olarak görüntüle ve PNG indir"
          >
            <Sparkles size={14} /> 🎨 Vitrin Kartı
          </button>
          <button 
            onClick={() => setShowProgressionModal(true)}
            className="btn btn-secondary"
            style={{ padding: '6px 10px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', border: '1px solid #38bdf8', color: '#38bdf8' }}
            title="1'den 20'ye Seviye Atlama ve Kariyer Yol Haritasını Görüntüle"
          >
            <Zap size={14} /> 📊 1-20 Yol Haritası
          </button>
          <button 
            onClick={() => setShowStatblockModal(true)}
            className="btn btn-secondary"
            style={{ padding: '6px 10px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', border: '1px solid #4ec9b0', color: '#4ec9b0' }}
            title="Resmi Paizo Statblock ve JSON Yedeği Görüntüle / İndir"
          >
            <FileText size={14} /> 📜 Statblock & JSON
          </button>
          <button 
            onClick={() => setShowPartyLootModal(true)}
            className="btn btn-secondary"
            style={{ padding: '6px 10px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', border: '1px solid #ffd700', color: '#ffd700' }}
            title="Parti Hazine Kasası ve Ganimet Paylaştırıcı"
          >
            <Coins size={14} /> 💰 Parti Kasası
          </button>
        </div>
      </div>

      {/* Main View Area */}
      {viewMode === 'pdf' ? (
        <div style={{ width: '100%', height: '700px', borderRadius: '8px', overflow: 'hidden', background: '#1e1e2f', position: 'relative', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
          {rendering && (
            <div style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              background: 'rgba(15, 15, 26, 0.9)',
              border: '1px solid var(--accent-gold)',
              padding: '6px 12px',
              borderRadius: '20px',
              color: 'var(--accent-gold)',
              fontSize: '11px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              zIndex: 10
            }}>
              <RefreshCw size={12} className="animate-spin" /> PDF Güncelleniyor...
            </div>
          )}
          
          {pdfError && <p role="alert">PDF güncellenemedi: {pdfError}</p>}
          {pdfUrl ? (
            <iframe 
              src={pdfUrl} 
              title="PF1e Live AcroForm PDF Sheet" 
              style={{ width: '100%', height: '100%', border: 'none' }}
            />
          ) : (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#8b949e', fontSize: '14px' }}>
              <RefreshCw size={20} className="animate-spin" style={{ marginRight: '8px' }} /> PDF Şablonu Yükleniyor...
            </div>
          )}
        </div>
      ) : viewMode === 'parchment' ? (
        <ParchmentSheetDisplay />
      ) : viewMode === 'summary' ? (

        /* Summary view alternative with detailed mathematical stat breakdowns */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Character Identity & Archetypes Banner */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(201,168,76,0.12) 0%, rgba(15,15,26,0.85) 100%)',
            border: '1px solid rgba(201,168,76,0.3)',
            borderRadius: '8px',
            padding: '14px 18px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px'
          }}>
            <div>
              <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: 'var(--accent-gold)', fontFamily: 'Cinzel, serif' }}>
                {name || 'İsimsiz Kahraman'}
              </div>
              <div style={{ fontSize: '0.85rem', color: '#d4c5a9', marginTop: '2px', display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                <span>{race || 'Irk'}</span>
                <span>•</span>
                <span style={{ fontWeight: 'bold', color: '#f0e6d2' }}>
                  {charClass || 'Sınıf'} {archetype ? `(${archetype})` : ''} Seviye {level || 1}
                </span>
                {recalcedData?.multiclass && Object.keys(recalcedData.multiclass).length > 0 && (
                  <span style={{ fontSize: '0.75rem', background: 'rgba(56,189,248,0.15)', color: '#38bdf8', border: '1px solid rgba(56,189,248,0.3)', padding: '1px 6px', borderRadius: '4px' }}>
                    Multiclass: {Object.entries(recalcedData.multiclass).map(([c, l]) => `${c} ${l}`).join(' / ')}
                  </span>
                )}
                {recalcedData?.age_details && (
                  <span style={{
                    fontSize: '0.75rem',
                    background: `${recalcedData.age_details.badge_color}20`,
                    color: recalcedData.age_details.badge_color,
                    border: `1px solid ${recalcedData.age_details.badge_color}50`,
                    padding: '1px 6px',
                    borderRadius: '4px',
                    fontWeight: 'bold'
                  }}>
                    ⏳ Yaş: {recalcedData.age_details.age} ({recalcedData.age_details.category_name})
                  </span>
                )}
              </div>
            </div>

            {/* Archetype Features Badges */}
            {recalcedData?.archetype_details && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                {recalcedData.archetype_details.granted_features?.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', justifyContent: 'flex-end' }}>
                    {recalcedData.archetype_details.granted_features.map((g, idx) => (
                      <span key={idx} style={{ fontSize: '0.72rem', color: '#3fb950', background: 'rgba(63,185,80,0.12)', border: '1px solid rgba(63,185,80,0.3)', padding: '2px 6px', borderRadius: '4px' }}>
                        ✦ {g}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Favored Class Bonus (FCB) Summary & Allocation Banner */}
          {recalcedData?.favored_class_bonus && (
            <div style={{
              background: '#121124',
              border: '1px solid rgba(201,168,76,0.3)',
              borderRadius: '8px',
              padding: '12px 16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '10px'
            }}>
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 'bold', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  ⭐ Favored Class: <span style={{ color: '#f0e6d2' }}>{recalcedData.favored_class_bonus.favored_class}</span>
                  {recalcedData.favored_class_bonus.secondary_favored_class && (
                    <span style={{ color: '#38bdf8' }}> / {recalcedData.favored_class_bonus.secondary_favored_class}</span>
                  )}
                  <span style={{ fontSize: '11px', color: '#8b949e', marginLeft: '6px' }}>
                    ({recalcedData.favored_class_bonus.allocated_count} / {recalcedData.favored_class_bonus.total_eligible_levels} Seviye Tahsis Edildi)
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '8px', marginTop: '4px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '11px', background: 'rgba(233,69,96,0.15)', color: '#ff6b81', border: '1px solid rgba(233,69,96,0.3)', padding: '2px 8px', borderRadius: '4px' }}>
                    💖 +{recalcedData.favored_class_bonus.hp_bonus} Can Puanı (HP)
                  </span>
                  <span style={{ fontSize: '11px', background: 'rgba(56,189,248,0.15)', color: '#38bdf8', border: '1px solid rgba(56,189,248,0.3)', padding: '2px 8px', borderRadius: '4px' }}>
                    📚 +{recalcedData.favored_class_bonus.skill_bonus} Yetenek Puanı (Skill Rank)
                  </span>
                  {(recalcedData.favored_class_bonus.racial_bonuses || []).map((rb, rIdx) => (
                    <span key={rIdx} style={{ fontSize: '11px', background: 'rgba(124,110,247,0.15)', color: '#a594ff', border: '1px solid rgba(124,110,247,0.3)', padding: '2px 8px', borderRadius: '4px' }}>
                      ✦ {rb.name} ({rb.allocated_ranks} Seviye: +{rb.effective_value})
                    </span>
                  ))}
                </div>
              </div>

              {/* Quick FCB Bulk Allocation Buttons */}
              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  type="button"
                  onClick={() => store.autoAllocateFCB && store.autoAllocateFCB('hp')}
                  style={{
                    background: 'rgba(233,69,96,0.15)',
                    color: '#ff6b81',
                    border: '1px solid rgba(233,69,96,0.4)',
                    borderRadius: '4px',
                    padding: '4px 8px',
                    fontSize: '11px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                  title="Tüm seviye FCB puanlarını Can Puanına (HP) ver"
                >
                  💖 Tümünü HP'ye Ver
                </button>
                <button
                  type="button"
                  onClick={() => store.autoAllocateFCB && store.autoAllocateFCB('skill')}
                  style={{
                    background: 'rgba(56,189,248,0.15)',
                    color: '#38bdf8',
                    border: '1px solid rgba(56,189,248,0.4)',
                    borderRadius: '4px',
                    padding: '4px 8px',
                    fontSize: '11px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                  title="Tüm seviye FCB puanlarını Yetenek Puanına (Skill) ver"
                >
                  📚 Tümünü Skill'e Ver
                </button>
              </div>
            </div>
          )}

          {/* Languages & Linguistics Tracking Card */}
          {recalcedData?.languages_analysis && (
            <div style={{
              background: '#121124',
              border: '1px solid rgba(56,189,248,0.25)',
              borderRadius: '8px',
              padding: '12px 16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '10px'
            }}>
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 'bold', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  🗣️ Bilinen Diller (Languages):
                  <span style={{ fontSize: '11px', color: '#8b949e', marginLeft: '6px' }}>
                    ({recalcedData.languages_analysis.total_selected_languages} / {recalcedData.languages_analysis.total_allowed_languages} Dil • {recalcedData.languages_analysis.automatic_languages?.length || 1} Otomatik + {recalcedData.languages_analysis.bonus_slots || 0} INT + {recalcedData.languages_analysis.linguistics_slots || 0} Linguistics)
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '6px', marginTop: '6px', flexWrap: 'wrap' }}>
                  {(recalcedData.languages_analysis.selected_languages || []).map((lang, lIdx) => (
                    <span key={lIdx} style={{ fontSize: '11px', background: 'rgba(56,189,248,0.12)', color: '#38bdf8', border: '1px solid rgba(56,189,248,0.3)', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold' }}>
                      {lang}
                    </span>
                  ))}
                  {recalcedData.languages_analysis.unallocated_slots > 0 && (
                    <span style={{ fontSize: '11px', background: 'rgba(254,202,87,0.15)', color: '#feca57', border: '1px solid rgba(254,202,87,0.3)', padding: '2px 8px', borderRadius: '4px' }}>
                      + {recalcedData.languages_analysis.unallocated_slots} Seçilebilir Dil Hakkı
                    </span>
                  )}
                </div>
              </div>

              {recalcedData.languages_analysis.warnings?.length > 0 && (
                <div style={{ fontSize: '11px', color: '#ff6b81', background: 'rgba(233,69,96,0.15)', border: '1px solid rgba(233,69,96,0.3)', padding: '4px 10px', borderRadius: '6px' }}>
                  ⚠️ {recalcedData.languages_analysis.warnings.join(' • ')}
                </div>
              )}
            </div>
          )}

          {/* Active Conditions & Situational Buffs Panel */}
          <ConditionsBuffsPanel />

          {/* Ability Scores Breakdown Grid */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.1rem', margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Activity size={16} /> Yetenek Puanları ve Katkıları (Ability Breakdown)
              </h4>
              {recalcedData.point_buy_analysis && (
                <span style={{
                  fontSize: '11px',
                  fontWeight: 'bold',
                  padding: '3px 8px',
                  borderRadius: '6px',
                  background: `${recalcedData.point_buy_analysis.badge_color}20`,
                  color: recalcedData.point_buy_analysis.badge_color,
                  border: `1px solid ${recalcedData.point_buy_analysis.badge_color}60`
                }}>
                  🎲 {recalcedData.point_buy_analysis.total_points} Puan • {recalcedData.point_buy_analysis.tier_name} (Ort: {recalcedData.point_buy_analysis.average_score})
                </span>
              )}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px' }}>
              {Object.entries(recalcedData.ability_scores || store.abilities || {}).map(([abName, totalScore]) => {
                if (abName === 'power_points') return null;
                const normName = abName.charAt(0).toUpperCase() + abName.slice(1);
                const baseScore = store.abilities[normName.toLowerCase()] || store.abilities[abName] || totalScore;
                const mod = recalcedData.ability_modifiers?.[normName] ?? Math.floor((totalScore - 10) / 2);
                const diff = totalScore - baseScore;
                const modSign = mod >= 0 ? `+${mod}` : `${mod}`;
                return (
                  <div key={abName} style={{ background: '#141426', border: '1px solid rgba(201,168,76,0.2)', padding: '10px', borderRadius: '8px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontWeight: 'bold', textTransform: 'uppercase' }}>{normName}</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--accent-gold)', margin: '2px 0' }}>
                      {totalScore} <span style={{ fontSize: '13px', color: '#3fb950' }}>({modSign})</span>
                    </div>
                    <div style={{ fontSize: '10px', color: '#8b949e' }}>
                      {baseScore} Taban {diff !== 0 ? `${diff >= 0 ? '+' : ''}${diff} Bonusu` : ''}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Combat Summary Grid with Math Breakdown */}
          <div>
            <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.1rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Shield size={16} /> Dövüş ve Savunma Detayları (Stat Breakdown)
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
              
              {/* HP Breakdown */}
              <div style={{ background: '#141426', border: '1px solid rgba(233,69,96,0.3)', padding: '12px', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '12px', color: '#8b949e', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Heart size={14} style={{ color: '#e94560' }} /> CAN PUANI (HP)
                  </span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#f0e6d2' }}>{recalcedData.hit_points || 8}</span>
                </div>
                <div style={{ fontSize: '11px', color: '#d4c5a9', marginTop: '6px', borderTop: '1px dashed rgba(255,255,255,0.08)', paddingTop: '6px' }}>
                  Formül: <b>{recalcedData.class_data?.hit_die ? `d${recalcedData.class_data.hit_die}` : 'd10'} Taban</b> + <b>{(recalcedData.ability_modifiers?.Constitution || 0) * level} Con Mod</b>
                  {(recalcedData.applied_modifiers || []).filter(m => m.target === 'hp' && m.value > 0).map((m, i) => (
                    <span key={i} style={{ color: '#3fb950' }}> + {m.value} ({m.source})</span>
                  ))}
                </div>
              </div>

              {/* AC Breakdown */}
              <div style={{ background: '#141426', border: '1px solid rgba(63,185,80,0.3)', padding: '12px', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '12px', color: '#8b949e', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Shield size={14} style={{ color: '#3fb950' }} /> ZIRH SINIFI (AC)
                  </span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#f0e6d2' }}>{recalcedData.armor_class || 10}</span>
                </div>
                <div style={{ fontSize: '11px', color: '#d4c5a9', marginTop: '6px', borderTop: '1px dashed rgba(255,255,255,0.08)', paddingTop: '6px' }}>
                  Formül: <b>10 Taban</b> + <b>{recalcedData.ability_modifiers?.Dexterity || 0} Dex Mod</b>
                  {(recalcedData.applied_modifiers || []).filter(m => m.target === 'ac' && m.value > 0).map((m, i) => (
                    <span key={i} style={{ color: '#3fb950' }}> + {m.value} ({m.source})</span>
                  ))}
                  <div style={{ fontSize: '10px', color: '#8b949e', marginTop: '4px' }}>
                    Touch AC: <b>{recalcedData.touch_ac || 10}</b> | Flat-Footed: <b>{recalcedData.flat_footed_ac || 10}</b>
                  </div>
                </div>
              </div>

              {/* Initiative Breakdown */}
              <div style={{ background: '#141426', border: '1px solid rgba(201,168,76,0.3)', padding: '12px', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '12px', color: '#8b949e', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Sparkles size={14} style={{ color: 'var(--accent-gold)' }} /> İNİSİYATİF
                  </span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 'bold', color: 'var(--accent-gold)' }}>
                    {recalcedData.initiative >= 0 ? `+${recalcedData.initiative}` : recalcedData.initiative || 0}
                  </span>
                </div>
                <div style={{ fontSize: '11px', color: '#d4c5a9', marginTop: '6px', borderTop: '1px dashed rgba(255,255,255,0.08)', paddingTop: '6px' }}>
                  Formül: <b>{recalcedData.ability_modifiers?.Dexterity >= 0 ? `+${recalcedData.ability_modifiers?.Dexterity}` : recalcedData.ability_modifiers?.Dexterity || 0} Dex Mod</b>
                  {(recalcedData.applied_modifiers || []).filter(m => m.target === 'initiative' && m.value !== 0).map((m, i) => (
                    <span key={i} style={{ color: '#38bdf8' }}> + {m.value} ({m.source})</span>
                  ))}
                </div>
              </div>

              {/* BAB & Combat Attacks Breakdown */}
              <div style={{ background: '#141426', border: '1px solid rgba(124,110,247,0.3)', padding: '12px', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '12px', color: '#8b949e', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Sword size={14} style={{ color: '#7c6ef7' }} /> BAB & SALDIRI
                  </span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#7c6ef7' }}>+{recalcedData.bab || 0}</span>
                </div>
                <div style={{ fontSize: '11px', color: '#d4c5a9', marginTop: '6px', borderTop: '1px dashed rgba(255,255,255,0.08)', paddingTop: '6px' }}>
                  Yakın Dövüş (Melee): <b>+{(recalcedData.melee_attack_bonus ?? (recalcedData.bab || 0) + (recalcedData.ability_modifiers?.Strength || 0))}</b> (+{recalcedData.bab || 0} BAB + {recalcedData.ability_modifiers?.Strength || 0} Str)
                  <br />
                  Menzilli (Ranged): <b>+{(recalcedData.ranged_attack_bonus ?? (recalcedData.bab || 0) + (recalcedData.ability_modifiers?.Dexterity || 0))}</b> (+{recalcedData.bab || 0} BAB + {recalcedData.ability_modifiers?.Dexterity || 0} Dex)
                  <div style={{ fontSize: '10px', color: '#8b949e', marginTop: '4px' }}>
                    CMB: <b>+{recalcedData.cmb || 0}</b> | CMD: <b>{recalcedData.cmd || 10}</b>
                  </div>
                </div>
              </div>

            </div>
          </div>

          {/* Saving Throws Math Breakdown */}
          <div style={{ background: '#141426', border: '1px solid rgba(255,255,255,0.08)', padding: '14px', borderRadius: '8px' }}>
            <h4 style={{ color: 'var(--accent-gold)', fontSize: '1rem', marginBottom: '10px' }}>Kurtarma Zarları Detayı (Saving Throws)</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
              {['Fortitude', 'Reflex', 'Will'].map(saveKey => {
                const totalSave = recalcedData.saving_throws?.[saveKey] || 0;
                const abKey = saveKey === 'Fortitude' ? 'Constitution' : saveKey === 'Reflex' ? 'Dexterity' : 'Wisdom';
                const abMod = recalcedData.ability_modifiers?.[abKey] || 0;
                const featSaveMods = (recalcedData.applied_modifiers || []).filter(m => m.target === `saving_throws.${saveKey}` || m.target === 'saving_throws.All');
                return (
                  <div key={saveKey} style={{ background: '#1a1a2e', padding: '10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 'bold' }}>
                      <span>{saveKey}</span>
                      <span style={{ color: 'var(--accent-gold)' }}>{totalSave >= 0 ? `+${totalSave}` : totalSave}</span>
                    </div>
                    <div style={{ fontSize: '10px', color: '#8b949e', marginTop: '4px' }}>
                      Mod: {abMod >= 0 ? `+${abMod}` : abMod} ({abKey.slice(0, 3)})
                      {featSaveMods.map((m, i) => (
                        <span key={i} style={{ color: '#38bdf8' }}> +{m.value} ({m.source})</span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Savaş & Manevra Matrisi (Combat & Maneuver Matrix - PF1e CRB p. 198-201) */}
          {recalcedData.maneuvers && Object.keys(recalcedData.maneuvers).length > 0 && (
            <div style={{ background: '#141426', border: '1px solid rgba(201,168,76,0.3)', padding: '14px', borderRadius: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ margin: 0, color: 'var(--accent-gold)', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Sword size={16} /> Savaş Manevraları Matrisi (Combat Maneuvers & Defense)
                </h4>
                <span style={{ fontSize: '11px', color: '#d4c5a9' }}>
                  Temel CMB: <b style={{ color: '#ffd700' }}>+{recalcedData.cmb || 0}</b> | Temel CMD: <b style={{ color: '#ffd700' }}>{recalcedData.cmd || 10}</b>
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '8px' }}>
                {Object.entries(recalcedData.maneuvers).map(([mName, mData]) => {
                  const hasFeatBonus = mData.bonus_cmb > 0 || mData.bonus_cmd > 0;
                  return (
                    <div key={mName} style={{
                      background: hasFeatBonus ? 'rgba(201,168,76,0.08)' : '#1a1a2e',
                      border: `1px solid ${hasFeatBonus ? 'rgba(201,168,76,0.4)' : 'rgba(255,255,255,0.05)'}`,
                      borderRadius: '6px',
                      padding: '8px 10px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', fontWeight: 'bold', color: hasFeatBonus ? '#ffd700' : '#f0e6d2' }}>
                          {mName}
                        </span>
                        {hasFeatBonus && (
                          <span style={{ fontSize: '9px', background: 'rgba(201,168,76,0.2)', color: '#ffd700', padding: '1px 4px', borderRadius: '3px' }}>
                            Feat
                          </span>
                        )}
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#8b949e' }}>
                        <span>CMB: <b style={{ color: '#38bdf8' }}>{mData.cmb_str}</b></span>
                        <span>CMD: <b style={{ color: '#4ec9b0' }}>{mData.cmd}</b></span>
                      </div>
                      {hasFeatBonus && (
                        <div style={{ fontSize: '9px', color: '#a594ff', marginTop: '2px' }}>
                          {mData.bonus_summary !== 'Standart' && mData.bonus_summary}
                          {mData.cmd_summary !== 'Standart' && ` | ${mData.cmd_summary}`}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Kuşanılmış Silahlar & Tam Saldırı Dizilimi Kartı */}
          {recalcedData.weapons && recalcedData.weapons.length > 0 && (
            <div style={{ background: '#141426', border: '1px solid rgba(124,110,247,0.3)', padding: '14px', borderRadius: '8px' }}>
              <h4 style={{ color: '#a594ff', fontSize: '1rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sword size={16} /> Silah Saldırı & Hasar Dizilimleri (Weapons & Full Attack)
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px' }}>
                {recalcedData.weapons.map((w, idx) => (
                  <div key={idx} style={{
                    background: '#1a1a2e',
                    border: '1px solid rgba(124,110,247,0.2)',
                    borderRadius: '8px',
                    padding: '10px 12px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 'bold', color: '#fff', fontSize: '13px' }}>{w.name}</span>
                      <span style={{ fontSize: '10px', color: '#a594ff', background: 'rgba(124,110,247,0.15)', padding: '2px 6px', borderRadius: '4px' }}>
                        Kritik: {w.crit_range || '20/x2'}
                      </span>
                    </div>
                    <div style={{ fontSize: '11px', color: '#d4c5a9' }}>
                      Saldırı (Tek / Tam): <b style={{ color: '#38bdf8' }}>{w.full_attack || w.calculated_attack}</b>
                      <br />
                      Hasar: <b style={{ color: '#f87171' }}>{w.calculated_damage}</b>
                    </div>
                    {w.power_attack && (
                      <div style={{ marginTop: '4px', padding: '6px 8px', background: 'rgba(233,69,96,0.1)', border: '1px solid rgba(233,69,96,0.3)', borderRadius: '6px', fontSize: '10px' }}>
                        <div style={{ color: '#e94560', fontWeight: 'bold' }}>⚡ Güç Saldırısı (Power Attack):</div>
                        <div style={{ color: '#d4c5a9' }}>
                          Saldırı: <b>{w.power_attack.full_attack}</b> ({w.power_attack.penalty} Penaltı)
                          <br />
                          Hasar: <b style={{ color: '#f87171' }}>{w.power_attack.damage}</b> (+{w.power_attack.bonus_damage} Hasar)
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Applied Modifiers Breakdown List */}
          {(recalcedData.applied_modifiers || []).length > 0 && (
            <div style={{ background: 'rgba(201,168,76,0.04)', border: '1px solid rgba(201,168,76,0.2)', padding: '14px', borderRadius: '8px' }}>
              <h4 style={{ color: 'var(--accent-gold)', fontSize: '1rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={16} /> Aktif Modifikatörler ve Kaynakları ({recalcedData.applied_modifiers.length})
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '8px' }}>
                {recalcedData.applied_modifiers.map((mod, idx) => (
                  <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#141426', padding: '6px 10px', borderRadius: '6px', fontSize: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <span>
                      <b style={{ color: '#f0e6d2' }}>{mod.source}</b>
                      <span style={{ fontSize: '10px', color: '#8b949e', marginLeft: '6px' }}>({mod.type})</span>
                    </span>
                    <span style={{ fontWeight: 'bold', color: mod.value >= 0 ? '#3fb950' : '#e94560' }}>
                      {mod.description || `${mod.value >= 0 ? '+' : ''}${mod.value} to ${mod.target}`}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Encumbrance & Carrying Capacity Visualizer */}
          {(() => {
            const enc = recalcedData.encumbrance || {};
            const cap = enc.carrying_capacity || recalcedData.carrying_capacity || {};
            const lightMax = cap.light_max || 33;
            const mediumMax = cap.medium_max || 66;
            const heavyMax = cap.heavy_max || 100;
            const totalWt = recalcedData.total_weight || enc.total_weight || 0;
            const percent = Math.min(100, Math.round((totalWt / (heavyMax || 100)) * 100));
            const status = enc.status || recalcedData.encumbrance_status || 'Light Load';
            const isMediumOrAbove = status.includes('Medium') || status.includes('Heavy') || status.includes('Overload');
            const statusColor = status.includes('Overload') ? '#e94560' : status.includes('Heavy') ? '#ff9f43' : status.includes('Medium') ? '#feca57' : '#4ec9b0';

            return (
              <div style={{ background: '#141426', padding: '14px', borderRadius: '8px', border: `1px solid ${statusColor}40` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', color: '#f0e6d2', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Shield size={16} style={{ color: statusColor }} /> Taşınabilirlik & Yük Durumu (Encumbrance)
                  </span>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: `${statusColor}20`, border: `1px solid ${statusColor}`, color: statusColor, fontWeight: 'bold' }}>
                      {status}
                    </span>
                    <span style={{ fontSize: '11px', color: (recalcedData.armor_check_penalty || 0) < 0 ? '#f87171' : '#8b949e', fontWeight: 'bold' }}>
                      ACP: {recalcedData.armor_check_penalty || 0}
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#8b949e', marginBottom: '4px' }}>
                  <span>Toplam Yük: <b style={{ color: '#f0e6d2' }}>{totalWt} lbs</b></span>
                  <span>Maksimum Kapasite: <b style={{ color: '#f0e6d2' }}>{heavyMax} lbs</b></span>
                </div>

                {/* Progress bar */}
                <div style={{ height: '8px', backgroundColor: '#0a0a14', borderRadius: '4px', overflow: 'hidden', border: '1px solid #2a2a3a', marginBottom: '6px' }}>
                  <div style={{ width: `${percent}%`, height: '100%', backgroundColor: statusColor, transition: 'width 0.3s ease' }} />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#64748b' }}>
                  <span>Hafif: {lightMax} lbs</span>
                  <span>Orta: {mediumMax} lbs</span>
                  <span>Ağır: {heavyMax} lbs</span>
                </div>

                {isMediumOrAbove && (
                  <div style={{ marginTop: '8px', padding: '6px 10px', borderRadius: '4px', background: `${statusColor}15`, border: `1px solid ${statusColor}30`, fontSize: '11px', color: statusColor }}>
                    ⚠️ {status} Kısıtlaması: Hareket hızı düşüşü ve Max DEX kısıtlaması aktif.
                  </div>
                )}
              </div>
            );
          })()}

          {/* Categorized Equipment List & Quick-Equip Management */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.1rem', margin: 0 }}>Kategorize Envanter & Donanım (Inventory)</h4>
              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  onClick={() => store.equipAllItems && store.equipAllItems()}
                  style={{
                    background: 'rgba(63, 185, 80, 0.15)',
                    color: '#3fb950',
                    border: '1px solid rgba(63, 185, 80, 0.4)',
                    borderRadius: '4px',
                    padding: '3px 8px',
                    fontSize: '11px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                  title="Tüm giyilebilir eşyaları kuşan"
                >
                  ⚔️ Tümünü Kuşan
                </button>
                <button
                  onClick={() => store.unequipAllItems && store.unequipAllItems()}
                  style={{
                    background: 'rgba(139, 148, 158, 0.15)',
                    color: '#8b949e',
                    border: '1px solid rgba(139, 148, 158, 0.4)',
                    borderRadius: '4px',
                    padding: '3px 8px',
                    fontSize: '11px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                  title="Tüm eşyaları çantaya kaldır"
                >
                  🎒 Tümünü Çıkar
                </button>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.3)', padding: '4px', borderRadius: '8px', marginBottom: '12px' }}>
              {['weapons', 'armor_shields', 'consumables', 'gear'].map(cat => (
                <button
                  key={cat}
                  onClick={() => setActiveEqTab(cat)}
                  style={{
                    flex: 1,
                    padding: '6px',
                    fontSize: '11px',
                    borderRadius: '6px',
                    border: 'none',
                    background: activeEqTab === cat ? 'var(--accent-gold)' : 'transparent',
                    color: activeEqTab === cat ? '#0f0f1a' : '#8b949e',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                >
                  {cat.toUpperCase()}
                </button>
              ))}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '280px', overflowY: 'auto' }}>
              {(recalcedData[activeEqTab] || []).length === 0 ? (
                <p style={{ fontSize: '12px', color: '#8b949e', fontStyle: 'italic' }}>Bu kategoride eşya yok.</p>
              ) : (
                (recalcedData[activeEqTab] || []).map((item, i) => {
                  const isEquipped = item.is_equipped !== false && item.equipped !== false;
                  // Find index in master store.equipment
                  const storeIdx = (store.equipment || []).findIndex(
                    it => (it.name || it.isim) === (item.name || item.isim)
                  );

                  return (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '8px 12px',
                        background: isEquipped ? '#16213e' : 'rgba(20, 20, 38, 0.5)',
                        border: isEquipped ? '1px solid rgba(63, 185, 80, 0.3)' : '1px solid rgba(255, 255, 255, 0.05)',
                        borderRadius: '6px',
                        fontSize: '12px'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {storeIdx >= 0 && (
                          <button
                            onClick={() => store.toggleEquipItem && store.toggleEquipItem(storeIdx)}
                            style={{
                              background: isEquipped ? 'rgba(63, 185, 80, 0.2)' : 'rgba(139, 148, 158, 0.15)',
                              color: isEquipped ? '#3fb950' : '#8b949e',
                              border: `1px solid ${isEquipped ? '#3fb95060' : '#8b949e40'}`,
                              borderRadius: '4px',
                              padding: '2px 6px',
                              fontSize: '10px',
                              fontWeight: 'bold',
                              cursor: 'pointer'
                            }}
                            title={isEquipped ? 'Çantaya kaldır (Unequip)' : 'Kuşan (Equip)'}
                          >
                            {isEquipped ? '⚔️ Kuşanıldı' : '🎒 Çantada'}
                          </button>
                        )}
                        <span style={{ color: isEquipped ? '#f0e6d2' : '#8b949e', fontWeight: isEquipped ? 'bold' : 'normal' }}>
                          {item.name || item.isim}
                        </span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '11px', color: '#8b949e' }}>
                        {item.price_gp ? <span style={{ color: '#ffd700' }}>{item.price_gp} gp</span> : null}
                        <span>{item.sistem_verisi?.weight?.value || item.weight || 0} lb</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Servet & Seviye Başı Bütçe Takipçisi (Wealth by Level - PF1e CRB Table 12-4) */}
          {recalcedData.wealth && (
            <div style={{ background: '#141426', border: '1px solid var(--border-gold)', borderRadius: '8px', padding: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h4 style={{ margin: 0, color: 'var(--gold-bright)', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Sparkles size={16} /> Servet & Seviye Başı Bütçe (Wealth by Level)
                </h4>
                <span style={{
                  fontSize: '11px',
                  fontWeight: 'bold',
                  padding: '3px 8px',
                  borderRadius: '6px',
                  background: recalcedData.wealth.status_code === 'over' ? 'rgba(233,69,96,0.2)' : recalcedData.wealth.status_code === 'under' ? 'rgba(56,189,248,0.2)' : 'rgba(63,185,80,0.2)',
                  color: recalcedData.wealth.status_code === 'over' ? '#e94560' : recalcedData.wealth.status_code === 'under' ? '#38bdf8' : '#3fb950',
                  border: `1px solid ${recalcedData.wealth.status_code === 'over' ? '#e94560' : recalcedData.wealth.status_code === 'under' ? '#38bdf8' : '#3fb950'}`
                }}>
                  {recalcedData.wealth.status} ({recalcedData.wealth.percentage}%)
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '8px', marginBottom: '10px' }}>
                <div style={{ background: '#1a1a2e', padding: '8px 10px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>TOPLAM SERVET (GP)</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#ffd700' }}>
                    {recalcedData.wealth.total_wealth_gp.toLocaleString()} gp
                  </div>
                </div>
                <div style={{ background: '#1a1a2e', padding: '8px 10px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>BEKLENEN WBL (Seviye {recalcedData.wealth.level})</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#f0e6d2' }}>
                    {recalcedData.wealth.expected_wbl_gp.toLocaleString()} gp
                  </div>
                </div>
                <div style={{ background: '#1a1a2e', padding: '8px 10px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>FARK (BÜTÇE DENGESİ)</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: recalcedData.wealth.difference_gp >= 0 ? '#3fb950' : '#38bdf8' }}>
                    {recalcedData.wealth.difference_gp >= 0 ? `+${recalcedData.wealth.difference_gp.toLocaleString()}` : `${recalcedData.wealth.difference_gp.toLocaleString()}`} gp
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                <div style={{
                  width: `${Math.min(100, recalcedData.wealth.percentage)}%`,
                  height: '100%',
                  background: recalcedData.wealth.status_code === 'over' ? '#e94560' : recalcedData.wealth.status_code === 'under' ? '#38bdf8' : '#3fb950',
                  transition: 'width 0.3s ease'
                }} />
              </div>
            </div>
          )}

          {/* 12 Büyülü Eşya Vücut Slotu Matrisi (12 Magic Item Body Slots - PF1e CRB p. 458) */}
          {recalcedData.magic_item_slots && (
            <div style={{ background: '#141426', border: '1px solid rgba(124,110,247,0.3)', borderRadius: '8px', padding: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ margin: 0, color: '#a594ff', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Shield size={16} /> 12 Büyülü Eşya Vücut Slotu (Magic Item Body Slots)
                </h4>
                {recalcedData.has_slot_conflicts && (
                  <span style={{ fontSize: '11px', background: 'rgba(233,69,96,0.2)', color: '#e94560', border: '1px solid #e94560', padding: '2px 8px', borderRadius: '4px', fontWeight: 'bold' }}>
                    ⚠️ {recalcedData.slot_conflicts.length} Slot Çakışması Var!
                  </span>
                )}
              </div>

              {/* Slot Conflicts Alert Banner */}
              {recalcedData.has_slot_conflicts && (
                <div style={{ background: 'rgba(233,69,96,0.1)', border: '1px solid rgba(233,69,96,0.4)', borderRadius: '6px', padding: '8px 12px', marginBottom: '12px', fontSize: '11px', color: '#ffb3b3' }}>
                  {recalcedData.slot_conflicts.map((c, i) => (
                    <div key={i} style={{ marginBottom: i < recalcedData.slot_conflicts.length - 1 ? '4px' : 0 }}>
                      ⚠️ <b>{c.slot_display}:</b> {c.message}
                    </div>
                  ))}
                </div>
              )}

              {/* 12 Slots Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '8px' }}>
                {[
                  { key: 'headband', label: 'Alınlık / Taç (Headband)' },
                  { key: 'head', label: 'Baş / Miğfer (Head)' },
                  { key: 'eyes', label: 'Göz / Gözlük (Eyes)' },
                  { key: 'neck', label: 'Boyun / Muska (Neck)' },
                  { key: 'shoulders', label: 'Omuz / Pelerin (Shoulders)' },
                  { key: 'armor', label: 'Zırh / Cübbe (Armor)' },
                  { key: 'body', label: 'Beden / Kaftan (Body)' },
                  { key: 'chest', label: 'Göğüs / Gömlek (Chest)' },
                  { key: 'belts', label: 'Kemer (Belt)' },
                  { key: 'wrists', label: 'Bilek / Bileklik (Wrists)' },
                  { key: 'hands', label: 'El / Eldiven (Hands)' },
                  { key: 'feet', label: 'Ayak / Bot (Feet)' },
                  { key: 'ring_1', label: 'Yüzük 1 (Ring 1)' },
                  { key: 'ring_2', label: 'Yüzük 2 (Ring 2)' }
                ].map(({ key, label }) => {
                  const equipped = recalcedData.magic_item_slots[key];
                  return (
                    <div key={key} style={{
                      background: equipped ? 'rgba(124,110,247,0.1)' : '#1a1a2e',
                      border: `1px solid ${equipped ? 'rgba(124,110,247,0.4)' : 'rgba(255,255,255,0.05)'}`,
                      borderRadius: '6px',
                      padding: '8px 10px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px'
                    }}>
                      <div style={{ fontSize: '10px', color: '#8b949e', fontWeight: 'bold' }}>{label}</div>
                      {equipped ? (
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#ffd700' }}>
                            {equipped.name}
                          </span>
                          {equipped.price_gp > 0 && (
                            <span style={{ fontSize: '10px', color: '#38bdf8' }}>
                              {equipped.price_gp.toLocaleString()} gp
                            </span>
                          )}
                        </div>
                      ) : (
                        <span style={{ fontSize: '11px', color: '#555a64', fontStyle: 'italic' }}>
                          [Boş Slot]
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

        </div>
      ) : viewMode === 'spells' ? (
        /* Spellbook & Interactive Spell Cards View Area */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(124,110,247,0.08)', padding: '14px 18px', borderRadius: '10px', border: '1px solid rgba(124,110,247,0.3)' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#a594ff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Wand2 size={20} />
                Büyü Kitabı & Günlük Yuva Takipçisi ({name})
              </h3>
              <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#8b949e' }}>
                Günlük büyü yuvalarınızı harcayın, hazırlanan büyülerinizi yönetin veya büyü kartlarından zar atın.
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <button
                type="button"
                className="gold-btn"
                onClick={() => store.restCharacter()}
                style={{ padding: '6px 14px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(124,110,247,0.2)', border: '1px solid #7c6ef7', color: '#d8b4fe', fontWeight: 'bold' }}
                title="Tüm büyü yuvalarını ve hazırlanan büyüleri sıfırlar"
              >
                🌙 Uzun Dinlenme Yap
              </button>
              <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#a594ff', background: 'rgba(124,110,247,0.15)', padding: '6px 12px', borderRadius: '8px', border: '1px solid rgba(124,110,247,0.3)' }}>
                CL +{recalcedData.spellcasting?.caster_level || level || 1}
              </div>
            </div>
          </div>

          {/* Spellcasting Engine Stat Header (DCs, Concentration, CL) */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', background: '#121124', padding: '14px', borderRadius: '8px', border: '1px solid rgba(124,110,247,0.25)' }}>
            <div style={{ textAlign: 'center', padding: '6px', background: 'rgba(124,110,247,0.1)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', color: '#a594ff', fontWeight: 'bold' }}>BÜYÜCÜ SEVİYESİ (CL)</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: '#ffffff' }}>+{recalcedData.spellcasting?.caster_level || level || 1}</div>
            </div>

            <div style={{ textAlign: 'center', padding: '6px', background: 'rgba(124,110,247,0.1)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', color: '#a594ff', fontWeight: 'bold' }}>ODAKLANMA (CONCENTRATION)</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: '#38bdf8' }}>
                {(recalcedData.spellcasting?.concentration_bonus ?? 0) >= 0 ? `+${recalcedData.spellcasting?.concentration_bonus || 0}` : recalcedData.spellcasting?.concentration_bonus || 0}
              </div>
            </div>

            {/* Spell DC Cards per Level (0..5) */}
            {[0, 1, 2, 3, 4, 5].map(lvlIdx => {
              const dcVal = recalcedData.spellcasting?.spell_dcs?.[String(lvlIdx)] || (10 + lvlIdx + (recalcedData.ability_modifiers?.Intelligence || 0));
              return (
                <div key={lvlIdx} style={{ textAlign: 'center', padding: '6px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-secondary)' }}>{lvlIdx === 0 ? 'Cantrip DC' : `${lvlIdx}. Seviye DC`}</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--accent-gold)' }}>{dcVal}</div>
                </div>
              );
            })}
          </div>

          {/* Spellbook Capacity & Scribing Cost Tracker (PF1e CRB p. 219, Table 9-3) */}
          {recalcedData.spellbook_scribing && (
            <div style={{ background: '#121124', border: '1px solid rgba(124,110,247,0.3)', borderRadius: '10px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h4 style={{ margin: 0, color: 'var(--gold-bright)', fontSize: '0.95rem', fontFamily: 'Cinzel, serif', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  📜 Büyü Kitabı Sayfa & Mürekkep Analizi (Spellbook Capacity & Scribing)
                </h4>
                <span style={{
                  fontSize: '11px',
                  fontWeight: 'bold',
                  padding: '3px 8px',
                  borderRadius: '6px',
                  background: recalcedData.spellbook_scribing.is_overflow ? 'rgba(233,69,96,0.2)' : 'rgba(78,201,176,0.2)',
                  color: recalcedData.spellbook_scribing.is_overflow ? '#e94560' : '#4ec9b0',
                  border: `1px solid ${recalcedData.spellbook_scribing.is_overflow ? '#e94560' : '#4ec9b0'}`
                }}>
                  {recalcedData.spellbook_scribing.books_needed} Cilt Gerekli ({recalcedData.spellbook_scribing.total_pages_used} / 100 Sayfa)
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '8px', marginBottom: '10px' }}>
                <div style={{ background: '#0a0914', padding: '8px 10px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>TOPLAM SAYFA</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#f0e6d2' }}>
                    {recalcedData.spellbook_scribing.total_pages_used} / {recalcedData.spellbook_scribing.books_needed * 100}
                  </div>
                </div>
                <div style={{ background: '#0a0914', padding: '8px 10px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>MÜREKKEP MALİYETİ</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#ffd700' }}>
                    {recalcedData.spellbook_scribing.total_cost_gp.toLocaleString()} gp
                  </div>
                </div>
                <div style={{ background: '#0a0914', padding: '8px 10px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>KİTAP DOLULUK ORANI</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#38bdf8' }}>
                    %{recalcedData.spellbook_scribing.percentage}
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                <div style={{
                  width: `${Math.min(100, (recalcedData.spellbook_scribing.total_pages_used % 100) || 100)}%`,
                  height: '100%',
                  background: recalcedData.spellbook_scribing.is_overflow ? '#e94560' : 'linear-gradient(90deg, #7c6ef7 0%, #4ec9b0 100%)',
                  transition: 'width 0.3s ease'
                }} />
              </div>
            </div>
          )}

          {/* Interactive Daily Spell Slots Grid */}
          {recalcedData.spell_slots && Object.keys(recalcedData.spell_slots).length > 0 && (
            <div style={{ background: '#121124', border: '1px solid var(--border-gold)', borderRadius: '10px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ margin: 0, color: 'var(--gold-bright)', fontSize: '0.95rem', fontFamily: 'Cinzel, serif', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  ✨ Günlük Büyü Yuvaları (Canlı Takip - Tıklayarak Harcayın)
                </h4>
                <span style={{ fontSize: '11px', color: '#8b949e' }}>
                  {recalcedData.spellcasting?.is_prepared ? 'Hazırlamalı Büyücü' : 'Spontane Büyücü'}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
                {Object.entries(recalcedData.spell_slots).map(([lvlStr, totalSlots]) => {
                  const lvl = parseInt(lvlStr);
                  const usedCount = store.usedSpellSlots?.[lvlStr] || 0;
                  const remaining = Math.max(0, totalSlots - usedCount);
                  const dcVal = recalcedData.spellcasting?.spell_dcs?.[lvlStr] || (10 + lvl);

                  return (
                    <div key={lvlStr} style={{ background: '#0a0914', border: '1px solid rgba(124,110,247,0.2)', borderRadius: '8px', padding: '10px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.82rem', fontWeight: 'bold', color: 'var(--gold-bright)' }}>
                          {lvl === 0 ? '0. Seviye (Cantrips)' : `${lvl}. Seviye Slotlar`}
                        </span>
                        <span style={{ fontSize: '0.65rem', background: 'rgba(124,110,247,0.2)', color: '#d8b4fe', padding: '1px 6px', borderRadius: '4px', fontWeight: 'bold' }}>
                          DC {dcVal}
                        </span>
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2px' }}>
                        <span style={{ fontSize: '0.72rem', color: remaining > 0 ? '#4ec9b0' : '#e94560', fontWeight: 600 }}>
                          {remaining} / {totalSlots} Slot Kalan
                        </span>

                        <div style={{ display: 'flex', gap: '4px' }}>
                          {Array.from({ length: totalSlots }).map((_, i) => {
                            const isUsed = i < usedCount;
                            return (
                              <div
                                key={i}
                                onClick={() => store.toggleSpellSlotUsed(lvlStr, totalSlots)}
                                title={isUsed ? `${lvl}. Seviye Slot Harcandı (Geri Almak İçin Tıkla)` : `${lvl}. Seviye Slot Hazır (Harcamak İçin Tıkla)`}
                                style={{
                                  width: '20px', height: '20px', borderRadius: '4px', cursor: 'pointer',
                                  backgroundColor: isUsed ? '#e94560' : 'rgba(78, 201, 176, 0.2)',
                                  border: `1px solid ${isUsed ? '#ff6b81' : '#4ec9b0'}`,
                                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                                  fontSize: '0.65rem', color: isUsed ? '#fff' : '#4ec9b0', fontWeight: 'bold',
                                  transition: 'all 0.15s ease'
                                }}
                              >
                                {isUsed ? '✕' : '✓'}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Prepared Spells Daily Overview for Prepared Casters */}
          {store.preparedSpells && Object.values(store.preparedSpells).some(arr => Array.isArray(arr) && arr.some(item => item && item.name)) && (
            <div style={{ background: '#121124', border: '1px solid rgba(124,110,247,0.3)', borderRadius: '10px', padding: '16px' }}>
              <h4 style={{ margin: '0 0 12px 0', color: '#a594ff', fontSize: '0.95rem', fontFamily: 'Cinzel, serif', display: 'flex', alignItems: 'center', gap: '6px' }}>
                🔮 Günün Hazırlanan Büyüleri (Prepared Spells)
              </h4>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {Object.entries(store.preparedSpells).map(([lvlStr, slots]) => {
                  if (!Array.isArray(slots) || !slots.some(s => s && s.name)) return null;
                  const lvl = parseInt(lvlStr);

                  return (
                    <div key={lvlStr} style={{ background: '#0a0914', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '8px', padding: '10px' }}>
                      <div style={{ fontSize: '0.78rem', color: 'var(--gold-bright)', fontWeight: 'bold', marginBottom: '8px', fontFamily: 'Cinzel, serif' }}>
                        {lvl === 0 ? '0. Seviye Hazırlanan Büyüler' : `${lvl}. Seviye Hazırlanan Büyüler`}
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '8px' }}>
                        {slots.map((pItem, sIdx) => {
                          if (!pItem || !pItem.name) return null;
                          const isCast = pItem.cast;
                          const appliedMeta = pItem.metamagic || [];

                          return (
                            <div
                              key={sIdx}
                              style={{
                                background: isCast ? 'rgba(233,69,96,0.08)' : 'rgba(78,201,176,0.08)',
                                border: `1px solid ${isCast ? 'rgba(233,69,96,0.3)' : 'rgba(78,201,176,0.3)'}`,
                                borderRadius: '6px', padding: '8px 10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                              }}
                            >
                              <div>
                                <div style={{ fontSize: '0.82rem', fontWeight: 'bold', color: isCast ? '#ff6b81' : '#f0e6d2' }}>
                                  #{sIdx + 1}: {pItem.name}
                                </div>
                                {appliedMeta.length > 0 && (
                                  <div style={{ display: 'flex', gap: '4px', marginTop: '2px' }}>
                                    {appliedMeta.map((m, mIdx) => (
                                      <span key={mIdx} style={{ fontSize: '0.6rem', color: '#d8b4fe', background: 'rgba(124,110,247,0.2)', padding: '1px 4px', borderRadius: '3px' }}>
                                        ✦ {m}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>

                              <button
                                type="button"
                                onClick={() => store.togglePreparedSpellCast(lvlStr, sIdx)}
                                style={{
                                  padding: '3px 8px', borderRadius: '4px', fontSize: '0.68rem', fontWeight: 'bold', cursor: 'pointer',
                                  backgroundColor: isCast ? '#e94560' : 'rgba(78, 201, 176, 0.2)',
                                  border: `1px solid ${isCast ? '#ff6b81' : '#4ec9b0'}`,
                                  color: isCast ? '#fff' : '#4ec9b0'
                                }}
                              >
                                {isCast ? '✕ Atıldı' : '✓ Hazır'}
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Grimoire Explorer & Filters Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
            <h4 style={{ margin: 0, color: 'var(--gold-bright)', fontSize: '1.1rem', fontFamily: 'Cinzel, serif', display: 'flex', alignItems: 'center', gap: '8px' }}>
              ✦ Büyü Defteri & Kartları ({store.spells?.length || 0})
            </h4>

            {/* Level & School Filter Pills */}
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
              <span style={{ fontSize: '11px', color: '#8b949e' }}>Seviye:</span>
              {['all', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'].map(fLvl => (
                <button
                  key={fLvl}
                  type="button"
                  onClick={() => setSpellLevelFilter(fLvl)}
                  style={{
                    padding: '3px 8px', borderRadius: '4px', fontSize: '0.68rem', cursor: 'pointer',
                    backgroundColor: spellLevelFilter === fLvl ? 'var(--accent-gold)' : 'rgba(255,255,255,0.05)',
                    border: `1px solid ${spellLevelFilter === fLvl ? 'var(--accent-gold)' : 'rgba(255,255,255,0.1)'}`,
                    color: spellLevelFilter === fLvl ? '#0f0f1a' : '#94a3b8',
                    fontWeight: 'bold'
                  }}
                >
                  {fLvl === 'all' ? 'Tümü' : `Lv ${fLvl}`}
                </button>
              ))}
            </div>
          </div>

          {(!store.spells || store.spells.length === 0) ? (
            <div style={{ textAlign: 'center', padding: '40px 20px', background: 'rgba(0,0,0,0.25)', borderRadius: '10px', border: '1px dashed rgba(124,110,247,0.3)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
              <Wand2 size={40} style={{ color: '#7c6ef7' }} />
              <div style={{ fontSize: '15px', color: '#f0e6d2', fontWeight: 'bold' }}>Henüz Büyü Eklemediniz</div>
              <p style={{ fontSize: '13px', color: '#8b949e', maxWidth: '400px', margin: 0 }}>
                Sol paneldeki <b>Büyü Seçimi</b> alanından Pathfinder 1e veritabanındaki 3.000+ büyü arasından karakterinize büyü ekleyebilirsiniz.
              </p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
              {store.spells
                .filter(sp => {
                  if (spellLevelFilter === 'all') return true;
                  const sLvl = typeof sp === 'object' ? (sp.sistem_verisi?.level ?? sp.level ?? 0) : 0;
                  return String(sLvl) === String(spellLevelFilter);
                })
                .map((sp, idx) => (
                  <SpellCard
                    key={idx}
                    spell={sp}
                    characterLevel={level}
                    characterClass={charClass}
                    onRemoveSpell={(spellNameToRemove) => store.removeSpell(spellNameToRemove)}
                    compact={false}
                  />
                ))}
            </div>
          )}
        </div>
      ) : viewMode === 'feats' ? (
        /* Feat & Trait Interactive Codex Cards View Area */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(201,168,76,0.08)', padding: '14px 18px', borderRadius: '10px', border: '1px solid rgba(201,168,76,0.3)' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={20} />
                Feat & Trait Kartları Kütüphanesi ({name})
              </h3>
              <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#8b949e' }}>
                Karakterinize tanımlı hüner (Feat) ve karakter özelliklerinin (Trait) açıklamalarını inceleyin.
              </p>
            </div>
            <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--accent-gold)', background: 'rgba(201,168,76,0.2)', padding: '4px 12px', borderRadius: '12px', border: '1px solid rgba(201,168,76,0.4)' }}>
              {feats.length} Feat | {traits.length} Trait Seçili
            </div>
          </div>

          {/* Feats Grid */}
          <div>
            <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.1rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              ✦ Seçili Hünerler (Feats - {feats.length})
            </h4>
            {feats.length === 0 ? (
              <p style={{ fontSize: '13px', color: '#8b949e', fontStyle: 'italic' }}>Henüz bir hüner (Feat) seçilmedi.</p>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '14px' }}>
                {feats.map((f, i) => {
                  const fName = typeof f === 'object' ? (f.isim || f.name || 'Feat') : String(f);
                  const sys = typeof f === 'object' ? (f.sistem_verisi || f.system || {}) : {};
                  const fCat = typeof f === 'object' ? (sys.feat_category || sys.category || f.kategori || f.category || 'General') : 'General';
                  const prereq = sys.prerequisites || sys.prereq || sys.onkosullar || f.prerequisite || f.prereq;
                  const desc = sys.description?.value || sys.description || sys.benefit || sys.fayda || f.aciklama || f.description || 'Etkili hüner yeteneği';

                  return (
                    <div key={i} style={{ background: '#141426', border: '1px solid rgba(201,168,76,0.3)', borderRadius: '10px', padding: '14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <span style={{ fontSize: '1rem', fontWeight: 'bold', color: 'var(--accent-gold)', fontFamily: 'Cinzel, serif' }}>
                          ✦ {fName}
                        </span>
                        <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '6px', background: 'rgba(201,168,76,0.15)', color: 'var(--accent-gold)', border: '1px solid rgba(201,168,76,0.3)' }}>
                          {fCat}
                        </span>
                      </div>
                      {prereq && prereq !== '-' && (
                        <div style={{ fontSize: '11px', color: '#38bdf8' }}>
                          <b>Ön Koşul:</b> {String(prereq).replace(/<[^>]*>/g, '')}
                        </div>
                      )}
                      <div style={{ fontSize: '12px', color: '#d4c5a9', lineHeight: '1.4', background: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '6px' }}>
                        {String(desc).replace(/<[^>]*>/g, '')}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Traits Grid */}
          <div style={{ marginTop: '10px' }}>
            <h4 style={{ color: '#7c6ef7', fontSize: '1.1rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🛡 Karakter & Soy Özellikleri (Traits - {traits.length})
            </h4>
            {traits.length === 0 ? (
              <p style={{ fontSize: '13px', color: '#8b949e', fontStyle: 'italic' }}>Henüz bir karakter özelliği (Trait) seçilmedi.</p>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '14px' }}>
                {traits.map((t, i) => {
                  const tName = typeof t === 'object' ? (t.isim || t.name || 'Trait') : String(t);
                  const sys = typeof t === 'object' ? (t.sistem_verisi || t.system || {}) : {};
                  const tCat = sys.trait_category || sys.category || t.kategori || t.category || 'Character Trait';
                  const desc = sys.description?.value || sys.description || sys.aciklama || t.aciklama || t.description || 'Trait etkisi aktif';

                  return (
                    <div key={i} style={{ background: '#141426', border: '1px solid rgba(124,110,247,0.3)', borderRadius: '10px', padding: '14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <span style={{ fontSize: '1rem', fontWeight: 'bold', color: '#a594ff', fontFamily: 'Cinzel, serif' }}>
                          🛡 {tName}
                        </span>
                        <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '6px', background: 'rgba(124,110,247,0.15)', color: '#a594ff', border: '1px solid rgba(124,110,247,0.3)' }}>
                          {tCat}
                        </span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#d4c5a9', lineHeight: '1.4', background: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '6px' }}>
                        {String(desc).replace(/<[^>]*>/g, '')}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      ) : null}

      {/* Companion Live Stat Block Card */}
      {store.companion && (
        <div style={{ marginTop: '20px', padding: '20px', background: 'linear-gradient(135deg, rgba(201,168,76,0.08) 0%, rgba(10,8,20,0.9) 100%)', border: '2px solid var(--accent-gold)', borderRadius: '12px', boxShadow: '0 0 20px rgba(0,0,0,0.5)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.4rem' }}>🐾</span>
              <div>
                <h4 style={{ margin: 0, color: 'var(--accent-gold)', fontFamily: 'Cinzel, serif', fontSize: '1.2rem' }}>
                  {store.companion.name || 'Yoldaş'} ({store.companion.species})
                </h4>
                <span style={{ fontSize: '12px', color: '#8b949e' }}>
                  {store.companion.type === 'animal_companion' ? 'Hayvan Yoldaş (Animal Companion)' :
                   store.companion.type === 'eidolon' ? 'Summoner Eidolon' :
                   store.companion.type === 'familiar' ? 'Sihirli Familiar' : 'Binek (Mount)'}
                </span>
              </div>
            </div>
            <div style={{ fontSize: '12px', background: 'rgba(201,168,76,0.15)', color: 'var(--accent-gold)', padding: '4px 12px', borderRadius: '12px', border: '1px solid rgba(201,168,76,0.3)', fontWeight: 'bold' }}>
              Seviye {store.companion.level || 1} Stat Bloğu
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', marginBottom: '12px' }}>
            <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', color: '#8b949e', textTransform: 'uppercase' }}>Can Puanı (HP)</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#3fb950' }}>{store.companion.hp} HP</div>
              <div style={{ fontSize: '10px', color: '#8b949e' }}>{store.companion.hd}d8 HD</div>
            </div>

            <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', color: '#8b949e', textTransform: 'uppercase' }}>Zırh Sınıfı (AC)</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#e94560' }}>{store.companion.ac} AC</div>
              <div style={{ fontSize: '10px', color: '#8b949e' }}>Doğal Zırh</div>
            </div>

            <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', color: '#8b949e', textTransform: 'uppercase' }}>Saldırı (Attacks)</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 'bold', color: 'var(--accent-gold)' }}>{store.companion.attacks}</div>
              <div style={{ fontSize: '10px', color: '#8b949e' }}>BAB: {store.companion.bab}</div>
            </div>
          </div>

          {store.companion.tricks && store.companion.tricks.length > 0 && (
            <div style={{ marginTop: '8px' }}>
              <span style={{ fontSize: '12px', color: 'var(--accent-gold)', fontWeight: 'bold' }}>Komut Numaraları (Tricks): </span>
              <span style={{ fontSize: '12px', color: '#f0e6d2' }}>{store.companion.tricks.join(', ')}</span>
            </div>
          )}

          {store.companion.evolutions && store.companion.evolutions.length > 0 && (
            <div style={{ marginTop: '8px' }}>
              <span style={{ fontSize: '12px', color: '#c4beff', fontWeight: 'bold' }}>Eidolon Evrimleri: </span>
              <span style={{ fontSize: '12px', color: '#f0e6d2' }}>{store.companion.evolutions.join(', ')}</span>
            </div>
          )}

          {store.companion.masterBonus && (
            <div style={{ marginTop: '8px' }}>
              <span style={{ fontSize: '12px', color: '#52b788', fontWeight: 'bold' }}>Efendi Bonusu: </span>
              <span style={{ fontSize: '12px', color: '#ffffff', fontWeight: 'bold' }}>{store.companion.masterBonus}</span>
            </div>
          )}

          {store.companion.notes && (
            <div style={{ marginTop: '8px', fontSize: '11px', color: '#8b949e', fontStyle: 'italic' }}>
              Notlar: {store.companion.notes}
            </div>
          )}
        </div>
      )}

      {isDiffModalOpen && (
        <CharacterDiffModal
          isOpen={isDiffModalOpen}
          onClose={() => setIsDiffModalOpen(false)}
          initialCharA={store.characterData || store}
        />
      )}

      {showCardModal && (
        <CharacterCardModal
          character={store}
          recalcedData={recalcedData}
          onClose={() => setShowCardModal(false)}
        />
      )}

      {showProgressionModal && (
        <ProgressionPlannerModal
          character={store}
          onClose={() => setShowProgressionModal(false)}
        />
      )}

      {showStatblockModal && (
        <StatblockModal
          character={store.characterData || store}
          recalcedData={recalcedData}
          onClose={() => setShowStatblockModal(false)}
        />
      )}

      {showPartyLootModal && (
        <PartyLootModal
          character={store.characterData || store}
          onClose={() => setShowPartyLootModal(false)}
        />
      )}

    </div>
  );
}
