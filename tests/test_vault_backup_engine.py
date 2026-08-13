import json
import pytest
from pathlib import Path

def test_vault_backup_schema_structure():
    """Verify Full Vault Backup JSON schema structure in jsonExportUtil.js."""
    export_util_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "src" / "utils" / "jsonExportUtil.js"
    assert export_util_path.exists()
    content = export_util_path.read_text(encoding="utf-8")

    assert "exportFullVaultBackup" in content
    assert "importFullVaultBackup" in content
    assert "app_name: 'Diyargezen'" in content or 'app_name: "Diyargezen"' in content
    assert "app_version: '2.0.0'" in content or 'app_version: "2.0.0"' in content
    assert "system: 'pathfinder1e'" in content or 'system: "pathfinder1e"' in content

def test_vault_backup_mock_parsing():
    """Test Python representation of full vault backup JSON schema."""
    mock_vault = {
        "app_name": "Diyargezen",
        "app_version": "2.0.0",
        "system": "pathfinder1e",
        "exported_at": "2026-08-13T14:00:00Z",
        "character_count": 2,
        "characters": [
            {"id": "char-1", "name": "Valeros", "system": "pathfinder1e", "level": 5},
            {"id": "char-2", "name": "Ezren", "system": "pathfinder1e", "level": 5}
        ]
    }

    raw_json = json.dumps(mock_vault)
    parsed = json.loads(raw_json)

    assert parsed["app_name"] == "Diyargezen"
    assert parsed["app_version"] == "2.0.0"
    assert parsed["character_count"] == 2
    assert len(parsed["characters"]) == 2
    assert parsed["characters"][0]["name"] == "Valeros"
