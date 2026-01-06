# Kural Kitabı Entegrasyonu - Sonraki Adımlar

## ✅ Tamamlanan Özellikler
1. ✅ Basit pattern matching modülü (`rule_extractor.py`)
2. ✅ Kural saklama/yükleme modülü (`rule_storage.py`)
3. ✅ Dinamik hesaplama motoru (`dynamic_calculator.py`)
4. ✅ GUI entegrasyonu - Kural yükleme butonu
5. ✅ PDF parsing desteği (PyPDF2)
6. ✅ Kural düzenleme arayüzü (`RuleEditorDialog`)
7. ✅ Kural doğrulama modülü (`rule_validator.py`)
8. ✅ Kural önizleme modülü (`rule_preview.py`)
9. ✅ Kural versiyonlama modülü (`rule_versioning.py`)
10. ✅ NLP ile gelişmiş kural çıkarma (`rule_extractor_nlp.py`)

## 🎯 Sonraki Adımlar (Öncelik Sırasına Göre)

### 1. ✅ Dinamik Hesaplamaları Entegre Et (Öncelik: Yüksek) - TAMAMLANDI
**Amaç**: Yüklenen kuralları gerçekten kullanmak

**Tamamlanan İşler**:
- ✅ `DndPage._update_character_stats()` içinde `calculate_dynamic_proficiency_bonus` kullanılıyor
- ✅ `DndPage._update_character_stats()` içinde `calculate_dynamic_armor_class` kullanılıyor
- ✅ `DndPage._update_character_stats()` içinde `calculate_dynamic_hit_points` kullanılıyor
- ✅ `MmPage._update_pl_limits()` içinde `calculate_dynamic_power_points` kullanılıyor
- ✅ `VtmPage._collect_character_data()` içinde `calculate_dynamic_health` ve `calculate_dynamic_willpower` kullanılıyor

**Fayda**: Kullanıcı kural kitabı yüklediğinde, hesaplamalar otomatik olarak o kurallara göre yapılır.

---

### 2. ✅ Kural Düzenleme Arayüzü (Öncelik: Orta) - TAMAMLANDI
**Amaç**: Yüklenen kuralları GUI'den düzenleyebilmek

**Tamamlanan İşler**:
- ✅ "✏️ Kural Düzenle" butonu eklendi (tüm sistemlerde)
- ✅ `RuleEditorDialog` kural düzenleme diyaloğu oluşturuldu
- ✅ JSON formatında kuralları göster/düzenle
- ✅ Kural kaydetme (otomatik versiyonlama ile)

**Fayda**: Kullanıcı yüklenen kuralları manuel olarak düzenleyebilir.

---

### 3. ✅ Kural Doğrulama (Öncelik: Orta) - TAMAMLANDI
**Amaç**: Yüklenen kuralların geçerliliğini kontrol etmek

**Tamamlanan İşler**:
- ✅ `rule_validator.py` modülü oluşturuldu
- ✅ Kural formatı doğrulama
- ✅ Eksik kural kontrolü
- ✅ Çelişkili kural tespiti (aralık çakışmaları vb.)
- ✅ Kullanıcıya uyarı mesajları (hata/uyarı/bilgi seviyeleri)
- ✅ "🔍 Kuralları Doğrula" butonu eklendi
- ✅ Otomatik doğrulama (yükleme ve kaydetme sırasında)

**Fayda**: Hatalı kurallar yüklenmeden önce tespit edilir.

---

### 4. ✅ Kural Önizleme (Öncelik: Düşük) - TAMAMLANDI
**Amaç**: Yüklenen kuralları görüntülemek

**Tamamlanan İşler**:
- ✅ `rule_preview.py` modülü oluşturuldu
- ✅ "👁️ Kuralları Görüntüle" butonu eklendi (tüm sistemlerde)
- ✅ `RulePreviewDialog` kural önizleme diyaloğu oluşturuldu
- ✅ Okunabilir format (JSON değil, düz metin)
- ✅ Sistem bazlı formatlama (D&D, M&M, VtM)

**Fayda**: Kullanıcı hangi kuralların yüklü olduğunu görebilir.

---

### 5. ✅ Kural Versiyonlama (Öncelik: Düşük) - TAMAMLANDI
**Amaç**: Farklı kural versiyonlarını yönetmek

**Tamamlanan İşler**:
- ✅ `rule_versioning.py` modülü oluşturuldu
- ✅ Kural versiyon takibi (timestamp bazlı)
- ✅ Versiyon geçmişi (son 50 versiyon)
- ✅ Versiyon geri yükleme (otomatik yedekleme ile)
- ✅ Versiyon silme
- ✅ "📦 Versiyon Yönetimi" butonu eklendi (tüm sistemlerde)
- ✅ `RuleVersionDialog` versiyon yönetimi diyaloğu oluşturuldu
- ✅ Otomatik versiyonlama (her kayıtta)

**Fayda**: Kullanıcı farklı kural versiyonlarını saklayabilir ve geri yükleyebilir.

---

### 6. ✅ NLP ile Gelişmiş Kural Çıkarma (Öncelik: Çok Düşük) - TAMAMLANDI
**Amaç**: Daha akıllı kural çıkarma

**Tamamlanan İşler**:
- ✅ `rule_extractor_nlp.py` modülü oluşturuldu
- ✅ spaCy entegrasyonu (opsiyonel)
- ✅ Doğal dil işleme ile kural çıkarma
- ✅ İlişki tanıma (anahtar kelime-değer ilişkileri)
- ✅ Seviye bazlı kural çıkarma
- ✅ Tablo yapısı analizi
- ✅ GUI entegrasyonu (NLP durumu göstergesi)
- ✅ Kullanıcı seçimi (NLP kullanılsın mı?)

**Fayda**: Daha karmaşık kurallar otomatik çıkarılabilir.

**Not**: Bu özellik opsiyoneldir - spaCy yoksa pattern matching kullanılır.

---

## 📋 Önerilen Sıralama - ✅ TÜMÜ TAMAMLANDI

1. ✅ **Dinamik Hesaplamaları Entegre Et** (En önemli - hemen yapılmalı) - **TAMAMLANDI**
2. ✅ **Kural Düzenleme Arayüzü** (Kullanıcı deneyimi için önemli) - **TAMAMLANDI**
3. ✅ **Kural Doğrulama** (Hata önleme için önemli) - **TAMAMLANDI**
4. ✅ **Kural Önizleme** (Kullanıcı deneyimi için faydalı) - **TAMAMLANDI**
5. ✅ **Kural Versiyonlama** (İleri seviye özellik) - **TAMAMLANDI**
6. ✅ **NLP ile Gelişmiş Kural Çıkarma** (Gelecek için) - **TAMAMLANDI**

**🎉 Tüm öncelikli özellikler başarıyla tamamlandı!**

---

## 🔧 Teknik Notlar

### Dinamik Hesaplamaları Entegre Etme Örneği

**Mevcut Kod** (DndPage):
```python
prof_bonus = calculate_proficiency_bonus(level)
```

**Yeni Kod**:
```python
# Önce yüklenen kuralları kontrol et
rules = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
prof_bonus = calculate_dynamic_proficiency_bonus(level, rules)
```

**Fallback Mekanizması**: Eğer kural yoksa, varsayılan hesaplama kullanılır (mevcut sistem).

---

## ⚠️ Dikkat Edilmesi Gerekenler

1. **Geriye Uyumluluk**: Mevcut hesaplamalar çalışmaya devam etmeli
2. **Performans**: Kural yükleme her hesaplamada yapılmamalı (cache kullanılmalı)
3. **Hata Yönetimi**: Kural yükleme hatası durumunda varsayılan hesaplamalar kullanılmalı
4. **Kullanıcı Deneyimi**: Kural yükleme/düzenleme işlemleri açık ve anlaşılır olmalı

