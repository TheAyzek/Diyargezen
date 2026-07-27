import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Sword, Sparkles, Activity, Lock, CheckCircle } from 'lucide-react';

export default function SystemSelector({ onSelect, onBack }) {
  const [systems, setSystems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/api/systems')
      .then(res => {
        setSystems(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching systems:', err);
        setLoading(false);
      });
  }, []);

  const getSystemIcon = (key) => {
    switch (key.toLowerCase()) {
      case 'dnd5e':
        return <Sword className="w-12 h-12" style={{ color: '#6c757d' }} />;
      case 'pf1e':
      case 'pathfinder1e':
        return <Activity className="w-12 h-12" style={{ color: '#c9a84c' }} />;
      default:
        return <Sparkles className="w-12 h-12" style={{ color: '#6c757d' }} />;
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', margin: '100px 0' }}>
        <div className="animate-fade-in" style={{ fontSize: '20px', color: '#c9a84c' }}>Sistemler Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h2 style={{ fontSize: '2.5rem', marginBottom: '12px' }}>Oyun Sistemi Seçin</h2>
        <p style={{ color: '#8b949e', fontSize: '1.1rem' }}>
          Şu anda platform **Pathfinder 1st Edition (PF1e)** kural motoruna tam destek sunmaktadır.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        {systems.map(sys => {
          const isActive = sys.is_active !== false && sys.key === 'pf1e';
          return (
            <div 
              key={sys.key} 
              className={`glass-card system-card ${!isActive ? 'disabled-card' : ''}`}
              onClick={() => isActive && onSelect(sys.key)}
              style={{ 
                transition: 'all 0.3s ease',
                opacity: isActive ? 1 : 0.5,
                cursor: isActive ? 'pointer' : 'not-allowed',
                position: 'relative',
                border: isActive ? '2px solid var(--accent-gold)' : '1px solid rgba(255,255,255,0.08)'
              }}
            >
              <div style={{ position: 'absolute', top: '16px', right: '16px' }}>
                {isActive ? (
                  <span style={{ fontSize: '11px', background: '#1b4332', color: '#52b788', padding: '4px 10px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 'bold' }}>
                    <CheckCircle size={12} /> Aktif
                  </span>
                ) : (
                  <span style={{ fontSize: '11px', background: '#343a40', color: '#adb5bd', padding: '4px 10px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 'bold' }}>
                    <Lock size={12} /> Yakında Gelecek
                  </span>
                )}
              </div>

              <div>
                <div style={{ marginBottom: '16px' }}>{getSystemIcon(sys.key)}</div>
                <h3 className="sys-title" style={{ fontSize: '1.5rem', marginBottom: '12px', color: isActive ? '#f0e6d2' : '#8b949e' }}>
                  {sys.name}
                </h3>
                <p style={{ color: isActive ? '#d4c5a9' : '#6c757d', fontSize: '0.95rem', lineHeight: '1.4' }}>
                  {sys.description}
                </p>
              </div>

              <div style={{ marginTop: '24px', alignSelf: 'flex-start' }}>
                <span style={{ fontSize: '12px', background: '#22223b', padding: '4px 8px', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  Zar: {sys.dice_system ? sys.dice_system.toUpperCase() : 'D20'}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ textAlign: 'center' }}>
        <button className="btn btn-secondary" onClick={onBack}>İptal Et</button>
      </div>
    </div>
  );
}
