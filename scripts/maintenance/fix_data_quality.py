"""
Veri kalitesi düzeltme scripti
- Race subrace name alanlarını doldurur
- Class hit_dice alanlarını doldurur
- Spell level validation yapar
"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/maintenance -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.data_loader import load_dnd_data

def fix_race_names(dnd_data):
    """Race subrace name alanlarını doldur"""
    print("=" * 70)
    print("Race Name Alanlari Duzenleniyor")
    print("=" * 70)
    
    races = dnd_data.get('races', {})
    fixed_count = 0
    
    # Subrace'leri bul ve name alanını ekle
    for race_name, race_data in races.items():
        if not isinstance(race_data, dict):
            continue
        
        # Eğer name alanı yoksa, race_name'i kullan
        if 'name' not in race_data:
            race_data['name'] = race_name
            fixed_count += 1
            print(f"  [DUZELT] {race_name}: name alani eklendi")
    
    print(f"\n[OK] {fixed_count} race name alani duzeltildi")
    return fixed_count

def fix_class_names(dnd_data):
    """Class name alanlarını doldur"""
    print("\n" + "=" * 70)
    print("Class Name Alanlari Duzenleniyor")
    print("=" * 70)
    
    classes = dnd_data.get('classes', {})
    fixed_count = 0
    
    # Class'ları bul ve name alanını ekle
    for class_name, class_data in classes.items():
        if not isinstance(class_data, dict):
            continue
        
        # Eğer name alanı yoksa, class_name'i kullan
        if 'name' not in class_data:
            class_data['name'] = class_name
            fixed_count += 1
            print(f"  [DUZELT] {class_name}: name alani eklendi")
    
    print(f"\n[OK] {fixed_count} class name alani duzeltildi")
    return fixed_count

def fix_class_hit_dice(dnd_data):
    """Class hit_dice alanlarını doldur"""
    print("\n" + "=" * 70)
    print("Class Hit Dice Alanlari Duzenleniyor")
    print("=" * 70)
    
    classes = dnd_data.get('classes', {})
    fixed_count = 0
    
    # Class hit_dice mapping (bilinen D&D 5e hit dice)
    hit_dice_map = {
        'Barbarian': 'd12',
        'Bard': 'd8',
        'Cleric': 'd8',
        'Druid': 'd8',
        'Fighter': 'd10',
        'Monk': 'd8',
        'Paladin': 'd10',
        'Ranger': 'd10',
        'Rogue': 'd8',
        'Sorcerer': 'd6',
        'Warlock': 'd8',
        'Wizard': 'd6',
        'Artificer': 'd8'
    }
    
    for class_name, class_data in classes.items():
        if not isinstance(class_data, dict):
            continue
        
        # Eğer hit_dice yoksa, mapping'den al
        if 'hit_dice' not in class_data or not class_data.get('hit_dice'):
            if class_name in hit_dice_map:
                class_data['hit_dice'] = hit_dice_map[class_name]
                fixed_count += 1
                print(f"  [DUZELT] {class_name}: hit_dice = {hit_dice_map[class_name]} eklendi")
            else:
                # Default olarak d8 kullan
                class_data['hit_dice'] = 'd8'
                fixed_count += 1
                print(f"  [DUZELT] {class_name}: hit_dice = d8 (default) eklendi")
    
    print(f"\n[OK] {fixed_count} class hit_dice alani duzeltildi")
    return fixed_count

def fix_spell_levels(dnd_data):
    """Spell level validation ve düzeltme"""
    print("\n" + "=" * 70)
    print("Spell Level Validation")
    print("=" * 70)
    
    spells = dnd_data.get('spells', {})
    fixed_count = 0
    invalid_count = 0
    
    for spell_name, spell_data in spells.items():
        if not isinstance(spell_data, dict):
            continue
        
        level = spell_data.get('level')
        
        # None veya geçersiz level değerleri
        if level is None:
            # Default olarak cantrip (0) kullan veya spell'i işaretle
            spell_data['level'] = 0
            spell_data['_level_fixed'] = True  # İşaretle, manuel kontrol gerekebilir
            fixed_count += 1
            if fixed_count <= 10:  # İlk 10'unu göster
                print(f"  [DUZELT] {spell_name}: level None -> 0 (cantrip) yapildi")
        elif isinstance(level, int):
            # Level 0-9 arasında olmalı (D&D 5e)
            if level < 0:
                spell_data['level'] = 0
                fixed_count += 1
                if fixed_count <= 10:
                    print(f"  [DUZELT] {spell_name}: level {level} -> 0 duzeltildi")
            elif level > 9:
                # 9. seviyeden yüksek spell'ler özel (epic level)
                # Bunları 9'a indir veya işaretle
                spell_data['level'] = 9
                spell_data['_level_capped'] = True
                fixed_count += 1
                invalid_count += 1
                if fixed_count <= 10:
                    print(f"  [DUZELT] {spell_name}: level {level} -> 9 (capped) yapildi")
        elif isinstance(level, str):
            # String level değerini parse et
            try:
                level_int = int(level)
                if 0 <= level_int <= 9:
                    spell_data['level'] = level_int
                    fixed_count += 1
                else:
                    spell_data['level'] = min(max(level_int, 0), 9)
                    fixed_count += 1
                    invalid_count += 1
            except ValueError:
                # Parse edilemezse default 0
                spell_data['level'] = 0
                spell_data['_level_fixed'] = True
                fixed_count += 1
    
    print(f"\n[OK] {fixed_count} spell level duzeltildi ({invalid_count} capped)")
    return fixed_count, invalid_count

def main():
    """Tum veri kalitesi duzeltmelerini yap"""
    print("=" * 70)
    print("VERI KALITESI DUZELTME")
    print("=" * 70)
    print()
    
    # Veriyi yukle
    print("[*] Veri yukleniyor...")
    dnd_data = load_dnd_data(project_root)
    
    # Duzenlemeleri yap
    race_fixed = fix_race_names(dnd_data)
    class_name_fixed = fix_class_names(dnd_data)
    class_fixed = fix_class_hit_dice(dnd_data)
    spell_fixed, spell_invalid = fix_spell_levels(dnd_data)
    
    # Kaydet
    data_file = project_root / "data" / "dnd_data.json"
    print(f"\n[*] Duzeltilmis veri kaydediliyor: {data_file}")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(dnd_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Veri kaydedildi!")
    
    # Ozet
    print("\n" + "=" * 70)
    print("DUZELTME OZETI")
    print("=" * 70)
    print(f"Race name alanlari: {race_fixed} duzeltildi")
    print(f"Class name alanlari: {class_name_fixed} duzeltildi")
    print(f"Class hit_dice alanlari: {class_fixed} duzeltildi")
    print(f"Spell level alanlari: {spell_fixed} duzeltildi ({spell_invalid} capped)")
    print(f"\nToplam: {race_fixed + class_name_fixed + class_fixed + spell_fixed} alan duzeltildi")
    
    print("\n[OK] Veri kalitesi duzeltme tamamlandi!")
    return 0

if __name__ == "__main__":
    sys.exit(main())


- Race subrace name alanlarını doldurur
- Class hit_dice alanlarını doldurur
- Spell level validation yapar
"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/maintenance -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.data_loader import load_dnd_data

def fix_race_names(dnd_data):
    """Race subrace name alanlarını doldur"""
    print("=" * 70)
    print("Race Name Alanlari Duzenleniyor")
    print("=" * 70)
    
    races = dnd_data.get('races', {})
    fixed_count = 0
    
    # Subrace'leri bul ve name alanını ekle
    for race_name, race_data in races.items():
        if not isinstance(race_data, dict):
            continue
        
        # Eğer name alanı yoksa, race_name'i kullan
        if 'name' not in race_data:
            race_data['name'] = race_name
            fixed_count += 1
            print(f"  [DUZELT] {race_name}: name alani eklendi")
    
    print(f"\n[OK] {fixed_count} race name alani duzeltildi")
    return fixed_count

def fix_class_names(dnd_data):
    """Class name alanlarını doldur"""
    print("\n" + "=" * 70)
    print("Class Name Alanlari Duzenleniyor")
    print("=" * 70)
    
    classes = dnd_data.get('classes', {})
    fixed_count = 0
    
    # Class'ları bul ve name alanını ekle
    for class_name, class_data in classes.items():
        if not isinstance(class_data, dict):
            continue
        
        # Eğer name alanı yoksa, class_name'i kullan
        if 'name' not in class_data:
            class_data['name'] = class_name
            fixed_count += 1
            print(f"  [DUZELT] {class_name}: name alani eklendi")
    
    print(f"\n[OK] {fixed_count} class name alani duzeltildi")
    return fixed_count

def fix_class_hit_dice(dnd_data):
    """Class hit_dice alanlarını doldur"""
    print("\n" + "=" * 70)
    print("Class Hit Dice Alanlari Duzenleniyor")
    print("=" * 70)
    
    classes = dnd_data.get('classes', {})
    fixed_count = 0
    
    # Class hit_dice mapping (bilinen D&D 5e hit dice)
    hit_dice_map = {
        'Barbarian': 'd12',
        'Bard': 'd8',
        'Cleric': 'd8',
        'Druid': 'd8',
        'Fighter': 'd10',
        'Monk': 'd8',
        'Paladin': 'd10',
        'Ranger': 'd10',
        'Rogue': 'd8',
        'Sorcerer': 'd6',
        'Warlock': 'd8',
        'Wizard': 'd6',
        'Artificer': 'd8'
    }
    
    for class_name, class_data in classes.items():
        if not isinstance(class_data, dict):
            continue
        
        # Eğer hit_dice yoksa, mapping'den al
        if 'hit_dice' not in class_data or not class_data.get('hit_dice'):
            if class_name in hit_dice_map:
                class_data['hit_dice'] = hit_dice_map[class_name]
                fixed_count += 1
                print(f"  [DUZELT] {class_name}: hit_dice = {hit_dice_map[class_name]} eklendi")
            else:
                # Default olarak d8 kullan
                class_data['hit_dice'] = 'd8'
                fixed_count += 1
                print(f"  [DUZELT] {class_name}: hit_dice = d8 (default) eklendi")
    
    print(f"\n[OK] {fixed_count} class hit_dice alani duzeltildi")
    return fixed_count

def fix_spell_levels(dnd_data):
    """Spell level validation ve düzeltme"""
    print("\n" + "=" * 70)
    print("Spell Level Validation")
    print("=" * 70)
    
    spells = dnd_data.get('spells', {})
    fixed_count = 0
    invalid_count = 0
    
    for spell_name, spell_data in spells.items():
        if not isinstance(spell_data, dict):
            continue
        
        level = spell_data.get('level')
        
        # None veya geçersiz level değerleri
        if level is None:
            # Default olarak cantrip (0) kullan veya spell'i işaretle
            spell_data['level'] = 0
            spell_data['_level_fixed'] = True  # İşaretle, manuel kontrol gerekebilir
            fixed_count += 1
            if fixed_count <= 10:  # İlk 10'unu göster
                print(f"  [DUZELT] {spell_name}: level None -> 0 (cantrip) yapildi")
        elif isinstance(level, int):
            # Level 0-9 arasında olmalı (D&D 5e)
            if level < 0:
                spell_data['level'] = 0
                fixed_count += 1
                if fixed_count <= 10:
                    print(f"  [DUZELT] {spell_name}: level {level} -> 0 duzeltildi")
            elif level > 9:
                # 9. seviyeden yüksek spell'ler özel (epic level)
                # Bunları 9'a indir veya işaretle
                spell_data['level'] = 9
                spell_data['_level_capped'] = True
                fixed_count += 1
                invalid_count += 1
                if fixed_count <= 10:
                    print(f"  [DUZELT] {spell_name}: level {level} -> 9 (capped) yapildi")
        elif isinstance(level, str):
            # String level değerini parse et
            try:
                level_int = int(level)
                if 0 <= level_int <= 9:
                    spell_data['level'] = level_int
                    fixed_count += 1
                else:
                    spell_data['level'] = min(max(level_int, 0), 9)
                    fixed_count += 1
                    invalid_count += 1
            except ValueError:
                # Parse edilemezse default 0
                spell_data['level'] = 0
                spell_data['_level_fixed'] = True
                fixed_count += 1
    
    print(f"\n[OK] {fixed_count} spell level duzeltildi ({invalid_count} capped)")
    return fixed_count, invalid_count

def main():
    """Tum veri kalitesi duzeltmelerini yap"""
    print("=" * 70)
    print("VERI KALITESI DUZELTME")
    print("=" * 70)
    print()
    
    # Veriyi yukle
    print("[*] Veri yukleniyor...")
    dnd_data = load_dnd_data(project_root)
    
    # Duzenlemeleri yap
    race_fixed = fix_race_names(dnd_data)
    class_name_fixed = fix_class_names(dnd_data)
    class_fixed = fix_class_hit_dice(dnd_data)
    spell_fixed, spell_invalid = fix_spell_levels(dnd_data)
    
    # Kaydet
    data_file = project_root / "data" / "dnd_data.json"
    print(f"\n[*] Duzeltilmis veri kaydediliyor: {data_file}")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(dnd_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Veri kaydedildi!")
    
    # Ozet
    print("\n" + "=" * 70)
    print("DUZELTME OZETI")
    print("=" * 70)
    print(f"Race name alanlari: {race_fixed} duzeltildi")
    print(f"Class name alanlari: {class_name_fixed} duzeltildi")
    print(f"Class hit_dice alanlari: {class_fixed} duzeltildi")
    print(f"Spell level alanlari: {spell_fixed} duzeltildi ({spell_invalid} capped)")
    print(f"\nToplam: {race_fixed + class_name_fixed + class_fixed + spell_fixed} alan duzeltildi")
    
    print("\n[OK] Veri kalitesi duzeltme tamamlandi!")
    return 0

if __name__ == "__main__":
    sys.exit(main())


- Race subrace name alanlarını doldurur
- Class hit_dice alanlarını doldurur
- Spell level validation yapar
"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/maintenance -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.data_loader import load_dnd_data

def fix_race_names(dnd_data):
    """Race subrace name alanlarını doldur"""
    print("=" * 70)
    print("Race Name Alanlari Duzenleniyor")
    print("=" * 70)
    
    races = dnd_data.get('races', {})
    fixed_count = 0
    
    # Subrace'leri bul ve name alanını ekle
    for race_name, race_data in races.items():
        if not isinstance(race_data, dict):
            continue
        
        # Eğer name alanı yoksa, race_name'i kullan
        if 'name' not in race_data:
            race_data['name'] = race_name
            fixed_count += 1
            print(f"  [DUZELT] {race_name}: name alani eklendi")
    
    print(f"\n[OK] {fixed_count} race name alani duzeltildi")
    return fixed_count

def fix_class_names(dnd_data):
    """Class name alanlarını doldur"""
    print("\n" + "=" * 70)
    print("Class Name Alanlari Duzenleniyor")
    print("=" * 70)
    
    classes = dnd_data.get('classes', {})
    fixed_count = 0
    
    # Class'ları bul ve name alanını ekle
    for class_name, class_data in classes.items():
        if not isinstance(class_data, dict):
            continue
        
        # Eğer name alanı yoksa, class_name'i kullan
        if 'name' not in class_data:
            class_data['name'] = class_name
            fixed_count += 1
            print(f"  [DUZELT] {class_name}: name alani eklendi")
    
    print(f"\n[OK] {fixed_count} class name alani duzeltildi")
    return fixed_count

def fix_class_hit_dice(dnd_data):
    """Class hit_dice alanlarını doldur"""
    print("\n" + "=" * 70)
    print("Class Hit Dice Alanlari Duzenleniyor")
    print("=" * 70)
    
    classes = dnd_data.get('classes', {})
    fixed_count = 0
    
    # Class hit_dice mapping (bilinen D&D 5e hit dice)
    hit_dice_map = {
        'Barbarian': 'd12',
        'Bard': 'd8',
        'Cleric': 'd8',
        'Druid': 'd8',
        'Fighter': 'd10',
        'Monk': 'd8',
        'Paladin': 'd10',
        'Ranger': 'd10',
        'Rogue': 'd8',
        'Sorcerer': 'd6',
        'Warlock': 'd8',
        'Wizard': 'd6',
        'Artificer': 'd8'
    }
    
    for class_name, class_data in classes.items():
        if not isinstance(class_data, dict):
            continue
        
        # Eğer hit_dice yoksa, mapping'den al
        if 'hit_dice' not in class_data or not class_data.get('hit_dice'):
            if class_name in hit_dice_map:
                class_data['hit_dice'] = hit_dice_map[class_name]
                fixed_count += 1
                print(f"  [DUZELT] {class_name}: hit_dice = {hit_dice_map[class_name]} eklendi")
            else:
                # Default olarak d8 kullan
                class_data['hit_dice'] = 'd8'
                fixed_count += 1
                print(f"  [DUZELT] {class_name}: hit_dice = d8 (default) eklendi")
    
    print(f"\n[OK] {fixed_count} class hit_dice alani duzeltildi")
    return fixed_count

def fix_spell_levels(dnd_data):
    """Spell level validation ve düzeltme"""
    print("\n" + "=" * 70)
    print("Spell Level Validation")
    print("=" * 70)
    
    spells = dnd_data.get('spells', {})
    fixed_count = 0
    invalid_count = 0
    
    for spell_name, spell_data in spells.items():
        if not isinstance(spell_data, dict):
            continue
        
        level = spell_data.get('level')
        
        # None veya geçersiz level değerleri
        if level is None:
            # Default olarak cantrip (0) kullan veya spell'i işaretle
            spell_data['level'] = 0
            spell_data['_level_fixed'] = True  # İşaretle, manuel kontrol gerekebilir
            fixed_count += 1
            if fixed_count <= 10:  # İlk 10'unu göster
                print(f"  [DUZELT] {spell_name}: level None -> 0 (cantrip) yapildi")
        elif isinstance(level, int):
            # Level 0-9 arasında olmalı (D&D 5e)
            if level < 0:
                spell_data['level'] = 0
                fixed_count += 1
                if fixed_count <= 10:
                    print(f"  [DUZELT] {spell_name}: level {level} -> 0 duzeltildi")
            elif level > 9:
                # 9. seviyeden yüksek spell'ler özel (epic level)
                # Bunları 9'a indir veya işaretle
                spell_data['level'] = 9
                spell_data['_level_capped'] = True
                fixed_count += 1
                invalid_count += 1
                if fixed_count <= 10:
                    print(f"  [DUZELT] {spell_name}: level {level} -> 9 (capped) yapildi")
        elif isinstance(level, str):
            # String level değerini parse et
            try:
                level_int = int(level)
                if 0 <= level_int <= 9:
                    spell_data['level'] = level_int
                    fixed_count += 1
                else:
                    spell_data['level'] = min(max(level_int, 0), 9)
                    fixed_count += 1
                    invalid_count += 1
            except ValueError:
                # Parse edilemezse default 0
                spell_data['level'] = 0
                spell_data['_level_fixed'] = True
                fixed_count += 1
    
    print(f"\n[OK] {fixed_count} spell level duzeltildi ({invalid_count} capped)")
    return fixed_count, invalid_count

def main():
    """Tum veri kalitesi duzeltmelerini yap"""
    print("=" * 70)
    print("VERI KALITESI DUZELTME")
    print("=" * 70)
    print()
    
    # Veriyi yukle
    print("[*] Veri yukleniyor...")
    dnd_data = load_dnd_data(project_root)
    
    # Duzenlemeleri yap
    race_fixed = fix_race_names(dnd_data)
    class_name_fixed = fix_class_names(dnd_data)
    class_fixed = fix_class_hit_dice(dnd_data)
    spell_fixed, spell_invalid = fix_spell_levels(dnd_data)
    
    # Kaydet
    data_file = project_root / "data" / "dnd_data.json"
    print(f"\n[*] Duzeltilmis veri kaydediliyor: {data_file}")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(dnd_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Veri kaydedildi!")
    
    # Ozet
    print("\n" + "=" * 70)
    print("DUZELTME OZETI")
    print("=" * 70)
    print(f"Race name alanlari: {race_fixed} duzeltildi")
    print(f"Class name alanlari: {class_name_fixed} duzeltildi")
    print(f"Class hit_dice alanlari: {class_fixed} duzeltildi")
    print(f"Spell level alanlari: {spell_fixed} duzeltildi ({spell_invalid} capped)")
    print(f"\nToplam: {race_fixed + class_name_fixed + class_fixed + spell_fixed} alan duzeltildi")
    
    print("\n[OK] Veri kalitesi duzeltme tamamlandi!")
    return 0

if __name__ == "__main__":
    sys.exit(main())


- Race subrace name alanlarını doldurur
- Class hit_dice alanlarını doldurur
- Spell level validation yapar
"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/maintenance -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.data_loader import load_dnd_data

def fix_race_names(dnd_data):
    """Race subrace name alanlarını doldur"""
    print("=" * 70)
    print("Race Name Alanlari Duzenleniyor")
    print("=" * 70)
    
    races = dnd_data.get('races', {})
    fixed_count = 0
    
    # Subrace'leri bul ve name alanını ekle
    for race_name, race_data in races.items():
        if not isinstance(race_data, dict):
            continue
        
        # Eğer name alanı yoksa, race_name'i kullan
        if 'name' not in race_data:
            race_data['name'] = race_name
            fixed_count += 1
            print(f"  [DUZELT] {race_name}: name alani eklendi")
    
    print(f"\n[OK] {fixed_count} race name alani duzeltildi")
    return fixed_count

def fix_class_names(dnd_data):
    """Class name alanlarını doldur"""
    print("\n" + "=" * 70)
    print("Class Name Alanlari Duzenleniyor")
    print("=" * 70)
    
    classes = dnd_data.get('classes', {})
    fixed_count = 0
    
    # Class'ları bul ve name alanını ekle
    for class_name, class_data in classes.items():
        if not isinstance(class_data, dict):
            continue
        
        # Eğer name alanı yoksa, class_name'i kullan
        if 'name' not in class_data:
            class_data['name'] = class_name
            fixed_count += 1
            print(f"  [DUZELT] {class_name}: name alani eklendi")
    
    print(f"\n[OK] {fixed_count} class name alani duzeltildi")
    return fixed_count

def fix_class_hit_dice(dnd_data):
    """Class hit_dice alanlarını doldur"""
    print("\n" + "=" * 70)
    print("Class Hit Dice Alanlari Duzenleniyor")
    print("=" * 70)
    
    classes = dnd_data.get('classes', {})
    fixed_count = 0
    
    # Class hit_dice mapping (bilinen D&D 5e hit dice)
    hit_dice_map = {
        'Barbarian': 'd12',
        'Bard': 'd8',
        'Cleric': 'd8',
        'Druid': 'd8',
        'Fighter': 'd10',
        'Monk': 'd8',
        'Paladin': 'd10',
        'Ranger': 'd10',
        'Rogue': 'd8',
        'Sorcerer': 'd6',
        'Warlock': 'd8',
        'Wizard': 'd6',
        'Artificer': 'd8'
    }
    
    for class_name, class_data in classes.items():
        if not isinstance(class_data, dict):
            continue
        
        # Eğer hit_dice yoksa, mapping'den al
        if 'hit_dice' not in class_data or not class_data.get('hit_dice'):
            if class_name in hit_dice_map:
                class_data['hit_dice'] = hit_dice_map[class_name]
                fixed_count += 1
                print(f"  [DUZELT] {class_name}: hit_dice = {hit_dice_map[class_name]} eklendi")
            else:
                # Default olarak d8 kullan
                class_data['hit_dice'] = 'd8'
                fixed_count += 1
                print(f"  [DUZELT] {class_name}: hit_dice = d8 (default) eklendi")
    
    print(f"\n[OK] {fixed_count} class hit_dice alani duzeltildi")
    return fixed_count

def fix_spell_levels(dnd_data):
    """Spell level validation ve düzeltme"""
    print("\n" + "=" * 70)
    print("Spell Level Validation")
    print("=" * 70)
    
    spells = dnd_data.get('spells', {})
    fixed_count = 0
    invalid_count = 0
    
    for spell_name, spell_data in spells.items():
        if not isinstance(spell_data, dict):
            continue
        
        level = spell_data.get('level')
        
        # None veya geçersiz level değerleri
        if level is None:
            # Default olarak cantrip (0) kullan veya spell'i işaretle
            spell_data['level'] = 0
            spell_data['_level_fixed'] = True  # İşaretle, manuel kontrol gerekebilir
            fixed_count += 1
            if fixed_count <= 10:  # İlk 10'unu göster
                print(f"  [DUZELT] {spell_name}: level None -> 0 (cantrip) yapildi")
        elif isinstance(level, int):
            # Level 0-9 arasında olmalı (D&D 5e)
            if level < 0:
                spell_data['level'] = 0
                fixed_count += 1
                if fixed_count <= 10:
                    print(f"  [DUZELT] {spell_name}: level {level} -> 0 duzeltildi")
            elif level > 9:
                # 9. seviyeden yüksek spell'ler özel (epic level)
                # Bunları 9'a indir veya işaretle
                spell_data['level'] = 9
                spell_data['_level_capped'] = True
                fixed_count += 1
                invalid_count += 1
                if fixed_count <= 10:
                    print(f"  [DUZELT] {spell_name}: level {level} -> 9 (capped) yapildi")
        elif isinstance(level, str):
            # String level değerini parse et
            try:
                level_int = int(level)
                if 0 <= level_int <= 9:
                    spell_data['level'] = level_int
                    fixed_count += 1
                else:
                    spell_data['level'] = min(max(level_int, 0), 9)
                    fixed_count += 1
                    invalid_count += 1
            except ValueError:
                # Parse edilemezse default 0
                spell_data['level'] = 0
                spell_data['_level_fixed'] = True
                fixed_count += 1
    
    print(f"\n[OK] {fixed_count} spell level duzeltildi ({invalid_count} capped)")
    return fixed_count, invalid_count

def main():
    """Tum veri kalitesi duzeltmelerini yap"""
    print("=" * 70)
    print("VERI KALITESI DUZELTME")
    print("=" * 70)
    print()
    
    # Veriyi yukle
    print("[*] Veri yukleniyor...")
    dnd_data = load_dnd_data(project_root)
    
    # Duzenlemeleri yap
    race_fixed = fix_race_names(dnd_data)
    class_name_fixed = fix_class_names(dnd_data)
    class_fixed = fix_class_hit_dice(dnd_data)
    spell_fixed, spell_invalid = fix_spell_levels(dnd_data)
    
    # Kaydet
    data_file = project_root / "data" / "dnd_data.json"
    print(f"\n[*] Duzeltilmis veri kaydediliyor: {data_file}")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(dnd_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Veri kaydedildi!")
    
    # Ozet
    print("\n" + "=" * 70)
    print("DUZELTME OZETI")
    print("=" * 70)
    print(f"Race name alanlari: {race_fixed} duzeltildi")
    print(f"Class name alanlari: {class_name_fixed} duzeltildi")
    print(f"Class hit_dice alanlari: {class_fixed} duzeltildi")
    print(f"Spell level alanlari: {spell_fixed} duzeltildi ({spell_invalid} capped)")
    print(f"\nToplam: {race_fixed + class_name_fixed + class_fixed + spell_fixed} alan duzeltildi")
    
    print("\n[OK] Veri kalitesi duzeltme tamamlandi!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

