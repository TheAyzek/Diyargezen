"""
Pydantic Doğrulama Modelleri
============================
Scraper'lardan gelen ham veriyi standart bir JSON şemasına doğrulayan
ve normalleştiren modeller.

Her TTRPG sistemi farklı terminoloji kullansa da (race/ancestry/clan,
class/archetype/bloodline) çıktılar bu ortak şemalara dönüştürülür.
Böylece ``data/`` dizinindeki JSON dosyaları uygulama genelinde tutarlı kalır.

Pydantic v2 kullanılır; ``model_validate`` ve ``model_dump`` ile
seri/deseri yapılır.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


# ======================================================================
# Evrensel Etki Modeli (Universal Effect Model)
# ======================================================================

class EffectModel(BaseModel):
    """
    Herhangi bir TTRPG sistemindeki herhangi bir bonusu, yetkinligi
    veya kural degisikligini temsil eden evrensel etki modeli.

    Ornekler:
      D&D 5e   : target="strength",  effect_type="stat_bonus",      value=2
      PF 1e    : target="fortitude",  effect_type="save_bonus",      value=2
      VtM 5e   : target="potence",    effect_type="add_dot",         value=1
      M&M 3e   : target="dodge",      effect_type="defense_bonus",   value=2
    """
    target: str = Field(
        ..., min_length=1,
        description="Etkilenen hedef: yetenek, beceri, savunma, disiplin vb.",
    )
    effect_type: str = Field(
        ..., min_length=1,
        description=(
            "Etki turu: stat_bonus | save_bonus | skill_bonus | "
            "add_proficiency | add_dot | defense_bonus | speed_bonus | "
            "hp_bonus | ac_bonus | resistance | immunity | advantage | "
            "disadvantage | damage_bonus | power_rank | ability_rank | "
            "pool_bonus | discipline_access | set_value | grant_trait"
        ),
    )
    value: Any = Field(
        default=0,
        description="Etki degeri: int, bool, str ('1d4'), float, vb.",
    )
    condition: str = Field(
        default="",
        description="Kosullu etki: 'while raging', 'only in darkness', vb.",
    )
    source: str = Field(
        default="",
        description="Etkinin kaynagi: 'Dwarf Racial', 'Fighter L1', vb.",
    )

    @field_validator("target")
    @classmethod
    def _normalize_target(cls, v: str) -> str:
        return v.strip().lower().replace(" ", "_")

    @field_validator("effect_type")
    @classmethod
    def _normalize_effect_type(cls, v: str) -> str:
        return v.strip().lower().replace(" ", "_").replace("-", "_")


# ======================================================================
# Ortak Yardimci Modeller
# ======================================================================

class AbilityScoreBonus(BaseModel):
    """Yetenek puani artisi (or. +2 DEX, +1 tum)."""
    strength: int = 0
    dexterity: int = 0
    constitution: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0

    def has_any(self) -> bool:
        return any(v != 0 for v in self.model_dump().values())


class SourceReference(BaseModel):
    """Kaynak URL ve kitap referansi."""
    url: str = ""
    book: str = ""
    page: str = ""


# ======================================================================
# Irk / Ancestry Modeli
# ======================================================================

class RaceModel(BaseModel):
    """
    Standart ırk/ancestry şeması — tüm sistemler için ortak.

    D&D 5e   → "race"
    PF 1e    → "race"
    VtM 5e   → "clan" olarak map'lenir, ability_score_increase boş kalır
    M&M 3e   → "origin" olarak map'lenir
    """
    name: str = Field(..., min_length=1, description="Irk/ancestry adı")
    system: str = Field(..., description="Kaynak sistem: dnd5e | pathfinder1e | vtm5e | mm3e")
    description: str = ""
    ability_score_increase: Dict[str, int] = Field(
        default_factory=dict,
        description="Yetenek artışları: {'dexterity': 2, 'constitution': -2}",
    )
    ability_score_increase_text: str = ""
    speed: int = Field(default=30, ge=0, description="Temel hareket hızı (ft)")
    speed_special: str = ""
    size: str = Field(default="Medium", description="Small | Medium | Large")
    traits: List[str] = Field(default_factory=list, description="Irksal özellikler")
    languages: List[str] = Field(default_factory=list)
    extra_languages: int = 0
    vision: str = Field(default="Normal", description="Normal | Low-Light | Darkvision")
    effects: List[EffectModel] = Field(default_factory=list, description="Evrensel etki listesi")
    source: SourceReference = Field(default_factory=SourceReference)

    @field_validator("size")
    @classmethod
    def _normalize_size(cls, v: str) -> str:
        mapping = {"s": "Small", "m": "Medium", "l": "Large", "t": "Tiny"}
        return mapping.get(v.strip().lower(), v.strip().title())

    @field_validator("system")
    @classmethod
    def _normalize_system(cls, v: str) -> str:
        return v.strip().lower().replace(" ", "").replace("-", "")


# ======================================================================
# Sınıf / Class Modeli
# ======================================================================

class ClassModel(BaseModel):
    """
    Standart sınıf şeması.

    PF 1e: BAB, saves, skill ranks
    D&D 5e: hit_die, saving_throw_proficiencies
    """
    name: str = Field(..., min_length=1)
    system: str
    description: str = ""
    hit_die: str = Field(default="d8", description="Can zarı: d6 | d8 | d10 | d12")
    skill_ranks_per_level: int = Field(default=2, ge=0)
    class_skills: List[str] = Field(default_factory=list)
    proficiencies: List[str] = Field(default_factory=list)
    saving_throws: List[str] = Field(
        default_factory=list,
        description="PF1e: good saves; D&D5e: proficient saves",
    )
    spellcasting: bool = False
    spellcasting_type: str = Field(
        default="",
        description="none | prepared | spontaneous | pact | innate",
    )
    features: Dict[str, Any] = Field(
        default_factory=dict,
        description="Seviyeye gore sinif ozellikleri: {'1': [...], '2': [...]}",
    )
    effects: List[EffectModel] = Field(default_factory=list, description="Evrensel etki listesi")
    source: SourceReference = Field(default_factory=SourceReference)

    @field_validator("hit_die")
    @classmethod
    def _validate_hit_die(cls, v: str) -> str:
        v = v.strip().lower()
        if v and not v.startswith("d"):
            v = f"d{v}"
        return v

    @field_validator("system")
    @classmethod
    def _normalize_system(cls, v: str) -> str:
        return v.strip().lower().replace(" ", "").replace("-", "")


# ======================================================================
# Büyü / Spell Modeli
# ======================================================================

class SpellModel(BaseModel):
    """
    Standart büyü şeması — PF 1e ve D&D 5e ortak.

    PF 1e: levels_by_class + school + subschool
    D&D 5e: level + school + is_ritual
    """
    name: str = Field(..., min_length=1)
    system: str
    level: int = Field(default=0, ge=0, le=9)
    school: str = Field(default="", description="abjuration | conjuration | ...")
    subschool: str = ""
    descriptor: str = ""
    casting_time: str = ""
    components: str = ""
    material_components: str = ""
    focus: str = ""
    spell_range: str = Field(default="", alias="range", description="Menzil")
    area: str = ""
    target: str = ""
    effect: str = ""
    duration: str = ""
    saving_throw: str = ""
    spell_resistance: str = ""
    description: str = ""
    higher_levels: str = Field(default="", description="D&D 5e: 'At Higher Levels' metni")
    is_ritual: bool = Field(default=False, description="D&D 5e ritüel büyüsü mü?")
    concentration: bool = False
    levels_by_class: Dict[str, int] = Field(
        default_factory=dict,
        description="PF 1e: {'Wizard': 3, 'Cleric': 4}",
    )
    source: SourceReference = Field(default_factory=SourceReference)

    model_config = {"populate_by_name": True}

    @field_validator("school")
    @classmethod
    def _normalize_school(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("system")
    @classmethod
    def _normalize_system(cls, v: str) -> str:
        return v.strip().lower().replace(" ", "").replace("-", "")


# ======================================================================
# Feat / Yetenek Modeli
# ======================================================================

class FeatModel(BaseModel):
    """Standart feat/yetenek şeması."""
    name: str = Field(..., min_length=1)
    system: str
    description: str = ""
    feat_type: str = Field(
        default="General",
        description="General | Combat | Metamagic | Item Creation | ...",
    )
    prerequisites: List[str] = Field(default_factory=list)
    benefit: str = ""
    normal: str = Field(default="", description="Feat olmadan normal davranış")
    special: str = ""
    effects: List[EffectModel] = Field(default_factory=list, description="Evrensel etki listesi")
    source: SourceReference = Field(default_factory=SourceReference)

    @field_validator("system")
    @classmethod
    def _normalize_system(cls, v: str) -> str:
        return v.strip().lower().replace(" ", "").replace("-", "")


# ======================================================================
# M&M 3e — Power / Advantage Modelleri
# ======================================================================

class PowerModel(BaseModel):
    """M&M 3e guc (power) semasi."""
    name: str = Field(..., min_length=1)
    system: str = "mm3e"
    description: str = ""
    cost_per_rank: int = Field(default=1, description="Rank basina PP maliyeti")
    action: str = ""
    range: str = ""
    duration: str = ""
    effect_names: List[str] = Field(default_factory=list, description="Ham efekt isimleri")
    extras: List[str] = Field(default_factory=list)
    flaws: List[str] = Field(default_factory=list)
    effects: List[EffectModel] = Field(default_factory=list, description="Evrensel etki listesi")
    source: SourceReference = Field(default_factory=SourceReference)


class AdvantageModel(BaseModel):
    """M&M 3e avantaj semasi."""
    name: str = Field(..., min_length=1)
    system: str = "mm3e"
    description: str = ""
    cost: str = Field(default="1", description="PP maliyeti veya 'Ranked'")
    advantage_type: str = Field(default="General", description="Combat | Fortune | General | Skill")
    ranked: bool = False
    effects: List[EffectModel] = Field(default_factory=list, description="Evrensel etki listesi")
    source: SourceReference = Field(default_factory=SourceReference)


# ======================================================================
# VtM 5e — Clan / Discipline Modelleri
# ======================================================================

class ClanModel(BaseModel):
    """VtM 5e clan semasi."""
    name: str = Field(..., min_length=1)
    system: str = "vtm5e"
    description: str = ""
    bane: str = Field(default="", description="Clan laneti")
    compulsion: str = ""
    disciplines: List[str] = Field(default_factory=list, description="Clan disiplinleri")
    favored_attributes: List[str] = Field(default_factory=list)
    clan_weakness: str = ""
    effects: List[EffectModel] = Field(default_factory=list, description="Evrensel etki listesi")
    source: SourceReference = Field(default_factory=SourceReference)


class DisciplineModel(BaseModel):
    """VtM 5e disiplin şeması."""
    name: str = Field(..., min_length=1)
    system: str = "vtm5e"
    description: str = ""
    powers: Dict[str, str] = Field(
        default_factory=dict,
        description="Seviyeye gore guçler: {'1': 'Bond Famulus', ...}",
    )
    source: SourceReference = Field(default_factory=SourceReference)


# ======================================================================
# Tüm Veri Paketini Sarmalayan Kök Model
# ======================================================================

class SystemDataBundle(BaseModel):
    """
    Tek bir TTRPG sistemi için çekilen tüm verinin sarmalayıcısı.
    ``data/<system>_data.json`` dosyasına doğrudan yazılır.
    """
    system: str
    source: str = ""
    races: Dict[str, Any] = Field(default_factory=dict)
    classes: Dict[str, Any] = Field(default_factory=dict)
    spells: Dict[str, Any] = Field(default_factory=dict)
    feats: Dict[str, Any] = Field(default_factory=dict)
    items: Dict[str, Any] = Field(default_factory=dict)
    skills: Dict[str, Any] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(
        default_factory=dict,
        description="Sisteme özgü ek veriler (backgrounds, archetypes vb.)",
    )

    def merge_into(self, existing: Dict[str, Any]) -> Dict[str, Any]:
        """Mevcut JSON verisinin üzerine non-destructive merge yap."""
        for section in ("races", "classes", "spells", "feats", "items", "skills"):
            new_data = getattr(self, section)
            if new_data:
                existing.setdefault(section, {}).update(new_data)
        for key, val in self.extra.items():
            if val:
                existing.setdefault(key, {}).update(val) if isinstance(val, dict) else None
        return existing
