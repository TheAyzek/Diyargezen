# creators/pathfinder1e_creator.py
"""
Pathfinder 1e Character Creator
Implements Pathfinder 1e specific rules: BAB, saves, skill ranks, feat prerequisites
"""

from typing import Dict, Any, List
from .base_creator import BaseCharacterCreator


class Pathfinder1ECreator(BaseCharacterCreator):
    """Pathfinder 1e Character Creator implementing all core rules"""

    def __init__(self):
        super().__init__("Pathfinder 1e", "pathfinder_1e_data.json")

    def create_character(self) -> Dict[str, Any]:
        """Create a Pathfinder 1e character with all required components"""
        print("=== Pathfinder 1e Karakter Oluşturucu ===")

        # Race selection
        race_names = sorted(self.data.get("races", {}).keys())
        selected_race = self._prompt_selection(race_names, "Irk seçin:")

        # Class selection
        class_names = sorted(self.data.get("classes", {}).keys())
        selected_class = self._prompt_selection(class_names, "Sınıf seçin:")

        # Get race and class data
        race_data = self.data["races"][selected_race]
        class_data = self.data["classes"][selected_class]

        # Ability score generation (Pathfinder uses 15 point buy)
        print("\nPathfinder 1e 15-point buy sistemi:")
        base_scores = self._prompt_pathfinder_point_buy()

        # Apply racial bonuses
        final_scores = self._apply_racial_bonuses(base_scores, race_data)

        # Calculate modifiers
        modifiers = {ability: (score - 10) // 2 for ability, score in final_scores.items()}

        # Calculate skill ranks
        int_modifier = modifiers["intelligence"]
        class_skill_ranks = class_data.get("skill_ranks_per_level", 2) + int_modifier
        total_skill_ranks = max(1, class_skill_ranks)  # Minimum 1

        # Select skills
        available_skills = self.data.get("skills", {})
        selected_skills = self._select_skills(available_skills, total_skill_ranks, class_data)

        # Select feat (with prerequisite checking)
        available_feats = self.data.get("feats", {})
        selected_feat = self._select_feat_with_prerequisites(available_feats, final_scores, modifiers)

        # Calculate BAB and saves
        bab = self._calculate_bab(class_data, 1)  # Level 1
        saves = self._calculate_saves(class_data, modifiers, 1)  # Level 1

        # Create character dict
        character = {
            "system": "PATHFINDER_1E",
            "name": input("Karakter adı: ").strip() or "İsimsiz",
            "race": selected_race,
            "class": selected_class,
            "level": 1,
            "experience": 0,
            "abilities": final_scores,
            "modifiers": modifiers,
            "race_data": race_data,
            "class_data": class_data,
            "skill_ranks": selected_skills,
            "total_skill_ranks": total_skill_ranks,
            "available_skill_ranks": total_skill_ranks - sum(selected_skills.values()),
            "feat": selected_feat,
            "bab": bab,
            "saves": saves,
            "hit_points": self._calculate_hit_points(class_data, modifiers["constitution"]),
            "initiative": modifiers["dexterity"],
            "speed": race_data.get("speed", 30)
        }

        # Calculate derived stats
        character.update(self.calculate_derived_stats(character))

        return character

    def _prompt_pathfinder_point_buy(self) -> Dict[str, int]:
        """Pathfinder 1e point buy (15 points, scores 7-18)"""
        cost_map = {7: -4, 8: -2, 9: -1, 10: 0, 11: 1, 12: 2, 13: 3, 14: 5, 15: 7, 16: 10, 17: 13, 18: 17}
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

        print("Point Buy sistemi (15 puan, 7-18 arası):")
        print("Maliyetler: 7:-4, 8:-2, 9:-1, 10:0, 11:1, 12:2, 13:3, 14:5, 15:7, 16:10, 17:13, 18:17")

        while True:
            scores = {}
            spent = 0

            for ability in abilities:
                while True:
                    try:
                        val = int(input(f"{ability.title()} (7-18): "))
                        if 7 <= val <= 18:
                            spent += cost_map[val]
                            scores[ability] = val
                            break
                        else:
                            print("7-18 arası değer girin.")
                    except ValueError:
                        print("Geçerli bir sayı girin.")

            if spent <= 15:
                print(f"Toplam harcanan puan: {spent}/15")
                return scores
            else:
                print(f"Çok fazla puan harcandı ({spent}/15). Tekrar deneyin.")

    def _apply_racial_bonuses(self, base_scores: Dict[str, int], race_data: Dict[str, Any]) -> Dict[str, int]:
        """Apply racial ability score modifiers"""
        final_scores = base_scores.copy()
        asi = race_data.get("ability_score_modifiers", {})

        for ability, modifier in asi.items():
            if ability in final_scores:
                final_scores[ability] += modifier

        return final_scores

    def _select_skills(self, available_skills: Dict[str, Any], total_ranks: int, class_data: Dict[str, Any]) -> Dict[str, int]:
        """Select skills and assign ranks"""
        class_skills = class_data.get("class_skills", [])
        selected = {}

        print(f"\nYetenek puanı dağıtımı ({total_ranks} puan):")
        print("Sınıf yetenekleri: " + ", ".join(class_skills))

        remaining_ranks = total_ranks

        while remaining_ranks > 0:
            print(f"\nKalan puan: {remaining_ranks}")
            skill_names = sorted(available_skills.keys())

            # Show current skill ranks
            print("Mevcut yetenek puanları:")
            for skill in skill_names:
                current = selected.get(skill, 0)
                is_class_skill = skill in class_skills
                print(f"  {skill}: {current} ({'sınıf yeteneği' if is_class_skill else 'çapraz sınıf'})")

            skill_choice = self._prompt_selection(skill_names, "Hangi yeteneğe puan vereceksiniz? (0: bitir)")

            if skill_choice == "0":
                break

            # Determine max ranks for this skill
            is_class_skill = skill_choice in class_skills
            max_ranks = total_ranks if is_class_skill else total_ranks // 2

            current_ranks = selected.get(skill_choice, 0)
            if current_ranks >= max_ranks:
                print(f"Bu yetenek için maksimum puana ulaştınız ({max_ranks})")
                continue

            # Ask how many ranks to add
            while True:
                try:
                    add_ranks = int(input(f"Kaç puan ekleyeceksiniz? (max {max_ranks - current_ranks}): "))
                    if 1 <= add_ranks <= (max_ranks - current_ranks) and add_ranks <= remaining_ranks:
                        selected[skill_choice] = current_ranks + add_ranks
                        remaining_ranks -= add_ranks
                        break
                    else:
                        print("Geçersiz miktar.")
                except ValueError:
                    print("Geçerli bir sayı girin.")

        return selected

    def _select_feat_with_prerequisites(self, available_feats: Dict[str, Any], abilities: Dict[str, int], modifiers: Dict[str, int]) -> str:
        """Select a feat with prerequisite checking"""
        print("\nFeat seçimi:")

        valid_feats = []
        for feat_name, feat_data in available_feats.items():
            prerequisites = feat_data.get("prerequisites", {})
            if self._check_prerequisites(prerequisites, abilities, modifiers):
                valid_feats.append(feat_name)
            else:
                print(f"  {feat_name}: Gereksinimler karşılanmıyor - {prerequisites}")

        if not valid_feats:
            print("Uygun feat bulunamadı! Temel feat veriliyor.")
            return "Temel Feat"

        selected_feat = self._prompt_selection(valid_feats, "Hangi feat'i seçiyorsunuz?")
        return selected_feat

    def _check_prerequisites(self, prerequisites: Dict[str, Any], abilities: Dict[str, int], modifiers: Dict[str, int]) -> bool:
        """Check if character meets feat prerequisites"""
        for prereq_type, prereq_value in prerequisites.items():
            if prereq_type == "ability":
                for ability, min_score in prereq_value.items():
                    if abilities.get(ability, 10) < min_score:
                        return False
            elif prereq_type == "bab":
                # BAB prerequisite (simplified for level 1)
                if prereq_value > 0:  # Any BAB requirement fails at level 1
                    return False
            # Add more prerequisite types as needed

        return True

    def _calculate_bab(self, class_data: Dict[str, Any], level: int) -> int:
        """Calculate Base Attack Bonus"""
        bab_progression = class_data.get("bab_progression", "medium")  # full, medium, low

        if bab_progression == "full":
            return level
        elif bab_progression == "medium":
            return (level * 3) // 4
        else:  # low
            return level // 2

    def _calculate_saves(self, class_data: Dict[str, Any], modifiers: Dict[str, int], level: int) -> Dict[str, int]:
        """Calculate saving throws"""
        save_progressions = class_data.get("saving_throws", {})
        saves = {}

        for save_type, progression in save_progressions.items():
            if progression == "good":
                base_save = 2 + (level // 2)  # +2 at level 1, +1 every 2 levels
            else:  # poor
                base_save = level // 3  # +0 at level 1, +1 every 3 levels

            ability_mod = modifiers.get(self._get_save_ability(save_type), 0)
            saves[save_type] = base_save + ability_mod

        return saves

    def _get_save_ability(self, save_type: str) -> str:
        """Get ability modifier for saving throw"""
        save_abilities = {
            "fortitude": "constitution",
            "reflex": "dexterity",
            "will": "wisdom"
        }
        return save_abilities.get(save_type, "constitution")

    def _calculate_hit_points(self, class_data: Dict[str, Any], con_modifier: int) -> int:
        """Calculate level 1 hit points"""
        hit_die = class_data.get("hit_die", 8)
        return hit_die + con_modifier

    def _prompt_selection(self, options: List[str], prompt: str) -> str:
        """Generic selection prompt"""
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}) {option}")

        while True:
            try:
                choice = int(input("Seçiminiz: "))
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                else:
                    print(f"1-{len(options)} arası seçin.")
            except ValueError:
                print("Geçerli bir sayı girin.")

    def validate_character(self, character: Dict[str, Any]) -> List[str]:
        """Validate Pathfinder 1e character data"""
        errors = []

        # Required fields
        required_fields = ["race", "class", "abilities", "level", "bab", "saves"]
        for field in required_fields:
            if field not in character:
                errors.append(f"Eksik alan: {field}")

        # Ability scores validation (7-18 for Pathfinder)
        if "abilities" in character:
            for ability, score in character["abilities"].items():
                if not (7 <= score <= 18):
                    errors.append(f"Geçersiz {ability} puanı: {score} (7-18 arası olmalı)")

        # Level validation
        if "level" in character and not (1 <= character["level"] <= 20):
            errors.append(f"Geçersiz seviye: {character['level']} (1-20 arası olmalı)")

        # BAB validation
        if "bab" in character and character["bab"] < 0:
            errors.append("BAB negatif olamaz")

        return errors

    def calculate_derived_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived statistics for Pathfinder 1e"""
        derived = {}

        # Armor Class (base 10 + dex + armor + etc.)
        dex_mod = character.get("modifiers", {}).get("dexterity", 0)
        derived["armor_class"] = 10 + dex_mod

        # Initiative
        derived["initiative"] = dex_mod

        # Skill modifiers (ability mod + ranks + misc)
        derived["skill_modifiers"] = {}
        skills_data = self.data.get("skills", {})
        modifiers = character.get("modifiers", {})
        skill_ranks = character.get("skill_ranks", {})

        for skill_name, skill_info in skills_data.items():
            ability = skill_info.get("ability", "dexterity")
            ability_mod = modifiers.get(ability, 0)
            ranks = skill_ranks.get(skill_name, 0)

            # Class skill bonus (+3 if ranks > 0)
            class_skills = character.get("class_data", {}).get("class_skills", [])
            class_bonus = 3 if (skill_name in class_skills and ranks > 0) else 0

            total_mod = ability_mod + ranks + class_bonus
            derived["skill_modifiers"][skill_name] = total_mod

        return derived