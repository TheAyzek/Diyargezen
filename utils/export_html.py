"""
Universal HTML/Web Character Sheet Export
Tum TTRPG sistemleri icin karakter kagidini HTML olarak export etme
D&D 5e, Pathfinder 1e, M&M 3e destegi
"""

import json
import base64
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from utils.portraits import find_portrait

EXPORT_DIR = Path(__file__).resolve().parent.parent / "exports"


# ============================================================================
# Ortak CSS stilleri
# ============================================================================

COMMON_CSS = """
:root {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-card: #0f3460;
    --text-primary: #e8e8e8;
    --text-secondary: #a8a8b8;
    --accent: #e94560;
    --accent2: #533483;
    --border: #2a2a4a;
    --success: #4ecca3;
    --warning: #f0a500;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    text-align: center;
    padding: 30px 20px;
    background: linear-gradient(135deg, var(--bg-secondary), var(--accent2));
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}

.header h1 {
    font-size: 2.5em;
    margin-bottom: 5px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

.header .subtitle {
    color: var(--text-secondary);
    font-size: 1.1em;
}

.portrait-section {
    text-align: center;
    margin: 20px 0;
}

.portrait-section img {
    max-width: 250px;
    max-height: 350px;
    border-radius: 12px;
    border: 3px solid var(--accent);
    box-shadow: 0 4px 20px rgba(233,69,96,0.3);
}

.section {
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid var(--border);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.section h2 {
    color: var(--accent);
    border-bottom: 2px solid var(--accent);
    padding-bottom: 8px;
    margin-bottom: 15px;
    font-size: 1.3em;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
}

.stat-box {
    background: var(--bg-card);
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    border: 1px solid var(--border);
}

.stat-box .label {
    font-size: 0.8em;
    color: var(--text-secondary);
    text-transform: uppercase;
}

.stat-box .value {
    font-size: 1.8em;
    font-weight: bold;
    color: var(--accent);
}

.stat-box .modifier {
    font-size: 1em;
    color: var(--success);
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
}

.info-item {
    background: var(--bg-card);
    padding: 10px 14px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    border: 1px solid var(--border);
}

.info-item .key {
    color: var(--text-secondary);
    font-size: 0.9em;
}

.info-item .val {
    color: var(--text-primary);
    font-weight: bold;
}

.list-section {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.tag {
    background: var(--bg-card);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.9em;
    border: 1px solid var(--border);
}

.tag.highlight {
    border-color: var(--accent);
    color: var(--accent);
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}

th, td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
}

th {
    color: var(--accent);
    font-weight: 600;
    background: var(--bg-card);
}

tr:hover { background: rgba(233,69,96,0.05); }

.footer {
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.8em;
    margin-top: 30px;
    padding: 15px;
}

@media (max-width: 600px) {
    .stat-grid { grid-template-columns: repeat(3, 1fr); }
    .info-grid { grid-template-columns: 1fr; }
    .header h1 { font-size: 1.8em; }
}

@media print {
    body { background: white; color: black; }
    .section { border: 1px solid #ccc; box-shadow: none; }
    .stat-box .value { color: #333; }
    .header { background: #eee; }
}
"""

# ============================================================================
# Sistem bazli tema renkleri
# ============================================================================

SYSTEM_THEMES = {
    "dnd5e": {"accent": "#e94560", "accent2": "#533483", "name": "D&D 5e"},
    "pathfinder1e": {"accent": "#e4a11b", "accent2": "#6b3a2a", "name": "Pathfinder 1e"},
    "mm3e": {"accent": "#1e90ff", "accent2": "#0a2a5e", "name": "Mutants & Masterminds 3e"},
}


def _get_portrait_base64(character: Dict[str, Any], system: str) -> Optional[str]:
    """Portre resmini base64 olarak al"""
    name = character.get("name", "")
    portrait_path = find_portrait(name, system)
    if portrait_path and portrait_path.exists():
        ext = portrait_path.suffix.lower().strip(".")
        mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
        with open(portrait_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{data}"
    return None


def _wrap_html(title: str, body_html: str, system: str = "dnd5e",
               portrait_b64: Optional[str] = None) -> str:
    """Ortak HTML sarmalayici"""
    theme = SYSTEM_THEMES.get(system, SYSTEM_THEMES["dnd5e"])
    theme_css = f"""
    :root {{
        --accent: {theme['accent']};
        --accent2: {theme['accent2']};
    }}
    """

    portrait_html = ""
    if portrait_b64:
        portrait_html = f'''
        <div class="portrait-section">
            <img src="{portrait_b64}" alt="Character Portrait">
        </div>
        '''

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Diyargezen Karakter Kagidi</title>
    <style>{COMMON_CSS}{theme_css}</style>
</head>
<body>
    <div class="container">
        {portrait_html}
        {body_html}
        <div class="footer">
            Diyargezen TTRPG Karakter Gelistirici | {theme['name']} | {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </div>
    </div>
</body>
</html>"""


# ============================================================================
# D&D 5e HTML Export
# ============================================================================

def _generate_dnd5e_html(character: Dict[str, Any]) -> str:
    """D&D 5e karakter kagidi HTML"""
    name = character.get("name", "Isimsiz")
    race = character.get("race", "?")
    char_class = character.get("class_display", character.get("class", "?"))
    level = character.get("level", 1)
    bg = character.get("background", "?")
    alignment = character.get("alignment", "?")

    # Header
    html = f"""
    <div class="header">
        <h1>{name}</h1>
        <div class="subtitle">{race} {char_class} (Seviye {level})</div>
    </div>
    """

    # Temel bilgiler
    html += """<div class="section"><h2>Temel Bilgiler</h2><div class="info-grid">"""
    for key, val in [
        ("Irk", race), ("Sinif", char_class), ("Seviye", level),
        ("Arka Plan", bg), ("Hizalama", alignment),
        ("Deneyim", character.get("experience_points", 0)),
    ]:
        html += f'<div class="info-item"><span class="key">{key}</span><span class="val">{val}</span></div>'
    html += "</div></div>"

    # Ability Scores
    abilities = character.get("abilities", {})
    html += """<div class="section"><h2>Yetenek Puanlari</h2><div class="stat-grid">"""
    for ability, score in abilities.items():
        mod = (score - 10) // 2
        mod_str = f"+{mod}" if mod >= 0 else str(mod)
        short = ability[:3].upper()
        html += f'''<div class="stat-box">
            <div class="label">{short}</div>
            <div class="value">{score}</div>
            <div class="modifier">{mod_str}</div>
        </div>'''
    html += "</div></div>"

    # Savas Istatistikleri
    hp = character.get("hit_points", 0)
    ac = character.get("armor_class", 10)
    init = character.get("initiative", 0)
    speed = character.get("speed", 30)
    prof = character.get("proficiency_bonus", 2)
    hit_dice = character.get("hit_dice", "?")

    html += """<div class="section"><h2>Savas Istatistikleri</h2><div class="stat-grid">"""
    for label, val in [
        ("HP", hp), ("AC", ac), ("Ins.", f"+{init}" if init >= 0 else str(init)),
        ("Hiz", f"{speed} ft"), ("Yeterlilik", f"+{prof}"), ("Hit Dice", hit_dice)
    ]:
        html += f'''<div class="stat-box">
            <div class="label">{label}</div>
            <div class="value">{val}</div>
        </div>'''
    html += "</div></div>"

    # Saving Throws
    saves = character.get("saving_throws", {})
    if saves:
        html += """<div class="section"><h2>Kurtulus Zarları</h2><div class="stat-grid">"""
        for save, val in saves.items():
            val_str = f"+{val}" if val >= 0 else str(val)
            html += f'''<div class="stat-box">
                <div class="label">{save[:3]}</div>
                <div class="value">{val_str}</div>
            </div>'''
        html += "</div></div>"

    # Skills
    skills = character.get("skills", {})
    if skills:
        html += """<div class="section"><h2>Beceriler</h2>
        <table><tr><th>Beceri</th><th>Bonus</th></tr>"""
        for skill, val in sorted(skills.items()):
            val_str = f"+{val}" if val >= 0 else str(val)
            html += f"<tr><td>{skill}</td><td>{val_str}</td></tr>"
        html += "</table></div>"

    # Features
    features = character.get("features", [])
    if features:
        html += """<div class="section"><h2>Ozellikler & Yetenekler</h2><div class="list-section">"""
        for feat in features:
            html += f'<span class="tag">{feat}</span>'
        html += "</div></div>"

    # Equipment
    equipment = character.get("equipment", [])
    if equipment:
        html += """<div class="section"><h2>Ekipman</h2><div class="list-section">"""
        for item in equipment:
            html += f'<span class="tag">{item}</span>'
        html += "</div></div>"

    return html


# ============================================================================
# Pathfinder 1e HTML Export
# ============================================================================

def _generate_pathfinder1e_html(character: Dict[str, Any]) -> str:
    """Pathfinder 1e karakter kagidi HTML"""
    name = character.get("name", "Isimsiz")
    race = character.get("race", "?")
    char_class = character.get("class", "?")
    level = character.get("level", 1)

    html = f"""
    <div class="header">
        <h1>{name}</h1>
        <div class="subtitle">{race} {char_class} (Seviye {level})</div>
    </div>
    """

    # Temel bilgiler
    html += """<div class="section"><h2>Temel Bilgiler</h2><div class="info-grid">"""
    for key, val in [
        ("Irk", race), ("Sinif", char_class), ("Seviye", level),
        ("Hizalama", character.get("alignment", "?")),
        ("Deity", character.get("deity", "-")),
        ("Deneyim", character.get("experience_points", 0)),
        ("BAB", character.get("base_attack_bonus", 0)),
        ("CMB", character.get("cmb", 0)),
        ("CMD", character.get("cmd", 10)),
    ]:
        html += f'<div class="info-item"><span class="key">{key}</span><span class="val">{val}</span></div>'
    html += "</div></div>"

    # Ability Scores
    abilities = character.get("abilities", {})
    html += """<div class="section"><h2>Yetenek Puanlari</h2><div class="stat-grid">"""
    for ability, score in abilities.items():
        mod = (score - 10) // 2
        mod_str = f"+{mod}" if mod >= 0 else str(mod)
        html += f'''<div class="stat-box">
            <div class="label">{ability[:3].upper()}</div>
            <div class="value">{score}</div>
            <div class="modifier">{mod_str}</div>
        </div>'''
    html += "</div></div>"

    # Savas
    hp = character.get("hit_points", 0)
    ac = character.get("armor_class", 10)
    speed = character.get("speed", 30)
    init = character.get("initiative", 0)
    html += """<div class="section"><h2>Savas Istatistikleri</h2><div class="stat-grid">"""
    for label, val in [
        ("HP", hp), ("AC", ac), ("Touch AC", character.get("touch_ac", 10)),
        ("Flat-Footed", character.get("flat_footed_ac", 10)),
        ("Init", f"+{init}" if init >= 0 else str(init)), ("Hiz", f"{speed} ft"),
    ]:
        html += f'''<div class="stat-box">
            <div class="label">{label}</div>
            <div class="value">{val}</div>
        </div>'''
    html += "</div></div>"

    # Saves
    saves = character.get("saving_throws", {})
    if saves:
        html += """<div class="section"><h2>Saving Throws</h2><div class="stat-grid">"""
        for save, val in saves.items():
            val_str = f"+{val}" if val >= 0 else str(val)
            html += f'''<div class="stat-box">
                <div class="label">{save}</div>
                <div class="value">{val_str}</div>
            </div>'''
        html += "</div></div>"

    # Skills
    skills = character.get("skills", {})
    if skills:
        html += """<div class="section"><h2>Beceriler</h2>
        <table><tr><th>Beceri</th><th>Rank</th><th>Bonus</th></tr>"""
        for skill, data in sorted(skills.items()):
            if isinstance(data, dict):
                html += f"<tr><td>{skill}</td><td>{data.get('ranks', 0)}</td><td>+{data.get('total', 0)}</td></tr>"
            else:
                html += f"<tr><td>{skill}</td><td>-</td><td>+{data}</td></tr>"
        html += "</table></div>"

    # Feats
    feats = character.get("feats", [])
    if feats:
        html += """<div class="section"><h2>Yetenekler (Feats)</h2><div class="list-section">"""
        for feat in feats:
            html += f'<span class="tag">{feat}</span>'
        html += "</div></div>"

    return html


# ============================================================================
# M&M 3e HTML Export
# ============================================================================

def _generate_mm3e_html(character: Dict[str, Any]) -> str:
    """M&M 3e karakter kagidi HTML"""
    name = character.get("name", "Isimsiz")
    pl = character.get("pl_value", 10)
    archetype = character.get("archetype", "?")
    total_pp = character.get("total_power_points", 150)
    remaining = character.get("remaining_power_points", 0)

    html = f"""
    <div class="header">
        <h1>{name}</h1>
        <div class="subtitle">PL {pl} | {archetype} | PP: {total_pp - remaining} / {total_pp}</div>
    </div>
    """

    # Temel bilgiler
    html += """<div class="section"><h2>Temel Bilgiler</h2><div class="info-grid">"""
    for key, val in [
        ("Power Level", pl), ("Arketip", archetype),
        ("Toplam PP", total_pp), ("Kalan PP", remaining),
        ("Hero Points", character.get("hero_points", 1)),
    ]:
        html += f'<div class="info-item"><span class="key">{key}</span><span class="val">{val}</span></div>'
    html += "</div></div>"

    # Abilities
    abilities = character.get("abilities", {})
    if isinstance(abilities, dict):
        # M&M abilities might be nested
        ability_scores = {}
        for k, v in abilities.items():
            if k == "power_points":
                continue
            if isinstance(v, dict):
                ability_scores[k] = v.get("rank", v.get("score", 0))
            else:
                ability_scores[k] = v

        if ability_scores:
            html += """<div class="section"><h2>Yetenekler (Abilities)</h2><div class="stat-grid">"""
            for ability, rank in ability_scores.items():
                html += f'''<div class="stat-box">
                    <div class="label">{ability[:3].upper()}</div>
                    <div class="value">{rank}</div>
                </div>'''
            html += "</div></div>"

    # Defenses
    defenses = character.get("defenses", {})
    if defenses:
        html += """<div class="section"><h2>Savunmalar (Defenses)</h2><div class="stat-grid">"""
        for defense, val in defenses.items():
            if isinstance(val, dict):
                val = val.get("total", val.get("rank", 0))
            html += f'''<div class="stat-box">
                <div class="label">{defense}</div>
                <div class="value">{val}</div>
            </div>'''
        html += "</div></div>"

    # Powers
    powers = character.get("powers", {})
    if powers:
        html += """<div class="section"><h2>Gucler (Powers)</h2>
        <table><tr><th>Guc</th><th>Rank</th><th>Tur</th></tr>"""
        if isinstance(powers, dict):
            for power, data in sorted(powers.items()):
                if isinstance(data, dict):
                    html += f"<tr><td>{power}</td><td>{data.get('rank', '-')}</td><td>{data.get('type', '-')}</td></tr>"
                else:
                    html += f"<tr><td>{power}</td><td>{data}</td><td>-</td></tr>"
        elif isinstance(powers, list):
            for power in powers:
                if isinstance(power, dict):
                    html += f"<tr><td>{power.get('name', '?')}</td><td>{power.get('rank', '-')}</td><td>{power.get('type', '-')}</td></tr>"
                else:
                    html += f"<tr><td>{power}</td><td>-</td><td>-</td></tr>"
        html += "</table></div>"

    # Advantages
    advantages = character.get("advantages", {})
    if advantages:
        html += """<div class="section"><h2>Avantajlar</h2><div class="list-section">"""
        if isinstance(advantages, dict):
            for adv in sorted(advantages.keys()):
                html += f'<span class="tag">{adv}</span>'
        elif isinstance(advantages, list):
            for adv in advantages:
                if isinstance(adv, dict):
                    html += f'<span class="tag">{adv.get("name", "?")}</span>'
                else:
                    html += f'<span class="tag">{adv}</span>'
        html += "</div></div>"

    # Skills
    skills = character.get("skills", {})
    if skills:
        html += """<div class="section"><h2>Beceriler</h2>
        <table><tr><th>Beceri</th><th>Rank</th></tr>"""
        if isinstance(skills, dict):
            for skill, val in sorted(skills.items()):
                if isinstance(val, dict):
                    val = val.get("rank", val.get("total", 0))
                html += f"<tr><td>{skill}</td><td>+{val}</td></tr>"
        html += "</table></div>"

    return html


# ============================================================================
# Ana export fonksiyonu
# ============================================================================

def export_character_html(character: Dict[str, Any], filename: Optional[str] = None) -> Path:
    """Karakter'i HTML olarak export et - tum sistemler"""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    system = character.get("system", "dnd5e").lower()
    name = character.get("name", "unnamed")

    # Sisteme gore normalize et
    system_key = _normalize_system(system)

    # Sisteme gore HTML olustur
    generators = {
        "dnd5e": _generate_dnd5e_html,
        "pathfinder1e": _generate_pathfinder1e_html,
        "mm3e": _generate_mm3e_html,
    }
    generator = generators.get(system_key, _generate_dnd5e_html)
    body_html = generator(character)

    # Portre
    portrait_b64 = _get_portrait_base64(character, system_key)

    # HTML sarmalayici
    full_html = _wrap_html(name, body_html, system_key, portrait_b64)

    # Dosya kaydet
    if not filename:
        safe_name = "".join(c for c in name if c.isalnum() or c in "._- ").strip()
        safe_name = safe_name.replace(" ", "_").lower()
        filename = f"{system_key}_{safe_name}"

    filepath = EXPORT_DIR / f"{filename}.html"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_html)

    return filepath


def _normalize_system(system: str) -> str:
    """Sistem string'ini standart forma getir"""
    s = system.lower().replace(" ", "").replace("_", "")
    if s in ["dnd5e", "dnd", "d&d5e", "d&d", "dungeonsdragons5e"]:
        return "dnd5e"
    if s in ["pathfinder1e", "pathfinder", "pf1e"]:
        return "pathfinder1e"
    if s in ["mm3e", "mutantsandmasterminds3e", "mutantsandmasterminds", "m&m"]:
        return "mm3e"
    return "dnd5e"

