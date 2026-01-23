#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pathfinder 1e - Part 1: Archives of Nethys'ten feat ve spell'leri çek
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
    print("Pathfinder 1e - Part 1: Archives of Nethys")
    print("=" * 60)
    print("Sadece feat'ler ve büyüler çekiliyor...\n")
    
    # Mevcut veriyi yükle (varsa)
    data_file = project_root / "data" / "pathfinder_1e_data.json"
    existing_data = {}
    if data_file.exists():
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"[OK] Mevcut veri yüklendi: {len(existing_data.get('races', {}))} ırk, {len(existing_data.get('classes', {}))} sınıf")
        except Exception as e:
            print(f"[UYARI] Mevcut veri yüklenemedi: {e}")
    
    # Archives of Nethys'ten sadece feat ve spell çek
    scraper_aon = PathfinderScraper(site="aonprd", delay=1.5)  # Biraz daha yavaş, siteyi yormamak için
    
    print("\n[1/2] Feat'ler çekiliyor...")
    feats_aon = scraper_aon.scrape_feats()
    
    print("\n[2/2] Büyüler çekiliyor...")
    spells_aon = scraper_aon.scrape_spells(max_spells=1000)  # Daha fazla büyü çek
    
    # Mevcut veriyle birleştir
    print("\n[3/3] Veriler birleştiriliyor...")
    merged_data = {
        "system": "PATHFINDER_1E",
        "source": "merged (aonprd + d20pfsrd)",
        "races": existing_data.get("races", {}),
        "classes": existing_data.get("classes", {}),
        "feats": _merge_category_data(existing_data.get("feats", {}), feats_aon),
        "spells": _merge_category_data(existing_data.get("spells", {}), spells_aon),
        "items": existing_data.get("items", {})
    }
    
    # Kaydet
    data_file.parent.mkdir(parents=True, exist_ok=True)
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("Part 1 Tamamlandı!")
    print("=" * 60)
    print(f"Feat'ler: {len(merged_data['feats'])} (yeni eklenen: {len(feats_aon)})")
    print(f"Büyüler: {len(merged_data['spells'])} (yeni eklenen: {len(spells_aon)})")
    print(f"\nVeriler kaydedildi: {data_file}")


