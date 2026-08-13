import pytest
from rules.calculators import categorize_items, is_item_magical

def test_equipment_magic_and_normal_categorization():
    """Test that weapons and armors are correctly separated into normal vs magical categories."""

    normal_sword = {"name": "Uzun Kılıç", "kategori": "weapon"}
    magic_sword = {"name": "+1 Longsword", "kategori": "weapon"}
    flaming_sword = {"name": "Flaming Scimitar", "kategori": "weapon", "is_magical": True}
    
    normal_armor = {"name": "Tam Plaka Zırh", "kategori": "armor"}
    magic_armor = {"name": "+2 Full Plate", "kategori": "armor"}
    büyülü_shield = {"name": "Büyülü Çelik Kalkan", "kategori": "shield"}

    # Test is_item_magical
    assert is_item_magical(normal_sword) is False
    assert is_item_magical(magic_sword) is True
    assert is_item_magical(flaming_sword) is True

    assert is_item_magical(normal_armor) is False
    assert is_item_magical(magic_armor) is True
    assert is_item_magical(büyülü_shield) is True

    # Test categorize_items
    equipment_list = [normal_sword, magic_sword, flaming_sword, normal_armor, magic_armor, büyülü_shield]
    categorized = categorize_items(equipment_list)

    # Check Weapons (Total, Normal, Magic)
    assert len(categorized["weapons"]) == 3
    assert len(categorized["weapons_normal"]) == 1
    assert len(categorized["weapons_magic"]) == 2
    assert categorized["weapons_normal"][0]["name"] == "Uzun Kılıç"

    # Check Armor & Shields (Total, Normal, Magic)
    assert len(categorized["armor_shields"]) == 3
    assert len(categorized["armor_normal"]) == 1
    assert len(categorized["armor_magic"]) == 2
    assert categorized["armor_normal"][0]["name"] == "Tam Plaka Zırh"
