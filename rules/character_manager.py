import sqlite3
import json
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

    def get_traits(self, system: str, query: str = "", category: str = "") -> List[DiyargezenEntity]:
        """Fetch character traits, filtered by optional search query and/or trait category.

        Returns only traits that have an explicit trait_category set (our curated list).
        Results are sorted alphabetically within each category.
        """
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            base_sql = (
                "SELECT isim, sistem, kategori, aciklama, sistem_verisi "
                "FROM entities "
                "WHERE sistem = ? AND kategori = 'trait' "
                "AND json_extract(sistem_verisi, '$.trait_category') IS NOT NULL "
            )
            params = [sys_norm]

            if query:
                base_sql += "AND (isim LIKE ? OR aciklama LIKE ?) "
                params.extend([f"%{query}%", f"%{query}%"])

            if category:
                base_sql += "AND json_extract(sistem_verisi, '$.trait_category') = ? "
                params.append(category)

            base_sql += "ORDER BY json_extract(sistem_verisi, '$.trait_category') ASC, isim COLLATE NOCASE ASC LIMIT 200"

            cursor.execute(base_sql, params)
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

    # Map of PF1e feat types found in name suffixes
    _FEAT_CATEGORY_SUFFIXES = {
        "Combat": ["(Combat)"],
        "Teamwork": ["(Teamwork)"],
        "Metamagic": ["(Metamagic)"],
        "Item Creation": ["(Item Creation)"],
        "Mythic": ["(Mythic)"],
        "Performance": ["(Performance)"],
        "Grit": ["(Grit)"],
        "Racial": [
            "(Dwarf)", "(Elf)", "(Gnome)", "(Half-Elf)", "(Half-Orc)", "(Half-Orc, Orc)",
            "(Halfling)", "(Human)", "(Aasimar)", "(Tiefling)", "(Goblin)", "(Drow)",
            "(Changeling)", "(Kitsune)", "(Nagaji)", "(Orc)", "(Samsaran)",
        ],
        "General": [],  # catch-all
    }

    @classmethod
    def _parse_feat_category(cls, feat_name: str) -> str:
        """Derive feat category from the name, checking parenthesized tags like (Combat), (Teamwork), etc."""
        import re
        name = feat_name.strip()
        m = re.search(r'\(([^)]+)\)', name)
        if m:
            tag = m.group(1).lower()
            if "combat" in tag:
                return "Combat"
            if "teamwork" in tag:
                return "Teamwork"
            if "metamagic" in tag:
                return "Metamagic"
            if "item creation" in tag:
                return "Item Creation"
            if "mythic" in tag:
                return "Mythic"
            if "performance" in tag:
                return "Performance"
            if "grit" in tag:
                return "Grit"
            races = ["dwarf", "elf", "gnome", "half-elf", "half-orc", "halfling", "human", "aasimar", "tiefling", "goblin", "drow", "kitsune", "orc"]
            if any(r in tag for r in races):
                return "Racial"
        return "General"

    def get_feats(self, system: str, query: str = "", category: str = "") -> List[DiyargezenEntity]:
        """Retrieve feats filtered by search query and/or category.

        Categories are derived from name tags: (Combat), (Teamwork), (Metamagic), etc.
        Template/index entries are excluded (names starting with #, (, [, *).
        """
        sys_norm = system.lower().replace("_", "").replace("-", "")
        results: List[DiyargezenEntity] = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Base query — exclude junk entries
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
                sql += "AND isim LIKE ? "
                params.append(f"%{query}%")

            sql += "ORDER BY isim COLLATE NOCASE ASC LIMIT 300"


            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                try:
                    feat_name = row[0]
                    feat_cat = self._parse_feat_category(feat_name)

                    # Apply strict category filter if specified
                    if category and feat_cat != category and category != "General":
                        continue

                    payload = json.loads(row[4]) if row[4] else {}
                    payload["feat_category"] = feat_cat

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
