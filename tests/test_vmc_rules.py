import pytest
from rules.vmc_engine import PF1eVMCEngine
from rules.calculators import PF1e_Calculator

def test_vmc_validation():
    """Verify primary and secondary VMC class validation."""
    # Same primary and secondary class -> Invalid
    is_valid, err = PF1eVMCEngine.is_vmc_allowed("Fighter", "Fighter")
    assert not is_valid
    assert "aynı olamaz" in err.lower()

    # Different primary and secondary class -> Valid
    is_valid, err = PF1eVMCEngine.is_vmc_allowed("Fighter", "Wizard")
    assert is_valid
    assert err == ""

def test_vmc_feat_deduction():
    """Verify forfeited feat count at levels 1, 3, 5, 7, 11, 15, 19."""
    assert PF1eVMCEngine.get_sacrificed_feat_count(1, "wizard") == 0
    assert PF1eVMCEngine.get_sacrificed_feat_count(2, "wizard") == 0
    assert PF1eVMCEngine.get_sacrificed_feat_count(3, "wizard") == 1
    assert PF1eVMCEngine.get_sacrificed_feat_count(6, "wizard") == 1
    assert PF1eVMCEngine.get_sacrificed_feat_count(7, "wizard") == 2
    assert PF1eVMCEngine.get_sacrificed_feat_count(11, "wizard") == 3
    assert PF1eVMCEngine.get_sacrificed_feat_count(15, "wizard") == 4
    assert PF1eVMCEngine.get_sacrificed_feat_count(19, "wizard") == 5
    assert PF1eVMCEngine.get_sacrificed_feat_count(20, "wizard") == 5

def test_vmc_barbarian_granted_features():
    """Verify VMC Barbarian granted features at various levels."""
    calc = PF1e_Calculator()

    # Level 1 Fighter with VMC Barbarian -> 0 VMC features
    char_lv1 = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "class": "Fighter",
        "level": 1,
        "variant_multiclass": "Barbarian",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10}
    }
    recalced1 = calc.update_all_stats(char_lv1)
    vmc_details1 = recalced1.get("variant_multiclass_details", {})
    assert vmc_details1["vmc_class"] == "Barbarian"
    assert vmc_details1["sacrificed_feat_count"] == 0
    assert len(vmc_details1["granted_features"]) == 0

    # Level 3 Fighter with VMC Barbarian -> Gains Rage
    char_lv3 = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "class": "Fighter",
        "level": 3,
        "variant_multiclass": "Barbarian",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10}
    }
    recalced3 = calc.update_all_stats(char_lv3)
    vmc_details3 = recalced3.get("variant_multiclass_details", {})
    assert vmc_details3["sacrificed_feat_count"] == 1
    assert len(vmc_details3["granted_features"]) == 1
    assert vmc_details3["granted_features"][0]["name"] == "Rage"

    # Level 7 Fighter with VMC Barbarian -> Gains Rage and Uncanny Dodge
    char_lv7 = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "class": "Fighter",
        "level": 7,
        "variant_multiclass": "Barbarian",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10}
    }
    recalced7 = calc.update_all_stats(char_lv7)
    vmc_details7 = recalced7.get("variant_multiclass_details", {})
    assert vmc_details7["sacrificed_feat_count"] == 2
    assert len(vmc_details7["granted_features"]) == 2
    feature_names = [f["name"] for f in vmc_details7["granted_features"]]
    assert "Rage" in feature_names
    assert "Uncanny Dodge" in feature_names

def test_vmc_wizard_granted_features():
    """Verify VMC Wizard granted features."""
    calc = PF1e_Calculator()

    char_lv11 = {
        "name": "Seoni",
        "system": "pathfinder1e",
        "class": "Sorcerer",
        "level": 11,
        "variant_multiclass": "Wizard",
        "abilities": {"strength": 8, "dexterity": 14, "constitution": 12, "intelligence": 14, "wisdom": 10, "charisma": 18}
    }
    recalced = calc.update_all_stats(char_lv11)
    vmc_details = recalced.get("variant_multiclass_details", {})
    assert vmc_details["vmc_class"] == "Wizard"
    assert vmc_details["sacrificed_feat_count"] == 3
    assert len(vmc_details["granted_features"]) == 3
