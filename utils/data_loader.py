import json
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from utils.performance import cached_load_json, LazyDataLoader

_DATA_CACHE: Dict[str, Dict[str, Any]] = {}
_LAZY_LOADERS: Dict[str, LazyDataLoader] = {}


def _load_json(path: Path) -> Dict[str, Any]:
    """JSON dosyasını yükle (cache ile)"""
    return cached_load_json(path, use_cache=True)


def _get_or_load(key: str, loader: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    if key not in _DATA_CACHE:
        _DATA_CACHE[key] = loader()
    return _DATA_CACHE[key]


def load_dnd_data(base_dir: Path, lazy: bool = False) -> Dict[str, Any]:
    """
    D&D verisini yükler. Ana dosya: data/dnd_data.json
    Ardından data/backgrounds/*.json içindeki tüm arka planları birleştirir.
    
    Args:
        base_dir: Proje ana dizini
        lazy: Lazy loading kullanılsın mı? (sadece gerektiğinde yükle)
    
    Returns:
        D&D verisi
    """
    if lazy:
        # Lazy loading kullan
        if "dnd" not in _LAZY_LOADERS:
            def _loader() -> Dict[str, Any]:
                data_path = base_dir / "data" / "dnd_data.json"
                data = _load_json(data_path)

                # Background uzantıları
                backgrounds_dir = base_dir / "data" / "backgrounds"
                merged_backgrounds: Dict[str, Any] = dict(data.get("backgrounds", {}))
                if backgrounds_dir.exists():
                    for file in sorted(backgrounds_dir.glob("*.json")):
                        try:
                            part = _load_json(file)
                            for name, payload in part.get("backgrounds", {}).items():
                                merged_backgrounds[name] = payload
                        except Exception:
                            # Bozuk dosyaları sessizce atla
                            continue
                data["backgrounds"] = merged_backgrounds
                return data
            
            _LAZY_LOADERS["dnd"] = LazyDataLoader(_loader)
        
        return _LAZY_LOADERS["dnd"].get()
    
    # Normal loading (cache ile)
    def _loader() -> Dict[str, Any]:
        data_path = base_dir / "data" / "dnd_data.json"
        data = _load_json(data_path)

        # Background uzantıları
        backgrounds_dir = base_dir / "data" / "backgrounds"
        merged_backgrounds: Dict[str, Any] = dict(data.get("backgrounds", {}))
        if backgrounds_dir.exists():
            for file in sorted(backgrounds_dir.glob("*.json")):
                try:
                    part = _load_json(file)
                    for name, payload in part.get("backgrounds", {}).items():
                        merged_backgrounds[name] = payload
                except Exception:
                    # Bozuk dosyaları sessizce atla
                    continue
        data["backgrounds"] = merged_backgrounds
        return data

    return _get_or_load("dnd", _loader)


def load_mm_data(base_dir: Path, lazy: bool = False) -> Dict[str, Any]:
    """M&M verisini cache'li şekilde döndür."""
    
    if lazy:
        if "mm" not in _LAZY_LOADERS:
            def _loader() -> Dict[str, Any]:
                data_path = base_dir / "data" / "mm_data.json"
                return _load_json(data_path)
            _LAZY_LOADERS["mm"] = LazyDataLoader(_loader)
        return _LAZY_LOADERS["mm"].get()
    
    def _loader() -> Dict[str, Any]:
        data_path = base_dir / "data" / "mm_data.json"
        return _load_json(data_path)

    return _get_or_load("mm", _loader)


def load_vtm_data(base_dir: Path, lazy: bool = False) -> Dict[str, Any]:
    """VtM verisini cache'li şekilde döndür."""
    
    if lazy:
        if "vtm" not in _LAZY_LOADERS:
            def _loader() -> Dict[str, Any]:
                data_path = base_dir / "data" / "vtm_data.json"
                return _load_json(data_path)
            _LAZY_LOADERS["vtm"] = LazyDataLoader(_loader)
        return _LAZY_LOADERS["vtm"].get()
    
    def _loader() -> Dict[str, Any]:
        data_path = base_dir / "data" / "vtm_data.json"
        return _load_json(data_path)

    return _get_or_load("vtm", _loader)


def clear_data_cache() -> None:
    """Tüm data cache'lerini temizle"""
    global _DATA_CACHE, _LAZY_LOADERS
    _DATA_CACHE.clear()
    for loader in _LAZY_LOADERS.values():
        loader.clear()
    _LAZY_LOADERS.clear()
