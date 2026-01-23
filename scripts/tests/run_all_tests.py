"""
Tum testleri calistir ve ozet rapor olustur
"""
import sys
from pathlib import Path
import subprocess

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))


def run_test(script_path: Path, test_name: str):
    """Test script'ini calistir"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}\n")
    
    try:
        # Windows'ta encoding sorunlarını önlemek için
        import os
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        
        # Output'u yazdir (sadece sonuçları)
        if result.stdout:
            # Sadece özet kısmını göster
            lines = result.stdout.split('\n')
            summary_start = -1
            for i, line in enumerate(lines):
                if 'TEST OZETI' in line or 'TEST SONUC' in line or 'TEST OZET' in line or 'OZETI' in line:
                    summary_start = i
                    break
            
            if summary_start >= 0:
                print('\n'.join(lines[summary_start:]))
            else:
                print(result.stdout[-500:])  # Son 500 karakter
        
        if result.stderr and 'charmap' not in result.stderr and 'codec' not in result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"HATA: {e}")
        return False


def main():
    """Tum testleri calistir"""
    print("=" * 70)
    print("DIYARGEZEN KAPSAMLI TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        ("test_character_creation_comprehensive.py", "Karakter Olusturma Testleri"),
        ("test_level_up_comprehensive.py", "Level Up Testleri"),
        ("test_spell_system.py", "Spell Sistemi Testleri"),
        ("test_data_validation.py", "Veri Dogrulama Testleri"),
        ("test_export_import.py", "Export/Import Testleri"),
    ]
    
    results = []
    for script_name, test_name in tests:
        # Test dosyaları aynı klasörde (tests/)
        script = Path(__file__).parent / script_name
        if not script.exists():
            # Project root'dan dene
            script = project_root / "scripts" / "tests" / script_name
        if script.exists():
            success = run_test(script, test_name)
            results.append((test_name, success))
        else:
            print(f"UYARI: Test script bulunamadi: {script}")
            results.append((test_name, False))
    
    # Ozet
    print("\n" + "=" * 70)
    print("GENEL TEST OZETI")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[HATA]"
        print(f"{status} {test_name}")
    
    print(f"\nToplam: {passed}/{total} test suite basarili")
    
    if passed == total:
        print("\n[OK] Tum test suite'ler basarili!")
        return 0
    else:
        print(f"\n[UYARI] {total - passed} test suite basarisiz.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

