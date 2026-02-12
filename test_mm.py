#!/usr/bin/env python3
"""
Test Mutants & Masterminds Character Creation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from creators import CharacterFactory

def test_mm():
    """Test M&M character creation"""
    print("=== Mutants & Masterminds Test ===")
    
    try:
        # Create creator
        creator = CharacterFactory.create_creator("mm3e")
        
        # Create character
        character = creator.create_character()
        
        print(f"✅ Karakter oluşturuldu:")
        print(f"   İsim: {character.get('name', 'N/A')}")
        print(f"   Sistem: {character.get('system', 'N/A')}")
        print(f"   Power Level: {character.get('power_level', 'N/A')}")
        print(f"   PL Value: {character.get('pl_value', 'N/A')}")
        print(f"   Kalan PP: {character.get('remaining_power_points', 'N/A')}")
        
        # Test powers
        if 'powers' in character:
            print(f"   Powers: {len(character['powers'])} adet")
            for power in character['powers'][:3]:  # Show first 3
                print(f"     - {power}")
        
        # Test advantages
        if 'advantages' in character:
            print(f"   Advantages: {len(character['advantages'])} adet")
        
        # Save character
        filename = "test_mm_character"
        if creator.save_character(character, filename):
            print(f"✅ Karakter kaydedildi: {filename}.json")
            return True
        else:
            print("❌ Karakter kaydedilemedi")
            return False
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    test_mm()
