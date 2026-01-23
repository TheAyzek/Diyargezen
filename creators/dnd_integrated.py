# creators/dnd_integrated.py
"""
D&D 5e Entegre Karakter Oluşturucu
Tüm D&D özelliklerini bir araya getiren sistem
"""

import sys
from pathlib import Path

# Ana dizini Python path'e ekle
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

def show_dnd_menu():
    """D&D ana menüsünü göster"""
    print("\n" + "=" * 60)
    print("D&D 5e Karakter Oluşturucu - Ana Menü")
    print("=" * 60)
    print()
    print("Ne yapmak istersiniz?")
    print()
    print("1. Yeni Karakter Oluştur")
    print("2. Mevcut Karakterleri Görüntüle")
    print("3. Karakter İstatistikleri")
    print("4. D&D Kuralları ve Bilgiler")
    print("5. Geri Dön")
    print()

def get_dnd_choice():
    """D&D menü seçimini al"""
    while True:
        try:
            choice = input("Seçiminizi yapın (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("Geçersiz seçim! Lütfen 1-5 arası bir sayı girin.")
        except KeyboardInterrupt:
            return '5'

def create_new_character():
    """Yeni karakter oluştur"""
    print("\n" + "=" * 60)
    print("Yeni D&D Karakteri Oluştur")
    print("=" * 60)
    print()
    print("Hangi yöntemi kullanmak istersiniz?")
    print()
    print("1. Hızlı Oluşturucu (Otomatik)")
    print("2. Detaylı Oluşturucu (Adım Adım)")
    print("3. Gelişmiş Oluşturucu (GUI)")
    print("4. Geri Dön")
    print()
    
    while True:
        try:
            choice = input("Yöntem seçin (1-4): ").strip()
            if choice == '1':
                quick_create()
                break
            elif choice == '2':
                detailed_create()
                break
            elif choice == '3':
                gui_create()
                break
            elif choice == '4':
                return
            else:
                print("Geçersiz seçim!")
        except KeyboardInterrupt:
            return

def quick_create():
    """Hızlı karakter oluşturucu"""
    print("\nHızlı karakter oluşturucu başlatılıyor...")
    try:
        from creators import dnd_creator
        dnd_creator.create_character()
    except Exception as e:
        print(f"Hata: {e}")

def detailed_create():
    """Detaylı karakter oluşturucu"""
    print("\nDetaylı karakter oluşturucu başlatılıyor...")
    # Burada daha detaylı bir oluşturucu olabilir
    try:
        from creators import dnd_creator
        dnd_creator.create_character()
    except Exception as e:
        print(f"Hata: {e}")

def gui_create():
    """GUI karakter oluşturucu"""
    print("\nGUI karakter oluşturucu başlatılıyor...")
    try:
        import subprocess
        gui_path = BASE_DIR / "gui" / "app.py"
        if gui_path.exists():
            print("GUI başlatılıyor...")
            subprocess.run([sys.executable, str(gui_path)])
        else:
            print("GUI dosyası bulunamadı!")
    except Exception as e:
        print(f"GUI başlatılamadı: {e}")

def view_characters():
    """Mevcut karakterleri görüntüle"""
    print("\n" + "=" * 60)
    print("Mevcut Karakterler")
    print("=" * 60)
    
    characters_dir = BASE_DIR / "characters"
    if not characters_dir.exists():
        characters_dir.mkdir(exist_ok=True)
        print("Henüz karakter oluşturulmamış.")
        return
    
    import json
    
    character_files = list(characters_dir.glob("*.json"))
    
    if not character_files:
        print("Henüz karakter oluşturulmamış.")
        return
    
    print(f"{len(character_files)} karakter bulundu:")
    print()
    
    for i, file_path in enumerate(character_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            
            name = char_data.get('name', 'İsimsiz')
            race = char_data.get('race', 'Bilinmeyen')
            character_class = char_data.get('character_class', 'Bilinmeyen')
            level = char_data.get('level', 1)
            
            print(f"{i}. {name} - Seviye {level} {race} {character_class}")
            
        except Exception as e:
            print(f"{i}. {file_path.name} (Okunamadı: {e})")

def show_dnd_info():
    """D&D bilgilerini göster"""
    print("\n" + "=" * 60)
    print("D&D 5e Bilgileri")
    print("=" * 60)
    print()
    print("Mevcut Özellikler:")
    print()
    print("• 14 Farklı Irk (Human, Elf, Dwarf, vb.)")
    print("• 14 Farklı Sınıf (Fighter, Wizard, Rogue, vb.)")
    print("• 42 Farklı Feat")
    print("• 98 Farklı Büyü (37 Cantrip + 61 1. Seviye)")
    print("• 1000+ Eşya (Silahlar, Zırhlar, Büyülü Eşyalar)")
    print("• Tam D&D 5e Uyumluluğu")
    print("• PDF Export")
    print("• Karakter Kaydetme/Yükleme")
    print()
    print("Desteklenen Sistemler:")
    print("• Player's Handbook (PHB)")
    print("• Xanathar's Guide to Everything")
    print("• Tasha's Cauldron of Everything")
    print("• Fizban's Treasury of Dragons")
    print("• Ve daha fazlası...")

def dnd_main():
    """D&D ana fonksiyonu"""
    while True:
        show_dnd_menu()
        choice = get_dnd_choice()
        
        if choice == '1':
            create_new_character()
        elif choice == '2':
            view_characters()
        elif choice == '3':
            print("\nKarakter istatistikleri özelliği yakında gelecek!")
        elif choice == '4':
            show_dnd_info()
        elif choice == '5':
            break
        
        print("\n" + "-" * 60 + "\n")
        
        # Devam etmek isteyip istemediğini sor
        try:
            continue_choice = input("D&D menüsünde kalmak ister misiniz? (e/h): ").strip().lower()
            if continue_choice not in ['e', 'evet', 'y', 'yes']:
                break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    dnd_main()
