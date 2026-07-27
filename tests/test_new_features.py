# tests/test_new_features.py
"""
Yeni eklenen ozellikler icin kapsamli testler:
- Multiclass sistemi
- Subclass verisi
- Condition/Status Effect sistemi
- Pathfinder spell temizleme
- Karakter validasyonu (multiclass dahil)
"""

import unittest
import sys
import json
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ============================================================================
# MULTICLASS TESTLERI
# ============================================================================

class TestMulticlass(unittest.TestCase):
    """Multiclass sistemi testleri"""

    def setUp(self):
        from utils.multiclass import (
            check_multiclass_prerequisites, get_multiclass_proficiencies,
            calculate_multiclass_spell_slots, calculate_multiclass_hp,
            calculate_multiclass_hit_dice, get_available_multiclass_options,
            apply_multiclass_level, get_total_character_level,
            MULTICLASS_PREREQUISITES, CLASS_HIT_DICE
        )
        self.check_prereqs = check_multiclass_prerequisites
        self.get_profs = get_multiclass_proficiencies
        self.calc_slots = calculate_multiclass_spell_slots
        self.calc_hp = calculate_multiclass_hp
        self.calc_hit_dice = calculate_multiclass_hit_dice
        self.get_options = get_available_multiclass_options
        self.apply_mc = apply_multiclass_level
        self.get_total = get_total_character_level
        self.PREREQS = MULTICLASS_PREREQUISITES
        self.HIT_DICE = CLASS_HIT_DICE

    def test_prerequisites_met(self):
        """Prerequisite'ler karsilandiginda True donmeli"""
        char = {
            "class": "Fighter",
            "abilities": {"Strength": 16, "Dexterity": 14, "Charisma": 13}
        }
        can_mc, reasons = self.check_prereqs(char, "Bard")
        self.assertTrue(can_mc, f"Reasons: {reasons}")

    def test_prerequisites_not_met(self):
        """Prerequisite'ler karsilanmadiginda False donmeli"""
        char = {
            "class": "Fighter",
            "abilities": {"Strength": 16, "Dexterity": 8, "Wisdom": 8}
        }
        can_mc, reasons = self.check_prereqs(char, "Monk")
        self.assertFalse(can_mc)
        self.assertTrue(len(reasons) > 0)

    def test_fighter_alternative_prereqs(self):
        """Fighter alternatif prerequisite (STR veya DEX)"""
        char = {
            "class": "Wizard",
            "abilities": {"Intelligence": 14, "Strength": 8, "Dexterity": 14}
        }
        can_mc, reasons = self.check_prereqs(char, "Fighter")
        self.assertTrue(can_mc, f"DEX 14 ile Fighter multiclass olmali: {reasons}")

    def test_multiclass_proficiencies(self):
        """Multiclass proficiency'leri donmeli"""
        profs = self.get_profs("Fighter")
        self.assertIn("armor", profs)
        self.assertIn("weapons", profs)

        profs_wiz = self.get_profs("Wizard")
        self.assertEqual(profs_wiz.get("armor", []), [])

    def test_multiclass_spell_slots_single_caster(self):
        """Tek sinif full caster spell slots"""
        slots = self.calc_slots({"Wizard": 5})
        self.assertEqual(slots.get(1), 4)
        self.assertEqual(slots.get(2), 3)
        self.assertEqual(slots.get(3), 2)

    def test_multiclass_spell_slots_mixed(self):
        """Karisik sinif spell slots"""
        # Wizard 5 + Cleric 3 = caster level 8
        slots = self.calc_slots({"Wizard": 5, "Cleric": 3})
        self.assertEqual(slots.get(1), 4)
        self.assertEqual(slots.get(2), 3)
        self.assertEqual(slots.get(3), 3)
        self.assertEqual(slots.get(4), 2)

    def test_multiclass_spell_slots_half_caster(self):
        """Half caster spell slot hesaplama"""
        # Paladin 6 = caster level 3
        slots = self.calc_slots({"Paladin": 6})
        self.assertEqual(slots.get(1), 4)
        self.assertEqual(slots.get(2), 2)

    def test_multiclass_hp(self):
        """Multiclass HP hesaplama"""
        # Fighter (d10) 5 + Wizard (d6) 3, CON mod +2
        hp = self.calc_hp({"Fighter": 5, "Wizard": 3}, con_modifier=2)
        # Fighter 1st: 10+2=12, Fighter 2-5: 4*(6+2)=32, Wizard 1-3: 3*(4+2)=18 = 62
        self.assertEqual(hp, 62)

    def test_multiclass_hit_dice(self):
        """Hit dice gosterimi"""
        display = self.calc_hit_dice({"Fighter": 5, "Wizard": 3})
        self.assertEqual(display, "5d10 + 3d6")

    def test_apply_multiclass_level(self):
        """apply_multiclass_level dogru calisir"""
        char = {
            "class": "Fighter",
            "level": 5,
            "abilities": {"Strength": 16, "Dexterity": 14, "Constitution": 14,
                          "Intelligence": 13, "Wisdom": 10, "Charisma": 8}
        }
        result = self.apply_mc(char, "Wizard")
        self.assertTrue(result.get("is_multiclass"))
        self.assertEqual(result["level"], 6)
        self.assertEqual(result["class_levels"]["Fighter"], 5)
        self.assertEqual(result["class_levels"]["Wizard"], 1)
        self.assertIn("Fighter 5", result.get("class_display", ""))

    def test_get_available_options(self):
        """Mevcut multiclass secenekleri"""
        char = {
            "class": "Fighter",
            "abilities": {"Strength": 16, "Dexterity": 14, "Constitution": 14,
                          "Intelligence": 13, "Wisdom": 10, "Charisma": 8}
        }
        options = self.get_options(char)
        self.assertTrue(len(options) > 0)
        # Fighter kendisi listede olmamali
        class_names = [o["class"] for o in options]
        self.assertNotIn("Fighter", class_names)

    def test_total_character_level(self):
        """Toplam seviye hesaplama"""
        char = {"class_levels": {"Fighter": 5, "Wizard": 3}, "level": 8}
        self.assertEqual(self.get_total(char), 8)

        char2 = {"level": 5}
        self.assertEqual(self.get_total(char2), 5)

    def test_all_classes_have_hit_dice(self):
        """Tum siniflar hit dice tablosunda olmali"""
        for cls in self.PREREQS:
            self.assertIn(cls, self.HIT_DICE, f"{cls} hit dice tablosunda yok")


# ============================================================================
# SUBCLASS TESTLERI
# ============================================================================

class TestSubclassData(unittest.TestCase):
    """Subclass veri testleri"""

    def setUp(self):
        from utils.subclass_data import (
            get_subclass_level, get_subclass_feature_name,
            get_subclass_options, needs_subclass_selection,
            SUBCLASS_LEVEL, SUBCLASS_OPTIONS
        )
        self.get_level = get_subclass_level
        self.get_name = get_subclass_feature_name
        self.get_options = get_subclass_options
        self.needs_selection = needs_subclass_selection
        self.LEVELS = SUBCLASS_LEVEL
        self.OPTIONS = SUBCLASS_OPTIONS

    def test_all_classes_have_subclass_level(self):
        """Her sinifin subclass seviyesi olmali"""
        for cls in ["Barbarian", "Bard", "Cleric", "Druid", "Fighter",
                     "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
                     "Warlock", "Wizard"]:
            level = self.get_level(cls)
            self.assertIn(level, [1, 2, 3], f"{cls} subclass seviyesi hatali: {level}")

    def test_all_classes_have_options(self):
        """Her sinifin subclass secenekleri olmali"""
        for cls in self.LEVELS:
            if cls in self.OPTIONS:
                options = self.get_options(cls)
                self.assertTrue(len(options) >= 2, f"{cls} en az 2 subclass secenegi olmali")
                for opt in options:
                    self.assertIn("name", opt)
                    self.assertIn("description", opt)

    def test_needs_subclass_at_correct_level(self):
        """Dogru seviyede subclass gereksinimi"""
        # Barbarian 3. seviye, subclass yok
        char = {"class": "Barbarian", "level": 3, "subclass": ""}
        self.assertTrue(self.needs_selection(char))

        # Barbarian 2. seviye
        char2 = {"class": "Barbarian", "level": 2, "subclass": ""}
        self.assertFalse(self.needs_selection(char2))

        # Barbarian 3. seviye, subclass zaten var
        char3 = {"class": "Barbarian", "level": 3, "subclass": "Path of the Berserker"}
        self.assertFalse(self.needs_selection(char3))

    def test_cleric_subclass_at_level_1(self):
        """Cleric 1. seviyede subclass secmeli"""
        level = self.get_level("Cleric")
        self.assertEqual(level, 1)

    def test_wizard_subclass_at_level_2(self):
        """Wizard 2. seviyede subclass secmeli"""
        level = self.get_level("Wizard")
        self.assertEqual(level, 2)

    def test_feature_names(self):
        """Feature isimleri dogru olmali"""
        self.assertEqual(self.get_name("Barbarian"), "Primal Path")
        self.assertEqual(self.get_name("Wizard"), "Arcane Tradition")
        self.assertEqual(self.get_name("Rogue"), "Roguish Archetype")


# ============================================================================
# CONDITION/STATUS EFFECT TESTLERI
# ============================================================================

class TestConditions(unittest.TestCase):
    """Condition sistemi testleri"""

    def setUp(self):
        from utils.conditions import (
            get_all_conditions, get_condition, get_conditions_by_category,
            add_condition_to_character, remove_condition_from_character,
            get_active_conditions, get_condition_summary, CONDITIONS
        )
        self.get_all = get_all_conditions
        self.get_one = get_condition
        self.by_category = get_conditions_by_category
        self.add_cond = add_condition_to_character
        self.remove_cond = remove_condition_from_character
        self.get_active = get_active_conditions
        self.get_summary = get_condition_summary
        self.CONDITIONS = CONDITIONS

    def test_all_standard_conditions_exist(self):
        """Tum standart D&D 5e condition'lari olmali"""
        required = ["Blinded", "Charmed", "Deafened", "Exhaustion", "Frightened",
                     "Grappled", "Incapacitated", "Invisible", "Paralyzed",
                     "Petrified", "Poisoned", "Prone", "Restrained", "Stunned",
                     "Unconscious"]
        for cond in required:
            self.assertIn(cond, self.CONDITIONS, f"{cond} eksik")

    def test_condition_has_required_fields(self):
        """Her condition gerekli alanlara sahip olmali"""
        for name, data in self.CONDITIONS.items():
            self.assertIn("name", data, f"{name}: name eksik")
            self.assertIn("icon", data, f"{name}: icon eksik")
            self.assertIn("description", data, f"{name}: description eksik")
            self.assertIn("effects", data, f"{name}: effects eksik")
            self.assertIsInstance(data["effects"], list)

    def test_add_condition(self):
        """Condition ekleme"""
        char = {"name": "Test", "active_conditions": []}
        self.add_cond(char, "Poisoned", duration="1 dakika")
        self.assertEqual(len(char["active_conditions"]), 1)
        self.assertEqual(char["active_conditions"][0]["name"], "Poisoned")

    def test_add_duplicate_condition(self):
        """Ayni condition iki kez eklenmemeli"""
        char = {"name": "Test", "active_conditions": []}
        self.add_cond(char, "Poisoned")
        self.add_cond(char, "Poisoned")
        self.assertEqual(len(char["active_conditions"]), 1)

    def test_remove_condition(self):
        """Condition kaldirma"""
        char = {"name": "Test", "active_conditions": []}
        self.add_cond(char, "Poisoned")
        self.add_cond(char, "Blinded")
        self.remove_cond(char, "Poisoned")
        self.assertEqual(len(char["active_conditions"]), 1)
        self.assertEqual(char["active_conditions"][0]["name"], "Blinded")

    def test_exhaustion_levels(self):
        """Exhaustion seviye sistemi"""
        char = {"name": "Test", "active_conditions": []}
        self.add_cond(char, "Exhaustion", level=3)
        self.assertEqual(char["active_conditions"][0]["level"], 3)

    def test_get_active_conditions_with_details(self):
        """Aktif condition'lar detay ile donmeli"""
        char = {"name": "Test", "active_conditions": []}
        self.add_cond(char, "Poisoned")
        active = self.get_active(char)
        self.assertEqual(len(active), 1)
        self.assertIn("icon", active[0])
        self.assertIn("effects", active[0])
        self.assertEqual(active[0]["icon"], "🤢")

    def test_condition_summary(self):
        """Condition ozet metni"""
        char = {"name": "Test", "active_conditions": []}
        self.add_cond(char, "Poisoned")
        self.add_cond(char, "Frightened")
        summary = self.get_summary(char)
        self.assertIn("Poisoned", summary)
        self.assertIn("Frightened", summary)

    def test_empty_summary(self):
        """Bos condition ozeti"""
        char = {"name": "Test"}
        summary = self.get_summary(char)
        self.assertEqual(summary, "Aktif durum efekti yok.")

    def test_categories(self):
        """Kategori filtreleme"""
        physical = self.by_category("physical")
        self.assertIn("Poisoned", physical)
        self.assertIn("Prone", physical)

        mental = self.by_category("mental")
        self.assertIn("Charmed", mental)
        self.assertIn("Frightened", mental)


# ============================================================================
# PATHFINDER SPELL TEMIZLEME TESTLERI
# ============================================================================

class TestPathfinderSpellCleaning(unittest.TestCase):
    """Pathfinder spell veri temizleme testleri"""

    def test_clean_spell_data(self):
        """Bozuk spell verisini temizleme"""
        from utils.pathfinder_scraper import clean_spell_data

        bozuk_spell = {
            "level": 1,
            "school": "abjuration",
            "subschool": "",
            "descriptor": "",
            "casting_time": "1 standard actionComponents V, S, M (a rabbit's foot)EffectRange personal Target youDuration 1 round/level",
            "components": "V, S, M (a rabbit's foot)EffectRange personal",
            "range": "personal Target youDuration 1 round",
            "target": "youDuration 1 round/level",
            "duration": "1 round/levelSaving Throw noneDescription some text",
            "saving_throw": "",
            "spell_resistance": "",
            "description": "Some spell description",
            "levels_by_class": {"Wizard": 1, "Time": 1, "Touchedduration": 1}
        }

        cleaned = clean_spell_data(bozuk_spell)

        # Casting time kisa olmali
        self.assertTrue(len(cleaned["casting_time"]) < 50, f"casting_time hala uzun: {cleaned['casting_time']}")

        # Bozuk class key'leri temizlenmis olmali
        self.assertIn("Wizard", cleaned["levels_by_class"])
        self.assertNotIn("Time", cleaned["levels_by_class"])
        self.assertNotIn("Touchedduration", cleaned["levels_by_class"])

    def test_core_spells_exist(self):
        """Core spell'ler mevcut olmali"""
        from utils.pathfinder_scraper import CORE_PF1E_SPELLS

        self.assertIn("Magic Missile", CORE_PF1E_SPELLS)
        self.assertIn("Fireball", CORE_PF1E_SPELLS)
        self.assertIn("Wish", CORE_PF1E_SPELLS)

        # Her spell gerekli alanlara sahip olmali
        for name, spell in CORE_PF1E_SPELLS.items():
            self.assertIn("level", spell, f"{name}: level eksik")
            self.assertIn("school", spell, f"{name}: school eksik")
            self.assertIn("description", spell, f"{name}: description eksik")
            self.assertIn("casting_time", spell, f"{name}: casting_time eksik")

    def test_core_spells_level_range(self):
        """Core spell'ler 0-9 araliginda olmali"""
        from utils.pathfinder_scraper import CORE_PF1E_SPELLS
        for name, spell in CORE_PF1E_SPELLS.items():
            self.assertIn(spell["level"], range(10), f"{name} level hatali: {spell['level']}")


# ============================================================================
# VALIDATION TESTLERI (MULTICLASS DAHIL)
# ============================================================================

class TestValidation(unittest.TestCase):
    """Karakter validasyon testleri"""

    def setUp(self):
        from creators.pathfinder1e_creator import Pathfinder1ECreator
        self.creator = Pathfinder1ECreator()

    def test_valid_character(self):
        """Gecerli karakter hatasiz donmeli"""
        char = {
            "name": "Test Fighter",
            "race": "Human",
            "class": "Fighter",
            "level": 5,
            "abilities": {"strength": 16, "dexterity": 14, "constitution": 15,
                          "intelligence": 10, "wisdom": 12, "charisma": 8},
            "bab": 5,
            "saves": {"fortitude": 4, "reflex": 1, "will": 1}
        }
        errors = self.creator.validate_character(char)
        # Sadece warning'ler olabilir, error olmamali
        real_errors = [e for e in errors if not e.startswith("[UYARI]")]
        self.assertEqual(len(real_errors), 0, f"Errors: {real_errors}")

    def test_multiclass_validation(self):
        """Multiclass karakter validasyonu"""
        char = {
            "name": "MC Test",
            "race": "Human",
            "class": "Fighter",
            "level": 8,
            "is_multiclass": True,
            "class_levels": {"Fighter": 5, "Wizard": 3},
            "abilities": {"strength": 16, "dexterity": 14, "constitution": 15,
                          "intelligence": 13, "wisdom": 10, "charisma": 8},
            "bab": 6,
            "saves": {"fortitude": 5, "reflex": 2, "will": 4}
        }
        errors = self.creator.validate_character(char)
        # Multiclass tutarli - class_levels toplami = level
        mc_errors = [e for e in errors if "Multiclass toplam seviye" in e]
        self.assertEqual(len(mc_errors), 0, f"MC level tutarsizligi: {mc_errors}")

    def test_multiclass_level_mismatch(self):
        """Multiclass seviye tutarsizligi uyari vermeli"""
        char = {
            "name": "MC Bad",
            "race": "Human",
            "class": "Fighter",
            "level": 10,  # Toplam 10 ama class_levels 8
            "is_multiclass": True,
            "class_levels": {"Fighter": 5, "Wizard": 3},
            "abilities": {"strength": 16, "dexterity": 14, "constitution": 15,
                          "intelligence": 13, "wisdom": 10, "charisma": 8},
        }
        errors = self.creator.validate_character(char)
        mc_warnings = [e for e in errors if "Multiclass toplam seviye" in e]
        self.assertTrue(len(mc_warnings) > 0, "Level tutarsizligi uyarisi olmali")


# ============================================================================
# CALCULATIONS (MULTICLASS) TESTLERI
# ============================================================================

class TestCalculationsMulticlass(unittest.TestCase):
    """Hesaplama fonksiyonlari multiclass testleri"""

    def test_calculate_all_dnd_stats_multiclass(self):
        """calculate_all_dnd_stats multiclass destegiyle calismali"""
        from utils.calculations import calculate_all_dnd_stats

        char = {
            "class": "Fighter",
            "level": 8,
            "is_multiclass": True,
            "class_levels": {"Fighter": 5, "Wizard": 3},
            "abilities": {"Strength": 16, "Dexterity": 14, "Constitution": 15,
                          "Intelligence": 13, "Wisdom": 10, "Charisma": 8}
        }
        stats = calculate_all_dnd_stats(char)
        self.assertEqual(stats["proficiency_bonus"], 3)  # Level 8 = +3
        self.assertIn("hit_dice", stats)
        # Multiclass hit dice "5d10 + 3d6" olmali
        self.assertIn("d10", stats["hit_dice"])
        self.assertIn("d6", stats["hit_dice"])

    def test_calculate_all_dnd_stats_single_class(self):
        """Normal karakter hesaplama calisir"""
        from utils.calculations import calculate_all_dnd_stats

        char = {
            "class": "Fighter",
            "level": 5,
            "abilities": {"Strength": 16, "Dexterity": 14, "Constitution": 15,
                          "Intelligence": 10, "Wisdom": 12, "Charisma": 8}
        }
        stats = calculate_all_dnd_stats(char)
        self.assertEqual(stats["proficiency_bonus"], 3)
        self.assertIn("skills", stats)
        self.assertIn("initiative", stats)


# ============================================================================
# ENCOUNTER TRACKER TESTLERI
# ============================================================================

class TestEncounterTracker(unittest.TestCase):
    """Encounter Tracker testleri - tum sistemler"""

    def setUp(self):
        from utils.encounter_tracker import EncounterTracker, Combatant, SYSTEM_RULES
        self.EncounterTracker = EncounterTracker
        self.Combatant = Combatant
        self.SYSTEM_RULES = SYSTEM_RULES

    def test_system_rules_exist_for_all(self):
        """Tum sistemlerin kurallari tanimli"""
        for system in ["dnd5e", "pathfinder1e", "mm3e"]:
            self.assertIn(system, self.SYSTEM_RULES)
            self.assertIn("name", self.SYSTEM_RULES[system])
            self.assertIn("initiative_stat", self.SYSTEM_RULES[system])

    def test_add_and_sort_combatants(self):
        """Katilimci ekleme ve initiative siralama"""
        tracker = self.EncounterTracker("dnd5e")
        c1 = self.Combatant(name="Fighter", initiative=15, max_hp=40, current_hp=40)
        c2 = self.Combatant(name="Wizard", initiative=20, max_hp=20, current_hp=20)
        c3 = self.Combatant(name="Goblin", initiative=12, max_hp=7, current_hp=7, is_player=False)
        tracker.add_combatant(c1)
        tracker.add_combatant(c2)
        tracker.add_combatant(c3)
        tracker.sort_by_initiative()
        self.assertEqual(tracker.combatants[0].name, "Wizard")
        self.assertEqual(tracker.combatants[1].name, "Fighter")
        self.assertEqual(tracker.combatants[2].name, "Goblin")

    def test_start_encounter_and_rounds(self):
        """Encounter baslama ve tur gecisi"""
        tracker = self.EncounterTracker("dnd5e")
        tracker.add_combatant(self.Combatant(name="A", initiative=20, max_hp=30, current_hp=30))
        tracker.add_combatant(self.Combatant(name="B", initiative=10, max_hp=20, current_hp=20))
        tracker.start_encounter()
        self.assertTrue(tracker.is_active)
        self.assertEqual(tracker.current_round, 1)
        self.assertEqual(tracker.get_current_combatant().name, "A")
        tracker.next_turn()
        self.assertEqual(tracker.get_current_combatant().name, "B")
        tracker.next_turn()  # Yeni round
        self.assertEqual(tracker.current_round, 2)
        self.assertEqual(tracker.get_current_combatant().name, "A")

    def test_damage_and_heal(self):
        """Hasar ve sifa mekanikleri"""
        tracker = self.EncounterTracker("dnd5e")
        tracker.add_combatant(self.Combatant(name="Hero", initiative=10, max_hp=50, current_hp=50))
        tracker.apply_damage("Hero", 20)
        self.assertEqual(tracker.combatants[0].current_hp, 30)
        tracker.apply_heal("Hero", 10)
        self.assertEqual(tracker.combatants[0].current_hp, 40)
        tracker.apply_damage("Hero", 100)
        self.assertEqual(tracker.combatants[0].current_hp, 0)  # 0'in altina dusmez
        tracker.apply_heal("Hero", 5)
        self.assertEqual(tracker.combatants[0].current_hp, 5)

    def test_remove_combatant(self):
        """Katilimci cikarma"""
        tracker = self.EncounterTracker("pathfinder1e")
        tracker.add_combatant(self.Combatant(name="PC", initiative=15))
        tracker.add_combatant(self.Combatant(name="NPC", initiative=10))
        self.assertEqual(len(tracker.combatants), 2)
        tracker.remove_combatant("NPC")
        self.assertEqual(len(tracker.combatants), 1)

    def test_combatant_conditions(self):
        """Katilimciya durum ekleme"""
        c = self.Combatant(name="Test", initiative=10)
        c.add_condition("Prone")
        c.add_condition("Blinded")
        self.assertEqual(len(c.conditions), 2)
        c.add_condition("Prone")  # Tekrar eklenmemeli
        self.assertEqual(len(c.conditions), 2)
        c.remove_condition("Prone")
        self.assertEqual(c.conditions, ["Blinded"])

    def test_from_character_dnd(self):
        """D&D karakterinden Combatant olusturma"""
        char = {
            "system": "dnd5e", "name": "Aragorn",
            "hit_points": 85, "armor_class": 17,
            "abilities": {"Dexterity": 14}
        }
        c = self.Combatant.from_character(char)
        self.assertEqual(c.name, "Aragorn")
        self.assertEqual(c.max_hp, 85)
        self.assertEqual(c.ac, 17)
        self.assertEqual(c.initiative, 2)  # (14-10)//2 = 2
        self.assertEqual(c.system, "dnd5e")

    def test_from_character_mm(self):
        """M&M karakterinden Combatant olusturma"""
        char = {
            "system": "mm3e", "name": "Captain",
            "abilities": {"Agility": 6},
            "defenses": {"Toughness": 10},
            "hero_points": 1
        }
        c = self.Combatant.from_character(char)
        self.assertEqual(c.name, "Captain")
        self.assertEqual(c.initiative, 6)

    def test_serialize_deserialize(self):
        """Tracker kaydetme ve yukleme"""
        tracker = self.EncounterTracker("dnd5e")
        tracker.add_combatant(self.Combatant(name="Test", initiative=15, max_hp=30, current_hp=30))
        tracker.start_encounter()
        data = tracker.to_dict()
        loaded = self.EncounterTracker.from_dict(data)
        self.assertEqual(len(loaded.combatants), 1)
        self.assertEqual(loaded.combatants[0].name, "Test")
        self.assertTrue(loaded.is_active)

    def test_end_encounter(self):
        """Encounter bitirme"""
        tracker = self.EncounterTracker("dnd5e")
        tracker.add_combatant(self.Combatant(name="A", initiative=10))
        tracker.start_encounter()
        self.assertTrue(tracker.is_active)
        tracker.end_encounter()
        self.assertFalse(tracker.is_active)

    def test_log_entries(self):
        """Log kayitlari tutulur"""
        tracker = self.EncounterTracker("dnd5e")
        tracker.add_combatant(self.Combatant(name="Hero", initiative=10, max_hp=50, current_hp=50))
        tracker.start_encounter()
        tracker.apply_damage("Hero", 10)
        self.assertTrue(len(tracker.log) > 0)


# ============================================================================
# HOMEBREW TESTLERI
# ============================================================================

class TestHomebrew(unittest.TestCase):
    """Homebrew sistemi testleri - tum sistemler"""

    def test_templates_exist_for_all_systems(self):
        """Tum sistemler icin homebrew sablonlari var"""
        from utils.homebrew import HOMEBREW_TEMPLATES, get_homebrew_types
        for system in ["dnd5e", "pathfinder1e", "mm3e"]:
            self.assertIn(system, HOMEBREW_TEMPLATES)
            types = get_homebrew_types(system)
            self.assertTrue(len(types) > 0, f"{system} icin homebrew turleri bos")

    def test_dnd5e_types(self):
        """D&D 5e homebrew turleri dogru"""
        from utils.homebrew import get_homebrew_types
        types = get_homebrew_types("dnd5e")
        self.assertIn("race", types)
        self.assertIn("class", types)
        self.assertIn("spell", types)
        self.assertIn("feat", types)
        self.assertIn("item", types)
        self.assertIn("background", types)

    def test_mm3e_types(self):
        """M&M 3e homebrew turleri dogru"""
        from utils.homebrew import get_homebrew_types
        types = get_homebrew_types("mm3e")
        self.assertIn("power", types)
        self.assertIn("advantage", types)
        self.assertIn("archetype", types)

    def test_get_template(self):
        """Sablon getirme calisiyor"""
        from utils.homebrew import get_homebrew_template
        template = get_homebrew_template("dnd5e", "spell")
        self.assertIn("name", template)
        self.assertIn("level", template)
        self.assertIn("school", template)
        self.assertEqual(template["name"], "")

    def test_validate_homebrew_missing_fields(self):
        """Zorunlu alan eksik oldugunda hata doner"""
        from utils.homebrew import validate_homebrew
        errors = validate_homebrew("dnd5e", "spell", {"level": 3})
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any("name" in e for e in errors))

    def test_validate_homebrew_valid(self):
        """Dogru veri hata donmez"""
        from utils.homebrew import validate_homebrew
        errors = validate_homebrew("dnd5e", "spell", {"name": "Fireball+", "level": 3, "school": "evocation"})
        self.assertEqual(len(errors), 0)

    def test_save_and_load_homebrew(self):
        """Homebrew kaydetme ve yukleme"""
        import tempfile
        import shutil
        from utils.homebrew import save_homebrew, load_all_homebrew, HOMEBREW_DIR

        # Gecici dizin kullan
        original_dir = HOMEBREW_DIR
        # Save test
        data = {"name": "Test Spell", "level": 1, "school": "evocation"}
        filepath = save_homebrew("dnd5e", "spell", data)
        self.assertTrue(filepath.exists())

        # Load test
        loaded = load_all_homebrew("dnd5e")
        found = False
        for key, items in loaded.items():
            for item in items:
                if item.get("name") == "Test Spell":
                    found = True
                    break
        self.assertTrue(found)

        # Temizle
        filepath.unlink(missing_ok=True)

    def test_inject_homebrew(self):
        """Homebrew verinin sistem verisine enjeksiyonu"""
        from utils.homebrew import inject_homebrew_into_data
        system_data = {"races": {"Elf": {}}, "spells": {}}
        # Inject (henuz homebrew yoksa bos kalir)
        result = inject_homebrew_into_data(system_data, "dnd5e")
        self.assertIn("races", result)


# ============================================================================
# PORTRAIT TESTLERI
# ============================================================================

class TestPortraits(unittest.TestCase):
    """Karakter portresi testleri"""

    def test_portrait_path_generation(self):
        """Portre yolu olusturma"""
        from utils.portraits import get_portrait_path
        path = get_portrait_path("Test Character", "dnd5e")
        self.assertIn("dnd5e_test_character", str(path))

    def test_portrait_path_different_systems(self):
        """Farkli sistemler icin farkli yollar"""
        from utils.portraits import get_portrait_path
        dnd = get_portrait_path("Hero", "dnd5e")
        mm = get_portrait_path("Hero", "mm3e")
        self.assertNotEqual(dnd, mm)

    def test_validate_nonexistent_file(self):
        """Olmayan dosya icin hata"""
        from utils.portraits import validate_portrait_file
        errors = validate_portrait_file("/nonexistent/file.png")
        self.assertTrue(len(errors) > 0)

    def test_display_sizes_per_system(self):
        """Her sistem icin farkli boyutlar"""
        from utils.portraits import get_display_size, get_thumbnail_size
        for system in ["dnd5e", "pathfinder1e", "mm3e"]:
            size = get_display_size(system)
            self.assertEqual(len(size), 2)
            thumb = get_thumbnail_size(system)
            self.assertEqual(len(thumb), 2)

    def test_has_portrait_false(self):
        """Portresi olmayan karakter icin False"""
        from utils.portraits import has_portrait
        self.assertFalse(has_portrait("nonexistent_character_xyz", "dnd5e"))

    def test_character_portrait_metadata(self):
        """Karakter verisine portre bilgisi ekleme"""
        from utils.portraits import set_portrait_on_character, get_portrait_from_character
        char = {"name": "Test"}
        char = set_portrait_on_character(char, "/path/to/image.png")
        self.assertEqual(get_portrait_from_character(char), "/path/to/image.png")

    def test_allowed_extensions(self):
        """Desteklenen dosya formatlari"""
        from utils.portraits import ALLOWED_EXTENSIONS
        self.assertIn(".png", ALLOWED_EXTENSIONS)
        self.assertIn(".jpg", ALLOWED_EXTENSIONS)
        self.assertIn(".jpeg", ALLOWED_EXTENSIONS)
        self.assertIn(".webp", ALLOWED_EXTENSIONS)


# ============================================================================
# HTML EXPORT TESTLERI
# ============================================================================

class TestHTMLExport(unittest.TestCase):
    """HTML export testleri - tum sistemler"""

    def test_normalize_system(self):
        """Sistem normalizasyonu"""
        from utils.export_html import _normalize_system
        self.assertEqual(_normalize_system("dnd5e"), "dnd5e")
        self.assertEqual(_normalize_system("D&D"), "dnd5e")
        self.assertEqual(_normalize_system("pathfinder"), "pathfinder1e")
        self.assertEqual(_normalize_system("MutantsAndMasterminds3e"), "mm3e")

    def test_system_themes(self):
        """Tum sistemler icin temalar tanimli"""
        from utils.export_html import SYSTEM_THEMES
        for system in ["dnd5e", "pathfinder1e", "mm3e"]:
            self.assertIn(system, SYSTEM_THEMES)
            self.assertIn("accent", SYSTEM_THEMES[system])

    def test_dnd5e_export(self):
        """D&D 5e HTML export"""
        from utils.export_html import export_character_html
        char = {
            "system": "dnd5e", "name": "Test Fighter",
            "race": "Human", "class": "Fighter", "level": 5,
            "abilities": {"Strength": 16, "Dexterity": 14, "Constitution": 15,
                          "Intelligence": 10, "Wisdom": 12, "Charisma": 8},
            "hit_points": 44, "armor_class": 18,
        }
        filepath = export_character_html(char, "test_dnd5e_export")
        self.assertTrue(filepath.exists())
        content = filepath.read_text(encoding="utf-8")
        self.assertIn("Test Fighter", content)
        self.assertIn("Fighter", content)
        self.assertIn("Human", content)
        filepath.unlink(missing_ok=True)

    def test_mm3e_export(self):
        """M&M 3e HTML export"""
        from utils.export_html import export_character_html
        char = {
            "system": "mm3e", "name": "Test Hero",
            "pl_value": 10, "archetype": "Powerhouse",
            "total_power_points": 150, "remaining_power_points": 5,
            "abilities": {"Strength": 8, "Agility": 4},
            "defenses": {"Toughness": 12, "Dodge": 8},
        }
        filepath = export_character_html(char, "test_mm3e_export")
        self.assertTrue(filepath.exists())
        content = filepath.read_text(encoding="utf-8")
        self.assertIn("Test Hero", content)
        self.assertIn("PL 10", content)
        filepath.unlink(missing_ok=True)

    def test_pathfinder1e_export(self):
        """Pathfinder 1e HTML export"""
        from utils.export_html import export_character_html
        char = {
            "system": "pathfinder1e", "name": "Test Ranger",
            "race": "Elf", "class": "Ranger", "level": 5,
            "abilities": {"Strength": 14, "Dexterity": 18, "Constitution": 12,
                          "Intelligence": 10, "Wisdom": 14, "Charisma": 8},
            "hit_points": 38, "armor_class": 18,
        }
        filepath = export_character_html(char, "test_pf1e_export")
        self.assertTrue(filepath.exists())
        content = filepath.read_text(encoding="utf-8")
        self.assertIn("Test Ranger", content)
        self.assertIn("Elf", content)
        filepath.unlink(missing_ok=True)

    def test_html_has_responsive_css(self):
        """HTML responsive CSS iceriyor"""
        from utils.export_html import export_character_html
        char = {"system": "dnd5e", "name": "CSS Test", "race": "Elf",
                "class": "Wizard", "level": 1, "abilities": {}}
        filepath = export_character_html(char, "test_css_check")
        content = filepath.read_text(encoding="utf-8")
        self.assertIn("@media", content)
        self.assertIn("grid", content)
        filepath.unlink(missing_ok=True)


class TestPDFExportAcroForm(unittest.TestCase):
    """Test class for verifying AcroForm PDF exports"""

    def setUp(self):
        import tempfile
        self.dnd_char = {
            "name": "Aragorn",
            "system": "DND5E",
            "class": "Ranger",
            "level": 5,
            "race": "Human",
            "background": "Outlander",
            "experience": 6500,
            "armor_class": 16,
            "hit_points": 45,
            "abilities": {"Strength": 16, "Dexterity": 14, "Constitution": 15, "Intelligence": 10, "Wisdom": 13, "Charisma": 8},
            "modifiers": {"strength": 3, "dexterity": 2, "constitution": 2, "intelligence": 0, "wisdom": 1, "charisma": -1},
            "saving_throws": {"Strength": 5, "Dexterity": 4},
            "skills": {"Acrobatics": 4, "Survival": 3},
            "equipment": ["Longsword", "Scale Mail"],
            "feats": ["Sharpshooter"]
        }
        self.pf_char = {
            "name": "Valeros",
            "system": "PATHFINDER1E",
            "class": "Fighter",
            "level": 1,
            "race": "Human",
            "abilities": {"Strength": 18, "Dexterity": 15, "Constitution": 14, "Intelligence": 12, "Wisdom": 10, "Charisma": 8},
            "modifiers": {"strength": 4, "dexterity": 2, "constitution": 2, "intelligence": 1, "wisdom": 0, "charisma": -1},
            "hit_points": 12,
            "armor_class": 16,
            "initiative": 2,
            "bab": 1,
            "saves": {"fortitude": 4, "reflex": 2, "will": 0}
        }
        self.mm_char = {
            "name": "Sentinel",
            "system": "MM3E",
            "pl_value": 10,
            "archetype": "Powerhouse",
            "abilities": {"strength": 12, "stamina": 10}
        }
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_dnd_pdf(self):
        from utils.export_pdf import export_dnd_character_pdf
        out_path = self.temp_dir / "aragorn.pdf"
        export_dnd_character_pdf(self.dnd_char, out_path)
        self.assertTrue(out_path.exists())
        self.assertGreater(out_path.stat().st_size, 0)

    def test_export_pf_pdf(self):
        from utils.export_pdf import export_pf1e_character_pdf
        out_path = self.temp_dir / "valeros.pdf"
        export_pf1e_character_pdf(self.pf_char, out_path)
        self.assertTrue(out_path.exists())
        self.assertGreater(out_path.stat().st_size, 0)

    def test_export_mm_pdf(self):
        from utils.export_pdf import export_mm_character_pdf
        out_path = self.temp_dir / "sentinel.pdf"
        export_mm_character_pdf(self.mm_char, out_path)
        self.assertTrue(out_path.exists())
        self.assertGreater(out_path.stat().st_size, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

