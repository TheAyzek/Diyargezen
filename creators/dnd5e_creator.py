# creators/dnd5e_creator.py
"""
D&D 5e Character Creator
Implements D&D 5e specific rules and calculations
"""

from typing import Dict, Any, List
from .base_creator import BaseCharacterCreator


class DND5ECreator(BaseCharacterCreator):
    """D&D 5e Character Creator implementing all 5e rules"""

    def __init__(self):
        super().__init__("D&D 5e", "dnd_data.json")

    def create_character(self) -> Dict[str, Any]:
        """Create a D&D 5e character with all required components"""
        print("=== D&D 5e Karakter Oluşturucu ===")

        # Race selection
        race_names = sorted(self.data.get("races", {}).keys())
        selected_race = self._prompt_selection(race_names, "Irk seçin:")

        # Class selection
        class_names = sorted(self.data.get("classes", {}).keys())
        selected_class = self._prompt_selection(class_names, "Sınıf seçin:")

        # Background selection
        background_names = sorted(self.data.get("backgrounds", {}).keys())
        selected_background = self._prompt_selection(background_names, "Arka plan seçin:")

        # Ability score generation
        ability_method = self._prompt_selection(
            ["Point Buy (27 points)", "Standard Array", "Manual Input"],
            "Yetenek puanı belirleme yöntemi:"
        )

        if ability_method == "Point Buy (27 points)":
            base_scores = self._prompt_point_buy()
        elif ability_method == "Standard Array":
            base_scores = self._prompt_standard_array()
        else:
            base_scores = self._prompt_manual_abilities()

        # Apply racial bonuses
        race_data = self.data["races"][selected_race]
        final_scores = self._apply_racial_bonuses(base_scores, race_data)

        # Calculate modifiers
        modifiers = {ability: (score - 10) // 2 for ability, score in final_scores.items()}

        # Get class data
        class_data = self.data["classes"][selected_class]
        background_data = self.data["backgrounds"][selected_background]

        # Equipment selection
        equipment = self._select_starting_equipment(class_data)

        # Create character dict
        character = {
            "system": "DND5E",
            "name": input("Karakter adı: ").strip() or "İsimsiz",
            "race": selected_race,
            "class": selected_class,
            "background": selected_background,
            "level": 1,
            "experience": 0,
            "abilities": final_scores,
            "modifiers": modifiers,
            "race_data": race_data,
            "class_data": class_data,
            "background_data": background_data,
            "equipment": equipment,
            "proficiency_bonus": 2,  # Level 1
            "hit_points": self._calculate_hit_points(class_data, modifiers["constitution"]),
            "armor_class": 10 + modifiers["dexterity"],  # Base AC, no armor
            "initiative": modifiers["dexterity"],
            "speed": race_data.get("speed", 30)
        }

        # Calculate derived stats
        character.update(self.calculate_derived_stats(character))

        return character

    def _prompt_point_buy(self) -> Dict[str, int]:
        """Point buy ability score generation (27 points)"""
        cost_map = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

        print("\nPoint Buy sistemi (27 puan):")
        print("Maliyet: 8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9")

        while True:
            scores = {}
            spent = 0

            for ability in abilities:
                while True:
                    try:
                        val = int(input(f"{ability.title()} (8-15): "))
                        if 8 <= val <= 15:
                            spent += cost_map[val]
                            scores[ability] = val
                            break
                        else:
                            print("8-15 arası değer girin.")
                    except ValueError:
                        print("Geçerli bir sayı girin.")

            if spent <= 27:
                print(f"Toplam harcanan puan: {spent}/27")
                return scores
            else:
                print(f"Çok fazla puan harcandı ({spent}/27). Tekrar deneyin.")

    def _prompt_standard_array(self) -> Dict[str, int]:
        """Standard array: 15, 14, 13, 12, 10, 8"""
        standard_array = [15, 14, 13, 12, 10, 8]
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

        print("\nStandard Array: [15, 14, 13, 12, 10, 8]")
        scores = {}

        for ability in abilities:
            remaining = [str(x) for x in standard_array]
            choice = self._prompt_selection(remaining, f"{ability.title()} için puan seçin (kalan: {remaining}):")
            scores[ability] = int(choice)
            standard_array.remove(int(choice))

        return scores

    def _prompt_manual_abilities(self) -> Dict[str, int]:
        """Manual ability score input"""
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        scores = {}

        for ability in abilities:
            while True:
                try:
                    val = int(input(f"{ability.title()} (1-20): "))
                    if 1 <= val <= 20:
                        scores[ability] = val
                        break
                    else:
                        print("1-20 arası değer girin.")
                except ValueError:
                    print("Geçerli bir sayı girin.")

        return scores

    def _apply_racial_bonuses(self, base_scores: Dict[str, int], race_data: Dict[str, Any]) -> Dict[str, int]:
        """Apply racial ability score bonuses"""
        final_scores = base_scores.copy()
        asi = race_data.get("ability_score_increase", {})

        # Handle "all" bonus (like Human +1 to all)
        if "all" in asi:
            for ability in final_scores:
                final_scores[ability] += asi["all"]

        # Handle specific bonuses
        for ability, bonus in asi.items():
            if ability != "all" and ability in final_scores:
                final_scores[ability] += bonus

        return final_scores

    def _select_starting_equipment(self, class_data: Dict[str, Any]) -> List[str]:
        """Select starting equipment from class options"""
        equip_options = class_data.get("starting_equipment_options", [])
        if not equip_options:
            return []

        print("\nBaşlangıç ekipmanı seçin:")
        option_descriptions = []
        for i, option in enumerate(equip_options):
            option_descriptions.append(f"Seçenek {i+1}: {', '.join(option)}")

        choice = self._prompt_selection(option_descriptions, "Ekipman seçenekleri:")
        choice_index = option_descriptions.index(choice)

        return equip_options[choice_index]

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
        """
        D&D 5e karakter validasyonu - IYILESTIRILDI
        Kural uygunlugu, veri butunlugu ve tutarlilik kontrolu
        """
        errors = []
        warnings = []

        # ---- Zorunlu alanlar ----
        required_fields = ["name", "race", "class", "abilities", "level"]
        for field in required_fields:
            if field not in character or not character.get(field):
                errors.append(f"Eksik alan: {field}")

        # ---- Level ----
        level = character.get("level", 0)
        if not isinstance(level, int) or not (1 <= level <= 20):
            errors.append(f"Gecersiz seviye: {level} (1-20 arasi olmali)")

        # ---- Ability scores ----
        abilities = character.get("abilities", {})
        expected_abilities = {"Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"}
        if abilities:
            for ability in expected_abilities:
                score = abilities.get(ability)
                if score is None:
                    # Kucuk harf kontrolu
                    score = abilities.get(ability.lower())
                if score is None:
                    warnings.append(f"Eksik yetenek puani: {ability}")
                elif not isinstance(score, int) or not (1 <= score <= 30):
                    errors.append(f"Gecersiz {ability} puani: {score} (1-30 arasi olmali)")

        # ---- Sinif gecerliligi ----
        char_class = character.get("class", "")
        if char_class and self.data:
            valid_classes = list(self.data.get("classes", {}).keys())
            if char_class not in valid_classes:
                warnings.append(f"Bilinmeyen sinif: {char_class}")

        # ---- Irk gecerliligi ----
        race = character.get("race", "")
        if race and self.data:
            valid_races = list(self.data.get("races", {}).keys())
            if race not in valid_races:
                warnings.append(f"Bilinmeyen irk: {race}")

        # ---- Background gecerliligi ----
        background = character.get("background", "")
        if background and self.data:
            valid_bgs = list(self.data.get("backgrounds", {}).keys())
            if background not in valid_bgs:
                warnings.append(f"Bilinmeyen arka plan: {background}")

        # ---- HP kontrolu ----
        hp = character.get("hit_points", character.get("hp"))
        if hp is not None and isinstance(hp, int):
            if hp <= 0:
                errors.append(f"HP 0 veya altinda olamaz: {hp}")
            # Basit ust sinir kontrolu: level * 12 + 20 (Barbarian d12 + max CON)
            max_possible = level * 12 + 40
            if hp > max_possible:
                warnings.append(f"HP cok yuksek gorunuyor: {hp} (max ~{max_possible})")

        # ---- AC kontrolu ----
        ac = character.get("armor_class")
        if ac is not None and isinstance(ac, int):
            if ac < 1 or ac > 30:
                warnings.append(f"AC olagan disi: {ac} (normal aralik: 10-25)")

        # ---- Proficiency Bonus ----
        prof = character.get("proficiency_bonus")
        if prof is not None and isinstance(prof, int):
            from utils.calculations import calculate_proficiency_bonus
            expected_prof = calculate_proficiency_bonus(level)
            if prof != expected_prof:
                warnings.append(f"Proficiency bonus tutarsiz: {prof} (seviye {level} icin {expected_prof} olmali)")

        # ---- Spell slots kontrolu ----
        spell_slots = character.get("spell_slots", {})
        if spell_slots and isinstance(spell_slots, dict):
            for slot_level, count in spell_slots.items():
                if isinstance(count, int) and count < 0:
                    errors.append(f"Spell slot negatif olamaz: Level {slot_level} = {count}")

        # ---- Attunement limit ----
        attuned_items = character.get("attuned_items", [])
        if len(attuned_items) > 3:
            errors.append(f"Attunement limiti asildi: {len(attuned_items)}/3")

        # ---- Multiclass kontrolu ----
        if character.get("is_multiclass"):
            class_levels = character.get("class_levels", {})
            if class_levels:
                total_from_classes = sum(class_levels.values())
                if total_from_classes != level:
                    warnings.append(
                        f"Multiclass toplam seviye tutarsiz: "
                        f"class_levels toplami={total_from_classes}, level={level}"
                    )
                # Prerequisite kontrolu
                try:
                    from utils.multiclass import check_multiclass_prerequisites
                    for cls in class_levels:
                        can_mc, reasons = check_multiclass_prerequisites(character, cls)
                        if not can_mc:
                            for r in reasons:
                                warnings.append(f"Multiclass prerequisite: {r}")
                except ImportError:
                    pass
            else:
                warnings.append("Multiclass isaretli ancak class_levels bilgisi yok")

        # Uyarilari da ekle (prefix ile)
        result = errors.copy()
        for w in warnings:
            result.append(f"[UYARI] {w}")

        return result

    def calculate_derived_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived statistics for D&D 5e"""
        from utils.calculations import calculate_all_dnd_stats

        # Use the comprehensive calculation function
        return calculate_all_dnd_stats(character, self.data)