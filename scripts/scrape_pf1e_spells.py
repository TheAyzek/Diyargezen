#!/usr/bin/env python3
"""
Pathfinder 1e Spell Scraping & Temizleme Script'i

Kullanim:
  # Sadece mevcut veriyi temizle ve core spell'leri ekle:
  python scripts/scrape_pf1e_spells.py --clean-only

  # AONPRD'den yeni spell'ler cek (batch):
  python scripts/scrape_pf1e_spells.py --scrape --batch-size 50 --max-batches 2

  # Her ikisini yap:
  python scripts/scrape_pf1e_spells.py --clean-only --scrape --batch-size 50
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

DATA_FILE = BASE_DIR / "data" / "pathfinder_1e_data.json"


def clean_existing_data():
    """Mevcut veriyi temizle ve core spell'leri ekle"""
    from utils.pathfinder_scraper import clean_existing_pathfinder_spells, ensure_core_spells_exist

    print("=" * 60)
    print("PATHFINDER 1e SPELL VERI TEMIZLEME")
    print("=" * 60)

    # Mevcut spell sayisi
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    before_count = len(data.get("spells", {}))
    print(f"\nMevcut spell sayisi: {before_count}")

    # Temizle
    print("\n1. Bozuk verileri temizleniyor...")
    cleaned = clean_existing_pathfinder_spells(DATA_FILE)
    print(f"   Temizlenen: {cleaned} spell")

    # Core spell'leri ekle
    print("\n2. Core spell'ler ekleniyor/guncelleniyor...")
    added = ensure_core_spells_exist(DATA_FILE)
    print(f"   Eklenen/Guncellenen: {added} spell")

    # Sonuc
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    after_count = len(data.get("spells", {}))
    print(f"\nSonuc: {before_count} -> {after_count} spell")

    # Kalite raporu
    print("\n--- KALITE RAPORU ---")
    good = 0
    bad = 0
    for name, spell in data.get("spells", {}).items():
        ct = spell.get("casting_time", "")
        if ct and len(ct) < 100:
            good += 1
        else:
            bad += 1
    print(f"Temiz spell: {good}")
    print(f"Hala bozuk: {bad}")
    if after_count > 0:
        print(f"Temizlik orani: %{100*good/after_count:.1f}")


def scrape_new_spells(batch_size=50, max_batches=1, start_from=0):
    """AONPRD'den yeni spell'ler cek"""
    try:
        from utils.pathfinder_scraper import PathfinderSpellScraper
    except ImportError:
        print("HATA: requests ve beautifulsoup4 gerekli!")
        print("pip install requests beautifulsoup4")
        return

    print("=" * 60)
    print("PATHFINDER 1e SPELL SCRAPING")
    print(f"Batch boyutu: {batch_size}, Max batch: {max_batches}")
    print("=" * 60)

    scraper = PathfinderSpellScraper(delay=1.5)

    # Spell listesini cek
    print("\nSpell listesi cekiliyor...")
    spell_names = scraper.scrape_spell_list()
    print(f"Toplam bulunan: {len(spell_names)} spell")

    if not spell_names:
        print("Spell listesi alinamadi!")
        return

    # Mevcut spell'leri yukle
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    existing_spells = data.get("spells", {})
    print(f"Mevcut veritabaninda: {len(existing_spells)} spell")

    # Eksik spell'leri bul
    missing = [n for n in spell_names if n not in existing_spells]
    print(f"Eksik spell: {len(missing)}")

    if not missing:
        print("Tum spell'ler zaten mevcut!")
        return

    # Batch scraping
    total_added = 0
    for batch_num in range(max_batches):
        batch_start = start_from + (batch_num * batch_size)
        batch_end = min(batch_start + batch_size, len(missing))

        if batch_start >= len(missing):
            break

        batch = missing[batch_start:batch_end]
        print(f"\nBatch {batch_num+1}: Spell {batch_start+1}-{batch_end} / {len(missing)}")

        results = scraper.scrape_spells_batch(batch, 0, len(batch))
        print(f"  Basarili: {len(results)} / {len(batch)}")

        # Veritabanina ekle
        for name, spell_data in results.items():
            existing_spells[name] = spell_data
            total_added += 1

        # Her batch sonrasi kaydet
        data["spells"] = existing_spells
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Kaydedildi. Toplam: {len(existing_spells)} spell")

    print(f"\n{'='*60}")
    print(f"TAMAMLANDI: {total_added} yeni spell eklendi")
    print(f"Toplam veritabani: {len(existing_spells)} spell")

    if start_from + max_batches * batch_size < len(missing):
        next_start = start_from + max_batches * batch_size
        print(f"\nDevam etmek icin:")
        print(f"  python scripts/scrape_pf1e_spells.py --scrape --batch-size {batch_size} --start-from {next_start}")


def main():
    parser = argparse.ArgumentParser(description="Pathfinder 1e Spell Scraping & Temizleme")
    parser.add_argument("--clean-only", action="store_true", help="Sadece mevcut veriyi temizle")
    parser.add_argument("--scrape", action="store_true", help="AONPRD'den yeni spell cek")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch boyutu (default: 50)")
    parser.add_argument("--max-batches", type=int, default=2, help="Max batch sayisi (default: 2)")
    parser.add_argument("--start-from", type=int, default=0, help="Baslangic indeksi")

    args = parser.parse_args()

    if not args.clean_only and not args.scrape:
        args.clean_only = True  # Default: sadece temizle

    if args.clean_only:
        clean_existing_data()

    if args.scrape:
        scrape_new_spells(args.batch_size, args.max_batches, args.start_from)


if __name__ == "__main__":
    main()
