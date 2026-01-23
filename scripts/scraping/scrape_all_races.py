"""
Tüm core races'leri scrape et ve dnd_data.json'a entegre et
Arka planda çalışacak şekilde tasarlandı
"""
import sys
import io
import json
from pathlib import Path

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Proje root'unu ekle
project_root = Path(__file__).parent.parent.parent  # scripts/scraping -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

def main():
    print("=" * 70)
    print("CORE RACES SCRAPING - Arka planda calisiyor")
    print("=" * 70)
    print()
    
    scraper = Dnd5eSrdScraper(rate_limit=2.0)
    
    # Tüm races'leri scrape et
    print("[*] Tum core races scrape ediliyor...")
    races_data = scraper.scrape_all_races(max_races=None, force_refresh=False)
    
    print(f"\n[OK] {len(races_data)} race scrape edildi!")
    print("\nScrape edilen races:")
    for race_name in sorted(races_data.keys()):
        print(f"  - {race_name}")
    
    # dnd_data.json'a entegre et
    dnd_data_path = project_root / "data" / "dnd_data.json"
    
    if dnd_data_path.exists():
        with open(dnd_data_path, 'r', encoding='utf-8') as f:
            dnd_data = json.load(f)
    else:
        dnd_data = {}
    
    # Races data'yı ekle/güncelle
    if "races" not in dnd_data:
        dnd_data["races"] = {}
    
    # Scraped data'yı merge et
    for race_name, race_info in races_data.items():
        dnd_data["races"][race_name] = race_info
    
    # Kaydet
    with open(dnd_data_path, 'w', encoding='utf-8') as f:
        json.dump(dnd_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Races data '{dnd_data_path}' dosyasina kaydedildi!")
    print(f"\n[*] Toplam {len(dnd_data.get('races', {}))} race mevcut.")
    
    # Özet
    print("\n" + "=" * 70)
    print("RACES SCRAPING TAMAMLANDI!")
    print("=" * 70)

if __name__ == "__main__":
    main()

    print("RACES SCRAPING TAMAMLANDI!")
    print("=" * 70)

if __name__ == "__main__":
    main()

    print("RACES SCRAPING TAMAMLANDI!")
    print("=" * 70)

if __name__ == "__main__":
    main()

    print("RACES SCRAPING TAMAMLANDI!")
    print("=" * 70)

if __name__ == "__main__":
    main()
