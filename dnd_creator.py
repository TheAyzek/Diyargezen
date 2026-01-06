import json
from pathlib import Path
from utils.data_loader import load_dnd_data


def _load_dnd_data() -> dict:
    base_dir = Path(__file__).parent
    return load_dnd_data(base_dir)


def _prompt_selection(options: list[str], prompt_text: str) -> str:
    """
    Kullanıcıya seçenekli bir liste sunar ve geçerli bir seçim döndürür.
    """
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


def _prompt_point_buy(abilities: list[str], total_points: int = 27) -> dict:
    """
    Basit 5e point-buy (8-15 arası, maliyet [8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9]).
    Kullanıcıdan her yetenek için değer alır, toplam puan sınırını uygular.
    """
    cost_map = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
    print("\nYetenek puanlarını point-buy ile belirleyelim (toplam 27 puan).")
    print("Geçerli değerler: 8-15. Her yetenek için bir değer girin.")
    while True:
        scores: dict[str, int] = {}
        spent = 0
        for ability in abilities:
            while True:
                raw = input(f"{ability} (8-15): ").strip()
                if raw.isdigit():
                    val = int(raw)
                    if 8 <= val <= 15:
                        spent += cost_map[val]
                        scores[ability] = val
                        break
                print("Geçersiz değer. 8 ile 15 arasında bir sayı girin.")
        if spent <= total_points:
            print(f"Toplam harcanan puan: {spent}/{total_points}")
            return scores
        print(f"Toplam {spent} puan harcandı, limit {total_points}. Tekrar deneyelim.\n")


def create_dnd_character() -> dict:
    """
    Kullanıcıyı adım adım yönlendirerek temel D&D 5e karakteri oluşturur.
    - Irk seçimi
    - Sınıf seçimi
    Seçimlere göre temel özellikleri birleştirip karakter sözlüğünü döndürür.
    """
    data = _load_dnd_data()

    race_names = sorted(data.get("races", {}).keys())
    class_names = sorted(data.get("classes", {}).keys())
    background_names = sorted(data.get("backgrounds", {}).keys())
    abilities = list(data.get("abilities", []))

    if not race_names or not class_names:
        raise RuntimeError("D&D veri dosyası eksik ya da bozuk: Irklar veya sınıflar bulunamadı.")
    if not background_names or not abilities:
        raise RuntimeError("D&D veri dosyası eksik ya da bozuk: Arka planlar veya yetenek listesi bulunamadı.")

    print("Önce ırkını seçelim:")
    selected_race = _prompt_selection(race_names, "Mevcut ırklar:")

    print("\nŞimdi de sınıfını belirleyelim:")
    selected_class = _prompt_selection(class_names, "Mevcut sınıflar:")

    print("\nArka planını seçelim:")
    selected_background = _prompt_selection(background_names, "Mevcut arka planlar:")

    race_data = data["races"][selected_race]
    class_data = data["classes"][selected_class]
    background_data = data["backgrounds"][selected_background]

    # Yetenek puanlarını kullanıcıdan point-buy ile al
    base_scores = _prompt_point_buy(abilities)

    # Irksal yetenek puanı artışlarını uygula
    asi = race_data.get("ability_score_increase", {})
    final_scores = {k: base_scores.get(k, 8) for k in abilities}
    # Human (all:1) gibi özel anahtar veya tek tek arttırımlar
    if "all" in asi:
        for k in final_scores:
            final_scores[k] += int(asi["all"])
    for key, inc in asi.items():
        if key == "all":
            continue
        if key in final_scores:
            final_scores[key] += int(inc)

    # Modifikator hesapla: (score - 10) // 2
    modifiers = {k: (v - 10) // 2 for k, v in final_scores.items()}

    # Sınıfın başlangıç ekipman seçeneklerinden bir set seçtir
    equip_options = class_data.get("starting_equipment_options", [])
    chosen_equipment = []
    if equip_options:
        print("\nBaşlangıç ekipmanını seçelim:")
        option_labels = [", ".join(opt) for opt in equip_options]
        chosen_label = _prompt_selection(option_labels, "Ekipman seçenekleri:")
        # Etiketler birebir sıralı, seçilen label'ın indexindeki listeyi al
        chosen_index = option_labels.index(chosen_label)
        chosen_equipment = equip_options[chosen_index]

    character: dict = {
        "system": "DND5E",
        "race": selected_race,
        "class": selected_class,
        "background": selected_background,
        "race_traits": race_data.get("traits", []),
        "speed": race_data.get("speed"),
        "ability_score_increase": asi,
        "abilities": final_scores,
        "hit_die": class_data.get("hit_die"),
        "primary_ability": class_data.get("primary_ability", []),
        "saving_throws": class_data.get("saving_throws", []),
        "ability_modifiers": modifiers,
        "equipment": chosen_equipment,
        "background_features": {
            "skill_proficiencies": background_data.get("skill_proficiencies", []),
            "feature": background_data.get("feature", "")
        }
    }

    print("\n--- Karakter Özeti ---")
    print(f"Sistem: {character['system']}")
    print(f"Irk: {character['race']}")
    print(f"Sınıf: {character['class']}")
    print(f"Arka Plan: {character['background']}")
    print(f"Hız: {character['speed']}")
    print(f"Irksal Özellikler: {', '.join(character['race_traits'])}")
    print(f"Yetenek Puanı Artışı: {character['ability_score_increase']}")
    print(f"Yetenek Puanları: {character['abilities']}")
    print(f"Can Zarı: {character['hit_die']}")
    print(f"Birincil Yetenek(ler): {', '.join(character['primary_ability'])}")
    print(f"Kurtarış Atışları: {', '.join(character['saving_throws'])}")
    print(f"Yetenek Modifikatorleri: {character['ability_modifiers']}")
    if character["equipment"]:
        print(f"Ekipman: {', '.join(character['equipment'])}")
    print("Arka Plan Özellikleri:")
    print(f"  Yetenek Uzmanlıkları: {', '.join(character['background_features']['skill_proficiencies'])}")
    print(f"  Özellik: {character['background_features']['feature']}")

    return character


if __name__ == "__main__":
    # Basit manuel çalışma
    create_dnd_character()


