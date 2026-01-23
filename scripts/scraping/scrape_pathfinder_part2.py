#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pathfinder 1e - Part 2: d20pfsrd'den spell'leri çek ve tamamla
"""

import sys
from pathlib import Path

# UTF-8 encoding zorla
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Proje kök dizinini path'e ekle
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from utils.pathfinder_scraper import PathfinderScraper, _merge_category_data
import json

if __name__ == "__main__":
    print("=" * 60)
    print("Pathfinder 1e - Part 2: d20pfsrd")
    print("=" * 60)
    print("d20pfsrd'den spell'leri çekiliyor...\n")
    
    # Mevcut veriyi yükle
    data_file = project_root / "data" / "pathfinder_1e_data.json"
    if not data_file.exists():
        print("[HATA] Part 1 önce çalıştırılmalı!")
        sys.exit(1)
    
    with open(data_file, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    print("[OK] Mevcut veri yüklendi:")
    print(f"  - {len(existing_data.get('races', {}))} ırk")
    print(f"  - {len(existing_data.get('classes', {}))} sınıf")
    print(f"  - {len(existing_data.get('feats', {}))} feat")
    print(f"  - {len(existing_data.get('spells', {}))} büyü")
    
    # d20pfsrd'den spell çek
    scraper_d20 = PathfinderScraper(site="d20pfsrd", delay=1.5)
    
    print("\n[1/1] Büyüler çekiliyor...")
    spells_d20 = scraper_d20.scrape_spells(max_spells=1000)
    
    # Birleştir
    print("\n[2/2] Veriler birleştiriliyor...")
    merged_data = {
        "system": "PATHFINDER_1E",
        "source": "merged (aonprd + d20pfsrd)",
        "races": existing_data.get("races", {}),
        "classes": existing_data.get("classes", {}),
        "feats": existing_data.get("feats", {}),
        "spells": _merge_category_data(existing_data.get("spells", {}), spells_d20),
        "items": existing_data.get("items", {})
    }
    
    # Kaydet
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("Part 2 Tamamlandı!")
    print("=" * 60)
    print(f"Toplam Büyüler: {len(merged_data['spells'])} (yeni eklenen: {len(spells_d20)})")
    print(f"\nVeriler kaydedildi: {data_file}")
    
    print("\n" + "=" * 60)
    print("FINAL İSTATİSTİKLER")
    print("=" * 60)
    print(f"Irklar: {len(merged_data['races'])}")
    print(f"Sınıflar: {len(merged_data['classes'])}")
    print(f"Feat'ler: {len(merged_data['feats'])}")
    print(f"Büyüler: {len(merged_data['spells'])}")
    print("=" * 60)


