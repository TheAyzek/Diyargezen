## Diyargezen FRP Karakter Yaratıcısı

## Öğrenci Bilgileri
- **Ad Soyad**: Deniz Şahin
- **Numara**: 2221032838
- **Telefon**: 05424275482
- **E-posta**: dnsshnonline@gmail.com

## Proje
- **Ad**: Diyargezen FRP Karakter Yaratıcısı
- **Konu**: Dört farklı FRP sistemi (D&D 5e, Pathfinder 1e, Mutants & Masterminds, Vampire: The Masquerade) için detaylı karakter oluşturma, düzenleme ve kaydetme.
- **Platform**: Masaüstü (Windows/macOS/Linux)
- **Teknolojiler**: Python, JSON; opsiyonel SQLite
- **Geliştirme Ortamı**: Visual Studio Code

## Özellikler

### Desteklenen Sistemler
- ✅ **D&D 5e**: Tam GUI desteği, 23 ırk, 14 sınıf, 42 feat, 1000+ eşya, point buy/standard array/manual ability scores
- ✅ **Pathfinder 1e**: CLI desteği, BAB/Saves hesaplamaları, skill ranks sistemi, feat prerequisites, 15-point buy
- ✅ **Mutants & Masterminds**: Tam GUI desteği, PL limit validasyonu, power/advantage yönetimi, power points economy
- ✅ **Vampire: The Masquerade**: Tam GUI desteği, dot system (1-5), clan disciplines, predator types, hunger/blood potency

### Genel Özellikler
- **Modüler mimari**: Factory Pattern ile sistem seçimi, her sistem için ayrı creator modülleri
- **Veri odaklı tasarım**: Sabit veriler `data/*.json` dosyalarında, web scraping ile doldurulabilir
- **Base Creator sınıfı**: Abstract base class ile inheritance ve ortak interface
- **Validation sistemi**: Her sistem için kapsamlı validasyon ve error reporting
- **Derived stats hesaplamaları**: Otomatik HP, AC, saves, skills hesaplamaları
- PySide6 ile modern GUI, qdarkstyle dark tema
- Adım bazlı karakter oluşturma sistemi (10+ adım, görsel navigasyon)
- JSON ve SQLite desteği: Karakterleri JSON veya SQLite veritabanına kaydet/yükle
- Gelişmiş SQLite diyaloğu: Arama, filtreleme, önizleme özellikleri
- PDF export: Tüm sistemler için PDF çıktısı (opsiyonel arkaplan görseli ile)
- Validasyon: M&M PL limit kontrolü, VtM attribute/skill dağılım sayaçları
- Ortak helper fonksiyonlar: Tüm sistemler için tutarlı kaydet/yükle deneyimi

## Mimari

### Factory Pattern
```python
from creators import CharacterFactory

# Sistem seçimi
creator = CharacterFactory.create_creator("dnd5e")
character = creator.create_character()

# Validasyon
errors = creator.validate_character(character)

# Derived stats
stats = creator.calculate_derived_stats(character)
```

### Creator Sınıfları
- `BaseCharacterCreator`: Abstract base class
- `DND5ECreator`: D&D 5e spesifik kurallar
- `Pathfinder1ECreator`: Pathfinder 1e BAB/saves/skill ranks
- `VTM5ECreator`: VtM dot system ve clan disciplines
- `MM3ECreator`: M&M PL limits ve power points

## Kurulum
```bash
pip install -r requirements.txt
```

## Çalıştırma

### GUI ile (Önerilen)
```bash
python -m gui.app
```
veya
```bash
python main.py
```

### Terminal ile
```bash
# D&D 5e
python creators/dnd5e_creator.py

# Pathfinder 1e
python creators/pathfinder1e_creator.py

# M&M 3e
python creators/mm3e_creator.py

# VtM 5e
python creators/vtm5e_creator.py
```

### Testler
```bash
python -m pytest tests/
# veya
python tests/test_creators.py
```

## Kullanım Kılavuzu

### Karakter Oluşturma
1. Uygulamayı başlatın
2. İstediğiniz sistem sekmesini seçin (D&D 5e / Pathfinder 1e / M&M / VtM)
3. "Yeni Karakter" butonuna tıklayın
4. Form alanlarını doldurun
5. "Kaydet" veya "SQLite Kaydet" ile kaydedin

### Karakter Yükleme
- **JSON**: "Karakter Yükle" butonu ile JSON dosyası seçin
- **SQLite**: "SQLite Yükle" butonu ile veritabanı seçin, gelişmiş diyalogdan karakter seçin

### PDF Export
1. Karakteri oluşturun veya yükleyin
2. "PDF Export" butonuna tıklayın
3. Kayıt konumunu seçin
4. (Opsiyonel) Arkaplan görseli eklemek isteyip istemediğinizi seçin

## Proje Yapısı
```
Diyargezen/
├── creators/
│   ├── base_creator.py      # Abstract base class
│   ├── dnd5e_creator.py     # D&D 5e implementation
│   ├── pathfinder1e_creator.py # Pathfinder 1e implementation
│   ├── vtm5e_creator.py     # VtM 5e implementation
│   ├── mm3e_creator.py      # M&M 3e implementation
│   └── __init__.py          # Factory registration
├── gui/
│   └── app.py               # Ana GUI uygulaması
├── utils/
│   ├── data_loader.py       # Veri yükleme (cache destekli)
│   ├── storage.py           # SQLite kayıt/yükleme
│   ├── export_pdf.py        # PDF export (tüm sistemler)
│   └── calculations.py      # Otomatik hesaplamalar
├── data/
│   ├── dnd_data.json        # D&D verileri (5.3MB)
│   ├── pathfinder_1e_data.json # Pathfinder verileri (1.6MB)
│   ├── mm_data.json         # M&M verileri (152KB)
│   ├── vtm_data.json        # VtM verileri (genişletilmiş)
│   └── backgrounds/         # Background verileri
├── tests/
│   └── test_creators.py     # Unit test'ler
├── characters/              # Oluşturulan karakterler (JSON)
└── docs/                    # Geliştirme dokümantasyonu
```

## Geliştirme Notları
- Tüm kod Türkçe yorumlarla yazılmıştır
- Modüler yapı sayesinde yeni sistemler kolayca eklenebilir
- Factory Pattern ile sistem seçimi ve genişletme
- Abstract base class ile tutarlı interface
- Kapsamlı validation ve error handling
- Ortak helper fonksiyonlar kod tekrarını önler
- Cache mekanizması ile performans optimize edilmiştir
- Unit test'ler ile kod kalitesi garanti altına alınmıştır


