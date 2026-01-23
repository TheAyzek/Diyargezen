#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mutants & Masterminds için tam veri çekme scripti
d20herosrd.com sitesinden tüm kuralları ve karakter oluşturma bilgilerini çeker
"""

import sys
import io
from pathlib import Path
import json

# Windows konsol encoding hatası için
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from utils.mm_scraper import MMScraper


def scrape_mm_complete(force_refresh: bool = False):
    """
    Tüm M&M verilerini çek ve kaydet
    
    Args:
        force_refresh: True ise mevcut veriyi görmezden gelip yeniden çeker
    """
    print("=" * 70)
    print("MUTANTS & MASTERMINDS VERİ ÇEKME")
    print("=" * 70)
    print()
    
    data_file = project_root / "data" / "mm_data.json"
    
    # Mevcut veriyi yükle
    existing_data = {}
    if data_file.exists() and not force_refresh:
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print("📂 Mevcut veri bulundu:")
            print(f"   - Archetypes: {len(existing_data.get('archetypes', {}))}")
            print(f"   - Abilities: {len(existing_data.get('abilities', {}))}")
            print(f"   - Skills: {len(existing_data.get('skills', {}))}")
            print(f"   - Advantages: {len(existing_data.get('advantages', {}))}")
            print(f"   - Powers: {len(existing_data.get('powers', {}))}")
            print("   ✅ Mevcut veri kullanılacak.")
            print("   💡 Yeniden çekmek için: python scripts/scrape_mm_complete.py --force")
            return data_file
        except Exception as e:
            print(f"⚠️  Mevcut veri yüklenemedi: {e}")
            print("   Veriler yeniden çekilecek...")
    
    if force_refresh:
        print("🔄 Force refresh aktif - tüm veriler yeniden çekilecek...")
    
    # Scraper'ı başlat
    scraper = MMScraper(delay=1.0)
    
    # Tüm verileri çek
    print("\n🚀 Veriler çekiliyor...")
    print("⚠️  Bu işlem birkaç dakika sürebilir. Lütfen bekleyin...\n")
    
    new_data = scraper.scrape_all(output_file=None)
    
    # Mevcut veri ile birleştir (eğer varsa ve force_refresh değilse)
    if existing_data and not force_refresh:
        print("\n📂 Mevcut veri ile birleştiriliyor...")
        # Her kategori için merge yap
        for category in ['archetypes', 'abilities', 'skills', 'advantages', 'powers', 'power_effects']:
            existing = existing_data.get(category, {})
            new = new_data.get(category, {})
            # Yeni verileri ekle, mevcut olanları koru
            merged = {**existing, **new}
            new_data[category] = merged
    
    # Power levels'i koru (eğer mevcut veri varsa)
    if existing_data.get('power_levels'):
        new_data['power_levels'] = existing_data['power_levels']
    
    # Kaydet
    print("\n" + "=" * 70)
    print("💾 Veriler kaydediliyor...")
    print("=" * 70)
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    
    # İstatistikler
    print(f"\n✅ Veriler kaydedildi: {data_file}")
    print("\n📊 İstatistikler:")
    print(f"   - Archetypes: {len(new_data.get('archetypes', {}))}")
    print(f"   - Abilities: {len(new_data.get('abilities', {}))}")
    print(f"   - Skills: {len(new_data.get('skills', {}))}")
    print(f"   - Advantages: {len(new_data.get('advantages', {}))}")
    print(f"   - Powers: {len(new_data.get('powers', {}))}")
    print(f"   - Power Effects: {len(new_data.get('power_effects', {}))}")
    
    return data_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Mutants & Masterminds verilerini çek")
    parser.add_argument("--force", action="store_true", 
                       help="Mevcut veriyi görmezden gelip yeniden çek")
    
    args = parser.parse_args()
    
    try:
        scrape_mm_complete(force_refresh=args.force)
    except KeyboardInterrupt:
        print("\n\n⚠️  İşlem kullanıcı tarafından iptal edildi.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

