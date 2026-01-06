"""
Son açılan dosyalar yönetimi
Son açılan karakterler ve şablonlar listesi
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def _get_recent_files_path(base_dir: Path) -> Path:
    """Son açılan dosyalar JSON dosyası yolu"""
    return base_dir / "characters" / ".recent_files.json"


def add_recent_character(base_dir: Path, character_file_path: str, character_name: str = "") -> None:
    """
    Son açılan karakterler listesine ekle
    
    Args:
        base_dir: Proje ana dizini
        character_file_path: Karakter dosyası yolu
        character_name: Karakter adı (opsiyonel)
    """
    recent_path = _get_recent_files_path(base_dir)
    recent_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Mevcut listeyi yükle
    recent_files = load_recent_characters(base_dir)
    
    # Yeni giriş
    new_entry = {
        "file_path": character_file_path,
        "character_name": character_name,
        "timestamp": datetime.now().isoformat(),
        "access_count": 1
    }
    
    # Eğer zaten listede varsa, erişim sayısını artır ve tarihi güncelle
    for entry in recent_files:
        if entry.get("file_path") == character_file_path:
            entry["access_count"] = entry.get("access_count", 1) + 1
            entry["timestamp"] = datetime.now().isoformat()
            if character_name:
                entry["character_name"] = character_name
            # Listeyi kaydet
            with open(recent_path, "w", encoding="utf-8") as f:
                json.dump(recent_files, f, ensure_ascii=False, indent=2)
            return
    
    # Yeni giriş ekle
    recent_files.insert(0, new_entry)
    
    # Son 20 karakteri sakla
    recent_files = recent_files[:20]
    
    # Kaydet
    with open(recent_path, "w", encoding="utf-8") as f:
        json.dump(recent_files, f, ensure_ascii=False, indent=2)


def load_recent_characters(base_dir: Path) -> List[Dict[str, Any]]:
    """
    Son açılan karakterler listesini yükle
    
    Args:
        base_dir: Proje ana dizini
    
    Returns:
        Son açılan karakterler listesi
    """
    recent_path = _get_recent_files_path(base_dir)
    
    if not recent_path.exists():
        return []
    
    try:
        with open(recent_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Dosya yollarını kontrol et ve geçersiz olanları kaldır
            valid_entries = []
            for entry in data:
                file_path = entry.get("file_path", "")
                if file_path and Path(file_path).exists():
                    valid_entries.append(entry)
            return valid_entries
    except Exception:
        return []


def clear_recent_characters(base_dir: Path) -> None:
    """
    Son açılan karakterler listesini temizle
    
    Args:
        base_dir: Proje ana dizini
    """
    recent_path = _get_recent_files_path(base_dir)
    if recent_path.exists():
        recent_path.unlink()


def get_recent_templates(base_dir: Path, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Sık kullanılan şablonları getir
    
    Args:
        base_dir: Proje ana dizini
        limit: Maksimum şablon sayısı
    
    Returns:
        Sık kullanılan şablonlar listesi
    """
    from utils.template_manager import list_templates
    
    templates = list_templates(base_dir)
    
    # Erişim sayısına göre sırala (eğer metadata varsa)
    # Şimdilik tarihe göre sırala
    templates.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return templates[:limit]

