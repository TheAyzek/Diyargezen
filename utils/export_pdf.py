from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pathlib import Path
from typing import Optional, Dict, Any, List
import base64
from io import BytesIO


def _get_character_image_bytes(character: dict) -> Optional[BytesIO]:
    """Karakter verisinden resmi al ve BytesIO olarak dondur"""
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


def _draw_character_image(c: canvas.Canvas, character: dict, width: float, height: float, x_offset: float = 0.5, y_offset: float = 0.5):
    """Karakter resmini PDF'e ekle"""
    image_bytes = _get_character_image_bytes(character)
    if not image_bytes:
        return
    try:
        from PIL import Image
        img = Image.open(image_bytes)
        img_width, img_height = img.size
        max_size = 2 * inch
        scale = min(max_size / img_width, max_size / img_height, 1.0)
        display_width = img_width * scale
        display_height = img_height * scale
        x = width - display_width - (x_offset * inch)
        y = height - display_height - (y_offset * inch)
        image_bytes.seek(0)
        image_reader = ImageReader(image_bytes)
        c.drawImage(image_reader, x, y, width=display_width, height=display_height, preserveAspectRatio=True)
    except Exception:
        pass


def _register_turkish_font() -> str:
    """Turkce karakter destegi icin TrueType font kayit et"""
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


def _create_canvas(output_path: Path, page_size: str, background_path: Optional[Path] = None):
    size = A4 if page_size.upper() == "A4" else letter
    c = canvas.Canvas(str(output_path), pagesize=size)
    width, height = size

    if background_path and background_path.exists():
        try:
            c.drawImage(str(background_path), 0, 0, width=width, height=height, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Logo
    logo_path = Path(__file__).resolve().parents[1] / "assets" / "diyargezer_logo.png"
    if logo_path.exists():
        try:
            from PIL import Image
            img = Image.open(str(logo_path))
            logo_width, logo_height = img.size
            max_size = 0.6 * inch
            scale = min(max_size / logo_width, max_size / logo_height, 1.0)
            display_w = logo_width * scale
            display_h = logo_height * scale
            logo_x = width - display_w - (0.35 * inch)
            logo_y = height - display_h - (0.35 * inch)
            logo = ImageReader(str(logo_path))
            c.drawImage(logo, logo_x, logo_y, width=display_w, height=display_h, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    return c, width, height


class PDFWriter:
    """PDF yazma islemlerini yoneten yardimci sinif"""

    def __init__(self, c: canvas.Canvas, width: float, height: float, font_name: str, margin: float = 0.5):
        self.c = c
        self.width = width
        self.height = height
        self.font_name = font_name
        self.margin = margin * inch
        self.x = self.margin
        self.y = height - self.margin
        self.min_y = self.margin + 0.3 * inch  # Alt sinir

    def _check_page_break(self, needed: float = 20):
        """Sayfa sonuna yaklasilmissa yeni sayfa olustur"""
        if self.y - needed < self.min_y:
            self.c.showPage()
            self.y = self.height - self.margin
            return True
        return False

    def title(self, text: str, size: int = 16):
        self._check_page_break(30)
        self.c.setFont(self.font_name, size)
        self.c.drawString(self.x, self.y, text)
        self.y -= size + 8

    def header(self, text: str, size: int = 13):
        self._check_page_break(25)
        self.y -= 5
        # Ince cizgi
        self.c.setStrokeColor(HexColor("#3498db"))
        self.c.setLineWidth(0.5)
        self.c.line(self.x, self.y + 2, self.width - self.margin, self.y + 2)
        self.c.setStrokeColor(HexColor("#000000"))
        self.y -= 3
        self.c.setFont(self.font_name, size)
        self.c.setFillColor(HexColor("#2c3e50"))
        self.c.drawString(self.x, self.y, text)
        self.c.setFillColor(HexColor("#000000"))
        self.y -= size + 4

    def line(self, text: str, size: int = 10, indent: int = 0, step: float = 14):
        self._check_page_break(step)
        self.c.setFont(self.font_name, size)
        self.c.drawString(self.x + indent, self.y, text)
        self.y -= step

    def key_value(self, key: str, value, indent: int = 0, size: int = 10):
        self._check_page_break(14)
        self.c.setFont(self.font_name, size)
        self.c.drawString(self.x + indent, self.y, f"{key}: {value}")
        self.y -= 14

    def two_column(self, left: str, right: str, size: int = 10):
        """Iki sutunlu satir"""
        self._check_page_break(14)
        self.c.setFont(self.font_name, size)
        mid = self.width / 2
        self.c.drawString(self.x, self.y, left)
        self.c.drawString(mid, self.y, right)
        self.y -= 14

    def three_column(self, col1: str, col2: str, col3: str, size: int = 10):
        """Uc sutunlu satir"""
        self._check_page_break(14)
        self.c.setFont(self.font_name, size)
        third = (self.width - 2 * self.margin) / 3
        self.c.drawString(self.x, self.y, col1)
        self.c.drawString(self.x + third, self.y, col2)
        self.c.drawString(self.x + 2 * third, self.y, col3)
        self.y -= 14

    def spacer(self, height: float = 8):
        self.y -= height

    def new_page(self):
        self.c.showPage()
        self.y = self.height - self.margin


def export_dnd_character_pdf(
    character: dict,
    output_path: Path,
    background_path: Optional[Path] = None,
    page_size: str = "A4",
    template: str = "standard"
) -> None:
    """
    D&D karakterini PDF'e yazar - IYILESTIRILDI
    Sayfa 1: Karakter bilgileri, istatistikler, ekipman
    Sayfa 2: Spell Sheet (spellcaster ise)
    """
    c, width, height = _create_canvas(output_path, page_size, background_path)
    font_name = _register_turkish_font()

    # Template ayarlari
    templates = {
        "compact":  {"title": 14, "header": 11, "normal": 9,  "line_sp": 12},
        "detailed": {"title": 18, "header": 14, "normal": 11, "line_sp": 16},
        "minimal":  {"title": 12, "header": 10, "normal": 8,  "line_sp": 10},
        "standard": {"title": 16, "header": 13, "normal": 10, "line_sp": 14},
    }
    tpl = templates.get(template, templates["standard"])

    _draw_character_image(c, character, width, height,
                          x_offset=0.7 if template in ["compact", "minimal"] else 0.5,
                          y_offset=0.7 if template in ["compact", "minimal"] else 0.5)

    w = PDFWriter(c, width, height, font_name)

    # ========================== SAYFA 1 ==========================
    w.title("Diyargezer - D&D 5e Karakter Kagidi", tpl["title"])

    # --- Temel Bilgiler ---
    w.header("TEMEL BILGILER", tpl["header"])
    w.two_column(
        f"Karakter: {character.get('name', 'Isimsiz')}",
        f"Seviye: {character.get('level', 1)}"
    )
    # Multiclass aware class display
    if character.get('is_multiclass') and character.get('class_levels'):
        class_parts = [f"{c} {l}" for c, l in character['class_levels'].items()]
        class_text = " / ".join(class_parts)
    else:
        class_text = character.get('class_display', character.get('class', ''))
    w.two_column(
        f"Irk: {character.get('race', '')}",
        f"Sinif: {class_text}"
    )
    if character.get('background'):
        w.two_column(
            f"Arka Plan: {character.get('background', '')}",
            f"Hiz: {character.get('speed', 30)} ft"
        )
    if character.get('alignment'):
        w.key_value("Hizalama", character['alignment'])

    # --- Yetenek Puanlari ---
    w.header("YETENEK PUANLARI", tpl["header"])
    abilities = character.get('abilities', {})
    mods = character.get('ability_modifiers', {})
    if not mods and abilities:
        mods = {k: (v - 10) // 2 for k, v in abilities.items()}

    ability_order = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    # 3 satir, 2 sutun
    for i in range(0, 6, 2):
        left_ab = ability_order[i] if i < len(ability_order) else ""
        right_ab = ability_order[i + 1] if i + 1 < len(ability_order) else ""
        left_val = f"{left_ab[:3].upper()}: {abilities.get(left_ab, 10)} ({mods.get(left_ab, 0):+d})" if left_ab else ""
        right_val = f"{right_ab[:3].upper()}: {abilities.get(right_ab, 10)} ({mods.get(right_ab, 0):+d})" if right_ab else ""
        w.two_column(left_val, right_val)

    # --- Savas Istatistikleri ---
    w.header("SAVAS ISTATISTIKLERI", tpl["header"])
    w.three_column(
        f"HP: {character.get('hit_points', character.get('hp', character.get('hp_max', '?')))}",
        f"AC: {character.get('armor_class', 10)}",
        f"Initiative: {character.get('initiative', mods.get('Dexterity', 0)):+d}"
    )
    w.two_column(
        f"Proficiency Bonus: +{character.get('proficiency_bonus', 2)}",
        f"Can Zari: {character.get('hit_die', character.get('hit_dice', ''))}"
    )

    # Saving throws
    save_mods = character.get('saving_throw_modifiers', character.get('saving_throws', {}))
    if isinstance(save_mods, dict) and save_mods:
        saves_text = "  ".join(f"{k[:3]}:{v:+d}" for k, v in save_mods.items() if isinstance(v, int))
        if saves_text:
            w.key_value("Kurtaris Atislari", saves_text)
    elif isinstance(save_mods, list) and save_mods:
        w.key_value("Kurtaris Atislari", ", ".join(save_mods))

    # Weapon attacks
    equipment_effects = character.get("equipment_effects", {})
    weapon_attacks = equipment_effects.get("weapon_attacks", [])
    if weapon_attacks and template != "minimal":
        w.spacer(4)
        w.line("Silah Saldirilari:", size=tpl["normal"])
        for atk in weapon_attacks:
            atk_str = f"  {atk['name']}: {atk['to_hit']} isabet, {atk['damage']} hasar"
            if atk.get("range"):
                atk_str += f" (menzil {atk['range']})"
            w.line(atk_str, size=tpl["normal"] - 1, indent=10)

    # --- Spellcasting ---
    spell_save_dc = character.get('spell_save_dc')
    spell_attack_bonus = character.get('spell_attack_bonus')
    spell_slots = character.get('spell_slots', {}) or {}

    if spell_save_dc is not None or spell_attack_bonus is not None or spell_slots:
        w.header("BUYU SISTEMI", tpl["header"])
        row_parts = []
        if spell_save_dc is not None:
            row_parts.append(f"Spell Save DC: {spell_save_dc}")
        if spell_attack_bonus is not None:
            row_parts.append(f"Spell Attack: +{spell_attack_bonus}")
        if row_parts:
            w.line("  ".join(row_parts))

        if spell_slots:
            slots_parts = []
            for lvl_key in sorted(spell_slots.keys(), key=lambda k: int(k) if str(k).isdigit() else 99):
                count = spell_slots[lvl_key]
                if count and int(count) > 0:
                    slots_parts.append(f"Lv{lvl_key}:{count}")
            if slots_parts:
                w.key_value("Spell Slots", "  ".join(slots_parts))

    # --- Beceriler ---
    skills = character.get('skills', {})
    if skills and template != "minimal":
        w.header("BECERILER", tpl["header"])
        skill_items = sorted(skills.items())
        for i in range(0, len(skill_items), 2):
            left = f"{skill_items[i][0]}: {skill_items[i][1]:+d}" if i < len(skill_items) else ""
            right = f"{skill_items[i+1][0]}: {skill_items[i+1][1]:+d}" if i + 1 < len(skill_items) else ""
            w.two_column(left, right)

        if 'passive_perception' in character:
            w.key_value("Pasif Algi", character['passive_perception'])

    # --- Ekipman ---
    equipment = character.get('equipment', [])
    starting_equipment = character.get('starting_equipment', [])
    all_eq = []
    for item in equipment:
        if isinstance(item, dict):
            all_eq.append(item.get('name', str(item)))
        elif isinstance(item, str):
            all_eq.append(item)
    for item in starting_equipment:
        if isinstance(item, str) and item not in all_eq:
            all_eq.append(item)

    if all_eq and template != "minimal":
        w.header("EKIPMAN", tpl["header"])
        # Uzun listeyi 2 sutun halinde goster
        for i in range(0, len(all_eq), 2):
            left = f"- {all_eq[i]}" if i < len(all_eq) else ""
            right = f"- {all_eq[i+1]}" if i + 1 < len(all_eq) else ""
            w.two_column(left, right)

        # Encumbrance
        try:
            from utils.calculations import calculate_encumbrance_details
            enc = calculate_encumbrance_details(character)
            total_w = enc.get("total_weight", 0)
            cap = enc.get("base_capacity", 0)
            if total_w > 0:
                w.key_value("Agirlik", f"{total_w:.1f} / {cap} lbs")
        except Exception:
            pass

    # --- Irk Ozellikleri & Sinif Ozellikleri ---
    traits = character.get('race_traits', [])
    if traits and template != "minimal":
        w.header("IRK OZELLIKLERI", tpl["header"])
        w.line(", ".join(traits), size=tpl["normal"] - 1)

    class_features = character.get("class_features", {})
    if class_features and template == "detailed":
        w.header("SINIF OZELLIKLERI", tpl["header"])
        for level_key, features_data in class_features.items():
            features = features_data.get("features", []) if isinstance(features_data, dict) else []
            if features:
                w.line(f"Seviye {level_key}: {', '.join(features)}", size=tpl["normal"] - 1)

    # Feats
    feats = character.get("feats", [])
    if feats:
        w.header("FEAT'LER", tpl["header"])
        w.line(", ".join(feats), size=tpl["normal"] - 1)

    # --- Diller & Araclar ---
    langs = character.get('languages', [])
    tools = character.get('tools', [])
    if (langs or tools) and template != "minimal":
        w.header("DILLER & ARACLAR", tpl["header"])
        if langs:
            w.key_value("Diller", ", ".join(langs))
        if tools:
            w.key_value("Araclar", ", ".join(tools))

    # --- Kisilik ---
    personality = character.get('personality', character.get('personal_traits', {}))
    if personality and any(personality.get(k) for k in ('trait', 'ideal', 'bond', 'flaw', 'personality_trait')) and template != "minimal":
        w.header("KISILIK", tpl["header"])
        for key, label in [('trait', 'Trait'), ('personality_trait', 'Trait'), ('ideal', 'Ideal'), ('bond', 'Bond'), ('flaw', 'Flaw')]:
            val = personality.get(key)
            if val:
                w.key_value(label, val, indent=10)

    # ========================== SAYFA 2: SPELL SHEET ==========================
    char_class = character.get('class', '')
    spellcaster_classes = ['Wizard', 'Bard', 'Cleric', 'Druid', 'Sorcerer', 'Warlock', 'Paladin', 'Ranger', 'Artificer', 'Blood Hunter']

    if char_class in spellcaster_classes and template != "minimal":
        # Spell verilerini topla
        char_spells = character.get('spells', {})
        spellbook = character.get('spellbook', [])
        prepared_spells = character.get('prepared_spells', [])

        has_spells = False
        if isinstance(char_spells, dict):
            has_spells = any(isinstance(v, list) and v for v in char_spells.values())
        elif isinstance(char_spells, list):
            has_spells = bool(char_spells)
        if spellbook:
            has_spells = True
        if prepared_spells:
            has_spells = True

        if has_spells:
            w.new_page()
            w.title(f"Buyu Sayfasi - {character.get('name', '')}", tpl["title"])

            # Spellcasting bilgileri
            w.header("BUYU BILGILERI", tpl["header"])
            info_parts = [f"Sinif: {char_class}"]
            if spell_save_dc is not None:
                info_parts.append(f"Save DC: {spell_save_dc}")
            if spell_attack_bonus is not None:
                info_parts.append(f"Attack: +{spell_attack_bonus}")
            w.line("  |  ".join(info_parts))

            if spell_slots:
                slots_line = "Spell Slots: " + "  ".join(
                    f"Lv{k}:{v}" for k, v in sorted(
                        ((k, v) for k, v in spell_slots.items() if str(k).isdigit() and int(v) > 0),
                        key=lambda x: int(x[0])
                    )
                )
                w.line(slots_line)

            # Hazirlanmis buyuler
            if prepared_spells:
                if isinstance(prepared_spells, dict):
                    flat = []
                    for v in prepared_spells.values():
                        if isinstance(v, list):
                            flat.extend(v)
                    prepared_spells = flat

                w.header("HAZIRLANMIS BUYULER", tpl["header"])
                for sp in prepared_spells:
                    w.line(f"  - {sp}", size=tpl["normal"] - 1, indent=10)

            # Spellbook (Wizard)
            if spellbook:
                if isinstance(spellbook, dict):
                    w.header("SPELLBOOK", tpl["header"])
                    for lvl_key in sorted(spellbook.keys(), key=lambda k: int(k) if str(k).isdigit() else 99):
                        sp_list = spellbook[lvl_key]
                        if isinstance(sp_list, list) and sp_list:
                            lvl_label = "Cantrip" if str(lvl_key) == "0" else f"Level {lvl_key}"
                            w.line(f"{lvl_label}:", size=tpl["normal"])
                            for sp in sp_list:
                                w.line(f"  - {sp}", size=tpl["normal"] - 1, indent=15)
                elif isinstance(spellbook, list):
                    w.header("SPELLBOOK", tpl["header"])
                    for sp in spellbook:
                        w.line(f"  - {sp}", size=tpl["normal"] - 1, indent=10)

            # Bilinen buyuler (level bazli)
            if isinstance(char_spells, dict):
                w.header("BILINEN BUYULER", tpl["header"])
                for lvl_key in sorted(char_spells.keys(), key=lambda k: int(k) if str(k).isdigit() else 99):
                    sp_list = char_spells[lvl_key]
                    if isinstance(sp_list, list) and sp_list:
                        if str(lvl_key) in ("0", "cantrips"):
                            lvl_label = "Cantrip"
                        else:
                            lvl_label = f"Level {lvl_key}"
                        w.line(f"{lvl_label}:", size=tpl["normal"])
                        for sp in sp_list:
                            w.line(f"  - {sp}", size=tpl["normal"] - 1, indent=15)
            elif isinstance(char_spells, list) and char_spells:
                w.header("BILINEN BUYULER", tpl["header"])
                for sp in char_spells:
                    w.line(f"  - {sp}", size=tpl["normal"] - 1, indent=10)

    c.showPage()
    c.save()


def export_mm_character_pdf(character: dict, output_path: Path, background_path: Optional[Path] = None, page_size: str = "A4") -> None:
    """M&M karakterini ozetleyen PDF."""
    c, width, height = _create_canvas(output_path, page_size, background_path)
    _draw_character_image(c, character, width, height)
    font_name = _register_turkish_font()
    w = PDFWriter(c, width, height, font_name)

    w.title("Diyargezer - M&M Karakter Ozeti", 16)
    w.header("TEMEL BILGILER")
    w.two_column(
        f"Karakter: {character.get('name', 'Isimsiz')}",
        f"Kod Adi: {character.get('codename', '-')}"
    )
    w.two_column(
        f"Power Level: {character.get('power_level', '-')}",
        f"Arketip: {character.get('archetype', '-')}"
    )

    w.header("ABILITY SCORES")
    for ability, value in character.get("abilities", {}).items():
        w.key_value(ability, value, indent=10)

    w.header("DEFENSES")
    for key, label in [("attack_bonus", "Attack Bonus"), ("effect_rank", "Effect Rank"),
                       ("defense", "Defense"), ("toughness", "Toughness")]:
        w.key_value(label, character.get('defenses', {}).get(key, 0), indent=10)
    w.key_value("Power Points", character.get('power_points', 0))

    powers = character.get("powers", [])
    if powers:
        w.header("POWERS")
        for power in powers:
            w.line(f"  - {power}", indent=10)

    advantages = character.get("advantages", [])
    if advantages:
        w.header("ADVANTAGES")
        for adv in advantages:
            w.line(f"  - {adv}", indent=10)

    notes = character.get("notes")
    if notes:
        w.header("NOTLAR")
        for line in notes.splitlines():
            w.line(f"  {line}", indent=10)

    c.showPage()
    c.save()

