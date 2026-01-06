"""
Kural Saklama/Yükleme Modülü
Çıkarılan kuralları JSON formatında saklar ve yükler.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


def get_rules_dir(base_dir: Path) -> Path:
    """Kurallar klasörünü oluştur ve döndür"""
    rules_dir = base_dir / "data" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    return rules_dir


def save_rules(rules: Dict[str, Any], base_dir: Path, system: str, create_version: bool = True, version_description: str = "") -> Path:
    """
    Kuralları JSON dosyasına kaydet
    
    Args:
        rules: Kaydedilecek kurallar
        base_dir: Proje base dizini
        system: Sistem adı
        create_version: Versiyon oluşturulsun mu (default: True)
        version_description: Versiyon açıklaması
    
    Returns:
        Kaydedilen dosya yolu
    """
    rules_dir = get_rules_dir(base_dir)
    rules_file = rules_dir / f"{system.lower()}_rules.json"
    
    # Mevcut kuralları versiyon olarak kaydet (varsa)
    if create_version and rules_file.exists():
        try:
            from utils.rule_versioning import save_version, load_rules
            current_rules = load_rules(base_dir, system)
            if current_rules:
                # Sadece kurallar değiştiyse versiyon oluştur
                if current_rules != rules:
                    desc = version_description or "Otomatik yedek"
                    save_version(current_rules, base_dir, system, desc)
        except Exception:
            # Versiyonlama hatası durumunda devam et
            pass
    
    # Kuralları kaydet
    with open(rules_file, 'w', encoding='utf-8') as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    
    return rules_file


def load_rules(base_dir: Path, system: str) -> Optional[Dict[str, Any]]:
    """
    Kuralları JSON dosyasından yükle
    """
    rules_dir = get_rules_dir(base_dir)
    rules_file = rules_dir / f"{system.lower()}_rules.json"
    
    if not rules_file.exists():
        return None
    
    try:
        with open(rules_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def merge_rules_with_defaults(custom_rules: Dict[str, Any], default_rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Özel kuralları varsayılan kurallarla birleştir
    Özel kurallar önceliklidir
    """
    merged = default_rules.copy()
    
    if 'rules' in custom_rules:
        if 'rules' not in merged:
            merged['rules'] = {}
        merged['rules'].update(custom_rules['rules'])
    
    return merged


def list_available_rules(base_dir: Path) -> Dict[str, bool]:
    """
    Mevcut kural dosyalarını listele
    """
    rules_dir = get_rules_dir(base_dir)
    systems = ['dnd5e', 'mutants_and_masterminds', 'vtm5e']
    
    available = {}
    for system in systems:
        rules_file = rules_dir / f"{system}_rules.json"
        available[system] = rules_file.exists()
    
    return available

