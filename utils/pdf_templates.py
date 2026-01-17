"""
PDF Templates Modülü - İYİLEŞTİRİLDİ (PDF Export İyileştirmeleri)
PDF export için template ve layout iyileştirmeleri
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from typing import Optional, Dict, Any, List
import base64
from io import BytesIO


def _register_turkish_font_for_template() -> str:
    """
    Türkçe karakter desteği için font kayıt et (template için)
    """
    font_candidates = [
        Path(__file__).resolve().parents[1] / "assets" / "fonts" / "DejaVuSans.ttf",
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/arialuni.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    registered_name = "DiyargezenSans"
    for candidate in font_candidates:
        try:
            if candidate.exists():
                pdfmetrics.registerFont(TTFont(registered_name, str(candidate)))
                return registered_name
        except Exception:
            continue
    return "Helvetica"


def _get_character_image_bytes(character: dict) -> Optional[BytesIO]:
    """
    Karakter verisinden resmi al ve BytesIO olarak döndür
    """
    image_data = character.get("image")
    if not image_data:
        return None
    
    try:
        if isinstance(image_data, str) and image_data.startswith('data:'):
            header, data = image_data.split(',', 1)
            image_bytes = base64.b64decode(data)
            return BytesIO(image_bytes)
        elif isinstance(image_data, str):
            image_path = Path(image_data)
            if image_path.exists():
                with open(image_path, 'rb') as f:
                    return BytesIO(f.read())
    except Exception:
        pass
    
    return None


def _get_color_scheme(color_scheme: str = "default") -> Dict[str, str]:
    """
    Renk şeması döndür - İYİLEŞTİRİLDİ (PDF Customization)
    """
    schemes = {
        "default": {
            "primary": "#2c3e50",
            "secondary": "#34495e",
            "accent": "#3498db",
            "success": "#27ae60",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "purple": "#9b59b6"
        },
        "blue": {
            "primary": "#1a237e",
            "secondary": "#283593",
            "accent": "#3f51b5",
            "success": "#1976d2",
            "danger": "#1565c0",
            "warning": "#0d47a1",
            "purple": "#311b92"
        },
        "green": {
            "primary": "#1b5e20",
            "secondary": "#2e7d32",
            "accent": "#4caf50",
            "success": "#388e3c",
            "danger": "#2e7d32",
            "warning": "#1b5e20",
            "purple": "#4a148c"
        },
        "red": {
            "primary": "#b71c1c",
            "secondary": "#c62828",
            "accent": "#d32f2f",
            "success": "#c62828",
            "danger": "#b71c1c",
            "warning": "#d32f2f",
            "purple": "#880e4f"
        }
    }
    return schemes.get(color_scheme, schemes["default"])


def _create_styles(font_name: str, color_scheme: str = "default") -> Dict[str, ParagraphStyle]:
    """
    PDF için stil tanımlamaları oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri + Customization)
    """
    scheme = _get_color_scheme(color_scheme)
    
    styles = {}
    
    # Başlık stili
    styles['title'] = ParagraphStyle(
        'CustomTitle',
        parent=getSampleStyleSheet()['Title'],
        fontName=font_name,
        fontSize=20,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # Alt başlık stili
    styles['heading'] = ParagraphStyle(
        'CustomHeading',
        parent=getSampleStyleSheet()['Heading1'],
        fontName=font_name,
        fontSize=14,
        textColor=colors.HexColor(scheme["secondary"]),
        spaceAfter=8,
        spaceBefore=12,
        alignment=TA_LEFT
    )
    
    # Normal metin stili
    styles['normal'] = ParagraphStyle(
        'CustomNormal',
        parent=getSampleStyleSheet()['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Vurgulu metin stili
    bold_font = 'Helvetica-Bold' if font_name == 'Helvetica' else font_name
    styles['bold'] = ParagraphStyle(
        'CustomBold',
        parent=getSampleStyleSheet()['Normal'],
        fontName=bold_font,
        fontSize=10,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    return styles


def _create_ability_scores_table(character: dict, styles: Dict[str, ParagraphStyle], color_scheme: str = "default") -> Table:
    """
    Ability Scores tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    abilities = character.get('abilities', {})
    mods = character.get('ability_modifiers', {})
    
    ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    ability_short = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    
    data = [["Yetenek", "Kısa", "Puan", "Mod"]]
    
    for i, ability in enumerate(ability_names):
        if ability in abilities:
            score = abilities[ability]
            modifier = mods.get(ability, 0)
            data.append([
                ability,
                ability_short[i],
                str(score),
                f"{modifier:+d}"
            ])
    
    table = Table(data, colWidths=[3*cm, 1.5*cm, 1.5*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _create_combat_stats_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Combat Statistics tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    data = [
        ["Savaş İstatistikleri", "Değer"],
        ["Armor Class (AC)", str(character.get('armor_class', 10))],
        ["Hit Points (HP)", str(character.get('hp_max', 8))],
        ["Hit Dice", character.get('hit_dice', 'd8')],
        ["Speed", f"{character.get('speed', 30)} ft"],
        ["Initiative", f"{character.get('initiative', 0):+d}"],
        ["Passive Perception", str(character.get('passive_perception', 10))],
    ]
    
    # Movement speed ve encumbrance bilgileri ekle
    if 'movement_speed' in character:
        data.append(["Movement Speed", f"{character['movement_speed']} ft"])
    
    table = Table(data, colWidths=[4*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff5f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffcccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffafa')]),
    ]))
    
    return table


def _create_saving_throws_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Saving Throws tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    save_mods = character.get('saving_throw_modifiers', {})
    proficient_saves = character.get('saving_throws', [])
    
    ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    ability_short = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    
    data = [["Yetenek", "Kısa", "Mod", "Uzman"]]
    
    for i, ability in enumerate(ability_names):
        modifier = save_mods.get(ability, 0)
        is_proficient = ability in proficient_saves
        proficient_mark = "✓" if is_proficient else ""
        data.append([
            ability,
            ability_short[i],
            f"{modifier:+d}",
            proficient_mark
        ])
    
    table = Table(data, colWidths=[3*cm, 1.5*cm, 1.5*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ebf5fb')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#aed6f1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _create_skills_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Skills tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    skills = character.get('skills', {})
    
    if not skills:
        return None
    
    data = [["Beceri", "Mod", "Uzman"]]
    
    # Skills'i alfabetik sırala
    for skill_name in sorted(skills.keys()):
        skill_mod = skills[skill_name]
        # Expertise kontrolü (2x proficiency için)
        is_expertise = skill_mod >= 5  # Basit kontrol, gerçekte expertise listesi kontrol edilmeli
        expertise_mark = "✓✓" if is_expertise else "✓" if skill_mod > 0 else ""
        data.append([
            skill_name,
            f"{skill_mod:+d}",
            expertise_mark
        ])
    
    table = Table(data, colWidths=[4*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eafaf1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#a9dfbf')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _build_standard_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Standard template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    """
    story = []
    
    # Başlık
    title_text = f"🎲 Diyargezen - D&D 5e Karakter Kağıdı"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.3*cm))
    
    # Karakter adı ve temel bilgiler
    char_name = character.get('name', 'İsimsiz Karakter')
    char_info = f"<b>{char_name}</b> | Level {character.get('level', 1)} | {character.get('race', '')} {character.get('class', '')}"
    if character.get('background'):
        char_info += f" | {character.get('background', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Default options
    if options is None:
        options = {"show_abilities": True, "show_combat_stats": True, "show_saving_throws": True, 
                   "show_skills": True, "show_equipment": True, "show_spells": True}
    
    # Ability Scores tablosu
    if options.get("show_abilities", True):
        story.append(Paragraph("<b>Yetenek Puanları</b>", styles['heading']))
        ability_table = _create_ability_scores_table(character, styles)
        story.append(ability_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Combat Statistics tablosu
    if options.get("show_combat_stats", True):
        story.append(Paragraph("<b>Savaş İstatistikleri</b>", styles['heading']))
        combat_table = _create_combat_stats_table(character, styles)
        story.append(combat_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Saving Throws tablosu
    if options.get("show_saving_throws", True):
        story.append(Paragraph("<b>Kurtarış Atışları</b>", styles['heading']))
        saves_table = _create_saving_throws_table(character, styles)
        story.append(saves_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Skills tablosu
    if options.get("show_skills", True):
        skills_table = _create_skills_table(character, styles)
        if skills_table:
            story.append(Paragraph("<b>Beceriler</b>", styles['heading']))
            story.append(skills_table)
            story.append(Spacer(1, 0.5*cm))
    
    # Equipment
    if options.get("show_equipment", True):
        equipment = character.get('equipment', [])
        if equipment:
            story.append(Paragraph("<b>Ekipman</b>", styles['heading']))
            eq_items = []
            for item in equipment[:10]:  # İlk 10 item
                if isinstance(item, dict):
                    item_name = item.get('name', str(item))
                    quantity = item.get('quantity', 1)
                    if quantity > 1:
                        eq_items.append(f"{item_name} x{quantity}")
                    else:
                        eq_items.append(item_name)
                else:
                    eq_items.append(str(item))
            
            eq_text = ", ".join(eq_items)
            if len(equipment) > 10:
                eq_text += f" ... ve {len(equipment) - 10} daha"
            story.append(Paragraph(eq_text, styles['normal']))
            story.append(Spacer(1, 0.3*cm))
    
    # Spells (kısa özet)
    if options.get("show_spells", True):
        spells = character.get('spells', {})
        if spells:
            story.append(Paragraph("<b>Büyüler (Özet)</b>", styles['heading']))
            spell_text = ""
            
            # Cantrips
            cantrips = spells.get('cantrips') or spells.get('1st_level') or []
            if cantrips:
                if isinstance(cantrips, list):
                    spell_text += f"<b>Cantrips:</b> {', '.join(cantrips[:5])}"
                    if len(cantrips) > 5:
                        spell_text += f" ... ve {len(cantrips) - 5} daha"
                else:
                    spell_text += f"<b>Cantrips:</b> {cantrips}"
            
            # Level 1 spells
            level1 = spells.get('level1') or spells.get('1st_level') or []
            if level1:
                if spell_text:
                    spell_text += "<br/>"
                if isinstance(level1, list):
                    spell_text += f"<b>Level 1:</b> {', '.join(level1[:5])}"
                    if len(level1) > 5:
                        spell_text += f" ... ve {len(level1) - 5} daha"
                else:
                    spell_text += f"<b>Level 1:</b> {level1}"
            
            if spell_text:
                story.append(Paragraph(spell_text, styles['normal']))
                story.append(Spacer(1, 0.3*cm))
    
    return story


def _build_compact_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Compact template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    Daha az detay, daha kompakt düzen
    """
    story = []
    
    # Başlık (daha küçük)
    title_text = f"🎲 Diyargezen - D&D 5e"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.2*cm))
    
    # Karakter adı ve temel bilgiler (tek satır)
    char_name = character.get('name', 'İsimsiz Karakter')
    char_info = f"<b>{char_name}</b> | Lv.{character.get('level', 1)} | {character.get('race', '')} {character.get('class', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.3*cm))
    
    # Ability Scores ve Combat Stats yan yana (2 kolon)
    # Bu için daha küçük tablolar oluştur
    story.append(Paragraph("<b>Yetenek Puanları & Savaş İstatistikleri</b>", styles['heading']))
    
    # Ability Scores (kompakt)
    abilities = character.get('abilities', {})
    mods = character.get('ability_modifiers', {})
    ability_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    ability_full = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    ability_data = [["Yetenek", "Puan", "Mod"]]
    for i, ability in enumerate(ability_full):
        if ability in abilities:
            ability_data.append([
                ability_names[i],
                str(abilities[ability]),
                f"{mods.get(ability, 0):+d}"
            ])
    
    ability_table = Table(ability_data, colWidths=[1.5*cm, 1.5*cm, 1.5*cm])
    ability_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
    ]))
    
    # Combat Stats (kompakt)
    combat_data = [
        ["AC", str(character.get('armor_class', 10))],
        ["HP", str(character.get('hp_max', 8))],
        ["Speed", f"{character.get('speed', 30)} ft"],
        ["Init", f"{character.get('initiative', 0):+d}"],
    ]
    
    combat_table = Table(combat_data, colWidths=[2*cm, 2*cm])
    combat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffcccc')),
    ]))
    
    # İki tabloyu yan yana koy (basit yaklaşım: alt alta)
    story.append(ability_table)
    story.append(Spacer(1, 0.2*cm))
    story.append(combat_table)
    story.append(Spacer(1, 0.3*cm))
    
    # Skills (kompakt, sadece proficient olanlar)
    skills = character.get('skills', {})
    if skills and isinstance(skills, dict):
        proficient_skills = [skill for skill, mod in skills.items() if mod > 0]
        if proficient_skills:
            story.append(Paragraph("<b>Beceriler (Uzman)</b>", styles['heading']))
            skills_text = ", ".join(sorted(proficient_skills))
            story.append(Paragraph(skills_text, styles['normal']))
            story.append(Spacer(1, 0.2*cm))
    
    return story


def _build_detailed_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Detailed template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    Tüm detaylar, class features, feats, vb.
    """
    story = _build_standard_template(character, styles)
    
    # Ek detaylar ekle
    # Class Features
    class_features = character.get("class_features", {})
    if class_features:
        story.append(Paragraph("<b>Sınıf Özellikleri</b>", styles['heading']))
        for level, features_data in sorted(class_features.items(), key=lambda x: int(x[0])):
            features = features_data.get("features", [])
            choices = features_data.get("choices", {})
            if features or choices:
                level_text = f"<b>Seviye {level}:</b>"
                feature_list = []
                for feature in features:
                    feature_list.append(f"• {feature}")
                for choice_type, options in choices.items():
                    feature_list.append(f"• {choice_type}: {', '.join(options)}")
                story.append(Paragraph(level_text, styles['normal']))
                for feature_item in feature_list:
                    story.append(Paragraph(feature_item, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Feats
    feats = character.get("feats", [])
    if feats:
        story.append(Paragraph("<b>Feat'ler</b>", styles['heading']))
        feat_text = " • ".join(feats)
        story.append(Paragraph(feat_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Languages
    languages = character.get('languages', [])
    if languages:
        story.append(Paragraph("<b>Diller</b>", styles['heading']))
        lang_text = ", ".join(languages)
        story.append(Paragraph(lang_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Personality Traits
    personality = character.get('personality', {})
    if personality and any(personality.values()):
        story.append(Paragraph("<b>Kişilik Özellikleri</b>", styles['heading']))
        if personality.get('trait'):
            story.append(Paragraph(f"<b>Trait:</b> {personality['trait']}", styles['normal']))
        if personality.get('ideal'):
            story.append(Paragraph(f"<b>Ideal:</b> {personality['ideal']}", styles['normal']))
        if personality.get('bond'):
            story.append(Paragraph(f"<b>Bond:</b> {personality['bond']}", styles['normal']))
        if personality.get('flaw'):
            story.append(Paragraph(f"<b>Flaw:</b> {personality['flaw']}", styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    return story


def export_dnd_character_pdf_improved(character: dict, output_path: Path, template: str = "standard", page_size: str = "A4", options: Optional[Dict[str, Any]] = None) -> None:
    """
    D&D karakterini iyileştirilmiş PDF'e yazar - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    
    Args:
        character: Karakter verisi
        output_path: PDF çıktı yolu
        template: Template adı ("standard", "compact", "detailed")
        page_size: Sayfa boyutu ("A4" veya "letter")
        options: Customization options dict:
            - show_abilities: bool (default: True)
            - show_combat_stats: bool (default: True)
            - show_saving_throws: bool (default: True)
            - show_skills: bool (default: True)
            - show_equipment: bool (default: True)
            - show_spells: bool (default: True)
            - show_features: bool (default: True) - class features, feats
            - show_personality: bool (default: True)
            - color_scheme: str (default: "default") - "default", "blue", "green", "red"
    """
    # Default options
    default_options = {
        "show_abilities": True,
        "show_combat_stats": True,
        "show_saving_throws": True,
        "show_skills": True,
        "show_equipment": True,
        "show_spells": True,
        "show_features": True,
        "show_personality": True,
        "color_scheme": "default"
    }
    
    if options:
        default_options.update(options)
    options = default_options
    
    size = A4 if page_size.upper() == "A4" else letter
    doc = SimpleDocTemplate(str(output_path), pagesize=size, 
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    
    font_name = _register_turkish_font_for_template()
    styles = _create_styles(font_name, color_scheme=options.get("color_scheme", "default"))
    
    # Template'e göre içerik oluştur (options ile)
    if template == "compact":
        story = _build_compact_template(character, styles, options)
    elif template == "detailed":
        story = _build_detailed_template(character, styles, options)
    else:  # standard
        story = _build_standard_template(character, styles, options)
    
    # PDF'i oluştur
    doc.build(story)


def _create_spell_table(spell_name: str, spell_data: dict, styles: Dict[str, ParagraphStyle], dnd_data: Optional[Dict[str, Any]] = None) -> Table:
    """
    Tek bir spell için tablo oluştur - İYİLEŞTİRİLDİ (PDF Spell Sheet)
    """
    # Spell data'yı al
    if dnd_data and 'spells' in dnd_data:
        full_spell_data = dnd_data['spells'].get(spell_name, {})
        spell_data = {**spell_data, **full_spell_data}
    
    level = spell_data.get('level', 0)
    school = spell_data.get('school', 'Unknown')
    casting_time = spell_data.get('casting_time', 'Unknown')
    range_text = spell_data.get('range', 'Unknown')
    components = spell_data.get('components', 'Unknown')
    duration = spell_data.get('duration', 'Unknown')
    description = spell_data.get('description', 'No description')
    
    # Ritual, Concentration, Material Components kontrolü
    from utils.calculations import is_ritual_spell, is_concentration_spell, extract_material_components
    
    is_ritual = is_ritual_spell(spell_name, spell_data, dnd_data)
    is_concentration = is_concentration_spell(spell_name, spell_data, dnd_data)
    material_info = extract_material_components(spell_data)
    
    # Tablo verisi
    data = [
        ["Özellik", "Değer"],
        ["Seviye", "Cantrip" if level == 0 else f"Level {level}"],
        ["Okul", school],
        ["Casting Time", casting_time],
        ["Range", range_text],
        ["Components", components],
        ["Duration", duration],
    ]
    
    # Özel özellikler
    special_features = []
    if is_ritual:
        special_features.append("Ritual")
    if is_concentration:
        special_features.append("Concentration")
    if material_info:
        material_text = material_info.get('component', '')
        if material_info.get('cost'):
            material_text += f" ({material_info['cost']})"
        if material_info.get('consumed'):
            material_text += " [Consumed]"
        special_features.append(f"Material: {material_text}")
    
    if special_features:
        data.append(["Özel Özellikler", ", ".join(special_features)])
    
    # Description (uzun metin için ayrı paragraf)
    table = Table(data, colWidths=[3*cm, 6*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f4ecf7')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d7bde2')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
    ]))
    
    return table, description


def export_dnd_spell_sheet_pdf(character: dict, output_path: Path, dnd_data: Optional[Dict[str, Any]] = None, page_size: str = "A4") -> None:
    """
    D&D karakterinin spell sheet'ini PDF'e yazar - İYİLEŞTİRİLDİ (PDF Spell Sheet)
    
    Args:
        character: Karakter verisi
        output_path: PDF çıktı yolu
        dnd_data: D&D veri yapısı (spell detayları için)
        page_size: Sayfa boyutu ("A4" veya "letter")
    """
    size = A4 if page_size.upper() == "A4" else letter
    doc = SimpleDocTemplate(str(output_path), pagesize=size, 
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    
    font_name = _register_turkish_font_for_template()
    styles = _create_styles(font_name)
    
    story = []
    
    # Başlık
    char_name = character.get('name', 'İsimsiz Karakter')
    title_text = f"🎲 Diyargezen - D&D 5e Spell Sheet: {char_name}"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.3*cm))
    
    # Karakter bilgisi
    char_info = f"Level {character.get('level', 1)} {character.get('race', '')} {character.get('class', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Spell Slots
    spell_slots = character.get('spell_slots', {})
    if spell_slots:
        story.append(Paragraph("<b>Spell Slots</b>", styles['heading']))
        slots_text = ", ".join([f"Level {level}: {slots}" for level, slots in sorted(spell_slots.items())])
        story.append(Paragraph(slots_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Spells by level
    spells = character.get('spells', {})
    
    # Cantrips
    cantrips = spells.get('cantrips', []) or spells.get('1st_level', [])
    if not isinstance(cantrips, list):
        cantrips = []
    
    if cantrips:
        story.append(Paragraph("<b>Cantrips</b>", styles['heading']))
        for spell_name in cantrips:
            spell_data = {'level': 0, 'name': spell_name}
            spell_table, description = _create_spell_table(spell_name, spell_data, styles, dnd_data)
            story.append(Paragraph(f"<b>{spell_name}</b>", styles['bold']))
            story.append(spell_table)
            if description and description != 'No description':
                # Description'ı paragraf olarak ekle
                desc_para = Paragraph(f"<i>{description[:200]}...</i>" if len(description) > 200 else f"<i>{description}</i>", styles['normal'])
                story.append(desc_para)
            story.append(Spacer(1, 0.3*cm))
        story.append(PageBreak())
    
    # Level 1-9 spells
    for level in range(1, 10):
        level_key = f"level{level}" if f"level{level}" in spells else f"{level}st_level" if level == 1 else f"{level}nd_level" if level == 2 else f"{level}rd_level" if level == 3 else f"{level}th_level"
        level_spells = spells.get(level_key, [])
        
        if level_spells:
            story.append(Paragraph(f"<b>Level {level} Spells</b>", styles['heading']))
            for spell_name in level_spells:
                spell_data = {'level': level, 'name': spell_name}
                spell_table, description = _create_spell_table(spell_name, spell_data, styles, dnd_data)
                story.append(Paragraph(f"<b>{spell_name}</b>", styles['bold']))
                story.append(spell_table)
                if description and description != 'No description':
                    desc_para = Paragraph(f"<i>{description[:200]}...</i>" if len(description) > 200 else f"<i>{description}</i>", styles['normal'])
                    story.append(desc_para)
                story.append(Spacer(1, 0.3*cm))
            story.append(PageBreak())
    
    # PDF'i oluştur
    doc.build(story)


PDF export için template ve layout iyileştirmeleri
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from typing import Optional, Dict, Any, List
import base64
from io import BytesIO


def _register_turkish_font_for_template() -> str:
    """
    Türkçe karakter desteği için font kayıt et (template için)
    """
    font_candidates = [
        Path(__file__).resolve().parents[1] / "assets" / "fonts" / "DejaVuSans.ttf",
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/arialuni.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    registered_name = "DiyargezenSans"
    for candidate in font_candidates:
        try:
            if candidate.exists():
                pdfmetrics.registerFont(TTFont(registered_name, str(candidate)))
                return registered_name
        except Exception:
            continue
    return "Helvetica"


def _get_character_image_bytes(character: dict) -> Optional[BytesIO]:
    """
    Karakter verisinden resmi al ve BytesIO olarak döndür
    """
    image_data = character.get("image")
    if not image_data:
        return None
    
    try:
        if isinstance(image_data, str) and image_data.startswith('data:'):
            header, data = image_data.split(',', 1)
            image_bytes = base64.b64decode(data)
            return BytesIO(image_bytes)
        elif isinstance(image_data, str):
            image_path = Path(image_data)
            if image_path.exists():
                with open(image_path, 'rb') as f:
                    return BytesIO(f.read())
    except Exception:
        pass
    
    return None


def _get_color_scheme(color_scheme: str = "default") -> Dict[str, str]:
    """
    Renk şeması döndür - İYİLEŞTİRİLDİ (PDF Customization)
    """
    schemes = {
        "default": {
            "primary": "#2c3e50",
            "secondary": "#34495e",
            "accent": "#3498db",
            "success": "#27ae60",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "purple": "#9b59b6"
        },
        "blue": {
            "primary": "#1a237e",
            "secondary": "#283593",
            "accent": "#3f51b5",
            "success": "#1976d2",
            "danger": "#1565c0",
            "warning": "#0d47a1",
            "purple": "#311b92"
        },
        "green": {
            "primary": "#1b5e20",
            "secondary": "#2e7d32",
            "accent": "#4caf50",
            "success": "#388e3c",
            "danger": "#2e7d32",
            "warning": "#1b5e20",
            "purple": "#4a148c"
        },
        "red": {
            "primary": "#b71c1c",
            "secondary": "#c62828",
            "accent": "#d32f2f",
            "success": "#c62828",
            "danger": "#b71c1c",
            "warning": "#d32f2f",
            "purple": "#880e4f"
        }
    }
    return schemes.get(color_scheme, schemes["default"])


def _create_styles(font_name: str, color_scheme: str = "default") -> Dict[str, ParagraphStyle]:
    """
    PDF için stil tanımlamaları oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri + Customization)
    """
    scheme = _get_color_scheme(color_scheme)
    
    styles = {}
    
    # Başlık stili
    styles['title'] = ParagraphStyle(
        'CustomTitle',
        parent=getSampleStyleSheet()['Title'],
        fontName=font_name,
        fontSize=20,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # Alt başlık stili
    styles['heading'] = ParagraphStyle(
        'CustomHeading',
        parent=getSampleStyleSheet()['Heading1'],
        fontName=font_name,
        fontSize=14,
        textColor=colors.HexColor(scheme["secondary"]),
        spaceAfter=8,
        spaceBefore=12,
        alignment=TA_LEFT
    )
    
    # Normal metin stili
    styles['normal'] = ParagraphStyle(
        'CustomNormal',
        parent=getSampleStyleSheet()['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Vurgulu metin stili
    bold_font = 'Helvetica-Bold' if font_name == 'Helvetica' else font_name
    styles['bold'] = ParagraphStyle(
        'CustomBold',
        parent=getSampleStyleSheet()['Normal'],
        fontName=bold_font,
        fontSize=10,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    return styles


def _create_ability_scores_table(character: dict, styles: Dict[str, ParagraphStyle], color_scheme: str = "default") -> Table:
    """
    Ability Scores tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    abilities = character.get('abilities', {})
    mods = character.get('ability_modifiers', {})
    
    ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    ability_short = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    
    data = [["Yetenek", "Kısa", "Puan", "Mod"]]
    
    for i, ability in enumerate(ability_names):
        if ability in abilities:
            score = abilities[ability]
            modifier = mods.get(ability, 0)
            data.append([
                ability,
                ability_short[i],
                str(score),
                f"{modifier:+d}"
            ])
    
    table = Table(data, colWidths=[3*cm, 1.5*cm, 1.5*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _create_combat_stats_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Combat Statistics tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    data = [
        ["Savaş İstatistikleri", "Değer"],
        ["Armor Class (AC)", str(character.get('armor_class', 10))],
        ["Hit Points (HP)", str(character.get('hp_max', 8))],
        ["Hit Dice", character.get('hit_dice', 'd8')],
        ["Speed", f"{character.get('speed', 30)} ft"],
        ["Initiative", f"{character.get('initiative', 0):+d}"],
        ["Passive Perception", str(character.get('passive_perception', 10))],
    ]
    
    # Movement speed ve encumbrance bilgileri ekle
    if 'movement_speed' in character:
        data.append(["Movement Speed", f"{character['movement_speed']} ft"])
    
    table = Table(data, colWidths=[4*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff5f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffcccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffafa')]),
    ]))
    
    return table


def _create_saving_throws_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Saving Throws tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    save_mods = character.get('saving_throw_modifiers', {})
    proficient_saves = character.get('saving_throws', [])
    
    ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    ability_short = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    
    data = [["Yetenek", "Kısa", "Mod", "Uzman"]]
    
    for i, ability in enumerate(ability_names):
        modifier = save_mods.get(ability, 0)
        is_proficient = ability in proficient_saves
        proficient_mark = "✓" if is_proficient else ""
        data.append([
            ability,
            ability_short[i],
            f"{modifier:+d}",
            proficient_mark
        ])
    
    table = Table(data, colWidths=[3*cm, 1.5*cm, 1.5*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ebf5fb')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#aed6f1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _create_skills_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Skills tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    skills = character.get('skills', {})
    
    if not skills:
        return None
    
    data = [["Beceri", "Mod", "Uzman"]]
    
    # Skills'i alfabetik sırala
    for skill_name in sorted(skills.keys()):
        skill_mod = skills[skill_name]
        # Expertise kontrolü (2x proficiency için)
        is_expertise = skill_mod >= 5  # Basit kontrol, gerçekte expertise listesi kontrol edilmeli
        expertise_mark = "✓✓" if is_expertise else "✓" if skill_mod > 0 else ""
        data.append([
            skill_name,
            f"{skill_mod:+d}",
            expertise_mark
        ])
    
    table = Table(data, colWidths=[4*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eafaf1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#a9dfbf')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _build_standard_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Standard template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    """
    story = []
    
    # Başlık
    title_text = f"🎲 Diyargezen - D&D 5e Karakter Kağıdı"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.3*cm))
    
    # Karakter adı ve temel bilgiler
    char_name = character.get('name', 'İsimsiz Karakter')
    char_info = f"<b>{char_name}</b> | Level {character.get('level', 1)} | {character.get('race', '')} {character.get('class', '')}"
    if character.get('background'):
        char_info += f" | {character.get('background', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Default options
    if options is None:
        options = {"show_abilities": True, "show_combat_stats": True, "show_saving_throws": True, 
                   "show_skills": True, "show_equipment": True, "show_spells": True}
    
    # Ability Scores tablosu
    if options.get("show_abilities", True):
        story.append(Paragraph("<b>Yetenek Puanları</b>", styles['heading']))
        ability_table = _create_ability_scores_table(character, styles)
        story.append(ability_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Combat Statistics tablosu
    if options.get("show_combat_stats", True):
        story.append(Paragraph("<b>Savaş İstatistikleri</b>", styles['heading']))
        combat_table = _create_combat_stats_table(character, styles)
        story.append(combat_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Saving Throws tablosu
    if options.get("show_saving_throws", True):
        story.append(Paragraph("<b>Kurtarış Atışları</b>", styles['heading']))
        saves_table = _create_saving_throws_table(character, styles)
        story.append(saves_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Skills tablosu
    if options.get("show_skills", True):
        skills_table = _create_skills_table(character, styles)
        if skills_table:
            story.append(Paragraph("<b>Beceriler</b>", styles['heading']))
            story.append(skills_table)
            story.append(Spacer(1, 0.5*cm))
    
    # Equipment
    if options.get("show_equipment", True):
        equipment = character.get('equipment', [])
        if equipment:
            story.append(Paragraph("<b>Ekipman</b>", styles['heading']))
            eq_items = []
            for item in equipment[:10]:  # İlk 10 item
                if isinstance(item, dict):
                    item_name = item.get('name', str(item))
                    quantity = item.get('quantity', 1)
                    if quantity > 1:
                        eq_items.append(f"{item_name} x{quantity}")
                    else:
                        eq_items.append(item_name)
                else:
                    eq_items.append(str(item))
            
            eq_text = ", ".join(eq_items)
            if len(equipment) > 10:
                eq_text += f" ... ve {len(equipment) - 10} daha"
            story.append(Paragraph(eq_text, styles['normal']))
            story.append(Spacer(1, 0.3*cm))
    
    # Spells (kısa özet)
    if options.get("show_spells", True):
        spells = character.get('spells', {})
        if spells:
            story.append(Paragraph("<b>Büyüler (Özet)</b>", styles['heading']))
            spell_text = ""
            
            # Cantrips
            cantrips = spells.get('cantrips') or spells.get('1st_level') or []
            if cantrips:
                if isinstance(cantrips, list):
                    spell_text += f"<b>Cantrips:</b> {', '.join(cantrips[:5])}"
                    if len(cantrips) > 5:
                        spell_text += f" ... ve {len(cantrips) - 5} daha"
                else:
                    spell_text += f"<b>Cantrips:</b> {cantrips}"
            
            # Level 1 spells
            level1 = spells.get('level1') or spells.get('1st_level') or []
            if level1:
                if spell_text:
                    spell_text += "<br/>"
                if isinstance(level1, list):
                    spell_text += f"<b>Level 1:</b> {', '.join(level1[:5])}"
                    if len(level1) > 5:
                        spell_text += f" ... ve {len(level1) - 5} daha"
                else:
                    spell_text += f"<b>Level 1:</b> {level1}"
            
            if spell_text:
                story.append(Paragraph(spell_text, styles['normal']))
                story.append(Spacer(1, 0.3*cm))
    
    return story


def _build_compact_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Compact template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    Daha az detay, daha kompakt düzen
    """
    story = []
    
    # Başlık (daha küçük)
    title_text = f"🎲 Diyargezen - D&D 5e"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.2*cm))
    
    # Karakter adı ve temel bilgiler (tek satır)
    char_name = character.get('name', 'İsimsiz Karakter')
    char_info = f"<b>{char_name}</b> | Lv.{character.get('level', 1)} | {character.get('race', '')} {character.get('class', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.3*cm))
    
    # Ability Scores ve Combat Stats yan yana (2 kolon)
    # Bu için daha küçük tablolar oluştur
    story.append(Paragraph("<b>Yetenek Puanları & Savaş İstatistikleri</b>", styles['heading']))
    
    # Ability Scores (kompakt)
    abilities = character.get('abilities', {})
    mods = character.get('ability_modifiers', {})
    ability_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    ability_full = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    ability_data = [["Yetenek", "Puan", "Mod"]]
    for i, ability in enumerate(ability_full):
        if ability in abilities:
            ability_data.append([
                ability_names[i],
                str(abilities[ability]),
                f"{mods.get(ability, 0):+d}"
            ])
    
    ability_table = Table(ability_data, colWidths=[1.5*cm, 1.5*cm, 1.5*cm])
    ability_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
    ]))
    
    # Combat Stats (kompakt)
    combat_data = [
        ["AC", str(character.get('armor_class', 10))],
        ["HP", str(character.get('hp_max', 8))],
        ["Speed", f"{character.get('speed', 30)} ft"],
        ["Init", f"{character.get('initiative', 0):+d}"],
    ]
    
    combat_table = Table(combat_data, colWidths=[2*cm, 2*cm])
    combat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffcccc')),
    ]))
    
    # İki tabloyu yan yana koy (basit yaklaşım: alt alta)
    story.append(ability_table)
    story.append(Spacer(1, 0.2*cm))
    story.append(combat_table)
    story.append(Spacer(1, 0.3*cm))
    
    # Skills (kompakt, sadece proficient olanlar)
    skills = character.get('skills', {})
    if skills and isinstance(skills, dict):
        proficient_skills = [skill for skill, mod in skills.items() if mod > 0]
        if proficient_skills:
            story.append(Paragraph("<b>Beceriler (Uzman)</b>", styles['heading']))
            skills_text = ", ".join(sorted(proficient_skills))
            story.append(Paragraph(skills_text, styles['normal']))
            story.append(Spacer(1, 0.2*cm))
    
    return story


def _build_detailed_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Detailed template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    Tüm detaylar, class features, feats, vb.
    """
    story = _build_standard_template(character, styles)
    
    # Ek detaylar ekle
    # Class Features
    class_features = character.get("class_features", {})
    if class_features:
        story.append(Paragraph("<b>Sınıf Özellikleri</b>", styles['heading']))
        for level, features_data in sorted(class_features.items(), key=lambda x: int(x[0])):
            features = features_data.get("features", [])
            choices = features_data.get("choices", {})
            if features or choices:
                level_text = f"<b>Seviye {level}:</b>"
                feature_list = []
                for feature in features:
                    feature_list.append(f"• {feature}")
                for choice_type, options in choices.items():
                    feature_list.append(f"• {choice_type}: {', '.join(options)}")
                story.append(Paragraph(level_text, styles['normal']))
                for feature_item in feature_list:
                    story.append(Paragraph(feature_item, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Feats
    feats = character.get("feats", [])
    if feats:
        story.append(Paragraph("<b>Feat'ler</b>", styles['heading']))
        feat_text = " • ".join(feats)
        story.append(Paragraph(feat_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Languages
    languages = character.get('languages', [])
    if languages:
        story.append(Paragraph("<b>Diller</b>", styles['heading']))
        lang_text = ", ".join(languages)
        story.append(Paragraph(lang_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Personality Traits
    personality = character.get('personality', {})
    if personality and any(personality.values()):
        story.append(Paragraph("<b>Kişilik Özellikleri</b>", styles['heading']))
        if personality.get('trait'):
            story.append(Paragraph(f"<b>Trait:</b> {personality['trait']}", styles['normal']))
        if personality.get('ideal'):
            story.append(Paragraph(f"<b>Ideal:</b> {personality['ideal']}", styles['normal']))
        if personality.get('bond'):
            story.append(Paragraph(f"<b>Bond:</b> {personality['bond']}", styles['normal']))
        if personality.get('flaw'):
            story.append(Paragraph(f"<b>Flaw:</b> {personality['flaw']}", styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    return story


def export_dnd_character_pdf_improved(character: dict, output_path: Path, template: str = "standard", page_size: str = "A4", options: Optional[Dict[str, Any]] = None) -> None:
    """
    D&D karakterini iyileştirilmiş PDF'e yazar - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    
    Args:
        character: Karakter verisi
        output_path: PDF çıktı yolu
        template: Template adı ("standard", "compact", "detailed")
        page_size: Sayfa boyutu ("A4" veya "letter")
        options: Customization options dict:
            - show_abilities: bool (default: True)
            - show_combat_stats: bool (default: True)
            - show_saving_throws: bool (default: True)
            - show_skills: bool (default: True)
            - show_equipment: bool (default: True)
            - show_spells: bool (default: True)
            - show_features: bool (default: True) - class features, feats
            - show_personality: bool (default: True)
            - color_scheme: str (default: "default") - "default", "blue", "green", "red"
    """
    # Default options
    default_options = {
        "show_abilities": True,
        "show_combat_stats": True,
        "show_saving_throws": True,
        "show_skills": True,
        "show_equipment": True,
        "show_spells": True,
        "show_features": True,
        "show_personality": True,
        "color_scheme": "default"
    }
    
    if options:
        default_options.update(options)
    options = default_options
    
    size = A4 if page_size.upper() == "A4" else letter
    doc = SimpleDocTemplate(str(output_path), pagesize=size, 
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    
    font_name = _register_turkish_font_for_template()
    styles = _create_styles(font_name, color_scheme=options.get("color_scheme", "default"))
    
    # Template'e göre içerik oluştur (options ile)
    if template == "compact":
        story = _build_compact_template(character, styles, options)
    elif template == "detailed":
        story = _build_detailed_template(character, styles, options)
    else:  # standard
        story = _build_standard_template(character, styles, options)
    
    # PDF'i oluştur
    doc.build(story)


def _create_spell_table(spell_name: str, spell_data: dict, styles: Dict[str, ParagraphStyle], dnd_data: Optional[Dict[str, Any]] = None) -> Table:
    """
    Tek bir spell için tablo oluştur - İYİLEŞTİRİLDİ (PDF Spell Sheet)
    """
    # Spell data'yı al
    if dnd_data and 'spells' in dnd_data:
        full_spell_data = dnd_data['spells'].get(spell_name, {})
        spell_data = {**spell_data, **full_spell_data}
    
    level = spell_data.get('level', 0)
    school = spell_data.get('school', 'Unknown')
    casting_time = spell_data.get('casting_time', 'Unknown')
    range_text = spell_data.get('range', 'Unknown')
    components = spell_data.get('components', 'Unknown')
    duration = spell_data.get('duration', 'Unknown')
    description = spell_data.get('description', 'No description')
    
    # Ritual, Concentration, Material Components kontrolü
    from utils.calculations import is_ritual_spell, is_concentration_spell, extract_material_components
    
    is_ritual = is_ritual_spell(spell_name, spell_data, dnd_data)
    is_concentration = is_concentration_spell(spell_name, spell_data, dnd_data)
    material_info = extract_material_components(spell_data)
    
    # Tablo verisi
    data = [
        ["Özellik", "Değer"],
        ["Seviye", "Cantrip" if level == 0 else f"Level {level}"],
        ["Okul", school],
        ["Casting Time", casting_time],
        ["Range", range_text],
        ["Components", components],
        ["Duration", duration],
    ]
    
    # Özel özellikler
    special_features = []
    if is_ritual:
        special_features.append("Ritual")
    if is_concentration:
        special_features.append("Concentration")
    if material_info:
        material_text = material_info.get('component', '')
        if material_info.get('cost'):
            material_text += f" ({material_info['cost']})"
        if material_info.get('consumed'):
            material_text += " [Consumed]"
        special_features.append(f"Material: {material_text}")
    
    if special_features:
        data.append(["Özel Özellikler", ", ".join(special_features)])
    
    # Description (uzun metin için ayrı paragraf)
    table = Table(data, colWidths=[3*cm, 6*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f4ecf7')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d7bde2')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
    ]))
    
    return table, description


def export_dnd_spell_sheet_pdf(character: dict, output_path: Path, dnd_data: Optional[Dict[str, Any]] = None, page_size: str = "A4") -> None:
    """
    D&D karakterinin spell sheet'ini PDF'e yazar - İYİLEŞTİRİLDİ (PDF Spell Sheet)
    
    Args:
        character: Karakter verisi
        output_path: PDF çıktı yolu
        dnd_data: D&D veri yapısı (spell detayları için)
        page_size: Sayfa boyutu ("A4" veya "letter")
    """
    size = A4 if page_size.upper() == "A4" else letter
    doc = SimpleDocTemplate(str(output_path), pagesize=size, 
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    
    font_name = _register_turkish_font_for_template()
    styles = _create_styles(font_name)
    
    story = []
    
    # Başlık
    char_name = character.get('name', 'İsimsiz Karakter')
    title_text = f"🎲 Diyargezen - D&D 5e Spell Sheet: {char_name}"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.3*cm))
    
    # Karakter bilgisi
    char_info = f"Level {character.get('level', 1)} {character.get('race', '')} {character.get('class', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Spell Slots
    spell_slots = character.get('spell_slots', {})
    if spell_slots:
        story.append(Paragraph("<b>Spell Slots</b>", styles['heading']))
        slots_text = ", ".join([f"Level {level}: {slots}" for level, slots in sorted(spell_slots.items())])
        story.append(Paragraph(slots_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Spells by level
    spells = character.get('spells', {})
    
    # Cantrips
    cantrips = spells.get('cantrips', []) or spells.get('1st_level', [])
    if not isinstance(cantrips, list):
        cantrips = []
    
    if cantrips:
        story.append(Paragraph("<b>Cantrips</b>", styles['heading']))
        for spell_name in cantrips:
            spell_data = {'level': 0, 'name': spell_name}
            spell_table, description = _create_spell_table(spell_name, spell_data, styles, dnd_data)
            story.append(Paragraph(f"<b>{spell_name}</b>", styles['bold']))
            story.append(spell_table)
            if description and description != 'No description':
                # Description'ı paragraf olarak ekle
                desc_para = Paragraph(f"<i>{description[:200]}...</i>" if len(description) > 200 else f"<i>{description}</i>", styles['normal'])
                story.append(desc_para)
            story.append(Spacer(1, 0.3*cm))
        story.append(PageBreak())
    
    # Level 1-9 spells
    for level in range(1, 10):
        level_key = f"level{level}" if f"level{level}" in spells else f"{level}st_level" if level == 1 else f"{level}nd_level" if level == 2 else f"{level}rd_level" if level == 3 else f"{level}th_level"
        level_spells = spells.get(level_key, [])
        
        if level_spells:
            story.append(Paragraph(f"<b>Level {level} Spells</b>", styles['heading']))
            for spell_name in level_spells:
                spell_data = {'level': level, 'name': spell_name}
                spell_table, description = _create_spell_table(spell_name, spell_data, styles, dnd_data)
                story.append(Paragraph(f"<b>{spell_name}</b>", styles['bold']))
                story.append(spell_table)
                if description and description != 'No description':
                    desc_para = Paragraph(f"<i>{description[:200]}...</i>" if len(description) > 200 else f"<i>{description}</i>", styles['normal'])
                    story.append(desc_para)
                story.append(Spacer(1, 0.3*cm))
            story.append(PageBreak())
    
    # PDF'i oluştur
    doc.build(story)


PDF export için template ve layout iyileştirmeleri
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from typing import Optional, Dict, Any, List
import base64
from io import BytesIO


def _register_turkish_font_for_template() -> str:
    """
    Türkçe karakter desteği için font kayıt et (template için)
    """
    font_candidates = [
        Path(__file__).resolve().parents[1] / "assets" / "fonts" / "DejaVuSans.ttf",
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/arialuni.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    registered_name = "DiyargezenSans"
    for candidate in font_candidates:
        try:
            if candidate.exists():
                pdfmetrics.registerFont(TTFont(registered_name, str(candidate)))
                return registered_name
        except Exception:
            continue
    return "Helvetica"


def _get_character_image_bytes(character: dict) -> Optional[BytesIO]:
    """
    Karakter verisinden resmi al ve BytesIO olarak döndür
    """
    image_data = character.get("image")
    if not image_data:
        return None
    
    try:
        if isinstance(image_data, str) and image_data.startswith('data:'):
            header, data = image_data.split(',', 1)
            image_bytes = base64.b64decode(data)
            return BytesIO(image_bytes)
        elif isinstance(image_data, str):
            image_path = Path(image_data)
            if image_path.exists():
                with open(image_path, 'rb') as f:
                    return BytesIO(f.read())
    except Exception:
        pass
    
    return None


def _get_color_scheme(color_scheme: str = "default") -> Dict[str, str]:
    """
    Renk şeması döndür - İYİLEŞTİRİLDİ (PDF Customization)
    """
    schemes = {
        "default": {
            "primary": "#2c3e50",
            "secondary": "#34495e",
            "accent": "#3498db",
            "success": "#27ae60",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "purple": "#9b59b6"
        },
        "blue": {
            "primary": "#1a237e",
            "secondary": "#283593",
            "accent": "#3f51b5",
            "success": "#1976d2",
            "danger": "#1565c0",
            "warning": "#0d47a1",
            "purple": "#311b92"
        },
        "green": {
            "primary": "#1b5e20",
            "secondary": "#2e7d32",
            "accent": "#4caf50",
            "success": "#388e3c",
            "danger": "#2e7d32",
            "warning": "#1b5e20",
            "purple": "#4a148c"
        },
        "red": {
            "primary": "#b71c1c",
            "secondary": "#c62828",
            "accent": "#d32f2f",
            "success": "#c62828",
            "danger": "#b71c1c",
            "warning": "#d32f2f",
            "purple": "#880e4f"
        }
    }
    return schemes.get(color_scheme, schemes["default"])


def _create_styles(font_name: str, color_scheme: str = "default") -> Dict[str, ParagraphStyle]:
    """
    PDF için stil tanımlamaları oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri + Customization)
    """
    scheme = _get_color_scheme(color_scheme)
    
    styles = {}
    
    # Başlık stili
    styles['title'] = ParagraphStyle(
        'CustomTitle',
        parent=getSampleStyleSheet()['Title'],
        fontName=font_name,
        fontSize=20,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # Alt başlık stili
    styles['heading'] = ParagraphStyle(
        'CustomHeading',
        parent=getSampleStyleSheet()['Heading1'],
        fontName=font_name,
        fontSize=14,
        textColor=colors.HexColor(scheme["secondary"]),
        spaceAfter=8,
        spaceBefore=12,
        alignment=TA_LEFT
    )
    
    # Normal metin stili
    styles['normal'] = ParagraphStyle(
        'CustomNormal',
        parent=getSampleStyleSheet()['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Vurgulu metin stili
    bold_font = 'Helvetica-Bold' if font_name == 'Helvetica' else font_name
    styles['bold'] = ParagraphStyle(
        'CustomBold',
        parent=getSampleStyleSheet()['Normal'],
        fontName=bold_font,
        fontSize=10,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    return styles


def _create_ability_scores_table(character: dict, styles: Dict[str, ParagraphStyle], color_scheme: str = "default") -> Table:
    """
    Ability Scores tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    abilities = character.get('abilities', {})
    mods = character.get('ability_modifiers', {})
    
    ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    ability_short = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    
    data = [["Yetenek", "Kısa", "Puan", "Mod"]]
    
    for i, ability in enumerate(ability_names):
        if ability in abilities:
            score = abilities[ability]
            modifier = mods.get(ability, 0)
            data.append([
                ability,
                ability_short[i],
                str(score),
                f"{modifier:+d}"
            ])
    
    table = Table(data, colWidths=[3*cm, 1.5*cm, 1.5*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _create_combat_stats_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Combat Statistics tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    data = [
        ["Savaş İstatistikleri", "Değer"],
        ["Armor Class (AC)", str(character.get('armor_class', 10))],
        ["Hit Points (HP)", str(character.get('hp_max', 8))],
        ["Hit Dice", character.get('hit_dice', 'd8')],
        ["Speed", f"{character.get('speed', 30)} ft"],
        ["Initiative", f"{character.get('initiative', 0):+d}"],
        ["Passive Perception", str(character.get('passive_perception', 10))],
    ]
    
    # Movement speed ve encumbrance bilgileri ekle
    if 'movement_speed' in character:
        data.append(["Movement Speed", f"{character['movement_speed']} ft"])
    
    table = Table(data, colWidths=[4*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff5f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffcccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffafa')]),
    ]))
    
    return table


def _create_saving_throws_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Saving Throws tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    save_mods = character.get('saving_throw_modifiers', {})
    proficient_saves = character.get('saving_throws', [])
    
    ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    ability_short = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    
    data = [["Yetenek", "Kısa", "Mod", "Uzman"]]
    
    for i, ability in enumerate(ability_names):
        modifier = save_mods.get(ability, 0)
        is_proficient = ability in proficient_saves
        proficient_mark = "✓" if is_proficient else ""
        data.append([
            ability,
            ability_short[i],
            f"{modifier:+d}",
            proficient_mark
        ])
    
    table = Table(data, colWidths=[3*cm, 1.5*cm, 1.5*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ebf5fb')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#aed6f1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _create_skills_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Skills tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    skills = character.get('skills', {})
    
    if not skills:
        return None
    
    data = [["Beceri", "Mod", "Uzman"]]
    
    # Skills'i alfabetik sırala
    for skill_name in sorted(skills.keys()):
        skill_mod = skills[skill_name]
        # Expertise kontrolü (2x proficiency için)
        is_expertise = skill_mod >= 5  # Basit kontrol, gerçekte expertise listesi kontrol edilmeli
        expertise_mark = "✓✓" if is_expertise else "✓" if skill_mod > 0 else ""
        data.append([
            skill_name,
            f"{skill_mod:+d}",
            expertise_mark
        ])
    
    table = Table(data, colWidths=[4*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eafaf1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#a9dfbf')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _build_standard_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Standard template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    """
    story = []
    
    # Başlık
    title_text = f"🎲 Diyargezen - D&D 5e Karakter Kağıdı"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.3*cm))
    
    # Karakter adı ve temel bilgiler
    char_name = character.get('name', 'İsimsiz Karakter')
    char_info = f"<b>{char_name}</b> | Level {character.get('level', 1)} | {character.get('race', '')} {character.get('class', '')}"
    if character.get('background'):
        char_info += f" | {character.get('background', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Default options
    if options is None:
        options = {"show_abilities": True, "show_combat_stats": True, "show_saving_throws": True, 
                   "show_skills": True, "show_equipment": True, "show_spells": True}
    
    # Ability Scores tablosu
    if options.get("show_abilities", True):
        story.append(Paragraph("<b>Yetenek Puanları</b>", styles['heading']))
        ability_table = _create_ability_scores_table(character, styles)
        story.append(ability_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Combat Statistics tablosu
    if options.get("show_combat_stats", True):
        story.append(Paragraph("<b>Savaş İstatistikleri</b>", styles['heading']))
        combat_table = _create_combat_stats_table(character, styles)
        story.append(combat_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Saving Throws tablosu
    if options.get("show_saving_throws", True):
        story.append(Paragraph("<b>Kurtarış Atışları</b>", styles['heading']))
        saves_table = _create_saving_throws_table(character, styles)
        story.append(saves_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Skills tablosu
    if options.get("show_skills", True):
        skills_table = _create_skills_table(character, styles)
        if skills_table:
            story.append(Paragraph("<b>Beceriler</b>", styles['heading']))
            story.append(skills_table)
            story.append(Spacer(1, 0.5*cm))
    
    # Equipment
    if options.get("show_equipment", True):
        equipment = character.get('equipment', [])
        if equipment:
            story.append(Paragraph("<b>Ekipman</b>", styles['heading']))
            eq_items = []
            for item in equipment[:10]:  # İlk 10 item
                if isinstance(item, dict):
                    item_name = item.get('name', str(item))
                    quantity = item.get('quantity', 1)
                    if quantity > 1:
                        eq_items.append(f"{item_name} x{quantity}")
                    else:
                        eq_items.append(item_name)
                else:
                    eq_items.append(str(item))
            
            eq_text = ", ".join(eq_items)
            if len(equipment) > 10:
                eq_text += f" ... ve {len(equipment) - 10} daha"
            story.append(Paragraph(eq_text, styles['normal']))
            story.append(Spacer(1, 0.3*cm))
    
    # Spells (kısa özet)
    if options.get("show_spells", True):
        spells = character.get('spells', {})
        if spells:
            story.append(Paragraph("<b>Büyüler (Özet)</b>", styles['heading']))
            spell_text = ""
            
            # Cantrips
            cantrips = spells.get('cantrips') or spells.get('1st_level') or []
            if cantrips:
                if isinstance(cantrips, list):
                    spell_text += f"<b>Cantrips:</b> {', '.join(cantrips[:5])}"
                    if len(cantrips) > 5:
                        spell_text += f" ... ve {len(cantrips) - 5} daha"
                else:
                    spell_text += f"<b>Cantrips:</b> {cantrips}"
            
            # Level 1 spells
            level1 = spells.get('level1') or spells.get('1st_level') or []
            if level1:
                if spell_text:
                    spell_text += "<br/>"
                if isinstance(level1, list):
                    spell_text += f"<b>Level 1:</b> {', '.join(level1[:5])}"
                    if len(level1) > 5:
                        spell_text += f" ... ve {len(level1) - 5} daha"
                else:
                    spell_text += f"<b>Level 1:</b> {level1}"
            
            if spell_text:
                story.append(Paragraph(spell_text, styles['normal']))
                story.append(Spacer(1, 0.3*cm))
    
    return story


def _build_compact_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Compact template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    Daha az detay, daha kompakt düzen
    """
    story = []
    
    # Başlık (daha küçük)
    title_text = f"🎲 Diyargezen - D&D 5e"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.2*cm))
    
    # Karakter adı ve temel bilgiler (tek satır)
    char_name = character.get('name', 'İsimsiz Karakter')
    char_info = f"<b>{char_name}</b> | Lv.{character.get('level', 1)} | {character.get('race', '')} {character.get('class', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.3*cm))
    
    # Ability Scores ve Combat Stats yan yana (2 kolon)
    # Bu için daha küçük tablolar oluştur
    story.append(Paragraph("<b>Yetenek Puanları & Savaş İstatistikleri</b>", styles['heading']))
    
    # Ability Scores (kompakt)
    abilities = character.get('abilities', {})
    mods = character.get('ability_modifiers', {})
    ability_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    ability_full = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    ability_data = [["Yetenek", "Puan", "Mod"]]
    for i, ability in enumerate(ability_full):
        if ability in abilities:
            ability_data.append([
                ability_names[i],
                str(abilities[ability]),
                f"{mods.get(ability, 0):+d}"
            ])
    
    ability_table = Table(ability_data, colWidths=[1.5*cm, 1.5*cm, 1.5*cm])
    ability_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
    ]))
    
    # Combat Stats (kompakt)
    combat_data = [
        ["AC", str(character.get('armor_class', 10))],
        ["HP", str(character.get('hp_max', 8))],
        ["Speed", f"{character.get('speed', 30)} ft"],
        ["Init", f"{character.get('initiative', 0):+d}"],
    ]
    
    combat_table = Table(combat_data, colWidths=[2*cm, 2*cm])
    combat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffcccc')),
    ]))
    
    # İki tabloyu yan yana koy (basit yaklaşım: alt alta)
    story.append(ability_table)
    story.append(Spacer(1, 0.2*cm))
    story.append(combat_table)
    story.append(Spacer(1, 0.3*cm))
    
    # Skills (kompakt, sadece proficient olanlar)
    skills = character.get('skills', {})
    if skills and isinstance(skills, dict):
        proficient_skills = [skill for skill, mod in skills.items() if mod > 0]
        if proficient_skills:
            story.append(Paragraph("<b>Beceriler (Uzman)</b>", styles['heading']))
            skills_text = ", ".join(sorted(proficient_skills))
            story.append(Paragraph(skills_text, styles['normal']))
            story.append(Spacer(1, 0.2*cm))
    
    return story


def _build_detailed_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Detailed template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    Tüm detaylar, class features, feats, vb.
    """
    story = _build_standard_template(character, styles)
    
    # Ek detaylar ekle
    # Class Features
    class_features = character.get("class_features", {})
    if class_features:
        story.append(Paragraph("<b>Sınıf Özellikleri</b>", styles['heading']))
        for level, features_data in sorted(class_features.items(), key=lambda x: int(x[0])):
            features = features_data.get("features", [])
            choices = features_data.get("choices", {})
            if features or choices:
                level_text = f"<b>Seviye {level}:</b>"
                feature_list = []
                for feature in features:
                    feature_list.append(f"• {feature}")
                for choice_type, options in choices.items():
                    feature_list.append(f"• {choice_type}: {', '.join(options)}")
                story.append(Paragraph(level_text, styles['normal']))
                for feature_item in feature_list:
                    story.append(Paragraph(feature_item, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Feats
    feats = character.get("feats", [])
    if feats:
        story.append(Paragraph("<b>Feat'ler</b>", styles['heading']))
        feat_text = " • ".join(feats)
        story.append(Paragraph(feat_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Languages
    languages = character.get('languages', [])
    if languages:
        story.append(Paragraph("<b>Diller</b>", styles['heading']))
        lang_text = ", ".join(languages)
        story.append(Paragraph(lang_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Personality Traits
    personality = character.get('personality', {})
    if personality and any(personality.values()):
        story.append(Paragraph("<b>Kişilik Özellikleri</b>", styles['heading']))
        if personality.get('trait'):
            story.append(Paragraph(f"<b>Trait:</b> {personality['trait']}", styles['normal']))
        if personality.get('ideal'):
            story.append(Paragraph(f"<b>Ideal:</b> {personality['ideal']}", styles['normal']))
        if personality.get('bond'):
            story.append(Paragraph(f"<b>Bond:</b> {personality['bond']}", styles['normal']))
        if personality.get('flaw'):
            story.append(Paragraph(f"<b>Flaw:</b> {personality['flaw']}", styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    return story


def export_dnd_character_pdf_improved(character: dict, output_path: Path, template: str = "standard", page_size: str = "A4", options: Optional[Dict[str, Any]] = None) -> None:
    """
    D&D karakterini iyileştirilmiş PDF'e yazar - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    
    Args:
        character: Karakter verisi
        output_path: PDF çıktı yolu
        template: Template adı ("standard", "compact", "detailed")
        page_size: Sayfa boyutu ("A4" veya "letter")
        options: Customization options dict:
            - show_abilities: bool (default: True)
            - show_combat_stats: bool (default: True)
            - show_saving_throws: bool (default: True)
            - show_skills: bool (default: True)
            - show_equipment: bool (default: True)
            - show_spells: bool (default: True)
            - show_features: bool (default: True) - class features, feats
            - show_personality: bool (default: True)
            - color_scheme: str (default: "default") - "default", "blue", "green", "red"
    """
    # Default options
    default_options = {
        "show_abilities": True,
        "show_combat_stats": True,
        "show_saving_throws": True,
        "show_skills": True,
        "show_equipment": True,
        "show_spells": True,
        "show_features": True,
        "show_personality": True,
        "color_scheme": "default"
    }
    
    if options:
        default_options.update(options)
    options = default_options
    
    size = A4 if page_size.upper() == "A4" else letter
    doc = SimpleDocTemplate(str(output_path), pagesize=size, 
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    
    font_name = _register_turkish_font_for_template()
    styles = _create_styles(font_name, color_scheme=options.get("color_scheme", "default"))
    
    # Template'e göre içerik oluştur (options ile)
    if template == "compact":
        story = _build_compact_template(character, styles, options)
    elif template == "detailed":
        story = _build_detailed_template(character, styles, options)
    else:  # standard
        story = _build_standard_template(character, styles, options)
    
    # PDF'i oluştur
    doc.build(story)


def _create_spell_table(spell_name: str, spell_data: dict, styles: Dict[str, ParagraphStyle], dnd_data: Optional[Dict[str, Any]] = None) -> Table:
    """
    Tek bir spell için tablo oluştur - İYİLEŞTİRİLDİ (PDF Spell Sheet)
    """
    # Spell data'yı al
    if dnd_data and 'spells' in dnd_data:
        full_spell_data = dnd_data['spells'].get(spell_name, {})
        spell_data = {**spell_data, **full_spell_data}
    
    level = spell_data.get('level', 0)
    school = spell_data.get('school', 'Unknown')
    casting_time = spell_data.get('casting_time', 'Unknown')
    range_text = spell_data.get('range', 'Unknown')
    components = spell_data.get('components', 'Unknown')
    duration = spell_data.get('duration', 'Unknown')
    description = spell_data.get('description', 'No description')
    
    # Ritual, Concentration, Material Components kontrolü
    from utils.calculations import is_ritual_spell, is_concentration_spell, extract_material_components
    
    is_ritual = is_ritual_spell(spell_name, spell_data, dnd_data)
    is_concentration = is_concentration_spell(spell_name, spell_data, dnd_data)
    material_info = extract_material_components(spell_data)
    
    # Tablo verisi
    data = [
        ["Özellik", "Değer"],
        ["Seviye", "Cantrip" if level == 0 else f"Level {level}"],
        ["Okul", school],
        ["Casting Time", casting_time],
        ["Range", range_text],
        ["Components", components],
        ["Duration", duration],
    ]
    
    # Özel özellikler
    special_features = []
    if is_ritual:
        special_features.append("Ritual")
    if is_concentration:
        special_features.append("Concentration")
    if material_info:
        material_text = material_info.get('component', '')
        if material_info.get('cost'):
            material_text += f" ({material_info['cost']})"
        if material_info.get('consumed'):
            material_text += " [Consumed]"
        special_features.append(f"Material: {material_text}")
    
    if special_features:
        data.append(["Özel Özellikler", ", ".join(special_features)])
    
    # Description (uzun metin için ayrı paragraf)
    table = Table(data, colWidths=[3*cm, 6*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f4ecf7')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d7bde2')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
    ]))
    
    return table, description


def export_dnd_spell_sheet_pdf(character: dict, output_path: Path, dnd_data: Optional[Dict[str, Any]] = None, page_size: str = "A4") -> None:
    """
    D&D karakterinin spell sheet'ini PDF'e yazar - İYİLEŞTİRİLDİ (PDF Spell Sheet)
    
    Args:
        character: Karakter verisi
        output_path: PDF çıktı yolu
        dnd_data: D&D veri yapısı (spell detayları için)
        page_size: Sayfa boyutu ("A4" veya "letter")
    """
    size = A4 if page_size.upper() == "A4" else letter
    doc = SimpleDocTemplate(str(output_path), pagesize=size, 
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    
    font_name = _register_turkish_font_for_template()
    styles = _create_styles(font_name)
    
    story = []
    
    # Başlık
    char_name = character.get('name', 'İsimsiz Karakter')
    title_text = f"🎲 Diyargezen - D&D 5e Spell Sheet: {char_name}"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.3*cm))
    
    # Karakter bilgisi
    char_info = f"Level {character.get('level', 1)} {character.get('race', '')} {character.get('class', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Spell Slots
    spell_slots = character.get('spell_slots', {})
    if spell_slots:
        story.append(Paragraph("<b>Spell Slots</b>", styles['heading']))
        slots_text = ", ".join([f"Level {level}: {slots}" for level, slots in sorted(spell_slots.items())])
        story.append(Paragraph(slots_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Spells by level
    spells = character.get('spells', {})
    
    # Cantrips
    cantrips = spells.get('cantrips', []) or spells.get('1st_level', [])
    if not isinstance(cantrips, list):
        cantrips = []
    
    if cantrips:
        story.append(Paragraph("<b>Cantrips</b>", styles['heading']))
        for spell_name in cantrips:
            spell_data = {'level': 0, 'name': spell_name}
            spell_table, description = _create_spell_table(spell_name, spell_data, styles, dnd_data)
            story.append(Paragraph(f"<b>{spell_name}</b>", styles['bold']))
            story.append(spell_table)
            if description and description != 'No description':
                # Description'ı paragraf olarak ekle
                desc_para = Paragraph(f"<i>{description[:200]}...</i>" if len(description) > 200 else f"<i>{description}</i>", styles['normal'])
                story.append(desc_para)
            story.append(Spacer(1, 0.3*cm))
        story.append(PageBreak())
    
    # Level 1-9 spells
    for level in range(1, 10):
        level_key = f"level{level}" if f"level{level}" in spells else f"{level}st_level" if level == 1 else f"{level}nd_level" if level == 2 else f"{level}rd_level" if level == 3 else f"{level}th_level"
        level_spells = spells.get(level_key, [])
        
        if level_spells:
            story.append(Paragraph(f"<b>Level {level} Spells</b>", styles['heading']))
            for spell_name in level_spells:
                spell_data = {'level': level, 'name': spell_name}
                spell_table, description = _create_spell_table(spell_name, spell_data, styles, dnd_data)
                story.append(Paragraph(f"<b>{spell_name}</b>", styles['bold']))
                story.append(spell_table)
                if description and description != 'No description':
                    desc_para = Paragraph(f"<i>{description[:200]}...</i>" if len(description) > 200 else f"<i>{description}</i>", styles['normal'])
                    story.append(desc_para)
                story.append(Spacer(1, 0.3*cm))
            story.append(PageBreak())
    
    # PDF'i oluştur
    doc.build(story)


PDF export için template ve layout iyileştirmeleri
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from typing import Optional, Dict, Any, List
import base64
from io import BytesIO


def _register_turkish_font_for_template() -> str:
    """
    Türkçe karakter desteği için font kayıt et (template için)
    """
    font_candidates = [
        Path(__file__).resolve().parents[1] / "assets" / "fonts" / "DejaVuSans.ttf",
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/arialuni.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    registered_name = "DiyargezenSans"
    for candidate in font_candidates:
        try:
            if candidate.exists():
                pdfmetrics.registerFont(TTFont(registered_name, str(candidate)))
                return registered_name
        except Exception:
            continue
    return "Helvetica"


def _get_character_image_bytes(character: dict) -> Optional[BytesIO]:
    """
    Karakter verisinden resmi al ve BytesIO olarak döndür
    """
    image_data = character.get("image")
    if not image_data:
        return None
    
    try:
        if isinstance(image_data, str) and image_data.startswith('data:'):
            header, data = image_data.split(',', 1)
            image_bytes = base64.b64decode(data)
            return BytesIO(image_bytes)
        elif isinstance(image_data, str):
            image_path = Path(image_data)
            if image_path.exists():
                with open(image_path, 'rb') as f:
                    return BytesIO(f.read())
    except Exception:
        pass
    
    return None


def _get_color_scheme(color_scheme: str = "default") -> Dict[str, str]:
    """
    Renk şeması döndür - İYİLEŞTİRİLDİ (PDF Customization)
    """
    schemes = {
        "default": {
            "primary": "#2c3e50",
            "secondary": "#34495e",
            "accent": "#3498db",
            "success": "#27ae60",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "purple": "#9b59b6"
        },
        "blue": {
            "primary": "#1a237e",
            "secondary": "#283593",
            "accent": "#3f51b5",
            "success": "#1976d2",
            "danger": "#1565c0",
            "warning": "#0d47a1",
            "purple": "#311b92"
        },
        "green": {
            "primary": "#1b5e20",
            "secondary": "#2e7d32",
            "accent": "#4caf50",
            "success": "#388e3c",
            "danger": "#2e7d32",
            "warning": "#1b5e20",
            "purple": "#4a148c"
        },
        "red": {
            "primary": "#b71c1c",
            "secondary": "#c62828",
            "accent": "#d32f2f",
            "success": "#c62828",
            "danger": "#b71c1c",
            "warning": "#d32f2f",
            "purple": "#880e4f"
        }
    }
    return schemes.get(color_scheme, schemes["default"])


def _create_styles(font_name: str, color_scheme: str = "default") -> Dict[str, ParagraphStyle]:
    """
    PDF için stil tanımlamaları oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri + Customization)
    """
    scheme = _get_color_scheme(color_scheme)
    
    styles = {}
    
    # Başlık stili
    styles['title'] = ParagraphStyle(
        'CustomTitle',
        parent=getSampleStyleSheet()['Title'],
        fontName=font_name,
        fontSize=20,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # Alt başlık stili
    styles['heading'] = ParagraphStyle(
        'CustomHeading',
        parent=getSampleStyleSheet()['Heading1'],
        fontName=font_name,
        fontSize=14,
        textColor=colors.HexColor(scheme["secondary"]),
        spaceAfter=8,
        spaceBefore=12,
        alignment=TA_LEFT
    )
    
    # Normal metin stili
    styles['normal'] = ParagraphStyle(
        'CustomNormal',
        parent=getSampleStyleSheet()['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Vurgulu metin stili
    bold_font = 'Helvetica-Bold' if font_name == 'Helvetica' else font_name
    styles['bold'] = ParagraphStyle(
        'CustomBold',
        parent=getSampleStyleSheet()['Normal'],
        fontName=bold_font,
        fontSize=10,
        textColor=colors.HexColor(scheme["primary"]),
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    return styles


def _create_ability_scores_table(character: dict, styles: Dict[str, ParagraphStyle], color_scheme: str = "default") -> Table:
    """
    Ability Scores tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    abilities = character.get('abilities', {})
    mods = character.get('ability_modifiers', {})
    
    ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    ability_short = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    
    data = [["Yetenek", "Kısa", "Puan", "Mod"]]
    
    for i, ability in enumerate(ability_names):
        if ability in abilities:
            score = abilities[ability]
            modifier = mods.get(ability, 0)
            data.append([
                ability,
                ability_short[i],
                str(score),
                f"{modifier:+d}"
            ])
    
    table = Table(data, colWidths=[3*cm, 1.5*cm, 1.5*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _create_combat_stats_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Combat Statistics tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    data = [
        ["Savaş İstatistikleri", "Değer"],
        ["Armor Class (AC)", str(character.get('armor_class', 10))],
        ["Hit Points (HP)", str(character.get('hp_max', 8))],
        ["Hit Dice", character.get('hit_dice', 'd8')],
        ["Speed", f"{character.get('speed', 30)} ft"],
        ["Initiative", f"{character.get('initiative', 0):+d}"],
        ["Passive Perception", str(character.get('passive_perception', 10))],
    ]
    
    # Movement speed ve encumbrance bilgileri ekle
    if 'movement_speed' in character:
        data.append(["Movement Speed", f"{character['movement_speed']} ft"])
    
    table = Table(data, colWidths=[4*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff5f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffcccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffafa')]),
    ]))
    
    return table


def _create_saving_throws_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Saving Throws tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    save_mods = character.get('saving_throw_modifiers', {})
    proficient_saves = character.get('saving_throws', [])
    
    ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    ability_short = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    
    data = [["Yetenek", "Kısa", "Mod", "Uzman"]]
    
    for i, ability in enumerate(ability_names):
        modifier = save_mods.get(ability, 0)
        is_proficient = ability in proficient_saves
        proficient_mark = "✓" if is_proficient else ""
        data.append([
            ability,
            ability_short[i],
            f"{modifier:+d}",
            proficient_mark
        ])
    
    table = Table(data, colWidths=[3*cm, 1.5*cm, 1.5*cm, 1.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ebf5fb')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#aed6f1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _create_skills_table(character: dict, styles: Dict[str, ParagraphStyle]) -> Table:
    """
    Skills tablosu oluştur - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    """
    skills = character.get('skills', {})
    
    if not skills:
        return None
    
    data = [["Beceri", "Mod", "Uzman"]]
    
    # Skills'i alfabetik sırala
    for skill_name in sorted(skills.keys()):
        skill_mod = skills[skill_name]
        # Expertise kontrolü (2x proficiency için)
        is_expertise = skill_mod >= 5  # Basit kontrol, gerçekte expertise listesi kontrol edilmeli
        expertise_mark = "✓✓" if is_expertise else "✓" if skill_mod > 0 else ""
        data.append([
            skill_name,
            f"{skill_mod:+d}",
            expertise_mark
        ])
    
    table = Table(data, colWidths=[4*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eafaf1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#a9dfbf')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    return table


def _build_standard_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Standard template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    """
    story = []
    
    # Başlık
    title_text = f"🎲 Diyargezen - D&D 5e Karakter Kağıdı"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.3*cm))
    
    # Karakter adı ve temel bilgiler
    char_name = character.get('name', 'İsimsiz Karakter')
    char_info = f"<b>{char_name}</b> | Level {character.get('level', 1)} | {character.get('race', '')} {character.get('class', '')}"
    if character.get('background'):
        char_info += f" | {character.get('background', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Default options
    if options is None:
        options = {"show_abilities": True, "show_combat_stats": True, "show_saving_throws": True, 
                   "show_skills": True, "show_equipment": True, "show_spells": True}
    
    # Ability Scores tablosu
    if options.get("show_abilities", True):
        story.append(Paragraph("<b>Yetenek Puanları</b>", styles['heading']))
        ability_table = _create_ability_scores_table(character, styles)
        story.append(ability_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Combat Statistics tablosu
    if options.get("show_combat_stats", True):
        story.append(Paragraph("<b>Savaş İstatistikleri</b>", styles['heading']))
        combat_table = _create_combat_stats_table(character, styles)
        story.append(combat_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Saving Throws tablosu
    if options.get("show_saving_throws", True):
        story.append(Paragraph("<b>Kurtarış Atışları</b>", styles['heading']))
        saves_table = _create_saving_throws_table(character, styles)
        story.append(saves_table)
        story.append(Spacer(1, 0.5*cm))
    
    # Skills tablosu
    if options.get("show_skills", True):
        skills_table = _create_skills_table(character, styles)
        if skills_table:
            story.append(Paragraph("<b>Beceriler</b>", styles['heading']))
            story.append(skills_table)
            story.append(Spacer(1, 0.5*cm))
    
    # Equipment
    if options.get("show_equipment", True):
        equipment = character.get('equipment', [])
        if equipment:
            story.append(Paragraph("<b>Ekipman</b>", styles['heading']))
            eq_items = []
            for item in equipment[:10]:  # İlk 10 item
                if isinstance(item, dict):
                    item_name = item.get('name', str(item))
                    quantity = item.get('quantity', 1)
                    if quantity > 1:
                        eq_items.append(f"{item_name} x{quantity}")
                    else:
                        eq_items.append(item_name)
                else:
                    eq_items.append(str(item))
            
            eq_text = ", ".join(eq_items)
            if len(equipment) > 10:
                eq_text += f" ... ve {len(equipment) - 10} daha"
            story.append(Paragraph(eq_text, styles['normal']))
            story.append(Spacer(1, 0.3*cm))
    
    # Spells (kısa özet)
    if options.get("show_spells", True):
        spells = character.get('spells', {})
        if spells:
            story.append(Paragraph("<b>Büyüler (Özet)</b>", styles['heading']))
            spell_text = ""
            
            # Cantrips
            cantrips = spells.get('cantrips') or spells.get('1st_level') or []
            if cantrips:
                if isinstance(cantrips, list):
                    spell_text += f"<b>Cantrips:</b> {', '.join(cantrips[:5])}"
                    if len(cantrips) > 5:
                        spell_text += f" ... ve {len(cantrips) - 5} daha"
                else:
                    spell_text += f"<b>Cantrips:</b> {cantrips}"
            
            # Level 1 spells
            level1 = spells.get('level1') or spells.get('1st_level') or []
            if level1:
                if spell_text:
                    spell_text += "<br/>"
                if isinstance(level1, list):
                    spell_text += f"<b>Level 1:</b> {', '.join(level1[:5])}"
                    if len(level1) > 5:
                        spell_text += f" ... ve {len(level1) - 5} daha"
                else:
                    spell_text += f"<b>Level 1:</b> {level1}"
            
            if spell_text:
                story.append(Paragraph(spell_text, styles['normal']))
                story.append(Spacer(1, 0.3*cm))
    
    return story


def _build_compact_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Compact template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    Daha az detay, daha kompakt düzen
    """
    story = []
    
    # Başlık (daha küçük)
    title_text = f"🎲 Diyargezen - D&D 5e"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.2*cm))
    
    # Karakter adı ve temel bilgiler (tek satır)
    char_name = character.get('name', 'İsimsiz Karakter')
    char_info = f"<b>{char_name}</b> | Lv.{character.get('level', 1)} | {character.get('race', '')} {character.get('class', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.3*cm))
    
    # Ability Scores ve Combat Stats yan yana (2 kolon)
    # Bu için daha küçük tablolar oluştur
    story.append(Paragraph("<b>Yetenek Puanları & Savaş İstatistikleri</b>", styles['heading']))
    
    # Ability Scores (kompakt)
    abilities = character.get('abilities', {})
    mods = character.get('ability_modifiers', {})
    ability_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    ability_full = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    ability_data = [["Yetenek", "Puan", "Mod"]]
    for i, ability in enumerate(ability_full):
        if ability in abilities:
            ability_data.append([
                ability_names[i],
                str(abilities[ability]),
                f"{mods.get(ability, 0):+d}"
            ])
    
    ability_table = Table(ability_data, colWidths=[1.5*cm, 1.5*cm, 1.5*cm])
    ability_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
    ]))
    
    # Combat Stats (kompakt)
    combat_data = [
        ["AC", str(character.get('armor_class', 10))],
        ["HP", str(character.get('hp_max', 8))],
        ["Speed", f"{character.get('speed', 30)} ft"],
        ["Init", f"{character.get('initiative', 0):+d}"],
    ]
    
    combat_table = Table(combat_data, colWidths=[2*cm, 2*cm])
    combat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffcccc')),
    ]))
    
    # İki tabloyu yan yana koy (basit yaklaşım: alt alta)
    story.append(ability_table)
    story.append(Spacer(1, 0.2*cm))
    story.append(combat_table)
    story.append(Spacer(1, 0.3*cm))
    
    # Skills (kompakt, sadece proficient olanlar)
    skills = character.get('skills', {})
    if skills and isinstance(skills, dict):
        proficient_skills = [skill for skill, mod in skills.items() if mod > 0]
        if proficient_skills:
            story.append(Paragraph("<b>Beceriler (Uzman)</b>", styles['heading']))
            skills_text = ", ".join(sorted(proficient_skills))
            story.append(Paragraph(skills_text, styles['normal']))
            story.append(Spacer(1, 0.2*cm))
    
    return story


def _build_detailed_template(character: dict, styles: Dict[str, ParagraphStyle], options: Optional[Dict[str, Any]] = None) -> List:
    """
    Detailed template içeriği oluştur - İYİLEŞTİRİLDİ (PDF Templates)
    Tüm detaylar, class features, feats, vb.
    """
    story = _build_standard_template(character, styles)
    
    # Ek detaylar ekle
    # Class Features
    class_features = character.get("class_features", {})
    if class_features:
        story.append(Paragraph("<b>Sınıf Özellikleri</b>", styles['heading']))
        for level, features_data in sorted(class_features.items(), key=lambda x: int(x[0])):
            features = features_data.get("features", [])
            choices = features_data.get("choices", {})
            if features or choices:
                level_text = f"<b>Seviye {level}:</b>"
                feature_list = []
                for feature in features:
                    feature_list.append(f"• {feature}")
                for choice_type, options in choices.items():
                    feature_list.append(f"• {choice_type}: {', '.join(options)}")
                story.append(Paragraph(level_text, styles['normal']))
                for feature_item in feature_list:
                    story.append(Paragraph(feature_item, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Feats
    feats = character.get("feats", [])
    if feats:
        story.append(Paragraph("<b>Feat'ler</b>", styles['heading']))
        feat_text = " • ".join(feats)
        story.append(Paragraph(feat_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Languages
    languages = character.get('languages', [])
    if languages:
        story.append(Paragraph("<b>Diller</b>", styles['heading']))
        lang_text = ", ".join(languages)
        story.append(Paragraph(lang_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Personality Traits
    personality = character.get('personality', {})
    if personality and any(personality.values()):
        story.append(Paragraph("<b>Kişilik Özellikleri</b>", styles['heading']))
        if personality.get('trait'):
            story.append(Paragraph(f"<b>Trait:</b> {personality['trait']}", styles['normal']))
        if personality.get('ideal'):
            story.append(Paragraph(f"<b>Ideal:</b> {personality['ideal']}", styles['normal']))
        if personality.get('bond'):
            story.append(Paragraph(f"<b>Bond:</b> {personality['bond']}", styles['normal']))
        if personality.get('flaw'):
            story.append(Paragraph(f"<b>Flaw:</b> {personality['flaw']}", styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    return story


def export_dnd_character_pdf_improved(character: dict, output_path: Path, template: str = "standard", page_size: str = "A4", options: Optional[Dict[str, Any]] = None) -> None:
    """
    D&D karakterini iyileştirilmiş PDF'e yazar - İYİLEŞTİRİLDİ (PDF Layout İyileştirmeleri)
    
    Args:
        character: Karakter verisi
        output_path: PDF çıktı yolu
        template: Template adı ("standard", "compact", "detailed")
        page_size: Sayfa boyutu ("A4" veya "letter")
        options: Customization options dict:
            - show_abilities: bool (default: True)
            - show_combat_stats: bool (default: True)
            - show_saving_throws: bool (default: True)
            - show_skills: bool (default: True)
            - show_equipment: bool (default: True)
            - show_spells: bool (default: True)
            - show_features: bool (default: True) - class features, feats
            - show_personality: bool (default: True)
            - color_scheme: str (default: "default") - "default", "blue", "green", "red"
    """
    # Default options
    default_options = {
        "show_abilities": True,
        "show_combat_stats": True,
        "show_saving_throws": True,
        "show_skills": True,
        "show_equipment": True,
        "show_spells": True,
        "show_features": True,
        "show_personality": True,
        "color_scheme": "default"
    }
    
    if options:
        default_options.update(options)
    options = default_options
    
    size = A4 if page_size.upper() == "A4" else letter
    doc = SimpleDocTemplate(str(output_path), pagesize=size, 
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    
    font_name = _register_turkish_font_for_template()
    styles = _create_styles(font_name, color_scheme=options.get("color_scheme", "default"))
    
    # Template'e göre içerik oluştur (options ile)
    if template == "compact":
        story = _build_compact_template(character, styles, options)
    elif template == "detailed":
        story = _build_detailed_template(character, styles, options)
    else:  # standard
        story = _build_standard_template(character, styles, options)
    
    # PDF'i oluştur
    doc.build(story)


def _create_spell_table(spell_name: str, spell_data: dict, styles: Dict[str, ParagraphStyle], dnd_data: Optional[Dict[str, Any]] = None) -> Table:
    """
    Tek bir spell için tablo oluştur - İYİLEŞTİRİLDİ (PDF Spell Sheet)
    """
    # Spell data'yı al
    if dnd_data and 'spells' in dnd_data:
        full_spell_data = dnd_data['spells'].get(spell_name, {})
        spell_data = {**spell_data, **full_spell_data}
    
    level = spell_data.get('level', 0)
    school = spell_data.get('school', 'Unknown')
    casting_time = spell_data.get('casting_time', 'Unknown')
    range_text = spell_data.get('range', 'Unknown')
    components = spell_data.get('components', 'Unknown')
    duration = spell_data.get('duration', 'Unknown')
    description = spell_data.get('description', 'No description')
    
    # Ritual, Concentration, Material Components kontrolü
    from utils.calculations import is_ritual_spell, is_concentration_spell, extract_material_components
    
    is_ritual = is_ritual_spell(spell_name, spell_data, dnd_data)
    is_concentration = is_concentration_spell(spell_name, spell_data, dnd_data)
    material_info = extract_material_components(spell_data)
    
    # Tablo verisi
    data = [
        ["Özellik", "Değer"],
        ["Seviye", "Cantrip" if level == 0 else f"Level {level}"],
        ["Okul", school],
        ["Casting Time", casting_time],
        ["Range", range_text],
        ["Components", components],
        ["Duration", duration],
    ]
    
    # Özel özellikler
    special_features = []
    if is_ritual:
        special_features.append("Ritual")
    if is_concentration:
        special_features.append("Concentration")
    if material_info:
        material_text = material_info.get('component', '')
        if material_info.get('cost'):
            material_text += f" ({material_info['cost']})"
        if material_info.get('consumed'):
            material_text += " [Consumed]"
        special_features.append(f"Material: {material_text}")
    
    if special_features:
        data.append(["Özel Özellikler", ", ".join(special_features)])
    
    # Description (uzun metin için ayrı paragraf)
    table = Table(data, colWidths=[3*cm, 6*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f4ecf7')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d7bde2')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
    ]))
    
    return table, description


def export_dnd_spell_sheet_pdf(character: dict, output_path: Path, dnd_data: Optional[Dict[str, Any]] = None, page_size: str = "A4") -> None:
    """
    D&D karakterinin spell sheet'ini PDF'e yazar - İYİLEŞTİRİLDİ (PDF Spell Sheet)
    
    Args:
        character: Karakter verisi
        output_path: PDF çıktı yolu
        dnd_data: D&D veri yapısı (spell detayları için)
        page_size: Sayfa boyutu ("A4" veya "letter")
    """
    size = A4 if page_size.upper() == "A4" else letter
    doc = SimpleDocTemplate(str(output_path), pagesize=size, 
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=1*cm, bottomMargin=1*cm)
    
    font_name = _register_turkish_font_for_template()
    styles = _create_styles(font_name)
    
    story = []
    
    # Başlık
    char_name = character.get('name', 'İsimsiz Karakter')
    title_text = f"🎲 Diyargezen - D&D 5e Spell Sheet: {char_name}"
    story.append(Paragraph(title_text, styles['title']))
    story.append(Spacer(1, 0.3*cm))
    
    # Karakter bilgisi
    char_info = f"Level {character.get('level', 1)} {character.get('race', '')} {character.get('class', '')}"
    story.append(Paragraph(char_info, styles['normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Spell Slots
    spell_slots = character.get('spell_slots', {})
    if spell_slots:
        story.append(Paragraph("<b>Spell Slots</b>", styles['heading']))
        slots_text = ", ".join([f"Level {level}: {slots}" for level, slots in sorted(spell_slots.items())])
        story.append(Paragraph(slots_text, styles['normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Spells by level
    spells = character.get('spells', {})
    
    # Cantrips
    cantrips = spells.get('cantrips', []) or spells.get('1st_level', [])
    if not isinstance(cantrips, list):
        cantrips = []
    
    if cantrips:
        story.append(Paragraph("<b>Cantrips</b>", styles['heading']))
        for spell_name in cantrips:
            spell_data = {'level': 0, 'name': spell_name}
            spell_table, description = _create_spell_table(spell_name, spell_data, styles, dnd_data)
            story.append(Paragraph(f"<b>{spell_name}</b>", styles['bold']))
            story.append(spell_table)
            if description and description != 'No description':
                # Description'ı paragraf olarak ekle
                desc_para = Paragraph(f"<i>{description[:200]}...</i>" if len(description) > 200 else f"<i>{description}</i>", styles['normal'])
                story.append(desc_para)
            story.append(Spacer(1, 0.3*cm))
        story.append(PageBreak())
    
    # Level 1-9 spells
    for level in range(1, 10):
        level_key = f"level{level}" if f"level{level}" in spells else f"{level}st_level" if level == 1 else f"{level}nd_level" if level == 2 else f"{level}rd_level" if level == 3 else f"{level}th_level"
        level_spells = spells.get(level_key, [])
        
        if level_spells:
            story.append(Paragraph(f"<b>Level {level} Spells</b>", styles['heading']))
            for spell_name in level_spells:
                spell_data = {'level': level, 'name': spell_name}
                spell_table, description = _create_spell_table(spell_name, spell_data, styles, dnd_data)
                story.append(Paragraph(f"<b>{spell_name}</b>", styles['bold']))
                story.append(spell_table)
                if description and description != 'No description':
                    desc_para = Paragraph(f"<i>{description[:200]}...</i>" if len(description) > 200 else f"<i>{description}</i>", styles['normal'])
                    story.append(desc_para)
                story.append(Spacer(1, 0.3*cm))
            story.append(PageBreak())
    
    # PDF'i oluştur
    doc.build(story)

