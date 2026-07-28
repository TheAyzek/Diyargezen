import sqlite3
import json
from pathlib import Path

# Complete Pathfinder 1e Class Details Dataset (39 Classes)
PF1E_CLASS_FULL_DETAILS = {
  "Alchemist": {
    "hit_die": "d8",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "İyi (+2)", "ref": "İyi (+2)", "will": "Zayıf (+0)"},
    "proficiencies": "Basit silahlar, bomba (bombs), hafif zırhlar.",
    "class_skills": ["Acrobatics", "Appraise", "Craft", "Disable Device", "Fly", "Heal", "Knowledge (arcana)", "Knowledge (nature)", "Perception", "Profession", "Spellcraft", "Survival", "Use Magic Device"],
    "spellcasting": True,
    "spellcasting_type": "Extracts (Spontaneous)"
  },
  "Barbarian": {
    "hit_die": "d12",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "İyi (+2)", "ref": "Zayıf (+0)", "will": "Zayıf (+0)"},
    "proficiencies": "Tüm basit ve savaş silahları, hafif ve orta zırhlar, kalkanlar (kule kalkanı hariç).",
    "class_skills": ["Acrobatics", "Climb", "Craft", "Handle Animal", "Intimidate", "Knowledge (nature)", "Perception", "Ride", "Survival", "Swim"],
    "spellcasting": False,
    "spellcasting_type": "Yok"
  },
  "Bard": {
    "hit_die": "d8",
    "skill_ranks_per_level": 6,
    "saving_throws": {"fort": "Zayıf (+0)", "ref": "İyi (+2)", "will": "İyi (+2)"},
    "proficiencies": "Tüm basit silahlar, longsword, rapier, sap, shortsword, shortbow, whip, hafif zırhlar ve kalkanlar.",
    "class_skills": ["Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disguise", "Escape Artist", "Intimidate", "Knowledge (all)", "Linguistics", "Perception", "Perform", "Profession", "Sense Motive", "Sleight of Hand", "Spellcraft", "Stealth", "Use Magic Device"],
    "spellcasting": True,
    "spellcasting_type": "Spontaneous (Arcane)"
  },
  "Cleric": {
    "hit_die": "d8",
    "skill_ranks_per_level": 2,
    "saving_throws": {"fort": "İyi (+2)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Tüm basit silahlar, tanrısının favori silahı, hafif/orta/ağır zırhlar ve tüm kalkanlar.",
    "class_skills": ["Appraise", "Craft", "Diplomacy", "Heal", "Knowledge (arcana)", "Knowledge (history)", "Knowledge (nobility)", "Knowledge (planes)", "Knowledge (religion)", "Linguistics", "Profession", "Sense Motive", "Spellcraft"],
    "spellcasting": True,
    "spellcasting_type": "Prepared (Divine)"
  },
  "Druid": {
    "hit_die": "d8",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "İyi (+2)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Club, dagger, dart, quarterstaff, scimitar, scythe, sickle, sling, spear, tahta hafif/orta zırhlar ve tahta kalkanlar.",
    "class_skills": ["Climb", "Craft", "Fly", "Handle Animal", "Heal", "Knowledge (geography)", "Knowledge (nature)", "Perception", "Profession", "Ride", "Spellcraft", "Survival", "Swim"],
    "spellcasting": True,
    "spellcasting_type": "Prepared (Divine)"
  },
  "Fighter": {
    "hit_die": "d10",
    "skill_ranks_per_level": 2,
    "saving_throws": {"fort": "İyi (+2)", "ref": "Zayıf (+0)", "will": "Zayıf (+0)"},
    "proficiencies": "Tüm basit ve savaş silahları, hafif, orta ve ağır zırhlar, tüm kalkanlar (kule kalkanı dahil).",
    "class_skills": ["Climb", "Craft", "Handle Animal", "Intimidate", "Knowledge (dungeoneering)", "Knowledge (engineering)", "Profession", "Ride", "Survival", "Swim"],
    "spellcasting": False,
    "spellcasting_type": "Yok"
  },
  "Monk": {
    "hit_die": "d8",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "İyi (+2)", "ref": "İyi (+2)", "will": "İyi (+2)"},
    "proficiencies": "Club, crossbow, dagger, handaxe, javelin, kama, nunchaku, quarterstaff, sai, shuriken, siangham, sling. Zırh veya kalkan yetkinliği yoktur.",
    "class_skills": ["Acrobatics", "Climb", "Craft", "Escape Artist", "Intimidate", "Knowledge (history)", "Knowledge (religion)", "Perception", "Perform", "Profession", "Ride", "Sense Motive", "Stealth", "Swim"],
    "spellcasting": False,
    "spellcasting_type": "Yok"
  },
  "Paladin": {
    "hit_die": "d10",
    "skill_ranks_per_level": 2,
    "saving_throws": {"fort": "İyi (+2)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Tüm basit ve savaş silahları, hafif, orta ve ağır zırhlar ve tüm kalkanlar (kule kalkanı hariç).",
    "class_skills": ["Craft", "Diplomacy", "Handle Animal", "Heal", "Knowledge (nobility)", "Knowledge (religion)", "Profession", "Ride", "Sense Motive", "Spellcraft"],
    "spellcasting": True,
    "spellcasting_type": "Prepared (Divine)"
  },
  "Ranger": {
    "hit_die": "d10",
    "skill_ranks_per_level": 6,
    "saving_throws": {"fort": "İyi (+2)", "ref": "İyi (+2)", "will": "Zayıf (+0)"},
    "proficiencies": "Tüm basit ve savaş silahları, hafif ve orta zırhlar, kalkanlar (kule kalkanı hariç).",
    "class_skills": ["Climb", "Craft", "Handle Animal", "Heal", "Intimidate", "Knowledge (dungeoneering)", "Knowledge (geography)", "Knowledge (nature)", "Perception", "Profession", "Ride", "Spellcraft", "Stealth", "Survival", "Swim"],
    "spellcasting": True,
    "spellcasting_type": "Prepared (Divine)"
  },
  "Rogue": {
    "hit_die": "d8",
    "skill_ranks_per_level": 8,
    "saving_throws": {"fort": "Zayıf (+0)", "ref": "İyi (+2)", "will": "Zayıf (+0)"},
    "proficiencies": "Tüm basit silahlar, hand crossbow, rapier, sap, shortbow, shortsword, hafif zırhlar.",
    "class_skills": ["Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disable Device", "Disguise", "Escape Artist", "Intimidate", "Knowledge (dungeoneering)", "Knowledge (local)", "Linguistics", "Perception", "Perform", "Profession", "Sense Motive", "Sleight of Hand", "Stealth", "Swim", "Use Magic Device"],
    "spellcasting": False,
    "spellcasting_type": "Yok"
  },
  "Sorcerer": {
    "hit_die": "d6",
    "skill_ranks_per_level": 2,
    "saving_throws": {"fort": "Zayıf (+0)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Tüm basit silahlar. Zırh veya kalkan yetkinliği yoktur.",
    "class_skills": ["Bluff", "Craft", "Fly", "Intimidate", "Knowledge (arcana)", "Profession", "Spellcraft", "Use Magic Device"],
    "spellcasting": True,
    "spellcasting_type": "Spontaneous (Arcane)"
  },
  "Wizard": {
    "hit_die": "d6",
    "skill_ranks_per_level": 2,
    "saving_throws": {"fort": "Zayıf (+0)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Club, dagger, heavy crossbow, light crossbow, quarterstaff. Zırh veya kalkan yetkinliği yoktur.",
    "class_skills": ["Appraise", "Craft", "Fly", "Knowledge (all)", "Linguistics", "Profession", "Spellcraft"],
    "spellcasting": True,
    "spellcasting_type": "Prepared (Arcane)"
  },
  "Cavalier": {
    "hit_die": "d10",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "İyi (+2)", "ref": "Zayıf (+0)", "will": "Zayıf (+0)"},
    "proficiencies": "Basit ve savaş silahları, hafif/orta/ağır zırhlar, tüm kalkanlar.",
    "class_skills": ["Bluff", "Climb", "Craft", "Diplomacy", "Handle Animal", "Intimidate", "Profession", "Ride", "Sense Motive", "Swim"],
    "spellcasting": False,
    "spellcasting_type": "Yok"
  },
  "Gunslinger": {
    "hit_die": "d10",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "İyi (+2)", "ref": "İyi (+2)", "will": "Zayıf (+0)"},
    "proficiencies": "Basit ve savaş silahları, tüm ateşli silahlar (firearms), hafif zırhlar.",
    "class_skills": ["Acrobatics", "Craft", "Heal", "Intimidate", "Knowledge (engineering)", "Knowledge (local)", "Perception", "Profession", "Ride", "Sleight of Hand", "Survival"],
    "spellcasting": False,
    "spellcasting_type": "Yok"
  },
  "Inquisitor": {
    "hit_die": "d8",
    "skill_ranks_per_level": 6,
    "saving_throws": {"fort": "İyi (+2)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Basit silahlar, hand crossbow, longbow, repeating crossbow, shortbow, tanrı silahı, hafif/orta zırhlar, kalkanlar.",
    "class_skills": ["Bluff", "Climb", "Craft", "Diplomacy", "Disguise", "Heal", "Intimidate", "Knowledge (all)", "Perception", "Profession", "Ride", "Sense Motive", "Spellcraft", "Stealth", "Survival", "Swim"],
    "spellcasting": True,
    "spellcasting_type": "Spontaneous (Divine)"
  },
  "Magus": {
    "hit_die": "d8",
    "skill_ranks_per_level": 2,
    "saving_throws": {"fort": "İyi (+2)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Basit ve savaş silahları, hafif zırhlar.",
    "class_skills": ["Climb", "Craft", "Fly", "Intimidate", "Knowledge (arcana)", "Knowledge (dungeoneering)", "Profession", "Ride", "Spellcraft", "Use Magic Device"],
    "spellcasting": True,
    "spellcasting_type": "Prepared (Arcane)"
  },
  "Oracle": {
    "hit_die": "d8",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "Zayıf (+0)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Basit silahlar, hafif ve orta zırhlar, kalkanlar.",
    "class_skills": ["Craft", "Diplomacy", "Heal", "Knowledge (history)", "Knowledge (planes)", "Knowledge (religion)", "Profession", "Sense Motive", "Spellcraft"],
    "spellcasting": True,
    "spellcasting_type": "Spontaneous (Divine)"
  },
  "Summoner": {
    "hit_die": "d8",
    "skill_ranks_per_level": 2,
    "saving_throws": {"fort": "Zayıf (+0)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Basit silahlar, hafif zırhlar.",
    "class_skills": ["Craft", "Fly", "Handle Animal", "Knowledge (all)", "Linguistics", "Profession", "Ride", "Spellcraft", "Use Magic Device"],
    "spellcasting": True,
    "spellcasting_type": "Spontaneous (Arcane)"
  },
  "Witch": {
    "hit_die": "d6",
    "skill_ranks_per_level": 2,
    "saving_throws": {"fort": "Zayıf (+0)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Basit silahlar. Zırh yetkinliği yoktur.",
    "class_skills": ["Craft", "Fly", "Heal", "Intimidate", "Knowledge (all)", "Profession", "Spellcraft", "Use Magic Device"],
    "spellcasting": True,
    "spellcasting_type": "Prepared (Arcane)"
  },
  "Arcanist": {
    "hit_die": "d6",
    "skill_ranks_per_level": 2,
    "saving_throws": {"fort": "Zayıf (+0)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Basit silahlar. Zırh yetkinliği yoktur.",
    "class_skills": ["Appraise", "Craft", "Fly", "Knowledge (all)", "Linguistics", "Profession", "Spellcraft", "Use Magic Device"],
    "spellcasting": True,
    "spellcasting_type": "Prepared/Spontaneous (Arcane Hybrid)"
  },
  "Bloodrager": {
    "hit_die": "d10",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "İyi (+2)", "ref": "Zayıf (+0)", "will": "Zayıf (+0)"},
    "proficiencies": "Basit ve savaş silahları, hafif ve orta zırhlar, kalkanlar.",
    "class_skills": ["Acrobatics", "Climb", "Craft", "Handle Animal", "Intimidate", "Knowledge (arcana)", "Perception", "Ride", "Spellcraft", "Survival", "Swim"],
    "spellcasting": True,
    "spellcasting_type": "Spontaneous (Arcane)"
  },
  "Brawler": {
    "hit_die": "d10",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "İyi (+2)", "ref": "İyi (+2)", "will": "Zayıf (+0)"},
    "proficiencies": "Basit silahlar, handaxe, shortsword, brawler silahları, hafif zırhlar, kalkanlar.",
    "class_skills": ["Acrobatics", "Climb", "Craft", "Escape Artist", "Intimidate", "Knowledge (dungeoneering)", "Knowledge (local)", "Perception", "Profession", "Ride", "Sense Motive", "Swim"],
    "spellcasting": False,
    "spellcasting_type": "Yok"
  },
  "Hunter": {
    "hit_die": "d8",
    "skill_ranks_per_level": 6,
    "saving_throws": {"fort": "İyi (+2)", "ref": "İyi (+2)", "will": "Zayıf (+0)"},
    "proficiencies": "Basit ve savaş silahları, hafif ve orta tahta zırhlar, kalkanlar.",
    "class_skills": ["Climb", "Craft", "Fly", "Handle Animal", "Heal", "Intimidate", "Knowledge (dungeoneering)", "Knowledge (geography)", "Knowledge (nature)", "Perception", "Profession", "Ride", "Spellcraft", "Stealth", "Survival", "Swim"],
    "spellcasting": True,
    "spellcasting_type": "Spontaneous (Divine)"
  },
  "Investigator": {
    "hit_die": "d8",
    "skill_ranks_per_level": 6,
    "saving_throws": {"fort": "Zayıf (+0)", "ref": "İyi (+2)", "will": "İyi (+2)"},
    "proficiencies": "Basit silahlar, blowgun, crossbow, hand crossbow, rapier, sap, shortbow, shortsword, sword cane, hafif zırhlar.",
    "class_skills": ["Acrobatics", "Appraise", "Bluff", "Climb", "Craft", "Diplomacy", "Disable Device", "Disguise", "Escape Artist", "Heal", "Intimidate", "Knowledge (all)", "Linguistics", "Perception", "Perform", "Profession", "Sense Motive", "Sleight of Hand", "Spellcraft", "Stealth", "Use Magic Device"],
    "spellcasting": True,
    "spellcasting_type": "Extracts (Spontaneous)"
  },
  "Slayer": {
    "hit_die": "d10",
    "skill_ranks_per_level": 6,
    "saving_throws": {"fort": "İyi (+2)", "ref": "İyi (+2)", "will": "Zayıf (+0)"},
    "proficiencies": "Basit ve savaş silahları, hafif ve orta zırhlar, kalkanlar.",
    "class_skills": ["Acrobatics", "Bluff", "Climb", "Craft", "Disguise", "Heal", "Intimidate", "Knowledge (dungeoneering)", "Knowledge (geography)", "Knowledge (local)", "Perception", "Profession", "Ride", "Sense Motive", "Stealth", "Survival", "Swim"],
    "spellcasting": False,
    "spellcasting_type": "Yok"
  },
  "Swashbuckler": {
    "hit_die": "d10",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "Zayıf (+0)", "ref": "İyi (+2)", "will": "Zayıf (+0)"},
    "proficiencies": "Basit ve savaş silahları, hafif zırhlar, buckler.",
    "class_skills": ["Acrobatics", "Bluff", "Climb", "Craft", "Diplomacy", "Escape Artist", "Intimidate", "Knowledge (local)", "Perception", "Perform", "Profession", "Ride", "Sense Motive", "Sleight of Hand", "Swim"],
    "spellcasting": False,
    "spellcasting_type": "Yok"
  },
  "Warpriest": {
    "hit_die": "d8",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "İyi (+2)", "ref": "Zayıf (+0)", "will": "İyi (+2)"},
    "proficiencies": "Basit ve savaş silahları, tanrının favori silahı, hafif/orta/ağır zırhlar, kalkanlar.",
    "class_skills": ["Climb", "Craft", "Diplomacy", "Handle Animal", "Heal", "Intimidate", "Knowledge (engineering)", "Knowledge (religion)", "Profession", "Ride", "Sense Motive", "Spellcraft", "Survival"],
    "spellcasting": True,
    "spellcasting_type": "Prepared (Divine)"
  },
  "Kineticist": {
    "hit_die": "d8",
    "skill_ranks_per_level": 4,
    "saving_throws": {"fort": "İyi (+2)", "ref": "İyi (+2)", "will": "Zayıf (+0)"},
    "proficiencies": "Basit silahlar, hafif zırhlar.",
    "class_skills": ["Acrobatics", "Craft", "Heal", "Intimidate", "Perception", "Profession", "Stealth", "Use Magic Device"],
    "spellcasting": False,
    "spellcasting_type": "Wild Talents (Spell-like)"
  }
}

def seed_class_details_to_dbs():
    project_root = Path(".")
    target_dbs = [
        project_root / "data" / "characters.db",
        project_root / "desktop" / "data" / "offline_pf1e.db",
        project_root / "dist" / "Diyargezen" / "_internal" / "data" / "characters.db"
    ]

    for db_path in target_dbs:
        if not db_path.exists():
            continue

        print(f"\nSeeding Class Details to: {db_path}")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if 'entities' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entities'")
        if not cursor.fetchone():
            conn.close()
            continue

        updated_count = 0
        for cls_name, info in PF1E_CLASS_FULL_DETAILS.items():
            cursor.execute(
                "SELECT id, sistem_verisi FROM entities WHERE sistem = 'pathfinder1e' AND kategori IN ('class', 'archetype') AND isim LIKE ?",
                (f"%{cls_name}%",)
            )
            rows = cursor.fetchall()
            for r_id, r_sv_raw in rows:
                try:
                    payload = json.loads(r_sv_raw) if r_sv_raw else {}
                except Exception:
                    payload = {}

                if isinstance(payload, dict):
                    payload["hit_die"] = info["hit_die"]
                    payload["skill_ranks_per_level"] = info["skill_ranks_per_level"]
                    payload["saving_throws"] = info["saving_throws"]
                    payload["proficiencies"] = info["proficiencies"]
                    payload["class_skills"] = info["class_skills"]
                    payload["spellcasting"] = info["spellcasting"]
                    payload["spellcasting_type"] = info["spellcasting_type"]

                    cursor.execute(
                        "UPDATE entities SET sistem_verisi = ? WHERE id = ?",
                        (json.dumps(payload, ensure_ascii=False), r_id)
                    )
                    updated_count += 1

        conn.commit()
        conn.close()
        print(f"Successfully updated {updated_count} class records in {db_path.name}.")

if __name__ == "__main__":
    seed_class_details_to_dbs()
