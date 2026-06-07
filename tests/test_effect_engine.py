"""
Evrensel Etki Motoru (Universal Effect Engine) Testleri
========================================================
EffectModel, apply_effects, smart parsers ve collect_effects testleri.
Ag baglantisi gerektirmez.
"""

from __future__ import annotations

import unittest
from copy import deepcopy

from scraping.models import (
    EffectModel, RaceModel, ClassModel, FeatModel,
    PowerModel, AdvantageModel,
)
from utils.calculations import (
    apply_effects,
    collect_effects_from_choices,
    parse_dnd5e_effect,
    parse_pf1e_effect,
    parse_mm3e_effect,
    parse_effect,
    parse_effects_batch,
)


# ======================================================================
# EffectModel Pydantic Testleri
# ======================================================================

class TestEffectModel(unittest.TestCase):

    def test_basic_creation(self):
        eff = EffectModel(target="STR", effect_type="stat_bonus", value=2)
        self.assertEqual(eff.target, "str")
        self.assertEqual(eff.effect_type, "stat_bonus")
        self.assertEqual(eff.value, 2)

    def test_target_normalization(self):
        eff = EffectModel(target="  Dexterity  ", effect_type="stat_bonus", value=1)
        self.assertEqual(eff.target, "dexterity")

    def test_target_space_to_underscore(self):
        eff = EffectModel(target="Blood Potency", effect_type="add_dot", value=1)
        self.assertEqual(eff.target, "blood_potency")

    def test_effect_type_normalization(self):
        eff = EffectModel(target="str", effect_type="Stat Bonus", value=2)
        self.assertEqual(eff.effect_type, "stat_bonus")

    def test_effect_type_dash_normalization(self):
        eff = EffectModel(target="ac", effect_type="ac-bonus", value=1)
        self.assertEqual(eff.effect_type, "ac_bonus")

    def test_condition_default_empty(self):
        eff = EffectModel(target="str", effect_type="stat_bonus", value=2)
        self.assertEqual(eff.condition, "")

    def test_condition_set(self):
        eff = EffectModel(
            target="str", effect_type="stat_bonus", value=4,
            condition="while raging",
        )
        self.assertEqual(eff.condition, "while raging")

    def test_source_field(self):
        eff = EffectModel(target="dodge", effect_type="defense_bonus", value=2, source="M&M Power")
        self.assertEqual(eff.source, "M&M Power")

    def test_value_can_be_string(self):
        eff = EffectModel(target="damage", effect_type="damage_bonus", value="1d6")
        self.assertEqual(eff.value, "1d6")

    def test_value_can_be_bool(self):
        eff = EffectModel(target="stealth", effect_type="add_proficiency", value=True)
        self.assertTrue(eff.value)

    def test_missing_target_raises(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            EffectModel(target="", effect_type="stat_bonus")

    def test_missing_effect_type_raises(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            EffectModel(target="str", effect_type="")


# ======================================================================
# models.py effects Entegrasyon Testleri
# ======================================================================

class TestModelsHaveEffects(unittest.TestCase):

    def test_race_model_has_effects(self):
        race = RaceModel(
            name="Dwarf", system="dnd5e",
            effects=[
                EffectModel(target="constitution", effect_type="stat_bonus", value=2),
                EffectModel(target="poison", effect_type="resistance", value=True),
            ],
        )
        self.assertEqual(len(race.effects), 2)
        self.assertEqual(race.effects[0].target, "constitution")

    def test_class_model_has_effects(self):
        cls = ClassModel(
            name="Fighter", system="dnd5e",
            effects=[
                EffectModel(target="heavy_armor", effect_type="add_proficiency", value=True),
            ],
        )
        self.assertEqual(len(cls.effects), 1)

    def test_feat_model_has_effects(self):
        feat = FeatModel(
            name="Tough", system="dnd5e",
            effects=[
                EffectModel(target="hp", effect_type="hp_bonus", value=2, source="Tough (per level)"),
            ],
        )
        self.assertEqual(feat.effects[0].effect_type, "hp_bonus")

    def test_power_model_has_effects(self):
        power = PowerModel(
            name="Blast",
            effects=[
                EffectModel(target="ranged_damage", effect_type="power_rank", value=10),
            ],
        )
        self.assertEqual(power.effects[0].value, 10)

    def test_advantage_model_has_effects(self):
        adv = AdvantageModel(
            name="Defensive Roll",
            effects=[
                EffectModel(target="toughness", effect_type="defense_bonus", value=2),
            ],
        )
        self.assertEqual(adv.effects[0].target, "toughness")

    def test_power_model_effect_names_backward_compat(self):
        power = PowerModel(name="Flight", effect_names=["Movement"])
        self.assertEqual(power.effect_names, ["Movement"])

    def test_empty_effects_default(self):
        race = RaceModel(name="Human", system="dnd5e")
        self.assertEqual(race.effects, [])


# ======================================================================
# apply_effects Testleri
# ======================================================================

class TestApplyEffects(unittest.TestCase):

    def _base_char(self) -> dict:
        return {
            "abilities": {
                "Strength": 10, "Dexterity": 10, "Constitution": 10,
                "Intelligence": 10, "Wisdom": 10, "Charisma": 10,
            },
            "level": 1,
        }

    def test_stat_bonus_dnd5e(self):
        char = self._base_char()
        effects = [
            {"target": "strength", "effect_type": "stat_bonus", "value": 2},
            {"target": "con", "effect_type": "stat_bonus", "value": 1},
        ]
        apply_effects(char, effects, "dnd5e")
        self.assertEqual(char["abilities"]["Strength"], 12)
        self.assertEqual(char["abilities"]["Constitution"], 11)

    def test_add_proficiency(self):
        char = self._base_char()
        effects = [
            {"target": "perception", "effect_type": "add_proficiency", "value": True},
            {"target": "stealth", "effect_type": "add_proficiency", "value": True},
        ]
        apply_effects(char, effects, "dnd5e")
        self.assertIn("perception", char["proficiencies"])
        self.assertIn("stealth", char["proficiencies"])

    def test_resistance(self):
        char = self._base_char()
        effects = [{"target": "poison", "effect_type": "resistance", "value": True}]
        apply_effects(char, effects, "dnd5e")
        self.assertIn("poison", char["resistances"])

    def test_immunity(self):
        char = self._base_char()
        effects = [{"target": "sleep", "effect_type": "immunity", "value": True}]
        apply_effects(char, effects, "dnd5e")
        self.assertIn("sleep", char["immunities"])

    def test_speed_bonus(self):
        char = self._base_char()
        effects = [{"target": "base", "effect_type": "speed_bonus", "value": 10}]
        apply_effects(char, effects, "dnd5e")
        self.assertEqual(char["speed_bonuses"]["base"], 10)

    def test_ac_bonus(self):
        char = self._base_char()
        effects = [{"target": "ac", "effect_type": "ac_bonus", "value": 1}]
        apply_effects(char, effects, "dnd5e")
        self.assertEqual(char["ac_bonus"], 1)

    def test_hp_bonus(self):
        char = self._base_char()
        effects = [
            {"target": "hp", "effect_type": "hp_bonus", "value": 5},
            {"target": "hp", "effect_type": "hp_bonus", "value": 3},
        ]
        apply_effects(char, effects, "dnd5e")
        self.assertEqual(char["hp_bonus"], 8)

    def test_advantage_disadvantage(self):
        char = self._base_char()
        effects = [
            {"target": "save_vs_poison", "effect_type": "advantage", "value": True},
            {"target": "stealth", "effect_type": "disadvantage", "value": True},
        ]
        apply_effects(char, effects, "dnd5e")
        self.assertIn("save_vs_poison", char["advantages"])
        self.assertIn("stealth", char["disadvantages"])

    def test_grant_trait(self):
        char = self._base_char()
        effects = [{"target": "darkvision", "effect_type": "grant_trait", "value": "60 ft."}]
        apply_effects(char, effects, "dnd5e")
        self.assertIn("darkvision: 60 ft.", char["granted_traits"])

    def test_conditional_effects_deferred(self):
        char = self._base_char()
        effects = [
            {"target": "strength", "effect_type": "stat_bonus", "value": 4,
             "condition": "while raging"},
        ]
        apply_effects(char, effects, "dnd5e")
        self.assertEqual(char["abilities"]["Strength"], 10)
        self.assertEqual(len(char["conditional_effects"]), 1)
        self.assertEqual(char["conditional_effects"][0]["condition"], "while raging")

    def test_conditional_effects_forced(self):
        char = self._base_char()
        effects = [
            {"target": "strength", "effect_type": "stat_bonus", "value": 4,
             "condition": "while raging"},
        ]
        apply_effects(char, effects, "dnd5e", ignore_conditions=True)
        self.assertEqual(char["abilities"]["Strength"], 14)

    def test_unknown_effect_type_skipped(self):
        char = self._base_char()
        effects = [{"target": "str", "effect_type": "xyzzy_nonexistent", "value": 99}]
        apply_effects(char, effects, "dnd5e")
        self.assertEqual(char["abilities"]["Strength"], 10)

    def test_empty_effects(self):
        char = self._base_char()
        original = deepcopy(char)
        apply_effects(char, [], "dnd5e")
        self.assertEqual(char, original)

    def test_multiple_stat_bonuses_stack(self):
        char = self._base_char()
        effects = [
            {"target": "dexterity", "effect_type": "stat_bonus", "value": 2},
            {"target": "dexterity", "effect_type": "stat_bonus", "value": 1},
        ]
        apply_effects(char, effects, "dnd5e")
        self.assertEqual(char["abilities"]["Dexterity"], 13)

    # ---- M&M 3e efektleri --------------------------------------------------

    def test_mm3e_defense_bonus(self):
        char = {}
        effects = [
            {"target": "dodge", "effect_type": "defense_bonus", "value": 2},
            {"target": "toughness", "effect_type": "defense_bonus", "value": 5},
        ]
        apply_effects(char, effects, "mm3e")
        self.assertEqual(char["defense_bonuses"]["dodge"], 2)
        self.assertEqual(char["defense_bonuses"]["toughness"], 5)

    def test_mm3e_power_rank(self):
        char = {}
        effects = [{"target": "blast", "effect_type": "power_rank", "value": 10}]
        apply_effects(char, effects, "mm3e")
        self.assertEqual(char["power_ranks"]["blast"], 10)

    def test_mm3e_ability_rank(self):
        char = {"abilities": {"Strength": 0}}
        effects = [{"target": "strength", "effect_type": "ability_rank", "value": 4}]
        apply_effects(char, effects, "mm3e")
        self.assertEqual(char["abilities"]["Strength"], 4)

    def test_mm3e_advantage_grant(self):
        char = {}
        effects = [{"target": "defensive_roll", "effect_type": "advantage_grant", "value": 3}]
        apply_effects(char, effects, "mm3e")
        self.assertIn("defensive_roll 3", char["mm_advantages"])

    def test_mm3e_skill_rank(self):
        char = {}
        effects = [{"target": "stealth", "effect_type": "skill_rank", "value": 8}]
        apply_effects(char, effects, "mm3e")
        self.assertEqual(char["skill_ranks"]["stealth"], 8)

    # ---- EffectModel nesnesiyle calisma ------------------------------------

    def test_apply_with_effect_model_objects(self):
        char = self._base_char()
        effects = [
            EffectModel(target="constitution", effect_type="stat_bonus", value=2),
            EffectModel(target="darkvision", effect_type="grant_trait", value="60 ft."),
        ]
        apply_effects(char, effects, "dnd5e")
        self.assertEqual(char["abilities"]["Constitution"], 12)
        self.assertIn("darkvision: 60 ft.", char["granted_traits"])


# ======================================================================
# collect_effects_from_choices Testleri
# ======================================================================

class TestCollectEffects(unittest.TestCase):

    def test_collect_from_race_and_class(self):
        choices = {
            "race": {
                "name": "Dwarf",
                "effects": [
                    {"target": "constitution", "effect_type": "stat_bonus", "value": 2},
                    {"target": "poison", "effect_type": "resistance", "value": True},
                ],
            },
            "class": {
                "name": "Fighter",
                "effects": [
                    {"target": "heavy_armor", "effect_type": "add_proficiency", "value": True},
                ],
            },
        }
        all_effects = collect_effects_from_choices(choices, "dnd5e")
        self.assertEqual(len(all_effects), 3)

    def test_empty_choices(self):
        self.assertEqual(collect_effects_from_choices({}, "dnd5e"), [])

    def test_no_effects_key(self):
        choices = {"race": {"name": "Human"}}
        self.assertEqual(collect_effects_from_choices(choices, "dnd5e"), [])

    def test_source_defaults_to_choice_key(self):
        choices = {
            "background": {
                "effects": [{"target": "stealth", "effect_type": "add_proficiency", "value": True}],
            },
        }
        effects = collect_effects_from_choices(choices, "dnd5e")
        self.assertEqual(effects[0]["source"], "background")


# ======================================================================
# D&D 5e Parser Testleri
# ======================================================================

class TestDnD5eParser(unittest.TestCase):

    def test_stat_bonus(self):
        result = parse_dnd5e_effect("+2 to Strength")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "strength")
        self.assertEqual(result["effect_type"], "stat_bonus")
        self.assertEqual(result["value"], 2)

    def test_stat_bonus_abbreviated(self):
        result = parse_dnd5e_effect("+1 to CON")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "con")
        self.assertEqual(result["value"], 1)

    def test_negative_stat_bonus(self):
        result = parse_dnd5e_effect("-2 Charisma")
        self.assertIsNotNone(result)
        self.assertEqual(result["value"], -2)

    def test_all_ability_scores(self):
        result = parse_dnd5e_effect("+1 to all ability scores")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "all_abilities")

    def test_darkvision(self):
        result = parse_dnd5e_effect("Darkvision 60 ft.")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "darkvision")
        self.assertEqual(result["effect_type"], "grant_trait")
        self.assertEqual(result["value"], "60 ft.")

    def test_proficiency(self):
        result = parse_dnd5e_effect("Proficiency in Perception")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "perception")
        self.assertEqual(result["effect_type"], "add_proficiency")

    def test_resistance(self):
        result = parse_dnd5e_effect("Resistance to fire damage")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "fire")
        self.assertEqual(result["effect_type"], "resistance")

    def test_immunity(self):
        result = parse_dnd5e_effect("Immunity to sleep")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "sleep")
        self.assertEqual(result["effect_type"], "immunity")

    def test_advantage_with_condition(self):
        result = parse_dnd5e_effect("Advantage on saving throws against poison")
        self.assertIsNotNone(result)
        self.assertEqual(result["effect_type"], "advantage")
        self.assertIn("poison", result["target"])

    def test_speed_bonus(self):
        result = parse_dnd5e_effect("+5 ft. speed")
        self.assertIsNotNone(result)
        self.assertEqual(result["effect_type"], "speed_bonus")
        self.assertEqual(result["value"], 5)

    def test_ac_bonus(self):
        result = parse_dnd5e_effect("+1 to AC")
        self.assertIsNotNone(result)
        self.assertEqual(result["effect_type"], "ac_bonus")
        self.assertEqual(result["value"], 1)

    def test_empty_text(self):
        self.assertIsNone(parse_dnd5e_effect(""))
        self.assertIsNone(parse_dnd5e_effect(None))

    def test_unparseable_text(self):
        self.assertIsNone(parse_dnd5e_effect("This is just flavor text"))


# ======================================================================
# PF 1e Parser Testleri
# ======================================================================

class TestPF1eParser(unittest.TestCase):

    def test_stat_bonus(self):
        result = parse_pf1e_effect("+2 to Constitution")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "constitution")
        self.assertEqual(result["effect_type"], "stat_bonus")
        self.assertEqual(result["value"], 2)

    def test_negative_stat(self):
        result = parse_pf1e_effect("-2 Charisma")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "charisma")
        self.assertEqual(result["value"], -2)

    def test_abbreviated_stat(self):
        result = parse_pf1e_effect("+2 Dex")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "dexterity")

    def test_save_bonus(self):
        result = parse_pf1e_effect("+2 racial bonus on saves against poison")
        self.assertIsNotNone(result)
        self.assertEqual(result["effect_type"], "save_bonus")
        self.assertEqual(result["value"], 2)

    def test_dodge_ac_bonus(self):
        result = parse_pf1e_effect("+2 dodge bonus to AC")
        self.assertIsNotNone(result)
        self.assertEqual(result["effect_type"], "ac_bonus")

    def test_skill_bonus(self):
        result = parse_pf1e_effect("+2 racial bonus on Perception checks")
        self.assertIsNotNone(result)
        self.assertEqual(result["effect_type"], "skill_bonus")
        self.assertEqual(result["value"], 2)

    def test_darkvision(self):
        result = parse_pf1e_effect("Darkvision 60 feet")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "darkvision")
        self.assertEqual(result["effect_type"], "grant_trait")

    def test_low_light_vision(self):
        result = parse_pf1e_effect("Low-Light Vision")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "low_light_vision")

    def test_empty_text(self):
        self.assertIsNone(parse_pf1e_effect(""))


# ======================================================================
# M&M 3e Parser Testleri
# ======================================================================

class TestMM3eParser(unittest.TestCase):

    def test_defense_bonus(self):
        result = parse_mm3e_effect("+2 to Dodge")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "dodge")
        self.assertEqual(result["effect_type"], "defense_bonus")
        self.assertEqual(result["value"], 2)

    def test_toughness_bonus(self):
        result = parse_mm3e_effect("+3 Toughness")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "toughness")
        self.assertEqual(result["effect_type"], "defense_bonus")

    def test_ability_rank(self):
        result = parse_mm3e_effect("+2 Strength")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "strength")
        self.assertEqual(result["effect_type"], "ability_rank")

    def test_power_rank(self):
        result = parse_mm3e_effect("Rank 5 Blast")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "blast")
        self.assertEqual(result["effect_type"], "power_rank")
        self.assertEqual(result["value"], 5)

    def test_advantage_grant(self):
        result = parse_mm3e_effect("Defensive Roll 3")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "defensive_roll")
        self.assertEqual(result["effect_type"], "advantage_grant")
        self.assertEqual(result["value"], 3)

    def test_skill_rank(self):
        result = parse_mm3e_effect("+4 to Stealth")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "stealth")
        self.assertEqual(result["effect_type"], "skill_rank")

    def test_empty_text(self):
        self.assertIsNone(parse_mm3e_effect(""))


# ======================================================================
# Dispatch Parser Testleri
# ======================================================================

class TestParseEffect(unittest.TestCase):

    def test_dispatch_dnd5e(self):
        result = parse_effect("+2 to Strength", "dnd5e")
        self.assertIsNotNone(result)
        self.assertEqual(result["effect_type"], "stat_bonus")

    def test_dispatch_pf1e(self):
        result = parse_effect("+2 to Constitution", "pathfinder1e")
        self.assertIsNotNone(result)
        self.assertEqual(result["target"], "constitution")

    def test_dispatch_mm3e(self):
        result = parse_effect("+2 to Dodge", "mm3e")
        self.assertIsNotNone(result)
        self.assertEqual(result["effect_type"], "defense_bonus")

    def test_unknown_system_fallback(self):
        result = parse_effect("+2 to Strength", "unknown_system")
        self.assertIsNotNone(result)


class TestParseEffectsBatch(unittest.TestCase):

    def test_batch_mixed_results(self):
        texts = [
            "+2 to Strength",
            "This is flavor text",
            "Darkvision 60 ft.",
            "Resistance to fire damage",
        ]
        results = parse_effects_batch(texts, "dnd5e")
        self.assertEqual(len(results), 3)

    def test_batch_empty(self):
        self.assertEqual(parse_effects_batch([], "dnd5e"), [])


# ======================================================================
# Uctan Uca (End-to-End) Senaryo Testleri
# ======================================================================

class TestEndToEndScenarios(unittest.TestCase):

    def test_dnd5e_dwarf_fighter(self):
        """D&D 5e Dwarf Fighter karakter olusturma senaryosu."""
        char = {
            "abilities": {
                "Strength": 15, "Dexterity": 10, "Constitution": 14,
                "Intelligence": 8, "Wisdom": 12, "Charisma": 10,
            },
            "level": 1,
        }
        race_effects = [
            {"target": "constitution", "effect_type": "stat_bonus", "value": 2},
            {"target": "wisdom", "effect_type": "stat_bonus", "value": 1},
            {"target": "poison", "effect_type": "resistance", "value": True},
            {"target": "darkvision", "effect_type": "grant_trait", "value": "60 ft."},
            {"target": "save_vs_poison", "effect_type": "advantage", "value": True,
             "condition": "saving throws against poison"},
        ]
        class_effects = [
            {"target": "heavy_armor", "effect_type": "add_proficiency", "value": True},
            {"target": "martial_weapons", "effect_type": "add_proficiency", "value": True},
        ]
        all_effects = race_effects + class_effects
        apply_effects(char, all_effects, "dnd5e")

        self.assertEqual(char["abilities"]["Constitution"], 16)
        self.assertEqual(char["abilities"]["Wisdom"], 13)
        self.assertIn("poison", char["resistances"])
        self.assertIn("darkvision: 60 ft.", char["granted_traits"])
        self.assertIn("heavy_armor", char["proficiencies"])
        self.assertIn("martial_weapons", char["proficiencies"])
        self.assertEqual(len(char["conditional_effects"]), 1)

    def test_mm3e_hero_build(self):
        """M&M 3e PL10 hero build senaryosu."""
        char = {"abilities": {"Strength": 0, "Stamina": 0}}
        effects = [
            {"target": "strength", "effect_type": "ability_rank", "value": 6},
            {"target": "stamina", "effect_type": "ability_rank", "value": 4},
            {"target": "dodge", "effect_type": "defense_bonus", "value": 8},
            {"target": "parry", "effect_type": "defense_bonus", "value": 10},
            {"target": "toughness", "effect_type": "defense_bonus", "value": 10},
            {"target": "blast", "effect_type": "power_rank", "value": 10},
            {"target": "defensive_roll", "effect_type": "advantage_grant", "value": 2},
            {"target": "stealth", "effect_type": "skill_rank", "value": 8},
        ]
        apply_effects(char, effects, "mm3e")

        self.assertEqual(char["abilities"]["Strength"], 6)
        self.assertEqual(char["abilities"]["Stamina"], 4)
        self.assertEqual(char["defense_bonuses"]["dodge"], 8)
        self.assertEqual(char["defense_bonuses"]["parry"], 10)
        self.assertEqual(char["power_ranks"]["blast"], 10)
        self.assertEqual(char["skill_ranks"]["stealth"], 8)
        self.assertIn("defensive_roll 2", char["mm_advantages"])


if __name__ == "__main__":
    unittest.main()
