import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { UserPlus, Trash, ChevronRight, Search, Shield, Sword, Sparkles } from 'lucide-react';

export default function CharacterList({ onSelectCharacter, onNewCharacter }) {
  const [characters, setCharacters] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = () => {
    setLoading(true);
    axios.get('/api/characters')
      .then(res => {
        setCharacters(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching characters:', err);
        setLoading(false);
      });
  };

  const handleDelete = (id, e) => {
    e.stopPropagation();
    if (window.confirm('Bu karakteri silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.')) {
      axios.delete(`/api/characters/${id}`)
        .then(() => {
          loadCharacters();
        })
        .catch(err => {
          console.error('Error deleting character:', err);
        });
    }
  };

  const getSystemBadge = (system) => {
    const sys = system.toLowerCase();
    let label = system;
    let bgColor = 'rgba(255, 255, 255, 0.05)';
    let border = '1px solid rgba(255, 255, 255, 0.1)';
    let textColor = '#f0e6d2';

    if (sys.includes('dnd') || sys.includes('dragon')) {
      label = 'D&D 5e';
      bgColor = 'rgba(233, 69, 96, 0.15)';
      border = '1px solid rgba(233, 69, 96, 0.3)';
      textColor = '#e94560';
    } else if (sys.includes('pf') || sys.includes('pathfinder')) {
      label = 'PF1e';
      bgColor = 'rgba(63, 185, 80, 0.15)';
      border = '1px solid rgba(63, 185, 80, 0.3)';
      textColor = '#3fb950';
    } else if (sys.includes('mm') || sys.includes('mastermind')) {
      label = 'M&M 3e';
      bgColor = 'rgba(201, 168, 76, 0.15)';
      border = '1px solid rgba(201, 168, 76, 0.3)';
      textColor = '#c9a84c';
    }

    return (
      <span style={{ 
        display: 'inline-block', 
        padding: '3px 8px', 
        borderRadius: '6px', 
        fontSize: '11px', 
        fontWeight: 'bold', 
        backgroundColor: bgColor, 
        border: border, 
        color: textColor 
      }}>
        {label}
      </span>
    );
  };

  const filteredCharacters = characters.filter(char => 
    char.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    char.system.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="animate-fade-in" style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '2rem' }}>Karakterlerim</h2>
          <p style={{ color: '#8b949e', fontSize: '0.95rem' }}>Diyarlar arası gezginlerinizin listesi.</p>
        </div>
        <button className="btn btn-primary" onClick={onNewCharacter}>
          <UserPlus size={16} /> Yeni Karakter Oluştur
        </button>
      </div>

      {/* Search Input */}
      <div className="glass-card" style={{ padding: '12px 20px', display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px', borderRadius: '8px' }}>
        <Search size={18} style={{ color: '#8b949e' }} />
        <input 
          type="text" 
          placeholder="Karakter adı veya sistem ara..." 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ background: 'transparent', border: 'none', color: '#f0e6d2', width: '100%', outline: 'none', fontSize: '15px' }}
        />
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', margin: '50px 0' }}>
          <div style={{ color: '#c9a84c' }}>Yükleniyor...</div>
        </div>
      ) : filteredCharacters.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '60px 20px', borderRadius: '12px' }}>
          <p style={{ color: '#d4c5a9', fontSize: '1.1rem', marginBottom: '20px' }}>
            {searchQuery ? 'Aramanızla eşleşen karakter bulunamadı.' : 'Henüz hiç karakter oluşturmamışsınız.'}
          </p>
          {!searchQuery && (
            <button className="btn btn-primary" onClick={onNewCharacter}>
              İlk Karakterini Yarat
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {filteredCharacters.map(char => {
            const charData = char.data || char.character_data || char;
            const portrait = charData.portrait || charData.avatar || charData.portrait_url || charData.image || char.portrait || char.avatar;

            return (
              <div 
                key={char.id} 
                className="glass-card hover-glow" 
                onClick={() => onSelectCharacter(char)}
                style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  padding: '14px 20px', 
                  borderRadius: '10px', 
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  border: '1px solid rgba(201,168,76,0.2)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  {portrait ? (
                    <div style={{ 
                      width: '52px', 
                      height: '52px', 
                      borderRadius: '10px', 
                      overflow: 'hidden',
                      border: '2px solid var(--gold-bright)', 
                      boxShadow: '0 0 12px rgba(201,168,76,0.3)',
                      flexShrink: 0,
                      background: '#0a0814'
                    }}>
                      <img 
                        src={portrait} 
                        alt={char.name} 
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                      />
                    </div>
                  ) : (
                    <div style={{ 
                      width: '52px', 
                      height: '52px', 
                      borderRadius: '10px', 
                      backgroundColor: '#1b172c', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      border: '1px solid rgba(201,168,76,0.3)',
                      boxShadow: '0 0 8px rgba(0,0,0,0.4)',
                      flexShrink: 0
                    }}>
                      {char.system.toLowerCase().includes('dnd') ? <Sword size={22} style={{ color: '#e94560' }} /> :
                       char.system.toLowerCase().includes('pf') ? <Shield size={22} style={{ color: '#3fb950' }} /> :
                       <Sparkles size={22} style={{ color: '#c9a84c' }} />}
                    </div>
                  )}

                  <div>
                    <h3 style={{ fontSize: '1.2rem', color: 'var(--gold-light)', fontFamily: 'Cinzel, serif', fontWeight: 'bold', marginBottom: '4px' }}>
                      {char.name}
                    </h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                      {getSystemBadge(char.system)}
                      <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                        {charData.race || 'Irk Belirtilmedi'} 
                        {charData.class && ` • ${charData.class}`}
                        {charData.archetype && ` (${charData.archetype})`}
                        {charData.level && ` • Seviye ${charData.level}`}
                      </span>
                    </div>
                  </div>
                </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <button 
                  className="btn btn-secondary" 
                  onClick={(e) => handleDelete(char.id, e)}
                  style={{ padding: '6px 12px', minHeight: 'unset', borderColor: 'transparent', color: '#8b949e' }}
                  onMouseOver={(e) => e.target.style.color = '#e94560'}
                  onMouseOut={(e) => e.target.style.color = '#8b949e'}
                >
                  <Trash size={15} />
                </button>
                <ChevronRight size={20} style={{ color: '#8b949e' }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
