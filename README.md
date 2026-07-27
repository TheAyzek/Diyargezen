# Diyargezer - Evrensel FRP Karakter Oluşturucu

## Öğrenci Bilgileri
- **Ad Soyad**: Deniz Şahin
- **Numara**: 2221032838
- **Telefon**: 05424275482
- **E-posta**: dnsshnonline@gmail.com

## Proje
- **Ad**: Diyargezer FRP Karakter Yaratıcısı
- **Konu**: TTRPG karakter oluşturma, düzenleme, kaydetme ve bulut senkronizasyonu
- **Platform**: Masaüstü (PySide6) + Web (React + FastAPI)
- **Teknolojiler**: Python, React, FastAPI, SQLite, Zustand, ReportLab

## Desteklenen Sistemler

| Sistem | Masaüstü | Web | Durum |
|--------|----------|-----|-------|
| **Pathfinder 1e** | Evet | Evet (tam destek) | Aktif |
| **D&D 5e** | Evet | Donduruldu | Yakında Gelecek (web) |
| **Mutants & Masterminds 3e** | Evet | Donduruldu | Yakında Gelecek (web) |

## Özellikler

### Web Platformu (PF1e Odaklı)
- JWT kimlik doğrulama ve kullanıcı oturumu
- Karakter CRUD (oluştur, oku, güncelle, sil)
- Canlı kural hesaplama (BAB, saves, AC, skills)
- Seviye atlama sihirbazı ve geri alma
- Trait seçimi (80+ kategorize trait)
- Portre yükleme
- PDF export (pdf-lib)
- Masaüstü ile bulut senkronizasyonu (`POST /api/sync`)

### Masaüstü Uygulaması
- PySide6 Dark Fantasy GUI (The Tavern / The Forge / Character Sheet)
- Offline-first yerel SQLite veritabanı
- Arka plan bulut senkronizasyonu (JWT)
- Üç TTRPG sistemi desteği
- Encounter Tracker, Homebrew Yöneticisi, Portre Yönetimi
- PDF ve HTML export

### Paylaşılan Çekirdek
- `rules/` — Kural motoru ve doğrulama
- `data/characters.db` — SQLite entity veritabanı
- `utils/` — Export, hesaplama, homebrew, portre yardımcıları

## Kurulum

### Backend (FastAPI)
```bash
cd web/backend
pip install -r requirements.txt
python run.py
```

### Frontend (React + Vite)
```bash
cd web/frontend
npm install
npm run dev
```

### Masaüstü (PySide6)
```bash
pip install -r requirements.txt
python desktop/main_desktop.py
```

## Proje Yapısı

```
Diyargezenweb/
├── rules/                     # Paylaşılan kural motoru
│   ├── pf1e_rules.py
│   ├── character_manager.py
│   └── calculators.py
├── data/
│   ├── characters.db          # SQLite entity DB
│   └── pathfinder_1e_data.json
├── desktop/                   # PySide6 masaüstü uygulaması
│   ├── main_desktop.py
│   ├── gui/
│   ├── sync_engine.py
│   └── local_db.py
├── web/
│   ├── backend/               # FastAPI REST API
│   │   ├── app/
│   │   └── tests/
│   └── frontend/              # React karakter kağıdı
│       └── src/
├── creators/                  # Karakter oluşturucu factory
├── utils/                     # Export, hesaplama, homebrew
├── scraper/                   # PF1e veri toplama scriptleri
├── tests/                     # Kök seviye unit testler
└── docs/                      # Dokümantasyon
```

## Testler

```bash
# Tüm testler (kök + backend)
python -m pytest tests/ web/backend/tests/ -v

# Yalnızca backend API testleri
python -m pytest web/backend/tests/ -v
```

## API Özeti

| Endpoint | Açıklama |
|----------|----------|
| `POST /api/auth/login` | JWT giriş |
| `GET /api/systems` | Desteklenen sistemler |
| `GET /api/characters` | Karakter listesi |
| `POST /api/characters` | Yeni karakter |
| `POST /api/characters/recalculate` | Canlı hesaplama |
| `GET /api/rules/{system}/traits` | PF1e trait listesi |
| `POST /api/sync` | Masaüstü bulut senk |
