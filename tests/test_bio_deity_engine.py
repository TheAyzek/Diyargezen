import pytest
from pathlib import Path

def test_deity_library_structure():
    """Verify PF1e Golarion deities library data in DeitySelectorModal.jsx."""
    deity_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "src" / "components" / "DeitySelectorModal.jsx"
    assert deity_path.exists()
    content = deity_path.read_text(encoding="utf-8")

    assert "PF1E_DEITIES" in content
    assert "Iomedae" in content
    assert "Sarenrae" in content
    assert "Desna" in content
    assert "Cayden Cailean" in content
    assert "Abadar" in content
    assert "Torag" in content
    assert "Nethys" in content
    assert "Pharasma" in content

def test_deity_favored_weapons_defined():
    """Verify deities have favored weapon assignments."""
    deity_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "src" / "components" / "DeitySelectorModal.jsx"
    content = deity_path.read_text(encoding="utf-8")

    assert "Longsword" in content
    assert "Scimitar" in content
    assert "Starknife" in content
    assert "Rapier" in content
    assert "Warhammer" in content
