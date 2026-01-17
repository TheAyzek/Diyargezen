"""
Spell veri yapısını kontrol et - ritual, concentration, upcasting bilgileri
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

dnd_file = project_root / "data" / "dnd_data.json"
with open(dnd_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

spells = data.get('spells', {})

print("=" * 70)
print("SPELL VERI YAPISI KONTROLU")
print("=" * 70)
print()

# Örnek spell'ler
sample_spells = ['Magic Missile', 'Fireball', 'Cure Wounds', 'Detect Magic', 'Shield', 
                 'Healing Word', 'Bless', 'Guidance', 'Find Familiar', 'Identify']

for spell_name in sample_spells:
    spell = spells.get(spell_name)
    if not spell:
        print(f"{spell_name}: [BULUNAMADI]")
        continue
    
    if not isinstance(spell, dict):
        print(f"{spell_name}: [DICT DEGIL]")
        continue
    
    print(f"{spell_name}:")
    print(f"  Level: {spell.get('level', 'N/A')}")
    print(f"  School: {spell.get('school', 'N/A')}")
    print(f"  Casting Time: {spell.get('casting_time', 'N/A')}")
    print(f"  Components: {spell.get('components', 'N/A')}")
    print(f"  Duration: {spell.get('duration', 'N/A')}")
    print(f"  Ritual: {spell.get('ritual', False)}")
    print(f"  Concentration: {spell.get('concentration', False)}")
    
    # Upcasting bilgisi (description'da olabilir)
    description = spell.get('description', '')
    has_upcasting = 'higher level' in description.lower() or 'at higher level' in description.lower()
    print(f"  Upcasting: {has_upcasting}")
    
    # Material components
    components = spell.get('components', '')
    has_material = 'M' in str(components) or 'material' in str(components).lower()
    material_desc = None
    if has_material and '(' in str(components):
        # Material component açıklamasını çıkar
        import re
        match = re.search(r'\(([^)]+)\)', str(components))
        if match:
            material_desc = match.group(1)
    print(f"  Material: {has_material} - {material_desc if material_desc else 'N/A'}")
    print()

# İstatistikler
print("=" * 70)
print("ISTATISTIKLER")
print("=" * 70)

total_spells = len(spells)
ritual_spells = sum(1 for s in spells.values() if isinstance(s, dict) and s.get('ritual', False))
concentration_spells = sum(1 for s in spells.values() if isinstance(s, dict) and s.get('concentration', False))
upcasting_spells = sum(1 for s in spells.values() if isinstance(s, dict) and 'higher level' in str(s.get('description', '')).lower())

print(f"Toplam spell: {total_spells}")
print(f"Ritual spell: {ritual_spells}")
print(f"Concentration spell: {concentration_spells}")
print(f"Upcasting spell (description'da): {upcasting_spells}")

# Component istatistikleri
has_material = sum(1 for s in spells.values() if isinstance(s, dict) and ('M' in str(s.get('components', '')) or 'material' in str(s.get('components', '')).lower()))
print(f"Material component: {has_material}")


Spell veri yapısını kontrol et - ritual, concentration, upcasting bilgileri
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

dnd_file = project_root / "data" / "dnd_data.json"
with open(dnd_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

spells = data.get('spells', {})

print("=" * 70)
print("SPELL VERI YAPISI KONTROLU")
print("=" * 70)
print()

# Örnek spell'ler
sample_spells = ['Magic Missile', 'Fireball', 'Cure Wounds', 'Detect Magic', 'Shield', 
                 'Healing Word', 'Bless', 'Guidance', 'Find Familiar', 'Identify']

for spell_name in sample_spells:
    spell = spells.get(spell_name)
    if not spell:
        print(f"{spell_name}: [BULUNAMADI]")
        continue
    
    if not isinstance(spell, dict):
        print(f"{spell_name}: [DICT DEGIL]")
        continue
    
    print(f"{spell_name}:")
    print(f"  Level: {spell.get('level', 'N/A')}")
    print(f"  School: {spell.get('school', 'N/A')}")
    print(f"  Casting Time: {spell.get('casting_time', 'N/A')}")
    print(f"  Components: {spell.get('components', 'N/A')}")
    print(f"  Duration: {spell.get('duration', 'N/A')}")
    print(f"  Ritual: {spell.get('ritual', False)}")
    print(f"  Concentration: {spell.get('concentration', False)}")
    
    # Upcasting bilgisi (description'da olabilir)
    description = spell.get('description', '')
    has_upcasting = 'higher level' in description.lower() or 'at higher level' in description.lower()
    print(f"  Upcasting: {has_upcasting}")
    
    # Material components
    components = spell.get('components', '')
    has_material = 'M' in str(components) or 'material' in str(components).lower()
    material_desc = None
    if has_material and '(' in str(components):
        # Material component açıklamasını çıkar
        import re
        match = re.search(r'\(([^)]+)\)', str(components))
        if match:
            material_desc = match.group(1)
    print(f"  Material: {has_material} - {material_desc if material_desc else 'N/A'}")
    print()

# İstatistikler
print("=" * 70)
print("ISTATISTIKLER")
print("=" * 70)

total_spells = len(spells)
ritual_spells = sum(1 for s in spells.values() if isinstance(s, dict) and s.get('ritual', False))
concentration_spells = sum(1 for s in spells.values() if isinstance(s, dict) and s.get('concentration', False))
upcasting_spells = sum(1 for s in spells.values() if isinstance(s, dict) and 'higher level' in str(s.get('description', '')).lower())

print(f"Toplam spell: {total_spells}")
print(f"Ritual spell: {ritual_spells}")
print(f"Concentration spell: {concentration_spells}")
print(f"Upcasting spell (description'da): {upcasting_spells}")

# Component istatistikleri
has_material = sum(1 for s in spells.values() if isinstance(s, dict) and ('M' in str(s.get('components', '')) or 'material' in str(s.get('components', '')).lower()))
print(f"Material component: {has_material}")




Spell veri yapısını kontrol et - ritual, concentration, upcasting bilgileri
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

dnd_file = project_root / "data" / "dnd_data.json"
with open(dnd_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

spells = data.get('spells', {})

print("=" * 70)
print("SPELL VERI YAPISI KONTROLU")
print("=" * 70)
print()

# Örnek spell'ler
sample_spells = ['Magic Missile', 'Fireball', 'Cure Wounds', 'Detect Magic', 'Shield', 
                 'Healing Word', 'Bless', 'Guidance', 'Find Familiar', 'Identify']

for spell_name in sample_spells:
    spell = spells.get(spell_name)
    if not spell:
        print(f"{spell_name}: [BULUNAMADI]")
        continue
    
    if not isinstance(spell, dict):
        print(f"{spell_name}: [DICT DEGIL]")
        continue
    
    print(f"{spell_name}:")
    print(f"  Level: {spell.get('level', 'N/A')}")
    print(f"  School: {spell.get('school', 'N/A')}")
    print(f"  Casting Time: {spell.get('casting_time', 'N/A')}")
    print(f"  Components: {spell.get('components', 'N/A')}")
    print(f"  Duration: {spell.get('duration', 'N/A')}")
    print(f"  Ritual: {spell.get('ritual', False)}")
    print(f"  Concentration: {spell.get('concentration', False)}")
    
    # Upcasting bilgisi (description'da olabilir)
    description = spell.get('description', '')
    has_upcasting = 'higher level' in description.lower() or 'at higher level' in description.lower()
    print(f"  Upcasting: {has_upcasting}")
    
    # Material components
    components = spell.get('components', '')
    has_material = 'M' in str(components) or 'material' in str(components).lower()
    material_desc = None
    if has_material and '(' in str(components):
        # Material component açıklamasını çıkar
        import re
        match = re.search(r'\(([^)]+)\)', str(components))
        if match:
            material_desc = match.group(1)
    print(f"  Material: {has_material} - {material_desc if material_desc else 'N/A'}")
    print()

# İstatistikler
print("=" * 70)
print("ISTATISTIKLER")
print("=" * 70)

total_spells = len(spells)
ritual_spells = sum(1 for s in spells.values() if isinstance(s, dict) and s.get('ritual', False))
concentration_spells = sum(1 for s in spells.values() if isinstance(s, dict) and s.get('concentration', False))
upcasting_spells = sum(1 for s in spells.values() if isinstance(s, dict) and 'higher level' in str(s.get('description', '')).lower())

print(f"Toplam spell: {total_spells}")
print(f"Ritual spell: {ritual_spells}")
print(f"Concentration spell: {concentration_spells}")
print(f"Upcasting spell (description'da): {upcasting_spells}")

# Component istatistikleri
has_material = sum(1 for s in spells.values() if isinstance(s, dict) and ('M' in str(s.get('components', '')) or 'material' in str(s.get('components', '')).lower()))
print(f"Material component: {has_material}")


Spell veri yapısını kontrol et - ritual, concentration, upcasting bilgileri
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

dnd_file = project_root / "data" / "dnd_data.json"
with open(dnd_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

spells = data.get('spells', {})

print("=" * 70)
print("SPELL VERI YAPISI KONTROLU")
print("=" * 70)
print()

# Örnek spell'ler
sample_spells = ['Magic Missile', 'Fireball', 'Cure Wounds', 'Detect Magic', 'Shield', 
                 'Healing Word', 'Bless', 'Guidance', 'Find Familiar', 'Identify']

for spell_name in sample_spells:
    spell = spells.get(spell_name)
    if not spell:
        print(f"{spell_name}: [BULUNAMADI]")
        continue
    
    if not isinstance(spell, dict):
        print(f"{spell_name}: [DICT DEGIL]")
        continue
    
    print(f"{spell_name}:")
    print(f"  Level: {spell.get('level', 'N/A')}")
    print(f"  School: {spell.get('school', 'N/A')}")
    print(f"  Casting Time: {spell.get('casting_time', 'N/A')}")
    print(f"  Components: {spell.get('components', 'N/A')}")
    print(f"  Duration: {spell.get('duration', 'N/A')}")
    print(f"  Ritual: {spell.get('ritual', False)}")
    print(f"  Concentration: {spell.get('concentration', False)}")
    
    # Upcasting bilgisi (description'da olabilir)
    description = spell.get('description', '')
    has_upcasting = 'higher level' in description.lower() or 'at higher level' in description.lower()
    print(f"  Upcasting: {has_upcasting}")
    
    # Material components
    components = spell.get('components', '')
    has_material = 'M' in str(components) or 'material' in str(components).lower()
    material_desc = None
    if has_material and '(' in str(components):
        # Material component açıklamasını çıkar
        import re
        match = re.search(r'\(([^)]+)\)', str(components))
        if match:
            material_desc = match.group(1)
    print(f"  Material: {has_material} - {material_desc if material_desc else 'N/A'}")
    print()

# İstatistikler
print("=" * 70)
print("ISTATISTIKLER")
print("=" * 70)

total_spells = len(spells)
ritual_spells = sum(1 for s in spells.values() if isinstance(s, dict) and s.get('ritual', False))
concentration_spells = sum(1 for s in spells.values() if isinstance(s, dict) and s.get('concentration', False))
upcasting_spells = sum(1 for s in spells.values() if isinstance(s, dict) and 'higher level' in str(s.get('description', '')).lower())

print(f"Toplam spell: {total_spells}")
print(f"Ritual spell: {ritual_spells}")
print(f"Concentration spell: {concentration_spells}")
print(f"Upcasting spell (description'da): {upcasting_spells}")

# Component istatistikleri
has_material = sum(1 for s in spells.values() if isinstance(s, dict) and ('M' in str(s.get('components', '')) or 'material' in str(s.get('components', '')).lower()))
print(f"Material component: {has_material}")






