import json
from pathlib import Path


def _load_mm_data() -> dict:
    """
    Mutants & Masterminds veri dosyasını yükler.
    Veri dosyası: data/mm_data.json
    """
    data_path = Path(__file__).parent / "data" / "mm_data.json"
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _prompt_selection(options: list[str], prompt_text: str) -> str:
    if not options:
        raise ValueError("Seçenek listesi boş olamaz.")
    print(prompt_text)
    for idx, option in enumerate(options, start=1):
        print(f"  {idx}) {option}")
    while True:
        choice = input("Seçiminizin numarasını girin: ").strip()
        if choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(options):
                return options[num - 1]
        print("Geçersiz seçim. Lütfen listedeki numaralardan birini girin.")


def create_mm_character() -> dict:
    """
    Kullanıcıyı yönlendirerek temel M&M karakteri oluşturur.
    Adımlar:
    - Power Level (PL) seçimi
    - Arketip seçimi (örnek öneriler için)
    """
    data = _load_mm_data()

    pl_names = sorted(data.get("power_levels", {}).keys())
    archetype_names = sorted(data.get("archetypes", {}).keys())
    abilities = list(data.get("abilities", []))

    if not pl_names or not archetype_names or not abilities:
        raise RuntimeError("M&M veri dosyası eksik ya da bozuk.")

    print("Önce Power Level (PL) seçelim:")
    selected_pl = _prompt_selection(pl_names, "Mevcut PL seçenekleri:")

    print("\nArketip seçelim (oyun tarzı için öneriler verir):")
    selected_archetype = _prompt_selection(archetype_names, "Mevcut arketipler:")

    pl_data = data["power_levels"][selected_pl]
    archetype_data = data["archetypes"][selected_archetype]

    character: dict = {
        "system": "MUTANTS_AND_MASTERMINDS",
        "power_level": selected_pl,
        "pl_caps": pl_data,
        "archetype": selected_archetype,
        "archetype_summary": archetype_data.get("summary", ""),
        "suggested_powers": archetype_data.get("suggested_powers", []),
        "suggested_advantages": archetype_data.get("suggested_advantages", []),
        "abilities": {name: 0 for name in abilities}
    }

    print("\n--- Karakter Özeti (M&M) ---")
    print(f"Sistem: {character['system']}")
    print(f"Power Level: {character['power_level']}")
    print(f"Limitler: {character['pl_caps']}")
    print(f"Arketip: {character['archetype']} - {character['archetype_summary']}")
    print(f"Önerilen Güçler: {', '.join(character['suggested_powers'])}")
    print(f"Önerilen Avantajlar: {', '.join(character['suggested_advantages'])}")
    print(f"Başlangıç Yetenekleri: {character['abilities']}")

    return character


if __name__ == "__main__":
    create_mm_character()


