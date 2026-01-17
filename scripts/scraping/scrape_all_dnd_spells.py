#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tüm D&D 5e spell'lerini çek ve dnd_data.json'a ekle"""

import sys
from pathlib import Path
import json

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

print("=" * 70)
print("TÜM D&D 5E SPELL'LERİ ÇEKİLİYOR")
print("=" * 70)
print()

# Argparse ile limit ve force parametreleri
import argparse
parser = argparse.ArgumentParser(description='D&D 5e spell\'leri çek')
parser.add_argument('--max', type=int, help='Maksimum spell sayısı (test için)')
parser.add_argument('--force', action='store_true', help='Cache\'i yeniden oluştur')
args = parser.parse_args()

# Scraper oluştur
scraper = Dnd5eSrdScraper(rate_limit=1.5)  # 1.5 saniye bekleme

# Spell'leri çek
spells = scraper.scrape_all_spells(max_spells=args.max, force_refresh=args.force)

print("\n" + "=" * 70)
print("SPELL'LER ÇEKİLDİ - ŞİMDİ DND_DATA.JSON'A EKLENİYOR")
print("=" * 70)

# Mevcut dnd_data.json'ı yükle
dnd_data_file = Path("data/dnd_data.json")
with open(dnd_data_file, 'r', encoding='utf-8') as f:
    dnd_data = json.load(f)

# Spell'leri ekle (veya güncelle)
if 'spells' not in dnd_data:
    dnd_data['spells'] = {}

# Yeni spell'leri ekle veya güncelle
added_count = 0
updated_count = 0

for spell_name, spell_data in spells.items():
    if spell_name in dnd_data['spells']:
        # Mevcut spell'i güncelle (5esrd.com verisi öncelikli)
        dnd_data['spells'][spell_name].update(spell_data)
        updated_count += 1
    else:
        # Yeni spell ekle
        dnd_data['spells'][spell_name] = spell_data
        added_count += 1

print(f"\n✅ {added_count} yeni spell eklendi")
print(f"🔄 {updated_count} spell güncellendi")
print(f"📊 Toplam spell sayısı: {len(dnd_data['spells'])}")

# Kaydet
print(f"\n💾 {dnd_data_file} dosyasına kaydediliyor...")
with open(dnd_data_file, 'w', encoding='utf-8') as f:
    json.dump(dnd_data, f, ensure_ascii=False, indent=2)

print(f"✅ Tamamlandı! {dnd_data_file} güncellendi.")

# Özet
print("\n" + "=" * 70)
print("ÖZET")
print("=" * 70)
print(f"  Toplam çekilen: {len(spells)}")
print(f"  DND data'ya eklenen: {added_count + updated_count}")
print(f"  Toplam spell (dnd_data.json): {len(dnd_data['spells'])}")
print()

# İstatistikler
levels = {}
schools = {}
for spell_name, spell in spells.items():
    level = spell.get('level')
    school = spell.get('school')
    if level is not None:
        levels[level] = levels.get(level, 0) + 1
    if school:
        schools[school] = schools.get(school, 0) + 1

print("Level Dağılımı:")
for level in sorted(levels.keys()):
    print(f"  Level {level}: {levels[level]} spell")

print("\nSchool Dağılımı:")
for school in sorted(schools.keys()):
    print(f"  {school}: {schools[school]} spell")


