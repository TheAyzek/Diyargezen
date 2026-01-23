from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from typing import Optional
import base64
from io import BytesIO


def _get_character_image_bytes(character: dict) -> Optional[BytesIO]:
    """
    Karakter verisinden resmi al ve BytesIO olarak döndür (PDF için)
    
    Args:
        character: Karakter verisi
    
    Returns:
        BytesIO veya None
    """
    image_data = character.get("image")
    if not image_data:
        return None
    
    try:
        if isinstance(image_data, str) and image_data.startswith('data:'):
            # Base64 string
            header, data = image_data.split(',', 1)
            image_bytes = base64.b64decode(data)
            return BytesIO(image_bytes)
        elif isinstance(image_data, str):
            # Dosya yolu (geriye uyumluluk)
            image_path = Path(image_data)
            if image_path.exists():
                with open(image_path, 'rb') as f:
                    return BytesIO(f.read())
    except Exception:
        pass
    
    return None


def _draw_character_image(c: canvas.Canvas, character: dict, width: float, height: float, x_offset: float = 0.5, y_offset: float = 0.5):
    """
    Karakter resmini PDF'e ekle
    
    Args:
        c: ReportLab canvas
        character: Karakter verisi
        width: Sayfa genişliği
        height: Sayfa yüksekliği
        x_offset: X offset (inch cinsinden)
        y_offset: Y offset (inch cinsinden)
    """
    image_bytes = _get_character_image_bytes(character)
    if not image_bytes:
        return
    
    try:
        from PIL import Image
        # Resmi yükle ve boyutlarını al
        img = Image.open(image_bytes)
        img_width, img_height = img.size
        
        # Resim boyutunu ayarla (maksimum 2 inch genişlik/yükseklik)
        max_size = 2 * inch
        scale = min(max_size / img_width, max_size / img_height, 1.0)
        display_width = img_width * scale
        display_height = img_height * scale
        
        # Sağ üst köşeye yerleştir
        x = width - display_width - (x_offset * inch)
        y = height - display_height - (y_offset * inch)
        
        # BytesIO'yu başa al (ImageReader için)
        image_bytes.seek(0)
        image_reader = ImageReader(image_bytes)
        
        # Resmi PDF'e ekle
        c.drawImage(image_reader, x, y, width=display_width, height=display_height, preserveAspectRatio=True)
    except Exception:
        # Resim eklenemezse sessizce devam et
        pass


def _register_turkish_font() -> str:
    """
    Türkçe karakter desteği için bir TrueType fontu kayıt eder.
    Öncelikle projedeki bir font dosyasına, ardından Windows/Linux
    sistem fontlarına bakar. Bulamazsa ReportLab'ın varsayılanını döner.
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
            # Bir font başarısız olursa diğerini dene
            continue
    return "Helvetica"  # Fallback (Unicode kısıtlı olabilir)


def _create_canvas(output_path: Path, page_size: str, background_path: Optional[Path] = None):
    size = A4 if page_size.upper() == "A4" else letter
    c = canvas.Canvas(str(output_path), pagesize=size)
    width, height = size

    # Arkaplan
    if background_path and background_path.exists():
        bg = str(background_path)
        try:
            c.drawImage(bg, 0, 0, width=width, height=height, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Küçük logo sağ üst köşede (fazla yer kaplamasın)
    logo_path = Path(__file__).resolve().parents[1] / "Gemini_Generated_Image_c510m9c510m9c510.png"
    if logo_path.exists():
        try:
            from PIL import Image
            img = Image.open(str(logo_path))
            logo_width, logo_height = img.size
            max_size = 0.6 * inch  # Çok küçük logo
            scale = min(max_size / logo_width, max_size / logo_height, 1.0)
            display_w = logo_width * scale
            display_h = logo_height * scale
            logo_x = width - display_w - (0.35 * inch)  # sağ üstten küçük boşluk
            logo_y = height - display_h - (0.35 * inch)
            logo = ImageReader(str(logo_path))
            c.drawImage(logo, logo_x, logo_y, width=display_w, height=display_h, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    return c, width, height


def export_dnd_character_pdf(character: dict, output_path: Path, background_path: Optional[Path] = None, page_size: str = "A4") -> None:
    """
    D&D karakterini basit bir PDF'e yazar. Eğer background_path verilirse görseli sayfa arkaplanı olarak yerleştirir.
    - character: dnd_creator.py'nin döndürdüğü sözlük yapısı ile uyumlu olmalı
    - output_path: oluşturulacak PDF dosyasının yolu
    - background_path: PNG/JPG veya PDF (tek sayfa) olabilir; varsa arkaplan olarak basılır
    """
    c, width, height = _create_canvas(output_path, page_size, background_path)

    font_name = _register_turkish_font()

    margin = 0.5 * inch
    x = margin
    y = height - margin

    def write_line(text: str, step: float = 14):
        nonlocal y
        c.setFont(font_name, 10)
        c.drawString(x, y, text)
        y -= step

    # Karakter resmini ekle (varsa)
    _draw_character_image(c, character, width, height, x_offset=0.5, y_offset=0.5)
    
    # Başlık
    c.setFont(font_name, 16)
    c.drawString(x, y, "🎲 Diyargezer - D&D 5e Karakter Kağıdı")
    y -= 25
    
    # Karakter adı
    c.setFont(font_name, 14)
    c.drawString(x, y, f"Karakter: {character.get('name', 'İsimsiz Karakter')}")
    y -= 20
    
    c.setFont(font_name, 10)
    write_line(f"Sistem: {character.get('system', '')}")
    write_line(f"Irk: {character.get('race', '')}")
    write_line(f"Sınıf: {character.get('class', '')}")
    if character.get('background'):
        write_line(f"Arka Plan: {character.get('background', '')}")
    write_line(f"Hız: {character.get('speed', '')}")
    write_line(f"Zırh Sınıfı: {character.get('armor_class', 10)}")
    write_line(f"Taşıma Kapasitesi: {character.get('carry_weight', 150)} lbs")
    write_line(f"Can Puanı: {character.get('hp_max', 8)}")
    
    # Equipment effects
    equipment_effects = character.get("equipment_effects", {})
    if equipment_effects.get("equipped_armor"):
        write_line(f"Zırh: {equipment_effects['equipped_armor']}")
    if equipment_effects.get("equipped_shield"):
        write_line(f"Kalkan: {equipment_effects['equipped_shield']}")
    if equipment_effects.get("stealth_disadvantage"):
        write_line("Gizlenme Dezavantajı: Evet (zırh)")
    
    # Weapon attacks
    weapon_attacks = equipment_effects.get("weapon_attacks", [])
    if weapon_attacks:
        write_line("Silah Saldırıları:")
        for attack in weapon_attacks:
            attack_str = f"  {attack['name']}: {attack['to_hit']} isabet, {attack['damage']} hasar"
            if attack.get("range"):
                attack_str += f" (menzil {attack['range']})"
            if attack.get("versatile_damage"):
                attack_str += f" / {attack['versatile_damage']} (versatile)"
            write_line(attack_str)
    
    # Magic items
    magic_items = [item for item in character.get("inventory", []) if item.get("category") == "magic_items"]
    if magic_items:
        write_line("Büyülü Eşyalar:")
        for item in magic_items:
            item_data = item.get("data", {})
            rarity = item_data.get("rarity", "unknown")
            rarity_colors = {
                "common": "Beyaz",
                "uncommon": "Yeşil", 
                "rare": "Mavi",
                "very rare": "Mor",
                "legendary": "Turuncu",
                "artifact": "Kırmızı"
            }
            rarity_text = rarity_colors.get(rarity, rarity.title())
            write_line(f"  {item['name']} ({rarity_text})")

    traits = ", ".join(character.get('race_traits', []))
    write_line(f"Irksal Özellikler: {traits}")

    abilities = character.get('abilities', {})
    mods = character.get('ability_modifiers', {})
    if abilities:
        write_line("Yetenek Puanları ve Modifikatorler:")
        for k in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
            if k in abilities:
                write_line(f"  {k}: {abilities[k]} (mod {mods.get(k, 0):+d})")

    write_line(f"Can Zarı: {character.get('hit_die', '')}")
    prim = ", ".join(character.get('primary_ability', []))
    write_line(f"Birincil Yetenek(ler): {prim}")
    saves = ", ".join(character.get('saving_throws', []))
    write_line(f"Kurtarış Atışları: {saves}")

    # Kurtarış modları
    save_mods = character.get('saving_throw_modifiers', {})
    if save_mods:
        write_line("Kurtarış Modları:")
        for ab in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
            if ab in save_mods:
                write_line(f"  {ab}: {save_mods[ab]:+d}")

    eq = ", ".join(character.get('equipment', []))
    if eq:
        write_line(f"Ekipman: {eq}")

    # Ek alanlar: hizalama, diller, araçlar, kişilik
    if character.get('alignment'):
        write_line(f"Hizalama: {character['alignment']}")
    langs = character.get('languages', [])
    if langs:
        write_line(f"Diller: {', '.join(langs)}")
    tools = character.get('tools', [])
    if tools:
        write_line(f"Araç Yeterlilikleri: {', '.join(tools)}")
    personality = character.get('personality', {})
    if any(personality.get(k) for k in ('trait','ideal','bond','flaw')):
        write_line("Kişilik:")
        if personality.get('trait'): write_line(f"  Trait: {personality['trait']}")
        if personality.get('ideal'): write_line(f"  Ideal: {personality['ideal']}")
        if personality.get('bond'): write_line(f"  Bond: {personality['bond']}")
        if personality.get('flaw'): write_line(f"  Flaw: {personality['flaw']}")

    bgf = character.get('background_features', {})
    if bgf:
        sp = ", ".join(bgf.get('skill_proficiencies', []))
        write_line("Arka Plan Özellikleri:")
        write_line(f"  Yetenek Uzmanlıkları: {sp}")
        write_line(f"  Özellik: {bgf.get('feature', '')}")

    # Beceriler ve pasif algı
    skills = character.get('skills', {})
    if skills:
        write_line("Beceriler (mod):")
        for sk in sorted(skills.keys()):
            write_line(f"  {sk}: {skills[sk]:+d}")
    if 'passive_perception' in character:
        write_line(f"Pasif Algı: {character['passive_perception']}")

    # Sınıf özel bilgiler
    class_name = character.get('class', '')
    if class_name in ('Wizard', 'Fighter', 'Rogue', 'Bard', 'Cleric', 'Druid', 'Sorcerer', 'Warlock', 'Paladin', 'Ranger', 'Monk', 'Barbarian', 'Artificer', 'Blood Hunter'):
        write_line("Sınıf Yeterlilikleri:")
        profs = character.get('class_proficiencies', {})
        for k in ('armor','weapons','tools','languages'):
            vals = ", ".join(profs.get(k, [])) if isinstance(profs.get(k, []), list) else str(profs.get(k, []))
            write_line(f"  {k.capitalize()}: {vals}")
        
        # Sınıf beceri ustalıkları
        class_skills = character.get('class_skill_proficiencies', [])
        if class_skills:
            write_line(f"Sınıf Beceri Ustalıkları: {', '.join(class_skills)}")
        
        # Expertise (Rogue)
        expertise = character.get('expertise', [])
        if expertise:
            write_line(f"Uzmanlık (Expertise): {', '.join(expertise)}")
        
        # Büyüler (büyü kullanan sınıflar)
        if class_name in ('Wizard', 'Bard', 'Cleric', 'Druid', 'Sorcerer', 'Warlock', 'Paladin', 'Ranger', 'Artificer', 'Blood Hunter'):
            spells = character.get('spells', {})
            if spells:
                write_line("Büyüler:")
                if spells.get('cantrips'):
                    write_line(f"  Cantrips: {', '.join(spells['cantrips'])}")
                if spells.get('level1'):
                    write_line(f"  Seviye 1: {', '.join(spells['level1'])}")
    
    # Sınıf özellikleri
    class_features = character.get("class_features", {})
    if class_features:
        write_line("Sınıf Özellikleri:")
        for level, features_data in class_features.items():
            features = features_data.get("features", [])
            choices = features_data.get("choices", {})
            if features or choices:
                write_line(f"  Seviye {level}:")
                for feature in features:
                    write_line(f"    - {feature}")
                for choice_type, options in choices.items():
                    write_line(f"    - {choice_type}: {', '.join(options)}")

    # Feat'ler
    feats = character.get("feats", [])
    if feats:
        write_line("Feat'ler:")
        for feat in feats:
            write_line(f"  - {feat}")

    # Kişisel özellikler
    personal_traits = character.get("personal_traits", {})
    if any(personal_traits.values()):
        write_line("Kişisel Özellikler:")
        
        # Fiziksel özellikler
        if personal_traits.get("height") or personal_traits.get("weight") or personal_traits.get("age"):
            physical = []
            if personal_traits.get("height"):
                physical.append(f"Boy: {personal_traits['height']}")
            if personal_traits.get("weight"):
                physical.append(f"Kilo: {personal_traits['weight']}")
            if personal_traits.get("age"):
                physical.append(f"Yaş: {personal_traits['age']}")
            write_line(f"  Fiziksel: {', '.join(physical)}")
        
        # Görünüm özellikleri
        if personal_traits.get("hair_color") or personal_traits.get("eye_color") or personal_traits.get("skin_color"):
            appearance = []
            if personal_traits.get("hair_color"):
                appearance.append(f"Saç: {personal_traits['hair_color']}")
            if personal_traits.get("eye_color"):
                appearance.append(f"Göz: {personal_traits['eye_color']}")
            if personal_traits.get("skin_color"):
                appearance.append(f"Ten: {personal_traits['skin_color']}")
            write_line(f"  Görünüm: {', '.join(appearance)}")
        
        # Alignment
        if personal_traits.get("alignment"):
            write_line(f"  Alignment: {personal_traits['alignment']}")
        
        # Kişilik özellikleri
        if personal_traits.get("personality_trait") or personal_traits.get("ideal") or personal_traits.get("bond") or personal_traits.get("flaw"):
            write_line("  Kişilik:")
            if personal_traits.get("personality_trait"):
                write_line(f"    Trait: {personal_traits['personality_trait']}")
            if personal_traits.get("ideal"):
                write_line(f"    Ideal: {personal_traits['ideal']}")
            if personal_traits.get("bond"):
                write_line(f"    Bond: {personal_traits['bond']}")
            if personal_traits.get("flaw"):
                write_line(f"    Flaw: {personal_traits['flaw']}")
        
        # Görünüm açıklaması
        if personal_traits.get("appearance_description"):
            write_line(f"  Açıklama: {personal_traits['appearance_description']}")
        
        # Ek diller
        if personal_traits.get("extra_languages"):
            write_line(f"  Ek Diller: {personal_traits['extra_languages']}")

    c.showPage()
    c.save()


def export_mm_character_pdf(character: dict, output_path: Path, background_path: Optional[Path] = None, page_size: str = "A4") -> None:
    """M&M karakterini özetleyen PDF."""
    c, width, height = _create_canvas(output_path, page_size, background_path)
    
    # Karakter resmini ekle (varsa)
    _draw_character_image(c, character, width, height, x_offset=0.5, y_offset=0.5)
    
    margin = 0.5 * inch
    x = margin
    y = height - margin

    def write(text: str, step: float = 14, bold: bool = False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 12 if bold else 10)
        c.drawString(x, y, text)
        y -= step

    write("🦸 Diyargezer - M&M Karakter Özeti", 18, True)
    write(f"Karakter: {character.get('name', 'İsimsiz')}  |  Kod Adı: {character.get('codename', '-')}", 16)
    write(f"Power Level: {character.get('power_level', '-')}", 16)
    write(f"Arketip: {character.get('archetype', '-')}", 16)
    write("", 12)

    write("Ability Scores:", 14, True)
    for ability, value in character.get("abilities", {}).items():
        write(f"  {ability}: {value}")

    write("", 12)
    write("Defenses:", 14, True)
    for key, label in [
        ("attack_bonus", "Attack Bonus"),
        ("effect_rank", "Effect Rank"),
        ("defense", "Defense"),
        ("toughness", "Toughness"),
    ]:
        write(f"  {label}: {character.get('defenses', {}).get(key, 0)}")
    write(f"Power Points: {character.get('power_points', 0)}")

    powers = character.get("powers", [])
    if powers:
        write("", 12)
        write("Powers:", 14, True)
        for power in powers:
            write(f"  - {power}")

    advantages = character.get("advantages", [])
    if advantages:
        write("", 12)
        write("Advantages:", 14, True)
        for adv in advantages:
            write(f"  - {adv}")

    notes = character.get("notes")
    if notes:
        write("", 12)
        write("Notlar:", 14, True)
        for line in notes.splitlines():
            write(f"  {line}")

    c.showPage()
    c.save()


def export_vtm_character_pdf(character: dict, output_path: Path, background_path: Optional[Path] = None, page_size: str = "A4") -> None:
    """VtM karakter özet PDF'i."""
    c, width, height = _create_canvas(output_path, page_size, background_path)
    
    # Karakter resmini ekle (varsa)
    _draw_character_image(c, character, width, height, x_offset=0.5, y_offset=0.5)
    
    margin = 0.5 * inch
    x = margin
    y = height - margin

    def write(text: str, step: float = 14, bold: bool = False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 12 if bold else 10)
        c.drawString(x, y, text)
        y -= step

    write("🧛 Diyargezer - VtM Karakter Özeti", 18, True)
    write(f"İsim: {character.get('name', 'İsimsiz')}  |  Clan: {character.get('clan', '-')}", 16)
    write(f"Chronicle: {character.get('chronicle', '-')}", 16)
    write(f"Concept: {character.get('concept', '-')}", 16)
    write("", 12)

    write("Attributes:", 14, True)
    for category, attrs in character.get("attributes", {}).items():
        values = ", ".join(f"{attr} {score}" for attr, score in attrs.items())
        write(f"  {category}: {values}")

    write("", 12)
    write("Skills:", 14, True)
    for category, skills in character.get("skills", {}).items():
        values = ", ".join(f"{skill} {score}" for skill, score in skills.items() if score)
        if values:
            write(f"  {category}: {values}")

    disciplines = character.get("disciplines", [])
    if disciplines:
        write("", 12)
        write("Disciplines:", 14, True)
        write(", ".join(disciplines))

    write("", 12)
    write(f"Humanity: {character.get('humanity', 0)}  |  Health: {character.get('health', 0)}  |  Willpower: {character.get('willpower', 0)}")

    notes = character.get("notes")
    if notes:
        write("", 12)
        write("Notlar:", 14, True)
        for line in notes.splitlines():
            write(f"  {line}")

    c.showPage()
    c.save()



    write("Attributes:", 14, True)
    for category, attrs in character.get("attributes", {}).items():
        values = ", ".join(f"{attr} {score}" for attr, score in attrs.items())
        write(f"  {category}: {values}")

    write("", 12)
    write("Skills:", 14, True)
    for category, skills in character.get("skills", {}).items():
        values = ", ".join(f"{skill} {score}" for skill, score in skills.items() if score)
        if values:
            write(f"  {category}: {values}")

    disciplines = character.get("disciplines", [])
    if disciplines:
        write("", 12)
        write("Disciplines:", 14, True)
        write(", ".join(disciplines))

    write("", 12)
    write(f"Humanity: {character.get('humanity', 0)}  |  Health: {character.get('health', 0)}  |  Willpower: {character.get('willpower', 0)}")

    notes = character.get("notes")
    if notes:
        write("", 12)
        write("Notlar:", 14, True)
        for line in notes.splitlines():
            write(f"  {line}")

    c.showPage()
    c.save()



    write("Attributes:", 14, True)
    for category, attrs in character.get("attributes", {}).items():
        values = ", ".join(f"{attr} {score}" for attr, score in attrs.items())
        write(f"  {category}: {values}")

    write("", 12)
    write("Skills:", 14, True)
    for category, skills in character.get("skills", {}).items():
        values = ", ".join(f"{skill} {score}" for skill, score in skills.items() if score)
        if values:
            write(f"  {category}: {values}")

    disciplines = character.get("disciplines", [])
    if disciplines:
        write("", 12)
        write("Disciplines:", 14, True)
        write(", ".join(disciplines))

    write("", 12)
    write(f"Humanity: {character.get('humanity', 0)}  |  Health: {character.get('health', 0)}  |  Willpower: {character.get('willpower', 0)}")

    notes = character.get("notes")
    if notes:
        write("", 12)
        write("Notlar:", 14, True)
        for line in notes.splitlines():
            write(f"  {line}")

    c.showPage()
    c.save()



    write("Attributes:", 14, True)
    for category, attrs in character.get("attributes", {}).items():
        values = ", ".join(f"{attr} {score}" for attr, score in attrs.items())
        write(f"  {category}: {values}")

    write("", 12)
    write("Skills:", 14, True)
    for category, skills in character.get("skills", {}).items():
        values = ", ".join(f"{skill} {score}" for skill, score in skills.items() if score)
        if values:
            write(f"  {category}: {values}")

    disciplines = character.get("disciplines", [])
    if disciplines:
        write("", 12)
        write("Disciplines:", 14, True)
        write(", ".join(disciplines))

    write("", 12)
    write(f"Humanity: {character.get('humanity', 0)}  |  Health: {character.get('health', 0)}  |  Willpower: {character.get('willpower', 0)}")

    notes = character.get("notes")
    if notes:
        write("", 12)
        write("Notlar:", 14, True)
        for line in notes.splitlines():
            write(f"  {line}")

    c.showPage()
    c.save()


