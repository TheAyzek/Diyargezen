"""
Diyargezen Pathfinder 1st Edition (PF1e) Variant Multiclassing (VMC) Engine

Architecture & Rule Specifications:
----------------------------------
Variant Multiclassing (VMC) is an optional system introduced in Pathfinder Unchained (p. 154).
Under VMC, a character selects a secondary VMC class (e.g. Barbarian, Wizard, Rogue, Fighter, Cleric, etc.)
at 1st level.

Core Mechanics & Restrictions:
1. Feat Deduction: The character forfeits their general feat choices at 3rd, 7th, 11th, 15th, and 19th levels.
2. Granted VMC Features: In exchange for the 5 sacrificed feats, at levels 3, 7, 11, 15, and 19,
   the character automatically gains signature secondary class features.
3. Class Restriction: The secondary VMC class CANNOT be the character's primary class or any of their multiclass levels.
"""

from typing import Dict, Any, List, Optional, Set, Tuple

# VMC Feature Progression Tables per Secondary Class
VMC_CLASS_DATABASE: Dict[str, Dict[int, List[Dict[str, Any]]]] = {
    "barbarian": {
        3: [{"name": "Rage", "description": "Öfke (Rage): Günde 4 + CON Mod tur öfkeye girebilir (+2 Sal/Has, +2 Will, +2 Temp HP).", "target": "hp", "value": 2}],
        7: [{"name": "Uncanny Dodge", "description": "Hazırlıksız Yakalanmama (Uncanny Dodge): Hazırlıksız yakalansanız bile DEX AC bonusunuzu korursunuz."}],
        11: [{"name": "Damage Reduction 1/-", "description": "Hasar Azaltma (DR 1/-): Tüm fiziksel saldırılardan 1 az hasar alırsınız.", "target": "dr", "value": 1}],
        15: [{"name": "Greater Rage", "description": "Büyük Öfke (Greater Rage): Öfke bonusları +3 Saldırı/Hasar ve +3 İrade tasarrufuna yükselir."}],
        19: [{"name": "Indomitable Will", "description": "Yıkılmaz İrade: Öfkedeyken efsun büyülerine karşı +4 bonus."}]
    },
    "bard": {
        3: [{"name": "Bardic Knowledge", "description": "Ozan Bilgisi (Bardic Knowledge): Tüm Bilgi (Knowledge) yetenek kontrollerine karakter seviyesinin yarısı kadar bonus."}],
        7: [{"name": "Bardic Performance", "description": "Ozan Gösterisi (Bardic Performance): Günde karakter seviyesi tur Cesaret Aşılama (Inspire Courage +1) yapabilir."}],
        11: [{"name": "Versatile Performance", "description": "Çok Yönlü Gösteri: Bir Performans yeteneğini ilişkili diğer iki skill yerine kullanabilir."}],
        15: [{"name": "Lore Master", "description": "Bilgi Üstadı: Günde 1 kez Bilgi zarında 20 atılmış sayılabilir."}],
        19: [{"name": "Inspiring Performance (+3)", "description": "İlham Veren Gösteri: Inspire Courage bonusu +3'e yükselir."}]
    },
    "cleric": {
        3: [{"name": "Deity & 1st Domain Power", "description": "Tanrı & 1. Alan Gücü: Seçilen Tanrının 1. Domain güçlerini seviye -2 ile kullanır."}],
        7: [{"name": "Channel Energy (1d6)", "description": "Kutsal Enerji Yayma (Channel Energy): Günde (1 + CHA Mod) kez 1d6 kutsal/lanetli enerji yayar."}],
        11: [{"name": "2nd Domain Power", "description": "2. Alan Gücü (Domain Power): Domain'in 8. seviye güçlerini kazanır."}],
        15: [{"name": "Channel Energy (3d6)", "description": "Kutsal Enerji Artışı: Channel Energy hasarı/iyileştirmesi 3d6'ya yükselir."}],
        19: [{"name": "Domain Master Capstone", "description": "Domain Üstadı: Domain güçleri tam seviyede çalışır."}]
    },
    "druid": {
        3: [{"name": "Wild Empathy & Nature Bond", "description": "Doğa Bağı & Hayvan Empatisi: Karakter seviyesi -3 ile Hayvan Yoldaşı (Companion) veya Domain kazanır."}],
        7: [{"name": "Woodland Stride", "description": "Orman Adımı: Doğal çalı, engel ve zorlu arazide yavaşlamadan hareket eder."}],
        11: [{"name": "Wild Shape (Beast Shape I)", "description": "Vahşi Biçim (Wild Shape): Günde 1 kez Küçük/Orta boy hayvana dönüşebilir."}],
        15: [{"name": "Wild Shape Improvement", "description": "Gelişmiş Vahşi Biçim: Elemental veya Büyük boy hayvana dönüşebilir."}],
        19: [{"name": "Timeless Body", "description": "Zamansız Beden: Yaşlanma cezalarından etkilenmez."}]
    },
    "fighter": {
        3: [{"name": "Bravery +1", "description": "Cesaret +1 (Bravery): Korku etkilerine karşı kurtulma zarlarına +1 bonus.", "target": "saving_throws.Will", "value": 1}],
        7: [{"name": "Armor Training 1", "description": "Zırh Eğitimi 1: Zırh Max Dex bonusunu +1 artırır, Armor Check Penalty'yi 1 azaltır.", "target": "armor_check_penalty", "value": 1}],
        11: [{"name": "Weapon Training 1", "description": "Silah Eğitimi 1: Seçilen silah grubuna +1 Saldırı ve +1 Hasar bonusu verir.", "target": "attack_bonus", "value": 1}],
        15: [{"name": "Armor Training 2", "description": "Zırh Eğitimi 2: Zırh Max Dex bonusu +2, Armor Check Penalty -2 olur.", "target": "armor_check_penalty", "value": 1}],
        19: [{"name": "Weapon Training 2", "description": "Silah Eğitimi 2: Silah grubu bonusu +2 Saldırı ve Hasar bonusuna yükselir."}]
    },
    "monk": {
        3: [{"name": "Unarmed Strike & AC Bonus", "description": "Silahsız Dövüş & AC Bonusu: Silahsız vuruşlar 1d6 hasar verir. Zırhsızken WIS bonusu AC'ye eklenir."}],
        7: [{"name": "Evasion", "description": "Sıyrılma (Evasion): Reflex zarında başarılı olursanız yarım hasar yerine SIFIR hasar alırsınız."}],
        11: [{"name": "Ki Pool (Magic)", "description": "Ki Havuzu: Ki harcayarak ek silahsız saldırı veya +4 AC kazanır."}],
        15: [{"name": "Abundant Step", "description": "Bolluk Adımı: Dimension Door büyüsü gibi ışınlanabilir."}],
        19: [{"name": "Diamond Soul", "description": "Elmas Ruh (Spell Resistance): Büyü Direnci (SR = Karakter Seviyesi + 10) kazanır."}]
    },
    "paladin": {
        3: [{"name": "Detect Evil & Smite Evil 1/day", "description": "Kötülüğü Cezalandır (Smite Evil): Günde 1 kez Kötü yaratığa karşı CHA bonusunu Saldırıya, seviyeyi Hasara ekler."}],
        7: [{"name": "Lay on Hands", "description": "Ellerle İyileştirme (Lay on Hands): Günde 1/2 seviye kez 1d6 hp iyileştirir."}],
        11: [{"name": "Aura of Courage & Mercy", "description": "Cesaret Halesi & Merhamet: Yakındaki müttefiklere korku bağışıklığı verir."}],
        15: [{"name": "Smite Evil 2/day", "description": "Smite Evil Artışı: Günde 2 kez Smite Evil kullanabilir."}],
        19: [{"name": "Holy Champion", "description": "Kutsal Şampiyon: Smite Evil kullanırken maksimum iyileştirme/hasar vurur."}]
    },
    "ranger": {
        3: [{"name": "Track & 1st Favored Enemy (+2)", "description": "İz Sürme & Seçkin Düşman (+2): Seçilen düşman türüne karşı +2 Saldırı, Hasar ve Algı bonusu."}],
        7: [{"name": "Favored Terrain (+2)", "description": "Seçkin Arazi (+2): Seçilen arazi türünde +2 Gizlilik, Algı ve Hayatta Kalma bonusu."}],
        11: [{"name": "2nd Favored Enemy (+2)", "description": "2. Seçkin Düşman: İkinci bir düşman türü seçilir."}],
        15: [{"name": "Quarry", "description": "Av: Avlanan hedef düşmana karşı Otomatik İz Sürme ve +2 Saldırı bonusu."}],
        19: [{"name": "Improved Evasion", "description": "Gelişmiş Sıyrılma: Reflex zarında başarısız olsanız bile sadece yarım hasar alırsınız."}]
    },
    "rogue": {
        3: [{"name": "Trapfinding", "description": "Tuzak Bulma (Trapfinding): Algı ve Tuzak Çözme zarlarına +1/2 seviye bonus. Büyülü tuzakları çözebilir."}],
        7: [{"name": "Sneak Attack +1d6", "description": "Sinsi Saldırı (+1d6): Hazırlıksız veya kuşatılmış hedeflere +1d6 ekstra hassas hasar."}],
        11: [{"name": "Uncanny Dodge", "description": "Hazırlıksız Yakalanmama: DEX AC bonusunu hazırlıksızken kaybetmez."}],
        15: [{"name": "Sneak Attack +2d6", "description": "Sinsi Saldırı Artışı: Sinsi Saldırı +2d6 ekstra hasara yükselir."}],
        19: [{"name": "Evasion", "description": "Sıyrılma (Evasion): Başarılı Reflex zarlarında sıfır hasar alır."}]
    },
    "sorcerer": {
        3: [{"name": "Bloodline 1st Power", "description": "Soybağı Gücü (Bloodline Power): Seçilen Soybağının (ör. Dragon, Arcane) 1. seviye gücünü kazanır."}],
        7: [{"name": "Bloodline Feat / Power", "description": "Soybağı Hüneri: Soybağının özel feat listesinden bir yetenek seçer."}],
        11: [{"name": "Bloodline 9th Power", "description": "Soybağı 9. Seviye Gücü: Soybağının gelişmiş gücünü kazanır."}],
        15: [{"name": "Bloodline 15th Power", "description": "Soybağı 15. Seviye Gücü: Soybağının usta gücünü kazanır."}],
        19: [{"name": "Bloodline Apotheosis", "description": "Soybağı Zirvesi (Apotheosis): Soybağının tam yaratık dönüşümünü kazanır."}]
    },
    "wizard": {
        3: [{"name": "Arcane School 1st Power & Familiar", "description": "Büyü Okulu & Tanıdık (Familiar): Büyü okulu (Evocation, Abjuration vb.) 1. seviye gücü ve Büyülü Yoldaş kazanır."}],
        7: [{"name": "Cantrips", "description": "Hileli Büyüler (Cantrips): Günde sınırsız 0. seviye büyü atabilir."}],
        11: [{"name": "Arcane School 8th Power", "description": "Büyü Okulu 8. Seviye Gücü: Okulun 8. seviye ana gücünü kazanır."}],
        15: [{"name": "School Discovery", "description": "Okul Keşfi: Okul büyü zarlarına +1 DC veya ek büyü alanı."}],
        19: [{"name": "School Mastery Capstone", "description": "Okul Üstadı: Okul büyülerinin tamamında usta sayılır."}]
    },
    "alchemist": {
        3: [{"name": "Alchemy & Bombs (1d6)", "description": "Simya & Bombalar: Günde (Level + INT Mod) adet simya bombası atabilir (1d6 + INT Hasar)."}],
        7: [{"name": "Mutagen", "description": "Mutajen: 10 dk sürer, seçilen fiziksel stat'a +4 alch bonusu, +2 Natural AC verir."}],
        11: [{"name": "Discovery", "description": "Simya Keşfi (Discovery): Bir Alchemist Keşfi seçer."}],
        15: [{"name": "Poison Immunity", "description": "Zehir Bağışıklığı: Tüm zehirlere tam bağışıklık kazanır."}],
        19: [{"name": "Greater Mutagen", "description": "Büyük Mutajen: Mutajen bonusları +6/+4 olur."}]
    },
    "gunslinger": {
        3: [{"name": "Firearm Proficiency & Gunsmithing", "description": "Ateşli Silah Yetkinliği & Silah Tamiri: Tüm ateşli silahlarda yetkindir."}],
        7: [{"name": "Grit & Deeds", "description": "Cesaret Puanları (Grit): Deadeye ve Quick Clear eylemlerini yapabilir."}],
        11: [{"name": "Targeting Deed", "description": "Hedefli Atış: Hedefin belirli uzvuna nişan alıp sakatlayabilir."}],
        15: [{"name": "Bleeding Wound Deed", "description": "Kanatan Yara: Ateşli silah atışları kanama hasarı verir."}],
        19: [{"name": "Evasive Deed", "description": "Ateş Altında Sıyrılma: Sıyrılma yeteneği kazanır."}]
    },
    "inquisitor": {
        3: [{"name": "Stern Gaze & Judgment", "description": "Sert Bakış & Yargı: Niyet Sezme ve Gözdağına +1/2 seviye bonus. Günde 1 Yargı (Judgment) açabilir."}],
        7: [{"name": "Solo Tactics", "description": "Tekil Taktikler: Müttefikler teamwork feat'e sahip olmasa bile avantajlarından yararlanır."}],
        11: [{"name": "Judgment 2/day", "description": "Yargı Artışı: Günde 2 kez Yargı açabilir."}],
        15: [{"name": "Teamwork Feat", "description": "Takım Yeteneği: Ekstra bir Teamwork Feat kazanır."}],
        19: [{"name": "True Judgment", "description": "Gerçek Yargı: Yargılanan hedefe ölümcül darbe indirme şansı."}]
    },
    "magus": {
        3: [{"name": "Arcane Pool & Spell Combat", "description": "Büyü Havuzu & Büyülü Dövüş: Silahına geçici +1 büyü bonusu yükler. Tek el silah ve büyü ile aynı anda vurabilir."}],
        7: [{"name": "Magus Arcana", "description": "Magus Arkana: Seçilen bir Magus Arcana yeteneği kazanır."}],
        11: [{"name": "Spellstrike", "description": "Büyü Vuruşu (Spellstrike): Dokunma büyülerini silahının darbesi üzerinden iletir."}],
        15: [{"name": "Advanced Magus Arcana", "description": "Gelişmiş Arkana: Üst seviye Magus Arcana kazanır."}],
        19: [{"name": "Greater Spell Combat", "description": "Büyük Büyülü Dövüş: Spell Combat yaparken zarlara ceza almaz."}]
    },
    "oracle": {
        3: [{"name": "Oracle Curse & 1st Revelation", "description": "Kahin Laneti & 1. Esin (Revelation): Bir Kahin laneti ve seçilen gizemin 1. esinini kazanır."}],
        7: [{"name": "2nd Revelation", "description": "2. Esin (Revelation): Gizemin ikinci esinini kazanır."}],
        11: [{"name": "Curse Advancement", "description": "Lanet İlerlemesi: Lanetin 5. seviye avantajı aktifleşir."}],
        15: [{"name": "3rd Revelation", "description": "3. Esin: Gizemin üçüncü esinini kazanır."}],
        19: [{"name": "Final Revelation", "description": "Son Esin: Gizemin zirve gücünü kazanır."}]
    }
}

# Levels where general feats are forfeited in PF1e VMC
VMC_FEAT_SACRIFICE_LEVELS: Set[int] = {3, 7, 11, 15, 19}


class PF1eVMCEngine:
    """Pathfinder 1e Variant Multiclassing (VMC) Rules Calculator."""

    @staticmethod
    def is_vmc_allowed(primary_class: str, secondary_vmc_class: str) -> Tuple[bool, str]:
        """
        Validates if secondary VMC class is eligible.
        Rule: VMC class cannot be the same as primary class.
        """
        p_clean = str(primary_class or "").lower().strip()
        s_clean = str(secondary_vmc_class or "").lower().strip()

        if not s_clean:
            return True, ""

        if p_clean == s_clean or p_clean in s_clean or s_clean in p_clean:
            return False, f"VMC İkincil Sınıfı ({secondary_vmc_class.title()}), karakterin ana sınıfı ({primary_class.title()}) ile aynı olamaz!"

        if s_clean not in VMC_CLASS_DATABASE:
            return False, f"Tanımsız VMC Sınıfı: {secondary_vmc_class}"

        return True, ""

    @staticmethod
    def get_sacrificed_feat_count(character_level: int, vmc_class: str) -> int:
        """
        Calculates how many general feats the character has forfeited up to character_level due to VMC.
        Sacrificed at levels 3, 7, 11, 15, 19.
        """
        if not vmc_class:
            return 0
        
        lvl = max(1, int(character_level))
        count = 0
        for s_lvl in VMC_FEAT_SACRIFICE_LEVELS:
            if lvl >= s_lvl:
                count += 1
        return count

    @classmethod
    def get_granted_vmc_features(cls, secondary_vmc_class: str, character_level: int) -> List[Dict[str, Any]]:
        """
        Returns all granted VMC class features for character_level.
        """
        v_key = str(secondary_vmc_class or "").lower().strip()
        if not v_key or v_key not in VMC_CLASS_DATABASE:
            return []

        lvl = max(1, int(character_level))
        progression = VMC_CLASS_DATABASE[v_key]
        granted: List[Dict[str, Any]] = []

        for req_lvl in sorted(progression.keys()):
            if lvl >= req_lvl:
                for feat_info in progression[req_lvl]:
                    f_copy = feat_info.copy()
                    f_copy["granted_at_level"] = req_lvl
                    f_copy["vmc_class"] = v_key.title()
                    granted.append(f_copy)

        return granted
