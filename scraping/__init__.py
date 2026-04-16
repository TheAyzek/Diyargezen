"""
Diyargezer Scraping Pipeline
=============================
SRD sitelerinden TTRPG kural verisi çeken modüler OOP pipeline.

Mimari:
  models.py        → Pydantic doğrulama modelleri
  base_scraper.py  → ABC: retry, rate-limit, sanitize, JSON kaydetme
  spiders/         → Site-spesifik scraper implementasyonları
  run_scraper.py   → Pipeline yöneticisi (CLI)
"""
