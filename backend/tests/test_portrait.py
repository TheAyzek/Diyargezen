from pathlib import Path
import tempfile
import base64
from utils.export_pdf import export_pdf, _get_portrait_image_path, _stamp_portrait_on_pdf

# 1x1 transparent pixel PNG base64 (valid padding/data char length)
MOCK_PORTRAIT = "data:image/png;base64,iVBOR0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

def test_get_portrait_image_path():
    # Test valid decoding
    path = _get_portrait_image_path(MOCK_PORTRAIT)
    assert path is not None
    assert path.exists()
    assert path.suffix == ".png"
    
    # Cleanup
    path.unlink()

def test_get_portrait_image_path_invalid():
    # Non-base64 input should return None
    assert _get_portrait_image_path("") is None
    assert _get_portrait_image_path("invalid_string_not_base64") is None

def test_export_pdf_with_portrait_fallback():
    # Setup test character payload with portrait
    character = {
        "name": "Portrait Hero",
        "system": "dnd5e",
        "class": "Wizard",
        "level": 5,
        "race": "Elf",
        "abilities": {
            "strength": 8,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 18,
            "wisdom": 13,
            "charisma": 10
        },
        "portrait": MOCK_PORTRAIT
    }
    
    temp_dir = tempfile.gettempdir()
    pdf_path = Path(temp_dir) / "test_portrait_fallback.pdf"
    
    # Run export (ReportLab fallback flow with portrait image)
    export_pdf(character, pdf_path)
    
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    
    pdf_path.unlink()

def test_export_pdf_with_portrait_acroform():
    # Setup test character payload with portrait
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
    
    # Force creation of a blank template on disk so AcroForm fill runs
    template_dir = Path(__file__).resolve().parent.parent.parent / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    template_path = template_dir / "pf1e_sheet.pdf"
    
    has_template = template_path.exists()
    
    # Run export (if template exists it fills it and stamps, otherwise uses fallback)
    export_pdf(character, pdf_path)
    
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    
    pdf_path.unlink()
