#!/usr/bin/env python3
"""
Diyargezer - Ultimate Character Builder
Modern CustomTkinter GUI for TTRPG Character Creation

Features:
- Dark Blue theme
- 4 TTRPG systems: D&D 5e, Pathfinder 1e, Vampire 5e, Mutants & Masterminds
- Step-by-step character creation wizard
- PDF export functionality
- Modern, responsive interface
"""

import customtkinter as ctk
from customtkinter import *
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Import character creators
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from creators.dnd5e_creator import DND5ECreator
    from creators.pathfinder1e_creator import Pathfinder1ECreator
    from creators.vtm5e_creator import VTM5ECreator
    from creators.mm3e_creator import MM3ECreator
    from creators.base_creator import CharacterFactory
except ImportError as e:
    print(f"Error importing creators: {e}")
    print("Please ensure all creator modules are available.")
    sys.exit(1)


class CharacterCreationWizard:
    """Step-by-step character creation wizard"""

    def __init__(self, parent, system_name: str, on_complete_callback):
        self.parent = parent
        self.system_name = system_name
        self.on_complete = on_complete_callback
        self.current_step = 0
        self.character_data = {}
        self.creator = CharacterFactory.create_creator(self.system_name)

        # Create wizard window
        self.wizard_window = ctk.CTkToplevel(parent)
        self.wizard_window.title(f"{system_name} - Karakter Oluşturma Sihirbazı")
        self.wizard_window.geometry("900x700")
        self.wizard_window.resizable(True, True)

        # Make it modal
        self.wizard_window.transient(parent)
        self.wizard_window.grab_set()

        # Initialize steps based on system
        self._init_steps()

        # Create wizard UI
        self._create_wizard_ui()

        # Show first step
        self._show_step(0)

    def _init_steps(self):
        """Initialize steps for the character creation process"""
        if self.system_name == "dnd5e":
            self.steps = [
                {"title": "Adım 1: Temel Bilgiler", "method": self._step_name_input},
                {"title": "Adım 2: Irk Seçimi", "method": self._step_race_selection},
                {"title": "Adım 3: Sınıf Seçimi", "method": self._step_class_selection},
                {"title": "Adım 4: Arka Plan", "method": self._step_background_selection},
                {"title": "Adım 5: Yetenek Puanları", "method": self._step_ability_scores},
                {"title": "Adım 6: Başlangıç Ekipmanı", "method": self._step_starting_equipment},
                {"title": "Adım 7: Onay ve Oluştur", "method": self._step_finalize}
            ]
        elif self.system_name == "pathfinder1e":
            self.steps = [
                {"title": "Adım 1: Temel Bilgiler", "method": self._step_name_input},
                {"title": "Adım 2: Irk Seçimi", "method": self._step_race_selection},
                {"title": "Adım 3: Sınıf Seçimi", "method": self._step_class_selection},
                {"title": "Adım 4: Archetype Seçimi", "method": self._step_archetype_selection},
                {"title": "Adım 5: Yetenek Puanları", "method": self._step_ability_scores},
                {"title": "Adım 6: Başlangıç Ekipmanı", "method": self._step_starting_equipment},
                {"title": "Adım 7: Onay ve Oluştur", "method": self._step_finalize}
            ]
        else:
            # Generic steps for other systems
            self.steps = [
                {"title": "Adım 1: Temel Bilgiler", "method": self._step_name_input},
                {"title": "Adım 2: Sistem Seçenekleri", "method": self._step_system_options},
                {"title": "Adım 3: Onay ve Oluştur", "method": self._step_finalize}
            ]

    def _create_wizard_ui(self):
        """Create the wizard user interface"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.wizard_window)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(pady=(20, 10))

        # Progress indicator
        self.progress_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Adım {self.current_step + 1} / {len(self.steps)}",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=(0, 20))

        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Navigation buttons
        self._create_navigation_buttons()

    def _create_navigation_buttons(self):
        """Create navigation buttons"""
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 20))

        # Previous button
        self.prev_button = ctk.CTkButton(
            button_frame,
            text="⬅️ Geri",
            command=self._previous_step,
            state="disabled",
            width=100
        )
        self.prev_button.pack(side="left", padx=(0, 10))

        # Next button
        self.next_button = ctk.CTkButton(
            button_frame,
            text="İleri ➡️",
            command=self._next_step,
            width=100
        )
        self.next_button.pack(side="left", padx=(0, 10))

        # Cancel button
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="İptal",
            command=self._cancel_wizard,
            fg_color="transparent",
            border_width=2,
            width=100
        )
        self.cancel_button.pack(side="right")

    def _show_step(self, step_index: int):
        """Show the specified step"""
        self.current_step = step_index
        step = self.steps[step_index]

        # Update title and progress
        self.title_label.configure(text=step["title"])
        self.progress_label.configure(text=f"Adım {step_index + 1} / {len(self.steps)}")

        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Show step content
        step["method"]()

        # Update navigation buttons
        self.prev_button.configure(state="normal" if step_index > 0 else "disabled")
        if step_index == len(self.steps) - 1:
            self.next_button.configure(text="Oluştur ✅", command=self._create_character)
        else:
            self.next_button.configure(text="İleri ➡️", command=self._next_step)

    def _next_step(self):
        """Go to next step"""
        self._collect_current_data()
        if self.current_step < len(self.steps) - 1:
            self._show_step(self.current_step + 1)

    def _previous_step(self):
        """Go to previous step"""
        self._collect_current_data()
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _cancel_wizard(self):
        """Cancel the wizard"""
        if messagebox.askyesno("İptal", "Karakter oluşturma sihirbazını iptal etmek istiyor musunuz?"):
            self.wizard_window.destroy()

    def _step_name_input(self):
        """Step 1: Character name input"""
        label = ctk.CTkLabel(
            self.content_frame,
            text="Karakterinizin adını girin:",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=(20, 10))

        self.name_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Örnek: Aragorn, Legolas, Gimli...",
            width=300
        )
        self.name_entry.pack(pady=(0, 20))

        # Pre-fill if we have data
        if "name" in self.character_data:
            self.name_entry.insert(0, self.character_data["name"])

    def _step_race_selection(self):
        """Step 2: Race selection"""
        label = ctk.CTkLabel(
            self.content_frame,
            text="Karakterinizin ırkını seçin:",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=(20, 10))

        races = sorted(self.creator.data.get("races", {}).keys())
        if not races:
            races = ["Human", "Elf", "Dwarf", "Halfling"]

        prev_race = self.character_data.get('race', races[0])
        if prev_race not in races:
            prev_race = races[0]
        self.race_var = ctk.StringVar(value=prev_race)
        race_menu = ctk.CTkOptionMenu(
            self.content_frame,
            variable=self.race_var,
            values=races,
            width=300
        )
        race_menu.pack(pady=(0, 10))

        info_frame = ctk.CTkScrollableFrame(self.content_frame, height=250)
        info_frame.pack(fill="x", padx=20, pady=(0, 10))

        desc_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=12),
            wraplength=450,
            justify="left"
        )
        desc_label.pack(pady=(5, 5), anchor="w")

        bonus_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3498db",
            wraplength=450,
            justify="left"
        )
        bonus_label.pack(pady=(0, 5), anchor="w")

        traits_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#27ae60",
            wraplength=450,
            justify="left"
        )
        traits_label.pack(pady=(0, 5), anchor="w")

        extra_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#95a5a6",
            wraplength=450,
            justify="left"
        )
        extra_label.pack(pady=(0, 5), anchor="w")

        def update_description(*args):
            race = self.race_var.get()
            race_data = self.creator.data.get("races", {}).get(race, {})

            desc = race_data.get("description", f"{race} ırkı.")
            desc_label.configure(text=desc)

            asi = race_data.get("ability_score_increase", {})
            if asi:
                ability_names = {
                    "strength": "STR", "dexterity": "DEX", "constitution": "CON",
                    "intelligence": "INT", "wisdom": "WIS", "charisma": "CHA", "all": "Tümü"
                }
                parts = [f"{ability_names.get(k, k)} +{v}" for k, v in asi.items()]
                bonus_label.configure(text=f"📊 Yetenek Bonusları: {', '.join(parts)}")
            else:
                bonus_label.configure(text="📊 Yetenek Bonusu: Yok")

            traits = race_data.get("traits", [])
            if traits:
                traits_label.configure(text=f"⚔️ Özellikler: {', '.join(traits)}")
            else:
                traits_label.configure(text="")

            extras = []
            speed = race_data.get("speed")
            if speed:
                extras.append(f"Hız: {speed} ft")
            size = race_data.get("size")
            if size:
                extras.append(f"Boyut: {size}")
            langs = race_data.get("languages", [])
            if langs:
                extras.append(f"Diller: {', '.join(langs)}")
            if extras:
                extra_label.configure(text=f"ℹ️ {' | '.join(extras)}")
            else:
                extra_label.configure(text="")

        self.race_var.trace("w", update_description)
        update_description()

    def _step_class_selection(self):
        """Step 3: Class selection"""
        label = ctk.CTkLabel(
            self.content_frame,
            text="Karakterinizin sınıfını seçin:",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=(20, 10))

        classes = sorted(self.creator.data.get("classes", {}).keys())
        if not classes:
            classes = ["Fighter", "Wizard", "Rogue", "Cleric"]

        prev_class = self.character_data.get('class', classes[0])
        if prev_class not in classes:
            prev_class = classes[0]
        self.class_var = ctk.StringVar(value=prev_class)
        class_menu = ctk.CTkOptionMenu(
            self.content_frame,
            variable=self.class_var,
            values=classes,
            width=300
        )
        class_menu.pack(pady=(0, 10))

        info_frame = ctk.CTkScrollableFrame(self.content_frame, height=250)
        info_frame.pack(fill="x", padx=20, pady=(0, 10))

        desc_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=12),
            wraplength=450,
            justify="left"
        )
        desc_label.pack(pady=(5, 5), anchor="w")

        stats_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e67e22",
            wraplength=450,
            justify="left"
        )
        stats_label.pack(pady=(0, 5), anchor="w")

        features_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#27ae60",
            wraplength=450,
            justify="left"
        )
        features_label.pack(pady=(0, 5), anchor="w")

        def update_description(*args):
            class_name = self.class_var.get()
            class_data = self.creator.data.get("classes", {}).get(class_name, {})

            desc = class_data.get("description", f"{class_name} sınıfı.")
            desc_label.configure(text=desc)

            parts = []
            hd = class_data.get("hit_die")
            if hd:
                parts.append(f"Hit Die: d{hd}")
            saves = class_data.get("saving_throws", [])
            if saves:
                parts.append(f"Saving Throws: {', '.join(saves)}")
            primary = class_data.get("primary_ability", "")
            if primary:
                parts.append(f"Primary: {primary}")
            if parts:
                stats_label.configure(text=f"🎯 {' | '.join(parts)}")
            else:
                stats_label.configure(text="")

            profs = class_data.get("proficiencies", {})
            feat_parts = []
            armor = profs.get("armor", [])
            if armor:
                feat_parts.append(f"Zırh: {', '.join(armor)}")
            weapons = profs.get("weapons", [])
            if weapons:
                feat_parts.append(f"Silah: {', '.join(weapons)}")
            if feat_parts:
                features_label.configure(text=f"🛡️ {' | '.join(feat_parts)}")
            else:
                features_label.configure(text="")

        self.class_var.trace("w", update_description)
        update_description()

    def _step_archetype_selection(self):
        """Step 4: Archetype selection (Pathfinder only)"""
        if self.system_name != "pathfinder1e":
            return

        label = ctk.CTkLabel(
            self.content_frame,
            text="Karakterinizin archetype'unu seçin:",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=(20, 10))

        # Get archetypes for selected class
        class_name = self.character_data.get("class", "Fighter")
        archetypes = self.creator.data.get("archetypes", {}).get(class_name, {})

        if not archetypes:
            # Fallback archetypes
            arch_names = [f"{class_name} Archetype {i+1}" for i in range(3)]
        else:
            arch_names = sorted(archetypes.keys())

        self.archetype_var = ctk.StringVar(value=arch_names[0] if arch_names else "Basic")
        arch_menu = ctk.CTkOptionMenu(
            self.content_frame,
            variable=self.archetype_var,
            values=arch_names if arch_names else ["Basic"],
            width=300
        )
        arch_menu.pack(pady=(0, 20))

        # Archetype description
        desc_label = ctk.CTkLabel(
            self.content_frame,
            text="Seçilen archetype hakkında bilgi burada görünecek.",
            font=ctk.CTkFont(size=12),
            wraplength=400
        )
        desc_label.pack(pady=(0, 20))

        # Update description when archetype changes
        def update_description(*args):
            arch_name = self.archetype_var.get()
            arch_data = archetypes.get(arch_name, {})
            description = arch_data.get("description", f"{arch_name} archetype hakkında detaylı bilgi bulunamadı.")
            desc_label.configure(text=description)

        self.archetype_var.trace("w", update_description)
        update_description()  # Initial update

    def _step_background_selection(self):
        """Step 4: Background selection (D&D only)"""
        if self.system_name != "dnd5e":
            return

        label = ctk.CTkLabel(
            self.content_frame,
            text="Karakterinizin arka planını seçin:",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=(20, 10))

        backgrounds = sorted(self.creator.data.get("backgrounds", {}).keys())
        if not backgrounds:
            backgrounds = ["Commoner", "Soldier", "Scholar", "Criminal"]

        prev_bg = self.character_data.get('background', backgrounds[0])
        if prev_bg not in backgrounds:
            prev_bg = backgrounds[0]
        self.background_var = ctk.StringVar(value=prev_bg)
        bg_menu = ctk.CTkOptionMenu(
            self.content_frame,
            variable=self.background_var,
            values=backgrounds,
            width=300
        )
        bg_menu.pack(pady=(0, 10))

        info_frame = ctk.CTkScrollableFrame(self.content_frame, height=200)
        info_frame.pack(fill="x", padx=20, pady=(0, 10))

        feature_label = ctk.CTkLabel(
            info_frame, text="", font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9b59b6", wraplength=450, justify="left"
        )
        feature_label.pack(pady=(5, 3), anchor="w")

        feat_desc_label = ctk.CTkLabel(
            info_frame, text="", font=ctk.CTkFont(size=11),
            wraplength=450, justify="left"
        )
        feat_desc_label.pack(pady=(0, 5), anchor="w")

        skills_label = ctk.CTkLabel(
            info_frame, text="", font=ctk.CTkFont(size=11),
            text_color="#3498db", wraplength=450, justify="left"
        )
        skills_label.pack(pady=(0, 3), anchor="w")

        equip_label = ctk.CTkLabel(
            info_frame, text="", font=ctk.CTkFont(size=11),
            text_color="#27ae60", wraplength=450, justify="left"
        )
        equip_label.pack(pady=(0, 3), anchor="w")

        def update_bg_info(*args):
            bg_name = self.background_var.get()
            bg_data = self.creator.data.get("backgrounds", {}).get(bg_name, {})

            feature = bg_data.get("feature", "")
            if feature:
                feature_label.configure(text=f"⭐ Özellik: {feature}")
            else:
                feature_label.configure(text="")

            feat_desc = bg_data.get("feature_description", "")
            feat_desc_label.configure(text=feat_desc if feat_desc else "")

            skills = bg_data.get("skill_proficiencies", [])
            tools = bg_data.get("tools", [])
            parts = []
            if skills:
                parts.append(f"Beceriler: {', '.join(skills)}")
            if tools:
                parts.append(f"Araçlar: {', '.join(tools)}")
            skills_label.configure(text=f"📚 {' | '.join(parts)}" if parts else "")

            equip = bg_data.get("equipment", [])
            if equip:
                equip_label.configure(text=f"🎒 Ekipman: {', '.join(equip)}")
            else:
                equip_label.configure(text="")

        self.background_var.trace("w", update_bg_info)
        update_bg_info()

    def _step_ability_scores(self):
        """Step 5: Ability scores"""
        if self.system_name == "dnd5e":
            label = ctk.CTkLabel(
                self.content_frame,
                text="Yetenek puanlarınızı belirleyin (Point Buy - 27 puan):",
                font=ctk.CTkFont(size=14)
            )
            label.pack(pady=(20, 10))

            # Point buy interface
            self.ability_entries = {}
            abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

            for ability in abilities:
                frame = ctk.CTkFrame(self.content_frame)
                frame.pack(fill="x", padx=20, pady=5)

                abbrev = ability[:3].upper()
                lbl = ctk.CTkLabel(frame, text=f"{abbrev}:", width=80)
                lbl.pack(side="left", padx=(10, 5))

                entry = ctk.CTkEntry(frame, placeholder_text="8-15", width=80)
                entry.pack(side="left", padx=(0, 10))
                self.ability_entries[abbrev] = entry

                modifier = ctk.CTkLabel(frame, text="(+0)", width=50)
                modifier.pack(side="left")

                # Update modifier when score changes
                def update_modifier(e=entry, m=modifier, abbr=abbrev):
                    try:
                        score = int(e.get())
                        mod = (score - 10) // 2
                        m.configure(text=f"({mod:+d})")
                    except:
                        m.configure(text="(+0)")

                entry.bind("<KeyRelease>", update_modifier)

        elif self.system_name == "pathfinder1e":
            label = ctk.CTkLabel(
                self.content_frame,
                text="Yetenek puanlarınızı girin (1-20 arası):",
                font=ctk.CTkFont(size=14)
            )
            label.pack(pady=(20, 10))

            # Ability score entries
            self.ability_entries = {}
            abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

            for i, ability in enumerate(abilities):
                frame = ctk.CTkFrame(self.content_frame)
                frame.pack(fill="x", padx=20, pady=5)

                lbl = ctk.CTkLabel(frame, text=f"{ability}:", width=60)
                lbl.pack(side="left", padx=(10, 5))

                entry = ctk.CTkEntry(frame, placeholder_text="10", width=80)
                entry.pack(side="left", padx=(0, 10))
                self.ability_entries[ability] = entry

                modifier = ctk.CTkLabel(frame, text="(+0)", width=50)
                modifier.pack(side="left")

                # Update modifier when score changes
                def update_modifier(e=entry, m=modifier):
                    try:
                        score = int(e.get())
                        mod = (score - 10) // 2
                        m.configure(text=f"({mod:+d})")
                    except:
                        m.configure(text="(+0)")

                entry.bind("<KeyRelease>", update_modifier)

    def _step_starting_equipment(self):
        """Step 6: Starting equipment selection - İYİLEŞTİRİLDİ"""
        if self.system_name not in ["dnd5e", "pathfinder1e"]:
            return

        # Background equipment'ı otomatik ekle
        background_name = self.character_data.get('background', '')
        background_equipment = []
        if background_name and self.system_name == "dnd5e":
            background_data = self.creator.data.get("backgrounds", {}).get(background_name, {})
            bg_equip = background_data.get("equipment", [])
            if isinstance(bg_equip, list):
                background_equipment = bg_equip
            elif isinstance(bg_equip, str):
                background_equipment = [bg_equip]

        # Background equipment bilgisi
        if background_equipment:
            bg_label = ctk.CTkLabel(
                self.content_frame,
                text=f"📦 Arka Plan Ekipmanı ({background_name}): {', '.join(background_equipment)}",
                font=ctk.CTkFont(size=12),
                text_color="#27ae60"
            )
            bg_label.pack(pady=(20, 5), padx=20, anchor="w")

        label = ctk.CTkLabel(
            self.content_frame,
            text="Sınıf ekipman seçeneklerinizden birini seçin:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.pack(pady=(10, 10))

        # Get selected class
        selected_class = self.character_data.get('class', 'Fighter')

        # Get equipment options from class data
        class_data = self.creator.data.get("classes", {}).get(selected_class, {})
        equipment_options = class_data.get("starting_equipment_options", [])

        if not equipment_options:
            # Fallback equipment
            equipment_options = [
                ["Leather Armor", "Longsword", "Shield", "Explorer's Pack"],
                ["Chain Mail", "Greatsword", "Dungeoneer's Pack"]
            ]

        # Create equipment selection widgets
        self.equipment_vars = []
        self.equipment_frames = []
        self.equipment_any_combos = {}  # "Any X" seçimleri için combo box'lar

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        for i, option_set in enumerate(equipment_options):
            # Option set frame
            option_frame = ctk.CTkFrame(scroll_frame)
            option_frame.pack(fill="x", padx=5, pady=5)
            self.equipment_frames.append(option_frame)

            # Radio button for selection
            var = ctk.StringVar(value="0" if i == 0 else "")
            radio = ctk.CTkRadioButton(
                option_frame,
                text=f"Seçenek {i+1}",
                variable=var,
                value=str(i),
                command=lambda idx=i: self._select_equipment_option(idx)
            )
            radio.pack(anchor="w", padx=10, pady=(10, 5))
            self.equipment_vars.append(var)

            # Equipment items listesi
            items_frame = ctk.CTkFrame(option_frame, fg_color="transparent")
            items_frame.pack(fill="x", padx=30, pady=(0, 10))

            for item in option_set:
                item_lower = item.lower()
                
                # "Any X" seçimleri için combo box
                if item_lower.startswith("any "):
                    item_type = item_lower.replace("any ", "").strip()
                    combo_frame = ctk.CTkFrame(items_frame, fg_color="transparent")
                    combo_frame.pack(fill="x", pady=2)

                    combo_label = ctk.CTkLabel(
                        combo_frame,
                        text=f"{item}:",
                        font=ctk.CTkFont(size=11),
                        width=200
                    )
                    combo_label.pack(side="left", padx=(0, 10))

                    combo = ctk.CTkComboBox(
                        combo_frame,
                        values=self._get_equipment_options_for_type(item_type),
                        state="disabled"  # Radio seçilene kadar disable
                    )
                    combo.pack(side="left", fill="x", expand=True)
                    
                    # Combo key: option_index_item_type
                    combo_key = f"{i}_{item_type.replace(' ', '_')}"
                    self.equipment_any_combos[combo_key] = combo
                    
                    # Radio seçildiğinde combo'yu enable et
                    def enable_combo(combo_ref=combo):
                        combo_ref.configure(state="normal")
                    radio.configure(command=lambda idx=i, enable=enable_combo: (self._select_equipment_option(idx), enable()))
                else:
                    # Normal item
                    item_label = ctk.CTkLabel(
                        items_frame,
                        text=f"• {item}",
                        font=ctk.CTkFont(size=11)
                    )
                    item_label.pack(anchor="w", padx=5, pady=2)

        # Default selection
        if self.equipment_vars:
            self.equipment_vars[0].set("0")
            self._select_equipment_option(0)

    def _get_equipment_options_for_type(self, item_type: str) -> list:
        """'Any X' seçimleri için uygun ekipman listesini döndür"""
        equipment_data = self.creator.data.get("equipment", {})
        weapons = equipment_data.get("weapons", {})
        armor = equipment_data.get("armor", {})
        tools = equipment_data.get("tools", {})

        item_type_lower = item_type.lower()
        
        if "martial weapon" in item_type_lower or "martial melee weapon" in item_type_lower:
            return list(weapons.keys())[:20]  # İlk 20 weapon
        elif "simple weapon" in item_type_lower:
            return list(weapons.keys())[:15]  # İlk 15 simple weapon
        elif "musical instrument" in item_type_lower:
            musical_instruments = ["Lute", "Flute", "Drum", "Horn", "Lyre", "Pan flute", "Shawm", "Viol"]
            return musical_instruments
        elif "light armor" in item_type_lower:
            return list(armor.keys())[:10]
        elif "medium armor" in item_type_lower:
            return list(armor.keys())[:10]
        elif "heavy armor" in item_type_lower:
            return list(armor.keys())[:10]
        else:
            return [item_type]  # Varsayılan

    def _select_equipment_option(self, option_index: int):
        """Handle equipment option selection - İYİLEŞTİRİLDİ"""
        # Diğer radio button'ları temizle
        for i, var in enumerate(self.equipment_vars):
            if i != option_index:
                var.set("")
                # Combo'ları disable et
                for combo_key, combo in self.equipment_any_combos.items():
                    if combo_key.startswith(f"{i}_"):
                        combo.configure(state="disabled")

        # Seçili option'ın combo'larını enable et
        for combo_key, combo in self.equipment_any_combos.items():
            if combo_key.startswith(f"{option_index}_"):
                combo.configure(state="normal")

        # Store selected equipment
        selected_class = self.character_data.get('class', 'Fighter')
        class_data = self.creator.data.get("classes", {}).get(selected_class, {})
        equipment_options = class_data.get("starting_equipment_options", [])

        if equipment_options and option_index < len(equipment_options):
            selected_option = equipment_options[option_index].copy()
            
            # "Any X" seçimlerini combo box'tan alınan değerlerle değiştir
            final_equipment = []
            for item in selected_option:
                item_lower = item.lower()
                if item_lower.startswith("any "):
                    item_type = item_lower.replace("any ", "").strip()
                    combo_key = f"{option_index}_{item_type.replace(' ', '_')}"
                    combo = self.equipment_any_combos.get(combo_key)
                    if combo and combo.cget("state") == "normal":
                        selected_value = combo.get()
                        if selected_value:
                            final_equipment.append(selected_value)
                        else:
                            final_equipment.append(item)  # Combo boşsa orijinal değeri kullan
                    else:
                        final_equipment.append(item)
                else:
                    final_equipment.append(item)
            
            self.character_data['starting_equipment'] = final_equipment
        else:
            # Fallback
            fallback_options = [
                ["Leather Armor", "Longsword", "Shield", "Explorer's Pack"],
                ["Chain Mail", "Greatsword", "Dungeoneer's Pack"]
            ]
            self.character_data['starting_equipment'] = fallback_options[option_index] if option_index < len(fallback_options) else fallback_options[0]

    def _step_system_options(self):
        """Step 2: Generic system options"""
        label = ctk.CTkLabel(
            self.content_frame,
            text=f"{self.system_name} sistemi için özel seçenekler yakında eklenecek.",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=50)

    def _step_finalize(self):
        """Step 6: Final confirmation"""
        # Collect all data
        summary_frame = ctk.CTkFrame(self.content_frame)
        summary_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            summary_frame,
            text="🎲 Karakter Özeti",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(20, 10))

        # Character summary
        summary_text = f"""
Sistem: {self.system_name.upper()}
Ad: {self.character_data.get('name', 'Belirlenmemiş')}

Irk: {self.character_data.get('race', 'Belirlenmemiş')}
Sınıf: {self.character_data.get('class', 'Belirlenmemiş')}
"""

        if self.system_name == "dnd5e":
            summary_text += f"Arka Plan: {self.character_data.get('background', 'Belirlenmemiş')}\n"
        elif self.system_name == "pathfinder1e":
            summary_text += f"Archetype: {self.character_data.get('archetype', 'Belirlenmemiş')}\n"

        summary_text += f"\nYetenek Puanları: {self.character_data.get('abilities', 'Belirlenmemiş')}"

        # Add starting equipment if selected
        starting_equipment = self.character_data.get('starting_equipment', [])
        if starting_equipment:
            summary_text += f"\n\nBaşlangıç Ekipmanı:\n" + "\n".join(f"• {item}" for item in starting_equipment)

        summary_label = ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        summary_label.pack(pady=(0, 20), anchor="w", padx=20)

        # Confirmation message
        confirm_label = ctk.CTkLabel(
            summary_frame,
            text="Karakteri oluşturmak için 'Oluştur' butonuna tıklayın.",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        confirm_label.pack(pady=(20, 10))

    def _collect_current_data(self):
        """Collect data from current step - only from live widgets"""
        try:
            if hasattr(self, 'name_entry') and self.name_entry.winfo_exists():
                self.character_data['name'] = self.name_entry.get().strip()
        except:
            pass

        try:
            if hasattr(self, 'race_var'):
                val = self.race_var.get()
                if val:
                    self.character_data['race'] = val
        except:
            pass

        try:
            if hasattr(self, 'class_var'):
                val = self.class_var.get()
                if val:
                    self.character_data['class'] = val
        except:
            pass

        try:
            if hasattr(self, 'background_var'):
                val = self.background_var.get()
                if val:
                    self.character_data['background'] = val
        except:
            pass

        try:
            if hasattr(self, 'archetype_var'):
                val = self.archetype_var.get()
                if val:
                    self.character_data['archetype'] = val
        except:
            pass

        try:
            if hasattr(self, 'ability_entries'):
                has_live_widget = any(
                    e.winfo_exists() for e in self.ability_entries.values()
                )
                if has_live_widget:
                    abilities = {}
                    for ability, entry in self.ability_entries.items():
                        try:
                            if entry.winfo_exists():
                                score = int(entry.get().strip())
                                abilities[ability] = score
                            else:
                                abilities[ability] = self.character_data.get('abilities', {}).get(ability, 10)
                        except:
                            abilities[ability] = self.character_data.get('abilities', {}).get(ability, 10)
                    self.character_data['abilities'] = abilities
        except:
            pass

        try:
            if hasattr(self, 'equipment_vars') and self.equipment_vars:
                has_live = any(True for v in self.equipment_vars if v.get())
                if has_live:
                    for i, var in enumerate(self.equipment_vars):
                        if var.get() == str(i):
                            self._select_equipment_option(i)
                            break
        except:
            pass

    def _create_character(self):
        """Create the character"""
        self._collect_current_data()

        # Validate required data
        if not self.character_data.get('name'):
            messagebox.showwarning("Uyarı", "Karakter adı gerekli!")
            return

        try:
            # Create character using the creator
            character = {
                "name": self.character_data['name'],
                "system": self.system_name,
                "race": self.character_data.get('race', 'Human'),
                "class": self.character_data.get('class', 'Fighter'),
                "level": 1,
                "abilities": self.character_data.get('abilities', {}),
            }

            if self.system_name == "dnd5e":
                character["background"] = self.character_data.get('background', 'Commoner')
                # Initialize spellbook for Wizard
                if character.get('class') == 'Wizard':
                    character["spellbook"] = []
                    character["prepared_spells"] = []
            elif self.system_name == "pathfinder1e":
                character["archetype"] = self.character_data.get('archetype', 'Basic')

            # Add starting equipment - İYİLEŞTİRİLDİ (Background equipment otomatik eklenir)
            starting_equipment = self.character_data.get('starting_equipment', []).copy()
            
            # Background equipment'ı ekle (eğer eklenmemişse)
            if self.system_name == "dnd5e":
                background_name = character.get('background', '')
                if background_name:
                    background_data = self.creator.data.get("backgrounds", {}).get(background_name, {})
                    bg_equip = background_data.get("equipment", [])
                    if isinstance(bg_equip, list):
                        for bg_item in bg_equip:
                            if bg_item not in starting_equipment:
                                starting_equipment.append(bg_item)
            
            character["starting_equipment"] = starting_equipment

            # Calculate derived stats
            derived_stats = self.creator.calculate_derived_stats(character)
            character.update(derived_stats)

            # Save character
            filename = f"{character['name'].lower().replace(' ', '_')}_{self.system_name.replace(' ', '').lower()}"
            success = self.creator.save_character(character, filename)

            if success:
                messagebox.showinfo("Başarılı", f"{character['name']} karakteri başarıyla oluşturuldu!")
                self.on_complete(character)
                self.wizard_window.destroy()
            else:
                messagebox.showerror("Hata", "Karakter kaydedilemedi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Karakter oluşturma hatası: {e}")


class DiyargezerGUI:
    """Main GUI application for Diyargezer Character Builder"""

    def __init__(self):
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("Diyargezer - Ultimate Character Builder")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # Initialize creators
        self._init_creators()

        # Create GUI components
        self._create_main_layout()

        # Load data for dropdowns
        self._load_system_data()

    def _init_creators(self):
        """Initialize character creators"""
        try:
            CharacterFactory.register_creator("dnd5e", DND5ECreator)
            CharacterFactory.register_creator("pathfinder1e", Pathfinder1ECreator)
            CharacterFactory.register_creator("vtm5e", VTM5ECreator)
            CharacterFactory.register_creator("mm3e", MM3ECreator)
            self.creators = {
                "D&D 5e": "dnd5e",
                "Pathfinder 1e": "pathfinder1e",
                "Vampire 5e": "vtm5e",
                "Mutants & Masterminds": "mm3e"
            }
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize creators: {e}")
            sys.exit(1)

    def _create_main_layout(self):
        """Create the main GUI layout"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="🎲 Diyargezer - Ultimate Character Builder",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))

        # Tabview for different TTRPG systems
        self.tabview = ctk.CTkTabview(self.main_frame, width=1100, height=600)
        self.tabview.pack(pady=(0, 20), padx=20)

        # Create tabs
        self.tabs = {}
        for system_name in self.creators.keys():
            tab = self.tabview.add(system_name)
            self.tabs[system_name] = tab
            self._create_tab_content(tab, system_name)

        # Bottom section with buttons and log
        self._create_bottom_section()

    def _create_tab_content(self, tab_frame, system_name):
        """Create content for a specific tab"""
        # Character name input
        name_frame = ctk.CTkFrame(tab_frame)
        name_frame.pack(fill="x", padx=20, pady=(20, 10))

        name_label = ctk.CTkLabel(name_frame, text="Karakter Adı:", font=ctk.CTkFont(weight="bold"))
        name_label.pack(side="left", padx=(20, 10))

        name_entry = ctk.CTkEntry(name_frame, placeholder_text="Karakter adını girin...")
        name_entry.pack(side="left", fill="x", expand=True, padx=(0, 20))

        # Store reference
        setattr(self, f"{system_name.lower().replace(' ', '_')}_name", name_entry)

        # Character summary frame (initially hidden)
        summary_frame = ctk.CTkFrame(tab_frame)
        summary_frame.pack(fill="x", padx=20, pady=(0, 10))
        summary_frame.pack_forget()  # Hide initially

        summary_label = ctk.CTkLabel(summary_frame, text="Karakter Özeti:", font=ctk.CTkFont(weight="bold"))
        summary_label.pack(anchor="w", padx=20, pady=(10, 5))

        summary_text = ctk.CTkTextbox(summary_frame, wrap="word", height=200)
        summary_text.pack(fill="x", padx=20, pady=(0, 10))

        # Store references
        setattr(self, f"{system_name.lower().replace(' ', '_')}_summary_frame", summary_frame)
        setattr(self, f"{system_name.lower().replace(' ', '_')}_summary_text", summary_text)

        # System-specific content
        if system_name == "D&D 5e":
            self._create_dnd_tab(tab_frame)
        elif system_name == "Pathfinder 1e":
            self._create_pathfinder_tab(tab_frame)
        elif system_name == "Vampire 5e":
            self._create_vtm_tab(tab_frame)
        elif system_name == "Mutants & Masterminds":
            self._create_mm_tab(tab_frame)

    def _open_spellbook_manager(self):
        """Wizard spellbook / prepared spells yönetim penceresi"""
        from creators import CharacterFactory
        from utils.calculations import calculate_spells_prepared

        current_tab = self.tabview.get()
        if current_tab != "D&D 5e":
            messagebox.showinfo("Bilgi", "Spellbook yöneticisi yalnızca D&D 5e sekmesinde kullanılabilir.")
            return

        # Karakter adını al
        name_entry = getattr(self, f"{current_tab.lower().replace(' ', '_')}_name")
        character_name = name_entry.get().strip()
        if not character_name:
            messagebox.showwarning("Uyarı", "Önce bir D&D 5e karakteri oluşturun veya adını girin.")
            return

        # Karakteri dosyadan yükle
        try:
            system_key = self.creators.get(current_tab)
            creator = CharacterFactory.create_creator(system_key)
            filename = f"{character_name.lower().replace(' ', '_')}_{system_key}"
            character = creator.load_character(filename)
        except Exception as e:
            messagebox.showerror("Hata", f"Karakter yüklenemedi: {e}")
            return

        # Sadece Wizard için spellbook yönetimi
        if character.get("class") != "Wizard":
            messagebox.showinfo("Bilgi", "Spellbook yönetimi yalnızca Wizard karakterler için geçerlidir.")
            return

        # Hazırlanabilecek büyü sayısını hesapla
        prepared_limit = calculate_spells_prepared(character) or 0
        prepared_current = character.get("prepared_spells", [])
        if isinstance(prepared_current, dict):
            # Eski format dict ise tüm seviyeleri tek listeye indir
            flat = []
            for spells in prepared_current.values():
                if isinstance(spells, list):
                    flat.extend(spells)
            prepared_current = flat

        # Spellbook formatını normalize et (seviye->liste veya düz liste)
        raw_spellbook = character.get("spellbook", {})
        if isinstance(raw_spellbook, list):
            spellbook_by_level = {"any": list(raw_spellbook)}
        elif isinstance(raw_spellbook, dict):
            spellbook_by_level = raw_spellbook
        else:
            spellbook_by_level = {}

        # Dialog oluştur
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Wizard Spellbook - {character_name}")
        dialog.geometry("480x580")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        info_text = f"Wizard spellbook'unuzdaki büyülerden hazırlanacakları seçin.\n"
        info_text += f"Hazırlanabilecek toplam büyü sayısı: {prepared_limit}"
        info_label = ctk.CTkLabel(main_frame, text=info_text, wraplength=440, justify="left")
        info_label.pack(pady=(0, 10))

        # Scrollable area
        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True, pady=(10, 10))

        checkbox_vars = {}

        def is_prepared(spell_name: str) -> bool:
            return spell_name in prepared_current

        # Seviye anahtarlarını sırala
        def level_sort_key(key: str):
            try:
                return int(key)
            except (TypeError, ValueError):
                return 99

        for level_key in sorted(spellbook_by_level.keys(), key=level_sort_key):
            spells = spellbook_by_level.get(level_key, [])
            try:
                level_int = int(level_key)
            except (TypeError, ValueError):
                level_int = None

            if level_int == 0:
                header_text = "Cantrips"
            elif level_int is not None:
                header_text = f"{level_int}. Seviye Büyüler"
            else:
                header_text = "Diğer Büyüler"

            header_label = ctk.CTkLabel(
                scroll_frame,
                text=f"=== {header_text} ===",
                font=ctk.CTkFont(weight="bold")
            )
            header_label.pack(anchor="w", pady=(8, 4), padx=10)

            for spell_name in spells:
                var = ctk.BooleanVar(value=is_prepared(spell_name))
                cb = ctk.CTkCheckBox(
                    scroll_frame,
                    text=spell_name,
                    variable=var
                )
                cb.pack(anchor="w", padx=20, pady=2)
                checkbox_vars[spell_name] = var

        # Alt butonlar
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        def on_cancel():
            dialog.destroy()

        def on_save():
            selected = [name for name, var in checkbox_vars.items() if var.get()]
            if prepared_limit and len(selected) > prepared_limit:
                messagebox.showwarning(
                    "Sınır Aşıldı",
                    f"En fazla {prepared_limit} büyü hazırlayabilirsiniz (şu an {len(selected)} seçili)."
                )
                return

            character["prepared_spells"] = selected

            try:
                creator.save_character(character, filename)
                messagebox.showinfo("Başarılı", "Hazırlanan büyüler güncellendi.")
                # Özet ekranını güncelle (sadece D&D 5e sekmesi için)
                self._show_character_summary(character, "D&D 5e")
            except Exception as e:
                messagebox.showerror("Hata", f"Karakter kaydedilemedi: {e}")

            dialog.destroy()

        cancel_btn = ctk.CTkButton(button_frame, text="İptal", command=on_cancel)
        cancel_btn.pack(side="right", padx=(0, 10))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Kaydet",
            command=on_save,
            font=ctk.CTkFont(weight="bold")
        )
        save_btn.pack(side="right", padx=(0, 10))

    def _open_equipment_manager(self):
        """Ekipman yönetim penceresi - Magic Items, Attunement, Encumbrance"""
        import json
        from tkinter import filedialog, messagebox
        from utils.calculations import (
            check_attunement_limit, can_attune_item,
            calculate_encumbrance_details, extract_magic_item_ac_bonus,
            extract_magic_item_bonus
        )

        # Karakter dosyası seç
        character_file = filedialog.askopenfilename(
            title="Karakter Dosyası Seçin",
            filetypes=[("JSON files", "*.json")],
            initialdir="characters"
        )
        if not character_file:
            return

        try:
            with open(character_file, 'r', encoding='utf-8') as f:
                character = json.load(f)
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okunamadı: {e}")
            return

        if not isinstance(character, dict) or 'name' not in character:
            messagebox.showerror("Hata", "Geçersiz karakter dosyası!")
            return

        # Dialog oluştur
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Ekipman Yönetimi - {character.get('name', 'Karakter')}")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # === Encumbrance Bilgisi ===
        encumbrance = calculate_encumbrance_details(character)
        enc_status = encumbrance.get("encumbrance_status", "unencumbered")
        enc_colors = {
            "unencumbered": "#27ae60",
            "at_capacity": "#f39c12",
            "encumbered": "#e67e22",
            "heavily_encumbered": "#e74c3c"
        }
        enc_text = {
            "unencumbered": "Normal",
            "at_capacity": "Kapasitede",
            "encumbered": "Yüklü (-10 ft hareket)",
            "heavily_encumbered": "Çok Yüklü (-20 ft hareket)"
        }

        enc_frame = ctk.CTkFrame(main_frame)
        enc_frame.pack(fill="x", pady=(0, 10))

        enc_label = ctk.CTkLabel(
            enc_frame,
            text=f"⚖️ Ağırlık: {encumbrance.get('total_weight', 0):.1f} / {encumbrance.get('base_capacity', 0)} lbs  |  "
                 f"Durum: {enc_text.get(enc_status, enc_status)}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=enc_colors.get(enc_status, "#ffffff")
        )
        enc_label.pack(padx=10, pady=8)

        # === Attunement Bilgisi ===
        attunement = check_attunement_limit(character)

        att_frame = ctk.CTkFrame(main_frame)
        att_frame.pack(fill="x", pady=(0, 10))

        att_color = "#27ae60" if attunement["can_attune_more"] else "#e74c3c"
        att_label = ctk.CTkLabel(
            att_frame,
            text=f"✨ Attunement: {attunement['current_attuned']}/{attunement['max_attuned']}  |  "
                 f"Kalan Slot: {attunement['remaining_slots']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=att_color
        )
        att_label.pack(padx=10, pady=8)

        if attunement["attuned_items"]:
            att_items_label = ctk.CTkLabel(
                att_frame,
                text=f"Attune: {', '.join(attunement['attuned_items'])}",
                font=ctk.CTkFont(size=11)
            )
            att_items_label.pack(padx=10, pady=(0, 5))

        # === Ekipman Listesi ===
        list_label = ctk.CTkLabel(
            main_frame,
            text="Mevcut Ekipman:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_label.pack(anchor="w", padx=10, pady=(10, 5))

        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        equipment = character.get("equipment", [])
        starting_equipment = character.get("starting_equipment", [])

        # Tüm ekipmanları birleştir
        all_equipment = []
        for item in equipment:
            if isinstance(item, dict):
                all_equipment.append(item)
            elif isinstance(item, str):
                all_equipment.append({"name": item, "type": "misc", "weight": 0})
        for item in starting_equipment:
            if isinstance(item, str):
                # Zaten all_equipment'da yoksa ekle
                if not any(e.get("name") == item for e in all_equipment):
                    all_equipment.append({"name": item, "type": "misc", "weight": 0})

        if not all_equipment:
            no_eq_label = ctk.CTkLabel(
                scroll_frame,
                text="Henüz ekipman yok.",
                font=ctk.CTkFont(size=12)
            )
            no_eq_label.pack(pady=20)
        else:
            for item in all_equipment:
                item_frame = ctk.CTkFrame(scroll_frame)
                item_frame.pack(fill="x", padx=5, pady=3)

                item_name = item.get("name", "Bilinmeyen")
                item_type = item.get("type", "misc")
                item_weight = item.get("weight", 0)
                is_attuned = item.get("attuned", False)
                requires_attunement = item.get("requires_attunement", False)

                # Magic item bonus bilgileri
                ac_bonus = extract_magic_item_ac_bonus(item)
                attack_bonus = extract_magic_item_bonus(item, "attack")
                damage_bonus = extract_magic_item_bonus(item, "damage")

                # İsim ve detay
                name_text = item_name
                if ac_bonus:
                    name_text += f" (+{ac_bonus} AC)"
                if attack_bonus:
                    name_text += f" (+{attack_bonus} Attack)"
                if damage_bonus:
                    name_text += f" (+{damage_bonus} Damage)"

                name_label = ctk.CTkLabel(
                    item_frame,
                    text=name_text,
                    font=ctk.CTkFont(size=12, weight="bold" if requires_attunement else "normal")
                )
                name_label.pack(side="left", padx=10, pady=5)

                # Ağırlık
                if item_weight:
                    weight_label = ctk.CTkLabel(
                        item_frame,
                        text=f"{item_weight} lb",
                        font=ctk.CTkFont(size=11),
                        text_color="#7f8c8d"
                    )
                    weight_label.pack(side="right", padx=10, pady=5)

                # Attunement durumu
                if is_attuned:
                    att_icon = ctk.CTkLabel(
                        item_frame,
                        text="✨ Attuned",
                        font=ctk.CTkFont(size=11),
                        text_color="#8e44ad"
                    )
                    att_icon.pack(side="right", padx=5, pady=5)
                elif requires_attunement:
                    att_icon = ctk.CTkLabel(
                        item_frame,
                        text="(Attunement Gerekli)",
                        font=ctk.CTkFont(size=11),
                        text_color="#e67e22"
                    )
                    att_icon.pack(side="right", padx=5, pady=5)

        # === Yeni Ekipman Ekleme ===
        add_frame = ctk.CTkFrame(main_frame)
        add_frame.pack(fill="x", pady=(10, 5))

        add_label = ctk.CTkLabel(
            add_frame,
            text="Yeni Ekipman Ekle:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        add_label.pack(side="left", padx=10, pady=5)

        new_item_entry = ctk.CTkEntry(add_frame, placeholder_text="Ekipman adı...")
        new_item_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        def on_add():
            item_name = new_item_entry.get().strip()
            if not item_name:
                return
            # Equipment listesine ekle
            eq_list = character.get("equipment", [])
            if not isinstance(eq_list, list):
                eq_list = []
            eq_list.append({"name": item_name, "type": "misc", "weight": 0, "quantity": 1})
            character["equipment"] = eq_list
            # Dosyaya kaydet
            try:
                with open(character_file, 'w', encoding='utf-8') as f:
                    json.dump(character, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Başarılı", f"{item_name} eklendi!")
                dialog.destroy()
                self._open_equipment_manager()  # Yeniden aç
            except Exception as e:
                messagebox.showerror("Hata", f"Kaydedilemedi: {e}")

        add_btn = ctk.CTkButton(add_frame, text="Ekle", command=on_add, width=80)
        add_btn.pack(side="right", padx=10, pady=5)

        # === Kapat butonu ===
        close_btn = ctk.CTkButton(
            main_frame,
            text="Kapat",
            command=dialog.destroy,
            width=100
        )
        close_btn.pack(pady=(5, 0))

    def _validate_character(self):
        """Karakter dogrulama - kural uygunlugu ve veri kontrolu"""
        import json
        from tkinter import filedialog, messagebox

        character_file = filedialog.askopenfilename(
            title="Dogrulanacak Karakter Dosyasi",
            filetypes=[("JSON files", "*.json")],
            initialdir="characters"
        )
        if not character_file:
            return

        try:
            with open(character_file, 'r', encoding='utf-8') as f:
                character = json.load(f)
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okunamadi: {e}")
            return

        system = character.get('system', '').lower()
        errors = []

        # Sisteme gore dogrulama
        try:
            if system in ['dnd5e', 'dnd']:
                from creators.dnd5e_creator import DND5ECreator
                creator = DND5ECreator()
                errors = creator.validate_character(character)
            elif system == 'pathfinder1e':
                from creators.pathfinder1e_creator import Pathfinder1ECreator
                creator = Pathfinder1ECreator()
                errors = creator.validate_character(character)
            elif system in ['mm3e', 'mm']:
                from creators.mm3e_creator import MM3ECreator
                creator = MM3ECreator()
                errors = creator.validate_character(character)
            elif system in ['vtm5e', 'vtm']:
                from creators.vtm5e_creator import VTM5ECreator
                creator = VTM5ECreator()
                errors = creator.validate_character(character)
            else:
                errors = [f"Bilinmeyen sistem: {system}"]
        except Exception as e:
            errors = [f"Dogrulama hatasi: {e}"]

        # Sonuc dialog'u
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Dogrulama - {character.get('name', '?')}")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        char_name = character.get('name', 'Bilinmeyen')
        if not errors:
            title_text = f"✅ {char_name} - Dogrulama Basarili!"
            title_color = "#27ae60"
        else:
            real_errors = [e for e in errors if not e.startswith("[UYARI]")]
            warnings = [e for e in errors if e.startswith("[UYARI]")]
            if real_errors:
                title_text = f"❌ {char_name} - {len(real_errors)} Hata, {len(warnings)} Uyari"
                title_color = "#e74c3c"
            else:
                title_text = f"⚠️ {char_name} - {len(warnings)} Uyari (hata yok)"
                title_color = "#f39c12"

        title_label = ctk.CTkLabel(
            frame, text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=title_color
        )
        title_label.pack(pady=(10, 10))

        result_text = ctk.CTkTextbox(frame, height=250)
        result_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if errors:
            for err in errors:
                result_text.insert("end", f"{err}\n")
        else:
            result_text.insert("end", "Tum kontroller basarili!\n\n")
            result_text.insert("end", f"Sistem: {character.get('system', '?')}\n")
            result_text.insert("end", f"Irk: {character.get('race', '?')}\n")
            result_text.insert("end", f"Sinif: {character.get('class', '?')}\n")
            result_text.insert("end", f"Seviye: {character.get('level', '?')}\n")
            result_text.insert("end", f"HP: {character.get('hit_points', character.get('hp', '?'))}\n")
            result_text.insert("end", f"AC: {character.get('armor_class', '?')}\n")

        close_btn = ctk.CTkButton(frame, text="Kapat", command=dialog.destroy, width=100)
        close_btn.pack(pady=(0, 5))

    def _compare_characters(self):
        """Iki karakteri yan yana karsilastir"""
        import json
        from tkinter import filedialog, messagebox

        # Ilk karakter
        file1 = filedialog.askopenfilename(
            title="1. Karakter Dosyasi Secin",
            filetypes=[("JSON files", "*.json")],
            initialdir="characters"
        )
        if not file1:
            return

        # Ikinci karakter
        file2 = filedialog.askopenfilename(
            title="2. Karakter Dosyasi Secin",
            filetypes=[("JSON files", "*.json")],
            initialdir="characters"
        )
        if not file2:
            return

        try:
            with open(file1, 'r', encoding='utf-8') as f:
                char1 = json.load(f)
            with open(file2, 'r', encoding='utf-8') as f:
                char2 = json.load(f)
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okunamadi: {e}")
            return

        # Karsilastirma dialog'u
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Karakter Karsilastirma")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Baslik
        name1 = char1.get('name', 'Karakter 1')
        name2 = char2.get('name', 'Karakter 2')

        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame, text=name1,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3498db"
        ).pack(side="left", expand=True)

        ctk.CTkLabel(
            header_frame, text="VS",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            header_frame, text=name2,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e74c3c"
        ).pack(side="left", expand=True)

        # Karsilastirma tablosu
        scroll = ctk.CTkScrollableFrame(main_frame)
        scroll.pack(fill="both", expand=True, pady=(0, 10))

        # Karsilastirma satirlari
        compare_fields = [
            ("Sistem", "system"),
            ("Irk", "race"),
            ("Sinif", "class"),
            ("Seviye", "level"),
            ("Arka Plan", "background"),
            ("HP", "hit_points"),
            ("AC", "armor_class"),
            ("Initiative", "initiative"),
            ("Proficiency Bonus", "proficiency_bonus"),
            ("Speed", "movement_speed"),
            ("Spell Save DC", "spell_save_dc"),
            ("Spell Attack", "spell_attack_bonus"),
        ]

        # Ability scores
        abilities_order = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

        def add_row(label: str, val1, val2):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", padx=5, pady=2)

            # Deger karsilastirmasi icin renk
            color1 = "#ffffff"
            color2 = "#ffffff"
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 > val2:
                    color1 = "#27ae60"
                    color2 = "#e74c3c"
                elif val2 > val1:
                    color1 = "#e74c3c"
                    color2 = "#27ae60"

            ctk.CTkLabel(row, text=str(val1 if val1 is not None else "-"),
                         text_color=color1, width=200).pack(side="left", expand=True)
            ctk.CTkLabel(row, text=label,
                         font=ctk.CTkFont(weight="bold"), width=150).pack(side="left")
            ctk.CTkLabel(row, text=str(val2 if val2 is not None else "-"),
                         text_color=color2, width=200).pack(side="left", expand=True)

        # Temel bilgiler
        for label, key in compare_fields:
            v1 = char1.get(key)
            v2 = char2.get(key)
            # hit_points alternatif anahtarlar
            if key == "hit_points":
                v1 = v1 or char1.get("hp")
                v2 = v2 or char2.get("hp")
            add_row(label, v1, v2)

        # Separator
        sep = ctk.CTkFrame(scroll, height=2, fg_color="#3498db")
        sep.pack(fill="x", padx=10, pady=8)

        # Ability scores
        abilities1 = char1.get("abilities", {})
        abilities2 = char2.get("abilities", {})
        for ab in abilities_order:
            s1 = abilities1.get(ab, abilities1.get(ab.lower()))
            s2 = abilities2.get(ab, abilities2.get(ab.lower()))
            mod1 = f"{s1} ({(s1-10)//2:+d})" if isinstance(s1, int) else str(s1)
            mod2 = f"{s2} ({(s2-10)//2:+d})" if isinstance(s2, int) else str(s2)
            add_row(ab[:3].upper(), mod1, mod2)

        # Separator
        sep2 = ctk.CTkFrame(scroll, height=2, fg_color="#3498db")
        sep2.pack(fill="x", padx=10, pady=8)

        # Skills karsilastirmasi (varsa)
        skills1 = char1.get("skills", {})
        skills2 = char2.get("skills", {})
        if isinstance(skills1, dict) and isinstance(skills2, dict):
            all_skills = sorted(set(list(skills1.keys()) + list(skills2.keys())))
            for skill in all_skills[:18]:
                s1 = skills1.get(skill)
                s2 = skills2.get(skill)
                if isinstance(s1, int):
                    s1 = f"{s1:+d}"
                if isinstance(s2, int):
                    s2 = f"{s2:+d}"
                add_row(skill, s1, s2)

        # Kapat
        ctk.CTkButton(main_frame, text="Kapat", command=dialog.destroy, width=100).pack(pady=(5, 0))

    def _create_dnd_tab(self, tab_frame):
        """Create D&D 5e specific content"""
        content_frame = ctk.CTkFrame(tab_frame)
        content_frame.pack(fill="x", padx=20, pady=(0, 20))

        info_label = ctk.CTkLabel(
            content_frame,
            text="Adım adım karakter oluşturma sihirbazı için 'Karakteri Oluştur' butonuna tıklayın.",
            font=ctk.CTkFont(size=12),
            wraplength=400
        )
        info_label.pack(pady=20)

        # Wizard spellbook / prepared spells yönetimi için buton
        spellbook_btn = ctk.CTkButton(
            content_frame,
            text="📖 Wizard Spellbook / Büyü Hazırlama",
            command=self._open_spellbook_manager,
            font=ctk.CTkFont(size=12),
            height=32
        )
        spellbook_btn.pack(pady=(0, 10))

        # Equipment yönetimi için buton
        equipment_btn = ctk.CTkButton(
            content_frame,
            text="🎒 Ekipman Yönetimi",
            command=self._open_equipment_manager,
            font=ctk.CTkFont(size=12),
            height=32
        )
        equipment_btn.pack(pady=(0, 10))

        # Karakter dogrulama butonu
        validate_btn = ctk.CTkButton(
            content_frame,
            text="✅ Karakter Doğrula",
            command=self._validate_character,
            font=ctk.CTkFont(size=12),
            height=32
        )
        validate_btn.pack(pady=(0, 10))

        # Karakter karsilastirma butonu
        compare_btn = ctk.CTkButton(
            content_frame,
            text="📊 Karakter Karşılaştır",
            command=self._compare_characters,
            font=ctk.CTkFont(size=12),
            height=32
        )
        compare_btn.pack(pady=(0, 10))

        # Condition Tracker button
        condition_btn = ctk.CTkButton(
            content_frame,
            text="🎭 Durum Efektleri (Conditions)",
            command=self._open_condition_tracker,
            font=ctk.CTkFont(size=12),
            height=32
        )
        condition_btn.pack(pady=(0, 10))

        # --- Yeni Evrensel Özellikler ---
        sep = ctk.CTkLabel(content_frame, text="─── Ek Araçlar ───", font=ctk.CTkFont(size=11), text_color="gray50")
        sep.pack(pady=(5, 5))

        encounter_btn = ctk.CTkButton(
            content_frame, text="⚔️ Encounter Tracker (Savaş Takip)",
            command=lambda: self._open_encounter_tracker("dnd5e"),
            font=ctk.CTkFont(size=12), height=32
        )
        encounter_btn.pack(pady=(0, 5))

        homebrew_btn = ctk.CTkButton(
            content_frame, text="🔧 Homebrew İçerik Yöneticisi",
            command=lambda: self._open_homebrew_manager("dnd5e"),
            font=ctk.CTkFont(size=12), height=32
        )
        homebrew_btn.pack(pady=(0, 5))

        portrait_btn = ctk.CTkButton(
            content_frame, text="🖼️ Karakter Portresi",
            command=lambda: self._open_portrait_manager("dnd5e"),
            font=ctk.CTkFont(size=12), height=32
        )
        portrait_btn.pack(pady=(0, 5))

        html_btn = ctk.CTkButton(
            content_frame, text="🌐 HTML/Web Export",
            command=lambda: self._export_html("dnd5e"),
            font=ctk.CTkFont(size=12), height=32
        )
        html_btn.pack(pady=(0, 10))

    def _open_condition_tracker(self):
        """Open Condition/Status Effect tracker dialog"""
        # Ask user to select a character
        character_file = filedialog.askopenfilename(
            title="Durum efekti yönetilecek karakteri seçin",
            filetypes=[("JSON files", "*.json")],
            initialdir="characters"
        )
        if not character_file:
            return

        try:
            with open(character_file, 'r', encoding='utf-8') as f:
                character = json.load(f)
        except Exception as e:
            messagebox.showerror("Hata", f"Karakter yüklenemedi: {e}")
            return

        try:
            from utils.conditions import (
                get_all_conditions, get_active_conditions,
                add_condition_to_character, remove_condition_from_character,
                get_condition_summary, CONDITIONS
            )
        except ImportError:
            messagebox.showerror("Hata", "Condition modülü yüklenemedi!")
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Durum Efektleri - {character.get('name', 'Karakter')}")
        dialog.geometry("850x600")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()

        # Title
        title = ctk.CTkLabel(
            dialog,
            text=f"🎭 {character.get('name', 'Karakter')} - Durum Efektleri",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(15, 10))

        # Main content: Left (active) + Right (add new)
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Left: Active conditions
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        left_title = ctk.CTkLabel(
            left_frame,
            text="Aktif Durumlar",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        left_title.pack(pady=(10, 5))

        active_scroll = ctk.CTkScrollableFrame(left_frame)
        active_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        def refresh_active_list():
            for w in active_scroll.winfo_children():
                w.destroy()

            active = get_active_conditions(character)
            if not active:
                empty_label = ctk.CTkLabel(
                    active_scroll,
                    text="Aktif durum efekti yok.\nSağ taraftan ekleyebilirsiniz.",
                    font=ctk.CTkFont(size=12),
                    text_color="gray60"
                )
                empty_label.pack(pady=30)
                return

            for cond in active:
                cond_frame = ctk.CTkFrame(active_scroll, border_width=1)
                cond_frame.pack(fill="x", pady=3, padx=3)

                # Header row
                header = ctk.CTkFrame(cond_frame, fg_color="transparent")
                header.pack(fill="x", padx=5, pady=(5, 0))

                icon = cond.get("icon", "❓")
                display_name = cond.get("display_name", cond.get("name", ""))
                level_info = f" (Lv{cond['level']})" if cond.get("level") else ""

                name_label = ctk.CTkLabel(
                    header,
                    text=f"{icon} {display_name}{level_info}",
                    font=ctk.CTkFont(size=13, weight="bold")
                )
                name_label.pack(side="left")

                # Remove button
                cond_name = cond.get("name", "")
                remove_btn = ctk.CTkButton(
                    header,
                    text="✕ Kaldır",
                    width=80,
                    height=24,
                    fg_color="#F44336",
                    hover_color="#D32F2F",
                    font=ctk.CTkFont(size=11),
                    command=lambda cn=cond_name: remove_and_refresh(cn)
                )
                remove_btn.pack(side="right")

                # Effects
                effects = cond.get("effects", [])
                if effects:
                    effects_text = "\n".join(f"  • {e}" for e in effects[:4])
                    effects_label = ctk.CTkLabel(
                        cond_frame,
                        text=effects_text,
                        font=ctk.CTkFont(size=10),
                        text_color="gray60",
                        justify="left"
                    )
                    effects_label.pack(anchor="w", padx=10, pady=(2, 5))

                # Duration/Notes
                duration = cond.get("duration", "")
                notes = cond.get("notes", "")
                if duration or notes:
                    meta_parts = []
                    if duration:
                        meta_parts.append(f"Süre: {duration}")
                    if notes:
                        meta_parts.append(f"Not: {notes}")
                    meta_label = ctk.CTkLabel(
                        cond_frame,
                        text=" | ".join(meta_parts),
                        font=ctk.CTkFont(size=10),
                        text_color="#FFB74D"
                    )
                    meta_label.pack(anchor="w", padx=10, pady=(0, 5))

        def remove_and_refresh(condition_name):
            remove_condition_from_character(character, condition_name)
            refresh_active_list()
            save_character()

        def save_character():
            try:
                with open(character_file, 'w', encoding='utf-8') as f:
                    json.dump(character, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        # Right: Add condition
        right_frame = ctk.CTkFrame(main_frame, width=350)
        right_frame.pack(side="right", fill="both", padx=(5, 0))
        right_frame.pack_propagate(False)

        right_title = ctk.CTkLabel(
            right_frame,
            text="Durum Ekle",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        right_title.pack(pady=(10, 5))

        # Category filter
        cat_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        cat_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(cat_frame, text="Kategori:", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        cat_var = ctk.StringVar(value="Hepsi")
        cat_combo = ctk.CTkComboBox(
            cat_frame,
            values=["Hepsi", "physical", "mental", "sensory", "magical", "class_feature"],
            variable=cat_var, width=140
        )
        cat_combo.pack(side="left")

        # Condition list
        cond_scroll = ctk.CTkScrollableFrame(right_frame, height=250)
        cond_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        selected_condition = ctk.StringVar(value="")

        def populate_conditions():
            for w in cond_scroll.winfo_children():
                w.destroy()
            cat_filter = cat_var.get()
            for name, data in CONDITIONS.items():
                if cat_filter != "Hepsi" and data.get("category") != cat_filter:
                    continue
                icon = data.get("icon", "")
                display = data.get("name", name)
                rb = ctk.CTkRadioButton(
                    cond_scroll,
                    text=f"{icon} {display}",
                    variable=selected_condition,
                    value=name,
                    font=ctk.CTkFont(size=11)
                )
                rb.pack(anchor="w", padx=5, pady=2)

        populate_conditions()
        cat_combo.configure(command=lambda _: populate_conditions())

        # Duration and notes
        options_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(options_frame, text="Süre:", font=ctk.CTkFont(size=11)).pack(anchor="w")
        duration_entry = ctk.CTkEntry(options_frame, placeholder_text="ör: 1 dakika, 10 tur...")
        duration_entry.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(options_frame, text="Not:", font=ctk.CTkFont(size=11)).pack(anchor="w")
        notes_entry = ctk.CTkEntry(options_frame, placeholder_text="Ek bilgi...")
        notes_entry.pack(fill="x", pady=(0, 5))

        # Exhaustion level
        exh_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        exh_frame.pack(fill="x", padx=10, pady=(0, 5))
        ctk.CTkLabel(exh_frame, text="Bitkinlik Seviyesi:", font=ctk.CTkFont(size=11)).pack(side="left")
        exh_var = ctk.StringVar(value="1")
        exh_combo = ctk.CTkComboBox(exh_frame, values=["1", "2", "3", "4", "5", "6"], variable=exh_var, width=60)
        exh_combo.pack(side="left", padx=5)

        def add_condition():
            cond_name = selected_condition.get()
            if not cond_name:
                messagebox.showwarning("Uyarı", "Bir durum seçin!")
                return
            duration = duration_entry.get().strip()
            notes = notes_entry.get().strip()
            level = int(exh_var.get()) if cond_name == "Exhaustion" else 1

            add_condition_to_character(character, cond_name, duration, notes, level)
            refresh_active_list()
            save_character()
            self._log_message(f"🎭 {character.get('name', '')}: {cond_name} eklendi")

        add_btn = ctk.CTkButton(
            right_frame,
            text="➕ Durumu Ekle",
            command=add_condition,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35
        )
        add_btn.pack(pady=(5, 10), padx=10)

        # Initial refresh
        refresh_active_list()

    def _create_pathfinder_tab(self, tab_frame):
        """Create Pathfinder 1e specific content with spell browser"""
        content_frame = ctk.CTkFrame(tab_frame)
        content_frame.pack(fill="x", padx=20, pady=(0, 10))

        info_label = ctk.CTkLabel(
            content_frame,
            text="Adım adım karakter oluşturma sihirbazı için 'Karakteri Oluştur' butonuna tıklayın.",
            font=ctk.CTkFont(size=12),
            wraplength=400
        )
        info_label.pack(pady=(10, 5))

        # Spell Browser button
        spell_btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        spell_btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        spell_browser_btn = ctk.CTkButton(
            spell_btn_frame,
            text="🔮 Büyü Tarayıcı (Spell Browser)",
            command=self._open_pf_spell_browser,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35
        )
        spell_browser_btn.pack(side="left", padx=(0, 10))

        spell_clean_btn = ctk.CTkButton(
            spell_btn_frame,
            text="🧹 Veriyi Temizle & Güncelle",
            command=self._clean_pf_spell_data,
            font=ctk.CTkFont(size=12),
            height=35
        )
        spell_clean_btn.pack(side="left")

        # --- Yeni Evrensel Özellikler ---
        sep = ctk.CTkLabel(content_frame, text="─── Ek Araçlar ───", font=ctk.CTkFont(size=11), text_color="gray50")
        sep.pack(pady=(5, 5))

        pf_extra_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        pf_extra_frame.pack(fill="x", padx=10, pady=(0, 10))

        encounter_btn = ctk.CTkButton(
            pf_extra_frame, text="⚔️ Encounter Tracker",
            command=lambda: self._open_encounter_tracker("pathfinder1e"),
            font=ctk.CTkFont(size=12), height=32
        )
        encounter_btn.pack(side="left", padx=(0, 5))

        homebrew_btn = ctk.CTkButton(
            pf_extra_frame, text="🔧 Homebrew",
            command=lambda: self._open_homebrew_manager("pathfinder1e"),
            font=ctk.CTkFont(size=12), height=32
        )
        homebrew_btn.pack(side="left", padx=(0, 5))

        portrait_btn = ctk.CTkButton(
            pf_extra_frame, text="🖼️ Portre",
            command=lambda: self._open_portrait_manager("pathfinder1e"),
            font=ctk.CTkFont(size=12), height=32
        )
        portrait_btn.pack(side="left", padx=(0, 5))

        html_btn = ctk.CTkButton(
            pf_extra_frame, text="🌐 HTML Export",
            command=lambda: self._export_html("pathfinder1e"),
            font=ctk.CTkFont(size=12), height=32
        )
        html_btn.pack(side="left")

    def _open_pf_spell_browser(self):
        """Open Pathfinder 1e Spell Browser dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Pathfinder 1e - Büyü Tarayıcı")
        dialog.geometry("900x650")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()

        # Load PF1e data
        try:
            data_file = Path(__file__).parent.parent / "data" / "pathfinder_1e_data.json"
            with open(data_file, 'r', encoding='utf-8') as f:
                pf_data = json.load(f)
            spells = pf_data.get("spells", {})
        except Exception as e:
            messagebox.showerror("Hata", f"Veri yüklenemedi: {e}")
            dialog.destroy()
            return

        # Title
        title = ctk.CTkLabel(
            dialog,
            text=f"🔮 Pathfinder 1e Büyü Tarayıcı ({len(spells)} büyü)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(15, 10))

        # Filter frame
        filter_frame = ctk.CTkFrame(dialog)
        filter_frame.pack(fill="x", padx=15, pady=(0, 10))

        # Search
        ctk.CTkLabel(filter_frame, text="Ara:").pack(side="left", padx=(10, 5))
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(filter_frame, textvariable=search_var, width=200, placeholder_text="Büyü adı...")
        search_entry.pack(side="left", padx=(0, 15))

        # Level filter
        ctk.CTkLabel(filter_frame, text="Seviye:").pack(side="left", padx=(0, 5))
        level_var = ctk.StringVar(value="Hepsi")
        level_combo = ctk.CTkComboBox(
            filter_frame,
            values=["Hepsi", "0 (Cantrip)", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
            variable=level_var, width=120
        )
        level_combo.pack(side="left", padx=(0, 15))

        # School filter
        ctk.CTkLabel(filter_frame, text="Okul:").pack(side="left", padx=(0, 5))
        school_var = ctk.StringVar(value="Hepsi")
        schools = ["Hepsi", "abjuration", "conjuration", "divination", "enchantment",
                    "evocation", "illusion", "necromancy", "transmutation", "universal"]
        school_combo = ctk.CTkComboBox(filter_frame, values=schools, variable=school_var, width=140)
        school_combo.pack(side="left", padx=(0, 10))

        # Class filter
        ctk.CTkLabel(filter_frame, text="Sınıf:").pack(side="left", padx=(0, 5))
        class_var = ctk.StringVar(value="Hepsi")
        # Collect all classes from spells
        all_classes = set()
        for s in spells.values():
            for c in s.get("levels_by_class", {}).keys():
                all_classes.add(c)
        class_list = ["Hepsi"] + sorted(all_classes)
        class_combo = ctk.CTkComboBox(filter_frame, values=class_list, variable=class_var, width=130)
        class_combo.pack(side="left")

        # Results frame
        results_frame = ctk.CTkFrame(dialog)
        results_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Left: spell list
        list_frame = ctk.CTkFrame(results_frame)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        spell_listbox = ctk.CTkScrollableFrame(list_frame)
        spell_listbox.pack(fill="both", expand=True)

        # Right: spell detail
        detail_frame = ctk.CTkFrame(results_frame, width=350)
        detail_frame.pack(side="right", fill="both", padx=(5, 0))
        detail_frame.pack_propagate(False)

        detail_text = ctk.CTkTextbox(detail_frame, wrap="word", font=ctk.CTkFont(size=12))
        detail_text.pack(fill="both", expand=True, padx=5, pady=5)
        detail_text.insert("1.0", "Bir büyü seçin...")
        detail_text.configure(state="disabled")

        # Spell selection handler
        def show_spell_detail(spell_name: str):
            spell = spells.get(spell_name, {})
            detail_text.configure(state="normal")
            detail_text.delete("1.0", "end")

            lines = [f"📜 {spell_name}", "=" * 40, ""]
            lines.append(f"Seviye: {spell.get('level', '?')}")
            lines.append(f"Okul: {spell.get('school', '?')}")
            sub = spell.get('subschool', '')
            if sub:
                lines.append(f"Alt-okul: {sub}")
            desc_val = spell.get('descriptor', '')
            if desc_val:
                lines.append(f"Descriptor: {desc_val}")
            lines.append("")
            lines.append(f"Casting Time: {spell.get('casting_time', '?')}")
            lines.append(f"Components: {spell.get('components', '?')}")
            rng = spell.get('range', '')
            if rng:
                lines.append(f"Range: {rng}")
            tgt = spell.get('target', '')
            if tgt:
                lines.append(f"Target: {tgt}")
            area = spell.get('area', '')
            if area:
                lines.append(f"Area: {area}")
            eff = spell.get('effect', '')
            if eff:
                lines.append(f"Effect: {eff}")
            lines.append(f"Duration: {spell.get('duration', '?')}")
            st = spell.get('saving_throw', '')
            if st:
                lines.append(f"Saving Throw: {st}")
            sr = spell.get('spell_resistance', '')
            if sr:
                lines.append(f"Spell Resistance: {sr}")
            lines.append("")

            # Classes
            lbc = spell.get('levels_by_class', {})
            if lbc:
                cls_parts = [f"{c} {l}" for c, l in sorted(lbc.items())]
                lines.append(f"Sınıflar: {', '.join(cls_parts)}")
                lines.append("")

            lines.append("─" * 40)
            desc = spell.get('description', 'Açıklama yok')
            lines.append(desc)

            detail_text.insert("1.0", "\n".join(lines))
            detail_text.configure(state="disabled")

        # Populate spell list
        spell_buttons = []

        def populate_spells():
            for widget in spell_listbox.winfo_children():
                widget.destroy()
            spell_buttons.clear()

            search = search_var.get().strip().lower()
            level_filter = level_var.get()
            school_filter = school_var.get()
            class_filter = class_var.get()

            filtered = []
            for name, data in sorted(spells.items()):
                # Search filter
                if search and search not in name.lower():
                    continue
                # Level filter
                if level_filter != "Hepsi":
                    target_level = 0 if "Cantrip" in level_filter else int(level_filter)
                    if data.get("level", -1) != target_level:
                        continue
                # School filter
                if school_filter != "Hepsi" and data.get("school", "").lower() != school_filter.lower():
                    continue
                # Class filter
                if class_filter != "Hepsi":
                    if class_filter not in data.get("levels_by_class", {}):
                        continue
                filtered.append((name, data))

            # Status
            count_label = ctk.CTkLabel(
                spell_listbox,
                text=f"Bulunan: {len(filtered)} büyü",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#4CAF50"
            )
            count_label.pack(anchor="w", padx=5, pady=(5, 3))

            for name, data in filtered[:200]:  # Performans icin limit
                level = data.get("level", 0)
                school = data.get("school", "")[:4]
                btn = ctk.CTkButton(
                    spell_listbox,
                    text=f"[Lv{level}] {name} ({school})",
                    anchor="w",
                    height=28,
                    font=ctk.CTkFont(size=11),
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray70", "gray30"),
                    command=lambda n=name: show_spell_detail(n)
                )
                btn.pack(fill="x", padx=2, pady=1)
                spell_buttons.append(btn)

        populate_spells()

        # Bind filter events
        search_var.trace_add("write", lambda *_: populate_spells())
        level_combo.configure(command=lambda _: populate_spells())
        school_combo.configure(command=lambda _: populate_spells())
        class_combo.configure(command=lambda _: populate_spells())

    def _clean_pf_spell_data(self):
        """Clean and update Pathfinder 1e spell data"""
        try:
            from utils.pathfinder_scraper import clean_existing_pathfinder_spells, ensure_core_spells_exist

            data_file = Path(__file__).parent.parent / "data" / "pathfinder_1e_data.json"

            # Once temizle
            cleaned = clean_existing_pathfinder_spells(data_file)
            # Sonra core spell'leri ekle
            added = ensure_core_spells_exist(data_file)

            self._log_message(f"✅ Pathfinder 1e spell verisi güncellendi!")
            self._log_message(f"   🧹 {cleaned} büyü temizlendi")
            self._log_message(f"   ✨ {added} core büyü eklendi/güncellendi")
            messagebox.showinfo(
                "Başarılı",
                f"Spell verisi güncellendi!\n"
                f"Temizlenen: {cleaned}\n"
                f"Eklenen/Güncellenen: {added}"
            )
        except Exception as e:
            messagebox.showerror("Hata", f"Veri temizleme hatası: {e}")
            self._log_message(f"⚠️ Spell veri temizleme hatası: {e}")

    def _create_vtm_tab(self, tab_frame):
        """Create Vampire 5e specific content"""
        content_frame = ctk.CTkFrame(tab_frame)
        content_frame.pack(fill="x", padx=20, pady=(0, 20))

        info_label = ctk.CTkLabel(
            content_frame,
            text="Adım adım karakter oluşturma sihirbazı için 'Karakteri Oluştur' butonuna tıklayın.",
            font=ctk.CTkFont(size=12),
            wraplength=400
        )
        info_label.pack(pady=(10, 5))

        # --- Evrensel Araçlar ---
        sep = ctk.CTkLabel(content_frame, text="─── Araçlar ───", font=ctk.CTkFont(size=11), text_color="gray50")
        sep.pack(pady=(5, 5))

        encounter_btn = ctk.CTkButton(
            content_frame, text="⚔️ Encounter Tracker (Savaş Takip)",
            command=lambda: self._open_encounter_tracker("vtm5e"),
            font=ctk.CTkFont(size=12), height=32
        )
        encounter_btn.pack(pady=(0, 5))

        homebrew_btn = ctk.CTkButton(
            content_frame, text="🔧 Homebrew İçerik Yöneticisi",
            command=lambda: self._open_homebrew_manager("vtm5e"),
            font=ctk.CTkFont(size=12), height=32
        )
        homebrew_btn.pack(pady=(0, 5))

        portrait_btn = ctk.CTkButton(
            content_frame, text="🖼️ Karakter Portresi",
            command=lambda: self._open_portrait_manager("vtm5e"),
            font=ctk.CTkFont(size=12), height=32
        )
        portrait_btn.pack(pady=(0, 5))

        html_btn = ctk.CTkButton(
            content_frame, text="🌐 HTML/Web Export",
            command=lambda: self._export_html("vtm5e"),
            font=ctk.CTkFont(size=12), height=32
        )
        html_btn.pack(pady=(0, 10))

    def _create_mm_tab(self, tab_frame):
        """Create Mutants & Masterminds specific content"""
        content_frame = ctk.CTkFrame(tab_frame)
        content_frame.pack(fill="x", padx=20, pady=(0, 20))

        info_label = ctk.CTkLabel(
            content_frame,
            text="Adım adım karakter oluşturma sihirbazı için 'Karakteri Oluştur' butonuna tıklayın.",
            font=ctk.CTkFont(size=12),
            wraplength=400
        )
        info_label.pack(pady=(10, 5))

        # --- Evrensel Araçlar ---
        sep = ctk.CTkLabel(content_frame, text="─── Araçlar ───", font=ctk.CTkFont(size=11), text_color="gray50")
        sep.pack(pady=(5, 5))

        encounter_btn = ctk.CTkButton(
            content_frame, text="⚔️ Encounter Tracker (Savaş Takip)",
            command=lambda: self._open_encounter_tracker("mm3e"),
            font=ctk.CTkFont(size=12), height=32
        )
        encounter_btn.pack(pady=(0, 5))

        homebrew_btn = ctk.CTkButton(
            content_frame, text="🔧 Homebrew İçerik Yöneticisi",
            command=lambda: self._open_homebrew_manager("mm3e"),
            font=ctk.CTkFont(size=12), height=32
        )
        homebrew_btn.pack(pady=(0, 5))

        portrait_btn = ctk.CTkButton(
            content_frame, text="🖼️ Karakter Portresi",
            command=lambda: self._open_portrait_manager("mm3e"),
            font=ctk.CTkFont(size=12), height=32
        )
        portrait_btn.pack(pady=(0, 5))

        html_btn = ctk.CTkButton(
            content_frame, text="🌐 HTML/Web Export",
            command=lambda: self._export_html("mm3e"),
            font=ctk.CTkFont(size=12), height=32
        )
        html_btn.pack(pady=(0, 10))

    # ==================================================================
    # ENCOUNTER TRACKER GUI (Tum Sistemler)
    # ==================================================================
    def _open_encounter_tracker(self, system: str = "dnd5e"):
        """Evrensel Encounter Tracker dialog"""
        from utils.encounter_tracker import EncounterTracker, Combatant, SYSTEM_RULES

        rules = SYSTEM_RULES.get(system, SYSTEM_RULES["dnd5e"])
        tracker = EncounterTracker(system=system)

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"⚔️ Encounter Tracker - {rules['name']}")
        dialog.geometry("950x700")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()

        # Title
        title = ctk.CTkLabel(
            dialog, text=f"⚔️ {rules['name']} - Encounter Tracker",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(10, 5))

        round_label = ctk.CTkLabel(dialog, text="Round: 0 | Encounter başlatılmadı",
                                   font=ctk.CTkFont(size=13))
        round_label.pack(pady=(0, 5))

        # Main layout: Left (initiative list) + Right (controls)
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left: Initiative order
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(left_frame, text="Initiative Sırası",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))

        init_scroll = ctk.CTkScrollableFrame(left_frame)
        init_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        def refresh_initiative():
            for w in init_scroll.winfo_children():
                w.destroy()

            if not tracker.combatants:
                ctk.CTkLabel(init_scroll, text="Henüz katılımcı yok.\nSağ panelden ekleyin.",
                             text_color="gray60").pack(pady=30)
                return

            for i, c in enumerate(tracker.combatants):
                is_current = (i == tracker.current_turn_index and tracker.is_active)
                border_color = "#e94560" if is_current else "#2a2a4a"
                fg = "#1a3a5c" if is_current else "transparent"

                row = ctk.CTkFrame(init_scroll, border_width=2, border_color=border_color, fg_color=fg)
                row.pack(fill="x", pady=2, padx=2)

                top = ctk.CTkFrame(row, fg_color="transparent")
                top.pack(fill="x", padx=5, pady=(5, 2))

                icon = "🎮" if c.is_player else "👹"
                marker = " ◄" if is_current else ""
                ctk.CTkLabel(top, text=f"{icon} {c.name} (Init: {c.initiative}){marker}",
                             font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

                if c.max_hp > 0:
                    hp_pct = c.current_hp / c.max_hp if c.max_hp > 0 else 0
                    hp_color = "#4ecca3" if hp_pct > 0.5 else "#f0a500" if hp_pct > 0.25 else "#e94560"
                    ctk.CTkLabel(top, text=f"HP: {c.current_hp}/{c.max_hp}",
                                 font=ctk.CTkFont(size=12), text_color=hp_color).pack(side="right")

                if c.conditions:
                    ctk.CTkLabel(row, text=f"  Durumlar: {', '.join(c.conditions)}",
                                 font=ctk.CTkFont(size=10), text_color="gray60").pack(anchor="w", padx=10, pady=(0, 3))

                # Damage / Heal buttons
                btn_frame = ctk.CTkFrame(row, fg_color="transparent")
                btn_frame.pack(fill="x", padx=5, pady=(0, 5))

                dmg_entry = ctk.CTkEntry(btn_frame, width=50, placeholder_text="HP")
                dmg_entry.pack(side="left", padx=2)

                ctk.CTkButton(btn_frame, text="-HP", width=40, height=24, fg_color="#e94560",
                              command=lambda e=dmg_entry, n=c.name: apply_dmg(n, e)).pack(side="left", padx=2)
                ctk.CTkButton(btn_frame, text="+HP", width=40, height=24, fg_color="#4ecca3",
                              command=lambda e=dmg_entry, n=c.name: apply_heal(n, e)).pack(side="left", padx=2)
                ctk.CTkButton(btn_frame, text="✕", width=30, height=24, fg_color="#888",
                              command=lambda n=c.name: remove_combatant(n)).pack(side="right", padx=2)

            update_round_label()

        def apply_dmg(name, entry):
            try:
                amt = int(entry.get())
                result = tracker.apply_damage(name, amt)
                refresh_initiative()
                refresh_log()
            except ValueError:
                pass

        def apply_heal(name, entry):
            try:
                amt = int(entry.get())
                result = tracker.apply_heal(name, amt)
                refresh_initiative()
                refresh_log()
            except ValueError:
                pass

        def remove_combatant(name):
            tracker.remove_combatant(name)
            refresh_initiative()

        def update_round_label():
            if tracker.is_active:
                current = tracker.get_current_combatant()
                cur_name = current.name if current else "?"
                round_label.configure(text=f"Round: {tracker.current_round} | Sıra: {cur_name}")
            else:
                round_label.configure(text=f"Round: {tracker.current_round} | {'Bitti' if tracker.current_round > 0 else 'Başlatılmadı'}")

        # Right: Controls
        right_frame = ctk.CTkFrame(main_frame, width=320)
        right_frame.pack(side="right", fill="both", padx=(5, 0))
        right_frame.pack_propagate(False)

        # Add combatant section
        ctk.CTkLabel(right_frame, text="Katılımcı Ekle",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))

        add_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        add_frame.pack(fill="x", padx=10)

        ctk.CTkLabel(add_frame, text="İsim:").pack(anchor="w")
        name_entry = ctk.CTkEntry(add_frame, placeholder_text="Karakter/canavar adı")
        name_entry.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(add_frame, text="Initiative:").pack(anchor="w")
        init_entry = ctk.CTkEntry(add_frame, placeholder_text="Zar sonucu")
        init_entry.pack(fill="x", pady=(0, 5))

        hp_ac_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        hp_ac_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(hp_ac_frame, text="HP:").pack(side="left")
        hp_entry = ctk.CTkEntry(hp_ac_frame, width=60, placeholder_text="HP")
        hp_entry.pack(side="left", padx=(2, 10))

        ctk.CTkLabel(hp_ac_frame, text="AC:").pack(side="left")
        ac_entry = ctk.CTkEntry(hp_ac_frame, width=60, placeholder_text="AC")
        ac_entry.pack(side="left", padx=2)

        is_player_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(add_frame, text="Oyuncu mu?", variable=is_player_var).pack(anchor="w", pady=3)

        def add_combatant():
            n = name_entry.get().strip()
            if not n:
                return
            init_val = int(init_entry.get()) if init_entry.get().strip() else 0
            hp_val = int(hp_entry.get()) if hp_entry.get().strip() else 0
            ac_val = int(ac_entry.get()) if ac_entry.get().strip() else 10
            c = Combatant(name=n, initiative=init_val, system=system,
                          max_hp=hp_val, current_hp=hp_val, ac=ac_val,
                          is_player=is_player_var.get())
            tracker.add_combatant(c)
            name_entry.delete(0, "end")
            init_entry.delete(0, "end")
            hp_entry.delete(0, "end")
            ac_entry.delete(0, "end")
            refresh_initiative()

        ctk.CTkButton(add_frame, text="➕ Ekle", command=add_combatant,
                       font=ctk.CTkFont(weight="bold"), height=32).pack(fill="x", pady=(5, 0))

        # Load from character file
        def load_from_file():
            filepath = filedialog.askopenfilename(
                title="Karakter Dosyası Seç", filetypes=[("JSON", "*.json")],
                initialdir="characters"
            )
            if not filepath:
                return
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    char_data = json.load(f)
                c = Combatant.from_character(char_data)
                tracker.add_combatant(c)
                refresh_initiative()
            except Exception as e:
                messagebox.showerror("Hata", f"Karakter yüklenemedi: {e}")

        ctk.CTkButton(add_frame, text="📂 Dosyadan Yükle", command=load_from_file,
                       height=28).pack(fill="x", pady=(5, 0))

        # Encounter controls
        ctrl_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=10, pady=(15, 5))

        ctk.CTkLabel(ctrl_frame, text="Encounter Kontrolü",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 5))

        def start_encounter():
            tracker.start_encounter()
            refresh_initiative()
            refresh_log()

        def next_turn():
            tracker.next_turn()
            refresh_initiative()
            refresh_log()

        def end_encounter():
            tracker.end_encounter()
            refresh_initiative()
            refresh_log()

        ctk.CTkButton(ctrl_frame, text="▶ Başlat", command=start_encounter,
                       fg_color="#4ecca3", hover_color="#3ba88a", height=35,
                       font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=2)
        ctk.CTkButton(ctrl_frame, text="⏭ Sonraki Tur", command=next_turn,
                       height=35, font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=2)
        ctk.CTkButton(ctrl_frame, text="⏹ Bitir", command=end_encounter,
                       fg_color="#e94560", hover_color="#c73850", height=35).pack(fill="x", pady=2)

        # Save/Load encounter
        def save_encounter():
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json", filetypes=[("JSON", "*.json")],
                title="Encounter Kaydet"
            )
            if filepath:
                tracker.save(Path(filepath))
                messagebox.showinfo("Başarılı", "Encounter kaydedildi!")

        def load_encounter():
            nonlocal tracker
            filepath = filedialog.askopenfilename(
                filetypes=[("JSON", "*.json")], title="Encounter Yükle"
            )
            if filepath:
                tracker = EncounterTracker.load(Path(filepath))
                refresh_initiative()
                refresh_log()

        io_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        io_frame.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(io_frame, text="💾 Kaydet", command=save_encounter, width=100, height=28).pack(side="left", padx=2)
        ctk.CTkButton(io_frame, text="📂 Yükle", command=load_encounter, width=100, height=28).pack(side="left", padx=2)

        # Log
        ctk.CTkLabel(right_frame, text="Encounter Log",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 2))
        log_box = ctk.CTkTextbox(right_frame, height=120)
        log_box.pack(fill="x", padx=10, pady=(0, 10))

        def refresh_log():
            log_box.delete("0.0", "end")
            for entry in tracker.log[-20:]:
                log_box.insert("end", f"{entry}\n")
            log_box.see("end")

        refresh_initiative()

    # ==================================================================
    # HOMEBREW MANAGER GUI (Tum Sistemler)
    # ==================================================================
    def _open_homebrew_manager(self, system: str = "dnd5e"):
        """Evrensel Homebrew İçerik Yöneticisi"""
        from utils.homebrew import (
            get_homebrew_types, get_homebrew_template, get_required_fields,
            validate_homebrew, save_homebrew, load_all_homebrew, delete_homebrew,
            HOMEBREW_DIR
        )

        types = get_homebrew_types(system)
        system_names = {
            "dnd5e": "D&D 5e", "pathfinder1e": "Pathfinder 1e",
            "vtm5e": "VtM 5e", "mm3e": "M&M 3e"
        }

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"🔧 Homebrew - {system_names.get(system, system)}")
        dialog.geometry("850x650")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"🔧 {system_names.get(system, system)} - Homebrew İçerik Yöneticisi",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))

        # Main: Left (existing) + Right (create new)
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left: Existing homebrew
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(left_frame, text="Mevcut Homebrew İçerikler",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))

        existing_scroll = ctk.CTkScrollableFrame(left_frame)
        existing_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        def refresh_existing():
            for w in existing_scroll.winfo_children():
                w.destroy()
            all_hb = load_all_homebrew(system)
            if not all_hb:
                ctk.CTkLabel(existing_scroll, text="Henüz homebrew içerik yok.\nSağ panelden oluşturun.",
                             text_color="gray60").pack(pady=30)
                return
            for key, items in all_hb.items():
                _, ctype = key.split("/", 1)
                type_display = types.get(ctype, ctype)
                ctk.CTkLabel(existing_scroll, text=f"── {type_display} ──",
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color="#e94560").pack(anchor="w", pady=(10, 3), padx=5)
                for item in items:
                    item_frame = ctk.CTkFrame(existing_scroll, border_width=1)
                    item_frame.pack(fill="x", pady=2, padx=5)
                    name = item.get("name", "?")
                    source = item.get("source", "Homebrew")
                    ctk.CTkLabel(item_frame, text=f"  {name} ({source})",
                                 font=ctk.CTkFont(size=12)).pack(side="left", padx=5, pady=5)
                    # Delete button
                    meta = item.get("_homebrew_meta", {})
                    safe_name = name.lower().replace(" ", "_")
                    fpath = HOMEBREW_DIR / system / f"{ctype}_{safe_name}.json"
                    ctk.CTkButton(item_frame, text="🗑️", width=30, height=24,
                                  fg_color="#F44336",
                                  command=lambda p=fpath: delete_and_refresh(p)).pack(side="right", padx=5, pady=5)

        def delete_and_refresh(filepath):
            delete_homebrew(filepath)
            refresh_existing()

        refresh_existing()

        # Right: Create new
        right_frame = ctk.CTkFrame(main_frame, width=380)
        right_frame.pack(side="right", fill="both", padx=(5, 0))
        right_frame.pack_propagate(False)

        ctk.CTkLabel(right_frame, text="Yeni İçerik Oluştur",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))

        # Content type selection
        type_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        type_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(type_frame, text="Tür:").pack(side="left")
        type_keys = list(types.keys())
        type_displays = [types[k] for k in type_keys]
        type_var = ctk.StringVar(value=type_displays[0] if type_displays else "")
        type_combo = ctk.CTkComboBox(type_frame, values=type_displays, variable=type_var, width=200)
        type_combo.pack(side="left", padx=5)

        # Dynamic form
        form_scroll = ctk.CTkScrollableFrame(right_frame, height=350)
        form_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        field_entries = {}

        def rebuild_form(*args):
            nonlocal field_entries
            field_entries.clear()
            for w in form_scroll.winfo_children():
                w.destroy()

            selected_display = type_var.get()
            selected_key = ""
            for k, d in types.items():
                if d == selected_display:
                    selected_key = k
                    break

            template = get_homebrew_template(system, selected_key)
            required = get_required_fields(system, selected_key)

            for field_name, default_val in template.items():
                if field_name.startswith("_"):
                    continue
                is_required = field_name in required
                label_text = f"{'* ' if is_required else ''}{field_name}:"
                ctk.CTkLabel(form_scroll, text=label_text,
                             font=ctk.CTkFont(size=11, weight="bold" if is_required else "normal")).pack(anchor="w", padx=5, pady=(5, 0))

                if isinstance(default_val, bool):
                    var = ctk.BooleanVar(value=default_val)
                    ctk.CTkCheckBox(form_scroll, text="Evet", variable=var).pack(anchor="w", padx=5)
                    field_entries[field_name] = ("bool", var)
                elif isinstance(default_val, (dict, list)):
                    entry = ctk.CTkTextbox(form_scroll, height=60)
                    entry.pack(fill="x", padx=5, pady=2)
                    entry.insert("0.0", json.dumps(default_val, ensure_ascii=False))
                    field_entries[field_name] = ("json", entry)
                elif isinstance(default_val, int):
                    entry = ctk.CTkEntry(form_scroll, placeholder_text=str(default_val))
                    entry.pack(fill="x", padx=5, pady=2)
                    field_entries[field_name] = ("int", entry)
                else:
                    entry = ctk.CTkEntry(form_scroll, placeholder_text=str(default_val) if default_val else "")
                    entry.pack(fill="x", padx=5, pady=2)
                    field_entries[field_name] = ("str", entry)

        type_combo.configure(command=lambda _: rebuild_form())
        rebuild_form()

        def save_new_homebrew():
            selected_display = type_var.get()
            selected_key = ""
            for k, d in types.items():
                if d == selected_display:
                    selected_key = k
                    break

            data = {}
            for field_name, (ftype, widget) in field_entries.items():
                if ftype == "bool":
                    data[field_name] = widget.get()
                elif ftype == "json":
                    raw = widget.get("0.0", "end").strip()
                    try:
                        data[field_name] = json.loads(raw) if raw else {}
                    except json.JSONDecodeError:
                        data[field_name] = raw
                elif ftype == "int":
                    raw = widget.get().strip()
                    data[field_name] = int(raw) if raw else 0
                else:
                    data[field_name] = widget.get().strip()

            errors = validate_homebrew(system, selected_key, data)
            if errors:
                messagebox.showwarning("Doğrulama Hatası", "\n".join(errors))
                return

            filepath = save_homebrew(system, selected_key, data)
            messagebox.showinfo("Başarılı", f"Homebrew kaydedildi!\n{filepath.name}")
            self._log_message(f"🔧 Homebrew: {data.get('name', '?')} ({selected_key}) kaydedildi")
            refresh_existing()

        ctk.CTkButton(right_frame, text="💾 Kaydet",
                       command=save_new_homebrew,
                       font=ctk.CTkFont(size=14, weight="bold"),
                       height=38).pack(pady=(5, 10), padx=10)

    # ==================================================================
    # PORTRAIT MANAGER GUI (Tum Sistemler)
    # ==================================================================
    def _open_portrait_manager(self, system: str = "dnd5e"):
        """Evrensel Karakter Portre Yöneticisi"""
        from utils.portraits import (
            add_portrait, remove_portrait, find_portrait, has_portrait,
            get_all_portraits, validate_portrait_file, PORTRAITS_DIR,
            get_display_size, ALLOWED_EXTENSIONS
        )

        system_names = {
            "dnd5e": "D&D 5e", "pathfinder1e": "Pathfinder 1e",
            "vtm5e": "VtM 5e", "mm3e": "M&M 3e"
        }

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"🖼️ Portre Yöneticisi - {system_names.get(system, system)}")
        dialog.geometry("700x550")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"🖼️ {system_names.get(system, system)} - Karakter Portre Yöneticisi",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))

        # Character selection
        sel_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        sel_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(sel_frame, text="Karakter Adı:", font=ctk.CTkFont(size=12)).pack(side="left")
        char_name_entry = ctk.CTkEntry(sel_frame, placeholder_text="Karakter adını girin...", width=250)
        char_name_entry.pack(side="left", padx=5)

        status_label = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=12))
        status_label.pack(pady=5)

        # Preview frame
        preview_frame = ctk.CTkFrame(dialog)
        preview_frame.pack(fill="both", expand=True, padx=15, pady=5)

        preview_label = ctk.CTkLabel(preview_frame, text="Portre önizlemesi\n(Karakter adını girin ve kontrol edin)",
                                     font=ctk.CTkFont(size=14), text_color="gray60")
        preview_label.pack(expand=True)

        current_portrait_path = [None]

        def check_portrait():
            name = char_name_entry.get().strip()
            if not name:
                status_label.configure(text="Karakter adı girin!", text_color="#e94560")
                return
            portrait = find_portrait(name, system)
            if portrait:
                current_portrait_path[0] = portrait
                status_label.configure(text=f"✅ Portre mevcut: {portrait.name}", text_color="#4ecca3")
                # Try to show image
                try:
                    from PIL import Image
                    img = Image.open(portrait)
                    display_size = get_display_size(system)
                    img.thumbnail(display_size)
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img,
                                           size=(img.width, img.height))
                    preview_label.configure(image=ctk_img, text="")
                    preview_label._ctk_image = ctk_img  # keep reference
                except Exception:
                    preview_label.configure(text=f"Portre: {portrait.name}\n(Önizleme için Pillow gerekli)",
                                           image=None)
            else:
                current_portrait_path[0] = None
                status_label.configure(text="Portre bulunamadı. 'Portre Ekle' ile ekleyebilirsiniz.",
                                       text_color="#f0a500")
                preview_label.configure(text="Portre yok", image=None)

        def add_new_portrait():
            name = char_name_entry.get().strip()
            if not name:
                messagebox.showwarning("Uyarı", "Karakter adı girin!")
                return
            ext_str = " ".join(f"*{e}" for e in ALLOWED_EXTENSIONS)
            filepath = filedialog.askopenfilename(
                title="Portre Resmi Seç",
                filetypes=[("Resim Dosyaları", ext_str), ("Tüm Dosyalar", "*.*")]
            )
            if not filepath:
                return
            errors = validate_portrait_file(filepath)
            if errors:
                messagebox.showerror("Hata", "\n".join(errors))
                return
            try:
                dest = add_portrait(name, filepath, system)
                messagebox.showinfo("Başarılı", f"Portre eklendi!\n{dest.name}")
                self._log_message(f"🖼️ {name} için portre eklendi")
                check_portrait()
            except Exception as e:
                messagebox.showerror("Hata", f"Portre eklenemedi: {e}")

        def remove_current_portrait():
            name = char_name_entry.get().strip()
            if not name:
                return
            if remove_portrait(name, system):
                messagebox.showinfo("Bilgi", "Portre silindi.")
                self._log_message(f"🖼️ {name} portresi silindi")
                check_portrait()
            else:
                messagebox.showinfo("Bilgi", "Silinecek portre bulunamadı.")

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 10))

        ctk.CTkButton(btn_frame, text="🔍 Kontrol Et", command=check_portrait,
                       width=120, height=35).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="➕ Portre Ekle", command=add_new_portrait,
                       width=120, height=35, fg_color="#4ecca3",
                       hover_color="#3ba88a").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑️ Portre Sil", command=remove_current_portrait,
                       width=120, height=35, fg_color="#e94560",
                       hover_color="#c73850").pack(side="left", padx=5)

        # All portraits list
        ctk.CTkLabel(dialog, text="Tüm Portreler:",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15)
        all_portraits = get_all_portraits()
        if all_portraits:
            portraits_text = ", ".join(all_portraits.keys())
        else:
            portraits_text = "Henüz portre yok"
        ctk.CTkLabel(dialog, text=portraits_text, font=ctk.CTkFont(size=11),
                     text_color="gray60", wraplength=650).pack(anchor="w", padx=15, pady=(0, 10))

    # ==================================================================
    # HTML/WEB EXPORT (Tum Sistemler)
    # ==================================================================
    def _export_html(self, system: str = "dnd5e"):
        """Evrensel HTML Export"""
        # Get current character name
        current_tab = self.tabview.get()
        name_entry = getattr(self, f"{current_tab.lower().replace(' ', '_')}_name", None)
        character_name = name_entry.get().strip() if name_entry else ""

        if not character_name:
            # Dosyadan sec
            character_file = filedialog.askopenfilename(
                title="HTML Export İçin Karakter Seçin",
                filetypes=[("JSON files", "*.json")],
                initialdir="characters"
            )
            if not character_file:
                return
            try:
                with open(character_file, 'r', encoding='utf-8') as f:
                    character = json.load(f)
            except Exception as e:
                messagebox.showerror("Hata", f"Karakter yüklenemedi: {e}")
                return
        else:
            try:
                system_key = self.creators.get(current_tab, system)
                creator = CharacterFactory.create_creator(system_key)
                filename = f"{character_name.lower().replace(' ', '_')}_{system_key}"
                character = creator.load_character(filename)
            except Exception:
                # Dosyadan sec
                character_file = filedialog.askopenfilename(
                    title="Karakter Dosyası Seçin",
                    filetypes=[("JSON files", "*.json")],
                    initialdir="characters"
                )
                if not character_file:
                    return
                try:
                    with open(character_file, 'r', encoding='utf-8') as f:
                        character = json.load(f)
                except Exception as e:
                    messagebox.showerror("Hata", f"Karakter yüklenemedi: {e}")
                    return

        try:
            from utils.export_html import export_character_html
            filepath = export_character_html(character)
            messagebox.showinfo("Başarılı",
                                f"HTML karakter kağıdı oluşturuldu!\n\n{filepath}\n\nTarayıcıda açmak ister misiniz?")
            self._log_message(f"🌐 {character.get('name', '?')} HTML export edildi: {filepath.name}")

            # Otomatik aç
            import webbrowser
            webbrowser.open(str(filepath))

        except Exception as e:
            messagebox.showerror("Hata", f"HTML export hatası: {e}")
            self._log_message(f"⚠️ HTML export hatası: {e}")

    def _create_bottom_section(self):
        """Create bottom section with buttons and log"""
        bottom_frame = ctk.CTkFrame(self.main_frame)
        bottom_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Button frame
        button_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 10))

        # Create Character button
        create_btn = ctk.CTkButton(
            button_frame,
            text="🎲 Karakteri Oluştur",
            command=self._start_character_creation,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        create_btn.pack(side="left", padx=(0, 10))

        # Level Up button
        levelup_btn = ctk.CTkButton(
            button_frame,
            text="⬆️ Level Up",
            command=self._start_level_up,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        levelup_btn.pack(side="left", padx=(0, 10))

        # Batch Operations button
        batch_btn = ctk.CTkButton(
            button_frame,
            text="📊 Toplu İşlemler",
            command=self._show_batch_operations,
            font=ctk.CTkFont(size=14),
            height=40
        )
        batch_btn.pack(side="left", padx=(0, 10))

        # PDF Export button
        pdf_btn = ctk.CTkButton(
            button_frame,
            text="📄 PDF Export",
            command=self._export_pdf,
            font=ctk.CTkFont(size=14),
            height=40
        )
        pdf_btn.pack(side="left", padx=(0, 10))

        # SQLite Save button
        sqlite_save_btn = ctk.CTkButton(
            button_frame,
            text="💾 SQLite Kaydet",
            command=self._sqlite_save,
            font=ctk.CTkFont(size=14),
            height=40
        )
        sqlite_save_btn.pack(side="left", padx=(0, 10))

        # SQLite Load button
        sqlite_load_btn = ctk.CTkButton(
            button_frame,
            text="📂 SQLite Yükle",
            command=self._sqlite_load,
            font=ctk.CTkFont(size=14),
            height=40
        )
        sqlite_load_btn.pack(side="left", padx=(0, 10))

        # Clear Log button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Log Temizle",
            command=self._clear_log,
            font=ctk.CTkFont(size=14),
            height=40
        )
        clear_btn.pack(side="left")

        # Log textbox
        log_label = ctk.CTkLabel(bottom_frame, text="Log Ekranı:", font=ctk.CTkFont(weight="bold"))
        log_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.log_textbox = ctk.CTkTextbox(bottom_frame, wrap="word")
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Initial log message
        self._log_message("Diyargezer GUI başlatıldı. Karakter oluşturmaya başlayabilirsiniz!")

    def _start_character_creation(self):
        """Start the character creation wizard"""
        current_tab = self.tabview.get()
        system_key = self.creators.get(current_tab)

        if not system_key:
            messagebox.showerror("Hata", f"Bilinmeyen sistem: {current_tab}")
            return

        # Get character name from the tab
        name_entry = getattr(self, f"{current_tab.lower().replace(' ', '_')}_name")
        initial_name = name_entry.get().strip()

        # Start wizard
        wizard = CharacterCreationWizard(
            self.root,
            system_key,
            self._on_character_created
        )

        # Pre-fill name if entered
        if initial_name:
            wizard.character_data['name'] = initial_name
            if hasattr(wizard, 'name_entry'):
                wizard.name_entry.insert(0, initial_name)

    def _start_level_up(self):
        """Start the level up wizard for an existing character"""
        # Ask user to select a character file
        character_file = filedialog.askopenfilename(
            title="Level Up Edilecek Karakteri Seç",
            filetypes=[("JSON files", "*.json")],
            initialdir="characters"
        )

        if not character_file:
            return

        try:
            # Load character data
            with open(character_file, 'r', encoding='utf-8') as f:
                character_data = json.load(f)

            # Validate character data
            if not isinstance(character_data, dict) or 'name' not in character_data:
                messagebox.showerror("Hata", "Geçersiz karakter dosyası!")
                return

            # Check if character is D&D 5e (only supported for now)
            system = character_data.get('system', '').lower()
            if system not in ['dnd5e', 'dnd']:
                messagebox.showerror("Hata", "Level up şu anda sadece D&D 5e karakterleri için destekleniyor!")
                return

            # Start level up wizard
            wizard = LevelUpWizard(
                self.root,
                character_data,
                self._on_level_up_complete
            )

        except Exception as e:
            messagebox.showerror("Hata", f"Karakter yüklenirken hata oluştu: {e}")

    def _on_level_up_complete(self, updated_character: Dict[str, Any]):
        """Callback when level up is complete"""
        self._log_message(f"✅ {updated_character['name']} başarıyla level up edildi!")
        self._log_message(f"📊 Yeni Seviye: {updated_character.get('level', 1)}")
        self._log_message(f"❤️ Yeni HP: {updated_character.get('hp', updated_character.get('hit_points', 0))}")

        # Multiclass info
        if updated_character.get('is_multiclass'):
            class_levels = updated_character.get('class_levels', {})
            parts = [f"{c} {l}" for c, l in class_levels.items()]
            self._log_message(f"🔀 Multiclass: {' / '.join(parts)}")
            hit_dice = updated_character.get('hit_dice', '')
            if hit_dice:
                self._log_message(f"🎲 Hit Dice: {hit_dice}")

        # Show updated character summary
        current_tab = self.tabview.get()
        self._show_character_summary(updated_character, current_tab)

    def _show_batch_operations(self):
        """Show batch operations dialog"""
        BatchOperationsDialog(self.root)

    def _on_character_created(self, character: Dict[str, Any]):
        """Callback when character creation is complete"""
        self._log_message(f"✅ {character['name']} karakteri başarıyla oluşturuldu!")
        self._log_message(f"📁 Sistem: {character['system']}")
        self._log_message(f"📋 Irk: {character.get('race', 'N/A')}")
        self._log_message(f"⚔️ Sınıf: {character.get('class', 'N/A')}")
        self._log_message(f"📊 Seviye: {character.get('level', 1)}")

        # Update the name field in the tab
        current_tab = self.tabview.get()
        name_entry = getattr(self, f"{current_tab.lower().replace(' ', '_')}_name")
        name_entry.delete(0, 'end')
        name_entry.insert(0, character['name'])

        # Show character summary
        self._show_character_summary(character, current_tab)

    def _show_character_summary(self, character: Dict[str, Any], tab_name: str):
        """Show character summary in the tab"""
        # Get summary widgets
        summary_frame = getattr(self, f"{tab_name.lower().replace(' ', '_')}_summary_frame")
        summary_text = getattr(self, f"{tab_name.lower().replace(' ', '_')}_summary_text")

        # Build summary text
        summary_lines = []
        summary_lines.append(f"🎲 {character['name']} - {character['system'].upper()}")
        summary_lines.append("=" * 50)
        summary_lines.append("")

        # Basic info
        summary_lines.append(f"📋 Irk: {character.get('race', 'N/A')}")

        # Multiclass display
        if character.get('is_multiclass') and character.get('class_levels'):
            class_levels = character['class_levels']
            class_parts = [f"{cls} {lvl}" for cls, lvl in class_levels.items()]
            summary_lines.append(f"⚔️ Sınıf: {' / '.join(class_parts)}")
        else:
            summary_lines.append(f"⚔️ Sınıf: {character.get('class_display', character.get('class', 'N/A'))}")
        summary_lines.append(f"📊 Toplam Seviye: {character.get('level', 1)}")

        # Subclass
        subclass = character.get('subclass', '')
        if subclass:
            summary_lines.append(f"🏛️ Subclass: {subclass}")

        if character['system'] == 'dnd5e':
            summary_lines.append(f"🏛️ Arka Plan: {character.get('background', 'N/A')}")
        elif character['system'] == 'pathfinder1e':
            summary_lines.append(f"🏛️ Archetype: {character.get('archetype', 'N/A')}")

        summary_lines.append("")

        # Abilities
        summary_lines.append("🎯 YETENEK PUANLARI:")
        abilities = character.get('abilities', {})
        for ability, score in abilities.items():
            mod = (score - 10) // 2
            summary_lines.append(f"  {ability}: {score} ({mod:+d})")
        summary_lines.append("")

        # Combat stats
        summary_lines.append("⚔️ SAVAŞ İSTATİSTİKLERİ:")
        summary_lines.append(f"  HP: {character.get('hit_points', 'N/A')}")
        summary_lines.append(f"  AC: {character.get('armor_class', 'N/A')}")
        summary_lines.append(f"  Proficiency Bonus: +{character.get('proficiency_bonus', 2)}")
        init = character.get('initiative', 'N/A')
        if isinstance(init, int):
            summary_lines.append(f"  Initiative: {init:+d}")
        else:
            summary_lines.append(f"  Initiative: {init}")
        summary_lines.append(f"  Speed: {character.get('movement_speed', character.get('speed', 30))} ft")

        # Hit dice (multiclass aware)
        hit_dice = character.get('hit_dice', '')
        if hit_dice:
            summary_lines.append(f"  Hit Dice: {hit_dice}")

        summary_lines.append("")

        # Jump Distance & Carrying Capacity
        jump = character.get('jump_distance', {})
        carrying = character.get('carrying_capacity', 0)
        if jump or carrying:
            summary_lines.append("🏃 FIZIKSEL:")
            if carrying:
                summary_lines.append(f"  Tasima Kapasitesi: {carrying} lbs")
            push = character.get('push_drag_lift', 0)
            if push:
                summary_lines.append(f"  Itme/Cekme/Kaldirma: {push} lbs")
            if jump:
                summary_lines.append(f"  Uzun Atlama (kosarak): {jump.get('long_jump_running', '?')} ft")
                summary_lines.append(f"  Uzun Atlama (durarak): {jump.get('long_jump_standing', '?')} ft")
                summary_lines.append(f"  Yuksek Atlama (kosarak): {jump.get('high_jump_running', '?')} ft")
            summary_lines.append("")

        # Spellcasting overview (D&D 5e için daha okunaklı özet)
        if character.get('system', '').lower() in ['dnd5e', 'dnd']:
            spell_save_dc = character.get('spell_save_dc')
            spell_attack_bonus = character.get('spell_attack_bonus')
            spell_slots = character.get('spell_slots', {}) or {}

            # Sadece gerçekten spellcaster ise göster
            if spell_save_dc is not None or spell_attack_bonus is not None or spell_slots:
                summary_lines.append("🔮 SPELLCASTING:")

                if spell_save_dc is not None:
                    summary_lines.append(f"  Spell Save DC: {spell_save_dc}")
                if spell_attack_bonus is not None:
                    summary_lines.append(f"  Spell Attack Bonus: +{spell_attack_bonus}")

                # Spell slots tablosu
                if spell_slots:
                    # Bazı yerlerde level anahtarları int, bazılarında string olabilir → normalize et
                    normalized_slots = {}
                    for level_key, count in spell_slots.items():
                        try:
                            lvl_int = int(level_key)
                        except (TypeError, ValueError):
                            # "cantrip" gibi özel anahtarları atla; cantrip'ler slot tüketmez
                            continue
                        normalized_slots[lvl_int] = count

                    if normalized_slots:
                        summary_lines.append("  Spell Slots:")
                        for lvl in sorted(normalized_slots.keys()):
                            count = normalized_slots[lvl]
                            if count and count > 0:
                                plural = "slots" if count != 1 else "slot"
                                summary_lines.append(f"    Lv{lvl}: {count} {plural}")

                summary_lines.append("")

        # Spells with Ritual/Concentration/Material info
        if character.get('system', '').lower() in ['dnd5e', 'dnd']:
            try:
                from utils.calculations import is_ritual_spell, is_concentration_spell, extract_material_components
                from pathlib import Path
                from utils.data_loader import load_dnd_data
                dnd_data = load_dnd_data(Path(__file__).parent.parent)
                all_spells = dnd_data.get("spells", {})
            except Exception:
                all_spells = {}

            # Bilinen/hazırlanan spell'leri topla
            known_spells = []
            char_spells = character.get("spells", {})
            if isinstance(char_spells, dict):
                for lvl_key, sp_list in char_spells.items():
                    if isinstance(sp_list, list):
                        known_spells.extend(sp_list)
            elif isinstance(char_spells, list):
                known_spells = char_spells

            prepared_spells = character.get("prepared_spells", [])
            if isinstance(prepared_spells, dict):
                flat = []
                for sp_list in prepared_spells.values():
                    if isinstance(sp_list, list):
                        flat.extend(sp_list)
                prepared_spells = flat

            # Spellbook (Wizard)
            spellbook = character.get('spellbook', [])
            if isinstance(spellbook, dict):
                flat_sb = []
                for sp_list in spellbook.values():
                    if isinstance(sp_list, list):
                        flat_sb.extend(sp_list)
                spellbook = flat_sb

            if spellbook:
                summary_lines.append("📖 SPELLBOOK:")
                for spell in spellbook[:10]:
                    tags = self._get_spell_tags(spell, all_spells)
                    summary_lines.append(f"  • {spell}{tags}")
                if len(spellbook) > 10:
                    summary_lines.append(f"  ... ve {len(spellbook) - 10} büyü daha")
                summary_lines.append("")

            if prepared_spells:
                summary_lines.append("✅ HAZIRLANMIŞ BÜYÜLER:")
                for spell in prepared_spells:
                    tags = self._get_spell_tags(spell, all_spells)
                    summary_lines.append(f"  • {spell}{tags}")
                summary_lines.append("")

            if known_spells and not spellbook:
                summary_lines.append("📜 BİLİNEN BÜYÜLER:")
                for spell in known_spells[:15]:
                    tags = self._get_spell_tags(spell, all_spells)
                    summary_lines.append(f"  • {spell}{tags}")
                if len(known_spells) > 15:
                    summary_lines.append(f"  ... ve {len(known_spells) - 15} büyü daha")
                summary_lines.append("")

            # Active concentration spell tracking
            active_concentration = character.get("active_concentration_spell")
            if active_concentration:
                summary_lines.append(f"🔴 AKTİF KONSANTRASYON: {active_concentration}")
                summary_lines.append("")
        else:
            # Non-D&D systems - simple spellbook display
            spellbook = character.get('spellbook', [])
            if spellbook:
                summary_lines.append("📖 SPELLBOOK:")
                for spell in spellbook[:10]:
                    summary_lines.append(f"  • {spell}")
                if len(spellbook) > 10:
                    summary_lines.append(f"  ... and {len(spellbook) - 10} more spells")
                summary_lines.append("")

        # Saving throws
        saving_throws = character.get('saving_throws', {})
        if saving_throws:
            summary_lines.append("🛡️ SAVING THROWS:")
            for save, mod in saving_throws.items():
                summary_lines.append(f"  {save.title()}: {mod:+d}")
            summary_lines.append("")

        # Skills
        skills = character.get('skills', {})
        if skills:
            summary_lines.append("🎭 SKILLS:")
            for skill, mod in skills.items():
                summary_lines.append(f"  {skill}: {mod:+d}")
            summary_lines.append("")

        # Equipment stats (Encumbrance & Attunement)
        if character.get('system', '').lower() in ['dnd5e', 'dnd']:
            try:
                from utils.calculations import calculate_encumbrance_details, check_attunement_limit
                encumbrance = calculate_encumbrance_details(character)
                enc_status = encumbrance.get("encumbrance_status", "unencumbered")
                enc_text_map = {
                    "unencumbered": "Normal",
                    "at_capacity": "Kapasitede",
                    "encumbered": "Yuklu (-10 ft)",
                    "heavily_encumbered": "Cok Yuklu (-20 ft)"
                }
                total_w = encumbrance.get("total_weight", 0)
                cap = encumbrance.get("base_capacity", 0)
                if total_w > 0 or any(character.get(k, []) for k in ["equipment", "starting_equipment"]):
                    summary_lines.append("⚖️ ENCUMBRANCE:")
                    summary_lines.append(f"  Agirlik: {total_w:.1f} / {cap} lbs")
                    summary_lines.append(f"  Durum: {enc_text_map.get(enc_status, enc_status)}")
                    summary_lines.append("")

                attunement = check_attunement_limit(character)
                if attunement["current_attuned"] > 0:
                    summary_lines.append(f"✨ ATTUNEMENT: {attunement['current_attuned']}/{attunement['max_attuned']}")
                    for ai in attunement["attuned_items"]:
                        summary_lines.append(f"  • {ai}")
                    summary_lines.append("")
            except Exception:
                pass

        # Active Conditions
        active_conditions = character.get('active_conditions', [])
        if active_conditions:
            summary_lines.append("🎭 AKTIF DURUM EFEKTLERI:")
            try:
                from utils.conditions import get_active_conditions
                for cond in get_active_conditions(character):
                    icon = cond.get("icon", "")
                    display = cond.get("display_name", cond.get("name", ""))
                    level = cond.get("level")
                    level_str = f" (Lv{level})" if level else ""
                    effects = cond.get("effects", [])
                    summary_lines.append(f"  {icon} {display}{level_str}")
                    if effects:
                        summary_lines.append(f"    → {effects[0]}")
            except ImportError:
                for cond in active_conditions:
                    summary_lines.append(f"  • {cond.get('name', '?')}")
            summary_lines.append("")

        # Starting Equipment
        starting_equipment = character.get('starting_equipment', [])
        if starting_equipment:
            summary_lines.append("🎒 STARTING EQUIPMENT:")
            for item in starting_equipment:
                # Equipment bilgilerini parse et (eğer dict ise)
                if isinstance(item, dict):
                    item_name = item.get('name', str(item))
                    item_desc = []
                    if item.get('cost'):
                        item_desc.append(f"({item['cost']})")
                    if item.get('weight'):
                        item_desc.append(f"{item['weight']} lb")
                    desc_str = " ".join(item_desc)
                    summary_lines.append(f"  • {item_name} {desc_str}".strip())
                else:
                    summary_lines.append(f"  • {item}")
            summary_lines.append("")

        # Update summary text
        summary_text.delete("0.0", "end")
        summary_text.insert("0.0", "\n".join(summary_lines))

        # Show the summary frame
        summary_frame.pack(fill="x", padx=20, pady=(0, 10))

    def _get_spell_tags(self, spell_name: str, all_spells: Dict[str, Any]) -> str:
        """Spell icin [Ritual], [Concentration], [M: ...] etiketlerini dondur"""
        try:
            from utils.calculations import is_ritual_spell, is_concentration_spell, extract_material_components
            spell_data = all_spells.get(spell_name, {})
            tags = []
            if is_ritual_spell(spell_name, spell_data):
                tags.append("[R]")
            if is_concentration_spell(spell_name, spell_data):
                tags.append("[C]")
            material = extract_material_components(spell_data)
            if material and material.get("cost"):
                tags.append(f"[M:{material['cost']}gp]")
            elif material:
                tags.append("[M]")
            if tags:
                return " " + " ".join(tags)
        except Exception:
            pass
        return ""

    def _create_character(self):
        """Legacy method - now uses wizard"""
        self._start_character_creation()

    def _create_dnd_character(self):
        """Legacy method"""
        pass

    def _create_pathfinder_character(self):
        """Legacy method"""
        pass

    def _create_vtm_character(self):
        """Legacy method"""
        pass

    def _create_mm_character(self):
        """Legacy method"""
        pass

    def _export_pdf(self):
        """Export character to PDF with template selection"""
        # Get current character name
        current_tab = self.tabview.get()
        name_entry = getattr(self, f"{current_tab.lower().replace(' ', '_')}_name")
        character_name = name_entry.get().strip()

        if not character_name:
            messagebox.showwarning("Uyarı", "Önce bir karakter oluşturun veya adını girin!")
            return

        # Try to load the character
        try:
            system_key = self.creators.get(current_tab)
            creator = CharacterFactory.create_creator(system_key)
            filename = f"{character_name.lower().replace(' ', '_')}_{system_key}"
            character = creator.load_character(filename)

            # Show template selection dialog
            self._show_pdf_template_dialog(character)

        except Exception as e:
            messagebox.showerror("Hata", f"Karakter bulunamadı: {e}")
            self._log_message(f"⚠️ PDF oluşturulamadı: {e}")

    def _show_pdf_template_dialog(self, character: Dict[str, Any]):
        """Show PDF template selection dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("PDF Template Seçimi")
        dialog.geometry("400x300")
        dialog.resizable(False, False)

        # Make it modal
        dialog.transient(self.root)
        dialog.grab_set()

        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text="PDF Template Seçin",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(20, 10))

        # Template selection
        template_var = ctk.StringVar(value="standard")

        templates = [
            ("standard", "Standart - Dengeli detay seviyesi"),
            ("detailed", "Detaylı - Daha fazla bilgi ve büyük font"),
            ("compact", "Kompakt - Küçük font, az boşluk"),
            ("minimal", "Minimal - Sadece temel bilgiler")
        ]

        template_frame = ctk.CTkFrame(dialog)
        template_frame.pack(fill="both", expand=True, padx=20, pady=10)

        for template_id, description in templates:
            rb = ctk.CTkRadioButton(
                template_frame,
                text=f"{template_id.title()}: {description}",
                variable=template_var,
                value=template_id,
                wraplength=300
            )
            rb.pack(anchor="w", pady=5, padx=10)

        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 20))

        def on_export():
            selected_template = template_var.get()
            dialog.destroy()
            self._generate_pdf(character, selected_template)

        def on_cancel():
            dialog.destroy()

        cancel_btn = ctk.CTkButton(button_frame, text="İptal", command=on_cancel)
        cancel_btn.pack(side="right", padx=(0, 10))

        export_btn = ctk.CTkButton(
            button_frame,
            text="PDF Oluştur",
            command=on_export,
            font=ctk.CTkFont(weight="bold")
        )
        export_btn.pack(side="right")

    def _generate_pdf(self, character: Dict[str, Any], template: str = "standard"):
        """Generate PDF for character with selected template"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="PDF olarak kaydet"
        )

        if not filename:
            return

        try:
            # Use the updated export function with template parameter
            from utils.export_pdf import export_dnd_character_pdf
            from pathlib import Path

            export_dnd_character_pdf(character, Path(filename), template=template)
            messagebox.showinfo("Başarılı", f"PDF başarıyla oluşturuldu!\n{filename}")
            self._log_message(f"📄 {character['name']} için {template} template ile PDF oluşturuldu!")

        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturma hatası: {e}")
            self._log_message(f"⚠️ PDF oluşturma hatası: {e}")

    # ==================================================================
    # SQLite KAYDETME / YUKLEME
    # ==================================================================
    def _sqlite_save(self):
        """Aktif karakteri SQLite veritabanına kaydet"""
        current_tab = self.tabview.get()
        name_entry = getattr(self, f"{current_tab.lower().replace(' ', '_')}_name", None)
        character_name = name_entry.get().strip() if name_entry else ""

        if not character_name:
            character_file = filedialog.askopenfilename(
                title="SQLite'a Kaydedilecek Karakteri Seçin",
                filetypes=[("JSON files", "*.json")],
                initialdir="characters"
            )
            if not character_file:
                return
            try:
                with open(character_file, 'r', encoding='utf-8') as f:
                    character = json.load(f)
            except Exception as e:
                messagebox.showerror("Hata", f"Karakter yüklenemedi: {e}")
                return
        else:
            try:
                system_key = self.creators.get(current_tab)
                creator = CharacterFactory.create_creator(system_key)
                filename = f"{character_name.lower().replace(' ', '_')}_{system_key}"
                character = creator.load_character(filename)
            except Exception:
                messagebox.showwarning("Uyarı", "Önce bir karakter oluşturun!")
                return

        try:
            from utils.storage import init_db, save_character as sqlite_save, CharacterRecord

            db_path = Path(__file__).parent.parent / "characters" / "diyargezer.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            init_db(db_path)

            record = CharacterRecord(
                id=None,
                system=character.get("system", "unknown"),
                name=character.get("name", "unnamed"),
                data=character
            )
            record_id = sqlite_save(db_path, record)
            messagebox.showinfo("Başarılı",
                                f"'{character.get('name')}' SQLite veritabanına kaydedildi!\nKayıt ID: {record_id}")
            self._log_message(f"💾 {character.get('name')} SQLite'a kaydedildi (ID: {record_id})")
        except Exception as e:
            messagebox.showerror("Hata", f"SQLite kayıt hatası: {e}")
            self._log_message(f"⚠️ SQLite kayıt hatası: {e}")

    def _sqlite_load(self):
        """SQLite veritabanından karakter yükle"""
        try:
            from utils.storage import init_db, list_characters, load_character as sqlite_load

            db_path = Path(__file__).parent.parent / "characters" / "diyargezer.db"
            if not db_path.exists():
                messagebox.showinfo("Bilgi", "SQLite veritabanı bulunamadı.\nÖnce bir karakter kaydedin.")
                return

            init_db(db_path)
            records = list_characters(db_path)

            if not records:
                messagebox.showinfo("Bilgi", "Veritabanında kayıtlı karakter yok.")
                return

            # Karakter secim dialog'u
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("SQLite - Karakter Yükle")
            dialog.geometry("500x450")
            dialog.resizable(True, True)
            dialog.transient(self.root)
            dialog.grab_set()

            ctk.CTkLabel(dialog, text="💾 SQLite Veritabanından Karakter Yükle",
                         font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))

            # Karakter listesi
            list_frame = ctk.CTkScrollableFrame(dialog)
            list_frame.pack(fill="both", expand=True, padx=15, pady=5)

            selected_id = ctk.IntVar(value=0)

            for rec in records:
                system = rec.system
                name = rec.name
                rb = ctk.CTkRadioButton(
                    list_frame,
                    text=f"[ID:{rec.id}] {name} ({system})",
                    variable=selected_id,
                    value=rec.id,
                    font=ctk.CTkFont(size=12)
                )
                rb.pack(anchor="w", padx=10, pady=3)

            def on_load():
                rec_id = selected_id.get()
                if rec_id == 0:
                    messagebox.showwarning("Uyarı", "Bir karakter seçin!")
                    return
                record = sqlite_load(db_path, rec_id)
                if record:
                    character = record.data
                    # JSON olarak da kaydet
                    safe_name = record.name.lower().replace(' ', '_')
                    sys_key = record.system.lower().replace(' ', '_')
                    json_path = Path(__file__).parent.parent / "characters" / f"{safe_name}_{sys_key}.json"
                    json_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(character, f, ensure_ascii=False, indent=2)

                    self._log_message(f"📂 {record.name} SQLite'dan yüklendi (ID: {rec_id})")
                    messagebox.showinfo("Başarılı",
                                        f"'{record.name}' yüklendi ve JSON olarak da kaydedildi.")
                    dialog.destroy()
                else:
                    messagebox.showerror("Hata", "Karakter bulunamadı!")

            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(fill="x", padx=15, pady=(5, 15))

            ctk.CTkButton(btn_frame, text="📂 Yükle", command=on_load,
                           font=ctk.CTkFont(weight="bold"), height=35).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="İptal", command=dialog.destroy,
                           height=35).pack(side="right", padx=5)

        except Exception as e:
            messagebox.showerror("Hata", f"SQLite yükleme hatası: {e}")
            self._log_message(f"⚠️ SQLite yükleme hatası: {e}")

    def _clear_log(self):
        """Clear the log textbox"""
        self.log_textbox.delete("0.0", "end")

    def _log_message(self, message: str):
        """Add message to log"""
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")

    def _load_system_data(self):
        """Load data for dropdown menus"""
        try:
            self._log_message("✅ Sistem verileri hazır!")
        except Exception as e:
            self._log_message(f"⚠️ Sistem verisi yüklenirken hata: {e}")

    def run(self):
        """Run the GUI"""
        self.root.mainloop()


class LevelUpWizard:
    """Level up wizard for existing characters"""

    def __init__(self, parent, character_data: dict, on_complete_callback):
        self.parent = parent
        self.character_data = character_data.copy()
        self.on_complete = on_complete_callback
        self.current_step = 0
        self.system_name = character_data.get("system", "dnd5e").lower()

        # Load system data
        self._load_system_data()

        # Create wizard window
        self.wizard_window = ctk.CTkToplevel(parent)
        self.wizard_window.title(f"Level Up - {character_data.get('name', 'Unknown')}")
        self.wizard_window.geometry("800x600")
        self.wizard_window.resizable(True, True)

        # Make it modal
        self.wizard_window.transient(parent)
        self.wizard_window.grab_set()

        # Initialize level up steps
        self._init_levelup_steps()

        # Create wizard UI
        self._create_wizard_ui()

        # Show first step
        self._show_step(0)

    def _load_system_data(self):
        """Load system-specific data"""
        try:
            if self.system_name == "dnd5e":
                data_file = Path(__file__).parent.parent / "data" / "dnd_data.json"
                with open(data_file, 'r', encoding='utf-8') as f:
                    self.system_data = json.load(f)
            else:
                self.system_data = {}
        except Exception as e:
            print(f"Error loading system data: {e}")
            self.system_data = {}

    def _init_levelup_steps(self):
        """Initialize level up steps"""
        current_level = self.character_data.get("level", 1)

        # Multiclass state
        self.is_multiclass_levelup = False
        self.multiclass_target_class = None
        self.multiclass_new_proficiencies = {}

        self.steps = [
            {"title": "Adım 1: Yeni Seviye", "method": self._step_level_selection},
            {"title": "Adım 2: Multiclass Sınıf Seçimi", "method": self._step_multiclass_class_selection},
            {"title": "Adım 3: Subclass Seçimi", "method": self._step_subclass_selection},
            {"title": "Adım 4: HP Artışı", "method": self._step_hp_increase},
            {"title": "Adım 5: Yetenek Artışı", "method": self._step_ability_increase},
            {"title": "Adım 6: Feat Seçimi", "method": self._step_feat_selection},
            {"title": "Adım 7: Sınıf Özellikleri", "method": self._step_class_features},
            {"title": "Adım 8: Büyü Seçimi", "method": self._step_spell_selection},
            {"title": "Adım 9: Onay ve Güncelle", "method": self._step_finalize_levelup}
        ]

    def _create_wizard_ui(self):
        """Create the wizard UI"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.wizard_window)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Level Up: {self.character_data.get('name', 'Unknown')}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400)
        self.progress_bar.pack(pady=(0, 20))
        self.progress_bar.set(0)

        # Step title
        self.step_title_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.step_title_label.pack(pady=(0, 10))

        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Navigation buttons
        nav_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(20, 0))

        self.back_button = ctk.CTkButton(
            nav_frame,
            text="← Geri",
            command=self._go_back,
            state="disabled"
        )
        self.back_button.pack(side="left", padx=(0, 10))

        self.next_button = ctk.CTkButton(
            nav_frame,
            text="İleri →",
            command=self._go_next
        )
        self.next_button.pack(side="right")

        self.cancel_button = ctk.CTkButton(
            nav_frame,
            text="İptal",
            command=self._cancel,
            fg_color="transparent",
            border_width=2
        )
        self.cancel_button.pack(side="right", padx=(0, 10))

    def _show_step(self, step_index: int):
        """Show the specified step"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if step_index >= len(self.steps):
            self._finalize_levelup()
            return

        step = self.steps[step_index]
        self.step_title_label.configure(text=step["title"])

        # Update progress bar
        progress = (step_index + 1) / len(self.steps)
        self.progress_bar.set(progress)

        # Update navigation buttons
        self.back_button.configure(state="normal" if step_index > 0 else "disabled")
        self.next_button.configure(text="İleri →" if step_index < len(self.steps) - 1 else "Tamamla")

        # Execute step method
        step["method"]()

    def _go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._show_step(self.current_step)

    def _go_next(self):
        """Go to next step"""
        try:
            # Validate and collect data from current step
            if not self._validate_current_step():
                return

            if self.current_step < len(self.steps) - 1:
                self.current_step += 1
                self._show_step(self.current_step)
            else:
                self._finalize_levelup()
        except Exception as e:
            messagebox.showerror("Hata", f"Adım geçişinde hata: {e}")

    def _validate_current_step(self):
        """Validate current step and collect data"""
        step_method = self.steps[self.current_step]["method"].__name__

        if step_method == "_step_level_selection":
            # Validate level input
            try:
                level_text = self.level_spinbox.get().strip()
                new_level = int(level_text)
                current_level = self.character_data.get("level", 1)

                if new_level <= current_level:
                    messagebox.showerror("Hata", f"Yeni seviye mevcut seviyeden ({current_level}) yüksek olmalı!")
                    return False

                if new_level > 20:
                    messagebox.showerror("Hata", "D&D 5e'de maksimum seviye 20'dir!")
                    return False

                self.selected_new_level = new_level

                # Capture multiclass checkbox state
                self.is_multiclass_levelup = getattr(self, 'multiclass_var', ctk.BooleanVar(value=False)).get()
                return True

            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir seviye numarası girin!")
                return False

        elif step_method == "_step_multiclass_class_selection":
            # Validate multiclass class selection
            if not self.is_multiclass_levelup:
                return True  # Skip validation if not multiclassing

            selected_class = getattr(self, 'mc_class_var', ctk.StringVar(value="")).get()
            if not selected_class:
                messagebox.showerror("Hata", "Lütfen bir sınıf seçin!")
                return False

            # Verify prerequisites one more time
            try:
                from utils.multiclass import check_multiclass_prerequisites
                can_mc, reasons = check_multiclass_prerequisites(self.character_data, selected_class)
                if not can_mc:
                    messagebox.showerror("Hata", f"Prerequisite'ler karşılanmıyor:\n" + "\n".join(reasons))
                    return False
            except ImportError:
                pass

            self.multiclass_target_class = selected_class

            # Store new class proficiencies
            try:
                from utils.multiclass import get_multiclass_proficiencies
                self.multiclass_new_proficiencies = get_multiclass_proficiencies(selected_class)
            except ImportError:
                self.multiclass_new_proficiencies = {}

            return True

        elif step_method == "_step_subclass_selection":
            # Collect subclass selection if applicable
            selected_subclass = getattr(self, 'subclass_var', ctk.StringVar(value="")).get()
            self.selected_subclass = selected_subclass if selected_subclass else None
            return True

        elif step_method == "_step_hp_increase":
            # Collect HP increase
            try:
                hp_text = self.hp_spinbox.get().strip()
                hp_increase = int(hp_text)
                if hp_increase < 0:
                    messagebox.showerror("Hata", "HP artışı negatif olamaz!")
                    return False
                self.hp_increase_amount = hp_increase
                return True
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir HP değeri girin!")
                return False

        elif step_method == "_step_ability_increase":
            # Collect ASI selections
            selected_abilities = []
            for ability, var in self.asi_selections.items():
                if var.get():
                    selected_abilities.append(ability)

            if len(selected_abilities) > 2:
                messagebox.showerror("Hata", "En fazla 2 yetenek seçebilirsiniz!")
                return False

            # Convert to changes dict
            self.asi_changes = {}
            for ability in selected_abilities:
                self.asi_changes[ability] = 1

            # If only one selected, give +2 to that ability
            if len(selected_abilities) == 1:
                self.asi_changes[selected_abilities[0]] = 2

            self.asi_taken = len(selected_abilities) > 0
            return True

        elif step_method == "_step_feat_selection":
            # Collect selected feat
            selected_feat = self.selected_feat.get()
            if selected_feat:
                self.selected_feat_name = selected_feat
            else:
                self.selected_feat_name = None
            return True

        elif step_method == "_step_spell_selection":
            # Spells are collected via checkboxes
            return True

        return True

    def _cancel(self):
        """Cancel the level up process"""
        if messagebox.askyesno("İptal", "Level up işlemini iptal etmek istediğinizden emin misiniz?"):
            self.wizard_window.destroy()

    def _step_level_selection(self):
        """Step 1: Select new level with multiclass option"""
        current_level = self.character_data.get("level", 1)
        current_class = self.character_data.get("class", "Unknown")

        # Info label
        class_display = self.character_data.get("class_display", current_class)
        info_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Mevcut Seviye: {current_level}  |  Sınıf: {class_display}\nYeni seviyeyi seçin:",
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(pady=(20, 10))

        # Level selection
        self.new_level_var = ctk.IntVar(value=current_level + 1)

        level_frame = ctk.CTkFrame(self.content_frame)
        level_frame.pack(fill="x", padx=20, pady=10)

        level_label = ctk.CTkLabel(level_frame, text="Yeni Toplam Seviye:")
        level_label.pack(side="left", padx=(0, 10))

        level_spinbox = ctk.CTkEntry(level_frame, width=100)
        level_spinbox.pack(side="left")
        level_spinbox.insert(0, str(current_level + 1))

        # Store reference for validation
        self.level_spinbox = level_spinbox

        # Multiclass checkbox
        mc_separator = ctk.CTkLabel(
            self.content_frame,
            text="─" * 60,
            font=ctk.CTkFont(size=10),
            text_color="gray50"
        )
        mc_separator.pack(pady=(15, 5))

        self.multiclass_var = ctk.BooleanVar(value=False)
        mc_checkbox = ctk.CTkCheckBox(
            self.content_frame,
            text="🔀 Multiclass: Bu seviyeyi farklı bir sınıfta al",
            variable=self.multiclass_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._update_multiclass_info
        )
        mc_checkbox.pack(pady=(5, 10), padx=20, anchor="w")

        # Multiclass info frame (prereqs vs.)
        self.mc_info_frame = ctk.CTkFrame(self.content_frame)
        self.mc_info_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.mc_info_label = ctk.CTkLabel(
            self.mc_info_frame,
            text="Multiclass aktif edildiğinde, bir sonraki adımda yeni sınıf seçeceksiniz.\n"
                 "D&D 5e kurallarına göre her iki sınıfın da ability prerequisite'lerini\n"
                 "karşılamanız gerekmektedir.",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            justify="left"
        )
        self.mc_info_label.pack(pady=8, padx=10, anchor="w")

        # Already multiclass info
        if self.character_data.get("is_multiclass"):
            class_levels = self.character_data.get("class_levels", {})
            mc_existing = ctk.CTkLabel(
                self.content_frame,
                text=f"⚡ Bu karakter zaten multiclass: {' / '.join(f'{c} {l}' for c, l in class_levels.items())}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#FFD700"
            )
            mc_existing.pack(pady=(5, 10), padx=20, anchor="w")

    def _update_multiclass_info(self):
        """Update multiclass info display when checkbox is toggled"""
        if self.multiclass_var.get():
            self.mc_info_label.configure(
                text="✅ Multiclass aktif! İleri'ye tıklayarak sınıf seçimine geçin.\n"
                     "Prerequisite'ler kontrol edilecek ve uygun sınıflar gösterilecek.",
                text_color="#4CAF50"
            )
        else:
            self.mc_info_label.configure(
                text="Multiclass aktif edildiğinde, bir sonraki adımda yeni sınıf seçeceksiniz.\n"
                     "D&D 5e kurallarına göre her iki sınıfın da ability prerequisite'lerini\n"
                     "karşılamanız gerekmektedir.",
                text_color="gray60"
            )

    def _step_multiclass_class_selection(self):
        """Step 2: Multiclass class selection (only shown if multiclass is selected)"""
        if not getattr(self, 'is_multiclass_levelup', False):
            # Skip this step if not multiclassing
            info_label = ctk.CTkLabel(
                self.content_frame,
                text="Multiclass seçilmedi. Mevcut sınıfta devam ediliyor.\nDevam etmek için İleri'ye tıklayın.",
                font=ctk.CTkFont(size=14)
            )
            info_label.pack(pady=(50, 20))
            return

        try:
            from utils.multiclass import get_available_multiclass_options, check_multiclass_prerequisites
        except ImportError:
            info_label = ctk.CTkLabel(
                self.content_frame,
                text="Multiclass modülü yüklenemedi!",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            info_label.pack(pady=(50, 20))
            return

        current_class = self.character_data.get("class", "")
        info_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Mevcut sınıf: {current_class}\nYeni sınıfınızı seçin:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_label.pack(pady=(10, 10))

        # Get available multiclass options
        options = get_available_multiclass_options(self.character_data)

        # Also allow continuing existing multiclass classes
        existing_class_levels = self.character_data.get("class_levels", {})

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame, height=350)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.mc_class_var = ctk.StringVar(value="")

        for option in options:
            cls = option["class"]
            can_mc = option["can_multiclass"]
            reasons = option["reasons"]
            prereqs = option["prerequisites"]
            hit_die = option["hit_die"]
            profs = option["proficiencies"]
            is_caster = option["is_spellcaster"]

            # Create a frame for each class option
            cls_frame = ctk.CTkFrame(scroll_frame, border_width=1)
            cls_frame.pack(fill="x", pady=3, padx=5)

            # Top row: Radio button + class name + hit die
            top_row = ctk.CTkFrame(cls_frame, fg_color="transparent")
            top_row.pack(fill="x", padx=5, pady=(5, 0))

            # Existing multiclass level info
            existing_lvl = existing_class_levels.get(cls, 0)
            level_text = f" (mevcut: Lvl {existing_lvl})" if existing_lvl > 0 else ""
            caster_icon = " 🔮" if is_caster else ""

            state = "normal" if can_mc else "disabled"
            radio = ctk.CTkRadioButton(
                top_row,
                text=f"{cls} ({hit_die}){caster_icon}{level_text}",
                variable=self.mc_class_var,
                value=cls,
                state=state,
                font=ctk.CTkFont(size=13, weight="bold" if can_mc else "normal")
            )
            radio.pack(side="left")

            # Status indicator
            if can_mc:
                status_label = ctk.CTkLabel(
                    top_row,
                    text="✅ Uygun",
                    font=ctk.CTkFont(size=11),
                    text_color="#4CAF50"
                )
            else:
                status_label = ctk.CTkLabel(
                    top_row,
                    text="❌ Uygun Değil",
                    font=ctk.CTkFont(size=11),
                    text_color="#F44336"
                )
            status_label.pack(side="right", padx=5)

            # Details row
            details = []
            prereq_strs = [f"{ab} >= {val}" for ab, val in prereqs.items()]
            if prereq_strs:
                details.append(f"Önkoşul: {', '.join(prereq_strs)}")

            armor_profs = profs.get("armor", [])
            weapon_profs = profs.get("weapons", [])
            if armor_profs or weapon_profs:
                prof_parts = []
                if armor_profs:
                    prof_parts.append(f"Zırh: {', '.join(armor_profs)}")
                if weapon_profs:
                    prof_parts.append(f"Silah: {', '.join(weapon_profs)}")
                details.append(f"Yeni Proficiency: {' | '.join(prof_parts)}")

            if not can_mc and reasons:
                details.append(f"⚠️ {'; '.join(reasons)}")

            if details:
                detail_label = ctk.CTkLabel(
                    cls_frame,
                    text="\n".join(details),
                    font=ctk.CTkFont(size=10),
                    text_color="gray60" if can_mc else "#FF9800",
                    justify="left",
                    wraplength=600
                )
                detail_label.pack(anchor="w", padx=15, pady=(0, 5))

    def _step_subclass_selection(self):
        """Step 3: Subclass selection (shown at appropriate level)"""
        try:
            from utils.subclass_data import (
                get_subclass_level, get_subclass_feature_name,
                get_subclass_options, needs_subclass_selection
            )
        except ImportError:
            info_label = ctk.CTkLabel(
                self.content_frame,
                text="Subclass modülü yüklenemedi.\nDevam etmek için İleri'ye tıklayın.",
                font=ctk.CTkFont(size=14)
            )
            info_label.pack(pady=(50, 20))
            return

        char_class = self.character_data.get("class", "")
        new_level = getattr(self, 'selected_new_level', self.character_data.get("level", 1) + 1)
        current_level = self.character_data.get("level", 1)
        existing_subclass = self.character_data.get("subclass", "")

        # Multiclass durumunda: target class'a gore subclass kontrol et
        if self.is_multiclass_levelup and self.multiclass_target_class:
            check_class = self.multiclass_target_class
            class_levels = self.character_data.get("class_levels", {})
            check_level = class_levels.get(check_class, 0) + 1
            # Multiclass'ta subclass secimi o sinifin kendi seviyesine gore
            required_level = get_subclass_level(check_class)
            existing_subclass = self.character_data.get("subclasses", {}).get(check_class, "")
            needs_selection = check_level == required_level and not existing_subclass
        else:
            check_class = char_class
            required_level = get_subclass_level(char_class)
            # Karakter bu seviyeye mi cikiyor?
            needs_selection = (
                new_level >= required_level
                and current_level < required_level
                and not existing_subclass
            )

        if not needs_selection:
            if existing_subclass:
                info_text = f"Mevcut subclass: {existing_subclass}\nDevam etmek için İleri'ye tıklayın."
            else:
                feature_name = get_subclass_feature_name(check_class)
                info_text = (
                    f"{check_class} sınıfı için {feature_name} seçimi seviye {required_level}'de yapılır.\n"
                    f"Bu adımda seçim gerekmiyor.\nDevam etmek için İleri'ye tıklayın."
                )
            info_label = ctk.CTkLabel(
                self.content_frame,
                text=info_text,
                font=ctk.CTkFont(size=14)
            )
            info_label.pack(pady=(50, 20))
            return

        # Subclass secimi gerekiyor!
        feature_name = get_subclass_feature_name(check_class)
        options = get_subclass_options(check_class)

        title_label = ctk.CTkLabel(
            self.content_frame,
            text=f"🏛️ {check_class}: {feature_name} Seçimi",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        subtitle = ctk.CTkLabel(
            self.content_frame,
            text=f"Seviye {required_level}'e ulaştınız! Alt sınıfınızı seçin:",
            font=ctk.CTkFont(size=13),
            text_color="gray60"
        )
        subtitle.pack(pady=(0, 10))

        if not options:
            no_data = ctk.CTkLabel(
                self.content_frame,
                text="Bu sınıf için subclass verisi bulunamadı.\nDevam etmek için İleri'ye tıklayın.",
                font=ctk.CTkFont(size=13)
            )
            no_data.pack(pady=20)
            return

        # Scrollable frame for options
        scroll_frame = ctk.CTkScrollableFrame(self.content_frame, height=350)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.subclass_var = ctk.StringVar(value="")

        for opt in options:
            opt_name = opt["name"]
            opt_desc = opt.get("description", "")

            opt_frame = ctk.CTkFrame(scroll_frame, border_width=1)
            opt_frame.pack(fill="x", pady=4, padx=5)

            radio = ctk.CTkRadioButton(
                opt_frame,
                text=opt_name,
                variable=self.subclass_var,
                value=opt_name,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            radio.pack(anchor="w", padx=10, pady=(8, 2))

            if opt_desc:
                desc_label = ctk.CTkLabel(
                    opt_frame,
                    text=opt_desc,
                    font=ctk.CTkFont(size=11),
                    text_color="gray60",
                    justify="left",
                    wraplength=600
                )
                desc_label.pack(anchor="w", padx=30, pady=(0, 8))

    def _step_hp_increase(self):
        """Step 4: HP increase calculation (multiclass aware)"""
        current_level = self.character_data.get("level", 1)
        new_level = getattr(self, 'selected_new_level', current_level + 1)

        # Multiclass: use target class's hit die
        if self.is_multiclass_levelup and self.multiclass_target_class:
            level_class = self.multiclass_target_class
            try:
                from utils.multiclass import CLASS_HIT_DICE
                hit_die = CLASS_HIT_DICE.get(level_class, 8)
            except ImportError:
                hit_die = self.system_data.get("classes", {}).get(level_class, {}).get("hit_die", 8)
        else:
            level_class = self.character_data.get("class", "")
            hit_die = self.system_data.get("classes", {}).get(level_class, {}).get("hit_die", 8)

        avg_hp = (hit_die // 2) + 1

        info_text = f"Seviye {current_level} → {new_level}\n"
        if self.is_multiclass_levelup:
            info_text += f"🔀 Multiclass: Yeni sınıf {self.multiclass_target_class} (Hit Die: d{hit_die})\n"
        else:
            info_text += f"Sınıf: {level_class} (Hit Die: d{hit_die})\n"
        info_text += f"Ortalama HP artışı: {avg_hp} + CON modifier\n\n"
        info_text += "Bu seviyede kazandığınız HP miktarını girin:"

        info_label = ctk.CTkLabel(
            self.content_frame,
            text=info_text,
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=(20, 10))

        # CON modifier info
        con_score = self.character_data.get("abilities", {}).get("Constitution",
                        self.character_data.get("abilities", {}).get("scores", {}).get("constitution", 10))
        con_mod = (con_score - 10) // 2
        con_info = ctk.CTkLabel(
            self.content_frame,
            text=f"Constitution: {con_score} (modifier: {con_mod:+d})  →  Toplam tavsiye: {avg_hp + con_mod}",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        con_info.pack(pady=(0, 10))

        # HP input
        hp_frame = ctk.CTkFrame(self.content_frame)
        hp_frame.pack(fill="x", padx=20, pady=10)

        hp_label = ctk.CTkLabel(hp_frame, text="HP Artışı:")
        hp_label.pack(side="left", padx=(0, 10))

        recommended_hp = avg_hp + con_mod
        self.hp_increase_var = ctk.IntVar(value=recommended_hp)
        hp_spinbox = ctk.CTkEntry(hp_frame, width=100)
        hp_spinbox.pack(side="left")
        hp_spinbox.insert(0, str(recommended_hp))

        self.hp_spinbox = hp_spinbox

        # Multiclass proficiency info
        if self.is_multiclass_levelup and self.multiclass_new_proficiencies:
            class_levels = self.character_data.get("class_levels", {})
            target_level = class_levels.get(self.multiclass_target_class, 0) + 1
            if target_level == 1:
                prof_frame = ctk.CTkFrame(self.content_frame)
                prof_frame.pack(fill="x", padx=20, pady=(15, 5))

                prof_title = ctk.CTkLabel(
                    prof_frame,
                    text=f"🛡️ {self.multiclass_target_class} Multiclass Proficiency'leri:",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                prof_title.pack(anchor="w", padx=10, pady=(5, 2))

                for ptype, items in self.multiclass_new_proficiencies.items():
                    if items:
                        items_text = ", ".join(items)
                        pl = ctk.CTkLabel(
                            prof_frame,
                            text=f"  {ptype.title()}: {items_text}",
                            font=ctk.CTkFont(size=11),
                            text_color="gray60"
                        )
                        pl.pack(anchor="w", padx=15, pady=1)

    def _step_ability_increase(self):
        """Step 3: Ability score increases"""
        new_level = getattr(self, 'selected_new_level', self.character_data.get("level", 1) + 1)

        # Determine if ASI is available
        asi_available = new_level in [4, 8, 12, 16, 19]

        if not asi_available:
            info_label = ctk.CTkLabel(
                self.content_frame,
                text="Bu seviyede Ability Score Increase (ASI) mevcut değil.\nDevam etmek için İleri'ye tıklayın.",
                font=ctk.CTkFont(size=14)
            )
            info_label.pack(pady=(50, 20))
            return

        info_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Seviye {new_level}: Ability Score Increase mevcut!\n\nİki yeteneği +1 artırabilir veya bir yeteneği +2 artırabilirsiniz.",
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(pady=(20, 10))

        # Ability selection frame
        ability_frame = ctk.CTkFrame(self.content_frame)
        ability_frame.pack(fill="x", padx=20, pady=20)

        # Current abilities
        current_abilities = self.character_data.get("abilities", {}).get("scores", {})

        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

        self.asi_selections = {}

        for ability in abilities:
            current_score = current_abilities.get(ability.lower(), 10)

            ability_row = ctk.CTkFrame(ability_frame)
            ability_row.pack(fill="x", pady=2)

            name_label = ctk.CTkLabel(ability_row, text=f"{ability}:", width=120)
            name_label.pack(side="left")

            current_label = ctk.CTkLabel(ability_row, text=f"Mevcut: {current_score}", width=80)
            current_label.pack(side="left")

            # Checkbox for +1 increase
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(ability_row, text="+1", variable=var, width=50)
            checkbox.pack(side="right", padx=(0, 10))

            self.asi_selections[ability.lower()] = var

    def _step_feat_selection(self):
        """Step 4: Feat selection"""
        new_level = getattr(self, 'selected_new_level', self.character_data.get("level", 1) + 1)

        # Check if feat is available (level 1, or ASI not taken at certain levels)
        feat_available = new_level == 1 or (new_level in [4, 8, 12, 16, 19] and not getattr(self, 'asi_taken', False))

        if not feat_available:
            info_label = ctk.CTkLabel(
                self.content_frame,
                text="Bu seviyede feat seçimi mevcut değil.\nDevam etmek için İleri'ye tıklayın.",
                font=ctk.CTkFont(size=14)
            )
            info_label.pack(pady=(50, 20))
            return

        info_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Seviye {new_level}: Feat seçimi mevcut!\n\nBir feat seçin:",
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(pady=(20, 10))

        # Feat selection
        feat_frame = ctk.CTkScrollableFrame(self.content_frame)
        feat_frame.pack(fill="both", expand=True, padx=20, pady=10)

        feats = self.system_data.get("equipment", {}).get("feats", {})
        feat_names = list(feats.keys())

        self.selected_feat = ctk.StringVar()

        for feat_name in feat_names[:20]:  # Limit for UI
            feat_info = feats.get(feat_name, {})
            description = feat_info.get("description", "Açıklama yok")

            feat_radio = ctk.CTkRadioButton(
                feat_frame,
                text=f"{feat_name}\n{description[:100]}{'...' if len(description) > 100 else ''}",
                variable=self.selected_feat,
                value=feat_name,
                wraplength=400
            )
            feat_radio.pack(anchor="w", pady=5, padx=10)

    def _step_class_features(self):
        """Step 5: Class features"""
        char_class = self.character_data.get("class", "")
        new_level = getattr(self, 'selected_new_level', self.character_data.get("level", 1) + 1)

        # Get class features for the new level
        class_data = self.system_data.get("classes", {}).get(char_class, {})
        features = class_data.get("features", [])

        # Filter features by level
        new_features = []
        for feature in features:
            if isinstance(feature, dict):
                feature_level = feature.get("level", 1)
                if feature_level == new_level:
                    new_features.append(feature.get("name", "Unknown"))

        if not new_features:
            info_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Seviye {new_level} için yeni sınıf özelliği bulunamadı.\nDevam etmek için İleri'ye tıklayın.",
                font=ctk.CTkFont(size=14)
            )
            info_label.pack(pady=(50, 20))
            return

        info_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Seviye {new_level}: Yeni sınıf özellikleri!\n\nAşağıdaki özellikler otomatik olarak eklenecek:",
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(pady=(20, 10))

        # Features list
        features_frame = ctk.CTkFrame(self.content_frame)
        features_frame.pack(fill="x", padx=20, pady=10)

        features_text = "\n".join(f"• {feature}" for feature in new_features)
        features_label = ctk.CTkLabel(
            features_frame,
            text=features_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        features_label.pack(pady=10, padx=10, anchor="w")

        # Store new features
        self.new_class_features = new_features

    def _step_spell_selection(self):
        """Step 6: Spell selection for spellcasters"""
        from utils.calculations import calculate_spells_known

        char_class = self.character_data.get("class", "")
        current_level = self.character_data.get("level", 1)
        new_level = getattr(self, 'selected_new_level', current_level + 1)

        # Check if character is a spellcaster
        class_data = self.system_data.get("classes", {}).get(char_class, {})
        is_spellcaster = class_data.get("spellcasting", False)

        if not is_spellcaster:
            info_label = ctk.CTkLabel(
                self.content_frame,
                text=f"{char_class} sınıfı büyücü değil.\nDevam etmek için İleri'ye tıklayın.",
                font=ctk.CTkFont(size=14)
            )
            info_label.pack(pady=(50, 20))
            return

        # Sadece known caster sınıflar için limitli seçim uygula
        known_info = calculate_spells_known({
            "class": char_class,
            "level": new_level
        })
        total_allowed = None
        already_known = 0
        remaining_can_learn = None

        # Mevcut karakterin bilinen büyülerini say (basit: character_data['spells'] dict'inde tüm listelerin toplamı)
        existing_spells = self.character_data.get("spells", {})
        if isinstance(existing_spells, dict):
            for key, val in existing_spells.items():
                if isinstance(val, list):
                    already_known += len(val)

        if known_info and "total" in known_info:
            total_allowed = known_info["total"]
            remaining_can_learn = max(0, total_allowed - already_known)

        header_text = f"Seviye {new_level}: Büyü seçimi!\n\n"
        if remaining_can_learn is not None:
            header_text += f"Bu seviyede toplam bilinen büyü sayınız: {total_allowed}\n"
            header_text += f"Şu anda bilinen büyü sayısı: {already_known}\n"
            header_text += f"Bu adımda en fazla {remaining_can_learn} yeni büyü seçebilirsiniz."
        else:
            header_text += "Yeni büyülerinizi seçin."

        info_label = ctk.CTkLabel(
            self.content_frame,
            text=header_text,
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(pady=(20, 10))

        # Spell selection
        spell_frame = ctk.CTkScrollableFrame(self.content_frame)
        spell_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Get available spells for the class
        class_spells = class_data.get("spells", [])
        all_spells = self.system_data.get("spells", {})

        # Filter spells by level (basit mantık: yeni seviye veya altı)
        available_spells = []
        for spell_name in class_spells:
            if not isinstance(spell_name, str):
                continue
            spell_data = all_spells.get(spell_name, {})
            spell_level = spell_data.get("level", 0)
            if isinstance(spell_level, int) and spell_level <= new_level:
                available_spells.append(spell_name)

        # Mevcut bilinen büyüleri işaretle ve yeni seçimleri burada tut
        self.selected_spells = []
        self._spell_checkboxes = {}
        self._spell_remaining_limit = remaining_can_learn

        def make_toggle(spell_name: str):
            def _inner_toggle():
                # Limit varsa, fazla seçimi engelle
                if spell_name in self.selected_spells:
                    self.selected_spells.remove(spell_name)
                else:
                    if self._spell_remaining_limit is not None and len(self.selected_spells) >= self._spell_remaining_limit:
                        # Checkbox'ı geri kapat
                        cb = self._spell_checkboxes.get(spell_name)
                        if cb is not None:
                            cb.deselect()
                        messagebox.showwarning(
                            "Sınır Aşıldı",
                            f"Bu seviyede en fazla {self._spell_remaining_limit} yeni büyü seçebilirsiniz."
                        )
                        return
                    self.selected_spells.append(spell_name)
            return _inner_toggle

        # Ritual/Concentration etiketleri icin import
        try:
            from utils.calculations import is_ritual_spell, is_concentration_spell
        except ImportError:
            is_ritual_spell = lambda *a, **k: False
            is_concentration_spell = lambda *a, **k: False

        for spell_name in available_spells:
            spell_data = all_spells.get(spell_name, {})
            description = spell_data.get("description", "Açıklama yok")
            level_val = spell_data.get("level", 0)

            # Spell etiketleri
            tags = []
            if is_ritual_spell(spell_name, spell_data):
                tags.append("[Ritual]")
            if is_concentration_spell(spell_name, spell_data):
                tags.append("[Conc.]")
            tag_str = " ".join(tags)
            if tag_str:
                tag_str = " " + tag_str

            checkbox = ctk.CTkCheckBox(
                spell_frame,
                text=f"{spell_name} (Lv{level_val}){tag_str}\n{description[:80]}{'...' if len(description) > 80 else ''}",
                command=make_toggle(spell_name)
            )
            checkbox.pack(anchor="w", pady=3, padx=10)
            self._spell_checkboxes[spell_name] = checkbox

    def _toggle_spell(self, spell_name: str):
        """Toggle spell selection"""
        if spell_name in self.selected_spells:
            self.selected_spells.remove(spell_name)
        else:
            self.selected_spells.append(spell_name)

    def _step_finalize_levelup(self):
        """Step 8: Finalize level up"""
        # Collect all changes
        changes_summary = []

        # Level change
        old_level = self.character_data.get("level", 1)
        new_level = getattr(self, 'selected_new_level', old_level + 1)

        # Multiclass info
        if self.is_multiclass_levelup and self.multiclass_target_class:
            changes_summary.append(f"🔀 MULTICLASS Level Up")
            changes_summary.append(f"Toplam Seviye: {old_level} → {new_level}")
            target_cls = self.multiclass_target_class
            existing_levels = self.character_data.get("class_levels", {})
            target_new_level = existing_levels.get(target_cls, 0) + 1
            changes_summary.append(f"Yeni Sınıf Seviyesi: {target_cls} → Lvl {target_new_level}")

            # Show multiclass proficiencies if first level in new class
            if target_new_level == 1 and self.multiclass_new_proficiencies:
                changes_summary.append("Yeni Proficiency'ler:")
                for ptype, items in self.multiclass_new_proficiencies.items():
                    if items:
                        changes_summary.append(f"  {ptype.title()}: {', '.join(items)}")
        else:
            changes_summary.append(f"Seviye: {old_level} → {new_level}")

        # HP increase
        hp_increase = getattr(self, 'hp_increase_amount', 0)
        if hp_increase > 0:
            old_hp = self.character_data.get("hp", self.character_data.get("hit_points", 0))
            new_hp = old_hp + hp_increase
            changes_summary.append(f"HP: {old_hp} → {new_hp} (+{hp_increase})")

        # ASI changes
        asi_changes = getattr(self, 'asi_changes', {})
        if asi_changes:
            changes_summary.append("Yetenek Artışları:")
            for ability, increase in asi_changes.items():
                old_score = self.character_data.get("abilities", {}).get("scores", {}).get(ability, 10)
                new_score = old_score + increase
                changes_summary.append(f"  {ability.title()}: {old_score} → {new_score} (+{increase})")

        # New feat
        new_feat = getattr(self, 'selected_feat_name', None)
        if new_feat:
            changes_summary.append(f"Yeni Feat: {new_feat}")

        # New class features
        new_features = getattr(self, 'new_class_features', [])
        if new_features:
            changes_summary.append("Yeni Sınıf Özellikleri:")
            for feature in new_features:
                changes_summary.append(f"  • {feature}")

        # New spells
        new_spells = getattr(self, 'selected_spells', [])
        if new_spells:
            changes_summary.append(f"Yeni Büyüler: {', '.join(new_spells)}")

        # Multiclass spell slots
        if self.is_multiclass_levelup:
            try:
                from utils.multiclass import calculate_multiclass_spell_slots
                class_levels = dict(self.character_data.get("class_levels", {}))
                if not class_levels:
                    current_class = self.character_data.get("class", "")
                    class_levels[current_class] = self.character_data.get("level", 1)
                # Simulate adding the new level
                target = self.multiclass_target_class
                class_levels[target] = class_levels.get(target, 0) + 1

                new_slots = calculate_multiclass_spell_slots(class_levels, self.character_data.get("subclasses", {}))
                if new_slots:
                    slot_text = ", ".join(f"Lv{k}: {v}" for k, v in sorted(new_slots.items()))
                    changes_summary.append(f"Multiclass Spell Slots: {slot_text}")
            except ImportError:
                pass

        # Subclass
        selected_subclass = getattr(self, 'selected_subclass', None)
        if selected_subclass:
            changes_summary.append(f"🏛️ Subclass: {selected_subclass}")

        # Summary
        summary_text = "Level Up Özeti:\n\n" + "\n".join(changes_summary)

        summary_label = ctk.CTkLabel(
            self.content_frame,
            text=summary_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        summary_label.pack(pady=(20, 20), padx=20, anchor="w")

        # Confirmation
        confirm_label = ctk.CTkLabel(
            self.content_frame,
            text="Değişiklikleri uygulamak için 'Tamamla' butonuna tıklayın.",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        confirm_label.pack(pady=(20, 10))

    def _finalize_levelup(self):
        """Apply all level up changes and close wizard"""
        try:
            new_level = getattr(self, 'selected_new_level', self.character_data.get("level", 1) + 1)

            # ---- MULTICLASS LEVEL UP ----
            if self.is_multiclass_levelup and self.multiclass_target_class:
                try:
                    from utils.multiclass import apply_multiclass_level
                    self.character_data = apply_multiclass_level(
                        self.character_data,
                        self.multiclass_target_class
                    )
                except ImportError:
                    # Fallback: manual multiclass application
                    self.character_data["level"] = new_level
                    class_levels = self.character_data.setdefault("class_levels", {})
                    if not class_levels:
                        current_class = self.character_data.get("class", "Fighter")
                        current_lvl = self.character_data.get("level", 1) - 1
                        class_levels[current_class] = current_lvl
                    target = self.multiclass_target_class
                    class_levels[target] = class_levels.get(target, 0) + 1
                    self.character_data["is_multiclass"] = True
                    parts = [f"{c} {l}" for c, l in class_levels.items()]
                    self.character_data["class_display"] = " / ".join(parts)
            else:
                # ---- NORMAL LEVEL UP ----
                self.character_data["level"] = new_level

            # Apply HP increase
            hp_increase = getattr(self, 'hp_increase_amount', 0)
            if hp_increase > 0:
                hp_key = "hp" if "hp" in self.character_data else "hit_points"
                current_hp = self.character_data.get(hp_key, 0)
                self.character_data[hp_key] = current_hp + hp_increase

            # Apply ASI changes
            asi_changes = getattr(self, 'asi_changes', {})
            if asi_changes:
                # Handle both flat and nested ability structures
                abilities = self.character_data.get("abilities", {})
                if "scores" in abilities:
                    scores = abilities["scores"]
                    for ability, increase in asi_changes.items():
                        scores[ability] = scores.get(ability, 10) + increase
                else:
                    for ability, increase in asi_changes.items():
                        # Try capitalized key first
                        for key in [ability, ability.title(), ability.capitalize(), ability.lower()]:
                            if key in abilities:
                                abilities[key] = abilities[key] + increase
                                break
                        else:
                            abilities[ability] = abilities.get(ability, 10) + increase

            # Apply subclass selection
            selected_subclass = getattr(self, 'selected_subclass', None)
            if selected_subclass:
                self.character_data["subclass"] = selected_subclass
                # Multiclass durumunda subclasses dict'ine de ekle
                if self.is_multiclass_levelup and self.multiclass_target_class:
                    subclasses = self.character_data.setdefault("subclasses", {})
                    subclasses[self.multiclass_target_class] = selected_subclass
                else:
                    subclasses = self.character_data.setdefault("subclasses", {})
                    char_class = self.character_data.get("class", "")
                    subclasses[char_class] = selected_subclass
                # Feature olarak da ekle
                features = self.character_data.setdefault("features", [])
                if selected_subclass not in features:
                    features.append(selected_subclass)

            # Apply new feat
            new_feat = getattr(self, 'selected_feat_name', None)
            if new_feat:
                features = self.character_data.setdefault("features", [])
                if new_feat not in features:
                    features.append(new_feat)

            # Apply new class features
            new_features = getattr(self, 'new_class_features', [])
            if new_features:
                features = self.character_data.setdefault("features", [])
                for feature in new_features:
                    if feature not in features:
                        features.append(feature)

            # Apply new spells
            new_spells = getattr(self, 'selected_spells', [])
            if new_spells:
                spells = self.character_data.setdefault("spells", {})
                # Add to appropriate level (simplified)
                for spell in new_spells:
                    spell_level = self.system_data.get("spells", {}).get(spell, {}).get("level", 0)
                    key = "cantrips" if spell_level == 0 else f"level{spell_level}"
                    spell_list = spells.setdefault(key, [])
                    if spell not in spell_list:
                        spell_list.append(spell)

            # Recalculate derived stats
            if self.system_name == "dnd5e":
                from utils.calculations import calculate_all_dnd_stats
                self.character_data = calculate_all_dnd_stats(self.character_data)

            # Save character file
            try:
                from creators.base_creator import CharacterFactory
                creator = CharacterFactory.create_creator("dnd5e")
                char_name = self.character_data.get("name", "unknown")
                filename = f"{char_name.lower().replace(' ', '_')}_dnd5e"
                creator.save_character(self.character_data, filename)
            except Exception:
                pass  # Save is best-effort

            # Call completion callback
            if self.on_complete:
                self.on_complete(self.character_data)

            mc_text = f" (Multiclass: {self.multiclass_target_class})" if self.is_multiclass_levelup else ""
            messagebox.showinfo("Başarılı", f"Karakter başarıyla level up edildi!{mc_text}")
            self.wizard_window.destroy()

        except Exception as e:
            messagebox.showerror("Hata", f"Level up sırasında hata oluştu: {str(e)}")


class BatchOperationsDialog:
    """Dialog for batch character operations"""

    def __init__(self, parent):
        self.parent = parent
        self.operations = {
            "Toplu PDF Export": self._batch_pdf_export,
            "Toplu Silme": self._batch_delete,
            "Karakter Analizi": self._batch_analyze,
            "Şablon Oluştur": self._batch_create_templates
        }

        self._create_dialog()

    def _create_dialog(self):
        """Create the batch operations dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Toplu İşlemler")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)

        # Make it modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Main frame
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Toplu Karakter İşlemleri",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Operations list
        operations_frame = ctk.CTkFrame(main_frame)
        operations_frame.pack(fill="both", expand=True, padx=20, pady=10)

        operations_label = ctk.CTkLabel(
            operations_frame,
            text="Mevcut İşlemler:",
            font=ctk.CTkFont(weight="bold")
        )
        operations_label.pack(anchor="w", pady=(10, 5))

        # Operation buttons
        for operation_name, operation_func in self.operations.items():
            btn = ctk.CTkButton(
                operations_frame,
                text=operation_name,
                command=lambda op=operation_func, name=operation_name: self._run_operation(op, name),
                height=35
            )
            btn.pack(fill="x", pady=2, padx=10)

        # Results area
        results_label = ctk.CTkLabel(
            main_frame,
            text="Sonuçlar:",
            font=ctk.CTkFont(weight="bold")
        )
        results_label.pack(anchor="w", padx=20, pady=(10, 5))

        self.results_text = ctk.CTkTextbox(main_frame, wrap="word", height=150)
        self.results_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Kapat",
            command=self.dialog.destroy
        )
        close_btn.pack(pady=(0, 10))

    def _run_operation(self, operation_func, operation_name):
        """Run the selected batch operation"""
        try:
            self.results_text.delete("0.0", "end")
            self.results_text.insert("end", f"🔄 {operation_name} başlatılıyor...\n\n")

            result = operation_func()

            self.results_text.insert("end", f"✅ {operation_name} tamamlandı!\n\n")
            self.results_text.insert("end", result)

        except Exception as e:
            error_msg = f"❌ Hata: {str(e)}\n"
            self.results_text.insert("end", error_msg)

    def _batch_pdf_export(self):
        """Batch PDF export operation"""
        characters_dir = Path("characters")
        if not characters_dir.exists():
            return "❌ Characters klasörü bulunamadı!"

        json_files = list(characters_dir.glob("*.json"))
        if not json_files:
            return "❌ Hiç karakter dosyası bulunamadı!"

        success_count = 0
        error_count = 0

        for json_file in json_files:
            try:
                # Load character
                with open(json_file, 'r', encoding='utf-8') as f:
                    character = json.load(f)

                # Export PDF
                pdf_filename = f"{json_file.stem}_sheet.pdf"
                pdf_path = characters_dir / "exports" / pdf_filename
                pdf_path.parent.mkdir(exist_ok=True)

                # Use the PDF export function
                from utils.export_pdf import export_dnd_character_pdf
                success = export_dnd_character_pdf(character, str(pdf_path))

                if success:
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                error_count += 1

        return f"📊 Toplu PDF Export Sonucu:\n✅ Başarılı: {success_count}\n❌ Hatalı: {error_count}\n📁 Toplam: {len(json_files)}"

    def _batch_delete(self):
        """Batch delete operation"""
        if not messagebox.askyesno("Onay", "TÜM karakterleri silmek istediğinizden emin misiniz? Bu işlem geri alınamaz!"):
            return "❌ İşlem iptal edildi."

        characters_dir = Path("characters")
        if not characters_dir.exists():
            return "❌ Characters klasörü bulunamadı!"

        json_files = list(characters_dir.glob("*.json"))
        if not json_files:
            return "ℹ️ Silinecek karakter bulunamadı."

        deleted_count = 0
        for json_file in json_files:
            try:
                json_file.unlink()
                deleted_count += 1
            except Exception:
                pass

        return f"🗑️ {deleted_count} karakter dosyası silindi."

    def _batch_analyze(self):
        """Batch character analysis"""
        characters_dir = Path("characters")
        if not characters_dir.exists():
            return "❌ Characters klasörü bulunamadı!"

        json_files = list(characters_dir.glob("*.json"))
        if not json_files:
            return "❌ Analiz edilecek karakter bulunamadı!"

        analysis_results = []
        total_characters = len(json_files)

        # Count by system
        systems = {}
        classes = {}
        races = {}
        levels = []

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    character = json.load(f)

                system = character.get('system', 'Unknown')
                systems[system] = systems.get(system, 0) + 1

                char_class = character.get('class', 'Unknown')
                classes[char_class] = classes.get(char_class, 0) + 1

                race = character.get('race', 'Unknown')
                races[race] = races.get(race, 0) + 1

                level = character.get('level', 1)
                levels.append(level)

            except Exception:
                pass

        # Build analysis report
        report = f"📊 Karakter Analizi Raporu\n\n"
        report += f"📁 Toplam Karakter: {total_characters}\n\n"

        report += "🎲 Sistem Dağılımı:\n"
        for system, count in systems.items():
            report += f"  {system}: {count}\n"

        report += "\n⚔️ Popüler Sınıflar:\n"
        sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)[:5]
        for char_class, count in sorted_classes:
            report += f"  {char_class}: {count}\n"

        report += "\n🏛️ Popüler Irklar:\n"
        sorted_races = sorted(races.items(), key=lambda x: x[1], reverse=True)[:5]
        for race, count in sorted_races:
            report += f"  {race}: {count}\n"

        if levels:
            avg_level = sum(levels) / len(levels)
            max_level = max(levels)
            min_level = min(levels)
            report += ".1f"
            report += f"  Maksimum: {max_level}\n"
            report += f"  Minimum: {min_level}\n"

        return report

    def _batch_create_templates(self):
        """Batch create templates from characters"""
        characters_dir = Path("characters")
        if not characters_dir.exists():
            return "❌ Characters klasörü bulunamadı!"

        json_files = list(characters_dir.glob("*.json"))
        if not json_files:
            return "❌ Şablon oluşturulacak karakter bulunamadı!"

        templates_created = 0

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    character = json.load(f)

                # Create template data
                template_data = {
                    "template_name": f"{character.get('name', 'Unknown')}_template",
                    "system": character.get('system', 'dnd5e'),
                    "description": f"{character.get('race', '')} {character.get('class', '')} şablonu",
                    "created_at": "2024-01-01T00:00:00",  # Would use datetime in real implementation
                    "template_data": {
                        "race": character.get('race'),
                        "class": character.get('class'),
                        "background": character.get('background'),
                        "abilities": character.get('abilities', {}).get('scores'),
                        "level": 1  # Templates start at level 1
                    }
                }

                # Save template (simplified - would use proper template manager)
                templates_dir = Path("characters") / "templates"
                templates_dir.mkdir(exist_ok=True)

                template_file = templates_dir / f"{template_data['template_name']}.json"
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, ensure_ascii=False, indent=2)

                templates_created += 1

            except Exception as e:
                print(f"Template creation error for {json_file}: {e}")

        return f"📝 {templates_created} şablon oluşturuldu."


if __name__ == "__main__":
    app = DiyargezerGUI()
    app.run()