from pathlib import Path
from typing import Dict, Any, Callable
from utils.performance import cached_load_json, LazyDataLoader

_DATA_CACHE: Dict[str, Dict[str, Any]] = {}
_LAZY_LOADERS: Dict[str, LazyDataLoader] = {}


def _load_json(path: Path) -> Dict[str, Any]:
    """JSON dosyasını yükle (cache ile)"""
    return cached_load_json(path, use_cache=True)


def _normalize_dnd_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    D&D veri kalitesi normalizasyonu:
    - Race'lerde eksik 'name' alanini doldur
    - Class'larda hit_die / hit_dice tutarliligini sagla
    - Duplicate lowercase class'lari kaldir
    - Spell'lerde null/gecersiz level degerlerini duzelt
    - Background'larda eksik alanlari doldur
    """
    # --- RACE NORMALIZASYONU ---
    races = data.get("races", {})
    for key, val in races.items():
        if isinstance(val, dict):
            if "name" not in val or not val.get("name"):
                val["name"] = key

    # --- CLASS NORMALIZASYONU ---
    classes = data.get("classes", {})
    # Lowercase duplicate'lari kaldir
    lowercase_dupes = [k for k in list(classes.keys()) if k != k.title() and k.title() in classes]
    for k in lowercase_dupes:
        del classes[k]

    for key, val in classes.items():
        if not isinstance(val, dict):
            continue
        # hit_die <-> hit_dice senkronizasyonu
        if "hit_die" in val and "hit_dice" not in val:
            val["hit_dice"] = val["hit_die"]
        elif "hit_dice" in val and "hit_die" not in val:
            val["hit_die"] = val["hit_dice"]
        # name eksikse ekle
        if "name" not in val or not val.get("name"):
            val["name"] = key
        # proficiencies eksikse ekle
        if "proficiencies" not in val:
            val["proficiencies"] = {"armor": [], "weapons": [], "tools": [], "languages": []}

    # --- SPELL NORMALIZASYONU ---
    spells = data.get("spells", {})
    for name, sp in spells.items():
        if not isinstance(sp, dict):
            continue
        level = sp.get("level")
        # null level -> 0 (cantrip varsayimi)
        if level is None:
            sp["level"] = 0
        # string level -> int
        elif isinstance(level, str):
            try:
                sp["level"] = int(level)
            except ValueError:
                sp["level"] = 0
        # float -> int
        elif isinstance(level, float):
            sp["level"] = int(level)
        # name eksikse ekle
        if "name" not in sp or not sp.get("name"):
            sp["name"] = name

    # --- BACKGROUND NORMALIZASYONU ---
    backgrounds = data.get("backgrounds", {})
    for key, val in backgrounds.items():
        if isinstance(val, dict):
            if "name" not in val or not val.get("name"):
                val["name"] = key
            if "equipment" not in val:
                val["equipment"] = []

    return data


def _get_or_load(key: str, loader: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    if key not in _DATA_CACHE:
        _DATA_CACHE[key] = loader()
    return _DATA_CACHE[key]


def load_dnd_data(base_dir: Path, lazy: bool = False) -> Dict[str, Any]:
    """
    D&D verisini yükler. Ana dosya: data/dnd_data.json
    Ardından data/backgrounds/*.json içindeki tüm arka planları birleştirir.
    """
    if lazy:
        if "dnd" not in _LAZY_LOADERS:
            def _loader() -> Dict[str, Any]:
                data_path = base_dir / "data" / "dnd_data.json"
                data = _load_json(data_path)

                backgrounds_dir = base_dir / "data" / "backgrounds"
                merged_backgrounds: Dict[str, Any] = dict(data.get("backgrounds", {}))
                if backgrounds_dir.exists():
                    for file in sorted(backgrounds_dir.glob("*.json")):
                        try:
                            part = _load_json(file)
                            for name, payload in part.get("backgrounds", {}).items():
                                merged_backgrounds[name] = payload
                        except Exception:
                            continue
                data["backgrounds"] = merged_backgrounds
                return _normalize_dnd_data(data)

            _LAZY_LOADERS["dnd"] = LazyDataLoader(_loader)
        return _LAZY_LOADERS["dnd"].get()

    def _loader() -> Dict[str, Any]:
        data_path = base_dir / "data" / "dnd_data.json"
        data = _load_json(data_path)

        backgrounds_dir = base_dir / "data" / "backgrounds"
        merged_backgrounds: Dict[str, Any] = dict(data.get("backgrounds", {}))
        if backgrounds_dir.exists():
            for file in sorted(backgrounds_dir.glob("*.json")):
                try:
                    part = _load_json(file)
                    for name, payload in part.get("backgrounds", {}).items():
                        merged_backgrounds[name] = payload
                except Exception:
                    continue
        data["backgrounds"] = merged_backgrounds
        return _normalize_dnd_data(data)

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


def _normalize_pathfinder_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pathfinder 1e veri kalitesi normalizasyonu:
    - Bozuk spell verisini temizle (birbirine karismis alanlar)
    - Core spell'lerin mevcut oldugundan emin ol
    - levels_by_class'tan bozuk key'leri kaldir
    """
    spells = data.get("spells", {})
    if not spells:
        return data

    try:
        from utils.pathfinder_scraper import clean_all_spells, CORE_PF1E_SPELLS

        # Mevcut spell'leri temizle
        cleaned = clean_all_spells(spells)

        # Core spell'leri ekle/guncelle
        for name, spell_data in CORE_PF1E_SPELLS.items():
            if name not in cleaned:
                cleaned[name] = spell_data
            else:
                # Bozuk mu kontrol et
                ct = cleaned[name].get("casting_time", "")
                if ct and len(ct) > 100:
                    cleaned[name] = spell_data

        data["spells"] = cleaned
    except ImportError:
        pass

    return data


def load_pathfinder_1e_data(base_dir: Path, lazy: bool = False) -> Dict[str, Any]:
    """Pathfinder 1e verisini cache'li şekilde döndür."""
    if lazy:
        if "pathfinder_1e" not in _LAZY_LOADERS:
            def _loader() -> Dict[str, Any]:
                data_path = base_dir / "data" / "pathfinder_1e_data.json"
                data = _load_json(data_path)
                return _normalize_pathfinder_data(data)
            _LAZY_LOADERS["pathfinder_1e"] = LazyDataLoader(_loader)
        return _LAZY_LOADERS["pathfinder_1e"].get()

    def _loader() -> Dict[str, Any]:
        data_path = base_dir / "data" / "pathfinder_1e_data.json"
        data = _load_json(data_path)
        return _normalize_pathfinder_data(data)

    return _get_or_load("pathfinder_1e", _loader)


def clear_data_cache() -> None:
    """Tüm data cache'lerini temizle"""
    global _DATA_CACHE, _LAZY_LOADERS
    _DATA_CACHE.clear()
    for loader in _LAZY_LOADERS.values():
        loader.clear()
    _LAZY_LOADERS.clear()
