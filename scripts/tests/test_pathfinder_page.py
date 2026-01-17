#!/usr/bin/env python3
"""PathfinderPage test scripti"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

try:
    from gui.app import PathfinderPage
    print("PathfinderPage import başarılı")
    
    print("\nPathfinderPage oluşturuluyor...")
    page = PathfinderPage()
    print(f"✓ PathfinderPage oluşturuldu!")
    print(f"✓ Adım sayısı: {len(page.steps)}")
    print(f"✓ Data yüklendi: {len(page.data.get('races', {}))} ırk, {len(page.data.get('classes', {}))} sınıf, {len(page.data.get('feats', {}))} feat")
    
    print("\nAdımlar:")
    for i, step in enumerate(page.steps):
        print(f"  {i+1}. {step['name']}: {step['description']}")
    
    print("\n✓ Test başarılı!")
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


