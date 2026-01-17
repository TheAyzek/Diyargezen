# D&D 5e Spell Batch Scraping Kılavuzu

## Sorun
4541 spell'i tek seferde çekmek çok uzun sürüyor ve "tool call ended before getting request" hatasına neden oluyor.

## Çözüm
Spell'leri parça parça (batch mode) çekiyoruz. Her batch'te 50-100 spell çekiliyor ve her batch sonunda cache'e kaydediliyor.

---

## Kullanım

### İlk Batch (50 spell)
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --max-batches 1
```

### Sonraki Batch'ler
Her batch sonunda script size sonraki batch için komut veriyor. Örnek:

```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 50
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 100
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 150
# ... ve böyle devam eder
```

### Parametreler

- `--batch-size N`: Her batch'te çekilecek spell sayısı (default: 100, önerilen: 50)
- `--start-from N`: Hangi indeksten başlanacak (devam için)
- `--max-batches N`: Maksimum kaç batch çekilecek (None = tümü)
- `--force`: Cache'i yeniden oluştur (tüm spell'leri yeniden çek)

### Örnekler

**50'şer 50'şer çek (1 batch):**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --max-batches 1
```

**100'er 100'er çek (5 batch):**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 100 --max-batches 5
```

**200. indeksten başla, 50'şer çek:**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 200
```

---

## İlerleme Takibi

Her batch sonunda:
- ✅ Başarılı spell sayısı gösterilir
- 💾 Cache güncellenir (`data/spells_cache.json`)
- 📊 Toplam spell sayısı gösterilir
- 📌 Sonraki batch için komut verilir

Cache dosyası (`data/spells_cache.json`) her batch sonunda güncellenir, bu yüzden yarıda kesilse bile kaldığı yerden devam edebilirsiniz.

---

## Otomatik Devam

Tüm spell'leri otomatik çekmek için bir loop script'i:

```bash
# Windows PowerShell
$start = 0
$batchSize = 50
while ($true) {
    python scripts/scrape_dnd_spells_batch.py --batch-size $batchSize --start-from $start --max-batches 1
    $start += $batchSize
    Start-Sleep -Seconds 5
}
```

```bash
# Linux/Mac Bash
start=0
batch_size=50
while true; do
    python scripts/scrape_dnd_spells_batch.py --batch-size $batch_size --start-from $start --max-batches 1
    start=$((start + batch_size))
    sleep 5
done
```

---

## Tahmini Süre

- Her spell: ~1.5 saniye (rate limiting)
- 50 spell batch: ~75 saniye (~1.25 dakika)
- 4541 spell (toplam): ~113 dakika (~2 saat)

**Önerilen Strateji:**
- Günlük 10-20 batch çek (500-1000 spell)
- Birkaç günde tamamlanır
- Her batch sonunda otomatik kaydedilir

---

## Sorun Giderme

### "Connection timeout" hatası
- Rate limit'i artırın: `rate_limit=2.0` (utils/dnd_5esrd_scraper.py)
- Batch size'ı küçültün: `--batch-size 25`

### "Cache corrupted" hatası
- Cache'i temizleyin: `--force` ile baştan başlayın

### "Spell not found" hatası
- Normal, bazı spell'ler 404 verir, atlanır

---

## Tamamlandığında

Tüm spell'ler çekildikten sonra:
1. `data/spells_cache.json` - Tüm çekilen spell'ler
2. `data/dnd_data.json` - D&D data'ya entegre edilmiş spell'ler

GUI'de artık tüm spell'leri görebilirsiniz! 🎉




## Sorun
4541 spell'i tek seferde çekmek çok uzun sürüyor ve "tool call ended before getting request" hatasına neden oluyor.

## Çözüm
Spell'leri parça parça (batch mode) çekiyoruz. Her batch'te 50-100 spell çekiliyor ve her batch sonunda cache'e kaydediliyor.

---

## Kullanım

### İlk Batch (50 spell)
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --max-batches 1
```

### Sonraki Batch'ler
Her batch sonunda script size sonraki batch için komut veriyor. Örnek:

```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 50
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 100
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 150
# ... ve böyle devam eder
```

### Parametreler

- `--batch-size N`: Her batch'te çekilecek spell sayısı (default: 100, önerilen: 50)
- `--start-from N`: Hangi indeksten başlanacak (devam için)
- `--max-batches N`: Maksimum kaç batch çekilecek (None = tümü)
- `--force`: Cache'i yeniden oluştur (tüm spell'leri yeniden çek)

### Örnekler

**50'şer 50'şer çek (1 batch):**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --max-batches 1
```

**100'er 100'er çek (5 batch):**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 100 --max-batches 5
```

**200. indeksten başla, 50'şer çek:**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 200
```

---

## İlerleme Takibi

Her batch sonunda:
- ✅ Başarılı spell sayısı gösterilir
- 💾 Cache güncellenir (`data/spells_cache.json`)
- 📊 Toplam spell sayısı gösterilir
- 📌 Sonraki batch için komut verilir

Cache dosyası (`data/spells_cache.json`) her batch sonunda güncellenir, bu yüzden yarıda kesilse bile kaldığı yerden devam edebilirsiniz.

---

## Otomatik Devam

Tüm spell'leri otomatik çekmek için bir loop script'i:

```bash
# Windows PowerShell
$start = 0
$batchSize = 50
while ($true) {
    python scripts/scrape_dnd_spells_batch.py --batch-size $batchSize --start-from $start --max-batches 1
    $start += $batchSize
    Start-Sleep -Seconds 5
}
```

```bash
# Linux/Mac Bash
start=0
batch_size=50
while true; do
    python scripts/scrape_dnd_spells_batch.py --batch-size $batch_size --start-from $start --max-batches 1
    start=$((start + batch_size))
    sleep 5
done
```

---

## Tahmini Süre

- Her spell: ~1.5 saniye (rate limiting)
- 50 spell batch: ~75 saniye (~1.25 dakika)
- 4541 spell (toplam): ~113 dakika (~2 saat)

**Önerilen Strateji:**
- Günlük 10-20 batch çek (500-1000 spell)
- Birkaç günde tamamlanır
- Her batch sonunda otomatik kaydedilir

---

## Sorun Giderme

### "Connection timeout" hatası
- Rate limit'i artırın: `rate_limit=2.0` (utils/dnd_5esrd_scraper.py)
- Batch size'ı küçültün: `--batch-size 25`

### "Cache corrupted" hatası
- Cache'i temizleyin: `--force` ile baştan başlayın

### "Spell not found" hatası
- Normal, bazı spell'ler 404 verir, atlanır

---

## Tamamlandığında

Tüm spell'ler çekildikten sonra:
1. `data/spells_cache.json` - Tüm çekilen spell'ler
2. `data/dnd_data.json` - D&D data'ya entegre edilmiş spell'ler

GUI'de artık tüm spell'leri görebilirsiniz! 🎉






## Sorun
4541 spell'i tek seferde çekmek çok uzun sürüyor ve "tool call ended before getting request" hatasına neden oluyor.

## Çözüm
Spell'leri parça parça (batch mode) çekiyoruz. Her batch'te 50-100 spell çekiliyor ve her batch sonunda cache'e kaydediliyor.

---

## Kullanım

### İlk Batch (50 spell)
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --max-batches 1
```

### Sonraki Batch'ler
Her batch sonunda script size sonraki batch için komut veriyor. Örnek:

```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 50
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 100
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 150
# ... ve böyle devam eder
```

### Parametreler

- `--batch-size N`: Her batch'te çekilecek spell sayısı (default: 100, önerilen: 50)
- `--start-from N`: Hangi indeksten başlanacak (devam için)
- `--max-batches N`: Maksimum kaç batch çekilecek (None = tümü)
- `--force`: Cache'i yeniden oluştur (tüm spell'leri yeniden çek)

### Örnekler

**50'şer 50'şer çek (1 batch):**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --max-batches 1
```

**100'er 100'er çek (5 batch):**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 100 --max-batches 5
```

**200. indeksten başla, 50'şer çek:**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 200
```

---

## İlerleme Takibi

Her batch sonunda:
- ✅ Başarılı spell sayısı gösterilir
- 💾 Cache güncellenir (`data/spells_cache.json`)
- 📊 Toplam spell sayısı gösterilir
- 📌 Sonraki batch için komut verilir

Cache dosyası (`data/spells_cache.json`) her batch sonunda güncellenir, bu yüzden yarıda kesilse bile kaldığı yerden devam edebilirsiniz.

---

## Otomatik Devam

Tüm spell'leri otomatik çekmek için bir loop script'i:

```bash
# Windows PowerShell
$start = 0
$batchSize = 50
while ($true) {
    python scripts/scrape_dnd_spells_batch.py --batch-size $batchSize --start-from $start --max-batches 1
    $start += $batchSize
    Start-Sleep -Seconds 5
}
```

```bash
# Linux/Mac Bash
start=0
batch_size=50
while true; do
    python scripts/scrape_dnd_spells_batch.py --batch-size $batch_size --start-from $start --max-batches 1
    start=$((start + batch_size))
    sleep 5
done
```

---

## Tahmini Süre

- Her spell: ~1.5 saniye (rate limiting)
- 50 spell batch: ~75 saniye (~1.25 dakika)
- 4541 spell (toplam): ~113 dakika (~2 saat)

**Önerilen Strateji:**
- Günlük 10-20 batch çek (500-1000 spell)
- Birkaç günde tamamlanır
- Her batch sonunda otomatik kaydedilir

---

## Sorun Giderme

### "Connection timeout" hatası
- Rate limit'i artırın: `rate_limit=2.0` (utils/dnd_5esrd_scraper.py)
- Batch size'ı küçültün: `--batch-size 25`

### "Cache corrupted" hatası
- Cache'i temizleyin: `--force` ile baştan başlayın

### "Spell not found" hatası
- Normal, bazı spell'ler 404 verir, atlanır

---

## Tamamlandığında

Tüm spell'ler çekildikten sonra:
1. `data/spells_cache.json` - Tüm çekilen spell'ler
2. `data/dnd_data.json` - D&D data'ya entegre edilmiş spell'ler

GUI'de artık tüm spell'leri görebilirsiniz! 🎉




## Sorun
4541 spell'i tek seferde çekmek çok uzun sürüyor ve "tool call ended before getting request" hatasına neden oluyor.

## Çözüm
Spell'leri parça parça (batch mode) çekiyoruz. Her batch'te 50-100 spell çekiliyor ve her batch sonunda cache'e kaydediliyor.

---

## Kullanım

### İlk Batch (50 spell)
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --max-batches 1
```

### Sonraki Batch'ler
Her batch sonunda script size sonraki batch için komut veriyor. Örnek:

```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 50
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 100
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 150
# ... ve böyle devam eder
```

### Parametreler

- `--batch-size N`: Her batch'te çekilecek spell sayısı (default: 100, önerilen: 50)
- `--start-from N`: Hangi indeksten başlanacak (devam için)
- `--max-batches N`: Maksimum kaç batch çekilecek (None = tümü)
- `--force`: Cache'i yeniden oluştur (tüm spell'leri yeniden çek)

### Örnekler

**50'şer 50'şer çek (1 batch):**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --max-batches 1
```

**100'er 100'er çek (5 batch):**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 100 --max-batches 5
```

**200. indeksten başla, 50'şer çek:**
```bash
python scripts/scrape_dnd_spells_batch.py --batch-size 50 --start-from 200
```

---

## İlerleme Takibi

Her batch sonunda:
- ✅ Başarılı spell sayısı gösterilir
- 💾 Cache güncellenir (`data/spells_cache.json`)
- 📊 Toplam spell sayısı gösterilir
- 📌 Sonraki batch için komut verilir

Cache dosyası (`data/spells_cache.json`) her batch sonunda güncellenir, bu yüzden yarıda kesilse bile kaldığı yerden devam edebilirsiniz.

---

## Otomatik Devam

Tüm spell'leri otomatik çekmek için bir loop script'i:

```bash
# Windows PowerShell
$start = 0
$batchSize = 50
while ($true) {
    python scripts/scrape_dnd_spells_batch.py --batch-size $batchSize --start-from $start --max-batches 1
    $start += $batchSize
    Start-Sleep -Seconds 5
}
```

```bash
# Linux/Mac Bash
start=0
batch_size=50
while true; do
    python scripts/scrape_dnd_spells_batch.py --batch-size $batch_size --start-from $start --max-batches 1
    start=$((start + batch_size))
    sleep 5
done
```

---

## Tahmini Süre

- Her spell: ~1.5 saniye (rate limiting)
- 50 spell batch: ~75 saniye (~1.25 dakika)
- 4541 spell (toplam): ~113 dakika (~2 saat)

**Önerilen Strateji:**
- Günlük 10-20 batch çek (500-1000 spell)
- Birkaç günde tamamlanır
- Her batch sonunda otomatik kaydedilir

---

## Sorun Giderme

### "Connection timeout" hatası
- Rate limit'i artırın: `rate_limit=2.0` (utils/dnd_5esrd_scraper.py)
- Batch size'ı küçültün: `--batch-size 25`

### "Cache corrupted" hatası
- Cache'i temizleyin: `--force` ile baştan başlayın

### "Spell not found" hatası
- Normal, bazı spell'ler 404 verir, atlanır

---

## Tamamlandığında

Tüm spell'ler çekildikten sonra:
1. `data/spells_cache.json` - Tüm çekilen spell'ler
2. `data/dnd_data.json` - D&D data'ya entegre edilmiş spell'ler

GUI'de artık tüm spell'leri görebilirsiniz! 🎉






