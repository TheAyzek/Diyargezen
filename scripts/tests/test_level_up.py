#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Level up sistemini test et"""

import sys
from pathlib import Path
import json

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))

# Test karakteri oluştur
test_character = {
    "system": "DND5E",
    "name": "Test Character",
    "race": "Human",
    "class": "Bard",
    "background": "Entertainer",
    "level": 1,
    "abilities": {
        "Strength": 10,
        "Dexterity": 14,
        "Constitution": 13,
        "Intelligence": 12,
        "Wisdom": 10,
        "Charisma": 16
    },
    "hp": 9,  # 8 (bard) + 1 (CON modifier)
    "features": [],
    "class_features": {},
    "feats": [],
    "spells": {}
}

# dnd_data.json yükle
dnd_file = Path("data/dnd_data.json")
with open(dnd_file, 'r', encoding='utf-8') as f:
    dnd_data = json.load(f)

print("=" * 70)
print("LEVEL UP SİSTEMİ TESTİ")
print("=" * 70)
print()

# Test: Level 1 -> Level 3 (Bard)
print("Test Senaryosu: Bard Level 1 -> Level 3")
print("-" * 70)

char_class = "Bard"
current_level = 1
new_level = 3

classes = dnd_data.get("classes", {})
if char_class in classes:
    class_data = classes[char_class]
    class_features_dict = class_data.get("class_features", {})
    
    print(f"\nClass: {char_class}")
    print(f"Level {current_level} -> {new_level}")
    print()
    
    # Her seviye için class features'ları kontrol et
    gained_features = []
    for level in range(current_level + 1, new_level + 1):
        level_str = str(level)
        if level_str in class_features_dict:
            level_features = class_features_dict[level_str]
            
            print(f"Seviye {level}:")
            
            # Features listesi
            if isinstance(level_features, dict):
                features_list = level_features.get("features", [])
                choices = level_features.get("choices", {})
            elif isinstance(level_features, list):
                features_list = level_features
                choices = {}
            else:
                features_list = []
                choices = {}
            
            if features_list:
                print(f"  OK: Features:")
                for feature in features_list:
                    print(f"     - {feature}")
                    gained_features.append((level, feature))
            
            if choices:
                print(f"  WARNING: Choices (secim gerekli):")
                for choice_type, choice_options in choices.items():
                    print(f"     - {choice_type}: {', '.join(choice_options[:3])}")
                    if len(choice_options) > 3:
                        print(f"       ... ve {len(choice_options) - 3} tane daha")
            
            if not features_list and not choices:
                print(f"  - Ozellik yok")
            print()
    
    print("=" * 70)
    print("SONUC")
    print("=" * 70)
    print(f"OK: Kazanilan features: {len(gained_features)}")
    for level, feature in gained_features:
        print(f"   Seviye {level}: {feature}")
    print()
    
    # ASI seviyelerini kontrol et
    asi_levels = [4, 8, 12, 16, 19]
    if char_class in ["Fighter", "Rogue"]:
        asi_levels = [4, 6, 8, 10, 12, 14, 16, 19]
    
    print(f"ASI seviyeleri ({char_class}): {asi_levels}")
    if new_level in asi_levels:
        print(f"  WARNING: Seviye {new_level} ASI seviyesi - ASI veya Feat secilmeli")
    else:
        print(f"  OK: Seviye {new_level} ASI seviyesi degil")
    print()
    
    # Spell slots kontrolü
    from utils.calculations import calculate_spell_slots
    test_char = test_character.copy()
    test_char["level"] = new_level
    
    class_data = {"classes": {char_class: class_data}}
    spell_slots = calculate_spell_slots(test_char, class_data)
    print(f"Spell slots (Level {new_level}): {spell_slots}")
    
else:
    print(f"ERROR: Class '{char_class}' bulunamadi!")

print()
print("=" * 70)


