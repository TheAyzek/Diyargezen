# Diyargezen - Proje Yapısı ve Mimari Rapor

**Son Güncelleme:** 5 Ağustos 2026  
**Durum:** Üretim Modu (Production Ready) — %100 Yasal PF1e Karakter Yaratıcısı & Standalone Masaüstü Paket Derlemesi Tamamlandı.  
**Test Durumu:** 284 Geçti (284 passed, 2 skipped in 412s).

```
Diyargezenweb/
│
├── rules/                         # Paylaşılan kural ve doğrulama motoru (desktop + web)
│   ├── pf1e_rules.py              # Pathfinder 1e doğrulama (Genişletilmiş ikonik feat zincirleri)
│   ├── character_manager.py       # Seviye atlatma sihirbazı (FCB & Retroaktif CON HP, state machine)
│   ├── calculators.py             # 5 adımlı bağımlı stat ve bonus hesaplama boru hattı
│   ├── rule_parser.py             # Kural ifadesi ve açıklama ayrıştırıcı
│   └── base_validator.py          # Soyut validator taban sınıfı
│
├── models/
│   └── entity.py                  # DiyargezenEntity veri modeli
│
├── data/
│   ├── characters.db              # 22.307 ön işlenmiş kural varlığı (159 MB SQLite)
│   ├── pathfinder_1e_data.json    # PF1e JSON varlık verisi
│   ├── pf1e_scraped_items.json    # Scrape edilmiş zırh, silah ve ekipmanlar
│   └── backgrounds/               # Karakter geçmiş şablonları
│
├── desktop/                       # Masaüstü uygulaması (PySide6)
│   ├── main_desktop.py            # Masaüstü giriş noktası
│   ├── build_exe.py               # Standalone PyInstaller & Portable ZIP derleyici
│   ├── Diyargezen.spec            # PyInstaller paketleme spesifikasyonu
│   ├── local_db.py                # Çevrimdışı SQLite (WAL modu, dirty state, tombstone)
│   ├── sync_engine.py             # Arka plan QThread senkronizasyon motoru
│   ├── api_client.py              # JWT REST istemcisi
│   ├── gui/
│   │   ├── main_window.py         # QStackedWidget + Gömülü FastAPI/Uvicorn yönetimi
│   │   ├── screens/               # Tavern (Dashboard), Forge (Wizard), Character Sheet
│   │   └── dialogs/               # Login, Subclass, Feat/Trait seçim diyaloğu
│   └── cli/                       # CLI karakter oluşturucu
│
├── web/
│   ├── backend/                   # FastAPI REST API
│   │   ├── run.py
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── core/              # config (AppData/Local çözümlenmesi), database
│   │   │   ├── routers/           # auth, characters, rules, sync, systems
│   │   │   ├── services/          # character, rules, auth, gm_engine
│   │   │   └── schemas/           # Pydantic v2 validasyon şemaları
│   │   └── tests/                 # API & Senkronizasyon entegrasyon testleri
│   │
│   └── frontend/                  # React + Vite (Dark Fantasy SaaS Teması)
│       ├── package.json
│       ├── public/templates/      # AcroForm PDF şablonları (pf1e_sheet.pdf)
│       └── src/
│           ├── App.jsx
│           ├── store/characterStore.js
│           └── components/        # Trait, Feat, Spell seçicileri ve PF1eSheet
│
├── creators/                      # Karakter Fabrika Katmanı (Factory Pattern)
│   ├── base_creator.py
│   └── pathfinder1e_creator.py    # %100 Yasal PF1e Karakter Üretici
│
├── utils/                         # Yardımcı Sürücüler
│   ├── data_loader.py             # Bellek içi kural varlık önbelleği
│   ├── export_pdf.py              # Canlı AcroForm PDF doldurma & portre damgalama (pypdf 7.0 uyumlu)
│   ├── soft_validation.py         # Soft-block esnek doğrulama ve homebrew işaretleyici
│   └── portraits.py               # Base64 portre kod çözücü
│
├── dist/                          # Derlenmiş Dağıtım Çıktıları
│   ├── Diyargezen/                # Diyargezen.exe Standalone Masaüstü Uygulaması
│   └── Diyargezen_Portable.zip    # Tek tıkla çalıştırılabilir taşınabilir ZIP paketi
│
├── templates/                     # Orijinal Pathfinder 1e AcroForm PDF Şablonu (pf1e_sheet.pdf)
│
├── tests/                         # Kök seviye birim ve entegrasyon testleri (284 test)
│
└── docs/                          # Mühendislik Dokümantasyonu
    ├── README.md
    ├── DEPLOYMENT.md
    ├── PROJE_YAPISI.md            # Bu dosya
    └── SIRADAKI_GOREVLER.md
```

## Veri Akışı ve Senkronizasyon Mimarisi

```
Scraper/JSON ──► characters.db (22.307 SQLite kural varlığı)
                      │
                      ▼
              CharacterManager (rules/)
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   FastAPI (web/backend)    PySide6 (desktop/)
          │                       │
          ▼                       ▼
   React Frontend          Local SQLite (WAL) + Background Sync (LWW)
```
