"""
Base Character Creator - Abstract Base Class (ABC) & Factory Pattern
====================================================================
Tüm TTRPG sistemlerinin miras alacağı ortak arayüzü tanımlar.

Soyut (abstract) metodlar:
  - create_character()      : İnteraktif karakter oluşturma
  - validate_character()    : Kural doğrulama
  - calculate_stats()       : Türetilmiş istatistik hesaplama
  - export_data()           : Seri hale getirilebilir veri dışa aktarma

Ortak (concrete) metodlar:
  - roll_dice(), roll_sum(), roll_4d6_drop_lowest()
  - calculate_ability_modifier(), add_ability_bonus()
  - list_available_races(), list_available_classes()
  - _prompt_selection()

Factory Pattern:
  - CreatorFactory: Sistem anahtarına göre doğru creator üretir;
    d20 vs d10 dice pool farklılıklarını meta-veri olarak taşır.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import logging
import random

logger = logging.getLogger(__name__)


# ======================================================================
# Dice System Meta-data
# ======================================================================

@dataclass(frozen=True)
class DiceSystem:
    """Bir TTRPG sisteminin zar mekanik tanımı."""
    name: str               # "d20", "d10_pool", "d6_pool", ...
    base_die: int           # Temel zar yüzü (20, 10, 6, ...)
    pool_based: bool        # Havuz (pool) sistemi mi?
    description: str = ""

DICE_D20 = DiceSystem("d20", 20, False, "Single d20 roll + modifiers (D&D, Pathfinder)")
DICE_D10_POOL = DiceSystem("d10_pool", 10, True, "d10 dice pool, successes on 6+ (VtM)")
DICE_D6_POOL = DiceSystem("d6_pool", 6, True, "d6 dice pool (M&M effect rolls)")


# ======================================================================
# Abstract Base Class
# ======================================================================

class BaseCharacterCreator(ABC):
    """
    Tüm TTRPG karakter oluşturucularının miras aldığı soyut temel sınıf.

    Alt sınıflar ``DICE_SYSTEM`` sınıf değişkenini tanımlamalı ve
    aşağıdaki dört metodu MUTLAKA implemente etmelidir:

    * ``create_character()``
    * ``validate_character()``
    * ``calculate_stats()``
    * ``export_data()``

    ``calculate_derived_stats()`` geriye dönük uyumluluk için
    ``calculate_stats()``'a yönlendirilir.
    """

    DICE_SYSTEM: DiceSystem = DICE_D20

    def __init__(self, system_name: str, data_file: str):
        self.system_name: str = system_name
        self.data_file: str = data_file
        self.data: Dict[str, Any] = self._load_data()

    # ------------------------------------------------------------------
    # Veri Yükleme
    # ------------------------------------------------------------------

    def _load_data(self) -> Dict[str, Any]:
        """Sisteme özel JSON veri dosyasını güvenli biçimde yükle."""
        data_path = Path(__file__).parent.parent / "data" / self.data_file
        try:
            with data_path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            raise FileNotFoundError(f"Veri dosyası bulunamadı: {data_path}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Geçersiz JSON formatı ({data_path}): {exc}")

    def get_system_name(self) -> str:
        """Sistemin görüntüleme adını döndür."""
        return self.system_name

    # ------------------------------------------------------------------
    # Abstract Methods
    # ------------------------------------------------------------------

    @abstractmethod
    def create_character(self) -> Dict[str, Any]:
        """Yeni bir karakter oluştur (interaktif)."""
        ...

    @abstractmethod
    def validate_character(self, character: Dict[str, Any]) -> List[str]:
        """Karakter verisini doğrula; hata listesi döndür (boş = geçerli)."""
        ...

    @abstractmethod
    def calculate_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Türetilmiş istatistikleri hesapla (HP, AC, saves, vb.)."""
        ...

    @abstractmethod
    def export_data(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """
        Karakteri dışa aktarılabilir (JSON-serializable) formata dönüştür.
        PDF veya dosya export'ları bu metodu kaynak olarak kullanır.
        """
        ...

    # Geriye dönük uyumluluk: eski kod "calculate_derived_stats" çağırıyorsa
    def calculate_derived_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Alias: ``calculate_stats()``'a yönlendirir (backward compat)."""
        return self.calculate_stats(character)

    # ------------------------------------------------------------------
    # Ortak: Zar Hesaplama
    # ------------------------------------------------------------------

    @staticmethod
    def roll_dice(num_dice: int, die_size: int) -> List[int]:
        """*num_dice* adet *die_size* yüzlü zar at; her birinin sonucunu döndür."""
        if num_dice < 1 or die_size < 2:
            raise ValueError(f"Geçersiz zar parametreleri: {num_dice}d{die_size}")
        return [random.randint(1, die_size) for _ in range(num_dice)]

    @staticmethod
    def roll_sum(num_dice: int, die_size: int) -> int:
        """Zar at ve toplamını döndür."""
        return sum(BaseCharacterCreator.roll_dice(num_dice, die_size))

    @staticmethod
    def roll_4d6_drop_lowest() -> int:
        """Klasik D&D yetenek üretimi: 4d6, en düşüğü at."""
        rolls = BaseCharacterCreator.roll_dice(4, 6)
        rolls.sort()
        return sum(rolls[1:])

    # ------------------------------------------------------------------
    # Ortak: Yetenek Hesaplama
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_ability_modifier(score: int) -> int:
        """Evrensel yetenek modifier: (score - 10) // 2"""
        return (score - 10) // 2

    def add_ability_bonus(
        self,
        abilities: Dict[str, int],
        ability_name: str,
        bonus: int,
    ) -> Dict[str, int]:
        """Belirtilen yeteneğe bonus ekle (immutable - kopya döndürür)."""
        updated = abilities.copy()
        if ability_name in updated:
            updated[ability_name] += bonus
        else:
            logger.warning("Bilinmeyen yetenek: %s", ability_name)
        return updated

    # ------------------------------------------------------------------
    # Ortak: Veri Sorgulama
    # ------------------------------------------------------------------

    def list_available_races(self) -> List[str]:
        """Mevcut ırk isimlerini sıralı olarak döndür."""
        return sorted(self.data.get("races", {}).keys())

    def list_available_classes(self) -> List[str]:
        """Mevcut sınıf isimlerini sıralı olarak döndür."""
        return sorted(self.data.get("classes", {}).keys())

    def get_race_data(self, race_name: str) -> Optional[Dict[str, Any]]:
        """Belirtilen ırkın verisini döndür; yoksa None."""
        return self.data.get("races", {}).get(race_name)

    def get_class_data(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Belirtilen sınıfın verisini döndür; yoksa None."""
        return self.data.get("classes", {}).get(class_name)

    # ------------------------------------------------------------------
    # Ortak: İnteraktif CLI Yardımcıları
    # ------------------------------------------------------------------

    @staticmethod
    def _prompt_selection(options: List[str], prompt: str) -> str:
        """Kullanıcıya numaralı liste göster ve seçim al."""
        print(f"\n{prompt}")
        for idx, option in enumerate(options, 1):
            print(f"  {idx}) {option}")
        while True:
            try:
                choice = int(input("Seçiminiz: "))
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                print(f"1-{len(options)} arası seçin.")
            except ValueError:
                print("Geçerli bir sayı girin.")

    # ------------------------------------------------------------------
    # Ortak: Karakter Kaydetme / Yükleme (JSON dosya)
    # ------------------------------------------------------------------

    def save_character(self, character: Dict[str, Any], filename: str) -> bool:
        """Karakteri characters/ dizinine JSON olarak kaydet."""
        try:
            chars_dir = Path(__file__).parent.parent / "characters"
            chars_dir.mkdir(exist_ok=True)
            filepath = chars_dir / f"{filename}.json"
            with filepath.open("w", encoding="utf-8") as fh:
                json.dump(character, fh, indent=2, ensure_ascii=False)
            return True
        except (OSError, TypeError) as exc:
            logger.error("Karakter kaydedilemedi: %s", exc)
            return False

    def load_character(self, filename: str) -> Dict[str, Any]:
        """Karakteri JSON dosyasından yükle."""
        chars_dir = Path(__file__).parent.parent / "characters"
        filepath = chars_dir / f"{filename}.json"
        if not filepath.exists():
            raise FileNotFoundError(f"Karakter dosyası bulunamadı: {filepath}")
        with filepath.open("r", encoding="utf-8") as fh:
            return json.load(fh)


# ======================================================================
# Factory Pattern -- CreatorFactory
# ======================================================================

class CreatorFactory:
    """
    Factory Pattern: Sistem anahtarına göre doğru creator instance'ı üretir.
    Ayrıca her sistemin zar mekanik bilgisini (d20 vs d10 pool) taşır.

    Kullanım::

        CreatorFactory.register("dnd5e", DND5ECreator)
        creator = CreatorFactory.create("dnd5e")
        print(creator.DICE_SYSTEM)  # DiceSystem(name='d20', ...)
    """

    _creators: Dict[str, type] = {}

    @classmethod
    def register(cls, system_key: str, creator_class: type) -> None:
        """Bir creator sınıfını sistem anahtarıyla kaydet (case-insensitive)."""
        if not (isinstance(creator_class, type) and issubclass(creator_class, BaseCharacterCreator)):
            raise TypeError(
                f"{creator_class} BaseCharacterCreator alt sınıfı olmalıdır"
            )
        cls._creators[system_key.lower()] = creator_class

    # Backward-compat alias
    register_creator = register

    @classmethod
    def create(cls, system_key: str) -> BaseCharacterCreator:
        """Kayıtlı creator'dan yeni bir instance oluştur."""
        key = system_key.lower()
        if key not in cls._creators:
            available = ", ".join(sorted(cls._creators.keys()))
            raise ValueError(f"Bilinmeyen sistem: '{system_key}'. Mevcut: {available}")
        return cls._creators[key]()

    # Backward-compat alias
    create_creator = create

    @classmethod
    def get_available_systems(cls) -> List[str]:
        """Kayıtlı sistem anahtarlarının listesini döndür."""
        return list(cls._creators.keys())

    @classmethod
    def get_dice_system(cls, system_key: str) -> DiceSystem:
        """Belirtilen sistemin zar mekanik bilgisini döndür."""
        creator = cls.create(system_key)
        return creator.DICE_SYSTEM

    @classmethod
    def get_system_info(cls) -> Dict[str, Dict[str, Any]]:
        """Tüm kayıtlı sistemlerin meta-bilgisini döndür."""
        info: Dict[str, Dict[str, Any]] = {}
        seen: set = set()
        for key, klass in cls._creators.items():
            class_name = klass.__name__
            if class_name in seen:
                continue
            seen.add(class_name)
            ds = klass.DICE_SYSTEM
            info[key] = {
                "class": class_name,
                "dice_system": ds.name,
                "base_die": ds.base_die,
                "pool_based": ds.pool_based,
            }
        return info


# Backward-compat alias
CharacterFactory = CreatorFactory
