"""
Kural Doğrulama Modülü
Yüklenen kuralların geçerliliğini kontrol eder.
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class ValidationSeverity(Enum):
    """Doğrulama hata seviyeleri"""
    ERROR = "error"      # Kritik hata - kural kullanılamaz
    WARNING = "warning"  # Uyarı - kural kullanılabilir ama sorunlu
    INFO = "info"        # Bilgi - öneri


class ValidationIssue:
    """Doğrulama sorunu"""
    def __init__(self, severity: ValidationSeverity, message: str, rule_name: Optional[str] = None):
        self.severity = severity
        self.message = message
        self.rule_name = rule_name
    
    def __str__(self):
        icon = {
            ValidationSeverity.ERROR: "❌",
            ValidationSeverity.WARNING: "⚠️",
            ValidationSeverity.INFO: "ℹ️"
        }.get(self.severity, "•")
        rule_part = f" [{self.rule_name}]" if self.rule_name else ""
        return f"{icon} {self.severity.value.upper()}{rule_part}: {self.message}"


def validate_rules_structure(rules: Dict[str, Any]) -> List[ValidationIssue]:
    """
    Kural yapısının temel doğruluğunu kontrol et
    """
    issues = []
    
    # system alanı kontrolü
    if "system" not in rules:
        issues.append(ValidationIssue(
            ValidationSeverity.ERROR,
            "Kural dosyasında 'system' alanı eksik"
        ))
    elif not isinstance(rules["system"], str):
        issues.append(ValidationIssue(
            ValidationSeverity.ERROR,
            "'system' alanı string olmalıdır"
        ))
    
    # rules alanı kontrolü
    if "rules" not in rules:
        issues.append(ValidationIssue(
            ValidationSeverity.WARNING,
            "Kural dosyasında 'rules' alanı eksik - hiçbir özel kural tanımlanmamış"
        ))
    elif not isinstance(rules["rules"], dict):
        issues.append(ValidationIssue(
            ValidationSeverity.ERROR,
            "'rules' alanı dictionary olmalıdır"
        ))
    
    return issues


def validate_rule_type(rule_name: str, rule_data: Dict[str, Any], expected_types: List[str]) -> List[ValidationIssue]:
    """
    Kural tipinin geçerli olup olmadığını kontrol et
    """
    issues = []
    
    if "type" not in rule_data:
        issues.append(ValidationIssue(
            ValidationSeverity.ERROR,
            f"Kural tipi belirtilmemiş. Beklenen tipler: {', '.join(expected_types)}",
            rule_name
        ))
        return issues
    
    rule_type = rule_data.get("type")
    if rule_type not in expected_types:
        issues.append(ValidationIssue(
            ValidationSeverity.ERROR,
            f"Geçersiz kural tipi '{rule_type}'. Beklenen tipler: {', '.join(expected_types)}",
            rule_name
        ))
    
    return issues


def validate_table_rule(rule_name: str, rule_data: Dict[str, Any]) -> List[ValidationIssue]:
    """
    Tablo tipindeki kuralı doğrula
    """
    issues = []
    
    if "data" not in rule_data:
        issues.append(ValidationIssue(
            ValidationSeverity.ERROR,
            "Tablo kuralında 'data' alanı eksik",
            rule_name
        ))
        return issues
    
    data = rule_data.get("data", {})
    if not isinstance(data, dict):
        issues.append(ValidationIssue(
            ValidationSeverity.ERROR,
            "Tablo kuralı 'data' alanı dictionary olmalıdır",
            rule_name
        ))
        return issues
    
    if not data:
        issues.append(ValidationIssue(
            ValidationSeverity.WARNING,
            "Tablo kuralı boş - hiçbir veri yok",
            rule_name
        ))
        return issues
    
    # Aralık çelişkilerini kontrol et
    ranges = []
    for key, value in data.items():
        if isinstance(key, str) and '-' in key:
            try:
                parts = key.split('-')
                if len(parts) == 2:
                    start = int(parts[0])
                    end = int(parts[1])
                    if start > end:
                        issues.append(ValidationIssue(
                            ValidationSeverity.ERROR,
                            f"Geçersiz aralık '{key}': başlangıç değeri bitiş değerinden büyük",
                            rule_name
                        ))
                    ranges.append((start, end, key, value))
            except ValueError:
                issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    f"Aralık formatı geçersiz: '{key}'",
                    rule_name
                ))
    
    # Aralık çakışmalarını kontrol et
    ranges.sort()
    for i in range(len(ranges) - 1):
        start1, end1, key1, value1 = ranges[i]
        start2, end2, key2, value2 = ranges[i + 1]
        
        if end1 >= start2:
            issues.append(ValidationIssue(
                ValidationSeverity.WARNING,
                f"Aralıklar çakışıyor: '{key1}' ve '{key2}'",
                rule_name
            ))
    
    return issues


def validate_armor_table_rule(rule_name: str, rule_data: Dict[str, Any]) -> List[ValidationIssue]:
    """
    Zırh tablosu kuralını doğrula
    """
    issues = []
    
    if "data" not in rule_data:
        issues.append(ValidationIssue(
            ValidationSeverity.ERROR,
            "Zırh tablosu kuralında 'data' alanı eksik",
            rule_name
        ))
        return issues
    
    data = rule_data.get("data", {})
    if not isinstance(data, dict):
        issues.append(ValidationIssue(
            ValidationSeverity.ERROR,
            "Zırh tablosu 'data' alanı dictionary olmalıdır",
            rule_name
        ))
        return issues
    
    for armor_name, armor_info in data.items():
        if not isinstance(armor_info, dict):
            issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                f"Zırh '{armor_name}' için veri dictionary olmalıdır",
                rule_name
            ))
            continue
        
        if "base" not in armor_info:
            issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                f"Zırh '{armor_name}' için 'base' AC değeri eksik",
                rule_name
            ))
        elif not isinstance(armor_info["base"], int):
            issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                f"Zırh '{armor_name}' için 'base' AC değeri integer olmalıdır",
                rule_name
            ))
        
        if "max_dex" in armor_info and armor_info["max_dex"] is not None:
            if not isinstance(armor_info["max_dex"], int):
                issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    f"Zırh '{armor_name}' için 'max_dex' değeri integer olmalıdır",
                    rule_name
                ))
    
    return issues


def validate_dnd_rules(rules: Dict[str, Any]) -> List[ValidationIssue]:
    """
    D&D kurallarını doğrula
    """
    issues = []
    rules_dict = rules.get("rules", {})
    
    # Proficiency Bonus kontrolü
    if "proficiency_bonus" in rules_dict:
        prof_rule = rules_dict["proficiency_bonus"]
        type_issues = validate_rule_type("proficiency_bonus", prof_rule, ["table"])
        issues.extend(type_issues)
        if prof_rule.get("type") == "table":
            issues.extend(validate_table_rule("proficiency_bonus", prof_rule))
    
    # Armor Class kontrolü
    if "armor_class" in rules_dict:
        armor_rule = rules_dict["armor_class"]
        type_issues = validate_rule_type("armor_class", armor_rule, ["armor_table", "formula"])
        issues.extend(type_issues)
        if armor_rule.get("type") == "armor_table":
            issues.extend(validate_armor_table_rule("armor_class", armor_rule))
    
    # Hit Dice kontrolü
    if "hit_dice" in rules_dict:
        hit_dice_rule = rules_dict["hit_dice"]
        type_issues = validate_rule_type("hit_dice", hit_dice_rule, ["table"])
        issues.extend(type_issues)
        if hit_dice_rule.get("type") == "table":
            issues.extend(validate_table_rule("hit_dice", hit_dice_rule))
    
    return issues


def validate_mm_rules(rules: Dict[str, Any]) -> List[ValidationIssue]:
    """
    M&M kurallarını doğrula
    """
    issues = []
    rules_dict = rules.get("rules", {})
    
    # Power Levels kontrolü
    if "power_levels" in rules_dict:
        pl_rule = rules_dict["power_levels"]
        type_issues = validate_rule_type("power_levels", pl_rule, ["table"])
        issues.extend(type_issues)
        if pl_rule.get("type") == "table":
            issues.extend(validate_table_rule("power_levels", pl_rule))
            
            # Power Points kontrolü
            data = pl_rule.get("data", {})
            for pl_key, pl_info in data.items():
                if isinstance(pl_info, dict):
                    if "power_points" not in pl_info:
                        issues.append(ValidationIssue(
                            ValidationSeverity.WARNING,
                            f"Power Level '{pl_key}' için 'power_points' değeri eksik",
                            "power_levels"
                        ))
                    elif not isinstance(pl_info["power_points"], int):
                        issues.append(ValidationIssue(
                            ValidationSeverity.ERROR,
                            f"Power Level '{pl_key}' için 'power_points' değeri integer olmalıdır",
                            "power_levels"
                        ))
    
    return issues


def validate_vtm_rules(rules: Dict[str, Any]) -> List[ValidationIssue]:
    """
    VtM kurallarını doğrula
    """
    issues = []
    rules_dict = rules.get("rules", {})
    
    # Health kontrolü
    if "health" in rules_dict:
        health_rule = rules_dict["health"]
        if not isinstance(health_rule, dict):
            issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                "Health kuralı dictionary olmalıdır",
                "health"
            ))
        else:
            if "base" not in health_rule:
                issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    "Health kuralında 'base' değeri eksik",
                    "health"
                ))
            elif not isinstance(health_rule["base"], int):
                issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    "Health kuralında 'base' değeri integer olmalıdır",
                    "health"
                ))
            
            if "attribute" not in health_rule:
                issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    "Health kuralında 'attribute' adı eksik",
                    "health"
                ))
            elif not isinstance(health_rule["attribute"], str):
                issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    "Health kuralında 'attribute' değeri string olmalıdır",
                    "health"
                ))
    
    # Willpower kontrolü
    if "willpower" in rules_dict:
        willpower_rule = rules_dict["willpower"]
        if not isinstance(willpower_rule, dict):
            issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                "Willpower kuralı dictionary olmalıdır",
                "willpower"
            ))
        else:
            if "attributes" not in willpower_rule:
                issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    "Willpower kuralında 'attributes' listesi eksik",
                    "willpower"
                ))
            elif not isinstance(willpower_rule["attributes"], list):
                issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    "Willpower kuralında 'attributes' değeri liste olmalıdır",
                    "willpower"
                ))
            elif len(willpower_rule["attributes"]) != 2:
                issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    f"Willpower kuralında 'attributes' listesi tam olarak 2 öğe içermelidir (şu anda {len(willpower_rule['attributes'])})",
                    "willpower"
                ))
    
    return issues


def validate_rules(rules: Dict[str, Any]) -> Tuple[bool, List[ValidationIssue]]:
    """
    Kuralları doğrula ve sorunları döndür
    
    Returns:
        (is_valid, issues): is_valid True ise kritik hata yok, issues tüm sorunların listesi
    """
    issues = []
    
    # Temel yapı kontrolü
    issues.extend(validate_rules_structure(rules))
    
    # Sistem bazlı doğrulama
    system = rules.get("system", "").upper()
    
    if system == "DND5E":
        issues.extend(validate_dnd_rules(rules))
    elif system == "MUTANTS_AND_MASTERMINDS":
        issues.extend(validate_mm_rules(rules))
    elif system == "VTM5E":
        issues.extend(validate_vtm_rules(rules))
    elif system:
        issues.append(ValidationIssue(
            ValidationSeverity.WARNING,
            f"Bilinmeyen sistem '{system}' - sistem özel doğrulamalar yapılamadı"
        ))
    
    # Kritik hataları kontrol et
    has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in issues)
    
    return not has_errors, issues


def format_validation_report(issues: List[ValidationIssue]) -> str:
    """
    Doğrulama raporunu formatla
    """
    if not issues:
        return "✅ Tüm kurallar geçerli! Hiçbir sorun bulunamadı."
    
    errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]
    warnings = [i for i in issues if i.severity == ValidationSeverity.WARNING]
    infos = [i for i in issues if i.severity == ValidationSeverity.INFO]
    
    lines = []
    
    if errors:
        lines.append(f"❌ KRİTİK HATALAR ({len(errors)}):")
        for issue in errors:
            lines.append(f"  {str(issue)}")
        lines.append("")
    
    if warnings:
        lines.append(f"⚠️ UYARILAR ({len(warnings)}):")
        for issue in warnings:
            lines.append(f"  {str(issue)}")
        lines.append("")
    
    if infos:
        lines.append(f"ℹ️ BİLGİLER ({len(infos)}):")
        for issue in infos:
            lines.append(f"  {str(issue)}")
    
    return "\n".join(lines)

