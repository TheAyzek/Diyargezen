# Sıradaki Görevler - Diyargezen

**Son Güncelleme:** 2026-07-22

---

## TAMAMLANAN (Web 2.0 Geçişi)

### Altyapı
1. **Masaüstü/Web Ayrımı** — `desktop/` ve `web/` dizinleri, paylaşılan `rules/` çekirdeği
2. **FastAPI Backend** — JWT auth, karakter CRUD, rules API, sync endpoint
3. **React Frontend** — Dashboard, auth, PF1e karakter kağıdı, Zustand state
4. **Offline-First Masaüstü** — Yerel SQLite, dirty queuing, BackgroundSyncThread
5. **Test Altyapısı** — httpx eklendi, 277 test geçiyor (4 skip)

### PF1e Web Özellikleri
6. **PF1e-Only Pivot** — Web'de yalnızca Pathfinder 1e aktif; D&D/M&M donduruldu
7. **Trait Sistemi** — TraitSelectorModal, `/api/rules/{system}/traits`, seed script (80+ trait)
8. **Seviye Atlama** — LevelUpWizard, level undo
9. **Portre Yükleme** — PortraitUpload bileşeni
10. **PDF Şablonları** — `web/frontend/public/templates/` altına taşındı

### Masaüstü (Önceki Sürüm — Hâlâ Aktif)
- 3 TTRPG sistemi karakter oluşturma
- Multiclassing, spell browser, encounter tracker
- Homebrew yöneticisi, portre yönetimi
- PDF/HTML export

---

## AÇIK GÖREVLER

### Yüksek Öncelik
1. **Trait bonus entegrasyonu** — Seçilen trait'lerin recalculate çıktısına yansıması
2. **PF1e feat akışı** — EntitySelectorModal ile çoklu feat seçimi
3. **Commit** — PF1e pivot değişikliklerini commit'le (kullanıcı isteğine bağlı)

### Orta Öncelik
4. **D&D 5e web geri getirme** — `dnd_data.json` + sheet bileşenleri
5. **M&M 3e web geri getirme** — `mm_data.json` + sheet bileşenleri
6. **Deployment kılavuzu** — Production ortamı kurulum adımları

### Düşük Öncelik
7. **CI/CD** — GitHub Actions test pipeline
8. **Docker** — docker-compose ile tek komut kurulum
9. **API dokümantasyonu** — OpenAPI/Swagger genişletme

---

## PROJE DURUMU

| Bileşen | Durum |
|---------|-------|
| Masaüstü (3 sistem) | Tamamlanmış |
| Web backend | Çalışır, testli |
| Web frontend (PF1e) | Aktif geliştirme, commit edilmemiş |
| Web frontend (D&D/M&M) | Dondurulmuş |
| Testler | 277 geçti, 4 skip |
| Dokümantasyon | Güncellendi (2026-07-22) |
