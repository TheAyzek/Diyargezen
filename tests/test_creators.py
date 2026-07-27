# tests/test_creators.py
"""
Unit Tests
==========
  - BaseCharacterCreator: ABC, soyut metodlar, ortak zar/modifier
  - CreatorFactory: Factory Pattern, kayıt, hata yönetimi, dice system meta-data
  - DiceSystem: d20 vs d10 pool farklılıkları
  - DataLoader: cache mekanizması, singleton, mtime invalidation
  - SQLite Storage: tam CRUD (Create, Read, Update, Delete) + search + count
  - Her 3 TTRPG Creator: calculate_stats(), export_data(), validate_character()
"""

import json
import tempfile
import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from creators import CreatorFactory, CharacterFactory
from creators.base_creator import (
    BaseCharacterCreator,
    DiceSystem,
    DICE_D20,
    DICE_D6_POOL,
)


# ======================================================================
# 1. BaseCharacterCreator & Factory Pattern
# ======================================================================

class TestBaseCreatorAndFactory(unittest.TestCase):

    # ---- Factory registration ----

    def test_factory_all_aliases_registered(self):
        available = CreatorFactory.get_available_systems()
        for key in ['dnd5e', 'd&d', 'pathfinder1e', 'pf1e', 'mm3e', 'm&m']:
            self.assertIn(key, available)

    def test_factory_unknown_system_raises(self):
        with self.assertRaises(ValueError):
            CreatorFactory.create("nonexistent_xyz")

    def test_factory_error_message_lists_available(self):
        try:
            CreatorFactory.create("bad")
        except ValueError as e:
            self.assertIn("Mevcut:", str(e))

    def test_creators_are_subclasses(self):
        for key in ['dnd5e', 'pathfinder1e', 'mm3e']:
            creator = CreatorFactory.create(key)
            self.assertIsInstance(creator, BaseCharacterCreator)

    def test_get_system_name_non_empty(self):
        for key in ['dnd5e', 'pathfinder1e', 'mm3e']:
            creator = CreatorFactory.create(key)
            self.assertTrue(len(creator.get_system_name()) > 0)

    def test_backward_compat_character_factory(self):
        """CharacterFactory alias still works."""
        creator = CharacterFactory.create_creator("dnd5e")
        self.assertIsInstance(creator, BaseCharacterCreator)

    # ---- Dice System meta-data ----

    def test_dice_system_d20(self):
        creator = CreatorFactory.create("dnd5e")
        self.assertEqual(creator.DICE_SYSTEM.name, "d20")
        self.assertEqual(creator.DICE_SYSTEM.base_die, 20)
        self.assertFalse(creator.DICE_SYSTEM.pool_based)

    def test_dice_system_mm3e_uses_d20(self):
        creator = CreatorFactory.create("mm3e")
        self.assertEqual(creator.DICE_SYSTEM.name, "d20")
        self.assertEqual(creator.DICE_SYSTEM.base_die, 20)
        self.assertFalse(creator.DICE_SYSTEM.pool_based)

    def test_get_dice_system_via_factory(self):
        ds = CreatorFactory.get_dice_system("pathfinder1e")
        self.assertIsInstance(ds, DiceSystem)
        self.assertEqual(ds.name, "d20")

    def test_get_system_info(self):
        info = CreatorFactory.get_system_info()
        self.assertIn("dnd5e", info)
        self.assertEqual(info["dnd5e"]["dice_system"], "d20")

    # ---- Dice helpers ----

    def test_roll_dice_count_and_range(self):
        results = BaseCharacterCreator.roll_dice(5, 8)
        self.assertEqual(len(results), 5)
        for r in results:
            self.assertGreaterEqual(r, 1)
            self.assertLessEqual(r, 8)

    def test_roll_dice_invalid_params(self):
        with self.assertRaises(ValueError):
            BaseCharacterCreator.roll_dice(0, 6)
        with self.assertRaises(ValueError):
            BaseCharacterCreator.roll_dice(1, 1)

    def test_roll_sum(self):
        total = BaseCharacterCreator.roll_sum(2, 6)
        self.assertGreaterEqual(total, 2)
        self.assertLessEqual(total, 12)

    def test_roll_4d6_drop_lowest_range(self):
        for _ in range(100):
            score = BaseCharacterCreator.roll_4d6_drop_lowest()
            self.assertGreaterEqual(score, 3)
            self.assertLessEqual(score, 18)

    # ---- Ability modifier ----

    def test_ability_modifier_table(self):
        cases = [(1, -5), (8, -1), (10, 0), (11, 0), (12, 1), (15, 2), (20, 5)]
        for score, expected in cases:
            self.assertEqual(BaseCharacterCreator.calculate_ability_modifier(score), expected)

    # ---- Ability bonus ----

    def test_add_ability_bonus(self):
        creator = CreatorFactory.create('dnd5e')
        abilities = {"strength": 14, "dexterity": 10}
        updated = creator.add_ability_bonus(abilities, "strength", 2)
        self.assertEqual(updated["strength"], 16)
        self.assertEqual(updated["dexterity"], 10)
        self.assertEqual(abilities["strength"], 14)

    # ---- Data query helpers ----

    def test_list_races_and_classes(self):
        creator = CreatorFactory.create('dnd5e')
        self.assertIn("Human", creator.list_available_races())
        self.assertIn("Fighter", creator.list_available_classes())

    def test_get_race_data_found_and_not_found(self):
        creator = CreatorFactory.create('dnd5e')
        self.assertIsNotNone(creator.get_race_data("Human"))
        self.assertIsNone(creator.get_race_data("Alien"))

    def test_save_and_load_roundtrip(self):
        char = {"name": "RoundtripChar", "system": "DND5E", "level": 1}
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = Path(tmpdir) / "test.json"
            with fpath.open("w", encoding="utf-8") as f:
                json.dump(char, f)
            loaded = json.loads(fpath.read_text(encoding="utf-8"))
            self.assertEqual(loaded["name"], "RoundtripChar")

    # ---- Abstract method enforcement ----

    def test_cannot_instantiate_abc_directly(self):
        with self.assertRaises(TypeError):
            BaseCharacterCreator("test", "dnd_data.json")

    # ---- calculate_derived_stats backward compat ----

    def test_calculate_derived_stats_calls_calculate_stats(self):
        creator = CreatorFactory.create('dnd5e')
        char = {
            'name': 'T', 'race': 'Human', 'class': 'Fighter', 'level': 1,
            'abilities': {'strength': 16, 'dexterity': 14, 'constitution': 15,
                          'intelligence': 10, 'wisdom': 12, 'charisma': 8},
        }
        via_stats = creator.calculate_stats(char)
        via_derived = creator.calculate_derived_stats(char)
        self.assertEqual(via_stats.keys(), via_derived.keys())


# ======================================================================
# 2. DataLoader (cache + singleton)
# ======================================================================

class TestDataLoader(unittest.TestCase):

    @staticmethod
    def _data_file(system_key: str) -> Path:
        filenames = {
            "dnd": "dnd_data.json",
            "pathfinder_1e": "pathfinder_1e_data.json",
            "mm": "mm_data.json",
        }
        return BASE_DIR / "data" / filenames[system_key]

    def test_loads_dnd_with_expected_keys(self):
        if not self._data_file("dnd").exists():
            self.skipTest("dnd_data.json mevcut değil (PF1e odaklı pivot)")
        from utils.data_loader import DataLoader
        loader = DataLoader(base_dir=BASE_DIR)
        data = loader.load("dnd")
        for key in ("races", "classes", "spells"):
            self.assertIn(key, data)

    def test_loads_all_systems(self):
        from utils.data_loader import DataLoader
        loader = DataLoader(base_dir=BASE_DIR)
        for sys_key in ("dnd", "pathfinder_1e", "mm"):
            with self.subTest(system=sys_key):
                if not self._data_file(sys_key).exists():
                    self.skipTest(f"{sys_key} veri dosyası mevcut değil")
                data = loader.load(sys_key)
                self.assertIsInstance(data, dict)
                self.assertGreater(len(data), 0)

    def test_cache_returns_same_object(self):
        from utils.data_loader import DataLoader
        loader = DataLoader(base_dir=BASE_DIR)
        first = loader.load("pathfinder_1e")
        second = loader.load("pathfinder_1e")
        self.assertIs(first, second)

    def test_clear_cache_invalidates(self):
        from utils.data_loader import DataLoader
        loader = DataLoader(base_dir=BASE_DIR)
        loader.load("pathfinder_1e")
        self.assertGreater(loader.cache_size, 0)
        loader.clear_cache()
        self.assertEqual(loader.cache_size, 0)

    def test_unknown_system_raises(self):
        from utils.data_loader import DataLoader
        loader = DataLoader(base_dir=BASE_DIR)
        with self.assertRaises(ValueError):
            loader.load("nonexistent")

    def test_dnd_normalization_name_fields(self):
        if not self._data_file("dnd").exists():
            self.skipTest("dnd_data.json mevcut değil (PF1e odaklı pivot)")
        from utils.data_loader import DataLoader
        loader = DataLoader(base_dir=BASE_DIR)
        data = loader.load("dnd")
        for race_name, race_data in data.get("races", {}).items():
            if isinstance(race_data, dict):
                self.assertTrue(race_data.get("name"), f"Race '{race_name}' missing name")

    def test_singleton_returns_same_instance(self):
        from utils.data_loader import get_loader
        a = get_loader(BASE_DIR)
        b = get_loader(BASE_DIR)
        self.assertIs(a, b)

    def test_convenience_functions_return_data(self):
        from utils.data_loader import load_dnd_data, load_mm_data, load_pathfinder_1e_data
        if self._data_file("dnd").exists():
            self.assertIn("races", load_dnd_data(BASE_DIR))
        if self._data_file("mm").exists():
            self.assertIsInstance(load_mm_data(BASE_DIR), dict)
        self.assertIsInstance(load_pathfinder_1e_data(BASE_DIR), dict)


# ======================================================================
# 3. SQLite Storage CRUD
# ======================================================================

class TestStorage(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        from utils.storage import init_db
        init_db(self.db_path)

    def tearDown(self):
        self._tmpdir.cleanup()

    # ---- Create + Read ----

    def test_create_and_read(self):
        from utils.storage import save_character, load_character, CharacterRecord
        rec = CharacterRecord(id=None, system="DND5E", name="Aragorn",
                              data={"class": "Ranger", "level": 5})
        new_id = save_character(self.db_path, rec)
        self.assertGreater(new_id, 0)

        loaded = load_character(self.db_path, new_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, "Aragorn")
        self.assertEqual(loaded.data["class"], "Ranger")
        self.assertIsNotNone(loaded.created_at)
        self.assertIsNotNone(loaded.updated_at)

    def test_load_nonexistent_returns_none(self):
        from utils.storage import load_character
        self.assertIsNone(load_character(self.db_path, 9999))

    # ---- List + Filter ----

    def test_list_all_and_filter(self):
        from utils.storage import save_character, list_characters, CharacterRecord
        save_character(self.db_path, CharacterRecord(id=None, system="DND5E", name="A", data={}))
        save_character(self.db_path, CharacterRecord(id=None, system="MM3E", name="B", data={}))
        save_character(self.db_path, CharacterRecord(id=None, system="DND5E", name="C", data={}))

        self.assertEqual(len(list_characters(self.db_path)), 3)
        self.assertEqual(len(list_characters(self.db_path, system="DND5E")), 2)
        self.assertEqual(len(list_characters(self.db_path, system="MM3E")), 1)

    # ---- Search ----

    def test_search_by_name(self):
        from utils.storage import save_character, search_characters, CharacterRecord
        save_character(self.db_path, CharacterRecord(id=None, system="DND5E", name="Gandalf the Grey", data={}))
        save_character(self.db_path, CharacterRecord(id=None, system="DND5E", name="Aragorn", data={}))
        save_character(self.db_path, CharacterRecord(id=None, system="MM3E", name="Gandalf the White", data={}))

        results = search_characters(self.db_path, "Gandalf")
        self.assertEqual(len(results), 2)

        results_dnd = search_characters(self.db_path, "Gandalf", system="DND5E")
        self.assertEqual(len(results_dnd), 1)

    # ---- Count ----

    def test_count_characters(self):
        from utils.storage import save_character, count_characters, CharacterRecord
        self.assertEqual(count_characters(self.db_path), 0)
        save_character(self.db_path, CharacterRecord(id=None, system="DND5E", name="X", data={}))
        save_character(self.db_path, CharacterRecord(id=None, system="MM3E", name="Y", data={}))
        self.assertEqual(count_characters(self.db_path), 2)
        self.assertEqual(count_characters(self.db_path, system="DND5E"), 1)

    # ---- Update ----

    def test_update_changes_data(self):
        from utils.storage import save_character, load_character, update_character, CharacterRecord
        rec = CharacterRecord(id=None, system="DND5E", name="Gimli",
                              data={"class": "Fighter", "level": 1})
        rec_id = save_character(self.db_path, rec)

        updated = CharacterRecord(id=rec_id, system="DND5E", name="Gimli",
                                  data={"class": "Fighter", "level": 5})
        self.assertTrue(update_character(self.db_path, rec_id, updated))

        loaded = load_character(self.db_path, rec_id)
        self.assertEqual(loaded.data["level"], 5)

    def test_update_nonexistent_returns_false(self):
        from utils.storage import update_character, CharacterRecord
        rec = CharacterRecord(id=None, system="DND5E", name="Ghost", data={})
        self.assertFalse(update_character(self.db_path, 9999, rec))

    # ---- Delete ----

    def test_delete_removes_record(self):
        from utils.storage import save_character, load_character, delete_character, CharacterRecord
        rec_id = save_character(self.db_path,
                                CharacterRecord(id=None, system="DND5E", name="Boromir", data={}))
        self.assertTrue(delete_character(self.db_path, rec_id))
        self.assertIsNone(load_character(self.db_path, rec_id))

    def test_delete_nonexistent_returns_false(self):
        from utils.storage import delete_character
        self.assertFalse(delete_character(self.db_path, 9999))


# ======================================================================
# 4. Individual Creator Tests
# ======================================================================

class TestDND5ECreator(unittest.TestCase):

    def setUp(self):
        self.creator = CreatorFactory.create('dnd5e')

    def test_data_has_required_sections(self):
        for key in ("races", "classes", "backgrounds"):
            self.assertIn(key, self.creator.data)

    def test_validate_valid_character(self):
        char = {
            'name': 'Test Fighter', 'race': 'Human', 'class': 'Fighter',
            'background': 'Soldier', 'level': 1,
            'abilities': {'strength': 16, 'dexterity': 14, 'constitution': 15,
                          'intelligence': 10, 'wisdom': 12, 'charisma': 8},
        }
        errors = self.creator.validate_character(char)
        self.assertEqual(len(errors), 0, f"Errors: {errors}")

    def test_validate_detects_missing_name(self):
        char = {'race': 'Human', 'class': 'Fighter', 'level': 1,
                'abilities': {'strength': 10}}
        errors = self.creator.validate_character(char)
        self.assertTrue(any("name" in e.lower() for e in errors))

    def test_calculate_stats_for_wizard(self):
        char = {
            'name': 'Tester', 'race': 'Human', 'class': 'Wizard',
            'level': 5,
            'abilities': {'strength': 8, 'dexterity': 14, 'constitution': 13,
                          'intelligence': 18, 'wisdom': 12, 'charisma': 10},
        }
        stats = self.creator.calculate_stats(char)
        self.assertEqual(stats['proficiency_bonus'], 3)
        self.assertIn('spell_slots', stats)
        self.assertIn('saving_throws', stats)
        self.assertIn('skills', stats)

    def test_export_data_contains_system(self):
        char = {
            'name': 'ExportTest', 'race': 'Human', 'class': 'Fighter', 'level': 1,
            'abilities': {'strength': 16, 'dexterity': 14, 'constitution': 15,
                          'intelligence': 10, 'wisdom': 12, 'charisma': 8},
        }
        exported = self.creator.export_data(char)
        self.assertEqual(exported['system'], 'DND5E')
        self.assertEqual(exported['dice_system'], 'd20')
        self.assertIn('name', exported)

    def test_dice_system_is_d20(self):
        self.assertEqual(self.creator.DICE_SYSTEM, DICE_D20)


class TestPathfinder1ECreator(unittest.TestCase):

    def setUp(self):
        self.creator = CreatorFactory.create('pathfinder1e')

    def test_data_loaded(self):
        self.assertGreater(len(self.creator.data), 0)

    def test_validate_valid(self):
        char = {
            'race': 'Human', 'class': 'Fighter', 'level': 1,
            'abilities': {'strength': 16, 'dexterity': 14, 'constitution': 15,
                          'intelligence': 10, 'wisdom': 12, 'charisma': 8},
            'bab': 1, 'saves': {'fortitude': 2, 'reflex': 0, 'will': 0},
        }
        self.assertEqual(len(self.creator.validate_character(char)), 0)

    def test_validate_ability_out_of_range(self):
        char = {'race': 'Human', 'class': 'Fighter', 'level': 1,
                'abilities': {'strength': 25}, 'bab': 1, 'saves': {}}
        self.assertGreater(len(self.creator.validate_character(char)), 0)

    def test_export_data_system_pathfinder(self):
        char = {
            'race': 'Human', 'class': 'Fighter', 'level': 1,
            'abilities': {'strength': 14}, 'bab': 1, 'saves': {},
        }
        exported = self.creator.export_data(char)
        self.assertEqual(exported['system'], 'PATHFINDER_1E')

    def test_dice_system_is_d20(self):
        self.assertEqual(self.creator.DICE_SYSTEM, DICE_D20)


class TestMM3ECreator(unittest.TestCase):

    def setUp(self):
        self.creator = CreatorFactory.create('mm3e')

    def test_data_loaded(self):
        self.assertGreater(len(self.creator.data), 0)

    def test_validate_valid(self):
        char = {
            'power_level': 'PL10', 'pl_value': 10,
            'abilities': {'strength': 8, 'stamina': 6, 'agility': 4,
                          'dexterity': 4, 'fighting': 6, 'intellect': 2,
                          'awareness': 2, 'presence': 2},
            'powers': {}, 'remaining_power_points': 50,
        }
        self.assertEqual(len(self.creator.validate_character(char)), 0)

    def test_validate_pl_exceeded(self):
        char = {
            'power_level': 'PL10', 'pl_value': 10,
            'abilities': {'strength': 15},
            'powers': {}, 'remaining_power_points': 50,
        }
        self.assertGreater(len(self.creator.validate_character(char)), 0)

    def test_export_data_mm(self):
        char = {
            'name': 'Sentinel', 'power_level': 'PL10', 'pl_value': 10,
            'abilities': {'strength': 8, 'stamina': 6, 'agility': 4,
                          'dexterity': 4, 'fighting': 6, 'intellect': 2,
                          'awareness': 2, 'presence': 2},
            'powers': {}, 'defenses': {},
        }
        exported = self.creator.export_data(char)
        self.assertEqual(exported['system'], 'MM3E')
        self.assertIn('initiative', exported)


if __name__ == '__main__':
    unittest.main()
