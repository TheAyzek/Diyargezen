import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.pf1e_gm_engine import PF1eGMEngine


from rules.pf1e_rules import PF1EValidator


def test_prerequisite_is_a_soft_block_until_gm_override():
    engine = PF1eGMEngine()
    character = {"level": 1, "bab": 0, "abilities": {"strength": 10}}
    rules = ["Str 13", "Base Attack Bonus +1"]

    blocked = engine.check_prerequisites(character, rules)
    assert [item.code for item in blocked] == ["ability_prerequisite", "bab_prerequisite"]
    assert not any(item.overridden for item in blocked)

    allowed = engine.check_prerequisites(character, rules, is_overridden=True)
    assert all(item.overridden for item in allowed)
    assert all(item.can_override for item in allowed)


def test_pf1e_validator_expanded_feat_prerequisites():
    """Test expanded feat prerequisite chains (e.g. Great Cleave, Spring Attack, Manyshot)."""
    validator = PF1EValidator()

    # Character trying to take Spring Attack without Mobility & Dodge and BAB < 4
    char = {
        "level": 2,
        "bab": 2,
        "abilities": {"strength": 14, "dexterity": 14, "intelligence": 10},
        "feats": ["Spring Attack"]
    }

    warnings = validator.validate(char)
    assert len(warnings) >= 2
    assert any("BAB en az +4" in w for w in warnings)
    assert any("Dodge" in w or "Mobility" in w for w in warnings)

    # Adding prerequisites eliminates warnings
    valid_char = {
        "level": 4,
        "bab": 4,
        "abilities": {"strength": 14, "dexterity": 14, "intelligence": 10},
        "feats": ["Dodge", "Mobility", "Spring Attack"]
    }
    assert len(validator.validate(valid_char)) == 0


def test_pf1e_validator_gm_override():
    """Test that gm_override suppresses all soft-block warnings completely."""
    validator = PF1EValidator()

    invalid_char = {
        "level": 1,
        "bab": 0,
        "abilities": {"str": 8, "dex": 8},
        "feats": ["Spring Attack", "Great Cleave", "Manyshot"],
        "gm_override": True
    }

    # Should return empty list because gm_override is True
    assert validator.validate(invalid_char) == []
