"""
Pathfinder 1e spell parsing test - yeni parser ile
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.pathfinder_scraper import PathfinderScraper

def main():
    print("=" * 70)
    print("PATHFINDER 1E SPELL PARSING TEST")
    print("=" * 70)
    print()
    
    scraper = PathfinderScraper(site="aonprd", delay=1.5)
    
    # Sadece 3 spell test et
    print("Test: 3 spell cekiliyor...")
    test_spells = scraper.scrape_spells(max_spells=3)
    
    print(f"\nOK: {len(test_spells)} spell cekildi")
    print("\n" + "=" * 70)
    print("PARSE SONUCLARI")
    print("=" * 70)
    
    for name, spell in test_spells.items():
        print(f"\n{name}:")
        print(f"  Level: {spell.get('level', '?')}")
        print(f"  Levels by Class: {spell.get('levels_by_class', {})}")
        print(f"  School: {spell.get('school', '?')}")
        print(f"  Casting Time: {spell.get('casting_time', '?')[:80]}")
        print(f"  Components: {spell.get('components', '?')[:80]}")
        print(f"  Material Components: {spell.get('material_components', '?')[:80]}")
        print(f"  Focus: {spell.get('focus', '?')[:80]}")
        print(f"  Range: {spell.get('range', '?')[:80]}")
        print(f"  Target: {spell.get('target', '?')[:80]}")
        print(f"  Area: {spell.get('area', '?')[:80]}")
        print(f"  Effect: {spell.get('effect', '?')[:80]}")
        print(f"  Duration: {spell.get('duration', '?')[:80]}")
        print(f"  Saving Throw: {spell.get('saving_throw', '?')[:80]}")
        print(f"  Spell Resistance: {spell.get('spell_resistance', '?')[:80]}")
        print(f"  Description: {spell.get('description', '?')[:150]}...")

if __name__ == "__main__":
    main()

