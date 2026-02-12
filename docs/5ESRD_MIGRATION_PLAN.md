# 5esrd.com D&D 5e Veri Güncelleme Planı

## Genel Bakış
Tüm D&D 5e verilerini (sınıflar, büyüler, ırklar, featler, arka planlar, ekipmanlar) [5esrd.com](https://www.5esrd.com/) sitesinden çekip mevcut verilerle birleştireceğiz.

## Mevcut Durum
- **Races**: 29 (mevcut)
- **Classes**: 14 (mevcut)
- **Spells**: 0 ❌ (çekilmesi gerekiyor)
- **Backgrounds**: 57 (mevcut)
- **Feats**: 0 ❌ (çekilmesi gerekiyor)
- **Equipment**: 9 (eksik - çekilmesi gerekiyor)

## Hedefler

### 1. Races (Irklar)
- **Kaynak**: https://www.5esrd.com/races/
- **Mevcut**: 29 race
- **Hedef**: Tüm SRD ırkları + subraces
- **Öncelik**: Yüksek (temel veri)

### 2. Classes (Sınıflar)
- **Kaynak**: https://www.5esrd.com/classes/ ve https://www.5esrd.com/database/class
- **Mevcut**: 14 class
- **Hedef**: Tüm SRD sınıfları + subclasses
- **Öncelik**: Yüksek (temel veri)

### 3. Spells (Büyüler) - KRİTİK
- **Kaynak**: https://www.5esrd.com/spellcasting/ ve https://www.5esrd.com/database/spell
- **Mevcut**: 0 ❌
- **Hedef**: Tüm SRD büyüleri (tüm seviyeler, tüm sınıflar)
- **Öncelik**: ÇOK YÜKSEK (eksik veri)

### 4. Feats (Yetenekler)
- **Kaynak**: https://www.5esrd.com/feats/ ve https://www.5esrd.com/database/feats/
- **Mevcut**: 0 ❌
- **Hedef**: Tüm SRD featleri
- **Öncelik**: Orta

### 5. Backgrounds (Arka Planlar)
- **Kaynak**: https://www.5esrd.com/backgrounds/ ve https://www.5esrd.com/database/background/
- **Mevcut**: 57 (iyi durumda)
- **Hedef**: Tüm SRD arka planları (güncelleme)
- **Öncelik**: Düşük

### 6. Equipment (Ekipman)
- **Kaynak**: https://www.5esrd.com/equipment/
- **Mevcut**: 9 (eksik)
- **Hedef**: Tüm ekipmanlar (armor, weapons, gear, tools, etc.)
- **Öncelik**: Orta

## Adım Adım Plan

### Faz 1: Analiz ve Hazırlık ✅ (Tamamlandı)
- [x] 5esrd.com yapısını analiz et
- [x] Doğru URL'leri belirle
- [x] Mevcut verileri kontrol et

### Faz 2: Scraper Geliştirme
- [ ] Genel scraper framework'ü oluştur
- [ ] Her kategori için özel scraper fonksiyonları
- [ ] Error handling ve retry mekanizması
- [ ] Rate limiting (saygılı scraping)

### Faz 3: Veri Çekme (Öncelik Sırasıyla)
1. **Spells** (en kritik - şu an 0)
2. **Classes** (subclasses ile)
3. **Races** (subraces ile)
4. **Feats**
5. **Equipment**
6. **Backgrounds** (güncelleme)

### Faz 4: Veri Birleştirme
- [ ] Mevcut verilerle yeni verileri merge et
- [ ] Çakışmaları çöz (5esrd.com öncelikli)
- [ ] Veri kalitesi kontrolü

### Faz 5: Test ve Doğrulama
- [ ] Veri yapısını doğrula
- [ ] GUI entegrasyonunu test et
- [ ] Eksik verileri tespit et ve düzelt

## Teknik Detaylar

### URL Yapısı
- **Races**: `/races/[race-name]/`
- **Classes**: `/classes/[class-name]/` veya `/database/class/[class-name]`
- **Spells**: `/database/spell/[spell-name]` veya `/spellcasting/spell-lists/`
- **Feats**: `/feats/[feat-name]/` veya `/database/feats/[feat-name]`
- **Backgrounds**: `/backgrounds/[bg-name]/` veya `/database/background/[bg-name]`
- **Equipment**: `/equipment/[category]/[item-name]`

### Veri Yapısı
Mevcut `dnd_data.json` yapısını koruyarak genişletilecek:
```json
{
  "races": { ... },
  "classes": { ... },
  "spells": { ... },  // ŞU AN BOŞ!
  "feats": { ... },   // ŞU AN BOŞ!
  "backgrounds": { ... },
  "equipment": { ... }
}
```

### Scraper Özellikleri
- **Retry mekanizması**: Başarısız istekleri 3 kez tekrar dene
- **Rate limiting**: İstekler arasında 1-2 saniye bekle
- **Cache**: Çekilen verileri cache'le (tekrar çekmeyi önle)
- **Progress tracking**: İlerlemeyi göster
- **Error logging**: Hataları logla

## İlk Adım
**Spells scraper'ını oluştur** - En kritik eksik veri!




## Genel Bakış
Tüm D&D 5e verilerini (sınıflar, büyüler, ırklar, featler, arka planlar, ekipmanlar) [5esrd.com](https://www.5esrd.com/) sitesinden çekip mevcut verilerle birleştireceğiz.

## Mevcut Durum
- **Races**: 29 (mevcut)
- **Classes**: 14 (mevcut)
- **Spells**: 0 ❌ (çekilmesi gerekiyor)
- **Backgrounds**: 57 (mevcut)
- **Feats**: 0 ❌ (çekilmesi gerekiyor)
- **Equipment**: 9 (eksik - çekilmesi gerekiyor)

## Hedefler

### 1. Races (Irklar)
- **Kaynak**: https://www.5esrd.com/races/
- **Mevcut**: 29 race
- **Hedef**: Tüm SRD ırkları + subraces
- **Öncelik**: Yüksek (temel veri)

### 2. Classes (Sınıflar)
- **Kaynak**: https://www.5esrd.com/classes/ ve https://www.5esrd.com/database/class
- **Mevcut**: 14 class
- **Hedef**: Tüm SRD sınıfları + subclasses
- **Öncelik**: Yüksek (temel veri)

### 3. Spells (Büyüler) - KRİTİK
- **Kaynak**: https://www.5esrd.com/spellcasting/ ve https://www.5esrd.com/database/spell
- **Mevcut**: 0 ❌
- **Hedef**: Tüm SRD büyüleri (tüm seviyeler, tüm sınıflar)
- **Öncelik**: ÇOK YÜKSEK (eksik veri)

### 4. Feats (Yetenekler)
- **Kaynak**: https://www.5esrd.com/feats/ ve https://www.5esrd.com/database/feats/
- **Mevcut**: 0 ❌
- **Hedef**: Tüm SRD featleri
- **Öncelik**: Orta

### 5. Backgrounds (Arka Planlar)
- **Kaynak**: https://www.5esrd.com/backgrounds/ ve https://www.5esrd.com/database/background/
- **Mevcut**: 57 (iyi durumda)
- **Hedef**: Tüm SRD arka planları (güncelleme)
- **Öncelik**: Düşük

### 6. Equipment (Ekipman)
- **Kaynak**: https://www.5esrd.com/equipment/
- **Mevcut**: 9 (eksik)
- **Hedef**: Tüm ekipmanlar (armor, weapons, gear, tools, etc.)
- **Öncelik**: Orta

## Adım Adım Plan

### Faz 1: Analiz ve Hazırlık ✅ (Tamamlandı)
- [x] 5esrd.com yapısını analiz et
- [x] Doğru URL'leri belirle
- [x] Mevcut verileri kontrol et

### Faz 2: Scraper Geliştirme
- [ ] Genel scraper framework'ü oluştur
- [ ] Her kategori için özel scraper fonksiyonları
- [ ] Error handling ve retry mekanizması
- [ ] Rate limiting (saygılı scraping)

### Faz 3: Veri Çekme (Öncelik Sırasıyla)
1. **Spells** (en kritik - şu an 0)
2. **Classes** (subclasses ile)
3. **Races** (subraces ile)
4. **Feats**
5. **Equipment**
6. **Backgrounds** (güncelleme)

### Faz 4: Veri Birleştirme
- [ ] Mevcut verilerle yeni verileri merge et
- [ ] Çakışmaları çöz (5esrd.com öncelikli)
- [ ] Veri kalitesi kontrolü

### Faz 5: Test ve Doğrulama
- [ ] Veri yapısını doğrula
- [ ] GUI entegrasyonunu test et
- [ ] Eksik verileri tespit et ve düzelt

## Teknik Detaylar

### URL Yapısı
- **Races**: `/races/[race-name]/`
- **Classes**: `/classes/[class-name]/` veya `/database/class/[class-name]`
- **Spells**: `/database/spell/[spell-name]` veya `/spellcasting/spell-lists/`
- **Feats**: `/feats/[feat-name]/` veya `/database/feats/[feat-name]`
- **Backgrounds**: `/backgrounds/[bg-name]/` veya `/database/background/[bg-name]`
- **Equipment**: `/equipment/[category]/[item-name]`

### Veri Yapısı
Mevcut `dnd_data.json` yapısını koruyarak genişletilecek:
```json
{
  "races": { ... },
  "classes": { ... },
  "spells": { ... },  // ŞU AN BOŞ!
  "feats": { ... },   // ŞU AN BOŞ!
  "backgrounds": { ... },
  "equipment": { ... }
}
```

### Scraper Özellikleri
- **Retry mekanizması**: Başarısız istekleri 3 kez tekrar dene
- **Rate limiting**: İstekler arasında 1-2 saniye bekle
- **Cache**: Çekilen verileri cache'le (tekrar çekmeyi önle)
- **Progress tracking**: İlerlemeyi göster
- **Error logging**: Hataları logla

## İlk Adım
**Spells scraper'ını oluştur** - En kritik eksik veri!






## Genel Bakış
Tüm D&D 5e verilerini (sınıflar, büyüler, ırklar, featler, arka planlar, ekipmanlar) [5esrd.com](https://www.5esrd.com/) sitesinden çekip mevcut verilerle birleştireceğiz.

## Mevcut Durum
- **Races**: 29 (mevcut)
- **Classes**: 14 (mevcut)
- **Spells**: 0 ❌ (çekilmesi gerekiyor)
- **Backgrounds**: 57 (mevcut)
- **Feats**: 0 ❌ (çekilmesi gerekiyor)
- **Equipment**: 9 (eksik - çekilmesi gerekiyor)

## Hedefler

### 1. Races (Irklar)
- **Kaynak**: https://www.5esrd.com/races/
- **Mevcut**: 29 race
- **Hedef**: Tüm SRD ırkları + subraces
- **Öncelik**: Yüksek (temel veri)

### 2. Classes (Sınıflar)
- **Kaynak**: https://www.5esrd.com/classes/ ve https://www.5esrd.com/database/class
- **Mevcut**: 14 class
- **Hedef**: Tüm SRD sınıfları + subclasses
- **Öncelik**: Yüksek (temel veri)

### 3. Spells (Büyüler) - KRİTİK
- **Kaynak**: https://www.5esrd.com/spellcasting/ ve https://www.5esrd.com/database/spell
- **Mevcut**: 0 ❌
- **Hedef**: Tüm SRD büyüleri (tüm seviyeler, tüm sınıflar)
- **Öncelik**: ÇOK YÜKSEK (eksik veri)

### 4. Feats (Yetenekler)
- **Kaynak**: https://www.5esrd.com/feats/ ve https://www.5esrd.com/database/feats/
- **Mevcut**: 0 ❌
- **Hedef**: Tüm SRD featleri
- **Öncelik**: Orta

### 5. Backgrounds (Arka Planlar)
- **Kaynak**: https://www.5esrd.com/backgrounds/ ve https://www.5esrd.com/database/background/
- **Mevcut**: 57 (iyi durumda)
- **Hedef**: Tüm SRD arka planları (güncelleme)
- **Öncelik**: Düşük

### 6. Equipment (Ekipman)
- **Kaynak**: https://www.5esrd.com/equipment/
- **Mevcut**: 9 (eksik)
- **Hedef**: Tüm ekipmanlar (armor, weapons, gear, tools, etc.)
- **Öncelik**: Orta

## Adım Adım Plan

### Faz 1: Analiz ve Hazırlık ✅ (Tamamlandı)
- [x] 5esrd.com yapısını analiz et
- [x] Doğru URL'leri belirle
- [x] Mevcut verileri kontrol et

### Faz 2: Scraper Geliştirme
- [ ] Genel scraper framework'ü oluştur
- [ ] Her kategori için özel scraper fonksiyonları
- [ ] Error handling ve retry mekanizması
- [ ] Rate limiting (saygılı scraping)

### Faz 3: Veri Çekme (Öncelik Sırasıyla)
1. **Spells** (en kritik - şu an 0)
2. **Classes** (subclasses ile)
3. **Races** (subraces ile)
4. **Feats**
5. **Equipment**
6. **Backgrounds** (güncelleme)

### Faz 4: Veri Birleştirme
- [ ] Mevcut verilerle yeni verileri merge et
- [ ] Çakışmaları çöz (5esrd.com öncelikli)
- [ ] Veri kalitesi kontrolü

### Faz 5: Test ve Doğrulama
- [ ] Veri yapısını doğrula
- [ ] GUI entegrasyonunu test et
- [ ] Eksik verileri tespit et ve düzelt

## Teknik Detaylar

### URL Yapısı
- **Races**: `/races/[race-name]/`
- **Classes**: `/classes/[class-name]/` veya `/database/class/[class-name]`
- **Spells**: `/database/spell/[spell-name]` veya `/spellcasting/spell-lists/`
- **Feats**: `/feats/[feat-name]/` veya `/database/feats/[feat-name]`
- **Backgrounds**: `/backgrounds/[bg-name]/` veya `/database/background/[bg-name]`
- **Equipment**: `/equipment/[category]/[item-name]`

### Veri Yapısı
Mevcut `dnd_data.json` yapısını koruyarak genişletilecek:
```json
{
  "races": { ... },
  "classes": { ... },
  "spells": { ... },  // ŞU AN BOŞ!
  "feats": { ... },   // ŞU AN BOŞ!
  "backgrounds": { ... },
  "equipment": { ... }
}
```

### Scraper Özellikleri
- **Retry mekanizması**: Başarısız istekleri 3 kez tekrar dene
- **Rate limiting**: İstekler arasında 1-2 saniye bekle
- **Cache**: Çekilen verileri cache'le (tekrar çekmeyi önle)
- **Progress tracking**: İlerlemeyi göster
- **Error logging**: Hataları logla

## İlk Adım
**Spells scraper'ını oluştur** - En kritik eksik veri!




## Genel Bakış
Tüm D&D 5e verilerini (sınıflar, büyüler, ırklar, featler, arka planlar, ekipmanlar) [5esrd.com](https://www.5esrd.com/) sitesinden çekip mevcut verilerle birleştireceğiz.

## Mevcut Durum
- **Races**: 29 (mevcut)
- **Classes**: 14 (mevcut)
- **Spells**: 0 ❌ (çekilmesi gerekiyor)
- **Backgrounds**: 57 (mevcut)
- **Feats**: 0 ❌ (çekilmesi gerekiyor)
- **Equipment**: 9 (eksik - çekilmesi gerekiyor)

## Hedefler

### 1. Races (Irklar)
- **Kaynak**: https://www.5esrd.com/races/
- **Mevcut**: 29 race
- **Hedef**: Tüm SRD ırkları + subraces
- **Öncelik**: Yüksek (temel veri)

### 2. Classes (Sınıflar)
- **Kaynak**: https://www.5esrd.com/classes/ ve https://www.5esrd.com/database/class
- **Mevcut**: 14 class
- **Hedef**: Tüm SRD sınıfları + subclasses
- **Öncelik**: Yüksek (temel veri)

### 3. Spells (Büyüler) - KRİTİK
- **Kaynak**: https://www.5esrd.com/spellcasting/ ve https://www.5esrd.com/database/spell
- **Mevcut**: 0 ❌
- **Hedef**: Tüm SRD büyüleri (tüm seviyeler, tüm sınıflar)
- **Öncelik**: ÇOK YÜKSEK (eksik veri)

### 4. Feats (Yetenekler)
- **Kaynak**: https://www.5esrd.com/feats/ ve https://www.5esrd.com/database/feats/
- **Mevcut**: 0 ❌
- **Hedef**: Tüm SRD featleri
- **Öncelik**: Orta

### 5. Backgrounds (Arka Planlar)
- **Kaynak**: https://www.5esrd.com/backgrounds/ ve https://www.5esrd.com/database/background/
- **Mevcut**: 57 (iyi durumda)
- **Hedef**: Tüm SRD arka planları (güncelleme)
- **Öncelik**: Düşük

### 6. Equipment (Ekipman)
- **Kaynak**: https://www.5esrd.com/equipment/
- **Mevcut**: 9 (eksik)
- **Hedef**: Tüm ekipmanlar (armor, weapons, gear, tools, etc.)
- **Öncelik**: Orta

## Adım Adım Plan

### Faz 1: Analiz ve Hazırlık ✅ (Tamamlandı)
- [x] 5esrd.com yapısını analiz et
- [x] Doğru URL'leri belirle
- [x] Mevcut verileri kontrol et

### Faz 2: Scraper Geliştirme
- [ ] Genel scraper framework'ü oluştur
- [ ] Her kategori için özel scraper fonksiyonları
- [ ] Error handling ve retry mekanizması
- [ ] Rate limiting (saygılı scraping)

### Faz 3: Veri Çekme (Öncelik Sırasıyla)
1. **Spells** (en kritik - şu an 0)
2. **Classes** (subclasses ile)
3. **Races** (subraces ile)
4. **Feats**
5. **Equipment**
6. **Backgrounds** (güncelleme)

### Faz 4: Veri Birleştirme
- [ ] Mevcut verilerle yeni verileri merge et
- [ ] Çakışmaları çöz (5esrd.com öncelikli)
- [ ] Veri kalitesi kontrolü

### Faz 5: Test ve Doğrulama
- [ ] Veri yapısını doğrula
- [ ] GUI entegrasyonunu test et
- [ ] Eksik verileri tespit et ve düzelt

## Teknik Detaylar

### URL Yapısı
- **Races**: `/races/[race-name]/`
- **Classes**: `/classes/[class-name]/` veya `/database/class/[class-name]`
- **Spells**: `/database/spell/[spell-name]` veya `/spellcasting/spell-lists/`
- **Feats**: `/feats/[feat-name]/` veya `/database/feats/[feat-name]`
- **Backgrounds**: `/backgrounds/[bg-name]/` veya `/database/background/[bg-name]`
- **Equipment**: `/equipment/[category]/[item-name]`

### Veri Yapısı
Mevcut `dnd_data.json` yapısını koruyarak genişletilecek:
```json
{
  "races": { ... },
  "classes": { ... },
  "spells": { ... },  // ŞU AN BOŞ!
  "feats": { ... },   // ŞU AN BOŞ!
  "backgrounds": { ... },
  "equipment": { ... }
}
```

### Scraper Özellikleri
- **Retry mekanizması**: Başarısız istekleri 3 kez tekrar dene
- **Rate limiting**: İstekler arasında 1-2 saniye bekle
- **Cache**: Çekilen verileri cache'le (tekrar çekmeyi önle)
- **Progress tracking**: İlerlemeyi göster
- **Error logging**: Hataları logla

## İlk Adım
**Spells scraper'ını oluştur** - En kritik eksik veri!









