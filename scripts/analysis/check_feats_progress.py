#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feats scraping ilerlemesini kontrol et"""

import sys
import codecs
from pathlib import Path
import json

# UTF-8 encoding fix for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

project_root = Path(__file__).parent.parent

def main():
    """İlerlemeyi kontrol et"""
    print("=" * 70)
    print("FEATS SCRAPING İLERLEME KONTROLÜ")
    print("=" * 70)
    
    # Cache dosyasını kontrol et
    cache_file = project_root / "data/cache/feats_cache.json"
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        total_feats = cache_data.get('total', 0)
        progress = cache_data.get('progress', 'N/A')
        scraped_at = cache_data.get('scraped_at', 'N/A')
        
        print("\n📦 Cache Durumu:")
        print(f"  ✅ Çekilen feat sayısı: {total_feats}")
        print(f"  📊 İlerleme: {progress}")
        print(f"  ⏰ Son güncelleme: {scraped_at}")
        
        # dnd_data.json'u kontrol et
        data_file = project_root / "data" / "dnd_data.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                dnd_data = json.load(f)
            
            feats_in_data = len(dnd_data.get('feats', {}))
            print("\n📋 dnd_data.json Durumu:")
            print(f"  ✅ Toplam feat: {feats_in_data}")
    else:
        print("\n⚠️  Cache dosyası henüz oluşturulmadı.")
    
    # Log dosyasını kontrol et
    log_file = project_root / "data/logs/feats_scraping_log.txt"
    if log_file.exists():
        print(f"\n📝 Log Dosyası: {log_file}")
        print("  Son 10 satır:")
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-10:]:
                print(f"    {line.rstrip()}")
    else:
        print("\n⚠️  Log dosyası henüz oluşturulmadı.")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()


