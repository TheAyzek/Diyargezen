from pathlib import Path
import tempfile
import base64
from utils.export_pdf import export_pdf, _get_portrait_image_path, _stamp_portrait_on_pdf

# Valid 1x1 PNG base64
MOCK_PORTRAIT = "data:image/png;base64,iVBOR0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

def test_get_portrait_image_path():
    path = _get_portrait_image_path(MOCK_PORTRAIT)
    assert path is not None
    assert path.exists()
    assert path.suffix == ".png"
    path.unlink()

def test_get_portrait_image_path_invalid():
    assert _get_portrait_image_path("") is None
    assert _get_portrait_image_path("invalid_string_not_base64") is None

def test_export_pdf_with_portrait_acroform():
    character = {
        "name": "AcroForm Hero",
        "system": "pf1e",
        "class": "Fighter",
        "level": 1,
        "race": "Human",
        "abilities": {
            "strength": 15,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 8
        },
        "portrait": MOCK_PORTRAIT
    }
    
    temp_dir = tempfile.gettempdir()
    pdf_path = Path(temp_dir) / "test_portrait_acroform.pdf"
    
    export_pdf(character, pdf_path)
    
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    
    if pdf_path.exists():
        pdf_path.unlink()
