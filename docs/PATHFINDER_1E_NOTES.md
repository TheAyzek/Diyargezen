# Pathfinder 1e Entegrasyonu - Notlar

## Mevcut Durum

### Tamamlananlar ✅
- **Irklar**: 83 ırk çekildi (77 aonprd + 7 d20pfsrd)
- **Sınıflar**: 73 sınıf çekildi (55 aonprd + 22 d20pfsrd)
- **Feat'ler**: 421 feat çekildi (d20pfsrd'den)
- **GUI Sayfası**: PathfinderPage class'ı oluşturuldu
- **MainWindow Entegrasyonu**: Pathfinder 1e sekmesi eklendi

### Eksikler / TODO ⚠️

#### 1. Büyüler (Spells) - ÖNEMLİ
- **Durum**: Hiç çekilemedi (0 büyü)
- **Sorun**: 
  - Archives of Nethys: Spells.aspx sayfasında direkt SpellsDisplay linkleri yok
  - d20pfsrd: `/spells/` URL'si 404 veriyor
- **Çözüm Önerileri**:
  1. Archives of Nethys için kategori sayfalarını detaylı incele
  2. d20pfsrd için doğru spell URL yapısını bul (/magic/spells/ gibi alternatifler)
  3. JavaScript ile yüklenen içerik varsa Selenium kullan
  4. Manuel ekleme seçeneği sun (kullanıcı büyüleri JSON'dan ekleyebilir)

#### 2. Karakter Oluşturma Arayüzü
- **Durum**: Basit dialog var, adım bazlı sistem henüz yok
- **Gerekenler**:
  - DndPage'e benzer adım bazlı wizard sistemi
  - Irk seçimi
  - Yetenek puanları dağıtımı (point-buy)
  - Sınıf becerileri seçimi
  - Feat seçimi
  - Büyü seçimi (büyüler çekildikten sonra)
  - Ekipman seçimi
  - Kişilik özellikleri

#### 3. Karakter Kaydetme/Yükleme
- **Durum**: Henüz geliştirilmedi
- **Gerekenler**:
  - JSON formatında kaydetme
  - Karakter listesi görüntüleme
  - Karakter yükleme

#### 4. PDF Export
- **Durum**: Henüz geliştirilmedi
- **Gerekenler**:
  - Pathfinder 1e karakter sheet formatı
  - PDF export fonksiyonu

## Büyü Çekimi için Detaylı Plan

### Archives of Nethys
```
Spells.aspx ana sayfası -> Kategori/Level/Class sayfaları bul
Her kategori sayfasından -> SpellsDisplay.aspx?ItemName=... linklerini çek
Detay sayfasından -> Büyü bilgilerini parse et
```

### d20pfsrd
```
Doğru spell URL yapısını bul (muhtemelen /magic/spells/ veya benzeri)
Spell listesi sayfasından -> Spell detay linklerini bul
Detay sayfasından -> Büyü bilgilerini parse et
```

## Sonraki Adımlar

1. **Öncelik 1**: Büyüleri çek - Pathfinder 1e için kritik
2. **Öncelik 2**: Adım bazlı karakter oluşturma arayüzünü tamamla
3. **Öncelik 3**: Karakter kaydetme/yükleme özelliklerini ekle
4. **Öncelik 4**: PDF export özelliğini ekle




## Mevcut Durum

### Tamamlananlar ✅
- **Irklar**: 83 ırk çekildi (77 aonprd + 7 d20pfsrd)
- **Sınıflar**: 73 sınıf çekildi (55 aonprd + 22 d20pfsrd)
- **Feat'ler**: 421 feat çekildi (d20pfsrd'den)
- **GUI Sayfası**: PathfinderPage class'ı oluşturuldu
- **MainWindow Entegrasyonu**: Pathfinder 1e sekmesi eklendi

### Eksikler / TODO ⚠️

#### 1. Büyüler (Spells) - ÖNEMLİ
- **Durum**: Hiç çekilemedi (0 büyü)
- **Sorun**: 
  - Archives of Nethys: Spells.aspx sayfasında direkt SpellsDisplay linkleri yok
  - d20pfsrd: `/spells/` URL'si 404 veriyor
- **Çözüm Önerileri**:
  1. Archives of Nethys için kategori sayfalarını detaylı incele
  2. d20pfsrd için doğru spell URL yapısını bul (/magic/spells/ gibi alternatifler)
  3. JavaScript ile yüklenen içerik varsa Selenium kullan
  4. Manuel ekleme seçeneği sun (kullanıcı büyüleri JSON'dan ekleyebilir)

#### 2. Karakter Oluşturma Arayüzü
- **Durum**: Basit dialog var, adım bazlı sistem henüz yok
- **Gerekenler**:
  - DndPage'e benzer adım bazlı wizard sistemi
  - Irk seçimi
  - Yetenek puanları dağıtımı (point-buy)
  - Sınıf becerileri seçimi
  - Feat seçimi
  - Büyü seçimi (büyüler çekildikten sonra)
  - Ekipman seçimi
  - Kişilik özellikleri

#### 3. Karakter Kaydetme/Yükleme
- **Durum**: Henüz geliştirilmedi
- **Gerekenler**:
  - JSON formatında kaydetme
  - Karakter listesi görüntüleme
  - Karakter yükleme

#### 4. PDF Export
- **Durum**: Henüz geliştirilmedi
- **Gerekenler**:
  - Pathfinder 1e karakter sheet formatı
  - PDF export fonksiyonu

## Büyü Çekimi için Detaylı Plan

### Archives of Nethys
```
Spells.aspx ana sayfası -> Kategori/Level/Class sayfaları bul
Her kategori sayfasından -> SpellsDisplay.aspx?ItemName=... linklerini çek
Detay sayfasından -> Büyü bilgilerini parse et
```

### d20pfsrd
```
Doğru spell URL yapısını bul (muhtemelen /magic/spells/ veya benzeri)
Spell listesi sayfasından -> Spell detay linklerini bul
Detay sayfasından -> Büyü bilgilerini parse et
```

## Sonraki Adımlar

1. **Öncelik 1**: Büyüleri çek - Pathfinder 1e için kritik
2. **Öncelik 2**: Adım bazlı karakter oluşturma arayüzünü tamamla
3. **Öncelik 3**: Karakter kaydetme/yükleme özelliklerini ekle
4. **Öncelik 4**: PDF export özelliğini ekle






## Mevcut Durum

### Tamamlananlar ✅
- **Irklar**: 83 ırk çekildi (77 aonprd + 7 d20pfsrd)
- **Sınıflar**: 73 sınıf çekildi (55 aonprd + 22 d20pfsrd)
- **Feat'ler**: 421 feat çekildi (d20pfsrd'den)
- **GUI Sayfası**: PathfinderPage class'ı oluşturuldu
- **MainWindow Entegrasyonu**: Pathfinder 1e sekmesi eklendi

### Eksikler / TODO ⚠️

#### 1. Büyüler (Spells) - ÖNEMLİ
- **Durum**: Hiç çekilemedi (0 büyü)
- **Sorun**: 
  - Archives of Nethys: Spells.aspx sayfasında direkt SpellsDisplay linkleri yok
  - d20pfsrd: `/spells/` URL'si 404 veriyor
- **Çözüm Önerileri**:
  1. Archives of Nethys için kategori sayfalarını detaylı incele
  2. d20pfsrd için doğru spell URL yapısını bul (/magic/spells/ gibi alternatifler)
  3. JavaScript ile yüklenen içerik varsa Selenium kullan
  4. Manuel ekleme seçeneği sun (kullanıcı büyüleri JSON'dan ekleyebilir)

#### 2. Karakter Oluşturma Arayüzü
- **Durum**: Basit dialog var, adım bazlı sistem henüz yok
- **Gerekenler**:
  - DndPage'e benzer adım bazlı wizard sistemi
  - Irk seçimi
  - Yetenek puanları dağıtımı (point-buy)
  - Sınıf becerileri seçimi
  - Feat seçimi
  - Büyü seçimi (büyüler çekildikten sonra)
  - Ekipman seçimi
  - Kişilik özellikleri

#### 3. Karakter Kaydetme/Yükleme
- **Durum**: Henüz geliştirilmedi
- **Gerekenler**:
  - JSON formatında kaydetme
  - Karakter listesi görüntüleme
  - Karakter yükleme

#### 4. PDF Export
- **Durum**: Henüz geliştirilmedi
- **Gerekenler**:
  - Pathfinder 1e karakter sheet formatı
  - PDF export fonksiyonu

## Büyü Çekimi için Detaylı Plan

### Archives of Nethys
```
Spells.aspx ana sayfası -> Kategori/Level/Class sayfaları bul
Her kategori sayfasından -> SpellsDisplay.aspx?ItemName=... linklerini çek
Detay sayfasından -> Büyü bilgilerini parse et
```

### d20pfsrd
```
Doğru spell URL yapısını bul (muhtemelen /magic/spells/ veya benzeri)
Spell listesi sayfasından -> Spell detay linklerini bul
Detay sayfasından -> Büyü bilgilerini parse et
```

## Sonraki Adımlar

1. **Öncelik 1**: Büyüleri çek - Pathfinder 1e için kritik
2. **Öncelik 2**: Adım bazlı karakter oluşturma arayüzünü tamamla
3. **Öncelik 3**: Karakter kaydetme/yükleme özelliklerini ekle
4. **Öncelik 4**: PDF export özelliğini ekle




## Mevcut Durum

### Tamamlananlar ✅
- **Irklar**: 83 ırk çekildi (77 aonprd + 7 d20pfsrd)
- **Sınıflar**: 73 sınıf çekildi (55 aonprd + 22 d20pfsrd)
- **Feat'ler**: 421 feat çekildi (d20pfsrd'den)
- **GUI Sayfası**: PathfinderPage class'ı oluşturuldu
- **MainWindow Entegrasyonu**: Pathfinder 1e sekmesi eklendi

### Eksikler / TODO ⚠️

#### 1. Büyüler (Spells) - ÖNEMLİ
- **Durum**: Hiç çekilemedi (0 büyü)
- **Sorun**: 
  - Archives of Nethys: Spells.aspx sayfasında direkt SpellsDisplay linkleri yok
  - d20pfsrd: `/spells/` URL'si 404 veriyor
- **Çözüm Önerileri**:
  1. Archives of Nethys için kategori sayfalarını detaylı incele
  2. d20pfsrd için doğru spell URL yapısını bul (/magic/spells/ gibi alternatifler)
  3. JavaScript ile yüklenen içerik varsa Selenium kullan
  4. Manuel ekleme seçeneği sun (kullanıcı büyüleri JSON'dan ekleyebilir)

#### 2. Karakter Oluşturma Arayüzü
- **Durum**: Basit dialog var, adım bazlı sistem henüz yok
- **Gerekenler**:
  - DndPage'e benzer adım bazlı wizard sistemi
  - Irk seçimi
  - Yetenek puanları dağıtımı (point-buy)
  - Sınıf becerileri seçimi
  - Feat seçimi
  - Büyü seçimi (büyüler çekildikten sonra)
  - Ekipman seçimi
  - Kişilik özellikleri

#### 3. Karakter Kaydetme/Yükleme
- **Durum**: Henüz geliştirilmedi
- **Gerekenler**:
  - JSON formatında kaydetme
  - Karakter listesi görüntüleme
  - Karakter yükleme

#### 4. PDF Export
- **Durum**: Henüz geliştirilmedi
- **Gerekenler**:
  - Pathfinder 1e karakter sheet formatı
  - PDF export fonksiyonu

## Büyü Çekimi için Detaylı Plan

### Archives of Nethys
```
Spells.aspx ana sayfası -> Kategori/Level/Class sayfaları bul
Her kategori sayfasından -> SpellsDisplay.aspx?ItemName=... linklerini çek
Detay sayfasından -> Büyü bilgilerini parse et
```

### d20pfsrd
```
Doğru spell URL yapısını bul (muhtemelen /magic/spells/ veya benzeri)
Spell listesi sayfasından -> Spell detay linklerini bul
Detay sayfasından -> Büyü bilgilerini parse et
```

## Sonraki Adımlar

1. **Öncelik 1**: Büyüleri çek - Pathfinder 1e için kritik
2. **Öncelik 2**: Adım bazlı karakter oluşturma arayüzünü tamamla
3. **Öncelik 3**: Karakter kaydetme/yükleme özelliklerini ekle
4. **Öncelik 4**: PDF export özelliğini ekle









