# Diyargezen FRP Karakter Yaratıcısı - Görsel Şemalar

## 📋 İçindekiler
1. [PlantUML Şemaları](#plantuml-şemaları)
2. [Görsel Mimari Diyagramları](#görsel-mimari-diyagramları)
3. [Kullanım Kılavuzu](#kullanım-kılavuzu)

---

## 🎨 PlantUML Şemaları

### Sistem Mimarisi (PlantUML)

```plantuml
@startuml Sistem_Mimarisi
!theme plain
skinparam backgroundColor #FFFFFF
skinparam componentStyle rectangle

package "Giriş Noktası" {
    [main.py] as Main
}

package "GUI Katmanı" {
    [MainWindow] as MW
    [DndPage] as DND
    [MmPage] as MM
    [VtmPage] as VTM
}

package "İş Mantığı" {
    [CharacterCreator] as CC
    [CharacterValidator] as CV
    [CharacterCalculator] as Calc
}

package "Veri Erişimi" {
    [DataLoader] as DL
    [Storage] as ST
    [PDFExporter] as PDF
}

package "Veri Katmanı" {
    database "dnd_data.json" as DND_DATA
    database "mm_data.json" as MM_DATA
    database "vtm_data.json" as VTM_DATA
    folder "characters/" as CHARS
    database "*.db" as DB
}

Main --> MW : başlatır
MW --> DND : içerir
MW --> MM : içerir
MW --> VTM : içerir

DND --> CC : kullanır
DND --> CV : kullanır
DND --> Calc : kullanır

CC --> DL : veri yükler
CV --> DL : veri yükler
Calc --> DL : veri yükler

DND --> ST : kayıt/yükleme
DND --> PDF : export

DL --> DND_DATA : okur
DL --> MM_DATA : okur
DL --> VTM_DATA : okur

ST --> CHARS : JSON yazar
ST --> DB : SQLite yazar
PDF --> CHARS : okur

@enduml
```

### Detaylı Sınıf Diyagramı (PlantUML)

```plantuml
@startuml Detayli_Sinif_Diyagrami
!theme plain
skinparam classAttributeIconSize 0

class MainWindow {
    -QTabWidget central
    -DndPage dnd_page
    -MmPage mm_page
    -VtmPage vtm_page
    --
    +__init__()
    +_apply_dark_theme()
    +_setup_shortcuts()
    +_set_window_icon()
}

class DndPage {
    -dict data
    -dict current_character
    -list inventory_items
    -QStackedWidget stacked_widget
    -QTabWidget tab_widget
    --
    +_load_dnd_data() : dict
    +_create_character() : dict
    +_save_character_to_file()
    +_load_existing_character()
    +_load_character_to_gui(dict)
    +_init_character_ui()
    +_init_spells_ui()
    +_init_levelup_ui()
    +_init_inventory_ui()
    +_init_dice_ui()
}

class DataLoader {
    +load_dnd_data(Path) : dict
}

class Storage {
    +init_db(Path)
    +save_character(Path, CharacterRecord) : int
    +load_character(Path, int) : CharacterRecord
    +list_characters(Path) : list
}

class PDFExporter {
    +export_dnd_character_pdf(dict, Path, Path, str)
}

class CharacterRecord {
    +int id
    +str system
    +str name
    +dict data
}

MainWindow "1" *-- "1" DndPage : contains
MainWindow "1" *-- "1" MmPage : contains
MainWindow "1" *-- "1" VtmPage : contains

DndPage ..> DataLoader : uses
DndPage ..> Storage : uses
DndPage ..> PDFExporter : uses

Storage ..> CharacterRecord : uses
PDFExporter ..> CharacterRecord : uses

@enduml
```

### Veritabanı ER Diyagramı (PlantUML)

```plantuml
@startuml Veritabani_ER
!theme plain
skinparam linetype ortho

entity "CHARACTERS" {
    * id : INTEGER <<PK>>
    --
    * system : TEXT
    * name : TEXT
    * data : TEXT <<JSON>>
    created_at : DATETIME
    updated_at : DATETIME
}

entity "CHARACTER_METADATA" {
    * id : INTEGER <<PK>>
    --
    * character_id : INTEGER <<FK>>
    * key : TEXT
    * value : TEXT
}

entity "CHARACTER_VERSIONS" {
    * id : INTEGER <<PK>>
    --
    * character_id : INTEGER <<FK>>
    * version_number : INTEGER
    * data : TEXT <<JSON>>
    created_at : DATETIME
}

CHARACTERS ||--o{ CHARACTER_METADATA : "has metadata"
CHARACTERS ||--o{ CHARACTER_VERSIONS : "has versions"

@enduml
```

### Sequence Diyagramı (PlantUML)

```plantuml
@startuml Karakter_Olusturma_Sequence
!theme plain
autonumber

actor Kullanıcı
participant "DndPage" as GUI
participant "CharacterWizard" as WIZ
participant "DataLoader" as DL
participant "CharacterCreator" as CC
participant "Storage" as ST

Kullanıcı -> GUI: "Yeni Karakter" tıkla
GUI -> WIZ: _start_new_character()
WIZ -> GUI: Wizard UI göster

Kullanıcı -> WIZ: İsim ve Irk seç
WIZ -> DL: Irk verilerini yükle
DL --> WIZ: Irk verileri

Kullanıcı -> WIZ: Sınıf seç
WIZ -> DL: Sınıf verilerini yükle
DL --> WIZ: Sınıf verileri

Kullanıcı -> WIZ: Tüm bilgileri gir
Kullanıcı -> WIZ: "Karakter Oluştur" tıkla

WIZ -> CC: _create_character()
CC -> CC: Irk bonuslarını uygula
CC -> CC: Modifikatörleri hesapla
CC --> WIZ: Karakter objesi

WIZ -> GUI: Karakteri kaydet
GUI -> ST: _save_character_to_file()
ST -> ST: JSON dosyasına yaz
ST --> GUI: Başarılı

GUI --> Kullanıcı: Karakter oluşturuldu

@enduml
```

---

## 🏗️ Görsel Mimari Diyagramları

### Katmanlı Mimari

```
┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │MainWindow│  │ DndPage   │  │ MmPage   │           │
│  │ (PySide6)│  │ (4296 satır)│ │ (Placeholder)│        │
│  └────┬─────┘  └────┬──────┘  └──────────┘           │
│       │             │                                  │
└───────┼─────────────┼──────────────────────────────────┘
        │             │
        ▼             ▼
┌─────────────────────────────────────────────────────────┐
│                  BUSINESS LOGIC LAYER                    │
│  ┌──────────────┐  ┌──────────────┐                  │
│  │Character     │  │Character      │                  │
│  │Creator       │  │Validator      │                  │
│  └──────┬───────┘  └──────┬───────┘                  │
│         │                 │                           │
│  ┌──────▼─────────────────▼───────┐                  │
│  │  CharacterCalculator            │                  │
│  │  - AC Hesaplama                  │                  │
│  │  - HP Hesaplama                  │                  │
│  │  - Modifikatör Hesaplama         │                  │
│  └──────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                  DATA ACCESS LAYER                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │DataLoader│  │ Storage   │  │PDFExporter│           │
│  │ (JSON)   │  │(SQLite/   │  │(ReportLab)│           │
│  │          │  │ JSON)     │  │           │           │
│  └────┬─────┘  └────┬──────┘  └────┬──────┘           │
└───────┼─────────────┼───────────────┼───────────────────┘
        │             │               │
        ▼             ▼               ▼
┌─────────────────────────────────────────────────────────┐
│                    DATA LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐│
│  │dnd_data.json │  │characters/    │  │*.db          ││
│  │(3631 satır)  │  │*.json         │  │(SQLite)      ││
│  └──────────────┘  └──────────────┘  └─────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Veri Akış Diyagramı (ASCII)

```
                    ┌─────────────┐
                    │  Kullanıcı  │
                    └──────┬──────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │         GUI Formları                │
        │  - İsim, Irk, Sınıf                │
        │  - Yetenek Puanları                 │
        │  - Beceriler, Büyüler               │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │     Karakter Validasyonu             │
        │  - Type Check                        │
        │  - Range Check                       │
        │  - Business Rules                    │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │     Karakter Objesi Oluşturma        │
        │  - Irk Bonusları Uygula             │
        │  - Modifikatörleri Hesapla           │
        │  - AC, HP Hesapla                    │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │         Kayıt Seçimi                 │
        └──────┬──────────────────┬──────────┘
               │                  │
               ▼                  ▼
    ┌─────────────────┐  ┌─────────────────┐
    │  JSON Export    │  │ SQLite Export    │
    │  characters/    │  │ *.db            │
    └─────────────────┘  └─────────────────┘
               │                  │
               └────────┬─────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │   PDF Export          │
            │   (Opsiyonel)         │
            └───────────────────────┘
```

### Modül Bağımlılık Ağacı

```
main.py
│
├── gui/app.py (4296 satır)
│   │
│   ├── utils/data_loader.py
│   │   └── data/dnd_data.json
│   │   └── data/mm_data.json
│   │   └── data/vtm_data.json
│   │
│   ├── utils/storage.py
│   │   ├── characters/*.json
│   │   └── *.db (SQLite)
│   │
│   ├── utils/export_pdf.py
│   │   ├── reportlab
│   │   └── Pillow
│   │
│   └── creators/dnd_integrated.py
│       └── dnd_creator.py
│
├── PySide6 (GUI Framework)
├── qdarkstyle (Theme)
└── External Dependencies
    ├── reportlab (PDF)
    ├── Pillow (Images)
    └── sqlite3 (Database)
```

---

## 📐 Kullanım Kılavuzu

### PlantUML Kullanımı

1. **PlantUML Kurulumu**:
```bash
# Java gereklidir
# PlantUML JAR dosyasını indirin
wget http://sourceforge.net/projects/plantuml/files/plantuml.jar/download -O plantuml.jar
```

2. **Diyagram Oluşturma**:
```bash
# PlantUML dosyasını PNG'ye çevir
java -jar plantuml.jar -tpng DETAYLI_SEMALAR.md

# SVG formatında
java -jar plantuml.jar -tsvg DETAYLI_SEMALAR.md
```

3. **Online Kullanım**:
   - http://www.plantuml.com/plantuml/ adresine gidin
   - PlantUML kodunu yapıştırın
   - PNG/SVG olarak indirin

### Mermaid Kullanımı

1. **Online Editor**:
   - https://mermaid.live/ adresine gidin
   - Mermaid kodunu yapıştırın
   - PNG/SVG olarak export edin

2. **VS Code Extension**:
   - "Markdown Preview Mermaid Support" extension'ını yükleyin
   - Markdown dosyalarında otomatik render

3. **GitHub/GitLab**:
   - Markdown dosyalarında otomatik render edilir
   - Pull request'lerde görsel olarak gösterilir

### Görsel Şema Oluşturma Scripti

Aşağıdaki Python scriptini kullanarak görsel şemalar oluşturabilirsiniz:

```python
# generate_diagrams.py
# Bu script Mermaid diyagramlarını görselleştirmek için kullanılabilir
# Ancak doğrudan Python ile Mermaid render etmek için
# mermaid.ink API veya benzeri servisler kullanılmalıdır
```

---

## 🎯 Şema Türleri ve Kullanım Alanları

| Şema Türü | Format | Kullanım Alanı | Araç |
|-----------|--------|----------------|------|
| Sistem Mimarisi | Mermaid/PlantUML | Genel sistem yapısı | Mermaid Live, PlantUML |
| Sınıf Diyagramı | UML/PlantUML | Kod yapısı | PlantUML, draw.io |
| Sequence Diyagramı | Mermaid/PlantUML | İşlem akışları | Mermaid Live, PlantUML |
| ER Diyagramı | PlantUML | Veritabanı yapısı | PlantUML, dbdiagram.io |
| State Diyagramı | Mermaid | Durum geçişleri | Mermaid Live |
| Component Diyagramı | Mermaid/PlantUML | Bileşen ilişkileri | Mermaid Live, PlantUML |

---

## 📝 Notlar

1. **PlantUML**: Java tabanlı, çok güçlü UML diyagram aracı
2. **Mermaid**: JavaScript tabanlı, markdown içinde kullanılabilir
3. **Görsel Şemalar**: ASCII art veya görsel araçlarla oluşturulabilir
4. **Export**: Tüm şemalar PNG, SVG veya PDF formatında export edilebilir

---

**Oluşturulma Tarihi**: 2024  
**Versiyon**: 1.0 - Görsel Şemalar  
**Geliştirici**: Deniz Şahin (2221032838)


