"""
Organizasyon sonrası path'leri güncelle
"""
import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/update_paths -> scripts -> project_root

def update_paths_in_file(file_path: Path):
    """Bir dosyadaki path'leri güncelle"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Cache dosyaları
        content = re.sub(
            r'Path\(["\']data/([^"\']+)_cache\.json["\']\)',
            r'Path("data/cache/\1_cache.json")',
            content
        )
        
        # Log dosyaları
        content = re.sub(
            r'Path\(["\']data/([^"\']+)_scraping_log\.txt["\']\)',
            r'Path("data/logs/\1_scraping_log.txt")',
            content
        )
        
        # String path'ler (cache)
        content = re.sub(
            r'["\']data/([^"\']+)_cache\.json["\']',
            r'"data/cache/\1_cache.json"',
            content
        )
        
        # String path'ler (logs)
        content = re.sub(
            r'["\']data/([^"\']+)_scraping_log\.txt["\']',
            r'"data/logs/\1_scraping_log.txt"',
            content
        )
        
        # project_root / "data" / "cache" / "*.json" formatı
        content = re.sub(
            r'project_root\s*/\s*["\']data["\']\s*/\s*["\']([^"\']+)_cache\.json["\']',
            r'project_root / "data/cache/\1_cache.json"',
            content
        )
        
        content = re.sub(
            r'project_root\s*/\s*["\']data["\']\s*/\s*["\']([^"\']+)_scraping_log\.txt["\']',
            r'project_root / "data/logs/\1_scraping_log.txt"',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  HATA: {file_path.name}: {e}")
        return False

def main():
    """Tüm script dosyalarındaki path'leri güncelle"""
    print("=" * 70)
    print("PATH GUNCELLEME BASLIYOR")
    print("=" * 70)
    print()
    
    # Scripts klasöründeki tüm Python dosyalarını bul
    scripts_dir = project_root / "scripts"
    python_files = list(scripts_dir.rglob("*.py"))
    
    # Utils klasöründeki ilgili dosyaları bul
    utils_files = [
        project_root / "utils" / "dnd_5esrd_scraper.py"
    ]
    
    all_files = python_files + utils_files
    
    updated_count = 0
    for file_path in all_files:
        if "organize_project.py" in str(file_path) or "update_paths" in str(file_path):
            continue  # Kendi kendini güncelleme
        
        if update_paths_in_file(file_path):
            print(f"  Guncellendi: {file_path.relative_to(project_root)}")
            updated_count += 1
    
    print(f"\nToplam {updated_count} dosya guncellendi.")
    print("\nPath guncelleme tamamlandi!")

if __name__ == "__main__":
    main()


"""
import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/update_paths -> scripts -> project_root

def update_paths_in_file(file_path: Path):
    """Bir dosyadaki path'leri güncelle"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Cache dosyaları
        content = re.sub(
            r'Path\(["\']data/([^"\']+)_cache\.json["\']\)',
            r'Path("data/cache/\1_cache.json")',
            content
        )
        
        # Log dosyaları
        content = re.sub(
            r'Path\(["\']data/([^"\']+)_scraping_log\.txt["\']\)',
            r'Path("data/logs/\1_scraping_log.txt")',
            content
        )
        
        # String path'ler (cache)
        content = re.sub(
            r'["\']data/([^"\']+)_cache\.json["\']',
            r'"data/cache/\1_cache.json"',
            content
        )
        
        # String path'ler (logs)
        content = re.sub(
            r'["\']data/([^"\']+)_scraping_log\.txt["\']',
            r'"data/logs/\1_scraping_log.txt"',
            content
        )
        
        # project_root / "data" / "cache" / "*.json" formatı
        content = re.sub(
            r'project_root\s*/\s*["\']data["\']\s*/\s*["\']([^"\']+)_cache\.json["\']',
            r'project_root / "data/cache/\1_cache.json"',
            content
        )
        
        content = re.sub(
            r'project_root\s*/\s*["\']data["\']\s*/\s*["\']([^"\']+)_scraping_log\.txt["\']',
            r'project_root / "data/logs/\1_scraping_log.txt"',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  HATA: {file_path.name}: {e}")
        return False

def main():
    """Tüm script dosyalarındaki path'leri güncelle"""
    print("=" * 70)
    print("PATH GUNCELLEME BASLIYOR")
    print("=" * 70)
    print()
    
    # Scripts klasöründeki tüm Python dosyalarını bul
    scripts_dir = project_root / "scripts"
    python_files = list(scripts_dir.rglob("*.py"))
    
    # Utils klasöründeki ilgili dosyaları bul
    utils_files = [
        project_root / "utils" / "dnd_5esrd_scraper.py"
    ]
    
    all_files = python_files + utils_files
    
    updated_count = 0
    for file_path in all_files:
        if "organize_project.py" in str(file_path) or "update_paths" in str(file_path):
            continue  # Kendi kendini güncelleme
        
        if update_paths_in_file(file_path):
            print(f"  Guncellendi: {file_path.relative_to(project_root)}")
            updated_count += 1
    
    print(f"\nToplam {updated_count} dosya guncellendi.")
    print("\nPath guncelleme tamamlandi!")

if __name__ == "__main__":
    main()


"""
import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/update_paths -> scripts -> project_root

def update_paths_in_file(file_path: Path):
    """Bir dosyadaki path'leri güncelle"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Cache dosyaları
        content = re.sub(
            r'Path\(["\']data/([^"\']+)_cache\.json["\']\)',
            r'Path("data/cache/\1_cache.json")',
            content
        )
        
        # Log dosyaları
        content = re.sub(
            r'Path\(["\']data/([^"\']+)_scraping_log\.txt["\']\)',
            r'Path("data/logs/\1_scraping_log.txt")',
            content
        )
        
        # String path'ler (cache)
        content = re.sub(
            r'["\']data/([^"\']+)_cache\.json["\']',
            r'"data/cache/\1_cache.json"',
            content
        )
        
        # String path'ler (logs)
        content = re.sub(
            r'["\']data/([^"\']+)_scraping_log\.txt["\']',
            r'"data/logs/\1_scraping_log.txt"',
            content
        )
        
        # project_root / "data" / "cache" / "*.json" formatı
        content = re.sub(
            r'project_root\s*/\s*["\']data["\']\s*/\s*["\']([^"\']+)_cache\.json["\']',
            r'project_root / "data/cache/\1_cache.json"',
            content
        )
        
        content = re.sub(
            r'project_root\s*/\s*["\']data["\']\s*/\s*["\']([^"\']+)_scraping_log\.txt["\']',
            r'project_root / "data/logs/\1_scraping_log.txt"',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  HATA: {file_path.name}: {e}")
        return False

def main():
    """Tüm script dosyalarındaki path'leri güncelle"""
    print("=" * 70)
    print("PATH GUNCELLEME BASLIYOR")
    print("=" * 70)
    print()
    
    # Scripts klasöründeki tüm Python dosyalarını bul
    scripts_dir = project_root / "scripts"
    python_files = list(scripts_dir.rglob("*.py"))
    
    # Utils klasöründeki ilgili dosyaları bul
    utils_files = [
        project_root / "utils" / "dnd_5esrd_scraper.py"
    ]
    
    all_files = python_files + utils_files
    
    updated_count = 0
    for file_path in all_files:
        if "organize_project.py" in str(file_path) or "update_paths" in str(file_path):
            continue  # Kendi kendini güncelleme
        
        if update_paths_in_file(file_path):
            print(f"  Guncellendi: {file_path.relative_to(project_root)}")
            updated_count += 1
    
    print(f"\nToplam {updated_count} dosya guncellendi.")
    print("\nPath guncelleme tamamlandi!")

if __name__ == "__main__":
    main()


"""
import re
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/update_paths -> scripts -> project_root

def update_paths_in_file(file_path: Path):
    """Bir dosyadaki path'leri güncelle"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Cache dosyaları
        content = re.sub(
            r'Path\(["\']data/([^"\']+)_cache\.json["\']\)',
            r'Path("data/cache/\1_cache.json")',
            content
        )
        
        # Log dosyaları
        content = re.sub(
            r'Path\(["\']data/([^"\']+)_scraping_log\.txt["\']\)',
            r'Path("data/logs/\1_scraping_log.txt")',
            content
        )
        
        # String path'ler (cache)
        content = re.sub(
            r'["\']data/([^"\']+)_cache\.json["\']',
            r'"data/cache/\1_cache.json"',
            content
        )
        
        # String path'ler (logs)
        content = re.sub(
            r'["\']data/([^"\']+)_scraping_log\.txt["\']',
            r'"data/logs/\1_scraping_log.txt"',
            content
        )
        
        # project_root / "data" / "cache" / "*.json" formatı
        content = re.sub(
            r'project_root\s*/\s*["\']data["\']\s*/\s*["\']([^"\']+)_cache\.json["\']',
            r'project_root / "data/cache/\1_cache.json"',
            content
        )
        
        content = re.sub(
            r'project_root\s*/\s*["\']data["\']\s*/\s*["\']([^"\']+)_scraping_log\.txt["\']',
            r'project_root / "data/logs/\1_scraping_log.txt"',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  HATA: {file_path.name}: {e}")
        return False

def main():
    """Tüm script dosyalarındaki path'leri güncelle"""
    print("=" * 70)
    print("PATH GUNCELLEME BASLIYOR")
    print("=" * 70)
    print()
    
    # Scripts klasöründeki tüm Python dosyalarını bul
    scripts_dir = project_root / "scripts"
    python_files = list(scripts_dir.rglob("*.py"))
    
    # Utils klasöründeki ilgili dosyaları bul
    utils_files = [
        project_root / "utils" / "dnd_5esrd_scraper.py"
    ]
    
    all_files = python_files + utils_files
    
    updated_count = 0
    for file_path in all_files:
        if "organize_project.py" in str(file_path) or "update_paths" in str(file_path):
            continue  # Kendi kendini güncelleme
        
        if update_paths_in_file(file_path):
            print(f"  Guncellendi: {file_path.relative_to(project_root)}")
            updated_count += 1
    
    print(f"\nToplam {updated_count} dosya guncellendi.")
    print("\nPath guncelleme tamamlandi!")

if __name__ == "__main__":
    main()

