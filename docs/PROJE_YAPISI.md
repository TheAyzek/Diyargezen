# Diyargezer - Proje Yapısı

**Son Güncelleme:** 2026-02-12

```
Diyargezer/
│
├── main.py                        # Ana giriş noktası (GUI başlatır)
├── requirements.txt               # Python bağımlılıkları
├── README.md                      # Proje açıklaması
├── .gitignore
│
├── gui/
│   ├── modern_gui.py              # Ana GUI (CustomTkinter) - 4800+ satır
│   ├── app.py                     # Eski PySide6 GUI (fallback)
│   ├── subclass_dialog.py         # Subclass seçim dialog (PySide6)
│   ├── pending_widget.py          # Pending choices widget (PySide6)
│   └── equipment_comparison_dialog.py  # Equipment karşılaştırma (PySide6)
│
├── creators/
│   ├── __init__.py                # Factory Pattern registrations
│   ├── base_creator.py            # Abstract base class
│   ├── dnd5e_creator.py           # D&D 5e karakter oluşturucu
│   ├── pathfinder1e_creator.py    # Pathfinder 1e karakter oluşturucu
│   └── mm3e_creator.py            # M&M 3e karakter oluşturucu
│
├── utils/
│   ├── calculations.py            # D&D 5e hesaplamalar (HP, AC, skills, saves)
│   ├── multiclass.py              # Multiclass sistemi (prerequisite, spell slots)
│   ├── subclass_data.py           # 60+ subclass tanımları
│   ├── conditions.py              # 19 condition/status effect
│   ├── encounter_tracker.py       # Evrensel encounter/savaş takip
│   ├── homebrew.py                # Evrensel homebrew içerik yönetimi
│   ├── portraits.py               # Karakter portre yönetimi
│   ├── export_pdf.py              # PDF export (çoklu template)
│   ├── export_html.py             # HTML/Web export (tüm sistemler)
│   ├── data_loader.py             # JSON veri yükleme (cache + normalizasyon)
│   ├── pathfinder_scraper.py      # PF1e spell scraper & data cleaner
│   ├── performance.py             # Cache ve lazy loading yardımcıları
│   ├── character_comparator.py    # Karakter karşılaştırma
│   ├── character_versioning.py    # Karakter versiyon yönetimi
│   ├── batch_operations.py        # Toplu işlemler
│   ├── storage.py                 # Kayıt/yükleme yardımcıları
│   └── ...                        # Diğer yardımcı modüller
│
├── data/
│   ├── dnd_data.json              # D&D 5e verileri (~5MB)
│   ├── pathfinder_1e_data.json    # Pathfinder 1e verileri (~1.5MB)
│   ├── mm_data.json               # M&M 3e verileri
│   └── backgrounds/               # Background örnekleri
│
├── tests/
│   ├── test_creators.py           # Creator unit testleri
│   └── test_new_features.py       # Özellik testleri (50+ test)
│
├── cli/                           # CLI modülleri (opsiyonel)
│   ├── wizard.py                  # CLI karakter sihirbazı
│   └── steps/                     # CLI adımları
│
├── scripts/
│   ├── scraping/                  # Web scraping scriptleri
│   ├── analysis/                  # Veri analiz scriptleri
│   └── maintenance/               # Bakım scriptleri
│
└── docs/
    ├── README.md                  # Dokümantasyon index
    ├── NEXT_STEPS.md              # Proje durumu & özellik listesi
    ├── SIRADAKI_GOREVLER.md       # Görev takibi (Türkçe)
    ├── PROJE_YAPISI.md            # Bu dosya
    ├── DND_RULES_ANALYSIS.md      # D&D kuralları analizi
    ├── EXE_BUILD_KILAVUZU.md      # PyInstaller build kılavuzu
    └── SPELL_BATCH_SCRAPING.md    # Batch spell scraping notları
```
