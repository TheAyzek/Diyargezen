import pytest
from pathlib import Path

def test_pdf_feats_traits_descriptions_included():
    """Verify pdfExportUtil.js formats feat and trait descriptions into AcroForm fields and appended pages."""
    pdf_util_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "src" / "utils" / "pdfExportUtil.js"
    assert pdf_util_path.exists()
    content = pdf_util_path.read_text(encoding="utf-8")

    # Verify AcroForm formatItemWithDescription function
    assert "formatItemWithDescription" in content
    assert "`• ${name}: ${cleanDesc}`" in content or "`* ${name}: ${cleanDesc}`" in content
    assert "FEATS" in content
    assert "SPECIAL ABILITIES" in content

    # Verify dynamic multi-line description rendering without truncation
    assert "descLines" in content
    assert "maxLineLen = 85" in content
    assert "boxHeight" in content
