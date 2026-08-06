"""
Diyargezen Character State Manager & Rules Compendium Interface

Architecture & Data Access Layer:
---------------------------------
This module serves as the primary data query broker and active state coordinator for Pathfinder 1e entities.
It acts as the bridge between SQLite persistent entity stores (`data/characters.db` / `entities`)
and the real-time rule calculation engine.

Design Patterns & Capabilities:
1. Unified Compendium Access: Queries races, classes, subraces, feats, traits, items, and spells with high performance.
2. Dynamic Categorization: Categorizes feats into Combat, Teamwork, Metamagic, Racial, General, and Class Features.
3. Resilience & Fallback Handling: Safely handles corrupted JSON payloads in entity storage without halting application execution.
4. Active Character Lifecycle: Maintains the state of active characters during session creation and level-up wizard steps.
"""

import sqlite3
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from db.entity_store import list_entities
from models.entity import DiyargezenEntity

class CharacterManager:
    """Manages active character data, rules engine queries, and real-time calculation updates."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path).resolve()
        self.active_character: Dict[str, Any] = {}

    def set_active_character(self, character: Dict[str, Any]) -> None:
        self.active_character = character

    def get_entities_by_category(self, system: str, category: str) -> List[DiyargezenEntity]:
        """Fetch available entities (races, classes, feats, items, skills) from SQLite database."""
        sys_norm = system.lower().replace("_", "").replace("-", "")
        return list_entities(self.db_path, sys_norm, category)

    def get_subraces_for_race(self, system: str, parent_race: str) -> List[DiyargezenEntity]:
        """Fetch subraces/heritages for a given parent race."""
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori IN ('race', 'feat') "
                "AND json_extract(sistem_verisi, '$.parent_race') = ? ",
                (sys_norm, parent_race)
            )
            for row in cursor.fetchall():
                try:
                    payload = json.loads(row[4]) if row[4] else {}
                    results.append(DiyargezenEntity(
                        isim=row[0], sistem=row[1], kategori=row[2],
                        aciklama=row[3] or "", sistem_verisi=payload
                    ))
                except Exception:
                    continue
            conn.close()
        except Exception:
            pass
        return results

    def get_top_level_races(self, system: str) -> List[DiyargezenEntity]:
        """Fetch all playable race entities from the SQLite database."""
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        CREATURE_TYPE_PREFIXES = ("Race: ", "race: ")

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute(
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori = 'race' "
                "AND aciklama NOT LIKE 'Contents%' "
                "AND isim NOT LIKE 'Race:%' "
                "ORDER BY isim COLLATE NOCASE",
                (sys_norm,)
            )
            seen_names = set()
            for row in cursor.fetchall():
                name: str = row[0]
                # Skip creature-type pseudo-races (e.g. 'Race: Aberration') and plurals (e.g. 'Humans')
                if any(name.startswith(p) for p in CREATURE_TYPE_PREFIXES):
                    continue
                if name.endswith('s') and name[:-1] in seen_names:
                    continue
                seen_names.add(name)

                try:
                    payload = json.loads(row[4]) if row[4] else {}
                    results.append(DiyargezenEntity(
                        isim=row[0], sistem=row[1], kategori=row[2],
                        aciklama=row[3] or "", sistem_verisi=payload
                    ))
                except Exception:
                    continue
            conn.close()
        except Exception as e:
            pass

        return results

    @classmethod
    def _parse_entity_category(cls, name: str, payload: dict) -> str:
        """Derive feat category from featType field, tags, and name patterns.

        Priority:
          1. system.featType / data.featType  (classFeat → ClassFeature, misc → General)
          2. Flattened tags list                (Combat, Teamwork, Metamagic, Mythic, Racial…)
          3. Name keyword heuristics
        """
        inner = payload.get('system', payload.get('data', {}))
        if not isinstance(inner, dict):
            inner = {}

        feat_type = inner.get('featType', payload.get('feat_type', ''))

        if feat_type == 'classFeat':
            return 'ClassFeature'
        if feat_type == 'misc':
            return 'General'

        # Flatten nested tags e.g. [['PFS'], ['Combat']]
        tags_raw = inner.get('tags', payload.get('tags', []))
        tag_strs = []
        for t in tags_raw:
            if isinstance(t, list):
                tag_strs.extend([str(x).strip().lower() for x in t])
            else:
                tag_strs.append(str(t).strip().lower())

        n_lower = name.lower()
        full_str = ' '.join(tag_strs) + ' ' + n_lower

        if 'combat' in tag_strs or 'combat' in n_lower: return 'Combat'
        if 'teamwork' in tag_strs or 'teamwork' in n_lower: return 'Teamwork'
        if 'metamagic' in tag_strs or 'metamagic' in n_lower: return 'Metamagic'
        if 'item creation' in full_str or 'itemcreation' in full_str: return 'Item Creation'
        if 'mythic' in tag_strs or 'mythic' in n_lower: return 'Mythic'
        if 'racial' in tag_strs or 'race' in tag_strs or 'racial' in n_lower: return 'Racial'
        if 'regional' in tag_strs or 'region' in tag_strs or 'regional' in n_lower: return 'Regional'
        if 'campaign' in tag_strs or 'campaign' in n_lower: return 'Campaign'
        if 'performance' in tag_strs or 'performance' in n_lower: return 'Performance'
        if 'style' in tag_strs or 'style' in n_lower: return 'Style'
        if 'critical' in tag_strs or 'critical' in n_lower: return 'Critical'
        if 'grit' in tag_strs or 'grit' in n_lower: return 'Grit'
        if 'panache' in tag_strs or 'panache' in n_lower: return 'Panache'
        if 'social' in tag_strs or 'social' in full_str: return 'Social'
        if 'faith' in tag_strs or 'religion' in tag_strs or 'faith' in full_str or 'religion' in full_str: return 'Faith'
        if 'magic' in tag_strs or 'spell' in tag_strs or 'magic' in full_str: return 'Magic'
        if 'equipment' in tag_strs or 'gear' in tag_strs: return 'Equipment'
        return 'General'

    def get_traits(self, system: str, query: str = "", category: str = "") -> List[DiyargezenEntity]:
        """Fetch character traits, filtered by optional search query and/or trait category."""
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            base_sql = (
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori = 'trait' "
            )
            params = [sys_norm]

            if query:
                base_sql += "AND (isim LIKE ? OR aciklama LIKE ?) "
                params.extend([f"%{query}%", f"%{query}%"])

            base_sql += "ORDER BY isim COLLATE NOCASE ASC LIMIT 1000"

            cursor.execute(base_sql, params)
            for row in cursor.fetchall():
                try:
                    payload = json.loads(row[4]) if row[4] else {}
                    t_cat = payload.get('trait_category') or self._parse_entity_category(row[0], payload)
                    payload['trait_category'] = t_cat

                    if category and category != 'All' and t_cat.lower() != category.lower():
                        continue

                    results.append(DiyargezenEntity(
                        isim=row[0], sistem=row[1], kategori=row[2],
                        aciklama=row[3] or "", sistem_verisi=payload
                    ))
                except Exception:
                    continue
            conn.close()
        except Exception:
            pass
        return results

    def get_feats(self, system: str, query: str = "", category: str = "") -> List[DiyargezenEntity]:
        """Retrieve feats filtered by search query and/or category."""
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            sql = (
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori IN ('feat', 'advantage') "
                "AND isim NOT LIKE '#%' "
                "AND isim NOT LIKE '[%' "
                "AND isim NOT LIKE '*%' "
                "AND length(isim) > 2 "
            )
            params: list = [sys_norm]

            if query:
                sql += "AND (isim LIKE ? OR aciklama LIKE ?) "
                params.extend([f"%{query}%", f"%{query}%"])

            sql += "ORDER BY isim COLLATE NOCASE ASC LIMIT 1500"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                try:
                    feat_name = row[0]
                    payload = json.loads(row[4]) if row[4] else {}
                    feat_cat = payload.get('feat_category') or self._parse_entity_category(feat_name, payload)
                    payload["feat_category"] = feat_cat

                    if category and category != 'All' and feat_cat.lower() != category.lower():
                        continue

                    results.append(DiyargezenEntity(
                        isim=feat_name, sistem=row[1], kategori=row[2],
                        aciklama=row[3] or "", sistem_verisi=payload
                    ))
                except Exception:
                    continue
        except Exception:
            pass
        return results

    def get_spells(
        self,
        system: str,
        query: str = "",
        level: Optional[int] = None,
        caster_class: str = "",
        school: str = ""
    ) -> List[DiyargezenEntity]:
        """Fetch spells filtered by query, spell level, caster class, and magic school."""
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            sql = (
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori = 'spell' "
            )
            params: list = [sys_norm]

            if query:
                sql += "AND isim LIKE ? "
                params.append(f"%{query}%")

            sql += "ORDER BY isim COLLATE NOCASE ASC LIMIT 300"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                try:
                    payload = json.loads(row[4]) if row[4] else {}
                    spell_lvl = payload.get("level")
                    spell_school = str(payload.get("school", "")).lower()
                    levels_by_class = payload.get("levels_by_class", {})

                    # Level filter
                    if level is not None:
                        matched = False
                        if isinstance(levels_by_class, dict) and caster_class:
                            for cname, clvl in levels_by_class.items():
                                if cname.lower() == caster_class.lower() and clvl == level:
                                    matched = True
                                    break
                        if not matched and spell_lvl != level:
                            continue

                    # Class filter
                    if caster_class and isinstance(levels_by_class, dict) and levels_by_class:
                        if not any(cname.lower() == caster_class.lower() for cname in levels_by_class.keys()):
                            continue

                    # School filter
                    if school and school.lower() not in spell_school:
                        continue

                    results.append(DiyargezenEntity(
                        isim=row[0], sistem=row[1], kategori=row[2],
                        aciklama=row[3] or "", sistem_verisi=payload
                    ))
                except Exception:
                    continue

            # Fallback/supplement from dedicated spells table if needed
            if len(results) < 50:
                seen_names = {e.isim.lower() for e in results}
                sp_sql = "SELECT isim, sistem, seviye, siniflar, aciklama FROM spells WHERE (sistem = ? OR sistem = 'pf1e')"
                sp_params = [sys_norm]
                if query:
                    sp_sql += " AND isim LIKE ?"
                    sp_params.append(f"%{query}%")
                if level is not None:
                    sp_sql += " AND seviye = ?"
                    sp_params.append(level)
                sp_sql += " ORDER BY isim COLLATE NOCASE ASC LIMIT 300"

                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                cursor.execute(sp_sql, sp_params)
                for r_name, r_sys, r_lvl, r_classes, r_desc in cursor.fetchall():
                    if r_name.lower() not in seen_names:
                        seen_names.add(r_name.lower())
                        try:
                            classes_dict = json.loads(r_classes) if r_classes and r_classes.startswith("{") else {}
                        except Exception:
                            classes_dict = {}
                        
                        if caster_class and classes_dict and not any(c.lower() == caster_class.lower() for c in classes_dict.keys()):
                            continue

                        results.append(DiyargezenEntity(
                            isim=r_name,
                            sistem=r_sys,
                            kategori="spell",
                            aciklama=r_desc or "",
                            sistem_verisi={"level": r_lvl, "levels_by_class": classes_dict}
                        ))
                conn.close()
        except Exception:
            pass
        return results

    def get_class_features(self, system: str, class_name: str = "", query: str = "") -> List[DiyargezenEntity]:
        """Return class-specific talents and features (Rage Powers, Rogue Talents, Discoveries, Hexes, Arcana, etc.)."""
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        
        CLASS_KEYWORDS = {
            "barbarian": ["Rage Power", "Totem"],
            "rogue": ["Rogue Talent", "Advanced Rogue Talent"],
            "ninja": ["Ninja Trick", "Master Trick", "Rogue Talent"],
            "alchemist": ["Discovery", "Alchemist Discovery", "Grand Discovery"],
            "witch": ["Hex", "Witch Hex", "Major Hex", "Grand Hex"],
            "magus": ["Magus Arcana", "Arcana"],
            "arcanist": ["Exploit", "Arcanist Exploit", "Greater Exploit"],
            "slayer": ["Slayer Talent", "Rogue Talent"],
            "oracle": ["Revelation", "Mystery"],
            "cleric": ["Domain Power", "Domain"],
            "paladin": ["Mercy", "Paladin Mercy"],
            "bloodrager": ["Bloodline Power", "Bloodline"],
            "sorcerer": ["Bloodline Power", "Bloodline"],
            "cavalier": ["Order", "Challenge"],
            "inquisitor": ["Inquisition", "Judgment"],
            "investigator": ["Investigator Talent"],
            "shaman": ["Hex", "Shaman Hex", "Spirit"],
            "vigilante": ["Vigilante Talent", "Social Talent"]
        }
        
        c_lower = class_name.lower().strip()
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            sql = "SELECT isim, sistem, kategori, aciklama, sistem_verisi FROM entities WHERE sistem = ? AND kategori = 'class_feature'"
            params = [sys_norm]

            if c_lower:
                kws = CLASS_KEYWORDS.get(c_lower, [class_name])
                kw_clauses = " OR ".join(["isim LIKE ? OR aciklama LIKE ?" for _ in kws])
                sql += f" AND ({kw_clauses})"
                for kw in kws:
                    params.extend([f"%{kw}%", f"%{kw}%"])

            if query:
                sql += " AND (isim LIKE ? OR aciklama LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])

            sql += " ORDER BY isim COLLATE NOCASE LIMIT 500"
            
            cursor.execute(sql, tuple(params))
            for row in cursor.fetchall():
                name: str = row[0]
                # Filter out any non-feature rule index entries if any
                if name.startswith("(") or name.startswith("*") or name.startswith("-") or name[0].isdigit():
                    continue
                try:
                    payload = json.loads(row[4]) if row[4] else {}
                    results.append(DiyargezenEntity(
                        isim=row[0], sistem=row[1], kategori="class_feature",
                        aciklama=row[3] or "", sistem_verisi=payload
                    ))
                except Exception:
                    continue
            conn.close()
        except Exception:
            pass

        # Fallback to general feat search if class_feature count is empty (for legacy DBs without re-indexing)
        if not results:
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                if c_lower:
                    kws = CLASS_KEYWORDS.get(c_lower, [class_name])
                else:
                    kws = ["Rage Power", "Rogue Talent", "Discovery", "Hex", "Arcana", "Exploit", "Revelation", "Mercy", "Bloodline", "Domain", "Inquisition", "Trick"]
                
                kw_clauses = " OR ".join(["isim LIKE ?" for _ in kws])
                params = [sys_norm]
                for kw in kws:
                    params.append(f"%{kw}%")
                sql = f"SELECT isim, sistem, kategori, aciklama, sistem_verisi FROM entities WHERE sistem = ? AND kategori = 'feat' AND ({kw_clauses})"
                if query:
                    sql += " AND (isim LIKE ? OR aciklama LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%"])
                sql += " ORDER BY isim COLLATE NOCASE LIMIT 300"
                cursor.execute(sql, tuple(params))
                for row in cursor.fetchall():
                    name: str = row[0]
                    if name.startswith("(") or name.startswith("*") or name.startswith("-") or name[0].isdigit():
                        continue
                    try:
                        payload = json.loads(row[4]) if row[4] else {}
                        results.append(DiyargezenEntity(
                            isim=row[0], sistem=row[1], kategori="class_feature",
                            aciklama=row[3] or "", sistem_verisi=payload
                        ))
                    except Exception:
                        continue
                conn.close()
            except Exception:
                pass

        return results



    def search_entities(self, system: str, category: str, query: str) -> List[DiyargezenEntity]:
        """Search database entities using standard LIKE search on name/isim.

        For equipment categories, dirty index/template names are excluded automatically.
        """
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Equipment search: also search companion categories, apply name filter
            if category in ("item", "equipment"):
                cursor.execute(
                    "SELECT isim, sistem, kategori, aciklama, sistem_verisi FROM entities "
                    "WHERE sistem = ? AND kategori IN ('item','equipment') "
                    "AND isim LIKE ? "
                    "AND isim NOT LIKE '(%)%' "   # remove (Index) ... entries
                    "AND isim NOT LIKE '#%' "      # remove #[CF_...] entries
                    "AND isim NOT LIKE '[%' "      # remove [bracket] entries
                    "AND isim NOT LIKE '*%' "      # remove *template entries
                    "ORDER BY isim COLLATE NOCASE LIMIT 200",
                    (sys_norm, f"%{query}%")
                )
            else:
                cursor.execute(
                    "SELECT isim, sistem, kategori, aciklama, sistem_verisi FROM entities "
                    "WHERE sistem = ? AND kategori = ? AND isim LIKE ? "
                    "ORDER BY isim COLLATE NOCASE LIMIT 200",
                    (sys_norm, category, f"%{query}%")
                )
            for r in cursor.fetchall():
                payload = json.loads(r[4]) if r[4] else {}
                results.append(
                    DiyargezenEntity(
                        isim=r[0], sistem=r[1], kategori=r[2], aciklama=r[3] or "", sistem_verisi=payload
                    )
                )
            conn.close()
        except Exception:
            pass
        return results

    # ------------------------------------------------------------------
    # Strict filtered queries
    # ------------------------------------------------------------------

    # PF1e iin oynanabilir sınıflar (Whitelist) — sadece bunlar UI'a gösterilir.
    # Canavar türleri (Outsider, Dragon vb.) ve NPC sınıfları (Adept, Expert vb.)
    # ne kadar sürüm veya suffix farklılığı olursa olsun engellenir.
    # "Unchained" ve "Unchained-equivalent" versiyonlar tercih edilir.
    _PF1E_PLAYABLE_CLASSES = {
        "alchemist", "antipaladin", "arcanist", "barbarian", "bard",
        "bloodrager", "brawler", "cavalier", "cleric", "druid",
        "fighter", "gunslinger", "hunter", "inquisitor", "investigator",
        "kineticist", "magus", "medium", "mesmerist", "monk",
        "ninja", "occultist", "oracle", "paladin", "psychic",
        "ranger", "rogue", "samurai", "shaman", "shifter",
        "skald", "slayer", "sorcerer", "spiritualist", "summoner",
        "swashbuckler", "vigilante", "warpriest", "witch", "wizard",
    }

    _PF1E_CLASS_DESCRIPTIONS = {
        "alchemist": "Simyacılar, iksirler, patlayıcı bombalar ve fiziksel güçlerini artıran iksir karışımları (mutagens) üreten gizemli zanaatkarlardır.",
        "antipaladin": "Antipaladinler, yıkım, kaos ve kötülüğün şampiyonlarıdır. Kutsal düzeni yıkmak ve korku salmak için kara büyü ve ağır silahlar kullanırlar.",
        "arcanist": "Arcanist'ler, büyücü (Wizard) araştırmacılığı ile büyücü soyu (Sorcerer) yeteneklerini birleştiren esnek büyü ustalarıdır.",
        "barbarian": "Barbarlar, savaş alanında kabile öfkesiyle (Rage) coşan, muazzam fiziksel güce ve dayanıklılığa sahip durdurulamaz savaşçılardır.",
        "bard": "Ozanlar, müzik, şiir ve büyü ilmiyle dostlarını ruhlandıran, zihinsel büyüler atan ve çok yönlü becerilere sahip macera ustalarıdır.",
        "bloodrager": "Bloodrager'lar, hatlarındaki ejderha veya fey kanının büyülü gücünü savaş öfkesiyle birleştiren yıkıcı dövüşçülerdir.",
        "brawler": "Brawler'lar, silahsız dövüşte ve yakın dövüş manevralarında ustalaşmış, savaş sırasında hızlıca esnek yetenekler kazanabilen dövüşçülerdir.",
        "cavalier": "Süvariler, sadık binekleri üstünde savaşa liderlik eden, belirli bir şövalyelik yemini (Order) doğrultusunda meydan okuyan soylu savaşçılardır.",
        "cleric": "Rahipler, inandıkları tanrıların ve inanç alanlarının (Domains) ilahi gücünü yönlendiren, iyileştirme ve ilahi koruma sağlayan kutsal büyülü savaşçılardır.",
        "druid": "Druid'ler, doğanın dengesini koruyan, vahşi hayvan biçimlerine (Wild Shape) bürünebilen ve doğa elementlerini yöneten ilahi büyücülerdir.",
        "fighter": "Dövüşçüler, tüm silah ve zırh türlerinde ustalaşmış, en geniş yetenek (Feat) çeşitliliğine sahip savaş alanı stratejistleridir.",
        "gunslinger": "Gunslinger'lar, barut, tabanca ve tüfek teknolojisini cesaret (Grit) ve ölümcül nişancılıkla birleştiren ateşli silah ustalarıdır.",
        "hunter": "Avcılar, doğadaki vahşi hayvan yoldaşlarıyla (Animal Companion) kusursuz bir uyum içinde savaşan esnek doğa koruyucularıdır.",
        "inquisitor": "Engizisyoncular, inançlarının düşmanlarını avlayan, yargı (Judgments) yeteneğiyle dövüşen ve gizli ilimleri ortaya çıkaranı ajanlardır.",
        "investigator": "Dedektifler, simyasal formüller ile keskin zekalarını (Inspiration) birleştirerek zindan çözümlerinde ve kritik vuruşlarda ustalaşmış araştırmacılardır.",
        "kineticist": "Kineticist'ler, vücutlarındaki element enerjilerini (Ateş, Su, Hava, Toprak) saf yıkıcı saldırılara dönüştüren psiyonik ustalarıdır.",
        "magus": "Magus'lar, bir elinde kılıç diğer elinde büyü tutarak kılıç darbelerini ölümcül büyülerle (Spellstrike) birleştiren hibrit savaşçılardır.",
        "medium": "Medyumlar, geçmiş efsanelerin ruhlarını (Spirits) çağırarak ruhların güçlerini kendi bedenlerine yükleyen gizemli aracılardır.",
        "mesmerist": "Mesmerist'ler, hipnoz, zihin oyunları ve illüzyonel büyülerle düşmanlarının zihnini felç eden psikolojik manipülatörlerdir.",
        "monk": "Keşişler, bedenlerini ve zihinlerini kusursuzlaştırarak silah kullanmadan ölümcül Ki enerjisi saldırıları yapan içsel güç ustalarıdır.",
        "ninja": "Ninjalar, gölgelerde saklanan, zehirler ve gizli Ki teknikleriyle düşmanlarını tek hamlede gafil avlayan suikastçılardır.",
        "occultist": "Occultist'ler, antik kalıntılara ve büyülü nesnelere (Focus Implements) güç yükleyerek gizli ilimleri yönlendiren toplayıcılardır.",
        "oracle": "Kahinler, tanrılar tarafından seçilmiş fakat ilahi bir lanetle (Curse) mühürlenmiş, tanrısal gizemleri (Mysteries) doğrudan yönlendiren büyücülerdir.",
        "paladin": "Paladinler, adalet, onur ve doğruluğun kutsal muhafızlarıdır. Kötülüğü cezalandırma (Smite Evil) ve ilahi şifa verme gücüne sahiptirler.",
        "psychic": "Psychic'ler, kelimeler veya hareketler yerine doğrudan zihin gücüyle (Psychic Magic) büyü üreten zihinsel büyü ustalarıdır.",
        "ranger": "Korucular, uzmanlaştığı düşman türlerini (Favored Enemy) ve arazi koşullarını (Favored Terrain) avlayan, okçuluk ve iz sürme ustası savaşçılardır.",
        "rogue": "Haydutlar/Hırsızlar, tuzakları etkisiz hale getiren, gafil avlama saldırılarıyla (Sneak Attack) yüksek hasar veren ve beceri ustası kıvrak karakterlerdir.",
        "samurai": "Samuraylar, sadakat, onur ve Bushido ilkelerine bağlı, binek üstünde veya tek kılıçla ölümcül kararlılıkla (Resolve) savaşan onurlu savaşçılardır.",
        "shaman": "Şamanlar, doğa ruhlarıyla (Spirits) bağlantı kurarak gizemli büyüler ve cadı büyüsü üreten ilahi arancılardır.",
        "shifter": "Shifter'lar, vahşi hayvanların özünü bedenlerine yansıtarak pençeler ve hayvan formlarıyla savaşan dönüşüm ustalarıdır.",
        "skald": "Skald'lar, kuzey efsanelerini şarkılarla ilham ederek tüm grubuna Barbar Öfkesi (Inspired Rage) kazandıran savaşçı ozanlardır.",
        "slayer": "Slayer'lar, Barbar ve Rogue tekniklerini birleştirerek hedefini inceleyen (Studied Target) ve acımasızca avlayan profesyonel avcılardır.",
        "sorcerer": "Büyücüler (Sorcerer), büyü yeteneğini kitaplardan değil, kanlarındaki ejderha veya fey soyundan alan doğuştan yetenekli büyücülerdir.",
        "spiritualist": "Spiritualist'ler, kendilerine sadık hayalet yoldaşlar (Phantom) çağırarak ruhani alem ile maddi alem arasında savaşan mistiklerdir.",
        "summoner": "Çağırıcılar, boyutlar arası özel olarak şekillendirdikleri Eidolon varlıklarıyla bağ kurup onları yanlarında savaştıran büyücülerdir.",
        "swashbuckler": "Silahşörler, rapier ve kılıç dövüşünde zarafet, cesaret (Panache) ve muazzam savuşturma (Parry) teknikleri sergileyen dövüşçülerdir.",
        "vigilante": "Vigilante'ler, gündüzleri halk adamı geceleri ise gizli kimliğiyle (Secret Identity) adalet dağıtan çifte yaşamlı kahramanlardır.",
        "warpriest": "Savaş Rahipleri, katanalarını veya kutsal silahlarını ilahi lütuflarla (Blessings) donatarak savaş alanında en ön safta dövüşen din adamlarıdır.",
        "witch": "Cadılar, patronlarından (Patrons) aldıkları kararsız büyüler ve lanetlerle (Hexes) düşmanlarını zayıflatan gizemli büyü ustalarıdır.",
        "wizard": "Büyücüler (Wizard), yıllarca süren kadim kitap araştırmalarıyla büyünün teorik yapısını çözen ve en geniş büyü defterine sahip büyü üstatlarıdır."
    }

    _DND5E_BLOCK_KEYWORDS = (
        "outsider", "humanoid", "aberration", "construct",
        "dragon", "fey", "undead", "vermin", "race:"
    )

    def get_clean_classes(self, system: str) -> List[DiyargezenEntity]:
        """Return only playable classes and archetypes, stripping NPC/creature-type entries."""
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        MONSTER_BLOCKLIST = {
            "outsider", "dragon", "construct", "animal companion", "vermin",
            "undead", "plant", "fey", "magical beast", "adept", "aristocrat",
            "commoner", "expert", "warrior"
        }
        BAD_CLASS_NAME_SUFFIXES = ("'s", "’s")
        BAD_EXACT_NAMES = {"bloodline", "rage"}

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori IN ('class', 'archetype') "
                "ORDER BY isim COLLATE NOCASE",
                (sys_norm,)
            )
            for row in cursor.fetchall():
                name: str = row[0]
                name_lower = name.lower().strip()

                # Block obvious NPC / monster creature-type classes or fragment entries
                if any(m in name_lower for m in MONSTER_BLOCKLIST):
                    continue
                if any(name_lower.endswith(sfx) for sfx in BAD_CLASS_NAME_SUFFIXES) or name_lower in BAD_EXACT_NAMES:
                    continue
                if "\ufffd" in name_lower or "'s" in name_lower or "’s" in name_lower or "&rsquo;s" in name_lower:
                    continue

                clean_prefix = name_lower.split("(")[0].replace("'s", "").replace("’s", "").strip()

                if "pathfinder" in sys_norm or "pf" in sys_norm:
                    is_base = clean_prefix in self._PF1E_PLAYABLE_CLASSES
                    is_arch = row[2] == 'archetype'
                    if not (is_base or is_arch):
                        continue
                elif "dnd" in sys_norm:
                    if any(kw in name_lower for kw in self._DND5E_BLOCK_KEYWORDS):
                        continue

                try:
                    payload = json.loads(row[4]) if row[4] else {}
                    raw_desc = (row[3] or "").strip()

                    def _is_dummy_desc(d: str) -> bool:
                        if not d:
                            return True
                        plain = re.sub(r'<[^>]*>', '', str(d)).strip()
                        if len(plain) < 30:
                            return True
                        plain_lower = plain.lower()
                        if plain_lower == 'contents' or plain_lower.startswith('contents') or plain_lower.startswith('class skills') or plain_lower.startswith('subpages') or plain_lower.startswith('skill:') or plain_lower.startswith('fatigued:') or plain_lower.startswith('shaken:') or plain_lower.startswith('sbc |'):
                            return True
                        if 'pathfinder products' in plain_lower or 'open gaming store' in plain_lower:
                            return True
                        return False

                    desc = raw_desc
                    if _is_dummy_desc(desc):
                        sv_desc = ""
                        if isinstance(payload, dict):
                            sv_desc = payload.get("description") or ""
                            sv_sys = payload.get("system")
                            if isinstance(sv_sys, dict):
                                sv_desc = sv_desc or sv_sys.get("description") or ""
                            if isinstance(sv_desc, dict):
                                sv_desc = sv_desc.get("value", "")
                        if isinstance(sv_desc, str) and not _is_dummy_desc(sv_desc):
                            desc = sv_desc

                    if _is_dummy_desc(desc):
                        desc = self._PF1E_CLASS_DESCRIPTIONS.get(clean_prefix, f"{name} sınıfı kural detayları ve yetenek şablonu.")

                    results.append(DiyargezenEntity(
                        isim=row[0], sistem=row[1], kategori=row[2],
                        aciklama=desc, sistem_verisi=payload
                    ))
                except Exception:
                    continue
            conn.close()
        except Exception:
            pass
        return results

    def get_clean_equipment(self, system: str, query: str = "") -> List[DiyargezenEntity]:
        """Return only real equipment items, filtering template/index garbage.

        Accepted inner types: weapon, armor, equipment, consumable, gear, shield, loot.
        Rejected:
        - Names starting with (, #, [, *, -, or a digit (index/chapter entries)
        - Items whose inner type is set but not in VALID_TYPES
        - Items whose inner type is empty AND name looks like a text/index entry
        """
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        VALID_TYPES = {"weapon", "armor", "equipment", "consumable", "gear", "shield", "loot"}

        # Characters that mark non-equipment entries at the START of the name
        _BAD_START_CHARS = tuple("(#[*-0123456789")

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            like_q = f"%{query}%" if query else "%"
            cursor.execute(
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori IN ('item','equipment') "
                "AND isim LIKE ? "
                "AND isim NOT LIKE '(%)%' "   # (Index) ...
                "AND isim NOT LIKE '#%' "      # #[CF_...] templates
                "AND isim NOT LIKE '[%' "      # [bracket] entries
                "AND isim NOT LIKE '*%' "      # *template entries
                "AND isim NOT LIKE '- %' "     # - bullet entries
                "AND isim NOT LIKE '--%' "     # -- separator lines
                "AND isim NOT GLOB '[0-9]*' "  # digit-prefixed chapter titles
                "ORDER BY isim COLLATE NOCASE LIMIT 2500",
                (sys_norm, like_q)
            )
            for row in cursor.fetchall():
                try:
                    name: str = row[0]
                    # Extra Python-side guard: reject single-char or very short names
                    if len(name.strip()) < 2:
                        continue
                    # Reject names starting with bad characters (catches edge cases SQL missed)
                    if name.startswith(_BAD_START_CHARS):
                        continue
                    payload = json.loads(row[4]) if row[4] else {}
                    inner_type = str(payload.get("type", "")).lower()
                    # If type is explicitly set, it must be a valid gear type
                    if inner_type and inner_type not in VALID_TYPES:
                        continue
                    # If type is missing, apply a name-based heuristic:
                    # reject entries that look like chapter/index titles
                    if not inner_type:
                        # Skip entries whose name is entirely uppercase or starts with
                        # a number-dot pattern like "1.", "1.1.", "0."
                        import re
                        if re.match(r"^\d+[\.\s]", name):
                            continue
                    results.append(DiyargezenEntity(
                        isim=name, sistem=row[1], kategori=row[2],
                        aciklama=row[3] or "", sistem_verisi=payload
                    ))
                except Exception:
                    continue
            conn.close()
        except Exception:
            pass
        return results

    def add_item_to_inventory(self, item_entity: DiyargezenEntity) -> Dict[str, Any]:
        """Add an item to character inventory and automatically recalculate statistics (such as AC)."""
        inventory = self.active_character.setdefault("equipment", [])

        sv = item_entity.sistem_verisi or {}
        item_data = {
            "name":         item_entity.isim,
            "type":         item_entity.kategori,
            "description":  item_entity.aciklama,
            "sistem_verisi": sv,
        }

        # Otomatik armor bonus güncelleme — sistem_verisi içindeki gerçek değeri kullan
        name_lower = item_entity.isim.lower()
        if "shield" in name_lower:
            sb = sv.get("shield_bonus", sv.get("armor_class", {}).get("value", 2) if isinstance(sv.get("armor_class"), dict) else 2)
            self.active_character["shield_bonus"] = max(int(sb), 0)
        elif "armor" in name_lower or item_entity.kategori in ("armor", "equipment"):
            ac_data = sv.get("armor_class", sv.get("armorClass", {}))
            if isinstance(ac_data, dict):
                ab = int(ac_data.get("value", ac_data.get("base", 0)))
            elif isinstance(ac_data, (int, float)):
                ab = int(ac_data)
            else:
                ab = 0
            if ab > 0:
                self.active_character["armor_bonus"] = ab

        inventory.append(item_data)
        self.recalculate_character()
        return self.active_character

    def recalculate_character(self) -> Dict[str, Any]:
        """Runs the calculation pipeline to update all derived statistics live.
        Prefers update_all_stats() (5-step pipeline) when available on the calculator.
        """
        sys_key = self.active_character.get("system", "").lower().replace("_", "").replace("-", "")

        if "dnd" in sys_key:
            from rules.calculators import DND5e_Calculator
            calc = DND5e_Calculator()
        elif "pathfinder" in sys_key or "pf" in sys_key:
            from rules.calculators import PF1e_Calculator
            calc = PF1e_Calculator()
        elif "mm" in sys_key:
            from rules.calculators import MnM3e_Calculator
            calc = MnM3e_Calculator()
        else:
            return self.active_character

        # Tercih: update_all_stats() (pipeline) varsa onu çağır
        if hasattr(calc, "update_all_stats"):
            derived = calc.update_all_stats(self.active_character)
        else:
            derived = calc.calculate(self.active_character)

        self.active_character.update(derived)
        self.active_character["derived"] = derived
        return self.active_character

    def calculate_level_up_slots(self, character: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        PF1e Seviye Atlatma Sihirbazı (Level-Up Wizard) için gerekli kazanım yuvalarını hesaplar.
        
        Algoritma Kuralları:
        1. Seviye Artışı: Mevcut seviyeye +1 ekler (maksimum 20).
        2. Nitelik Puanı Artışı (Ability Score Increase): 4, 8, 12, 16 ve 20. seviyelerde +1 stat puanı kazanılır.
        3. Başarım (Feat) Slotu: Tekli seviyelerde (1, 3, 5, 7, 9, 11, 13, 15, 17, 19) Genel Feat slotu açılır.
        4. Can Puanı (HP) Artışı: Ortalama HP `floor(HD / 2) + 1 + CON_mod` (Minimum 1 HP).
        5. Beceri Puanları (Skill Ranks): `Class_Skill_Base + INT_mod` (Minimum 1 rank, Irk bonusu eklenebilir).
        
        Args:
            character (Optional[Dict[str, Any]]): Denetlenecek karakter verisi (Varsayılan: active_character).
            
        Returns:
            Dict[str, Any]: Seviye atlama adımındaki kazanım yuvaları sözlüğü.
        """
        char = character or self.active_character
        curr_level = char.get("level", 1)
        new_level = min(curr_level + 1, 20)

        # 1. Ability Score Increase check
        has_stat_increase = (new_level in {4, 8, 12, 16, 20})

        # 2. Feat Slot check
        has_new_feat = (new_level % 2 == 1)

        # 3. CON modifier for HP gain
        abilities = char.get("abilities", {})
        con_score = abilities.get("constitution", abilities.get("con", 10))
        con_mod = (con_score - 10) // 2

        # Hit die default 10 for Fighter/Paladin/Ranger if not explicitly passed
        hit_die = char.get("hit_die", 10)
        hp_average_gain = max(1, (hit_die // 2) + 1 + con_mod)

        # 4. Intelligence modifier for Skill Ranks
        int_score = abilities.get("intelligence", abilities.get("int", 10))
        int_mod = (int_score - 10) // 2

        class_skill_base = char.get("class_skill_points", 4)
        is_human = str(char.get("race", "")).lower() == "human"
        skill_ranks_available = max(1, class_skill_base + int_mod + (1 if is_human else 0))

        return {
            "current_level": curr_level,
            "new_level": new_level,
            "has_stat_increase": has_stat_increase,
            "stat_increase_points": 1 if has_stat_increase else 0,
            "has_new_feat": has_new_feat,
            "hp_average_gain": hp_average_gain,
            "skill_ranks_available": skill_ranks_available,
            "favored_class_bonus_options": ["hp", "skill_rank"],
        }

    def apply_level_up(self, choices: Dict[str, Any], character: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Seviye atlama sihirbazı seçimlerini karaktere uygular ve stat boru hattını yeniden tetikler.
        
        Args:
            choices (Dict[str, Any]): Seviye atlama sırasında oyuncunun seçtiği kararlar
                (stat_increase, hp_gain, skill_ranks, feats, favored_class_bonus).
            character (Optional[Dict[str, Any]]): Güncellenecek karakter (Varsayılan: active_character).
            
        Returns:
            Dict[str, Any]: Güncellenmiş ve yeniden hesaplanmış karakter verisi.
        """
        char = character or self.active_character
        slots = self.calculate_level_up_slots(char)
        curr_level = slots["current_level"]
        new_level = slots["new_level"]

        # Track old CON modifier prior to stat increase
        abilities = char.setdefault("abilities", {})
        old_con_score = abilities.get("constitution", abilities.get("con", 10))
        old_con_mod = (old_con_score - 10) // 2

        char["level"] = new_level

        # Apply stat increase if applicable
        if slots["has_stat_increase"] and "stat_increase" in choices:
            stat_name = choices["stat_increase"]
            target_key = stat_name
            for k in abilities.keys():
                if k.lower() in (stat_name.lower(), stat_name[:3].lower()):
                    target_key = k
                    break
            curr_val = abilities.get(target_key, 10)
            abilities[target_key] = curr_val + 1

        # Check retroactive CON modifier HP increase (PF1e CRB p. 16)
        new_con_score = abilities.get("constitution", abilities.get("con", 10))
        new_con_mod = (new_con_score - 10) // 2
        retroactive_hp = 0
        if new_con_mod > old_con_mod:
            # Retroactive +1 HP per previous level
            retroactive_hp = curr_level * (new_con_mod - old_con_mod)

        # Apply Base HP gain + Retroactive CON HP
        hp_gained = choices.get("hp_gain", slots["hp_average_gain"])
        curr_max_hp = char.get("max_hp", 10)
        
        # Favored Class Bonus (FCB) HP choice
        fcb_choice = choices.get("favored_class_bonus", "")
        fcb_hp = 1 if fcb_choice == "hp" else 0

        char["max_hp"] = curr_max_hp + hp_gained + retroactive_hp + fcb_hp

        # Apply new skill ranks
        new_skills = choices.get("skill_ranks", {})
        if new_skills:
            curr_skills = char.setdefault("skill_ranks", {})
            for sk, ranks in new_skills.items():
                curr_skills[sk] = curr_skills.get(sk, 0) + ranks

        # Apply new feats
        new_feats = choices.get("feats", [])
        if new_feats:
            curr_feats = char.setdefault("feats", [])
            for ft in new_feats:
                if ft not in curr_feats:
                    curr_feats.append(ft)

        # Recalculate derived statistics
        self.active_character = char
        self.recalculate_character()

        # Validate soft-block rules & store warnings on character
        sys_key = char.get("system", "").lower()
        if "pf" in sys_key or "pathfinder" in sys_key:
            try:
                from rules.pf1e_rules import PF1EValidator
                validator = PF1EValidator()
                char["validation_warnings"] = validator.validate(char)
            except Exception:
                pass

        return self.active_character

