# D&D 5e Karakter Oluşturma Kuralları - Durum Analizi

## ✅ Mevcut Kurallar (Uygulanmış)

### 1. Temel Karakter Oluşturma
- ✅ Irk seçimi ve yetenek puanı artışları
- ✅ Sınıf seçimi
- ✅ Arka plan seçimi
- ✅ Point-buy sistemi (27 puan)
- ✅ Yetenek modifier hesaplama: `(score - 10) // 2`

### 2. Hesaplama Fonksiyonları
- ✅ **Hit Points**: 1st level = max hit die + CON modifier
- ✅ **Proficiency Bonus**: Level'a göre (+2 to +6)
- ✅ **Armor Class**: 10 + DEX modifier (armor yoksa)
- ✅ **Saving Throws**: Class'a göre proficiency
- ✅ **Spell Slots**: Level ve class'a göre
- ✅ **Spell Save DC**: 8 + proficiency + spellcasting ability modifier
- ✅ **Spell Attack Bonus**: Proficiency + spellcasting ability modifier
- ✅ **Passive Perception**: 10 + WIS modifier + proficiency (eğer Perception proficient)

### 3. Dinamik Kural Desteği
- ✅ `calculate_dynamic_hit_points` - Kurallara göre HP hesaplama
- ✅ `calculate_dynamic_proficiency_bonus` - Kurallara göre proficiency
- ✅ `calculate_dynamic_armor_class` - Kurallara göre AC hesaplama
- ✅ Rule storage ve loading sistemi mevcut

---

## ⚠️ Eksik veya İyileştirilebilir Kurallar

### 1. Skill Proficiencies (Kritik)
**Mevcut Durum:** Class skills seçimi var ama background skills ile birleştirme eksik
**D&D 5e Kuralı:**
- Background'dan 2 skill proficiency
- Class'dan belirli sayıda skill proficiency (sınıfa göre değişir)
- Bazı skill'ler hem background hem class'ta olabilir (tekrar sayılmaz)
- Total: Background + Class skill sayısı (max 2 overlap)

**Eksik:**
```python
# Şu an sadece class skills seçiliyor, background skills eklenmiyor
selected_skills = [item.text() for item in self.wiz_skills.selectedItems()]
character["skills"]["class_skills"] = selected_skills
```

**Gerekli Düzeltme:**
```python
# Background skills otomatik eklenmeli
background_data = self.data["backgrounds"][character["background"]]
background_skills = background_data.get("skill_proficiencies", [])
class_skills = selected_skills  # Kullanıcı seçtiği skills

# Birleştir (tekrar edenler bir kez sayılır)
all_proficient_skills = list(set(background_skills + class_skills))
character["skills"]["proficiencies"] = all_proficient_skills
```

---

### 2. Starting Equipment Seçimi (Orta Öncelik)
**Mevcut Durum:** `starting_equipment_options` veri dosyasında var ama GUI'de tam entegre değil
**D&D 5e Kuralı:**
- Class'a göre başlangıç ekipmanı seçenekleri
- Background'dan da ekipman gelir
- "A or B" seçimleri
- "Any X" seçimleri

**Eksik:** Kullanıcı ekipman seçimini adım bazlı yapamıyor

---

### 3. Subclass (Archetype) Seçimi (Önemli)
**Mevcut Durum:** Veri dosyasında subclass'lar var ama GUI'de seçim yapılamıyor
**D&D 5e Kuralı:**
- Çoğu class 3. seviyede subclass seçer
- Bazı class'lar 1. seviyede seçer (Cleric, Sorcerer, Warlock)
- Subclass seçimi class features'ı değiştirir

**Eksik:** 3. seviyede subclass seçimi GUI'de yok

**Gerekli Ek:**
- Level up ekranında subclass seçim adımı
- Subclass seçildikten sonra class features güncelleme

---

### 4. Feat vs ASI (Ability Score Improvement) (Önemli)
**Mevcut Durum:** Feat seçimi var ama ASI ile karşılaştırma yok
**D&D 5e Kuralı:**
- 4, 8, 12, 16, 19. seviyelerde: Feat **VEYA** +2 ASI **VEYA** +1/+1 ASI
- Bazı feat'ler önkoşul gerektirir (ability score minimum'ları)
- Human Variant: 1. seviyede feat alabilir

**Eksik:** Level up'ta feat vs ASI seçimi yok

**Gerekli Ek:**
- Level up ekranında "Feat" veya "ASI" seçimi
- ASI seçildiğinde: +2 tek yetenek veya +1/+1 iki yetenek
- Feat seçildiğinde: Önkoşul kontrolü

---

### 5. Spell Preparation (Büyü Hazırlama) (Kritik)
**Mevcut Durum:** Spell listesi var ama preparation sistemi yok
**D&D 5e Kuralı:**
- **Wizard**: Spell book'tan hazırlanır (Level + INT modifier kadar spell)
- **Cleric/Druid/Paladin**: Tüm spell listesinden hazırlanır (Level + spellcasting modifier)
- **Sorcerer/Bard/Warlock**: Hazırlanmaz, bilinen spell'ler (spells known)
- **Ranger**: Spells known (hazırlanmaz)

**Eksik:** Spell preparation hesaplama ve GUI yok

**Gerekli Ek:**
```python
def calculate_spells_prepared(character, class_data):
    char_class = character["class"]
    level = character["level"]
    abilities = character["abilities"]
    
    if char_class in ["Sorcerer", "Bard", "Warlock", "Ranger"]:
        # Spells Known sistem (hazırlanmaz)
        return None  # Sadece bilinen spell'ler
    
    # Spellcasting ability modifier'ı al
    spellcasting_ability = get_spellcasting_ability(char_class)
    modifier = calculate_ability_modifier(abilities[spellcasting_ability])
    
    # Hazırlanan spell sayısı = Level + modifier
    spells_prepared = level + modifier
    return min(spells_prepared, get_spell_slots(character)[level])  # Max spell slot sayısı
```

---

### 6. Expertise (Uzmanlık) (Önemli)
**Mevcut Durum:** Rogue ve Bard için Expertise yok
**D&D 5e Kuralı:**
- Rogue: 1. seviyede 2 skill'e expertise (double proficiency)
- Bard: 3. seviyede expertise alır
- Ranger: Bazı subclass'lar expertise verir

**Eksik:** Expertise skill'leri işaretleme ve hesaplama yok

**Gerekli Ek:**
```python
# Skill modifier hesaplama
skill_modifier = ability_modifier
if skill in proficient_skills:
    skill_modifier += proficiency_bonus
if skill in expertise_skills:  # YENİ
    skill_modifier += proficiency_bonus  # Double proficiency
```

---

### 7. Multiclassing (Çok Sınıflı) (Düşük Öncelik)
**Mevcut Durum:** Yok
**D&D 5e Kuralları:**
- Ability score minimum'ları (her iki class için)
- Hit dice kombinasyonu
- Proficiency bonus: Toplam level'a göre
- Spell slots: Multiclass spellcaster table
- Class features'lar ayrı hesaplanır

**Not:** Bu oldukça karmaşık, şimdilik skip edilebilir

---

### 8. Initiative (Giriş Sırası) (Basit)
**Mevcut Durum:** Hesaplanmıyor
**D&D 5e Kuralı:** `DEX modifier` (proficiency bonus eklenmez)

**Eksik:** Initiative hesaplama basit eklenebilir

---

### 9. Level Up Kuralları (Önemli)
**Mevcut Durum:** Level up ekranı var ama kurallar tam değil
**D&D 5e Kuralları:**
- HP artışı: Hit die + CON modifier (veya ortalama: hit die/2 + 1 + CON)
- Yeni class features
- Spell slots artışı
- ASI veya Feat (4/8/12/16/19)
- Subclass seçimi (3. seviyede)

**Eksik:** Level up ekranında bu kuralların otomatik uygulanması

---

## 📊 Öncelik Sırası

### 🔴 Kritik (Hemen Eklenmeli)
1. **Skill Proficiencies Kombinasyonu** - Background + Class skills birleştirme
2. **Spell Preparation** - Wizard/Cleric vs Sorcerer/Bard farkı

### 🟡 Önemli (Kısa Vadede)
3. **Subclass Seçimi** - 3. seviyede subclass seçim ekranı
4. **Feat vs ASI** - Level up'ta seçim ekranı
5. **Expertise** - Rogue/Bard için double proficiency

### 🟢 Orta (Uzun Vadede)
6. **Starting Equipment GUI** - Ekipman seçim ekranı
7. **Level Up Otomasyonu** - Kuralların otomatik uygulanması
8. **Initiative** - Basit hesaplama

### ⚪ Düşük (İleride)
9. **Multiclassing** - Çok karmaşık, şimdilik skip

---

## 🛠️ Nasıl Ekleyebiliriz?

### 1. Kural Dosyası Yapısı
Kuralları `data/dnd_rules.json` dosyasına ekleyebiliriz:

```json
{
  "skill_proficiencies": {
    "rule": "Background skills + Class skills (overlap tekrar sayılmaz)"
  },
  "spell_preparation": {
    "prepared_casters": ["Wizard", "Cleric", "Druid", "Paladin"],
    "known_casters": ["Sorcerer", "Bard", "Warlock", "Ranger"],
    "preparation_formula": "level + spellcasting_ability_modifier"
  },
  "expertise": {
    "rogue": {
      "level_1": {
        "skills": 2,
        "description": "Choose 2 skill proficiencies for expertise"
      }
    },
    "bard": {
      "level_3": {
        "skills": 2,
        "description": "Choose 2 skill proficiencies for expertise"
      }
    }
  }
}
```

### 2. GUI Entegrasyonu
- Her kural için GUI widget'ı ekle
- Kural doğrulama fonksiyonları
- Otomatik hesaplama tetikleme

### 3. Test Senaryoları
- Farklı class kombinasyonları test et
- Edge case'leri kontrol et (Human Variant, multiclass hazırlığı)

---

## 📝 Sonuç

**Mevcut Durum:** %60-70 tamamlanmış
**Eksik Kısımlar:** Skill combinations, Spell preparation, Subclass, Feat/ASI
**Önerilen Yaklaşım:** Öncelik sırasına göre adım adım ekleme




## ✅ Mevcut Kurallar (Uygulanmış)

### 1. Temel Karakter Oluşturma
- ✅ Irk seçimi ve yetenek puanı artışları
- ✅ Sınıf seçimi
- ✅ Arka plan seçimi
- ✅ Point-buy sistemi (27 puan)
- ✅ Yetenek modifier hesaplama: `(score - 10) // 2`

### 2. Hesaplama Fonksiyonları
- ✅ **Hit Points**: 1st level = max hit die + CON modifier
- ✅ **Proficiency Bonus**: Level'a göre (+2 to +6)
- ✅ **Armor Class**: 10 + DEX modifier (armor yoksa)
- ✅ **Saving Throws**: Class'a göre proficiency
- ✅ **Spell Slots**: Level ve class'a göre
- ✅ **Spell Save DC**: 8 + proficiency + spellcasting ability modifier
- ✅ **Spell Attack Bonus**: Proficiency + spellcasting ability modifier
- ✅ **Passive Perception**: 10 + WIS modifier + proficiency (eğer Perception proficient)

### 3. Dinamik Kural Desteği
- ✅ `calculate_dynamic_hit_points` - Kurallara göre HP hesaplama
- ✅ `calculate_dynamic_proficiency_bonus` - Kurallara göre proficiency
- ✅ `calculate_dynamic_armor_class` - Kurallara göre AC hesaplama
- ✅ Rule storage ve loading sistemi mevcut

---

## ⚠️ Eksik veya İyileştirilebilir Kurallar

### 1. Skill Proficiencies (Kritik)
**Mevcut Durum:** Class skills seçimi var ama background skills ile birleştirme eksik
**D&D 5e Kuralı:**
- Background'dan 2 skill proficiency
- Class'dan belirli sayıda skill proficiency (sınıfa göre değişir)
- Bazı skill'ler hem background hem class'ta olabilir (tekrar sayılmaz)
- Total: Background + Class skill sayısı (max 2 overlap)

**Eksik:**
```python
# Şu an sadece class skills seçiliyor, background skills eklenmiyor
selected_skills = [item.text() for item in self.wiz_skills.selectedItems()]
character["skills"]["class_skills"] = selected_skills
```

**Gerekli Düzeltme:**
```python
# Background skills otomatik eklenmeli
background_data = self.data["backgrounds"][character["background"]]
background_skills = background_data.get("skill_proficiencies", [])
class_skills = selected_skills  # Kullanıcı seçtiği skills

# Birleştir (tekrar edenler bir kez sayılır)
all_proficient_skills = list(set(background_skills + class_skills))
character["skills"]["proficiencies"] = all_proficient_skills
```

---

### 2. Starting Equipment Seçimi (Orta Öncelik)
**Mevcut Durum:** `starting_equipment_options` veri dosyasında var ama GUI'de tam entegre değil
**D&D 5e Kuralı:**
- Class'a göre başlangıç ekipmanı seçenekleri
- Background'dan da ekipman gelir
- "A or B" seçimleri
- "Any X" seçimleri

**Eksik:** Kullanıcı ekipman seçimini adım bazlı yapamıyor

---

### 3. Subclass (Archetype) Seçimi (Önemli)
**Mevcut Durum:** Veri dosyasında subclass'lar var ama GUI'de seçim yapılamıyor
**D&D 5e Kuralı:**
- Çoğu class 3. seviyede subclass seçer
- Bazı class'lar 1. seviyede seçer (Cleric, Sorcerer, Warlock)
- Subclass seçimi class features'ı değiştirir

**Eksik:** 3. seviyede subclass seçimi GUI'de yok

**Gerekli Ek:**
- Level up ekranında subclass seçim adımı
- Subclass seçildikten sonra class features güncelleme

---

### 4. Feat vs ASI (Ability Score Improvement) (Önemli)
**Mevcut Durum:** Feat seçimi var ama ASI ile karşılaştırma yok
**D&D 5e Kuralı:**
- 4, 8, 12, 16, 19. seviyelerde: Feat **VEYA** +2 ASI **VEYA** +1/+1 ASI
- Bazı feat'ler önkoşul gerektirir (ability score minimum'ları)
- Human Variant: 1. seviyede feat alabilir

**Eksik:** Level up'ta feat vs ASI seçimi yok

**Gerekli Ek:**
- Level up ekranında "Feat" veya "ASI" seçimi
- ASI seçildiğinde: +2 tek yetenek veya +1/+1 iki yetenek
- Feat seçildiğinde: Önkoşul kontrolü

---

### 5. Spell Preparation (Büyü Hazırlama) (Kritik)
**Mevcut Durum:** Spell listesi var ama preparation sistemi yok
**D&D 5e Kuralı:**
- **Wizard**: Spell book'tan hazırlanır (Level + INT modifier kadar spell)
- **Cleric/Druid/Paladin**: Tüm spell listesinden hazırlanır (Level + spellcasting modifier)
- **Sorcerer/Bard/Warlock**: Hazırlanmaz, bilinen spell'ler (spells known)
- **Ranger**: Spells known (hazırlanmaz)

**Eksik:** Spell preparation hesaplama ve GUI yok

**Gerekli Ek:**
```python
def calculate_spells_prepared(character, class_data):
    char_class = character["class"]
    level = character["level"]
    abilities = character["abilities"]
    
    if char_class in ["Sorcerer", "Bard", "Warlock", "Ranger"]:
        # Spells Known sistem (hazırlanmaz)
        return None  # Sadece bilinen spell'ler
    
    # Spellcasting ability modifier'ı al
    spellcasting_ability = get_spellcasting_ability(char_class)
    modifier = calculate_ability_modifier(abilities[spellcasting_ability])
    
    # Hazırlanan spell sayısı = Level + modifier
    spells_prepared = level + modifier
    return min(spells_prepared, get_spell_slots(character)[level])  # Max spell slot sayısı
```

---

### 6. Expertise (Uzmanlık) (Önemli)
**Mevcut Durum:** Rogue ve Bard için Expertise yok
**D&D 5e Kuralı:**
- Rogue: 1. seviyede 2 skill'e expertise (double proficiency)
- Bard: 3. seviyede expertise alır
- Ranger: Bazı subclass'lar expertise verir

**Eksik:** Expertise skill'leri işaretleme ve hesaplama yok

**Gerekli Ek:**
```python
# Skill modifier hesaplama
skill_modifier = ability_modifier
if skill in proficient_skills:
    skill_modifier += proficiency_bonus
if skill in expertise_skills:  # YENİ
    skill_modifier += proficiency_bonus  # Double proficiency
```

---

### 7. Multiclassing (Çok Sınıflı) (Düşük Öncelik)
**Mevcut Durum:** Yok
**D&D 5e Kuralları:**
- Ability score minimum'ları (her iki class için)
- Hit dice kombinasyonu
- Proficiency bonus: Toplam level'a göre
- Spell slots: Multiclass spellcaster table
- Class features'lar ayrı hesaplanır

**Not:** Bu oldukça karmaşık, şimdilik skip edilebilir

---

### 8. Initiative (Giriş Sırası) (Basit)
**Mevcut Durum:** Hesaplanmıyor
**D&D 5e Kuralı:** `DEX modifier` (proficiency bonus eklenmez)

**Eksik:** Initiative hesaplama basit eklenebilir

---

### 9. Level Up Kuralları (Önemli)
**Mevcut Durum:** Level up ekranı var ama kurallar tam değil
**D&D 5e Kuralları:**
- HP artışı: Hit die + CON modifier (veya ortalama: hit die/2 + 1 + CON)
- Yeni class features
- Spell slots artışı
- ASI veya Feat (4/8/12/16/19)
- Subclass seçimi (3. seviyede)

**Eksik:** Level up ekranında bu kuralların otomatik uygulanması

---

## 📊 Öncelik Sırası

### 🔴 Kritik (Hemen Eklenmeli)
1. **Skill Proficiencies Kombinasyonu** - Background + Class skills birleştirme
2. **Spell Preparation** - Wizard/Cleric vs Sorcerer/Bard farkı

### 🟡 Önemli (Kısa Vadede)
3. **Subclass Seçimi** - 3. seviyede subclass seçim ekranı
4. **Feat vs ASI** - Level up'ta seçim ekranı
5. **Expertise** - Rogue/Bard için double proficiency

### 🟢 Orta (Uzun Vadede)
6. **Starting Equipment GUI** - Ekipman seçim ekranı
7. **Level Up Otomasyonu** - Kuralların otomatik uygulanması
8. **Initiative** - Basit hesaplama

### ⚪ Düşük (İleride)
9. **Multiclassing** - Çok karmaşık, şimdilik skip

---

## 🛠️ Nasıl Ekleyebiliriz?

### 1. Kural Dosyası Yapısı
Kuralları `data/dnd_rules.json` dosyasına ekleyebiliriz:

```json
{
  "skill_proficiencies": {
    "rule": "Background skills + Class skills (overlap tekrar sayılmaz)"
  },
  "spell_preparation": {
    "prepared_casters": ["Wizard", "Cleric", "Druid", "Paladin"],
    "known_casters": ["Sorcerer", "Bard", "Warlock", "Ranger"],
    "preparation_formula": "level + spellcasting_ability_modifier"
  },
  "expertise": {
    "rogue": {
      "level_1": {
        "skills": 2,
        "description": "Choose 2 skill proficiencies for expertise"
      }
    },
    "bard": {
      "level_3": {
        "skills": 2,
        "description": "Choose 2 skill proficiencies for expertise"
      }
    }
  }
}
```

### 2. GUI Entegrasyonu
- Her kural için GUI widget'ı ekle
- Kural doğrulama fonksiyonları
- Otomatik hesaplama tetikleme

### 3. Test Senaryoları
- Farklı class kombinasyonları test et
- Edge case'leri kontrol et (Human Variant, multiclass hazırlığı)

---

## 📝 Sonuç

**Mevcut Durum:** %60-70 tamamlanmış
**Eksik Kısımlar:** Skill combinations, Spell preparation, Subclass, Feat/ASI
**Önerilen Yaklaşım:** Öncelik sırasına göre adım adım ekleme






## ✅ Mevcut Kurallar (Uygulanmış)

### 1. Temel Karakter Oluşturma
- ✅ Irk seçimi ve yetenek puanı artışları
- ✅ Sınıf seçimi
- ✅ Arka plan seçimi
- ✅ Point-buy sistemi (27 puan)
- ✅ Yetenek modifier hesaplama: `(score - 10) // 2`

### 2. Hesaplama Fonksiyonları
- ✅ **Hit Points**: 1st level = max hit die + CON modifier
- ✅ **Proficiency Bonus**: Level'a göre (+2 to +6)
- ✅ **Armor Class**: 10 + DEX modifier (armor yoksa)
- ✅ **Saving Throws**: Class'a göre proficiency
- ✅ **Spell Slots**: Level ve class'a göre
- ✅ **Spell Save DC**: 8 + proficiency + spellcasting ability modifier
- ✅ **Spell Attack Bonus**: Proficiency + spellcasting ability modifier
- ✅ **Passive Perception**: 10 + WIS modifier + proficiency (eğer Perception proficient)

### 3. Dinamik Kural Desteği
- ✅ `calculate_dynamic_hit_points` - Kurallara göre HP hesaplama
- ✅ `calculate_dynamic_proficiency_bonus` - Kurallara göre proficiency
- ✅ `calculate_dynamic_armor_class` - Kurallara göre AC hesaplama
- ✅ Rule storage ve loading sistemi mevcut

---

## ⚠️ Eksik veya İyileştirilebilir Kurallar

### 1. Skill Proficiencies (Kritik)
**Mevcut Durum:** Class skills seçimi var ama background skills ile birleştirme eksik
**D&D 5e Kuralı:**
- Background'dan 2 skill proficiency
- Class'dan belirli sayıda skill proficiency (sınıfa göre değişir)
- Bazı skill'ler hem background hem class'ta olabilir (tekrar sayılmaz)
- Total: Background + Class skill sayısı (max 2 overlap)

**Eksik:**
```python
# Şu an sadece class skills seçiliyor, background skills eklenmiyor
selected_skills = [item.text() for item in self.wiz_skills.selectedItems()]
character["skills"]["class_skills"] = selected_skills
```

**Gerekli Düzeltme:**
```python
# Background skills otomatik eklenmeli
background_data = self.data["backgrounds"][character["background"]]
background_skills = background_data.get("skill_proficiencies", [])
class_skills = selected_skills  # Kullanıcı seçtiği skills

# Birleştir (tekrar edenler bir kez sayılır)
all_proficient_skills = list(set(background_skills + class_skills))
character["skills"]["proficiencies"] = all_proficient_skills
```

---

### 2. Starting Equipment Seçimi (Orta Öncelik)
**Mevcut Durum:** `starting_equipment_options` veri dosyasında var ama GUI'de tam entegre değil
**D&D 5e Kuralı:**
- Class'a göre başlangıç ekipmanı seçenekleri
- Background'dan da ekipman gelir
- "A or B" seçimleri
- "Any X" seçimleri

**Eksik:** Kullanıcı ekipman seçimini adım bazlı yapamıyor

---

### 3. Subclass (Archetype) Seçimi (Önemli)
**Mevcut Durum:** Veri dosyasında subclass'lar var ama GUI'de seçim yapılamıyor
**D&D 5e Kuralı:**
- Çoğu class 3. seviyede subclass seçer
- Bazı class'lar 1. seviyede seçer (Cleric, Sorcerer, Warlock)
- Subclass seçimi class features'ı değiştirir

**Eksik:** 3. seviyede subclass seçimi GUI'de yok

**Gerekli Ek:**
- Level up ekranında subclass seçim adımı
- Subclass seçildikten sonra class features güncelleme

---

### 4. Feat vs ASI (Ability Score Improvement) (Önemli)
**Mevcut Durum:** Feat seçimi var ama ASI ile karşılaştırma yok
**D&D 5e Kuralı:**
- 4, 8, 12, 16, 19. seviyelerde: Feat **VEYA** +2 ASI **VEYA** +1/+1 ASI
- Bazı feat'ler önkoşul gerektirir (ability score minimum'ları)
- Human Variant: 1. seviyede feat alabilir

**Eksik:** Level up'ta feat vs ASI seçimi yok

**Gerekli Ek:**
- Level up ekranında "Feat" veya "ASI" seçimi
- ASI seçildiğinde: +2 tek yetenek veya +1/+1 iki yetenek
- Feat seçildiğinde: Önkoşul kontrolü

---

### 5. Spell Preparation (Büyü Hazırlama) (Kritik)
**Mevcut Durum:** Spell listesi var ama preparation sistemi yok
**D&D 5e Kuralı:**
- **Wizard**: Spell book'tan hazırlanır (Level + INT modifier kadar spell)
- **Cleric/Druid/Paladin**: Tüm spell listesinden hazırlanır (Level + spellcasting modifier)
- **Sorcerer/Bard/Warlock**: Hazırlanmaz, bilinen spell'ler (spells known)
- **Ranger**: Spells known (hazırlanmaz)

**Eksik:** Spell preparation hesaplama ve GUI yok

**Gerekli Ek:**
```python
def calculate_spells_prepared(character, class_data):
    char_class = character["class"]
    level = character["level"]
    abilities = character["abilities"]
    
    if char_class in ["Sorcerer", "Bard", "Warlock", "Ranger"]:
        # Spells Known sistem (hazırlanmaz)
        return None  # Sadece bilinen spell'ler
    
    # Spellcasting ability modifier'ı al
    spellcasting_ability = get_spellcasting_ability(char_class)
    modifier = calculate_ability_modifier(abilities[spellcasting_ability])
    
    # Hazırlanan spell sayısı = Level + modifier
    spells_prepared = level + modifier
    return min(spells_prepared, get_spell_slots(character)[level])  # Max spell slot sayısı
```

---

### 6. Expertise (Uzmanlık) (Önemli)
**Mevcut Durum:** Rogue ve Bard için Expertise yok
**D&D 5e Kuralı:**
- Rogue: 1. seviyede 2 skill'e expertise (double proficiency)
- Bard: 3. seviyede expertise alır
- Ranger: Bazı subclass'lar expertise verir

**Eksik:** Expertise skill'leri işaretleme ve hesaplama yok

**Gerekli Ek:**
```python
# Skill modifier hesaplama
skill_modifier = ability_modifier
if skill in proficient_skills:
    skill_modifier += proficiency_bonus
if skill in expertise_skills:  # YENİ
    skill_modifier += proficiency_bonus  # Double proficiency
```

---

### 7. Multiclassing (Çok Sınıflı) (Düşük Öncelik)
**Mevcut Durum:** Yok
**D&D 5e Kuralları:**
- Ability score minimum'ları (her iki class için)
- Hit dice kombinasyonu
- Proficiency bonus: Toplam level'a göre
- Spell slots: Multiclass spellcaster table
- Class features'lar ayrı hesaplanır

**Not:** Bu oldukça karmaşık, şimdilik skip edilebilir

---

### 8. Initiative (Giriş Sırası) (Basit)
**Mevcut Durum:** Hesaplanmıyor
**D&D 5e Kuralı:** `DEX modifier` (proficiency bonus eklenmez)

**Eksik:** Initiative hesaplama basit eklenebilir

---

### 9. Level Up Kuralları (Önemli)
**Mevcut Durum:** Level up ekranı var ama kurallar tam değil
**D&D 5e Kuralları:**
- HP artışı: Hit die + CON modifier (veya ortalama: hit die/2 + 1 + CON)
- Yeni class features
- Spell slots artışı
- ASI veya Feat (4/8/12/16/19)
- Subclass seçimi (3. seviyede)

**Eksik:** Level up ekranında bu kuralların otomatik uygulanması

---

## 📊 Öncelik Sırası

### 🔴 Kritik (Hemen Eklenmeli)
1. **Skill Proficiencies Kombinasyonu** - Background + Class skills birleştirme
2. **Spell Preparation** - Wizard/Cleric vs Sorcerer/Bard farkı

### 🟡 Önemli (Kısa Vadede)
3. **Subclass Seçimi** - 3. seviyede subclass seçim ekranı
4. **Feat vs ASI** - Level up'ta seçim ekranı
5. **Expertise** - Rogue/Bard için double proficiency

### 🟢 Orta (Uzun Vadede)
6. **Starting Equipment GUI** - Ekipman seçim ekranı
7. **Level Up Otomasyonu** - Kuralların otomatik uygulanması
8. **Initiative** - Basit hesaplama

### ⚪ Düşük (İleride)
9. **Multiclassing** - Çok karmaşık, şimdilik skip

---

## 🛠️ Nasıl Ekleyebiliriz?

### 1. Kural Dosyası Yapısı
Kuralları `data/dnd_rules.json` dosyasına ekleyebiliriz:

```json
{
  "skill_proficiencies": {
    "rule": "Background skills + Class skills (overlap tekrar sayılmaz)"
  },
  "spell_preparation": {
    "prepared_casters": ["Wizard", "Cleric", "Druid", "Paladin"],
    "known_casters": ["Sorcerer", "Bard", "Warlock", "Ranger"],
    "preparation_formula": "level + spellcasting_ability_modifier"
  },
  "expertise": {
    "rogue": {
      "level_1": {
        "skills": 2,
        "description": "Choose 2 skill proficiencies for expertise"
      }
    },
    "bard": {
      "level_3": {
        "skills": 2,
        "description": "Choose 2 skill proficiencies for expertise"
      }
    }
  }
}
```

### 2. GUI Entegrasyonu
- Her kural için GUI widget'ı ekle
- Kural doğrulama fonksiyonları
- Otomatik hesaplama tetikleme

### 3. Test Senaryoları
- Farklı class kombinasyonları test et
- Edge case'leri kontrol et (Human Variant, multiclass hazırlığı)

---

## 📝 Sonuç

**Mevcut Durum:** %60-70 tamamlanmış
**Eksik Kısımlar:** Skill combinations, Spell preparation, Subclass, Feat/ASI
**Önerilen Yaklaşım:** Öncelik sırasına göre adım adım ekleme




## ✅ Mevcut Kurallar (Uygulanmış)

### 1. Temel Karakter Oluşturma
- ✅ Irk seçimi ve yetenek puanı artışları
- ✅ Sınıf seçimi
- ✅ Arka plan seçimi
- ✅ Point-buy sistemi (27 puan)
- ✅ Yetenek modifier hesaplama: `(score - 10) // 2`

### 2. Hesaplama Fonksiyonları
- ✅ **Hit Points**: 1st level = max hit die + CON modifier
- ✅ **Proficiency Bonus**: Level'a göre (+2 to +6)
- ✅ **Armor Class**: 10 + DEX modifier (armor yoksa)
- ✅ **Saving Throws**: Class'a göre proficiency
- ✅ **Spell Slots**: Level ve class'a göre
- ✅ **Spell Save DC**: 8 + proficiency + spellcasting ability modifier
- ✅ **Spell Attack Bonus**: Proficiency + spellcasting ability modifier
- ✅ **Passive Perception**: 10 + WIS modifier + proficiency (eğer Perception proficient)

### 3. Dinamik Kural Desteği
- ✅ `calculate_dynamic_hit_points` - Kurallara göre HP hesaplama
- ✅ `calculate_dynamic_proficiency_bonus` - Kurallara göre proficiency
- ✅ `calculate_dynamic_armor_class` - Kurallara göre AC hesaplama
- ✅ Rule storage ve loading sistemi mevcut

---

## ⚠️ Eksik veya İyileştirilebilir Kurallar

### 1. Skill Proficiencies (Kritik)
**Mevcut Durum:** Class skills seçimi var ama background skills ile birleştirme eksik
**D&D 5e Kuralı:**
- Background'dan 2 skill proficiency
- Class'dan belirli sayıda skill proficiency (sınıfa göre değişir)
- Bazı skill'ler hem background hem class'ta olabilir (tekrar sayılmaz)
- Total: Background + Class skill sayısı (max 2 overlap)

**Eksik:**
```python
# Şu an sadece class skills seçiliyor, background skills eklenmiyor
selected_skills = [item.text() for item in self.wiz_skills.selectedItems()]
character["skills"]["class_skills"] = selected_skills
```

**Gerekli Düzeltme:**
```python
# Background skills otomatik eklenmeli
background_data = self.data["backgrounds"][character["background"]]
background_skills = background_data.get("skill_proficiencies", [])
class_skills = selected_skills  # Kullanıcı seçtiği skills

# Birleştir (tekrar edenler bir kez sayılır)
all_proficient_skills = list(set(background_skills + class_skills))
character["skills"]["proficiencies"] = all_proficient_skills
```

---

### 2. Starting Equipment Seçimi (Orta Öncelik)
**Mevcut Durum:** `starting_equipment_options` veri dosyasında var ama GUI'de tam entegre değil
**D&D 5e Kuralı:**
- Class'a göre başlangıç ekipmanı seçenekleri
- Background'dan da ekipman gelir
- "A or B" seçimleri
- "Any X" seçimleri

**Eksik:** Kullanıcı ekipman seçimini adım bazlı yapamıyor

---

### 3. Subclass (Archetype) Seçimi (Önemli)
**Mevcut Durum:** Veri dosyasında subclass'lar var ama GUI'de seçim yapılamıyor
**D&D 5e Kuralı:**
- Çoğu class 3. seviyede subclass seçer
- Bazı class'lar 1. seviyede seçer (Cleric, Sorcerer, Warlock)
- Subclass seçimi class features'ı değiştirir

**Eksik:** 3. seviyede subclass seçimi GUI'de yok

**Gerekli Ek:**
- Level up ekranında subclass seçim adımı
- Subclass seçildikten sonra class features güncelleme

---

### 4. Feat vs ASI (Ability Score Improvement) (Önemli)
**Mevcut Durum:** Feat seçimi var ama ASI ile karşılaştırma yok
**D&D 5e Kuralı:**
- 4, 8, 12, 16, 19. seviyelerde: Feat **VEYA** +2 ASI **VEYA** +1/+1 ASI
- Bazı feat'ler önkoşul gerektirir (ability score minimum'ları)
- Human Variant: 1. seviyede feat alabilir

**Eksik:** Level up'ta feat vs ASI seçimi yok

**Gerekli Ek:**
- Level up ekranında "Feat" veya "ASI" seçimi
- ASI seçildiğinde: +2 tek yetenek veya +1/+1 iki yetenek
- Feat seçildiğinde: Önkoşul kontrolü

---

### 5. Spell Preparation (Büyü Hazırlama) (Kritik)
**Mevcut Durum:** Spell listesi var ama preparation sistemi yok
**D&D 5e Kuralı:**
- **Wizard**: Spell book'tan hazırlanır (Level + INT modifier kadar spell)
- **Cleric/Druid/Paladin**: Tüm spell listesinden hazırlanır (Level + spellcasting modifier)
- **Sorcerer/Bard/Warlock**: Hazırlanmaz, bilinen spell'ler (spells known)
- **Ranger**: Spells known (hazırlanmaz)

**Eksik:** Spell preparation hesaplama ve GUI yok

**Gerekli Ek:**
```python
def calculate_spells_prepared(character, class_data):
    char_class = character["class"]
    level = character["level"]
    abilities = character["abilities"]
    
    if char_class in ["Sorcerer", "Bard", "Warlock", "Ranger"]:
        # Spells Known sistem (hazırlanmaz)
        return None  # Sadece bilinen spell'ler
    
    # Spellcasting ability modifier'ı al
    spellcasting_ability = get_spellcasting_ability(char_class)
    modifier = calculate_ability_modifier(abilities[spellcasting_ability])
    
    # Hazırlanan spell sayısı = Level + modifier
    spells_prepared = level + modifier
    return min(spells_prepared, get_spell_slots(character)[level])  # Max spell slot sayısı
```

---

### 6. Expertise (Uzmanlık) (Önemli)
**Mevcut Durum:** Rogue ve Bard için Expertise yok
**D&D 5e Kuralı:**
- Rogue: 1. seviyede 2 skill'e expertise (double proficiency)
- Bard: 3. seviyede expertise alır
- Ranger: Bazı subclass'lar expertise verir

**Eksik:** Expertise skill'leri işaretleme ve hesaplama yok

**Gerekli Ek:**
```python
# Skill modifier hesaplama
skill_modifier = ability_modifier
if skill in proficient_skills:
    skill_modifier += proficiency_bonus
if skill in expertise_skills:  # YENİ
    skill_modifier += proficiency_bonus  # Double proficiency
```

---

### 7. Multiclassing (Çok Sınıflı) (Düşük Öncelik)
**Mevcut Durum:** Yok
**D&D 5e Kuralları:**
- Ability score minimum'ları (her iki class için)
- Hit dice kombinasyonu
- Proficiency bonus: Toplam level'a göre
- Spell slots: Multiclass spellcaster table
- Class features'lar ayrı hesaplanır

**Not:** Bu oldukça karmaşık, şimdilik skip edilebilir

---

### 8. Initiative (Giriş Sırası) (Basit)
**Mevcut Durum:** Hesaplanmıyor
**D&D 5e Kuralı:** `DEX modifier` (proficiency bonus eklenmez)

**Eksik:** Initiative hesaplama basit eklenebilir

---

### 9. Level Up Kuralları (Önemli)
**Mevcut Durum:** Level up ekranı var ama kurallar tam değil
**D&D 5e Kuralları:**
- HP artışı: Hit die + CON modifier (veya ortalama: hit die/2 + 1 + CON)
- Yeni class features
- Spell slots artışı
- ASI veya Feat (4/8/12/16/19)
- Subclass seçimi (3. seviyede)

**Eksik:** Level up ekranında bu kuralların otomatik uygulanması

---

## 📊 Öncelik Sırası

### 🔴 Kritik (Hemen Eklenmeli)
1. **Skill Proficiencies Kombinasyonu** - Background + Class skills birleştirme
2. **Spell Preparation** - Wizard/Cleric vs Sorcerer/Bard farkı

### 🟡 Önemli (Kısa Vadede)
3. **Subclass Seçimi** - 3. seviyede subclass seçim ekranı
4. **Feat vs ASI** - Level up'ta seçim ekranı
5. **Expertise** - Rogue/Bard için double proficiency

### 🟢 Orta (Uzun Vadede)
6. **Starting Equipment GUI** - Ekipman seçim ekranı
7. **Level Up Otomasyonu** - Kuralların otomatik uygulanması
8. **Initiative** - Basit hesaplama

### ⚪ Düşük (İleride)
9. **Multiclassing** - Çok karmaşık, şimdilik skip

---

## 🛠️ Nasıl Ekleyebiliriz?

### 1. Kural Dosyası Yapısı
Kuralları `data/dnd_rules.json` dosyasına ekleyebiliriz:

```json
{
  "skill_proficiencies": {
    "rule": "Background skills + Class skills (overlap tekrar sayılmaz)"
  },
  "spell_preparation": {
    "prepared_casters": ["Wizard", "Cleric", "Druid", "Paladin"],
    "known_casters": ["Sorcerer", "Bard", "Warlock", "Ranger"],
    "preparation_formula": "level + spellcasting_ability_modifier"
  },
  "expertise": {
    "rogue": {
      "level_1": {
        "skills": 2,
        "description": "Choose 2 skill proficiencies for expertise"
      }
    },
    "bard": {
      "level_3": {
        "skills": 2,
        "description": "Choose 2 skill proficiencies for expertise"
      }
    }
  }
}
```

### 2. GUI Entegrasyonu
- Her kural için GUI widget'ı ekle
- Kural doğrulama fonksiyonları
- Otomatik hesaplama tetikleme

### 3. Test Senaryoları
- Farklı class kombinasyonları test et
- Edge case'leri kontrol et (Human Variant, multiclass hazırlığı)

---

## 📝 Sonuç

**Mevcut Durum:** %60-70 tamamlanmış
**Eksik Kısımlar:** Skill combinations, Spell preparation, Subclass, Feat/ASI
**Önerilen Yaklaşım:** Öncelik sırasına göre adım adım ekleme







