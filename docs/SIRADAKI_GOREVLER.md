# Sıradaki Görevler - Diyargezen

**Son Güncelleme:** 2025-01-XX  
**Tamamlanan Görevler:** D&D 5e Veri Güncelleme, Test ve Hata Düzeltme

---

## ✅ Tamamlanan Görevler

1. **D&D 5e Veri Güncelleme** ✅
   - Classes: 13 class cache'de
   - Races: 9 race çekildi (33 toplam)
   - Feats: 1258 feat cache'de
   - Equipment: 243 item cache'de
   - Backgrounds: 57 background mevcut

2. **Test ve Hata Düzeltme** ✅
   - 5 test suite eklendi
   - 20+ test case
   - %95+ başarı oranı
   - Veri doğrulama testleri eklendi
   - Export/Import testleri eklendi

---

## 🎯 Sıradaki Görevler (Öncelik Sırasına Göre)

### 🔴 Yüksek Öncelik (Kısa Vadede - Bu Hafta)

#### 1. Veri Kalitesi İyileştirmeleri
**Durum:** ⚠️ Testlerde sorunlar tespit edildi  
**Öncelik:** 🔴 Yüksek  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- Race subrace'lerde `name` alanı eksik (24 sorun) - Düzelt
- Class'larda `hit_dice` alanı eksik (17 sorun) - Düzelt
- Spell'lerde geçersiz level değerleri (81 sorun) - Filtrele/validasyon

**Fayda:** Veri kalitesi artar, testler daha güvenilir olur

---

#### 2. Spell Sistemi İyileştirmeleri
**Durum:** ⚠️ Temel seviye var  
**Öncelik:** 🟡 Orta-Yüksek  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- **Spell Upcasting** - Daha yüksek seviyeli slot ile cast (damage artışı hesaplama)
- **Ritual Casting tracking** - Ritual spell'leri takip etme
- **Concentration tracking** - Concentration spell'leri takip etme
- **Material Components inventory** - Material component gereksinimlerini takip etme

**Fayda:** Spellcaster kullanıcıları için çok faydalı, D&D 5e kurallarını daha iyi destekler

---

#### 3. Equipment Yönetimi İyileştirmeleri
**Durum:** ✅ Temel var  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- **Magic Items bonusları** - AC, Attack, Damage bonusları hesaplama
- **Attunement tracking** - Attunement limit (3 item) takibi
- **Equipment Comparison** - İki ekipmanı karşılaştırma
- **Encumbrance Details** - Daha detaylı encumbrance hesaplama

**Fayda:** Equipment yönetimi daha kullanışlı olur

---

### 🟡 Orta Öncelik (Orta Vadede - Gelecek Hafta)

#### 4. PDF Export İyileştirmeleri
**Durum:** ✅ Çalışıyor  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 4-5 saat

**Yapılacaklar:**
- **PDF Layout iyileştirmeleri** - Daha iyi düzen, okunabilirlik
- **PDF Templates** - Farklı şablon seçenekleri
- **PDF Spell Sheet** - Ayrı spell sayfası
- **PDF Customization** - Özelleştirilebilir PDF

**Fayda:** Export kalitesi artar, kullanıcı memnuniyeti artar

---

#### 5. Karakter İstatistikleri İyileştirmeleri
**Durum:** ✅ Temel var  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- **Speed Modifiers** - Feats ve spells'den gelen speed modifier'ları (kısmen eklendi)
- **Skill Check Modifiers** - Skill check modifier'ları (expertise, jack of all trades, vb.)
- **Carrying Capacity detaylı hesaplama** - Strength * 15, encumbrance rules
- **Jump Distance hesaplama** - Long jump, high jump

**Fayda:** İstatistik hesaplamaları daha doğru olur

---

### 🟢 Düşük Öncelik (Uzun Vadede - İleride)

#### 6. Pathfinder 1e Spell Scraping
**Durum:** ⚠️ Parsing iyileştirildi ama tam scraping yok  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 4-6 saat

**Yapılacaklar:**
- Tam spell scraping (Archives of Nethys, d20pfsrd)
- Spell parsing iyileştirmeleri
- GUI entegrasyonu

---

#### 7. Veri Doğrulama ve Validasyon
**Durum:** ⚠️ Temel var  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- Rule Validation - D&D 5e kurallarına uygunluk kontrolü
- Data Integrity Check - Veri bütünlüğü kontrolü
- Character Validation - Karakter veri doğrulama

---

#### 8. Multiclassing
**Durum:** ❌ Eksik  
**Öncelik:** 🟢 Düşük (karmaşık)  
**Tahmini Süre:** 10-15 saat

**Not:** Karmaşık, şimdilik skip edilebilir

---

#### 9. Karakter Karşılaştırma
**Durum:** ⚠️ Temel var  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- Side-by-Side Comparison
- Statistics Graph

---

## 📋 Öncelik Sırası Özet

### Bu Hafta (Yüksek Öncelik)
1. **Veri Kalitesi İyileştirmeleri** (2-3 saat) - Testlerde tespit edilen sorunları düzelt
2. **Spell Sistemi İyileştirmeleri** (3-4 saat) - Upcasting, Ritual, Concentration
3. **Equipment Yönetimi İyileştirmeleri** (3-4 saat) - Magic items, Attunement

**Toplam:** ~8-11 saat

### Gelecek Hafta (Orta Öncelik)
4. **PDF Export İyileştirmeleri** (4-5 saat)
5. **Karakter İstatistikleri İyileştirmeleri** (2-3 saat)

**Toplam:** ~6-8 saat

### İleride (Düşük Öncelik)
6. **Pathfinder 1e Spell Scraping** (4-6 saat)
7. **Veri Doğrulama ve Validasyon** (2-3 saat)
8. **Multiclassing** (10-15 saat - skip edilebilir)
9. **Karakter Karşılaştırma** (3-4 saat)

---

## 🎯 Önerilen Sonraki Adım

**En Öncelikli:** Veri Kalitesi İyileştirmeleri

**Sebep:**
- Testlerde tespit edilen sorunlar var
- Veri kalitesi artarsa diğer sistemler daha güvenilir olur
- Nispeten hızlı tamamlanabilir (2-3 saat)

**Yapılacaklar:**
1. Race subrace name alanlarını doldur
2. Class hit_dice alanlarını doldur
3. Spell level validation ekle

**Başlangıç:**
```bash
# Veri kalitesi düzeltmeleri için script oluştur
# veya mevcut scraping scriptlerini güncelle
```

---

## 📊 Mevcut Durum

**Tamamlanma Oranı:** ~%90

**Tamamlanan:**
- ✅ Karakter oluşturma sistemi
- ✅ Level up sistemi
- ✅ Spell sistemi (temel)
- ✅ Equipment yönetimi (temel)
- ✅ PDF export (temel)
- ✅ Test sistemi (20+ test case)
- ✅ D&D 5e veri güncelleme (scraping)

**Eksikler:**
- ⚠️ Veri kalitesi iyileştirmeleri (testlerde tespit edilen sorunlar)
- ⚠️ Spell sistemi iyileştirmeleri (Upcasting, Ritual, Concentration)
- ⚠️ Equipment yönetimi iyileştirmeleri (Magic items, Attunement)
- ⚠️ GUI testleri (PySide6/Qt)
- ⚠️ PDF export iyileştirmeleri

---

**Sonraki Adım:** Veri Kalitesi İyileştirmeleri ile başla



**Son Güncelleme:** 2025-01-XX  
**Tamamlanan Görevler:** D&D 5e Veri Güncelleme, Test ve Hata Düzeltme

---

## ✅ Tamamlanan Görevler

1. **D&D 5e Veri Güncelleme** ✅
   - Classes: 13 class cache'de
   - Races: 9 race çekildi (33 toplam)
   - Feats: 1258 feat cache'de
   - Equipment: 243 item cache'de
   - Backgrounds: 57 background mevcut

2. **Test ve Hata Düzeltme** ✅
   - 5 test suite eklendi
   - 20+ test case
   - %95+ başarı oranı
   - Veri doğrulama testleri eklendi
   - Export/Import testleri eklendi

---

## 🎯 Sıradaki Görevler (Öncelik Sırasına Göre)

### 🔴 Yüksek Öncelik (Kısa Vadede - Bu Hafta)

#### 1. Veri Kalitesi İyileştirmeleri
**Durum:** ⚠️ Testlerde sorunlar tespit edildi  
**Öncelik:** 🔴 Yüksek  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- Race subrace'lerde `name` alanı eksik (24 sorun) - Düzelt
- Class'larda `hit_dice` alanı eksik (17 sorun) - Düzelt
- Spell'lerde geçersiz level değerleri (81 sorun) - Filtrele/validasyon

**Fayda:** Veri kalitesi artar, testler daha güvenilir olur

---

#### 2. Spell Sistemi İyileştirmeleri
**Durum:** ⚠️ Temel seviye var  
**Öncelik:** 🟡 Orta-Yüksek  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- **Spell Upcasting** - Daha yüksek seviyeli slot ile cast (damage artışı hesaplama)
- **Ritual Casting tracking** - Ritual spell'leri takip etme
- **Concentration tracking** - Concentration spell'leri takip etme
- **Material Components inventory** - Material component gereksinimlerini takip etme

**Fayda:** Spellcaster kullanıcıları için çok faydalı, D&D 5e kurallarını daha iyi destekler

---

#### 3. Equipment Yönetimi İyileştirmeleri
**Durum:** ✅ Temel var  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- **Magic Items bonusları** - AC, Attack, Damage bonusları hesaplama
- **Attunement tracking** - Attunement limit (3 item) takibi
- **Equipment Comparison** - İki ekipmanı karşılaştırma
- **Encumbrance Details** - Daha detaylı encumbrance hesaplama

**Fayda:** Equipment yönetimi daha kullanışlı olur

---

### 🟡 Orta Öncelik (Orta Vadede - Gelecek Hafta)

#### 4. PDF Export İyileştirmeleri
**Durum:** ✅ Çalışıyor  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 4-5 saat

**Yapılacaklar:**
- **PDF Layout iyileştirmeleri** - Daha iyi düzen, okunabilirlik
- **PDF Templates** - Farklı şablon seçenekleri
- **PDF Spell Sheet** - Ayrı spell sayfası
- **PDF Customization** - Özelleştirilebilir PDF

**Fayda:** Export kalitesi artar, kullanıcı memnuniyeti artar

---

#### 5. Karakter İstatistikleri İyileştirmeleri
**Durum:** ✅ Temel var  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- **Speed Modifiers** - Feats ve spells'den gelen speed modifier'ları (kısmen eklendi)
- **Skill Check Modifiers** - Skill check modifier'ları (expertise, jack of all trades, vb.)
- **Carrying Capacity detaylı hesaplama** - Strength * 15, encumbrance rules
- **Jump Distance hesaplama** - Long jump, high jump

**Fayda:** İstatistik hesaplamaları daha doğru olur

---

### 🟢 Düşük Öncelik (Uzun Vadede - İleride)

#### 6. Pathfinder 1e Spell Scraping
**Durum:** ⚠️ Parsing iyileştirildi ama tam scraping yok  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 4-6 saat

**Yapılacaklar:**
- Tam spell scraping (Archives of Nethys, d20pfsrd)
- Spell parsing iyileştirmeleri
- GUI entegrasyonu

---

#### 7. Veri Doğrulama ve Validasyon
**Durum:** ⚠️ Temel var  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- Rule Validation - D&D 5e kurallarına uygunluk kontrolü
- Data Integrity Check - Veri bütünlüğü kontrolü
- Character Validation - Karakter veri doğrulama

---

#### 8. Multiclassing
**Durum:** ❌ Eksik  
**Öncelik:** 🟢 Düşük (karmaşık)  
**Tahmini Süre:** 10-15 saat

**Not:** Karmaşık, şimdilik skip edilebilir

---

#### 9. Karakter Karşılaştırma
**Durum:** ⚠️ Temel var  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- Side-by-Side Comparison
- Statistics Graph

---

## 📋 Öncelik Sırası Özet

### Bu Hafta (Yüksek Öncelik)
1. **Veri Kalitesi İyileştirmeleri** (2-3 saat) - Testlerde tespit edilen sorunları düzelt
2. **Spell Sistemi İyileştirmeleri** (3-4 saat) - Upcasting, Ritual, Concentration
3. **Equipment Yönetimi İyileştirmeleri** (3-4 saat) - Magic items, Attunement

**Toplam:** ~8-11 saat

### Gelecek Hafta (Orta Öncelik)
4. **PDF Export İyileştirmeleri** (4-5 saat)
5. **Karakter İstatistikleri İyileştirmeleri** (2-3 saat)

**Toplam:** ~6-8 saat

### İleride (Düşük Öncelik)
6. **Pathfinder 1e Spell Scraping** (4-6 saat)
7. **Veri Doğrulama ve Validasyon** (2-3 saat)
8. **Multiclassing** (10-15 saat - skip edilebilir)
9. **Karakter Karşılaştırma** (3-4 saat)

---

## 🎯 Önerilen Sonraki Adım

**En Öncelikli:** Veri Kalitesi İyileştirmeleri

**Sebep:**
- Testlerde tespit edilen sorunlar var
- Veri kalitesi artarsa diğer sistemler daha güvenilir olur
- Nispeten hızlı tamamlanabilir (2-3 saat)

**Yapılacaklar:**
1. Race subrace name alanlarını doldur
2. Class hit_dice alanlarını doldur
3. Spell level validation ekle

**Başlangıç:**
```bash
# Veri kalitesi düzeltmeleri için script oluştur
# veya mevcut scraping scriptlerini güncelle
```

---

## 📊 Mevcut Durum

**Tamamlanma Oranı:** ~%90

**Tamamlanan:**
- ✅ Karakter oluşturma sistemi
- ✅ Level up sistemi
- ✅ Spell sistemi (temel)
- ✅ Equipment yönetimi (temel)
- ✅ PDF export (temel)
- ✅ Test sistemi (20+ test case)
- ✅ D&D 5e veri güncelleme (scraping)

**Eksikler:**
- ⚠️ Veri kalitesi iyileştirmeleri (testlerde tespit edilen sorunlar)
- ⚠️ Spell sistemi iyileştirmeleri (Upcasting, Ritual, Concentration)
- ⚠️ Equipment yönetimi iyileştirmeleri (Magic items, Attunement)
- ⚠️ GUI testleri (PySide6/Qt)
- ⚠️ PDF export iyileştirmeleri

---

**Sonraki Adım:** Veri Kalitesi İyileştirmeleri ile başla





**Son Güncelleme:** 2025-01-XX  
**Tamamlanan Görevler:** D&D 5e Veri Güncelleme, Test ve Hata Düzeltme

---

## ✅ Tamamlanan Görevler

1. **D&D 5e Veri Güncelleme** ✅
   - Classes: 13 class cache'de
   - Races: 9 race çekildi (33 toplam)
   - Feats: 1258 feat cache'de
   - Equipment: 243 item cache'de
   - Backgrounds: 57 background mevcut

2. **Test ve Hata Düzeltme** ✅
   - 5 test suite eklendi
   - 20+ test case
   - %95+ başarı oranı
   - Veri doğrulama testleri eklendi
   - Export/Import testleri eklendi

---

## 🎯 Sıradaki Görevler (Öncelik Sırasına Göre)

### 🔴 Yüksek Öncelik (Kısa Vadede - Bu Hafta)

#### 1. Veri Kalitesi İyileştirmeleri
**Durum:** ⚠️ Testlerde sorunlar tespit edildi  
**Öncelik:** 🔴 Yüksek  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- Race subrace'lerde `name` alanı eksik (24 sorun) - Düzelt
- Class'larda `hit_dice` alanı eksik (17 sorun) - Düzelt
- Spell'lerde geçersiz level değerleri (81 sorun) - Filtrele/validasyon

**Fayda:** Veri kalitesi artar, testler daha güvenilir olur

---

#### 2. Spell Sistemi İyileştirmeleri
**Durum:** ⚠️ Temel seviye var  
**Öncelik:** 🟡 Orta-Yüksek  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- **Spell Upcasting** - Daha yüksek seviyeli slot ile cast (damage artışı hesaplama)
- **Ritual Casting tracking** - Ritual spell'leri takip etme
- **Concentration tracking** - Concentration spell'leri takip etme
- **Material Components inventory** - Material component gereksinimlerini takip etme

**Fayda:** Spellcaster kullanıcıları için çok faydalı, D&D 5e kurallarını daha iyi destekler

---

#### 3. Equipment Yönetimi İyileştirmeleri
**Durum:** ✅ Temel var  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- **Magic Items bonusları** - AC, Attack, Damage bonusları hesaplama
- **Attunement tracking** - Attunement limit (3 item) takibi
- **Equipment Comparison** - İki ekipmanı karşılaştırma
- **Encumbrance Details** - Daha detaylı encumbrance hesaplama

**Fayda:** Equipment yönetimi daha kullanışlı olur

---

### 🟡 Orta Öncelik (Orta Vadede - Gelecek Hafta)

#### 4. PDF Export İyileştirmeleri
**Durum:** ✅ Çalışıyor  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 4-5 saat

**Yapılacaklar:**
- **PDF Layout iyileştirmeleri** - Daha iyi düzen, okunabilirlik
- **PDF Templates** - Farklı şablon seçenekleri
- **PDF Spell Sheet** - Ayrı spell sayfası
- **PDF Customization** - Özelleştirilebilir PDF

**Fayda:** Export kalitesi artar, kullanıcı memnuniyeti artar

---

#### 5. Karakter İstatistikleri İyileştirmeleri
**Durum:** ✅ Temel var  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- **Speed Modifiers** - Feats ve spells'den gelen speed modifier'ları (kısmen eklendi)
- **Skill Check Modifiers** - Skill check modifier'ları (expertise, jack of all trades, vb.)
- **Carrying Capacity detaylı hesaplama** - Strength * 15, encumbrance rules
- **Jump Distance hesaplama** - Long jump, high jump

**Fayda:** İstatistik hesaplamaları daha doğru olur

---

### 🟢 Düşük Öncelik (Uzun Vadede - İleride)

#### 6. Pathfinder 1e Spell Scraping
**Durum:** ⚠️ Parsing iyileştirildi ama tam scraping yok  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 4-6 saat

**Yapılacaklar:**
- Tam spell scraping (Archives of Nethys, d20pfsrd)
- Spell parsing iyileştirmeleri
- GUI entegrasyonu

---

#### 7. Veri Doğrulama ve Validasyon
**Durum:** ⚠️ Temel var  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- Rule Validation - D&D 5e kurallarına uygunluk kontrolü
- Data Integrity Check - Veri bütünlüğü kontrolü
- Character Validation - Karakter veri doğrulama

---

#### 8. Multiclassing
**Durum:** ❌ Eksik  
**Öncelik:** 🟢 Düşük (karmaşık)  
**Tahmini Süre:** 10-15 saat

**Not:** Karmaşık, şimdilik skip edilebilir

---

#### 9. Karakter Karşılaştırma
**Durum:** ⚠️ Temel var  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- Side-by-Side Comparison
- Statistics Graph

---

## 📋 Öncelik Sırası Özet

### Bu Hafta (Yüksek Öncelik)
1. **Veri Kalitesi İyileştirmeleri** (2-3 saat) - Testlerde tespit edilen sorunları düzelt
2. **Spell Sistemi İyileştirmeleri** (3-4 saat) - Upcasting, Ritual, Concentration
3. **Equipment Yönetimi İyileştirmeleri** (3-4 saat) - Magic items, Attunement

**Toplam:** ~8-11 saat

### Gelecek Hafta (Orta Öncelik)
4. **PDF Export İyileştirmeleri** (4-5 saat)
5. **Karakter İstatistikleri İyileştirmeleri** (2-3 saat)

**Toplam:** ~6-8 saat

### İleride (Düşük Öncelik)
6. **Pathfinder 1e Spell Scraping** (4-6 saat)
7. **Veri Doğrulama ve Validasyon** (2-3 saat)
8. **Multiclassing** (10-15 saat - skip edilebilir)
9. **Karakter Karşılaştırma** (3-4 saat)

---

## 🎯 Önerilen Sonraki Adım

**En Öncelikli:** Veri Kalitesi İyileştirmeleri

**Sebep:**
- Testlerde tespit edilen sorunlar var
- Veri kalitesi artarsa diğer sistemler daha güvenilir olur
- Nispeten hızlı tamamlanabilir (2-3 saat)

**Yapılacaklar:**
1. Race subrace name alanlarını doldur
2. Class hit_dice alanlarını doldur
3. Spell level validation ekle

**Başlangıç:**
```bash
# Veri kalitesi düzeltmeleri için script oluştur
# veya mevcut scraping scriptlerini güncelle
```

---

## 📊 Mevcut Durum

**Tamamlanma Oranı:** ~%90

**Tamamlanan:**
- ✅ Karakter oluşturma sistemi
- ✅ Level up sistemi
- ✅ Spell sistemi (temel)
- ✅ Equipment yönetimi (temel)
- ✅ PDF export (temel)
- ✅ Test sistemi (20+ test case)
- ✅ D&D 5e veri güncelleme (scraping)

**Eksikler:**
- ⚠️ Veri kalitesi iyileştirmeleri (testlerde tespit edilen sorunlar)
- ⚠️ Spell sistemi iyileştirmeleri (Upcasting, Ritual, Concentration)
- ⚠️ Equipment yönetimi iyileştirmeleri (Magic items, Attunement)
- ⚠️ GUI testleri (PySide6/Qt)
- ⚠️ PDF export iyileştirmeleri

---

**Sonraki Adım:** Veri Kalitesi İyileştirmeleri ile başla



**Son Güncelleme:** 2025-01-XX  
**Tamamlanan Görevler:** D&D 5e Veri Güncelleme, Test ve Hata Düzeltme

---

## ✅ Tamamlanan Görevler

1. **D&D 5e Veri Güncelleme** ✅
   - Classes: 13 class cache'de
   - Races: 9 race çekildi (33 toplam)
   - Feats: 1258 feat cache'de
   - Equipment: 243 item cache'de
   - Backgrounds: 57 background mevcut

2. **Test ve Hata Düzeltme** ✅
   - 5 test suite eklendi
   - 20+ test case
   - %95+ başarı oranı
   - Veri doğrulama testleri eklendi
   - Export/Import testleri eklendi

---

## 🎯 Sıradaki Görevler (Öncelik Sırasına Göre)

### 🔴 Yüksek Öncelik (Kısa Vadede - Bu Hafta)

#### 1. Veri Kalitesi İyileştirmeleri
**Durum:** ⚠️ Testlerde sorunlar tespit edildi  
**Öncelik:** 🔴 Yüksek  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- Race subrace'lerde `name` alanı eksik (24 sorun) - Düzelt
- Class'larda `hit_dice` alanı eksik (17 sorun) - Düzelt
- Spell'lerde geçersiz level değerleri (81 sorun) - Filtrele/validasyon

**Fayda:** Veri kalitesi artar, testler daha güvenilir olur

---

#### 2. Spell Sistemi İyileştirmeleri
**Durum:** ⚠️ Temel seviye var  
**Öncelik:** 🟡 Orta-Yüksek  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- **Spell Upcasting** - Daha yüksek seviyeli slot ile cast (damage artışı hesaplama)
- **Ritual Casting tracking** - Ritual spell'leri takip etme
- **Concentration tracking** - Concentration spell'leri takip etme
- **Material Components inventory** - Material component gereksinimlerini takip etme

**Fayda:** Spellcaster kullanıcıları için çok faydalı, D&D 5e kurallarını daha iyi destekler

---

#### 3. Equipment Yönetimi İyileştirmeleri
**Durum:** ✅ Temel var  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- **Magic Items bonusları** - AC, Attack, Damage bonusları hesaplama
- **Attunement tracking** - Attunement limit (3 item) takibi
- **Equipment Comparison** - İki ekipmanı karşılaştırma
- **Encumbrance Details** - Daha detaylı encumbrance hesaplama

**Fayda:** Equipment yönetimi daha kullanışlı olur

---

### 🟡 Orta Öncelik (Orta Vadede - Gelecek Hafta)

#### 4. PDF Export İyileştirmeleri
**Durum:** ✅ Çalışıyor  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 4-5 saat

**Yapılacaklar:**
- **PDF Layout iyileştirmeleri** - Daha iyi düzen, okunabilirlik
- **PDF Templates** - Farklı şablon seçenekleri
- **PDF Spell Sheet** - Ayrı spell sayfası
- **PDF Customization** - Özelleştirilebilir PDF

**Fayda:** Export kalitesi artar, kullanıcı memnuniyeti artar

---

#### 5. Karakter İstatistikleri İyileştirmeleri
**Durum:** ✅ Temel var  
**Öncelik:** 🟡 Orta  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- **Speed Modifiers** - Feats ve spells'den gelen speed modifier'ları (kısmen eklendi)
- **Skill Check Modifiers** - Skill check modifier'ları (expertise, jack of all trades, vb.)
- **Carrying Capacity detaylı hesaplama** - Strength * 15, encumbrance rules
- **Jump Distance hesaplama** - Long jump, high jump

**Fayda:** İstatistik hesaplamaları daha doğru olur

---

### 🟢 Düşük Öncelik (Uzun Vadede - İleride)

#### 6. Pathfinder 1e Spell Scraping
**Durum:** ⚠️ Parsing iyileştirildi ama tam scraping yok  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 4-6 saat

**Yapılacaklar:**
- Tam spell scraping (Archives of Nethys, d20pfsrd)
- Spell parsing iyileştirmeleri
- GUI entegrasyonu

---

#### 7. Veri Doğrulama ve Validasyon
**Durum:** ⚠️ Temel var  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 2-3 saat

**Yapılacaklar:**
- Rule Validation - D&D 5e kurallarına uygunluk kontrolü
- Data Integrity Check - Veri bütünlüğü kontrolü
- Character Validation - Karakter veri doğrulama

---

#### 8. Multiclassing
**Durum:** ❌ Eksik  
**Öncelik:** 🟢 Düşük (karmaşık)  
**Tahmini Süre:** 10-15 saat

**Not:** Karmaşık, şimdilik skip edilebilir

---

#### 9. Karakter Karşılaştırma
**Durum:** ⚠️ Temel var  
**Öncelik:** 🟢 Düşük  
**Tahmini Süre:** 3-4 saat

**Yapılacaklar:**
- Side-by-Side Comparison
- Statistics Graph

---

## 📋 Öncelik Sırası Özet

### Bu Hafta (Yüksek Öncelik)
1. **Veri Kalitesi İyileştirmeleri** (2-3 saat) - Testlerde tespit edilen sorunları düzelt
2. **Spell Sistemi İyileştirmeleri** (3-4 saat) - Upcasting, Ritual, Concentration
3. **Equipment Yönetimi İyileştirmeleri** (3-4 saat) - Magic items, Attunement

**Toplam:** ~8-11 saat

### Gelecek Hafta (Orta Öncelik)
4. **PDF Export İyileştirmeleri** (4-5 saat)
5. **Karakter İstatistikleri İyileştirmeleri** (2-3 saat)

**Toplam:** ~6-8 saat

### İleride (Düşük Öncelik)
6. **Pathfinder 1e Spell Scraping** (4-6 saat)
7. **Veri Doğrulama ve Validasyon** (2-3 saat)
8. **Multiclassing** (10-15 saat - skip edilebilir)
9. **Karakter Karşılaştırma** (3-4 saat)

---

## 🎯 Önerilen Sonraki Adım

**En Öncelikli:** Veri Kalitesi İyileştirmeleri

**Sebep:**
- Testlerde tespit edilen sorunlar var
- Veri kalitesi artarsa diğer sistemler daha güvenilir olur
- Nispeten hızlı tamamlanabilir (2-3 saat)

**Yapılacaklar:**
1. Race subrace name alanlarını doldur
2. Class hit_dice alanlarını doldur
3. Spell level validation ekle

**Başlangıç:**
```bash
# Veri kalitesi düzeltmeleri için script oluştur
# veya mevcut scraping scriptlerini güncelle
```

---

## 📊 Mevcut Durum

**Tamamlanma Oranı:** ~%90

**Tamamlanan:**
- ✅ Karakter oluşturma sistemi
- ✅ Level up sistemi
- ✅ Spell sistemi (temel)
- ✅ Equipment yönetimi (temel)
- ✅ PDF export (temel)
- ✅ Test sistemi (20+ test case)
- ✅ D&D 5e veri güncelleme (scraping)

**Eksikler:**
- ⚠️ Veri kalitesi iyileştirmeleri (testlerde tespit edilen sorunlar)
- ⚠️ Spell sistemi iyileştirmeleri (Upcasting, Ritual, Concentration)
- ⚠️ Equipment yönetimi iyileştirmeleri (Magic items, Attunement)
- ⚠️ GUI testleri (PySide6/Qt)
- ⚠️ PDF export iyileştirmeleri

---

**Sonraki Adım:** Veri Kalitesi İyileştirmeleri ile başla






