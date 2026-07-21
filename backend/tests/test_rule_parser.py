from rules.rule_parser import RuleParser

def test_parse_skills():
    # Simple skill bonus
    res = RuleParser.parse_description("You get a +2 racial bonus on Perception checks.", "pf1e", "Test Feat", "feat")
    assert len(res) == 1
    assert res[0]["target"] == "skills.perception"
    assert res[0]["value"] == 2

    # Multiple skills
    res = RuleParser.parse_description("You get a +2 bonus on Perception and Sense Motive checks.", "pf1e", "Test Feat", "feat")
    targets = [m["target"] for m in res]
    assert "skills.perception" in targets
    assert "skills.sense_motive" in targets
    assert all(m["value"] == 2 for m in res)

def test_parse_ac():
    res = RuleParser.parse_description("You gain a +1 dodge bonus to AC.", "pf1e", "Test Feat", "feat")
    assert len(res) == 1
    assert res[0]["target"] == "ac"
    assert res[0]["value"] == 1

def test_parse_saves():
    res = RuleParser.parse_description("You get a +2 bonus on all Will saving throws.", "pf1e", "Test Feat", "feat")
    assert len(res) == 1
    assert res[0]["target"] == "saving_throws.Will"
    assert res[0]["value"] == 2

def test_parse_initiative():
    res = RuleParser.parse_description("You gain a +4 bonus on initiative checks.", "pf1e", "Test Feat", "feat")
    assert len(res) == 1
    assert res[0]["target"] == "initiative"
    assert res[0]["value"] == 4

def test_parse_abilities():
    res = RuleParser.parse_description("+2 Dexterity, +2 Intelligence, -2 Constitution", "pf1e", "Elf", "race")
    targets = {m["target"]: m["value"] for m in res}
    assert targets.get("dexterity") == 2
    assert targets.get("intelligence") == 2
    assert targets.get("constitution") == -2
