#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D&D 5e spell'lerini parça parça çek (batch mode)"""

import sys
from pathlib import Path
import json
import argparse

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

def main():
    parser = argparse.ArgumentParser(description='D&D 5e spell\'leri parça parça çek')
    parser.add_argument('--batch-size', type=int, default=100, help='Her batch\'te çekilecek spell sayısı (default: 100)')
    parser.add_argument('--start-from', type=int, default=0, help='Başlangıç indeksi (devam için)')
    parser.add_argument('--max-batches', type=int, help='Maksimum batch sayısı (None = tümü)')
    parser.add_argument('--force', action='store_true', help='Cache\'i yeniden oluştur')
    args = parser.parse_args()
    
    print("=" * 70)
    print("D&D 5E SPELL'LERİ PARÇA PARÇA ÇEKİLİYOR")
    print("=" * 70)
    print(f"Batch size: {args.batch_size}")
    print(f"Start from: {args.start_from}")
    if args.max_batches:
        print(f"Max batches: {args.max_batches}")
    print()
    
    # Scraper oluştur
    scraper = Dnd5eSrdScraper(rate_limit=1.5)
    
    # Cache dosyasını yükle
    cache_file = Path("data/cache/spells_cache.json")
    cached_spells = {}
    
    if not args.force and cache_file.exists():
        print(f"📦 Cache dosyası yükleniyor: {cache_file}")
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached_data = json.load(f)
            if cached_data.get('spells'):
                cached_spells = cached_data['spells']
                print(f"  ✅ {len(cached_spells)} spell cache'den yüklendi")
    
    # Spell linklerini çek
    print("\n🔍 Spell linkleri çekiliyor...")
    spell_links = scraper.scrape_all_spell_links()
    print(f"  ✅ {len(spell_links)} unique spell linki bulundu")
    
    # Cache'de olmayan spell'leri filtrele
    cached_names = set(cached_spells.keys())
    spell_links = [(name, url) for name, url in spell_links if name not in cached_names]
    
    if not spell_links:
        print("\n✅ Tüm spell'ler zaten cache'de!")
        return
    
    print(f"  🔄 {len(spell_links)} yeni spell çekilecek")
    
    # Başlangıç indeksinden başla
    spell_links = spell_links[args.start_from:]
    total_spells = len(spell_links)
    
    if total_spells == 0:
        print("\n✅ Belirtilen indeksten sonra çekilecek spell yok!")
        return
    
    # Batch'ler halinde çek
    all_spells = cached_spells.copy()
    batch_num = 0
    total_batches = (total_spells + args.batch_size - 1) // args.batch_size
    
    if args.max_batches:
        total_batches = min(total_batches, args.max_batches)
    
    print(f"\n📖 {total_batches} batch çekilecek")
    print(f"  Her batch: {args.batch_size} spell")
    print()
    
    for i in range(0, total_spells, args.batch_size):
        if args.max_batches and batch_num >= args.max_batches:
            break
        
        batch_num += 1
        batch_spells = spell_links[i:i + args.batch_size]
        batch_size = len(batch_spells)
        
        print(f"📦 Batch {batch_num}/{total_batches} ({batch_size} spell)...")
        print(f"  İndeks: {args.start_from + i} - {args.start_from + i + batch_size - 1}")
        
        batch_results = {}
        success_count = 0
        
        for j, (name, url) in enumerate(batch_spells, 1):
            if j % 10 == 0:
                print(f"    ... {j}/{batch_size} spell çekildi ({success_count} başarılı)")
            
            spell_data = scraper.scrape_spell_detail(url, name)
            if spell_data and spell_data.get('name'):
                batch_results[spell_data['name']] = spell_data
                success_count += 1
        
        # Batch sonuçlarını birleştir
        all_spells.update(batch_results)
        
        # Her batch sonunda cache'e kaydet
        cache_data = {
            'total': len(all_spells),
            'spells': all_spells,
            'source': '5esrd.com',
            'scraped_at': Path(__file__).stat().st_mtime,
            'progress': f'{args.start_from + i + batch_size}/{args.start_from + total_spells}',
            'last_batch': batch_num,
            'total_batches': total_batches
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ Batch tamamlandı: {success_count}/{batch_size} başarılı")
        print(f"  💾 Cache güncellendi: {len(all_spells)} toplam spell")
        print()
    
    # Final - dnd_data.json'a ekle
    print("\n" + "=" * 70)
    print("SPELL'LER ÇEKİLDİ - ŞİMDİ DND_DATA.JSON'A EKLENİYOR")
    print("=" * 70)
    
    dnd_data_file = Path("data/dnd_data.json")
    with open(dnd_data_file, 'r', encoding='utf-8') as f:
        dnd_data = json.load(f)
    
    if 'spells' not in dnd_data:
        dnd_data['spells'] = {}
    
    # Yeni spell'leri ekle veya güncelle
    added_count = 0
    updated_count = 0
    
    for spell_name, spell_data in all_spells.items():
        if spell_name not in dnd_data['spells']:
            dnd_data['spells'][spell_name] = spell_data
            added_count += 1
        else:
            # Mevcut spell'i güncelle (5esrd.com verisi öncelikli)
            dnd_data['spells'][spell_name].update(spell_data)
            updated_count += 1
    
    print(f"\n✅ {added_count} yeni spell eklendi")
    print(f"🔄 {updated_count} spell güncellendi")
    print(f"📊 Toplam spell sayısı: {len(dnd_data['spells'])}")
    
    # Kaydet
    print(f"\n💾 {dnd_data_file} dosyasına kaydediliyor...")
    with open(dnd_data_file, 'w', encoding='utf-8') as f:
        json.dump(dnd_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Tamamlandı! {dnd_data_file} güncellendi.")
    
    # Özet
    print("\n" + "=" * 70)
    print("ÖZET")
    print("=" * 70)
    print(f"  Toplam çekilen: {len(all_spells)}")
    print(f"  Bu batch'te: {success_count}")
    print(f"  DND data'ya eklenen: {added_count + updated_count}")
    print(f"  Toplam spell (dnd_data.json): {len(dnd_data['spells'])}")
    print()
    
    # Sonraki batch için bilgi
    remaining = total_spells - (batch_num * args.batch_size)
    if remaining > 0:
        next_start = args.start_from + (batch_num * args.batch_size)
        print(f"📌 Sonraki batch için:")
        print(f"  python scripts/scrape_dnd_spells_batch.py --batch-size {args.batch_size} --start-from {next_start}")
        print()

if __name__ == "__main__":
    main()


