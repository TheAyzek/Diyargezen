# main.py
"""
Diyargezer - Evrensel FRP Karakter Oluşturucu
Ana giriş noktası - Sistem seçimi ve yönlendirme
"""

import sys
from pathlib import Path

# Ana dizini Python path'e ekle
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

def show_main_menu():
    """Ana menüyü göster"""
    print("=" * 60)
    print("Diyargezer - Evrensel FRP Karakter Oluşturucu")
    print("=" * 60)
    print()
    print("Hangi sistem için karakter oluşturmak istersiniz?")
    print()
    print("1. 🎨 Modern GUI Arayüzü (ÖNERİLEN - Tüm Sistemler)")
    print("2. Dungeons & Dragons 5e")
    print("3. Pathfinder 1e")
    print("4. Mutants & Masterminds")
    print("5. Vampire: The Masquerade")
    print("6. Çıkış")
    print()

def get_user_choice():
    """Kullanıcı seçimini al"""
    while True:
        try:
            choice = input("Seçiminizi yapın (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            else:
                print("Geçersiz seçim! Lütfen 1-6 arası bir sayı girin.")
        except KeyboardInterrupt:
            print("\nProgram kapatılıyor...")
            sys.exit(0)

def launch_gui_system():
    """GUI Arayüzünü başlat - Tüm Sistemler"""
    print("\nModern GUI Arayüzü başlatılıyor... Lütfen bekleyin.")
    try:
        from gui.modern_gui import main as modern_gui_main
        modern_gui_main()
    except ImportError as e:
        print(f"Modern GUI yüklenirken hata: {e}")
        print("Eski GUI'ye geçiliyor...")
        try:
            from gui.app import main as old_gui_main
            old_gui_main()
        except ImportError as e2:
            print(f"Eski GUI de yüklenemedi: {e2}")
            print("GUI sistemi kullanılamıyor. Lütfen bağımlılıkları kontrol edin.")
        print(f"GUI başlatılamadı: {e}")
        print("PySide6 kurulu olduğundan emin olun: pip install PySide6")
    except Exception as e:
        print(f"GUI hatası: {e}")

def launch_dnd_system():
    """D&D sistemini başlat - Sadece GUI"""
    print("\nD&D 5e GUI sistemine hoş geldiniz!")
    print("Tüm D&D özellikleri hazır:")
    print("• 23 Irk, 14 Sınıf")
    print("• 42 Feat, 2 Büyü")
    print("• 1000+ Eşya")
    print("• PDF Export")
    print("• GUI Arayüzü")
    print()
    
    launch_dnd_gui()

def launch_dnd_gui():
    """D&D GUI sistemini başlat"""
    print("\nD&D GUI başlatılıyor...")
    try:
        # GUI'yi başlat
        import subprocess
        import sys
        
        # GUI dosyasını çalıştır
        gui_path = BASE_DIR / "gui" / "app.py"
        if gui_path.exists():
            print("GUI başlatılıyor... Lütfen bekleyin.")
            subprocess.run([sys.executable, str(gui_path)])
        else:
            print("GUI dosyası bulunamadı!")
            
    except Exception as e:
        print(f"GUI başlatılamadı: {e}")
        print("GUI başlatılamadı. Lütfen PySide6 kurulu olduğundan emin olun.")

# Terminal sistemi kaldırıldı - sadece GUI kullanılıyor

def launch_mm_system():
    """M&M sistemini başlat - Factory Pattern ile"""
    print("\nMutants & Masterminds GUI sistemine hoş geldiniz!")
    print("Tüm M&M özellikleri hazır:")
    print("• Power Level sistemi")
    print("• PL limit validasyonu")
    print("• Power ve Advantage yönetimi")
    print("• PDF Export")
    print("• GUI Arayüzü")
    print()
    
    try:
        from creators import CharacterFactory
        creator = CharacterFactory.create_creator("mm3e")
        character = creator.create_character()
        
        # Karakteri kaydet
        filename = f"{character['name'].lower().replace(' ', '_')}_mm3e"
        if creator.save_character(character, filename):
            print(f"\nKarakter '{character['name']}' kaydedildi: {filename}.json")
        
        print("\nKarakter özeti:")
        print(f"İsim: {character['name']}")
        print(f"Sistem: {character['system']}")
        print(f"Power Level: {character['power_level']} (PL {character['pl_value']})")
        print(f"Kalan PP: {character['remaining_power_points']}")
        
    except Exception as e:
        print(f"M&M karakter oluşturma hatası: {e}")

def launch_vtm_system():
    """VtM sistemini başlat - Factory Pattern ile"""
    print("\nVampire: The Masquerade GUI sistemine hoş geldiniz!")
    print("Tüm VtM özellikleri hazır:")
    print("• Klan sistemi")
    print("• Attribute/Skill dağılım sayaçları")
    print("• Discipline yönetimi")
    print("• PDF Export")
    print("• GUI Arayüzü")
    print()
    
    try:
        from creators import CharacterFactory
        creator = CharacterFactory.create_creator("vtm5e")
        character = creator.create_character()
        
        # Karakteri kaydet
        filename = f"{character['name'].lower().replace(' ', '_')}_vtm5e"
        if creator.save_character(character, filename):
            print(f"\nKarakter '{character['name']}' kaydedildi: {filename}.json")
        
        print("\nKarakter özeti:")
        print(f"İsim: {character['name']}")
        print(f"Sistem: {character['system']}")
        print(f"Klan: {character['clan']}")
        print(f"Predator Type: {character['predator_type']}")
        print(f"Blood Potency: {character['blood_potency']}")
        
    except Exception as e:
        print(f"VtM karakter oluşturma hatası: {e}")

def launch_pathfinder_system():
    """Pathfinder 1e sistemini başlat - Factory Pattern ile"""
    print("\nPathfinder 1e CLI sistemine hoş geldiniz!")
    print("Tüm Pathfinder özellikleri hazır:")
    print("• 77 Irk")
    print("• 73 Sınıf")
    print("• 421 Feat")
    print("• 500+ Büyü")
    print("• BAB/Saves hesaplamaları")
    print("• Skill ranks sistemi")
    print("• Feat prerequisites")
    print()
    
    try:
        from creators import CharacterFactory
        creator = CharacterFactory.create_creator("pathfinder1e")
        character = creator.create_character()
        
        # Karakteri kaydet
        filename = f"{character['name'].lower().replace(' ', '_')}_pf1e"
        if creator.save_character(character, filename):
            print(f"\nKarakter '{character['name']}' kaydedildi: {filename}.json")
        
        print("\nKarakter özeti:")
        print(f"İsim: {character['name']}")
        print(f"Sistem: {character['system']}")
        print(f"Irk: {character['race']}")
        print(f"Sınıf: {character['class']}")
        print(f"Seviye: {character['level']}")
        print(f"BAB: {character['bab']}")
        print(f"Saves: {character['saves']}")
        
    except Exception as e:
        print(f"Pathfinder karakter oluşturma hatası: {e}")

def main():
    """Ana fonksiyon"""
    try:
        while True:
            show_main_menu()
            choice = get_user_choice()
            
            if choice == '1':
                launch_gui_system()
            elif choice == '2':
                launch_dnd_system()
            elif choice == '3':
                launch_pathfinder_system()
            elif choice == '4':
                launch_mm_system()
            elif choice == '5':
                launch_vtm_system()
            elif choice == '6':
                print("\nHoşça kalın! Maceralarınızda başarılar!")
                break
            
            print("\n" + "-" * 60 + "\n")
            
            # Devam etmek isteyip istemediğini sor
            try:
                continue_choice = input("Ana menüye dönmek ister misiniz? (e/h): ").strip().lower()
                if continue_choice not in ['e', 'evet', 'y', 'yes']:
                    print("\nHoşça kalın! Maceralarınızda başarılar!")
                    break
            except KeyboardInterrupt:
                print("\n\nHoşça kalın! Maceralarınızda başarılar!")
                break
                
    except KeyboardInterrupt:
        print("\n\nProgram kapatılıyor...")
    except Exception as e:
        print(f"\nBeklenmeyen bir hata oluştu: {e}")
        print("Program kapatılıyor...")

if __name__ == "__main__":
    main()