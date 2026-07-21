import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, X } from 'lucide-react';

export default function EntitySelectorModal({ isOpen, onClose, system, category, title, onSelect }) {
  const [entities, setEntities] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadEntities();
    }
  }, [isOpen, category, system]);

  const loadEntities = () => {
    setLoading(true);
    // Map category plural/endpoint name
    let endpointCategory = category;
    if (category === 'equipment') endpointCategory = 'equipment';
    else if (category === 'feats') endpointCategory = 'feats';
    else if (category === 'races') endpointCategory = 'races';
    else if (category === 'classes') endpointCategory = 'classes';
    else if (category === 'spells') endpointCategory = 'spells';
    else if (category === 'powers') endpointCategory = 'powers';

    axios.get(`/api/rules/${system}/${endpointCategory}`, {
      params: { query: searchQuery }
    })
      .then(res => {
        setEntities(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching entities:', err);
        setLoading(false);
      });
  };

  // Trigger load on search query change (debounce is better, but this works for basic search)
  useEffect(() => {
    if (isOpen) {
      const delayDebounce = setTimeout(() => {
        loadEntities();
      }, 300);
      return () => clearTimeout(delayDebounce);
    }
  }, [searchQuery]);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(15, 15, 26, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div className="glass-card animate-fade-in" style={{
        width: '100%',
        maxWidth: '700px',
        maxHeight: '85vh',
        display: 'flex',
        flexDirection: 'column',
        padding: '24px',
        border: '1px solid rgba(201, 168, 76, 0.35)',
        boxShadow: '0 0 30px rgba(0, 0, 0, 0.8)'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ fontSize: '1.4rem', color: '#c9a84c' }}>{title}</h3>
          <button 
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
            onMouseOver={(e) => e.target.style.color = '#e94560'}
            onMouseOut={(e) => e.target.style.color = '#8b949e'}
          >
            <X size={24} />
          </button>
        </div>

        {/* Search Bar */}
        <div style={{ 
          background: 'rgba(34, 34, 59, 0.6)', 
          border: '1px solid rgba(255,255,255,0.1)', 
          borderRadius: '8px', 
          padding: '10px 14px', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '10px', 
          marginBottom: '20px' 
        }}>
          <Search size={18} style={{ color: '#8b949e' }} />
          <input 
            type="text" 
            placeholder={`${title} ara...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: '#f0e6d2', width: '100%', outline: 'none' }}
          />
        </div>

        {/* Entities List */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#c9a84c' }}>Aranıyor...</div>
          ) : entities.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#8b949e' }}>Sonuç bulunamadı.</div>
          ) : (
            entities.map((ent, idx) => (
              <div 
                key={idx}
                onClick={() => {
                  onSelect(ent);
                  onClose();
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.05)',
                  borderRadius: '8px',
                  padding: '14px 18px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = 'rgba(201, 168, 76, 0.05)';
                  e.currentTarget.style.borderColor = 'rgba(201, 168, 76, 0.3)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                }}
              >
                <div style={{ fontWeight: 'bold', color: '#f0e6d2', marginBottom: '6px', fontSize: '15px' }}>
                  {ent.isim}
                </div>
                {ent.aciklama && (
                  <div 
                    style={{ fontSize: '13px', color: '#8b949e', lineHeight: '1.4' }}
                    dangerouslySetInnerHTML={{ __html: ent.aciklama }}
                  />
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
