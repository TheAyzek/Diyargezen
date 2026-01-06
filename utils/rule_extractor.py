"""
Kural Çıkarma Modülü
Kural kitabından (metin/PDF) kuralları otomatik çıkarır.
"""

import re
from typing import Dict, Any, List, Optional
from pathlib import Path


def extract_proficiency_bonus_table(text: str) -> Optional[Dict[str, int]]:
    """
    Proficiency Bonus tablosunu çıkar
    Örnek formatlar:
    - "Level 1-4: +2"
    - "1-4: +2"
    - "Levels 1-4: +2"
    """
    patterns = [
        r'(?:Level|Levels?)\s*(\d+)[-\s]+(\d+)[:\s]+[+]?(\d+)',
        r'(\d+)[-\s]+(\d+)[:\s]+[+]?(\d+)',
        r'Level\s*(\d+)[:\s]+[+]?(\d+)',
    ]
    
    result = {}
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) == 3:
                start, end, bonus = match.groups()
                result[f"{start}-{end}"] = int(bonus)
            elif len(match.groups()) == 2:
                level, bonus = match.groups()
                result[f"{level}-{level}"] = int(bonus)
    
    return result if result else None


def extract_formula(text: str, keyword: str) -> Optional[str]:
    """
    Belirli bir anahtar kelime için formül çıkar
    Örnek: "Hit Points = hit_dice + con_modifier"
    """
    # Anahtar kelimeyi içeren satırları bul
    lines = text.split('\n')
    for line in lines:
        if keyword.lower() in line.lower():
            # Formülü çıkar (eşittir işaretinden sonra)
            if '=' in line:
                formula = line.split('=', 1)[1].strip()
                # Basit temizleme
                formula = re.sub(r'[^\w\s\+\-\*\/\(\)]', '', formula)
                return formula
    
    return None


def extract_table(text: str, table_name: str) -> Optional[List[Dict[str, Any]]]:
    """
    Tablo formatındaki verileri çıkar
    Örnek:
    Level | Proficiency Bonus
    1-4   | +2
    5-8   | +3
    """
    # Tablo başlığını bul
    lines = text.split('\n')
    start_idx = None
    for i, line in enumerate(lines):
        if table_name.lower() in line.lower():
            start_idx = i + 1
            break
    
    if start_idx is None:
        return None
    
    # Tablo verilerini çıkar (sonraki 10 satır)
    table_data = []
    for i in range(start_idx, min(start_idx + 10, len(lines))):
        line = lines[i].strip()
        if not line or line.startswith('---'):
            continue
        
        # Pipe veya tab ile ayrılmış değerler
        parts = re.split(r'[|\t]+', line)
        if len(parts) >= 2:
            table_data.append({
                'key': parts[0].strip(),
                'value': parts[1].strip()
            })
    
    return table_data if table_data else None


def extract_armor_rules(text: str) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Zırh kurallarını çıkar
    Örnek: "Leather Armor: AC 11 + Dex modifier"
    """
    armor_patterns = [
        r'(\w+\s+Armor|Leather|Chain\s+Mail|Plate|Studded\s+Leather)[:\s]+AC\s+(\d+)(?:\s*\+\s*Dex\s+modifier)?(?:,\s*max\s*\+(\d+))?',
        r'(\w+\s+Armor)[:\s]+AC\s+(\d+)',
    ]
    
    armors = {}
    for pattern in armor_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            armor_name = match.group(1).lower()
            base_ac = int(match.group(2))
            max_dex = int(match.group(3)) if len(match.groups()) > 2 and match.group(3) else None
            
            armors[armor_name] = {
                'base': base_ac,
                'max_dex': max_dex,
                'allows_dex': 'dex' in match.group(0).lower()
            }
    
    return armors if armors else None


def extract_hit_dice_rules(text: str) -> Optional[Dict[str, int]]:
    """
    Sınıf Hit Dice kurallarını çıkar
    Örnek: "Wizard: d6", "Fighter: d10"
    """
    patterns = [
        r'(\w+)[:\s]+d(\d+)',
        r'(\w+)\s+Hit\s+Dice[:\s]+d(\d+)',
    ]
    
    hit_dice = {}
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            class_name = match.group(1)
            dice_value = int(match.group(2))
            hit_dice[class_name] = dice_value
    
    return hit_dice if hit_dice else None


def extract_power_level_rules(text: str) -> Optional[Dict[str, Dict[str, int]]]:
    """
    M&M Power Level kurallarını çıkar
    Örnek: "PL 10: Power Points = 150"
    """
    patterns = [
        r'PL\s*(\d+)[:\s]+Power\s+Points\s*=\s*(\d+)',
        r'Power\s+Level\s+(\d+)[:\s]+(\d+)\s+points',
    ]
    
    pl_rules = {}
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            pl = match.group(1)
            points = int(match.group(2))
            pl_rules[f"PL{pl}"] = {'power_points': points}
    
    return pl_rules if pl_rules else None


def extract_vtm_rules(text: str) -> Optional[Dict[str, Any]]:
    """
    VtM kurallarını çıkar
    Örnek: "Health = 3 + Stamina", "Willpower = Resolve + Composure"
    """
    rules = {}
    
    # Health kuralı
    health_match = re.search(r'Health\s*=\s*(\d+)\s*\+\s*(\w+)', text, re.IGNORECASE)
    if health_match:
        rules['health'] = {
            'base': int(health_match.group(1)),
            'attribute': health_match.group(2)
        }
    
    # Willpower kuralı
    willpower_match = re.search(r'Willpower\s*=\s*(\w+)\s*\+\s*(\w+)', text, re.IGNORECASE)
    if willpower_match:
        rules['willpower'] = {
            'attributes': [willpower_match.group(1), willpower_match.group(2)]
        }
    
    return rules if rules else None


def extract_rules_from_text(text: str, system: str) -> Dict[str, Any]:
    """
    Metinden tüm kuralları çıkar
    """
    rules = {
        'system': system,
        'rules': {}
    }
    
    # Proficiency Bonus tablosu (D&D)
    if system == 'DND5E':
        prof_table = extract_proficiency_bonus_table(text)
        if prof_table:
            rules['rules']['proficiency_bonus'] = {
                'type': 'table',
                'data': prof_table
            }
        
        # Zırh kuralları
        armor_rules = extract_armor_rules(text)
        if armor_rules:
            rules['rules']['armor_class'] = {
                'type': 'armor_table',
                'data': armor_rules
            }
        
        # Hit Dice kuralları
        hit_dice = extract_hit_dice_rules(text)
        if hit_dice:
            rules['rules']['hit_dice'] = {
                'type': 'table',
                'data': hit_dice
            }
    
    # M&M kuralları
    elif system == 'MUTANTS_AND_MASTERMINDS':
        pl_rules = extract_power_level_rules(text)
        if pl_rules:
            rules['rules']['power_levels'] = {
                'type': 'table',
                'data': pl_rules
            }
    
    # VtM kuralları
    elif system == 'VTM5E':
        vtm_rules = extract_vtm_rules(text)
        if vtm_rules:
            rules['rules'].update(vtm_rules)
    
    return rules


def extract_rules_from_file(file_path: Path, system: str, use_nlp: bool = False) -> Dict[str, Any]:
    """
    Dosyadan kuralları çıkar
    
    Args:
        file_path: Dosya yolu
        system: Sistem adı
        use_nlp: NLP kullanılsın mı (opsiyonel, default: False)
    
    Returns:
        Çıkarılan kurallar
    """
    try:
        if file_path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        elif file_path.suffix.lower() == '.pdf':
            # PDF parsing (basit versiyon)
            try:
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except ImportError:
                raise ImportError("PyPDF2 kütüphanesi gerekli. 'pip install PyPDF2' ile yükleyin.")
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {file_path.suffix}")
        
        # NLP kullanılıyorsa NLP modülünü kullan
        if use_nlp:
            try:
                from utils.rule_extractor_nlp import extract_rules_with_nlp
                return extract_rules_with_nlp(text, system, use_nlp=True)
            except Exception:
                # NLP hatası durumunda pattern matching'e geri dön
                pass
        
        return extract_rules_from_text(text, system)
    
    except Exception as e:
        raise Exception(f"Kural çıkarma hatası: {str(e)}")

