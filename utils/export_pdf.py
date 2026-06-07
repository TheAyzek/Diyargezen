from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)


def inspect_pdf_fields(template_path: Path) -> List[str]:
    """Inspects a PDF file and returns list of interactive form field names.
    Prints all field names to terminal.
    """
    if not template_path.exists():
        logger.warning(f"File not found: {template_path}")
        return []
    try:
        reader = PdfReader(template_path)
        fields = reader.get_fields()
        if fields:
            names = list(fields.keys())
            print(f"\n--- PDF FORM FIELDS FOR {template_path.name} ---")
            for name in sorted(names):
                print(f"  Field: {name}")
            return names
        print(f"No fields found in {template_path.name}")
    except Exception as e:
        logger.error(f"Error inspecting PDF fields: {e}")
    return []


def get_ability(char: dict, name: str, default: int = 10) -> int:
    abilities = char.get("abilities", {})
    for k, v in abilities.items():
        if k.lower() == name.lower():
            try:
                return int(v)
            except:
                pass
    # default to 0 for MM3e stamina/presence etc if not found
    if name.lower() in ("stamina", "fighting", "intellect", "awareness", "presence"):
        return 0
    return default


def get_modifier(char: dict, name: str, default: int = 0) -> int:
    score = get_ability(char, name, default=10)
    return (score - 10) // 2


def format_mod(val: int) -> str:
    try:
        val = int(val)
        return f"{val:+d}" if val >= 0 else f"{val:d}"
    except (ValueError, TypeError):
        return str(val)


# Mapping dictionaries for systems with placeholder mappings
PDF_MAPPINGS = {
    "dnd5e": {
        # Ortak Başlık & RPG Detayları
        "CharacterName": lambda c: c.get("name", ""),
        "CharacterName 2": lambda c: c.get("name", ""),
        "ClassLevel": lambda c: f"{c.get('class', '')} {c.get('level', 1)}",
        "Race ": lambda c: c.get("race", ""),
        "Background": lambda c: c.get("background", ""),
        "PlayerName": lambda c: "Diyargezen",
        "Alignment": lambda c: c.get("alignment", ""),
        "XP": lambda c: str(c.get("experience", 0)),
        "Age": lambda c: str(c.get("age", "")),
        "Deity": lambda c: c.get("deity", ""),
        
        # Statlar & Savaş
        "STR": lambda c: str(get_ability(c, "strength")),
        "STRmod": lambda c: format_mod(get_modifier(c, "strength")),
        "DEX": lambda c: str(get_ability(c, "dexterity")),
        "DEXmod ": lambda c: format_mod(get_modifier(c, "dexterity")),
        "CON": lambda c: str(get_ability(c, "constitution")),
        "CONmod": lambda c: format_mod(get_modifier(c, "constitution")),
        "INT": lambda c: str(get_ability(c, "intelligence")),
        "INTmod": lambda c: format_mod(get_modifier(c, "intelligence")),
        "WIS": lambda c: str(get_ability(c, "wisdom")),
        "WISmod": lambda c: format_mod(get_modifier(c, "wisdom")),
        "CHA": lambda c: str(get_ability(c, "charisma")),
        "CHamod": lambda c: format_mod(get_modifier(c, "charisma")),
        
        "AC": lambda c: str(c.get("armor_class", 10)),
        "Initiative": lambda c: format_mod(c.get("initiative", get_modifier(c, "dexterity"))),
        "Speed": lambda c: str(c.get("speed", 30)),
        "ProfBonus": lambda c: f"+{c.get('proficiency_bonus', 2)}",
        "HPMax": lambda c: str(c.get("hit_points", 10)),
        "HPCurrent": lambda c: str(c.get("hit_points", 10)),
        
        # Saves
        "ST Strength": lambda c: format_mod(c.get("saving_throws", {}).get("Strength", get_modifier(c, "strength"))),
        "ST Dexterity": lambda c: format_mod(c.get("saving_throws", {}).get("Dexterity", get_modifier(c, "dexterity"))),
        "ST Constitution": lambda c: format_mod(c.get("saving_throws", {}).get("Constitution", get_modifier(c, "constitution"))),
        "ST Intelligence": lambda c: format_mod(c.get("saving_throws", {}).get("Intelligence", get_modifier(c, "intelligence"))),
        "ST Wisdom": lambda c: format_mod(c.get("saving_throws", {}).get("Wisdom", get_modifier(c, "wisdom"))),
        "ST Charisma": lambda c: format_mod(c.get("saving_throws", {}).get("Charisma", get_modifier(c, "charisma"))),
        
        # Multiline alanlar için birleştirilmiş veriler
        "Skills": lambda c: "\n".join(f"{k}: {format_mod(v)}" for k, v in c.get("skills", {}).items()),
        "Features and Traits": lambda c: "\n".join(c.get("feats", [])),
        "Equipment": lambda c: "\n".join(item.get("name", str(item)) if isinstance(item, dict) else str(item) for item in c.get("equipment", [])),
    },
    "pf1e": {
        # Ortak Başlık & RPG Detayları
        "Character Name": lambda c: c.get("name", ""),
        "Classes & Levels": lambda c: f"{c.get('class', '')} {c.get('level', 1)}",
        "Race": lambda c: c.get("race", ""),
        "Alignment": lambda c: c.get("alignment", ""),
        "Deity": lambda c: c.get("deity", ""),
        "Age": lambda c: str(c.get("age", "")),
        "Background": lambda c: c.get("background", ""),
        "Size": lambda c: c.get("size", "Medium"),
        
        # Statlar & Savaş
        "strength": lambda c: str(get_ability(c, "strength")),
        "strength_mod": lambda c: format_mod(get_modifier(c, "strength")),
        "dexterity": lambda c: str(get_ability(c, "dexterity")),
        "dexterity_mod": lambda c: format_mod(get_modifier(c, "dexterity")),
        "constitution": lambda c: str(get_ability(c, "constitution")),
        "constitution_mod": lambda c: format_mod(get_modifier(c, "constitution")),
        "intelligence": lambda c: str(get_ability(c, "intelligence")),
        "intelligence_mod": lambda c: format_mod(get_modifier(c, "intelligence")),
        "WIS": lambda c: str(get_ability(c, "wisdom")),
        "WIS_mod": lambda c: format_mod(get_modifier(c, "wisdom")),
        "charisma": lambda c: str(get_ability(c, "charisma")),
        "charisma_mod": lambda c: format_mod(get_modifier(c, "charisma")),
        
        "hit points": lambda c: str(c.get("hit_points", 0)),
        "armor class": lambda c: str(c.get("armor_class", 10)),
        "touch_ac": lambda c: str(c.get("touch_ac", 10)),
        "flat_footed_ac": lambda c: str(c.get("flat_footed_ac", 10)),
        "INITIATIVE": lambda c: format_mod(c.get("initiative", get_modifier(c, "dexterity"))),
        "BASE ATTACK BONUS": lambda c: format_mod(c.get("bab", 0)),
        "CMB": lambda c: format_mod(c.get("cmb", 0)),
        "CMD": lambda c: str(c.get("cmd", 10)),
        
        # Saves
        "FORTITUDE": lambda c: format_mod(c.get("saving_throws", {}).get("Fortitude", get_modifier(c, "constitution"))),
        "REFLEX": lambda c: format_mod(c.get("saving_throws", {}).get("Reflex", get_modifier(c, "dexterity"))),
        "WILL": lambda c: format_mod(c.get("saving_throws", {}).get("Will", get_modifier(c, "wisdom"))),
        
        # Multiline
        "Skills": lambda c: "\n".join(f"{k}: {format_mod(v)}" for k, v in c.get("skills", {}).items()),
        "Feats": lambda c: "\n".join(c.get("feats", [])),
        "Equipment": lambda c: "\n".join(item.get("name", str(item)) if isinstance(item, dict) else str(item) for item in c.get("equipment", [])),
    },
    "mm3e": {
        # Ortak Başlık & RPG Detayları
        "CharacterName": lambda c: c.get("name", ""),
        "PowerLevel": lambda c: str(c.get("power_level", c.get("pl_value", 10))),
        "Archetype": lambda c: c.get("class", c.get("archetype", "")),
        "TotalPowerPoints": lambda c: str(c.get("total_power_points", 150)),
        "RemainingPowerPoints": lambda c: str(c.get("remaining_power_points", 0)),
        "Age": lambda c: str(c.get("age", "")),
        "Alignment": lambda c: c.get("alignment", ""),
        "Background": lambda c: c.get("background", ""),
        
        # Statlar (Rank)
        "strength": lambda c: str(get_ability(c, "strength", default=0)),
        "stamina": lambda c: str(get_ability(c, "stamina", default=0)),
        "agility": lambda c: str(get_ability(c, "agility", default=0)),
        "dexterity": lambda c: str(get_ability(c, "dexterity", default=0)),
        "fighting": lambda c: str(get_ability(c, "fighting", default=0)),
        "intellect": lambda c: str(get_ability(c, "intellect", default=0)),
        "awareness": lambda c: str(get_ability(c, "awareness", default=0)),
        "presence": lambda c: str(get_ability(c, "presence", default=0)),
        
        # Defenses & Speed/Init
        "dodge": lambda c: str(c.get("defenses", {}).get("Dodge", get_ability(c, "agility", 0))),
        "parry": lambda c: str(c.get("defenses", {}).get("Parry", get_ability(c, "fighting", 0))),
        "toughness": lambda c: str(c.get("defenses", {}).get("Toughness", get_ability(c, "stamina", 0))),
        "fortitude": lambda c: str(c.get("defenses", {}).get("Fortitude", get_ability(c, "stamina", 0))),
        "will": lambda c: str(c.get("defenses", {}).get("Will", get_ability(c, "awareness", 0))),
        "initiative": lambda c: format_mod(c.get("initiative", get_ability(c, "agility", 0))),
        "speed": lambda c: str(c.get("speed", 30)),
        
        # Multiline
        "Skills": lambda c: "\n".join(f"{k}: {format_mod(v)}" for k, v in c.get("skills", {}).items()),
        "Powers": lambda c: "\n".join(f"{k} ({v.get('cost')} PP): {v.get('description')}" if isinstance(v, dict) else str(v) for k, v in c.get("powers", {}).items()) if isinstance(c.get("powers"), dict) else "\n".join(c.get("powers", [])),
        "Advantages": lambda c: "\n".join(c.get("feats", [])),
    }
}


def _fill_pdf_form(character: dict, template_name: str, mapping: dict, output_path: Path) -> None:
    """Helper function to load template, fill AcroForm fields, and save to output_path."""
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    template_path = template_dir / template_name
    
    # Handle mnm3e double extension on disk if needed
    if template_name == "mnm3e_sheet.pdf" and not template_path.exists():
        template_path = template_dir / "mnm3e_sheet.pdf.pdf"
        
    if not template_path.exists():
        raise FileNotFoundError(f"PDF şablonu bulunamadı: {template_path}")
        
    reader = PdfReader(template_path)
    writer = PdfWriter()
    writer.append(reader)
    
    # Evaluate mapping
    fields_to_fill = {}
    for pdf_field, value_getter in mapping.items():
        try:
            val = value_getter(character) if callable(value_getter) else value_getter
            if val is not None:
                fields_to_fill[pdf_field] = str(val)
        except Exception as e:
            logger.warning(f"Field {pdf_field} error: {e}")
            
    # Dynamic list matching for sequential boxes (e.g. eq_1, eq_2, item_1, feat_1)
    all_pdf_fields = reader.get_fields() or {}
    
    # 1. Equipment sequential matching
    eq_list = character.get("equipment", [])
    for idx, item in enumerate(eq_list, 1):
        name = item.get("name", "") if isinstance(item, dict) else str(item)
        qty = f" x{item.get('quantity')}" if isinstance(item, dict) and item.get("quantity") else ""
        item_str = f"{name}{qty}"
        
        for prefix in ["eq", "eq_", "equipment", "equipment_", "item", "item_"]:
            f_name = f"{prefix}{idx}"
            if f_name in all_pdf_fields:
                fields_to_fill[f_name] = item_str
                break
                
    # 2. Feats sequential matching
    feat_list = character.get("feats", [])
    for idx, feat in enumerate(feat_list, 1):
        for prefix in ["feat", "feat_", "feature", "feature_", "power", "power_"]:
            f_name = f"{prefix}{idx}"
            if f_name in all_pdf_fields:
                fields_to_fill[f_name] = str(feat)
                break
                
    # Fill values on all pages
    if fields_to_fill:
        for page in writer.pages:
            try:
                writer.update_page_form_field_values(page, fields_to_fill)
            except Exception as e:
                logger.debug(f"Could not update fields on page: {e}")
                
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)


def export_dnd_character_pdf(character: dict, output_path: Path, *args, **kwargs) -> None:
    """D&D 5e karakterini fillable PDF form şablonuna doldurarak kaydeder."""
    _fill_pdf_form(character, "dnd5e_sheet.pdf", PDF_MAPPINGS["dnd5e"], output_path)


def export_pf1e_character_pdf(character: dict, output_path: Path, *args, **kwargs) -> None:
    """Pathfinder 1e karakterini fillable PDF form şablonuna doldurarak kaydeder."""
    _fill_pdf_form(character, "pf1e_sheet.pdf", PDF_MAPPINGS["pf1e"], output_path)


def export_mm_character_pdf(character: dict, output_path: Path, *args, **kwargs) -> None:
    """Mutants & Masterminds 3e karakterini fillable PDF form şablonuna doldurarak kaydeder."""
    _fill_pdf_form(character, "mnm3e_sheet.pdf", PDF_MAPPINGS["mm3e"], output_path)


def export_pdf(character: dict, output_path: Path) -> None:
    """Sistem anahtarına göre doğru fillable PDF şablonunu tetikler."""
    system = character.get("system", "").upper()
    if "DND" in system:
        export_dnd_character_pdf(character, output_path)
    elif "MM" in system or "MUTANTS" in system:
        export_mm_character_pdf(character, output_path)
    elif "PATHFINDER" in system or "PF" in system:
        export_pf1e_character_pdf(character, output_path)
    else:
        export_dnd_character_pdf(character, output_path)
