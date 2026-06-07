"""
Data Loader Module
==================
data/ dizinindeki JSON veri dosyalarını performanslı bir önbellekleme
(cache) mekanizmasıyla yükler.

Özellikler:
  - Thread-safe LRU cache ile tekrarlı diskten okumaları engeller
  - Lazy loading: veri yalnızca ilk erişimde yüklenir
  - Dosya değişiklik zamanı (mtime) ile otomatik cache invalidation
  - Sistem bazlı normalizasyon (D&D, Pathfinder)
  - Singleton instance: modül çapında tek bir DataLoader kullanılır

Kullanım:
    from utils.data_loader import get_loader
    loader = get_loader()          # singleton
    dnd   = loader.load("dnd")
    pf    = loader.load("pathfinder_1e")
    loader.clear_cache()           # belleği serbest bırak
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# ======================================================================
# Low-level cache
# ======================================================================

class _LRUCache:
    """Thread-safe LRU (Least Recently Used) cache."""

    def __init__(self, max_size: int = 64):
        self._max_size = max_size
        self._store: Dict[str, Tuple[Any, float]] = {}  # key -> (value, access_time)
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, _ = entry
            self._store[key] = (value, time.monotonic())
            return value

    def put(self, key: str, value: Any) -> None:
        with self._lock:
            if key not in self._store and len(self._store) >= self._max_size:
                oldest = min(self._store, key=lambda k: self._store[k][1])
                del self._store[oldest]
            self._store[key] = (value, time.monotonic())

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)


# ======================================================================
# JSON disk reader with mtime check
# ======================================================================

_file_cache = _LRUCache(max_size=128)
_mtime_registry: Dict[str, float] = {}
_mtime_lock = Lock()


def _load_json_cached(path: Path) -> Dict[str, Any]:
    """
    JSON dosyasını disk-cache'li olarak oku.
    Dosya mtime değişmişse cache'i otomatik invalidate eder.
    """
    key = str(path.resolve())
    current_mtime = 0.0
    try:
        current_mtime = os.path.getmtime(key)
    except OSError:
        pass

    with _mtime_lock:
        cached_mtime = _mtime_registry.get(key, 0.0)
        if current_mtime != cached_mtime:
            _file_cache.invalidate(key)
            _mtime_registry[key] = current_mtime

    cached = _file_cache.get(key)
    if cached is not None:
        return cached

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    _file_cache.put(key, data)
    return data


# ======================================================================
# DataLoader class
# ======================================================================

class DataLoader:
    """
    Merkezi veri yükleyici.

    Tüm TTRPG sistemlerinin JSON verilerini önbellekli olarak yükler.
    Aynı veri ikinci istendiğinde diskten okuma yapılmaz; bellekteki
    önbellekten döndürülür.
    """

    SYSTEM_FILES: Dict[str, str] = {
        "dnd": "dnd_data.json",
        "pathfinder_1e": "pathfinder_1e_data.json",
        "mm": "mm_data.json",
    }

    def __init__(self, base_dir: Optional[Path] = None):
        self._base_dir = base_dir or Path(__file__).parent.parent
        self._cache = _LRUCache(max_size=32)

    # ---- public API --------------------------------------------------

    def load(self, system_key: str) -> Dict[str, Any]:
        """Sisteme ait JSON verisini yükle (cache destekli)."""
        cached = self._cache.get(system_key)
        if cached is not None:
            return cached

        _loaders: Dict[str, Callable[[], Dict[str, Any]]] = {
            "dnd": self._load_dnd,
            "pathfinder_1e": self._load_pathfinder,
            "mm": lambda: self._load_simple("mm_data.json"),
        }

        loader_fn = _loaders.get(system_key)
        if loader_fn is None:
            available = ", ".join(sorted(_loaders.keys()))
            raise ValueError(f"Bilinmeyen sistem: '{system_key}'. Mevcut: {available}")

        data = loader_fn()
        self._cache.put(system_key, data)
        return data

    def clear_cache(self) -> None:
        """Tüm önbelleği temizle."""
        self._cache.clear()
        _file_cache.clear()
        with _mtime_lock:
            _mtime_registry.clear()
        logger.debug("DataLoader cache temizlendi")

    @property
    def cache_size(self) -> int:
        return self._cache.size

    # ---- internal loaders --------------------------------------------

    def _json(self, filename: str) -> Dict[str, Any]:
        return _load_json_cached(self._base_dir / "data" / filename)

    def _load_simple(self, filename: str) -> Dict[str, Any]:
        return self._json(filename)

    def _load_dnd(self) -> Dict[str, Any]:
        data = self._json("dnd_data.json")
        backgrounds_dir = self._base_dir / "data" / "backgrounds"
        merged: Dict[str, Any] = dict(data.get("backgrounds", {}))
        if backgrounds_dir.exists():
            for fp in sorted(backgrounds_dir.glob("*.json")):
                try:
                    part = _load_json_cached(fp)
                    for name, payload in part.get("backgrounds", {}).items():
                        merged[name] = payload
                except Exception:
                    logger.warning("Background dosyası okunamadı: %s", fp)
                    continue
            data["backgrounds"] = merged
        return _normalize_dnd_data(data)

    def _load_pathfinder(self) -> Dict[str, Any]:
        data = self._json("pathfinder_1e_data.json")
        return _normalize_pathfinder_data(data)


# ======================================================================
# Singleton accessor
# ======================================================================

_singleton_loader: Optional[DataLoader] = None
_singleton_lock = Lock()


def get_loader(base_dir: Optional[Path] = None) -> DataLoader:
    """Modül çapında tekil (singleton) DataLoader döndür."""
    global _singleton_loader
    if _singleton_loader is None:
        with _singleton_lock:
            if _singleton_loader is None:
                _singleton_loader = DataLoader(base_dir)
    return _singleton_loader


# ======================================================================
# Normalization helpers
# ======================================================================

def _normalize_dnd_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """D&D veri kalitesi normalizasyonu."""
    for key, val in data.get("races", {}).items():
        if isinstance(val, dict) and not val.get("name"):
            val["name"] = key

    classes = data.get("classes", {})
    for k in [k for k in classes if k != k.title() and k.title() in classes]:
        del classes[k]
    for key, val in classes.items():
        if not isinstance(val, dict):
            continue
        if "hit_die" in val and "hit_dice" not in val:
            val["hit_dice"] = val["hit_die"]
        elif "hit_dice" in val and "hit_die" not in val:
            val["hit_die"] = val["hit_dice"]
        if not val.get("name"):
            val["name"] = key
        val.setdefault("proficiencies", {"armor": [], "weapons": [], "tools": [], "languages": []})

    for name, sp in data.get("spells", {}).items():
        if not isinstance(sp, dict):
            continue
        level = sp.get("level")
        if level is None:
            sp["level"] = 0
        elif isinstance(level, str):
            try:
                sp["level"] = int(level)
            except ValueError:
                sp["level"] = 0
        elif isinstance(level, float):
            sp["level"] = int(level)
        if not sp.get("name"):
            sp["name"] = name

    for key, val in data.get("backgrounds", {}).items():
        if isinstance(val, dict):
            if not val.get("name"):
                val["name"] = key
            val.setdefault("equipment", [])

    return data


def _normalize_pathfinder_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Pathfinder 1e veri kalitesi normalizasyonu."""
    spells = data.get("spells", {})
    if not spells:
        return data
    try:
        from utils.pathfinder_scraper import clean_all_spells, CORE_PF1E_SPELLS
        cleaned = clean_all_spells(spells)
        for name, spell_data in CORE_PF1E_SPELLS.items():
            if name not in cleaned:
                cleaned[name] = spell_data
            elif len(cleaned[name].get("casting_time", "")) > 100:
                cleaned[name] = spell_data
        data["spells"] = cleaned
    except ImportError:
        pass
    return data


# ======================================================================
# Module-level convenience functions (backward compat)
# ======================================================================

def load_dnd_data(base_dir: Path, lazy: bool = False) -> Dict[str, Any]:
    """D&D verisini yükler (cache destekli)."""
    return get_loader(base_dir).load("dnd")


def load_mm_data(base_dir: Path, lazy: bool = False) -> Dict[str, Any]:
    """M&M verisini yükler (cache destekli)."""
    return get_loader(base_dir).load("mm")


def load_pathfinder_1e_data(base_dir: Path, lazy: bool = False) -> Dict[str, Any]:
    """Pathfinder 1e verisini yükler (cache destekli)."""
    return get_loader(base_dir).load("pathfinder_1e")


def clear_data_cache() -> None:
    """Tüm data cache'lerini temizle (singleton dahil)."""
    global _singleton_loader
    if _singleton_loader is not None:
        _singleton_loader.clear_cache()
    _file_cache.clear()
    with _mtime_lock:
        _mtime_registry.clear()
