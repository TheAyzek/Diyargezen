"""
Universal Character Portrait Manager
Tum TTRPG sistemleri icin karakter portresi yonetimi
Resim ekleme, goruntuleme, boyutlandirma
"""

import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

PORTRAITS_DIR = Path(__file__).resolve().parent.parent / "data" / "portraits"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
THUMBNAIL_SIZE = (150, 150)
DISPLAY_SIZE = (300, 400)

# Sistem bazli varsayilan portre boyutlari
SYSTEM_PORTRAIT_SIZES = {
    "dnd5e": {"display": (300, 400), "thumbnail": (100, 133)},
    "pathfinder1e": {"display": (300, 400), "thumbnail": (100, 133)},
    "vtm5e": {"display": (280, 380), "thumbnail": (93, 126)},
    "mm3e": {"display": (320, 420), "thumbnail": (107, 140)},
}


def ensure_portraits_dir():
    """Portre dizinini olustur"""
    PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)


def get_portrait_path(character_name: str, system: str = "dnd5e") -> Path:
    """Karakter icin portre dosya yolunu olustur"""
    ensure_portraits_dir()
    safe_name = "".join(c for c in character_name if c.isalnum() or c in "._- ").strip()
    safe_name = safe_name.replace(" ", "_").lower()
    return PORTRAITS_DIR / f"{system}_{safe_name}"


def validate_portrait_file(filepath: str) -> List[str]:
    """Portre dosyasini dogrula"""
    errors = []
    path = Path(filepath)

    if not path.exists():
        errors.append("Dosya bulunamadi")
        return errors

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        errors.append(f"Desteklenmeyen format: {path.suffix}. Desteklenen: {', '.join(ALLOWED_EXTENSIONS)}")

    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        errors.append(f"Dosya cok buyuk: {size_mb:.1f}MB (max: 5MB)")

    return errors


def add_portrait(character_name: str, source_path: str,
                 system: str = "dnd5e") -> Optional[Path]:
    """Karakter'e portre ekle"""
    errors = validate_portrait_file(source_path)
    if errors:
        raise ValueError("; ".join(errors))

    source = Path(source_path)
    dest_base = get_portrait_path(character_name, system)
    dest = dest_base.with_suffix(source.suffix.lower())

    # Dosyayi kopyala
    shutil.copy2(source, dest)

    return dest


def remove_portrait(character_name: str, system: str = "dnd5e") -> bool:
    """Karakter'in portresini sil"""
    portrait = find_portrait(character_name, system)
    if portrait and portrait.exists():
        portrait.unlink()
        return True
    return False


def find_portrait(character_name: str, system: str = "dnd5e") -> Optional[Path]:
    """Karakter'in portresini bul"""
    base = get_portrait_path(character_name, system)
    for ext in ALLOWED_EXTENSIONS:
        candidate = base.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None


def has_portrait(character_name: str, system: str = "dnd5e") -> bool:
    """Karakter'in portresi var mi kontrol et"""
    return find_portrait(character_name, system) is not None


def get_all_portraits() -> Dict[str, Path]:
    """Tum portreleri listele"""
    ensure_portraits_dir()
    result = {}
    for f in PORTRAITS_DIR.iterdir():
        if f.suffix.lower() in ALLOWED_EXTENSIONS:
            result[f.stem] = f
    return result


def set_portrait_on_character(character: Dict[str, Any], portrait_path: str) -> Dict[str, Any]:
    """Karakter verisine portre bilgisi ekle"""
    character["portrait"] = str(portrait_path)
    return character


def get_portrait_from_character(character: Dict[str, Any]) -> Optional[str]:
    """Karakter verisinden portre yolunu al"""
    return character.get("portrait")


def get_display_size(system: str = "dnd5e") -> tuple:
    """Sistem icin varsayilan goruntuleme boyutunu dondur"""
    return SYSTEM_PORTRAIT_SIZES.get(system, {"display": DISPLAY_SIZE})["display"]


def get_thumbnail_size(system: str = "dnd5e") -> tuple:
    """Sistem icin varsayilan thumbnail boyutunu dondur"""
    return SYSTEM_PORTRAIT_SIZES.get(system, {"thumbnail": THUMBNAIL_SIZE})["thumbnail"]

