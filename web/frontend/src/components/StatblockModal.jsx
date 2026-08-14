import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Copy, Check, Download, FileText, Code, Sparkles } from 'lucide-react';

export default function StatblockModal({ character, recalcedData, onClose }) {
  const [statblockData, setStatblockData] = useState({ plain_text: '', markdown: '' });
  const [activeTab, setActiveTab] = useState('plain_text'); // 'plain_text', 'markdown', 'json'
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    axios.post('/api/rules/generate-statblock', {
      character: character,
      recalced_data: recalcedData
    })
      .then(res => {
        setStatblockData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error generating statblock:', err);
        setLoading(false);
      });
  }, [character, recalcedData]);

  const jsonString = JSON.stringify({
    app: "Diyargezen Pathfinder 1e Character Creator",
    schema_version: "2.0",
    export_date: new Date().toISOString(),
    character: character
  }, null, 2);

  const getActiveContent = () => {
    if (activeTab === 'plain_text') return statblockData.plain_text;
    if (activeTab === 'markdown') return statblockData.markdown;
    return jsonString;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(getActiveContent());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJson = () => {
    const charName = character?.name || 'character';
    const cleanName = charName.toLowerCase().replace(/[^a-z0-9]/g, '_');
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${cleanName}_backup.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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
        maxWidth: '850px',
        maxHeight: '90vh',
        boxShadow: '0 10px 40px rgba(0,0,0,0.8), 0 0 20px rgba(201,168,76,0.2)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Modal Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 22px',
          borderBottom: '1px solid rgba(201,168,76,0.3)',
          background: 'linear-gradient(90deg, rgba(201,168,76,0.15) 0%, transparent 100%)'
        }}>
          <div>
            <h3 style={{ margin: 0, color: 'var(--accent-gold)', fontSize: '1.25rem', fontFamily: 'Cinzel, serif', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={20} /> Resmi Paizo Statblock & JSON Dışa Aktarma
            </h3>
            <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#a594ff' }}>
              Discord, forumlar, VTT aktarımı ve tam karakter yedeği
            </p>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Tab Selection & Actions Bar */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
          background: 'rgba(0,0,0,0.2)'
        }}>
          <div style={{ display: 'flex', gap: '6px' }}>
            <button
              type="button"
              onClick={() => setActiveTab('plain_text')}
              style={{
                padding: '6px 12px',
                fontSize: '12px',
                borderRadius: '6px',
                border: 'none',
                background: activeTab === 'plain_text' ? 'var(--accent-gold)' : 'rgba(255,255,255,0.05)',
                color: activeTab === 'plain_text' ? '#0f0f1a' : '#c9d1d9',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              📄 Resmi Statblock (Paizo)
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('markdown')}
              style={{
                padding: '6px 12px',
                fontSize: '12px',
                borderRadius: '6px',
                border: 'none',
                background: activeTab === 'markdown' ? 'var(--accent-gold)' : 'rgba(255,255,255,0.05)',
                color: activeTab === 'markdown' ? '#0f0f1a' : '#c9d1d9',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              💬 Markdown (Discord / Forum)
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('json')}
              style={{
                padding: '6px 12px',
                fontSize: '12px',
                borderRadius: '6px',
                border: 'none',
                background: activeTab === 'json' ? 'var(--accent-gold)' : 'rgba(255,255,255,0.05)',
                color: activeTab === 'json' ? '#0f0f1a' : '#c9d1d9',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              <Code size={13} style={{ display: 'inline', marginRight: '4px' }} /> JSON Verisi
            </button>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              onClick={handleCopy}
              className="btn btn-secondary"
              style={{
                padding: '6px 14px',
                fontSize: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                border: '1px solid var(--accent-gold)',
                color: '#ffd700'
              }}
            >
              {copied ? <Check size={14} style={{ color: '#3fb950' }} /> : <Copy size={14} />}
              {copied ? 'Kopyalandı!' : 'Panoya Kopyala'}
            </button>

            <button
              type="button"
              onClick={handleDownloadJson}
              className="btn btn-primary"
              style={{
                padding: '6px 14px',
                fontSize: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Download size={14} /> .json İndir
            </button>
          </div>
        </div>

        {/* Content Box */}
        <div style={{ padding: '16px 20px', flex: 1, overflowY: 'auto' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#ffd700' }}>Statblock derleniyor...</div>
          ) : (
            <pre style={{
              background: '#07070f',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '8px',
              padding: '16px',
              color: '#e6edf3',
              fontSize: '12px',
              lineHeight: '1.6',
              fontFamily: 'Consolas, "Courier New", monospace',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              margin: 0,
              maxHeight: '55vh',
              overflowY: 'auto'
            }}>
              {getActiveContent()}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
