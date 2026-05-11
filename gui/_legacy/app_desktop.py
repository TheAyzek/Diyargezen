"""
Diyargezer Desktop GUI
======================
CustomTkinter ile modern masaüstü arayüzü.

Özellikler:
  - Sistem seçimi (Combobox): D&D 5e, Pathfinder 1e, VtM 5e, M&M 3e
  - Karakter isim girişi
  - "Oluştur" butonu → CreatorFactory ile karakter oluşturma
  - "SQLite'a Kaydet" butonu → storage.py ile kalıcı kayıt
  - "PDF'e Aktar" butonu → export_pdf.py ile PDF çıktısı
  - Kaydedilmiş karakter listesi + yükleme

Backend ile entegrasyon:
  - CreatorFactory (creators/base_creator.py)
  - storage.py (utils/storage.py)
  - export_pdf.py (utils/export_pdf.py)
"""

from __future__ import annotations

import json
import logging
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Dict, Optional

import customtkinter as ctk
from PIL import Image as PILImage

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "diyargezer_logo.png"
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from creators import CreatorFactory
from creators.base_creator import BaseCharacterCreator
from utils.storage import (
    CharacterRecord,
    init_db,
    save_character,
    load_character,
    list_characters,
    delete_character,
)

logger = logging.getLogger(__name__)

DB_PATH = BASE_DIR / "data" / "characters.db"

SYSTEM_DISPLAY = {
    "dnd5e": "D&D 5th Edition",
    "pathfinder1e": "Pathfinder 1st Edition",
    "vtm5e": "Vampire: The Masquerade 5e",
    "mm3e": "Mutants & Masterminds 3e",
}

SYSTEM_KEYS = list(SYSTEM_DISPLAY.keys())
SYSTEM_LABELS = list(SYSTEM_DISPLAY.values())


class DiyargezerApp(ctk.CTk):
    """Ana uygulama penceresi."""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Diyargezer - TTRPG Karakter Yöneticisi")
        self.geometry("960x680")
        self.minsize(800, 600)

        self._set_window_icon()

        init_db(DB_PATH)

        self._current_character: Optional[Dict[str, Any]] = None
        self._current_creator: Optional[BaseCharacterCreator] = None

        self._build_ui()
        self._refresh_character_list()

    def _set_window_icon(self) -> None:
        """Pencere ikonunu ayarla."""
        try:
            if LOGO_PATH.exists():
                icon_image = tk.PhotoImage(file=str(LOGO_PATH))
                self.iconphoto(True, icon_image)
                self._icon_ref = icon_image
        except Exception:
            pass

    # ------------------------------------------------------------------
    # UI Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---- Left Panel: Create ----
        left = ctk.CTkFrame(self, width=320, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_propagate(False)

        # Logo
        try:
            if LOGO_PATH.exists():
                logo_img = ctk.CTkImage(
                    light_image=PILImage.open(LOGO_PATH),
                    dark_image=PILImage.open(LOGO_PATH),
                    size=(80, 80),
                )
                ctk.CTkLabel(left, image=logo_img, text="").pack(pady=(15, 0))
        except Exception:
            pass

        ctk.CTkLabel(left, text="Diyargezer", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(4, 0))
        ctk.CTkLabel(left, text="TTRPG Karakter Yönetimi", font=ctk.CTkFont(size=11), text_color="gray60").pack(pady=(0, 12))

        ctk.CTkLabel(left, text="TTRPG Sistemi:").pack(anchor="w", padx=20)
        self._system_var = ctk.StringVar(value=SYSTEM_LABELS[0])
        self._system_combo = ctk.CTkComboBox(
            left, values=SYSTEM_LABELS, variable=self._system_var,
            width=260, state="readonly",
        )
        self._system_combo.pack(padx=20, pady=(0, 10))

        ctk.CTkLabel(left, text="Karakter Adı:").pack(anchor="w", padx=20)
        self._name_entry = ctk.CTkEntry(left, placeholder_text="Karakter adını girin...", width=260)
        self._name_entry.pack(padx=20, pady=(0, 10))

        ctk.CTkLabel(left, text="Başlangıç Seviyesi: 1", text_color="gray60").pack(anchor="w", padx=20, pady=(0, 15))

        self._create_btn = ctk.CTkButton(left, text="Karakter Oluştur", command=self._on_create, width=260)
        self._create_btn.pack(padx=20, pady=5)

        sep = ctk.CTkFrame(left, height=2, fg_color="gray40")
        sep.pack(fill="x", padx=20, pady=15)

        self._save_btn = ctk.CTkButton(left, text="SQLite'a Kaydet", command=self._on_save, width=260, state="disabled")
        self._save_btn.pack(padx=20, pady=5)

        self._pdf_btn = ctk.CTkButton(left, text="PDF'e Aktar", command=self._on_export_pdf, width=260, state="disabled")
        self._pdf_btn.pack(padx=20, pady=5)

        self._json_btn = ctk.CTkButton(left, text="JSON Dışa Aktar", command=self._on_export_json, width=260, state="disabled")
        self._json_btn.pack(padx=20, pady=5)

        # ---- Right Panel: Details + List ----
        right = ctk.CTkFrame(self, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Character detail
        detail_frame = ctk.CTkFrame(right)
        detail_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        detail_frame.grid_rowconfigure(0, weight=1)
        detail_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(detail_frame, text="Karakter Detayları", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        self._detail_text = ctk.CTkTextbox(detail_frame, wrap="word", state="disabled")
        self._detail_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Saved characters list
        list_frame = ctk.CTkFrame(right)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(list_header, text="Kayıtlı Karakterler", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(list_header, text="Yenile", width=70, command=self._refresh_character_list).pack(side="right")
        ctk.CTkButton(list_header, text="Sil", width=60, fg_color="red", hover_color="darkred",
                       command=self._on_delete_selected).pack(side="right", padx=5)

        self._char_listbox = tk.Listbox(list_frame, bg="#2b2b2b", fg="white", selectbackground="#1f6aa5",
                                         font=("Consolas", 11), borderwidth=0, highlightthickness=0)
        self._char_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self._char_listbox.bind("<<ListboxSelect>>", self._on_list_select)

        self._char_ids: list[int] = []

        # ---- Status bar ----
        self._status = ctk.CTkLabel(self, text="Hazır", anchor="w")
        self._status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_system_key(self) -> str:
        label = self._system_var.get()
        idx = SYSTEM_LABELS.index(label) if label in SYSTEM_LABELS else 0
        return SYSTEM_KEYS[idx]

    def _set_status(self, msg: str) -> None:
        self._status.configure(text=msg)
        self.update_idletasks()

    def _show_character(self, char: Dict[str, Any]) -> None:
        self._detail_text.configure(state="normal")
        self._detail_text.delete("1.0", "end")
        text = json.dumps(char, indent=2, ensure_ascii=False, default=str)
        self._detail_text.insert("1.0", text)
        self._detail_text.configure(state="disabled")

    def _toggle_action_buttons(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self._save_btn.configure(state=state)
        self._pdf_btn.configure(state=state)
        self._json_btn.configure(state=state)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_create(self) -> None:
        """Karakter oluştur (GUI modunda: her zaman 1. seviyeden başlar)."""
        name = self._name_entry.get().strip() or "İsimsiz Kahraman"
        system_key = self._get_system_key()
        level = 1

        try:
            self._set_status(f"{system_key} için karakter oluşturuluyor...")
            creator = CreatorFactory.create(system_key)
            self._current_creator = creator

            if system_key in ("dnd5e", "pathfinder1e"):
                abilities = {
                    "strength": BaseCharacterCreator.roll_4d6_drop_lowest(),
                    "dexterity": BaseCharacterCreator.roll_4d6_drop_lowest(),
                    "constitution": BaseCharacterCreator.roll_4d6_drop_lowest(),
                    "intelligence": BaseCharacterCreator.roll_4d6_drop_lowest(),
                    "wisdom": BaseCharacterCreator.roll_4d6_drop_lowest(),
                    "charisma": BaseCharacterCreator.roll_4d6_drop_lowest(),
                }
                races = creator.list_available_races()
                classes = creator.list_available_classes()

                char: Dict[str, Any] = {
                    "system": system_key.upper(),
                    "name": name,
                    "race": races[0] if races else "Human",
                    "class": classes[0] if classes else "Fighter",
                    "level": level,
                    "abilities": abilities,
                    "modifiers": {k: (v - 10) // 2 for k, v in abilities.items()},
                }
                if system_key == "pathfinder1e":
                    char["bab"] = level
                    char["saves"] = {"fortitude": 2, "reflex": 0, "will": 0}

            elif system_key == "vtm5e":
                char = {
                    "system": "VTM5E",
                    "name": name,
                    "clan": "Brujah",
                    "attributes": {
                        "physical": {"strength": 2, "dexterity": 3, "stamina": 2},
                        "social": {"charisma": 2, "manipulation": 1, "composure": 2},
                        "mental": {"intelligence": 2, "wits": 2, "resolve": 1},
                    },
                    "skills": {"physical": {}, "social": {}, "mental": {}},
                    "disciplines": {"Potence": 1},
                    "humanity": 7,
                    "blood_potency": 1,
                }

            elif system_key == "mm3e":
                pl = 10
                char = {
                    "system": "MM3E",
                    "name": name,
                    "power_level": f"PL{pl}",
                    "pl_value": pl,
                    "total_power_points": pl * 15,
                    "remaining_power_points": pl * 15,
                    "abilities": {
                        "strength": 2, "stamina": 2, "agility": 2, "dexterity": 2,
                        "fighting": 2, "intellect": 2, "awareness": 2, "presence": 2,
                    },
                    "powers": {},
                    "defenses": {},
                }
            else:
                char = {"system": system_key.upper(), "name": name, "level": level}

            stats = creator.calculate_stats(char)
            char.update(stats)
            self._current_character = char
            self._show_character(char)
            self._toggle_action_buttons(True)
            self._set_status(f"'{name}' oluşturuldu ({creator.get_system_name()}, {creator.DICE_SYSTEM.name})")

        except Exception as exc:
            logger.exception("Karakter oluşturma hatası")
            messagebox.showerror("Hata", str(exc))
            self._set_status("Hata!")

    def _on_save(self) -> None:
        """Mevcut karakteri SQLite'a kaydet."""
        if not self._current_character:
            return
        try:
            rec = CharacterRecord(
                id=None,
                system=self._current_character.get("system", "UNKNOWN"),
                name=self._current_character.get("name", "İsimsiz"),
                data=self._current_character,
            )
            new_id = save_character(DB_PATH, rec)
            self._set_status(f"Karakter SQLite'a kaydedildi (ID: {new_id})")
            self._refresh_character_list()
        except Exception as exc:
            logger.exception("Kayıt hatası")
            messagebox.showerror("Hata", str(exc))

    def _on_export_pdf(self) -> None:
        """Mevcut karakteri PDF'e aktar."""
        if not self._current_character:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"{self._current_character.get('name', 'karakter')}.pdf",
        )
        if not filepath:
            return
        try:
            system = self._current_character.get("system", "").upper()
            output = Path(filepath)
            if "DND" in system or "D&D" in system:
                from utils.export_pdf import export_dnd_character_pdf
                export_dnd_character_pdf(self._current_character, output)
            elif "VTM" in system:
                from utils.export_pdf import export_vtm_character_pdf
                export_vtm_character_pdf(self._current_character, output)
            elif "MM" in system or "MUTANT" in system:
                from utils.export_pdf import export_mm_character_pdf
                export_mm_character_pdf(self._current_character, output)
            else:
                from utils.export_pdf import export_dnd_character_pdf
                export_dnd_character_pdf(self._current_character, output)
            self._set_status(f"PDF kaydedildi: {filepath}")
        except Exception as exc:
            logger.exception("PDF export hatası")
            messagebox.showerror("Hata", str(exc))

    def _on_export_json(self) -> None:
        """Mevcut karakteri JSON dosyasına aktar."""
        if not self._current_character or not self._current_creator:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile=f"{self._current_character.get('name', 'karakter')}.json",
        )
        if not filepath:
            return
        try:
            exported = self._current_creator.export_data(self._current_character)
            with open(filepath, "w", encoding="utf-8") as fh:
                json.dump(exported, fh, indent=2, ensure_ascii=False, default=str)
            self._set_status(f"JSON kaydedildi: {filepath}")
        except Exception as exc:
            logger.exception("JSON export hatası")
            messagebox.showerror("Hata", str(exc))

    def _on_delete_selected(self) -> None:
        """Listeden seçili karakteri sil."""
        sel = self._char_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._char_ids):
            return
        rec_id = self._char_ids[idx]
        if messagebox.askyesno("Onay", "Seçili karakter silinsin mi?"):
            delete_character(DB_PATH, rec_id)
            self._refresh_character_list()
            self._set_status(f"Karakter silindi (ID: {rec_id})")

    def _on_list_select(self, event: Any) -> None:
        """Listeden karakter seçildiğinde detayları göster."""
        sel = self._char_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._char_ids):
            return
        rec_id = self._char_ids[idx]
        record = load_character(DB_PATH, rec_id)
        if record:
            self._current_character = record.data
            system_key = record.system.lower().replace("_", "")
            try:
                self._current_creator = CreatorFactory.create(system_key)
            except ValueError:
                self._current_creator = None
            self._show_character(record.data)
            self._toggle_action_buttons(True)
            self._set_status(f"Yüklendi: {record.name} (ID: {rec_id})")

    def _refresh_character_list(self) -> None:
        """SQLite'tan karakter listesini yenile."""
        self._char_listbox.delete(0, tk.END)
        self._char_ids.clear()
        try:
            records = list_characters(DB_PATH)
            for rec in records:
                display = f"[{rec.system}] {rec.name} (ID:{rec.id})"
                self._char_listbox.insert(tk.END, display)
                self._char_ids.append(rec.id)
        except Exception as exc:
            logger.warning("Karakter listesi yüklenemedi: %s", exc)


def main() -> None:
    """Uygulamayı başlat."""
    logging.basicConfig(level=logging.INFO)
    app = DiyargezerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
