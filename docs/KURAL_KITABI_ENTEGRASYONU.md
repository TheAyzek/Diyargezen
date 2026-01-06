# Kural Kitabı Entegrasyonu - Plan

## 🎯 Amaç
Kullanıcı kural kitabını (PDF/TXT) yükleyip, programın kuralları otomatik çıkararak hesaplamaları yapması.

## 📋 Mevcut Durum
- Kurallar manuel olarak `data/*.json` dosyalarında saklanıyor
- Hesaplamalar `utils/calculations.py` içinde hardcoded

## 🔄 Önerilen Sistem

### 1. Kural Kitabı Yükleme
```
Kullanıcı → PDF/TXT dosyası seçer
    ↓
Program → Dosyayı parse eder
    ↓
Program → Kuralları çıkarır
    ↓
Program → JSON formatında saklar
```

### 2. Kural Çıkarma Yöntemleri

#### A. Pattern Matching (Basit)
- Tablo formatlarını tanıma (Proficiency Bonus tablosu)
- Formül tanıma ("PL × 15", "3 + Stamina")
- Anahtar kelime tanıma ("Proficiency Bonus", "Armor Class")

#### B. NLP (Gelişmiş)
- Doğal dil işleme ile kural çıkarma
- İlişkileri anlama (ör: "seviyeye göre", "her seviyede")

#### C. Yapılandırılmış Format (En Kolay)
- Kullanıcı kuralları belirli formatta yazar
- Program parse eder

### 3. Kural Saklama Formatı

```json
{
  "system": "DND5E",
  "rules": {
    "proficiency_bonus": {
      "type": "table",
      "description": "Proficiency Bonus by Level",
      "data": {
        "1-4": 2,
        "5-8": 3,
        "9-12": 4,
        "13-16": 5,
        "17-20": 6
      }
    },
    "armor_class": {
      "type": "formula",
      "description": "Armor Class calculation",
      "formula": "base + dex_modifier",
      "armor_types": {
        "leather": {"base": 11, "max_dex": null},
        "chain_mail": {"base": 16, "max_dex": 0}
      }
    },
    "hit_points": {
      "type": "formula",
      "description": "Hit Points calculation",
      "formula": "hit_dice + con_modifier + (average_roll + con_modifier) * (level - 1)",
      "class_hit_dice": {
        "Wizard": 6,
        "Fighter": 10
      }
    }
  }
}
```

## 🛠️ Teknik Gereksinimler

### Gerekli Kütüphaneler
- `PyPDF2` veya `pdfplumber` - PDF parsing
- `re` - Regex pattern matching
- `json` - Kural saklama
- (Opsiyonel) `spaCy` veya `nltk` - NLP

### Yeni Modüller
1. `utils/rule_parser.py` - Kural kitabı parsing
2. `utils/rule_extractor.py` - Kural çıkarma
3. `utils/rule_storage.py` - Kural saklama/yükleme
4. `utils/dynamic_calculator.py` - Dinamik hesaplama motoru

## 📝 Örnek Kullanım Senaryosu

### Senaryo 1: D&D 5e Kural Kitabı Yükleme
```
1. Kullanıcı "Kural Kitabı Yükle" butonuna tıklar
2. D&D 5e Player's Handbook PDF'i seçer
3. Program PDF'i parse eder
4. Program şunları çıkarır:
   - Proficiency Bonus tablosu
   - Armor Class kuralları
   - Hit Points hesaplama formülü
   - Spell Slots tablosu
5. Kurallar `data/rules/dnd5e_rules.json` olarak kaydedilir
6. Hesaplamalar artık bu kurallara göre yapılır
```

### Senaryo 2: Manuel Kural Girişi
```
1. Kullanıcı "Kural Düzenle" butonuna tıklar
2. Yapılandırılmış formatta kural yazar:
   ```
   Proficiency Bonus:
   1-4: +2
   5-8: +3
   9-12: +4
   13-16: +5
   17-20: +6
   ```
3. Program parse edip saklar
```

## 🎨 UI Tasarımı

### Yeni Butonlar
- "Kural Kitabı Yükle" (her sistem sayfasında)
- "Kural Düzenle" (ayarlar menüsünde)
- "Kuralları Sıfırla" (varsayılan kurallara dön)

### Yeni Diyaloglar
- Kural kitabı yükleme diyaloğu
- Kural düzenleme diyaloğu
- Kural önizleme diyaloğu

## 🔧 Uygulama Adımları

### Faz 1: Basit Pattern Matching
1. PDF'den metin çıkarma
2. Tablo formatlarını tanıma (regex)
3. Basit formülleri parse etme
4. JSON'a kaydetme

### Faz 2: Dinamik Hesaplama
1. JSON'dan kuralları yükleme
2. Formül interpreter
3. Tablo lookup
4. Hesaplama motoru

### Faz 3: Gelişmiş Özellikler
1. NLP ile kural çıkarma
2. Kural doğrulama
3. Kural versiyonlama
4. Kural paylaşımı

## ⚠️ Zorluklar ve Çözümler

### Zorluk 1: PDF Formatı
- **Sorun**: PDF'ler farklı formatlarda olabilir
- **Çözüm**: Birden fazla parser denemek, kullanıcıya format seçeneği sunmak

### Zorluk 2: Kural Çıkarma Doğruluğu
- **Sorun**: Otomatik çıkarma %100 doğru olmayabilir
- **Çözüm**: Kullanıcıya onaylatma, düzenleme imkanı

### Zorluk 3: Kural Çakışmaları
- **Sorun**: Farklı kaynaklardan çelişkili kurallar
- **Çözüm**: Kural öncelik sistemi, kullanıcı seçimi

## 📊 Örnek Kural Çıkarma

### Girdi (PDF'den çıkarılan metin):
```
Proficiency Bonus
Your proficiency bonus is based on your level:
Level 1-4: +2
Level 5-8: +3
Level 9-12: +4
Level 13-16: +5
Level 17-20: +6
```

### Çıktı (JSON):
```json
{
  "proficiency_bonus": {
    "type": "table",
    "ranges": {
      "1-4": 2,
      "5-8": 3,
      "9-12": 4,
      "13-16": 5,
      "17-20": 6
    }
  }
}
```

## 🚀 Başlangıç Önerisi

1. **Basit başla**: Yapılandırılmış metin formatı ile kural girişi
2. **PDF desteği ekle**: PyPDF2 ile basit PDF parsing
3. **Pattern matching**: Regex ile tablo/formül tanıma
4. **Dinamik hesaplama**: JSON'dan kuralları okuyup hesaplama

## 📚 Kaynaklar
- PyPDF2 dokümantasyonu
- Regex pattern örnekleri
- JSON schema validation

