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


def test_compound_prerequisites_check_every_clause_and_dict_feats():
    engine = PF1eGMEngine()
    failed = engine.check_prerequisites({'abilities': {'strength': 10}, 'bab': 0}, ['Str 13, BAB +1'])
    assert [item.code for item in failed] == ['ability_prerequisite', 'bab_prerequisite']
    assert engine.check_prerequisites({'feats': [{'isim': 'Dodge'}]}, ['Feat: Dodge']) == []


def test_unknown_or_alternative_rules_are_not_silently_validated():
    engine = PF1eGMEngine()
    for text in ['Str 13 or Dex 13', 'Ability to cast arcane spells']:
        result = engine.check_prerequisites({}, [text])
        assert result and result[0].severity == 'warning'
        assert result[0].can_override


def test_selection_override_requires_a_reason_and_source_fallback_is_visible():
    character = {'abilities': {'strength': 8}, 'selections': [
        {'prerequisites': ['Str 13'], 'is_overridden': True, 'reason': ''}],
        'class_data': {'_provenance': {'fallback_fields': ['hit_die']}}}
    engine = PF1eGMEngine()
    result = engine.evaluate_character(character)
    assert not result[0]['overridden']
    assert any(item['code'] == 'scraper_fallback' for item in result)
    character['selections'][0]['reason'] = 'Campaign exception'
    assert engine.evaluate_character(character)[0]['overridden']
