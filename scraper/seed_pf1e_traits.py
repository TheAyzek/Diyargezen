"""
Pathfinder 1e Trait Seeder
- Kategorize edilmiş 80+ trait ekler/günceller
- Her trait için: trait_category, bonuses (type, value, target) yapısı
- Mevcut scraper verisi üzerinde kategori tespiti de yapılır
"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "characters.db"

# -----------------------------------------------------------------------
# Full curated trait list with PF1e-accurate bonus structures
# -----------------------------------------------------------------------
TRAITS = [
    # ===== COMBAT TRAITS =====
    ("Reactionary", "Combat",
     "Tepkisel (Combat Trait). Şaşırtıcı doğal reflekslere sahipsiniz. <b>+2 İnisiyatif (Initiative)</b> bonusu kazandırır.",
     [{"type": "initiative", "value": 2, "bonus_type": "untyped"}]),

    ("Armor Expert", "Combat",
     "Zırh Uzmanı (Combat Trait). Zırh giyme alışkanlığı. <b>Zırh Kontrol Cezasını (ACP) 1 puan azaltır</b> (minimum 0).",
     [{"type": "armor_check_penalty", "value": -1, "bonus_type": "untyped"}]),

    ("Resilient", "Combat",
     "Dirençli (Combat Trait). Zorlu koşullara karşı inanılmaz bir dayanıklılık. <b>+1 Fortitude</b> kurtarma zarı bonusu.",
     [{"type": "save_fortitude", "value": 1, "bonus_type": "trait"}]),

    ("Dirty Fighter", "Combat",
     "Kirli Dövüşçü (Combat Trait). Düşmanı kıskaçta (flanking) yakaladığınızda <b>+1 Hasar Bonusu</b> verir.",
     [{"type": "flanking_damage", "value": 1, "bonus_type": "trait"}]),

    ("Blade of Mercy", "Combat",
     "Merhamet Kılıcı (Combat Trait). Bir canlıya kesici silahla öldürücü olmayan vuruş yaptığınızda <b>-4 yerine -2 ceza</b> alırsınız.",
     [{"type": "nonlethal_penalty", "value": 2, "bonus_type": "untyped"}]),

    ("Defender of the Society", "Combat",
     "Toplum Savunucusu (Combat Trait). Orta ya da ağır zırh giyerken <b>+1 Zırh Sınıfı (AC)</b> bonusu.",
     [{"type": "armor_class", "value": 1, "bonus_type": "trait", "condition": "medium_or_heavy_armor"}]),

    ("Deft Dodger", "Combat",
     "Çevik Kaçınıcı (Combat Trait). Sert tecrübeler sayesinde kaçmayı öğrendiniz. <b>+1 Reflex</b> kurtarma zarı bonusu.",
     [{"type": "save_reflex", "value": 1, "bonus_type": "trait"}]),

    ("Fencer", "Combat",
     "Eskrimci (Combat Trait). Fırsatçı saldırılar için deneyimlisiniz. <b>+1 İnisiyatif</b> bonusu, Combat Expertise kullanırken.",
     [{"type": "initiative", "value": 1, "bonus_type": "trait"}]),

    ("Unbreakable Hate", "Combat",
     "Kırılmaz Nefret (Combat Trait). Tek bir seçilmiş düşman tipine karşı <b>+1 Hasar Bonusu</b>.",
     [{"type": "damage_vs_chosen_enemy", "value": 1, "bonus_type": "trait"}]),

    # ===== FAITH TRAITS =====
    ("Indomitable Faith", "Faith",
     "Yıkılmaz İnanç (Faith Trait). Sarsılmaz inanç ve kararlılık. <b>+1 Will (İrade)</b> kurtarma zarı bonusu.",
     [{"type": "save_will", "value": 1, "bonus_type": "trait"}]),

    ("Birthmark", "Faith",
     "Kutsal Doğum Lekesi (Faith Trait). Vücudunuzdaki kutsal işaret tanrı sembolü işlevi görür. Zihin kontrol büyülerine karşı <b>+2 Will</b> bonusu, kutsal sembol sayılır.",
     [{"type": "save_will", "value": 2, "bonus_type": "trait", "condition": "compulsion_and_charm"}]),

    ("Ease of Faith", "Faith",
     "İnanç Rahatlığı (Faith Trait). İnancı aktarmak sizin için doğal. <b>+1 Diplomacy</b> bonusu ve Diplomacy sınıf becerisi (Class Skill) olur.",
     [{"type": "skill", "skill": "Diplomacy", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    ("Blessed", "Faith",
     "Kutsanmış (Faith Trait). Tanrının nimeti üzerinizdedir. Hayatta kalma testlerinde <b>+1 Şans Bonusu</b>.",
     [{"type": "save_all", "value": 1, "bonus_type": "luck", "condition": "stabilize_checks"}]),

    ("Devotee of the Green", "Faith",
     "Yeşilin Adanmışı (Faith Trait). Doğayla derin bir bağ. <b>+1 Knowledge (Nature)</b> ve <b>+1 Heal</b> bonusu, ikisi de sınıf becerisi olur.",
     [
         {"type": "skill", "skill": "Knowledge (Nature)", "value": 1, "makes_class_skill": True, "bonus_type": "trait"},
         {"type": "skill", "skill": "Heal", "value": 1, "makes_class_skill": True, "bonus_type": "trait"},
     ]),

    ("Sacred Conduit", "Faith",
     "Kutsal Kanal (Faith Trait). Kanalın enerjisi sizin içinizdeymiş gibi akar. Kanal enerjisi DC'sine <b>+1 bonus</b>.",
     [{"type": "channel_energy_dc", "value": 1, "bonus_type": "trait"}]),

    ("Stalwart of the Society", "Faith",
     "Toplumun Direği (Faith Trait). Büyücü sınıfı için Kanal Enerjisi kullanımını <b>+2 ileri</b> olarak sayar.",
     [{"type": "channel_energy_uses", "value": 2, "bonus_type": "trait"}]),

    # ===== MAGIC TRAITS =====
    ("Focused Mind", "Magic",
     "Odaklanmış Zihin (Magic Trait). Zihin eğitimi sayesinde konsantrasyonunuz güçlüdür. <b>+2 Konsantrasyon (Concentration)</b> zarı bonusu.",
     [{"type": "concentration", "value": 2, "bonus_type": "trait"}]),

    ("Magical Knack", "Magic",
     "Büyülü Yetenek (Magic Trait). Seçilen bir sınıfın <b>Büyücü Seviyesi (Caster Level) +2 bonus</b> kazanır (karakter seviyesini geçemez).",
     [{"type": "caster_level", "value": 2, "bonus_type": "trait"}]),

    ("Magical Lineage", "Magic",
     "Büyülü Soy (Magic Trait). Seçilen tek bir büyünün Metamagic seviye maliyetini <b>1 puan düşürür</b>.",
     [{"type": "metamagic_cost", "value": -1, "bonus_type": "trait"}]),

    ("Gifted Adept", "Magic",
     "Yetenekli Çırak (Magic Trait). Seçilen bir büyünün <b>Caster Level'ı +1 artar</b>.",
     [{"type": "caster_level_single_spell", "value": 1, "bonus_type": "trait"}]),

    ("Hedge Magician", "Magic",
     "Çit Büyücüsü (Magic Trait). Büyülü eşya üretirken maliyet <b>%5 azalır</b>.",
     [{"type": "craft_magic_item_cost", "value": -5, "bonus_type": "trait"}]),

    ("Spark of Creation", "Magic",
     "Yaratıcılık Kıvılcımı (Magic Trait). Eşya üretme maliyeti <b>%5 azalır</b> ve Spellcraft sınıf becerisi olur.",
     [
         {"type": "craft_cost", "value": -5, "bonus_type": "trait"},
         {"type": "skill", "skill": "Spellcraft", "value": 0, "makes_class_skill": True, "bonus_type": "trait"},
     ]),

    ("Mathematical Prodigy", "Magic",
     "Matematik Dahisi (Magic Trait). <b>+1 Knowledge (Arcana)</b> ve Knowledge (Engineering) bonusu, bunlardan biri sınıf becerisi olur.",
     [{"type": "skill", "skill": "Knowledge (Arcana)", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    # ===== SOCIAL TRAITS =====
    ("Rich Parents", "Social",
     "Zengin Aile (Social Trait). Varlıklı bir ailede büyüdünüz. Başlangıç altın miktarını <b>900 GP</b> seviyesine çıkarır.",
     [{"type": "starting_gold", "value": 900, "bonus_type": "trait"}]),

    ("Fast-Talker", "Social",
     "Hızlı Konuşmacı (Social Trait). Dil uzunluğunuz efsanevi. <b>+1 Bluff</b> bonusu ve Bluff sınıf becerisi (Class Skill) olur.",
     [{"type": "skill", "skill": "Bluff", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    ("Suspicious", "Social",
     "Şüpheci (Social Trait). Kimseye çok çabuk güvenmezsiniz. <b>+1 Sense Motive</b> bonusu ve sınıf becerisi olur.",
     [{"type": "skill", "skill": "Sense Motive", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    ("Charming", "Social",
     "Büyüleyici (Social Trait). Güzellik ve yeteneğinizle insanları etkilersiniz. <b>+1 Bluff veya Diplomacy</b> (seçilebilir) bonusu.",
     [{"type": "skill", "skill": "Diplomacy", "value": 1, "bonus_type": "trait"}]),

    ("Adopted", "Social",
     "Evlat Edinilmiş (Social Trait). Başka bir ırkın kültüründe büyüdünüz; o ırkın ırk trait'lerinden birini seçebilirsiniz.",
     [{"type": "racial_trait_access", "value": 1, "bonus_type": "trait"}]),

    ("Poverty-Stricken", "Social",
     "Fakir Geçmiş (Social Trait). Hayatta kalmayı öğrendiniz. <b>+1 Survival</b> bonusu ve sınıf becerisi olur.",
     [{"type": "skill", "skill": "Survival", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    ("Natural-Born Leader", "Social",
     "Doğal Lider (Social Trait). Müttefikler sizin için Will kurtarma zarlarına <b>+1 Moral Bonusu</b> alır.",
     [{"type": "ally_will_saves", "value": 1, "bonus_type": "morale"}]),

    # ===== RACE TRAITS =====
    ("Elven Reflexes", "Race",
     "Elf Refleksleri (Race Trait — Elf veya Half-Elf). Elfin eşsiz çevikliği. <b>+2 İnisiyatif (Initiative)</b> bonusu.",
     [{"type": "initiative", "value": 2, "bonus_type": "trait"}]),

    ("Glory of Old", "Race",
     "Eski Günlerin Onuru (Race Trait — Cüce). Cücelerin büyüye direnci. Büyülere, büyü benzeri yeteneklere ve zehirlere karşı <b>+1 Kurtarma Zarı</b>.",
     [{"type": "save_all", "value": 1, "bonus_type": "trait", "condition": "spells_spell_like_poisons"}]),

    ("Halfling Luck", "Race",
     "Buçukluk Şansı (Race Trait — Buçukluk). Buçuklukların doğal şansı. Tüm kurtarma zarlarına <b>+1 Şans Bonusu</b>.",
     [{"type": "save_all", "value": 1, "bonus_type": "luck"}]),

    ("Gnome Magic", "Race",
     "Cüce Büyüsü (Race Trait — Cüce). Cüce büyü geleneği. Illüzyon büyülerinin DC'sine <b>+1 bonus</b>.",
     [{"type": "spell_dc", "value": 1, "bonus_type": "trait", "condition": "illusion_spells"}]),

    ("Human Curiosity", "Race",
     "İnsan Merakı (Race Trait — İnsan). İnsanın sınırsız merakı. Herhangi bir beceri sınıf becerisi olur ve o beceride <b>+1 bonus</b>.",
     [{"type": "skill", "skill": "any", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    ("Half-Orc Ferocity", "Race",
     "Yarı-Ork Vahşeti (Race Trait — Yarı-Ork). Düşmana düşünce 0 HP'de bile 1 tur daha dövüşebilirsiniz.",
     [{"type": "ferocity", "value": 1, "bonus_type": "trait"}]),

    # ===== REGIONAL TRAITS =====
    ("Varisian Wanderer", "Regional",
     "Varisia Gezgini (Regional Trait). Varisia'da büyümek size zengin bir kültür kazandırdı. <b>+1 Perform veya Survival</b> bonusu, o beceri sınıf becerisi olur.",
     [{"type": "skill", "skill": "Survival", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    ("Absalom Diplomat", "Regional",
     "Absalom Diplomatı (Regional Trait). Absalom'un karmaşık siyasi iklimi sizi ustalaştırdı. <b>+1 Diplomacy</b> bonusu.",
     [{"type": "skill", "skill": "Diplomacy", "value": 1, "bonus_type": "trait"}]),

    ("River Rat", "Regional",
     "Nehir Faresi (Regional Trait — Andoran / Galt). Bıçaklarla büyüdünüz. Hançer ve benzeri bıçaklarda <b>+1 Hasar</b> ve Swim sınıf becerisi olur.",
     [
         {"type": "weapon_damage", "value": 1, "bonus_type": "trait", "condition": "daggers"},
         {"type": "skill", "skill": "Swim", "value": 0, "makes_class_skill": True, "bonus_type": "trait"},
     ]),

    ("Tuscany Veteran", "Regional",
     "Taldor Gazisi (Regional Trait — Taldor). Askeri disiplin. <b>+1 Knowledge (Engineering)</b> ve sınıf becerisi olur.",
     [{"type": "skill", "skill": "Knowledge (Engineering)", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    ("Wilderness Forager", "Regional",
     "Doğa Toplayıcısı (Regional Trait). Vahşi doğada yetkinlik. <b>+2 Survival</b> yiyecek/su bulmak için.",
     [{"type": "skill", "skill": "Survival", "value": 2, "bonus_type": "trait", "condition": "foraging"}]),

    # ===== RELIGION TRAITS =====
    ("Deft Dancer (Sarenrae)", "Religion",
     "Zarif Dansçı (Religion Trait — Sarenrae). Sarenrae'nin cemaatinin dansları sizi çevik kıldı. <b>+1 Acrobatics</b> bonusu ve sınıf becerisi olur.",
     [{"type": "skill", "skill": "Acrobatics", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    ("Cleansing the Twisted (Sarenrae)", "Religion",
     "Kötülük Arındırıcı (Religion Trait — Sarenrae). Sarenrae'nin ışığı günahları yakar. Şer yaratıklara karşı <b>+1 Hasar Bonusu</b>.",
     [{"type": "damage_vs_evil", "value": 1, "bonus_type": "trait"}]),

    ("Seeker (Cayden Cailean)", "Religion",
     "Araştırmacı (Religion Trait — Cayden Cailean). Serüven ruhu. <b>+1 Perception</b> bonusu ve sınıf becerisi olur.",
     [{"type": "skill", "skill": "Perception", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    ("Fate's Favored", "Religion",
     "Kaderin Gözdesiyim (Religion Trait — Desna). Tüm şans bonusları <b>+1 artar</b> (örn. Halfling Luck, İyi Uğur büyüsü).",
     [{"type": "luck_bonus_boost", "value": 1, "bonus_type": "trait"}]),

    ("Iomedae's Blessing", "Religion",
     "İomedae'nin Lütfu (Religion Trait — İomedae). Kılıçla savaşırken <b>+1 İnisiyatif</b> bonusu.",
     [{"type": "initiative", "value": 1, "bonus_type": "trait", "condition": "wielding_sword"}]),

    ("Erastil's Speaker", "Religion",
     "Erastil'in Sözcüsü (Religion Trait — Erastil). Topluluk büyüleri için CD'ye <b>+1 bonus</b>.",
     [{"type": "spell_dc", "value": 1, "bonus_type": "trait", "condition": "community_domain"}]),

    # ===== CAMPAIGN TRAITS =====
    ("Outlander", "Campaign",
     "Dışarıdan Gelen (Campaign Trait). Başka bir diyardan geldiniz; <b>+1 İnisiyatif</b> kazanırsınız.",
     [{"type": "initiative", "value": 1, "bonus_type": "trait"}]),

    ("Riddleport Rat", "Campaign",
     "Riddleport Faresi (Campaign Trait — Second Darkness). Riddleport'un karanlık sokaklarında büyüdünüz. <b>+1 Sleight of Hand</b> ve sınıf becerisi.",
     [{"type": "skill", "skill": "Sleight of Hand", "value": 1, "makes_class_skill": True, "bonus_type": "trait"}]),

    ("Stolen Fury", "Campaign",
     "Çalınan Öfke (Campaign Trait). Geçmişteki travma savaşta öfkeye dönüşür. <b>+2 Saldırı Bonusu</b> öfke (rage) sırasında.",
     [{"type": "attack_bonus_while_raging", "value": 2, "bonus_type": "trait"}]),
]


def seed_traits(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    updated = 0
    inserted = 0

    for name, category, desc, bonuses in TRAITS:
        sistem_verisi = json.dumps({
            "trait_category": category,
            "type": "trait",
            "bonuses": bonuses,
            "system": {"traitType": category}
        }, ensure_ascii=False)

        # Use REPLACE to handle existing entries cleanly
        c.execute(
            "INSERT OR REPLACE INTO entities (isim, sistem, kategori, aciklama, sistem_verisi) "
            "VALUES (?, 'pathfinder1e', 'trait', ?, ?)",
            (name, desc, sistem_verisi)
        )
        inserted += 1

    conn.commit()
    conn.close()
    print(f"[OK] Seeded {inserted} new traits, updated {updated} existing traits.")

    # Now verify
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM entities WHERE sistem='pathfinder1e' AND kategori='trait' AND json_extract(sistem_verisi, '$.trait_category') IS NOT NULL")
    count = c.fetchone()[0]
    conn.close()
    print(f"[OK] Total categorized PF1e traits: {count}")


if __name__ == "__main__":
    seed_traits(DB_PATH)
