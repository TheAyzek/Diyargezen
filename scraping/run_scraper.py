#!/usr/bin/env python3
"""
Diyargezer Scraping Pipeline — Master Controller
==================================================
Tum TTRPG spider'larini tek merkezden yonetir.

Kullanim:
    python -m scraping.run_scraper                          # Tum sistemler
    python -m scraping.run_scraper -s pathfinder1e dnd5e    # Secili sistemler
    python -m scraping.run_scraper -s mm3e --only powers    # Tek bolum
    python -m scraping.run_scraper -p                       # Paralel calistir
    python -m scraping.run_scraper --dry-run                # Baglanti testi
    python -m scraping.run_scraper --list                   # Spider listesi

Ozellikler:
    - ThreadPoolExecutor ile concurrent spider calistirma
    - Rate-limit korumali (spider basina farkli delay)
    - Pydantic validasyon hatalari loglanir, program cokmez
    - Non-destructive merge (mevcut data/ dosyalari korunur)
    - Estetik ilerleme loglama
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Type

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scraping.base_scraper import BaseScraper
from scraping.spiders.pf1e_d20pfsrd_spider import PF1eD20pfsrdSpider

logger = logging.getLogger("scraping")

# ======================================================================
# Spider Registry
# ======================================================================

SPIDER_REGISTRY: Dict[str, Type[BaseScraper]] = {
    "pathfinder1e": PF1eD20pfsrdSpider,
}

SYSTEM_LABELS: Dict[str, str] = {
    "pathfinder1e": "Pathfinder 1e",
}


# ======================================================================
# Pipeline Runner
# ======================================================================

class PipelineRunner:
    """Tum spider'lari yoneten master pipeline sinifi."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        parallel: bool = False,
        max_workers: int = 3,
    ) -> None:
        self._output_dir = output_dir or BASE_DIR / "data"
        self._parallel = parallel
        self._max_workers = max_workers
        self._results: Dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Ana Calistirma
    # ------------------------------------------------------------------

    def run(
        self,
        systems: Optional[List[str]] = None,
        only_section: Optional[str] = None,
    ) -> Dict[str, dict]:
        """
        Belirtilen sistemlerin spider'larini calistir.

        Args:
            systems: Sistem key'leri. None ise tumu.
            only_section: Sadece belirli bolum (races, classes, spells, feats).
        """
        targets = systems or list(SPIDER_REGISTRY.keys())
        self._results = {}

        unknown = set(targets) - set(SPIDER_REGISTRY.keys())
        if unknown:
            logger.error("Bilinmeyen sistem(ler): %s", unknown)
            logger.info("Kayitli: %s", list(SPIDER_REGISTRY.keys()))
            return {}

        self._print_banner(targets, only_section)
        start = time.monotonic()

        if self._parallel and len(targets) > 1:
            self._run_parallel(targets, only_section)
        else:
            self._run_sequential(targets, only_section)

        elapsed = time.monotonic() - start
        self._print_summary(elapsed)
        return self._results

    # ------------------------------------------------------------------
    # Sequential / Parallel
    # ------------------------------------------------------------------

    def _run_sequential(self, targets: List[str], only: Optional[str]) -> None:
        total = len(targets)
        for i, sys_key in enumerate(targets):
            label = SYSTEM_LABELS.get(sys_key, sys_key)
            logger.info("")
            logger.info("[%d/%d] %s baslatiliyor...", i + 1, total, label)
            self._run_single_spider(sys_key, only)

    def _run_parallel(self, targets: List[str], only: Optional[str]) -> None:
        logger.info("Paralel mod: %d worker", self._max_workers)
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = {
                executor.submit(self._run_single_spider, sys_key, only): sys_key
                for sys_key in targets
            }
            for future in as_completed(futures):
                sys_key = futures[future]
                label = SYSTEM_LABELS.get(sys_key, sys_key)
                try:
                    future.result()
                    logger.info("[%s] Tamamlandi.", label)
                except Exception as exc:
                    logger.error("[%s] HATA: %s", label, exc)
                    self._results[sys_key] = {"requests": 0, "errors": 1, "output": "FAILED"}

    def _run_single_spider(self, sys_key: str, only: Optional[str]) -> None:
        """Tek bir spider'i calistir (try-except zirhli)."""
        spider_cls = SPIDER_REGISTRY[sys_key]
        label = SYSTEM_LABELS.get(sys_key, sys_key)

        try:
            with spider_cls(output_dir=self._output_dir) as spider:
                if only:
                    method_name = f"scrape_{only}"
                    method = getattr(spider, method_name, None)

                    if method is None:
                        private_name = f"_scrape_{only}"
                        method = getattr(spider, private_name, None)

                    if method is None:
                        logger.error("[%s] '%s' bolumu bulunamadi", label, only)
                        return

                    logger.info("[%s] Sadece '%s' cekiliyor...", label, only)
                    result = method()
                    from scraping.models import SystemDataBundle
                    bundle = SystemDataBundle(system=sys_key, **{only: result})
                    path = spider.merge_and_save(bundle, spider.OUTPUT_FILE)
                else:
                    path = spider.scrape_and_save()

                stats = spider.stats()
                self._results[sys_key] = {**stats, "output": str(path)}

        except Exception as exc:
            logger.error("[%s] Spider hatasi: %s", label, exc, exc_info=True)
            self._results[sys_key] = {"requests": 0, "errors": 1, "output": "FAILED"}

    # ------------------------------------------------------------------
    # Baglanti Testi
    # ------------------------------------------------------------------

    def dry_run(self, systems: Optional[List[str]] = None) -> Dict[str, bool]:
        """Hedef sitelere baglanti testi yap."""
        targets = systems or list(SPIDER_REGISTRY.keys())
        connectivity: Dict[str, bool] = {}

        logger.info("Baglanti testi baslatiliyor...")
        logger.info("")

        for sys_key in targets:
            spider_cls = SPIDER_REGISTRY[sys_key]
            label = SYSTEM_LABELS.get(sys_key, sys_key)
            try:
                with spider_cls(output_dir=self._output_dir) as spider:
                    logger.info("[%s] %s", label, spider.BASE_URL)
                    soup = spider.fetch(spider.BASE_URL)
                    ok = soup is not None
                    connectivity[sys_key] = ok
                    logger.info("  -> %s", "OK" if ok else "BASARISIZ")
            except Exception as exc:
                logger.error("[%s] Hata: %s", label, exc)
                connectivity[sys_key] = False

        logger.info("")
        total = len(connectivity)
        ok_count = sum(1 for v in connectivity.values() if v)
        logger.info("Sonuc: %d/%d basarili", ok_count, total)
        return connectivity

    # ------------------------------------------------------------------
    # Estetik Cikti
    # ------------------------------------------------------------------

    def _print_banner(self, targets: List[str], only: Optional[str]) -> None:
        labels = [SYSTEM_LABELS.get(t, t) for t in targets]

        logger.info("")
        logger.info("+--------------------------------------------+")
        logger.info("|   Diyargezer Scraping Pipeline  v2.0       |")
        logger.info("+--------------------------------------------+")
        logger.info("| Hedefler : %-30s |", ", ".join(labels))
        if only:
            logger.info("| Bolum    : %-30s |", only)
        logger.info("| Mod      : %-30s |", "PARALEL" if self._parallel else "SIRAYLA")
        logger.info("| Cikti    : %-30s |", str(self._output_dir))
        logger.info("+--------------------------------------------+")
        logger.info("")

    def _print_summary(self, elapsed: float) -> None:
        logger.info("")
        logger.info("=" * 55)
        logger.info("  PIPELINE TAMAMLANDI  (%.1f saniye)", elapsed)
        logger.info("=" * 55)

        total_req = 0
        total_err = 0
        for sys_key, info in self._results.items():
            label = SYSTEM_LABELS.get(sys_key, sys_key)
            req = info.get("requests", 0)
            err = info.get("errors", 0)
            out = info.get("output", "?")
            total_req += req
            total_err += err

            status = "OK" if err == 0 else f"{err} HATA"
            logger.info(
                "  %-15s %4d istek  [%s]  -> %s",
                label, req, status, Path(out).name if out != "FAILED" else "BASARISIZ",
            )

        logger.info("-" * 55)
        logger.info(
            "  TOPLAM         %4d istek  %d hata", total_req, total_err,
        )
        logger.info("=" * 55)


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diyargezer Scraping Pipeline -- SRD veri cekme araci",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ornekler:
  python -m scraping.run_scraper                     # Tum sistemler
  python -m scraping.run_scraper -s dnd5e mm3e       # Secili sistemler
  python -m scraping.run_scraper -s mm3e --only powers
  python -m scraping.run_scraper -p                  # Paralel
  python -m scraping.run_scraper --dry-run           # Baglanti testi
""",
    )
    parser.add_argument(
        "--system", "-s", nargs="+",
        choices=list(SPIDER_REGISTRY.keys()),
        help="Calistirilacak sistem(ler)",
    )
    parser.add_argument(
        "--only",
        choices=["races", "classes", "spells", "feats", "powers", "advantages",
                 "skills", "disciplines", "archetypes"],
        help="Sadece belirli bir veri bolumu",
    )
    parser.add_argument("--parallel", "-p", action="store_true", help="Paralel calistir")
    parser.add_argument("--list", "-l", action="store_true", help="Kayitli spider'lari listele")
    parser.add_argument("--dry-run", action="store_true", help="Sadece baglanti testi")
    parser.add_argument("--output-dir", "-o", type=Path, default=None, help="Cikti dizini")
    parser.add_argument("--verbose", "-v", action="store_true", help="Detayli log")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if args.list:
        print("\nDiyargezer Scraping Pipeline -- Kayitli Spider'lar")
        print("-" * 55)
        for key, cls in SPIDER_REGISTRY.items():
            label = SYSTEM_LABELS.get(key, key)
            print(f"  {label:17s}  {cls.__name__:25s}  {cls.BASE_URL}")
        print(f"\nToplam: {len(SPIDER_REGISTRY)} spider")
        print()
        return

    runner = PipelineRunner(
        output_dir=args.output_dir,
        parallel=args.parallel,
    )

    if args.dry_run:
        results = runner.dry_run(args.system)
        all_ok = all(results.values())
        sys.exit(0 if all_ok else 1)

    runner.run(systems=args.system, only_section=args.only)


if __name__ == "__main__":
    main()
