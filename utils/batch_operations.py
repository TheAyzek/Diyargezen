"""
Toplu işlemler modülü
Birden fazla karakter üzerinde aynı anda işlem yapma
"""
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime


def batch_export_characters(
    character_files: List[str],
    output_dir: Path,
    format_type: str,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """
    Birden fazla karakteri toplu olarak export et
    
    Args:
        character_files: Karakter dosya yolları listesi
        output_dir: Çıktı dizini
        format_type: Export formatı (PDF, HTML, JSON, CSV)
        progress_callback: İlerleme callback fonksiyonu (current, total, filename)
    
    Returns:
        İşlem sonuçları (başarılı, başarısız, hatalar)
    """
    results = {
        "success": [],
        "failed": [],
        "errors": []
    }
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for idx, char_file in enumerate(character_files, 1):
        try:
            # İlerleme callback
            if progress_callback:
                progress_callback(idx, len(character_files), Path(char_file).name)
            
            # Karakteri yükle
            with open(char_file, "r", encoding="utf-8") as f:
                character = json.load(f)
            
            # Dosya adını oluştur
            char_name = character.get("name", "karakter")
            # Dosya adında geçersiz karakterleri temizle
            safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            
            # Export formatına göre dosya uzantısı
            extensions = {
                "PDF": ".pdf",
                "HTML": ".html",
                "JSON": ".json",
                "CSV": ".csv"
            }
            ext = extensions.get(format_type, ".txt")
            
            output_file = output_dir / f"{safe_name}{ext}"
            
            # Export işlemi
            if format_type == "PDF":
                from utils.export_pdf import export_pdf
                export_pdf(character, output_file)
            
            elif format_type == "HTML":
                from utils.export_formats import export_character_html
                export_character_html(character, output_file)
            
            elif format_type == "JSON":
                from utils.export_formats import export_character_json
                export_character_json(character, output_file)
            
            elif format_type == "CSV":
                from utils.export_formats import export_character_csv
                export_character_csv(character, output_file)
            
            else:
                raise ValueError(f"Desteklenmeyen format: {format_type}")
            
            results["success"].append({
                "file": char_file,
                "output": str(output_file),
                "name": char_name
            })
            
        except Exception as e:
            error_msg = f"{Path(char_file).name}: {str(e)}"
            results["failed"].append(char_file)
            results["errors"].append(error_msg)
    
    return results


def batch_delete_characters(
    character_files: List[str],
    backup_dir: Optional[Path] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """
    Birden fazla karakteri toplu olarak sil (yedekleme ile)
    
    Args:
        character_files: Karakter dosya yolları listesi
        backup_dir: Yedek dizini (None ise yedekleme yapılmaz)
        progress_callback: İlerleme callback fonksiyonu
    
    Returns:
        İşlem sonuçları
    """
    results = {
        "deleted": [],
        "backed_up": [],
        "failed": [],
        "errors": []
    }
    
    # Yedek dizini oluştur
    if backup_dir:
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = backup_dir / f"backup_{timestamp}"
        backup_subdir.mkdir(parents=True, exist_ok=True)
    
    for idx, char_file in enumerate(character_files, 1):
        try:
            # İlerleme callback
            if progress_callback:
                progress_callback(idx, len(character_files), Path(char_file).name)
            
            file_path = Path(char_file)
            
            if not file_path.exists():
                results["failed"].append(char_file)
                results["errors"].append(f"{file_path.name}: Dosya bulunamadı")
                continue
            
            # Yedekleme
            if backup_dir and backup_subdir:
                backup_file = backup_subdir / file_path.name
                shutil.copy2(file_path, backup_file)
                results["backed_up"].append(str(backup_file))
            
            # Silme
            file_path.unlink()
            results["deleted"].append(char_file)
            
        except Exception as e:
            error_msg = f"{Path(char_file).name}: {str(e)}"
            results["failed"].append(char_file)
            results["errors"].append(error_msg)
    
    return results


def batch_analyze_characters(
    character_files: List[str],
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """
    Birden fazla karakteri toplu olarak analiz et
    
    Args:
        character_files: Karakter dosya yolları listesi
        progress_callback: İlerleme callback fonksiyonu
    
    Returns:
        Analiz sonuçları
    """
    results = {
        "analyses": [],
        "failed": [],
        "errors": []
    }
    
    # D&D için class_data yükle
    from utils.data_loader import load_dnd_data
    class_data = None
    try:
        from pathlib import Path
        base_dir = Path(__file__).parent.parent
        class_data = load_dnd_data(base_dir)
    except:
        pass
    
    for idx, char_file in enumerate(character_files, 1):
        try:
            # İlerleme callback
            if progress_callback:
                progress_callback(idx, len(character_files), Path(char_file).name)
            
            # Karakteri yükle
            with open(char_file, "r", encoding="utf-8") as f:
                character = json.load(f)
            
            # Analiz et
            from utils.character_statistics import analyze_character
            
            analysis = analyze_character(character, class_data)
            
            results["analyses"].append({
                "file": char_file,
                "name": character.get("name", "İsimsiz"),
                "analysis": analysis
            })
            
        except Exception as e:
            error_msg = f"{Path(char_file).name}: {str(e)}"
            results["failed"].append(char_file)
            results["errors"].append(error_msg)
    
    return results


def batch_create_templates(
    character_files: List[str],
    base_dir: Path,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """
    Birden fazla karakterden şablon oluştur
    
    Args:
        character_files: Karakter dosya yolları listesi
        base_dir: Proje ana dizini
        progress_callback: İlerleme callback fonksiyonu
    
    Returns:
        İşlem sonuçları
    """
    results = {
        "created": [],
        "failed": [],
        "errors": []
    }
    
    from utils.template_manager import save_template
    
    for idx, char_file in enumerate(character_files, 1):
        try:
            # İlerleme callback
            if progress_callback:
                progress_callback(idx, len(character_files), Path(char_file).name)
            
            # Karakteri yükle
            with open(char_file, "r", encoding="utf-8") as f:
                character = json.load(f)
            
            # Şablon adı
            char_name = character.get("name", "karakter")
            template_name = f"{char_name}_template"
            
            # Şablon oluştur
            template_path = save_template(
                character,
                base_dir,
                template_name,
                f"Karakter: {char_name} için şablon"
            )
            
            results["created"].append({
                "file": char_file,
                "template": str(template_path),
                "name": char_name
            })
            
        except Exception as e:
            error_msg = f"{Path(char_file).name}: {str(e)}"
            results["failed"].append(char_file)
            results["errors"].append(error_msg)
    
    return results


def get_characters_from_directory(
    directory: Path,
    system_filter: Optional[str] = None
) -> List[str]:
    """
    Dizindeki tüm karakter dosyalarını getir
    
    Args:
        directory: Karakter dizini
        system_filter: Sistem filtresi (DND5E, MUTANTS_AND_MASTERMINDS, MM3E)
    
    Returns:
        Karakter dosya yolları listesi
    """
    character_files = []
    
    if not directory.exists():
        return character_files
    
    for json_file in directory.glob("*.json"):
        try:
            # Sistem filtresi kontrolü
            if system_filter:
                with open(json_file, "r", encoding="utf-8") as f:
                    character = json.load(f)
                    if character.get("system") != system_filter:
                        continue
            
            character_files.append(str(json_file))
        except:
            # Geçersiz JSON dosyası, atla
            continue
    
    return sorted(character_files)

