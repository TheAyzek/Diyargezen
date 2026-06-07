#!/usr/bin/env python3
"""Manuel ETL çalıştırıcı: python run_etl.py [--force]"""

import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from etl.pipeline import run_etl


def main() -> None:
    parser = argparse.ArgumentParser(description="Diyargezen ETL — JSON → SQLite")
    parser.add_argument("--force", action="store_true", help="Cache'i yoksay, yeniden yükle")
    parser.add_argument(
        "--systems",
        nargs="+",
        default=["dnd5e", "pathfinder1e", "mm3e"],
        help="Yüklenecek sistemler",
    )
    args = parser.parse_args()
    totals = run_etl(systems=args.systems, force=args.force)
    print("ETL tamamlandı:")
    for sys_name, count in totals.items():
        print(f"  {sys_name}: {count} entity")


if __name__ == "__main__":
    main()
