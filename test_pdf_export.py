#!/usr/bin/env python3
"""
Test PDF Export for All Systems
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from creators import CharacterFactory
from utils.export_pdf import (
    export_dnd_character_pdf,
    export_mm_character_pdf, 
    export_vtm_character_pdf
)
from pathlib import Path

def test_pdf_export():
    """Test PDF export for all systems"""
    print("=== PDF Export Test - Tüm Sistemler ===")
    
    systems = [
        ("dnd5e", "D&D 5e"),
        ("pathfinder1e", "Pathfinder 1e"),
        ("mm3e", "Mutants & Masterminds"),
        ("vtm5e", "Vampire: The Masquerade")
    ]
    
    results = {}
    
    for system_key, system_name in systems:
        print(f"\n--- {system_name} PDF Export Test ---")
        
        try:
            # Create character
            creator = CharacterFactory.create_creator(system_key)
            character = creator.create_character()
            
            # Test PDF export
            filename = Path(f"test_{system_key}_character.pdf")
            
            try:
                if system_key == "dnd5e":
                    export_dnd_character_pdf(character, filename)
                elif system_key == "mm3e":
                    export_mm_character_pdf(character, filename)
                elif system_key == "vtm5e":
                    export_vtm_character_pdf(character, filename)
                elif system_key == "pathfinder1e":
                    # Use D&D export for Pathfinder as fallback
                    export_dnd_character_pdf(character, filename)
                
                print(f"✅ {system_name}: PDF başarıyla oluşturuldu - {filename}")
                results[system_name] = "✅ Başarılı"
            except Exception as export_error:
                print(f"❌ {system_name}: PDF oluşturulamadı - {export_error}")
                results[system_name] = f"❌ Export Hatası: {export_error}"
                
        except Exception as e:
            print(f"❌ {system_name}: Hata - {e}")
            results[system_name] = f"❌ Hata: {e}"
    
    # Summary
    print("\n=== PDF Export Özeti ===")
    for system_name, result in results.items():
        print(f"{system_name}: {result}")
    
    # Check if all successful
    success_count = sum(1 for r in results.values() if "✅" in r)
    total_count = len(results)
    
    print(f"\nSonuç: {success_count}/{total_count} sistemde PDF export başarılı")
    
    return success_count == total_count

if __name__ == "__main__":
    test_pdf_export()
