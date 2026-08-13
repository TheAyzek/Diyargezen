import React, { useState } from 'react';
import { X, BookOpen, Shield, Sword, Sparkles, CheckCircle2 } from 'lucide-react';
import { useCharacterStore } from '../store/characterStore';

export const PF1E_DEITIES = [
  {
    id: 'iomedae',
    name: 'Iomedae',
    title: 'The Inheritor (Mirasçı)',
    alignment: 'LG',
    portfolio: 'Adalet, Onur, Cesaret, Hükümranlık',
    favoredWeapon: 'Longsword (Uzun Kılıç)',
    domains: ['Glory', 'Good', 'Law', 'Sun', 'War'],
    symbol: '☀️ Qanlı Kılıç',
    description: 'Şövalyelerin, paladinlerin ve doğru adalet yolunda savaşanların koruyucusu.'
  },
  {
    id: 'sarenrae',
    name: 'Sarenrae',
    title: 'The Dawnflower (Şafak Çiçeği)',
    alignment: 'NG',
    portfolio: 'Şifa, Güneş, Bağışlanma, Dürüstlük',
    favoredWeapon: 'Scimitar (Pala)',
    domains: ['Fire', 'Good', 'Healing', 'Repos', 'Sun'],
    symbol: '🌅 Alevli Güneş',
    description: 'Merhamet ve şifa dağıtan, ancak kötülüğe karşı kılıcını çekmekten çekinmeyen tanrıça.'
  },
  {
    id: 'desna',
    name: 'Desna',
    title: 'Song of the Spheres (Kürelerin Şarkısı)',
    alignment: 'CG',
    portfolio: 'Düşler, Yıldızlar, Şans, Seyahat',
    favoredWeapon: 'Starknife (Yıldız Bıçağı)',
    domains: ['Chaos', 'Good', 'Liberation', 'Luck', 'Travel'],
    symbol: '🦋 Kelebek',
    description: 'Gezginlerin, şairlerin ve kelebek kanatlarındaki özgürlüğün koruyucusu.'
  },
  {
    id: 'cayden_cailean',
    name: 'Cayden Cailean',
    title: 'The Drunken Hero (Sarhoş Kahraman)',
    alignment: 'CG',
    portfolio: 'Özgürlük, Şarap, Cesaret, Macera',
    favoredWeapon: 'Rapier (Mekik Kılıç)',
    domains: ['Chaos', 'Charm', 'Good', 'Strength', 'Travel'],
    symbol: '🍺 Şarap Kupası',
    description: 'Bir iddia üzerine tanrılık sınavını geçen özgür ruhlu macera koruyucusu.'
  },
  {
    id: 'abadar',
    name: 'Abadar',
    title: 'Master of the First Vault (İlk Kasa Efendisi)',
    alignment: 'LN',
    portfolio: 'Şehirler, Zenginlik, Kanun, Ticaret',
    favoredWeapon: 'Light Crossbow (Hafif Arbalet)',
    domains: ['Earth', 'Law', 'Nobility, Protection', 'Travel'],
    symbol: '🗝️ Altın Anahtar',
    description: 'Medeniyetin, şehir düzeninin ve adil ticaretin koruyucusu.'
  },
  {
    id: 'torag',
    name: 'Torag',
    title: 'Father of Creation (Yaratılış Babası)',
    alignment: 'LG',
    portfolio: 'Demircilik, Koruma, Strateji',
    favoredWeapon: 'Warhammer (Savaş Çekici)',
    domains: ['Artifice', 'Earth', 'Good', 'Law', 'Protection'],
    symbol: '🔨 Çekiç ve Örs',
    description: 'Cücelerin ulu babası, demircilerin ve kırılmaz savunmanın ustası.'
  },
  {
    id: 'nethys',
    name: 'Nethys',
    title: 'The All-Seeing Eye (Her Şeyi Gören Göz)',
    alignment: 'TN',
    portfolio: 'Büyü, Bilgi, Tüm Büyülü Sanatlar',
    favoredWeapon: 'Quarterstaff (Asa)',
    domains: ['Destruction', 'Knowledge', 'Magic', 'Protection', 'Rune'],
    symbol: '👁️ Çift Renkli Yüz',
    description: 'Büyünün hem yıkıcı hem de koruyucu gücünü temsil eden bilge tanrı.'
  },
  {
    id: 'pharasma',
    name: 'Pharasma',
    title: 'Lady of Graves (Mezarlar Hanımefendisi)',
    alignment: 'TN',
    portfolio: 'Kader, Ölüm, Doğum, Kehanet',
    favoredWeapon: 'Dagger (Hançer)',
    domains: ['Death', 'Healing', 'Knowledge', 'Repose', 'Water'],
    symbol: '🌀 Spiralli Göz',
    description: 'Ruhların yargıcı, yaşam döngüsünün ve doğumun değişmez hakimi.'
  },
  {
    id: 'erastil',
    name: 'Erastil',
    title: 'Old Deadeye (Koca Göz)',
    alignment: 'LG',
    portfolio: 'Aile, Çiftçilik, Avcılık, Topluluk',
    favoredWeapon: 'Longbow (Uzun Yay)',
    domains: ['Animal', 'Community', 'Good', 'Law', 'Plant'],
    symbol: '🦌 Geyik Boynuzu',
    description: 'Köy yaşamının, ailenin ve doğayla uyumlu avcılığın koruyucusu.'
  },
  {
    id: 'gorum',
    name: 'Gorum',
    title: 'Our Lord in Iron (Demir Lordumuz)',
    alignment: 'CN',
    portfolio: 'Güç, Savaş, Muhafızlık, Çatışma',
    favoredWeapon: 'Greatsword (Çift El Kılıç)',
    domains: ['Chaos', 'Destruction', 'Glory', 'Strength', 'War'],
    symbol: '🛡️ Dikenli Kask',
    description: 'Sadece savaşın heyecanı ve zaferin onuru için kılıç sallayan demir zırhlı tanrı.'
  },
  {
    id: 'gozreh',
    name: 'Gozreh',
    title: 'The Wind and Waves (Rüzgar ve Dalgalar)',
    alignment: 'TN',
    portfolio: 'Doğa, Hava Durumu, Deniz',
    favoredWeapon: 'Trident (Üç Dişli Mızrak)',
    domains: ['Air', 'Animal', 'Plant', 'Water', 'Weather'],
    symbol: '🌊 Deniz Dalgası ve Yaprak',
    description: 'Okyanusların fırtınasını ve doğanın bakir dengesini temsil eden güç.'
  },
  {
    id: 'shelyn',
    name: 'Shelyn',
    title: 'Eternal Rose (Ebedi Gül)',
    alignment: 'NG',
    portfolio: 'Güzellik, Sanat, Aşk, Müzik',
    favoredWeapon: 'Glaive (Karakol Harbi)',
    domains: ['Air', 'Charm', 'Good', 'Luck', 'Protection'],
    symbol: '🌹 Kuşlu Gül',
    description: 'Sevginin, barışın ve tutkulu sanatın zarif koruyucusu.'
  },
  {
    id: 'asmodeus',
    name: 'Asmodeus',
    title: 'Prince of Darkness (Karanlık Prensi)',
    alignment: 'LE',
    portfolio: 'Zulüm, Gurur, Anlaşmalar, Cehennem',
    favoredWeapon: 'Heavy Mace (Ağır Topuz)',
    domains: ['Evil', 'Fire', 'Law', 'Magic', 'Trickery'],
    symbol: '⚖️ Beş Köşeli Yıldız Pentagram',
    description: 'Disiplinli mutlak düzeni ve bağlayıcı kanlı sözleşmeleri yöneten lord.'
  },
  {
    id: 'irori',
    name: 'Irori',
    title: 'Master of Masters (Ustalar Ustası)',
    alignment: 'LN',
    portfolio: 'Tarih, Bilgi, Öz-Mükemmellik',
    favoredWeapon: 'Unarmed Strike (Çıplak El)',
    domains: ['Healing', 'Knowledge', 'Law', 'Rune', 'Strength'],
    symbol: '✋ Mavi El',
    description: 'Zihinsel ve fiziksel disiplinle tanrılığa ulaşan keşişlerin rehberi.'
  }
];

export default function DeitySelectorModal({ isOpen, onClose }) {
  const { deity, updateField } = useCharacterStore();
  const [searchQuery, setSearchQuery] = useState('');

  if (!isOpen) return null;

  const filteredDeities = PF1E_DEITIES.filter(d => {
    const q = searchQuery.toLowerCase();
    return d.name.toLowerCase().includes(q) || d.portfolio.toLowerCase().includes(q) || d.alignment.toLowerCase().includes(q);
  });

  const handleSelect = (d) => {
    updateField('deity', d.name);
    onClose();
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      backgroundColor: 'rgba(7, 6, 15, 0.95)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem'
    }}>
      <div style={{
        backgroundColor: '#12101f', border: '1px solid var(--border-gold)', borderRadius: '14px',
        width: '100%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto',
        boxShadow: '0 20px 50px rgba(0,0,0,0.85)', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px'
      }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(201,168,76,0.2)', paddingBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(201,168,76,0.15)', border: '1px solid var(--gold-bright)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <BookOpen size={18} color="var(--gold-bright)" />
            </div>
            <div>
              <h3 style={{ margin: 0, fontFamily: 'Cinzel, serif', color: 'var(--gold-light)', fontSize: '1.2rem' }}>
                Pathfinder 1e Tanrı Kütüphanesi (Deities of Golarion)
              </h3>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Karakterinizin inancı, etki alanları (Domains) ve favori silahları
              </div>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem' }}>
            <X size={20} />
          </button>
        </div>

        {/* Search Input */}
        <input
          className="rune-input"
          placeholder="Tanrı ismi, etki alanı veya hizalama ara (örn: Sarenrae, Healing, LG)..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          style={{ padding: '8px 12px', fontSize: '0.85rem' }}
        />

        {/* Deities Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(230px, 1fr))', gap: '12px' }}>
          {filteredDeities.map(d => {
            const isSelected = deity === d.name;
            return (
              <div
                key={d.id}
                onClick={() => handleSelect(d)}
                style={{
                  backgroundColor: isSelected ? 'rgba(201,168,76,0.2)' : '#171526',
                  border: isSelected ? '2px solid var(--gold-bright)' : '1px solid rgba(201,168,76,0.25)',
                  borderRadius: '8px', padding: '12px', cursor: 'pointer', transition: 'all 0.2s ease',
                  display: 'flex', flexDirection: 'column', gap: '6px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.95rem', fontWeight: 'bold', color: 'var(--gold-bright)', fontFamily: 'Cinzel, serif' }}>
                    {d.symbol} {d.name}
                  </span>
                  <span style={{ fontSize: '0.68rem', padding: '2px 6px', borderRadius: '4px', background: 'rgba(124,110,247,0.2)', border: '1px solid #7c6ef7', color: '#c4beff', fontWeight: 'bold' }}>
                    {d.alignment}
                  </span>
                </div>

                <div style={{ fontSize: '0.72rem', fontStyle: 'italic', color: 'var(--gold-pale)' }}>
                  {d.title}
                </div>

                <div style={{ fontSize: '0.73rem', color: '#94a3b8' }}>
                  ⚔️ <b>Favori Silah:</b> {d.favoredWeapon}
                </div>

                <div style={{ fontSize: '0.72rem', color: '#e2e8f0', lineHeight: '1.3' }}>
                  {d.description}
                </div>

                {isSelected && (
                  <div style={{ fontSize: '0.7rem', color: '#4ade80', fontWeight: 'bold', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <CheckCircle2 size={13} /> Seçili Tanrı
                  </div>
                )}
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
