#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch scraping ilerlemesini kontrol et"""

import sys
from pathlib import Path
import json

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 70)
print("BATCH SCRAPING İLERLEME KONTROLÜ")
print("=" * 70)
print()

# Cache dosyasını kontrol et
cache_file = Path("data/cache/spells_cache.json")
if cache_file.exists():
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    spells_in_cache = cache_data.get('spells', {})
    total_in_cache = len(spells_in_cache)
    progress = cache_data.get('progress', 'Bilinmiyor')
    
    print(f"📦 Cache'deki spell sayısı: {total_in_cache}")
    print(f"📊 İlerleme: {progress}")
    print()
    
    # Scraper ile toplam spell sayısını kontrol et
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from utils.dnd_5esrd_scraper import Dnd5eSrdScraper
        scraper = Dnd5eSrdScraper(rate_limit=0.5)  # Hızlı kontrol için
        spell_links = scraper.scrape_all_spell_links()
        total_spells = len(spell_links)
        
        remaining = total_spells - total_in_cache
        percentage = (total_in_cache / total_spells * 100) if total_spells > 0 else 0
        
        print(f"📊 Toplam spell (sitede): {total_spells}")
        print(f"✅ Çekilen: {total_in_cache} ({percentage:.1f}%)")
        print(f"⏳ Kalan: {remaining}")
        
        if remaining > 0:
            batch_size = 50
            remaining_batches = (remaining + batch_size - 1) // batch_size
            print(f"📦 Tahmini kalan batch: {remaining_batches}")
            next_start = total_in_cache - (total_in_cache % batch_size)
            print(f"📌 Sonraki komut: python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from {next_start}")
        else:
            print("\n🎉 TÜM SPELL'LER ÇEKİLDİ!")
    except Exception as e:
        print(f"⚠️ Toplam kontrolü yapılamadı: {e}")
else:
    print("❌ Cache dosyası bulunamadı")

print()
print("=" * 70)

# dnd_data.json kontrolü
dnd_file = Path("data/dnd_data.json")
if dnd_file.exists():
    with open(dnd_file, 'r', encoding='utf-8') as f:
        dnd_data = json.load(f)
    spells_in_dnd = dnd_data.get('spells', {})
    print(f"📚 dnd_data.json'daki spell sayısı: {len(spells_in_dnd)}")
    print()


