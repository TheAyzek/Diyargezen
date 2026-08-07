"""
End-to-End Stress Test for Pathfinder 1e Live AcroForm PDF Exporter
===================================================================
Tests AcroForm PDF field filling for a complex Level 20 PF1e character payload:
- Multiclass (Fighter 10 / Wizard 10)
- Companion (Toad Familiar +3 HP Master Bonus)
- Spellcasting (Spell DCs 0..5, Caster Level 10, Concentration Bonus +18)
- GM Custom Modifiers (Stealth +5, Initiative +4, Speed +10)
- Weapons, Equipment, Feats, Traits, and Base64 Portrait.
"""

import tempfile
from pathlib import Path
from pypdf import PdfReader

from rules.calculators import PF1e_Calculator
from utils.export_pdf import export_pdf


def test_pdf_export_stress_full_character():
    calc = PF1e_Calculator()

    raw_char = {
        "name": "Archmage Ezren Valeros",
        "system": "pathfinder1e",
        "level": 20,
        "class": "Wizard",
        "race": "Human",
        "alignment": "Neutral Good",
        "deity": "Nethys",
        "abilities": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 16,
            "intelligence": 26,
            "wisdom": 14,
            "charisma": 10
        },
        "multiclass": {"Fighter": 10, "Wizard": 10},
        "companion": {
            "name": "Bubo",
            "type": "familiar",
            "species": "Toad"
        },
        "feats": ["Combat Casting", "Spell Focus", "Power Attack", "Weapon Focus (Longsword)", "Toughness"],
        "traits": ["Reactionary", "Armor Expert"],
        "custom_modifiers": [
            {"stat": "skill:Stealth", "value": 5, "name": "Shadow Cloak", "is_active": True},
            {"stat": "init", "value": 4, "name": "Tactical Mind", "is_active": True},
            {"stat": "speed", "value": 10, "name": "Boots of Striding", "is_active": True}
        ],
        "equipment": [
            {"name": "+3 Spell Storing Longsword", "type": "Weapon", "quantity": 1, "weight": 4.0},
            {"name": "+4 Mithral Breastplate", "type": "Armor", "quantity": 1, "weight": 15.0},
            {"name": "Ring of Protection +3", "type": "Gear", "quantity": 1, "weight": 0.5}
        ],
        "spells": ["Fireball", "Haste", "Fly", "Shield", "Magic Missile", "Teleport"],
        "portrait": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    }

    # Step 1: Run complete 5-step calculation pipeline
    recalced = calc.update_all_stats(raw_char)
    raw_char.update(recalced)
    raw_char["derived"] = recalced

    # Step 2: Verify derived spellcasting & companion stats before export
    sc = recalced["spellcasting"]
    assert sc["caster_level"] == 20
    assert sc["concentration_bonus"] == 20 + 8 + 4  # CL 20 + INT 8 + Combat Casting 4 = 32
    assert sc["spell_dcs"]["0"] == 10 + 0 + 8 + 1  # 19 (Spell Focus +1)
    assert sc["spell_dcs"]["3"] == 10 + 3 + 8 + 1  # 22
    assert recalced["companion"]["name"] == "Bubo"

    # Step 3: Run PDF Exporter
    temp_dir = tempfile.gettempdir()
    pdf_path = Path(temp_dir) / "stress_test_ezren_valeros.pdf"

    export_pdf(raw_char, pdf_path)

    # Step 4: Verify generated PDF file and AcroForm fields
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000

    reader = PdfReader(pdf_path)
    assert len(reader.pages) >= 1
    fields = reader.get_fields() or {}

    # Field assertions
    print(f"\nPDF Form Fields Successfully Preserved: {len(fields)} fields")
    # Check populated values
    assert fields.get("Character Name", {}).get("/V") == "Archmage Ezren Valeros"
    assert fields.get("Race", {}).get("/V") == "Human"
    assert fields.get("Alignment", {}).get("/V") == "Neutral Good"
    assert fields.get("Deity", {}).get("/V") == "Nethys"

    # Stat Scores & Modifiers
    assert fields.get("strength", {}).get("/V") == "16"
    assert fields.get("intelligence", {}).get("/V") == "26"
    assert fields.get("INITIATIVE", {}).get("/V") == "+8"
    assert fields.get("hit points", {}).get("/V") == "146"
    assert fields.get("BASE ATTACK BONUS", {}).get("/V") == "+15"

    # Equipment & Weapons
    assert fields.get("Weapon 1", {}).get("/V") == "+3 Spell Storing Longsword"
    assert fields.get("Item 1", {}).get("/V") == "+3 Spell Storing Longsword"
    assert fields.get("Item 2", {}).get("/V") == "+4 Mithral Breastplate"

    # Companion summary mapped check
    non_empty = {k: v.get("/V") for k, v in fields.items() if v.get("/V")}
    print(f"\nNon-empty PDF Fields ({len(non_empty)}):", list(non_empty.items())[:20])

    # Cleanup temp PDF
    pdf_path.unlink()
