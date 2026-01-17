#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tüm D&D 5e feat'lerini çek"""

import sys
import codecs
from pathlib import Path

# UTF-8 encoding fix for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Proje root dizinine ekle
project_root = Path(__file__).parent.parent.parent  # scripts/scraping -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper
import json

def main():
    """Tüm feat'leri çek"""
    import argparse
    
    parser = argparse.ArgumentParser(description='D&D 5e Feats Scraper')
    parser.add_argument('--max', type=int, help='Maximum number of feats to scrape (for testing)')
    parser.add_argument('--force', action='store_true', help='Force refresh (ignore cache)')
    args = parser.parse_args()
    
    print("=" * 70)
    print("TÜM D&D 5E FEATS ÇEKİLİYOR")
    print("=" * 70)
    
    scraper = Dnd5eSrdScraper(rate_limit=1.5)
    
    # Tüm feat'leri çek
    print("\n🔍 Feat'ler çekiliyor...")
    if args.max:
        print(f"  ⚠️  Test modu: İlk {args.max} feat çekilecek")
        feats = scraper.scrape_all_feats(max_feats=args.max, force_refresh=args.force)
    else:
        feats = scraper.scrape_all_feats(force_refresh=args.force)
    
    print(f"\n✅ Toplam {len(feats)} feat çekildi!")
    
    # dnd_data.json'a entegre et
    data_file = project_root / "data" / "dnd_data.json"
    if data_file.exists():
        print(f"\n📦 dnd_data.json'a entegre ediliyor...")
        with open(data_file, 'r', encoding='utf-8') as f:
            dnd_data = json.load(f)
        
        # Feat'leri ekle (mevcut feat'lerle birleştir)
        if 'feats' not in dnd_data:
            dnd_data['feats'] = {}
        
        # Yeni feat'leri ekle, mevcut olanları güncelle
        existing_count = len(dnd_data['feats'])
        dnd_data['feats'].update(feats)
        new_count = len(dnd_data['feats'])
        
        # Kaydet
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(dnd_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {new_count - existing_count} yeni feat eklendi, toplam {new_count} feat dnd_data.json'da!")
    else:
        print(f"⚠️  dnd_data.json bulunamadı: {data_file}")
    
    print("\n" + "=" * 70)
    print("✅ FEATS SCRAPING TAMAMLANDI")
    print("=" * 70)

if __name__ == "__main__":
    main()

