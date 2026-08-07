"""
Diyargezen Rules Engine API Router
==================================
Pathfinder 1st Edition (PF1e) kural verilerini ve soft-block denetimlerini sunan API rotaları.

Akademik Mimari Notu:
---------------------
Bu servis, d20pfsrd/aonprd scraper verileri ile Foundry VTT veri setlerini birleştiren
Unified Rules DB mimarisini kullanır. Arama sorgularında öncelikle Foundry VTT şemalarına
başvurulur; eksik veri veya özel alan bulunması durumunda Scraper fallback katmanı devreye girer.
Prerequisite (ön koşul) denetimlerinde sert engeller yerine soft-validation uyarısı ve
'is_overridden' (GM İzniyle Ez) bayrağı sunulur.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.entity import EntityResponseSchema
from app.services.rules_service import RulesService


router = APIRouter(prefix="/rules", tags=["Rules"])
service = RulesService()


@router.get(
    "/{system}/races",
    response_model=List[EntityResponseSchema],
    summary="Oynanabilir Irkları Getir",
    description="Belirtilen kural sistemi (örn: pathfinder1e) için oynanabilir tüm ana ırkları getirir."
)
@router.get(
    "/{system}/race",
    response_model=List[EntityResponseSchema],
    include_in_schema=False
)
def get_races(system: str, query: str = Query("", description="Irk adı veya açıklama arama filtresi")):
    races = service.get_races(system, query=query)
    return [EntityResponseSchema.model_validate(r, from_attributes=True) for r in races]

@router.get(
    "/{system}/subraces",
    response_model=List[EntityResponseSchema],
    summary="Alt Irk / Miras (Subrace/Heritage) Getir",
    description="Seçilen ana ırk için alt ırk veya alt miras türlerini listeler."
)
def get_subraces(system: str, parent_race: str):
    subraces = service.get_subraces(system, parent_race)
    return [EntityResponseSchema.model_validate(r, from_attributes=True) for r in subraces]

@router.get(
    "/{system}/classes",
    response_model=List[EntityResponseSchema],
    summary="Sınıf ve Arketip Kataloğunu Getir",
    description="Sistemde tanımlı tüm temel sınıfları ve arketipleri getirir."
)
@router.get(
    "/{system}/class",
    response_model=List[EntityResponseSchema],
    include_in_schema=False
)
def get_classes(system: str, query: str = Query("", description="Sınıf adı veya arketip arama filtresi")):
    classes = service.get_classes(system, query=query)
    return [EntityResponseSchema.model_validate(c, from_attributes=True) for c in classes]

@router.get(
    "/{system}/feats",
    response_model=List[EntityResponseSchema],
    summary="Feat (Yetenek/Haret) Arama & Listeleme",
    description="Arama metni ve kategori filtresine (Combat, Teamwork, Metamagic vb.) göre feat listesini getirir."
)
def search_feats(
    system: str,
    query: str = Query("", description="Feat adı veya açıklama arama filtresi"),
    category: str = Query("", description="Feat kategorisi (Combat, Teamwork, Metamagic vb.)"),
    class_name: str = Query("", description="Kullanıcı sınıfı filtresi (Fighter, Barbarian, Wizard vb.)")
):
    feats = service.get_feats(system, query=query, category=category, class_name=class_name)
    return [EntityResponseSchema.model_validate(f, from_attributes=True) for f in feats]

@router.get(
    "/{system}/equipment",
    response_model=List[EntityResponseSchema],
    summary="Ekipman & Eşya Arama",
    description="Silah, zırh, kalkan ve maceracı eşyalarını arar."
)
def search_equipment(
    system: str,
    query: str = Query("", description="Eşya adı filtresi"),
    category: str = Query("", description="Kategori filtresi (weapons, armor, gear, potions vb.)")
):
    items = service.get_equipment(system, query=query, category=category)
    return [EntityResponseSchema.model_validate(i, from_attributes=True) for i in items]


@router.get(
    "/{system}/spells",
    response_model=List[EntityResponseSchema],
    summary="Büyü Kütüphanesi Arama",
    description="Büyü seviyesi (0-9), büyücü sınıfı ve büyü okuna göre filtreleme imkanı sunar."
)
def search_spells(
    system: str,
    query: str = Query("", description="Büyü ismi arama filtresi"),
    level: Optional[int] = Query(None, description="Büyü seviyesi filtresi (0-9)"),
    caster_class: str = Query("", description="Büyücü sınıfı (Wizard, Cleric, Sorcerer vb.)"),
    school: str = Query("", description="Büyü okulu (Evocation, Abjuration vb.)")
):
    spells = service.get_spells(system, query=query, level=level, caster_class=caster_class, school=school)
    return [EntityResponseSchema.model_validate(s, from_attributes=True) for s in spells]

@router.get(
    "/{system}/powers",
    response_model=List[EntityResponseSchema],
    summary="Özel Güç Arama",
    description="Sistemdeki özel güçleri listeler."
)
def search_powers(system: str, query: str = Query("", description="Güç ismi filtresi")):
    powers = service.get_powers(system, query)
    return [EntityResponseSchema.model_validate(p, from_attributes=True) for p in powers]

@router.get(
    "/{system}/traits",
    response_model=List[EntityResponseSchema],
    summary="Karakter Trait (Karakter Özelliği) Arama",
    description="PF1e karakter trait'lerini kategori ve isim filtresiyle arar."
)
def search_traits(system: str, query: str = Query("", description="Trait ismi filtresi"), category: str = Query("", description="Trait kategorisi (Combat, Social, Magic vb.)")):
    traits = service.get_traits(system, query, category)
    return [EntityResponseSchema.model_validate(t, from_attributes=True) for t in traits]

@router.get(
    "/{system}/class-features",
    response_model=List[EntityResponseSchema],
    summary="Sınıf Yetenekleri ve Özellikleri Arama",
    description="Sınıfa özel yetenekleri (Rage Powers, Rogue Talents, Hexes, Discoveries vb.) arar."
)
def search_class_features(
    system: str,
    class_name: str = Query("", description="Sınıf adı (Barbarian, Rogue, Witch, Alchemist vb.)"),
    query: str = Query("", description="Yetenek ismi filtresi")
):
    features = service.get_class_features(system, class_name=class_name, query=query)
    return [EntityResponseSchema.model_validate(f, from_attributes=True) for f in features]

@router.get(
    "/{system}/mechanics",
    response_model=List[EntityResponseSchema],
    summary="Genel Kurallar ve Savaş Mekanikleri Arama",
    description="Savaş eylemleri, durum şartları (Conditions) ve genel sistem kurallarını listeler."
)
def search_mechanics(
    system: str,
    query: str = Query("", description="Kural veya durum adı filtresi"),
    category: str = Query("", description="Kural kategorisi (Condition, Combat, Environment vb.)")
):
    mechanics = service.get_mechanics(system, query, category)
    return [EntityResponseSchema.model_validate(m, from_attributes=True) for m in mechanics]

@router.get(
    "/{system}/search",
    response_model=List[EntityResponseSchema],
    summary="Genel Kural Varlığı Arama",
    description="Kategori gözetmeksizin herhangi bir kural kütüphanesi varlığını arar."
)
def search_all_entities(
    system: str,
    category: str = Query(..., description="Varlık kategorisi (race, class, feat, spell, item)"),
    query: str = Query("", description="Arama metni")
):
    entities = service.search_entities(system, category, query)
    return [EntityResponseSchema.model_validate(e, from_attributes=True) for e in entities]



class PrereqCheckRequest(BaseModel):
    character: dict
    entity_data: dict
    is_overridden: bool = False

@router.post(
    "/validate-prerequisites",
    summary="Ön Koşul Denetimi ve Soft-Validation",
    description="Bir feat, büyü veya seçimin ön koşullarını GM esneklik seçeneği (`is_overridden`) ile denetler."
)
def validate_prerequisites(payload: PrereqCheckRequest):
    from rules.calculators import PF1e_Calculator
    calc = PF1e_Calculator()
    return calc.check_prerequisites(payload.character, payload.entity_data, payload.is_overridden)
