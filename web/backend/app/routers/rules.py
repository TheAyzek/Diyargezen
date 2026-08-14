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
from typing import List, Optional, Dict, Any
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
    class_name: str = Query("", description="Kullanıcı sınıfı filtresi (Fighter, Barbarian, Wizard vb.)"),
    limit: Optional[int] = Query(None, description="Döndürülecek maksimum nesne sayısı")
):
    feats = service.get_feats(system, query=query, category=category, class_name=class_name, limit=limit)
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
    category: str = Query("", description="Kategori filtresi (weapons, armor, gear, potions vb.)"),
    limit: Optional[int] = Query(None, description="Döndürülecek maksimum nesne sayısı")
):
    items = service.get_equipment(system, query=query, category=category, limit=limit)
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
    level: Optional[str] = Query(None, description="Büyü seviyesi filtresi (0-9)"),
    caster_class: str = Query("", description="Büyücü sınıfı (Wizard, Cleric, Sorcerer vb.)"),
    school: str = Query("", description="Büyü okulu (Evocation, Abjuration vb.)"),
    limit: Optional[int] = Query(None, description="Döndürülecek maksimum nesne sayısı")
):
    parsed_level: Optional[int] = None
    if level is not None and str(level).strip() != "":
        try:
            parsed_level = int(level)
        except ValueError:
            parsed_level = None

    spells = service.get_spells(system, query=query, level=parsed_level, caster_class=caster_class, school=school, limit=limit)
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
def search_traits(system: str, query: str = Query("", description="Trait ismi filtresi"), category: str = Query("", description="Trait kategorisi (Combat, Social, Magic vb.)"), limit: Optional[int] = Query(None, description="Döndürülecek maksimum nesne sayısı")):
    traits = service.get_traits(system, query, category, limit=limit)
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
    query: str = Query("", description="Yetenek ismi filtresi"),
    limit: Optional[int] = Query(None, description="Döndürülecek maksimum nesne sayısı")
):
    features = service.get_class_features(system, class_name=class_name, query=query, limit=limit)
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


class CharacterDiffRequest(BaseModel):
    character_a: dict
    character_b: dict

@router.post(
    "/character-diff",
    summary="Karakter Versiyon ve Snapshot Karşılaştırma",
    description="İki karakter veya snapshot arasındaki tüm stat, savaş, yetenek, feat ve servet farklarını hesaplar."
)
def get_character_diff(payload: CharacterDiffRequest):
    from rules.character_diff import compute_character_diff
    return compute_character_diff(payload.character_a, payload.character_b)


@router.get(
    "/conditions-buffs",
    summary="Resmi PF1e Koşulları ve Durum Buff'ları",
    description="Karakter üzerinde anlık uygulanabilen 30+ resmi koşul ve büyü buff listesini döner."
)
def list_conditions_and_buffs():
    from rules.conditions_engine import get_available_conditions_and_buffs
    return get_available_conditions_and_buffs()


class SpellbookScribingRequest(BaseModel):
    spells: list
    book_size: int = 100

@router.post(
    "/spellbook-scribing",
    summary="Büyü Kitabı Sayfa & Mürekkep Maliyet Hesabı",
    description="Büyü listesinin 100 sayfalık büyü defterindeki doluluğunu ve mürekkep altın maliyetini hesaplar."
)
def get_spellbook_scribing(payload: SpellbookScribingRequest):
    from rules.spellbook_scribing import calculate_spellbook_pages_and_cost
    return calculate_spellbook_pages_and_cost(payload.spells, payload.book_size)


class ScrollCraftingRequest(BaseModel):
    spell_level: int
    caster_level: Optional[int] = None

@router.post(
    "/scroll-crafting",
    summary="Tomar Üretim Maliyeti (Scribe Scroll)",
    description="Bir büyünün tomar üretim maliyetini ve pazar fiyatını hesaplar."
)
def get_scroll_crafting(payload: ScrollCraftingRequest):
    from rules.spellbook_scribing import calculate_scroll_crafting_cost
    return calculate_scroll_crafting_cost(payload.spell_level, payload.caster_level)


class PointBuyEvalRequest(BaseModel):
    ability_scores: Dict[str, Any]

@router.post(
    "/point-buy-eval",
    summary="Point Buy Eşdeğeri & Stat Analizi",
    description="6 temel yetenek skorunun toplam Point Buy puanını ve fantezi seviyesini (Low, Standard, High, Epic) hesaplar."
)
def evaluate_point_buy(payload: PointBuyEvalRequest):
    from rules.dice_analytics import calculate_point_buy_equivalent
    return calculate_point_buy_equivalent(payload.ability_scores)


@router.get(
    "/dice-arrays",
    summary="Resmi ve Dengeli Stat Şablonları & Zar Dağılımları",
    description="PF1e hazır stat dizilim şablonlarını ve 4d6/3d6/2d6+6 istatistiklerini döner."
)
def get_dice_arrays_and_stats():
    from rules.dice_analytics import get_stat_array_templates, get_dice_generation_stats
    return {
        "templates": get_stat_array_templates(),
        "dice_stats": get_dice_generation_stats()
    }


@router.get(
    "/favored-class-options",
    summary="Favored Class Bonus Seçenekleri (HP, Skill, Irksal)",
    description="Belirtilen ırk ve sınıf için resmi Core ve APG/ARG Favored Class bonus seçeneklerini döner."
)
def get_fcb_options(race: str = Query("Human"), char_class: str = Query("Fighter")):
    from rules.favored_class_engine import get_racial_fcb_options
    return get_racial_fcb_options(race, char_class)


class EvaluateFCBRequest(BaseModel):
    character: Dict[str, Any]

@router.post(
    "/evaluate-fcb",
    summary="Karakter Favored Class Bonus Dağılımını Değerlendir",
    description="Karakterin FCB tercihlerini, toplam kazanılan HP/Skill ve irksal bonuslarını hesaplar."
)
def evaluate_fcb(payload: EvaluateFCBRequest):
    from rules.favored_class_engine import evaluate_favored_class_bonuses
    return evaluate_favored_class_bonuses(payload.character)


@router.get(
    "/languages-catalog",
    summary="PF1e Resmi Diller ve Alfabeler Kataloğu",
    description="PF1e tüm resmi diller, alfabeler ve ırksal başlangıç/bonus dil listesini döner."
)
def get_languages():
    from rules.languages_engine import get_languages_catalog
    return get_languages_catalog()


class EvaluateLanguagesRequest(BaseModel):
    character: Dict[str, Any]

@router.post(
    "/evaluate-languages",
    summary="Karakter Dillerini ve Dil Kotasını Değerlendir",
    description="Karakterin başlangıç, bonus ve Linguistics yeteneği dillerini ve kotasını doğrular."
)
def evaluate_languages(payload: EvaluateLanguagesRequest):
    from rules.languages_engine import evaluate_character_languages
    return evaluate_character_languages(payload.character)


@router.get(
    "/age-tables",
    summary="PF1e Yaş, Boy ve Kilo Tabloları",
    description="PF1e resmi ırk başlangıç yaşları, yaşlanma sınırları ve boy/kilo zar formüllerini döner."
)
def get_age_and_physical_tables():
    from rules.age_height_weight import get_physical_rules_catalog
    return get_physical_rules_catalog()


class EvaluateAgeRequest(BaseModel):
    race: str
    age: Optional[int] = None

@router.post(
    "/evaluate-age",
    summary="Karakter Yaş Kategorisi & Stat Modifikatörleri",
    description="Karakterin yaşına göre yaşlanma kategorisini (Orta Yaş, Yaşlı, Kadim) ve net stat etkilerini hesaplar."
)
def evaluate_age(payload: EvaluateAgeRequest):
    from rules.age_height_weight import get_age_category_and_modifiers
    return get_age_category_and_modifiers(payload.race, payload.age)


class GeneratePhysicalRequest(BaseModel):
    race: str
    char_class: str = "Fighter"
    gender: str = "male"

@router.post(
    "/generate-physical",
    summary="Rastgele Başlangıç Yaşı, Boy ve Kilo Üretici",
    description="Karakterin ırk, sınıf ve cinsiyetine göre resmi zar formülleriyle rastgele yaş, boy ve kilo üretir."
)
def generate_physical(payload: GeneratePhysicalRequest):
    from rules.age_height_weight import generate_random_starting_age, generate_random_height_weight
    age_res = generate_random_starting_age(payload.race, payload.char_class)
    hw_res = generate_random_height_weight(payload.race, payload.gender)
    return {
        "starting_age": age_res,
        "height_weight": hw_res
    }


class CharacterCardRequest(BaseModel):
    character: Dict[str, Any]

@router.post(
    "/character-card",
    summary="Karakter Vitrin Kartı Verisi",
    description="Karakterin vitrin kartı ve sosyal medya paylaşımı için özet metriklerini döner."
)
def get_character_card(payload: CharacterCardRequest):
    from rules.character_card import generate_character_card_data
    return generate_character_card_data(payload.character)


@router.get(
    "/metamagic-catalog",
    summary="PF1e Resmi Metamagic Featleri Kataloğu",
    description="PF1e tüm resmi Metamagic featlerini ve slot seviye artışlarını döner."
)
def get_metamagics():
    from rules.metamagic_engine import get_metamagic_catalog
    return get_metamagic_catalog()


class EvaluateMetamagicRequest(BaseModel):
    spell: Dict[str, Any]
    applied_metamagic: List[Any]
    caster_type: str = "prepared"
    casting_mod: int = 0

@router.post(
    "/evaluate-metamagic",
    summary="Metabüyü Uygulanmış Büyü Simülasyonu",
    description="Büyüye uygulanan metamagic featlerine göre slot gereksinimi, döküm süresi ve DC'yi hesaplar."
)
def evaluate_metamagic(payload: EvaluateMetamagicRequest):
    from rules.metamagic_engine import calculate_metamagic_spell
    return calculate_metamagic_spell(
        payload.spell,
        payload.applied_metamagic,
        payload.caster_type,
        payload.casting_mod
    )


@router.get(
    "/crafting-catalog",
    summary="PF1e Eşya ve Simya Üretim Kataloğu",
    description="PF1e eşya üretim featleri, formülleri ve Alchemist mutajen tiplerini döner."
)
def get_crafting():
    from rules.alchemy_crafting import get_crafting_catalog
    return get_crafting_catalog()


class CalculatePotionRequest(BaseModel):
    spell_name: str = "Cure Light Wounds"
    spell_level: int = 1
    caster_level: int = 1

@router.post(
    "/calculate-potion",
    summary="İksir Üretim Maliyeti ve DC Hesapla",
    description="İksir için piyasa fiyatı, ham madde maliyeti, gün/saat süresi ve Spellcraft DC'sini hesaplar."
)
def calculate_potion(payload: CalculatePotionRequest):
    from rules.alchemy_crafting import calculate_potion_crafting
    return calculate_potion_crafting(payload.spell_name, payload.spell_level, payload.caster_level)


class CalculateItemCraftingRequest(BaseModel):
    item_name: str
    item_type: str = "wondrous"
    market_price_gp: int = 1000
    item_cl: int = 1
    missing_prereqs_count: int = 0

@router.post(
    "/calculate-item-crafting",
    summary="Büyülü Eşya Üretim Maliyeti ve DC Hesapla",
    description="Harika eşya, silah, zırh veya asa üretimi için ham madde maliyeti, gün ve DC hesaplar."
)
def calculate_item_crafting(payload: CalculateItemCraftingRequest):
    from rules.alchemy_crafting import calculate_magic_item_crafting
    return calculate_magic_item_crafting(
        payload.item_name,
        payload.item_type,
        payload.market_price_gp,
        payload.item_cl,
        payload.missing_prereqs_count
    )


class EvaluateMutagenRequest(BaseModel):
    mutagen_type: str = "strength"
    alchemist_level: int = 1

@router.post(
    "/evaluate-mutagen",
    summary="Alchemist Mutajen Etkilerini Hesapla",
    description="Mutajenin kazandırdığı fiziksel stat artışı, doğal zırh bonusu, zihinsel ceza ve süresini hesaplar."
)
def evaluate_mutagen(payload: EvaluateMutagenRequest):
    from rules.alchemy_crafting import calculate_mutagen_effects
    return calculate_mutagen_effects(payload.mutagen_type, payload.alchemist_level)


@router.get(
    "/background-catalog",
    summary="PF1e Ultimate Campaign Arka Plan Tabloları & Story Feat Kataloğu",
    description="Vatan, aile, çocukluk, motivasyon tabloları ve hikaye featlerini döner."
)
def get_background_catalog():
    from rules.background_generator import get_background_tables_catalog
    return get_background_tables_catalog()


class GenerateBackgroundRequest(BaseModel):
    race: str = "Human"
    char_class: str = "Fighter"
    alignment: str = "TN"

@router.post(
    "/generate-background",
    summary="Rastgele Karakter Arka Plan Hikayesi Üretici",
    description="Ultimate Campaign tablolarından zengin biyografi, vatan, aile ve hikaye featleri üretir."
)
def generate_background(payload: GenerateBackgroundRequest):
    from rules.background_generator import generate_random_background
    return generate_random_background(payload.race, payload.char_class, payload.alignment)


class CompileBackgroundRequest(BaseModel):
    background_data: Dict[str, Any]

@router.post(
    "/compile-background",
    summary="Arka Plan Bölümlerini Hikaye Metnine Derle",
    description="Vatan, aile, çocukluk ve motivasyon verilerinden yapılandırılmış hikaye metni oluşturur."
)
def compile_bg_text(payload: CompileBackgroundRequest):
    from rules.background_generator import compile_background_narrative
    narrative = compile_background_narrative(payload.background_data)
    return {"narrative_biography": narrative}


@router.get(
    "/progression-matrix",
    summary="1-20 Seviye Atlama İlerleme Matrisi",
    description="Karakter sınıfı ve ırkına göre 1'den 20'ye kadar tüm BAB, save, feat ve yetenek açılımlarını döner."
)
def get_progression_matrix(
    char_class: str = Query("Fighter", description="Karakter sınıfı"),
    race: str = Query("Human", description="Karakter ırkı"),
    archetype: str = Query("", description="Karakter arketipi")
):
    from rules.progression_planner import generate_progression_matrix
    return generate_progression_matrix(char_class, race, archetype)


@router.get(
    "/weapon-abilities-catalog",
    summary="PF1e Silah Özel Nitelikleri Kataloğu",
    description="Flaming, Frost, Shock, Keen, Holy, Speed gibi tüm resmi Paizo silah niteliklerini döner."
)
def get_weapon_abilities():
    from rules.weapon_special_abilities import get_weapon_abilities_catalog
    return get_weapon_abilities_catalog()


class EvaluateWeaponAbilitiesRequest(BaseModel):
    weapon: Dict[str, Any]
    base_enhancement: int = 1
    applied_abilities: List[str] = []
    is_bane_active: bool = False

@router.post(
    "/evaluate-weapon-abilities",
    summary="Büyülü Silah Nitelikleri ve Hasar Simülasyonu",
    description="Silahın elementel hasar zarlarını, kritik aralığını, tam tur ekstra saldırılarını ve GP fiyatını hesaplar."
)
def evaluate_weapon_abilities(payload: EvaluateWeaponAbilitiesRequest):
    from rules.weapon_special_abilities import calculate_weapon_magical_properties
    return calculate_weapon_magical_properties(
        payload.weapon,
        payload.base_enhancement,
        payload.applied_abilities,
        payload.is_bane_active
    )


@router.get(
    "/armor-abilities-catalog",
    summary="PF1e Zırh ve Kalkan Özel Nitelikleri Kataloğu",
    description="Fortification, Shadow, Slick, Spell Resistance, Animated gibi tüm resmi Paizo zırh ve kalkan niteliklerini döner."
)
def get_armor_abilities():
    from rules.armor_special_abilities import get_armor_abilities_catalog
    return get_armor_abilities_catalog()


class EvaluateArmorAbilitiesRequest(BaseModel):
    armor: Dict[str, Any]
    base_enhancement: int = 1
    applied_abilities: List[str] = []

@router.post(
    "/evaluate-armor-abilities",
    summary="Büyülü Zırh ve Kalkan Savunma Simülasyonu",
    description="Zırh veya kalkanın toplam AC bonusu, SR, kritik engelleme şansı, yetenek bonusları ve GP piyasa fiyatını hesaplar."
)
def evaluate_armor_abilities(payload: EvaluateArmorAbilitiesRequest):
    from rules.armor_special_abilities import calculate_armor_magical_properties
    return calculate_armor_magical_properties(
        payload.armor,
        payload.base_enhancement,
        payload.applied_abilities
    )


class GenerateStatblockRequest(BaseModel):
    character: Dict[str, Any]
    recalced_data: Optional[Dict[str, Any]] = None

@router.post(
    "/generate-statblock",
    summary="Resmi Paizo Statblock Üretici",
    description="Karakter verilerini Paizo resmi standartlarında Plain Text ve Markdown statblock formatına dönüştürür."
)
def generate_statblock(payload: GenerateStatblockRequest):
    from rules.statblock_engine import generate_paizo_statblock
    return generate_paizo_statblock(payload.character, payload.recalced_data)


class ValidateJsonRequest(BaseModel):
    json_data: Dict[str, Any]

@router.post(
    "/validate-character-json",
    summary="Karakter JSON Dosyası Doğrulama",
    description="İçe aktarılan karakter JSON dosyasının veri şemasını ve geçerliliğini denetler."
)
def validate_char_json(payload: ValidateJsonRequest):
    from rules.statblock_engine import validate_imported_character_json
    return validate_imported_character_json(payload.json_data)


class SplitPartyLootRequest(BaseModel):
    coins: Dict[str, Any] = {"pp": 0, "gp": 0, "sp": 0, "cp": 0}
    gems_art: List[Dict[str, Any]] = []
    items: List[Dict[str, Any]] = []
    party_members: List[str] = ["Oyuncu 1", "Oyuncu 2", "Oyuncu 3", "Oyuncu 4"]
    include_party_fund: bool = True

@router.post(
    "/split-party-loot",
    summary="Parti Ganimeti ve Hazine Paylaştırıcı",
    description="Ortak sikkeleri, mücevherleri ve eşyaları parti üyelerine ve ortak fona eşit paylaştırır."
)
def split_party_loot(payload: SplitPartyLootRequest):
    from rules.party_loot_engine import calculate_party_loot_split
    return calculate_party_loot_split(
        payload.coins,
        payload.gems_art,
        payload.items,
        payload.party_members,
        payload.include_party_fund
    )


class EvaluateTwfRequest(BaseModel):
    bab: int = 1
    str_mod: int = 0
    dex_mod: int = 0
    primary_weapon: Optional[Dict[str, Any]] = None
    offhand_weapon: Optional[Dict[str, Any]] = None
    feats: List[Any] = []
    is_weapon_finesse: bool = False

@router.post(
    "/evaluate-twf",
    summary="Çift Silahla Dövüş (TWF) Saldırı Dizilimi ve Hasar Hesaplayıcı",
    description="Birincil ve ikincil silah, BAB, statlar ve hünerlere göre tam tur çift el saldırı dizilimini ve hasarını hesaplar."
)
def evaluate_twf(payload: EvaluateTwfRequest):
    from rules.two_weapon_fighting import calculate_twf_attack_profile
    return calculate_twf_attack_profile(
        payload.bab,
        payload.str_mod,
        payload.dex_mod,
        payload.primary_weapon,
        payload.offhand_weapon,
        payload.feats,
        payload.is_weapon_finesse
    )


@router.get(
    "/class-alignment-rules",
    summary="PF1e Sınıf ve Tanrı Hizalanış Kural Kataloğu",
    description="Paladin, Monk, Barbarian, Druid ve Cleric için resmi hizalanış kurallarını döner."
)
def get_alignment_rules():
    from rules.alignment_restrictions import get_all_alignment_rules
    return get_all_alignment_rules()


class ValidateAlignmentRequest(BaseModel):
    char_class: str = "Paladin"
    alignment: str = "LG"
    deity_name: str = ""
    archetype: str = ""

@router.post(
    "/validate-alignment",
    summary="Karakter Sınıf ve Hizalanış Uyumluluğu Doğrulayıcı",
    description="Karakter sınıfı, hizalanışı ve tanrısı arasındaki resmi kural uyumunu denetler."
)
def validate_align(payload: ValidateAlignmentRequest):
    from rules.alignment_restrictions import validate_character_alignment
    return validate_character_alignment(
        payload.char_class,
        payload.alignment,
        payload.deity_name,
        payload.archetype
    )


















