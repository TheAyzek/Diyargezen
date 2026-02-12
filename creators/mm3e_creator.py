# creators/mm3e_creator.py
"""
Mutants & Masterminds 3e Character Creator
Implements M&M 3e rules: Classless, point buy, PL limits, power points
"""

from typing import Dict, Any, List
from .base_creator import BaseCharacterCreator


class MM3ECreator(BaseCharacterCreator):
    """Mutants & Masterminds 3e Character Creator"""

    def __init__(self):
        super().__init__("Mutants & Masterminds 3e", "mm_data.json")

    def create_character(self) -> Dict[str, Any]:
        """Create a M&M 3e character"""
        print("=== Mutants & Masterminds 3e Karakter Oluşturucu ===")

        # Power Level selection
        pl_names = sorted(self.data.get("power_levels", {}).keys())
        selected_pl = self._prompt_selection(pl_names, "Power Level (PL) seçin:")

        # Archetype selection (optional guidance)
        archetype_names = sorted(self.data.get("archetypes", {}).keys())
        selected_archetype = self._prompt_selection(
            archetype_names + ["Özel (Custom)"],
            "Arketip seçin (rehberlik için):"
        )

        # Get PL data
        pl_data = self.data["power_levels"][selected_pl]
        pl_value = pl_data.get("pl", 10)
        power_points = pl_data.get("power_points", 150)

        # Ability scores (point buy from power points)
        abilities = self._purchase_abilities(power_points, pl_value)

        # Skills (point buy)
        remaining_pp, skills = self._purchase_skills(abilities["power_points"], pl_value)

        # Advantages (point buy)
        remaining_pp, advantages = self._purchase_advantages(remaining_pp)

        # Powers (point buy with PL limits)
        remaining_pp, powers = self._purchase_powers(remaining_pp, pl_value)

        # Equipment/Defenses
        remaining_pp, defenses = self._purchase_defenses(remaining_pp, pl_value)

        # Archetype data
        archetype_data = {}
        if selected_archetype != "Özel (Custom)":
            archetype_data = self.data["archetypes"][selected_archetype]

        # Create character dict
        character = {
            "system": "MUTANTS_AND_MASTERMINDS_3E",
            "name": input("Karakter adı: ").strip() or "İsimsiz",
            "power_level": selected_pl,
            "pl_value": pl_value,
            "total_power_points": power_points,
            "remaining_power_points": remaining_pp,
            "abilities": abilities,
            "skills": skills,
            "advantages": advantages,
            "powers": powers,
            "defenses": defenses,
            "archetype": selected_archetype,
            "archetype_data": archetype_data,
            "pl_data": pl_data
        }

        # Calculate derived stats
        character.update(self.calculate_derived_stats(character))

        return character

    def _purchase_abilities(self, total_pp: int, pl: int) -> Dict[str, Any]:
        """Purchase ability scores using power points"""
        abilities = ["strength", "stamina", "agility", "dexterity", "fighting", "intellect", "awareness", "presence"]
        base_costs = {ability: 0 for ability in abilities}  # All start at 0

        print(f"\nYetenek puanları (PL {pl} limiti, {total_pp} PP toplam):")
        print("Maliyet: Her +1 için 1 PP (max PL+2)")

        purchased = {}
        remaining_pp = total_pp

        for ability in abilities:
            while True:
                try:
                    score = int(input(f"{ability.title()} (-5 to {pl+2}): "))
                    if -5 <= score <= pl + 2:
                        cost = abs(score) * 2 if score < 0 else score  # -1 = 2 PP, +1 = 1 PP
                        if cost <= remaining_pp:
                            purchased[ability] = score
                            remaining_pp -= cost
                            print(f"  {ability.title()}: {score} (maliyet: {cost} PP, kalan: {remaining_pp})")
                            break
                        else:
                            print(f"Yetersiz PP (maliyet: {cost}, mevcut: {remaining_pp})")
                    else:
                        print(f"PL limitini aşamaz: -5 to {pl+2}")
                except ValueError:
                    print("Geçerli bir sayı girin.")

        purchased["power_points"] = remaining_pp
        return purchased

    def _purchase_skills(self, available_pp: int, pl: int) -> tuple[int, Dict[str, int]]:
        """Purchase skills using power points"""
        available_skills = self.data.get("skills", {})
        skills = {}

        print(f"\nYetenekler (kalan PP: {available_pp}):")
        print("Maliyet: Her rank için 1 PP (max PL+2)")

        remaining_pp = available_pp

        while remaining_pp > 0:
            skill_names = sorted(available_skills.keys()) + ["Bitir"]
            skill_choice = self._prompt_selection(skill_names, f"Yetenek seçin (kalan PP: {remaining_pp}):")

            if skill_choice == "Bitir":
                break

            current_ranks = skills.get(skill_choice, 0)
            max_ranks = pl + 2

            if current_ranks >= max_ranks:
                print(f"Bu yetenek için maksimum rank aşıldı ({max_ranks})")
                continue

            while True:
                try:
                    ranks_to_add = int(input(f"Kaç rank ekleyeceksiniz? (max {max_ranks - current_ranks}): "))
                    cost = ranks_to_add

                    if 1 <= ranks_to_add <= (max_ranks - current_ranks) and cost <= remaining_pp:
                        skills[skill_choice] = current_ranks + ranks_to_add
                        remaining_pp -= cost
                        print(f"  {skill_choice}: {skills[skill_choice]} ranks (maliyet: {cost})")
                        break
                    else:
                        print("Geçersiz miktar.")
                except ValueError:
                    print("Geçerli bir sayı girin.")

        return remaining_pp, skills

    def _purchase_advantages(self, available_pp: int) -> tuple[int, List[str]]:
        """Purchase advantages"""
        available_advantages = self.data.get("advantages", [])
        advantages = []

        print(f"\nAvantajlar (kalan PP: {available_pp}):")
        print("Maliyet: Çeşitli (1-5 PP)")

        remaining_pp = available_pp

        while remaining_pp > 0:
            adv_names = sorted(available_advantages) + ["Bitir"]
            adv_choice = self._prompt_selection(adv_names, f"Avantaj seçin (kalan PP: {remaining_pp}):")

            if adv_choice == "Bitir":
                break

            # Get advantage cost (simplified)
            cost = self._get_advantage_cost(adv_choice)

            if cost <= remaining_pp:
                advantages.append(adv_choice)
                remaining_pp -= cost
                print(f"  {adv_choice} eklendi (maliyet: {cost} PP)")
            else:
                print(f"Yetersiz PP (maliyet: {cost}, mevcut: {remaining_pp})")

        return remaining_pp, advantages

    def _purchase_powers(self, available_pp: int, pl: int) -> tuple[int, Dict[str, Any]]:
        """Purchase powers with PL limits"""
        available_powers = self.data.get("powers", {})
        powers = {}

        print(f"\nGüçler (PL {pl} limiti, kalan PP: {available_pp}):")
        print("PL Hard Limit: Attack Bonus + Damage Bonus ≤ PL × 2")

        remaining_pp = available_pp
        attack_bonus = 0
        damage_bonus = 0

        while remaining_pp > 0:
            power_names = sorted(available_powers.keys()) + ["Bitir"]
            power_choice = self._prompt_selection(power_names, f"Güç seçin (kalan PP: {remaining_pp}):")

            if power_choice == "Bitir":
                break

            # Check PL limit for attack/damage powers
            power_data = available_powers[power_choice]
            power_type = power_data.get("type", "other")

            if power_type in ["attack", "damage"]:
                if attack_bonus + damage_bonus >= pl * 2:
                    print(f"PL hard limit aşıldı! (mevcut: {attack_bonus + damage_bonus}, limit: {pl * 2})")
                    continue

            # Power effects and modifiers
            power_config = self._configure_power(power_choice, power_data, remaining_pp)

            if power_config:
                cost = power_config["cost"]
                powers[power_choice] = power_config
                remaining_pp -= cost

                # Update PL tracking
                if power_type == "attack":
                    attack_bonus += power_config.get("attack_bonus", 0)
                elif power_type == "damage":
                    damage_bonus += power_config.get("damage_bonus", 0)

                print(f"  {power_choice} eklendi (maliyet: {cost} PP)")

        return remaining_pp, powers

    def _configure_power(self, power_name: str, power_data: Dict[str, Any], available_pp: int) -> Dict[str, Any]:
        """Configure power with effects and modifiers"""
        base_cost = power_data.get("base_cost", 1)
        effects = power_data.get("effects", [])

        print(f"\n{power_name} yapılandırması:")

        # Select effects
        selected_effects = []
        for effect in effects:
            effect_names = [effect["name"]] + ["Atla"]
            choice = self._prompt_selection(effect_names, f"Etki seçin ({effect['name']}):")

            if choice != "Atla":
                selected_effects.append(effect)

        # Calculate total cost with modifiers
        total_cost = base_cost
        for effect in selected_effects:
            modifier = effect.get("cost_modifier", 1)
            total_cost *= modifier

        if total_cost > available_pp:
            print(f"Çok pahalı ({total_cost} PP, mevcut: {available_pp})")
            return None

        return {
            "base_cost": base_cost,
            "effects": selected_effects,
            "cost": total_cost,
            "total_cost": total_cost
        }

    def _purchase_defenses(self, available_pp: int, pl: int) -> tuple[int, Dict[str, int]]:
        """Purchase defenses"""
        defenses = ["dodge", "parry", "fortitude", "toughness", "will"]
        defense_scores = {}

        print(f"\nDefensler (PL {pl} limiti, kalan PP: {available_pp}):")
        print("Maliyet: Her +1 için 1 PP (max PL+2)")

        remaining_pp = available_pp

        for defense in defenses:
            while True:
                try:
                    score = int(input(f"{defense.title()} defense (0 to {pl+2}): "))
                    if 0 <= score <= pl + 2:
                        cost = score
                        if cost <= remaining_pp:
                            defense_scores[defense] = score
                            remaining_pp -= cost
                            print(f"  {defense.title()}: {score} (maliyet: {cost} PP)")
                            break
                        else:
                            print(f"Yetersiz PP (maliyet: {cost}, mevcut: {remaining_pp})")
                    else:
                        print(f"PL limitini aşamaz: 0 to {pl+2}")
                except ValueError:
                    print("Geçerli bir sayı girin.")

        return remaining_pp, defense_scores

    def _get_advantage_cost(self, advantage: str) -> int:
        """Get advantage cost (simplified)"""
        cost_map = {
            "Agile Feint": 1,
            "All-out Attack": 1,
            "Animal Empathy": 1,
            "Artificer": 1,
            "Assessment": 1,
            "Attractive": 1,
            "Beginner's Luck": 1,
            "Benefit": 1,
            "Chokehold": 1,
            "Close Attack": 1,
            "Combat Sense": 1,
            "Connected": 1,
            "Contacts": 1,
            "Daze": 1,
            "Defensive Attack": 1,
            "Defensive Roll": 1,
            "Diehard": 1,
            "Eidetic Memory": 1,
            "Equipment": 1,
            "Evasion": 1,
            "Extraordinary Effort": 1,
            "Fascinate": 1,
            "Fast Grab": 1,
            "Fearless": 1,
            "Fighting Style": 1,
            "Grabbing Finesse": 1,
            "Great Endurance": 1,
            "Hide in Plain Sight": 1,
            "Improved Aim": 1,
            "Improved Critical": 1,
            "Improved Defense": 1,
            "Improved Disarm": 1,
            "Improved Grab": 1,
            "Improved Hold": 1,
            "Improved Initiative": 1,
            "Improved Smash": 1,
            "Improved Trip": 1,
            "Improvised Tools": 1,
            "Improvised Weapons": 1,
            "Inspire": 1,
            "Instant Up": 1,
            "Interpose": 1,
            "Inventor": 1,
            "Jack-of-all-trades": 1,
            "Languages": 1,
            "Leadership": 1,
            "Luck": 1,
            "Minion": 1,
            "Move-by Action": 1,
            "Power Attack": 1,
            "Precise Attack": 1,
            "Prone Fighting": 1,
            "Quick Draw": 1,
            "Ranged Attack": 1,
            "Redirect": 1,
            "Ritualist": 1,
            "Second Chance": 1,
            "Seize Initiative": 1,
            "Set-up": 1,
            "Sidekick": 1,
            "Skill Mastery": 1,
            "Startle": 1,
            "Takedown": 1,
            "Taunt": 1,
            "Teamwork": 1,
            "Throwing Mastery": 1,
            "Tracking": 1,
            "Trance": 1,
            "Ultimate Effort": 2,
            "Uncanny Dodge": 1,
            "Weapon Bind": 1,
            "Weapon Break": 1,
            "Well-informed": 1
        }
        return cost_map.get(advantage, 1)

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
        """Validate M&M 3e character data"""
        errors = []
        pl = character.get("pl_value", 10)

        # Required fields
        required_fields = ["power_level", "abilities", "powers"]
        for field in required_fields:
            if field not in character:
                errors.append(f"Eksik alan: {field}")

        # PL limits validation
        attack_bonus = 0
        damage_bonus = 0

        if "powers" in character:
            for power_name, power_data in character["powers"].items():
                power_type = self.data.get("powers", {}).get(power_name, {}).get("type", "other")
                if power_type == "attack":
                    attack_bonus += power_data.get("attack_bonus", 0)
                elif power_type == "damage":
                    damage_bonus += power_data.get("damage_bonus", 0)

        if attack_bonus + damage_bonus > pl * 2:
            errors.append(f"PL hard limit aşılmış: {attack_bonus + damage_bonus} > {pl * 2}")

        # Ability score validation
        if "abilities" in character:
            for ability, score in character["abilities"].items():
                if ability != "power_points" and not (-5 <= score <= pl + 2):
                    errors.append(f"Geçersiz {ability}: {score} (PL limit: -5 to {pl+2})")

        # Power points validation
        if character.get("remaining_power_points", 0) < 0:
            errors.append("Negatif power point kalmış")

        return errors

    def calculate_derived_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived statistics for M&M 3e"""
        derived = {}

        abilities = character.get("abilities", {})
        skills = character.get("skills", {})
        defenses = character.get("defenses", {})

        # Initiative = Agility + Awareness
        agility = abilities.get("agility", 0)
        awareness = abilities.get("awareness", 0)
        derived["initiative"] = agility + awareness

        # Attack bonuses
        strength = abilities.get("strength", 0)
        dexterity = abilities.get("dexterity", 0)
        fighting = abilities.get("fighting", 0)

        derived["melee_attack"] = strength + fighting
        derived["ranged_attack"] = dexterity + fighting

        # Defense totals
        derived["dodge_total"] = defenses.get("dodge", 0) + agility
        derived["parry_total"] = defenses.get("parry", 0) + fighting
        derived["fortitude_total"] = defenses.get("fortitude", 0) + abilities.get("stamina", 0)
        derived["toughness_total"] = defenses.get("toughness", 0) + abilities.get("stamina", 0)
        derived["will_total"] = defenses.get("will", 0) + awareness

        return derived