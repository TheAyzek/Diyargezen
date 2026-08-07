import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "pathfinder_1e_data.json"

# Core & Featured PF1e Official Racial Ability Score Modifiers
RACE_ASI_FIXES = {
    "Dwarf": ({"constitution": 2, "wisdom": 2, "charisma": -2}, "+2 Constitution, +2 Wisdom, -2 Charisma"),
    "Elf": ({"dexterity": 2, "intelligence": 2, "constitution": -2}, "+2 Dexterity, +2 Intelligence, -2 Constitution"),
    "Gnome": ({"constitution": 2, "charisma": 2, "strength": -2}, "+2 Constitution, +2 Charisma, -2 Strength"),
    "Half-Elf": ({"any": 2}, "+2 to One Ability Score"),
    "Halfling": ({"dexterity": 2, "charisma": 2, "strength": -2}, "+2 Dexterity, +2 Charisma, -2 Strength"),
    "Half-Orc": ({"any": 2}, "+2 to One Ability Score"),
    "Human": ({"any": 2}, "+2 to One Ability Score"),
    "Aasimar": ({"wisdom": 2, "charisma": 2}, "+2 Wisdom, +2 Charisma"),
    "Android": ({"dexterity": 2, "intelligence": 2, "charisma": -2}, "+2 Dexterity, +2 Intelligence, -2 Charisma"),
    "Aphorite": ({"strength": 2, "wisdom": 2, "charisma": -2}, "+2 Strength, +2 Wisdom, -2 Charisma"),
    "Aquatic Elf": ({"dexterity": 2, "intelligence": 2, "constitution": -2}, "+2 Dexterity, +2 Intelligence, -2 Constitution"),
    "Catfolk": ({"dexterity": 2, "charisma": 2, "wisdom": -2}, "+2 Dexterity, +2 Charisma, -2 Wisdom"),
    "Changeling": ({"wisdom": 2, "charisma": 2, "constitution": -2}, "+2 Wisdom, +2 Charisma, -2 Constitution"),
    "Dhampir": ({"dexterity": 2, "charisma": 2, "constitution": -2}, "+2 Dexterity, +2 Charisma, -2 Constitution"),
    "Drow": ({"dexterity": 2, "charisma": 2, "constitution": -2}, "+2 Dexterity, +2 Charisma, -2 Constitution"),
    "Duergar": ({"constitution": 2, "wisdom": 2, "charisma": -4}, "+2 Constitution, +2 Wisdom, -4 Charisma"),
    "Duskwalker": ({"dexterity": 2, "wisdom": 2, "constitution": -2}, "+2 Dexterity, +2 Wisdom, -2 Constitution"),
    "Fetchling": ({"dexterity": 2, "charisma": 2, "wisdom": -2}, "+2 Dexterity, +2 Charisma, -2 Wisdom"),
    "Ganzi": ({"constitution": 2, "charisma": 2, "intelligence": -2}, "+2 Constitution, +2 Charisma, -2 Intelligence"),
    "Gillman": ({"constitution": 2, "charisma": 2, "wisdom": -2}, "+2 Constitution, +2 Charisma, -2 Wisdom"),
    "Goblin": ({"dexterity": 4, "strength": -2, "charisma": -2}, "+4 Dexterity, -2 Strength, -2 Charisma"),
    "Grippli": ({"dexterity": 2, "wisdom": 2, "strength": -2}, "+2 Dexterity, +2 Wisdom, -2 Strength"),
    "Hobgoblin": ({"dexterity": 2, "constitution": 2}, "+2 Dexterity, +2 Constitution"),
    "Ifrit": ({"dexterity": 2, "charisma": 2, "wisdom": -2}, "+2 Dexterity, +2 Charisma, -2 Wisdom"),
    "Kasatha": ({"dexterity": 2, "wisdom": 2}, "+2 Dexterity, +2 Wisdom"),
    "Kitsune": ({"dexterity": 2, "charisma": 2, "strength": -2}, "+2 Dexterity, +2 Charisma, -2 Strength"),
    "Kobold": ({"dexterity": 2, "strength": -4, "constitution": -2}, "+2 Dexterity, -4 Strength, -2 Constitution"),
    "Merfolk": ({"dexterity": 2, "constitution": 2, "charisma": 2}, "+2 Dexterity, +2 Constitution, +2 Charisma"),
    "Monkey Goblin": ({"dexterity": 4, "wisdom": -2, "charisma": -2}, "+4 Dexterity, -2 Wisdom, -2 Charisma"),
    "Nagaji": ({"strength": 2, "charisma": 2, "intelligence": -2}, "+2 Strength, +2 Charisma, -2 Intelligence"),
    "Orc": ({"strength": 4, "intelligence": -2, "wisdom": -2, "charisma": -2}, "+4 Strength, -2 Intelligence, -2 Wisdom, -2 Charisma"),
    "Oread": ({"strength": 2, "wisdom": 2, "charisma": -2}, "+2 Strength, +2 Wisdom, -2 Charisma"),
    "Ratfolk": ({"dexterity": 2, "intelligence": 2, "strength": -2}, "+2 Dexterity, +2 Intelligence, -2 Strength"),
    "Samsaran": ({"intelligence": 2, "wisdom": 2, "constitution": -2}, "+2 Intelligence, +2 Wisdom, -2 Constitution"),
    "Strix": ({"dexterity": 2, "charisma": -2}, "+2 Dexterity, -2 Charisma"),
    "Suli": ({"strength": 2, "charisma": 2, "intelligence": -2}, "+2 Strength, +2 Charisma, -2 Intelligence"),
    "Svirfneblin": ({"dexterity": 2, "wisdom": 2, "strength": -2, "charisma": -4}, "+2 Dexterity, +2 Wisdom, -2 Strength, -4 Charisma"),
    "Sylph": ({"dexterity": 2, "intelligence": 2, "constitution": -2}, "+2 Dexterity, +2 Intelligence, -2 Constitution"),
    "Tengu": ({"dexterity": 2, "wisdom": 2, "constitution": -2}, "+2 Dexterity, +2 Wisdom, -2 Constitution"),
    "Tiefling": ({"dexterity": 2, "intelligence": 2, "charisma": -2}, "+2 Dexterity, +2 Intelligence, -2 Charisma"),
    "Undine": ({"dexterity": 2, "wisdom": 2, "charisma": -2}, "+2 Dexterity, +2 Wisdom, -2 Charisma"),
    "Vanara": ({"dexterity": 2, "wisdom": 2, "charisma": -2}, "+2 Dexterity, +2 Wisdom, -2 Charisma"),
    "Vishkanya": ({"dexterity": 2, "charisma": 2, "wisdom": -2}, "+2 Dexterity, +2 Charisma, -2 Wisdom"),
    "Wayang": ({"dexterity": 2, "intelligence": 2, "wisdom": -2}, "+2 Dexterity, +2 Intelligence, -2 Wisdom"),
}

RACE_TRAITS_STRUCTURE = {
    "Dwarf": {
        "standard_traits": [
            "Medium", "Slow and Steady", "Darkvision", "Defensive Training", "Greed",
            "Hatred", "Hardy", "Stability", "Stonecunning", "Weapon Familiarity"
        ],
        "alternate_traits": [
            {"name": "Barrow Warden", "replaces": ["Hatred"], "description": "Replaces hatred."},
            {"name": "Craftsman", "replaces": ["Greed"], "description": "Replaces greed."},
            {"name": "Deep Warrior", "replaces": ["Defensive Training", "Hatred"], "description": "Replaces defensive training and hatred."},
            {"name": "Desert Delver", "replaces": ["Greed", "Stonecunning"], "description": "Replaces greed and stonecunning."},
            {"name": "Dusksight", "replaces": ["Darkvision"], "description": "Replaces darkvision."},
            {"name": "Iron Within", "replaces": ["Defensive Training", "Hatred"], "description": "Replaces defensive training and hatred."},
            {"name": "Lorekeeper", "replaces": ["Greed"], "description": "Replaces greed."},
            {"name": "Minesight", "replaces": ["Darkvision"], "description": "Replaces darkvision."},
            {"name": "Relentless", "replaces": ["Stability"], "description": "Replaces stability."},
            {"name": "Rock Stepper", "replaces": ["Stonecunning"], "description": "Replaces stonecunning."},
            {"name": "Saltbeard", "replaces": ["Defensive Training", "Hatred", "Stonecunning"], "description": "Replaces defensive training, hatred, and stonecunning."},
            {"name": "Shadowplay", "replaces": ["Greed"], "description": "Replaces greed."},
            {"name": "Siege Survivor", "replaces": ["Hardy"], "description": "Replaces hardy."},
            {"name": "Sky Sentinel", "replaces": ["Defensive Training", "Hatred"], "description": "Replaces defensive training and hatred."},
            {"name": "Slag Child", "replaces": ["Hardy"], "description": "Replaces hardy."},
            {"name": "Spell Smasher", "replaces": ["Hatred"], "description": "Replaces hatred."},
            {"name": "Stoic Negotiator", "replaces": ["Greed"], "description": "Replaces greed."},
            {"name": "Surface Survivalist", "replaces": ["Stonecunning"], "description": "Replaces stonecunning."},
            {"name": "Wyrmscourged", "replaces": ["Defensive Training", "Hatred"], "description": "Replaces defensive training and hatred."}
        ]
    },
    "Elf": {
        "standard_traits": [
            "Medium", "Elven Speed", "Low-Light Vision", "Elven Immunities", "Elven Magic", "Keen Senses", "Weapon Familiarity"
        ],
        "alternate_traits": [
            {"name": "Arcane Focus", "replaces": ["Weapon Familiarity"], "description": "Replaces weapon familiarity."},
            {"name": "Crossbow Training", "replaces": ["Weapon Familiarity"], "description": "Replaces weapon familiarity."},
            {"name": "Desert Fleet", "replaces": ["Elven Speed"], "description": "Replaces elven speed."},
            {"name": "Dreamspeaker", "replaces": ["Elven Immunities"], "description": "Replaces elven immunities."},
            {"name": "Elemental Resistance", "replaces": ["Elven Immunities"], "description": "Replaces elven immunities."},
            {"name": "Envoy", "replaces": ["Elven Magic"], "description": "Replaces elven magic."},
            {"name": "Fleet-Footed", "replaces": ["Weapon Familiarity"], "description": "Replaces weapon familiarity."},
            {"name": "Lightbringer", "replaces": ["Elven Magic"], "description": "Replaces elven magic."},
            {"name": "Long-Lived", "replaces": ["Elven Magic"], "description": "Replaces elven magic."},
            {"name": "Silent Hunter", "replaces": ["Elven Magic"], "description": "Replaces elven magic."},
            {"name": "Spirit of the Waters", "replaces": ["Elven Magic"], "description": "Replaces elven magic."},
            {"name": "Urbanite", "replaces": ["Keen Senses"], "description": "Replaces keen senses."},
            {"name": "Woodcraft", "replaces": ["Elven Magic"], "description": "Replaces elven magic."}
        ]
    },
    "Gnome": {
        "standard_traits": [
            "Small", "Slow Speed", "Low-Light Vision", "Defensive Training", "Gnome Magic",
            "Hatred", "Illusion Resistance", "Keen Senses", "Obsessive", "Weapon Familiarity"
        ],
        "alternate_traits": [
            {"name": "Academician", "replaces": ["Obsessive"], "description": "Replaces obsessive."},
            {"name": "Artisan", "replaces": ["Obsessive"], "description": "Replaces obsessive."},
            {"name": "Bog-Treader", "replaces": ["Defensive Training", "Hatred"], "description": "Replaces defensive training and hatred."},
            {"name": "Darkvision", "replaces": ["Low-Light Vision"], "description": "Replaces low-light vision."},
            {"name": "Eternal Hope", "replaces": ["Defensive Training", "Hatred"], "description": "Replaces defensive training and hatred."},
            {"name": "Fell Magic", "replaces": ["Gnome Magic"], "description": "Replaces gnome magic."},
            {"name": "First World Magic", "replaces": ["Gnome Magic"], "description": "Replaces gnome magic."},
            {"name": "Gift of Tongues", "replaces": ["Defensive Training", "Hatred"], "description": "Replaces defensive training and hatred."},
            {"name": "Inquisitive", "replaces": ["Keen Senses"], "description": "Replaces keen senses."},
            {"name": "Master Tinker", "replaces": ["Defensive Training", "Hatred"], "description": "Replaces defensive training and hatred."},
            {"name": "Pyromaniac", "replaces": ["Gnome Magic"], "description": "Replaces gnome magic."},
            {"name": "Utilitarian Magic", "replaces": ["Gnome Magic"], "description": "Replaces gnome magic."}
        ]
    },
    "Half-Elf": {
        "standard_traits": [
            "Medium", "Normal Speed", "Low-Light Vision", "Adaptability", "Elf Blood",
            "Elven Immunities", "Keen Senses", "Multitalented"
        ],
        "alternate_traits": [
            {"name": "Ancestral Arms", "replaces": ["Adaptability"], "description": "Replaces adaptability."},
            {"name": "Arcane Training", "replaces": ["Multitalented"], "description": "Replaces multitalented."},
            {"name": "Dual Talent", "replaces": ["Adaptability", "Multitalented"], "description": "Replaces adaptability and multitalented. Grants +2 to a second ability score."},
            {"name": "Elven Arcane Focus", "replaces": ["Adaptability"], "description": "Replaces adaptability."},
            {"name": "Integrated", "replaces": ["Adaptability"], "description": "Replaces adaptability."},
            {"name": "Kindred-Raised", "replaces": ["Adaptability"], "description": "Replaces adaptability."},
            {"name": "Overlook", "replaces": ["Adaptability"], "description": "Replaces adaptability."},
            {"name": "Sociable", "replaces": ["Adaptability"], "description": "Replaces adaptability."},
            {"name": "Water Child", "replaces": ["Adaptability", "Multitalented"], "description": "Replaces adaptability and multitalented."},
            {"name": "Wary", "replaces": ["Adaptability"], "description": "Replaces adaptability."}
        ]
    },
    "Halfling": {
        "standard_traits": [
            "Small", "Slow Speed", "Fearless", "Halfling Luck", "Keen Senses", "Sure-Footed", "Weapon Familiarity"
        ],
        "alternate_traits": [
            {"name": "Adaptable Luck", "replaces": ["Halfling Luck"], "description": "Replaces halfling luck."},
            {"name": "Craven", "replaces": ["Fearless"], "description": "Replaces fearless."},
            {"name": "Fleet of Foot", "replaces": ["Slow Speed", "Sure-Footed"], "description": "Replaces slow speed and sure-footed."},
            {"name": "Ingratiating", "replaces": ["Fearless"], "description": "Replaces fearless."},
            {"name": "Low-Light Vision", "replaces": ["Keen Senses"], "description": "Replaces keen senses."},
            {"name": "Outrider", "replaces": ["Sure-Footed"], "description": "Replaces sure-footed."},
            {"name": "Polyglot", "replaces": ["Keen Senses"], "description": "Replaces keen senses."},
            {"name": "Practicality", "replaces": ["Fearless"], "description": "Replaces fearless."},
            {"name": "Shiftless", "replaces": ["Sure-Footed"], "description": "Replaces sure-footed."},
            {"name": "Underfoot", "replaces": ["Halfling Luck"], "description": "Replaces halfling luck."},
            {"name": "Wanderlust", "replaces": ["Fearless", "Halfling Luck"], "description": "Replaces fearless and halfling luck."}
        ]
    },
    "Half-Orc": {
        "standard_traits": [
            "Medium", "Normal Speed", "Darkvision", "Intimidating", "Orc Blood",
            "Orc Ferocity", "Weapon Familiarity"
        ],
        "alternate_traits": [
            {"name": "Bestial", "replaces": ["Orc Ferocity"], "description": "Replaces orc ferocity."},
            {"name": "Chain Fighter", "replaces": ["Weapon Familiarity"], "description": "Replaces weapon familiarity."},
            {"name": "City-Raised", "replaces": ["Weapon Familiarity"], "description": "Replaces weapon familiarity."},
            {"name": "Fate's Favored", "replaces": ["Orc Ferocity"], "description": "Replaces orc ferocity."},
            {"name": "Overlooked Inkeeper", "replaces": ["Intimidating"], "description": "Replaces intimidating."},
            {"name": "Sacred Tattoo", "replaces": ["Orc Ferocity"], "description": "Replaces orc ferocity."},
            {"name": "Scavenger", "replaces": ["Intimidating"], "description": "Replaces intimidating."},
            {"name": "Shaman's Apprentice", "replaces": ["Orc Ferocity"], "description": "Replaces orc ferocity."},
            {"name": "Toothy", "replaces": ["Orc Ferocity"], "description": "Replaces orc ferocity."}
        ]
    },
    "Human": {
        "standard_traits": [
            "Medium", "Normal Speed", "Bonus Feat", "Skilled"
        ],
        "alternate_traits": [
            {"name": "Adopted Heritage", "replaces": ["Bonus Feat"], "description": "Replaces bonus feat."},
            {"name": "Dual Talent", "replaces": ["Bonus Feat", "Skilled"], "description": "Replaces bonus feat and skilled. Grants +2 to a second ability score."},
            {"name": "Eye for Talent", "replaces": ["Bonus Feat"], "description": "Replaces bonus feat."},
            {"name": "Focused Study", "replaces": ["Bonus Feat"], "description": "Replaces bonus feat."},
            {"name": "Heart of the Fields", "replaces": ["Skilled"], "description": "Replaces skilled."},
            {"name": "Heart of the Mountains", "replaces": ["Skilled"], "description": "Replaces skilled."},
            {"name": "Heart of the Sea", "replaces": ["Skilled"], "description": "Replaces skilled."},
            {"name": "Heart of the Slums", "replaces": ["Skilled"], "description": "Replaces skilled."},
            {"name": "Heart of the Snows", "replaces": ["Skilled"], "description": "Replaces skilled."},
            {"name": "Heart of the Streets", "replaces": ["Skilled"], "description": "Replaces skilled."},
            {"name": "Heart of the Sun", "replaces": ["Skilled"], "description": "Replaces skilled."},
            {"name": "Heart of the Wilderness", "replaces": ["Skilled"], "description": "Replaces skilled."}
        ]
    },
    "Tiefling": {
        "standard_traits": [
            "Medium", "Normal Speed", "Darkvision", "Fiendish Resistance", "Fiendish Sorcery", "Preternatural Awareness", "Skilled"
        ],
        "alternate_traits": [
            {"name": "Beguiling Liar", "replaces": ["Fiendish Sorcery"], "description": "Replaces fiendish sorcery."},
            {"name": "Claws", "replaces": ["Fiendish Sorcery"], "description": "Replaces fiendish sorcery."},
            {"name": " Maw or Claw", "replaces": ["Fiendish Sorcery"], "description": "Replaces fiendish sorcery."},
            {"name": "Pass for Human", "replaces": ["Darkvision"], "description": "Replaces darkvision."},
            {"name": "Scaled Skin", "replaces": ["Fiendish Resistance"], "description": "Replaces fiendish resistance."},
            {"name": "Soul Seer", "replaces": ["Fiendish Sorcery"], "description": "Replaces fiendish sorcery."},
            {"name": "Vestigial Wings", "replaces": ["Fiendish Sorcery"], "description": "Replaces fiendish sorcery."}
        ]
    }
}

def main():
    if not DATA_FILE.exists():
        print(f"Error: {DATA_FILE} not found.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    races = data.get("races", {})
    updated_count = 0

    for race_name, (asi_dict, asi_text) in RACE_ASI_FIXES.items():
        if race_name in races:
            races[race_name]["ability_score_increase"] = asi_dict
            races[race_name]["ability_score_increase_text"] = asi_text
            updated_count += 1

    for race_name, trait_struct in RACE_TRAITS_STRUCTURE.items():
        if race_name in races:
            races[race_name]["standard_traits"] = trait_struct["standard_traits"]
            races[race_name]["alternate_traits"] = trait_struct["alternate_traits"]
            races[race_name]["traits"] = trait_struct["standard_traits"]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully updated {updated_count} race ability score modifiers & traits in {DATA_FILE.name}")

if __name__ == "__main__":
    main()
