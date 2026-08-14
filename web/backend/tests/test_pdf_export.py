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


def test_export_pdf_pf1e_inventory_and_weapon_cards():
    """Test exporting PF1e character with inventory item weights, carrying capacity, AC breakdown, and weapon cards."""
    from rules.calculators import PF1e_Calculator
    
    raw_character = {
        "name": "Kyra the Cleric",
        "system": "pathfinder1e",
        "class": "Cleric",
        "level": 3,
        "race": "Human",
        "abilities": {"strength": 14, "dexterity": 10, "constitution": 14, "intelligence": 10, "wisdom": 16, "charisma": 12},
        "equipment": [
            {"name": "Scimitar +1", "type": "Weapon", "quantity": 1, "weight": 4.0},
            {"name": "Chainmail", "type": "Armor", "quantity": 1, "weight": 40.0},
            {"name": "Heavy Steel Shield", "type": "Shield", "quantity": 1, "weight": 15.0}
        ],
        "armor_bonus": 6,
        "shield_bonus": 2
    }
    
    # Run calculator
    calc = PF1e_Calculator()
    recalced = calc.update_all_stats(raw_character)
    raw_character.update(recalced)
    raw_character["derived"] = recalced
    
    temp_dir = tempfile.gettempdir()
    pdf_path = Path(temp_dir) / "test_pf1e_weapons_inventory.pdf"

    export_pdf(raw_character, pdf_path)

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 500

    reader = PdfReader(pdf_path)
    fields = reader.get_fields() or {}

    # Verify form values populated
    assert fields.get("Item 1", {}).get("/V") == "Scimitar +1"
    assert fields.get("WT 1", {}).get("/V") == "4.0"
    assert fields.get("TOTAL WEIGHT", {}).get("/V") == "59.0"
    assert fields.get("Light", {}).get("/V") in ("76", "76.0", "76.7", "58", "58.0", "58.3")
    assert fields.get("armor class", {}).get("/V") == "18"
    assert fields.get("TOUCH", {}).get("/V") == "10"
    assert fields.get("FLATFOOTED", {}).get("/V") == "18"

    # Weapon cards
    assert fields.get("Weapon 1", {}).get("/V") == "Scimitar +1"
    assert fields.get("Bonus 1", {}).get("/V") == "+6"
    assert fields.get("Damage 1", {}).get("/V") == "1d6 + 4"

    pdf_path.unlink()

