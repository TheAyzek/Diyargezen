# Pathfinder 1e SRD & Foundry VTT Scraper Modülü

Bu modül, Diyargezen TTRPG platformundaki Pathfinder 1e kural ve eşya veritabanını zenginleştirmek için tasarlanmıştır.

## 📌 Özellikler

1. **Foundry VTT Paket Ayrıştırma**: `data/pf1e-content-main/src/packs/` altındaki 38 compendium paketindeki binlerce Feat, Item, Spell, Trait verisini doğrudan okur.
2. **SRD Silah & Zırh Yedeklemesi**: Foundry paketlerinde eksik olan standart PF1e silahlarını (Longsword, Dagger, Greatsword, Bows vb.) ve zırhlarını (Full Plate, Chainmail, Leather, Shields vb.) otomatik olarak ekler.
3. **SQLite Seed Entegrasyonu**: Verileri `data/characters.db` SQLite veritabanının `entities` tablosuna doğrudan yazar.

## 🚀 Çalıştırma

Sanal ortam aktifken terminalden aşağıdaki komutu çalıştırabilirsiniz:

```bash
python scraper/pf1e_weapons_armor_scraper.py --target all
```

### Parametreler:
- `--target srd`: Sadece standart SRD silah ve zırhlarını ekler.
- `--target foundry`: Sadece Foundry VTT JSON paketlerini ayrıştırır.
- `--target all`: Tüm kaynakları işler ve veritabanını günceller.
