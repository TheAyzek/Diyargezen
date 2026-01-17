#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M&M entegrasyonunu test et"""

import sys
import io
from pathlib import Path
import json

# Windows konsol encoding hatası için
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Veri dosyasını yükle
data_file = project_root / "data" / "mm_data.json"

print("=" * 70)
print("MUTANTS & MASTERMINDS ENTEGRASYON TESTİ")
print("=" * 70)
print()

if not data_file.exists():
    print("❌ M&M veri dosyası bulunamadı!")
    sys.exit(1)

with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("✅ Veri dosyası yüklendi")
print()

# 1. Veri Yapısı Testi
print("1️⃣  VERİ YAPISI TESTİ")
print("-" * 70)

required_keys = ['system', 'source', 'abilities', 'archetypes', 'skills', 'advantages', 'powers', 'power_effects', 'power_levels']
missing_keys = [key for key in required_keys if key not in data]
if missing_keys:
    print(f"❌ Eksik anahtarlar: {missing_keys}")
else:
    print("✅ Tüm gerekli anahtarlar mevcut")

print(f"   - System: {data.get('system')}")
print(f"   - Source: {data.get('source')}")
print()

# 2. Abilities Testi
print("2️⃣  ABILITIES TESTİ")
print("-" * 70)
abilities = data.get('abilities', {})
required_abilities = ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]
missing_abilities = [ab for ab in required_abilities if ab not in abilities]
if missing_abilities:
    print(f"❌ Eksik abilities: {missing_abilities}")
else:
    print(f"✅ Tüm {len(abilities)} ability mevcut")

# Açıklamaları kontrol et
empty_descriptions = [name for name, ab_data in abilities.items() if not ab_data.get('description') or 'core abilities' in ab_data.get('description', '').lower()]
if empty_descriptions:
    print(f"⚠️  Eksik açıklamalı abilities: {empty_descriptions}")
else:
    print("✅ Tüm abilities açıklamaları mevcut")

print()

# 3. Archetypes Testi
print("3️⃣  ARCHETYPES TESTİ")
print("-" * 70)
archetypes = data.get('archetypes', {})
print(f"✅ {len(archetypes)} archetype mevcut")

# Suggested powers/advantages/skills kontrolü
sample_archetype = list(archetypes.values())[0] if archetypes else None
if sample_archetype:
    suggested_powers = len(sample_archetype.get('suggested_powers', []))
    suggested_advantages = len(sample_archetype.get('suggested_advantages', []))
    suggested_skills = len(sample_archetype.get('suggested_skills', []))
    
    print(f"   Örnek Archetype ({sample_archetype.get('name')}):")
    print(f"     - Suggested Powers: {suggested_powers}")
    print(f"     - Suggested Advantages: {suggested_advantages}")
    print(f"     - Suggested Skills: {suggested_skills}")
    
    if suggested_powers == 0:
        print("   ⚠️  Suggested Powers boş!")
    if suggested_advantages == 0:
        print("   ⚠️  Suggested Advantages boş!")
    if suggested_skills == 0:
        print("   ⚠️  Suggested Skills boş!")

print()

# 4. Skills Testi
print("4️⃣  SKILLS TESTİ")
print("-" * 70)
skills = data.get('skills', {})
print(f"✅ {len(skills)} skill mevcut")
if len(skills) > 0:
    sample_skill = list(skills.values())[0]
    print(f"   Örnek Skill: {sample_skill.get('name')} (Key Ability: {sample_skill.get('key_ability', 'N/A')})")
print()

# 5. Advantages Testi
print("5️⃣  ADVANTAGES TESTİ")
print("-" * 70)
advantages = data.get('advantages', {})
print(f"✅ {len(advantages)} advantage mevcut")
if len(advantages) > 0:
    sample_advantage = list(advantages.values())[0]
    print(f"   Örnek Advantage: {sample_advantage.get('name')} (Cost: {sample_advantage.get('cost', 'N/A')})")
print()

# 6. Powers Testi
print("6️⃣  POWERS TESTİ")
print("-" * 70)
powers = data.get('powers', {})
print(f"✅ {len(powers)} power mevcut")
if len(powers) > 0:
    sample_power = list(powers.values())[0]
    print(f"   Örnek Power: {sample_power.get('name')} (Cost: {sample_power.get('cost_per_rank', 'N/A')}/rank)")
print()

# 7. Power Effects Testi
print("7️⃣  POWER EFFECTS TESTİ")
print("-" * 70)
power_effects = data.get('power_effects', {})
print(f"✅ {len(power_effects)} power effect mevcut")
if len(power_effects) < 10:
    print(f"   ⚠️  Power Effects sayısı düşük ({len(power_effects)}), daha fazla effect çekilmeli")
if len(power_effects) > 0:
    sample_effect = list(power_effects.values())[0]
    print(f"   Örnek Effect: {sample_effect.get('name')} (Category: {sample_effect.get('category', 'N/A')})")
print()

# 8. Power Levels Testi
print("8️⃣  POWER LEVELS TESTİ")
print("-" * 70)
power_levels = data.get('power_levels', {})
print(f"✅ {len(power_levels)} power level mevcut")
for pl_name, pl_data in power_levels.items():
    print(f"   {pl_name}: Attack={pl_data.get('attack_bonus_cap')}, Defense={pl_data.get('defense_cap')}")
print()

# 9. Data Loader Testi
print("9️⃣  DATA LOADER TESTİ")
print("-" * 70)
try:
    from utils.data_loader import load_mm_data
    loaded_data = load_mm_data(project_root)
    if loaded_data:
        print("✅ Data loader çalışıyor")
        print(f"   Yüklenen abilities: {len(loaded_data.get('abilities', {}))}")
        print(f"   Yüklenen archetypes: {len(loaded_data.get('archetypes', {}))}")
    else:
        print("❌ Data loader boş veri döndürdü")
except Exception as e:
    print(f"❌ Data loader hatası: {e}")
    import traceback
    traceback.print_exc()

print()

# 10. GUI Testi (Basit)
print("🔟 GUI ENTEGRASYON TESTİ")
print("-" * 70)
try:
    from PySide6.QtWidgets import QApplication
    from gui.app import MmPage
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    print("✅ QApplication oluşturuldu")
    
    mm_page = MmPage()
    print("✅ MmPage oluşturuldu")
    
    # Veri kontrolü
    if hasattr(mm_page, 'data'):
        if mm_page.data:
            print("✅ MmPage verisi yüklendi")
            print(f"   - Archetypes: {len(mm_page.data.get('archetypes', {}))}")
            print(f"   - Abilities: {len(mm_page.data.get('abilities', {}))}")
        else:
            print("❌ MmPage verisi boş")
    else:
        print("⚠️  MmPage'de data özelliği yok")
    
except Exception as e:
    print(f"⚠️  GUI testi hatası (beklenen, headless mode): {e}")

print()
print("=" * 70)
print("TEST TAMAMLANDI")
print("=" * 70)

