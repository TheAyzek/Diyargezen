# main.py
"""
Diyargezer - Evrensel FRP Karakter Oluşturucu
Ana giriş noktası - Sistem seçimi ve yönlendirme
"""

import sys
import os
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
    print("1. Dungeons & Dragons 5e")
    print("2. Mutants & Masterminds")
    print("3. Vampire: The Masquerade")
    print("4. Çıkış")
    print()

def get_user_choice():
    """Kullanıcı seçimini al"""
    while True:
        try:
            choice = input("Seçiminizi yapın (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            else:
                print("Geçersiz seçim! Lütfen 1-4 arası bir sayı girin.")
        except KeyboardInterrupt:
            print("\nProgram kapatılıyor...")
            sys.exit(0)

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
    """M&M sistemini başlat - GUI"""
    print("\nMutants & Masterminds GUI sistemine hoş geldiniz!")
    print("Tüm M&M özellikleri hazır:")
    print("• Power Level sistemi")
    print("• PL limit validasyonu")
    print("• Power ve Advantage yönetimi")
    print("• PDF Export")
    print("• GUI Arayüzü")
    print()
    launch_dnd_gui()  # Aynı GUI, farklı sekme

def launch_vtm_system():
    """VtM sistemini başlat - GUI"""
    print("\nVampire: The Masquerade GUI sistemine hoş geldiniz!")
    print("Tüm VtM özellikleri hazır:")
    print("• Klan sistemi")
    print("• Attribute/Skill dağılım sayaçları")
    print("• Discipline yönetimi")
    print("• PDF Export")
    print("• GUI Arayüzü")
    print()
    launch_dnd_gui()  # Aynı GUI, farklı sekme

def main():
    """Ana fonksiyon"""
    try:
        while True:
            show_main_menu()
            choice = get_user_choice()
            
            if choice == '1':
                launch_dnd_system()
            elif choice == '2':
                launch_mm_system()
            elif choice == '3':
                launch_vtm_system()
            elif choice == '4':
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