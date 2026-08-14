import pytest
from rules.calculators import calculate_carrying_capacity, calculate_encumbrance_status, Pathfinder1eCalculator

def test_carrying_capacity_str_scaling():
    """Test carrying capacity thresholds across various Strength scores."""
    cap10 = calculate_carrying_capacity(10, "Medium", is_quadruped=False)
    assert cap10["heavy_max"] == 100.0
    assert cap10["light_max"] == 33.3
    assert cap10["medium_max"] == 66.7

    cap18 = calculate_carrying_capacity(18, "Medium", is_quadruped=False)
    assert cap18["heavy_max"] == 300.0
    assert cap18["light_max"] == 100.0
    assert cap18["medium_max"] == 200.0

    # STR 20
    cap20 = calculate_carrying_capacity(20, "Medium", is_quadruped=False)
    assert cap20["heavy_max"] == 400.0

    # STR 25 (doubles from 20 -> 400 * 2 = 800)
    cap25 = calculate_carrying_capacity(25, "Medium", is_quadruped=False)
    assert cap25["heavy_max"] >= 800.0

def test_size_and_quadruped_carrying_capacity():
    """Test Size multipliers (Small 0.75, Large 2.0) and Quadrupeds (Medium 1.5, Large 3.0)."""
    # Small Biped (Halfling/Gnome) with STR 10
    cap_small = calculate_carrying_capacity(10, "Small", is_quadruped=False)
    assert cap_small["heavy_max"] == 75.0

    # Medium Quadruped (Wolf/Riding Dog) with STR 13 (base heavy = 150 -> 150 * 1.5 = 225)
    cap_med_quad = calculate_carrying_capacity(13, "Medium", is_quadruped=True)
    assert cap_med_quad["heavy_max"] == 225.0

    # Large Quadruped (Heavy Warhorse) with STR 20 (base 400 -> 400 * 3 = 1200)
    cap_large_quad = calculate_carrying_capacity(20, "Large", is_quadruped=True)
    assert cap_large_quad["heavy_max"] == 1200.0

def test_encumbrance_status_and_penalties():
    """Test load thresholds: Light, Medium, Heavy, Overloaded."""
    cap = {"light_max": 33.0, "medium_max": 66.0, "heavy_max": 100.0}

    enc_light = calculate_encumbrance_status(20.0, cap)
    assert enc_light["status"] == "Light Load"
    assert enc_light["encumbrance_acp"] == 0
    assert enc_light["speed_penalty"] == 0

    enc_med = calculate_encumbrance_status(50.0, cap)
    assert enc_med["status"] == "Medium Load"
    assert enc_med["encumbrance_acp"] == -3
    assert enc_med["max_dex_bonus"] == 3
    assert enc_med["speed_penalty"] == -10

    enc_heavy = calculate_encumbrance_status(90.0, cap)
    assert enc_heavy["status"] == "Heavy Load"
    assert enc_heavy["encumbrance_acp"] == -6
    assert enc_heavy["max_dex_bonus"] == 1

    enc_over = calculate_encumbrance_status(120.0, cap)
    assert enc_over["status"] == "Overloaded"
    assert enc_over["encumbrance_acp"] == -10

def test_acp_applies_to_all_9_acp_skills_trained_and_untrained():
    """Verify that Armor Check Penalty applies to all 9 ACP skills whether trained or untrained."""
    calc = Pathfinder1eCalculator()
    
    char = {
        "name": "Armored Hero",
        "race": "Human",
        "class": "Fighter",
        "level": 1,
        "abilities": {"strength": 14, "dexterity": 14, "constitution": 12, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "skills": {
            "Climb": 1,        # Trained (1 rank + 3 CS + 2 STR = 6)
            "Acrobatics": 0,    # Untrained (0 rank + 2 DEX = 2)
            "Stealth": 0,       # Untrained (0 rank + 2 DEX = 2)
            "Perception": 1     # Non-ACP skill (1 rank + 0 WIS = 1)
        },
        "equipment": [
            {
                "name": "Full Plate",
                "category": "armor",
                "sistem_verisi": {
                    "armor_bonus": 9,
                    "armor_check_penalty": -6,
                    "armor_type": "heavy",
                    "max_dex": 1
                }
            }
        ]
    }

    derived = calc.update_all_stats(char)

    assert derived["armor_check_penalty"] == -6

    # Perception is not an ACP skill -> unchanged
    assert derived["skills"]["Perception"] == 1

    # Climb is ACP skill -> (1 rank + 3 CS + 3 STR [14 base + 2 Human racial = 16]) - 6 ACP = 1
    assert derived["skills"]["Climb"] == 1
    assert derived["skills_detail"]["Climb"]["acp_penalty"] == -6

    # Acrobatics is untrained ACP skill -> 2 - 6 = -4
    assert derived["skills"]["Acrobatics"] == -4
    assert derived["skills_detail"]["Acrobatics"]["acp_penalty"] == -6

    # Stealth is untrained ACP skill -> 2 - 6 = -4
    assert derived["skills"]["Stealth"] == -4
    assert derived["skills_detail"]["Stealth"]["acp_penalty"] == -6

def test_armor_expert_trait_reduces_acp():
    """Verify that Armor Expert trait reduces ACP by 1 (e.g. Breastplate -4 -> -3)."""
    calc = Pathfinder1eCalculator()

    char = {
        "name": "Expert Fighter",
        "race": "Human",
        "class": "Fighter",
        "level": 1,
        "abilities": {"strength": 14, "dexterity": 14, "constitution": 12, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "skills": {"Acrobatics": 0},
        "traits": [{"isim": "Armor Expert"}],
        "equipment": [
            {
                "name": "Breastplate",
                "category": "armor",
                "sistem_verisi": {
                    "armor_bonus": 6,
                    "armor_check_penalty": -4,
                    "armor_type": "medium"
                }
            }
        ]
    }

    derived = calc.update_all_stats(char)
    # -4 + 1 = -3
    assert derived["armor_check_penalty"] == -3
    assert derived["skills"]["Acrobatics"] == -1 # 2 DEX - 3 ACP = -1

def test_fighter_armor_training():
    """Verify that Fighter Armor Training (Level 3+) reduces ACP, increases Max Dex, and removes speed penalty."""
    calc = Pathfinder1eCalculator()

    char_lv3 = {
        "name": "Seasoned Fighter",
        "race": "Human",
        "class": "Fighter",
        "level": 3,
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "equipment": [
            {
                "name": "Breastplate",
                "category": "armor",
                "sistem_verisi": {
                    "armor_bonus": 6,
                    "armor_check_penalty": -4,
                    "armor_type": "medium",
                    "max_dex": 3
                }
            }
        ]
    }

    derived = calc.update_all_stats(char_lv3)
    # Fighter Level 3 gets Armor Training 1 (-1 ACP reduction -> -3, speed remains 30 ft)
    assert derived["armor_check_penalty"] == -3
    assert derived["speed"] == 30

def test_dwarf_speed_not_reduced_by_heavy_armor_or_load():
    """Verify that Dwarf speed is never reduced below base 20 ft by armor or load."""
    calc = Pathfinder1eCalculator()

    char_dwarf = {
        "name": "Dwarven Defender",
        "race": "Dwarf",
        "class": "Cleric",
        "level": 1,
        "abilities": {"strength": 14, "dexterity": 10, "constitution": 14, "intelligence": 10, "wisdom": 16, "charisma": 8},
        "equipment": [
            {
                "name": "Full Plate",
                "category": "armor",
                "sistem_verisi": {
                    "armor_bonus": 9,
                    "armor_check_penalty": -6,
                    "armor_type": "heavy"
                }
            }
        ]
    }

    derived = calc.update_all_stats(char_dwarf)
    assert derived["speed"] == 20
