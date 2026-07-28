import sqlite3
import json
from pathlib import Path

# Complete Pathfinder 1st Edition Playable Class Descriptions (Core, Base, Hybrid, Occult, Alternate)
PF1E_CLASS_DESCRIPTIONS = {
    "Barbarian": (
        "Vahşi ve durdurulamaz bir savaşçı olan Barbarian, muharebe meydanında öfkesini (Rage) serbest bırakarak "
        "fiziksel gücünü, dayanıklılığını ve savaş reflekslerini zirveye taşır. Ağır zırhlara ihtiyaç duymadan "
        "korkusuzca ön saflarda çarpışır, yüksek Can Zarı (d12) ve Vahşet Yetenekleri (Rage Powers) ile düşmanlarını yok eder."
    ),
    "Bard": (
        "Büyü, müzik ve savaş sanatlarını harmanlayan büyüleyici bir performans ustası. Bard, Ozan İlhamı (Bardic Performance) "
        "sayesinde müttefiklerine ilham verir, düşmanların zihnini bulandırır. Büyülü ezgileri, geniş beceri havuzu (Skill Ranks) "
        "ve gizemli bilgeliği (Bardic Knowledge) ile maceracı grubunun vazgeçilmez lideridir."
    ),
    "Cleric": (
        "Tanrıların ve ilahi güçlerin sadık temsilcisi. Cleric, güçlü ilahi büyüler (Divine Spells) okuyarak müttefiklerini iyileştirir, "
        "kutsal alanlar (Domains) yaratır ve zombi/tayf gibi doğaüstü yaratıkları Kutsal Enerji (Channel Energy) ile defeder. "
        "Ağır zırh kuşanıp yakın dövüşte savaşabileceği gibi saf ilahi büyücü olarak da rol alabilir."
    ),
    "Druid": (
        "Doğanın kadim koruyucusu ve vahşi yaşamın ustası. Druid, hayvan formlarına dönüşebilme yeteneğine (Wild Shape) sahiptir, "
        "elementleri kontrol eder ve yanında sadık bir Yoldaş Hayvan (Animal Companion) ile savaşır. Doğa ilahi büyüleri ile "
        "fırtınalar koparır, müttefiklerini iyileştirir ve doğanın dengesini korur."
    ),
    "Fighter": (
        "Silahların, zırhların ve stratejik savaş sanatının eşsiz ustası. Fighter, diğer tüm sınıflardan daha fazla Savaş Yeteneğine "
        "(Bonus Combat Feats) sahiptir. Zırh Eğitimi (Armor Training) ve Silah Eğitimi (Weapon Training) sayesinde seçtiği silahta "
        "mükemmelleşir ve muharebe alanında durdurulamaz bir disiplin sergiler."
    ),
    "Monk": (
        "Zihin ve beden disiplinini en üst seviyeye taşımış silahsız dövüş ustası. Monk, silah kuşanmadan (Unarmed Strike) "
        "yıkıcı darbeler indirir, Ki enerjisini kullanarak süper insan refleksleri ve hareket kabiliyeti sergiler. Kesintisiz "
        "darbe kombinasyonları (Flurry of Blows) ve zırhsız savunmasıyla bilgelik ve gücü birleştirir."
    ),
    "Paladin": (
        "Adalet, onur ve doğruluğun şövalyesi. Paladin, kötülükle savaşmak için ilahi güçle donatılmıştır. Kötülüğü Cezalandırma "
        "(Smite Evil) ile düşmanlarına ilahi gazap yağdırır, Ellerin Dokunuşu (Lay on Hands) ile anında iyileşme sağlar ve "
        "kutsal binek veya silah bağıyla iyiliğin sarsılmaz kalesi olarak hizmet eder."
    ),
    "Ranger": (
        "Vahşi doğanın uzlaşmaz avcısı ve iz sürücüsü. Ranger, Seçilmiş Düşman (Favored Enemy) ve Seçilmiş Arazi (Favored Terrain) "
        "uzmanlıkları sayesinde belirli yaratık türlerine ve coğrafyalara karşı üstün avantaj kazanır. Çift silah kullanımı veya "
        "okçulukta uzmanlaşarak doğa büyüleriyle avını amansızca takip eder."
    ),
    "Rogue": (
        "Gölgelerin, kilitlerin ve kritik darbelerin ustası. Rogue, düşmanlarının zayıf noktalarını saptayarak Sinsi Saldırı "
        "(Sneak Attack) ile muazzam hasar verir. Yüksek beceri puanları, tuzak saptama (Trapfinding) ve Hırsızlık Yetenekleri "
        "(Rogue Talents) ile her türlü tehlikeli kilit ve mekanizmayı kolayca çözer."
    ),
    "Sorcerer": (
        "Büyüsel gücü doğuştan kanında taşıyan gizemli büyücü. Sorcerer, büyülerini ezberlemeye ihtiyaç duymadan içgüdüsel olarak "
        "okur. Soy Hattı (Bloodline) gücü (Ejderha kanı, İblis kanı, Fey kanı vb.) sayesinde benzersiz doğaüstü yetenekler ve "
        "büyü çeşitliliği kazanır."
    ),
    "Wizard": (
        "Yıllarca süren teorik araştırma ve kadim kitapların incelemesiyle büyü sanatında ustalaşmış zihin. Wizard, Büyü Kitabı "
        "(Spellbook) sayesinde devasa bir büyü yelpazesine erişebilir. Seçtiği Büyü Okulu (Arcane School) uzmanlığı ile evrenin "
        "fiziksel ve zihinsel kurallarını büker."
    ),
    "Alchemist": (
        "Kimya, simya ve gizemli iksirlerin dahi yaratıcısı. Alchemist, patlayıcı Simya Bombaları (Bombs) fırlatır, fiziksel "
        "özelliklerini devasa seviyelere çıkaran Mutajenler (Mutagens) demler ve arkadaşları için özel simyasal ekstraktlar (Extracts) hazırlar."
    ),
    "Cavalier": (
        "Savaş alanında binek üstünde fırtınalar estiren gururlu şövalye. Cavalier, seçtiği Şövalyelik Yemini (Order) ile grubuna "
        "taktiksel bonuslar (Tactician) sağlar ve Meydan Okuma (Challenge) yeteneğiyle tek bir hedefi yok etmeye odaklanır."
    ),
    "Gunslinger": (
        "Ateşli silahların ve barutun tehlikeli ustası. Gunslinger, Cesaret (Grit) puanlarını harcayarak imkansız atışlar (Deeds) "
        "gerçekleştirir, mermileriyle zırhları delip geçer ve menzilli savaşta amansız bir tehlike oluşturur."
    ),
    "Inquisitor": (
        "İnancın acımasız ve kararlı yargıcı. Inquisitor, Yargılama (Judgment) yeteneği ile savaşın gidişatına göre statlarını "
        "anlık olarak uyarlar. İlahi büyüler, İşbirliği Yetenekleri (Teamwork Feats) ve tespit büyüleri ile inanç düşmanlarını avlar."
    ),
    "Magus": (
        "Kılıç ve büyüyü tek bir beden ve hamlede birleştiren dövüşçü büyücü. Magus, Büyü Saldırısı (Spellstrike) ile büyüsünü "
        "silahının ucuyla düşmana iletir, Büyü Savaşçılığı (Spell Combat) ile tek turda hem kılıç sallar hem büyü okur."
    ),
    "Oracle": (
        "Tanrılardan doğrudan gizemli vahiyler alan ama bu vahiylerin bedelini bir Lanet (Oracle's Curse) ile ödeyen ilahi büyücü. "
        "Gizem (Mystery) yetenekleri sayesinde benzersiz doğaüstü vahiy güçlerine (Revelations) kavuşur."
    ),
    "Summoner": (
        "Boyutlar arası geçitler açarak kendi tasarladığı Efsanevi Yaratığı (Eidolon) çağıran büyücü. Eidolon'unu kalkanlar, kanatlar, "
        "pençeler ve sihirli organlarla özelleştirebilir ve savaşta onunla omuz omuza çarpışır."
    ),
    "Witch": (
        "Gizemli bir koruyucu (Patron) ile anlaşma yapmış, Büyülü Tanıdığı (Familiars) aracılığıyla büyü okuyan mistik güç. "
        "Witch, Büyücülük Niyetleri (Hexes) ile düşmanlarını lanetler, uyutur, zayıflatır ve zihinlerini felç eder."
    ),
    "Arcanist": (
        "Wizard'ın akademik bilgisi ile Sorcerer'ın esnekliğini birleştiren hibrit sınıf. Arcane Reservoir puanlarını harcayarak "
        "büyülerinin menzilini, zorluk derecesini (DC) ve etkisini anlık olarak güçlendiren Arcane Exploits yeteneklerine sahiptir."
    ),
    "Bloodrager": (
        "Barbarian'ın yıkıcı öfkesi ile Sorcerer'ın kan bağını birleştiren dehşet verici savaşçı. Kan Öfkesine (Bloodrage) girdiği "
        "anda vücudundan büyülü auralar saçar ve öfke halindeyken anlık büyüler okuyabilir."
    ),
    "Brawler": (
        "Zırhsız, silahsız ve dövüş kulübü disiplinine sahip göğüs göğüse savaşçı. Dövüş Esnekliği (Martial Flexibility) sayesinde "
        "savaşın tam ortasında ihtiyaç duyduğu Combat Feat'i anında zihnine getirip kullanabilir."
    ),
    "Hunter": (
        "Ranger ile Druid'in doğa bağını derinleştiren hibrit sınıf. Hayvan yoldaşıyla telepatik ve taktiksel bağ kurarak "
        "Hayvan Odakları (Animal Focus) ile kendine ve hayvanına anlık stat bonusları kazandırır."
    ),
    "Investigator": (
        "Rogue'un gizliliği ve Alchemist'in simya bilgisini birleştiren usta dedektif. İlham (Inspiration) puanlarını harcayarak "
        "tüm beceri zarlarına, saldırılarına ve savunmalarına ek zarlar (d6) ekler."
    ),
    "Slayer": (
        "Rogue'un Sinsi Saldırısı ile Fighter'ın silah disiplinini birleştiren profesyonel suikastçı. Hedeflenen Av (Studied Target) "
        "yetenekleriyle kurbanını inceleyerek ona karşı kaçınılmaz darbeyi indirir."
    ),
    "Swashbuckler": (
        "Zarafet, hız ve hafif silahların (Rapier vb.) gösterişli ustası. Panache puanlarını kullanarak düşman saldırılarını "
        "Savuşturur ve Karşı Saldırı yapar (Parry and Riposte), çevikliğiyle savaş meydanında şov yapar."
    ),
    "Warpriest": (
        "Cleric ile Fighter'ın gücünü birleştiren kutsal savaşçı. Kutsal Silah (Sacred Weapon) ve Kutsal Zırh yetenekleriyle "
        "silahını anında büyüleyebilir, Kutsal Lütuf (Fervor) ile tek eylemde kendini iyileştirip büyü okuyabilir."
    ),
    "Kineticist": (
        "Elementlerin (Ateş, Su, Toprak, Hava, Aether) saf enerjisini kendi bedeninden geçiren psişik doğa gücü. Kinetik Patlama "
        "(Kinetic Blast) fırlatarak sınırsız element hasarı verir ve Beden Yakması (Burn) ile kendini riske atarak gücünü katlar."
    ),
    "Occultist": (
        "Kadim nesneler ve kalıntılar (Implements) aracılığıyla psişik büyüler okuyan arkeolog büyücü. Nesnelere zihinsel enerji "
        "(Mental Focus) yükleyerek kalkanlar, büyülü auralar ve doğaüstü güçler elde eder."
    ),
    "Psychic": (
        "Zihnin saf gücüyle gerçekliği büken saf psişik büyücü. Düşünce ve His bileşenleri ile sessiz ve hareketsiz büyüler okur, "
        "Zihin Mimarisi (Phrenic Amplifications) ile büyülerinin mekaniklerini değiştirir."
    ),
    "Vigilante": (
        "Çift kimlikli (Sosyal Kimlik ve Kahraman/Suikastçı Kimliği) gizemli savaşçı. Şehirde saygın bir soylu gibi yaşarken "
        "geceleri Maskeli Kahraman kimliğine bürünerek Sosyal ve Savaş Yetenekleri (Vigilante Talents) sergiler."
    ),
    "Ninja": (
        "Gölgelerin, gizli suikastların ve Ki enerjisinin doğulu ustası. İllüzyonlar yaratır, görünmez olur ve sinsi darbelerle "
        "düşmanlarını hissettirmeden ortadan kaldırır."
    ),
    "Samurai": (
        "Onur yeminine bağlı, atlı ve kılıç ustası doğulu savaşçı. Kararlılık (Resolve) yeteneği sayesinde ölümcül darbelerden "
        "ayakta kalır ve hedeflerine karşı amansız meydan okumalar gerçekleştirir."
    ),
    "Skald": (
        "Bard'ın müziksel ilhamı ile Barbarian'ın vahşi öfkesini birleştiren kuzeyli savaşçı. İlham Verici Öfke (Inspired Rage) "
        "şarkısıyla tüm müttefiklerini aynı anda öfke moduna geçirerek onlara Barbarian yetenekleri kazandırır."
    )
}

def enrich_classes():
    db_path = Path("data/characters.db")
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path.resolve()}")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    updated_count = 0
    skipped_count = 0

    cursor.execute(
        "SELECT id, isim, aciklama, sistem_verisi FROM entities WHERE sistem = 'pathfinder1e' AND kategori IN ('class', 'archetype')"
    )
    rows = cursor.fetchall()
    print(f"Total PF1e class/archetype rows in DB: {len(rows)}")

    for row in rows:
        entity_id, name, current_desc, sv_raw = row[0], row[1], row[2] or "", row[3]
        
        # Check matching class description
        matched_desc = None
        for cls_name, cls_desc in PF1E_CLASS_DESCRIPTIONS.items():
            if cls_name.lower() in name.lower():
                matched_desc = cls_desc
                break

        # Decide if description needs replacement (if empty, starts with Contents, Skill:, or contains HTML/Contents)
        needs_fix = (
            not current_desc or 
            current_desc.startswith("Contents") or 
            current_desc.startswith("Skill:") or 
            "Contents" in current_desc or 
            len(current_desc) < 30
        )

        if matched_desc and needs_fix:
            try:
                payload = json.loads(sv_raw) if (sv_raw and sv_raw != "null") else {}
            except Exception:
                payload = {}

            if isinstance(payload, dict):
                payload["description"] = matched_desc

            cursor.execute(
                "UPDATE entities SET aciklama = ?, sistem_verisi = ? WHERE id = ?",
                (matched_desc, json.dumps(payload, ensure_ascii=False), entity_id)
            )
            updated_count += 1
            print(f"[UPDATED] {name}: {matched_desc[:70]}...")
        else:
            skipped_count += 1

    conn.commit()
    conn.close()
    print("\n==========================================")
    print(f"Enrichment Complete!")
    print(f"Successfully Updated Classes: {updated_count}")
    print(f"Unchanged/Existing Valid Classes: {skipped_count}")
    print("==========================================")

if __name__ == "__main__":
    enrich_classes()
