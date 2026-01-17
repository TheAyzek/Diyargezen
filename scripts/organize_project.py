"""
Proje dosyalarini organize et
"""
import shutil
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent

def organize_scripts():
    """Scripts klasörünü organize et"""
    scripts_dir = project_root / "scripts"
    
    # Test dosyaları
    test_files = list(scripts_dir.glob("test_*.py")) + [scripts_dir / "run_all_tests.py"]
    tests_dir = scripts_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    print(f"Test dosyalari tasiniyor: {len(test_files)} dosya")
    for f in test_files:
        if f.exists():
            dest = tests_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Scraping dosyaları
    scraping_files = (
        list(scripts_dir.glob("scrape_*.py")) +
        [scripts_dir / "run_all_batches.py", scripts_dir / "run_all_batches.ps1"]
    )
    scraping_dir = scripts_dir / "scraping"
    scraping_dir.mkdir(exist_ok=True)
    
    print(f"\nScraping dosyalari tasiniyor: {len(scraping_files)} dosya")
    for f in scraping_files:
        if f.exists():
            dest = scraping_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Analiz dosyaları
    analysis_files = (
        list(scripts_dir.glob("analyze_*.py")) +
        list(scripts_dir.glob("check_*.py")) +
        list(scripts_dir.glob("debug_*.py")) +
        list(scripts_dir.glob("find_*.py")) +
        [scripts_dir / "detailed_5esrd_analysis.py",
         scripts_dir / "detailed_feats_analysis.py",
         scripts_dir / "extract_race_details.py",
         scripts_dir / "final_mm_report.py"]
    )
    analysis_dir = scripts_dir / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    
    print(f"\nAnaliz dosyalari tasiniyor: {len(analysis_files)} dosya")
    for f in analysis_files:
        if f.exists():
            dest = analysis_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Bakım dosyaları
    maintenance_files = (
        list(scripts_dir.glob("clean_*.py")) +
        list(scripts_dir.glob("merge_*.py")) +
        list(scripts_dir.glob("fix_*.py"))
    )
    maintenance_dir = scripts_dir / "maintenance"
    maintenance_dir.mkdir(exist_ok=True)
    
    print(f"\nBakim dosyalari tasiniyor: {len(maintenance_files)} dosya")
    for f in maintenance_files:
        if f.exists():
            dest = maintenance_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def organize_data():
    """Data klasörünü organize et"""
    data_dir = project_root / "data"
    
    # Cache dosyaları
    cache_files = list(data_dir.glob("*_cache.json"))
    cache_dir = data_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    
    print(f"\nCache dosyalari tasiniyor: {len(cache_files)} dosya")
    for f in cache_files:
        if f.exists():
            dest = cache_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Log dosyaları
    log_files = list(data_dir.glob("*_log.txt"))
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    print(f"\nLog dosyalari tasiniyor: {len(log_files)} dosya")
    for f in log_files:
        if f.exists():
            dest = logs_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def organize_root_files():
    """Root klasöründeki dosyaları organize et"""
    root = project_root
    
    # Test dosyaları -> scripts/tests/
    test_files = [
        root / "test_project.py",
        root / "elf_race_test.json",
        root / "human_race_test.json"
    ]
    tests_dir = root / "scripts" / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    print(f"\nRoot'taki test dosyalari tasiniyor: {len(test_files)} dosya")
    for f in test_files:
        if f.exists():
            dest = tests_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Geçici HTML dosyaları -> scripts/temp/
    html_files = list(root.glob("*_*.html")) + list(root.glob("test_*.html"))
    temp_dir = root / "scripts" / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    print(f"\nGecici HTML dosyalari tasiniyor: {len(html_files)} dosya")
    for f in html_files:
        if f.exists() and f.name not in ["xref-Diyargezen.html"]:  # Build dosyasını atla
            dest = temp_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # MD dosyaları -> docs/ (sadece belirli olanlar)
    md_files_to_move = [
        "PROJE_SEMASI.md",
        "SISTEM_DURUM_RAPORU.md",
        "TEST_SUITE_REPORT.md",
        "SISTEM_KONTROL_RAPORU.md",
        "TEST_RAPORU.md",
        "GEREKSINIM_KARSILASTIRMA.md",
        "EXE_BUILD_KILAVZU.md",
        "SEMALAR_OZET.md",
        "GORSEL_SEMALAR.md",
        "DETAYLI_SEMALAR.md",
        "SUNUM_NOTLARI.md",
        "PROJE_ORGANIZASYON_PLANI.md"
    ]
    docs_dir = root / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    print(f"\nRoot'taki MD dosyalari tasiniyor: {len(md_files_to_move)} dosya")
    for md_file in md_files_to_move:
        f = root / md_file
        if f.exists():
            dest = docs_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # ASCII_SEMALAR.txt -> docs/ veya sil
    ascii_file = root / "ASCII_SEMALAR.txt"
    if ascii_file.exists():
        dest = docs_dir / "ASCII_SEMALAR.txt"
        if not dest.exists():
            shutil.move(str(ascii_file), str(dest))
            print(f"  -> ASCII_SEMALAR.txt")

def organize_characters():
    """Characters klasöründeki PDF dosyalarını organize et"""
    chars_dir = project_root / "characters"
    pdf_files = list(chars_dir.glob("*.pdf"))
    exports_dir = chars_dir / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    print(f"\nPDF dosyalari tasiniyor: {len(pdf_files)} dosya")
    for f in pdf_files:
        if f.exists():
            dest = exports_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def main():
    """Ana organizasyon fonksiyonu"""
    print("=" * 70)
    print("PROJE ORGANIZASYONU BASLIYOR")
    print("=" * 70)
    print()
    
    try:
        organize_scripts()
        organize_data()
        organize_root_files()
        organize_characters()
        
        print("\n" + "=" * 70)
        print("ORGANIZASYON TAMAMLANDI!")
        print("=" * 70)
        print("\nNOT: Import path'lerini guncellemeyi unutmayin!")
        
    except Exception as e:
        print(f"\nHATA: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


Proje dosyalarini organize et
"""
import shutil
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent

def organize_scripts():
    """Scripts klasörünü organize et"""
    scripts_dir = project_root / "scripts"
    
    # Test dosyaları
    test_files = list(scripts_dir.glob("test_*.py")) + [scripts_dir / "run_all_tests.py"]
    tests_dir = scripts_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    print(f"Test dosyalari tasiniyor: {len(test_files)} dosya")
    for f in test_files:
        if f.exists():
            dest = tests_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Scraping dosyaları
    scraping_files = (
        list(scripts_dir.glob("scrape_*.py")) +
        [scripts_dir / "run_all_batches.py", scripts_dir / "run_all_batches.ps1"]
    )
    scraping_dir = scripts_dir / "scraping"
    scraping_dir.mkdir(exist_ok=True)
    
    print(f"\nScraping dosyalari tasiniyor: {len(scraping_files)} dosya")
    for f in scraping_files:
        if f.exists():
            dest = scraping_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Analiz dosyaları
    analysis_files = (
        list(scripts_dir.glob("analyze_*.py")) +
        list(scripts_dir.glob("check_*.py")) +
        list(scripts_dir.glob("debug_*.py")) +
        list(scripts_dir.glob("find_*.py")) +
        [scripts_dir / "detailed_5esrd_analysis.py",
         scripts_dir / "detailed_feats_analysis.py",
         scripts_dir / "extract_race_details.py",
         scripts_dir / "final_mm_report.py"]
    )
    analysis_dir = scripts_dir / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    
    print(f"\nAnaliz dosyalari tasiniyor: {len(analysis_files)} dosya")
    for f in analysis_files:
        if f.exists():
            dest = analysis_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Bakım dosyaları
    maintenance_files = (
        list(scripts_dir.glob("clean_*.py")) +
        list(scripts_dir.glob("merge_*.py")) +
        list(scripts_dir.glob("fix_*.py"))
    )
    maintenance_dir = scripts_dir / "maintenance"
    maintenance_dir.mkdir(exist_ok=True)
    
    print(f"\nBakim dosyalari tasiniyor: {len(maintenance_files)} dosya")
    for f in maintenance_files:
        if f.exists():
            dest = maintenance_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def organize_data():
    """Data klasörünü organize et"""
    data_dir = project_root / "data"
    
    # Cache dosyaları
    cache_files = list(data_dir.glob("*_cache.json"))
    cache_dir = data_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    
    print(f"\nCache dosyalari tasiniyor: {len(cache_files)} dosya")
    for f in cache_files:
        if f.exists():
            dest = cache_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Log dosyaları
    log_files = list(data_dir.glob("*_log.txt"))
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    print(f"\nLog dosyalari tasiniyor: {len(log_files)} dosya")
    for f in log_files:
        if f.exists():
            dest = logs_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def organize_root_files():
    """Root klasöründeki dosyaları organize et"""
    root = project_root
    
    # Test dosyaları -> scripts/tests/
    test_files = [
        root / "test_project.py",
        root / "elf_race_test.json",
        root / "human_race_test.json"
    ]
    tests_dir = root / "scripts" / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    print(f"\nRoot'taki test dosyalari tasiniyor: {len(test_files)} dosya")
    for f in test_files:
        if f.exists():
            dest = tests_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Geçici HTML dosyaları -> scripts/temp/
    html_files = list(root.glob("*_*.html")) + list(root.glob("test_*.html"))
    temp_dir = root / "scripts" / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    print(f"\nGecici HTML dosyalari tasiniyor: {len(html_files)} dosya")
    for f in html_files:
        if f.exists() and f.name not in ["xref-Diyargezen.html"]:  # Build dosyasını atla
            dest = temp_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # MD dosyaları -> docs/ (sadece belirli olanlar)
    md_files_to_move = [
        "PROJE_SEMASI.md",
        "SISTEM_DURUM_RAPORU.md",
        "TEST_SUITE_REPORT.md",
        "SISTEM_KONTROL_RAPORU.md",
        "TEST_RAPORU.md",
        "GEREKSINIM_KARSILASTIRMA.md",
        "EXE_BUILD_KILAVZU.md",
        "SEMALAR_OZET.md",
        "GORSEL_SEMALAR.md",
        "DETAYLI_SEMALAR.md",
        "SUNUM_NOTLARI.md",
        "PROJE_ORGANIZASYON_PLANI.md"
    ]
    docs_dir = root / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    print(f"\nRoot'taki MD dosyalari tasiniyor: {len(md_files_to_move)} dosya")
    for md_file in md_files_to_move:
        f = root / md_file
        if f.exists():
            dest = docs_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # ASCII_SEMALAR.txt -> docs/ veya sil
    ascii_file = root / "ASCII_SEMALAR.txt"
    if ascii_file.exists():
        dest = docs_dir / "ASCII_SEMALAR.txt"
        if not dest.exists():
            shutil.move(str(ascii_file), str(dest))
            print(f"  -> ASCII_SEMALAR.txt")

def organize_characters():
    """Characters klasöründeki PDF dosyalarını organize et"""
    chars_dir = project_root / "characters"
    pdf_files = list(chars_dir.glob("*.pdf"))
    exports_dir = chars_dir / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    print(f"\nPDF dosyalari tasiniyor: {len(pdf_files)} dosya")
    for f in pdf_files:
        if f.exists():
            dest = exports_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def main():
    """Ana organizasyon fonksiyonu"""
    print("=" * 70)
    print("PROJE ORGANIZASYONU BASLIYOR")
    print("=" * 70)
    print()
    
    try:
        organize_scripts()
        organize_data()
        organize_root_files()
        organize_characters()
        
        print("\n" + "=" * 70)
        print("ORGANIZASYON TAMAMLANDI!")
        print("=" * 70)
        print("\nNOT: Import path'lerini guncellemeyi unutmayin!")
        
    except Exception as e:
        print(f"\nHATA: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())




Proje dosyalarini organize et
"""
import shutil
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent

def organize_scripts():
    """Scripts klasörünü organize et"""
    scripts_dir = project_root / "scripts"
    
    # Test dosyaları
    test_files = list(scripts_dir.glob("test_*.py")) + [scripts_dir / "run_all_tests.py"]
    tests_dir = scripts_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    print(f"Test dosyalari tasiniyor: {len(test_files)} dosya")
    for f in test_files:
        if f.exists():
            dest = tests_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Scraping dosyaları
    scraping_files = (
        list(scripts_dir.glob("scrape_*.py")) +
        [scripts_dir / "run_all_batches.py", scripts_dir / "run_all_batches.ps1"]
    )
    scraping_dir = scripts_dir / "scraping"
    scraping_dir.mkdir(exist_ok=True)
    
    print(f"\nScraping dosyalari tasiniyor: {len(scraping_files)} dosya")
    for f in scraping_files:
        if f.exists():
            dest = scraping_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Analiz dosyaları
    analysis_files = (
        list(scripts_dir.glob("analyze_*.py")) +
        list(scripts_dir.glob("check_*.py")) +
        list(scripts_dir.glob("debug_*.py")) +
        list(scripts_dir.glob("find_*.py")) +
        [scripts_dir / "detailed_5esrd_analysis.py",
         scripts_dir / "detailed_feats_analysis.py",
         scripts_dir / "extract_race_details.py",
         scripts_dir / "final_mm_report.py"]
    )
    analysis_dir = scripts_dir / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    
    print(f"\nAnaliz dosyalari tasiniyor: {len(analysis_files)} dosya")
    for f in analysis_files:
        if f.exists():
            dest = analysis_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Bakım dosyaları
    maintenance_files = (
        list(scripts_dir.glob("clean_*.py")) +
        list(scripts_dir.glob("merge_*.py")) +
        list(scripts_dir.glob("fix_*.py"))
    )
    maintenance_dir = scripts_dir / "maintenance"
    maintenance_dir.mkdir(exist_ok=True)
    
    print(f"\nBakim dosyalari tasiniyor: {len(maintenance_files)} dosya")
    for f in maintenance_files:
        if f.exists():
            dest = maintenance_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def organize_data():
    """Data klasörünü organize et"""
    data_dir = project_root / "data"
    
    # Cache dosyaları
    cache_files = list(data_dir.glob("*_cache.json"))
    cache_dir = data_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    
    print(f"\nCache dosyalari tasiniyor: {len(cache_files)} dosya")
    for f in cache_files:
        if f.exists():
            dest = cache_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Log dosyaları
    log_files = list(data_dir.glob("*_log.txt"))
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    print(f"\nLog dosyalari tasiniyor: {len(log_files)} dosya")
    for f in log_files:
        if f.exists():
            dest = logs_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def organize_root_files():
    """Root klasöründeki dosyaları organize et"""
    root = project_root
    
    # Test dosyaları -> scripts/tests/
    test_files = [
        root / "test_project.py",
        root / "elf_race_test.json",
        root / "human_race_test.json"
    ]
    tests_dir = root / "scripts" / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    print(f"\nRoot'taki test dosyalari tasiniyor: {len(test_files)} dosya")
    for f in test_files:
        if f.exists():
            dest = tests_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Geçici HTML dosyaları -> scripts/temp/
    html_files = list(root.glob("*_*.html")) + list(root.glob("test_*.html"))
    temp_dir = root / "scripts" / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    print(f"\nGecici HTML dosyalari tasiniyor: {len(html_files)} dosya")
    for f in html_files:
        if f.exists() and f.name not in ["xref-Diyargezen.html"]:  # Build dosyasını atla
            dest = temp_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # MD dosyaları -> docs/ (sadece belirli olanlar)
    md_files_to_move = [
        "PROJE_SEMASI.md",
        "SISTEM_DURUM_RAPORU.md",
        "TEST_SUITE_REPORT.md",
        "SISTEM_KONTROL_RAPORU.md",
        "TEST_RAPORU.md",
        "GEREKSINIM_KARSILASTIRMA.md",
        "EXE_BUILD_KILAVZU.md",
        "SEMALAR_OZET.md",
        "GORSEL_SEMALAR.md",
        "DETAYLI_SEMALAR.md",
        "SUNUM_NOTLARI.md",
        "PROJE_ORGANIZASYON_PLANI.md"
    ]
    docs_dir = root / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    print(f"\nRoot'taki MD dosyalari tasiniyor: {len(md_files_to_move)} dosya")
    for md_file in md_files_to_move:
        f = root / md_file
        if f.exists():
            dest = docs_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # ASCII_SEMALAR.txt -> docs/ veya sil
    ascii_file = root / "ASCII_SEMALAR.txt"
    if ascii_file.exists():
        dest = docs_dir / "ASCII_SEMALAR.txt"
        if not dest.exists():
            shutil.move(str(ascii_file), str(dest))
            print(f"  -> ASCII_SEMALAR.txt")

def organize_characters():
    """Characters klasöründeki PDF dosyalarını organize et"""
    chars_dir = project_root / "characters"
    pdf_files = list(chars_dir.glob("*.pdf"))
    exports_dir = chars_dir / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    print(f"\nPDF dosyalari tasiniyor: {len(pdf_files)} dosya")
    for f in pdf_files:
        if f.exists():
            dest = exports_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def main():
    """Ana organizasyon fonksiyonu"""
    print("=" * 70)
    print("PROJE ORGANIZASYONU BASLIYOR")
    print("=" * 70)
    print()
    
    try:
        organize_scripts()
        organize_data()
        organize_root_files()
        organize_characters()
        
        print("\n" + "=" * 70)
        print("ORGANIZASYON TAMAMLANDI!")
        print("=" * 70)
        print("\nNOT: Import path'lerini guncellemeyi unutmayin!")
        
    except Exception as e:
        print(f"\nHATA: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


Proje dosyalarini organize et
"""
import shutil
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent

def organize_scripts():
    """Scripts klasörünü organize et"""
    scripts_dir = project_root / "scripts"
    
    # Test dosyaları
    test_files = list(scripts_dir.glob("test_*.py")) + [scripts_dir / "run_all_tests.py"]
    tests_dir = scripts_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    print(f"Test dosyalari tasiniyor: {len(test_files)} dosya")
    for f in test_files:
        if f.exists():
            dest = tests_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Scraping dosyaları
    scraping_files = (
        list(scripts_dir.glob("scrape_*.py")) +
        [scripts_dir / "run_all_batches.py", scripts_dir / "run_all_batches.ps1"]
    )
    scraping_dir = scripts_dir / "scraping"
    scraping_dir.mkdir(exist_ok=True)
    
    print(f"\nScraping dosyalari tasiniyor: {len(scraping_files)} dosya")
    for f in scraping_files:
        if f.exists():
            dest = scraping_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Analiz dosyaları
    analysis_files = (
        list(scripts_dir.glob("analyze_*.py")) +
        list(scripts_dir.glob("check_*.py")) +
        list(scripts_dir.glob("debug_*.py")) +
        list(scripts_dir.glob("find_*.py")) +
        [scripts_dir / "detailed_5esrd_analysis.py",
         scripts_dir / "detailed_feats_analysis.py",
         scripts_dir / "extract_race_details.py",
         scripts_dir / "final_mm_report.py"]
    )
    analysis_dir = scripts_dir / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    
    print(f"\nAnaliz dosyalari tasiniyor: {len(analysis_files)} dosya")
    for f in analysis_files:
        if f.exists():
            dest = analysis_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Bakım dosyaları
    maintenance_files = (
        list(scripts_dir.glob("clean_*.py")) +
        list(scripts_dir.glob("merge_*.py")) +
        list(scripts_dir.glob("fix_*.py"))
    )
    maintenance_dir = scripts_dir / "maintenance"
    maintenance_dir.mkdir(exist_ok=True)
    
    print(f"\nBakim dosyalari tasiniyor: {len(maintenance_files)} dosya")
    for f in maintenance_files:
        if f.exists():
            dest = maintenance_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def organize_data():
    """Data klasörünü organize et"""
    data_dir = project_root / "data"
    
    # Cache dosyaları
    cache_files = list(data_dir.glob("*_cache.json"))
    cache_dir = data_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    
    print(f"\nCache dosyalari tasiniyor: {len(cache_files)} dosya")
    for f in cache_files:
        if f.exists():
            dest = cache_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Log dosyaları
    log_files = list(data_dir.glob("*_log.txt"))
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    print(f"\nLog dosyalari tasiniyor: {len(log_files)} dosya")
    for f in log_files:
        if f.exists():
            dest = logs_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def organize_root_files():
    """Root klasöründeki dosyaları organize et"""
    root = project_root
    
    # Test dosyaları -> scripts/tests/
    test_files = [
        root / "test_project.py",
        root / "elf_race_test.json",
        root / "human_race_test.json"
    ]
    tests_dir = root / "scripts" / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    print(f"\nRoot'taki test dosyalari tasiniyor: {len(test_files)} dosya")
    for f in test_files:
        if f.exists():
            dest = tests_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # Geçici HTML dosyaları -> scripts/temp/
    html_files = list(root.glob("*_*.html")) + list(root.glob("test_*.html"))
    temp_dir = root / "scripts" / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    print(f"\nGecici HTML dosyalari tasiniyor: {len(html_files)} dosya")
    for f in html_files:
        if f.exists() and f.name not in ["xref-Diyargezen.html"]:  # Build dosyasını atla
            dest = temp_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # MD dosyaları -> docs/ (sadece belirli olanlar)
    md_files_to_move = [
        "PROJE_SEMASI.md",
        "SISTEM_DURUM_RAPORU.md",
        "TEST_SUITE_REPORT.md",
        "SISTEM_KONTROL_RAPORU.md",
        "TEST_RAPORU.md",
        "GEREKSINIM_KARSILASTIRMA.md",
        "EXE_BUILD_KILAVZU.md",
        "SEMALAR_OZET.md",
        "GORSEL_SEMALAR.md",
        "DETAYLI_SEMALAR.md",
        "SUNUM_NOTLARI.md",
        "PROJE_ORGANIZASYON_PLANI.md"
    ]
    docs_dir = root / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    print(f"\nRoot'taki MD dosyalari tasiniyor: {len(md_files_to_move)} dosya")
    for md_file in md_files_to_move:
        f = root / md_file
        if f.exists():
            dest = docs_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")
    
    # ASCII_SEMALAR.txt -> docs/ veya sil
    ascii_file = root / "ASCII_SEMALAR.txt"
    if ascii_file.exists():
        dest = docs_dir / "ASCII_SEMALAR.txt"
        if not dest.exists():
            shutil.move(str(ascii_file), str(dest))
            print(f"  -> ASCII_SEMALAR.txt")

def organize_characters():
    """Characters klasöründeki PDF dosyalarını organize et"""
    chars_dir = project_root / "characters"
    pdf_files = list(chars_dir.glob("*.pdf"))
    exports_dir = chars_dir / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    print(f"\nPDF dosyalari tasiniyor: {len(pdf_files)} dosya")
    for f in pdf_files:
        if f.exists():
            dest = exports_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                print(f"  -> {f.name}")

def main():
    """Ana organizasyon fonksiyonu"""
    print("=" * 70)
    print("PROJE ORGANIZASYONU BASLIYOR")
    print("=" * 70)
    print()
    
    try:
        organize_scripts()
        organize_data()
        organize_root_files()
        organize_characters()
        
        print("\n" + "=" * 70)
        print("ORGANIZASYON TAMAMLANDI!")
        print("=" * 70)
        print("\nNOT: Import path'lerini guncellemeyi unutmayin!")
        
    except Exception as e:
        print(f"\nHATA: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())






