"""
D&D 5e Condition (Durum Efekti) Sistemi
Karakter uzerindeki aktif durumlari takip etme
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


# ============================================================================
# D&D 5e Standart Condition'lar
# ============================================================================

CONDITIONS: Dict[str, Dict[str, Any]] = {
    "Blinded": {
        "name": "Blinded (Kör)",
        "icon": "🙈",
        "description": "Kör bir yaratık göremez ve görmeye dayalı yetenek kontrollerinde otomatik başarısız olur.",
        "effects": [
            "Görmeye dayalı yetenek kontrollerinde otomatik başarısızlık",
            "Saldırı zarlarında dezavantaj",
            "Yaratığa yapılan saldırı zarlarında avantaj"
        ],
        "category": "sensory"
    },
    "Charmed": {
        "name": "Charmed (Büyülenmiş)",
        "icon": "💕",
        "description": "Büyülenen yaratık büyüleyene saldıramaz veya zararlı büyü/yetenek kullanamaz.",
        "effects": [
            "Büyüleyene saldıramaz veya zararlı yetenek kullanamaz",
            "Büyüleyenin sosyal etkileşim kontrollerinde avantajı var"
        ],
        "category": "mental"
    },
    "Deafened": {
        "name": "Deafened (Sağır)",
        "icon": "🔇",
        "description": "Sağır bir yaratık duyamaz ve duymaya dayalı yetenek kontrollerinde otomatik başarısız olur.",
        "effects": [
            "Duymaya dayalı yetenek kontrollerinde otomatik başarısızlık"
        ],
        "category": "sensory"
    },
    "Exhaustion": {
        "name": "Exhaustion (Bitkinlik)",
        "icon": "😫",
        "description": "Bitkinliğin 6 seviyesi vardır. Her seviye kümülatiftir.",
        "effects": [
            "Seviye 1: Yetenek kontrollerinde dezavantaj",
            "Seviye 2: Hız yarıya düşer",
            "Seviye 3: Saldırı ve saving throw'larda dezavantaj",
            "Seviye 4: HP maksimumu yarıya düşer",
            "Seviye 5: Hız 0 olur",
            "Seviye 6: Ölüm"
        ],
        "has_levels": True,
        "max_level": 6,
        "category": "physical"
    },
    "Frightened": {
        "name": "Frightened (Korkmuş)",
        "icon": "😨",
        "description": "Korkmuş yaratık, korkunun kaynağını görebildiği sürece dezavantaja sahiptir.",
        "effects": [
            "Korkunun kaynağı görüş alanındayken yetenek ve saldırı zarlarında dezavantaj",
            "Korkunun kaynağına kendi iradesiyle yaklaşamaz"
        ],
        "category": "mental"
    },
    "Grappled": {
        "name": "Grappled (Tutulmuş)",
        "icon": "🤼",
        "description": "Tutulmuş yaratığın hızı 0 olur ve hız bonusu alamaz.",
        "effects": [
            "Hız 0 olur",
            "Tutan yaratık incapacitated olursa veya menzil dışına çıkarılırsa sona erer"
        ],
        "category": "physical"
    },
    "Incapacitated": {
        "name": "Incapacitated (Etkisiz)",
        "icon": "💤",
        "description": "Etkisiz bir yaratık aksiyon veya reaksiyon alamaz.",
        "effects": [
            "Aksiyon veya reaksiyon alamaz"
        ],
        "category": "physical"
    },
    "Invisible": {
        "name": "Invisible (Görünmez)",
        "icon": "👻",
        "description": "Görünmez yaratık, büyü veya özel duyu olmadan görülemez.",
        "effects": [
            "Gizlenme için heavily obscured sayılır",
            "Ses veya izler ile yeri tahmin edilebilir",
            "Saldırı zarlarında avantaj",
            "Yaratığa yapılan saldırı zarlarında dezavantaj"
        ],
        "category": "sensory"
    },
    "Paralyzed": {
        "name": "Paralyzed (Felçli)",
        "icon": "⚡",
        "description": "Felçli bir yaratık hareket edemez ve konuşamaz.",
        "effects": [
            "Incapacitated (aksiyon/reaksiyon yok)",
            "Hareket edemez, konuşamaz",
            "STR ve DEX saving throw'larında otomatik başarısızlık",
            "Yaratığa yapılan saldırı zarlarında avantaj",
            "5 feet içinden gelen saldırılar otomatik critical hit"
        ],
        "category": "physical"
    },
    "Petrified": {
        "name": "Petrified (Taşlaşmış)",
        "icon": "🗿",
        "description": "Taşlaşmış yaratık ve taşıdıkları taşa dönüşür.",
        "effects": [
            "Ağırlık 10 katına çıkar",
            "Yaşlanma durur",
            "Incapacitated, hareket/konuşma yok",
            "Çevresinden habersiz",
            "Saldırı zarlarında avantaj (yaratığa karşı)",
            "STR ve DEX saving throw otomatik başarısızlık",
            "Zehir ve hastalığa bağışıklık (mevcut olanlar askıya alınır)",
            "Tüm hasarlara dayanıklılık"
        ],
        "category": "physical"
    },
    "Poisoned": {
        "name": "Poisoned (Zehirlenmiş)",
        "icon": "🤢",
        "description": "Zehirlenmiş yaratığın saldırı ve yetenek kontrollerinde dezavantajı vardır.",
        "effects": [
            "Saldırı zarlarında dezavantaj",
            "Yetenek kontrollerinde dezavantaj"
        ],
        "category": "physical"
    },
    "Prone": {
        "name": "Prone (Yere Serilmiş)",
        "icon": "🛌",
        "description": "Yere serilmiş yaratık sadece sürünerek hareket edebilir.",
        "effects": [
            "Sadece sürünerek hareket (her 1 feet = 2 feet hareket harcama)",
            "Kalkmak için hız'ın yarısını harcamalı",
            "Saldırı zarlarında dezavantaj",
            "5 feet içinden saldırılarda avantaj (saldırgana)",
            "5 feet dışından saldırılarda dezavantaj (saldırgana)"
        ],
        "category": "physical"
    },
    "Restrained": {
        "name": "Restrained (Kısıtlanmış)",
        "icon": "⛓️",
        "description": "Kısıtlanmış yaratığın hızı 0 olur.",
        "effects": [
            "Hız 0 olur, hız bonusu alamaz",
            "Saldırı zarlarında dezavantaj",
            "Yaratığa yapılan saldırı zarlarında avantaj",
            "DEX saving throw'larında dezavantaj"
        ],
        "category": "physical"
    },
    "Stunned": {
        "name": "Stunned (Sersemletilmiş)",
        "icon": "💫",
        "description": "Sersemletilmiş yaratık incapacitated ve tepkisizdir.",
        "effects": [
            "Incapacitated (aksiyon/reaksiyon yok)",
            "Konuşamaz, kekeleme dışında",
            "STR ve DEX saving throw'larında otomatik başarısızlık",
            "Yaratığa yapılan saldırı zarlarında avantaj"
        ],
        "category": "physical"
    },
    "Unconscious": {
        "name": "Unconscious (Bayılmış)",
        "icon": "😵",
        "description": "Bayılmış yaratık incapacitated, hareket edemez ve çevresinden habersizdir.",
        "effects": [
            "Incapacitated, hareket/konuşma yok",
            "Taşıdıklarını düşürür, yere serilir",
            "STR ve DEX saving throw otomatik başarısızlık",
            "Yaratığa yapılan saldırı zarlarında avantaj",
            "5 feet içinden gelen saldırılar otomatik critical hit"
        ],
        "category": "physical"
    },
    # --- Ekstra Yaygın Durumlar ---
    "Concentrating": {
        "name": "Concentrating (Konsantrasyon)",
        "icon": "🎯",
        "description": "Bir konsantrasyon büyüsünü sürdürüyor. Hasar alınca CON saving throw gerekir.",
        "effects": [
            "Yeni konsantrasyon büyüsü yapılamaz",
            "Hasar alınca CON saving throw (DC 10 veya hasar/2, hangisi büyükse)",
            "Incapacitated veya öldürülürse konsantrasyon bozulur"
        ],
        "category": "magical"
    },
    "Blessed": {
        "name": "Blessed (Kutsanmış)",
        "icon": "✨",
        "description": "Bless büyüsü etkisinde. Saldırı ve saving throw'lara +1d4 bonus.",
        "effects": [
            "Saldırı zarlarına +1d4",
            "Saving throw'lara +1d4"
        ],
        "category": "magical"
    },
    "Hasted": {
        "name": "Hasted (Hızlanmış)",
        "icon": "⚡",
        "description": "Haste büyüsü etkisinde. Hız iki katı, AC +2, ekstra aksiyon.",
        "effects": [
            "Hız iki katına çıkar",
            "AC +2",
            "DEX saving throw'larında avantaj",
            "Her tur bir ekstra aksiyon (Attack, Dash, Disengage, Hide, Use Object)"
        ],
        "category": "magical"
    },
    "Raging": {
        "name": "Raging (Öfkeli)",
        "icon": "🔥",
        "description": "Barbarian Rage aktif. Ekstra hasar, dayanıklılık, avantaj.",
        "effects": [
            "Melee saldırılara bonus hasar (Rage Damage)",
            "Bludgeoning/piercing/slashing hasara dayanıklılık",
            "STR kontrollerinde ve saving throw'larında avantaj",
            "Büyü yapamaz veya konsantre olamaz"
        ],
        "category": "class_feature"
    },
}


def get_all_conditions() -> Dict[str, Dict[str, Any]]:
    """Tum condition'lari dondur"""
    return CONDITIONS


def get_condition(name: str) -> Optional[Dict[str, Any]]:
    """Belirli bir condition'i dondur"""
    return CONDITIONS.get(name)


def get_conditions_by_category(category: str) -> List[str]:
    """Kategoriye gore condition listesi"""
    return [name for name, data in CONDITIONS.items() if data.get("category") == category]


def add_condition_to_character(character: Dict[str, Any], condition_name: str, 
                                duration: str = "", notes: str = "", level: int = 1) -> Dict[str, Any]:
    """Karaktere condition ekle"""
    active = character.setdefault("active_conditions", [])

    # Ayni condition zaten varsa ekleme
    for c in active:
        if c.get("name") == condition_name:
            # Exhaustion icin seviye guncelle
            if condition_name == "Exhaustion":
                c["level"] = min(level, 6)
            return character

    entry = {
        "name": condition_name,
        "added": datetime.now().isoformat(),
        "duration": duration,
        "notes": notes,
    }

    # Exhaustion seviye bilgisi
    cond_data = CONDITIONS.get(condition_name, {})
    if cond_data.get("has_levels"):
        entry["level"] = min(level, cond_data.get("max_level", 6))

    active.append(entry)
    return character


def remove_condition_from_character(character: Dict[str, Any], condition_name: str) -> Dict[str, Any]:
    """Karakterden condition kaldir"""
    active = character.get("active_conditions", [])
    character["active_conditions"] = [c for c in active if c.get("name") != condition_name]
    return character


def get_active_conditions(character: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Karakterin aktif condition'larini dondur (condition detayi ile)"""
    active = character.get("active_conditions", [])
    result = []
    for entry in active:
        name = entry.get("name", "")
        cond_data = CONDITIONS.get(name, {})
        result.append({
            **entry,
            "icon": cond_data.get("icon", "❓"),
            "display_name": cond_data.get("name", name),
            "effects": cond_data.get("effects", []),
            "description": cond_data.get("description", ""),
            "category": cond_data.get("category", ""),
        })
    return result


def get_condition_summary(character: Dict[str, Any]) -> str:
    """Karakter icin condition ozet metni"""
    active = get_active_conditions(character)
    if not active:
        return "Aktif durum efekti yok."

    parts = []
    for c in active:
        icon = c.get("icon", "")
        name = c.get("display_name", c.get("name", ""))
        level = c.get("level")
        if level:
            parts.append(f"{icon} {name} (Lv{level})")
        else:
            parts.append(f"{icon} {name}")
    return " | ".join(parts)
