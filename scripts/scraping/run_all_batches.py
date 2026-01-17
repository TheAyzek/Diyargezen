#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tüm batch'leri bitene kadar otomatik çalıştır"""

import sys
from pathlib import Path
import json
import subprocess
import time

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

def get_current_progress():
    """Mevcut ilerlemeyi al"""
    cache_file = Path("data/cache/spells_cache.json")
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        return len(cache_data.get('spells', {}))
    return 0

def get_total_spells():
    """Toplam spell sayısını al"""
    scraper = Dnd5eSrdScraper(rate_limit=0.5)  # Hızlı kontrol
    spell_links = scraper.scrape_all_spell_links()
    return len(spell_links)

def main():
    batch_size = 50
    start_from = 100  # Son başarılı batch'ten devam
    max_consecutive_errors = 3
    error_count = 0
    batch_count = 0
    
    print("=" * 70)
    print("OTOMATIK BATCH SCRAPING BASLIYOR")
    print("=" * 70)
    print(f"Batch size: {batch_size}")
    print(f"Start from: {start_from}")
    print()
    
    # Mevcut durumu kontrol et
    current_spells = get_current_progress()
    print(f"📦 Mevcut spell sayısı: {current_spells}")
    
    # Toplam spell sayısını al
    try:
        total_spells = get_total_spells()
        remaining = total_spells - current_spells
        print(f"📊 Toplam spell: {total_spells}")
        print(f"⏳ Kalan: {remaining}")
        
        if remaining <= 0:
            print("\n🎉 TÜM SPELL'LER ZATEN ÇEKİLMİŞ!")
            return
        
        estimated_batches = (remaining + batch_size - 1) // batch_size
        print(f"📦 Tahmini kalan batch: {estimated_batches}")
        print()
    except Exception as e:
        print(f"⚠️ Toplam kontrolü yapılamadı: {e}")
        print("Devam ediliyor...")
        print()
    
    # Start from'u mevcut spell sayısına göre ayarla
    start_from = (current_spells // batch_size) * batch_size
    
    while True:
        batch_count += 1
        print(f"[{batch_count}] Batch başlatılıyor (indeks: {start_from})...")
        print("-" * 70)
        
        try:
            # Batch script'ini çalıştır
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/scrape_dnd_spells_batch.py",
                    "--batch-size", str(batch_size),
                    "--start-from", str(start_from),
                    "--max-batches", "1"
                ],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=300  # 5 dakika timeout
            )
            
            # Çıktıyı göster
            if result.stdout:
                print(result.stdout)
            if result.stderr and result.returncode != 0:
                print(f"⚠️ Hata: {result.stderr}")
            
            # Başarı kontrolü
            if result.returncode == 0 and "Batch tamamlandı" in result.stdout:
                error_count = 0  # Başarılı, error count'u sıfırla
                
                # Yeni progress kontrol et
                new_spells = get_current_progress()
                if new_spells > current_spells:
                    # Yeni spell'ler eklendi
                    current_spells = new_spells
                    print(f"\n✅ Batch {batch_count} tamamlandı. Toplam: {current_spells} spell")
                    
                    # Sonraki batch için indeksi güncelle
                    start_from += batch_size
                    
                    # Hala çekilecek spell var mı kontrol et
                    try:
                        total = get_total_spells()
                        if current_spells >= total:
                            print("\n🎉 TÜM SPELL'LER ÇEKİLDİ!")
                            break
                        remaining = total - current_spells
                        print(f"⏳ Kalan: {remaining} spell ({remaining // batch_size} batch)")
                    except:
                        pass  # Toplam kontrol hatası önemli değil
                    
                    print()
                    time.sleep(2)  # Kısa bir bekleme
                else:
                    # Yeni spell eklenmedi, muhtemelen bitti
                    print("\n⚠️ Yeni spell eklenmedi. Muhtemelen tüm spell'ler çekildi.")
                    break
            else:
                # Hata oluştu
                error_count += 1
                print(f"\n⚠️ Hata oluştu (Error count: {error_count}/{max_consecutive_errors})")
                
                if error_count >= max_consecutive_errors:
                    print("❌ Çok fazla hata, durduruluyor.")
                    print(f"Son başarılı indeks: {start_from}")
                    break
                
                print("10 saniye beklenip tekrar deneniyor...")
                time.sleep(10)
                
        except subprocess.TimeoutExpired:
            print(f"\n⏱️ Batch timeout (5 dakika aşıldı). Devam ediliyor...")
            error_count += 1
            if error_count >= max_consecutive_errors:
                print("❌ Çok fazla timeout, durduruluyor.")
                break
            time.sleep(5)
            
        except Exception as e:
            print(f"\n❌ Beklenmeyen hata: {e}")
            error_count += 1
            if error_count >= max_consecutive_errors:
                print("❌ Çok fazla hata, durduruluyor.")
                break
            time.sleep(5)
        
        # Güvenlik kontrolü
        if batch_count > 200:
            print("\n⚠️ 200 batch limit'ine ulaşıldı. Durduruluyor.")
            print(f"Son başarılı indeks: {start_from}")
            break
    
    # Final özet
    print("\n" + "=" * 70)
    print("SCRAPING TAMAMLANDI")
    print("=" * 70)
    final_spells = get_current_progress()
    print(f"Toplam batch: {batch_count}")
    print(f"Son indeks: {start_from}")
    print(f"Toplam çekilen spell: {final_spells}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Kullanıcı tarafından durduruldu (Ctrl+C)")
        print("İlerleme kaydedildi, istediğiniz zaman devam edebilirsiniz.")
        sys.exit(0)


