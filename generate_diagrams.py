#!/usr/bin/env python3
"""
Diyargezen Proje Şemaları - Görsel Diyagram Oluşturucu
Bu script, proje şemalarını görselleştirmek için yardımcı araçlar sağlar.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any


def create_project_structure_diagram() -> str:
    """Proje yapısını görselleştiren ASCII diyagram oluşturur"""
    diagram = """
Diyargezen Proje Yapısı
═══════════════════════════════════════════════════════════

Diyargezen/
│
├── 📄 main.py                    # Ana giriş noktası
├── 📄 dnd_creator.py             # D&D terminal oluşturucu
├── 📄 mm_creator.py              # M&M oluşturucu
├── 📄 vtm_creator.py             # VtM oluşturucu
│
├── 📁 gui/
│   ├── 📄 app.py                 # Ana GUI (4296 satır) ⭐
│   ├── 📄 app_backup.py         # Yedek
│   ├── 📄 app_clean.py          # Temiz versiyon
│   └── 📄 app_simple.py         # Basit versiyon
│
├── 📁 creators/
│   ├── 📄 __init__.py
│   └── 📄 dnd_integrated.py      # Entegre D&D
│
├── 📁 utils/
│   ├── 📄 data_loader.py         # JSON yükleme
│   ├── 📄 storage.py             # SQLite/JSON kayıt
│   └── 📄 export_pdf.py         # PDF export
│
├── 📁 data/
│   ├── 📄 dnd_data.json          # D&D verileri (3631 satır)
│   ├── 📄 mm_data.json           # M&M verileri
│   ├── 📄 vtm_data.json          # VtM verileri
│   └── 📁 backgrounds/
│       └── 📄 srd_examples.json
│
├── 📁 characters/                # Oluşturulan karakterler
│   └── 📄 *.json                 # Karakter dosyaları
│
├── 📁 assets/
│   └── 📄 diyargezer_logo.png    # Logo
│
├── 📄 requirements.txt           # Bağımlılıklar
└── 📄 README.md                  # Dokümantasyon

═══════════════════════════════════════════════════════════
"""
    return diagram


def create_data_flow_diagram() -> str:
    """Veri akış diyagramını ASCII formatında oluşturur"""
    diagram = """
Veri Akış Diyagramı
═══════════════════════════════════════════════════════════

                    ┌─────────────┐
                    │  Kullanıcı  │
                    └──────┬──────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │         GUI Formları                │
        │  • İsim, Irk, Sınıf                 │
        │  • Yetenek Puanları (Point Buy)      │
        │  • Beceriler, Büyüler, Feat'ler     │
        │  • Kişisel Özellikler               │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │     Karakter Validasyonu             │
        │  ✓ Type Check                        │
        │  ✓ Range Check (8-15, 1-20)          │
        │  ✓ Point Buy Total (≤27)            │
        │  ✓ Feat Prerequisites                │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │     Karakter Objesi Oluşturma       │
        │  • Irk Bonusları Uygula             │
        │  • Modifikatörleri Hesapla          │
        │  • AC = 10 + Dex Mod                │
        │  • HP = Hit Die + Con Mod           │
        │  • Proficiency Bonus Hesapla        │
        └──────────────┬─────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │         Kayıt Seçimi                │
        └──────┬──────────────────┬──────────┘
               │                  │
               ▼                  ▼
    ┌─────────────────┐  ┌─────────────────┐
    │  JSON Export    │  │ SQLite Export    │
    │  characters/    │  │ *.db            │
    │  {name}_karakter│  │ id, system, name │
    │  .json          │  │ data (JSON)      │
    └─────────────────┘  └─────────────────┘
               │                  │
               └────────┬─────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │   PDF Export          │
            │   (Opsiyonel)         │
            │   + Arkaplan Desteği  │
            └───────────────────────┘

═══════════════════════════════════════════════════════════
"""
    return diagram


def create_architecture_diagram() -> str:
    """Mimari diyagramını ASCII formatında oluşturur"""
    diagram = """
Katmanlı Mimari Yapısı
═══════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │ MainWindow   │  │   DndPage    │  │   MmPage     ││
│  │ (PySide6)    │  │ (4296 satır) │  │ (Placeholder)││
│  │              │  │              │  │              ││
│  │ • Dark Theme │  │ • Wizard     │  │ • Yakında    ││
│  │ • Shortcuts  │  │ • Tabs       │  │              ││
│  │ • Icon       │  │ • Forms     │  │              ││
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘│
│         │                 │                          │
└─────────┼─────────────────┼──────────────────────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────────────────────────┐
│                  BUSINESS LOGIC LAYER                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  CharacterCreator                                │  │
│  │  • _create_character()                           │  │
│  │  • Irk bonusları uygula                          │  │
│  │  • Modifikatörleri hesapla                       │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  CharacterValidator                              │  │
│  │  • Point buy kontrolü                            │  │
│  │  • Feat prerequisites                            │  │
│  │  • Sınıf gereksinimleri                          │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  CharacterCalculator                             │  │
│  │  • AC = 10 + Dex Mod                             │  │
│  │  • HP = Hit Die + Con Mod                        │  │
│  │  • Proficiency Bonus                             │  │
│  │  • Skill Modifiers                               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│                  DATA ACCESS LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │ DataLoader   │  │   Storage    │  │ PDFExporter  ││
│  │              │  │              │  │              ││
│  │ • JSON Parse │  │ • SQLite     │  │ • ReportLab  ││
│  │ • Cache    │  │ • JSON Write   │  │ • Pillow     ││
│  │ • Merge      │  │ • CRUD       │  │ • Background ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘│
└─────────┼─────────────────┼─────────────────┼─────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────┐
│                    DATA LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │dnd_data.json │  │characters/   │  │*.db          ││
│  │(3631 satır)  │  │*.json        │  │(SQLite)      ││
│  │              │  │              │  │              ││
│  │• 23 Irk      │  │• Karakterler │  │• Veritabanı  ││
│  │• 14 Sınıf    │  │• JSON format │  │• JSON string ││
│  │• 42 Feat     │  │              │  │              ││
│  │• 1000+ Eşya  │  │              │  │              ││
│  └──────────────┘  └──────────────┘  └──────────────┘│
└─────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════
"""
    return diagram


def create_module_dependency_tree() -> str:
    """Modül bağımlılık ağacını oluşturur"""
    diagram = """
Modül Bağımlılık Ağacı
═══════════════════════════════════════════════════════════

main.py
│
├──► gui/app.py (4296 satır) ⭐ ANA MODÜL
│   │
│   ├──► utils/data_loader.py
│   │   ├──► data/dnd_data.json (3631 satır)
│   │   ├──► data/mm_data.json
│   │   └──► data/vtm_data.json
│   │
│   ├──► utils/storage.py
│   │   ├──► characters/*.json (JSON kayıt)
│   │   └──► *.db (SQLite kayıt)
│   │
│   ├──► utils/export_pdf.py
│   │   ├──► reportlab (PDF oluşturma)
│   │   ├──► Pillow (Görüntü işleme)
│   │   └──► assets/diyargezer_logo.png
│   │
│   └──► creators/dnd_integrated.py
│       └──► dnd_creator.py
│
├──► PySide6 (GUI Framework)
│   ├──► QtWidgets
│   ├──► QtCore
│   └──► QtGui
│
├──► qdarkstyle (Dark Theme)
│
└──► External Dependencies
    ├──► reportlab (PDF Export)
    ├──► Pillow (Image Processing)
    └──► sqlite3 (Database - Built-in)

═══════════════════════════════════════════════════════════
"""
    return diagram


def create_character_creation_flow() -> str:
    """Karakter oluşturma akışını görselleştirir"""
    diagram = """
Karakter Oluşturma Akışı
═══════════════════════════════════════════════════════════

[Başlangıç]
    │
    ▼
┌─────────────────┐
│   Ana Menü      │
│  (DndPage)      │
└────────┬────────┘
         │
         ├──► [Yeni Karakter] ──┐
         │                      │
         ├──► [Karakter Yükle] │
         │                      │
         └──► [Mevcut Karakterler]
                              │
                              ▼
                    ┌──────────────────┐
                    │  Karakter Wizard │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Adım 1-3     │    │ Adım 4        │    │ Adım 5-7     │
│              │    │              │    │              │
│ • İsim       │───►│ • Yetenek     │───►│ • Beceriler  │
│ • Irk        │    │   Puanları    │    │ • Büyüler    │
│ • Sınıf      │    │   (Point Buy) │    │ • Feat'ler   │
│ • Arka Plan  │    │               │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Adım 8-10        │
                    │                  │
                    │ • Kişisel        │
                    │   Özellikler     │
                    │ • Fiziksel       │
                    │   Özellikler     │
                    │ • Görünüm        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Karakter Objesi  │
                    │ Oluşturuluyor    │
                    │                  │
                    │ • Irk bonusları  │
                    │ • Modifikatörler │
                    │ • AC/HP hesapla  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Karakter         │
                    │ Oluşturuldu ✓    │
                    └────────┬─────────┘
                             │
                             ▼
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ JSON Kaydet  │    │ SQLite Kaydet│    │ PDF Export    │
│              │    │              │    │              │
│ characters/  │    │ *.db         │    │ *.pdf        │
└────────────┘    └──────────────┘    └──────────────┘

═══════════════════════════════════════════════════════════
"""
    return diagram


def save_diagrams_to_file(output_file: Path = Path("ASCII_SEMALAR.txt")):
    """Tüm diyagramları bir dosyaya kaydeder"""
    diagrams = [
        ("Proje Yapısı", create_project_structure_diagram()),
        ("Veri Akış Diyagramı", create_data_flow_diagram()),
        ("Mimari Diyagram", create_architecture_diagram()),
        ("Modül Bağımlılık Ağacı", create_module_dependency_tree()),
        ("Karakter Oluşturma Akışı", create_character_creation_flow()),
    ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("Diyargezen FRP Karakter Yaraticisi - ASCII Semalar\n")
        f.write("=" * 70 + "\n\n")
        
        for title, diagram in diagrams:
            f.write(f"\n{'=' * 70}\n")
            f.write(f"{title}\n")
            f.write(f"{'=' * 70}\n")
            f.write(diagram)
            f.write("\n\n")
    
    print(f"✅ Diyagramlar '{output_file}' dosyasına kaydedildi!")


def main():
    """Ana fonksiyon"""
    import sys
    import io
    
    # Windows encoding sorununu çöz
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("Diyargezen Proje Semalari Olusturucu")
    print("=" * 70)
    
    # ASCII diyagramları oluştur
    save_diagrams_to_file()
    
    print("\nOlusturulan Semalar:")
    print("  - Proje Yapisi")
    print("  - Veri Akis Diyagrami")
    print("  - Mimari Diyagram")
    print("  - Modul Bagimlilik Agaci")
    print("  - Karakter Olusturma Akisi")
    print("\nTamamlandi!")


if __name__ == "__main__":
    main()

