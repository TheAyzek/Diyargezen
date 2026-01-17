# Proje Yapısı - Diyargezen D&D 5e Karakter Yaratıcısı

**Son Güncelleme:** 2025-01-XX  
**Durum:** Organize edildi ✅

---

## 📁 Dizin Yapısı

```
Diyargezen/
├── README.md                    # Ana dokümantasyon
├── requirements.txt             # Python bağımlılıkları
├── main.py                      # Ana giriş noktası (GUI)
│
├── gui/                         # GUI uygulaması
│   └── app.py                   # Ana GUI uygulaması (PySide6)
│
├── cli/                         # CLI uygulaması
│   ├── __init__.py
│   ├── context.py
│   ├── io.py
│   ├── wizard.py
│   ├── steps/                   # Wizard adımları
│   │   ├── intro.py
│   │   ├── race.py
│   │   ├── class_features.py
│   │   └── ...
│   └── utils/
│
├── creators/                    # Sistem-specific creators
│   ├── __init__.py
│   └── dnd_integrated.py
│
├── utils/                       # Yardımcı fonksiyonlar
│   ├── calculations.py          # D&D hesaplamaları
│   ├── data_loader.py           # Veri yükleme
│   ├── export_pdf.py            # PDF export
│   ├── storage.py               # JSON/SQLite kayıt
│   ├── dnd_5esrd_scraper.py     # D&D 5e scraper
│   ├── pathfinder_scraper.py    # Pathfinder 1e scraper
│   └── ...
│
├── data/                        # Veri dosyaları
│   ├── dnd_data.json            # Ana D&D 5e verisi
│   ├── mm_data.json             # Mutants & Masterminds verisi
│   ├── vtm_data.json            # Vampire: The Masquerade verisi
│   ├── pathfinder_1e_data.json  # Pathfinder 1e verisi
│   │
│   ├── cache/                   # Cache dosyaları
│   │   ├── classes_cache.json
│   │   ├── feats_cache.json
│   │   ├── spells_cache.json
│   │   └── equipment_cache.json
│   │
│   ├── logs/                    # Log dosyaları
│   │   ├── classes_scraping_log.txt
│   │   └── feats_scraping_log.txt
│   │
│   ├── backgrounds/             # Background örnekleri
│   │   └── srd_examples.json
│   │
│   ├── rules/                   # Kural dosyaları
│   │
│   └── test_data/               # Test verileri
│       ├── elf_race_test.json
│       └── human_race_test.json
│
├── scripts/                     # Utility scriptleri
│   ├── organize_project.py      # Proje organizasyon scripti
│   ├── update_paths_after_organize.py  # Path güncelleme scripti
│   │
│   ├── tests/                   # Test scriptleri
│   │   ├── run_all_tests.py
│   │   ├── test_character_creation_comprehensive.py
│   │   ├── test_level_up_comprehensive.py
│   │   ├── test_spell_system.py
│   │   └── ...
│   │
│   ├── scraping/                # Scraping scriptleri
│   │   ├── scrape_all_classes.py
│   │   ├── scrape_all_races.py
│   │   ├── scrape_all_feats.py
│   │   ├── scrape_all_equipment.py
│   │   ├── scrape_all_dnd_spells.py
│   │   ├── scrape_dnd_spells_batch.py
│   │   ├── scrape_pathfinder_spells.py
│   │   └── run_all_batches.py
│   │
│   ├── analysis/                # Analiz scriptleri
│   │   ├── analyze_5esrd_*.py
│   │   ├── check_*.py
│   │   ├── debug_*.py
│   │   ├── find_*.py
│   │   └── ...
│   │
│   ├── maintenance/             # Bakım scriptleri
│   │   ├── clean_*.py
│   │   ├── merge_*.py
│   │   └── fix_*.py
│   │
│   └── temp/                    # Geçici dosyalar
│       └── *.html               # Test HTML dosyaları
│
├── docs/                        # Dokümantasyon
│   ├── README.md                # Dokümantasyon index (TODO)
│   ├── PROJECT_STATUS.md        # Proje durumu
│   ├── SYSTEM_STATUS.md         # Sistem durumu
│   ├── DEVELOPMENT.md           # Geliştirme notları (TODO: birleştir)
│   ├── PROJE_ORGANIZASYON_PLANI.md  # Organizasyon planı
│   └── ...
│
├── characters/                  # Karakter dosyaları
│   ├── *.json                   # Aktif karakterler
│   ├── templates/               # Karakter şablonları
│   ├── exports/                 # PDF export'lar
│   │   └── *.pdf
│   └── versions/                # Versiyon dosyaları
│       └── [character_name]/
│           └── version_*.json
│
├── assets/                      # Statik dosyalar
│   ├── diyargezer_logo.png
│   ├── logo_placeholder.txt
│   └── README.txt
│
├── build/                       # Build dosyaları (gitignore)
│   └── Diyargezen/
│
├── dist/                        # Dağıtım dosyaları (gitignore)
│   └── Diyargezen.exe
│
├── build_exe.py                 # PyInstaller build scripti
├── Diyargezen.spec              # PyInstaller spec dosyası
├── build_exe_simple.bat         # Basit build scripti
└── build_exe_simple.sh          # Basit build scripti (Linux/Mac)

```

---

## 📋 Klasör Açıklamaları

### `/gui`
Ana GUI uygulaması. PySide6 ile geliştirilmiş.

### `/cli`
Terminal tabanlı CLI uygulaması. Wizard sistemi ile karakter oluşturma.

### `/utils`
Yardımcı fonksiyonlar ve modüller:
- Hesaplamalar (HP, AC, spell slots, vb.)
- Veri yükleme ve kaydetme
- Export fonksiyonları (PDF, HTML, JSON, CSV)
- Web scraping (D&D 5e, Pathfinder 1e, M&M)
- Karakter yönetimi (versioning, comparison, statistics)

### `/data`
Tüm veri dosyaları:
- **Ana veri dosyaları:** `dnd_data.json`, `mm_data.json`, vb.
- **cache/:** Web scraping cache dosyaları
- **logs/:** Scraping log dosyaları
- **backgrounds/:** Background örnekleri
- **test_data/:** Test için kullanılan veriler

### `/scripts`
Utility scriptleri, organize edilmiş:
- **tests/:** Test scriptleri (karakter oluşturma, level up, spell sistemi)
- **scraping/:** Web scraping scriptleri
- **analysis/:** Veri analizi ve debug scriptleri
- **maintenance/:** Bakım scriptleri (clean, merge, fix)
- **temp/:** Geçici dosyalar

### `/docs`
Tüm dokümantasyon dosyaları (Markdown formatında).

### `/characters`
Karakter dosyaları:
- Aktif karakterler (JSON)
- PDF export'lar
- Versiyon dosyaları
- Şablonlar

### `/assets`
Statik dosyalar (logo, görseller, vb.).

---

## 🔧 Path Yapısı

### Cache Dosyaları
- Eski: `data/classes_cache.json`
- Yeni: `data/cache/classes_cache.json`

### Log Dosyaları
- Eski: `data/classes_scraping_log.txt`
- Yeni: `data/logs/classes_scraping_log.txt`

### Test Dosyaları
- Eski: `test_project.py` (root)
- Yeni: `scripts/tests/test_project.py`

### Dokümantasyon
- Eski: `PROJE_SEMASI.md` (root)
- Yeni: `docs/PROJE_SEMASI.md`

---

## 📝 Notlar

1. **Import Path'leri:** Tüm import path'leri güncellendi (scripts/, utils/, vb.)
2. **Cache Path'leri:** Cache dosyaları `data/cache/` altında
3. **Log Path'leri:** Log dosyaları `data/logs/` altında
4. **Test Path'leri:** Test dosyaları `scripts/tests/` altında
5. **Doc Path'leri:** Tüm dokümantasyon `docs/` altında

---

## 🚀 Kullanım

### Testleri Çalıştırma
```bash
python scripts/tests/run_all_tests.py
```

### Scraping Yapma
```bash
python scripts/scraping/scrape_all_classes.py
python scripts/scraping/scrape_all_races.py
```

### Analiz Yapma
```bash
python scripts/analysis/check_scraping_status.py
```

---

## ✅ Organizasyon Durumu

- ✅ Scripts klasörü organize edildi (tests/, scraping/, analysis/, maintenance/)
- ✅ Data klasörü organize edildi (cache/, logs/, test_data/)
- ✅ Root klasörü temizlendi (test dosyaları, MD dosyaları taşındı)
- ✅ Characters klasörü organize edildi (exports/ eklendi)
- ✅ Path'ler güncellendi (cache/, logs/)
- ⚠️ Dokümantasyon birleştirilmesi gerekiyor
- ⚠️ Boş dosyalar temizlenebilir

---

## 📊 İstatistikler

- **Toplam Dosya:** ~2099 Python dosyası
- **Script Dosyaları:** ~80 script (organize edildi)
- **Test Dosyaları:** ~30 test scripti
- **Scraping Scriptleri:** ~14 scraping scripti
- **Analiz Scriptleri:** ~37 analiz scripti
- **Bakım Scriptleri:** ~4 bakım scripti

---

**Son Güncelleme:** Organizasyon tamamlandı ✅

