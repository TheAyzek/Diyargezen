# DİYARGEZEN — GÖREV LİSTESİ VE YOL HARİTASI (ROADMAP)

Bu dosya, Diyargezen projesinin mimari gelişimini, tamamlanan motorlarını ve sıradaki geliştirme hedeflerini kayıt altına alan **Ana Görev Çizelgesi**'dir.

> [!IMPORTANT]
> **TEMEL KAPSAM VE ÇALIŞMA KURALI:**
> - Diyargezen **SADECE bir Pathfinder 1e Karakter Yaratıcısı ve Yöneticisidir (Character Creator & Builder)**.
> - Canlı savaş takipçisi, zar günlüğü, VTT harita motoru veya oturum içi araçlar KAPSAM DIŞIDIR.
> - Tüm geliştirme maddeleri %100 karakter yaratımı, seviye atlatma, donanım hesaplama, kural denetimi ve karakter kağıdı / PDF çıktısına odaklıdır.
> - Her oturum başlangıcında bu dosyadaki ilk `[ ]` görevi işlenir ve tamamlandığında `[x]` olarak işaretlenir.

---

## 🚀 AKTİF GELİŞTİRME DÖNGÜSÜ (SIRADAKİ GÖREVLER)

- [x] **1. İki Silahla Dövüş & Çift El Karakter Saldırı Matrisi (Two-Weapon Fighting Builder - CRB p. 202)**
  - *Kapsam:* Karakter oluştururken çift silah kuşanan (Ranger, Rogue, Fighter) yapılar için birincil ve ikincil el silahlarının saldırı bonusları (-4/-8, hafif ikincil silah -2/-2, *Two-Weapon Fighting* feat'i ile -2/-2), ikincil el hasar çarpanı ($0.5\times\text{STR}$ vs *Double Slice* $1\times\text{STR}$) ve *Improved/Greater TWF* ek saldırı dizilimlerinin karakter kağıdına yazılması.

- [x] **2. Karakter Hizalanışı & Sınıf Kural Uyumluluğu Motoru (Alignment & Class Restrictions - CRB p. 166-167)**
  - *Kapsam:* Paladin (Zorunlu LG), Monk (Zorunlu Lawful: LG/LN/LE), Barbarian (Non-lawful), Druid (Zorunlu en az bir eksende Neutral: NG/LN/TN/CN/NE), Cleric (Seçilen tanrının hizalanışından en fazla 1 adım uzaklıkta olma kuralı: One-step rule). Uyumsuzluk durumunda soft-block kural uyarısı ve GM esneklik desteği.

- [ ] **3. Prestij Sınıfları & İleri Önkoşul Motoru (Prestige Classes Builder - CRB Chapter 11)**
  - *Kapsam:* Arcane Archer, Assassin, Dragon Disciple, Duelist, Eldritch Knight, Loremaster, Mystic Theurge, Pathfinder Chronicler, Shadowdancer vb. prestij sınıflarının BAB, Beceri (Skill Rank), Feat ve Büyü Seviyesi önkoşullarının karakter yaratımında denetlenmesi ve çoklu sınıf ilerlemesine entegrasyonu.

- [ ] **4. İlahiyat, Alan (Domains) & Oracle Gizemleri Seçim Motoru (Deities, Domains & Mysteries - CRB p. 40-48 & APG)**
  - *Kapsam:* Karakter yaratırken tapınılan tanrıya bağlı 2 Alan (Domain), bahşedilen alan güçleri (Domain Powers), her seviye için kazanılan alan büyüleri (Domain Spell Slots) ve Oracle sınıfları için Gizem (Mystery) / Vahiy (Revelation) yetenekleri seçicisi.

---

## 📜 GEÇMİŞ GELİŞTİRME DÖNGÜSÜ (TAMAMLANAN GÖREVLER)

- [x] **1. Silah Büyülü Nitelikleri & Elementel Hasar Motoru (CRB p. 468-472)**
- [x] **2. Zırh & Kalkan Özel Nitelikleri Motoru (CRB p. 463-466)**
- [x] **3. Resmi Paizo Statblock Üretici & JSON Yedekleme (Statblock Formatter & JSON Portability)**
- [x] **4. Parti Kasası & Hazine Paylaştırma Motoru (Party Loot & Treasure Splitter)**

---

## ✅ TAMAMLANAN TÜM SİSTEMLER VE KURAL MOTORLARI

- [x] **6 Temel Yetenek Skoru, Point Buy & Zar Analitik Motoru (CRB p. 15-16)**
- [x] **Irklar, Alt Irklar, Boyut, Duyu ve Irksal Özellikler**
- [x] **Hünerler (Feats) & Önkoşul Ağacı Doğrulama Motoru**
- [x] **Sınıflar, Arketipler, Çoklu Sınıf (Multiclassing) & Variant Multiclassing (VMC)**
- [x] **BAB, Saldırılar (Tekil/Tam/Güç Saldırısı), CMB, CMD & Savaş Manevraları Matrisi (CRB p. 198-201)**
- [x] **Can Puanı (HP), Zırh Sınıfı (AC, Touch, Flat-Footed), Kurtarma Zarları (Fort, Ref, Will)**
- [x] **Statü Etkileri & Durumsal Güçlendirmeler Motoru (Conditions & Situational Buffs Engine)**
- [x] **12 Vücut Slotu (Magic Item Body Slots) & Seviyeye Göre Servet (WBL) Takipçisi**
- [x] **Yük Sınırları, Zırh Ceza Puanı (ACP), Maksimum Dex Bonusu & Hız Cezaları**
- [x] **Büyü Döküm Motoru, Günlük Slotlar, Konsantrasyon, DC, Büyü Kitabı Yazma & Tomar Üretimi (CRB p. 219 & 550)**
- [x] **Favored Class Bonus (FCB) & Irksal Özel Tercih Motoru (CRB p. 31 & APG/ARG)**
- [x] **Diller & Dilbilimi Motoru (Languages & Linguistics Engine - CRB p. 65 & 100)**
- [x] **Yaş Kategorileri, Boy & Kilo Motoru (Age, Height & Weight - CRB p. 168-169)**
- [x] **Hayvan Yoldaşı & Familiar Derinleştirme Motoru**
- [x] **Karakter Kıyaslama & Snapshot Diff Modalı**
- [x] **Portre Stüdyosu & Avatar Yönetimi**
- [x] **Offline-First Masaüstü/Web Çift Yönlü Senkronizasyon & Kasa Yedekleme Motoru**
- [x] **Şık Karakter Paylaşım Kartı (Showcase Card & Canvas PNG Export)**
- [x] **Metamagic (Metabüyü) & Büyü Slotu Simülasyon Motoru (CRB p. 136 & Chapter 9)**
- [x] **Simya, İksir ve Eşya Üretim Motoru (Alchemy & Item Crafting - CRB Chapter 15 & APG)**
- [x] **Karakter Geçmişi & Hikaye Feat Motoru (Ultimate Campaign Background Generator)**
- [x] **Seviye Atlama Yol Haritası & İlerleme Planlayıcı (Progression Planner 1-20 - CRB Chapter 3 & 4)**
