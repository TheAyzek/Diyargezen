# Sıradaki Adımlar - Diyargezen

**Son Güncelleme:** 2026-07-22
**Aktif Sistem:** Pathfinder 1e (web); D&D 5e + M&M 3e (masaüstü)

---

## Tamamlanan (Web 2.0)

- Masaüstü ve web ayrımı (`desktop/`, `web/`)
- FastAPI backend: JWT auth, karakter CRUD, rules API, sync endpoint
- React frontend: PF1e karakter kağıdı, dashboard, sistem seçici
- PF1e-only web pivot (D&D/M&M web arayüzünden kaldırıldı)
- PF1e trait sistemi (TraitSelectorModal, seed script, API endpoint)
- Masaüstü offline-first SQLite + BackgroundSyncThread
- PDF şablonları `web/frontend/public/templates/` altına taşındı
- Backend test altyapısı (httpx, 22 API testi)

## Devam Eden / Sıradaki

### Yüksek Öncelik
1. **Trait bonus hesaplama** — Seçilen trait'lerin initiative, save vb. bonuslarını recalculate'a entegre et
2. **PF1e feat seçimi** — EntitySelectorModal ile feat ekleme akışını tamamla
3. **Web PDF export** — Frontend pdf-lib ile client-side export doğrulama

### Orta Öncelik
4. **D&D 5e web geri getirme** — Veri dosyaları ve sheet bileşenlerini yeniden etkinleştir
5. **M&M 3e web geri getirme** — Aynı şekilde dondurulmuş sistemleri aç
6. **Dokümantasyon senkronizasyonu** — API referansı, deployment kılavuzu

### Düşük Öncelik
7. **CI pipeline** — GitHub Actions ile otomatik test
8. **Docker compose** — Tek komutla backend + frontend ayağa kaldırma
9. **Pydantic ConfigDict migration** — Deprecation uyarılarını gider

## Test Durumu

| Set | Sonuç |
|-----|-------|
| `tests/` (kök) | 255 geçti, 4 atlandı (D&D/M&M veri dosyası yok) |
| `web/backend/tests/` | 22 geçti |
