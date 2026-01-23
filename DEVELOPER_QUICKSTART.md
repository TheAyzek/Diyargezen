# 🚀 GUI KORUMA - GELİŞTİRİCİ BAŞLANGIC REHBERİ

## Hızlı İlk Kontrol

```bash
# Proje root'unda
cd c:\Users\dnssh\OneDrive\Belgeler\Diyargezen

# Sistem durumunu kontrol et
python verify_gui_features.py
```

✅ Tüm kontroller geçerse devam et
❌ Bir kontrol başarısızsa `GUI_OZELLIKLER.md` kontrol et

---

## 📚 Önemli Dosyalar

1. **GUI_OZELLIKLER.md** 
   - Sistem-spesifik kuralların tam referans rehberi
   - Ne yazık ki 4 sistem karışmadan: Bura kontrol et

2. **GUI_KORUMA_KONTROL_LISTESI.md**
   - Değişiklik yapılacaksa: Checklist'i kontrol et
   - Test prosedürü: Tüm 4 sistem için test et

3. **verify_gui_features.py**
   - Sistem durumunu otomatik kontrol et
   - Her değişiklikten sonra çalıştır

4. **gui/app.py**
   - Ana GUI dosyası (10,319 satır)
   - Sistem-spesifik kurallar burada kodlanmış

---

## 🔧 Sık Yapılan İşlemler

### 1️⃣ Sadece Kontrol Yapmak İstersen

```bash
python verify_gui_features.py
```

**Çıkmalı**: ✅ Tüm kontroller başarılı

---

### 2️⃣ D&D 5e'ye Özellik Eklemek İstersem

**Adım 1: Planla**
```
- ASI sistemi mi? → ASI mekanikleri kontrol et (GUI_OZELLIKLER.md)
- Feat mi? → Feat seçimi kontrol et
- Büyü mü? → Spell slot hesapları kontrol et
- Multiclass mi? → Multiclass kurallarını kontrol et
```

**Adım 2: Geliştir**
```python
# gui/app.py'de sistem-spesifik kodunu ekle
# D&D 5e için: characterCreationDND5E() işlevini bul ve düzenle

# Kodda sistem-spesifik yorum yaz:
# D&D 5e: ASI seçimi - Seviye 4, 8, 12, 16, 20'de kullanıcı seçer
```

**Adım 3: Test Et**
```bash
# D&D 5e karakteri oluştur ve test et
python gui/app.py

# System seç → D&D 5e
# Karakter oluştur ve özelliği test et
# Karakteri kaydet/yükle kontrol et
```

**Adım 4: Verify Et**
```bash
python verify_gui_features.py
```

**Adım 5: Commit Et**
```bash
git add gui/app.py
git commit -m "Feat: D&D 5e'ye [özellik] eklendi

- [Açıklama]
- Sistem-spesifik: [İlgili kurallar]
- Test edildi: D&D 5e ✓
- Diğer sistemler etkilenmedi"
```

---

### 3️⃣ Pathfinder'a Özellik Eklemek İstersem

**Pathfinder Özellikleri**:
- Feat per level (1, 3, 5, 7, 9, 11, 13, 15, 17, 19)
- Prestige class desteği
- Ability progression kuralları

```bash
# Pathfinder karakteri oluştur
python gui/app.py → Pathfinder seç

# Kontrol et
python verify_gui_features.py
```

---

### 4️⃣ M&M'ye Özellik Eklemek İstersem

**M&M Özellikleri**:
- Power Points sistemi
- Extra/Flaw selection
- Power level calculations

```bash
# M&M karakteri oluştur
python gui/app.py → M&M seç

# Kontrol et
python verify_gui_features.py
```

---

### 5️⃣ VtM'ye Özellik Eklemek İstersem

**VtM Özellikleri**:
- Klan seçimi (3 klan)
- Discipline selection
- Blood resonance

```bash
# VtM karakteri oluştur
python gui/app.py → VtM seç

# Kontrol et
python verify_gui_features.py
```

---

## 📋 PRE-COMMIT CHECKLIST

Commit yapılmadan önce kontrol et:

```
[ ] verify_gui_features.py başarılı mı?
[ ] Tüm 4 sistem test edildi mi?
[ ] Sistem-spesifik kurallar korundu mu?
[ ] GUI_OZELLIKLER.md güncellendi mi? (yeni feature ise)
[ ] Commit mesajı açıklayıcı mı?
[ ] Kod yorumları eklendi mi?
```

---

## 🐛 Sorun Giderme

### Sorun: verify_gui_features.py başarısız

**Çözüm 1: Veri dosyasını kontrol et**
```bash
# data/ klasöründe tüm JSON dosyaları var mı?
dir data\*.json

# ✅ dnd_data.json
# ✅ pathfinder_1e_data.json
# ✅ mm_data.json
# ✅ vtm_data.json
```

**Çözüm 2: GUI dosyalarını kontrol et**
```bash
# gui/ klasörü tamam mı?
dir gui\*.py

# ✅ app.py
# ✅ subclass_dialog.py
# ✅ equipment_comparison_dialog.py
# ✅ pending_widget.py
```

**Çözüm 3: Utils modüllerini kontrol et**
```bash
# utils/ klasöründe kritik dosyalar var mı?
dir utils\*.py | findstr /i "calculation data_loader export storage"
```

---

### Sorun: GUI çalışmıyor

**Adım 1: Error mesajını oku**
```bash
python gui/app.py

# Hangi sistem seçilmişse, o sistem kodunu kontrol et
# gui/app.py'de: characterCreationDND5E(), characterCreationPathfinder(), vb.
```

**Adım 2: Veri yükleme kontrol et**
```python
# gui/app.py'de yaklaşık satır 1500-2000 arası
# load_dnd_data(), load_pathfinder_data() vb. fonksiyonlar
```

**Adım 3: Sistem seçimi kontrol et**
```bash
# GUI açıldığında "D&D 5e" vs seçilmiş mi?
# System dropdown'unu kontrol et
```

---

### Sorun: Özellik diğer sistemleri etkiliyor

**Adım 1: Kodun sistem-spesifik bölümde olup olmadığını kontrol et**
```python
# ❌ YANLIŞ:
if race == "Elf":
    bonus = 2  # Tüm sistemler için geçerli

# ✅ DOĞRU:
if system == "DND5E" and race == "Elf":
    bonus = 2  # Sadece D&D 5e'de geçerli
```

**Adım 2: GUI_OZELLIKLER.md kontrol et**
- Sistemler arası hiç karışma olmamalı

**Adım 3: Test et**
```bash
# Tüm 4 sistem için karakteri yüklemeyi test et
python gui/app.py
```

---

## 🎓 Eğitim Kaynakları

### D&D 5e Kuralları
- GUI_OZELLIKLER.md → "D&D 5E" bölümü
- gui/app.py → `characterCreationDND5E()`

### Pathfinder 1e Kuralları
- GUI_OZELLIKLER.md → "Pathfinder 1E" bölümü
- gui/app.py → `characterCreationPathfinder()`

### M&M 3e Kuralları
- GUI_OZELLIKLER.md → "M&M 3E" bölümü
- gui/app.py → `characterCreationMM()`

### VtM 5e Kuralları
- GUI_OZELLIKLER.md → "VtM 5E" bölümü
- gui/app.py → `characterCreationVtM()`

---

## 📞 Hızlı Referans

| İhtiyaç | Dosya | Bölüm |
|---------|-------|-------|
| Sistem kuralları | GUI_OZELLIKLER.md | İlgili sistem |
| Kontrol listesi | GUI_KORUMA_KONTROL_LISTESI.md | İlgili kontrol |
| Otomatik doğrulama | verify_gui_features.py | Çalıştır |
| Ana kod | gui/app.py | characterCreation* |
| Hesaplamalar | utils/calculations.py | İlgili fonksiyon |
| Veri | data/*.json | İlgili sistem |

---

## ⚡ Başlangıç Komutları

```bash
# Projeyi aç
cd c:\Users\dnssh\OneDrive\Belgeler\Diyargezen

# GUI'yi başlat
python gui/app.py

# Sistem kontrol et
python verify_gui_features.py

# Değişiklikleri commit et (template)
git add .
git commit -m "Feat/Fix: [Açıklama]

- [Değişiklik 1]
- [Değişiklik 2]

Sistem: [D&D 5e/Pathfinder/M&M/VtM]
Test: [Sistem adı] ✓
Dikkat: [Varsa ek notlar]"
```

---

**Son Güncelleme**: 2026-01-23  
**Versiyon**: 1.0  
**Durum**: ✅ Tüm Sistemler Korunuyor
