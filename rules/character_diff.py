"""
Pathfinder 1st Edition Character Diff & Snapshot Comparison Engine
===================================================================
Provides deterministic mathematical and structural comparison between two PF1e characters
or two snapshots of the same character (e.g. Level 1 vs Level 5 vs Level 10).

Calculates:
- Progression & Level Deltas
- Ability Scores & Modifiers Deltas
- Combat Metrics (HP, BAB, AC, Saves, CMB, CMD, Speed, Maneuvers)
- Skill Ranks and Bonus Deltas
- Feats & Traits Added / Removed
- Spellcasting (CL, Concentration, Spell Slots)
- Wealth & Equipment (GP, Weight, Gear Added/Removed)
"""

from typing import Dict, Any, List, Set, Optional
from rules.calculators import PF1e_Calculator


def _format_delta(val: int) -> str:
    return f"+{val}" if val > 0 else (str(val) if val < 0 else "0")


def compute_character_diff(char_a: Dict[str, Any], char_b: Dict[str, Any]) -> Dict[str, Any]:
    """Computes a complete, structured diff between Character A (Base) and Character B (Target)."""
    calc = PF1e_Calculator()

    # Recalculate derived stats for both to guarantee 100% accuracy
    copy_a = dict(char_a)
    copy_b = dict(char_b)
    der_a = calc.update_all_stats(copy_a)
    der_b = calc.update_all_stats(copy_b)

    # 1. Progression & Identity Diff
    lvl_a = max(1, int(copy_a.get("level") or 1))
    lvl_b = max(1, int(copy_b.get("level") or 1))
    lvl_delta = lvl_b - lvl_a

    progression = {
        "name_a": copy_a.get("name") or "Karakter A",
        "name_b": copy_b.get("name") or "Karakter B",
        "level_a": lvl_a,
        "level_b": lvl_b,
        "level_delta": lvl_delta,
        "level_delta_str": _format_delta(lvl_delta),
        "class_a": copy_a.get("class") or "Sınıfsız",
        "class_b": copy_b.get("class") or "Sınıfsız",
        "archetype_a": copy_a.get("archetype") or copy_a.get("archetypes") or None,
        "archetype_b": copy_b.get("archetype") or copy_b.get("archetypes") or None,
        "race_a": copy_a.get("race") or "Bilinmiyor",
        "race_b": copy_b.get("race") or "Bilinmiyor",
        "alignment_a": copy_a.get("alignment") or "TN",
        "alignment_b": copy_b.get("alignment") or "TN"
    }

    # 2. Ability Scores & Modifiers Diff
    abilities_diff = {}
    for ab in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
        score_a = der_a.get("ability_scores", {}).get(ab, 10)
        score_b = der_b.get("ability_scores", {}).get(ab, 10)
        mod_a = der_a.get("ability_modifiers", {}).get(ab, 0)
        mod_b = der_b.get("ability_modifiers", {}).get(ab, 0)

        score_delta = score_b - score_a
        mod_delta = mod_b - mod_a

        abilities_diff[ab] = {
            "score_a": score_a,
            "score_b": score_b,
            "score_delta": score_delta,
            "score_delta_str": _format_delta(score_delta),
            "mod_a": mod_a,
            "mod_b": mod_b,
            "mod_delta": mod_delta,
            "mod_delta_str": _format_delta(mod_delta)
        }

    # 3. Combat Metrics Diff
    hp_a = der_a.get("hit_points", 0)
    hp_b = der_b.get("hit_points", 0)
    hp_delta = hp_b - hp_a

    bab_a = der_a.get("bab", 0)
    bab_b = der_b.get("bab", 0)
    bab_delta = bab_b - bab_a

    ac_a = der_a.get("armor_class", 10)
    ac_b = der_b.get("armor_class", 10)
    ac_delta = ac_b - ac_a

    touch_a = der_a.get("touch_ac", 10)
    touch_b = der_b.get("touch_ac", 10)
    touch_delta = touch_b - touch_a

    ff_a = der_a.get("flat_footed_ac", 10)
    ff_b = der_b.get("flat_footed_ac", 10)
    ff_delta = ff_b - ff_a

    init_a = der_a.get("initiative", 0)
    init_b = der_b.get("initiative", 0)
    init_delta = init_b - init_a

    speed_a = der_a.get("speed", 30)
    speed_b = der_b.get("speed", 30)
    speed_delta = speed_b - speed_a

    cmb_a = der_a.get("cmb", 0)
    cmb_b = der_b.get("cmb", 0)
    cmb_delta = cmb_b - cmb_a

    cmd_a = der_a.get("cmd", 10)
    cmd_b = der_b.get("cmd", 10)
    cmd_delta = cmd_b - cmd_a

    # Saving Throws
    saves_a = der_a.get("saving_throws", {})
    saves_b = der_b.get("saving_throws", {})
    saves_diff = {}
    for sv_k in ["Fortitude", "Reflex", "Will"]:
        sv_a = saves_a.get(sv_k, 0)
        sv_b = saves_b.get(sv_k, 0)
        sv_delta = sv_b - sv_a
        saves_diff[sv_k] = {
            "val_a": sv_a,
            "val_b": sv_b,
            "delta": sv_delta,
            "delta_str": _format_delta(sv_delta)
        }

    # Maneuvers Breakdown Diff
    man_a = der_a.get("maneuvers", {})
    man_b = der_b.get("maneuvers", {})
    maneuvers_diff = {}
    all_maneuver_keys = set(man_a.keys()) | set(man_b.keys())
    for mk in all_maneuver_keys:
        m_obj_a = man_a.get(mk, {"cmb": 0, "cmd": 10})
        m_obj_b = man_b.get(mk, {"cmb": 0, "cmd": 10})
        m_cmb_a = m_obj_a.get("cmb", 0)
        m_cmb_b = m_obj_b.get("cmb", 0)
        m_cmd_a = m_obj_a.get("cmd", 10)
        m_cmd_b = m_obj_b.get("cmd", 10)
        maneuvers_diff[mk] = {
            "cmb_a": m_cmb_a,
            "cmb_b": m_cmb_b,
            "cmb_delta": m_cmb_b - m_cmb_a,
            "cmd_a": m_cmd_a,
            "cmd_b": m_cmd_b,
            "cmd_delta": m_cmd_b - m_cmd_a,
        }

    combat = {
        "hit_points": {"val_a": hp_a, "val_b": hp_b, "delta": hp_delta, "delta_str": _format_delta(hp_delta)},
        "bab": {"val_a": bab_a, "val_b": bab_b, "delta": bab_delta, "delta_str": _format_delta(bab_delta)},
        "armor_class": {"val_a": ac_a, "val_b": ac_b, "delta": ac_delta, "delta_str": _format_delta(ac_delta)},
        "touch_ac": {"val_a": touch_a, "val_b": touch_b, "delta": touch_delta, "delta_str": _format_delta(touch_delta)},
        "flat_footed_ac": {"val_a": ff_a, "val_b": ff_b, "delta": ff_delta, "delta_str": _format_delta(ff_delta)},
        "initiative": {"val_a": init_a, "val_b": init_b, "delta": init_delta, "delta_str": _format_delta(init_delta)},
        "speed": {"val_a": speed_a, "val_b": speed_b, "delta": speed_delta, "delta_str": _format_delta(speed_delta)},
        "cmb": {"val_a": cmb_a, "val_b": cmb_b, "delta": cmb_delta, "delta_str": _format_delta(cmb_delta)},
        "cmd": {"val_a": cmd_a, "val_b": cmd_b, "delta": cmd_delta, "delta_str": _format_delta(cmd_delta)},
        "saving_throws": saves_diff,
        "maneuvers": maneuvers_diff
    }

    # 4. Skills Diff
    sk_a = der_a.get("skills", {})
    sk_b = der_b.get("skills", {})
    sk_det_a = der_a.get("skills_detail", {})
    sk_det_b = der_b.get("skills_detail", {})

    skills_diff = {}
    improved_skills = []
    for sk in calc.PF_SKILL_LIST:
        tot_a = sk_a.get(sk, 0)
        tot_b = sk_b.get(sk, 0)
        rank_a = sk_det_a.get(sk, {}).get("ranks", sk_det_a.get(sk, {}).get("rank", 0))
        rank_b = sk_det_b.get(sk, {}).get("ranks", sk_det_b.get(sk, {}).get("rank", 0))

        tot_delta = tot_b - tot_a
        rank_delta = rank_b - rank_a

        if tot_delta != 0 or rank_delta != 0 or rank_a > 0 or rank_b > 0:
            item_data = {
                "skill": sk,
                "total_a": tot_a,
                "total_b": tot_b,
                "total_delta": tot_delta,
                "total_delta_str": _format_delta(tot_delta),
                "rank_a": rank_a,
                "rank_b": rank_b,
                "rank_delta": rank_delta,
                "rank_delta_str": _format_delta(rank_delta)
            }
            skills_diff[sk] = item_data
            if tot_delta > 0 or rank_delta > 0:
                improved_skills.append(item_data)

    # 5. Feats & Traits Diff
    def _extract_names(raw_list: List[Any]) -> Set[str]:
        names = set()
        for item in raw_list or []:
            if isinstance(item, dict):
                n = item.get("name") or item.get("isim")
                if n: names.add(str(n).strip())
            elif isinstance(item, str) and item.strip():
                names.add(item.strip())
        return names

    feats_a = _extract_names(copy_a.get("feats", []))
    feats_b = _extract_names(copy_b.get("feats", []))
    feats_diff = {
        "added": sorted(list(feats_b - feats_a)),
        "removed": sorted(list(feats_a - feats_b)),
        "common": sorted(list(feats_a & feats_b))
    }

    traits_a = _extract_names(copy_a.get("traits", []))
    traits_b = _extract_names(copy_b.get("traits", []))
    traits_diff = {
        "added": sorted(list(traits_b - traits_a)),
        "removed": sorted(list(traits_a - traits_b)),
        "common": sorted(list(traits_a & traits_b))
    }

    # 6. Spellcasting Diff
    sp_a = der_a.get("spellcasting", {}) or {}
    sp_b = der_b.get("spellcasting", {}) or {}
    slots_a = der_a.get("spell_slots", {}) or {}
    slots_b = der_b.get("spell_slots", {}) or {}

    cl_a = sp_a.get("caster_level", 0)
    cl_b = sp_b.get("caster_level", 0)
    conc_a = sp_a.get("concentration_bonus", 0)
    conc_b = sp_b.get("concentration_bonus", 0)

    slots_diff = {}
    for lvl_idx in range(10):
        s_k = str(lvl_idx)
        s_a = int(slots_a.get(s_k, 0))
        s_b = int(slots_b.get(s_k, 0))
        s_delta = s_b - s_a
        if s_a > 0 or s_b > 0:
            slots_diff[s_k] = {
                "level": lvl_idx,
                "slots_a": s_a,
                "slots_b": s_b,
                "delta": s_delta,
                "delta_str": _format_delta(s_delta)
            }

    spellcasting = {
        "has_spellcasting_a": bool(sp_a.get("has_spells", False) or slots_a),
        "has_spellcasting_b": bool(sp_b.get("has_spells", False) or slots_b),
        "caster_level": {"val_a": cl_a, "val_b": cl_b, "delta": cl_b - cl_a, "delta_str": _format_delta(cl_b - cl_a)},
        "concentration": {"val_a": conc_a, "val_b": conc_b, "delta": conc_b - conc_a, "delta_str": _format_delta(conc_b - conc_a)},
        "spell_slots": slots_diff
    }

    # 7. Wealth & Gear Diff
    w_a = der_a.get("wealth", {}) or {}
    w_b = der_b.get("wealth", {}) or {}

    wealth_a = w_a.get("total_wealth_gp", 0.0)
    wealth_b = w_b.get("total_wealth_gp", 0.0)
    wealth_delta = wealth_b - wealth_a

    wt_a = der_a.get("total_weight", 0.0)
    wt_b = der_b.get("total_weight", 0.0)
    wt_delta = round(wt_b - wt_a, 2)

    gear_a = _extract_names(copy_a.get("equipment", []))
    gear_b = _extract_names(copy_b.get("equipment", []))

    wealth_and_gear = {
        "total_wealth_gp": {"val_a": wealth_a, "val_b": wealth_b, "delta": wealth_delta, "delta_str": _format_delta(int(wealth_delta))},
        "total_weight_lbs": {"val_a": wt_a, "val_b": wt_b, "delta": wt_delta, "delta_str": _format_delta(int(wt_delta))},
        "items_added": sorted(list(gear_b - gear_a)),
        "items_removed": sorted(list(gear_a - gear_b)),
        "items_common": sorted(list(gear_a & gear_b))
    }

    return {
        "progression": progression,
        "abilities": abilities_diff,
        "combat": combat,
        "skills": skills_diff,
        "improved_skills": improved_skills,
        "feats": feats_diff,
        "traits": traits_diff,
        "spellcasting": spellcasting,
        "wealth_and_gear": wealth_and_gear
    }
