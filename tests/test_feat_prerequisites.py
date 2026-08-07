import unittest

def evaluate_prerequisites(feat, character, current_selected_feats=None):
    """Python backend/mirror helper to test prerequisite evaluation logic."""
    if not character:
        return {"valid": True, "warnings": []}

    current_selected_feats = current_selected_feats or []
    warnings = []
    sys = feat.get("sistem_verisi", {})
    prereqs = sys.get("prerequisites") or sys.get("prereqs") or feat.get("prerequisites") or []
    if isinstance(prereqs, str):
        prereqs = [prereqs]
    elif not isinstance(prereqs, list):
        prereqs = []

    if feat.get("prerequisite") and isinstance(feat["prerequisite"], str) and feat["prerequisite"] not in prereqs:
        prereqs.append(feat["prerequisite"])

    abilities = character.get("abilities") or character.get("ability_scores") or {}
    scores = {
        "str": int(abilities.get("strength") or abilities.get("Strength") or 10),
        "dex": int(abilities.get("dexterity") or abilities.get("Dexterity") or 10),
        "con": int(abilities.get("constitution") or abilities.get("Constitution") or 10),
        "int": int(abilities.get("intelligence") or abilities.get("Intelligence") or 10),
        "wis": int(abilities.get("wisdom") or abilities.get("Wisdom") or 10),
        "cha": int(abilities.get("charisma") or abilities.get("Charisma") or 10),
    }

    derived = character.get("derived") or character.get("recalcedData") or {}
    bab = int(character.get("bab") or derived.get("bab") or 0)
    total_level = int(character.get("level") or 1)

    existing_feats = [(f.get("isim") or f.get("name") if isinstance(f, dict) else str(f)).lower().strip() for f in character.get("feats", [])]
    wizard_selected = [(f.get("isim") or f.get("name") if isinstance(f, dict) else str(f)).lower().strip() for f in current_selected_feats]
    all_known_feats = set(existing_feats + wizard_selected)

    import re
    for p in prereqs:
        p_str = str(p).strip()
        if not p_str or p_str.lower() in ("none", "-"):
            continue

        m_ab = re.findall(r"(?:Str(?:ength)?|Dex(?:terity)?|Con(?:stitution)?|Int(?:elligence)?|Wis(?:dom)?|Cha(?:risma)?)\s*(\d+)", p_str, re.I)
        if m_ab:
            matches = re.finditer(r"([a-z]+)\s*(\d+)", p_str, re.I)
            for m in matches:
                stat_prefix = m.group(1).lower()[:3]
                req_val = int(m.group(2))
                curr_val = scores.get(stat_prefix, 10)
                if curr_val < reqVal if 'reqVal' in locals() else curr_val < req_val:
                    warnings.append(f"{stat_prefix.upper()} >= {req_val} gerekli (Mevcut: {curr_val})")

        m_bab = re.search(r"(?:Base attack bonus|BAB)\s*\+?\s*(\d+)", p_str, re.I)
        if m_bab:
            req_bab = int(m_bab.group(1))
            if bab < req_bab:
                warnings.append(f"BAB >= +{req_bab} gerekli (Mevcut: +{bab})")

        m_lvl = re.search(r"(?:Character level|Caster level|Level)\s*(\d+)", p_str, re.I)
        if m_lvl:
            req_lvl = int(m_lvl.group(1))
            if total_level < req_lvl:
                warnings.append(f"Level >= {req_lvl} gerekli (Mevcut: {total_level})")

        common_feat_prereqs = [
            "Power Attack", "Dodge", "Point-Blank Shot", "Precise Shot", "Combat Expertise",
            "Weapon Focus", "Mobility", "Deadly Aim", "Dazzling Display", "Improved Unarmed Strike"
        ]
        for cfp in common_feat_prereqs:
            if cfp.lower() in p_str.lower():
                has_it = any(cfp.lower() in kf for kf in all_known_feats)
                if not has_it:
                    warnings.append(f"Ön Feat Gerekli: {cfp}")

    return {"valid": len(warnings) == 0, "warnings": warnings}


class TestFeatPrerequisites(unittest.TestCase):
    def test_power_attack_prerequisite_fails_low_str(self):
        """Power Attack requires Str 13. Character with Str 10 should fail validation."""
        feat = {"name": "Power Attack", "sistem_verisi": {"prerequisites": ["Str 13", "BAB +1"]}}
        character = {"abilities": {"strength": 10}, "bab": 1, "level": 1}
        res = evaluate_prerequisites(feat, character)
        self.assertFalse(res["valid"])
        self.assertTrue(any("STR" in w for w in res["warnings"]))

    def test_cleave_prerequisite_fails_missing_power_attack(self):
        """Cleave requires Power Attack. Character without Power Attack should fail."""
        feat = {"name": "Cleave", "sistem_verisi": {"prerequisites": ["Power Attack", "BAB +1"]}}
        character = {"abilities": {"strength": 14}, "bab": 1, "level": 1, "feats": []}
        res = evaluate_prerequisites(feat, character)
        self.assertFalse(res["valid"])
        self.assertTrue(any("Power Attack" in w for w in res["warnings"]))

    def test_power_attack_passes_when_prereqs_met(self):
        """Power Attack passes when Str >= 13 and BAB >= +1."""
        feat = {"name": "Power Attack", "sistem_verisi": {"prerequisites": ["Str 13", "BAB +1"]}}
        character = {"abilities": {"strength": 14}, "bab": 1, "level": 1}
        res = evaluate_prerequisites(feat, character)
        self.assertTrue(res["valid"])
        self.assertEqual(len(res["warnings"]), 0)


if __name__ == "__main__":
    unittest.main()
