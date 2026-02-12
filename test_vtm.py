#!/usr/bin/env python3
"""
Test Vampire: The Masquerade Character Creation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from creators import CharacterFactory

def test_vtm():
    """Test VtM character creation"""
    print("=== Vampire: The Masquerade Test ===")
    
    try:
        # Create creator
        creator = CharacterFactory.create_creator("vtm5e")
        
        # Create character
        character = creator.create_character()
        
        print(f"✅ Karakter oluşturuldu:")
        print(f"   İsim: {character.get('name', 'N/A')}")
        print(f"   Sistem: {character.get('system', 'N/A')}")
        print(f"   Klan: {character.get('clan', 'N/A')}")
        print(f"   Predator Type: {character.get('predator_type', 'N/A')}")
        print(f"   Blood Potency: {character.get('blood_potency', 'N/A')}")
        print(f"   Humanity: {character.get('humanity', 'N/A')}")
        
        # Test attributes
        if 'attributes' in character:
            attrs = character['attributes']
            print(f"   Attributes:")
            for attr_type, values in attrs.items():
                print(f"     {attr_type}: {values}")
        
        # Test skills
        if 'skills' in character:
            skills = character['skills']
            print(f"   Skills:")
            for skill_type, values in skills.items():
                print(f"     {skill_type}: {values}")
        
        # Test disciplines
        if 'disciplines' in character:
            print(f"   Disciplines: {len(character['disciplines'])} adet")
            for disc in character['disciplines']:
                print(f"     - {disc}")
        
        # Save character
        filename = "test_vtm_character"
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
    test_vtm()
