"""
Equipment scraping test script
"""
import sys
from pathlib import Path

# Proje root'unu ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

def main():
    print("=" * 70)
    print("EQUIPMENT SCRAPING TEST")
    print("=" * 70)
    print()
    
    scraper = Dnd5eSrdScraper()
    
    # Sadece Weapons kategorisini test et
    print("🔍 Weapons kategorisi test ediliyor...")
    weapons_url = f"{scraper.BASE_URL}/equipment/weapons/"
    
    weapons = scraper.scrape_equipment_from_table(weapons_url, "Weapons")
    
    print(f"\n✅ {len(weapons)} weapon çekildi!")
    print("\nİlk 10 weapon:")
    print("-" * 70)
    for i, weapon in enumerate(weapons[:10], 1):
        print(f"{i}. {weapon.get('name', 'Unknown')}")
        if 'cost' in weapon:
            print(f"   Cost: {weapon['cost']}")
        if 'damage' in weapon:
            print(f"   Damage: {weapon['damage']}")
        if 'weight' in weapon:
            print(f"   Weight: {weapon['weight']}")
        if 'properties' in weapon:
            print(f"   Properties: {', '.join(weapon['properties'])}")
        print()

if __name__ == "__main__":
    main()

