#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pathfinder 1e CLI - Karakter oluşturma wizard'ı
"""

from pathlib import Path
import sys

# Ana dizini Python path'e ekle
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from cli import CharacterContext, CharacterWizard
from cli.steps import (
    IntroStep,
    RaceStep,
    BackgroundStep,
    AbilityStep,
    PersonalityStep,
    EquipmentStep,
    SummaryStep,
)
from utils.data_loader import load_dnd_data


def load_pathfinder_data(base_dir: Path):
    """Pathfinder 1e veri dosyasını yükle"""
    import json
    data_file = base_dir / "data" / "pathfinder_1e_data.json"
    
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {
        "races": {},
        "classes": {},
        "feats": {},
        "spells": {}
    }


def build_wizard(base_dir: Path) -> CharacterWizard:
    """Pathfinder 1e wizard'ı oluştur"""
    data = load_pathfinder_data(base_dir)
    
    races = data.get("races", {})
    classes = data.get("classes", {})
    backgrounds = data.get("backgrounds", {})  # Empty for now
    abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    languages = []  # D&D veri dosyasından çek
    
    steps = [
        IntroStep(classes=sorted(classes.keys())),
        RaceStep(races=races),
        BackgroundStep(backgrounds=backgrounds),
        AbilityStep(abilities=abilities),
        PersonalityStep(available_languages=languages),
        EquipmentStep(classes=classes),
        SummaryStep(),
    ]
    return CharacterWizard(steps)


def main() -> None:
    """Ana fonksiyon"""
    print("\n" + "=" * 60)
    print("Pathfinder 1e Karakter Oluşturma Sistemi")
    print("=" * 60)
    print()
    
    base_dir = Path(__file__).resolve().parent
    ctx = CharacterContext()
    
    try:
        wizard = build_wizard(base_dir)
        ctx = wizard.run(ctx)
        
        # Karakteri kaydet
        from utils.storage import save_character, _safe_name
        import json
        
        char_name = ctx.get("name", "Unnamed")
        safe_name = _safe_name(char_name)
        char_file = base_dir / "characters" / f"{safe_name}_pathfinder.json"
        char_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Pathfinder veri ekle
        ctx["system"] = "PATHFINDER_1E"
        ctx["created_at"] = str(Path(char_file).stem)
        
        with open(char_file, 'w', encoding='utf-8') as f:
            json.dump(ctx, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Karakter kaydedildi: {char_file}")
        
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından iptal edildi.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
