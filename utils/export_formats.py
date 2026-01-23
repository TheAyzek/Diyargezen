"""
Ek export formatları modülü
HTML, JSON, CSV export desteği
"""
from pathlib import Path
import json
import csv
from datetime import datetime


def export_character_html(character: dict, output_path: Path) -> None:
    """
    Karakteri HTML formatında export et
    
    Args:
        character: Karakter verisi
        output_path: Çıktı dosyası yolu
    """
    system = character.get("system", "UNKNOWN")
    name = character.get("name", "İsimsiz Karakter")
    
    html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Karakter Kağıdı</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 20px;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section h2 {{
            color: #2c3e50;
            font-size: 1.8em;
            margin-bottom: 15px;
            border-left: 5px solid #3498db;
            padding-left: 15px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .info-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #3498db;
        }}
        .info-item strong {{
            color: #2c3e50;
            display: block;
            margin-bottom: 5px;
        }}
        .info-item span {{
            color: #7f8c8d;
        }}
        .character-image {{
            text-align: center;
            margin: 20px 0;
        }}
        .character-image img {{
            max-width: 300px;
            max-height: 300px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .list-item {{
            background: #f8f9fa;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #27ae60;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{name}</h1>
            <div class="subtitle">Diyargezer - {system} Karakter Kağıdı</div>
        </div>
        <div class="content">
"""
    
    # Karakter resmi
    image_data = character.get("image")
    if image_data:
        html_content += """            <div class="character-image">
                <img src="data:image/png;base64,"""
        if isinstance(image_data, str) and image_data.startswith('data:'):
            # Base64 string'den sadece data kısmını al
            _, data = image_data.split(',', 1)
            html_content += data
        html_content += """ alt="Karakter Resmi">
            </div>
"""
    
    # Sistem bazlı içerik
    if system == "DND5E":
        html_content += _generate_dnd_html(character)
    elif system == "MUTANTS_AND_MASTERMINDS":
        html_content += _generate_mm_html(character)
    elif system == "VTM5E":
        html_content += _generate_vtm_html(character)
    else:
        html_content += _generate_generic_html(character)
    
    html_content += """        </div>
        <div class="footer">
            <p>Diyargezer FRP Karakter Oluşturucu - Oluşturulma Tarihi: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def _generate_dnd_html(character: dict) -> str:
    """D&D karakteri için HTML içeriği"""
    html = ""
    
    # Temel Bilgiler
    html += """            <div class="section">
                <h2>📋 Temel Bilgiler</h2>
                <div class="info-grid">
"""
    basic_fields = [
        ("race", "Irk"),
        ("class", "Sınıf"),
        ("background", "Arka Plan"),
        ("level", "Seviye"),
        ("alignment", "Hizalama"),
    ]
    for field, label in basic_fields:
        value = character.get(field, "")
        if value:
            html += f"""                    <div class="info-item">
                        <strong>{label}</strong>
                        <span>{value}</span>
                    </div>
"""
    html += """                </div>
            </div>
"""
    
    # Ability Scores
    abilities = character.get("abilities", {})
    if abilities:
        html += """            <div class="section">
                <h2>💪 Yetenek Puanları</h2>
                <div class="info-grid">
"""
        mods = character.get("ability_modifiers", {})
        for ability in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
            if ability in abilities:
                val = abilities[ability]
                mod = mods.get(ability, 0)
                html += f"""                    <div class="info-item">
                        <strong>{ability}</strong>
                        <span>{val} (mod {mod:+d})</span>
                    </div>
"""
        html += """                </div>
            </div>
"""
    
    # Skills
    skills = character.get("skills", {})
    if skills:
        html += """            <div class="section">
                <h2>🎯 Beceriler</h2>
"""
        profs = skills.get("proficiencies", {})
        if profs:
            for skill, prof in profs.items():
                if prof:
                    html += f"""                <div class="list-item">{skill}</div>
"""
        html += """            </div>
"""
    
    # Spells
    spells = character.get("spells", {})
    if spells:
        html += """            <div class="section">
                <h2>✨ Büyüler</h2>
"""
        for level, spell_list in spells.items():
            if spell_list:
                html += f"""                <h3>{level.replace('_', ' ').title()}</h3>
"""
                for spell in spell_list:
                    html += f"""                <div class="list-item">{spell}</div>
"""
        html += """            </div>
"""
    
    return html


def _generate_mm_html(character: dict) -> str:
    """M&M karakteri için HTML içeriği"""
    html = ""
    
    # Temel Bilgiler
    html += """            <div class="section">
                <h2>📋 Temel Bilgiler</h2>
                <div class="info-grid">
"""
    basic_fields = [
        ("codename", "Kod Adı"),
        ("power_level", "Power Level"),
        ("archetype", "Arketip"),
    ]
    for field, label in basic_fields:
        value = character.get(field, "")
        if value:
            html += f"""                    <div class="info-item">
                        <strong>{label}</strong>
                        <span>{value}</span>
                    </div>
"""
    html += """                </div>
            </div>
"""
    
    # Abilities
    abilities = character.get("abilities", {})
    if abilities:
        html += """            <div class="section">
                <h2>💪 Ability Scores</h2>
                <div class="info-grid">
"""
        for ability, value in abilities.items():
            html += f"""                    <div class="info-item">
                        <strong>{ability}</strong>
                        <span>{value}</span>
                    </div>
"""
        html += """                </div>
            </div>
"""
    
    # Defenses
    defenses = character.get("defenses", {})
    if defenses:
        html += """            <div class="section">
                <h2>🛡️ Savunmalar</h2>
                <div class="info-grid">
"""
        defense_labels = {
            "attack_bonus": "Attack Bonus",
            "effect_rank": "Effect Rank",
            "defense": "Defense",
            "toughness": "Toughness",
        }
        for key, label in defense_labels.items():
            value = defenses.get(key, 0)
            html += f"""                    <div class="info-item">
                        <strong>{label}</strong>
                        <span>{value}</span>
                    </div>
"""
        html += f"""                    <div class="info-item">
                        <strong>Power Points</strong>
                        <span>{character.get('power_points', 0)}</span>
                    </div>
"""
        html += """                </div>
            </div>
"""
    
    # Powers
    powers = character.get("powers", [])
    if powers:
        html += """            <div class="section">
                <h2>⚡ Powers</h2>
"""
        for power in powers:
            html += f"""                <div class="list-item">{power}</div>
"""
        html += """            </div>
"""
    
    return html


def _generate_vtm_html(character: dict) -> str:
    """VtM karakteri için HTML içeriği"""
    html = ""
    
    # Temel Bilgiler
    html += """            <div class="section">
                <h2>📋 Temel Bilgiler</h2>
                <div class="info-grid">
"""
    basic_fields = [
        ("clan", "Clan"),
        ("chronicle", "Chronicle"),
        ("concept", "Concept"),
        ("player", "Player"),
    ]
    for field, label in basic_fields:
        value = character.get(field, "")
        if value:
            html += f"""                    <div class="info-item">
                        <strong>{label}</strong>
                        <span>{value}</span>
                    </div>
"""
    html += """                </div>
            </div>
"""
    
    # Attributes
    attributes = character.get("attributes", {})
    if attributes:
        html += """            <div class="section">
                <h2>💪 Attributes</h2>
"""
        for category, attrs in attributes.items():
            html += f"""                <h3>{category}</h3>
                <div class="info-grid">
"""
            for attr, score in attrs.items():
                html += f"""                    <div class="info-item">
                        <strong>{attr}</strong>
                        <span>{score}</span>
                    </div>
"""
            html += """                </div>
"""
        html += """            </div>
"""
    
    # Skills
    skills = character.get("skills", {})
    if skills:
        html += """            <div class="section">
                <h2>🎯 Skills</h2>
"""
        for category, skill_dict in skills.items():
            html += f"""                <h3>{category}</h3>
                <div class="info-grid">
"""
            for skill, score in skill_dict.items():
                if score:
                    html += f"""                    <div class="info-item">
                        <strong>{skill}</strong>
                        <span>{score}</span>
                    </div>
"""
            html += """                </div>
"""
        html += """            </div>
"""
    
    # Disciplines
    disciplines = character.get("disciplines", [])
    if disciplines:
        html += """            <div class="section">
                <h2>🧛 Disciplines</h2>
"""
        for disc in disciplines:
            html += f"""                <div class="list-item">{disc}</div>
"""
        html += """            </div>
"""
    
    # Stats
    html += """            <div class="section">
                <h2>📊 İstatistikler</h2>
                <div class="info-grid">
"""
    html += f"""                    <div class="info-item">
                        <strong>Humanity</strong>
                        <span>{character.get('humanity', 0)}</span>
                    </div>
                    <div class="info-item">
                        <strong>Health</strong>
                        <span>{character.get('health', 0)}</span>
                    </div>
                    <div class="info-item">
                        <strong>Willpower</strong>
                        <span>{character.get('willpower', 0)}</span>
                    </div>
"""
    html += """                </div>
            </div>
"""
    
    return html


def _generate_generic_html(character: dict) -> str:
    """Genel karakter için HTML içeriği"""
    html = """            <div class="section">
                <h2>📋 Karakter Bilgileri</h2>
                <div class="info-grid">
"""
    for key, value in character.items():
        if key not in ["image", "system"] and value:
            if isinstance(value, (dict, list)):
                continue
            html += f"""                    <div class="info-item">
                        <strong>{key.replace('_', ' ').title()}</strong>
                        <span>{value}</span>
                    </div>
"""
    html += """                </div>
            </div>
"""
    return html


def export_character_json(character: dict, output_path: Path, pretty: bool = True) -> None:
    """
    Karakteri JSON formatında export et
    
    Args:
        character: Karakter verisi
        output_path: Çıktı dosyası yolu
        pretty: İndentli JSON (varsayılan: True)
    """
    with open(output_path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(character, f, ensure_ascii=False, indent=2)
        else:
            json.dump(character, f, ensure_ascii=False)


def export_character_csv(character: dict, output_path: Path) -> None:
    """
    Karakteri CSV formatında export et (basit tablo formatı)
    
    Args:
        character: Karakter verisi
        output_path: Çıktı dosyası yolu
    """
    system = character.get("system", "UNKNOWN")
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Başlık
        writer.writerow(["Özellik", "Değer"])
        writer.writerow([])
        
        # Temel bilgiler
        writer.writerow(["=== TEMEL BİLGİLER ==="])
        writer.writerow(["İsim", character.get("name", "")])
        writer.writerow(["Sistem", system])
        
        if system == "DND5E":
            writer.writerow(["Irk", character.get("race", "")])
            writer.writerow(["Sınıf", character.get("class", "")])
            writer.writerow(["Arka Plan", character.get("background", "")])
            writer.writerow(["Seviye", character.get("level", "")])
            
            writer.writerow([])
            writer.writerow(["=== YETENEK PUANLARI ==="])
            abilities = character.get("abilities", {})
            mods = character.get("ability_modifiers", {})
            for ability in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
                if ability in abilities:
                    val = abilities[ability]
                    mod = mods.get(ability, 0)
                    writer.writerow([ability, f"{val} (mod {mod:+d})"])
            
            writer.writerow([])
            writer.writerow(["=== BECERİLER ==="])
            skills = character.get("skills", {}).get("proficiencies", {})
            for skill, prof in skills.items():
                if prof:
                    writer.writerow([skill, "Proficient"])
            
            writer.writerow([])
            writer.writerow(["=== BÜYÜLER ==="])
            spells = character.get("spells", {})
            for level, spell_list in spells.items():
                if spell_list:
                    writer.writerow([level.replace("_", " ").title(), ", ".join(spell_list)])
        
        elif system == "MUTANTS_AND_MASTERMINDS":
            writer.writerow(["Kod Adı", character.get("codename", "")])
            writer.writerow(["Power Level", character.get("power_level", "")])
            writer.writerow(["Arketip", character.get("archetype", "")])
            
            writer.writerow([])
            writer.writerow(["=== ABILITY SCORES ==="])
            abilities = character.get("abilities", {})
            for ability, value in abilities.items():
                writer.writerow([ability, value])
            
            writer.writerow([])
            writer.writerow(["=== SAVUNMALAR ==="])
            defenses = character.get("defenses", {})
            defense_labels = {
                "attack_bonus": "Attack Bonus",
                "effect_rank": "Effect Rank",
                "defense": "Defense",
                "toughness": "Toughness",
            }
            for key, label in defense_labels.items():
                writer.writerow([label, defenses.get(key, 0)])
            writer.writerow(["Power Points", character.get("power_points", 0)])
            
            writer.writerow([])
            writer.writerow(["=== POWERS ==="])
            powers = character.get("powers", [])
            for power in powers:
                writer.writerow(["Power", power])
        
        elif system == "VTM5E":
            writer.writerow(["Clan", character.get("clan", "")])
            writer.writerow(["Chronicle", character.get("chronicle", "")])
            writer.writerow(["Concept", character.get("concept", "")])
            
            writer.writerow([])
            writer.writerow(["=== ATTRIBUTES ==="])
            attributes = character.get("attributes", {})
            for category, attrs in attributes.items():
                for attr, score in attrs.items():
                    writer.writerow([f"{category} - {attr}", score])
            
            writer.writerow([])
            writer.writerow(["=== SKILLS ==="])
            skills = character.get("skills", {})
            for category, skill_dict in skills.items():
                for skill, score in skill_dict.items():
                    if score:
                        writer.writerow([f"{category} - {skill}", score])
            
            writer.writerow([])
            writer.writerow(["=== DISCIPLINES ==="])
            disciplines = character.get("disciplines", [])
            for disc in disciplines:
                writer.writerow(["Discipline", disc])
            
            writer.writerow([])
            writer.writerow(["=== İSTATİSTİKLER ==="])
            writer.writerow(["Humanity", character.get("humanity", 0)])
            writer.writerow(["Health", character.get("health", 0)])
            writer.writerow(["Willpower", character.get("willpower", 0)])

