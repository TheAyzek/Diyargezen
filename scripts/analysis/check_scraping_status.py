"""Mevcut scraping durumunu kontrol et"""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/analysis -> scripts -> project_root

# dnd_data.json kontrolü
dnd_data_path = project_root / "data" / "dnd_data.json"
if dnd_data_path.exists():
    with open(dnd_data_path, 'r', encoding='utf-8') as f:
        dnd_data = json.load(f)
    print("=" * 70)
    print("DND_DATA.JSON DURUMU")
    print("=" * 70)
    print(f"Races: {len(dnd_data.get('races', {}))}")
    print(f"Classes: {len(dnd_data.get('classes', {}))}")
    print(f"Feats: {len(dnd_data.get('feats', {}))}")
    print(f"Backgrounds: {len(dnd_data.get('backgrounds', {}))}")
    print(f"Spells: {len(dnd_data.get('spells', {}))}")
    print()

# Cache dosyaları kontrolü
cache_files = {
    "classes_cache.json": "Classes",
    "feats_cache.json": "Feats",
    "spells_cache.json": "Spells"
}

print("=" * 70)
print("CACHE DOSYALARI DURUMU")
print("=" * 70)
for cache_file, name in cache_files.items():
    cache_path = project_root / "data" / "cache" / cache_file
    if cache_path.exists():
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        if isinstance(cache_data, dict):
            if 'total' in cache_data:
                print(f"{name}: {cache_data.get('total', 0)} (cache'de)")
            elif name.lower() in cache_data:
                count = len(cache_data[name.lower()])
                print(f"{name}: {count} (cache'de)")
            else:
                count = len(cache_data)
                print(f"{name}: {count} (cache'de)")
        else:
            print(f"{name}: Cache dosyası formatı farklı")
    else:
        print(f"{name}: [YOK] Cache dosyasi yok")

# Races cache kontrolü
races_cache_path = project_root / "data/cache/races_cache.json"
if races_cache_path.exists():
    with open(races_cache_path, 'r', encoding='utf-8') as f:
        races_cache = json.load(f)
    print(f"Races: {len(races_cache.get('races', {}))} (cache'de)")
else:
    print("Races: [YOK] Cache dosyasi yok")

print()
print("=" * 70)
print("YAPILMAMIŞ SCRAPING'LER")
print("=" * 70)

# Backgrounds scraping kontrolü
if 'backgrounds' in dnd_data and len(dnd_data['backgrounds']) > 0:
    print("[OK] Backgrounds: Var")
else:
    print("[YOK] Backgrounds: YAPILMADI")

# Equipment scraping kontrolü (full equipment list)
if 'equipment' in dnd_data and len(dnd_data.get('equipment', {})) > 10:
    print("[OK] Equipment: Var")
else:
    print("[YOK] Equipment: YAPILMADI (sadece starting_equipment_options var)")

