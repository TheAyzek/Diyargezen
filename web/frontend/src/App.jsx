import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Sparkles, LogOut } from 'lucide-react';
import diyargezerLogo from './diyargezer_logo.png';
import Dashboard from './components/Dashboard';
import SystemSelector from './components/SystemSelector';
import PF1eSheet from './components/sheets/PF1eSheet';
import Auth from './components/Auth';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [username, setUsername] = useState(localStorage.getItem('username') || '');
  const [view, setView] = useState('dashboard'); // 'dashboard', 'select-system', 'edit-character'
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [selectedSystem, setSelectedSystem] = useState('pf1e');

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
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <header className="app-header">
          <div className="app-logo" style={{ display: 'flex', alignItems: 'center' }}>
            <img src={diyargezerLogo} alt="Diyargezen Logo" style={{ height: '32px', width: 'auto', marginRight: '10px' }} /> DİYARGEZEN
          </div>
          <div style={{ fontSize: '13px', color: '#8b949e', letterSpacing: '0.5px' }}>
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
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* App Header Bar */}
      <header className="app-header">
        <div className="app-logo" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }} onClick={() => setView('dashboard')}>
          <img src={diyargezerLogo} alt="Diyargezen Logo" style={{ height: '32px', width: 'auto', marginRight: '10px' }} /> DİYARGEZEN
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span style={{ fontSize: '13px', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            Gezgin: <b style={{ color: 'var(--accent-gold)' }}>{username}</b>
          </span>
          <button 
            className="btn btn-secondary" 
            onClick={handleLogout}
            style={{ 
              padding: '4px 8px', 
              fontSize: '11px', 
              minHeight: 'unset', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '4px',
              borderColor: 'rgba(233, 69, 96, 0.3)',
              color: 'var(--color-ruby)'
            }}
          >
            <LogOut size={12} /> Çıkış
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="main-content">
        {view === 'dashboard' && (
          <Dashboard 
            onSelectCharacter={handleSelectCharacter} 
            onNewCharacter={handleNewCharacter} 
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
