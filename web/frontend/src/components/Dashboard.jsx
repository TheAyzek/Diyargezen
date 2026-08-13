import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  UserPlus, Trash, ChevronRight, Search, Shield, Sword, Sparkles, 
  TrendingUp, Users, Award, BookOpen, Download
} from 'lucide-react';
import PresetCharactersModal from './PresetCharactersModal';
import { importCharacterJSONFile } from '../utils/jsonExportUtil';
import { useCharacterStore } from '../store/characterStore';

export default function Dashboard({ onSelectCharacter, onNewCharacter, onOpenAuth }) {
  const [characters, setCharacters] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [presetModalOpen, setPresetModalOpen] = useState(false);
  const fileInputRef = useRef(null);
  const { loadPresetCharacter } = useCharacterStore();

  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username');
  const isLoggedIn = token && token !== 'offline-guest-token';

  const handleImportFile = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      importCharacterJSONFile(file, (parsed) => {
        loadPresetCharacter(parsed);
        onSelectCharacter({ ...parsed, system: 'pf1e' });
      });
    }
  };

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = () => {
    setLoading(true);
    // Guest users (no valid JWT) can't fetch from server — show empty list
    if (!isLoggedIn) {
      setCharacters([]);
      setLoading(false);
      return;
    }
    axios.get('/api/characters')
      .then(res => {
        setCharacters(Array.isArray(res.data) ? res.data : []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching characters:', err);
        // On 401/403 (invalid or expired token), show empty list gracefully
        setCharacters([]);
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

  // Stats calculation
  const totalCount = characters.length;
  
  const systemCounts = characters.reduce((acc, char) => {
    const sys = char.system.toLowerCase();
    if (sys.includes('dnd') || sys.includes('dragon')) acc.dnd = (acc.dnd || 0) + 1;
    else if (sys.includes('pf') || sys.includes('pathfinder')) acc.pf = (acc.pf || 0) + 1;
    else acc.mnm = (acc.mnm || 0) + 1;
    return acc;
  }, { dnd: 0, pf: 0, mnm: 0 });

  const highestLevelChar = characters.reduce((max, char) => {
    const levelVal = char.data?.level || 1;
    if (!max || levelVal > (max.data?.level || 1)) return char;
    return max;
  }, null);

  return (
    <div className="animate-fade-in" style={{ maxWidth: '1000px', margin: '0 auto', paddingBottom: '40px' }}>
      
      {/* Member Account / Guest Status Banner */}
      {isLoggedIn ? (
        <div style={{
          padding: '12px 18px',
          marginBottom: '20px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, rgba(63,185,80,0.12) 0%, rgba(30,90,40,0.18) 100%)',
          border: '1px solid rgba(63,185,80,0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '10px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Shield size={20} style={{ color: '#3fb950' }} />
            <span style={{ fontSize: '0.88rem', color: '#f0e6d2' }}>
              Üye Hesabı: <b style={{ color: '#3fb950', fontFamily: 'Cinzel, serif' }}>{username}</b> — Tüm karakterleriniz şifrelenmiş üye alanınızda saklanıyor.
            </span>
          </div>
          <span style={{ fontSize: '0.75rem', padding: '3px 10px', borderRadius: '12px', background: 'rgba(63,185,80,0.2)', border: '1px solid rgba(63,185,80,0.4)', color: '#3fb950', fontWeight: 'bold' }}>
            🔒 Üye Kasanız Aktif
          </span>
        </div>
      ) : (
        <div style={{
          padding: '14px 18px',
          marginBottom: '20px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, rgba(201,168,76,0.12) 0%, rgba(130,95,25,0.18) 100%)',
          border: '1px solid rgba(201,168,76,0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sparkles size={20} style={{ color: 'var(--gold-bright)' }} />
            <span style={{ fontSize: '0.85rem', color: '#f0e6d2' }}>
              <b>Misafir Modundasınız:</b> Oluşturduğunuz karakterlerin üye hesabınıza kaydolması ve tüm cihazlarınızdan erişilmesi için ücretsiz üye olun!
            </span>
          </div>
          {onOpenAuth && (
            <button
              onClick={onOpenAuth}
              style={{
                padding: '6px 14px',
                borderRadius: '6px',
                background: 'linear-gradient(135deg, rgba(201,168,76,0.3) 0%, rgba(130,95,25,0.4) 100%)',
                border: '1px solid var(--gold-bright)',
                color: 'var(--gold-bright)',
                fontSize: '0.8rem',
                fontFamily: 'Cinzel, serif',
                fontWeight: 'bold',
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              🔐 Üye Ol / Giriş Yap
            </button>
          )}
        </div>
      )}

      {/* Title & Primary Action */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', margin: 0, fontWeight: '700', color: 'var(--accent-gold)' }}>
            Karakter Kataloğu
          </h1>
          <p style={{ color: '#8b949e', fontSize: '0.9rem', margin: '4px 0 0 0' }}>Diyarlar arası gezginlerinizin listesi.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <input
            type="file"
            accept=".json"
            ref={fileInputRef}
            onChange={handleImportFile}
            style={{ display: 'none' }}
          />

          <button
            className="btn"
            onClick={() => fileInputRef.current?.click()}
            style={{
              backgroundColor: 'rgba(78, 201, 176, 0.15)', border: '1px solid #4ec9b0',
              color: '#4ec9b0', fontSize: '0.85rem', fontWeight: 700,
              display: 'flex', alignItems: 'center', gap: '6px'
            }}
          >
            <Download size={16} /> 📥 Karakter Yükle (.json)
          </button>

          <button
            className="btn"
            onClick={() => setPresetModalOpen(true)}
            style={{
              backgroundColor: 'rgba(201,168,76,0.15)', border: '1px solid var(--border-gold)',
              color: 'var(--gold-bright)', fontSize: '0.85rem', fontWeight: 700,
              display: 'flex', alignItems: 'center', gap: '6px'
            }}
          >
            <Sparkles size={16} /> ✨ Hazır Şablon İle Başla
          </button>

          <button className="btn btn-primary" onClick={onNewCharacter}>
            <UserPlus size={16} /> Yeni Karakter Yarat
          </button>
        </div>
      </div>

      <PresetCharactersModal
        isOpen={presetModalOpen}
        onClose={() => setPresetModalOpen(false)}
        onSelectPreset={(preset) => {
          onSelectCharacter({ ...preset, system: 'pf1e' });
        }}
      />

      {/* Search Bar */}
      <div className="glass-card" style={{ padding: '10px 16px', display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <Search size={18} style={{ color: '#8b949e' }} />
        <input 
          type="text" 
          placeholder="Karakter adı veya sistem ara..." 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ background: 'transparent', border: 'none', color: '#f0e6d2', width: '100%', outline: 'none', fontSize: '15px' }}
        />
      </div>

      {/* Character List Grid */}
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', margin: '50px 0' }}>
          <div style={{ color: 'var(--accent-gold)' }}>Gezginler yükleniyor...</div>
        </div>
      ) : filteredCharacters.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '60px 20px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
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
          {filteredCharacters.map(char => (
            <div 
              key={char.id} 
              className="glass-card character-row" 
              onClick={() => onSelectCharacter(char)}
              style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                padding: '16px 24px', 
                borderRadius: '8px', 
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                border: '1px solid rgba(255,255,255,0.05)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                
                {/* Portrait or System Icon */}
                {(() => {
                  const charPortrait = char.data?.portrait || char.portrait;
                  return (
                    <div style={{ 
                      width: '46px', 
                      height: '46px', 
                      borderRadius: '8px', 
                      backgroundColor: '#161625', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      border: charPortrait ? '1.5px solid var(--accent-gold, #c9a84c)' : '1px solid rgba(255, 255, 255, 0.05)',
                      boxShadow: charPortrait ? '0 0 10px rgba(201,168,76,0.25)' : 'none',
                      overflow: 'hidden',
                      flexShrink: 0
                    }}>
                      {charPortrait ? (
                        <img 
                          src={charPortrait} 
                          alt={char.name} 
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                        />
                      ) : char.system.toLowerCase().includes('dnd') ? (
                        <Sword size={18} style={{ color: '#e94560' }} />
                      ) : char.system.toLowerCase().includes('pf') ? (
                        <Shield size={18} style={{ color: '#3fb950' }} />
                      ) : (
                        <Sparkles size={18} style={{ color: '#c9a84c' }} />
                      )}
                    </div>
                  );
                })()}

                <div>
                  <h3 style={{ fontSize: '1.2rem', color: '#f0e6d2', fontWeight: 'bold', margin: '0 0 4px 0' }}>
                    {char.name}
                  </h3>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {getSystemBadge(char.system)}
                    <span style={{ fontSize: '12px', color: '#8b949e' }}>
                      {char.data.race || 'Irk Belirtilmedi'}
                      {(char.data.class || char.data.archetype) && ` • ${char.data.class || char.data.archetype}`}
                      {char.data.level && ` • Seviye ${char.data.level}`}
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
