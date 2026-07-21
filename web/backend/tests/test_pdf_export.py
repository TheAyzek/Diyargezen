from pathlib import Path
import tempfile
from utils.export_pdf import export_pdf

def test_export_pdf_fallback():
    # Setup test character payload
    character = {
        "name": "Test Hero",
        "system": "dnd5e",
        "class": "Cleric",
        "level": 3,
        "race": "Dwarf",
        "abilities": {
            "strength": 14,
            "dexterity": 10,
            "constitution": 15,
            "intelligence": 10,
            "wisdom": 16,
            "charisma": 8
        },
        "saving_throws": {
            "Strength": 2,
            "Dexterity": 0,
            "Constitution": 4,
            "Intelligence": 0,
            "Wisdom": 5,
            "Charisma": 1
        },
        "skills": {
            "Acrobatics": 0,
            "Perception": 5,
            "History": 2
        },
        "hit_points": 24,
        "armor_class": 16,
        "initiative": 0,
        "total_weight": 45.5,
        "encumbrance_status": "Light",
        "spell_slots": {
            "1": 4,
            "2": 2
        },
        "feats": ["Toughness"]
    }
    
    # Path to temp PDF
    temp_dir = tempfile.gettempdir()
    pdf_path = Path(temp_dir) / "test_character_sheet.pdf"
    
    # Run export (will use ReportLab fallback since assets/templates/*.pdf won't exist in tests)
    export_pdf(character, pdf_path)
    
    # Assert
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    
    # Cleanup
    pdf_path.unlink()
