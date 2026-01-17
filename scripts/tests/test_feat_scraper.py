#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feat scraper test scripti"""

import sys
import codecs
from pathlib import Path

# UTF-8 encoding fix for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Proje root dizinine ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

def main():
    """Test feat scraper"""
    print("=" * 70)
    print("FEAT SCRAPER TEST")
    print("=" * 70)
    
    scraper = Dnd5eSrdScraper(rate_limit=1.5)
    
    # İlk 5 feat'i test et
    print("\n🔍 İlk 5 feat'i test ediyoruz...")
    feats = scraper.scrape_all_feats(max_feats=5, force_refresh=False)
    
    print(f"\n✅ {len(feats)} feat çekildi")
    print("\n📋 Çekilen Feat'ler:")
    for i, (name, data) in enumerate(feats.items(), 1):
        print(f"\n{i}. {name}")
        if data.get('prerequisite'):
            print(f"   Prerequisite: {data['prerequisite']}")
        if data.get('description'):
            desc = data['description'][:100] + "..." if len(data['description']) > 100 else data['description']
            print(f"   Description: {desc}")

if __name__ == "__main__":
    main()


