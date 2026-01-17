#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pathfinder 1e büyülerini çek ve mevcut veriye ekle
"""

import sys
from pathlib import Path
import json

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from utils.pathfinder_scraper import PathfinderScraper, _merge_category_data


def scrape_and_merge_spells(force_refresh: bool = False, max_spells: int = 2000):
    """
    Büyüleri çek ve mevcut veriye ekle
    
    Args:
        force_refresh: True ise mevcut büyüleri görmezden gelip yeniden çeker
        max_spells: Maksimum çekilecek büyü sayısı
    """
    print("=" * 70)
    print("PATHFINDER 1E BÜYÜ ÇEKME")
    print("=" * 70)
    print()
    
    data_file = project_root / "data" / "pathfinder_1e_data.json"
    
    # Mevcut veriyi yükle
    existing_data = {}
    if data_file.exists():
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            existing_spells_count = len(existing_data.get('spells', {}))
            print(f"Mevcut veri yuklendi: {existing_spells_count} buyu mevcut")
            
            if existing_spells_count > 0 and not force_refresh:
                print("   OK: Mevcut buyuler kullanilacak.")
                print("   Not: Yeniden cekmek icin: python scripts/scrape_pathfinder_spells.py --force")
                return data_file
        except Exception as e:
            print(f"WARNING: Mevcut veri yuklenemedi: {e}")
    
    # 1. Archives of Nethys'ten çek
    print("\n" + "=" * 70)
    print("1. Archives of Nethys (aonprd.com)")
    print("=" * 70)
    scraper_aon = PathfinderScraper(site="aonprd", delay=1.0)
    
    print(f"\nBuyuler cekiliyor (aonprd, max {max_spells})...")
    spells_aon = scraper_aon.scrape_spells(max_spells=max_spells)
    print(f"OK: {len(spells_aon)} buyu cekildi (aonprd)")
    
    # 2. d20pfsrd.com'dan çek
    print("\n" + "=" * 70)
    print("2. d20pfsrd.com")
    print("=" * 70)
    scraper_d20 = PathfinderScraper(site="d20pfsrd", delay=1.0)
    
    print(f"\nBuyuler cekiliyor (d20pfsrd, max {max_spells})...")
    spells_d20 = scraper_d20.scrape_spells(max_spells=max_spells)
    print(f"OK: {len(spells_d20)} buyu cekildi (d20pfsrd)")
    
    # 3. Verileri birleştir
    print("\n" + "=" * 70)
    print("Buyuler birlestiriliyor...")
    print("=" * 70)
    
    merged_spells = _merge_category_data(spells_aon, spells_d20)
    
    # Mevcut büyüleri de birleştir (eğer varsa)
    if existing_data.get('spells', {}):
        print("Mevcut buyuler ile birlestiriliyor...")
        merged_spells = _merge_category_data(merged_spells, existing_data.get('spells', {}))
    
    # 4. İstatistikler
    print("\n" + "=" * 70)
    print("BIRLESTIRME ISTATISTIKLERI")
    print("=" * 70)
    print(f"\nBuyuler:")
    print(f"  - Archives of Nethys: {len(spells_aon)}")
    print(f"  - d20pfsrd.com: {len(spells_d20)}")
    print(f"  - Birlestirilmis: {len(merged_spells)}")
    
    # Ortak büyüleri bul
    common_spells = set(spells_aon.keys()) & set(spells_d20.keys())
    print(f"  - Ortak buyuler: {len(common_spells)}")
    if common_spells:
        print(f"    Ornekler: {', '.join(list(common_spells)[:5])}")
    
    # 5. Veriyi kaydet
    if not existing_data:
        existing_data = {
            "system": "PATHFINDER_1E",
            "races": {},
            "classes": {},
            "feats": {},
            "spells": {},
            "items": {}
        }
    
    existing_data["spells"] = merged_spells
    existing_data["source"] = existing_data.get("source", "merged (aonprd + d20pfsrd)")
    
    print("\n" + "=" * 70)
    print("Veriler kaydediliyor...")
    print("=" * 70)
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nOK: Buyuler kaydedildi: {data_file}")
    print(f"   - Toplam buyu: {len(merged_spells)}")
    
    return data_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Pathfinder 1e büyülerini çek")
    parser.add_argument("--force", action="store_true", 
                       help="Mevcut büyüleri görmezden gelip yeniden çek")
    parser.add_argument("--max", type=int, default=2000,
                       help="Maksimum çekilecek büyü sayısı (default: 2000)")
    
    args = parser.parse_args()
    
    try:
        scrape_and_merge_spells(force_refresh=args.force, max_spells=args.max)
    except KeyboardInterrupt:
        print("\n\nWARNING: Islem kullanici tarafindan iptal edildi.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


