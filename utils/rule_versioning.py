"""
Kural Versiyonlama Modülü
Kural versiyonlarını takip eder ve geri yüklemeyi sağlar.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class RuleVersion:
    """Kural versiyonu"""
    version_id: str  # Timestamp bazlı ID
    timestamp: str  # ISO format timestamp
    description: str  # Kullanıcı açıklaması (opsiyonel)
    rules: Dict[str, Any]  # Kural verisi


def get_versions_dir(base_dir: Path, system: str) -> Path:
    """Versiyonlar klasörünü oluştur ve döndür"""
    versions_dir = base_dir / "data" / "rules" / "versions" / system.lower()
    versions_dir.mkdir(parents=True, exist_ok=True)
    return versions_dir


def get_versions_metadata_file(base_dir: Path, system: str) -> Path:
    """Versiyon metadata dosyasının yolunu döndür"""
    rules_dir = base_dir / "data" / "rules"
    return rules_dir / f"{system.lower()}_versions.json"


def create_version_id() -> str:
    """Yeni versiyon ID oluştur (timestamp bazlı)"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_version(rules: Dict[str, Any], base_dir: Path, system: str, description: str = "") -> RuleVersion:
    """
    Kural versiyonunu kaydet
    
    Args:
        rules: Kaydedilecek kurallar
        base_dir: Proje base dizini
        system: Sistem adı
        description: Versiyon açıklaması
    
    Returns:
        Oluşturulan versiyon
    """
    version_id = create_version_id()
    timestamp = datetime.now().isoformat()
    
    version = RuleVersion(
        version_id=version_id,
        timestamp=timestamp,
        description=description,
        rules=rules.copy()
    )
    
    # Versiyon dosyasını kaydet
    versions_dir = get_versions_dir(base_dir, system)
    version_file = versions_dir / f"{system.lower()}_v{version_id}.json"
    
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(version), f, ensure_ascii=False, indent=2)
    
    # Metadata dosyasını güncelle
    metadata_file = get_versions_metadata_file(base_dir, system)
    versions_list = load_versions_list(base_dir, system)
    
    # Yeni versiyonu başa ekle (en yeni önce)
    versions_list.insert(0, {
        "version_id": version_id,
        "timestamp": timestamp,
        "description": description,
        "file": str(version_file.relative_to(base_dir))
    })
    
    # Son 50 versiyonu sakla (eski versiyonları sil)
    if len(versions_list) > 50:
        # Eski versiyon dosyalarını sil
        for old_version in versions_list[50:]:
            old_file = base_dir / old_version["file"]
            if old_file.exists():
                old_file.unlink()
        versions_list = versions_list[:50]
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(versions_list, f, ensure_ascii=False, indent=2)
    
    return version


def load_versions_list(base_dir: Path, system: str) -> List[Dict[str, Any]]:
    """
    Versiyon listesini yükle
    
    Returns:
        Versiyon metadata listesi (en yeni önce)
    """
    metadata_file = get_versions_metadata_file(base_dir, system)
    
    if not metadata_file.exists():
        return []
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def load_version(base_dir: Path, system: str, version_id: str) -> Optional[RuleVersion]:
    """
    Belirli bir versiyonu yükle
    
    Args:
        base_dir: Proje base dizini
        system: Sistem adı
        version_id: Versiyon ID
    
    Returns:
        Versiyon verisi veya None
    """
    versions_list = load_versions_list(base_dir, system)
    
    # Versiyon metadata'sını bul
    version_meta = None
    for v in versions_list:
        if v["version_id"] == version_id:
            version_meta = v
            break
    
    if not version_meta:
        return None
    
    # Versiyon dosyasını yükle
    version_file = base_dir / version_meta["file"]
    
    if not version_file.exists():
        return None
    
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            version_data = json.load(f)
            return RuleVersion(**version_data)
    except Exception:
        return None


def restore_version(base_dir: Path, system: str, version_id: str) -> bool:
    """
    Belirli bir versiyonu geri yükle (aktif kurallar olarak)
    
    Args:
        base_dir: Proje base dizini
        system: Sistem adı
        version_id: Geri yüklenecek versiyon ID
    
    Returns:
        Başarılı ise True
    """
    version = load_version(base_dir, system, version_id)
    
    if not version:
        return False
    
    # Mevcut kuralları versiyon olarak kaydet (geri dönüş için)
    from utils.rule_storage import load_rules, save_rules
    
    current_rules = load_rules(base_dir, system)
    if current_rules:
        save_version(current_rules, base_dir, system, "Geri yükleme öncesi otomatik yedek")
    
    # Versiyonu aktif kurallar olarak kaydet
    save_rules(version.rules, base_dir, system)
    
    return True


def delete_version(base_dir: Path, system: str, version_id: str) -> bool:
    """
    Belirli bir versiyonu sil
    
    Args:
        base_dir: Proje base dizini
        system: Sistem adı
        version_id: Silinecek versiyon ID
    
    Returns:
        Başarılı ise True
    """
    versions_list = load_versions_list(base_dir, system)
    
    # Versiyon metadata'sını bul ve sil
    version_meta = None
    for i, v in enumerate(versions_list):
        if v["version_id"] == version_id:
            version_meta = versions_list.pop(i)
            break
    
    if not version_meta:
        return False
    
    # Versiyon dosyasını sil
    version_file = base_dir / version_meta["file"]
    if version_file.exists():
        version_file.unlink()
    
    # Metadata dosyasını güncelle
    metadata_file = get_versions_metadata_file(base_dir, system)
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(versions_list, f, ensure_ascii=False, indent=2)
    
    return True


def format_version_info(version_meta: Dict[str, Any]) -> str:
    """
    Versiyon bilgisini formatla
    
    Returns:
        Formatlanmış versiyon bilgisi
    """
    timestamp = version_meta.get("timestamp", "")
    description = version_meta.get("description", "")
    
    try:
        dt = datetime.fromisoformat(timestamp)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        formatted_time = timestamp
    
    if description:
        return f"{formatted_time} - {description}"
    else:
        return formatted_time

