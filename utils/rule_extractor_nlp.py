"""
NLP ile Gelişmiş Kural Çıkarma Modülü
Doğal dil işleme kullanarak daha akıllı kural çıkarma.
"""

import re
from typing import Dict, Any, List, Optional

# spaCy opsiyonel - yoksa pattern matching kullanılır
try:
    import spacy
    SPACY_AVAILABLE = True
    # Türkçe model yoksa İngilizce kullanılır
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        try:
            nlp = spacy.load("en_core_web_md")
        except OSError:
            nlp = None
            SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False
    nlp = None


def is_nlp_available() -> bool:
    """NLP kütüphanesi mevcut mu?"""
    return SPACY_AVAILABLE and nlp is not None


def extract_relationships_nlp(text: str, keyword: str) -> List[Dict[str, Any]]:
    """
    NLP kullanarak anahtar kelime ile ilgili ilişkileri çıkar
    
    Args:
        text: İşlenecek metin
        keyword: Aranacak anahtar kelime (örn: "proficiency bonus", "level")
    
    Returns:
        İlişki listesi
    """
    if not is_nlp_available():
        return []
    
    relationships = []
    doc = nlp(text)
    
    # Anahtar kelimeyi içeren cümleleri bul
    keyword_lower = keyword.lower()
    
    for sent in doc.sents:
        sent_text = sent.text.lower()
        if keyword_lower in sent_text:
            # Dependency parsing ile ilişkileri bul
            for token in sent:
                # Sayısal değerler ve aralıklar
                if token.like_num or token.text.isdigit():
                    # Anahtar kelimeye yakın sayıları bul
                    relationships.append({
                        "type": "value",
                        "keyword": keyword,
                        "value": token.text,
                        "context": sent.text
                    })
                
                # Aralık ifadeleri ("1-4", "level 1 to 4")
                if "-" in token.text or "to" in token.text.lower():
                    relationships.append({
                        "type": "range",
                        "keyword": keyword,
                        "range": token.text,
                        "context": sent.text
                    })
    
    return relationships


def extract_table_structure_nlp(text: str, table_name: str) -> Optional[List[Dict[str, Any]]]:
    """
    NLP kullanarak tablo yapısını çıkar
    
    Args:
        text: İşlenecek metin
        table_name: Tablo adı (örn: "Proficiency Bonus")
    
    Returns:
        Tablo verisi
    """
    if not is_nlp_available():
        return None
    
    # Tablo başlığını bul
    lines = text.split('\n')
    table_data = []
    
    for i, line in enumerate(lines):
        if table_name.lower() in line.lower():
            # Sonraki satırları analiz et
            doc = nlp(line)
            
            # Sayısal değerleri ve aralıkları bul
            for j in range(i + 1, min(i + 20, len(lines))):
                next_line = lines[j].strip()
                if not next_line or next_line.startswith('---'):
                    continue
                
                # NLP ile parse et
                line_doc = nlp(next_line)
                
                # Sayısal değerleri çıkar
                numbers = [token.text for token in line_doc if token.like_num or token.text.isdigit()]
                ranges = []
                
                # Aralık ifadelerini bul
                for token in line_doc:
                    if "-" in token.text:
                        ranges.append(token.text)
                
                if numbers or ranges:
                    table_data.append({
                        "line": next_line,
                        "numbers": numbers,
                        "ranges": ranges,
                        "raw": next_line
                    })
    
    return table_data if table_data else None


def extract_formula_nlp(text: str, keyword: str) -> Optional[str]:
    """
    NLP kullanarak formül çıkar
    
    Args:
        text: İşlenecek metin
        keyword: Aranacak anahtar kelime
    
    Returns:
        Çıkarılan formül
    """
    if not is_nlp_available():
        return None
    
    doc = nlp(text)
    keyword_lower = keyword.lower()
    
    for sent in doc.sents:
        sent_text = sent.text.lower()
        if keyword_lower in sent_text and "=" in sent.text:
            # Eşittir işaretinden sonrasını al
            parts = sent.text.split("=", 1)
            if len(parts) == 2:
                formula = parts[1].strip()
                # NLP ile temizle (sadece önemli kelimeleri tut)
                formula_doc = nlp(formula)
                important_tokens = [
                    token.text for token in formula_doc
                    if not token.is_stop and not token.is_punct
                ]
                return " ".join(important_tokens)
    
    return None


def extract_level_based_rules_nlp(text: str) -> Dict[str, Any]:
    """
    NLP kullanarak seviye bazlı kuralları çıkar
    
    Örnek: "At level 5, proficiency bonus increases to +3"
    
    Returns:
        Seviye bazlı kural verisi
    """
    if not is_nlp_available():
        return {}
    
    rules = {}
    doc = nlp(text)
    
    # Seviye ifadelerini bul
    level_patterns = [
        r'level\s+(\d+)',
        r'at\s+level\s+(\d+)',
        r'level\s+(\d+)\s+and\s+above',
    ]
    
    for sent in doc.sents:
        sent_text = sent.text.lower()
        
        # Seviye bazlı ifadeleri bul
        for pattern in level_patterns:
            matches = re.finditer(pattern, sent_text, re.IGNORECASE)
            for match in matches:
                level = match.group(1)
                
                # Bu cümledeki sayısal değerleri bul
                sent_doc = nlp(sent.text)
                numbers = [token.text for token in sent_doc if token.like_num]
                
                if numbers:
                    rules[level] = {
                        "level": level,
                        "values": numbers,
                        "context": sent.text
                    }
    
    return rules


def enhance_extraction_with_nlp(text: str, system: str, base_rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    NLP kullanarak mevcut çıkarımı geliştir
    
    Args:
        text: İşlenecek metin
        system: Sistem adı
        base_rules: Pattern matching ile çıkarılan temel kurallar
    
    Returns:
        Geliştirilmiş kurallar
    """
    if not is_nlp_available():
        return base_rules
    
    enhanced_rules = base_rules.copy()
    
    # D&D için NLP geliştirmeleri
    if system == 'DND5E':
        # Proficiency Bonus için NLP
        if 'proficiency_bonus' not in enhanced_rules.get('rules', {}):
            prof_relationships = extract_relationships_nlp(text, "proficiency bonus")
            if prof_relationships:
                # İlişkilerden tablo oluştur
                prof_table = {}
                for rel in prof_relationships:
                    if rel['type'] == 'range':
                        # Aralık ve değer eşleştirmesi yap
                        pass  # Daha gelişmiş eşleştirme gerekir
        
        # Level bazlı kurallar
        level_rules = extract_level_based_rules_nlp(text)
        if level_rules:
            if 'level_based' not in enhanced_rules.get('rules', {}):
                enhanced_rules.setdefault('rules', {})['level_based'] = {
                    'type': 'level_table',
                    'data': level_rules
                }
    
    return enhanced_rules


def extract_rules_with_nlp(text: str, system: str, use_nlp: bool = True) -> Dict[str, Any]:
    """
    NLP kullanarak kuralları çıkar (opsiyonel)
    
    Args:
        text: İşlenecek metin
        system: Sistem adı
        use_nlp: NLP kullanılsın mı (default: True, ama yoksa pattern matching kullanılır)
    
    Returns:
        Çıkarılan kurallar
    """
    # Önce pattern matching ile temel kuralları çıkar
    from utils.rule_extractor import extract_rules_from_text
    base_rules = extract_rules_from_text(text, system)
    
    # NLP mevcut ve isteniyorsa geliştir
    if use_nlp and is_nlp_available():
        enhanced_rules = enhance_extraction_with_nlp(text, system, base_rules)
        return enhanced_rules
    
    return base_rules


def get_nlp_status() -> Dict[str, Any]:
    """
    NLP durumunu döndür
    
    Returns:
        NLP durum bilgisi
    """
    status = {
        "available": is_nlp_available(),
        "library": "spaCy" if SPACY_AVAILABLE else None,
        "model_loaded": nlp is not None if SPACY_AVAILABLE else False
    }
    
    if is_nlp_available():
        status["model_name"] = nlp.meta.get("name", "unknown") if hasattr(nlp, 'meta') else "unknown"
    
    return status

