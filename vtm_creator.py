import json
from pathlib import Path


def _load_vtm_data() -> dict:
    """
    Vampire: The Masquerade veri dosyasını yükler.
    Veri dosyası: data/vtm_data.json
    """
    data_path = Path(__file__).parent / "data" / "vtm_data.json"
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


def create_vtm_character() -> dict:
    """
    Kullanıcıyı yönlendirerek temel VtM karakteri oluşturur.
    Adımlar:
    - Klan seçimi
    İleride: Nitelikler, beceriler, avantajlar (gelişmeye açık)
    """
    data = _load_vtm_data()

    clan_names = sorted(data.get("clans", {}).keys())
    if not clan_names:
        raise RuntimeError("VtM veri dosyası eksik ya da bozuk: Klan bulunamadı.")

    print("Önce klanı seçelim:")
    selected_clan = _prompt_selection(clan_names, "Mevcut klanlar:")

    clan = data["clans"][selected_clan]

    # Başlangıç dağılımı için attribute ve skill iskeleti
    attributes = data.get("attributes", {})
    skills = data.get("skills", {})

    character: dict = {
        "system": "VAMPIRE_THE_MASQUERADE",
        "clan": selected_clan,
        "bane": clan.get("bane", ""),
        "disciplines": clan.get("disciplines", []),
        "attributes": {group: {name: 1 for name in names} for group, names in attributes.items()},
        "skills": {group: {name: 0 for name in names} for group, names in skills.items()},
    }

    print("\n--- Karakter Özeti (VtM) ---")
    print(f"Sistem: {character['system']}")
    print(f"Klan: {character['clan']}")
    print(f"Lanet (Bane): {character['bane']}")
    print(f"Disiplinler: {', '.join(character['disciplines'])}")
    print("Nitelikler (başlangıç):")
    for group, group_attrs in character["attributes"].items():
        print(f"  {group}: {group_attrs}")
    print("Beceriler (başlangıç):")
    for group, group_skills in character["skills"].items():
        print(f"  {group}: {group_skills}")

    return character


if __name__ == "__main__":
    create_vtm_character()


