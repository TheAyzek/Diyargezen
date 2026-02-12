#!/usr/bin/env python3
"""
Test Pathfinder 1e Character Creation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from creators import CharacterFactory

def test_pathfinder():
    """Test Pathfinder character creation"""
    print("=== Pathfinder 1e Test ===")
    
    try:
        # Create creator
        creator = CharacterFactory.create_creator("pathfinder1e")
        
        # Create character with automatic selections for testing
        character = creator.create_character()
        
        print(f"✅ Karakter oluşturuldu:")
        print(f"   İsim: {character.get('name', 'N/A')}")
        print(f"   Irk: {character.get('race', 'N/A')}")
        print(f"   Sınıf: {character.get('class', 'N/A')}")
        print(f"   Seviye: {character.get('level', 'N/A')}")
        print(f"   BAB: {character.get('bab', 'N/A')}")
        print(f"   Saves: {character.get('saves', 'N/A')}")
        
        # Test feat selection
        if 'feats' in character:
            print(f"   Feats: {len(character['feats'])} adet")
            for feat in character['feats'][:3]:  # Show first 3
                print(f"     - {feat}")
        
        # Save character
        filename = "test_pathfinder_character"
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
    test_pathfinder()
