"""
Tüm equipment'leri scrape et ve dnd_data.json'a entegre et
Arka planda çalışacak şekilde tasarlandı
"""
import sys
import json
from pathlib import Path

# Proje root'unu ekle
project_root = Path(__file__).parent.parent.parent  # scripts/scraping -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

def main():
    print("=" * 70)
    print("EQUIPMENT SCRAPING - Arka planda calisiyor")
    print("=" * 70)
    print()
    
    scraper = Dnd5eSrdScraper(rate_limit=2.0)
    
    # Tüm equipment'leri scrape et
    print("Equipment kategorileri scrape ediliyor...")
    equipment_data = scraper.scrape_all_equipment(force_refresh=False)
    
    print("\n[OK] Equipment scraping tamamlandi!")
    print("\nScrape edilen kategoriler:")
    total_items = 0
    for category, items in equipment_data.items():
        count = len(items)
        total_items += count
        print(f"  - {category}: {count} item")
    
    print(f"\n[*] Toplam {total_items} equipment item cekildi!")
    
    # dnd_data.json'a entegre et
    dnd_data_path = project_root / "data" / "dnd_data.json"
    
    if dnd_data_path.exists():
        with open(dnd_data_path, 'r', encoding='utf-8') as f:
            dnd_data = json.load(f)
    else:
        dnd_data = {}
    
    # Equipment data'yı düz bir listeye çevir (kategori bazlı değil, tek bir liste)
    all_equipment = []
    for category, items in equipment_data.items():
        for item in items:
            # Category'yi item'a ekle
            item['category'] = category
            all_equipment.append(item)
    
    # Equipment data'yı ekle/güncelle
    # Önce mevcut equipment'i al (eğer varsa)
    if "equipment" not in dnd_data:
        dnd_data["equipment"] = {}
    elif isinstance(dnd_data["equipment"], list):
        # Eğer liste ise, dict'e çevir (name -> item mapping)
        existing_dict = {}
        for item in dnd_data["equipment"]:
            if isinstance(item, dict) and "name" in item:
                existing_dict[item["name"]] = item
        dnd_data["equipment"] = existing_dict
    
    # Scraped data'yı merge et (name bazlı)
    equipment_dict = {}
    for item in all_equipment:
        name = item.get("name", "")
        if name:
            # Eğer aynı isimde item varsa, scraped data'yı kullan (daha güncel)
            equipment_dict[name] = item
    
    # Mevcut equipment ile birleştir (mevcut item'ları koru, scraped olanları güncelle)
    for name, item in equipment_dict.items():
        dnd_data["equipment"][name] = item
    
    # Kaydet
    with open(dnd_data_path, 'w', encoding='utf-8') as f:
        json.dump(dnd_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Equipment data '{dnd_data_path}' dosyasina kaydedildi!")
    print(f"[*] Toplam {len(dnd_data.get('equipment', {}))} equipment item mevcut.")
    
    # Özet
    print("\n" + "=" * 70)
    print("EQUIPMENT SCRAPING TAMAMLANDI!")
    print("=" * 70)

if __name__ == "__main__":
    main()

