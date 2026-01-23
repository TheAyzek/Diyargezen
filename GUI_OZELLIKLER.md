# GUI Özellikleri - Korunması Gereken Sistem-Spesifik Kurallar

## 📋 Genel Yapı

**Dosya**: `gui/app.py` (10,319 satır)
**Framework**: PySide6 (Qt)
**Diller**: Python 3.12+
**Durum**: Restore edildi (Commit 0634f35)

---

## 🎮 Sistem-Spesifik Özellikler

### 1️⃣ D&D 5e (Dungeons & Dragons 5th Edition)

#### Point-Buy Yöntemi
- Kullanıcı temel yetenek puanlarını (Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma) seçebilir
- Point-buy sistemi: 27 puan dağıtımı
- Her yetenek 3-18 arası değer alabilir

#### Abilite Score Increase (ASI)
- Seviye 4, 8, 12, 16, 20'de ASI mevcut
- Kullanıcı tercih edebilir:
  - İki yetenek puanını +2 artırma
  - Dört yetenek puanını +1 artırma
  - Feat seçme

#### Sınıf Sistemi
- 15 farklı D&D sınıfı: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard, Artificer, Blood Hunter, Way of Mercy
- Her sınıf seviye değişikliğinde özel özellikleri (class features) güncellenir
- Hit Dice hesaplaması otomatik yapılır

#### Çok Sınıflılık (Multiclassing)
- Aynı karaktere birden fazla sınıf eklenebilir
- Her sınıfın seviyesi bağımsız şekilde yönetilir
- Proficiency bonusu tüm sınıflar temelinde hesaplanır
- Spell slot hesaplaması çok sınıf seviyelerini dikkate alır

#### Feat (Özellik) Seçimi
- 1,258+ feat mevcuttur
- Seviyelerde feat seçme imkanı (ASI seviyelerinde)
- Feat önkoşulları (prerequisites) kontrol edilir

#### Büyü (Spell) Sistemi
- Sınıfa özgü spell listesi
- Spell slotları sınıf ve seviye temelinde otomatik hesaplanır
- Spell hazırlama (preparation)
- Ritual casting desteği
- Concentration tracking
- Upcasting sistemi
- 2,469+ D&D büyüsü veritabanında

#### Silah ve Ekipman
- Proficiency yönetimi
- Armor Class (AC) otomatik hesapla
- Bonus hesapları
- 233+ ekipman seçeneği

#### Bilgisi ve Yetenekler
- Proficiency seçimi
- Expertise (Rogue, Bard özellikleri)
- Saving throws
- Skill modifiers

#### Çıkmazlar (Backgrounds)
- 57+ background mevcuttur
- Background'a özgü bonuslar
- Skill proficiency benzeri özellikler

---

### 2️⃣ Pathfinder 1e

#### Yetenek Puanları
- 4d6 düşürme (highest 3) yöntemi
- Manuel atama seçeneği
- Irksal bonuslar otomatik uygulanır

#### Irklar (Races)
- 77 farklı ırk (83'ten normalize edildi - duplikatlar kaldırıldı)
- Her ırkın kendi ability score adjustments
- Irksal özellikleri (racial traits)
- Favored class bonusu

#### Sınıflar (Classes)
- 58 farklı sınıf (73'ten normalize edildi - duplikatlar kaldırıldı)
- Seviyeleme systemi
- Class abilities per level
- Prestige classes desteği

#### Feat Sistemi
- 421+ feat mevcuttur
- Feat seçimi her seviyede:
  - Level 1, 3, 5, 7, 9, 11, 13, 15, 17, 19
  - Bonus feats sınıfa göre değişir
- Feat chain tracking (prerequisites)
- Combat feats special handling

#### Büyü Sistemi
- Sınıfa ve seviyeye özgü spell lists
- Spell per day hesapları
- Spell DC hesapları
- Pathfinder spell mechanics
- 500+ Pathfinder büyüsü

#### Seçenek Kurallar
- House rules entegrasyonu
- Alternate class features
- Prestige class multiclassing desteği

---

### 3️⃣ Mutants & Masterminds 3e (M&M)

#### Puan Tabanlı Sistem
- Power Point sistemi
- Ability scores (benzer D&D'ye ama M&M kurallarına uygun)
- Power level hesapları

#### Powers (Yetenekler)
- 21+ power category mevcuttur
- Modular power system
- Extra (power enhancement) seçimi
- Flaw (power reduction) seçimi
- Power point cost hesapları

#### Skills
- M&M-specific skill list
- Skill rank allocation
- Ability modifier uygulaması

#### Equipment
- Gadget creation
- Device system
- Power point cost tracking

---

### 4️⃣ Vampire: The Masquerade 5e (VtM)

#### Klan Seçimi
- 3 klan mevcuttur
- Klan-özgü mekanikler:
  - Klan-specific attributes
  - Klan-specific disciplines

#### Disciplines
- Bloodline-specific abilities
- Level-based progression
- Power selection

#### Attributes
- VtM attribute system (Physical, Social, Mental)
- Ability modifiers

#### Blood Resonance
- Resonance selection
- Power mechanics

---

## 🔧 Kritik İşlevler

### Dialog Sistemleri
- `SqliteCharacterDialog`: Karakter yükleme/seçme
- `CharacterListDialog`: Karakter listesi görüntüleme
- `TemplateManagerDialog`: Template yönetimi
- `CharacterIntroDialog`: D&D karakteri oluşturma
- `SubclassDialog`: Alt-sınıf seçimi (subclass_dialog.py)
- `EquipmentComparisonDialog`: Ekipman karşılaştırma (equipment_comparison_dialog.py)

### Veri Yönetimi
```python
from utils.data_loader import load_dnd_data, load_mm_data, load_vtm_data
from utils.character_versioning import save_character_version, load_character_version
from utils.storage import save_character, load_character
```

### Hesaplama Sistemleri
```python
from utils.calculations import (
    calculate_spell_slots,
    calculate_spell_save_dc,
    calculate_spell_attack_bonus,
    calculate_armor_class,
    calculate_mm_ability_modifier,
)
```

### Export Sistemleri
```python
from utils.export_pdf import (
    export_dnd_character_pdf,
    export_mm_character_pdf,
    export_vtm_character_pdf,
)
from utils.export_formats import (
    export_character_html,
    export_character_json,
    export_character_csv,
)
```

---

## ✅ Korunması Gereken Özellikler

### D&D 5e - KRITIK
- [ ] Point-buy yöntemi
- [ ] ASI level selection (4, 8, 12, 16, 20)
- [ ] Multiclassing desteği
- [ ] Spell slot hesapları
- [ ] Proficiency bonus hesapları
- [ ] Feat seçimi ve ön koşulları

### Pathfinder 1e - KRITIK
- [ ] Feat selection per level (1, 3, 5, 7, ...)
- [ ] Prestige class desteği
- [ ] Ability score progression
- [ ] Spell per day hesapları

### M&M - KRITIK
- [ ] Power Point sistemi
- [ ] Extra/Flaw selection
- [ ] Power level calculations

### VtM - KRITIK
- [ ] Klan-özgü mekanikler
- [ ] Discipline selection
- [ ] Resonance system

---

## 📊 GUI Komponentleri

### Ana Pencere (MainWindow)
- Sistem seçme (D&D 5e, Pathfinder, M&M, VtM)
- Karakter oluşturma/yükleme
- Template yönetimi
- Export seçenekleri
- Kurallar yönetimi (Rule Editor)

### Sistem-Spesifik Sayfalar
- **D&D 5e**: dnd_character_creation_widget → characterCreationDND5E()
- **Pathfinder**: pathfinder_character_creation_widget → characterCreationPathfinder()
- **M&M**: mm_character_creation_widget → characterCreationMM()
- **VtM**: vtm_character_creation_widget → characterCreationVtM()

---

## 🚀 Önemli Notlar

1. **Sistem Bağımsızlığı**: Her sistem kendi kurallarına uyar, aralarında karışma yoktur
2. **Veritabanı Entegrasyonu**: Karakterler SQLite'de saklanır ve versiyonlanır
3. **Kurallar Motoru**: Dinamik kurallar yükleme ve uygulama
4. **PDF Export**: Türkçe font desteği ile tam layout preservation

---

## 📝 Geliştirme Kuralları

Gelecekteki geliştirmelerde:
- ✅ Sistem-spesifik kurallar HERMETİKLY ayrılmış tutulmalı
- ✅ Yeni özellik eklenirken tüm 4 sistem göz önüne alınmalı
- ✅ Bir sistemin kuralları diğerini etkilememelidir
- ✅ Tüm değişiklikler Git ile versiyonlanmalıdır
- ✅ Test edilmemiş değişiklik push edilmemelidir

---

**Son Güncelleme**: 2026-01-23
**Durum**: Tüm özellikler aktif ve korunmuştur
**Commit Hash**: 0634f35 (Başarılı restore)
