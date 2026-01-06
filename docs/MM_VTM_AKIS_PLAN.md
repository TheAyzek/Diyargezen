## MM & VtM - Veri Yükleme / Kaydetme Akış Planı

Bu plan, `MmPage` ve `VtmPage` bileşenlerinin DndPage ile aynı kaydet/yükle deneyimini paylaşmasını hedefler.

---

### 1. Veri Yükleme (Data Loader)

#### 1.1 Fonksiyonlar
`utils/data_loader.py` içine aşağıdaki fonksiyonlar eklenecek:

```python
_CACHE = {}

def load_mm_data(base_dir: Path) -> Dict[str, Any]:
    if "mm" not in _CACHE:
        path = base_dir / "data" / "mm_data.json"
        _CACHE["mm"] = _safe_json_read(path)
    return _CACHE["mm"]

def load_vtm_data(base_dir: Path) -> Dict[str, Any]:
    if "vtm" not in _CACHE:
        path = base_dir / "data" / "vtm_data.json"
        _CACHE["vtm"] = _safe_json_read(path)
    return _CACHE["vtm"]
```

- `_safe_json_read` mevcut `load_dnd_data` içinde kullanılan try/except bloğu ile ortaklaştırılabilir.
- Arka plan (background) dosyaları gibi ek dizinler şimdilik yok; gelecekte `data/vtm/` alt klasörleri eklenebilir.

#### 1.2 Kullanım
- `MmPage.__init__` ve `VtmPage.__init__` içinde `self.data = load_mm_data(BASE_DIR)` / `load_vtm_data(...)`
- DndPage’deki `_load_dnd_data` fonksiyonu ile aynı caching deseni.

---

### 2. Kaydetme / Yükleme Akışı

#### 2.1 JSON Kaydetme
- Ortak `save_character_to_file(character: dict, parent: QWidget)` helper fonksiyonu oluştur:
  ```python
  def save_character_to_file(character, parent):
      system = character.get("system", "CHARACTER")
      default_name = f"{character.get('name', 'isimsiz')}_{system.lower()}"
      # QFileDialog ile yol seçimi
      # json.dump(..., ensure_ascii=False, indent=2)
  ```
- DndPage, MmPage, VtmPage bu yardımcıyı kullanacak.
- Dosya adı önerisi: `{system}_{name}.json`

#### 2.2 JSON Yükleme
- Ortak helper: `load_character_from_file(parent) -> dict | None`
  - QFileDialog ile `.json` seç
  - `json.load`
  - `character.get("system")` ile hangi sayfaya ait olduğunu belirleme (ileride cross-load engeli için)

#### 2.3 Otomatik / Manuel Kaydetme
- DndPage’deki `_auto_save_character` sadece D&D için geçerli; MM/VTM sayfalarında opsiyonel hale getirilecek (toggle checkbox?).
- En azından manuel `Kaydet` butonu D&D ile aynı diyaloğu kullanmalı.

---

### 3. storage.py (SQLite) Entegrasyonu

#### 3.1 Tablo Yapısı
Mevcut `characters` tablosu halihazırda `system` alanını içerdiği için değişikliğe ihtiyaç yok.

#### 3.2 Ortak Fonksiyonlar
- `storage.py` içindeki `save_character` çağrısı için `system` alanı `MUTANTS_AND_MASTERMINDS` veya `VTM5E` olarak kullanılacak.
- `list_characters` fonksiyonundan dönen kayıtlar UI tarafında filtrelenecek:
  ```python
  [rec for rec in list_characters(db_path) if rec.system == "MUTANTS_AND_MASTERMINDS"]
  ```
- İleride `list_characters_by_system(db_path, system)` yardımcı fonksiyon eklenebilir (opsiyonel).

---

### 4. Serializer (Karakter Dict)

#### 4.1 D&D Formatına Uyum
- Her sistem için `_create_character_*` fonksiyonu, ortak `dict` yapısını izlemeli:
  ```python
  {
    "system": "MUTANTS_AND_MASTERMINDS",
    "name": "...",
    "meta": { ... },        # Sistem özgü alanlar
    "statistics": { ... },  # ability/power/discipline değerleri
    "notes": "...",
  }
  ```
- PDF export henüz sadece D&D için; diğer sistemlerde `PDF` butonu disable edilip tooltip verilecek.

#### 4.2 Önerilen Alanlar
- **M&M**: `power_level`, `abilities`, `powers`, `advantages`, `defenses`, `power_points`
- **VtM**: `clan`, `attributes`, `skills`, `disciplines`, `humanity`, `willpower`, `health`, `bane`

---

### 5. UI Entegrasyonu

#### 5.1 Toolbar / Buttons
- Ortak buton seti:
  - `QPushButton("Yeni")` → `_start_new_character_*`
  - `QPushButton("Yükle")` → `_load_existing_character_*`
  - `QPushButton("Kaydet")` → `_save_character_to_file_*`
  - `QPushButton("PDF", enabled=False)` → tooltip: "Yakında"
- Bu butonlar `DndPage` içinde `self._create_toolbar()` gibi bir helper ile soyutlanabilir.

#### 5.2 Dialog ve Mesajlar
- QFileDialog başlıkları: `"M&M Karakter Kaydet"`, `"VtM Karakter Yükle"` vb.
- QMessageBox mesajlarını Türkçe tut, sistem adıyla özelleştir.

---

### 6. Test Planı

1. **JSON Kaydet/Yükle**
   - M&M sayfasında temel bir karakter oluştur, JSON kaydet.
   - Dosya içeriğinde `system: MUTANTS_AND_MASTERMINDS` olduğunu doğrula.
   - Aynı dosyayı yükle, form alanlarının dolduğunu kontrol et.

2. **SQLite Kaydet/Yükle**
   - `storage.py.init_db` ile test DB oluştur.
   - M&M karakterini kaydet, `list_characters` çıktısında gör.
   - `system` filtresi ile sadece ilgili kayıtları listele.

3. **Çapraz Sistem Koruması**
   - D&D karakter dosyasını M&M sayfasında yüklemeye çalış → hata mesajı göster.
   - M&M dosyasını VtM sayfasında yüklerken de aynı kontrol.

---

### 7. Sonraki Adımlar
1. Ortak helper fonksiyonlarını (`save_character_to_file`, `load_character_from_file`) `gui/utils_gui.py` veya topluca `gui/app.py` içinde tanımla.
2. `utils/data_loader.py` güncellemesini yap.
3. `MmPage` ve `VtmPage` sınıflarına yeni kaydet/yükle akışını bağla.
4. UI butonlarını aktif hale getirip test et.



