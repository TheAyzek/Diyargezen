#!/usr/bin/env python3
"""
Pathfinder 1e verilerini web'den çekmek için script
Kullanım: python scripts/scrape_pathfinder.py [aonprd|d20pfsrd]
"""

import sys
from pathlib import Path

# Proje kök dizinini path'e ekle
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from utils.pathfinder_scraper import scrape_pathfinder_data

if __name__ == "__main__":
    site = sys.argv[1] if len(sys.argv) > 1 else "both"
    
    if site not in ["aonprd", "d20pfsrd", "both"]:
        print("❌ Hata: Geçersiz site. 'aonprd', 'd20pfsrd' veya 'both' kullanın.")
        print("   'both' seçeneği her iki siteden de veri çekip birleştirir.")
        sys.exit(1)
    
    if site == "both":
        print("🚀 Pathfinder 1e verileri çekiliyor: Her iki siteden (birleştirilmiş)")
        print("⚠️  Bu işlem 10-15 dakika sürebilir...\n")
    else:
        print(f"🚀 Pathfinder 1e verileri çekiliyor: {site}")
        print("⚠️  Bu işlem birkaç dakika sürebilir...\n")
    
    try:
        merge_sites = (site == "both")
        output_file = scrape_pathfinder_data(site=site, merge_sites=merge_sites)
        print(f"\n✅ Başarılı! Veriler kaydedildi: {output_file}")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

