import React, { useState, useEffect, useRef } from 'react';
import { captureSession, assertSession, isCurrentSession } from '../utils/sessionScope';
import { triggerSync } from '../utils/syncEngine';
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
  getSyncConflicts,
  resolveSyncConflict,
  saveLocalCharacter 
} from '../utils/offlineStorage';
import { useCharacterStore } from '../store/characterStore';
import { hasNativeStorage } from '../utils/nativeStorage';
import { getConflictArchives, restoreConflictArchive } from '../utils/offlineStorage';

export default function Dashboard({ onSelectCharacter, onNewCharacter, onOpenAuth }) {
  const [characters, setCharacters] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [archives, setArchives] = useState([]);
  const [storageError, setStorageError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [presetModalOpen, setPresetModalOpen] = useState(false);
  const fileInputRef = useRef(null);
  const { loadPresetCharacter, isOnline } = useCharacterStore();

  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username');
  const isLoggedIn = token && token !== 'offline-guest-token';

  const handleImportFile = async (e) => {
    const session = captureSession();
    const file = e.target.files?.[0];
    if (file) {
      try {
      const envelope = JSON.parse(await file.text());
      assertSession(session);
      if (Array.isArray(envelope.characters)) {
        await importFullVaultBackup(file, loadCharacters);
        return;
      }
      await importCharacterJSONFile(file, async (parsed) => {
        assertSession(session);
        loadPresetCharacter(parsed);
        const record = {
          id: `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          name: parsed.name || 'İsimsiz Kahraman',
          system: (parsed.system || 'pf1e').toLowerCase(),
          data: parsed,
          is_dirty: true
        };
        const saved = await saveLocalCharacter(record, true, session);
        assertSession(session);
        loadCharacters();
        onSelectCharacter(saved);
      });
      } catch (error) { if (isCurrentSession(session)) setStorageError(error.message); }
      finally { e.target.value = ''; }
    }
  };

  useEffect(() => {
    loadCharacters();
    const session = captureSession();
    const refresh = async () => {
      try {
        const [records, pending] = await Promise.all([getAllLocalCharacters(session), getSyncConflicts(session)]);
        if (isCurrentSession(session)) { setCharacters(records); setConflicts(pending); }
      } catch { /* Session changed; do not update the old view. */ }
    };
    window.addEventListener('diyargezen-sync-updated', refresh);
    return () => window.removeEventListener('diyargezen-sync-updated', refresh);
  }, []);

  const loadCharacters = async () => {
    const session = captureSession();
    setLoading(true);
    try {
      const local = await getAllLocalCharacters(session);
      if (!isCurrentSession(session)) return;
      setCharacters(local);
      await triggerSync(session.token);
      const updated = await getAllLocalCharacters(session);
      const pending = await getSyncConflicts(session);
      const recovered = await getConflictArchives(session);
      if (isCurrentSession(session)) { setCharacters(updated); setConflicts(pending); setArchives(recovered); setStorageError(''); }
    } catch (error) {
      if (isCurrentSession(session)) setStorageError(error.message);
    } finally {
      if (isCurrentSession(session)) setLoading(false);
    }
  };

  const resolveConflict = async (record, choice) => {
    const session = captureSession();
    if (!window.confirm(choice === 'local'
      ? 'Yerel sürüm sunucuya yeni bir işlem olarak gönderilecek. Sunucuda yeni değişiklik varsa tekrar çakışabilir. Devam edilsin mi?'
      : 'Sunucu sürümü kullanılacak. Yerel sürüm kurtarma arşivinde korunacak. Devam edilsin mi?')) return;
    try {
      await resolveSyncConflict(record.id, record.conflict.operation_id, record.local_revision, choice, session);
      if (isCurrentSession(session)) await loadCharacters();
    } catch (error) {
      if (isCurrentSession(session)) alert('Çözüm uygulanamadı; listeyi yenileyin. ' + error.message);
    }
  };

  const handleDelete = async (char, e) => {
    e.stopPropagation();
    const session = captureSession();
    if (!window.confirm(`"${char.name}" karakterini silmek istediğinizden emin misiniz?`)) return;
    try {
      await deleteLocalCharacter(char.id, session);
      await triggerSync(session.token);
      if (isCurrentSession(session)) loadCharacters();
    } catch (error) {
      if (isCurrentSession(session)) alert('Karakter silinemedi: ' + error.message);
    }
  };

  const handleClone = async (char, e) => {
    const session = captureSession();
    e.stopPropagation();
    try {
      const cloned = await cloneLocalCharacter(char.id, session);
      alert(`✨ "${char.name}" başarıyla klonlandı! Yeni kopya mahzene eklendi.`);
      loadCharacters();
    } catch (err) {
      if (!isCurrentSession(session)) return;
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
        await saveLocalCharacter(newRecord, true, session);
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
      <section className="journal-hero">
        <span className="eyebrow">Karakter mahzeni • Pathfinder 1e</span>
        <h1>Bir sonraki maceran burada.</h1>
        <p>Kahramanlarının hikâyesini kaldığın yerden sürdür ya da yeni bir efsanenin ilk sayfasını aç.</p>
        <button className="btn btn-primary" onClick={onNewCharacter}><UserPlus size={17} /> Yeni bir kahraman yarat</button>
      </section>
      {storageError && <p role="alert">Yerel depo açılamadı: {storageError} <button onClick={loadCharacters}>Tekrar dene</button></p>}
      {hasNativeStorage() && <p>
        Masaüstü kayıtları SQLite içinde tutulur. Önceki tarayıcı kayıtları silinmedi.
        <button onClick={() => exportFullVaultBackup({ browserStore: true })}>Önceki tarayıcı deposunu yedekle</button>
        {' '}İsterseniz yedeği inceleyip yeni kopyalar olarak içe aktarabilirsiniz.
      </p>}
      {archives.length > 0 && <details className="recovery-archive">
        <summary>Kurtarma arşivi ({archives.length})</summary>
        <p>Çakışma çözülmeden önce korunan yerel sürümler. Kurtarma yeni bir karakter oluşturur; mevcut kaydı değiştirmez.</p>
        {archives.map(archive => <div key={archive.key}>
          <span>{archive.value.name}</span>{' '}
          <button onClick={async () => {
            try { await restoreConflictArchive(archive.key); await loadCharacters(); }
            catch (error) { setStorageError(error.message); }
          }}>Yeni kopya olarak kurtar</button>
        </div>)}
      </details>}
      {conflicts.map(record => (
        <section key={record.id} style={{ border: '1px solid #d99b32', padding: 16, marginBottom: 16 }}>
          <h3>Senkronizasyon çakışması: {record.name}</h3>
          <p>Yerel değişiklik korunuyor; çözüm seçilene kadar gönderilmeyecek.</p>
          <details><summary>Yerel sürüm {record.is_deleted ? '(silme isteği)' : ''}</summary>
            <pre style={{ whiteSpace: 'pre-wrap', maxHeight: 240, overflow: 'auto' }}>{JSON.stringify({ name: record.name, data: record.data }, null, 2)}</pre>
          </details>
          <details><summary>Sunucu sürümü (revizyon {record.conflict.actual_revision})</summary>
            <pre style={{ whiteSpace: 'pre-wrap', maxHeight: 240, overflow: 'auto' }}>{JSON.stringify(record.conflict.server_character, null, 2)}</pre>
          </details>
          <button onClick={() => resolveConflict(record, 'local')}>Yerel sürümü gönder</button>
          <button onClick={() => resolveConflict(record, 'server')}>Sunucu sürümünü kullan</button>
        </section>
      ))}
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Eski sürümün ortak yerel deposu korunur ancak bu listeye otomatik aktarılmaz.
        Misafir kayıtları da hesaplardan ayrıdır. Elinizdeki JSON yedeğini içe aktararak bu hesaba kopyalayabilirsiniz.
      </p>
      
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
              Üye Hesabı: <b style={{ color: '#3fb950', fontFamily: 'Cinzel, serif' }}>{username}</b> — Bu hesabın karakterleri ayrı yerel depoda tutulur; bağlantı olduğunda senkronize edilir.
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
              <b>Misafir Modundasınız:</b> Kayıtlar yalnızca bu cihazın yerel deposundadır. Hesabınıza taşımak için mahzeni JSON olarak yedekleyip giriş sonrası içe aktarın.
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
            title="Karakterlerinizi JSON dosyası olarak yedekleyin. Dosya şifrelenmez; güvenli yerde saklayın."
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
