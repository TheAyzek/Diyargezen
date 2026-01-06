## MM & VtM GUI Gereksinimleri

### 1. Mutants & Masterminds (M&M)

#### Veri Özeti
- `power_levels`: PL8/PL10/PL12 limitleri (attack/effect/defense/toughness)
- `abilities`: Strength, Stamina, Agility, Dexterity, Fighting, Intellect, Awareness, Presence
- `archetypes`: Blaster, Bruiser, Detective (önerilen power ve advantage listeleri)

#### Zorunlu Girdiler
| Alan | Kaynak | Kontrol |
|------|--------|---------|
| Karakter adı | Kullanıcı | boş bırakılamaz |
| Power Level | `power_levels` | seçim zorunlu |
| Arketip | `archetypes` | seçim zorunlu |
| Ability Scores | sabit 8 alan | numeric (min 0, max 20?) |
| Power Points | manuel alan | toplam PP gösterimi |

#### UI Taslak Akışı
1. **Temel Bilgiler**: İsim, kahraman adı, Power Level, arketip özeti (read-only)
2. **Ability Scores**: 8 adet `QSpinBox`, PL limitlerine göre uyarı
3. **Power & Advantage Önerileri**: `QListWidget` (çoklu seçim), arketip önerileri otomatik highlight
4. **Notlar / Kısa Arka Plan**: `QTextEdit`
5. **Özet**: hesaplanmış caps (Attack vs PL, Defense vs PL)

#### Ek Gereksinimler
- Point tracker: Toplam PP, harcanan PP (manuel giriş + otomatik hesap)
- Validasyon: seçilen ability/attack değerleri PL limitleri aşınca uyarı
- Kaydetme: `system = "MUTANTS_AND_MASTERMINDS"`
- PDF/JSON formatı: D&D ile aynı sözlük yapısını kullan, ek alanları `mm_specific` anahtarında tut

---

### 2. Vampire: The Masquerade (VtM)

#### Veri Özeti
- `clans`: Brujah, Ventrue, Toreador (bane + 3 discipline)
- `attributes`: Physical/Social/Mental başlıkları altında 3’er özellik
- `skills`: Physical/Social/Mental kategorilerde 9’ar beceri

#### Zorunlu Girdiler
| Alan | Kaynak | Kontrol |
|------|--------|---------|
| Karakter adı | Kullanıcı | boş bırakılamaz |
| Klan | `clans` | seçim zorunlu (bane + disiplinleri göster) |
| Öznitelik noktaları | `attributes` | klasik 4/3/3 dağıtım (özelleştirilebilir) |
| Beceri noktaları | `skills` | kategori başına limit |
| Disiplinler | clan default 3, ek seçim opsiyonu |
| Predator Type, Chronicle vb. | manuel alan (opsiyonel) |

#### UI Taslak Akışı
1. **Temel Bilgiler**: İsim, Klan, Chronicle, Sire, Concept
2. **Attributes**: Physical/Social/Mental bölümleri, her bir özellik için `QSpinBox` (0-5)
3. **Skills**: kategori bazlı `QListWidget` + `QSpinBox` (0-5), toplam pool göstergesi
4. **Discipline & Bane**: Klan bane açıklaması (read-only), clan disiplinleri listesi, ekstra slotlar
5. **Özet**: insanlık (Humanity), Health, Willpower otomatik hesap (Stamina + Resolve, Composure + Resolve)

#### Ek Gereksinimler
- Nokta dağıtım kuralları (ör. Attributes: 1 kategori 4, ikisi 3/2) opsiyonel toggle
- İleride Röle/Touchstone/Predator Type alanları eklenebilir
- Kaydetme: `system = "VTM5E"`
- PDF export: VtM karakter kağıdı şablonuna uyumlu (gelecek sprint)

---

### 3. Ortak Gereksinimler
- **Veri Yükleme**: `utils/data_loader.py` içine `load_mm_data`, `load_vtm_data` fonksiyonları ekle (cache destekli)
- **Kaydet/Yükle**: `storage.py` mevcut yapısı aynı; `system` alanı ile filtreleme
- **GUI Yapısı**:
  - `MainWindow` tabbar: DndPage / MmPage / VtmPage
  - Her sayfa için `QStackedWidget`: ana menü + wizard/tablar
  - Ortak butonlar: Yeni, Kaydet, Yükle, PDF (hazır olmadığında disabled)
- **Validasyon**: her sayfa `_validate_character()` metoduna sahip olmalı
- **Serializer**: D&D’ye benzer `dict` döndüren `_create_character()` fonksiyonu oluştur

---

### 4. Sonraki Adımlar
1. `utils/data_loader.py` güncelle → `load_mm_data`, `load_vtm_data`
2. `gui/app.py` içinde `MmPage` ve `VtmPage` sınıflarını DndPage benzeri yapı ile genişlet
3. JSON kaydetme formatını örnek karakterle test et:
   ```json
   {
     "system": "MUTANTS_AND_MASTERMINDS",
     "name": "Photon",
     "power_level": "PL10",
     "abilities": {...},
     "powers": [...],
     "advantages": [...],
     "notes": "..."
   }
   ```
4. UI maketlerini (Qt Designer taslağı veya çizim) hazırlayıp kullanıcı akışını doğrula



