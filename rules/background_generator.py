"""
Pathfinder 1st Edition Background & Story Feat Engine
=====================================================
References:
- Paizo Pathfinder RPG: Ultimate Campaign (Chapter 1: Character Background)
- Pathfinder RPG: Ultimate Magic (Story Feats)

Sections:
1. Homeland & Environment
2. Family Background & Social Standing
3. Childhood Major Event
4. Adventuring Motivation & Conflict
5. Paizo Story Feats (Goal & Completion Benefit)
"""

import random
from typing import Dict, Any, List, Optional


HOMELANDS_TABLE: List[Dict[str, Any]] = [
    {"key": "city", "name_tr": "Metropol / Büyük Şehir", "desc": "Büyük krallık başkentlerinin taş sokaklarında, kütüphanelerinde ve kalabalık pazar yerlerinde büyüdü.", "trait_affinity": "Street Smarts / Diplomacy"},
    {"key": "forest", "name_tr": "Kadim Ormanlar", "desc": "Güneş ışığının zor girdiği ulu ağaçların ve fey varlıklarının fısıldadığı derin korularda büyüdü.", "trait_affinity": "Nature / Stealth"},
    {"key": "mountain", "name_tr": "Yüksek Dağlar & Zirveler", "desc": "Karlı geçitlerin, sarp uçurumların ve fırtına rüzgarlarının hüküm sürdüğü doruklarda yetişti.", "trait_affinity": "Climb / Survival"},
    {"key": "coastal", "name_tr": "Sahil & Korsan Koyları", "desc": "Dalgaların sesi, tuzlu rüzgarlar ve deniz ticaret gemilerinin limanlarında macera tutkusuyla büyüdü.", "trait_affinity": "Swim / Profession (Sailor)"},
    {"key": "desert", "name_tr": "Sonsuz Çöller & Vahalar", "desc": "Kavurucu kum tepelerinin ve serapların gizlediği kadim kalıntıların gölgesinde yaşadı.", "trait_affinity": "Endurance / Survival"},
    {"key": "underground", "name_tr": "Yeraltı (Darklands / Caverns)", "desc": "Güneşin hiç doğmadığı derin mağaralarda, parıldayan mantar ormanlarında ve yeraltı şehirlerinde yetişti.", "trait_affinity": "Darkvision / Dungeoneering"},
    {"key": "rural", "name_tr": "Huzurlu Kırsal Köy", "desc": "Verimli tarım arazilerinin ve samimi kasaba topluluklarının sadeliğinde büyüdü.", "trait_affinity": "Handle Animal / Craft"},
    {"key": "planar", "name_tr": "Düzlemsel Sınırlar (Outer Planes)", "desc": "Maddi dünyanın ötesinde, elemental veya tanrısal boyutların enerji fırtınalarına tanıklık etti.", "trait_affinity": "Knowledge (Planes) / Spellcraft"}
]


FAMILY_STANDING_TABLE: List[Dict[str, Any]] = [
    {"key": "noble", "name_tr": "Soylu / Aristokrat Hanedan", "desc": "Gümüş kaşıkla doğdu; saray entrikaları, görgü kuralları ve hanedan sorumluluklarıyla eğitildi."},
    {"key": "merchant", "name_tr": "Zengin Tüccar Loncası", "desc": "Altının ve baharat ticaretinin gücünü erken yaşta öğrendi; kervan yollarında büyüdü."},
    {"key": "artisan", "name_tr": "Usta Zanaatkar Ocağı", "desc": "Demirci ocaklarında, simya atölyelerinde veya marangozhanelerde alın teriyle yetişti."},
    {"key": "serf", "name_tr": "Toprağa Bağlı Köylü", "desc": "Sade ama dirençli bir hayat sürdü; toprağın ve doğanın döngülerini yakından tanıdı."},
    {"key": "military", "name_tr": "Gazi & Askeri Aile", "desc": "Kılıç sesleri ve disiplin marşlarıyla büyüdü; aile mirası savaş onurudur."},
    {"key": "clergy", "name_tr": "Manastır / Tapınak Yetimi", "desc": "Tanrısal dualar, kutsal metinler ve şifahanelerde rahiplerin himayesinde eğitildi."},
    {"key": "underworld", "name_tr": "Sokak Çetesi / Yeraltı Dünyası", "desc": "Karanlık sokaklarda hayatta kalmayı, hırsız loncalarının işaret dilini ve kaçmayı öğrendi."},
    {"key": "nomad", "name_tr": "Göçebe Kabile", "desc": "Hiçbir şehre bağlı kalmadan, mevsimlerin ve yıldızların rehberliğinde özgürce yaşadı."}
]


CHILDHOOD_EVENTS_TABLE: List[Dict[str, Any]] = [
    {"key": "prodigy", "name_tr": "Erken Büyüsel Deha", "desc": "Henüz çocukken açıklanamayan güçler sergiledi ve yerel büyücülerin dikkatini çekti."},
    {"key": "monster_attack", "name_tr": "Canavar Baskınından Kurtulan", "desc": "Köyünü yok eden korkunç bir yaratığın pençesinden mucizevi bir şekilde sağ kurtuldu."},
    {"key": "master_mentorship", "name_tr": "Kadim Ustanın Çırağı", "desc": "Gezgin bir usta savaşçı veya münzevi bilge tarafından gizli öğretilerle yetiştirildi."},
    {"key": "mysterious_relic", "name_tr": "Gizemli Yadigar Bulan", "desc": "Harabelerde kadim bir tılsım veya sembol buldu; kaderi o günden sonra değişti."},
    {"key": "family_exile", "name_tr": "Hanedan İhaneti & Sürgün", "desc": "Ailesi bir komplo sonucu unvanlarını kaybetti ve uzak diyarlara sürgün edildi."},
    {"key": "raised_by_beasts", "name_tr": "Vahşi Doğada Hayatta Kalma", "desc": "Bir süre ormanda kurtlar veya ayılarla birlikte yaşayarak hayatta kalma içgüdüleri kazandı."},
    {"key": "prophetic_dream", "name_tr": "Kehanet Rüyası", "desc": "Rüyasında tanrısal bir işaret veya dünyayı sarsacak bir felaketin vizyonunu gördü."}
]


MOTIVATION_CONFLICT_TABLE: List[Dict[str, Any]] = [
    {"key": "vengeance", "name_tr": "Kişisel İntikam", "desc": "Geçmişte kendisine veya sevdiklerine zarar veren zalim bir düşmanı bulup adaleti sağlamak."},
    {"key": "ancient_knowledge", "name_tr": "Kadim Bilgi & Sır Arayışı", "desc": "Unutulmuş medeniyetlerin büyülerini, tarihin kayıp yapraklarını keşfetmek."},
    {"key": "duty", "name_tr": "Vatan & Onur Görevi", "desc": "Topraklarını, halkını ve inandığı değerleri yaklaşan karanlık tehditlere karşı korumak."},
    {"key": "redemption", "name_tr": "Geçmiş Hatanın Kefareti", "desc": "Gençliğinde yaptığı affedilmez bir hatanın vicdan azabını iyilikle telafi etmek."},
    {"key": "glory_wanderlust", "name_tr": "Gezginlik & Efsanevi Şan", "desc": "Adını ozanların şarkılarına kazımak ve haritaların ötesindeki diyarları görmek."},
    {"key": "divine_calling", "name_tr": "İlahi Misyon & Kader", "desc": "Tanrısının kutsal emrini yerine getirmek ve dünyaya ışığı yaymak."}
]


STORY_FEATS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "arisen": {
        "name": "Arisen (Ölümden Dönen)",
        "prereq": "Ölümcül bir darbeden veya ölümden dönmüş olmak.",
        "benefit": "Ölüm etkilerine ve hastalıklara karşı kurtarma zarlarına +2 bonus.",
        "goal": "Seni neredeyse öldüren varlığı veya türünü tek başına alt etmek.",
        "completion_benefit": "+1 Kalıcı Dayanıklılık (Constitution) puanı ve ölüm eşiği +5 HP artışı."
    },
    "champion": {
        "name": "Champion (Meydan Okuyan Şampiyon)",
        "prereq": "Bir onur yemini veya meydan okuma geçmişi.",
        "benefit": "Tekil meydan okunan düşmanlara karşı saldırı ve hasara +1 bonus.",
        "goal": "Kendi seviyenden en az 3 CR yüksek bir şampiyonu teke tek onurlu düelloda yenmek.",
        "completion_benefit": "Meydan okuma bonusu +2'ye çıkar ve kritik vuruş teyit zarlarına +4 bonus kazanılır."
    },
    "fearless": {
        "name": "Fearless (Korkusuz Yürek)",
        "prereq": "Korkunç bir travmayı atlatmış olmak.",
        "benefit": "Korku (Fear/Shaken) etkilerine karşı kurtarma zarlarına +2 bonus.",
        "goal": "Kendi seviyenden en az 3 CR yüksek korku yayan bir yaratığa karşı tek başına direnmek.",
        "completion_benefit": "Tüm korku ve panik etkilerine karşı tam Bağışıklık (Immunity to Fear)."
    },
    "liberator": {
        "name": "Liberator (Kurtarıcı / Özgürlük Savaşçısı)",
        "prereq": "Tutsaklık geçmişi veya kölelik karşıtı yemin.",
        "benefit": "Kaçış Sanatı (Escape Artist) ve Felç/Dolaşık etkilerine karşı +2 kurtarma bonusu.",
        "goal": "Zulüm altındaki en az 50 masum tutsağı veya köleyi özgürlüğe kavuşturmak.",
        "completion_benefit": "Özgürlük Hareketi (Freedom of Movement) etkisi gibi her türlü büyüsel kısıtlamaya karşı kalıcı +4 bonus."
    },
    "redemption": {
        "name": "Redemption (Kefaret Yolu)",
        "prereq": "Büyük bir günah veya karanlık geçmiş.",
        "benefit": "Zihin etkileyen büyülere ve suçluluk illüzyonlarına karşı +2 kurtarma bonusu.",
        "goal": "Büyük bir düşmanı iyi yola döndürmek veya geçmişte yıktığın bir kutsal mabedi yeniden inşa etmek.",
        "completion_benefit": "+1 Kalıcı Karizma puanı ve günde 1 kez başarısız irade zarını yeniden atma hakkı."
    },
    "true_love": {
        "name": "True Love (Gerçek Aşk)",
        "prereq": "Hayatını adayacak kadar bağlı olduğun bir sevgili/yoldaş.",
        "benefit": "Sevgilini korurken veya onun yanındayken tüm zarlara +1 moral bonusu.",
        "goal": "Sevgilini ölümcül bir tehlikeden veya kaçırılmaktan kurtarmak.",
        "completion_benefit": "Moral bonusu +2'ye çıkar ve günde 1 kez ölümcül bir hasarı 1 HP'de durdurma gücü."
    },
    "untamed_wilds": {
        "name": "Untamed Wilds (Yaban Muhafızı)",
        "prereq": "Vahşi doğada uzun süre izole yaşamış olmak.",
        "benefit": "Hayatta Kalma (Survival) ve Vahşi Empati zarlarına +2 bonus.",
        "goal": "En az 100 milkarelik vahşi bir bölgeyi istilacı canavarlardan temizleyip koruma altına almak.",
        "completion_benefit": "Doğal arazilerde Hız (Speed) +10 ft artar ve arazide asla ayak izi/koku bırakılmaz."
    }
}


def generate_random_background(
    race: str = "Human",
    char_class: str = "Fighter",
    alignment: str = "TN"
) -> Dict[str, Any]:
    """Generates consistent random background sections and story feat suggestions."""
    homeland = random.choice(HOMELANDS_TABLE)
    family = random.choice(FAMILY_STANDING_TABLE)
    childhood = random.choice(CHILDHOOD_EVENTS_TABLE)
    motivation = random.choice(MOTIVATION_CONFLICT_TABLE)

    # Pick 2 recommended story feats
    story_keys = list(STORY_FEATS_REGISTRY.keys())
    selected_story_keys = random.sample(story_keys, 2)
    recommended_story_feats = [
        {"key": k, **STORY_FEATS_REGISTRY[k]} for k in selected_story_keys
    ]

    narrative = (
        f"{race} kökenli bu kahraman, {homeland['name_tr'].lower()} topraklarında dünyaya geldi. "
        f"{family['name_tr']} ortamında yetişerek {family['desc'].lower()} "
        f"Çocukluğunda yaşadığı '{childhood['name_tr']}' dönüm noktası ({childhood['desc']}) kaderini çizdi. "
        f"Şimdi ise '{motivation['name_tr']}' motivasyonuyla ({motivation['desc'].lower()}) yollara düşmüş bir maceracıdır."
    )

    return {
        "race": race,
        "class": char_class,
        "alignment": alignment,
        "homeland": homeland,
        "family": family,
        "childhood_event": childhood,
        "motivation": motivation,
        "recommended_story_feats": recommended_story_feats,
        "narrative_biography": narrative
    }


def compile_background_narrative(background_data: Dict[str, Any]) -> str:
    """Compiles custom background parts into rich prose."""
    h = background_data.get("homeland", {})
    f = background_data.get("family", {})
    c = background_data.get("childhood_event", {})
    m = background_data.get("motivation", {})

    h_name = h.get("name_tr") or h.get("name") or "Bilinmeyen Topraklar"
    f_name = f.get("name_tr") or f.get("name") or "Geleneksel Aile"
    c_name = c.get("name_tr") or c.get("name") or "Önemli Bir Olay"
    m_name = m.get("name_tr") or m.get("name") or "Macera Arayışı"

    return (
        f"Vatanı: {h_name}.\n"
        f"Aile Kökeni: {f_name} - {f.get('desc', '')}\n"
        f"Çocukluk Dönüm Noktası: {c_name} - {c.get('desc', '')}\n"
        f"Maceraya Çıkış Motivasyonu: {m_name} - {m.get('desc', '')}"
    )


def get_background_tables_catalog() -> Dict[str, Any]:
    """Returns complete Ultimate Campaign background catalog."""
    return {
        "homelands": HOMELANDS_TABLE,
        "family_standings": FAMILY_STANDING_TABLE,
        "childhood_events": CHILDHOOD_EVENTS_TABLE,
        "motivations": MOTIVATION_CONFLICT_TABLE,
        "story_feats": STORY_FEATS_REGISTRY
    }
