# 📋 SIRADAKI GÖREVLER - Diyargezen

**Son Güncelleme**: 2026-01-23  
**Durum**: ✅ GUI Özellikleri Korunuyor - **Sırada Ne Yapılacak?**

---

## ✅ SON TAMAMLANAN

- ✅ GUI Özellikleri Koruma Sistemi (7 dosya, 5 commit)
- ✅ Tüm 4 Sistem-Spesifik Kurallar Belgelendi
- ✅ Otomatik Kontrol Scriptleri (detaylı + simple)
- ✅ Geliştirici Rehberleri
- ✅ HTML Status Paneli

---

## 🔴 YÜKSEK ÖNCELİK (Kısa Vadede)

### 1. GUI Fonksiyonel Test ⭐ EN ÖNCELİKLİ
**Durum**: ⚠️ Restore edildi ama detaylı test yok  
**Yapılacak**:
- [ ] D&D 5e: Karakter oluştur → Kaydet → Yükle
- [ ] Pathfinder: Feat seçimi test et
- [ ] M&M: Power seçimi test et
- [ ] VtM: Klan seçimi test et
- [ ] Tüm sistemlerde PDF export test et

**Beklenen Süre**: 2-3 saat

---

### 2. D&D 5e Spell Scraping Tamamlanması
**Durum**: 📊 2469 spell var, tahmini 2084 daha var  
**Yapılacak**:
- [ ] Kalan ~2000 spell'i çek
- [ ] Spell data'sını validate et
- [ ] Duplicate check et
- [ ] dnd_data.json'ı finalize et

**Beklenen Süre**: 1-2 saat (background scraping)

---

### 3. Advanced Creator Özelliği
**Durum**: ❌ Silindi (GUI restore sırasında)  
**Yapılacak**:
- [ ] Step-by-step character creation dialog
- [ ] Spell seçimi (Spellcasters için)
- [ ] Feat seçimi (ASI seviyelerinde)
- [ ] Equipment seçimi
- [ ] Multi-select UI components

**Beklenen Süre**: 4-5 saat

---

## 🟡 ORTA ÖNCELİK (Gelecek Hafta)

### 4. Pathfinder Detaylı Test
**Durum**: ⚠️ Data var ama GUI test yok  
**Yapılacak**:
- [ ] Feat per level seçimi (1, 3, 5, 7, ...)
- [ ] Prestige class multiclassing
- [ ] Ability score progression
- [ ] Spell per day hesapları

**Beklenen Süre**: 2-3 saat

---

### 5. M&M Power System Testi
**Durum**: ⚠️ Power categories var ama detaylı test yok  
**Yapılacak**:
- [ ] Power Point allocation
- [ ] Extra/Flaw selection
- [ ] Power level calculations
- [ ] Power combinations

**Beklenen Süre**: 2 saat

---

### 6. VtM Discipline System Testi
**Durum**: ⚠️ Klan seçimi var ama Discipline yok  
**Yapılacak**:
- [ ] Discipline seçimi per klan
- [ ] Discipline power seçimi
- [ ] Blood Resonance sistem
- [ ] Klan-özgü mekanikler

**Beklenen Süre**: 1-2 saat

---

## 🟢 DÜŞÜK ÖNCELİK (Uzun Vadede)

### 7. Başka Sistem Entegrasyonu
**Durum**: ❌ Başlanmadı  
**Seçenekler**:
- [ ] Pathfinder 2e
- [ ] Starfinder
- [ ] Shadowrun
- [ ] Cyberpunk
- [ ] Powered by the Apocalypse (PbtA)

**Beklenen Süre**: Sistem başına 8-10 saat

---

### 8. Web Arayüzü (Django/FastAPI)
**Durum**: ❌ Başlanmadı  
**Yapılacak**:
- [ ] REST API oluştur
- [ ] React/Vue frontend
- [ ] Character cloud sync
- [ ] Multiplayer support

**Beklenen Süre**: 20-30 saat

---

### 9. Mobile App (Flutter/React Native)
**Durum**: ❌ Başlanmadı  
**Yapılacak**:
- [ ] iOS/Android app
- [ ] Offline support
- [ ] Push notifications

**Beklenen Süre**: 30-40 saat

---

## 📊 ÖNERİLEN ÇALIŞMA PLANI

### Bugün/Bu Hafta
1. **GUI Fonksiyonel Test** (2-3 saat)
   - Tüm 4 sistem karakteri test et
   - PDF export test et
   - Hata varsa logla

2. **D&D Spell Scraping** (1-2 saat - arka plan)
   - Kalan spell'leri çek
   - Validate et

### Gelecek Hafta
3. **Advanced Creator** (4-5 saat)
   - Step-by-step dialog
   - Spell/Feat/Equipment seçimi

4. **Sistem-Spesifik Detaylı Test** (5-7 saat)
   - Pathfinder, M&M, VtM test
   - Bugs fix et

---

## 📌 Açık Sorular

1. **GUI'de ne test etmek istiyorsun?**
   - Tüm 4 sistem mi?
   - Sadece D&D 5e mi?

2. **Advanced Creator'u geliştirmek mi?**
   - Step-by-step creation mi?
   - Başka özellik mi?

3. **Başka sistem eklemek mi?**
   - Pathfinder 2e mi?
   - Başka sistem mi?

---

**Sırada hangi görev olmasını istiyorsun?**