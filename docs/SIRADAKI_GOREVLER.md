# Sıradaki Görevler - Diyargezen

**Son Güncelleme:** 2026-07-28

---

## TAMAMLANAN (Web 2.0 Geçişi & PF1e Pivotu & DevOps)

### Altyapı
1. **Masaüstü/Web Ayrımı** — `desktop/` ve `web/` dizinleri, paylaşılan `rules/` çekirdeği
2. **FastAPI Backend** — JWT auth, karakter CRUD, rules API, sync endpoint
3. **React Frontend** — Dashboard, auth, PF1e karakter kağıdı, Zustand state
4. **Offline-First Masaüstü** — Yerel SQLite, dirty queuing, BackgroundSyncThread
5. **Test Altyapısı** — 280+ test geçiyor (2 skip)

### PF1e Web & Masaüstü Tasarım Özellikleri
6. **PF1e-Only Pivot** — Web'de yalnızca Pathfinder 1e aktif; D&D/M&M donduruldu
7. **Trait Sistemi & Entegrasyonu** — TraitSelectorModal, `/api/rules/{system}/traits`, seed script (50+ trait), recalculate bonus entegrasyonu (İnisiyatif, Kurtarma Zarları, Beceri & Sınıf Becerileri, ACP, AC)
8. **Feat Akışı** — FeatSelectorModal bileşeni ve slot kısıtlamalı feat yönetimi
9. **Seviye Atlama** — LevelUpWizard, level undo
10. **Portre Yükleme** — PortraitUpload bileşeni
11. **Masaüstü & Web Tasarım Senkronizasyonu** — Custom Google fontları (`Cinzel`, `EB Garamond`, `DM Mono`) PySide6 `QFontDatabase` katmanına yüklendi, `DARK_FANTASY_QSS` teması `index.css` renk paleti (`#0f0f1a`, `#e6c567`, `#1e1e36`, 12px glass-card yapısı) ile eşlendi.

### DevOps & Dağıtım Altyapısı
12. **Docker Konteynerizasyon** — FastAPI Backend + React Nginx Multi-Stage Frontend + SQLite kalıcılığı ile tek komutlu `docker-compose.yml` altyapısı kuruldu.
13. **CI/CD Pipeline** — `.github/workflows/ci.yml` ile Python Pytest suite, React build kontrolü ve Docker Compose doğrulaması otomatilleştirildi.
14. **Production Deployment Kılavuzu** — `docs/DEPLOYMENT.md` ile SSL Certbot, Nginx reverse proxy, systemd servis ve crontab otomatik veritabanı yedekleme kılavuzu oluşturuldu.

---

## AÇIK GÖREVLER

### Ertelemede / Beklemede
1. **D&D 5e / M&M 3e web geri getirme** — Kullanıcı talimatı doğrultusunda aksini söyleyene kadar ertelendi.

### Gelecek İyileştirmeler
2. **API Dokümantasyonu Genişletme** — OpenAPI/Swagger detaylı şemaları
3. **PWA / Mobil Desteği** — PWA manifest ve offline service worker

---

## PROJE DURUMU

| Bileşen | Durum |
|---------|-------|
| Masaüstü (PF1e + High Fantasy UI) | Tamamlanmış (Web ile %100 Tasarım Eşitliği) |
| Web Backend (FastAPI) | Çalışır, Testli & Dockerized |
| Web Frontend (PF1e) | Tamamlanmış, Dockerized & Nginx Proxy |
| CI/CD Pipeline | Tamamlanmış (`ci.yml`) |
| Deployment Dokümantasyonu | Tamamlanmış (`docs/DEPLOYMENT.md`) |
| Testler | 280+ geçti, 2 skip |
| Dokümantasyon | Güncellendi (2026-07-28) |
