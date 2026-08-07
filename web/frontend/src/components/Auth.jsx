import React, { useState } from 'react';
import axios from 'axios';
import { Lock, User, UserPlus, LogIn, AlertCircle } from 'lucide-react';

export default function Auth({ onLoginSuccess, onGuestContinue }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username.trim() || !password.trim()) {
      setError('Lütfen tüm alanları doldurun.');
      return;
    }

    if (!isLogin && password !== confirmPassword) {
      setError('Şifreler eşleşmiyor. Lütfen şifrenizi tekrar kontrol edin.');
      return;
    }

    setLoading(true);

    try {
      if (isLogin) {
        const response = await axios.post('/api/auth/login-json', {
          username: username.trim(),
          password: password.trim()
        });

        const token = response.data.access_token;
        const uname = response.data.username || username;
        localStorage.setItem('token', token);
        localStorage.setItem('username', uname);
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        onLoginSuccess(token, uname);
      } else {
        const response = await axios.post('/api/auth/register', {
          username: username.trim(),
          password: password.trim()
        });

        const token = response.data.access_token;
        const uname = response.data.username || username;
        localStorage.setItem('token', token);
        localStorage.setItem('username', uname);
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        onLoginSuccess(token, uname);
      }
    } catch (err) {
      console.error('Auth error detail:', err);
      if (!err.response) {
        setError(`Sunucuya bağlanılamadı. Lütfen internet bağlantınızı ve Render backend durumunu kontrol edin.`);
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          if (detail.includes('already registered') || detail.includes('zaten var')) {
            setError('Bu kullanıcı adı zaten alınmış. Lütfen farklı bir kullanıcı adı seçin.');
          } else if (detail.includes('Incorrect username or password')) {
            setError('Kullanıcı adı veya şifre hatalı!');
          } else {
            setError(detail);
          }
        } else if (Array.isArray(detail) && detail.length > 0) {
          setError(`Doğrulama Hatası: ${detail[0].msg || JSON.stringify(detail[0])}`);
        } else {
          setError(`Hata: ${JSON.stringify(detail)}`);
        }
      } else {
        setError(`Hata (${err.response.status}): İşlem gerçekleştirilemedi.`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      maxWidth: '450px',
      margin: '60px auto',
      width: '100%',
      padding: '0 16px'
    }}>
      <div className="glass-card animate-fade-in" style={{
        padding: '40px',
        borderRadius: '16px',
        boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.6), 0 0 15px rgba(201, 168, 76, 0.1)',
        border: '1px solid rgba(201, 168, 76, 0.25)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <h1 style={{ 
            fontSize: '2.2rem', 
            marginBottom: '6px', 
            background: 'linear-gradient(135deg, #f0e6d2, var(--accent-gold))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontFamily: 'Cinzel, serif'
          }}>
            🎲 DİYARGEZEN
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '13px', margin: 0 }}>
            {isLogin ? 'Karakter Mahzeninize Giriş Yapın' : 'Yeni Bir Gezgin Üyeliği Oluşturun'}
          </p>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', background: 'rgba(10,8,20,0.6)', padding: '4px', borderRadius: '8px', border: '1px solid rgba(201,168,76,0.2)' }}>
          <button
            type="button"
            onClick={() => { setIsLogin(true); setError(''); }}
            style={{
              flex: 1,
              padding: '10px',
              borderRadius: '6px',
              fontFamily: 'Cinzel, serif',
              fontSize: '0.82rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              background: isLogin ? 'linear-gradient(180deg, rgba(201,168,76,0.25) 0%, rgba(130,95,25,0.3) 100%)' : 'transparent',
              border: isLogin ? '1px solid var(--gold-bright)' : '1px solid transparent',
              color: isLogin ? 'var(--gold-bright)' : 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            <LogIn size={15} /> Giriş Yap
          </button>
          <button
            type="button"
            onClick={() => { setIsLogin(false); setError(''); }}
            style={{
              flex: 1,
              padding: '10px',
              borderRadius: '6px',
              fontFamily: 'Cinzel, serif',
              fontSize: '0.82rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              background: !isLogin ? 'linear-gradient(180deg, rgba(78,201,176,0.25) 0%, rgba(30,100,90,0.3) 100%)' : 'transparent',
              border: !isLogin ? '1px solid #4ec9b0' : '1px solid transparent',
              color: !isLogin ? '#7ee787' : 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            <UserPlus size={15} /> Yeni Üyelik
          </button>
        </div>

        {error && (
          <div style={{
            background: 'rgba(233, 69, 96, 0.15)',
            border: '1px solid rgba(233, 69, 96, 0.3)',
            color: 'var(--color-ruby)',
            padding: '12px',
            borderRadius: '8px',
            marginBottom: '20px',
            fontSize: '13px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <User size={13} /> Kullanıcı Adı
            </label>
            <input
              type="text"
              className="form-input"
              placeholder="Gezgin adı"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Lock size={13} /> Şifre
            </label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete={isLogin ? "current-password" : "new-password"}
            />
          </div>

          {!isLogin && (
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Lock size={13} /> Şifre Tekrar
              </label>
              <input
                type="password"
                className="form-input"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                autoComplete="new-password"
              />
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', marginTop: '10px', minHeight: '45px' }}
            disabled={loading}
          >
            {loading ? 'Yükleniyor...' : isLogin ? (
              <>
                <LogIn size={16} /> Giriş Yap
              </>
            ) : (
              <>
                <UserPlus size={16} /> Kayıt Ol
              </>
            )}
          </button>
        </form>

        <div style={{ 
          marginTop: '25px', 
          textAlign: 'center', 
          fontSize: '13px', 
          color: 'var(--color-text-muted)',
          borderTop: '1px solid rgba(255, 255, 255, 0.05)',
          paddingTop: '20px'
        }}>
          {isLogin ? (
            <>
              Henüz bir hesabınız yok mu?{' '}
              <button 
                type="button" 
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  color: 'var(--accent-gold)', 
                  fontWeight: 'bold', 
                  cursor: 'pointer',
                  outline: 'none'
                }}
                onClick={() => {
                  setIsLogin(false);
                  setError('');
                }}
              >
                Kayıt Olun
              </button>
            </>
          ) : (
            <>
              Zaten bir hesabınız var mı?{' '}
              <button 
                type="button" 
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  color: 'var(--accent-gold)', 
                  fontWeight: 'bold', 
                  cursor: 'pointer',
                  outline: 'none'
                }}
                onClick={() => {
                  setIsLogin(true);
                  setError('');
                }}
              >
                Giriş Yapın
              </button>
            </>
          )}

          {onGuestContinue && (
            <div style={{
              marginTop: '20px',
              paddingTop: '16px',
              borderTop: '1px solid rgba(201, 168, 76, 0.15)',
              textAlign: 'center'
            }}>
              <button
                type="button"
                onClick={onGuestContinue}
                style={{
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(201, 168, 76, 0.35)',
                  borderRadius: '8px',
                  color: '#d4c5a9',
                  fontSize: '0.85rem',
                  padding: '10px 16px',
                  cursor: 'pointer',
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  fontWeight: 'bold',
                  transition: 'all 0.2s ease'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = 'rgba(201, 168, 76, 0.12)';
                  e.currentTarget.style.color = '#f0e6d2';
                  e.currentTarget.style.borderColor = 'rgba(201, 168, 76, 0.6)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
                  e.currentTarget.style.color = '#d4c5a9';
                  e.currentTarget.style.borderColor = 'rgba(201, 168, 76, 0.35)';
                }}
              >
                ✨ Üyeliksiz / Misafir Olarak Devam Et →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
