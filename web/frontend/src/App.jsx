import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LogOut, BookOpen, User, FileText, Wifi, WifiOff, RefreshCw } from 'lucide-react';

import diyargezerLogo from './diyargezer_logo.png';
import Dashboard from './components/Dashboard';
import SystemSelector from './components/SystemSelector';
import PF1eSheet from './components/sheets/PF1eSheet';
import Auth from './components/Auth';
import RulesCompendium from './components/RulesCompendium';
import NotFound from './components/NotFound';
import { useCharacterStore } from './store/characterStore';
import { exportCharacterPDF } from './utils/pdfExportUtil';

export default function App() {
  const initialToken = localStorage.getItem('token');
  const initialGuest = localStorage.getItem('isGuest') === 'true';

  const [token, setToken] = useState(initialToken || (initialGuest ? 'offline-guest-token' : ''));
  const [username, setUsername] = useState(localStorage.getItem('username') || (initialGuest ? 'Yerel Gezgin' : ''));
  const [isGuest, setIsGuest] = useState(initialGuest);
  const [view, setView] = useState('dashboard'); // 'dashboard', 'select-system', 'edit-character', 'rules-compendium'
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [selectedSystem, setSelectedSystem] = useState('pf1e');

  const { isOnline, syncStatus, setOnlineStatus } = useCharacterStore();

  // Dynamic Page Title
  useEffect(() => {
    switch (view) {
      case 'dashboard':
        document.title = 'Diyargezen — Karakterlerim';
        break;
      case 'rules-compendium':
        document.title = 'Diyargezen — Kural Kütüphanesi (PF1e)';
        break;
      case 'select-system':
        document.title = 'Diyargezen — Sistem Seçimi';
        break;
      case 'edit-character':
        document.title = `Diyargezen — ${selectedCharacter?.name || 'Karakter Kağıdı'}`;
        break;
      case 'auth':
        document.title = 'Diyargezen — Giriş / Kayıt';
        break;
      default:
        document.title = 'Diyargezen — 404 Bulunamadı';
        break;
    }
  }, [view, selectedCharacter]);

  useEffect(() => {
    const handleOnline = () => setOnlineStatus(true);
    const handleOffline = () => setOnlineStatus(false);


    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [setOnlineStatus]);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      axios.defaults.headers.common['Authorization'] = `Bearer offline-guest-token`;
    }
  }, [token]);

  const handleLoginSuccess = (newToken, newUser) => {
    setToken(newToken);
    setUsername(newUser);
    setIsGuest(false);
    localStorage.setItem('token', newToken);
    localStorage.setItem('username', newUser);
    localStorage.removeItem('isGuest');
    setView('dashboard');
  };

  const handleGuestContinue = () => {
    setToken('offline-guest-token');
    setUsername('Yerel Gezgin');
    setIsGuest(true);
    localStorage.setItem('isGuest', 'true');
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setView('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('isGuest');
    setToken('');
    setUsername('');
    setIsGuest(false);
    setView('dashboard');
  };

  const handleSelectCharacter = (character) => {
    setSelectedCharacter(character);
    setSelectedSystem(character.system.toLowerCase());
    setView('edit-character');
  };

  const handleNewCharacter = () => {
    setView('select-system');
  };

  const handleSelectSystem = (systemKey) => {
    setSelectedSystem(systemKey.toLowerCase());
    setSelectedCharacter(null);
    setView('edit-character');
  };

  const handleSaveCharacter = (charPayload) => {
    if (selectedCharacter?.id) {
      // Update existing character
      axios.put(`/api/characters/${selectedCharacter.id}`, charPayload)
        .then(() => {
          setView('dashboard');
        })
        .catch(err => {
          console.error('Error saving character:', err);
          alert('Karakter kaydedilemedi!');
        });
    } else {
      // Create new character
      axios.post('/api/characters', charPayload)
        .then(() => {
          setView('dashboard');
        })
        .catch(err => {
          console.error('Error creating character:', err);
          alert('Karakter oluşturulamadı!');
        });
    }
  };

  const renderActiveSheet = () => {
    return (
      <PF1eSheet 
        character={selectedCharacter} 
        onSave={handleSaveCharacter} 
        onCancel={() => setView('dashboard')} 
      />
    );
  };

  if (!token && !isGuest) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--void)' }}>
        <header className="app-header" style={{ background: 'rgba(7,6,15,0.95)', borderBottom: '1px solid var(--border-gold)' }}>
          <div className="app-logo" style={{ display: 'flex', alignItems: 'center' }}>
            <img src={diyargezerLogo} alt="Diyargezen Logo" style={{ height: '34px', width: 'auto', marginRight: '10px' }} />
            <span className="shimmer-text" style={{ fontFamily: 'Cinzel Decorative, Cinzel, serif', letterSpacing: '0.1em' }}>DİYARGEZEN</span>
          </div>
          <div style={{ fontSize: '0.75rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-pale)', letterSpacing: '0.15em' }}>
            Pathfinder 1st Edition TTRPG Web Platform
          </div>
        </header>
        <main className="main-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
          <Auth onLoginSuccess={handleLoginSuccess} onGuestContinue={handleGuestContinue} />
        </main>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--void)' }}>
      
      {/* High-Fantasy App Header Bar */}
      <header className="app-header" style={{ background: 'linear-gradient(180deg, rgba(10,8,20,0.99) 0%, rgba(7,6,15,0.97) 100%)', borderBottom: '1px solid rgba(201,168,76,0.25)', minHeight: 58, height: 'auto', padding: '8px 16px', flexWrap: 'wrap', gap: '10px' }}>
        <div className="header-border-top" />
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div className="app-logo" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }} onClick={() => setView('dashboard')}>
            <img src={diyargezerLogo} alt="Diyargezen Logo" style={{ height: '34px', width: 'auto', marginRight: '10px' }} />
            <span className="shimmer-text" style={{ fontFamily: 'Cinzel Decorative, Cinzel, serif', letterSpacing: '0.1em' }}>DİYARGEZEN</span>
          </div>

          <nav style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => setView('dashboard')}
              style={{
                background: view === 'dashboard' ? 'rgba(201,168,76,0.15)' : 'transparent',
                border: view === 'dashboard' ? '1px solid var(--border-gold)' : '1px solid transparent',
                color: view === 'dashboard' ? 'var(--gold-bright)' : 'var(--text-muted)',
                fontFamily: 'Cinzel, serif',
                fontSize: '0.75rem',
                padding: '5px 12px',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <User size={13} /> Karakterlerim
            </button>

            <button
              onClick={() => setView('rules-compendium')}
              style={{
                background: view === 'rules-compendium' ? 'rgba(201,168,76,0.15)' : 'transparent',
                border: view === 'rules-compendium' ? '1px solid var(--border-gold)' : '1px solid transparent',
                color: view === 'rules-compendium' ? 'var(--gold-bright)' : 'var(--text-muted)',
                fontFamily: 'Cinzel, serif',
                fontSize: '0.75rem',
                padding: '5px 12px',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <BookOpen size={13} /> Kural Kütüphanesi
            </button>
          </nav>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Sync Status Badge */}
          <div 
            title={isOnline ? 'Sunucu ve yerel veritabanı ile senkronize' : 'İnternet bağlantısı yok - Tüm değişiklikler yerel SQLite/IndexedDB kasanıza kaydediliyor'}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem',
              padding: '4px 10px', borderRadius: '12px', cursor: 'help',
              backgroundColor: isOnline ? (syncStatus === 'syncing' ? 'rgba(201, 168, 76, 0.15)' : 'rgba(78, 201, 176, 0.15)') : 'rgba(233, 69, 96, 0.15)',
              border: `1px solid ${isOnline ? (syncStatus === 'syncing' ? '#ffd700' : '#4ec9b0') : '#e94560'}`,
              color: isOnline ? (syncStatus === 'syncing' ? '#ffd700' : '#4ec9b0') : '#ff6b81', fontWeight: 600,
              transition: 'all 0.3s ease'
            }}
          >
            {isOnline ? (
              syncStatus === 'syncing' ? (
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <RefreshCw size={12} className="animate-spin" color="#ffd700" /> Senkronize Ediliyor...
                </span>
              ) : (
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <Wifi size={12} color="#4ec9b0" /> 🟢 Senkronize (Yerel + Bulut)
                </span>
              )
            ) : (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <WifiOff size={12} color="#e94560" /> 🟡 Çevrimdışı (Yerel Kasa Aktif)
              </span>
            )}
          </div>


          {/* Quick PDF Export when editing */}
          {view === 'edit-character' && (
            <button
              onClick={() => exportCharacterPDF(useCharacterStore.getState())}
              style={{
                padding: '4px 10px', backgroundColor: 'rgba(201,168,76,0.15)', border: '1px solid var(--border-gold)',
                borderRadius: '6px', color: 'var(--gold-bright)', fontSize: '0.72rem', fontWeight: 700,
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontFamily: 'Cinzel, serif'
              }}
            >
              <FileText size={13} /> 📄 PDF İndir
            </button>
          )}

          <div style={{ border: '1px solid var(--border-crimson)', borderRadius: 1, padding: '4px 12px', background: 'rgba(110,16,16,0.15)' }}>
            <span style={{ fontFamily: 'Cinzel, serif', fontSize: '0.55rem', letterSpacing: '0.14em', color: '#e87070', textTransform: 'uppercase' }}>Pathfinder 1e</span>
          </div>

          {(token && token !== 'offline-guest-token') ? (
            <>
              <span style={{ fontSize: '0.85rem', fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                Gezgin: <b className="shimmer-text">{username}</b>
              </span>
              <button 
                className="crimson-btn" 
                onClick={handleLogout}
                style={{ padding: '5px 10px', fontSize: '0.65rem' }}
              >
                <LogOut size={12} /> Çıkış
              </button>
            </>
          ) : (
            <button
              onClick={() => setView('auth')}
              style={{
                padding: '5px 14px',
                background: 'linear-gradient(135deg, rgba(201,168,76,0.3) 0%, rgba(130,95,25,0.4) 100%)',
                border: '1px solid var(--gold-bright)',
                borderRadius: '6px',
                color: 'var(--gold-bright)',
                fontSize: '0.75rem',
                fontFamily: 'Cinzel, serif',
                fontWeight: 'bold',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 0 10px rgba(201,168,76,0.2)'
              }}
            >
              🔐 Giriş Yap / Kayıt Ol
            </button>
          )}
        </div>

        <div className="header-border-bottom" />
      </header>

      {/* Main Container */}
      <main className="main-content" style={{ marginTop: '16px', marginBottom: '24px' }}>
        {view === 'auth' && (
          <Auth onLoginSuccess={handleLoginSuccess} />
        )}

        {view === 'dashboard' && (
          <Dashboard 
            onSelectCharacter={handleSelectCharacter} 
            onNewCharacter={handleNewCharacter} 
            onOpenAuth={() => setView('auth')}
          />
        )}

        {view === 'rules-compendium' && (
          <RulesCompendium 
            onBack={() => setView('dashboard')} 
          />
        )}
        
        {view === 'select-system' && (
          <SystemSelector 
            onSelect={handleSelectSystem} 
            onBack={() => setView('dashboard')} 
          />
        )}

        {view === 'edit-character' && renderActiveSheet()}

        {!['auth', 'dashboard', 'rules-compendium', 'select-system', 'edit-character'].includes(view) && (
          <NotFound onGoHome={() => setView('dashboard')} />
        )}
      </main>

    </div>
  );
}


