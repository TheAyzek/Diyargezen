import React, { useState, useEffect, useRef } from 'react';
import { X, RefreshCw, Download, FileText, Sparkles, AlertCircle } from 'lucide-react';
import { generateCharacterPDFBlobUrl, exportCharacterPDF } from '../utils/pdfExportUtil';

export default function LivePDFModal({ isOpen, onClose, store }) {
  const [pdfUrl, setPdfUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const activeUrlRef = useRef(null);

  const renderPDF = async () => {
    if (!store) return;
    setLoading(true);
    setError(null);
    try {
      const newUrl = await generateCharacterPDFBlobUrl(store);
      if (activeUrlRef.current) {
        URL.revokeObjectURL(activeUrlRef.current);
      }
      activeUrlRef.current = newUrl;
      setPdfUrl(newUrl);
    } catch (err) {
      console.error('Live PDF generation failed:', err);
      setError(err.message || 'Canlı PDF oluşturulamadı.');
    } finally {
      setLoading(false);
    }
  };

  // Debounced auto-refresh on store changes (400ms)
  useEffect(() => {
    if (!isOpen) return;

    const timer = setTimeout(() => {
      renderPDF();
    }, 400);

    return () => clearTimeout(timer);
  }, [
    isOpen,
    store?.name,
    store?.level,
    store?.race,
    store?.class,
    store?.abilities,
    store?.skills,
    store?.feats,
    store?.traits,
    store?.spells,
    store?.equipment,
    store?.recalcedData
  ]);

  // Clean up object URLs on unmount
  useEffect(() => {
    return () => {
      if (activeUrlRef.current) {
        URL.revokeObjectURL(activeUrlRef.current);
        activeUrlRef.current = null;
      }
    };
  }, []);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(5, 5, 12, 0.85)',
      backdropFilter: 'blur(8px)',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '16px'
    }}>
      <div style={{
        background: 'linear-gradient(145deg, rgba(15, 12, 28, 0.98) 0%, rgba(26, 21, 46, 0.95) 100%)',
        border: '1px solid rgba(201, 168, 76, 0.35)',
        borderRadius: '12px',
        width: '95vw',
        maxWidth: '1200px',
        height: '92vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.7), 0 0 30px rgba(201, 168, 76, 0.15)',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '14px 20px',
          borderBottom: '1px solid rgba(201, 168, 76, 0.2)',
          background: 'rgba(10, 8, 20, 0.6)',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: 32,
              height: 32,
              borderRadius: '6px',
              background: 'linear-gradient(135deg, rgba(201,168,76,0.3) 0%, rgba(124,110,247,0.3) 100%)',
              border: '1px solid rgba(201,168,76,0.4)',
              display: 'flex',
              alignItems: 'center',
              justify: 'center'
            }}>
              <FileText size={18} style={{ color: '#ffd700' }} />
            </div>
            <div>
              <h2 style={{
                fontFamily: 'Cinzel, serif',
                fontSize: '1.1rem',
                color: 'var(--gold-bright, #ffd700)',
                margin: 0,
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                Resmi PF1e AcroForm Karakter Kağıdı (Canlı Önizleme)
                {loading && (
                  <span style={{ fontSize: '0.72rem', color: '#c084fc', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Sparkles size={12} className="animate-spin" /> Yenileniyor...
                  </span>
                )}
              </h2>
              <div style={{ fontSize: '0.72rem', color: 'var(--gold-pale, #94a3b8)', marginTop: 2 }}>
                Sol panelde yaptığınız değişiklikler 400ms içinde canlı PDF formuna yansır.
              </div>
            </div>
          </div>

          {/* Action Toolbar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={renderPDF}
              disabled={loading}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                color: '#cbd5e1',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '0.78rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.2s'
              }}
            >
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
              Yenile
            </button>

            <button
              onClick={() => exportCharacterPDF(store)}
              style={{
                background: 'linear-gradient(135deg, rgba(201,168,76,0.3) 0%, rgba(139,94,20,0.5) 100%)',
                border: '1px solid rgba(201,168,76,0.6)',
                color: '#fff',
                padding: '6px 14px',
                borderRadius: '6px',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 2px 10px rgba(201,168,76,0.2)'
              }}
            >
              <Download size={14} />
              PDF İndir
            </button>

            <button
              onClick={onClose}
              style={{
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#f87171',
                padding: '6px 10px',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center'
              }}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Content Body / iframe */}
        <div style={{ flex: 1, position: 'relative', background: '#0f172a' }}>
          {error ? (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
              color: '#f87171',
              background: 'rgba(30, 15, 20, 0.9)',
              padding: '24px 32px',
              borderRadius: '8px',
              border: '1px solid rgba(239, 68, 68, 0.4)'
            }}>
              <AlertCircle size={36} style={{ marginBottom: 12 }} />
              <div style={{ fontWeight: 'bold', fontSize: '1rem', marginBottom: 6 }}>PDF Önizleme Hatası</div>
              <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>{error}</div>
              <button
                onClick={renderPDF}
                style={{ marginTop: 16, background: '#ef4444', color: '#fff', border: 'none', padding: '6px 16px', borderRadius: '4px', cursor: 'pointer' }}
              >
                Tekrar Deneyin
              </button>
            </div>
          ) : pdfUrl ? (
            <iframe
              src={pdfUrl}
              title="Resmi PF1e AcroForm Karakter Kağıdı"
              style={{
                width: '100%',
                height: '100%',
                border: 'none',
                background: '#525659'
              }}
            />
          ) : (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
              color: 'var(--gold-bright, #ffd700)'
            }}>
              <Sparkles size={32} className="animate-spin" style={{ marginBottom: 12 }} />
              <div style={{ fontFamily: 'Cinzel, serif', fontSize: '0.95rem' }}>PF1e AcroForm PDF Çiziliyor...</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
