import sqlite3
import json
from pathlib import Path

# Pathfinder 1st Edition Comprehensive Class Features with Descriptions and Levels
PF1E_CLASS_FEATURES = {
    "Barbarian": [
        ("Fast Movement (Ex)", 1, "Barbarian'ın karada hareket hızı, zırhsız veya hafif/orta zırh giyerken +10 feet artar."),
        ("Rage (Ex)", 1, "Barbarian günde belirli sayıda tur öfkeye girebilir. Öfkelendiğinde Melee Attack, Melee Damage, Will save ve Con puanlarına +4 bonus alır, AC'sine -2 ceza alır."),
        ("Rage Powers (Ex)", 2, "Barbarian 2. seviyeden itibaren her 2 seviyede bir özel Öfke Yeteneği (Rage Power) kazanır (Örn: Totem powers, Knockback, Superstition)."),
        ("Uncanny Dodge (Ex)", 2, "2. seviyeden itibaren Barbarian yakalanmadığı veya görünmez bir düşman saldırmadığı sürece Dex modifikatörünü AC'sine korur, sürpriz saldırılarda hazırlıksız yakalanmaz."),
        ("Trap Sense (Ex)", 3, "Barbarian tuzaklara karşı yapılan Reflex kurtarma atışlarına ve AC'sine +1 bonus kazanır."),
        ("Improved Uncanny Dodge (Ex)", 5, "Barbarian artık kuşatılamaz (flank edilemez). Rogue sinsi saldırıları için en az 4 seviye yüksek olmalıdır."),
        ("Damage Reduction (Ex)", 7, "7. seviyeden itibaren Barbarian her fiziksel darbede DR 1/- kazanır. Bu değer her 3 seviyede bir +1 artar (DR 2/- 10. seviye, DR 3/- 13. seviye vb.)."),
        ("Greater Rage (Ex)", 11, "Öfkelendiğinde Str ve Con bonusu +6'ya, Will save bonusu +3'e yükselir."),
        ("Indomitable Will (Ex)", 14, "Öfkedeyken büyü büyüleme ve zihin etkilerine karşı kurtarma atışlarına +4 bonus kazanır."),
        ("Tireless Rage (Ex)", 17, "Öfke bittiğinde artık yorulmaz (fatigued olmaz)."),
        ("Mighty Rage (Ex)", 20, "Öfkelendiğinde Str ve Con bonusu +8'e, Will save bonusu +4'e yükselir.")
    ],
    "Bard": [
        ("Bardic Knowledge (Ex)", 1, "Bard tüm Knowledge beceri zarlarına seviyesinin yarısı kadar (+1/2 level) bonus ekler ve tüm Knowledge becerilerini eğitimsiz kullanabilir."),
        ("Bardic Performance (Su)", 1, "Müzik, şiir ve konuşma ile müttefiklerine cesaret verir (Inspire Courage: +1 attack/damage), düşmanları büyüler veya büyüleri bozar."),
        ("Cantrips", 1, "Bard 0. seviye büyüleri (cantrips) sınırsız sayıda okuyabilir."),
        ("Versatile Performance (Ex)", 2, "Bard belirli bir Perform becerisini (Örn: Sing, Oratory) başka becerilerin (Örn: Diplomacy, Sense Motive) yerine zar atarken kullanabilir."),
        ("Well-Versed (Ex)", 2, "Bard ozan performanslarına, ses efektli büyülere ve illüzyonlara karşı kurtarma atışlarına +4 bonus kazanır."),
        ("Lore Master (Ex)", 5, "Günde 1 kez herhangi bir Knowledge zarında doğrudan 20 almış gibi (Take 20) işlem yapabilir."),
        ("Jack-of-All-Trades (Ex)", 10, "10. seviyeden itibaren Bard eğitimsiz olduğu beceri zarlarını dahi tam eğitimli gibi kullanabilir.")
    ],
    "Cleric": [
        ("Aura (Ex)", 1, "Cleric tanrısının hizalamasına (Alignment) uygun güçlü bir kutsal veya lanetli aura yayar."),
        ("Channel Energy (Su)", 1, "Cleric kutsal sembolünü doğrultarak 30 feet yarıçapındaki alanda d6 pozitif veya negatif enerji saçar. Müttefikleri iyileştirir veya zombileri yakar."),
        ("Domains", 1, "Cleric tanrısından 2 adet Alan (Domain) seçer. Her alan Cleric'e özel büyüler ve doğaüstü güçler kazandırır."),
        ("Spells", 1, "Cleric tanrısından doğrudan ilahi büyüler hazırlar. Kendiliğinden (Spontaneous) İyileştirme veya Hasar büyülerine dönüştürebilir.")
    ],
    "Druid": [
        ("Animal Companion (Ex)", 1, "Druid doğayla uyum içinde sadık bir Hayvan Yoldaşı kazanır veya doğa alanından (Domain) güç alır."),
        ("Nature Bond (Ex)", 1, "Druid doğa ruhlarıyla kopmaz bir bağ kurar."),
        ("Nature Sense (Ex)", 1, "Knowledge (nature) ve Survival zarlarına +2 bonus kazanır."),
        ("Wild Empathy (Ex)", 1, "Druid hayvanlarla etkileşime girerek tutumlarını iyileştirmek için zar atabilir."),
        ("Woodland Stride (Ex)", 2, "Doğal çalılar, dikenler ve zorlu arazilerde hız kaybetmeden ilerleyebilir."),
        ("Trackless Step (Ex)", 3, "Doğal ortamlarda geride hiçbir iz veya koku bırakmaz."),
        ("Resist Nature's Lure (Ex)", 4, "Fey ve doğa yaratıklarının büyüsel etkilerine karşı +4 kurtarma bonusu kazanır."),
        ("Wild Shape (Su)", 4, "Druid günde birkaç kez farklı boyutlardaki hayvan, elementel veya bitki formlarına dönüşebilir.")
    ],
    "Fighter": [
        ("Bonus Feats", 1, "Fighter 1. seviyede ve ardından HER çift seviyede bir ekstra Combat Feat kazanır."),
        ("Armor Training (Ex)", 3, "Zırh giyerken Zırh Dövüş Cezası (ACP) 1 azalır ve Dex Maksimum AC bonusu +1 artar. Zırhla tam hızda hareket edebilir."),
        ("Weapon Training (Ex)", 5, "Seçtiği silah grubunda (Örn: Heavy Blades, Bows) saldırı ve hasar zarlarına +1 bonus kazanır (Her 4 seviyede bir bonus artar)."),
        ("Armor Mastery (Ex)", 19, "Ağır zırh giyerken DR 5/- kazanır."),
        ("Weapon Mastery (Ex)", 20, "Seçtiği bir silahta yaptığı tüm kritik vurma tehditleri otomatik doğrulanır ve kritik çarpanı +1 artar.")
    ],
    "Monk": [
        ("Flurry of Blows (Ex)", 1, "Monk silahsız veya monk silahlarıyla ekstra saldırı yapabilir."),
        ("Unarmed Strike (Ex)", 1, "Monk silahsız saldırılarında devasa d6/d8/d10/2d6/2d8 hasar zarları kullanır ve vücudunun her uzvunu silah sayar."),
        ("AC Bonus (Ex)", 1, "Zırhsızken Wisdom modifikatörünü ve seviye bonusunu AC ve CMD skoruna ekler."),
        ("Evasion (Ex)", 2, "Reflex kurtarma atışında başarılı olursa yarı hasar almak yerine HİÇ hasar almaz."),
        ("Fast Movement (Ex)", 3, "Zırhsızken karadaki hareket hızı +10 feet artar (20. seviyede +60 feet'e ulaşır)."),
        ("Ki Pool (Su)", 4, "Monk Ki puanlarını harcayarak ek saldırı yapabilir, hızını +20 feet artırabilir veya AC'sine +4 dodge bonusu ekleyebilir."),
        ("Purity of Body (Ex)", 5, "Tüm hastalıklara karşı tam bağışıklık kazanır."),
        ("Diamond Body (Su)", 11, "Tüm zehirlere karşı tam bağışıklık kazanır.")
    ],
    "Paladin": [
        ("Aura of Good (Ex)", 1, "Paladin güçlü bir iyilik aurası saçar."),
        ("Detect Evil (Sp)", 1, "Paladin istediği an kötülüğü tespit etme büyüsü okuyabilir."),
        ("Smite Evil (Su)", 1, "Paladin kötü bir hedef seçer. Saldırı zarlarına Cha modunu, hasar zarlarına Paladin seviyesini ekler. Hedefin AC bonuslarını deler."),
        ("Lay on Hands (Su)", 2, "Paladin dokunarak müttefiklerini iyileştirir (seviye/2 d6). Kendini iyileştirmek Swift Action'dır."),
        ("Divine Grace (Su)", 2, "Paladin Charisma modifikatörünü TÜM kurtarma atışlarına (Fort, Ref, Will) ekler."),
        ("Aura of Courage (Su)", 3, "Paladin korkuya karşı bağışıktır. 10 feet yakınındaki müttefikleri korkuya karşı +4 bonus kazanır."),
        ("Divine Health (Ex)", 3, "Paladin tüm hastalıklara bağışıktır."),
        ("Mercy (Su)", 3, "Lay on Hands kullandığında hedefin durumlarını (Fatigued, Shaken, Diseased, Poisoned vb.) anında iyileştirir.")
    ],
    "Rogue": [
        ("Sneak Attack (Ex)", 1, "Düşman hazırlıksız yakalandığında veya kuşatıldığında (Flank) +1d6 ekstra sinsi hasar verir (Her 2 seviyede +1d6 artar)."),
        ("Trapfinding (Ex)", 1, "Tuzak arama Perception zarlarına ve Disable Device zarlarına seviyesinin yarısını ekler. Büyülü tuzakları çözebilir."),
        ("Evasion (Ex)", 2, "Reflex atışında başarılı olursa alan etkilerinden sıfır hasar alır."),
        ("Rogue Talents (Ex)", 2, "2. seviyeden itibaren her 2 seviyede bir özel Hırsız Yeteneği (Bleeding Attack, Fast Stealth, Opportunist vb.) kazanır."),
        ("Uncanny Dodge (Ex)", 4, "Hazırlıksız yakalansa dahi Dex bonusunu AC'de korur.")
    ],
    "Sorcerer": [
        ("Bloodline (Ex/Su)", 1, "Sorcerer bir Soy Hattı (Draconic, Arcane, Abyssal, Celestial, Fey vb.) seçer. Özel büyüler, güçler ve bonus featler kazanır."),
        ("Eschew Materials", 1, "Maliyetsiz büyü bileşenlerine ihtiyaç duymadan büyü okur."),
        ("Spontaneous Spellcasting", 1, "Büyülerini ezberlemeden anlık olarak okur.")
    ],
    "Wizard": [
        ("Arcane Bond (Ex/Su)", 1, "Wizard bir Büyülü Nesne (Ring, Wand, Staff) veya Büyülü Tanıdık (Familiar) seçer."),
        ("Arcane School", 1, "Bir Büyü Okulunda uzmanlaşır. Özel okul güçleri ve ekstra büyü slotları kazanır."),
        ("Spellbook", 1, "Büyülerini kadim büyü kitabından ezberleyerek hazırlar.")
    ],
    "Alchemist": [
        ("Alchemy (Su)", 1, "Simyasal iksir ve ekstraktlar hazırlar."),
        ("Bombs (Su)", 1, "Patlayıcı yangın/asit bombaları fırlatır (1d6 + Int mod, her 2 seviyede +1d6)."),
        ("Mutagen (Su)", 1, "İçtiğinde fiziksel statını (Str/Dex/Con) +4 artıran ama zihinsel statı -2 düşüren simyasal iksir demler."),
        ("Discoveries (Su)", 2, "2. seviyeden itibaren bombalarını ve mutajenlerini özelleştiren simya keşifleri yapar (Infusion, Explosive Bomb, Wings vb.).")
    ],
    "Witch": [
        ("Hexes (Su)", 1, "Sınırsız sayıda kullanabildiği mistik lanet ve lütuflar saçar (Evil Eye, Slumber, Healing, Misfortune, Cackle vb.)."),
        ("Witch's Familiar", 1, "Büyülerini cadı tanıdığı (Familiar) aracılığıyla saklar ve öğrenir."),
        ("Patron Spells", 2, "Seçtiği Gizemli Koruyucudan ekstra tematik büyüler kazanır.")
    ],
    "Magus": [
        ("Spell Combat (Ex)", 1, "Tek turda bir elinde kılıçla saldırırken diğer eliyle büyü okuyabilir."),
        ("Spellstrike (Su)", 1, "Okuduğu dokunuş büyüsünü silahının ucuyla düşmana iletir, hem silah hem büyü hasarı verir."),
        ("Arcane Pool (Su)", 1, "Puanlarını harcayarak silahına geçici elemental büyüler (+1 Flaming, Keen vb.) ekler."),
        ("Magus Arcana (Su)", 3, "Özel kılıç-büyü kombinasyon yetenekleri kazanır.")
    ],
    "Gunslinger": [
        ("Grit (Ex)", 1, "Kritik vuruşlar ve ölümcül atışlarla tazelenen Cesaret puanları kazanır."),
        ("Deeds (Ex)", 1, "Grit puanlarını harcayarak hedefin silahını düşürme, durdurulamaz atışlar yapma ve sektirme atışları gerçekleştirir."),
        ("Gunsmith (Ex)", 1, "Kendi ateşli silahını tamir eder ve mermilerini demler.")
    ],
    "Inquisitor": [
        ("Judgments (Su)", 1, "Savaş anında inancının gücüyle AC, Saldırı, Hasar veya Kurtarma atışlarına anlık bonuslar seçer."),
        ("Monster Lore (Ex)", 1, "Yaratıkların zayıf noktalarını teşhis etmede Wisdom modunu da ekler."),
        ("Teamwork Feats", 3, "Müttefikleri sahip olmasa dahi İşbirliği Yeteneklerinin bonuslarını tek başına tetikleyebilir.")
    ],
    "Oracle": [
        ("Oracle's Curse (EX)", 1, "Karakter fiziksel veya zihinsel bir lanet taşır (Clouded Vision, Deaf, Lame vb.) ancak bu lanet ona benzersiz güçler verir."),
        ("Mystery (SU)", 1, "İlahi bir Gizem (Battle, Life, Flame, Time vb.) seçerek vahiy güçleri (Revelations) kazanır.")
    ]
};

def seed_class_features():
    db_path = Path("data/characters.db")
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path.resolve()}")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    inserted_cf = 0
    updated_classes = 0

    for cls_name, feature_list in PF1E_CLASS_FEATURES.items():
        detailed_features_map = []

        for feat_tuple in feature_list:
            feat_name, req_level, feat_desc = feat_tuple
            
            # Check if class_feature entity exists in DB
            cursor.execute(
                "SELECT id FROM entities WHERE sistem = 'pathfinder1e' AND kategori = 'class_feature' AND isim = ?",
                (feat_name,)
            )
            row = cursor.fetchone()

            sv_data = {
                "class_name": cls_name,
                "level_acquired": req_level,
                "description": feat_desc
            }

            if not row:
                cursor.execute(
                    "INSERT INTO entities (sistem, kategori, isim, aciklama, sistem_verisi) VALUES (?, ?, ?, ?, ?)",
                    ("pathfinder1e", "class_feature", feat_name, feat_desc, json.dumps(sv_data, ensure_ascii=False))
                )
                inserted_cf += 1
            else:
                cursor.execute(
                    "UPDATE entities SET aciklama = ?, sistem_verisi = ? WHERE id = ?",
                    (feat_desc, json.dumps(sv_data, ensure_ascii=False), row[0])
                )

            detailed_features_map.append({
                "name": feat_name,
                "level": req_level,
                "description": feat_desc
            })

        # Update class entity's sistem_verisi with features_detailed
        cursor.execute(
            "SELECT id, sistem_verisi FROM entities WHERE sistem = 'pathfinder1e' AND kategori IN ('class', 'archetype') AND isim LIKE ?",
            (f"%{cls_name}%",)
        )
        class_rows = cursor.fetchall()
        for c_row in class_rows:
            c_id, c_sv_raw = c_row[0], c_row[1]
            try:
                c_payload = json.loads(c_sv_raw) if c_sv_raw else {}
            except Exception:
                c_payload = {}

            if isinstance(c_payload, dict):
                c_payload["features_detailed"] = detailed_features_map
                cursor.execute(
                    "UPDATE entities SET sistem_verisi = ? WHERE id = ?",
                    (json.dumps(c_payload, ensure_ascii=False), c_id)
                )
                updated_classes += 1

    conn.commit()
    conn.close()

    print("==========================================")
    print("Class Features Seeding Complete!")
    print(f"Inserted/Updated Class Feature Entities: {inserted_cf}")
    print(f"Updated Class Records with Detailed Features: {updated_classes}")
    print("==========================================")

if __name__ == "__main__":
    seed_class_features()
