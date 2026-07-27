# Sıradaki Görevler - Diyargezen

**Son Güncelleme:** 2026-07-27

---

## TAMAMLANAN (Web 2.0 Geçişi & PF1e Pivotu)

### Altyapı
1. **Masaüstü/Web Ayrımı** — `desktop/` ve `web/` dizinleri, paylaşılan `rules/` çekirdeği
2. **FastAPI Backend** — JWT auth, karakter CRUD, rules API, sync endpoint
3. **React Frontend** — Dashboard, auth, PF1e karakter kağıdı, Zustand state
4. **Offline-First Masaüstü** — Yerel SQLite, dirty queuing, BackgroundSyncThread
5. **Test Altyapısı** — 280 test geçiyor (2 skip)

### PF1e Web Özellikleri
6. **PF1e-Only Pivot** — Web'de yalnızca Pathfinder 1e aktif; D&D/M&M donduruldu
7. **Trait Sistemi & Entegrasyonu** — TraitSelectorModal, `/api/rules/{system}/traits`, seed script (50+ trait), recalculate bonus entegrasyonu (İnisiyatif, Kurtarma Zarları, Beceri & Sınıf Becerileri, ACP, AC)
8. **Feat Akışı** — FeatSelectorModal bileşeni ve slot kısıtlamalı feat yönetimi
9. **Seviye Atlama** — LevelUpWizard, level undo
10. **Portre Yükleme** — PortraitUpload bileşeni
11. **Git Commit** — Tüm PF1e pivot değişiklikleri ve kural geliştirmeleri commit edildi (`542ceb1e`)

---

## AÇIK GÖREVLER

### Ertelemede / Beklemede
1. **D&D 5e / M&M 3e web geri getirme** — Kullanıcı talimatı doğrultusunda aksini söyleyene kadar ertelendi.

### Yüksek Öncelik
2. **Deployment kılavuzu** — Production ortamı kurulum adımları

### Düşük Öncelik
3. **CI/CD** — GitHub Actions test pipeline
4. **Docker** — docker-compose ile tek komut kurulum
5. **API dokümantasyonu** — OpenAPI/Swagger genişletme

---

## PROJE DURUMU

| Bileşen | Durum |
|---------|-------|
| Masaüstü (3 sistem) | Tamamlanmış |
| Web backend | Çalışır, testli |
| Web frontend (PF1e) | Tamamlanmış & Commit Edilmiş (`542ceb1e`) |
| Web frontend (D&D/M&M) | Dondurulmuş (Beklemede) |
| Testler | 280 geçti, 2 skip |
| Dokümantasyon | Güncellendi (2026-07-27) |
