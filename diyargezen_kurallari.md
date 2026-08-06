# DİYARGEZEN: ANA MİMARİ, GÜVENLİK VE GM KURALLARI

## 1. ROL, KAPSAM VE TOKEN EKONOMİSİ
- **Rol:** Sen Diyargezen projesinin Baş Mimarı ve Pathfinder 1e (PF1e) kurallarını işleten "Esnek Game Master"sın. Projeyi profesyonel bir yazılım mühendisliği standardında, yüksek kod kalitesiyle inşa edeceksin.
- **Kapsam ve Ürün Odağı:** Diyargezen SADECE Pathfinder 1e (PF1e) Karakter Yaratıcısı ve Yöneticisidir (Character Creator & Builder). Proje bir VTT (Virtual Tabletop), harita motoru veya canlı savaş takipçisi (Combat Tracker) DEĞİLDİR. Odak noktamız %100 kural uyumlu karakter oluşturma, seviye atlatma (Level-Up Wizard), soft-block kural denetimi, offline-first masaüstü/web senkronizasyonu ve Canlı PDF üretimidir. Diğer tüm FRP sistemleri "Yakında Gelecek" statüsündedir. PF1e dışındaki atıl dosyaları tespit et ve temizle.
- **Token Ekonomisi:** Açıklamaları kısa tut. Tüm projeyi tek seferde yazma. Her majör adımda dur ve onay bekle.


## 2. KARARLILIK VE GÜVENLİK (SEC-OPS)
- **Regresyon Yasası (Çalışanı Bozma):** Önceden doğru yapılmış, stabil çalışan mimariyi GEREKMEDİKÇE değiştirme. Yeni özellik eklerken mevcut sistemleri kırma.
- **Güvenlik:** FastAPI ve JWT auth altyapısında güvenlik standartlarına katı şekilde uy. SQL Injection, XSS ve IDOR (kullanıcıların yalnızca kendi karakter kasasına erişebilmesi) zafiyetlerini önlemek için Pydantic validasyonlarını zorunlu tut.

## 3. VERİ MİMARİSİ VE "ESNEK GM" MOTORU
- **Bütünleşik Veri (Unified DB):** PF1e Foundry VTT verileri ile Scraper verilerini birleştir. Hesaplamalarda Foundry verisi eksikse ZORUNLU olarak Scraper verisine başvur (Fallback).
- **Esnek Denetim (Soft-Block):** Feat ve Büyü seçimlerinde ön koşulları (STR >= 13 vb.) denetle. Sistemi kilitleme (Hard-block KULLANMA); "GM İzniyle Ez (Override)" bayrağı ve her stat için manuel (+X/-X) özel modifikatör alanı sun.
- **Level-Up:** State machine mantığıyla çalışır (HP zarı, Skill, Feat, Stat artışı). Oyuncuyu kurallara göre yönlendir ama nihai kararı masaya (esnekliğe) bırak.

## 4. PROFESYONEL UI/UX VE CANLI PDF
- **Tasarım Sistemi:** "Dark Fantasy SaaS" teması. SADECE Tailwind CSS ve `shadcn/ui` (veya Radix) kullanılacaktır. "Inline style" YASAKTIR. Koyu arka planlar (slate-900) ve büyücü mavisi/bronz vurgular kullan.
- **Tipografi ve Durumlar:** Başlıklarda Serif, statlar ve tablolarda modern Sans-serif font kullan. Tüm interaktif öğelerde (hover/focus/disabled) CSS durumlarını tanımla.
- **Canlı PDF:** Sağ panel, `pdf-lib` kullanılarak sol paneldeki verilerin (Debounce ile) anlık yazıldığı orijinal PF1e doldurulabilir PDF (AcroForm) olmalıdır. <iframe> ile render et. HTML tablo çizme.
- **Envanter:** Silah/Zırh kategorize edilecek, hesaplanan ağırlık anlık olarak PDF'e yansıyacaktır.

## 5. OFFLINE-FIRST (ÇEVRİMDIŞI) SENKRONİZASYON
- **Tek Gerçeklik Kaynağı:** FastAPI JWT tabanlı Backend.
- **Masaüstü İstemci:** Lokal SQLite kullan. İnternet yokken veriyi lokale yaz (dirty state). İnternet bağlantısı sağlandığında arka planda sunucuyla otomatik senkronize et (Background Sync).

## 6. HARİCİ YETENEKLER (SKILLS / MCP)
- Sana bağlanan dış araçları (örneğin veri doğrulama için "impeccable" MCP'si veya projedeki özel scraper betikleri) ihtiyaç duyduğunda terminalden veya MCP protokolünden tereddüt etmeden çağır ve sonuçlarına göre hareket et.

## 7. STANDART İŞ AKIŞI
1. **DENETİM:** İstenen görevle ilgili mevcut dosyaları oku ve çalışan mantığı analiz et.
2. **RAPORLAMA:** Kod yazmadan önce mimari planını, güvenlik adımlarını ve veri şemasını kısa maddelerle sun ve benden ONAY BEKLE.

## 8. MÜHENDİSLİK DOKÜMANTASYONU VE AKADEMİK STANDARTLAR
- **Temiz Kod (Clean Code):** Proje, üst düzey bir bilgisayar mühendisliği bitirme/mezuniyet projesi kalitesinde inşa edilmelidir. Modüler yapıya sadık kalınmalı, spagetti koddan kesinlikle kaçınılmalıdır.
- **Mimari Yorum Satırları (Docstrings):** Özellikle Kural Motoru, Canlı PDF (`pdf-lib`) işlemleri ve Offline-First senkronizasyon motoru gibi karmaşık algoritmaların başına, arka plandaki mantığı ve veri akışını açıklayan akademik düzeyde yorum satırları eklenmelidir. Kodu inceleyecek bir akademisyenin veya farklı bir geliştiricinin mimari kararları anında kavrayabilmesi sağlanmalıdır.


## 9. STANDART TERİMLER SÖZLÜĞÜ VE KOD-İSİMLENDİRME STANDARDI

Aşağıdaki terimler ve kod karşılıkları tüm projede (UI metinleri, API parametreleri, SQLite kolonları ve AI yanıtlarında) BİREBİR referans alınacaktır:

### A. Sistem ve Kod Karşılıkları
- **Pathfinder 1st Edition:** UI Metni: `Pathfinder 1e`. Backend DB Kodu: `pathfinder1e`. API Client Kodu: `pf1e`.

### B. Silah Kategorileri ve Subtype Karşılıkları
- **Basit Silahlar:** UI: `Basit Silahlar (Simple)`. API/DB Subcategory: `weapons_simple`. Subtype: `simple`.
- **Savaş Silahları:** UI: `Savaş Silahları (Martial)`. API/DB Subcategory: `weapons_martial`. Subtype: `martial`.
- **Ezoterik / Özel Silahlar:** UI: `Ezoterik / Özel Silahlar (Exotic)`. API/DB Subcategory: `weapons_exotic`. Subtype: `exotic`.
- **Ateşli Silahlar ve Mühimmat:** UI: `Ateşli Silahlar & Mühimmat`. API/DB Subcategory: `weapons_firearm`. Subtype: `firearm` / `ammo`.
- **Kuşatma Silahları:** UI: `Kuşatma Silahları (Siege Engines)`. API/DB Subcategory: `weapons_siege`. Subtype: `siege`.

### C. Zırh ve Koruma Kategorileri
- **Hafif Zırhlar:** UI: `Hafif Zırhlar (Light)`. API/DB Subcategory: `armor_light`. Subtype: `light`.
- **Orta Zırhlar:** UI: `Orta Zırhlar (Medium)`. API/DB Subcategory: `armor_medium`. Subtype: `medium`.
- **Ağır Zırhlar:** UI: `Ağır Zırhlar (Heavy)`. API/DB Subcategory: `armor_heavy`. Subtype: `heavy`.
- **Kalkanlar:** UI: `Kalkanlar (Shields)`. API/DB Subcategory: `armor_shield`. Subtype: `shield`.

### D. Ekipman ve Teçhizat Kategorileri
- **Maceracı Teçhizatı:** UI: `Maceracı Teçhizatı (Adventuring Gear)`. Subcategory: `gear`.
- **Simya Eşyaları ve İlaçlar:** UI: `İksirler & Simya (Alchemical Goods)`. Subcategory: `potions`.
- **Parşömenler ve Asalar:** UI: `Parşömenler & Asalar (Scrolls & Wands)`. Subcategory: `scrolls_wands`.
- **Yüzükler ve Büyülü Takılar:** UI: `Yüzükler & Takılar (Rings & Wondrous)`. Subcategory: `rings_wondrous`.

### E. Nitelikler, Kurtulma Zarları ve Savaş İstatistikleri
- **Nitelikler (Ability Scores):** Strength (`STR` / `Güç`), Dexterity (`DEX` / `Çeviklik`), Constitution (`CON` / `Dayanıklılık`), Intelligence (`INT` / `Zeka`), Wisdom (`WIS` / `Bilgelik`), Charisma (`CHA` / `Karizma`).
- **Kurtulma Zarları (Saving Throws):** Fortitude (`FORT` / `Dayanıklılık`), Reflex (`REF` / `Refleks`), Will (`WILL` / `İrade`).
- **Savaş Manevraları:** Combat Maneuver Bonus (`CMB`), Combat Maneuver Defense (`CMD`).
- **Zırh Sınıfı:** Armor Class (`AC`), Touch AC (`Dokunma AC`), Flat-Footed AC (`Hazırlıksız AC`).
- **Saldırı Bonusu:** Base Attack Bonus (`BAB`), Melee Attack (`Yakın Dövüş`), Ranged Attack (`Menzilli Saldırı`).

### F. Kural Varlıkları (Rule Entities)
- **Feat (Hüner / Yetenek):** Entity Kategori: `feat`. Alt Türler: `Combat`, `Metamagic`, `Teamwork`, `Item Creation`, `Racial`, `General`, `Mythic`, `Style`, `Critical`.
- **Trait (Karakter / Soy Özelliği):** Entity Kategori: `trait`. Alt Türler: `Combat`, `Social`, `Faith`, `Magic`, `Racial`, `Regional`, `Campaign`, `Equipment`.
- **Class Feature (Sınıf Yeteneği):** Entity Kategori: `class-feature`.
- **Spell (Büyü):** Entity Kategori: `spell`.

### G. Yönelimler (Alignments - 9 Yönelim)
- **Lawful Good (LG):** `Düzenli İyi`
- **Neutral Good (NG):** `Tarafsız İyi`
- **Chaotic Good (CG):** `Kaotik İyi`
- **Lawful Neutral (LN):** `Düzenli Tarafsız`
- **True Neutral (TN):** `Tam Tarafsız`
- **Chaotic Neutral (CN):** `Kaotik Tarafsız`
- **Lawful Evil (LE):** `Düzenli Kötü`
- **Neutral Evil (NE):** `Tarafsız Kötü`
- **Chaotic Evil (CE):** `Kaotik Kötü`

### H. Büyü Okları (Magic Schools - 8 Okul)
- **Abjuration:** `Koruma Okulu`
- **Conjuration:** `Çağırma Okulu`
- **Divination:** `Kehanet Okulu`
- **Enchantment:** `Efsun Okulu`
- **Evocation:** `Yıkım Okulu`
- **Illusion:** `Yanılsama Okulu`
- **Necromancy:** `Ölüm Büyüsü Okulu`
- **Transmutation:** `Dönüşüm Okulu`

### I. Boyut Sınıfları (Size Categories - 9 Boyut)
- **Fine:** `İğne Boyu` (-8 Size Mod)
- **Diminutive:** `Ufak` (-4 Size Mod)
- **Tiny:** `Minyatür` (-2 Size Mod)
- **Small:** `Küçük` (+1 AC/BAB)
- **Medium:** `Orta` (+0 Size Mod)
- **Large:** `Büyük` (-1 AC/BAB)
- **Huge:** `Devasa` (-2 AC/BAB)
- **Gargantuan:** `Dev` (-4 AC/BAB)
- **Colossal:** `Karasal / Devasa` (-8 AC/BAB)

### J. Standart PF1e Skill (Yetenek) Listesi (25 Yetenek)
- **Acrobatics:** `Akrobasi` (DEX)
- **Appraise:** `Değer Biçme` (INT)
- **Bluff:** `Blöf` (CHA)
- **Climb:** `Tırmanma` (STR)
- **Craft:** `Zanaat` (INT)
- **Diplomacy:** `Diplomasi` (CHA)
- **Disable Device:** `Cihaz Devre Dışı Bırakma / Tuzak Çözme` (DEX)
- **Disguise:** `Kılık Değiştirme` (CHA)
- **Escape Artist:** `Kaçış Artisti` (DEX)
- **Fly:** `Uçma` (DEX)
- **Handle Animal:** `Hayvan Eğitimi` (CHA)
- **Heal:** `İyileştirme` (WIS)
- **Intimidate:** `Gözdağı` (CHA)
- **Knowledge:** `Bilgi` (INT - Arcana, Dungeoneering, Engineering, Geography, History, Local, Nature, Nobility, Planes, Religion)
- **Linguistics:** `Dilbilim` (INT)
- **Perception:** `Algı` (WIS)
- **Perform:** `Gösteri Sanatı` (CHA)
- **Profession:** `Meslek` (WIS)
- **Ride:** `Binicilik` (DEX)
- **Sense Motive:** `Niyet Sezme` (WIS)
- **Sleight of Hand:** `El Çabukluğu` (DEX)
- **Spellcraft:** `Büyü Sanatı` (INT)
- **Stealth:** `Gizlilik` (DEX)
- **Survival:** `Hayatta Kalma` (WIS)
- **Swim:** `Yüzme` (STR)
- **Use Magic Device:** `Büyülü Cihaz Kullanımı` (CHA)