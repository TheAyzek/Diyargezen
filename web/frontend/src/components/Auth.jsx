import React, { useState } from 'react';
import axios from 'axios';
import { Lock, User, UserPlus, LogIn, AlertCircle } from 'lucide-react';

export default function Auth({ onLoginSuccess }) {
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
      setError('Şifreler uyuşmuyor.');
      return;
    }

    setLoading(true);

    try {
      if (isLogin) {
        // Login using form data (OAuth2PasswordRequestForm expects username/password as form-data or JSON depends on implementation)
        // Let's first try sending as json. In auth.py, we have:
        // @router.post("/token")
        // def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
        // OAuth2PasswordRequestForm expects application/x-www-form-urlencoded!
        // Wait, let's check auth.py to see if there is another endpoint or if token endpoint uses form-data.
        // Let's use urlencoded or form-data for /api/auth/token.
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await axios.post('/api/auth/token', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });

        const token = response.data.access_token;
        localStorage.setItem('token', token);
        localStorage.setItem('username', username);
        
        // Setup axios default authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        onLoginSuccess(token, username);
      } else {
        // Register endpoint
        await axios.post('/api/auth/register', {
          username,
          password
        });
        
        // After successful registration, auto-login
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await axios.post('/api/auth/token', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });

        const token = response.data.access_token;
        localStorage.setItem('token', token);
        localStorage.setItem('username', username);
        
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        onLoginSuccess(token, username);
      }
    } catch (err) {
      console.error('Auth error:', err);
      if (!err.response) {
        setError('Sunucuya bağlanılamadı. Lütfen backend sunucusunun (port 8000) çalıştığından ve aktif olduğundan emin olun.');
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          setError(detail === 'Username already registered.' ? 'Bu kullanıcı adı zaten alınmış. Lütfen farklı bir ad deneyin.' : detail);
        } else if (Array.isArray(detail) && detail.length > 0) {
          setError(detail[0].msg || 'Girdi doğrulaması başarısız oldu.');
        } else {
          setError(isLogin ? 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.' : 'Kayıt işlemi başarısız oldu.');
        }
      } else {
        setError(isLogin ? 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.' : 'Kayıt işlemi başarısız oldu.');
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
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{ 
            fontSize: '2.2rem', 
            marginBottom: '10px', 
            background: 'linear-gradient(135deg, #f0e6d2, var(--accent-gold))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            🎲 DİYARGEZEN
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>
            {isLogin ? 'Karakter Mahzenine Giriş Yapın' : 'Yeni Bir Gezgin Hesabı Oluşturun'}
          </p>
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
        </div>
      </div>
    </div>
  );
}
