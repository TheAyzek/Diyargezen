from pathlib import Path
import tempfile
from pypdf import PdfReader
from utils.export_pdf import export_pdf, _get_portrait_image_path

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
    
    # Run export
    export_pdf(character, pdf_path)
    
    # Assert
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    
    # Cleanup
    pdf_path.unlink()


def test_export_pdf_pf1e_character():
    """Test exporting a full Pathfinder 1st Edition character payload."""
    character = {
        "name": "Valeros the Brave",
        "system": "pathfinder1e",
        "class": "Fighter",
        "level": 5,
        "race": "Human",
        "alignment": "Neutral Good",
        "deity": "Iomedae",
        "abilities": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 10
        },
        "saving_throws": {
            "Fortitude": 6,
            "Reflex": 3,
            "Will": 2
        },
        "skills": {
            "Climb": 7,
            "Intimidate": 5,
            "Swim": 6
        },
        "hit_points": 44,
        "armor_class": 19,
        "base_attack_bonus": 5,
        "cmd": 20,
        "cmb": 8,
        "initiative": 2,
        "total_weight": 55.0,
        "inventory": [
            {"name": "Longsword +1", "type": "Weapon", "quantity": 1, "weight": 4.0},
            {"name": "Breastplate", "type": "Armor", "quantity": 1, "weight": 30.0}
        ],
        "traits": ["Reactionary", "Armor Expert"],
        "feats": ["Power Attack", "Weapon Focus (Longsword)", "Toughness"]
    }

    temp_dir = tempfile.gettempdir()
    pdf_path = Path(temp_dir) / "test_pf1e_character_sheet.pdf"

    export_pdf(character, pdf_path)

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 500

    reader = PdfReader(pdf_path)
    assert len(reader.pages) >= 1

    pdf_path.unlink()


def test_export_pdf_with_portrait():
    """Test PDF export with base64 portrait image stamping."""
    tiny_base64_png = (
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )
    
    # Verify portrait decoder helper
    portrait_file = _get_portrait_image_path(tiny_base64_png)
    assert portrait_file is not None
    assert portrait_file.exists()

    character = {
        "name": "Seoni",
        "system": "pathfinder1e",
        "class": "Sorcerer",
        "level": 4,
        "race": "Human",
        "portrait": tiny_base64_png,
        "abilities": {
            "strength": 8, "dexterity": 14, "constitution": 12,
            "intelligence": 12, "wisdom": 10, "charisma": 18
        },
        "hit_points": 22,
        "armor_class": 12,
    }

    temp_dir = tempfile.gettempdir()
    pdf_path = Path(temp_dir) / "test_portrait_character.pdf"

    export_pdf(character, pdf_path)

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 500

    pdf_path.unlink()
    if portrait_file.exists():
        portrait_file.unlink()
