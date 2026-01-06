# Diyargezen EXE Oluşturma Kılavuzu

Bu kılavuz, Diyargezen projesini Windows executable (.exe) dosyasına dönüştürmek için adım adım talimatlar içerir.

---

## 📋 Gereksinimler

### 1. Python Kurulumu
- Python 3.8+ kurulu olmalı
- Proje bağımlılıkları kurulu olmalı:
  ```bash
  pip install -r requirements.txt
  ```

### 2. PyInstaller Kurulumu
```bash
pip install pyinstaller
```

---

## 🚀 Hızlı Başlangıç

### Yöntem 1: Otomatik Build Script (Önerilen)

```bash
python build_exe.py
```

Bu script otomatik olarak:
- PyInstaller'ın kurulu olup olmadığını kontrol eder
- Gerekli ayarları yapar
- EXE dosyasını oluşturur

**Çıktı**: `dist/Diyargezen.exe`

### Yöntem 2: Manuel PyInstaller Komutu

```bash
pyinstaller Diyargezen.spec
```

veya

```bash
pyinstaller --name=Diyargezen --onefile --windowed --add-data="data;data" --add-data="assets;assets" gui/app.py
```

---

## ⚙️ Build Seçenekleri

### Tek Dosya (OneFile) - Önerilen
- **Avantaj**: Tek .exe dosyası, dağıtımı kolay
- **Dezavantaj**: İlk açılış biraz yavaş olabilir (dosya açılıyor)
- **Kullanım**: `--onefile` parametresi ile

### Klasör (OneDir)
- **Avantaj**: Daha hızlı başlama
- **Dezavantaj**: Bir klasör oluşturur, tüm dosyalar birlikte dağıtılmalı
- **Kullanım**: `--onefile` parametresini kaldırın

### Konsol Penceresi
- **GUI için**: `--windowed` (konsol penceresi göstermez)
- **CLI için**: `--console` (konsol penceresi gösterir)

---

## 📁 Dosya Yapısı

Build sonrası oluşan dosyalar:

```
Diyargezen/
├── build/              # Geçici build dosyaları
├── dist/               # Oluşturulan EXE dosyası
│   └── Diyargezen.exe  # Ana executable
└── Diyargezen.spec     # PyInstaller spec dosyası
```

---

## 🔧 Özelleştirme

### Icon Değiştirme

1. Icon dosyasını `assets/` klasörüne ekleyin (`.ico` formatı önerilir)
2. `Diyargezen.spec` dosyasında icon yolunu güncelleyin:
   ```python
   icon='assets/diyargezen_icon.ico'
   ```

### Ek Data Dosyaları Ekleme

`Diyargezen.spec` dosyasında `datas` listesine ekleyin:

```python
datas = [
    ('data', 'data'),
    ('assets', 'assets'),
    ('characters', 'characters'),  # Yeni eklenen
]
```

### Hidden Imports Ekleme

Eksik modüller için `hiddenimports` listesine ekleyin:

```python
hiddenimports = [
    # ... mevcut imports
    'yeni_modul',
]
```

---

## 🐛 Sorun Giderme

### Problem: "ModuleNotFoundError"

**Çözüm**: Eksik modülü `hiddenimports` listesine ekleyin.

### Problem: "Data files not found"

**Çözüm**: `datas` listesinde doğru yol olduğundan emin olun. Windows'ta `;` kullanın, Linux/Mac'te `:` kullanın.

### Problem: EXE çok büyük

**Çözüm**: 
- Gereksiz modülleri `excludes` listesine ekleyin
- UPX sıkıştırmayı kullanın (`upx=True`)

### Problem: EXE yavaş başlıyor

**Çözüm**: 
- `--onefile` yerine klasör yapısı kullanın
- UPX sıkıştırmayı kapatın (`upx=False`)

### Problem: Antivirus uyarısı

**Çözüm**: 
- PyInstaller ile oluşturulan EXE'ler bazen false positive verir
- Code signing ekleyebilirsiniz (ücretli sertifika gerekir)

---

## 📦 Dağıtım

### Tek Dosya Dağıtımı
1. `dist/Diyargezen.exe` dosyasını kopyalayın
2. Kullanıcıya gönderin
3. Kullanıcı çift tıklayarak çalıştırabilir

### Klasör Dağıtımı
1. `dist/Diyargezen/` klasörünün tamamını kopyalayın
2. Kullanıcıya gönderin
3. Kullanıcı `Diyargezen.exe` dosyasını çalıştırabilir

### Installer Oluşturma (Opsiyonel)

Inno Setup veya NSIS kullanarak installer oluşturabilirsiniz:

```bash
# Inno Setup örneği
# installer.iss dosyası oluşturun ve derleyin
```

---

## ✅ Test

EXE'yi test etmek için:

1. `dist/Diyargezen.exe` dosyasını çalıştırın
2. Tüm özellikleri test edin:
   - Karakter oluşturma
   - Karakter kaydetme/yükleme
   - PDF export
   - Kural yönetimi
   - vb.

---

## 📝 Notlar

- İlk build biraz uzun sürebilir (5-10 dakika)
- EXE dosyası yaklaşık 50-100 MB olabilir (tüm bağımlılıklar dahil)
- Windows Defender veya diğer antivirusler false positive verebilir
- EXE'yi farklı Windows sürümlerinde test edin

---

## 🎯 Hızlı Komutlar

```bash
# PyInstaller kur
pip install pyinstaller

# Build yap
python build_exe.py

# Veya manuel
pyinstaller Diyargezen.spec

# Build'i temizle ve yeniden yap
pyinstaller --clean Diyargezen.spec
```

---

**Başarılar! 🚀**


