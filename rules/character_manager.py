import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from db.entity_store import list_entities
from models.entity import DiyargezenEntity

class CharacterManager:
    """Manages active character data, rules engine queries, and real-time calculation updates."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.active_character: Dict[str, Any] = {}

    def set_active_character(self, character: Dict[str, Any]) -> None:
        self.active_character = character

    def get_entities_by_category(self, system: str, category: str) -> List[DiyargezenEntity]:
        """Fetch available entities (races, classes, feats, items, skills) from SQLite database."""
        sys_norm = system.lower().replace("_", "").replace("-", "")
        return list_entities(self.db_path, sys_norm, category)

    def get_subraces_for_race(self, system: str, parent_race: str) -> List[DiyargezenEntity]:
        """Fetch subraces/heritages for a given parent race.

        Searches both 'race' and 'feat' categories because:
        - D&D 5e: subraces stored as kategori='race' with parent_race set
        - PF1e: racial traits/heritages stored as kategori='feat' with parent_race set
          (after the parser fix that correctly maps type='feat' entities)
        """
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori IN ('race', 'feat') "
                "AND json_extract(sistem_verisi, '$.parent_race') = ? "
                "ORDER BY isim COLLATE NOCASE",
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
        """Fetch only top-level races (those without a parent_race) from the DB.

        Priority:
        1. Entities with kategori='race', no parent_race, name NOT a creature-type stub
        2. PF1e fallback: synthesise stubs from distinct parent_race values on feat entities
           (PF1e data pack has no standalone race entries — only racial trait feats)
        """
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []

        # Names that indicate a FoundryVTT creature-type pseudo-race (not a PC race)
        CREATURE_TYPE_PREFIXES = ("Race: ", "race: ")

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Primary: real race entities with no parent, excluding creature-type stubs
            cursor.execute(
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori = 'race' "
                "AND (json_extract(sistem_verisi, '$.parent_race') IS NULL "
                "     OR json_extract(sistem_verisi, '$.parent_race') = '') "
                "ORDER BY isim COLLATE NOCASE",
                (sys_norm,)
            )
            for row in cursor.fetchall():
                # Skip creature-type pseudo-races (e.g. 'Race: Aberration')
                if any(row[0].startswith(p) for p in CREATURE_TYPE_PREFIXES):
                    continue
                try:
                    payload = json.loads(row[4]) if row[4] else {}
                    results.append(DiyargezenEntity(
                        isim=row[0], sistem=row[1], kategori=row[2],
                        aciklama=row[3] or "", sistem_verisi=payload
                    ))
                except Exception:
                    continue

            # Fallback: synthesise parent-race stubs from distinct parent_race values
            # on feat entities.  Used for PF1e where the data pack only has racial
            # trait feats — no standalone race entries exist.
            if not results:
                if "pathfinder" in sys_norm or "pf" in sys_norm:
                    cursor.execute("""
                        SELECT DISTINCT json_extract(sistem_verisi, '$.parent_race') 
                        FROM entities 
                        WHERE sistem = ? AND kategori = 'feat' 
                        AND TRIM(LOWER(json_extract(sistem_verisi, '$.parent_race'))) IN (
                            'human', 'elf', 'dwarf', 'gnome', 'halfling', 'half-elf', 'half-orc',
                            'aasimar', 'tiefling', 'ifrit', 'oread', 'sylph', 'undine',
                            'catfolk', 'tengu', 'ratfolk', 'fetchling', 'dhampir', 'drow',
                            'goblin', 'hobgoblin', 'kobold', 'orc', 'kitsune', 'changeling',
                            'wayang', 'nagaji', 'samsaran', 'vishkanya', 'grippli', 'merfolk',
                            'strix', 'svirfneblin', 'vanara'
                        )
                        ORDER BY json_extract(sistem_verisi, '$.parent_race') COLLATE NOCASE
                    """, (sys_norm,))
                else:
                    cursor.execute(
                        "SELECT DISTINCT json_extract(sistem_verisi, '$.parent_race') "
                        "FROM entities "
                        "WHERE sistem = ? AND kategori = 'feat' "
                        "AND json_extract(sistem_verisi, '$.parent_race') IS NOT NULL "
                        "AND json_extract(sistem_verisi, '$.parent_race') != '' "
                        "ORDER BY json_extract(sistem_verisi, '$.parent_race') COLLATE NOCASE",
                        (sys_norm,)
                    )
                # Load PF1e full race data from JSON
                import json
                from pathlib import Path
                pf1e_data = {}
                try:
                    j_path = Path(__file__).parent.parent / "data" / "pathfinder_1e_data.json"
                    if j_path.exists():
                        with open(j_path, "r", encoding="utf-8") as f:
                            pf1e_data = json.load(f).get("races", {})
                except Exception:
                    pass

                for (parent_name,) in cursor.fetchall():
                    if parent_name and not any(parent_name.startswith(p) for p in CREATURE_TYPE_PREFIXES):
                        race_info = pf1e_data.get(parent_name, {})
                        
                        desc = race_info.get("description", f"{parent_name} ırkı (Pathfinder 1e)")
                        if "speed" in race_info:
                            desc += f"<br><br><b>Hız:</b> {race_info['speed']} ft"
                        if "size" in race_info:
                            desc += f" | <b>Boyut:</b> {race_info['size']}"
                        if "ability_score_increase_text" in race_info:
                            desc += f"<br><b>Yetenek Bonusu:</b> {race_info['ability_score_increase_text']}"
                        if "traits" in race_info and race_info["traits"]:
                            desc += f"<br><br><b>Özellikler:</b> {', '.join(race_info['traits'])}"
                            
                        sistem_verisi = {"synthesised": True}
                        if race_info:
                            sistem_verisi.update(race_info)
                            
                        results.append(DiyargezenEntity(
                            isim=parent_name,
                            sistem=sys_norm,
                            kategori="race",
                            aciklama=desc,
                            sistem_verisi=sistem_verisi
                        ))

            conn.close()
        except Exception:
            pass
        if not results and ("pathfinder" in sys_norm or "pf" in sys_norm):
            fallback_race_names = [
                "Human", "Elf", "Dwarf", "Gnome", "Halfling", "Half-Elf", "Half-Orc",
                "Aasimar", "Tiefling", "Ifrit", "Oread", "Sylph", "Undine", "Catfolk",
                "Tengu", "Ratfolk", "Fetchling", "Dhampir", "Drow", "Goblin", "Hobgoblin",
                "Kobold", "Orc", "Kitsune", "Changeling", "Wayang", "Nagaji", "Samsaran",
                "Vishkanya", "Grippli", "Merfolk", "Strix", "Svirfneblin", "Vanara"
            ]
            for r_name in fallback_race_names:
                results.append(
                    DiyargezenEntity(
                        isim=r_name,
                        sistem="pathfinder1e",
                        kategori="race",
                        aciklama=f"{r_name} (PF1e Brute-Force Fallback)",
                        sistem_verisi={"synthesised": True}
                    )
                )
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

    # DND5e için NPC/canavar filtresi — bu sistem için sadece
    # aşağıdaki çok açık NPC girişleri engellenir (DND5e'de bu nadiren gerekir).
    _DND5E_BLOCK_KEYWORDS = (
        "outsider", "humanoid", "aberration", "construct",
        "dragon", "fey", "undead", "vermin",
        "race:",
    )

    def get_clean_classes(self, system: str) -> List[DiyargezenEntity]:
        """Return only playable classes, stripping NPC/creature-type entries.

        Sistem-spesifik filtreleme:
        - DND5e: minimal blocklist; mevcut 14 sınıf doğrudan dönür.
        - PF1e: Whitelist tabanlı; sadece _PF1E_PLAYABLE_CLASSES listesindeki
          isimler (prefix eşleşmesi) kabul edilir. Böylece Outsider/Dragon/
          NPC seri girdi hiçbir keyword kara listesi olmadan temizlenir.
        - MM3e: minimal filtreleme (kategori='class' yeterli).
        """
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori = 'class' "
                "ORDER BY isim COLLATE NOCASE",
                (sys_norm,)
            )
            for row in cursor.fetchall():
                name: str = row[0]
                name_lower = name.lower()

                if "pathfinder" in sys_norm or "pf" in sys_norm:
                    # PF1e: Whitelist tabanlı — isim beyaz listede bir kelimeyle başlıyorsa kabul
                    prefix = name_lower.split("(")[0].strip()  # "Monk (Unchained)" -> "monk"
                    if prefix not in self._PF1E_PLAYABLE_CLASSES:
                        continue
                elif "dnd" in sys_norm:
                    # DND5e: sadece açık NPC/canavar marker'larını engelle
                    if any(kw in name_lower for kw in self._DND5E_BLOCK_KEYWORDS):
                        continue
                # MM3e ve diğerleri: SQL sanitisasyonu yeterli

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
                "ORDER BY isim COLLATE NOCASE LIMIT 300",
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


    def get_traits(self, system: str) -> List[DiyargezenEntity]:
        """Return character traits (PF1e trait category).

        Traits are mechanically distinct from feats in PF1e and are stored
        with kategori='trait' after the parser fix.
        """
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results = list_entities(self.db_path, sys_norm, "trait")
        if not results and ("pathfinder" in sys_norm or "pf" in sys_norm):
            fallback_trait_names = [
                "Reactionary (Combat)", "Armor Expert (Combat)", "Courageous (Combat)",
                "Magical Knack (Magic)", "Focused Mind (Magic)", "Student of Philosophy (Social)",
                "Fast-Talker (Social)", "Fate's Favored (Faith)", "Birthmark (Faith)",
                "Deft Dodger (Combat)", "Resilient (Combat)"
            ]
            for t_name in fallback_trait_names:
                results.append(
                    DiyargezenEntity(
                        isim=t_name,
                        sistem="pathfinder1e",
                        kategori="trait",
                        aciklama=f"{t_name} (PF1e Brute-Force Fallback)",
                        sistem_verisi={}
                    )
                )
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
        return self.active_character
