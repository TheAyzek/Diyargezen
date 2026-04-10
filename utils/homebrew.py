"""
Universal Homebrew Content Manager
Tum TTRPG sistemleri icin ozel icerik olusturma ve yonetme
D&D 5e, Pathfinder 1e, VtM 5e, M&M 3e destegi
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

HOMEBREW_DIR = Path(__file__).resolve().parent.parent / "data" / "homebrew"


# Sistem bazli homebrew sablonlari
HOMEBREW_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "dnd5e": {
        "race": {
            "template": {
                "name": "", "source": "Homebrew",
                "ability_score_increase": {},
                "speed": 30, "size": "Medium",
                "traits": [], "languages": ["Common"],
                "description": ""
            },
            "required": ["name", "ability_score_increase"],
            "display_name": "Irk (Race)"
        },
        "class": {
            "template": {
                "name": "", "source": "Homebrew",
                "hit_die": 8, "primary_ability": "",
                "saving_throws": [], "armor_proficiencies": [],
                "weapon_proficiencies": [], "skill_choices": [],
                "skill_count": 2, "spellcasting": False,
                "features": {}, "description": ""
            },
            "required": ["name", "hit_die"],
            "display_name": "Sinif (Class)"
        },
        "spell": {
            "template": {
                "name": "", "source": "Homebrew",
                "level": 0, "school": "evocation",
                "casting_time": "1 action", "range": "60 feet",
                "components": "V, S", "duration": "Instantaneous",
                "classes": [], "description": "",
                "ritual": False, "concentration": False
            },
            "required": ["name", "level", "school"],
            "display_name": "Buyu (Spell)"
        },
        "feat": {
            "template": {
                "name": "", "source": "Homebrew",
                "prerequisite": "", "description": "",
                "benefits": []
            },
            "required": ["name"],
            "display_name": "Feat"
        },
        "item": {
            "template": {
                "name": "", "source": "Homebrew",
                "type": "weapon", "rarity": "common",
                "attunement": False, "description": "",
                "properties": {}
            },
            "required": ["name", "type"],
            "display_name": "Esya (Item)"
        },
        "background": {
            "template": {
                "name": "", "source": "Homebrew",
                "skill_proficiencies": [], "tool_proficiencies": [],
                "languages": [], "equipment": [],
                "feature": "", "description": ""
            },
            "required": ["name"],
            "display_name": "Arka Plan (Background)"
        },
    },
    "pathfinder1e": {
        "race": {
            "template": {
                "name": "", "source": "Homebrew",
                "ability_score_increase": {},
                "speed": 30, "size": "Medium",
                "traits": [], "languages": ["Common"],
                "description": ""
            },
            "required": ["name"],
            "display_name": "Irk (Race)"
        },
        "spell": {
            "template": {
                "name": "", "source": "Homebrew",
                "level": 0, "school": "evocation",
                "casting_time": "1 standard action",
                "components": "V, S", "range": "medium",
                "duration": "instantaneous",
                "saving_throw": "none", "spell_resistance": "no",
                "levels_by_class": {}, "description": ""
            },
            "required": ["name", "level"],
            "display_name": "Buyu (Spell)"
        },
        "feat": {
            "template": {
                "name": "", "source": "Homebrew",
                "type": "General", "prerequisite": "",
                "benefit": "", "description": ""
            },
            "required": ["name"],
            "display_name": "Feat"
        },
    },
    "vtm5e": {
        "clan": {
            "template": {
                "name": "", "source": "Homebrew",
                "disciplines": [], "bane": "",
                "compulsion": "", "description": ""
            },
            "required": ["name", "disciplines"],
            "display_name": "Klan (Clan)"
        },
        "discipline": {
            "template": {
                "name": "", "source": "Homebrew",
                "type": "Physical",
                "levels": {
                    "1": {"name": "", "cost": "", "description": ""},
                    "2": {"name": "", "cost": "", "description": ""},
                    "3": {"name": "", "cost": "", "description": ""},
                },
                "description": ""
            },
            "required": ["name"],
            "display_name": "Disiplin (Discipline)"
        },
        "predator_type": {
            "template": {
                "name": "", "source": "Homebrew",
                "description": "",
                "bonus_discipline": "",
                "specialty": ""
            },
            "required": ["name"],
            "display_name": "Avcı Tipi (Predator Type)"
        },
        "loresheet": {
            "template": {
                "name": "", "source": "Homebrew",
                "levels": {},
                "description": ""
            },
            "required": ["name"],
            "display_name": "Lore Sheet"
        },
    },
    "mm3e": {
        "power": {
            "template": {
                "name": "", "source": "Homebrew",
                "type": "Attack", "action": "Standard",
                "range": "Ranged", "duration": "Instant",
                "cost_per_rank": 1, "description": "",
                "extras": [], "flaws": []
            },
            "required": ["name", "type"],
            "display_name": "Guc (Power)"
        },
        "advantage": {
            "template": {
                "name": "", "source": "Homebrew",
                "type": "General", "ranked": False,
                "description": ""
            },
            "required": ["name"],
            "display_name": "Avantaj (Advantage)"
        },
        "archetype": {
            "template": {
                "name": "", "source": "Homebrew",
                "power_level": 10,
                "abilities": {}, "skills": {},
                "powers": [], "advantages": [],
                "description": ""
            },
            "required": ["name"],
            "display_name": "Arketip (Archetype)"
        },
        "complication": {
            "template": {
                "name": "", "source": "Homebrew",
                "type": "Motivation",
                "description": ""
            },
            "required": ["name"],
            "display_name": "Komplikasyon (Complication)"
        },
    },
}


def get_homebrew_types(system: str) -> Dict[str, str]:
    """Sistem icin mevcut homebrew turlerini dondur"""
    templates = HOMEBREW_TEMPLATES.get(system, {})
    return {key: val["display_name"] for key, val in templates.items()}


def get_homebrew_template(system: str, content_type: str) -> Dict[str, Any]:
    """Belirli bir homebrew turu icin bos sablon dondur"""
    return HOMEBREW_TEMPLATES.get(system, {}).get(content_type, {}).get("template", {}).copy()


def get_required_fields(system: str, content_type: str) -> List[str]:
    """Zorunlu alanlari dondur"""
    return HOMEBREW_TEMPLATES.get(system, {}).get(content_type, {}).get("required", [])


def validate_homebrew(system: str, content_type: str, data: Dict[str, Any]) -> List[str]:
    """Homebrew icerigini dogrula"""
    errors = []
    required = get_required_fields(system, content_type)
    for field in required:
        if field not in data or not data[field]:
            errors.append(f"Zorunlu alan eksik: {field}")
    return errors


def save_homebrew(system: str, content_type: str, data: Dict[str, Any]) -> Path:
    """Homebrew icerigini kaydet"""
    # Dizin olustur
    save_dir = HOMEBREW_DIR / system
    save_dir.mkdir(parents=True, exist_ok=True)

    # Dosya adi
    name = data.get("name", "unnamed").lower().replace(" ", "_")
    filename = f"{content_type}_{name}.json"
    filepath = save_dir / filename

    # Metadata ekle
    data["_homebrew_meta"] = {
        "system": system,
        "type": content_type,
        "created": datetime.now().isoformat(),
        "version": "1.0"
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def load_all_homebrew(system: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Tum homebrew iceriklerini yukle"""
    result = {}

    if not HOMEBREW_DIR.exists():
        return result

    search_dirs = []
    if system:
        sys_dir = HOMEBREW_DIR / system
        if sys_dir.exists():
            search_dirs.append(sys_dir)
    else:
        for d in HOMEBREW_DIR.iterdir():
            if d.is_dir():
                search_dirs.append(d)

    for sys_dir in search_dirs:
        sys_name = sys_dir.name
        for json_file in sys_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                meta = data.get("_homebrew_meta", {})
                content_type = meta.get("type", "unknown")
                key = f"{sys_name}/{content_type}"
                if key not in result:
                    result[key] = []
                result[key].append(data)
            except Exception:
                continue

    return result


def delete_homebrew(filepath: Path) -> bool:
    """Homebrew dosyasini sil"""
    try:
        if filepath.exists():
            filepath.unlink()
            return True
    except Exception:
        pass
    return False


def inject_homebrew_into_data(system_data: Dict[str, Any], system: str) -> Dict[str, Any]:
    """
    Homebrew iceriklerini sistem verisine enjekte et.
    Ornegin: Homebrew race'leri dnd_data.json'daki races'e ekle.
    """
    homebrew = load_all_homebrew(system)

    for key, items in homebrew.items():
        _, content_type = key.split("/", 1)

        # Sistem verisindeki dogru section'a ekle
        if content_type == "race":
            section = system_data.setdefault("races", {})
        elif content_type == "class":
            section = system_data.setdefault("classes", {})
        elif content_type == "spell":
            section = system_data.setdefault("spells", {})
        elif content_type == "feat":
            section = system_data.setdefault("feats", {})
        elif content_type == "item":
            section = system_data.setdefault("equipment", {}).setdefault("items", {})
        elif content_type == "background":
            section = system_data.setdefault("backgrounds", {})
        elif content_type == "clan":
            section = system_data.setdefault("clans", {})
        elif content_type == "discipline":
            section = system_data.setdefault("disciplines", {})
        elif content_type == "power":
            section = system_data.setdefault("powers", {})
        elif content_type == "advantage":
            section = system_data.setdefault("advantages", {})
        elif content_type == "archetype":
            section = system_data.setdefault("archetypes", {})
        else:
            continue

        for item in items:
            name = item.get("name", "")
            if name and isinstance(section, dict):
                section[name] = item

    return system_data

