# PowerShell script - Tüm batch'leri bitene kadar çalıştır
$start = 100  # Son çekilen batch'ten devam (50, 100, ...)
$batchSize = 50
$maxConsecutiveErrors = 3
$errorCount = 0
$batchCount = 0

Write-Host "========================================"
Write-Host "OTOMATIK BATCH SCRAPING BASLIYOR"
Write-Host "========================================"
Write-Host "Batch size: $batchSize"
Write-Host "Start from: $start"
Write-Host ""

while ($true) {
    $batchCount++
    Write-Host "[$batchCount] Batch starting from index $start..." -ForegroundColor Cyan
    
    $output = python scripts/scrape_dnd_spells_batch.py --batch-size $batchSize --start-from $start --max-batches 1 2>&1
    
    # Çıktıyı göster
    Write-Host $output
    
    # Başarılı mı kontrol et
    if ($LASTEXITCODE -eq 0 -and $output -match "Batch tamamlandı") {
        $errorCount = 0  # Başarılı, error count'u sıfırla
        
        # Sonraki başlangıç indeksini bul
        $start += $batchSize
        
        # "Sonraki batch için" satırını kontrol et
        if ($output -match "yeni spell.*çekilecek|Toplam.*spell") {
            # Hala çekilecek spell var
            Write-Host "`n✅ Batch $batchCount tamamlandı. Devam ediliyor...`n" -ForegroundColor Green
            Start-Sleep -Seconds 2  # Kısa bir bekleme
        } else {
            # Tüm spell'ler çekildi
            Write-Host "`n🎉 TÜM BATCH'LER TAMAMLANDI!`n" -ForegroundColor Green
            break
        }
    } else {
        $errorCount++
        Write-Host "`n⚠️ Hata oluştu (Error count: $errorCount/$maxConsecutiveErrors)" -ForegroundColor Yellow
        
        if ($errorCount -ge $maxConsecutiveErrors) {
            Write-Host "❌ Çok fazla hata, durduruluyor." -ForegroundColor Red
            Write-Host "Son başarılı indeks: $start" -ForegroundColor Yellow
            break
        }
        
        # Hata durumunda biraz bekle ve tekrar dene
        Write-Host "5 saniye beklenip tekrar deneniyor..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
    
    # Güvenlik kontrolü - çok fazla batch olmamalı
    if ($batchCount -gt 200) {
        Write-Host "`n⚠️ 200 batch limit'ine ulaşıldı. Durduruluyor." -ForegroundColor Yellow
        Write-Host "Son başarılı indeks: $start" -ForegroundColor Yellow
        break
    }
}

Write-Host "`n========================================"
Write-Host "SCRAPING TAMAMLANDI"
Write-Host "========================================"
Write-Host "Toplam batch: $batchCount"
Write-Host "Son indeks: $start"
Write-Host ""


