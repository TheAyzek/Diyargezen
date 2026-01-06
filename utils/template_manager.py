"""
Karakter şablon yönetimi modülü
Şablon kaydetme, yükleme, listeleme ve silme işlemleri
"""
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


def _ensure_templates_dir(base_dir: Path) -> Path:
    """Şablon klasörünü oluştur ve döndür"""
    templates_dir = base_dir / "characters" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    return templates_dir


def save_template(character: Dict[str, Any], base_dir: Path, template_name: str, description: str = "") -> Path:
    """
    Karakteri şablon olarak kaydet (isim ve sistem bilgisi hariç)
    
    Args:
        character: Karakter verisi
        base_dir: Proje ana dizini
        template_name: Şablon adı
        description: Şablon açıklaması (opsiyonel)
    
    Returns:
        Kaydedilen şablon dosyası yolu
    """
    templates_dir = _ensure_templates_dir(base_dir)
    
    # Şablon verisi oluştur (isim ve sistem bilgisi hariç)
    template_data = {
        "template_name": template_name,
        "description": description,
        "system": character.get("system"),
        "created_at": datetime.now().isoformat(),
        "template_data": {}
    }
    
    # Karakter verisini kopyala (isim hariç)
    for key, value in character.items():
        if key not in ["name", "system"]:
            template_data["template_data"][key] = value
    
    # Dosya adını oluştur
    safe_name = template_name.replace(" ", "_").replace("/", "_")
    template_path = templates_dir / f"{safe_name}.json"
    
    # Şablonu kaydet
    with open(template_path, "w", encoding="utf-8") as f:
        json.dump(template_data, f, ensure_ascii=False, indent=2)
    
    return template_path


def load_template(template_path: Path) -> Optional[Dict[str, Any]]:
    """
    Şablon dosyasını yükle
    
    Args:
        template_path: Şablon dosyası yolu
    
    Returns:
        Şablon verisi veya None
    """
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def list_templates(base_dir: Path, system_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Tüm şablonları listele
    
    Args:
        base_dir: Proje ana dizini
        system_filter: Sistem filtresi (opsiyonel)
    
    Returns:
        Şablon listesi
    """
    templates_dir = _ensure_templates_dir(base_dir)
    templates = []
    
    if not templates_dir.exists():
        return templates
    
    for template_path in templates_dir.glob("*.json"):
        template_data = load_template(template_path)
        if template_data:
            if system_filter and template_data.get("system") != system_filter:
                continue
            template_data["_file_path"] = str(template_path)
            templates.append(template_data)
    
    # Tarihe göre sırala (en yeni önce)
    templates.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return templates


def delete_template(template_path: Path) -> bool:
    """
    Şablon dosyasını sil
    
    Args:
        template_path: Şablon dosyası yolu
    
    Returns:
        Başarılı ise True
    """
    try:
        if template_path.exists():
            template_path.unlink()
            return True
    except Exception:
        pass
    return False


def create_character_from_template(template: Dict[str, Any], character_name: str) -> Dict[str, Any]:
    """
    Şablondan yeni karakter oluştur
    
    Args:
        template: Şablon verisi
        character_name: Yeni karakter adı
    
    Returns:
        Karakter verisi
    """
    template_data = template.get("template_data", {})
    
    # Karakter verisini oluştur
    character = {
        "system": template.get("system"),
        "name": character_name,
        **template_data
    }
    
    return character

