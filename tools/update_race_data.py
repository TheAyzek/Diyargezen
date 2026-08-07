import json
import os

OFFICIAL_PF1E_ASI = {
    'dwarf': {'constitution': 2, 'wisdom': 2, 'charisma': -2},
    'elf': {'dexterity': 2, 'intelligence': 2, 'constitution': -2},
    'gnome': {'constitution': 2, 'charisma': 2, 'strength': -2},
    'half-elf': {'any': 2},
    'halfling': {'dexterity': 2, 'charisma': 2, 'strength': -2},
    'half-orc': {'any': 2},
    'human': {'any': 2},
    'primitive human': {'any': 2},
    'aasimar': {'wisdom': 2, 'charisma': 2},
    'adaro': {'dexterity': 2, 'constitution': 2, 'intelligence': -2},
    'android': {'dexterity': 2, 'intelligence': 2, 'charisma': -2},
    'aphorite': {'strength': 2, 'wisdom': 2, 'charisma': -2},
    'aquatic elf': {'dexterity': 2, 'intelligence': 2, 'constitution': -2},
    'astomoi': {'intelligence': 2, 'wisdom': 2, 'constitution': -2},
    'being of ib': {'wisdom': 2, 'charisma': -2},
    'boggard': {'constitution': 2, 'wisdom': 2, 'charisma': -2},
    'caligni': {'dexterity': 2, 'constitution': 2, 'intelligence': -2},
    'catfolk': {'dexterity': 2, 'charisma': 2, 'wisdom': -2},
    'cecaelia': {'dexterity': 2, 'wisdom': 2, 'constitution': -2},
    'changeling': {'wisdom': 2, 'charisma': 2, 'constitution': -2},
    'deep one hybrid': {'constitution': 2, 'wisdom': 2, 'dexterity': -2},
    'dhampir': {'dexterity': 2, 'charisma': 2, 'constitution': -2},
    'drow': {'dexterity': 2, 'charisma': 2, 'constitution': -2},
    'drow noble': {'dexterity': 4, 'intelligence': 2, 'wisdom': 2, 'charisma': 2, 'constitution': -2},
    'duergar': {'constitution': 2, 'wisdom': 2, 'charisma': -4},
    'duskwalker': {'dexterity': 2, 'wisdom': 2, 'constitution': -2},
    'fetchling': {'dexterity': 2, 'charisma': 2, 'wisdom': -2},
    'ganzi': {'constitution': 2, 'charisma': 2, 'intelligence': -2},
    'gathlain': {'dexterity': 2, 'charisma': 2, 'constitution': -2},
    'ghoran': {'constitution': 2, 'charisma': 2, 'intelligence': -2},
    'gillman': {'constitution': 2, 'charisma': 2, 'wisdom': -2},
    'goblin': {'dexterity': 4, 'strength': -2, 'charisma': -2},
    'green martian': {'strength': 2, 'wisdom': 2, 'charisma': -2},
    'grindylow': {'dexterity': 4, 'strength': -2, 'wisdom': -2},
    'grippli': {'dexterity': 2, 'wisdom': 2, 'strength': -2},
    'hobgoblin': {'dexterity': 2, 'constitution': 2},
    'ifrit': {'dexterity': 2, 'charisma': 2, 'wisdom': -2},
    'kasatha': {'dexterity': 2, 'wisdom': 2},
    'kitsune': {'dexterity': 2, 'charisma': 2, 'strength': -2},
    'kobold': {'dexterity': 2, 'strength': -4, 'constitution': -2},
    'kuru': {'dexterity': 2, 'constitution': 2, 'intelligence': -2},
    'lashunta': {'intelligence': 2, 'charisma': 2, 'constitution': -2},
    'locathah': {'dexterity': 2, 'wisdom': 2, 'strength': -2},
    'merfolk': {'dexterity': 2, 'constitution': 2, 'charisma': 2},
    'monkey goblin': {'dexterity': 4, 'wisdom': -2, 'charisma': -2},
    'munavri': {'dexterity': 2, 'intelligence': 2, 'charisma': 2, 'strength': -2},
    'nagaji': {'strength': 2, 'charisma': 2, 'intelligence': -2},
    'naiad': {'dexterity': 2, 'charisma': 2, 'strength': -2},
    'orang-pendak': {'strength': 2, 'wisdom': 2, 'intelligence': -2},
    'orc': {'strength': 4, 'intelligence': -2, 'wisdom': -2, 'charisma': -2},
    'oread': {'strength': 2, 'wisdom': 2, 'charisma': -2},
    'ratfolk': {'dexterity': 2, 'intelligence': 2, 'strength': -2},
    'reborn samsaran': {'intelligence': 2, 'wisdom': 2, 'constitution': -2},
    'reptoid': {'strength': 2, 'charisma': 2, 'intelligence': -2},
    'rougarou': {'strength': 2, 'wisdom': 2, 'intelligence': -2},
    'sahuagin': {'strength': 2, 'wisdom': 2, 'charisma': -2},
    'samsaran': {'intelligence': 2, 'wisdom': 2, 'constitution': -2},
    'shabti': {'constitution': 2, 'charisma': 2},
    'skinwalker': {'wisdom': 2, 'intelligence': -2},
    'strix': {'dexterity': 2, 'charisma': -2},
    'suli': {'strength': 2, 'charisma': 2, 'intelligence': -2},
    'svirfneblin': {'dexterity': 2, 'wisdom': 2, 'strength': -2, 'charisma': -4},
    'sylph': {'dexterity': 2, 'intelligence': 2, 'constitution': -2},
    'syrinx': {'wisdom': 2, 'dexterity': -2},
    'tengu': {'dexterity': 2, 'wisdom': 2, 'constitution': -2},
    'tiefling': {'dexterity': 2, 'intelligence': 2, 'charisma': -2},
    'triaxian': {'constitution': 2, 'wisdom': 2, 'strength': -2},
    'triton': {'strength': 2, 'charisma': 2, 'intelligence': -2},
    'trox': {'strength': 6, 'dexterity': -2, 'intelligence': -2, 'wisdom': -2, 'charisma': -2},
    'undine': {'dexterity': 2, 'wisdom': 2, 'charisma': -2},
    'vanara': {'dexterity': 2, 'wisdom': 2, 'charisma': -2},
    'vine leshy': {'constitution': 2, 'wisdom': 2, 'intelligence': -2},
    'vishkanya': {'dexterity': 2, 'charisma': 2, 'wisdom': -2},
    'wayang': {'dexterity': 2, 'intelligence': 2, 'wisdom': -2},
    'wyrwood': {'dexterity': 2, 'intelligence': 2, 'constitution': -2},
    'wyvaran': {'dexterity': 2, 'wisdom': 2, 'intelligence': -2},
    'yaddithian': {'constitution': 2, 'intelligence': 2, 'wisdom': -2}
}

def format_asi_text(asi_dict):
    if 'any' in asi_dict:
        return f"+{asi_dict['any']} to One Ability Score"
    parts = []
    for stat, val in asi_dict.items():
        sign = f"+{val}" if val >= 0 else f"{val}"
        parts.append(f"{sign} {stat.capitalize()}")
    return ", ".join(parts)

def update_json_data():
    json_path = 'data/pathfinder_1e_data.json'
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    races = data.get('races', {})
    updated_count = 0

    # Clean plural duplicate keys if present e.g. Dwarves, Elves
    keys_to_remove = [k for k in races.keys() if k.endswith('s') and k[:-1] in races]
    for k in keys_to_remove:
        del races[k]

    for race_key, race_obj in races.items():
        r_norm = race_key.lower().strip()
        if r_norm in OFFICIAL_PF1E_ASI:
            official_asi = OFFICIAL_PF1E_ASI[r_norm]
            race_obj['ability_score_increase'] = official_asi
            race_obj['ability_score_increase_text'] = format_asi_text(official_asi)
            updated_count += 1

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated {updated_count} races in {json_path}")

if __name__ == '__main__':
    update_json_data()
