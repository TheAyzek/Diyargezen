import React, { useState } from 'react';
import axios from 'axios';
import { X, Coins, Sparkles, Plus, Trash2, Users, Shield, Check, DollarSign } from 'lucide-react';

export default function PartyLootModal({ character, onClose }) {
  const [coins, setCoins] = useState({ pp: 10, gp: 500, sp: 200, cp: 50 });
  const [gems, setGems] = useState([
    { name: 'Yakut (Ruby)', value_gp: 150, qty: 2 },
    { name: 'Zümrüt Heykelcik', value_gp: 300, qty: 1 }
  ]);
  const [items, setItems] = useState([
    { name: '+1 Longsword', value_gp: 2315, qty: 1, claimed_by: character?.name || '' },
    { name: 'Potion of Cure Moderate Wounds', value_gp: 300, qty: 2, claimed_by: '' }
  ]);
  const [members, setMembers] = useState([
    character?.name || 'Kahraman 1',
    'Büyücü',
    'Rahip',
    'Hırsız'
  ]);
  const [newMemberName, setNewMemberName] = useState('');
  const [includePartyFund, setIncludePartyFund] = useState(true);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCalculate = () => {
    setLoading(true);
    axios.post('/api/rules/split-party-loot', {
      coins,
      gems_art: gems,
      items,
      party_members: members,
      include_party_fund: includePartyFund
    })
      .then(res => {
        setResult(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error splitting loot:', err);
        setLoading(false);
      });
  };

  const addMember = () => {
    if (newMemberName.trim() && !members.includes(newMemberName.trim())) {
      setMembers([...members, newMemberName.trim()]);
      setNewMemberName('');
    }
  };

  const removeMember = (idx) => {
    setMembers(members.filter((_, i) => i !== idx));
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(5, 5, 10, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        background: '#0d0c18',
        border: '2px solid var(--accent-gold)',
        borderRadius: '12px',
        width: '100%',
        maxWidth: '850px',
        maxHeight: '90vh',
        boxShadow: '0 10px 40px rgba(0,0,0,0.8), 0 0 20px rgba(201,168,76,0.2)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Modal Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 22px',
          borderBottom: '1px solid rgba(201,168,76,0.3)',
          background: 'linear-gradient(90deg, rgba(201,168,76,0.15) 0%, transparent 100%)'
        }}>
          <div>
            <h3 style={{ margin: 0, color: 'var(--accent-gold)', fontSize: '1.25rem', fontFamily: 'Cinzel, serif', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Coins size={20} /> Parti Kasası & Hazine Paylaştırma
            </h3>
            <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#a594ff' }}>
              Sikke, mücevher ve ganimetleri üyeler ve ortak fon arasında adil paylaştırın
            </p>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Body */}
        <div style={{ padding: '20px', flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* 1. Coins Input Bar */}
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
            <h4 style={{ margin: '0 0 10px', fontSize: '13px', color: '#ffd700' }}>🪙 Sikke Havuzu (Coins)</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
              <div>
                <label style={{ fontSize: '11px', color: '#a594ff', display: 'block' }}>Platin (PP = 10 GP)</label>
                <input
                  type="number"
                  value={coins.pp}
                  onChange={(e) => setCoins({ ...coins, pp: parseInt(e.target.value) || 0 })}
                  className="input-field"
                  style={{ width: '100%', padding: '6px 8px', fontSize: '13px' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: '#ffd700', display: 'block' }}>Altın (GP)</label>
                <input
                  type="number"
                  value={coins.gp}
                  onChange={(e) => setCoins({ ...coins, gp: parseInt(e.target.value) || 0 })}
                  className="input-field"
                  style={{ width: '100%', padding: '6px 8px', fontSize: '13px' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: '#c9d1d9', display: 'block' }}>Gümüş (SP = 0.1 GP)</label>
                <input
                  type="number"
                  value={coins.sp}
                  onChange={(e) => setCoins({ ...coins, sp: parseInt(e.target.value) || 0 })}
                  className="input-field"
                  style={{ width: '100%', padding: '6px 8px', fontSize: '13px' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: '#e69d72', display: 'block' }}>Bakır (CP = 0.01 GP)</label>
                <input
                  type="number"
                  value={coins.cp}
                  onChange={(e) => setCoins({ ...coins, cp: parseInt(e.target.value) || 0 })}
                  className="input-field"
                  style={{ width: '100%', padding: '6px 8px', fontSize: '13px' }}
                />
              </div>
            </div>
          </div>

          {/* 2. Party Members & Party Fund Option */}
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <h4 style={{ margin: 0, fontSize: '13px', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Users size={14} /> Parti Üyeleri ({members.length} Kişi)
              </h4>
              <label style={{ fontSize: '12px', color: '#ffd700', display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={includePartyFund}
                  onChange={(e) => setIncludePartyFund(e.target.checked)}
                />
                🏦 Parti Ortak Fonu (1 Ekstra Pay)
              </label>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '10px' }}>
              {members.map((m, idx) => (
                <span
                  key={idx}
                  style={{
                    background: 'rgba(56,189,248,0.15)',
                    border: '1px solid rgba(56,189,248,0.3)',
                    color: '#38bdf8',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  {m}
                  {members.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeMember(idx)}
                      style={{ background: 'transparent', border: 'none', color: '#ff6b81', cursor: 'pointer', padding: 0 }}
                    >
                      <X size={12} />
                    </button>
                  )}
                </span>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '6px' }}>
              <input
                type="text"
                placeholder="Yeni üye ekle..."
                value={newMemberName}
                onChange={(e) => setNewMemberName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addMember()}
                className="input-field"
                style={{ flex: 1, padding: '4px 10px', fontSize: '12px' }}
              />
              <button
                type="button"
                onClick={addMember}
                className="btn btn-secondary"
                style={{ padding: '4px 12px', fontSize: '12px' }}
              >
                <Plus size={13} /> Ekle
              </button>
            </div>
          </div>

          {/* Action Trigger */}
          <button
            type="button"
            onClick={handleCalculate}
            className="btn btn-primary"
            style={{ padding: '10px', fontSize: '14px', fontWeight: 'bold' }}
          >
            ⚡ Hazineyi Paylaştır
          </button>

          {/* 3. Distribution Results */}
          {result && (
            <div style={{ background: 'rgba(212,175,55,0.08)', border: '1px solid rgba(212,175,55,0.3)', borderRadius: '8px', padding: '16px' }}>
              <h4 style={{ margin: '0 0 12px', color: '#ffd700', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={16} /> Paylaştırma Raporu
              </h4>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '14px' }}>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '8px 12px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>TOPLAM LİKİT HAZİNE</div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#ffd700' }}>{result.total_liquid_gp} GP</div>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '8px 12px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>KİŞİ BAŞINA DÜŞEN NAKİT</div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#3fb950' }}>{result.gp_per_member} GP</div>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '8px 12px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '10px', color: '#8b949e' }}>ORTAK KASA / FON</div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#38bdf8' }}>{result.party_fund_gp} GP</div>
                </div>
              </div>

              {/* Members shares list */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {result.member_shares.map((share, sIdx) => (
                  <div
                    key={sIdx}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      background: 'rgba(0,0,0,0.2)',
                      padding: '8px 12px',
                      borderRadius: '4px',
                      fontSize: '12px'
                    }}
                  >
                    <span style={{ fontWeight: 'bold', color: '#f0e6d2' }}>👤 {share.member_name}</span>
                    <span style={{ color: '#3fb950', fontWeight: 'bold' }}>+{share.cash_gp} GP</span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
