import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LogOut, BookOpen, User, FileText, Wifi, WifiOff } from 'lucide-react';
import diyargezerLogo from './diyargezer_logo.png';
import Dashboard from './components/Dashboard';
import SystemSelector from './components/SystemSelector';
import PF1eSheet from './components/sheets/PF1eSheet';
import Auth from './components/Auth';
import RulesCompendium from './components/RulesCompendium';
import { useCharacterStore } from './store/characterStore';
import { exportCharacterPDF } from './utils/pdfExportUtil';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [username, setUsername] = useState(localStorage.getItem('username') || '');
  const [view, setView] = useState('dashboard'); // 'dashboard', 'select-system', 'edit-character', 'rules-compendium'
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [selectedSystem, setSelectedSystem] = useState('pf1e');

  const { isOnline, syncStatus, setOnlineStatus } = useCharacterStore();

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
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  const handleLoginSuccess = (newToken, newUser) => {
    setToken(newToken);
    setUsername(newUser);
    setView('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setToken(null);
    setUsername('');
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

  if (!token) {
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
          <Auth onLoginSuccess={handleLoginSuccess} />
        </main>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--void)' }}>
      
      {/* High-Fantasy App Header Bar */}
      <header className="app-header" style={{ background: 'linear-gradient(180deg, rgba(10,8,20,0.99) 0%, rgba(7,6,15,0.97) 100%)', borderBottom: '1px solid rgba(201,168,76,0.25)', height: 58, padding: '0 24px' }}>
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
          <div style={{
            display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem',
            padding: '3px 10px', borderRadius: '12px',
            backgroundColor: isOnline ? 'rgba(78, 201, 176, 0.15)' : 'rgba(233, 69, 96, 0.15)',
            border: `1px solid ${isOnline ? '#4ec9b0' : '#e94560'}`,
            color: isOnline ? '#4ec9b0' : '#ff6b81', fontWeight: 600
          }}>
            {isOnline ? <Wifi size={13} color="#4ec9b0" /> : <WifiOff size={13} color="#e94560" />}
            <span>{isOnline ? '🟢 Senkronize' : '🟡 Çevrimdışı (Yerel Kayıt)'}</span>
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
        </div>

        <div className="header-border-bottom" />
      </header>

      {/* Main Container */}
      <main className="main-content" style={{ marginTop: '16px', marginBottom: '24px' }}>
        {view === 'dashboard' && (
          <Dashboard 
            onSelectCharacter={handleSelectCharacter} 
            onNewCharacter={handleNewCharacter} 
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
      </main>

    </div>
  );
}

