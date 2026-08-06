import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Sword, Sparkles, Activity, Lock, CheckCircle } from 'lucide-react';

const DEFAULT_SYSTEMS = [
  {
    key: 'pf1e',
    name: 'Pathfinder 1st Edition',
    dice_system: 'd20',
    description: 'Pathfinder 1st Edition Core ruleset, class-and-level modular progression (Aktif & Tam Destek).',
    is_active: true,
    badge: 'Aktif (Tam Destek)'
  },
  {
    key: 'dnd5e',
    name: 'D&D 5th Edition',
    dice_system: 'd20',
    description: 'Dungeons & Dragons 5e SRD ruleset (Donduruldu).',
    is_active: false,
    badge: 'Yakında Gelecek'
  },
  {
    key: 'mnm',
    name: 'Mutants & Masterminds 3e',
    dice_system: 'd20',
    description: 'Mutants & Masterminds 3rd Edition point-buy system (Donduruldu).',
    is_active: false,
    badge: 'Yakında Gelecek'
  }
];

export default function SystemSelector({ onSelect, onBack }) {
  const [systems, setSystems] = useState(DEFAULT_SYSTEMS);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get('/api/systems')
      .then(res => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setSystems(res.data);
        }
      })
      .catch(err => {
        console.warn('Backend systems endpoint unreachable, using offline fallback systems list:', err);
      });
  }, []);

  const getSystemIcon = (key) => {
    switch (key.toLowerCase()) {
      case 'dnd5e':
        return <Sword className="w-12 h-12 text-slate-500" />;
      case 'pf1e':
      case 'pathfinder1e':
        return <Activity className="w-12 h-12 text-amber-400" />;
      default:
        return <Sparkles className="w-12 h-12 text-slate-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center my-24">
        <div className="animate-fade-in text-xl text-amber-400 font-serif">Sistemler Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in max-w-4xl mx-auto my-8 px-4">
      <div className="text-center mb-10">
        <h2 className="text-4xl font-serif font-bold text-amber-300 mb-3 tracking-wide">Oyun Sistemi Seçin</h2>
        <p className="text-slate-400 text-lg">
          Şu anda platform <strong className="text-amber-400">Pathfinder 1st Edition (PF1e)</strong> kural motoruna tam destek sunmaktadır.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {systems.map(sys => {
          const isActive = sys.is_active !== false && sys.key === 'pf1e';
          return (
            <div 
              key={sys.key} 
              className={`glass-card system-card relative transition-all duration-300 p-6 flex flex-col justify-between rounded-xl border ${
                isActive 
                  ? 'border-amber-500/60 shadow-lg shadow-amber-500/10 cursor-pointer hover:border-amber-400 hover:shadow-amber-500/20' 
                  : 'border-slate-800 opacity-50 cursor-not-allowed'
              }`}
              onClick={() => isActive && onSelect(sys.key)}
            >
              <div className="absolute top-4 right-4">
                {isActive ? (
                  <span className="text-xs bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 px-2.5 py-1 rounded-full flex items-center gap-1 font-bold">
                    <CheckCircle size={12} /> Aktif
                  </span>
                ) : (
                  <span className="text-xs bg-slate-900 text-slate-400 border border-slate-700/50 px-2.5 py-1 rounded-full flex items-center gap-1 font-bold">
                    <Lock size={12} /> Yakında Gelecek
                  </span>
                )}
              </div>

              <div>
                <div className="mb-4">{getSystemIcon(sys.key)}</div>
                <h3 className={`sys-title text-2xl font-serif font-bold mb-3 ${isActive ? 'text-amber-200' : 'text-slate-500'}`}>
                  {sys.name}
                </h3>
                <p className={`text-sm leading-relaxed ${isActive ? 'text-amber-100/70' : 'text-slate-500'}`}>
                  {sys.description}
                </p>
              </div>

              <div className="mt-6 self-start">
                <span className="text-xs bg-slate-900/90 text-amber-200/80 px-2.5 py-1 rounded border border-amber-500/20 font-mono">
                  Zar: {sys.dice_system ? sys.dice_system.toUpperCase() : 'D20'}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="text-center">
        <button className="btn btn-secondary px-6 py-2.5 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-amber-300 transition-colors" onClick={onBack}>İptal Et</button>
      </div>
    </div>
  );
}

