"""
Pathfinder 1e spell scraping test
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.pathfinder_scraper import PathfinderScraper

def main():
    print("=" * 70)
    print("PATHFINDER 1E SPELL SCRAPING TEST")
    print("=" * 70)
    print()
    
    # Mevcut spell'leri kontrol et
    data_file = project_root / "data" / "pathfinder_1e_data.json"
    if data_file.exists():
        import json
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        spells = data.get('spells', {})
        print(f"Mevcut spell sayisi: {len(spells)}")
        
        if spells:
            print("\nOrnek 3 spell:")
            for i, (name, spell) in enumerate(list(spells.items())[:3], 1):
                print(f"\n{i}. {name}:")
                print(f"   Level: {spell.get('level', '?')}")
                print(f"   School: {spell.get('school', '?')}")
                print(f"   Casting Time: {spell.get('casting_time', '?')[:80]}")
                print(f"   Components: {spell.get('components', '?')[:80]}")
                print(f"   Range: {spell.get('range', '?')[:80]}")
                print(f"   Duration: {spell.get('duration', '?')[:80]}")
    
    # Yeni spell scraping testi (sadece 3 spell)
    print("\n" + "=" * 70)
    print("YENI SPELL SCRAPING TEST (3 spell)")
    print("=" * 70)
    print()
    
    scraper = PathfinderScraper(site="aonprd", delay=1.5)
    test_spells = scraper.scrape_spells(max_spells=3)
    
    print(f"\nTest scraping: {len(test_spells)} spell cekildi")
    for name, spell in test_spells.items():
        print(f"\n- {name}:")
        print(f"  Level: {spell.get('level', '?')}")
        print(f"  School: {spell.get('school', '?')}")
        print(f"  Casting Time: {spell.get('casting_time', '?')[:60]}")
        print(f"  Components: {spell.get('components', '?')[:60]}")

if __name__ == "__main__":
    main()

