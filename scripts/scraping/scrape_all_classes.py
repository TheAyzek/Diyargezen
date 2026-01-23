#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tüm class'ları scrape et ve dnd_data.json'a entegre et"""

import sys
import io
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("5ESRD.COM CLASSES SCRAPING")
print("=" * 70)
print()

scraper = Dnd5eSrdScraper(rate_limit=2.0)  # 2 saniye delay

# Cache kontrolü
cache_file = project_root / "data" / "cache" / "classes_cache.json"
classes = {}
cached_classes = {}

if cache_file.exists():
    print(f"📦 Cache dosyası bulundu: {cache_file}")
    with open(cache_file, 'r', encoding='utf-8') as f:
        cached = json.load(f)
        if cached.get('classes'):
            cached_classes = cached['classes']
            classes.update(cached_classes)
            print(f"  ✅ {len(cached_classes)} class cache'den yüklendi")

# Class linklerini çek
print("\n🔍 Class linkleri çekiliyor...")
class_links = scraper.scrape_all_class_links()

if not class_links:
    print("  ⚠️  Class linkleri bulunamadı! Mevcut cache'i döndürüyoruz.")
    exit(1)

print(f"\n📖 {len(class_links)} class bulundu")
print("  Class'lar:", ", ".join([name for name, _ in class_links]))

# Cache'de olmayan class'ları filtrele
cached_names = set(cached_classes.keys())
new_class_links = [(name, url) for name, url in class_links if name not in cached_names]

if new_class_links:
    print(f"\n🔄 {len(new_class_links)} yeni class çekilecek ({len(cached_names)} zaten cache'de)")
else:
    print("\n✅ Tüm class'lar zaten cache'de!")
    exit(0)

total = len(new_class_links)
print(f"\n📖 {total} class detayı çekiliyor...")
print("  (Bu işlem uzun sürebilir, lütfen bekleyin...)\n")

log_file = project_root / "data" / "logs" / "classes_scraping_log.txt"
with open(log_file, 'a', encoding='utf-8') as log:
    log.write(f"\n{'=' * 70}\n")
    log.write(f"Classes Scraping Başlangıç: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log.write(f"{'=' * 70}\n")

for i, (name, url) in enumerate(new_class_links, 1):
    if i % 2 == 0:
        successful = len([k for k in classes.keys() if k not in cached_names])
        print(f"  ... {i}/{total} class çekildi ({successful} başarılı)")
        
        # Her 5 class'ta bir cache'e kaydet
        if i % 5 == 0:
            all_classes_temp = {**cached_classes, **classes}
            cache_data = {
                'total': len(all_classes_temp),
                'classes': all_classes_temp,
                'source': '5esrd.com',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'progress': f'{i}/{total}'
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"  💾 İlerleme kaydedildi: {successful} yeni class, toplam {len(all_classes_temp)}")
    
    class_data = scraper.scrape_class_detail(url, name)
    if class_data and class_data.get('name'):
        classes[class_data['name']] = class_data
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"✅ {name}: {url}\n")
    else:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"❌ {name}: {url} - Scrape edilemedi\n")

print(f"\n✅ {len([k for k in classes.keys() if k not in cached_names])} yeni class başarıyla çekildi")
print(f"   Toplam: {len(classes)} class (cache dahil)")

# Final cache'e kaydet
all_classes = {**cached_classes, **classes}
cache_data = {
    'total': len(all_classes),
    'classes': all_classes,
    'source': '5esrd.com',
    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
}
with open(cache_file, 'w', encoding='utf-8') as f:
    json.dump(cache_data, f, ensure_ascii=False, indent=2)
print(f"💾 Cache'e kaydedildi: {cache_file}")

# dnd_data.json'a entegre et
print("\n📦 dnd_data.json'a entegre ediliyor...")
data_file = project_root / "data" / "dnd_data.json"
if data_file.exists():
    with open(data_file, 'r', encoding='utf-8') as f:
        dnd_data = json.load(f)
    
    existing_classes = dnd_data.get("classes", {})
    new_count = 0
    
    for class_name, class_data in all_classes.items():
        if class_name not in existing_classes:
            dnd_data.setdefault("classes", {})[class_name] = class_data
            new_count += 1
        else:
            # Mevcut class'ı güncelle (scraped data ile merge)
            existing = existing_classes[class_name]
            # Scraped data'yı mevcut data ile birleştir (scraped data öncelikli)
            for key, value in class_data.items():
                if value:  # Sadece boş olmayan değerleri güncelle
                    existing[key] = value
            dnd_data["classes"][class_name] = existing
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(dnd_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {new_count} yeni class eklendi, toplam {len(dnd_data.get('classes', {}))} class dnd_data.json'da!")
    
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"\n✅ Toplam {len(all_classes)} class çekildi!\n")
        log.write(f"Bitiş: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"\n{'=' * 70}\n")
        log.write("✅ CLASSES SCRAPING TAMAMLANDI\n")
        log.write(f"{'=' * 70}\n")

print("\n" + "=" * 70)
print("✅ CLASSES SCRAPING TAMAMLANDI")
print("=" * 70)




