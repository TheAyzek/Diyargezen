from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
from pypdf import PdfReader, PdfWriter
import base64
import tempfile

logger = logging.getLogger(__name__)


def _get_portrait_image_path(portrait_data: str) -> Optional[Path]:
    """Decodes base64 data URL and writes to a temporary image file, returning its path."""
    if not portrait_data:
        return None
    if not isinstance(portrait_data, str):
        return None
        
    try:
        if portrait_data.startswith("data:image/"):
            # Split data URL header from base64 string
            header, base64_str = portrait_data.split(",", 1)
            # Find extension
            ext = "png"
            if "jpeg" in header or "jpg" in header:
                ext = "jpg"
            elif "webp" in header:
                ext = "webp"
            elif "gif" in header:
                ext = "gif"
        else:
            # Check if it's a file path
            try:
                path = Path(portrait_data)
                if path.exists() and path.is_file():
                    return path
            except Exception:
                pass
            return None
            
        # Clean up base64 string
        base64_str = base64_str.strip().replace(" ", "").replace("\n", "").replace("\r", "")
        
        # Auto-pad base64 string if length is not a multiple of 4
        missing_padding = len(base64_str) % 4
        if missing_padding:
            base64_str += "=" * (4 - missing_padding)
            
        img_data = base64.b64decode(base64_str)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
        temp_file.write(img_data)
        temp_file.close()
        return Path(temp_file.name)
    except Exception as e:
        logger.error(f"Error decoding portrait image: {e}")
        return None


def _stamp_portrait_on_pdf(pdf_path: Path, portrait_path: Path, system: str) -> None:
    """Stamps/draws the portrait image onto the first page of the PDF at pdf_path."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    sys_lower = system.lower()
    if "dnd" in sys_lower or "5e" in sys_lower:
        x, y, w, h = 442, 612, 118, 100
    elif "pathfinder" in sys_lower or "pf" in sys_lower:
        x, y, w, h = 380, 545, 175, 160
    elif "mm" in sys_lower or "mnm" in sys_lower:
        x, y, w, h = 412, 472, 152, 152
    else:
        x, y, w, h = 442, 612, 118, 100
        
    temp_overlay = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_overlay.close()
    overlay_path = Path(temp_overlay.name)
    
    try:
        c = canvas.Canvas(str(overlay_path), pagesize=letter)
        c.drawImage(str(portrait_path), x, y, width=w, height=h, mask='auto', preserveAspectRatio=True)
        c.showPage()
        c.save()
        
        reader = PdfReader(pdf_path)
        overlay_reader = PdfReader(overlay_path)
        
        writer = PdfWriter()
        writer.append(reader)

        if writer.pages and overlay_reader.pages:
            writer.pages[0].merge_page(overlay_reader.pages[0])
                
        with open(pdf_path, "wb") as f:
            writer.write(f)
    except Exception as e:
        logger.error(f"Error stamping portrait overlay on PDF: {e}")
    finally:
        if overlay_path.exists():
            overlay_path.unlink()


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


def _skill(char: dict, key: str, default: int = 0) -> str:
    """Karakterin beceri değerini güvenli şekilde çeker ve formatlar.
    char['skills'] sözlüğü yoksa veya key eksikse '' döndürür — asla çökmez.
    """
    try:
        skills = char.get("skills", {})
        
        def normalize_key(k: str) -> str:
            if not k:
                return ""
            val = str(k).lower().strip().replace(" ", "").replace("_", "").replace("(", "").replace(")", "")
            for prefix in ("craft", "perform", "profession"):
                if val.startswith(prefix):
                    return prefix
            return val
            
        target = normalize_key(key)
        val = None
        for k, v in skills.items():
            if normalize_key(k) == target:
                val = v
                break
        if val is None:
            val = default
        return format_mod(int(val))
    except Exception:
        return ""


def _safe_slot(char: dict, level_key: str) -> str:
    """DND5e karakter sözlüğündeki spell slot sayısını güvenle çeker.
    'spell_slots' varsa oradan, yoksa boş döner (Graceful Fail).
    Warlock Pact Magic: pact slot seviyesiyle eşleşen level_key'e yazar.
    """
    try:
        slots = char.get("spell_slots", {})
        if not slots:
            return ""
        # Warlock kontrolü: pact_slots varsa sadece pact seviyesine yaz
        if "pact_slots" in slots:
            if str(level_key) == str(slots.get("pact_slot_level", "")):
                return str(slots["pact_slots"])
            return ""
        val = slots.get(str(level_key), "")
        return str(val) if val else ""
    except Exception:
        return ""


def _safe_pf1e_concentration(char: dict) -> str:
    """PF1e Concentration bonusunu güvenle hesaplar (Graceful Fail).
    CL + casting_ability_modifier (PF1e CRB p. 206).
    Büyücü değilse veya hata olursa boş döner.
    PF2e KESİNLİKLE desteklenmez.
    """
    try:
        class_data = char.get("class_data") or {}
        casting_ability = class_data.get("spellcasting_ability", "")
        if not casting_ability:
            return ""
        level = int(char.get("level", 1))
        ab_score = get_ability(char, casting_ability.lower(), default=10)
        ab_mod = (ab_score - 10) // 2
        return format_mod(level + ab_mod)
    except Exception:
        return ""


def _format_classes_and_levels(char: dict) -> str:
    """Format single class with archetype or multiclass progression for character sheet headers."""
    mc = char.get("derived", {}).get("multiclass") or char.get("multiclass")
    if mc and isinstance(mc, dict) and len(mc) > 0:
        return " / ".join(f"{cls_name} {lvl}" for cls_name, lvl in mc.items())
    
    cls_name = char.get("class") or char.get("sinif") or ""
    arch = char.get("archetype") or char.get("derived", {}).get("archetype") or ""
    lvl = char.get("level") or char.get("seviye") or 1
    
    if arch:
        return f"{cls_name} ({arch}) {lvl}"
    return f"{cls_name} {lvl}"


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
        
        # ── DnD5e BECERİ ALANLARI (PDF'deki gerçek field isimleri) ──────────
        # Toplam beceri bonusu (modifier + proficiency bonus)
        "Acrobatics":      lambda c: _skill(c, "acrobatics"),
        "Animal":          lambda c: _skill(c, "animal_handling"),
        "Arcana":          lambda c: _skill(c, "arcana"),
        "Athletics":       lambda c: _skill(c, "athletics"),
        "Deception ":      lambda c: _skill(c, "deception"),
        "History ":        lambda c: _skill(c, "history"),
        "Insight":         lambda c: _skill(c, "insight"),
        "Intimidation":    lambda c: _skill(c, "intimidation"),
        "Investigation ": lambda c: _skill(c, "investigation"),
        "Medicine":        lambda c: _skill(c, "medicine"),
        "Nature":          lambda c: _skill(c, "nature"),
        "Perception ":     lambda c: _skill(c, "perception"),
        "Performance":     lambda c: _skill(c, "performance"),
        "Religion":        lambda c: _skill(c, "religion"),
        "SleightofHand":   lambda c: _skill(c, "sleight_of_hand"),
        "Stealth ":        lambda c: _skill(c, "stealth"),
        "Survival":        lambda c: _skill(c, "survival"),

        # Yeterlilik (Proficiency) checkbox'ları — PDF'deki sıra:
        # Check Box 11=Acrobatics, 12=AnimalHandling, 13=Arcana, 14=Athletics,
        # 15=Deception, 16=History, 17=Insight, 18=Intimidation, 19=Investigation,
        # 20=Medicine, 21=Nature, 22=Perception, 23=Performance, 24=Persuasion,
        # 25=Religion, 26=SleightOfHand, 27=Stealth, 28=Survival
        "Check Box 11": lambda c: "Yes" if "acrobatics"     in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 12": lambda c: "Yes" if "animal handling" in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 13": lambda c: "Yes" if "arcana"         in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 14": lambda c: "Yes" if "athletics"      in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 15": lambda c: "Yes" if "deception"      in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 16": lambda c: "Yes" if "history"        in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 17": lambda c: "Yes" if "insight"        in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 18": lambda c: "Yes" if "intimidation"   in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 19": lambda c: "Yes" if "investigation"  in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 20": lambda c: "Yes" if "medicine"       in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 21": lambda c: "Yes" if "nature"         in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 22": lambda c: "Yes" if "perception"     in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 23": lambda c: "Yes" if "performance"    in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 24": lambda c: "Yes" if "persuasion"     in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 25": lambda c: "Yes" if "religion"       in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 26": lambda c: "Yes" if "sleight of hand" in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 27": lambda c: "Yes" if "stealth"        in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",
        "Check Box 28": lambda c: "Yes" if "survival"       in [s.lower() for s in c.get("skill_proficiencies", [])] else "Off",

        # Multiline alanlar için birleştirilmiş veriler
        "Features and Traits": lambda c: "\n".join(c.get("feats", [])),
        "Equipment": lambda c: "\n".join(item.get("name", str(item)) if isinstance(item, dict) else str(item) for item in c.get("equipment", [])),

        # ── ADIM 4: Büyü Alanlari (Graceful Fail) ─────────────────────────────
        # calculate_spells() cevabını yeniden çalıştırmak yerine karakter
        # sözlüğünde önce kaydedilmiş spell_data'ya bakar.
        # Büyücsüz karakterlerde veya alan eksikliğinde boş döner — asla çökmez.
        "SpellcastingClass": lambda c: (
            c.get("class", "") if c.get("class_data", {}).get("spellcasting_ability") else ""
        ),
        "SpellSaveDC": lambda c: (
            str(c.get("derived", {}).get("spell_save_dc") or c.get("spell_save_dc", ""))
        ),
        "SpellAtkBonus": lambda c: (
            format_mod(int(c.get("derived", {}).get("spell_attack_bonus") or c.get("spell_attack_bonus", 0)))
            if (c.get("derived", {}).get("spell_attack_bonus") or c.get("spell_attack_bonus")) is not None else ""
        ),
        # Spell slots: SlotsTotal1 ... SlotsTotal9 (PHB format)
        # Warlock'ta pakt slot seviyesine göre doldurulur, geri kalanlar boş.
        "SlotsTotal1": lambda c: _safe_slot(c, "1"),
        "SlotsTotal2": lambda c: _safe_slot(c, "2"),
        "SlotsTotal3": lambda c: _safe_slot(c, "3"),
        "SlotsTotal4": lambda c: _safe_slot(c, "4"),
        "SlotsTotal5": lambda c: _safe_slot(c, "5"),
        "SlotsTotal6": lambda c: _safe_slot(c, "6"),
        "SlotsTotal7": lambda c: _safe_slot(c, "7"),
        "SlotsTotal8": lambda c: _safe_slot(c, "8"),
        "SlotsTotal9": lambda c: _safe_slot(c, "9"),
    },
    "pf1e": {
        # Ortak Başlık & RPG Detayları
        "Character Name": lambda c: c.get("name", ""),
        "Classes & Levels": lambda c: _format_classes_and_levels(c),
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
        "TOUCH": lambda c: str(c.get("touch_ac", 10)),
        "flat_footed_ac": lambda c: str(c.get("flat_footed_ac", 10)),
        "FLATFOOTED": lambda c: str(c.get("flat_footed_ac", 10)),
        "INITIATIVE": lambda c: format_mod(c.get("initiative", get_modifier(c, "dexterity"))),
        "BASE ATTACK BONUS": lambda c: format_mod(c.get("bab", 0)),
        "CMB": lambda c: format_mod(c.get("cmb", 0)),
        "CMD": lambda c: str(c.get("cmd", 10)),
        
        # Saves
        "FORTITUDE": lambda c: format_mod(c.get("saving_throws", {}).get("Fortitude", get_modifier(c, "constitution"))),
        "REFLEX": lambda c: format_mod(c.get("saving_throws", {}).get("Reflex", get_modifier(c, "dexterity"))),
        "WILL": lambda c: format_mod(c.get("saving_throws", {}).get("Will", get_modifier(c, "wisdom"))),
        
        # ── PF1e BECERİ ALANLARI (PDF'deki gerçek field isimleri) ───────────
        # PF1e şablonunda beceriler kendi adlarıyla field olarak tanımlı.
        # Toplam beceri bonusu = Ranks + Class Skill (+3) + Ability Mod + Misc
        "Acrobatics":              lambda c: _skill(c, "acrobatics"),
        "Appraise":                lambda c: _skill(c, "appraise"),
        "Bluff":                   lambda c: _skill(c, "bluff"),
        "Climb":                   lambda c: _skill(c, "climb"),
        "Craft_2":                 lambda c: _skill(c, "craft"),
        "Diplomacy":               lambda c: _skill(c, "diplomacy"),
        "Disable Device":          lambda c: _skill(c, "disable_device"),
        "Disguise":                lambda c: _skill(c, "disguise"),
        "Escape Artist":           lambda c: _skill(c, "escape_artist"),
        "Fly":                     lambda c: _skill(c, "fly"),
        "Handle Animal":           lambda c: _skill(c, "handle_animal"),
        "Heal":                    lambda c: _skill(c, "heal"),
        "Intimidate":              lambda c: _skill(c, "intimidate"),
        "Knowledge arcana":        lambda c: _skill(c, "knowledge_arcana"),
        "Knowledge dungeoneering": lambda c: _skill(c, "knowledge_dungeoneering"),
        "Knowledge engineering":   lambda c: _skill(c, "knowledge_engineering"),
        "Knowledge geography":     lambda c: _skill(c, "knowledge_geography"),
        "Knowledge history":       lambda c: _skill(c, "knowledge_history"),
        "Knowledge local":         lambda c: _skill(c, "knowledge_local"),
        "Knowledge nature":        lambda c: _skill(c, "knowledge_nature"),
        "Knowledge nobility":      lambda c: _skill(c, "knowledge_nobility"),
        "Knowledge planes":        lambda c: _skill(c, "knowledge_planes"),
        "Knowledge religion":      lambda c: _skill(c, "knowledge_religion"),
        "Linguistics":             lambda c: _skill(c, "linguistics"),
        "Perception":              lambda c: _skill(c, "perception"),
        "Perform":                 lambda c: _skill(c, "perform"),
        "Profession":              lambda c: _skill(c, "profession"),
        "Ride":                    lambda c: _skill(c, "ride"),
        "Sense Motive":            lambda c: _skill(c, "sense_motive"),
        "Sleight of Hand":         lambda c: _skill(c, "sleight_of_hand"),
        "Spellcraft":              lambda c: _skill(c, "spellcraft"),
        "Stealth":                 lambda c: _skill(c, "stealth"),
        "Survival":                lambda c: _skill(c, "survival"),
        "Swim":                    lambda c: _skill(c, "swim"),
        "Use Magic Device":        lambda c: _skill(c, "use_magic_device"),

        # ── PF1e TAŞIMA KAPASİTESİ & ENVANTER ───────────────────────────────
        "TOTAL WEIGHT": lambda c: str(c.get("derived", {}).get("total_weight") or c.get("total_weight", 0.0)),
        "Light": lambda c: str(c.get("derived", {}).get("carrying_capacity", {}).get("light_max") or c.get("carrying_capacity", {}).get("light_max") or c.get("carrying_capacity", {}).get("light", "")),
        "Medium": lambda c: str(c.get("derived", {}).get("carrying_capacity", {}).get("medium_max") or c.get("carrying_capacity", {}).get("medium_max") or c.get("carrying_capacity", {}).get("medium", "")),
        "Heavy": lambda c: str(c.get("derived", {}).get("carrying_capacity", {}).get("heavy_max") or c.get("carrying_capacity", {}).get("heavy_max") or c.get("carrying_capacity", {}).get("heavy", "")),
        "Lift Over": lambda c: str(c.get("derived", {}).get("carrying_capacity", {}).get("heavy_max") or c.get("carrying_capacity", {}).get("heavy_max") or c.get("carrying_capacity", {}).get("heavy", "")),
        "Drag or": lambda c: str(round(float(c.get("derived", {}).get("carrying_capacity", {}).get("heavy_max") or c.get("carrying_capacity", {}).get("heavy_max") or c.get("carrying_capacity", {}).get("heavy", 0) or 0) * 5, 1)),

        # ── PF1e AC BREAKDOWN (ZIRH SINIFI AYRIŞTIRMASI) ───────────────────
        "Armor": lambda c: str(c.get("derived", {}).get("ac_breakdown", {}).get("armor") or c.get("armor_bonus", 0)),
        "Shield": lambda c: str(c.get("derived", {}).get("ac_breakdown", {}).get("shield") or c.get("shield_bonus", 0)),
        "Dex_2": lambda c: format_mod(c.get("derived", {}).get("ac_breakdown", {}).get("dex") or get_modifier(c, "dexterity")),
        "Natural": lambda c: str(c.get("derived", {}).get("ac_breakdown", {}).get("natural") or c.get("natural_armor", 0)),
        "Deflect": lambda c: str(c.get("derived", {}).get("ac_breakdown", {}).get("deflection") or 0),
        "Misc": lambda c: str(c.get("derived", {}).get("ac_breakdown", {}).get("misc") or 0),

        # ── PF1e PARA / GOLD ──────────────────────────────────────────────
        "Gold": lambda c: str(c.get("money", {}).get("gp", c.get("gold", 0))),
        "Silver": lambda c: str(c.get("money", {}).get("sp", c.get("silver", 0))),
        "Copper": lambda c: str(c.get("money", {}).get("cp", c.get("copper", 0))),
        "Platinum": lambda c: str(c.get("money", {}).get("pp", c.get("platinum", 0))),

        # Multiline
        "Feats": lambda c: "\n".join(c.get("feats", [])),
        "Equipment": lambda c: "\n".join(item.get("name", str(item)) if isinstance(item, dict) else str(item) for item in c.get("equipment", [])),

        # ── ADIM 4: Büyü Alanlari PF1e (Graceful Fail) ──────────────────────
        # Caster Level (CL), Concentration ve Bonus Slot bilgisi.
        # PF1e CRB kurallarına göre: CL = seviye, Conc = CL + ability_mod.
        # PF2e KESİNLİKLE desteklenmez.
        "Caster Level": lambda c: (
            str(c.get("level", ""))
            if c.get("class_data", {}).get("spellcasting_ability") else ""
        ),
        "Concentration": lambda c: (
            _safe_pf1e_concentration(c)
        ),
        "Spellcasting Class": lambda c: (
            c.get("class", "") if c.get("class_data", {}).get("spellcasting_ability") else ""
        ),
        # Arcane Spell Failure — 0 eğer büyücü değilse boş bırak
        "Arcane Spell Failure": lambda c: (
            "0%" if c.get("class_data", {}).get("spellcasting_ability") else ""
        ),
        "DOMAINSSPECIALTY SCHOOL 1": lambda c: str(
            c.get("specialty_school") or c.get("domain") or c.get("bloodline") or ""
        ),
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
        
        # Ability Ranks (M&M3e'de rank = modifier, doğrudan yazılır)
        "strength":  lambda c: str(get_ability(c, "strength", default=0)),
        "stamina":   lambda c: str(get_ability(c, "stamina", default=0)),
        "agility":   lambda c: str(get_ability(c, "agility", default=0)),
        "dexterity": lambda c: str(get_ability(c, "dexterity", default=0)),
        "fighting":  lambda c: str(get_ability(c, "fighting", default=0)),
        "intellect": lambda c: str(get_ability(c, "intellect", default=0)),
        "awareness": lambda c: str(get_ability(c, "awareness", default=0)),
        "presence":  lambda c: str(get_ability(c, "presence", default=0)),
        
        # Defenses (pipeline'dan hesaplanmış değerler)
        "dodge":      lambda c: format_mod(c.get("defenses", {}).get("Dodge",     get_ability(c, "agility",   0))),
        "parry":      lambda c: format_mod(c.get("defenses", {}).get("Parry",     get_ability(c, "fighting",  0))),
        "toughness":  lambda c: format_mod(c.get("defenses", {}).get("Toughness", get_ability(c, "stamina",   0))),
        "fortitude":  lambda c: format_mod(c.get("defenses", {}).get("Fortitude", get_ability(c, "stamina",   0))),
        "will":       lambda c: format_mod(c.get("defenses", {}).get("Will",      get_ability(c, "awareness", 0))),
        "initiative": lambda c: format_mod(c.get("initiative", get_ability(c, "agility", 0))),
        "speed":      lambda c: str(c.get("speed", 30)),
        
        # ── MM3e BECERİ ALANLARI ───────────────────────────────────────────────
        # M&M 3e PDF'inde fillable field yok — Skills alanına yapılandırılmış
        # metin olarak yazılır. Her beceri ayrı satırda: "Beceri Adı: +X"
        # _skill() helper'ı snake_case ve Title Case her ikisini de çözümler.
        "Skills": lambda c: "\n".join(
            f"{sk.replace('_', ' ').title()}: {_skill(c, sk)}"
            for sk in [
                "acrobatics", "athletics", "close_combat",
                "deception", "expertise", "insight",
                "intimidation", "investigation", "perception",
                "persuasion", "ranged_combat", "sleight_of_hand",
                "stealth", "technology", "treatment", "vehicles",
            ]
            if _skill(c, sk) not in ("", "+0")   # sadece rank > 0 olanları göster
        ) or "—",
        
        # Multiline
        "Powers":     lambda c: (
            "\n".join(
                f"{k} ({v.get('cost', '?')} PP): {v.get('description', '')}"
                if isinstance(v, dict) else str(v)
                for k, v in c.get("powers", {}).items()
            ) if isinstance(c.get("powers"), dict)
            else "\n".join(c.get("powers", []))
        ),
        "Advantages": lambda c: "\n".join(c.get("feats", [])),
    }
}

# Aliases so both "pf1e" and "pathfinder1e" keys resolve correctly
PDF_MAPPINGS["pathfinder1e"] = PDF_MAPPINGS["pf1e"]
PDF_MAPPINGS["dnd5e_alias"] = PDF_MAPPINGS["dnd5e"]  # kept for completeness


def _resolve_pdf_template(template_name: str) -> Path:
    """Locate a PDF template in legacy or web public directories."""
    root = Path(__file__).resolve().parent.parent
    search_dirs = [
        root / "templates",
        root / "web" / "frontend" / "public" / "templates",
    ]
    candidates = [template_name]
    if template_name == "mnm3e_sheet.pdf":
        candidates.append("mnm3e_sheet.pdf.pdf")

    for template_dir in search_dirs:
        for name in candidates:
            path = template_dir / name
            if path.exists():
                return path

    searched = ", ".join(str(d / template_name) for d in search_dirs)
    raise FileNotFoundError(f"PDF şablonu bulunamadı: {template_name} (aranan: {searched})")


def _fill_pdf_form(character: dict, template_name: str, mapping: dict, output_path: Path) -> None:
    """Helper function to load template, fill AcroForm fields, and save to output_path."""
    template_path = _resolve_pdf_template(template_name)
        
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
    
    # PF1e Advanced Skill Mapping (Rank, Stat Mod, Class Skill)
    if template_name == "pf1e_sheet.pdf":
        ranks_data = character.get("skill_ranks", {}) or {}
        skills_data = character.get("skills", {}) or {}
        class_skills = character.get("class_data", {}).get("class_skills", []) or []

        def normalize_key(k: str) -> str:
            if not k:
                return ""
            val = str(k).lower().strip().replace(" ", "").replace("_", "").replace("(", "").replace(")", "")
            for prefix in ("craft", "perform", "profession"):
                if val.startswith(prefix):
                    return prefix
            return val

        # Pre-build normalized mappings
        norm_ranks = {normalize_key(k): v for k, v in ranks_data.items() if k is not None}
        norm_skills = {normalize_key(k): v for k, v in skills_data.items() if k is not None}
        norm_class_skills = {normalize_key(k) for k in class_skills if k is not None}

        pf1e_skill_names = [
            "Acrobatics", "Appraise", "Bluff", "Climb", "Craft_2", "Diplomacy", 
            "Disable Device", "Disguise", "Escape Artist", "Fly", "Handle Animal", 
            "Heal", "Intimidate", "Knowledge arcana", "Knowledge dungeoneering", 
            "Knowledge engineering", "Knowledge geography", "Knowledge history", 
            "Knowledge local", "Knowledge nature", "Knowledge nobility", 
            "Knowledge planes", "Knowledge religion", "Linguistics", "Perception", 
            "Perform", "Profession", "Ride", "Sense Motive", "Sleight of Hand", 
            "Spellcraft", "Stealth", "Survival", "Swim", "Use Magic Device"
        ]

        for sk in pf1e_skill_names:
            sk_norm = normalize_key(sk)
            
            # Rank (forced to str)
            rank = norm_ranks.get(sk_norm, 0)
            if rank:
                for suffix in [" Ranks", "_Rank", " Rank", "Ranks"]:
                    if f"{sk}{suffix}" in all_pdf_fields:
                        fields_to_fill[f"{sk}{suffix}"] = str(rank)
            
            # Class Skill
            is_class = sk_norm in norm_class_skills
            if is_class:
                for suffix in [" Class Skill", "_Class", " CS"]:
                    if f"{sk}{suffix}" in all_pdf_fields:
                        fields_to_fill[f"{sk}{suffix}"] = "Yes"
            
            # Total & Stat Mod
            total = norm_skills.get(sk_norm, "")
            if total != "":
                for suffix in [" Total", "_Total", ""]:
                    if f"{sk}{suffix}" in all_pdf_fields:
                        fields_to_fill[f"{sk}{suffix}"] = str(total)
                
                try:
                    class_bonus = 3 if (is_class and int(rank) > 0) else 0
                    ab_mod = int(total) - int(rank) - class_bonus
                    for suffix in [" Ab Mod", "_Mod", " Mod", " Ability"]:
                        if f"{sk}{suffix}" in all_pdf_fields:
                            fields_to_fill[f"{sk}{suffix}"] = str(ab_mod)
                except Exception:
                    pass

    # 1. Equipment & Individual Weights sequential matching
    eq_list = character.get("equipment", [])
    for idx, item in enumerate(eq_list, 1):
        if idx > 26:
            break
        name = item.get("name") or item.get("isim") or str(item) if isinstance(item, dict) else str(item)
        qty = item.get("quantity", 1) if isinstance(item, dict) else 1
        qty_str = f" x{qty}" if qty > 1 else ""
        item_str = f"{name}{qty_str}"
        
        # Item name field (e.g., "Item 1", "Item 2")
        for prefix in ["Item ", "Item", "eq", "eq_", "equipment", "equipment_"]:
            f_name = f"{prefix}{idx}"
            if f_name in all_pdf_fields:
                fields_to_fill[f_name] = item_str
                break

        # Item total weight field (e.g., "WT 1", "WT 2")
        if isinstance(item, dict):
            try:
                from rules.calculators import extract_weight_and_qty
                w_val, q_val = extract_weight_and_qty(item)
                item_total_wt = round(w_val * q_val, 1)
                if item_total_wt > 0:
                    for wt_prefix in ["WT ", "WT", "wt_", "Weight"]:
                        wt_fname = f"{wt_prefix}{idx}"
                        if wt_fname in all_pdf_fields:
                            fields_to_fill[wt_fname] = str(item_total_wt)
                            break
            except Exception:
                pass

    # 1b. Weapon Cards matching (Weapon 1..5, Attack 1..5, Damage 1..5, Critical 1..5, Range 1..5, Type 1..5)
    weapons_list = character.get("derived", {}).get("weapons") or character.get("weapons") or []
    for idx, w in enumerate(weapons_list[:5], 1):
        if isinstance(w, dict):
            w_name = w.get("name") or w.get("isim") or "Silah"
            atk_str = w.get("calculated_attack") or "+0"
            dmg_str = w.get("calculated_damage") or "1d6"
            crit_str = w.get("crit_range") or "20/x2"
            range_str = w.get("range") or "Melee"
            type_str = w.get("type") or "Slashing"
            
            if f"Weapon {idx}" in all_pdf_fields:
                fields_to_fill[f"Weapon {idx}"] = w_name
            if f"Attack {idx}" in all_pdf_fields:
                fields_to_fill[f"Attack {idx}"] = atk_str
            elif f"Bonus {idx}" in all_pdf_fields:
                fields_to_fill[f"Bonus {idx}"] = atk_str
            if f"Damage {idx}" in all_pdf_fields:
                fields_to_fill[f"Damage {idx}"] = dmg_str
            if f"Critical {idx}" in all_pdf_fields:
                fields_to_fill[f"Critical {idx}"] = crit_str
            if f"Range {idx}" in all_pdf_fields:
                fields_to_fill[f"Range {idx}"] = range_str
            if f"Type {idx}" in all_pdf_fields:
                fields_to_fill[f"Type {idx}"] = type_str

    # 1c. Companion & Familiar PDF Mapping
    comp_obj = character.get("derived", {}).get("companion") or character.get("companion")
    if comp_obj and isinstance(comp_obj, dict):
        comp_name = comp_obj.get("name") or "Yoldaş"
        comp_species = comp_obj.get("species") or comp_obj.get("type") or "Animal Companion"
        comp_hp = comp_obj.get("hp", 0)
        comp_ac = comp_obj.get("ac", 10)
        comp_attacks = comp_obj.get("attacks") or "Doğal Saldırı"
        comp_summary = f"YOLDAŞ: {comp_name} ({comp_species}) | Can: {comp_hp} HP | Zırh: {comp_ac} AC | Saldırı: {comp_attacks}"
        
        for comp_field in ["Special Attacks", "Special Attacks 2", "Notes", "Character Notes"]:
            if comp_field in all_pdf_fields and comp_field not in fields_to_fill:
                fields_to_fill[comp_field] = comp_summary
                break
            elif comp_field in fields_to_fill:
                fields_to_fill[comp_field] = f"{fields_to_fill[comp_field]} | {comp_summary}"
                break
                
    # 2. Feats sequential matching (FEATS 1..12)
    feat_list = character.get("feats", [])
    for idx, feat in enumerate(feat_list, 1):
        if idx > 12:
            break
        feat_name = feat.get("name") or feat.get("isim") if isinstance(feat, dict) else str(feat)
        for prefix in ["FEATS ", "FEATS", "FEAT ", "FEAT", "feat ", "feat", "feat_", "feature", "feature_", "power", "power_"]:
            f_name = f"{prefix}{idx}"
            if f_name in all_pdf_fields:
                fields_to_fill[f_name] = str(feat_name)
                break

    # 2b. Special Abilities, Traits & Archetype Features (SPECIAL ABILITIES 1..20)
    special_abilities = []
    # Traits
    for tr in character.get("traits", []):
        tr_name = tr.get("name") or tr.get("isim") if isinstance(tr, dict) else str(tr)
        special_abilities.append(f"Trait: {tr_name}")
    # Archetype granted features
    arch_granted = character.get("derived", {}).get("archetype_details", {}).get("granted_features", [])
    for g in arch_granted:
        special_abilities.append(f"Arketip: {g}")
    # Class & Racial Features / Special Abilities
    for sa in (character.get("special_abilities", []) or character.get("racial_traits", [])):
        sa_name = sa.get("name") or sa.get("isim") if isinstance(sa, dict) else str(sa)
        if sa_name and sa_name not in special_abilities:
            special_abilities.append(sa_name)

    for idx, ab_text in enumerate(special_abilities, 1):
        if idx > 20:
            break
        for prefix in ["SPECIAL ABILITIES ", "SPECIAL ABILITIES", "Special Abilities ", "Special Ability ", "special_ability_", "special_ability"]:
            f_name = f"{prefix}{idx}"
            if f_name in all_pdf_fields:
                fields_to_fill[f_name] = str(ab_text)
                break

    # 3. Spells sequential matching
    spell_list = character.get("spells", [])
    for idx, spell in enumerate(spell_list, 1):
        # Bazı D&D5e PDF'lerinde "Spells 1014" gibi numaralar vardır, bu basit sequential eşleşme bazılarını yakalayabilir
        for prefix in ["spell", "spell_", "Spells", "Spells "]:
            f_name = f"{prefix}{idx}"
    # 3b. Spellcasting Engine PDF Mapping (DCs, Concentration, CL)
    sc_obj = character.get("derived", {}).get("spellcasting") or character.get("spellcasting")
    if sc_obj and isinstance(sc_obj, dict):
        cl_val = sc_obj.get("caster_level", 1)
        conc_val = sc_obj.get("concentration_bonus", 0)
        conc_str = f"+{conc_val}" if conc_val >= 0 else str(conc_val)
        
        for cl_field in ["CL", "Caster Level", "CASTER LEVEL"]:
            if cl_field in all_pdf_fields:
                fields_to_fill[cl_field] = str(cl_val)
        for conc_field in ["Concentration", "CONCENTRATION", "Concentration Check"]:
            if conc_field in all_pdf_fields:
                fields_to_fill[conc_field] = conc_str

        dcs = sc_obj.get("spell_dcs", {})
        for lvl_i in range(0, 10):
            dc_val = dcs.get(str(lvl_i)) or dcs.get(lvl_i)
            if dc_val:
                for dc_prefix in [f"Spell DC {lvl_i}", f"DC {lvl_i}", f"SPELL DC {lvl_i}"]:
                    if dc_prefix in all_pdf_fields:
                        fields_to_fill[dc_prefix] = str(dc_val)
                
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
    """Sistem anahtarına göre doğru fillable PDF şablonunu tetikler.
    Şablon dosyaları bulunamazsa, ReportLab kullanarak dinamik ve şık bir PDF üretir.
    """
    system = character.get("system", "").upper()
    portrait_path = None
    if character.get("portrait"):
        portrait_path = _get_portrait_image_path(character["portrait"])
        
    try:
        if "DND" in system:
            export_dnd_character_pdf(character, output_path)
        elif "MM" in system or "MUTANTS" in system:
            export_mm_character_pdf(character, output_path)
        elif "PATHFINDER" in system or "PF" in system:
            export_pf1e_character_pdf(character, output_path)
        else:
            export_dnd_character_pdf(character, output_path)
            
        if portrait_path and output_path.exists():
            _stamp_portrait_on_pdf(output_path, portrait_path, system)
    except FileNotFoundError as e:
        logger.warning(f"AcroForm template not found ({e}). Generating fallback PDF using ReportLab.")
        generate_reportlab_fallback_pdf(character, output_path, portrait_path=portrait_path)
    finally:
        if portrait_path and portrait_path.exists() and tempfile.gettempdir().lower() in str(portrait_path).lower():
            try:
                portrait_path.unlink()
            except Exception:
                pass


def generate_reportlab_fallback_pdf(character: dict, output_path: Path, portrait_path: Optional[Path] = None) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        textColor=colors.HexColor("#c9a84c"),
        fontSize=24,
        leading=28,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        textColor=colors.HexColor("#8b949e"),
        fontSize=12,
        spaceAfter=15
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        textColor=colors.HexColor("#16213e"),
        fontSize=14,
        leading=18,
        spaceBefore=10,
        spaceAfter=6,
        borderColor=colors.HexColor("#c9a84c"),
        borderWidth=1,
        borderRadius=2,
        borderPadding=4
    )
    
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=9,
        leading=11
    )
    
    cell_bold_style = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        fontName='Helvetica-Bold'
    )
    
    # 0 & 1. Logo & Header Block Layout (Table containing Portrait next to details)
    header_left = []
    logo_path = Path("c:/Users/dnssh/OneDrive/Belgeler/Diyargezenweb/assets/diyargezer_logo.png")
    if logo_path.exists():
        try:
            header_left.append(Image(str(logo_path), width=120, height=36))
            header_left.append(Spacer(1, 6))
        except Exception:
            pass
            
    name = character.get("name", "İsimsiz Kahraman")
    system = character.get("system", "").upper()
    char_class = character.get("class", "Sınıfsız")
    level = character.get("level", 1)
    race = character.get("race", "Irksız")
    
    header_left.append(Paragraph(f"DİYARGEZEN KARAKTER KAĞIDI", title_style))
    header_left.append(Paragraph(f"Sistem: {system} | Karakter: {name} | Sınıf & Seviye: {char_class} {level} | Irk: {race}", subtitle_style))
    
    header_right = []
    if portrait_path and portrait_path.exists():
        try:
            header_right.append(Image(str(portrait_path), width=80, height=100))
        except Exception:
            pass
            
    header_cols = [header_left, header_right] if header_right else [header_left]
    col_widths = [440, 100] if header_right else [540]
    
    header_table = Table([header_cols], colWidths=col_widths)
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 10))
    
    # 2. Abilities Grid Table
    story.append(Paragraph("YETENEK SKORLARI", section_title_style))
    
    abilities_data = [
        [Paragraph("STR", cell_bold_style), Paragraph("DEX", cell_bold_style), Paragraph("CON", cell_bold_style),
         Paragraph("INT", cell_bold_style), Paragraph("WIS", cell_bold_style), Paragraph("CHA", cell_bold_style)]
    ]
    
    scores_row = []
    mods_row = []
    
    abs_list = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    for ab in abs_list:
        score = get_ability(character, ab)
        mod = get_modifier(character, ab)
        scores_row.append(Paragraph(str(score), cell_style))
        mods_row.append(Paragraph(format_mod(mod), cell_bold_style))
        
    abilities_data.append(scores_row)
    abilities_data.append(mods_row)
    
    ab_table = Table(abilities_data, colWidths=[90]*6)
    ab_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#16213e")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#c9a84c")),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#f8f9fa")),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#eef1f6")),
    ]))
    
    for col_idx in range(6):
        abilities_data[0][col_idx].style.textColor = colors.white
        
    story.append(ab_table)
    story.append(Spacer(1, 12))
    
    # 3. Combat Metrics
    story.append(Paragraph("SAVAŞ VE HAYATTA KALMA", section_title_style))
    hp = character.get("hit_points", character.get("derived", {}).get("hit_points", 10))
    ac = character.get("armor_class", character.get("derived", {}).get("armor_class", 10))
    init = character.get("initiative", character.get("derived", {}).get("initiative", 0))
    bab = character.get("bab", character.get("derived", {}).get("bab", 0))
    
    combat_data = [
        [Paragraph("Hit Points (HP)", cell_bold_style), Paragraph("Armor Class (AC)", cell_bold_style), 
         Paragraph("Initiative", cell_bold_style), Paragraph("Base Attack Bonus (BAB)", cell_bold_style)],
        [Paragraph(str(hp), cell_style), Paragraph(str(ac), cell_style), 
         Paragraph(format_mod(init), cell_style), Paragraph(format_mod(bab), cell_style)]
    ]
    
    c_table = Table(combat_data, colWidths=[135]*4)
    c_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#16213e")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#c9a84c")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#f8f9fa")),
    ]))
    for col_idx in range(4):
        combat_data[0][col_idx].style.textColor = colors.white
        
    story.append(c_table)
    story.append(Spacer(1, 12))
    
    # 4. Saves & Skills Split Tables
    story.append(Paragraph("KURTARMA ZARLARI VE BECERİLER", section_title_style))
    
    saves_list = []
    saves_data = character.get("saving_throws", {}) or {}
    for s_name, s_val in saves_data.items():
        saves_list.append([Paragraph(s_name, cell_bold_style), Paragraph(format_mod(s_val), cell_style)])
        
    if not saves_list:
        saves_list = [[Paragraph("Saving Throws bulunamadı.", cell_style), Paragraph("", cell_style)]]
        
    skills_list = []
    skills_data = character.get("skills", {}) or {}
    for sk_name, sk_val in list(skills_data.items())[:12]:
        display_name = sk_name.replace("_", " ").title()
        skills_list.append([Paragraph(display_name, cell_style), Paragraph(format_mod(sk_val), cell_bold_style)])
        
    if not skills_list:
        skills_list = [[Paragraph("Skills bulunamadı.", cell_style), Paragraph("", cell_style)]]
        
    saves_table = Table(saves_list, colWidths=[100, 50])
    saves_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    
    skills_table = Table(skills_list, colWidths=[200, 50])
    skills_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    
    split_table = Table([[saves_table, skills_table]], colWidths=[180, 360])
    split_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(split_table)
    story.append(Spacer(1, 12))
    
    # 5. Equipment & Weight
    story.append(Paragraph(f"ENVANTER (Toplam Ağırlık: {character.get('total_weight', 0.0)} lb | Taşıma Durumu: {character.get('encumbrance_status', 'Light')})", section_title_style))
    
    eq_rows = [[Paragraph("Eşya Adı", cell_bold_style), Paragraph("Kategori", cell_bold_style), Paragraph("Ağırlık", cell_bold_style)]]
    for item in character.get("equipment", [])[:10]:
        name_it = item.get("name", "Bilinmeyen Eşya") if isinstance(item, dict) else str(item)
        cat_it = item.get("type", "Loot") if isinstance(item, dict) else "Loot"
        w_it = item.get("sistem_verisi", {}).get("weight", 0.0) if isinstance(item, dict) else 0.0
        eq_rows.append([Paragraph(name_it, cell_style), Paragraph(cat_it, cell_style), Paragraph(f"{w_it} lb", cell_style)])
        
    if len(eq_rows) == 1:
        eq_rows.append([Paragraph("Envanter boş.", cell_style), Paragraph("", cell_style), Paragraph("", cell_style)])
        
    eq_table = Table(eq_rows, colWidths=[300, 140, 100])
    eq_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#16213e")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#c9a84c")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f8f9fa")),
    ]))
    for col_idx in range(3):
        eq_rows[0][col_idx].style.textColor = colors.white
        
    story.append(eq_table)
    story.append(Spacer(1, 12))
    
    # 6. Feats and Spells
    story.append(Paragraph("FEAT & TRAITS VE BÜYÜLER", section_title_style))
    
    feats = character.get("feats", [])
    feats_str = ", ".join(f["name"] if isinstance(f, dict) else str(f) for f in feats) or "Seçili Feat bulunmuyor."
    story.append(Paragraph(f"<b>Seçili Feats / Özellikler:</b> {feats_str}", cell_style))
    story.append(Spacer(1, 6))
    
    sp_slots = character.get("spell_slots", {})
    if sp_slots:
        slots_str = ", ".join(f"Seviye {lvl}: {slots} Slot" for lvl, slots in sp_slots.items())
        story.append(Paragraph(f"<b>Mevcut Büyü Slotları:</b> {slots_str}", cell_style))
        
    doc.build(story)

