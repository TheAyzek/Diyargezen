# Diyargezen - Proje Yapısı

**Son Güncelleme:** 2026-07-22

```
Diyargezenweb/
│
├── rules/                         # Paylaşılan kural motoru (desktop + web)
│   ├── pf1e_rules.py              # Pathfinder 1e doğrulama
│   ├── character_manager.py       # SQLite entity sorguları
│   ├── calculators.py             # İstatistik hesaplama
│   ├── rule_parser.py             # Kural ifadesi ayrıştırıcı
│   └── base_validator.py          # Abstract validator
│
├── models/
│   └── entity.py                  # DiyargezenEntity modeli
│
├── data/
│   ├── characters.db              # Ana SQLite veritabanı (entities, users, characters)
│   ├── pathfinder_1e_data.json    # PF1e JSON verisi
│   ├── pf1e_scraped_items.json    # Scrape edilmiş ekipman/zırh
│   └── backgrounds/               # D&D background örnekleri
│
├── desktop/                       # Masaüstü uygulaması (PySide6)
│   ├── main_desktop.py            # Giriş noktası
│   ├── local_db.py                # Offline SQLite
│   ├── sync_engine.py             # Bulut senkronizasyon motoru
│   ├── api_client.py              # JWT REST istemcisi
│   ├── gui/
│   │   ├── main_window.py
│   │   ├── screens/               # Tavern, Forge, Character Sheet
│   │   └── dialogs/               # Login, subclass vb.
│   └── cli/                       # CLI karakter sihirbazı
│
├── web/
│   ├── backend/                   # FastAPI REST API
│   │   ├── run.py
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── core/              # config, database
│   │   │   ├── routers/           # auth, characters, rules, sync, systems
│   │   │   ├── services/          # character, rules, auth
│   │   │   └── schemas/
│   │   └── tests/                 # 22 API testi
│   │
│   └── frontend/                  # React + Vite
│       ├── package.json
│       ├── public/templates/      # PDF şablonları (pf1e, dnd5e, mnm3e)
│       └── src/
│           ├── App.jsx
│           ├── store/characterStore.js
│           └── components/
│               ├── Dashboard.jsx
│               ├── Auth.jsx
│               ├── TraitSelectorModal.jsx
│               └── sheets/        # PF1eSheet, controls, displays
│
├── creators/                      # Factory Pattern karakter oluşturucular
│   ├── base_creator.py
│   ├── dnd5e_creator.py
│   ├── pathfinder1e_creator.py
│   └── mm3e_creator.py
│
├── utils/                         # Paylaşılan yardımcılar
│   ├── data_loader.py             # JSON veri yükleme (cache)
│   ├── export_pdf.py              # PDF export (çoklu template dizini)
│   ├── export_html.py
│   ├── encounter_tracker.py
│   ├── homebrew.py
│   └── portraits.py
│
├── scraper/                       # Veri toplama
│   ├── pf1e_weapons_armor_scraper.py
│   └── seed_pf1e_traits.py        # 80+ kategorize trait seeder
│
├── templates/                     # Legacy PDF şablonları (pf1e_sheet.pdf)
│
├── tests/                         # Kök seviye unit testler (250+)
│
└── docs/
    ├── README.md
    ├── NEXT_STEPS.md
    ├── PROJE_YAPISI.md            # Bu dosya
    └── SIRADAKI_GOREVLER.md
```

## Veri Akışı

```
Scraper/JSON ──► characters.db (SQLite entities)
                      │
                      ▼
              CharacterManager (rules/)
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   FastAPI (web/backend)    PySide6 (desktop/)
          │                       │
          ▼                       ▼
   React Frontend          Local SQLite + Sync
```
