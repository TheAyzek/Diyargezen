# 🛡️ Diyargezen - Pathfinder 1e Karakter Yaratıcısı & Yöneticisi

> **Diyargezen**, Pathfinder 1st Edition (PF1e) masaüstü rol yapma oyunu (TTRPG) kural sistemini %100 yasal kurallarla uygulayan, çevrimdışı öncelikli (offline-first) masaüstü istemcisine ve bulut senkronizasyonlu web platformuna sahip gelişmiş bir karakter yönetim mimarisidir.

---

## 👨‍💻 Öğrenci & Geliştirici Bilgileri
- **Ad Soyad:** Deniz Şahin
- **Öğrenci No:** 2221032838
- **Telefon:** 05424275482
- **E-posta:** dnsshnonline@gmail.com
- **Repository:** [https://github.com/TheAyzek/Diyargezen](https://github.com/TheAyzek/Diyargezen)

---

## 🎯 Ürün Kapsamı & Temel Amaç (Product Scope)

- **Strict Scope:** Diyargezen **SADECE** bir **Pathfinder 1st Edition (PF1e) Karakter Yaratıcısı ve Yöneticisidir**.
- **Kapsam Dışı:** Uygulama bir VTT (Virtual Tabletop), harita motoru veya savaş simülatörü **DEĞİLDİR**.
- **Ana Odak Noktaları:**
  1. **%100 Yasal Karakter Oluşturma:** BAB, AC, Saves, Skill Ranks, Trait ve Feat modifikatörlerinin dinamik hesaplanması.
  2. **Seviye Atlatma Sihirbazı (Level-Up Wizard):** HP zarı, stat artışı (4, 8, 12, 16, 20), yetenek ve başarım dağıtım durum makinesi.
  3. **Soft-Block GM Esneklik Motoru:** Sert engeller yerine uyarılı yönlendirme ve `is_overridden` bayrağı ile GM takdirine saygı gösterilmesi.
  4. **Offline-First Senkronizasyon:** Çevrimdışı yerel SQLite WAL veritabanı, LWW (Last-Write-Wins) çakışma çözümü ve Tombstone Soft-Delete protokolü.
  5. **Canlı AcroForm PDF Export:** `pdf-lib` ve ReportLab ile 300ms debounced canlı PDF önizlemesi ve resmi Pathfinder 1e karakter kağıdı çıktısı.

---

## 🏛️ Mimari ve Bileşenler

```mermaid
graph TD
    subgraph Desktop ["Masaüstü İstemcisi (PySide6)"]
        GUI["Dark Fantasy PySide6 GUI"]
        LocalDB[("Yerel SQLite (WAL)")]
        SyncWorker["QThread Sync Engine"]
        GUI --> LocalDB
        GUI --> SyncWorker
    end

    subgraph Cloud ["Bulut Platformu (FastAPI + React)"]
        API["FastAPI REST Backend"]
        WebUI["React + Vite Frontend"]
        CloudDB[("SQLite Unified DB")]
        API --> CloudDB
        WebUI --> API
    end

    SyncWorker <-->|POST /api/sync (JWT + LWW)| API
```

### 1. Kural Motoru & Hesaplayıcılar (`rules/`)
- **`pf1e_rules.py`**: Karakter verilerini inceler; ırksal bonuslar, sınıf özellikleri, başarım önkoşulları ve trait kategori çakışmalarını doğrular. GM override bayrağı aktifse soft-block uyarılarını devre dışı bırakır.
- **`character_manager.py`**: Statik hesaplamaları yürütür (`calculate_stats`). Level-Up durum makinesi ile `calculate_level_up_slots` ve `apply_level_up` metodlarını sunar.
- **`calculators.py`**: Stat modifikatörü, yetenek puanı tabloları ve temelleri barındırır.

### 2. Çevrimdışı Senkronizasyon Motoru (`desktop/` & `web/backend/app/routers/sync.py`)
- **Çevrimdışı Öncelikli SQLite (`desktop/local_db.py`)**: Tüm karakterler ve oturum bilgileri yerel SQLite WAL veritabanında saklanır. Değişikliklerde `is_dirty = 1` olarak işaretlenir.
- **LWW Çakışma Çözümü**: İstemci ve sunucu güncellenme zaman damgaları (ISO-8601 UTC `datetime`) karşılaştırılır; en son yazılan veri geçerli sayılır.
- **Tombstone Soft Delete**: Çevrimdışı silinen karakterler silindi işareti (`is_deleted = 1`) alarak sunucuya bildirilir ve senkronizasyon el sıkışmasından sonra yerel veritabanından tamamen temizlenir.

### 3. Birleştirilmiş Veritabanı & İndeksleme (`db/` & `etl/`)
- **Foundry VTT + Scraper Fallback**: Pathfinder 1e veri seti Foundry VTT modüllerinden ve Scraper (d20pfsrd / AoNPRD) kaynaklarından harmanlanır.
- **Bileşik İndeksleme (Composite Indexing)**: `entities` tablosu üzerindeki `(sistem, kategori, isim)` indeksi sayesinde 15.000+ kural ögesinin arama yanıt süresi 10ms'nin altındadır.

---

## 🔒 Siber Güvenlik & Sistem Dayanıklılığı (SecOps)

- **CRLF Header Injection Koruması**: Karakter isimleri `_sanitize_filename` regex mantığı (`[^a-zA-Z0-9_\-]`) ile dezenfekte edilerek PDF indirme başlıklarında (`Content-Disposition`) kod enjeksiyonu ve Path Traversal zafiyetleri önlenir.
- **Hassas Veri Sızıntısı Koruması (Stack Trace Masking)**: FastAPI `main.py` üzerindeki global exception handler yakalanmamış 500 dahili sunucu hatalarında sunucu dosya yollarını istemciye sızdırmaz; hatayı güvenle loglar.
- **IDOR & Yetkilendirme Kontrolü**: Tüm karakter REST API uç noktalarında `_owned_character` kontrolü ile kullanıcıların sadece kendi karakterlerine erişebilmesi garanti edilir.
- **%100 Parametrik SQL**: Tüm SQLite veritabanı sorguları parametreleştirilmiş (`?`) bağlamda çalışır; SQL Enjeksiyonuna karşı korumalıdır.

---

## 🛠️ Kurulum & Çalıştırma

### Gereksinimler
- Python 3.10+
- Node.js 18+ (Web Frontend için)

### 1. Web Backend (FastAPI)
```bash
cd web/backend
pip install -r requirements.txt
python run.py
```
*API Swagger Dokümantasyonu: `http://localhost:8000/docs`*

### 2. Web Frontend (React + Vite)
```bash
cd web/frontend
npm install
npm run dev
```
*Arayüz Adresi: `http://localhost:5173`*

### 3. Masaüstü Uygulaması (PySide6)
```bash
pip install -r requirements.txt
python desktop/main_desktop.py
```

---

## 📦 Paketleme & Windows Kurulum Paketleri (Build & Installer)

Masaüstü PySide6 uygulaması bağımsız executable (`.exe`) ve Windows Kurucu (`Setup.exe`) paketlerine dönüştürülebilir:

### Standalone Executable (.exe) Derleme
```bash
python desktop/build_exe.py
```
*Çıktı Dizin: `dist/Diyargezen/Diyargezen.exe`*

### Windows Kurulum Paketi (InnoSetup Setup.exe & Portable ZIP)
```bash
python desktop/build_installer.py
```
*Çıktı Dizin: `dist/Diyargezen_Setup_v2.0.exe` ve `dist/Diyargezen_Portable_v2.0.zip`*

---

## 🧪 Test Çalıştırma

Tüm birim ve entegrasyon testleri Pytest ile yürütülür (%100 geçiş oranı, 281 geçen test):

```bash
# Tüm proje test kümesini çalıştır
.\.venv\Scripts\pytest.exe -v

# Özel backend ve güvenlik testlerini çalıştır
.\.venv\Scripts\pytest.exe web/backend/tests/ -v
```

---

## 📜 Lisans
Bu proje **Open Gaming License (OGL 1.0a)** ve **MIT Lisansı** altında geliştirilmiştir.
