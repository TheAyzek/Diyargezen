# Proje Organizasyon Planı

**Tarih:** 2025-01-XX  
**Amaç:** Projeyi düzenli ve bakımı kolay bir yapıya kavuşturmak

---

## 🔍 Mevcut Sorunlar

### Root Klasörü
- ❌ Çok fazla test dosyası (test_project.py, *_test.json, *_test.html)
- ❌ Çok fazla markdown dosyası (15+ MD dosyası)
- ❌ Geçici analiz dosyaları (human_race_*.html, test_*.html)
- ❌ Karışık dosya yapısı

### Scripts Klasörü
- ❌ 83 dosya (çok karmaşık)
- ❌ Test dosyaları, scraping scriptleri, analiz dosyaları karışık
- ❌ Geçici/debug scriptleri
- ❌ Düzenli alt klasör yapısı yok

### Data Klasörü
- ❌ Cache dosyaları ve log dosyaları karışık
- ❌ Test dosyaları (elf_race_test.json, human_race_test.json)
- ❌ Alt klasör yapısı eksik

### Docs Klasörü
- ⚠️ Root'ta da MD dosyaları var (duplicate)
- ⚠️ Dosyalar organize değil

### Characters Klasörü
- ✅ Versiyon dosyaları düzenli
- ⚠️ PDF dosyaları karakter dosyalarıyla karışık

---

## 📁 Yeni Yapı Önerisi

```
Diyargezen/
├── README.md (ana README)
├── requirements.txt
├── main.py
├── build_exe.py
├── Diyargezen.spec
│
├── gui/                    # GUI uygulaması
│   └── app.py
│
├── cli/                    # CLI uygulaması
│   ├── __init__.py
│   ├── context.py
│   ├── io.py
│   ├── wizard.py
│   ├── steps/
│   └── utils/
│
├── creators/               # Sistem-specific creators
│   ├── __init__.py
│   └── dnd_integrated.py
│
├── utils/                  # Yardımcı fonksiyonlar
│   ├── calculations.py
│   ├── data_loader.py
│   ├── export_pdf.py
│   ├── storage.py
│   ├── scraper*.py
│   └── ...
│
├── data/                   # Veri dosyaları
│   ├── dnd_data.json
│   ├── mm_data.json
│   ├── vtm_data.json
│   ├── pathfinder_1e_data.json
│   ├── cache/              # Cache dosyaları
│   │   ├── classes_cache.json
│   │   ├── feats_cache.json
│   │   ├── spells_cache.json
│   │   └── equipment_cache.json
│   ├── logs/               # Log dosyaları
│   │   ├── classes_scraping_log.txt
│   │   └── feats_scraping_log.txt
│   └── test_data/          # Test verileri
│       ├── elf_race_test.json
│       └── human_race_test.json
│
├── scripts/                # Utility scriptleri
│   ├── tests/              # Test scriptleri
│   │   ├── test_project.py
│   │   ├── test_character_creation_comprehensive.py
│   │   ├── test_level_up_comprehensive.py
│   │   ├── test_spell_system.py
│   │   └── run_all_tests.py
│   ├── scraping/           # Scraping scriptleri
│   │   ├── scrape_all_classes.py
│   │   ├── scrape_all_races.py
│   │   ├── scrape_all_feats.py
│   │   ├── scrape_all_equipment.py
│   │   └── scrape_all_dnd_spells.py
│   ├── analysis/           # Analiz scriptleri
│   │   ├── analyze_5esrd_*.py
│   │   ├── check_*.py
│   │   └── debug_*.py
│   └── maintenance/        # Bakım scriptleri
│       ├── clean_*.py
│       └── merge_*.py
│
├── tests/                  # Unit testler (alternatif)
│   └── (boş bırakılabilir, scripts/tests/ kullanılabilir)
│
├── docs/                   # Dokümantasyon
│   ├── README.md           # Dokümantasyon index
│   ├── PROJECT_STATUS.md   # Proje durumu
│   ├── SYSTEM_STATUS.md    # Sistem durumu (birleştirilmiş)
│   ├── DEVELOPMENT.md      # Geliştirme notları
│   └── ARCHITECTURE.md     # Mimari dokümantasyon
│
├── characters/             # Karakter dosyaları
│   ├── *.json              # Aktif karakterler
│   ├── *.pdf               # PDF export'lar
│   ├── templates/          # Şablonlar
│   └── versions/           # Versiyon dosyaları
│
├── assets/                 # Statik dosyalar
│   ├── diyargezer_logo.png
│   └── README.txt
│
├── build/                  # Build dosyaları (gitignore)
│   └── ...
│
└── dist/                   # Dağıtım dosyaları (gitignore)
    └── ...

```

---

## 📋 Yapılacaklar Listesi

### 1. Root Klasörü Temizleme
- [ ] Test dosyalarını `scripts/tests/` klasörüne taşı
  - test_project.py
  - *_test.json (root'taki)
  - *_test.html (root'taki)
- [ ] Markdown dosyalarını `docs/` klasörüne taşı veya birleştir
  - PROJE_SEMASI.md → docs/
  - SISTEM_DURUM_RAPORU.md → docs/
  - TEST_SUITE_REPORT.md → docs/
  - vb.
- [ ] Geçici HTML dosyalarını temizle veya `scripts/temp/` klasörüne taşı
  - human_race_*.html
  - test_*.html
- [ ] Diğer geçici dosyaları temizle
  - ASCII_SEMALAR.txt → docs/ veya sil
  - Gemini_Generated_Image_*.png → assets/ veya sil

### 2. Scripts Klasörü Organizasyonu
- [ ] `scripts/tests/` klasörü oluştur
  - Tüm test_*.py dosyalarını taşı
  - run_all_tests.py'yi taşı
- [ ] `scripts/scraping/` klasörü oluştur
  - Tüm scrape_*.py dosyalarını taşı
  - run_all_batches.py'yi taşı
  - run_all_batches.ps1'yi taşı
- [ ] `scripts/analysis/` klasörü oluştur
  - Tüm analyze_*.py dosyalarını taşı
  - Tüm check_*.py dosyalarını taşı
  - Tüm debug_*.py dosyalarını taşı
  - find_*.py dosyalarını taşı
- [ ] `scripts/maintenance/` klasörü oluştur
  - clean_*.py dosyalarını taşı
  - merge_*.py dosyalarını taşı
  - fix_*.py dosyalarını taşı

### 3. Data Klasörü Organizasyonu
- [ ] `data/cache/` klasörü oluştur
  - Tüm *_cache.json dosyalarını taşı
- [ ] `data/logs/` klasörü oluştur
  - Tüm *_log.txt dosyalarını taşı
- [ ] `data/test_data/` klasörü oluştur
  - Test JSON dosyalarını taşı (elf_race_test.json, vb.)
- [ ] `data/backgrounds/` klasörü zaten var (tut)

### 4. Docs Klasörü Organizasyonu
- [ ] Root'taki MD dosyalarını docs/'a taşı
- [ ] Benzer içerikli dosyaları birleştir
  - PROJECT_STATUS.md, DURUM_RAPORU.md → SYSTEM_STATUS.md
  - EKSIK_OZELLIKLER.md, NEXT_STEPS.md, SONRAKI_ADIMLAR.md → DEVELOPMENT.md
  - TEST_RAPORU.md, TEST_SUITE_REPORT.md → tests/README.md
- [ ] docs/README.md oluştur (index)
- [ ] Güncel dokümantasyonu birleştir

### 5. Characters Klasörü Organizasyonu
- [ ] PDF dosyalarını `characters/exports/` klasörüne taşı (opsiyonel)
- [ ] Versiyon yapısını tut (zaten iyi)

### 6. Temizleme
- [ ] Boş dosyaları sil (65 boş dosya var)
- [ ] Geçici/debug dosyalarını temizle
- [ ] .gitignore'ı güncelle

---

## 🚀 Uygulama Planı

### Adım 1: Klasör Yapısını Oluştur
1. `scripts/tests/` oluştur
2. `scripts/scraping/` oluştur
3. `scripts/analysis/` oluştur
4. `scripts/maintenance/` oluştur
5. `data/cache/` oluştur
6. `data/logs/` oluştur
7. `data/test_data/` oluştur
8. `characters/exports/` oluştur (opsiyonel)

### Adım 2: Dosyaları Taşı
1. Test dosyalarını taşı
2. Scraping scriptlerini taşı
3. Analiz scriptlerini taşı
4. Cache ve log dosyalarını taşı
5. MD dosyalarını taşı ve birleştir

### Adım 3: Import Path'lerini Güncelle
1. Tüm script dosyalarındaki import path'lerini güncelle
2. Test scriptlerindeki path'leri güncelle
3. Scraping scriptlerindeki path'leri güncelle

### Adım 4: Dokümantasyonu Güncelle
1. docs/README.md oluştur
2. Birleştirilmiş dokümantasyonu oluştur
3. README.md'yi güncelle

### Adım 5: Temizleme
1. Boş dosyaları temizle
2. Geçici dosyaları temizle
3. .gitignore'ı güncelle

---

## ⚠️ Dikkat Edilmesi Gerekenler

1. **Import Path'leri:** Dosya taşıma sonrası tüm import path'leri güncellenmeli
2. **Relative Path'ler:** Scriptlerdeki relative path'ler güncellenmeli
3. **Test Scriptleri:** Test scriptleri hala çalışmalı
4. **Scraping Scriptleri:** Scraping scriptleri hala çalışmalı
5. **Cache Dosyaları:** Cache dosyaları taşındıktan sonra path'ler güncellenmeli

---

## 📊 Beklenen Sonuç

### Öncesi
- Root: 50+ dosya
- Scripts: 83 dosya (karmaşık)
- Data: Karışık yapı
- Docs: Root'ta ve docs/'ta duplicate

### Sonrası
- Root: ~10 dosya (sadece ana dosyalar)
- Scripts: 4 alt klasör (organize)
- Data: 3 alt klasör (organize)
- Docs: Tek yerde, organize
- Daha kolay navigasyon
- Daha kolay bakım
- Daha kolay anlama

---

## 🎯 Sonraki Adımlar

1. Bu planı onayla
2. Klasör yapısını oluştur
3. Dosyaları sistematik olarak taşı
4. Import path'lerini güncelle
5. Test et
6. Dokümantasyonu güncelle

