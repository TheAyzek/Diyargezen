## Diyargezen FRP Karakter Yaratıcısı

### Öğrenci Bilgileri
- **Ad Soyad**: Deniz Şahin
- **Numara**: 2221032838
- **Telefon**: 05424275482
- **E-posta**: dnsshnonline@gmail.com

### Proje
- **Ad**: Diyargezen FRP Karakter Yaratıcısı
- **Konu**: Üç farklı FRP sistemi (D&D 5e, Mutants & Masterminds, Vampire: The Masquerade) için detaylı karakter oluşturma, düzenleme ve kaydetme.
- **Platform**: Masaüstü (Windows/macOS/Linux)
- **Teknolojiler**: Python, JSON; opsiyonel SQLite
- **Geliştirme Ortamı**: Visual Studio Code

### Özellikler

#### Desteklenen Sistemler
- ✅ **D&D 5e**: Tam GUI desteği, 23 ırk, 14 sınıf, 42 feat, 1000+ eşya
- ✅ **Mutants & Masterminds**: Tam GUI desteği, PL limit validasyonu, power/advantage yönetimi
- ✅ **Vampire: The Masquerade**: Tam GUI desteği, attribute/skill sayaçları, discipline yönetimi

#### Genel Özellikler
- Modüler mimari: Her sistem için ayrı modüller (`dnd_creator.py`, `mm_creator.py`, `vtm_creator.py`)
- Veri odaklı tasarım: Sabit veriler `data/*.json` dosyalarında
- PySide6 ile modern GUI, qdarkstyle dark tema
- Adım bazlı karakter oluşturma sistemi (10+ adım, görsel navigasyon)
- JSON ve SQLite desteği: Karakterleri JSON veya SQLite veritabanına kaydet/yükle
- Gelişmiş SQLite diyaloğu: Arama, filtreleme, önizleme özellikleri
- PDF export: Tüm sistemler için PDF çıktısı (opsiyonel arkaplan görseli ile)
- Validasyon: M&M PL limit kontrolü, VtM attribute/skill dağılım sayaçları
- Ortak helper fonksiyonlar: Tüm sistemler için tutarlı kaydet/yükle deneyimi

### Kurulum
```bash
pip install -r requirements.txt
```

### Çalıştırma

#### GUI ile (Önerilen)
```bash
python -m gui.app
```
veya
```bash
python main.py
```

#### Terminal ile (D&D için)
```bash
python dnd_creator.py
```

### Kullanım Kılavuzu

#### Karakter Oluşturma
1. Uygulamayı başlatın
2. İstediğiniz sistem sekmesini seçin (D&D 5e / M&M / VtM)
3. "Yeni Karakter" butonuna tıklayın
4. Form alanlarını doldurun
5. "Kaydet" veya "SQLite Kaydet" ile kaydedin

#### Karakter Yükleme
- **JSON**: "Karakter Yükle" butonu ile JSON dosyası seçin
- **SQLite**: "SQLite Yükle" butonu ile veritabanı seçin, gelişmiş diyalogdan karakter seçin

#### PDF Export
1. Karakteri oluşturun veya yükleyin
2. "PDF Export" butonuna tıklayın
3. Kayıt konumunu seçin
4. (Opsiyonel) Arkaplan görseli eklemek isteyip istemediğinizi seçin

### PDF Çıktısı Arkaplanı
`assets/` klasörüne boş karakter kağıdınızı (PNG/JPG önerilir) koyun; PDF dışa aktarım sırasında seçebilirsiniz. Tüm sistemler (D&D, M&M, VtM) için desteklenir.

### SQLite Kullanımı (Opsiyonel)
GUI üzerinde "SQLite Kaydet" ve "SQLite Yükle" butonları ile `.db` dosyası seçip çalışabilirsiniz. Karakterler JSON payload olarak saklanır.

**Gelişmiş Özellikler:**
- Sistem filtresi (D&D / M&M / VtM / Tümü)
- Arama özelliği (karakter adı ile)
- Karakter önizleme
- Çift tıklama ile hızlı yükleme

### Proje Şemaları
Proje için detaylı şemalar oluşturulmuştur:
- `PROJE_SEMASI.md` - Ana proje şeması ve genel bakış
- `DETAYLI_SEMALAR.md` - Teknik detaylar, UML diyagramları
- `GORSEL_SEMALAR.md` - PlantUML ve görsel şemalar
- `ASCII_SEMALAR.txt` - Terminal'de görüntülenebilir ASCII diyagramlar
- `SEMALAR_OZET.md` - Tüm şemaların özeti

### Proje Yapısı
```
Diyargezen/
├── gui/
│   └── app.py              # Ana GUI uygulaması
├── utils/
│   ├── data_loader.py      # Veri yükleme (cache destekli)
│   ├── storage.py          # SQLite kayıt/yükleme
│   ├── export_pdf.py       # PDF export (tüm sistemler)
│   └── calculations.py     # Otomatik hesaplamalar (planlandı)
├── data/
│   ├── dnd_data.json       # D&D verileri (3631 satır)
│   ├── mm_data.json        # M&M verileri
│   └── vtm_data.json       # VtM verileri
├── characters/             # Oluşturulan karakterler (JSON)
└── docs/                   # Geliştirme dokümantasyonu
```

### Geliştirme Notları
- Tüm kod Türkçe yorumlarla yazılmıştır
- Modüler yapı sayesinde yeni sistemler kolayca eklenebilir
- Ortak helper fonksiyonlar kod tekrarını önler
- Cache mekanizması ile performans optimize edilmiştir


