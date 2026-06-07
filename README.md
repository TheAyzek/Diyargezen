# Diyargezer - Evrensel FRP Karakter Oluşturucu

## Öğrenci Bilgileri
- **Ad Soyad**: Deniz Şahin
- **Numara**: 2221032838
- **Telefon**: 05424275482
- **E-posta**: dnsshnonline@gmail.com

## Proje
- **Ad**: Diyargezer FRP Karakter Yaratıcısı
- **Konu**: Üç farklı FRP sistemi için detaylı karakter oluşturma, düzenleme ve kaydetme
- **Platform**: Masaüstü (Windows/macOS/Linux)
- **Teknolojiler**: Python, CustomTkinter, JSON, ReportLab

## Desteklenen Sistemler

| Sistem | Özellikler |
|--------|-----------|
| **D&D 5e** | 23 ırk, 14 sınıf, 60+ subclass, multiclassing, 4000+ büyü, equipment, level up |
| **Pathfinder 1e** | 77 ırk, 73 sınıf, 421 feat, 500+ büyü, BAB/saves, skill ranks |
| **Mutants & Masterminds 3e** | Power Level sistemi, PL limit validasyonu, power points economy |

## Özellikler

### Karakter Yönetimi
- Adım adım karakter oluşturma sihirbazı
- Level up sistemi (HP, ASI/Feat, class features, spell slots, subclass seçimi)
- Multiclassing (prerequisite kontrolü, spell slot birleştirme, hit dice)
- Condition/Status Effect takibi (15 standart D&D condition + ekstra)

### Araçlar (Tüm 3 Sistemde)
- **Encounter Tracker**: Savaş sırası, initiative, HP takibi, tur sayacı, hasar/şifa
- **Homebrew İçerik Yöneticisi**: Özel sınıf/ırk/büyü/güç ekleme
- **Karakter Portreleri**: Resim ekleme/görüntüleme, çoklu format desteği
- **HTML/Web Export**: Responsive karakter kağıdı, sistem bazlı temalar

### Export
- **PDF Export**: Çoklu template (standart, detaylı, kompakt, minimal)
- **HTML Export**: Responsive web sayfası, tarayıcıda açma
- **JSON**: Karakter verisi kaydetme/yükleme

### Teknik
- Modern CustomTkinter GUI (dark blue tema)
- Factory Pattern ile modüler mimari
- 50+ unit test
- Spell browser (Pathfinder 1e)
- Karakter doğrulama ve karşılaştırma

## Kurulum

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
# GUI (Önerilen)
python main.py

# Doğrudan GUI
python -m gui.modern_gui
```

## Proje Yapısı

```
Diyargezer/
├── main.py                    # Ana giriş noktası
├── gui/
│   └── modern_gui.py          # Ana GUI uygulaması (CustomTkinter)
├── creators/
│   ├── base_creator.py        # Abstract base class
│   ├── dnd5e_creator.py       # D&D 5e
│   ├── pathfinder1e_creator.py # Pathfinder 1e
│   └── mm3e_creator.py        # M&M 3e
├── utils/
│   ├── calculations.py        # D&D hesaplamalar
│   ├── multiclass.py          # Multiclass sistemi
│   ├── subclass_data.py       # Subclass verileri
│   ├── conditions.py          # Durum efektleri
│   ├── encounter_tracker.py   # Savaş takip
│   ├── homebrew.py            # Homebrew içerik
│   ├── portraits.py           # Karakter portreleri
│   ├── export_pdf.py          # PDF export
│   ├── export_html.py         # HTML export
│   ├── data_loader.py         # Veri yükleme
│   └── pathfinder_scraper.py  # PF1e spell scraper
├── data/
│   ├── dnd_data.json          # D&D 5e verileri
│   ├── pathfinder_1e_data.json # Pathfinder verileri
│   └── mm_data.json           # M&M verileri
├── tests/
│   ├── test_creators.py       # Creator testleri
│   └── test_new_features.py   # Özellik testleri (50+)
├── docs/                      # Dokümantasyon
└── requirements.txt           # Bağımlılıklar
```

## Testler

```bash
python -m pytest tests/ -v
```
