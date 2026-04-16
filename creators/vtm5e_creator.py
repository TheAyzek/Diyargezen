# creators/vtm5e_creator.py
"""
Vampire: The Masquerade 5e Character Creator
Implements VtM 5e rules: Clan-based, dot system, attributes/skills/disciplines.
Dice System: d10 dice pool (successes on 6+)
"""

from typing import Dict, Any, List
from .base_creator import BaseCharacterCreator, DICE_D10_POOL


class VTM5ECreator(BaseCharacterCreator):
    """Vampire: The Masquerade 5e Character Creator"""

    DICE_SYSTEM = DICE_D10_POOL

    def __init__(self):
        super().__init__("Vampire: The Masquerade 5e", "vtm_data.json")

    def create_character(self) -> Dict[str, Any]:
        """Create a VtM 5e character"""
        print("=== Vampire: The Masquerade 5e Karakter Oluşturucu ===")

        # Clan selection
        clan_names = sorted(self.data.get("clans", {}).keys())
        selected_clan = self._prompt_selection(clan_names, "Klan seçin:")

        # Predator type selection (affects attribute distribution)
        predator_types = self.data.get("predator_types", {})
        selected_predator = self._prompt_selection(
            sorted(predator_types.keys()),
            "Predator Type seçin:"
        )

        # Get clan and predator data
        clan_data = self.data["clans"][selected_clan]
        predator_data = predator_types[selected_predator]

        # Attribute distribution (7/5/3 dots for Physical/Social/Mental)
        attributes = self._distribute_attribute_dots(predator_data)

        # Skill distribution (9/7/4 dots for Physical/Social/Mental)
        skills = self._distribute_skill_dots()

        # Discipline selection (clan-based)
        disciplines = self._select_clan_disciplines(clan_data)

        # Background selection
        backgrounds = self._select_backgrounds()

        # Create character dict
        character = {
            "system": "VAMPIRE_THE_MASQUERADE_5E",
            "name": input("Karakter adı: ").strip() or "İsimsiz",
            "clan": selected_clan,
            "predator_type": selected_predator,
            "generation": 13,  # Starting generation
            "blood_potency": 1,
            "hunger": 1,  # Starting hunger
            "humanity": 7,  # Starting humanity
            "attributes": attributes,
            "skills": skills,
            "disciplines": disciplines,
            "backgrounds": backgrounds,
            "clan_data": clan_data,
            "predator_data": predator_data,
            "health": 3,  # Base health
            "willpower": 3  # Base willpower
        }

        # Calculate derived stats
        character.update(self.calculate_derived_stats(character))

        return character

    def _distribute_attribute_dots(self, predator_data: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
        """Distribute attribute dots based on predator type"""
        # Base distribution: 7/5/3 for Physical/Social/Mental
        base_distribution = {"physical": 7, "social": 5, "mental": 3}

        # Predator type modifiers
        predator_mods = predator_data.get("attribute_modifiers", {})

        # Apply modifiers
        distribution = {}
        for category in ["physical", "social", "mental"]:
            base_dots = base_distribution[category]
            modifier = predator_mods.get(category, 0)
            distribution[category] = base_dots + modifier

        # Get attribute categories
        attribute_categories = self.data.get("attributes", {})

        attributes = {}
        for category, dots in distribution.items():
            if category in attribute_categories:
                attr_dict = {}
                attr_names = attribute_categories[category]

                print(f"\n{category.title()} nitelikleri ({dots} puan):")
                remaining_dots = dots

                for attr in attr_names:
                    while True:
                        try:
                            dots_to_assign = int(input(f"{attr.title()} (0-5, kalan: {remaining_dots}): "))
                            if 0 <= dots_to_assign <= 5 and dots_to_assign <= remaining_dots:
                                attr_dict[attr] = dots_to_assign
                                remaining_dots -= dots_to_assign
                                break
                            else:
                                print("Geçersiz değer.")
                        except ValueError:
                            print("Geçerli bir sayı girin.")

                    if remaining_dots == 0:
                        break

                attributes[category] = attr_dict

        return attributes

    def _distribute_skill_dots(self) -> Dict[str, Dict[str, int]]:
        """Distribute skill dots (9/7/4 for Physical/Social/Mental)"""
        distribution = {"physical": 9, "social": 7, "mental": 4}
        skill_categories = self.data.get("skills", {})

        skills = {}
        for category, dots in distribution.items():
            if category in skill_categories:
                skill_dict = {}
                skill_names = skill_categories[category]

                print(f"\n{category.title()} becerileri ({dots} puan):")
                remaining_dots = dots

                for skill in skill_names:
                    while True:
                        try:
                            dots_to_assign = int(input(f"{skill.title()} (0-5, kalan: {remaining_dots}): "))
                            if 0 <= dots_to_assign <= 5 and dots_to_assign <= remaining_dots:
                                skill_dict[skill] = dots_to_assign
                                remaining_dots -= dots_to_assign
                                break
                            else:
                                print("Geçersiz değer.")
                        except ValueError:
                            print("Geçerli bir sayı girin.")

                    if remaining_dots == 0:
                        break

                skills[category] = skill_dict

        return skills

    def _select_clan_disciplines(self, clan_data: Dict[str, Any]) -> Dict[str, int]:
        """Select clan disciplines (starting dots)"""
        clan_disciplines = clan_data.get("disciplines", [])
        disciplines = {}

        print("\nKlan disiplinleri (1 puan her birine):")
        for discipline in clan_disciplines:
            disciplines[discipline] = 1
            print(f"  {discipline}: 1")

        return disciplines

    def _select_backgrounds(self) -> Dict[str, int]:
        """Select backgrounds (5 dots total)"""
        available_backgrounds = self.data.get("backgrounds", {})
        backgrounds = {}

        print("\nArka planlar (5 puan toplam):")
        remaining_dots = 5

        while remaining_dots > 0:
            bg_names = sorted(available_backgrounds.keys())
            bg_choice = self._prompt_selection(bg_names, f"Arka plan seçin (kalan puan: {remaining_dots}):")

            while True:
                try:
                    dots = int(input(f"{bg_choice} için kaç puan? (max {remaining_dots}): "))
                    if 1 <= dots <= remaining_dots:
                        backgrounds[bg_choice] = dots
                        remaining_dots -= dots
                        break
                    else:
                        print("Geçersiz miktar.")
                except ValueError:
                    print("Geçerli bir sayı girin.")

        return backgrounds

    def validate_character(self, character: Dict[str, Any]) -> List[str]:
        """Validate VtM 5e character data"""
        errors = []

        # Required fields
        required_fields = ["clan", "attributes", "skills", "disciplines"]
        for field in required_fields:
            if field not in character:
                errors.append(f"Eksik alan: {field}")

        # Attribute validation (dot system 0-5)
        if "attributes" in character:
            for category, attrs in character["attributes"].items():
                for attr, dots in attrs.items():
                    if not (0 <= dots <= 5):
                        errors.append(f"Geçersiz {attr} niteliği: {dots} (0-5 arası olmalı)")

        # Skill validation
        if "skills" in character:
            for category, skills in character["skills"].items():
                for skill, dots in skills.items():
                    if not (0 <= dots <= 5):
                        errors.append(f"Geçersiz {skill} becerisi: {dots} (0-5 arası olmalı)")

        # Blood potency validation
        if "blood_potency" in character and not (0 <= character["blood_potency"] <= 10):
            errors.append("Blood potency 0-10 arası olmalı")

        return errors

    def calculate_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived statistics for VtM 5e"""
        derived: Dict[str, Any] = {}

        stamina = character.get("attributes", {}).get("physical", {}).get("stamina", 1)
        derived["max_health"] = stamina + 3

        composure = character.get("attributes", {}).get("social", {}).get("composure", 1)
        resolve = character.get("attributes", {}).get("mental", {}).get("resolve", 1)
        derived["max_willpower"] = composure + resolve

        dexterity = character.get("attributes", {}).get("physical", {}).get("dexterity", 1)
        derived["initiative"] = dexterity + composure

        wits = character.get("attributes", {}).get("mental", {}).get("wits", 1)
        derived["defense"] = min(dexterity, wits)

        strength = character.get("attributes", {}).get("physical", {}).get("strength", 1)
        derived["speed"] = strength + dexterity + 5

        return derived

    def export_data(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """VtM 5e karakterini JSON-serializable formata dönüştür."""
        safe_keys = {
            "system", "name", "clan", "predator_type", "generation",
            "blood_potency", "hunger", "humanity", "attributes", "skills",
            "disciplines", "backgrounds",
        }
        exported: Dict[str, Any] = {"system": "VTM5E", "dice_system": self.DICE_SYSTEM.name}
        for key in safe_keys:
            if key in character:
                exported[key] = character[key]
        stats = self.calculate_stats(character)
        exported.update({k: v for k, v in stats.items() if k not in exported})
        return exported