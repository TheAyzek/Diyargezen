#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pathfinder 1e verilerini her iki siteden çekip birleştir
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from utils.pathfinder_scraper import PathfinderScraper, _merge_category_data
import json


def merge_pathfinder_data_from_both_sites(force_refresh: bool = False):
    """
    Her iki siteden veri çek ve birleştir.
    Mevcut veri varsa onu kullanır, sadece eksikleri çeker.
    
    Args:
        force_refresh: True ise mevcut veriyi görmezden gelip yeniden çeker
    """
    print("=" * 70)
    print("PATHFINDER 1E VERİ BİRLEŞTİRME")
    print("=" * 70)
    print()
    
    output_file = project_root / "data" / "pathfinder_1e_data.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Önce mevcut veriyi yükle (eğer varsa)
    existing_data = {}
    if output_file.exists() and not force_refresh:
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            races_count = len(existing_data.get('races', {}))
            classes_count = len(existing_data.get('classes', {}))
            
            if races_count > 0 or classes_count > 0:
                print(f"📂 Mevcut veri bulundu: {races_count} ırk, {classes_count} sınıf")
                print("   ✅ Mevcut veri kullanılacak.")
                print("   💡 Yeniden çekmek için: python scripts/merge_pathfinder_data.py --force")
                
                # Mevcut veriyi döndür
                return output_file
            else:
                print("⚠️  Mevcut dosya boş, veriler yeniden çekilecek...")
        except Exception as e:
            print(f"⚠️  Mevcut veri yüklenemedi: {e}")
            print("   Veriler yeniden çekilecek...")
    
    # Eğer force_refresh veya veri yoksa, çek
    if force_refresh:
        print("🔄 Force refresh aktif - tüm veriler yeniden çekilecek...")
    
    # 1. Archives of Nethys'ten çek
    print("\n" + "=" * 70)
    print("📚 1. Archives of Nethys (aonprd.com)")
    print("=" * 70)
    scraper_aon = PathfinderScraper(site="aonprd", delay=1.0)
    
    print("\n🏃 Irklar çekiliyor (aonprd)...")
    races_aon = scraper_aon.scrape_races()
    print(f"✅ {len(races_aon)} ırk çekildi")
    
    print("\n⚔️ Sınıflar çekiliyor (aonprd)...")
    classes_aon = scraper_aon.scrape_classes()
    print(f"✅ {len(classes_aon)} sınıf çekildi")
    
    # 2. d20pfsrd.com'dan çek
    print("\n" + "=" * 70)
    print("📚 2. d20pfsrd.com")
    print("=" * 70)
    scraper_d20 = PathfinderScraper(site="d20pfsrd", delay=1.0)
    
    print("\n🏃 Irklar çekiliyor (d20pfsrd)...")
    races_d20 = scraper_d20.scrape_races()
    print(f"✅ {len(races_d20)} ırk çekildi")
    
    print("\n⚔️ Sınıflar çekiliyor (d20pfsrd)...")
    classes_d20 = scraper_d20.scrape_classes()
    print(f"✅ {len(classes_d20)} sınıf çekildi")
    
    # 3. Verileri birleştir
    print("\n" + "=" * 70)
    print("🔗 Veriler birleştiriliyor...")
    print("=" * 70)
    
    # Irkları birleştir (aonprd öncelikli)
    print("\n🏃 Irklar birleştiriliyor...")
    merged_races = _merge_category_data(races_aon, races_d20)
    
    # Sınıfları birleştir (aonprd öncelikli)
    print("⚔️ Sınıflar birleştiriliyor...")
    merged_classes = _merge_category_data(classes_aon, classes_d20)
    
    # Mevcut veriyi de birleştir (eğer varsa ve force_refresh değilse)
    if existing_data and not force_refresh:
        print("📂 Mevcut veri ile birleştiriliyor...")
        merged_races = _merge_category_data(merged_races, existing_data.get('races', {}))
        merged_classes = _merge_category_data(merged_classes, existing_data.get('classes', {}))
    
    # 4. İstatistikler
    print("\n" + "=" * 70)
    print("📊 BİRLEŞTİRME İSTATİSTİKLERİ")
    print("=" * 70)
    print("\n🏃 Irklar:")
    print(f"  - Archives of Nethys: {len(races_aon)}")
    print(f"  - d20pfsrd.com: {len(races_d20)}")
    print(f"  - Birleştirilmiş: {len(merged_races)}")
    
    # Ortak ırkları bul
    common_races = set(races_aon.keys()) & set(races_d20.keys())
    print(f"  - Ortak ırklar: {len(common_races)}")
    if common_races:
        print(f"    Örnekler: {', '.join(list(common_races)[:5])}")
    
    print("\n⚔️ Sınıflar:")
    print(f"  - Archives of Nethys: {len(classes_aon)}")
    print(f"  - d20pfsrd.com: {len(classes_d20)}")
    print(f"  - Birleştirilmiş: {len(merged_classes)}")
    
    # Ortak sınıfları bul
    common_classes = set(classes_aon.keys()) & set(classes_d20.keys())
    print(f"  - Ortak sınıflar: {len(common_classes)}")
    if common_classes:
        print(f"    Örnekler: {', '.join(list(common_classes)[:5])}")
    
    # 5. Veriyi kaydet
    merged_data = {
        "system": "PATHFINDER_1E",
        "source": "merged (aonprd + d20pfsrd)",
        "races": merged_races,
        "classes": merged_classes,
        "feats": existing_data.get('feats', {}),  # Feat'ler şimdilik mevcut veriden
        "spells": existing_data.get('spells', {}),  # Büyüler şimdilik mevcut veriden
        "items": existing_data.get('items', {})  # Ekipman şimdilik mevcut veriden
    }
    
    print("\n" + "=" * 70)
    print("💾 Veriler kaydediliyor...")
    print("=" * 70)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Birleştirilmiş veriler kaydedildi: {output_file}")
    print(f"   - Toplam ırk: {len(merged_races)}")
    print(f"   - Toplam sınıf: {len(merged_classes)}")
    
    return output_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Pathfinder 1e verilerini çek ve birleştir")
    parser.add_argument("--force", action="store_true", 
                       help="Mevcut veriyi görmezden gelip yeniden çek")
    
    args = parser.parse_args()
    
    try:
        merge_pathfinder_data_from_both_sites(force_refresh=args.force)
    except KeyboardInterrupt:
        print("\n\n⚠️  İşlem kullanıcı tarafından iptal edildi.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

