import React from 'react';
import { Wifi, WifiOff, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { useCharacterStore } from '../store/characterStore';
import { triggerSync } from '../utils/syncEngine';

export default function SyncStatusBadge({ token }) {
  const isOnline = useCharacterStore((s) => s.isOnline);
  const syncStatus = useCharacterStore((s) => s.syncStatus);

  const handleManualSync = () => {
    if (token) {
      triggerSync(token);
    }
  };

  if (!isOnline) {
    return (
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: '16px',
          fontSize: '0.72rem',
          background: 'rgba(245, 158, 11, 0.15)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          color: '#fbbf24',
          fontFamily: 'Cinzel, serif',
          fontWeight: 600
        }}
        title="İnternet bağlantısı yok. Karakter değişiklikleriniz IndexedDB lokal kasasında saklanır ve çevrimiçi olduğunuzda otomatik eşleşir."
      >
        <WifiOff size={13} style={{ color: '#fbbf24' }} />
        Çevrimdışı (Lokal Kayıt)
      </div>
    );
  }

  if (syncStatus === 'syncing') {
    return (
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: '16px',
          fontSize: '0.72rem',
          background: 'rgba(168, 85, 247, 0.15)',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          color: '#c084fc',
          fontFamily: 'Cinzel, serif',
          fontWeight: 600
        }}
      >
        <RefreshCw size={13} className="animate-spin" style={{ color: '#c084fc' }} />
        Senkronize Ediliyor...
      </div>
    );
  }

  if (syncStatus === 'offline_pending') {
    return (
      <button
        onClick={handleManualSync}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: '16px',
          fontSize: '0.72rem',
          background: 'rgba(234, 179, 8, 0.15)',
          border: '1px solid rgba(234, 179, 8, 0.4)',
          color: '#facc15',
          fontFamily: 'Cinzel, serif',
          fontWeight: 600,
          cursor: 'pointer'
        }}
        title="Tıklayarak arka plan senkronizasyonunu başlatın"
      >
        <AlertCircle size={13} style={{ color: '#facc15' }} />
        Eşleşme Bekliyor (Şimdi Senkronize Et)
      </button>
    );
  }

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 10px',
        borderRadius: '16px',
        fontSize: '0.72rem',
        background: 'rgba(34, 197, 94, 0.12)',
        border: '1px solid rgba(34, 197, 94, 0.3)',
        color: '#4ade80',
        fontFamily: 'Cinzel, serif',
        fontWeight: 600
      }}
      title="Tüm verileriniz bulut sunucusu ile senkronize durumda."
    >
      <CheckCircle2 size={13} style={{ color: '#4ade80' }} />
      Senkronize
    </div>
  );
}
