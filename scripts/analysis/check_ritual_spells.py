"""
Ritual spell detection testi - Identify ve Find Familiar'ı kontrol et
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.calculations import is_ritual_spell

dnd_file = project_root / "data" / "dnd_data.json"
with open(dnd_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

spells = data.get('spells', {})

print("=" * 70)
print("RITUAL SPELL DETECTION TESTI")
print("=" * 70)
print()

test_spells = ['Identify', 'Find Familiar', 'Detect Magic', 'Magic Missile']

for spell_name in test_spells:
    spell_data = spells.get(spell_name)
    if not spell_data:
        print(f"{spell_name}: [BULUNAMADI]")
        continue
    
    print(f"{spell_name}:")
    print(f"  casting_time: {spell_data.get('casting_time', 'N/A')}")
    print(f"  components: {spell_data.get('components', 'N/A')}")
    print(f"  duration: {spell_data.get('duration', 'N/A')}")
    print(f"  ritual flag: {spell_data.get('ritual', 'N/A')}")
    
    description = spell_data.get('description', '')
    has_ritual_text = 'ritual' in description.lower() if description else False
    print(f"  description'da 'ritual' var mi: {has_ritual_text}")
    
    if has_ritual_text and len(description) > 0:
        # Ritual geçen kısmı göster
        import re
        ritual_match = re.search(r'.{0,100}ritual.{0,100}', description, re.IGNORECASE)
        if ritual_match:
            print(f"  Ritual context: ...{ritual_match.group(0)}...")
    
    # Fonksiyonu test et
    is_ritual = is_ritual_spell(spell_name, spell_data, data)
    expected = spell_name in ['Identify', 'Find Familiar', 'Detect Magic']
    status = "OK" if is_ritual == expected else "HATA"
    print(f"  is_ritual_spell() = {is_ritual} (expected: {expected}) [{status}]")
    print()


Ritual spell detection testi - Identify ve Find Familiar'ı kontrol et
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.calculations import is_ritual_spell

dnd_file = project_root / "data" / "dnd_data.json"
with open(dnd_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

spells = data.get('spells', {})

print("=" * 70)
print("RITUAL SPELL DETECTION TESTI")
print("=" * 70)
print()

test_spells = ['Identify', 'Find Familiar', 'Detect Magic', 'Magic Missile']

for spell_name in test_spells:
    spell_data = spells.get(spell_name)
    if not spell_data:
        print(f"{spell_name}: [BULUNAMADI]")
        continue
    
    print(f"{spell_name}:")
    print(f"  casting_time: {spell_data.get('casting_time', 'N/A')}")
    print(f"  components: {spell_data.get('components', 'N/A')}")
    print(f"  duration: {spell_data.get('duration', 'N/A')}")
    print(f"  ritual flag: {spell_data.get('ritual', 'N/A')}")
    
    description = spell_data.get('description', '')
    has_ritual_text = 'ritual' in description.lower() if description else False
    print(f"  description'da 'ritual' var mi: {has_ritual_text}")
    
    if has_ritual_text and len(description) > 0:
        # Ritual geçen kısmı göster
        import re
        ritual_match = re.search(r'.{0,100}ritual.{0,100}', description, re.IGNORECASE)
        if ritual_match:
            print(f"  Ritual context: ...{ritual_match.group(0)}...")
    
    # Fonksiyonu test et
    is_ritual = is_ritual_spell(spell_name, spell_data, data)
    expected = spell_name in ['Identify', 'Find Familiar', 'Detect Magic']
    status = "OK" if is_ritual == expected else "HATA"
    print(f"  is_ritual_spell() = {is_ritual} (expected: {expected}) [{status}]")
    print()




Ritual spell detection testi - Identify ve Find Familiar'ı kontrol et
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.calculations import is_ritual_spell

dnd_file = project_root / "data" / "dnd_data.json"
with open(dnd_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

spells = data.get('spells', {})

print("=" * 70)
print("RITUAL SPELL DETECTION TESTI")
print("=" * 70)
print()

test_spells = ['Identify', 'Find Familiar', 'Detect Magic', 'Magic Missile']

for spell_name in test_spells:
    spell_data = spells.get(spell_name)
    if not spell_data:
        print(f"{spell_name}: [BULUNAMADI]")
        continue
    
    print(f"{spell_name}:")
    print(f"  casting_time: {spell_data.get('casting_time', 'N/A')}")
    print(f"  components: {spell_data.get('components', 'N/A')}")
    print(f"  duration: {spell_data.get('duration', 'N/A')}")
    print(f"  ritual flag: {spell_data.get('ritual', 'N/A')}")
    
    description = spell_data.get('description', '')
    has_ritual_text = 'ritual' in description.lower() if description else False
    print(f"  description'da 'ritual' var mi: {has_ritual_text}")
    
    if has_ritual_text and len(description) > 0:
        # Ritual geçen kısmı göster
        import re
        ritual_match = re.search(r'.{0,100}ritual.{0,100}', description, re.IGNORECASE)
        if ritual_match:
            print(f"  Ritual context: ...{ritual_match.group(0)}...")
    
    # Fonksiyonu test et
    is_ritual = is_ritual_spell(spell_name, spell_data, data)
    expected = spell_name in ['Identify', 'Find Familiar', 'Detect Magic']
    status = "OK" if is_ritual == expected else "HATA"
    print(f"  is_ritual_spell() = {is_ritual} (expected: {expected}) [{status}]")
    print()


Ritual spell detection testi - Identify ve Find Familiar'ı kontrol et
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.calculations import is_ritual_spell

dnd_file = project_root / "data" / "dnd_data.json"
with open(dnd_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

spells = data.get('spells', {})

print("=" * 70)
print("RITUAL SPELL DETECTION TESTI")
print("=" * 70)
print()

test_spells = ['Identify', 'Find Familiar', 'Detect Magic', 'Magic Missile']

for spell_name in test_spells:
    spell_data = spells.get(spell_name)
    if not spell_data:
        print(f"{spell_name}: [BULUNAMADI]")
        continue
    
    print(f"{spell_name}:")
    print(f"  casting_time: {spell_data.get('casting_time', 'N/A')}")
    print(f"  components: {spell_data.get('components', 'N/A')}")
    print(f"  duration: {spell_data.get('duration', 'N/A')}")
    print(f"  ritual flag: {spell_data.get('ritual', 'N/A')}")
    
    description = spell_data.get('description', '')
    has_ritual_text = 'ritual' in description.lower() if description else False
    print(f"  description'da 'ritual' var mi: {has_ritual_text}")
    
    if has_ritual_text and len(description) > 0:
        # Ritual geçen kısmı göster
        import re
        ritual_match = re.search(r'.{0,100}ritual.{0,100}', description, re.IGNORECASE)
        if ritual_match:
            print(f"  Ritual context: ...{ritual_match.group(0)}...")
    
    # Fonksiyonu test et
    is_ritual = is_ritual_spell(spell_name, spell_data, data)
    expected = spell_name in ['Identify', 'Find Familiar', 'Detect Magic']
    status = "OK" if is_ritual == expected else "HATA"
    print(f"  is_ritual_spell() = {is_ritual} (expected: {expected}) [{status}]")
    print()








