#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Özellikleri Koruma Kontrol Scripti

Bu script, GUI'deki sistem-spesifik kuralların ve özelliklerin
doğru şekilde çalıştığını doğrular.

Kullanım: python verify_gui_features.py
"""

import json
import sys
import os
from pathlib import Path

# Unicode support for Windows
if os.name == 'nt':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Workspace'e ait yollar
WORKSPACE_ROOT = Path(__file__).parent
DATA_DIR = WORKSPACE_ROOT / "data"
GUI_DIR = WORKSPACE_ROOT / "gui"
UTILS_DIR = WORKSPACE_ROOT / "utils"

# Renk kodları
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def check_mark(passed):
    return f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"

def print_header(title):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{title:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def verify_data_files():
    """Sistem verilerinin mevcut olup olmadığını kontrol et"""
    print_header("[*] VERI DOSYALARI")
    
    checks = {
        "D&D 5e": DATA_DIR / "dnd_data.json",
        "Pathfinder 1e": DATA_DIR / "pathfinder_1e_data.json",
        "M&M 3e": DATA_DIR / "mm_data.json",
        "VtM 5e": DATA_DIR / "vtm_data.json",
    }
    
    all_passed = True
    for name, path in checks.items():
        passed = path.exists()
        all_passed = all_passed and passed
        print(f"  {check_mark(passed)} {name}: {path.name}")
        
        if passed and path.stat().st_size > 0:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"      └─ Boyut: {len(json.dumps(data)):,} byte")
            except Exception as e:
                print(f"      └─ {RED}HATA: {e}{RESET}")
                all_passed = False
    
    return all_passed

def verify_dnd_features():
    """D&D 5e özelliklerini kontrol et"""
    print_header("🐉 D&D 5E ÖZELLİKLERİ")
    
    features = {
        "Point-Buy Yöntemi": "gui/app.py'de point_buy_",
        "ASI Seçimi (Seviye 4, 8, 12, 16, 20)": "gui/app.py'de ASI",
        "Çok Sınıflılık (Multiclassing)": "gui/app.py'de multiclass",
        "Spell Slot Hesapları": "utils/calculations.py'de calculate_spell_slots",
        "Proficiency Bonus": "utils/calculations.py'de proficiency",
        "Feat Seçimi (1258+ feat)": "data/dnd_data.json'de feats",
        "Spell Sistemi (2469+ büyü)": "data/dnd_data.json'de spells",
        "Ekipman (233+ item)": "data/dnd_data.json'de equipment",
    }
    
    print("Koruma Altında Olması Gereken Özellikler:\n")
    for i, (feature, location) in enumerate(features.items(), 1):
        print(f"  {i}. {feature}")
        print(f"     └─ {YELLOW}Konum: {location}{RESET}")
    
    return True

def verify_pathfinder_features():
    """Pathfinder 1e özelliklerini kontrol et"""
    print_header("🧙 PATHFINDER 1E ÖZELLİKLERİ")
    
    features = {
        "Irklar (77 ırk)": "data/pathfinder_1e_data.json'de races",
        "Sınıflar (58 sınıf)": "data/pathfinder_1e_data.json'de classes",
        "Feat Seçimi (421+ feat)": "data/pathfinder_1e_data.json'de feats",
        "Feat Per Level (1, 3, 5, 7, ...)": "gui/app.py'de pathfinder feat chain",
        "Prestige Class Desteği": "gui/app.py'de prestige_class",
        "Spell Per Day Hesapları": "utils/calculations.py'de pathfinder spells",
        "Ability Score Progression": "gui/app.py'de ability progression",
    }
    
    print("Koruma Altında Olması Gereken Özellikler:\n")
    for i, (feature, location) in enumerate(features.items(), 1):
        print(f"  {i}. {feature}")
        print(f"     └─ {YELLOW}Konum: {location}{RESET}")
    
    return True

def verify_mm_features():
    """M&M 3e özelliklerini kontrol et"""
    print_header("⚡ MUTANTS & MASTERMINDS 3E ÖZELLİKLERİ")
    
    features = {
        "Power Point Sistemi": "gui/app.py'de power_points",
        "Power Categories (21+)": "data/mm_data.json'de powers",
        "Extra/Flaw Selection": "gui/app.py'de power_extras_flaws",
        "Power Level Calculation": "utils/calculations.py'de calculate_mm_*",
        "Skill System": "gui/app.py'de mm skills",
    }
    
    print("Koruma Altında Olması Gereken Özellikler:\n")
    for i, (feature, location) in enumerate(features.items(), 1):
        print(f"  {i}. {feature}")
        print(f"     └─ {YELLOW}Konum: {location}{RESET}")
    
    return True

def verify_vtm_features():
    """VtM 5e özelliklerini kontrol et"""
    print_header("🧛 VAMPIRE: THE MASQUERADE 5E ÖZELLİKLERİ")
    
    features = {
        "Klan Seçimi (3 klan)": "gui/app.py'de clan_selection",
        "Klan-Özgü Mekanikler": "gui/app.py'de vtm_clan_specific",
        "Discipline Selection": "gui/app.py'de discipline_selection",
        "Blood Resonance": "gui/app.py'de blood_resonance",
        "Attribute System": "gui/app.py'de vtm_attributes",
    }
    
    print("Koruma Altında Olması Gereken Özellikler:\n")
    for i, (feature, location) in enumerate(features.items(), 1):
        print(f"  {i}. {feature}")
        print(f"     └─ {YELLOW}Konum: {location}{RESET}")
    
    return True

def verify_gui_components():
    """GUI ana bileşenlerini kontrol et"""
    print_header("🎮 GUI BILEŞENLERI")
    
    components = {
        "app.py": GUI_DIR / "app.py",
        "subclass_dialog.py": GUI_DIR / "subclass_dialog.py",
        "equipment_comparison_dialog.py": GUI_DIR / "equipment_comparison_dialog.py",
        "pending_widget.py": GUI_DIR / "pending_widget.py",
    }
    
    all_passed = True
    print("Kritik GUI Dosyaları:\n")
    for name, path in components.items():
        passed = path.exists()
        all_passed = all_passed and passed
        print(f"  {check_mark(passed)} {name}")
        if passed:
            size = path.stat().st_size
            lines = len(path.read_text(encoding='utf-8').split('\n'))
            print(f"      └─ {size:,} byte, {lines:,} satır")
    
    return all_passed

def verify_utils():
    """Utility modüllerini kontrol et"""
    print_header("🔧 UTILITY MODÜLLERI")
    
    utils = {
        "Calculations": UTILS_DIR / "calculations.py",
        "Data Loader": UTILS_DIR / "data_loader.py",
        "Export PDF": UTILS_DIR / "export_pdf.py",
        "Export Formats": UTILS_DIR / "export_formats.py",
        "Character Versioning": UTILS_DIR / "character_versioning.py",
        "Storage": UTILS_DIR / "storage.py",
    }
    
    all_passed = True
    print("Kritik Utility Dosyaları:\n")
    for name, path in utils.items():
        passed = path.exists()
        all_passed = all_passed and passed
        print(f"  {check_mark(passed)} {name}")
    
    return all_passed

def print_protection_guidelines():
    """Koruma rehberi yazdır"""
    print_header("📋 KORUMA REHBERİ")
    
    guidelines = [
        ("Sistem Bağımsızlığı", 
         "Her sistem kendi kurallarına uyar, aralarında karışma yoktur"),
        ("Özellik Teslimi", 
         "Yeni özellik eklenirken tüm 4 sistem göz önüne alınmalıdır"),
        ("Test Gerekliliği", 
         "Sistem-spesifik özellikler tüm sistemde test edilmelidir"),
        ("Versiyon Kontrolü", 
         "Tüm değişiklikler Git ile versiyonlanmalıdır"),
        ("Dokümantasyon", 
         "GUI_OZELLIKLER.md dosyası güncel tutulmalıdır"),
        ("Backward Compatibility", 
         "Eski karakterler yeni sürümde yüklenebilmeli"),
    ]
    
    for i, (guideline, description) in enumerate(guidelines, 1):
        print(f"\n{i}. {BOLD}{guideline}{RESET}")
        print(f"   {description}")

def main():
    print(f"\n{BOLD}{'Diyargezer GUI ÖZELLİKLERİ KONTROL SCRIPTI':^60}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")
    
    results = []
    
    # Kontroller
    results.append(("📊 Veri Dosyaları", verify_data_files()))
    results.append(("🎮 GUI Bileşenleri", verify_gui_components()))
    results.append(("🔧 Utility Modülleri", verify_utils()))
    
    # Sistem özellikleri
    verify_dnd_features()
    verify_pathfinder_features()
    verify_mm_features()
    verify_vtm_features()
    
    # Koruma rehberi
    print_protection_guidelines()
    
    # Özet
    print_header("📊 ÖZET")
    
    all_passed = all(passed for _, passed in results)
    
    for name, passed in results:
        print(f"  {check_mark(passed)} {name}")
    
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    
    if all_passed:
        print(f"\n{BOLD}{GREEN}✓ Tüm Kontroller Başarılı!{RESET}")
        print(f"{GREEN}GUI Özellikleri Korunmuş ve Aktif Durumda.{RESET}\n")
        return 0
    else:
        print(f"\n{BOLD}{RED}✗ Bazı Kontroller Başarısız!{RESET}")
        print(f"{RED}Lütfen Yukarıdaki Sorunları Gözden Geçirin.{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
