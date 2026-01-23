#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geliştirilmiş ırk scraper'ı test et"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from utils.pathfinder_scraper import PathfinderScraper
import json

def test_race_scraper():
    print("=" * 60)
    print("Geliştirilmiş Irk Scraper Test")
    print("=" * 60)
    
    # Archives of Nethys'ten Human ırkını test et
    print("\n[1] Archives of Nethys - Human Race")
    print("-" * 60)
    scraper = PathfinderScraper(site="aonprd", delay=2.0)
    
    human_url = "https://aonprd.com/RacesDisplay.aspx?ItemName=Human"
    human_data = scraper._scrape_race_detail(human_url)
    
    if human_data:
        print(f"\nAbility Score Increase: {human_data.get('ability_score_increase', {})}")
        print(f"Ability Score Text: {human_data.get('ability_score_increase_text', '')}")
        print(f"Size: {human_data.get('size', '')}")
        print(f"Speed: {human_data.get('speed', '')} ({human_data.get('speed_special', '')})")
        print(f"Languages (Auto): {human_data.get('languages_automatic', [])}")
        print(f"Languages (Bonus): {human_data.get('languages_bonus', [])}")
        print(f"Vision: {human_data.get('vision', '')} ({human_data.get('vision_range', 0)})")
        print(f"Traits: {human_data.get('traits', [])[:5]}")
        print(f"Favored Class: {human_data.get('favored_classes', [])}")
        print(f"Description: {human_data.get('description', '')[:200]}...")
        
        # JSON olarak kaydet
        with open("human_race_test.json", "w", encoding="utf-8") as f:
            json.dump(human_data, f, ensure_ascii=False, indent=2)
        print("\n[OK] Test verisi kaydedildi: human_race_test.json")
    else:
        print("[HATA] Human race verisi cekilemedi!")
    
    # Elf ırkını da test et (farklı özelliklere sahip)
    print("\n" + "=" * 60)
    print("[2] Archives of Nethys - Elf Race")
    print("-" * 60)
    
    elf_url = "https://aonprd.com/RacesDisplay.aspx?ItemName=Elf"
    elf_data = scraper._scrape_race_detail(elf_url)
    
    if elf_data:
        print(f"\nAbility Score Increase: {elf_data.get('ability_score_increase', {})}")
        print(f"Size: {elf_data.get('size', '')}")
        print(f"Speed: {elf_data.get('speed', '')}")
        print(f"Vision: {elf_data.get('vision', '')} ({elf_data.get('vision_range', 0)})")
        print(f"Traits: {elf_data.get('traits', [])[:5]}")
        print(f"Languages: {elf_data.get('languages', [])[:5]}")
        
        with open("elf_race_test.json", "w", encoding="utf-8") as f:
            json.dump(elf_data, f, ensure_ascii=False, indent=2)
        print("\n[OK] Test verisi kaydedildi: elf_race_test.json")
    else:
        print("[HATA] Elf race verisi cekilemedi!")

if __name__ == "__main__":
    try:
        test_race_scraper()
        print("\n[OK] Test tamamlandi!")
    except Exception as e:
        print(f"[HATA] Hata: {e}")
        import traceback
        traceback.print_exc()


