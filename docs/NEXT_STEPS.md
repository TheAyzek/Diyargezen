# Sıradaki Adımlar - Diyargezen

**Son Güncelleme:** 2026-07-27
**Aktif Sistem:** Pathfinder 1e (web); D&D 5e + M&M 3e (masaüstü)

---

## Tamamlanan (Web 2.0 & PF1e Pivotu)

- Masaüstü ve web ayrımı (`desktop/`, `web/`)
- FastAPI backend: JWT auth, karakter CRUD, rules API, sync endpoint
- React frontend: PF1e canlı karakter kağıdı, dashboard, sistem seçici
- PF1e-only web pivot (D&D/M&M web arayüzünden donduruldu/kaldırıldı)
- PF1e trait sistemi (TraitSelectorModal, 50+ trait seed script, API endpoint)
- PF1e trait bonus entegrasyonu (Initiative, saves, skills, class skills, ACP, AC `calculators.py` motorunda aktif)
- PF1e feat seçimi (FeatSelectorModal, `computeFeatSlots` slot kısıtlaması ile dynamic feat yönetimi)
- Web PDF export (Backend `pypdf` form dolgusu + frontend `exportPdf` indirme desteği)
- Masaüstü offline-first SQLite + BackgroundSyncThread
- PDF şablonları `web/frontend/public/templates/` altına taşındı
- Backend & Kural test altyapısı (280 test geçti, 2 atlandı)

## Devam Eden / Sıradaki

### Yüksek Öncelik (Tamamlandı)
- [x] **Trait bonus hesaplama** — Seçilen trait'lerin initiative, save, skill, ACP vb. bonusları recalculate'e entegre edildi.
- [x] **PF1e feat seçimi** — FeatSelectorModal bileşeni ve slot kısıtlamalı feat akışı tamamlandı.
- [x] **Web PDF export** — PDF export ve şablon doldurma altyapısı doğrulandı.

### Orta Öncelik (Dondurulmuş / Ertelendi)
- [ ] **D&D 5e web geri getirme** — Veri dosyaları ve sheet bileşenlerini yeniden etkinleştir (Kullanıcı talimatıyla beklemede).
- [ ] **M&M 3e web geri getirme** — Aynı şekilde dondurulmuş sistemleri aç (Kullanıcı talimatıyla beklemede).
- [ ] **Dokümantasyon senkronizasyonu** — API referansı, deployment kılavuzu.

### Düşük Öncelik (Açık Görevler)
- [ ] **CI pipeline** — GitHub Actions ile otomatik test
- [ ] **Docker compose** — Tek komutla backend + frontend ayağa kaldırma
- [ ] **Pydantic ConfigDict migration** — Deprecation uyarılarını gider (`class Config` -> `model_config = ConfigDict(...)`)

## Test Durumu

| Set | Sonuç |
|-----|-------|
| Test Suiti (Tüm Testler) | 280 geçti, 2 atlandı |
| Backend & Rules Testleri | Tamamı aktif ve yeşil |
