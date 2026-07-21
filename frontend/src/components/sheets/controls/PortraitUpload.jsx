import React, { useState } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { useCharacterStore } from '../../../store/characterStore';

export default function PortraitUpload() {
  const { portrait, updateField } = useCharacterStore();
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState('');

  const processFile = (file) => {
    setError('');
    
    // Check if it's an image
    if (!file.type.startsWith('image/')) {
      setError('Lütfen geçerli bir görsel dosyası seçin (PNG, JPG, WEBP).');
      return;
    }

    // Max size 5MB
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('Görsel boyutu 5MB\'tan küçük olmalıdır.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target && e.target.result) {
        updateField('portrait', e.target.result);
      }
    };
    reader.onerror = () => {
      setError('Dosya okunurken bir hata oluştu.');
    };
    reader.readAsDataURL(file);
  };

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files && files[0]) {
      processFile(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      processFile(files[0]);
    }
  };

  const handleClear = () => {
    updateField('portrait', '');
    setError('');
  };

  return (
    <div className="form-group" style={{ marginBottom: '16px' }}>
      <label className="form-label">Karakter Portresi (Avatar)</label>
      
      {portrait ? (
        <div style={{
          position: 'relative',
          width: '120px',
          height: '120px',
          borderRadius: '10px',
          border: '2px solid var(--accent-gold)',
          overflow: 'hidden',
          boxShadow: '0 0 15px rgba(201, 168, 76, 0.2)',
          background: 'rgba(0,0,0,0.2)',
          margin: '8px 0',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          transition: 'all 0.3s ease'
        }}>
          <img 
            src={portrait} 
            alt="Portrait Preview" 
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover'
            }} 
          />
          <button
            onClick={handleClear}
            style={{
              position: 'absolute',
              top: '4px',
              right: '4px',
              background: '#e94560',
              border: 'none',
              borderRadius: '50%',
              width: '24px',
              height: '24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              color: 'white',
              boxShadow: '0 2px 5px rgba(0,0,0,0.3)',
              transition: 'transform 0.2s ease',
            }}
            title="Görseli kaldır"
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            <X size={14} />
          </button>
        </div>
      ) : (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          style={{
            border: `2px dashed ${isDragOver ? 'var(--accent-gold)' : 'rgba(255,255,255,0.15)'}`,
            borderRadius: '10px',
            padding: '20px 16px',
            textAlign: 'center',
            background: isDragOver ? 'rgba(201,168,76,0.05)' : 'rgba(255,255,255,0.01)',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '8px',
            margin: '8px 0'
          }}
          onClick={() => document.getElementById('portrait-file-input').click()}
        >
          <input
            id="portrait-file-input"
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <Upload size={24} style={{ color: isDragOver ? 'var(--accent-gold)' : 'var(--color-text-muted)' }} />
          <span style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
            Görsel sürükleyin veya <b>Gözatın</b>
          </span>
          <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
            PNG, JPG, WEBP veya GIF (Maks. 5MB)
          </span>
        </div>
      )}

      {error && (
        <div style={{ color: '#e94560', fontSize: '11px', marginTop: '4px', fontWeight: 'bold' }}>
          {error}
        </div>
      )}
    </div>
  );
}
