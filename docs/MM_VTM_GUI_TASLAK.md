## MM & VtM GUI Taslak Planı

> Bu belge, `gui/app.py` içinde yer alan `MmPage` ve `VtmPage` sınıflarını fonksiyonel hale getirmek için önerilen UI/wizard taslaklarını, kullanılacak PySide6 bileşenlerini ve validasyon adımlarını içerir.

---

### 1. Mutants & Masterminds (MmPage)

#### 1.1 Genel Yapı
- `QStackedWidget` tabanlı akış (Ana menü → Karakter wizard → Özelleştirme sekmeleri)
- Üst kısımda başlık + Power Level seçimi, alt kısımda sekmeler
- Ortak buton çubuğu: `Yeni Karakter`, `Kaydet`, `Yükle`, `Özet`, `PDF (devre dışı)`

#### 1.2 Wizard Adımları
1. **Temel Bilgiler**
   - Bileşenler: `QLineEdit` (karakter adı, kod adı), `QComboBox` (Power Level), `QComboBox` (Arketip)
   - Arketip seçildiğinde `QTextEdit` içinde özet + öneriler gösterilir
   - Validasyon: isim boş olamaz, PL & arketip seçili olmalı

2. **Ability Scores**
   - 8 adet `QSpinBox` (Strength, Stamina, ... Presence)
   - PL limitlerini gösteren `QLabel` + progress bar (opsiyonel)
   - `QLabel` ile “Toplam Ability Cost: X / PP” izlensin
   - Validasyon: min=0, max=20; opsiyonel auto-calc (PL + 10 kuralı)

3. **Powers & Advantages**
   - Arketipten gelen önerileri `QListWidget` (sol) olarak göster, kullanıcı ekleyebilsin (sağ panel `QListWidget`)
   - `QPushButton` ile “Öneriyi ekle” / “Kaldır” akışı
   - Manuel giriş için `QLineEdit` + `QSpinBox` (rank) alanı
   - Validasyon: Toplam Power Points ≤ PL * 15 (varsayılan)

4. **Beceriler ve Savunmalar**
   - `QSpinBox` seti: Attack Bonus, Effect Rank, Defense, Toughness
   - Otomatik PL karşılaştırmaları; limit aşıldığında kırmızı uyarı
   - Opsiyonel skill tablosu (Name, Rank)

5. **Özet / Notlar**
   - `QTextEdit` (arka plan, notlar)
   - `QTextBrowser` (dinamik özet)
   - “Karakteri Oluştur” butonu → `_create_character_mm()`

#### 1.3 Metod Taslakları
- `_init_mm_ui()`: ana layout kurulum
- `_update_pl_limits()`: PL seçimi değişince limit label’ları güncelle
- `_calculate_mm_summary()`: ability, power ve defense özetlerini text’e dök
- `_validate_mm_character()`: zorunlu alan ve PL limit kontrolleri
- `_create_mm_character()`: JSON kaydı için dict döndür (`system: MUTANTS_AND_MASTERMINDS`)

---

### 2. Vampire: The Masquerade (VtmPage)

#### 2.1 Genel Yapı
- `QTabWidget` içinde 4 sekme:
  1. **Temel Bilgiler**
  2. **Attributes**
  3. **Skills & Disciplines**
  4. **Özet / Humanity**
- Üstte clan seçimi + bane gösterimi
- Alt buton çubuğu: `Yeni`, `Kaydet`, `Yükle`, `PDF (devre dışı)`

#### 2.2 Sekme Detayları
1. **Temel Bilgiler**
   - `QFormLayout`: Name, Player, Chronicle, Concept, Ambition, Desire, Clan
   - Clan seçilince bane (`QLabel`) ve default disiplinler (`QListWidget`) gösterilir

2. **Attributes**
   - 3 `QGroupBox` (Physical/Social/Mental)
   - Her grup için 3 `QSpinBox` (0-5)
   - Nokta dağıtım kuralları (ör. 4/3/3) için `QLabel` + counter

3. **Skills & Disciplines**
   - Skills: kategori bazlı `QTableWidget` (Skill, Rank) veya 3 combo + spin
   - Disciplines: clan default listesi + ekstra slotlar, `QComboBox` ile
   - Humanity, Willpower, Health otomatik hesabı için `QLabel`

4. **Özet**
   - `QTextBrowser` içinde:
     - Attributes (dot gösterimi)
     - Skills listesi
     - Disciplines
     - Bane, Predator Type, Touchstones
   - `QPushButton` “Karakteri Oluştur”

#### 2.3 Metod Taslakları
- `_init_vtm_ui()`
- `_update_clan_info()` → bane + discipline gösterimi
- `_validate_vtm_character()` → isim, clan, puan dağıtımı kontrolleri
- `_calculate_vtm_stats()` → Health, Willpower, Humanity
- `_create_vtm_character()` → `system: VTM5E` sözlüğü

---

### 3. Ortak UI Notları
- Toolbar butonları `QHBoxLayout` ile sayfa başında/sonunda hizalanmalı
- `_load_existing_character()` ve `_save_character_to_file()` benzeri fonksiyonlar paylaşıma açık olacak
- Henüz hazır olmayan özellikler (PDF export) disable edilip tooltip ile “Yakında” denebilir
- DndPage’deki tema/stylesheet kuralları aynı şekilde uygulanacak

---

### 4. Sonraki Teknik Adımlar
1. `gui/app.py` içinde `MmPage` ve `VtmPage` sınıflarını bu taslağa göre genişlet
2. Gereken veriyi `utils/data_loader.py` üzerinden cache’le
3. Her sayfa için `_create_character_*` fonksiyonları yazarak JSON kaydetme uyumu sağla
4. Validasyon ve özet ekranlarını tamamladıktan sonra kaydet/yükle akışı bağlanacak



