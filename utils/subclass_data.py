"""
D&D 5e Subclass Veritabani (SRD + Temel Secenekler)
Her sinif icin subclass secenekleri, secim seviyeleri ve kisa aciklamalar
"""

from typing import Dict, Any, List

# Sinif -> Subclass secim seviyesi
SUBCLASS_LEVEL: Dict[str, int] = {
    "Barbarian": 3,
    "Bard": 3,
    "Cleric": 1,
    "Druid": 2,
    "Fighter": 3,
    "Monk": 3,
    "Paladin": 3,
    "Ranger": 3,
    "Rogue": 3,
    "Sorcerer": 1,
    "Warlock": 1,
    "Wizard": 2,
    "Artificer": 3,
    "Blood Hunter": 3,
}

# Sinif -> Subclass ozellik adi
SUBCLASS_FEATURE_NAME: Dict[str, str] = {
    "Barbarian": "Primal Path",
    "Bard": "Bard College",
    "Cleric": "Divine Domain",
    "Druid": "Druid Circle",
    "Fighter": "Martial Archetype",
    "Monk": "Monastic Tradition",
    "Paladin": "Sacred Oath",
    "Ranger": "Ranger Conclave",
    "Rogue": "Roguish Archetype",
    "Sorcerer": "Sorcerous Origin",
    "Warlock": "Otherworldly Patron",
    "Wizard": "Arcane Tradition",
    "Artificer": "Artificer Specialist",
    "Blood Hunter": "Blood Hunter Order",
}

# Tum subclass secenekleri
SUBCLASS_OPTIONS: Dict[str, List[Dict[str, str]]] = {
    "Barbarian": [
        {"name": "Path of the Berserker", "description": "Savaş çılgınlığına odaklanır. Frenzy ile bonus action saldırı, Mindless Rage ile charm/fear bağışıklığı."},
        {"name": "Path of the Totem Warrior", "description": "Doğa ruhlarından güç alır. Bear (dayanıklılık), Eagle (hız), Wolf (takım çalışması) totem seçenekleri."},
        {"name": "Path of the Ancestral Guardian", "description": "Ataların ruhlarını çağırır. Saldırdığı hedeflere atalar yapışır ve onların diğer müttefiklere saldırmasını zorlaştırır."},
        {"name": "Path of the Storm Herald", "description": "Fırtına gücünü kullanır. Desert (ateş), Sea (yıldırım), Tundra (buz) seçenekleri."},
        {"name": "Path of the Zealot", "description": "İlahi öfke ile savaşır. Rage sırasında ekstra radiant/necrotic hasar. Ölümden kolay diriltilir."},
    ],
    "Bard": [
        {"name": "College of Lore", "description": "Bilgi ve sırlar uzmanı. Ek proficiency'ler, Cutting Words ile düşman zarlarını düşürme."},
        {"name": "College of Valor", "description": "Savaşçı ozan. Medium armor ve shield proficiency, Combat Inspiration ile müttefiklere savaş desteği."},
        {"name": "College of Glamour", "description": "Fey büyüsü ile büyüleyici performanslar. Mantle of Inspiration ile müttefiklere geçici HP."},
        {"name": "College of Swords", "description": "Kılıç dansçısı. Blade Flourish ile saldırırken bonus efektler, Fighting Style kazanır."},
        {"name": "College of Whispers", "description": "Gizli ajan ve manipülatör. Psychic Blades ile ekstra psionic hasar, Words of Terror ile korkutma."},
    ],
    "Cleric": [
        {"name": "Life Domain", "description": "Şifa uzmanı. Şifa büyüleri güçlendirilmiş, heavy armor proficiency, Disciple of Life ile ekstra şifa."},
        {"name": "Light Domain", "description": "Işık ve ateş gücü. Warding Flare ile saldırılara dezavantaj, güçlü ateş büyüleri."},
        {"name": "Tempest Domain", "description": "Fırtına ve yıldırım gücü. Wrath of the Storm ile yıldırım karşı saldırısı, martial weapon proficiency."},
        {"name": "War Domain", "description": "Savaş tanrısı hizmetkarı. Bonus action saldırı, War Priest ile ekstra saldırılar, heavy armor/martial weapon."},
        {"name": "Knowledge Domain", "description": "Bilgi tanrısı. Ek dil ve proficiency'ler, düşünceleri okuma, Channel Divinity ile bilgi edinme."},
        {"name": "Nature Domain", "description": "Doğa tanrısı. Druid cantrip, heavy armor, hayvan ve bitki büyüleri."},
        {"name": "Trickery Domain", "description": "Hile ve aldatma. İllüzyon klonu yaratma, gizlilik büyüleri, Blessing of the Trickster."},
    ],
    "Druid": [
        {"name": "Circle of the Land", "description": "Arazi büyücüsü. Ek büyüler (bölgeye göre), Natural Recovery ile spell slot geri kazanma."},
        {"name": "Circle of the Moon", "description": "Şekil değiştirme uzmanı. Combat Wild Shape (bonus action), daha güçlü hayvan formları, CR limiti artışı."},
        {"name": "Circle of Dreams", "description": "Feywild bağlantısı. Balm of the Summer Court ile şifa, Hearth of Moonlight ile güvenli dinlenme alanı."},
        {"name": "Circle of the Shepherd", "description": "Ruh koruyucusu. Spirit Totem (Bear/Hawk/Unicorn) ile müttefiklere buff, güçlü conjuration büyüleri."},
    ],
    "Fighter": [
        {"name": "Champion", "description": "Saf savaşçı mükemmelliği. Improved Critical (19-20), Remarkable Athlete, ek Fighting Style."},
        {"name": "Battle Master", "description": "Taktik savaş uzmanı. Superiority Dice ile manevralar (Trip, Riposte, Disarming Attack vs.)."},
        {"name": "Eldritch Knight", "description": "Büyü-kılıç karışımı. Wizard büyü listesinden abjuration/evocation büyüleri, War Magic."},
        {"name": "Arcane Archer", "description": "Büyülü okçu. Arcane Shot seçenekleri ile oklara büyü efektleri ekleme."},
        {"name": "Cavalier", "description": "Atlı şövalye. Unwavering Mark ile müttefikleri koruma, atlı savaş uzmanlığı."},
        {"name": "Samurai", "description": "Disiplinli savaşçı. Fighting Spirit ile geçici HP ve advantage, Elegant Courtier ile sosyal beceri."},
    ],
    "Monk": [
        {"name": "Way of the Open Hand", "description": "Dövüş sanatı ustası. Open Hand Technique ile push/prone/reaction engelleme, Quivering Palm."},
        {"name": "Way of Shadow", "description": "Gölge ninja. Karanlıkta gizlenme büyüleri, Shadow Step ile teleport, gizlilik odaklı."},
        {"name": "Way of the Four Elements", "description": "Elemental bükücü. Ki noktaları ile ateş/su/toprak/hava büyüleri kullanma."},
        {"name": "Way of the Drunken Master", "description": "Sarhoş usta. Flurry of Blows ile hareket, saldırı kaçırmalara karşı redirect."},
        {"name": "Way of the Kensei", "description": "Silah ustası. Seçilen silahları monk weapon olarak kullanma, Agile Parry ile AC bonusu."},
    ],
    "Paladin": [
        {"name": "Oath of Devotion", "description": "Klasik kutsal şövalye. Sacred Weapon ile saldırı bonusu, Turn the Unholy, Aura of Devotion."},
        {"name": "Oath of the Ancients", "description": "Doğa ve ışık koruyucusu. Büyülere karşı dayanıklılık aurası, fey bağlantılı büyüler."},
        {"name": "Oath of Vengeance", "description": "İntikam yemini. Vow of Enmity ile tek hedefe advantage, Relentless Avenger ile takip."},
        {"name": "Oath of Conquest", "description": "Fetih ve hakimiyet. Frightened düşmanları yavaşlatma, Conquering Presence ile korkutma."},
        {"name": "Oath of Redemption", "description": "Barış ve kurtuluş. Hasarı emme ile müttefikleri koruma, ikna ve diplomasi odaklı."},
    ],
    "Ranger": [
        {"name": "Hunter", "description": "Av uzmanı. Colossus Slayer/Giant Killer/Horde Breaker ile çeşitli avcılık tarzları."},
        {"name": "Beast Master", "description": "Hayvan dostluğu. Bir companion hayvanla birlikte savaşma, hayvanın güçlenmesi."},
        {"name": "Gloom Stalker", "description": "Karanlık avcısı. Karanlıkta görünmezlik, ilk tur ekstra saldırı, Dread Ambusher."},
        {"name": "Horizon Walker", "description": "Düzlemler arası gezgin. Planar Warrior ile ekstra force hasar, teleportasyon yetenekleri."},
        {"name": "Monster Slayer", "description": "Canavar avcısı. Supernatural Defense ile saving throw bonusu, Slayer's Prey ile ekstra hasar."},
    ],
    "Rogue": [
        {"name": "Thief", "description": "Klasik hırsız. Fast Hands ile bonus action nesne kullanımı, Second-Story Work ile tırmanma."},
        {"name": "Assassin", "description": "Suikastçı. Surprise round'da otomatik critical, Assassinate ile ilk turda avantaj."},
        {"name": "Arcane Trickster", "description": "Büyücü hırsız. Wizard büyü listesinden illusion/enchantment büyüleri, Mage Hand Legerdemain."},
        {"name": "Swashbuckler", "description": "Karizmatik düellocu. Rakish Audacity ile initiative ve Sneak Attack kolaylığı, Fancy Footwork."},
        {"name": "Mastermind", "description": "Beyin takımı. Bonus action Help, Master of Intrigue ile kimlik taklit, taktik uzmanı."},
        {"name": "Scout", "description": "Keşifçi. Skirmisher ile reaction hareket, Nature/Survival expertise, hızlı hareket."},
    ],
    "Sorcerer": [
        {"name": "Draconic Bloodline", "description": "Ejderha soyundan güç. Ek HP, doğal zırh (AC 13+DEX), element hasarı güçlendirme."},
        {"name": "Wild Magic", "description": "Kaotik büyü gücü. Wild Magic Surge ile rastgele efektler, Tides of Chaos ile advantage."},
        {"name": "Divine Soul", "description": "İlahi büyü kaynağı. Cleric büyü listesine erişim, Favored by the Gods ile saving throw bonusu."},
        {"name": "Shadow Magic", "description": "Gölge düzlemi gücü. Karanlık görüşü, Strength of the Grave ile ölümden kaçış, Shadow Walk."},
        {"name": "Storm Sorcery", "description": "Fırtına gücü. Büyü sonrası uçma, yıldırım/gök gürültüsü büyüleri güçlendirme."},
    ],
    "Warlock": [
        {"name": "The Archfey", "description": "Fey lordu patronu. Fey Presence ile charm/frighten, Misty Escape ile kaybolma, illusion büyüleri."},
        {"name": "The Fiend", "description": "Şeytan patronu. Dark One's Blessing ile öldürme sonrası geçici HP, ateş büyüleri."},
        {"name": "The Great Old One", "description": "Kozmik varlık patronu. Telepati, Awakened Mind, psionic büyüler, çılgınlık temaları."},
        {"name": "The Celestial", "description": "Melek patronu. Healing Light ile şifa, radiant/fire dayanıklılığı, kutsal büyüler."},
        {"name": "The Hexblade", "description": "Lanetli silah patronu. Medium armor/shield, Charisma ile saldırı, Hexblade's Curse ile hasar bonusu."},
    ],
    "Wizard": [
        {"name": "School of Abjuration", "description": "Koruma büyüsü uzmanı. Arcane Ward ile büyü kalkanı, abjuration büyüleri güçlendirilmiş."},
        {"name": "School of Conjuration", "description": "Çağırma büyüsü uzmanı. Minor Conjuration ile küçük nesneler yaratma, teleportasyon."},
        {"name": "School of Divination", "description": "Kehanet uzmanı. Portent ile geleceği görme (zarları önceden belirleme), Third Eye."},
        {"name": "School of Enchantment", "description": "Büyüleme uzmanı. Hypnotic Gaze ile hipnoz, Split Enchantment ile çift hedef, hafıza silme."},
        {"name": "School of Evocation", "description": "Yıkım büyüsü uzmanı. Sculpt Spells ile müttefikleri koruma, Empowered Evocation ile hasar bonusu."},
        {"name": "School of Illusion", "description": "İllüzyon uzmanı. Improved Minor Illusion, gerçekçi illüzyonlar, Illusory Reality."},
        {"name": "School of Necromancy", "description": "Ölüm büyüsü uzmanı. Undead yaratma, öldürme ile HP kazanma, Undead Thralls."},
        {"name": "School of Transmutation", "description": "Dönüşüm uzmanı. Transmuter's Stone ile buff, şekil değiştirme, madde dönüşümü."},
    ],
}


def get_subclass_level(char_class: str) -> int:
    """Sinifin subclass secim seviyesini dondur"""
    return SUBCLASS_LEVEL.get(char_class, 3)


def get_subclass_feature_name(char_class: str) -> str:
    """Sinifin subclass ozellik adini dondur"""
    return SUBCLASS_FEATURE_NAME.get(char_class, "Subclass")


def get_subclass_options(char_class: str) -> List[Dict[str, str]]:
    """Sinif icin mevcut subclass seceneklerini dondur"""
    return SUBCLASS_OPTIONS.get(char_class, [])


def needs_subclass_selection(character: dict) -> bool:
    """Karakterin subclass secimi yapmasi gerekip gerekmedigi"""
    char_class = character.get("class", "")
    level = character.get("level", 1)
    subclass = character.get("subclass", "")

    required_level = get_subclass_level(char_class)
    return level >= required_level and not subclass

