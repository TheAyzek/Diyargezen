import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.pf1e_gm_engine import PF1eGMEngine


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
