#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D&D 5e Feats - Arka Plan Çekimi"""

import sys
import codecs
from pathlib import Path
import datetime

# UTF-8 encoding fix for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Proje root dizinine ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper
import json

def main():
    """Tüm feat'leri arka planda çek"""
    log_file = project_root / "data/logs/feats_scraping_log.txt"
    
    # Log dosyasına yaz
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write("=" * 70 + "\n")
        log.write("D&D 5E FEATS SCRAPING - ARKA PLAN\n")
        log.write("=" * 70 + "\n")
        log.write(f"Başlangıç: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Toplam feat sayısı: ~1368\n")
        log.write(f"Tahmini süre: ~34 dakika (1.5 saniye/feat)\n")
        log.write("=" * 70 + "\n\n")
        log.flush()
        
        print("=" * 70)
        print("D&D 5E FEATS SCRAPING - ARKA PLAN")
        print("=" * 70)
        print(f"📝 Log dosyası: {log_file}")
        print(f"⏰ Başlangıç: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Toplam feat: ~1368")
        print(f"⏱️  Tahmini süre: ~34 dakika")
        print("=" * 70)
        print("\n💡 İpucu: Bu pencereyi kapatabilirsiniz, çekim arka planda devam edecek.")
        print(f"   İlerlemeyi görmek için: {log_file} dosyasını kontrol edin.\n")
        
        scraper = Dnd5eSrdScraper(rate_limit=1.5)
        
        try:
            # Tüm feat'leri çek
            log.write("🔍 Feat'ler çekiliyor...\n")
            log.flush()
            
            feats = scraper.scrape_all_feats(force_refresh=False)
            
            log.write(f"\n✅ Toplam {len(feats)} feat çekildi!\n")
            log.write(f"Bitiş: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.flush()
            
            # dnd_data.json'a entegre et
            data_file = project_root / "data" / "dnd_data.json"
            if data_file.exists():
                log.write(f"\n📦 dnd_data.json'a entegre ediliyor...\n")
                log.flush()
                
                with open(data_file, 'r', encoding='utf-8') as f:
                    dnd_data = json.load(f)
                
                # Feat'leri ekle
                if 'feats' not in dnd_data:
                    dnd_data['feats'] = {}
                
                existing_count = len(dnd_data['feats'])
                dnd_data['feats'].update(feats)
                new_count = len(dnd_data['feats'])
                
                # Kaydet
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(dnd_data, f, ensure_ascii=False, indent=2)
                
                log.write(f"✅ {new_count - existing_count} yeni feat eklendi, toplam {new_count} feat dnd_data.json'da!\n")
                log.flush()
                
                print(f"\n✅ {new_count} feat başarıyla çekildi ve dnd_data.json'a eklendi!")
            else:
                log.write(f"⚠️  dnd_data.json bulunamadı: {data_file}\n")
                log.flush()
            
            log.write("\n" + "=" * 70 + "\n")
            log.write("✅ FEATS SCRAPING TAMAMLANDI\n")
            log.write("=" * 70 + "\n")
            log.flush()
            
        except KeyboardInterrupt:
            log.write("\n⚠️  Kullanıcı tarafından durduruldu.\n")
            log.write(f"İlerleme cache'de kaydedildi, kaldığı yerden devam edebilirsiniz.\n")
            log.flush()
            print("\n⚠️  Durduruldu. İlerleme cache'de kaydedildi.")
        except Exception as e:
            log.write(f"\n❌ Hata: {str(e)}\n")
            log.write(f"İlerleme cache'de kaydedildi, kaldığı yerden devam edebilirsiniz.\n")
            log.flush()
            import traceback
            log.write(traceback.format_exc())
            log.flush()
            print(f"\n❌ Hata oluştu: {e}")
            print(f"İlerleme cache'de kaydedildi, log dosyasına bakın: {log_file}")

if __name__ == "__main__":
    main()


