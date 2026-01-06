"""
Karakter versiyonlama modülü
Karakter değişiklik geçmişi, versiyon geri yükleme ve değişiklik notları
"""
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib


def _ensure_versions_dir(base_dir: Path, character_name: str) -> Path:
    """Versiyon klasörünü oluştur ve döndür"""
    safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).rstrip() or "karakter"
    versions_dir = base_dir / "characters" / "versions" / safe_name
    versions_dir.mkdir(parents=True, exist_ok=True)
    return versions_dir


def _get_character_hash(character: dict) -> str:
    """Karakter verisinin hash'ini hesapla (değişiklik tespiti için)"""
    # Image verisini hash'ten çıkar (çok büyük olabilir)
    char_copy = character.copy()
    if "image" in char_copy:
        del char_copy["image"]
    
    char_str = json.dumps(char_copy, sort_keys=True)
    return hashlib.md5(char_str.encode()).hexdigest()


def save_character_version(
    character: dict,
    base_dir: Path,
    character_file_path: str,
    change_note: str = ""
) -> Optional[Path]:
    """
    Karakter versiyonunu kaydet
    
    Args:
        character: Karakter verisi
        base_dir: Proje ana dizini
        character_file_path: Karakter dosyası yolu
        change_note: Değişiklik notu (opsiyonel)
    
    Returns:
        Kaydedilen versiyon dosyası yolu veya None (değişiklik yoksa)
    """
    character_name = character.get("name", "İsimsiz")
    versions_dir = _ensure_versions_dir(base_dir, character_name)
    
    # Mevcut versiyonları kontrol et
    existing_versions = list_character_versions(base_dir, character_file_path)
    
    # Eğer versiyon varsa, son versiyonla karşılaştır
    if existing_versions:
        last_version = load_character_version(existing_versions[-1]["file_path"])
        if last_version:
            current_hash = _get_character_hash(character)
            last_hash = _get_character_hash(last_version.get("character_data", {}))
            
            # Değişiklik yoksa versiyon kaydetme
            if current_hash == last_hash:
                return None
    
    # Yeni versiyon oluştur
    timestamp = datetime.now()
    version_number = len(existing_versions) + 1
    
    version_data = {
        "version_number": version_number,
        "timestamp": timestamp.isoformat(),
        "character_name": character_name,
        "character_file_path": character_file_path,
        "change_note": change_note,
        "character_data": character
    }
    
    # Versiyon dosyası adı
    safe_timestamp = timestamp.strftime("%Y%m%d_%H%M%S")
    version_file = versions_dir / f"version_{version_number:04d}_{safe_timestamp}.json"
    
    # Versiyonu kaydet
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(version_data, f, ensure_ascii=False, indent=2)
    
    # Eski versiyonları temizle (son 50 versiyonu sakla)
    _cleanup_old_versions(versions_dir, keep_count=50)
    
    return version_file


def load_character_version(version_path: Path) -> Optional[Dict[str, Any]]:
    """
    Versiyon dosyasını yükle
    
    Args:
        version_path: Versiyon dosyası yolu
    
    Returns:
        Versiyon verisi veya None
    """
    try:
        with open(version_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def list_character_versions(base_dir: Path, character_file_path: str) -> List[Dict[str, Any]]:
    """
    Karakterin tüm versiyonlarını listele
    
    Args:
        base_dir: Proje ana dizini
        character_file_path: Karakter dosyası yolu
    
    Returns:
        Versiyon listesi (tarihe göre sıralı)
    """
    # Karakter dosyasından isim al
    try:
        with open(character_file_path, "r", encoding="utf-8") as f:
            character = json.load(f)
            character_name = character.get("name", "İsimsiz")
    except Exception:
        return []
    
    versions_dir = _ensure_versions_dir(base_dir, character_name)
    
    if not versions_dir.exists():
        return []
    
    versions = []
    for version_file in sorted(versions_dir.glob("version_*.json")):
        version_data = load_character_version(version_file)
        if version_data:
            version_data["file_path"] = str(version_file)
            versions.append(version_data)
    
    # Tarihe göre sırala (en yeni önce)
    versions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return versions


def restore_character_version(version_path: Path, target_file_path: str) -> bool:
    """
    Versiyonu geri yükle
    
    Args:
        version_path: Versiyon dosyası yolu
        target_file_path: Hedef karakter dosyası yolu
    
    Returns:
        Başarılı ise True
    """
    try:
        version_data = load_character_version(version_path)
        if not version_data:
            return False
        
        character_data = version_data.get("character_data", {})
        if not character_data:
            return False
        
        # Mevcut karakteri yedekle
        target_path = Path(target_file_path)
        if target_path.exists():
            backup_path = target_path.with_suffix(".json.backup")
            target_path.rename(backup_path)
        
        # Versiyonu geri yükle
        with open(target_file_path, "w", encoding="utf-8") as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception:
        return False


def delete_character_version(version_path: Path) -> bool:
    """
    Versiyon dosyasını sil
    
    Args:
        version_path: Versiyon dosyası yolu
    
    Returns:
        Başarılı ise True
    """
    try:
        if version_path.exists():
            version_path.unlink()
            return True
    except Exception:
        pass
    return False


def _cleanup_old_versions(versions_dir: Path, keep_count: int = 50) -> None:
    """Eski versiyonları temizle (son N versiyonu sakla)"""
    try:
        version_files = sorted(versions_dir.glob("version_*.json"))
        if len(version_files) > keep_count:
            # En eski versiyonları sil
            for old_file in version_files[:-keep_count]:
                old_file.unlink()
    except Exception:
        pass


def compare_versions(version1_path: Path, version2_path: Path) -> Dict[str, Any]:
    """
    İki versiyonu karşılaştır
    
    Args:
        version1_path: İlk versiyon dosyası yolu
        version2_path: İkinci versiyon dosyası yolu
    
    Returns:
        Karşılaştırma sonuçları
    """
    v1_data = load_character_version(version1_path)
    v2_data = load_character_version(version2_path)
    
    if not v1_data or not v2_data:
        return {"error": "Versiyon yüklenemedi"}
    
    char1 = v1_data.get("character_data", {})
    char2 = v2_data.get("character_data", {})
    
    # Basit karşılaştırma (hash bazlı)
    hash1 = _get_character_hash(char1)
    hash2 = _get_character_hash(char2)
    
    return {
        "version1": {
            "version_number": v1_data.get("version_number", 0),
            "timestamp": v1_data.get("timestamp", ""),
            "change_note": v1_data.get("change_note", ""),
            "hash": hash1
        },
        "version2": {
            "version_number": v2_data.get("version_number", 0),
            "timestamp": v2_data.get("timestamp", ""),
            "change_note": v2_data.get("change_note", ""),
            "hash": hash2
        },
        "identical": hash1 == hash2
    }

