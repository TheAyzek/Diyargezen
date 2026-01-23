from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# This module provides minimal PDF template helpers. The original file
# contained large embedded natural-language blocks and markdown that
# broke Python syntax. To allow static analysis and incremental fixes,
# we replace it with a compact, syntactically-correct implementation
# that preserves the public functions used elsewhere.

try:
    # Optional: use reportlab if installed for proper PDF output.
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
    from reportlab.lib.styles import ParagraphStyle
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def _register_turkish_font_for_template() -> str:
    """Return a font name to use in templates. Falls back to a standard font.

    This is intentionally simple so the module remains importable even
    when reportlab or custom fonts are not available.
    """
    return "Helvetica"


def _create_styles(font_name: str, color_scheme: str = "default") -> Dict[str, Any]:
    """Return a minimal styles mapping used by template builders.

    When reportlab is available this returns simple ParagraphStyle placeholders;
    otherwise returns a dict of strings to avoid import errors elsewhere.
    """
    if REPORTLAB_AVAILABLE:
        base = ParagraphStyle("base", fontName=font_name, fontSize=10)
        return {
            "title": ParagraphStyle("title", parent=base, fontSize=14, leading=16),
            "heading": ParagraphStyle("heading", parent=base, fontSize=11, leading=13),
            "normal": base,
            "bold": ParagraphStyle("bold", parent=base, fontName=font_name),
        }
    return {"title": "title", "heading": "heading", "normal": "normal", "bold": "bold"}


def _build_standard_template(character: dict, styles: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> List[Any]:
    """Build a minimal 'standard' template representation.

    If reportlab is available this returns a list of flowables; otherwise
    returns a list of strings describing the content.
    """
    if REPORTLAB_AVAILABLE:
        story = []
        story.append(Paragraph(f"Name: {character.get('name', 'Unknown')}", styles.get("title")))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"Class: {character.get('class', '')} - Level {character.get('level', 1)}", styles.get("normal")))
        story.append(Spacer(1, 0.2 * cm))
        return story

    # Fallback: simple list of strings
    return [f"Name: {character.get('name', 'Unknown')}", f"Class: {character.get('class', '')} - Level {character.get('level', 1)}"]


def _build_compact_template(character: dict, styles: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> List[Any]:
    # For now compact == standard
    return _build_standard_template(character, styles, options)


def _build_detailed_template(character: dict, styles: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> List[Any]:
    # For now detailed == standard with extra lines
    base = _build_standard_template(character, styles, options)
    if REPORTLAB_AVAILABLE:
        base.append(Spacer(1, 0.1 * cm))
        base.append(Paragraph("(Detailed view placeholder)", styles.get("normal")))
        return base
    base.append("(Detailed view placeholder)")
    return base


def _create_spell_table(spell_name: str, spell_data: dict, styles: Dict[str, Any], dnd_data: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Any], str]:
    """Return a (table, description) tuple. Table may be a reportlab Table or None in fallback.

    This keeps the function signature used elsewhere without implementing complex layout.
    """
    description = spell_data.get("description", "No description")
    if REPORTLAB_AVAILABLE:
        rows = [["Property", "Value"], ["Level", str(spell_data.get("level", 0))], ["Name", spell_name]]
        table = Table(rows)
        return table, description
    return None, description


def export_dnd_character_pdf_improved(character: dict, output_path: Path, template: str = "standard", page_size: str = "A4", options: Optional[Dict[str, Any]] = None) -> None:
    """Export a character to PDF (best-effort).

    If reportlab is not available this writes a plain-text fallback file
    with the same base name and a .txt extension so callers still get an output.
    """
    styles = _create_styles(_register_turkish_font_for_template(), color_scheme=(options or {}).get("color_scheme", "default"))
    if template == "compact":
        story = _build_compact_template(character, styles, options)
    elif template == "detailed":
        story = _build_detailed_template(character, styles, options)
    else:
        story = _build_standard_template(character, styles, options)

    if REPORTLAB_AVAILABLE:
        size = A4 if page_size.upper() == "A4" else letter
        doc = SimpleDocTemplate(str(output_path), pagesize=size, rightMargin=1 * cm, leftMargin=1 * cm, topMargin=1 * cm, bottomMargin=1 * cm)
        doc.build(list(story))
        return

    # Fallback: write a simple text file
    txt_path = Path(str(output_path) + ".txt")
    with txt_path.open("w", encoding="utf-8") as f:
        for item in story:
            f.write(str(item) + "\n")


def export_dnd_spell_sheet_pdf(character: dict, output_path: Path, dnd_data: Optional[Dict[str, Any]] = None, page_size: str = "A4") -> None:
    """Export a simple spell sheet. Uses `_create_spell_table` for structure."""
    styles = _create_styles(_register_turkish_font_for_template())
    spells = character.get("spells", {})
    story = []
    # Add a heading per spell level
    for level_key, spells_list in spells.items():
        story.append(f"Level: {level_key}")
        for spell_name in (spells_list or []):
            table, desc = _create_spell_table(spell_name, {"level": 0, "name": spell_name}, styles, dnd_data)
            story.append(spell_name)
            if desc:
                story.append(desc)

    if REPORTLAB_AVAILABLE:
        size = A4 if page_size.upper() == "A4" else letter
        doc = SimpleDocTemplate(str(output_path), pagesize=size, rightMargin=1 * cm, leftMargin=1 * cm, topMargin=1 * cm, bottomMargin=1 * cm)
        # convert non-flowables to Paragraphs if needed
        flowables = []
        for item in story:
            if isinstance(item, str):
                flowables.append(Paragraph(item, styles.get("normal")))
            else:
                flowables.append(item)
        doc.build(flowables)
        return

    txt_path = Path(str(output_path) + ".txt")
    with txt_path.open("w", encoding="utf-8") as f:
        for item in story:
            f.write(str(item) + "\n")

