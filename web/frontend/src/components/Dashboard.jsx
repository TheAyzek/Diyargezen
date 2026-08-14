import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  UserPlus, Trash, ChevronRight, Search, Shield, Sword, Sparkles, 
  TrendingUp, Users, Award, BookOpen, Download, Copy, FileDown
} from 'lucide-react';
import PresetCharactersModal from './PresetCharactersModal';
import { 
  importCharacterJSONFile, 
  exportFullVaultBackup, 
  importFullVaultBackup,
  exportCharacterRecordJSON 
} from '../utils/jsonExportUtil';
import { 
  getAllLocalCharacters, 
  deleteLocalCharacter, 
  cloneLocalCharacter,
  saveLocalCharacter 
} from '../utils/offlineStorage';
import { useCharacterStore } from '../store/characterStore';

export default function Dashboard({ onSelectCharacter, onNewCharacter, onOpenAuth }) {
  const [characters, setCharacters] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [presetModalOpen, setPresetModalOpen] = useState(false);
  const fileInputRef = useRef(null);
  const { loadPresetCharacter, isOnline } = useCharacterStore();

  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username');
  const isLoggedIn = token && token !== 'offline-guest-token';

  const handleImportFile = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      importCharacterJSONFile(file, async (parsed) => {
        loadPresetCharacter(parsed);
        const record = {
          id: `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          name: parsed.name || 'İsimsiz Kahraman',
          system: (parsed.system || 'pf1e').toLowerCase(),
          data: parsed,
          is_dirty: true
        };
        await saveLocalCharacter(record, true);
        loadCharacters();
        onSelectCharacter({ ...parsed, system: 'pf1e' });
      });
    }
  };

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    setLoading(true);
    try {
      // 1. Fetch local characters from IndexedDB
      const localChars = await getAllLocalCharacters();
      let mergedMap = new Map();

      // Store local chars by ID/server_id
      localChars.forEach(c => {
        const key = c.server_id || c.id;
        mergedMap.set(String(key), {
          id: c.id,
          server_id: c.server_id,
          name: c.name || c.data?.name || 'İsimsiz Gezgin',
          system: c.system || c.data?.system || 'pf1e',
          data: c.data || c,
          created_at: c.created_at,
          updated_at: c.updated_at,
          isLocalOnly: !c.server_id
        });
      });

      // 2. If logged in and online, fetch server characters and merge
      if (isLoggedIn) {
        try {
          const res = await axios.get('/api/characters');
          if (Array.isArray(res.data)) {
            res.data.forEach(srvChar => {
              const key = String(srvChar.id);
              const existing = mergedMap.get(key);
              mergedMap.set(key, {
                id: existing?.id || srvChar.id,
                server_id: srvChar.id,
                name: srvChar.name,
                system: srvChar.system,
                data: srvChar.data || srvChar,
                created_at: srvChar.created_at,
                updated_at: srvChar.updated_at,
                isLocalOnly: false
              });
            });
          }
        } catch (serverErr) {
          console.warn('Server fetch skipped or offline, using local vault:', serverErr);
        }
      }

      setCharacters(Array.from(mergedMap.values()));
    } catch (err) {
      console.error('Error loading vault characters:', err);
      setCharacters([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (char, e) => {
    e.stopPropagation();
    if (!window.confirm(`"${char.name}" karakterini mahzenden silmek istediğinizden emin misiniz?`)) {
      return;
    }

    try {
      // Delete from server if server_id exists and user is logged in
      if (char.server_id && isLoggedIn) {
        try {
          await axios.delete(`/api/characters/${char.server_id}`);
        } catch (err) {
          console.warn('Could not delete from server:', err);
        }
      }

      // Always delete from local IndexedDB
      await deleteLocalCharacter(char.id);
      loadCharacters();
    } catch (err) {
      console.error('Error deleting character:', err);
      alert('Karakter silinirken hata oluştu.');
    }
  };

  const handleClone = async (char, e) => {
    e.stopPropagation();
    try {
      const cloned = await cloneLocalCharacter(char.id);
      alert(`✨ "${char.name}" başarıyla klonlandı! Yeni kopya mahzene eklendi.`);
      loadCharacters();
    } catch (err) {
      // Fallback clone by re-saving data
      try {
        const rawData = char.data || char;
        const newRecord = {
          id: `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          name: `${char.name} (Kopya)`,
          system: char.system || 'pf1e',
          data: { ...rawData, name: `${char.name} (Kopya)` },
          is_dirty: true
        };
        await saveLocalCharacter(newRecord, true);
        alert(`✨ "${char.name}" başarıyla klonlandı!`);
        loadCharacters();
      } catch (cloneErr) {
        console.error('Error cloning character:', cloneErr);
        alert('Klonlama sırasında bir hata oluştu.');
      }
    }
  };

  const handleExportSingle = (char, e) => {
    e.stopPropagation();
    exportCharacterRecordJSON(char);
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
            onClick={() => exportFullVaultBackup()}
            style={{
              backgroundColor: 'rgba(124, 110, 247, 0.15)', border: '1px solid #7c6ef7',
              color: '#a594ff', fontSize: '0.85rem', fontWeight: 700,
              display: 'flex', alignItems: 'center', gap: '6px'
            }}
            title="Tüm karakterlerinizi tek tıkla şifreli/şemalı JSON dosyası olarak yedekleyin"
          >
            <Download size={16} /> 📦 Mahzeni Yedekle
          </button>

          <button
            className="btn"
            onClick={() => fileInputRef.current?.click()}
            style={{
              backgroundColor: 'rgba(78, 201, 176, 0.15)', border: '1px solid #4ec9b0',
              color: '#4ec9b0', fontSize: '0.85rem', fontWeight: 700,
              display: 'flex', alignItems: 'center', gap: '6px'
            }}
          >
            <Download size={16} /> 📥 Karakter / Mahzen Yükle
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
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <h3 style={{ fontSize: '1.2rem', color: '#f0e6d2', fontWeight: 'bold', margin: '0' }}>
                      {char.name}
                    </h3>
                    {char.isLocalOnly && (
                      <span style={{ fontSize: '10px', padding: '1px 6px', borderRadius: '4px', background: 'rgba(255,215,0,0.12)', color: '#ffd700', border: '1px solid rgba(255,215,0,0.3)', fontWeight: 'bold' }} title="Bu karakter yerel tarayıcı mahzeninde saklanmaktadır">
                        📦 Yerel
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '4px' }}>
                    {getSystemBadge(char.system)}
                    <span style={{ fontSize: '12px', color: '#8b949e' }}>
                      {char.data?.race || 'Irk Belirtilmedi'}
                      {(char.data?.class || char.data?.archetype) && ` • ${char.data?.class || char.data?.archetype}`}
                      {char.data?.level && ` • Seviye ${char.data?.level}`}
                    </span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button 
                  type="button"
                  className="btn btn-secondary" 
                  onClick={(e) => handleExportSingle(char, e)}
                  style={{ padding: '6px 10px', minHeight: 'unset', color: '#4ec9b0', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', background: 'rgba(78,201,176,0.1)', border: '1px solid rgba(78,201,176,0.25)' }}
                  title="Bu karakteri JSON dosyası olarak indir"
                >
                  <FileDown size={14} /> JSON
                </button>
                <button 
                  type="button"
                  className="btn btn-secondary" 
                  onClick={(e) => handleClone(char, e)}
                  style={{ padding: '6px 10px', minHeight: 'unset', color: '#a594ff', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', background: 'rgba(124,110,247,0.1)', border: '1px solid rgba(124,110,247,0.25)' }}
                  title="Karakteri klonla ve yeni bir slot oluştur"
                >
                  <Copy size={14} /> Klonla
                </button>
                <button 
                  type="button"
                  className="btn btn-secondary" 
                  onClick={(e) => handleDelete(char, e)}
                  style={{ padding: '6px 10px', minHeight: 'unset', color: '#e87070', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', background: 'rgba(233,69,96,0.1)', border: '1px solid rgba(233,69,96,0.25)' }}
                  title="Karakteri mahzenden sil"
                >
                  <Trash size={14} />
                </button>
                <ChevronRight size={18} style={{ color: '#8b949e', marginLeft: '4px' }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
