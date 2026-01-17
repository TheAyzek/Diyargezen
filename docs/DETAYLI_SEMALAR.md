# Diyargezen FRP Karakter Yaratıcısı - Detaylı Şemalar

## 📋 İçindekiler
1. [Detaylı UML Sınıf Diyagramları](#detaylı-uml-sınıf-diyagramları)
2. [Sequence Diyagramları](#sequence-diyagramları)
3. [Veritabanı Şeması](#veritabanı-şeması)
4. [API/Interface Şeması](#apiinterface-şeması)
5. [State Diyagramları](#state-diyagramları)
6. [Component Diyagramları](#component-diyagramları)

---

## 🏛️ Detaylı UML Sınıf Diyagramları

### Ana Sınıf Yapısı

```mermaid
classDiagram
    class QApplication {
        +exec()
        +setStyleSheet()
    }
    
    class MainWindow {
        -QTabWidget central
        -DndPage dnd_page
        -MmPage mm_page
        -VtmPage vtm_page
        +__init__()
        +_apply_dark_theme()
        +_setup_shortcuts()
        +_set_window_icon()
        +_new_character_shortcut()
        +_load_character_shortcut()
        +_save_character_shortcut()
        +_export_shortcut()
        +_show_help()
    }
    
    class DndPage {
        -dict data
        -dict current_character
        -list inventory_items
        -QStackedWidget stacked_widget
        -QTabWidget tab_widget
        -dict _data_cache
        -dict _summary_cache
        +__init__()
        +_load_dnd_data() dict
        +_load_logo() QPixmap
        +_init_ui()
        +_init_main_menu()
        +_init_character_ui()
        +_init_spells_ui()
        +_init_levelup_ui()
        +_init_inventory_ui()
        +_init_dice_ui()
        +_start_new_character()
        +_create_character() dict
        +_save_character_to_file()
        +_load_existing_character()
        +_load_character_to_gui(dict)
        +_back_to_main_menu()
        +_update_point_buy_info()
        +_refresh_class_options()
        +_refresh_class_features()
        +_refresh_feats()
        +_check_feat_prerequisites(str, dict) bool
        +_calculate_available_feat_count(int, str) int
        +_complete_character()
        +_update_spells_list()
        +_load_current_character_inventory()
        +_refresh_current_character_info()
        +_load_character_for_levelup()
        +_level_up_character()
        +_load_character_image()
        +_remove_character_image()
        +_load_character_image_to_gui(dict)
    }
    
    class MmPage {
        -QLabel mm_character_image_label
        -str current_character_image_data
        +__init__()
        +_load_character_image()
        +_remove_character_image()
        +_load_character_image_to_gui(dict)
    }
    
    class VtmPage {
        -QLabel vtm_character_image_label
        -str current_character_image_data
        +__init__()
        +_load_character_image()
        +_remove_character_image()
        +_load_character_image_to_gui(dict)
    }
    
    class DataLoader {
        +load_dnd_data(Path) dict
    }
    
    class CharacterRecord {
        +int id
        +str system
        +str name
        +dict data
    }
    
    class Storage {
        +init_db(Path)
        +save_character(Path, CharacterRecord) int
        +load_character(Path, int) CharacterRecord
        +list_characters(Path) list[CharacterRecord]
    }
    
    class PDFExporter {
        +export_dnd_character_pdf(dict, Path, Path, str)
    }
    
    class DndCreator {
        +create_dnd_character() dict
        +_prompt_point_buy(list, int) dict
        +_prompt_selection(list, str) str
        +_load_dnd_data() dict
    }
    
    class CharacterContext {
        +name: str
        +race: str
        +char_class: str
        +background: str
        +level: int
        +to_dict() dict
    }
    
    class Step {
        <<abstract>>
        +run(ctx: CharacterContext) StepResult
    }
    
    class CharacterWizard {
        -steps: list[Step]
        +run(ctx: CharacterContext) CharacterContext
    }
    
    class DndCLIEntrypoint {
        +main()
    }
    
    MainWindow --> DndPage : contains
    MainWindow --> MmPage : contains
    MainWindow --> VtmPage : contains
    MainWindow --> QApplication : uses
    DndPage --> DataLoader : uses
    DndPage --> Storage : uses
    DndPage --> PDFExporter : uses
    DndPage --> DndCreator : uses
    Storage --> CharacterRecord : uses
    PDFExporter --> CharacterRecord : uses
    DndCLIEntrypoint --> CharacterWizard : uses
    CharacterWizard --> Step : manages
    DndCLIEntrypoint --> CharacterContext : builds
    
    note for DndPage "4296 satır kod\nTüm D&D özellikleri"
    note for Storage "SQLite ve JSON\nkayıt/yükleme"
    note for PDFExporter "PDF export\narkaplan desteği"
    note for DndCLIEntrypoint "dnd_cli.py / dnd_levelup_cli.py\nAdım bazlı CLI wizard"
```

### GUI Bileşenleri Detayı

```mermaid
classDiagram
    class DndPage {
        <<GUI Component>>
    }
    
    class CharacterWizard {
        -QLineEdit character_name_edit
        -QComboBox race_cb
        -QComboBox class_cb
        -QComboBox bg_cb
        -QSpinBox ability_spins[]
        -QListWidget wiz_skills
        -QListWidget wiz_cantrips
        -QListWidget wiz_level1
        -QListWidget feats_list
        -QTextEdit trait_edit
        -QTextEdit ideal_edit
        -QTextEdit bond_edit
        -QTextEdit flaw_edit
        -QComboBox alignment_cb
        -QLineEdit height_edit
        -QLineEdit weight_edit
        -QLineEdit age_edit
        -QLineEdit hair_color_edit
        -QLineEdit eye_color_edit
        -QLineEdit skin_color_edit
        -QTextEdit appearance_desc_edit
        -QLabel character_image_label
        -str current_character_image_data
        -QTextEdit summary
    }
    
    class SpellsManager {
        -QComboBox spells_character_combo
        -QLabel spellcasting_check_label
        -QListWidget spells_list
        -QTextEdit spell_info
        -QComboBox spell_level_cb
        -QListWidget available_spells
        -QPushButton add_spell_btn
        -QPushButton remove_spell_btn
    }
    
    class LevelUpManager {
        -QLineEdit levelup_search
        -QListWidget levelup_character_list
        -QComboBox levelup_character_combo
        -QSpinBox new_level_spin
        -QTextEdit levelup_preview
        -QComboBox asi_feat_choice
        -QListWidget available_feats_list
        -QPushButton level_up_btn
    }
    
    class InventoryManager {
        -QLineEdit inventory_search
        -QListWidget inventory_items_list
        -QTextEdit item_info
        -QListWidget character_inventory
        -QLabel weight_label
        -QPushButton add_item_btn
        -QPushButton remove_item_btn
        -QPushButton equip_item_btn
    }
    
    class DiceRoller {
        -QComboBox dice_type_cb
        -QSpinBox dice_count_spin
        -QSpinBox modifier_spin
        -QPushButton roll_btn
        -QTextEdit dice_results
    }
    
    DndPage --> CharacterWizard : contains
    DndPage --> SpellsManager : contains
    DndPage --> LevelUpManager : contains
    DndPage --> InventoryManager : contains
    DndPage --> DiceRoller : contains
```

---

## 🔄 Sequence Diyagramları

### Karakter Oluşturma Akışı

```mermaid
sequenceDiagram
    participant U as Kullanıcı
    participant GUI as DndPage
    participant W as CharacterWizard
    participant DL as DataLoader
    participant CC as CharacterCreator
    participant S as Storage
    
    U->>GUI: "Yeni Karakter" butonuna tıkla
    GUI->>W: _start_new_character()
    W->>GUI: Wizard UI göster
    
    U->>W: İsim ve Irk seç
    W->>DL: Irk verilerini yükle
    DL-->>W: Irk verileri
    
    U->>W: Sınıf seç
    W->>DL: Sınıf verilerini yükle
    DL-->>W: Sınıf verileri
    
    U->>W: Arka plan seç
    W->>DL: Arka plan verilerini yükle
    DL-->>W: Arka plan verileri
    
    U->>W: Yetenek puanları ata
    W->>W: Point buy hesapla
    
    U->>W: Beceriler seç
    U->>W: Büyüler seç
    U->>W: Feat'ler seç
    U->>W: Kişisel bilgiler gir
    
    U->>W: "Karakter Oluştur" butonuna tıkla
    W->>CC: _create_character()
    CC->>CC: Irk bonuslarını uygula
    CC->>CC: Modifikatörleri hesapla
    CC->>CC: AC ve HP hesapla
    CC-->>W: Karakter objesi
    
    W->>GUI: Karakteri kaydet
    GUI->>S: _save_character_to_file()
    S->>S: JSON dosyasına yaz
    S-->>GUI: Başarılı
    
    GUI->>U: Karakter oluşturuldu mesajı
    GUI->>GUI: Sekmeleri göster
```

### Karakter Yükleme Akışı

```mermaid
sequenceDiagram
    participant U as Kullanıcı
    participant GUI as DndPage
    participant FD as FileDialog
    participant S as Storage
    participant DL as DataLoader
    participant W as CharacterWizard
    
    U->>GUI: "Karakter Yükle" butonuna tıkla
    GUI->>FD: Dosya seçim dialogu aç
    FD-->>U: Dosya seç
    U->>FD: JSON/SQLite dosyası seç
    FD-->>GUI: Dosya yolu
    
    alt JSON Dosyası
        GUI->>DL: JSON dosyasını oku
        DL->>DL: JSON parse et
        DL-->>GUI: Karakter verisi
    else SQLite Dosyası
        GUI->>S: load_character()
        S->>S: SQLite sorgusu
        S->>S: JSON deserialize
        S-->>GUI: CharacterRecord
        GUI->>GUI: CharacterRecord.data
    end
    
    GUI->>GUI: _load_character_to_gui()
    GUI->>W: Form alanlarını doldur
    W->>W: Tüm UI elemanlarını güncelle
    W-->>GUI: UI güncellendi
    
    GUI->>GUI: Sekmeleri göster
    GUI-->>U: Karakter yüklendi
```

### PDF Export Akışı

```mermaid
sequenceDiagram
    participant U as Kullanıcı
    participant GUI as DndPage
    participant FD as FileDialog
    participant PE as PDFExporter
    participant RL as ReportLab
    
    U->>GUI: "PDF Export" butonuna tıkla
    GUI->>FD: Çıktı dosyası seç
    FD-->>U: Dosya yolu seç
    U->>FD: Kayıt konumu seç
    FD-->>GUI: Çıktı yolu
    
    GUI->>FD: Arkaplan görseli seç (opsiyonel)
    FD-->>GUI: Arkaplan yolu (veya None)
    
    GUI->>PE: export_dnd_character_pdf()
    PE->>RL: Canvas oluştur
    RL-->>PE: Canvas objesi
    
    alt Arkaplan var
        PE->>RL: drawImage(background)
    end
    
    PE->>RL: drawImage(logo)
    PE->>RL: drawString(başlık)
    PE->>RL: drawString(karakter bilgileri)
    PE->>RL: drawString(yetenekler)
    PE->>RL: drawString(beceriler)
    PE->>RL: drawString(büyüler)
    PE->>RL: drawString(envanter)
    PE->>RL: drawString(kişilik)
    
    PE->>RL: showPage()
    PE->>RL: save()
    RL-->>PE: PDF dosyası oluşturuldu
    
    PE-->>GUI: Başarılı
    GUI-->>U: PDF oluşturuldu mesajı
```

### Level Up Akışı

```mermaid
sequenceDiagram
    participant U as Kullanıcı
    participant GUI as DndPage
    participant LM as LevelUpManager
    participant S as Storage
    participant DL as DataLoader
    
    U->>GUI: "Level Up" sekmesine geç
    GUI->>LM: _init_levelup_ui()
    LM->>S: list_characters()
    S-->>LM: Karakter listesi
    LM->>LM: Karakter listesini göster
    
    U->>LM: Karakter seç
    LM->>S: load_character()
    S-->>LM: Karakter verisi
    LM->>LM: _load_character_for_levelup()
    LM->>LM: Mevcut seviyeyi göster
    
    U->>LM: Yeni seviye seç
    LM->>DL: Sınıf özelliklerini yükle
    DL-->>LM: Seviye özellikleri
    LM->>LM: _update_class_features()
    LM->>LM: ASI/Feat seçeneklerini göster
    
    U->>LM: ASI veya Feat seç
    LM->>LM: Seçimi doğrula
    LM->>LM: Önizlemeyi güncelle
    
    U->>LM: "Level Up" butonuna tıkla
    LM->>LM: _level_up_character()
    LM->>LM: Seviyeyi artır
    LM->>LM: Özellikleri ekle
    LM->>LM: HP'yi güncelle
    LM->>LM: Prof bonusunu güncelle
    
    LM->>S: save_character()
    S->>S: Güncellenmiş karakteri kaydet
    S-->>LM: Başarılı
    
    LM-->>GUI: Level up tamamlandı
    GUI-->>U: Seviye atlandı mesajı
```

---

## 🗄️ Veritabanı Şeması

### SQLite Veritabanı Yapısı

```mermaid
erDiagram
    CHARACTERS {
        int id PK "PRIMARY KEY AUTOINCREMENT"
        string system "NOT NULL - DND5E, M&M, VtM"
        string name "NOT NULL"
        string data "NOT NULL - JSON string"
        datetime created_at "AUTO - INSERT trigger"
        datetime updated_at "AUTO - UPDATE trigger"
    }
    
    CHARACTERS ||--o{ CHARACTER_METADATA : "has"
    
    CHARACTER_METADATA {
        int id PK
        int character_id FK
        string key "metadata key"
        string value "metadata value"
    }
    
    CHARACTER_VERSIONS {
        int id PK
        int character_id FK
        int version_number
        string data "JSON string"
        datetime created_at
    }
    
    CHARACTERS ||--o{ CHARACTER_VERSIONS : "has versions"
```

### JSON Veri Yapısı (characters/)

```mermaid
graph TB
    A[Karakter JSON Dosyası] --> B[system: DND5E]
    A --> C[name: string]
    A --> D[race: string]
    A --> E[class: string]
    A --> F[level: int]
    A --> G[abilities: dict]
    A --> H[ability_modifiers: dict]
    A --> I[skills: dict]
    A --> J[spells: dict]
    A --> K[feats: list]
    A --> L[equipment: list]
    A --> M[inventory: list]
    A --> N[personality: dict]
    A --> O[physical: dict]
    A --> P[appearance: dict]
    A --> P1[image: string (base64)]
    A --> Q[background: string]
    A --> R[background_features: dict]
    A --> S[class_features: dict]
    A --> T[equipment_effects: dict]
    
    G --> G1[Strength: int]
    G --> G2[Dexterity: int]
    G --> G3[Constitution: int]
    G --> G4[Intelligence: int]
    G --> G5[Wisdom: int]
    G --> G6[Charisma: int]
    
    I --> I1[class_skills: list]
    I --> I2[proficiencies: dict]
    
    J --> J1[cantrips: list]
    J --> J2[1st_level: list]
    J --> J3[spell_slots: dict]
    
    M --> M1[name: string]
    M --> M2[category: string]
    M --> M3[weight: float]
    M --> M4[quantity: int]
    M --> M5[equipped: bool]
    M --> M6[data: dict]
    
    N --> N1[trait: string]
    N --> N2[ideal: string]
    N --> N3[bond: string]
    N --> N4[flaw: string]
    N --> N5[alignment: string]
    
    O --> O1[height: string]
    O --> O2[weight: string]
    O --> O3[age: string]
    
    P --> P1[hair_color: string]
    P --> P2[eye_color: string]
    P --> P3[skin_color: string]
    P --> P4[description: string]
```

### Veri İlişkileri

```mermaid
erDiagram
    DND_DATA {
        string races "23 ırk"
        string classes "14 sınıf"
        string backgrounds "arka planlar"
        string feats "42 feat"
        string spells "büyüler"
        string items "1000+ eşya"
    }
    
    CHARACTER {
        string race "FK -> races"
        string class "FK -> classes"
        string background "FK -> backgrounds"
        list feats "FK -> feats"
        list spells "FK -> spells"
        list inventory "FK -> items"
    }
    
    RACE {
        string name PK
        dict ability_score_increase
        list traits
        int speed
    }
    
    CLASS {
        string name PK
        string hit_die
        list primary_ability
        list saving_throws
        list class_skills
        dict class_features
    }
    
    FEAT {
        string name PK
        dict prerequisites
        string description
    }
    
    SPELL {
        string name PK
        string level
        string school
        string description
    }
    
    ITEM {
        string name PK
        string category
        float weight
        string cost
        dict properties
    }
    
    DND_DATA ||--o{ RACE : contains
    DND_DATA ||--o{ CLASS : contains
    DND_DATA ||--o{ FEAT : contains
    DND_DATA ||--o{ SPELL : contains
    DND_DATA ||--o{ ITEM : contains
    
    CHARACTER }o--|| RACE : uses
    CHARACTER }o--|| CLASS : uses
    CHARACTER }o--o{ FEAT : has
    CHARACTER }o--o{ SPELL : knows
    CHARACTER }o--o{ ITEM : owns
```

---

## 🔌 API/Interface Şeması

### Modül Arayüzleri

```mermaid
graph TB
    subgraph "Public API"
        A[data_loader.py] --> A1[load_dnd_data: Path -> dict]
        B[storage.py] --> B1[init_db: Path -> None]
        B --> B2[save_character: Path, CharacterRecord -> int]
        B --> B3[load_character: Path, int -> CharacterRecord]
        B --> B4[list_characters: Path -> list[CharacterRecord]]
        C[export_pdf.py] --> C1[export_dnd_character_pdf: dict, Path, Path, str -> None]
    end
    
    subgraph "Internal API"
        D[DndPage] --> D1[_load_dnd_data: -> dict]
        D --> D2[_create_character: -> dict]
        D --> D3[_save_character_to_file: -> None]
        D --> D4[_load_existing_character: -> None]
        D --> D5[_load_character_to_gui: dict -> None]
    end
    
    subgraph "Data Structures"
        E[CharacterRecord] --> E1[id: int]
        E --> E2[system: str]
        E --> E3[name: str]
        E --> E4[data: dict]
    end
```

### Fonksiyon İmzaları

```python
# utils/data_loader.py
def load_dnd_data(base_dir: Path) -> Dict[str, Any]:
    """
    D&D verisini yükler ve background dosyalarını birleştirir.
    
    Args:
        base_dir: Proje ana dizini
        
    Returns:
        Tüm D&D verilerini içeren dict
    """

# utils/storage.py
def init_db(db_path: Path) -> None:
    """SQLite veritabanını başlatır."""

def save_character(db_path: Path, record: CharacterRecord) -> int:
    """
    Karakteri SQLite'a kaydeder.
    
    Returns:
        Kaydedilen karakterin ID'si
    """

def load_character(db_path: Path, record_id: int) -> Optional[CharacterRecord]:
    """ID ile karakteri yükler."""

def list_characters(db_path: Path) -> list[CharacterRecord]:
    """Tüm karakterleri listeler."""

# utils/export_pdf.py
def export_dnd_character_pdf(
    character: dict,
    output_path: Path,
    background_path: Optional[Path] = None,
    page_size: str = "A4"
) -> None:
    """
    D&D karakterini PDF'e export eder.
    
    Args:
        character: Karakter verisi
        output_path: PDF çıktı yolu
        background_path: Opsiyonel arkaplan görseli
        page_size: A4 veya Letter
    """

# gui/app.py - DndPage
class DndPage(QWidget):
    def _load_dnd_data(self) -> dict:
        """D&D verisini cache ile yükler."""
    
    def _create_character(self) -> dict:
        """GUI'den karakter oluşturur."""
    
    def _save_character_to_file(self) -> None:
        """Karakteri JSON dosyasına kaydeder."""
    
    def _load_existing_character(self) -> None:
        """JSON/SQLite'dan karakter yükler."""
    
    def _load_character_to_gui(self, character: dict) -> None:
        """Karakter verisini GUI'ye yükler."""
```

### Veri Kontratları

```mermaid
graph LR
    A[Karakter Verisi] --> B[Validasyon]
    B --> C{Geçerli mi?}
    C -->|Evet| D[İşleme]
    C -->|Hayır| E[Hata]
    
    B --> B1[system: DND5E]
    B --> B2[name: non-empty]
    B --> B3[race: valid race]
    B --> B4[class: valid class]
    B --> B5[abilities: 6 keys]
    B --> B6[level: 1-20]
```

---

## 🔀 State Diyagramları

### Karakter Oluşturma State Machine

```mermaid
stateDiagram-v2
    [*] --> AnaMenu
    
    AnaMenu --> YeniKarakter: Yeni Karakter
    AnaMenu --> KarakterYukle: Karakter Yükle
    AnaMenu --> MevcutKarakterler: Mevcut Karakterler
    
    YeniKarakter --> WizardAdim1: Başlat
    WizardAdim1 --> WizardAdim2: İsim & Irk Seç
    WizardAdim2 --> WizardAdim3: Sınıf Seç
    WizardAdim3 --> WizardAdim4: Arka Plan Seç
    WizardAdim4 --> WizardAdim5: Yetenek Puanları
    WizardAdim5 --> WizardAdim6: Beceriler
    WizardAdim6 --> WizardAdim7: Büyüler
    WizardAdim7 --> WizardAdim8: Feat'ler
    WizardAdim8 --> WizardAdim9: Kişisel Özellikler
    WizardAdim9 --> WizardAdim10: Fiziksel Özellikler
    WizardAdim10 --> WizardAdim11: Görünüm
    WizardAdim11 --> KarakterOlusturuldu: Tamamla
    
    KarakterOlusturuldu --> KarakterSekmeleri: Göster
    KarakterSekmeleri --> KarakterBilgileri: Karakter Sekmesi
    KarakterSekmeleri --> Buyuler: Büyüler Sekmesi
    KarakterSekmeleri --> LevelUp: Level Up Sekmesi
    KarakterSekmeleri --> Envanter: Envanter Sekmesi
    KarakterSekmeleri --> Dice: Dice Sekmesi
    
    KarakterYukle --> KarakterYuklendi: Dosya Seç
    KarakterYuklendi --> KarakterSekmeleri: Yükle
    
    MevcutKarakterler --> KarakterSecildi: Karakter Seç
    KarakterSecildi --> KarakterSekmeleri: Aç
    
    KarakterSekmeleri --> AnaMenu: Ana Menüye Dön
    KarakterSekmeleri --> Kaydet: Kaydet
    Kaydet --> KarakterSekmeleri: Başarılı
    
    KarakterSekmeleri --> PDFExport: PDF Export
    PDFExport --> KarakterSekmeleri: Tamamlandı
    
    LevelUp --> SeviyeAtlandi: Level Up
    SeviyeAtlandi --> KarakterSekmeleri: Güncelle
```

### Karakter Verisi State Machine

```mermaid
stateDiagram-v2
    [*] --> Bos
    
    Bos --> Olusturuluyor: Wizard Başlatıldı
    Olusturuluyor --> Gecersiz: Validasyon Başarısız
    Olusturuluyor --> Gecerli: Validasyon Başarılı
    
    Gecerli --> Kaydediliyor: Kaydet Butonu
    Kaydediliyor --> Kaydedildi: JSON/SQLite
    Kaydediliyor --> Hata: Kayıt Hatası
    
    Kaydedildi --> Yukleniyor: Yükle Butonu
    Yukleniyor --> Gecerli: Yükleme Başarılı
    Yukleniyor --> Hata: Yükleme Hatası
    
    Gecerli --> Duzenleniyor: Düzenle
    Duzenleniyor --> Gecerli: Değişiklikler Kaydedildi
    Duzenleniyor --> Gecersiz: Geçersiz Değişiklik
    
    Gecerli --> ExportEdiliyor: PDF Export
    ExportEdiliyor --> Gecerli: Export Başarılı
    ExportEdiliyor --> Hata: Export Hatası
    
    Hata --> Gecerli: Düzelt
    Gecersiz --> Duzenleniyor: Düzelt
```

---

## 🧩 Component Diyagramları

### Sistem Bileşenleri

```mermaid
graph TB
    subgraph "Presentation Layer"
        A[MainWindow<br/>PySide6]
        B[DndPage<br/>GUI]
        C[MmPage<br/>Placeholder]
        D[VtmPage<br/>Placeholder]
    end
    
    subgraph "Business Logic Layer"
        E[CharacterCreator<br/>Karakter Oluşturma]
        F[CharacterValidator<br/>Validasyon]
        G[calculations.py<br/>Otomatik Hesaplamalar]
        G1[calculate_dnd_stats<br/>D&D Hesaplamaları]
        G2[calculate_mm_stats<br/>M&M Hesaplamaları]
        G3[calculate_vtm_stats<br/>VtM Hesaplamaları]
        G --> G1
        G --> G2
        G --> G3
        RULE_EXT[rule_extractor.py<br/>Kural Çıkarma]
        RULE_STOR[rule_storage.py<br/>Kural Saklama]
        DYN_CALC[dynamic_calculator.py<br/>Dinamik Hesaplama]
        RULE_EXT --> RULE_STOR
        RULE_STOR --> DYN_CALC
        DYN_CALC --> G
    end
    
    subgraph "Data Access Layer"
        H[DataLoader<br/>JSON Yükleme]
        I[Storage<br/>SQLite/JSON]
        J[PDFExporter<br/>PDF Oluşturma]
    end
    
    subgraph "Data Layer"
        K[dnd_data.json<br/>3631 satır]
        L[mm_data.json]
        M[vtm_data.json]
        N[characters/<br/>JSON dosyaları]
        O[*.db<br/>SQLite dosyaları]
        P[data/rules/<br/>Kural dosyaları]
    end
    
    A --> B
    A --> C
    A --> D
    
    B --> E
    B --> F
    B --> G
    B --> RULE_EXT
    
    E --> H
    E --> I
    F --> H
    G --> H
    B --> J
    RULE_EXT --> RULE_STOR
    RULE_STOR --> DYN_CALC
    DYN_CALC --> G
    
    H --> K
    H --> L
    H --> M
    I --> N
    I --> O
    J --> N
    RULE_STOR --> P
    DYN_CALC --> P
```

### Modül Bağımlılıkları

```mermaid
graph LR
    A[main.py] --> B[gui/app.py]
    B --> C[utils/data_loader.py]
    B --> D[utils/storage.py]
    B --> E[utils/export_pdf.py]
    B --> F[creators/dnd_integrated.py]
    
    F --> G[dnd_creator.py]
    G --> C
    
    B --> H[PySide6]
    B --> I[qdarkstyle]
    E --> J[reportlab]
    E --> K[Pillow]
    D --> L[sqlite3]
    
    C --> M[data/dnd_data.json]
    C --> N[data/mm_data.json]
    C --> O[data/vtm_data.json]
    
    D --> P[characters/*.json]
    D --> Q[*.db]
    
    style A fill:#3498db
    style B fill:#2ecc71
    style C fill:#f39c12
    style D fill:#e74c3c
    style E fill:#9b59b6
```

---

## 📊 Veri Akış Detayları

### Karakter Verisi İşleme Pipeline

```mermaid
flowchart TD
    A[Kullanıcı Girdileri] --> B[Form Validasyonu]
    B --> C{Geçerli mi?}
    C -->|Hayır| D[Hata Mesajı]
    C -->|Evet| E[Veri Toplama]
    
    E --> F[Irk Bonusları Uygula]
    F --> G[Modifikatörleri Hesapla]
    G --> H[AC Hesapla]
    H --> I[HP Hesapla]
    I --> J[Proficiency Bonus Hesapla]
    J --> K[Skill Modifiers Hesapla]
    K --> L[Karakter Objesi]
    
    L --> M{Kayıt Tipi?}
    M -->|JSON| N[JSON Serialize]
    M -->|SQLite| O[SQLite Insert]
    
    N --> P[Dosyaya Yaz]
    O --> Q[Veritabanına Yaz]
    
    P --> R[Başarılı]
    Q --> R
    
    D --> S[Kullanıcıya Göster]
    R --> T[GUI Güncelle]
```

### Cache Mekanizması

```mermaid
flowchart LR
    A[Veri İsteği] --> B{Cache var mı?}
    B -->|Evet| C[Cache'den Döndür]
    B -->|Hayır| D[Dosyadan Oku]
    D --> E[JSON Parse]
    E --> F[Cache'e Kaydet]
    F --> G[Döndür]
    
    H[Veri Değişikliği] --> I[Cache'i Temizle]
    I --> J[Yeni Veri Yükle]
```

---

## 🔐 Güvenlik ve Validasyon

### Input Validasyon Şeması

```mermaid
graph TB
    A[Kullanıcı Girdisi] --> B[Type Check]
    B --> C[Range Check]
    C --> D[Format Check]
    D --> E[Business Rule Check]
    E --> F{Geçerli mi?}
    F -->|Evet| G[İşleme]
    F -->|Hayır| H[Hata Mesajı]
    
    B --> B1[String: non-empty]
    B --> B2[Integer: 1-20]
    B --> B3[Float: >= 0]
    
    C --> C1[Ability: 8-15 base]
    C --> C2[Level: 1-20]
    C --> C3[Weight: >= 0]
    
    D --> D1[Name: alphanumeric + spaces]
    D --> D2[Email: valid format]
    
    E --> E1[Point Buy: total <= 27]
    E --> E2[Feat Prerequisites]
    E --> E3[Class Requirements]
```

---

**Oluşturulma Tarihi**: 2024  
**Versiyon**: 2.0 - Detaylı Şemalar  
**Geliştirici**: Deniz Şahin (2221032838)


