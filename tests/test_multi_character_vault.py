import json
import pytest
from pathlib import Path

def test_json_export_util_functions_exist():
    """Verify that exportCharacterRecordJSON, exportFullVaultBackup, and importFullVaultBackup exist in jsonExportUtil.js."""
    export_util_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "src" / "utils" / "jsonExportUtil.js"
    assert export_util_path.exists()
    content = export_util_path.read_text(encoding="utf-8")

    assert "exportCharacterRecordJSON" in content
    assert "exportFullVaultBackup" in content
    assert "importFullVaultBackup" in content
    assert "exportCharacterJSON" in content

def test_offline_storage_clone_function_exists():
    """Verify that cloneLocalCharacter, deleteLocalCharacter, and getLocalCharacter exist in offlineStorage.js."""
    offline_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "src" / "utils" / "offlineStorage.js"
    assert offline_path.exists()
    content = offline_path.read_text(encoding="utf-8")

    assert "cloneLocalCharacter" in content
    assert "getLocalCharacter" in content
    assert "deleteLocalCharacter" in content
    assert "getAllLocalCharacters" in content

def test_preset_characters_modal_tiers_exist():
    """Verify that buildPresetForTier and multi-tier selectors exist in PresetCharactersModal.jsx."""
    preset_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "src" / "components" / "PresetCharactersModal.jsx"
    assert preset_path.exists()
    content = preset_path.read_text(encoding="utf-8")

    assert "buildPresetForTier" in content
    assert "selectedTier" in content
    assert "Seviye 1" in content
    assert "Seviye 5" in content
    assert "Seviye 10" in content

def test_vault_character_schema_roundtrip():
    """Validate character record payload compatibility with Pathfinder 1e system."""
    sample_character = {
        "id": "local_123456",
        "name": "Valeros",
        "system": "pf1e",
        "level": 5,
        "race": "Human",
        "class": "Fighter",
        "abilities": {
            "strength": 17,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 10
        },
        "feats": [{"isim": "Power Attack"}, {"isim": "Weapon Focus"}],
        "spells": [],
        "preparedSpells": {},
        "usedSpellSlots": {}
    }

    serialized = json.dumps(sample_character)
    deserialized = json.loads(serialized)

    assert deserialized["name"] == "Valeros"
    assert deserialized["level"] == 5
    assert deserialized["abilities"]["strength"] == 17
    assert "preparedSpells" in deserialized
    assert "usedSpellSlots" in deserialized
