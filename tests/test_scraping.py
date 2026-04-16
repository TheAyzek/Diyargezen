"""
Scraping Pipeline Testleri
===========================
Pydantic modelleri, base_scraper yardimcilari ve tum spider'lari test eder.
Ag baglantisi gerektirmez — tum testler offline calisir.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scraping.models import (
    RaceModel, ClassModel, SpellModel, FeatModel,
    PowerModel, AdvantageModel, ClanModel, DisciplineModel,
    SystemDataBundle, AbilityScoreBonus, SourceReference,
)
from scraping.base_scraper import sanitize_html, BaseScraper


# ======================================================================
# Pydantic Model Testleri — Temel Modeller
# ======================================================================

class TestRaceModel(unittest.TestCase):

    def test_valid_race(self):
        race = RaceModel(
            name="Dwarf", system="pathfinder1e",
            ability_score_increase={"constitution": 2, "wisdom": 2, "charisma": -2},
            speed=20, traits=["Darkvision", "Hardy"],
        )
        self.assertEqual(race.name, "Dwarf")
        self.assertEqual(race.speed, 20)
        self.assertEqual(race.ability_score_increase["constitution"], 2)

    def test_size_normalization(self):
        self.assertEqual(RaceModel(name="Halfling", system="dnd5e", size="s").size, "Small")
        self.assertEqual(RaceModel(name="Half-Orc", system="dnd5e", size="MEDIUM").size, "Medium")

    def test_system_normalization(self):
        self.assertEqual(RaceModel(name="Elf", system=" Pathfinder 1e ").system, "pathfinder1e")

    def test_missing_name_raises(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            RaceModel(name="", system="dnd5e")

    def test_negative_speed_raises(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            RaceModel(name="Bad", system="dnd5e", speed=-10)

    def test_model_dump_roundtrip(self):
        data = {"name": "Human", "system": "dnd5e", "speed": 30, "traits": ["Versatile"]}
        race = RaceModel.model_validate(data)
        dumped = race.model_dump()
        self.assertEqual(dumped["name"], "Human")
        self.assertIsInstance(dumped["traits"], list)


class TestClassModel(unittest.TestCase):

    def test_valid_class(self):
        cls = ClassModel(
            name="Fighter", system="pathfinder1e", hit_die="d10",
            saving_throws=["Fortitude"], spellcasting=False,
        )
        self.assertEqual(cls.hit_die, "d10")
        self.assertFalse(cls.spellcasting)

    def test_hit_die_normalization(self):
        self.assertEqual(ClassModel(name="Wizard", system="dnd5e", hit_die="6").hit_die, "d6")

    def test_features_dict(self):
        cls = ClassModel(
            name="Barbarian", system="pathfinder1e",
            features={"1": ["Fast Movement", "Rage"], "2": ["Uncanny Dodge"]},
        )
        self.assertEqual(len(cls.features["1"]), 2)


class TestSpellModel(unittest.TestCase):

    def test_valid_spell(self):
        spell = SpellModel(
            name="Fireball", system="pathfinder1e", level=3, school="evocation",
            levels_by_class={"Sorcerer": 3, "Wizard": 3},
        )
        self.assertEqual(spell.level, 3)
        self.assertEqual(spell.school, "evocation")

    def test_school_normalization(self):
        self.assertEqual(SpellModel(name="Shield", system="dnd5e", school="Abjuration").school, "abjuration")

    def test_level_range_validation(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            SpellModel(name="Bad", system="dnd5e", level=10)

    def test_dnd5e_spell_fields(self):
        spell = SpellModel(
            name="Detect Magic", system="dnd5e", level=1,
            is_ritual=True, concentration=True, higher_levels="At higher levels...",
        )
        self.assertTrue(spell.is_ritual)
        self.assertTrue(spell.concentration)


class TestFeatModel(unittest.TestCase):

    def test_valid_feat(self):
        feat = FeatModel(
            name="Power Attack", system="pathfinder1e", feat_type="Combat",
            prerequisites=["Str 13", "BAB +1"],
        )
        self.assertEqual(feat.feat_type, "Combat")
        self.assertEqual(len(feat.prerequisites), 2)


# ======================================================================
# Pydantic Model Testleri — M&M 3e Modelleri
# ======================================================================

class TestPowerModel(unittest.TestCase):

    def test_valid_power(self):
        power = PowerModel(
            name="Blast", system="mm3e", cost_per_rank=2,
            action="Standard", range="Ranged", duration="Instant",
            description="Ranged damage effect.",
        )
        self.assertEqual(power.name, "Blast")
        self.assertEqual(power.cost_per_rank, 2)

    def test_default_system(self):
        self.assertEqual(PowerModel(name="Flight").system, "mm3e")

    def test_extras_and_flaws(self):
        power = PowerModel(
            name="Affliction", extras=["Extra Condition", "Cumulative"],
            flaws=["Limited Degree"],
        )
        self.assertEqual(len(power.extras), 2)
        self.assertEqual(len(power.flaws), 1)


class TestAdvantageModel(unittest.TestCase):

    def test_valid_advantage(self):
        adv = AdvantageModel(
            name="Defensive Roll", cost="1 per rank",
            advantage_type="Combat", ranked=True,
        )
        self.assertEqual(adv.advantage_type, "Combat")
        self.assertTrue(adv.ranked)

    def test_default_system(self):
        self.assertEqual(AdvantageModel(name="Luck").system, "mm3e")


# ======================================================================
# Pydantic Model Testleri — VtM 5e Modelleri
# ======================================================================

class TestClanModel(unittest.TestCase):

    def test_valid_clan(self):
        clan = ClanModel(
            name="Brujah", system="vtm5e",
            disciplines=["Celerity", "Potence", "Presence"],
            bane="Quick to anger", compulsion="Rage",
            favored_attributes=["Strength", "Charisma"],
        )
        self.assertEqual(clan.name, "Brujah")
        self.assertEqual(len(clan.disciplines), 3)
        self.assertIn("Celerity", clan.disciplines)

    def test_default_system(self):
        self.assertEqual(ClanModel(name="Nosferatu").system, "vtm5e")


class TestDisciplineModel(unittest.TestCase):

    def test_valid_discipline(self):
        disc = DisciplineModel(
            name="Animalism",
            powers={"1": "Bond Famulus", "2": "Sense the Beast", "3": "Feral Whispers"},
        )
        self.assertEqual(disc.name, "Animalism")
        self.assertEqual(disc.powers["1"], "Bond Famulus")

    def test_empty_powers(self):
        disc = DisciplineModel(name="Auspex")
        self.assertEqual(disc.powers, {})


# ======================================================================
# SystemDataBundle Testleri
# ======================================================================

class TestSystemDataBundle(unittest.TestCase):

    def test_merge_into_existing(self):
        bundle = SystemDataBundle(
            system="pathfinder1e",
            races={"Dwarf": {"speed": 20}},
            classes={"Fighter": {"hit_die": "d10"}},
        )
        existing = {"races": {"Elf": {"speed": 30}}, "spells": {"Fireball": {"level": 3}}}
        merged = bundle.merge_into(existing)
        self.assertIn("Dwarf", merged["races"])
        self.assertIn("Elf", merged["races"])
        self.assertIn("Fighter", merged["classes"])
        self.assertIn("Fireball", merged["spells"])

    def test_merge_does_not_delete(self):
        bundle = SystemDataBundle(system="dnd5e", races={"Human": {"speed": 30}})
        existing = {"races": {"Elf": {"speed": 30}}, "feats": {"Alert": {}}}
        merged = bundle.merge_into(existing)
        self.assertIn("Elf", merged["races"])
        self.assertIn("Alert", merged["feats"])

    def test_extra_merge(self):
        bundle = SystemDataBundle(
            system="vtm5e",
            extra={"clans": {"Brujah": {"bane": "Rage"}}, "disciplines": {"Celerity": {}}},
        )
        existing = {"clans": {"Nosferatu": {}}}
        merged = bundle.merge_into(existing)
        self.assertIn("Brujah", merged["clans"])
        self.assertIn("Nosferatu", merged["clans"])
        self.assertIn("Celerity", merged["disciplines"])


# ======================================================================
# HTML Sanitization Testleri
# ======================================================================

class TestSanitizeHtml(unittest.TestCase):

    def test_strips_script(self):
        result = sanitize_html('<p>Hello</p><script>alert("x")</script><p>World</p>')
        self.assertNotIn("script", result)
        self.assertIn("Hello", result)

    def test_br_to_newline(self):
        self.assertIn("Line 1\nLine 2", sanitize_html("Line 1<br>Line 2"))

    def test_html_entities(self):
        self.assertEqual(sanitize_html("5 &gt; 3 &amp; 2 &lt; 4"), "5 > 3 & 2 < 4")

    def test_empty_input(self):
        self.assertEqual(sanitize_html(""), "")
        self.assertEqual(sanitize_html(None), "")

    def test_strips_style(self):
        result = sanitize_html('<style>body{color:red}</style><p>Content</p>')
        self.assertNotIn("color", result)
        self.assertIn("Content", result)


# ======================================================================
# BaseScraper Dogrulama Testleri
# ======================================================================

class TestBaseScraperValidation(unittest.TestCase):

    def test_validate_item_success(self):
        result = BaseScraper.validate_item({"name": "Elf", "system": "dnd5e"}, RaceModel)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Elf")

    def test_validate_item_failure(self):
        self.assertIsNone(BaseScraper.validate_item({"name": "", "system": "dnd5e"}, RaceModel))

    def test_validate_batch(self):
        items = [
            {"name": "Elf", "system": "dnd5e"},
            {"name": "", "system": "dnd5e"},
            {"name": "Dwarf", "system": "pathfinder1e"},
        ]
        valid, rejected = BaseScraper.validate_batch(items, RaceModel)
        self.assertEqual(len(valid), 2)
        self.assertEqual(rejected, 1)


# ======================================================================
# JSON Save / Merge Testi
# ======================================================================

class TestSaveAndMerge(unittest.TestCase):

    def _make_dummy_spider(self, output_dir):
        class DummySpider(BaseScraper):
            SYSTEM_KEY = "test"
            BASE_URL = "http://example.com"
            def scrape(self): pass
            def scrape_races(self): return {}
            def scrape_classes(self): return {}
        return DummySpider(output_dir=output_dir)

    def test_save_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            spider = self._make_dummy_spider(Path(tmpdir))
            path = spider.save_json({"races": {"Elf": {"speed": 30}}}, "test.json")
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["races"]["Elf"]["speed"], 30)

    def test_merge_preserves_existing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            existing_file = tmppath / "data.json"
            existing_file.write_text(
                json.dumps({"system": "dnd5e", "races": {"Elf": {"speed": 30}}}),
                encoding="utf-8",
            )

            spider = self._make_dummy_spider(tmppath)
            spider.SYSTEM_KEY = "dnd5e"
            bundle = SystemDataBundle(system="dnd5e", races={"Human": {"speed": 30}})
            spider.merge_and_save(bundle, "data.json")

            loaded = json.loads(existing_file.read_text(encoding="utf-8"))
            self.assertIn("Elf", loaded["races"])
            self.assertIn("Human", loaded["races"])


# ======================================================================
# PF1e Spider Parse Testleri
# ======================================================================

class TestPF1eSpiderParsing(unittest.TestCase):

    def test_parse_ability_bonuses(self):
        from scraping.spiders.pf1e_d20pfsrd_spider import PF1eD20pfsrdSpider
        bonuses = PF1eD20pfsrdSpider._parse_ability_bonuses(
            "+2 Constitution, +2 Wisdom, -2 Charisma"
        )
        self.assertEqual(bonuses["constitution"], 2)
        self.assertEqual(bonuses["wisdom"], 2)
        self.assertEqual(bonuses["charisma"], -2)

    def test_parse_ability_bonuses_en_dash(self):
        from scraping.spiders.pf1e_d20pfsrd_spider import PF1eD20pfsrdSpider
        bonuses = PF1eD20pfsrdSpider._parse_ability_bonuses("+2 Dex, \u20132 Con")
        self.assertEqual(bonuses["dexterity"], 2)
        self.assertEqual(bonuses["constitution"], -2)

    def test_parse_ability_bonuses_empty(self):
        from scraping.spiders.pf1e_d20pfsrd_spider import PF1eD20pfsrdSpider
        self.assertEqual(PF1eD20pfsrdSpider._parse_ability_bonuses(""), {})


# ======================================================================
# D&D 5e Spider Testleri
# ======================================================================

class TestDnD5eSpider(unittest.TestCase):

    def test_extract_ability_bonuses(self):
        from scraping.spiders.dnd5e_spider import DnD5eSpider
        bonuses = DnD5eSpider._extract_ability_bonuses([
            {"ability_score": {"name": "DEX"}, "bonus": 2},
            {"ability_score": {"name": "INT"}, "bonus": 1},
        ])
        self.assertEqual(bonuses["dexterity"], 2)
        self.assertEqual(bonuses["intelligence"], 1)

    def test_extract_empty_bonuses(self):
        from scraping.spiders.dnd5e_spider import DnD5eSpider
        self.assertEqual(DnD5eSpider._extract_ability_bonuses([]), {})

    def test_map_spell(self):
        from scraping.spiders.dnd5e_spider import DnD5eSpider
        spider = DnD5eSpider.__new__(DnD5eSpider)
        result = spider._map_spell({
            "name": "Fireball",
            "level": 3,
            "school": {"name": "Evocation"},
            "casting_time": "1 action",
            "range": "150 feet",
            "duration": "Instantaneous",
            "concentration": False,
            "ritual": False,
            "desc": ["A bright streak flashes..."],
            "components": ["V", "S", "M"],
            "material": "bat guano",
            "classes": [{"name": "Sorcerer"}, {"name": "Wizard"}],
            "index": "fireball",
        })
        self.assertEqual(result["name"], "Fireball")
        self.assertEqual(result["level"], 3)
        self.assertEqual(result["school"], "evocation")
        self.assertIn("Sorcerer", result["levels_by_class"])
        self.assertIn("bat guano", result["components"])


# ======================================================================
# M&M 3e Spider Testleri
# ======================================================================

class TestMM3eSpider(unittest.TestCase):

    def test_spider_instantiation(self):
        from scraping.spiders.mm3e_spider import MM3eSpider
        spider = MM3eSpider.__new__(MM3eSpider)
        self.assertEqual(spider.SYSTEM_KEY, "mm3e")
        self.assertEqual(spider.OUTPUT_FILE, "mm_data.json")

    def test_scrape_classes_returns_empty(self):
        """M&M 3e'de geleneksel 'class' yok."""
        from scraping.spiders.mm3e_spider import MM3eSpider
        spider = MM3eSpider.__new__(MM3eSpider)
        self.assertEqual(spider.scrape_classes(), {})
        self.assertEqual(spider.scrape_races(), {})


# ======================================================================
# VtM 5e Spider Testleri
# ======================================================================

class TestVtM5eSpider(unittest.TestCase):

    def test_spider_instantiation(self):
        from scraping.spiders.vtm5e_spider import VtM5eSpider
        spider = VtM5eSpider.__new__(VtM5eSpider)
        self.assertEqual(spider.SYSTEM_KEY, "vtm5e")
        self.assertEqual(spider.OUTPUT_FILE, "vtm_data.json")

    def test_known_clans_populated(self):
        from scraping.spiders.vtm5e_spider import _KNOWN_CLANS
        self.assertGreaterEqual(len(_KNOWN_CLANS), 8)
        self.assertIn("Brujah", _KNOWN_CLANS)
        self.assertIn("Nosferatu", _KNOWN_CLANS)
        self.assertIn("Ventrue", _KNOWN_CLANS)

    def test_known_disciplines_populated(self):
        from scraping.spiders.vtm5e_spider import _KNOWN_DISCIPLINES
        self.assertGreaterEqual(len(_KNOWN_DISCIPLINES), 10)
        self.assertIn("Animalism", _KNOWN_DISCIPLINES)
        self.assertIn("Dominate", _KNOWN_DISCIPLINES)
        self.assertIn("Potence", _KNOWN_DISCIPLINES)

    def test_scrape_classes_returns_empty(self):
        """VtM 5e'de geleneksel 'class' yok."""
        from scraping.spiders.vtm5e_spider import VtM5eSpider
        spider = VtM5eSpider.__new__(VtM5eSpider)
        self.assertEqual(spider.scrape_classes(), {})


# ======================================================================
# Pipeline Runner Testleri
# ======================================================================

class TestPipelineRunner(unittest.TestCase):

    def test_unknown_system_returns_empty(self):
        from scraping.run_scraper import PipelineRunner
        runner = PipelineRunner()
        result = runner.run(systems=["nonexistent_system"])
        self.assertEqual(result, {})

    def test_all_spiders_registered(self):
        from scraping.run_scraper import SPIDER_REGISTRY
        self.assertIn("pathfinder1e", SPIDER_REGISTRY)
        self.assertIn("dnd5e", SPIDER_REGISTRY)
        self.assertIn("mm3e", SPIDER_REGISTRY)
        self.assertIn("vtm5e", SPIDER_REGISTRY)
        self.assertEqual(len(SPIDER_REGISTRY), 4)

    def test_system_labels_match_registry(self):
        from scraping.run_scraper import SPIDER_REGISTRY, SYSTEM_LABELS
        for key in SPIDER_REGISTRY:
            self.assertIn(key, SYSTEM_LABELS, f"{key} label eksik")


if __name__ == "__main__":
    unittest.main()
