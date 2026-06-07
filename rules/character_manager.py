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
                cursor.execute(
                    "SELECT DISTINCT json_extract(sistem_verisi, '$.parent_race') "
                    "FROM entities "
                    "WHERE sistem = ? AND kategori = 'feat' "
                    "AND json_extract(sistem_verisi, '$.parent_race') IS NOT NULL "
                    "AND json_extract(sistem_verisi, '$.parent_race') != '' "
                    "ORDER BY json_extract(sistem_verisi, '$.parent_race') COLLATE NOCASE",
                    (sys_norm,)
                )
                for (parent_name,) in cursor.fetchall():
                    if parent_name and not any(parent_name.startswith(p) for p in CREATURE_TYPE_PREFIXES):
                        results.append(DiyargezenEntity(
                            isim=parent_name,
                            sistem=sys_norm,
                            kategori="race",
                            aciklama=f"{parent_name} ırkı (Pathfinder 1e)",
                            sistem_verisi={"synthesised": True}
                        ))

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

    # NPC / creature-type / pseudo-class names that must never appear in the
    # playable class dropdown.
    _NPC_CLASS_KEYWORDS = (
        # Generic creature types
        "outsider", "humanoid", "aberration", "animal", "construct",
        "dragon", "fey", "magical beast", "monstrous humanoid", "ooze",
        "plant", "undead", "vermin",
        # PF1e NPC-only base classes
        "adept", "aristocrat", "commoner", "expert", "warrior",
        # PF1e companion/familiar/summon pseudo-classes
        "eidolon", "familiar", "companion", "drake", "phantom",
        # Class ability sub-entries incorrectly stored as classes
        "rage",        # Barbarian class ability
        # Fragments / suffixes (e.g. "alchemist's familiar", "alchemist\u2019s")
        "'s", "\u2019s",
        # Bloodline/archetype sub-entries stored as class
        "bloodline",
        # Generic NPC marker
        "npc",
        # Leftover race prefixes
        "race:",
    )

    def get_clean_classes(self, system: str) -> List[DiyargezenEntity]:
        """Return only playable classes, stripping NPC/creature-type entries.

        Filters both by SQL (name NOT LIKE patterns) and by a Python-side
        keyword blocklist so that entries like 'Humanoid', 'Undead', etc.
        are never presented to the user.
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
                # SQL-level name sanitisation
                "AND isim NOT LIKE '(%)%' "
                "AND isim NOT LIKE '#%' "
                "AND isim NOT LIKE '[%' "
                "AND isim NOT LIKE '*%' "
                "AND isim NOT LIKE 'Race:%' "
                "ORDER BY isim COLLATE NOCASE",
                (sys_norm,)
            )
            for row in cursor.fetchall():
                name_lower = row[0].lower()
                # Python-side blocklist for NPC/creature-type names
                if any(kw in name_lower for kw in self._NPC_CLASS_KEYWORDS):
                    continue
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
        return list_entities(self.db_path, sys_norm, "trait")


    def add_item_to_inventory(self, item_entity: DiyargezenEntity) -> Dict[str, Any]:
        """Add an item to character inventory and automatically recalculate statistics (such as AC)."""
        inventory = self.active_character.setdefault("equipment", [])
        
        # Formulate item data
        item_data = {
            "name": item_entity.isim,
            "type": item_entity.kategori,
            "description": item_entity.aciklama,
            "sistem_verisi": item_entity.sistem_verisi
        }
        
        # Automatically update armor bonuses if armor is added
        name_lower = item_entity.isim.lower()
        if "armor" in name_lower or "shield" in name_lower:
            # Basic parsing of armor class value from description/metadata
            ac_base = item_entity.sistem_verisi.get("armor_class", {}).get("base", 10)
            if "shield" in name_lower:
                self.active_character["shield_bonus"] = item_entity.sistem_verisi.get("shield_bonus", 2)
            else:
                self.active_character["armor_bonus"] = ac_base - 10
            
        inventory.append(item_data)
        self.recalculate_character()
        return self.active_character

    def recalculate_character(self) -> Dict[str, Any]:
        """Runs the calculation engines to update all derived statistics live."""
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

        derived = calc.calculate(self.active_character)
        self.active_character.update(derived)
        return self.active_character
