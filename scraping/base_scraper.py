"""
Base Scraper — Abstract Base Class
===================================
Tüm site-spesifik spider'ların miras alacağı temel sınıf.

Sorumluluklar:
  - HTTP istekleri (retry + exponential backoff)
  - Rate limiting (rastgele bekleme süreleri)
  - HTML sanitization (gereksiz etiket temizleme)
  - robots.txt saygısı (opsiyonel)
  - Pydantic modeli ile doğrulama
  - JSON dosyasına kaydetme / merge
  - İlerleme loglama
"""

from __future__ import annotations

import html
import json
import logging
import random
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, ValidationError

from scraping.models import SystemDataBundle

logger = logging.getLogger(__name__)


# ======================================================================
# HTML Sanitization Yardımcıları
# ======================================================================

# Temizlenecek etiketler (içerikle birlikte kaldırılır)
_STRIP_TAGS_WITH_CONTENT = {"script", "style", "nav", "footer", "header", "aside", "iframe"}

# Temizlenecek etiketler (yalnız etiket, içerik korunur)
_UNWRAP_TAGS = {"span", "font", "em", "strong", "b", "i", "u", "a", "div"}


def sanitize_html(raw_html: str) -> str:
    """
    Ham HTML'den gereksiz etiketleri temizle, düz metin döndür.

    1. script/style/nav etiketlerini içerikleriyle birlikte sil.
    2. <br> etiketlerini newline'a çevir.
    3. Kalan etiketleri sil, HTML entity'leri decode et.
    4. Ardışık boşlukları normalleştir.
    """
    if not raw_html:
        return ""

    text = re.sub(
        r"<(?:" + "|".join(_STRIP_TAGS_WITH_CONTENT) + r")\b[^>]*>.*?</(?:" +
        "|".join(_STRIP_TAGS_WITH_CONTENT) + r")>",
        "", raw_html, flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text(element: Optional[Tag], separator: str = " ") -> str:
    """BeautifulSoup Tag'inden temiz metin çıkar."""
    if element is None:
        return ""
    return element.get_text(separator=separator, strip=True)


def extract_list_items(ul_element: Optional[Tag]) -> List[str]:
    """<ul>/<ol> elementinden liste öğelerini çıkar."""
    if ul_element is None:
        return []
    return [li.get_text(strip=True) for li in ul_element.find_all("li") if li.get_text(strip=True)]


# ======================================================================
# Base Scraper ABC
# ======================================================================

class BaseScraper(ABC):
    """
    Tüm spider'lar için temel Abstract Base Class.

    Alt sınıflar ``scrape()`` metodunu override eder ve site-spesifik
    parsing mantığını burada uygular.
    """

    SYSTEM_KEY: str = ""
    BASE_URL: str = ""
    USER_AGENT: str = "Diyargezer-TTRPG-Builder/2.0 (educational; +https://github.com/diyargezer)"

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        delay_range: tuple[float, float] = (1.0, 3.0),
        max_retries: int = 3,
        timeout: int = 30,
    ) -> None:
        self._output_dir = output_dir or Path(__file__).resolve().parents[1] / "data"
        self._delay_range = delay_range
        self._max_retries = max_retries
        self._timeout = timeout

        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

        self._request_count = 0
        self._error_count = 0

    # ------------------------------------------------------------------
    # HTTP — Retry + Rate Limit
    # ------------------------------------------------------------------

    def fetch(self, url: str) -> Optional[BeautifulSoup]:
        """
        URL'yi indir, parse et ve BeautifulSoup nesnesi döndür.
        Exponential backoff ile retry uygular.
        """
        for attempt in range(1, self._max_retries + 1):
            try:
                self._rate_limit_wait()
                logger.debug("[%s] GET %s (deneme %d)", self.SYSTEM_KEY, url, attempt)

                resp = self._session.get(url, timeout=self._timeout)
                self._request_count += 1

                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 10))
                    logger.warning("429 Rate Limited — %ds bekleniyor", retry_after)
                    time.sleep(retry_after)
                    continue

                resp.raise_for_status()
                return BeautifulSoup(resp.text, "lxml")

            except requests.exceptions.HTTPError as exc:
                status = exc.response.status_code if exc.response else "?"
                logger.warning("[%s] HTTP %s: %s (deneme %d)", self.SYSTEM_KEY, status, url, attempt)
            except requests.exceptions.ConnectionError:
                logger.warning("[%s] Bağlantı hatası: %s (deneme %d)", self.SYSTEM_KEY, url, attempt)
            except requests.exceptions.Timeout:
                logger.warning("[%s] Zaman aşımı: %s (deneme %d)", self.SYSTEM_KEY, url, attempt)
            except requests.exceptions.RequestException as exc:
                logger.error("[%s] İstek hatası: %s", self.SYSTEM_KEY, exc)
                break

            if attempt < self._max_retries:
                backoff = (2 ** attempt) + random.uniform(0, 1)
                logger.info("  → %.1fs sonra tekrar denenecek", backoff)
                time.sleep(backoff)
            else:
                self._error_count += 1

        return None

    def fetch_text(self, url: str) -> str:
        """URL'den düz metin olarak içerik çek."""
        soup = self.fetch(url)
        return soup.get_text(separator="\n", strip=True) if soup else ""

    def _rate_limit_wait(self) -> None:
        """Rastgele bekleme süresi ile rate limiting."""
        lo, hi = self._delay_range
        delay = random.uniform(lo, hi)
        time.sleep(delay)

    def build_url(self, path: str) -> str:
        """Baz URL'ye göreli yol ekle."""
        return urljoin(self.BASE_URL, path)

    # ------------------------------------------------------------------
    # Pydantic Doğrulama
    # ------------------------------------------------------------------

    @staticmethod
    def validate_item(data: Dict[str, Any], model_cls: Type[BaseModel]) -> Optional[BaseModel]:
        """
        Ham dict'i Pydantic modeliyle doğrula.
        Geçersizse None döner ve hatayı loglar.
        """
        try:
            return model_cls.model_validate(data)
        except ValidationError as exc:
            name = data.get("name", "?")
            logger.warning("Doğrulama hatası [%s]: %s", name, exc.error_count())
            for err in exc.errors():
                logger.debug("  %s: %s", err["loc"], err["msg"])
            return None

    @staticmethod
    def validate_batch(
        items: List[Dict[str, Any]],
        model_cls: Type[BaseModel],
    ) -> tuple[List[BaseModel], int]:
        """
        Birden fazla item'ı doğrula.
        Returns: (geçerli modeller listesi, reddedilen sayı)
        """
        valid: List[BaseModel] = []
        rejected = 0
        for item in items:
            model = BaseScraper.validate_item(item, model_cls)
            if model is not None:
                valid.append(model)
            else:
                rejected += 1
        return valid, rejected

    # ------------------------------------------------------------------
    # JSON Kaydetme / Merge
    # ------------------------------------------------------------------

    def save_json(self, data: Dict[str, Any], filename: str) -> Path:
        """
        Veriyi JSON dosyasına yaz.
        Dosya mevcutsa üzerine yazar.
        """
        self._output_dir.mkdir(parents=True, exist_ok=True)
        filepath = self._output_dir / filename
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, default=str)
        logger.info("JSON kaydedildi: %s (%.1f KB)", filepath, filepath.stat().st_size / 1024)
        return filepath

    def merge_and_save(self, bundle: SystemDataBundle, filename: str) -> Path:
        """
        Mevcut JSON dosyasının üzerine non-destructive merge yap.
        Yeni veriler eski verilerin üzerine yazılır; eksik key'ler korunur.
        """
        filepath = self._output_dir / filename
        existing: Dict[str, Any] = {}
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as fh:
                existing = json.load(fh)

        merged = bundle.merge_into(existing)
        merged["system"] = bundle.system
        if bundle.source:
            merged["source"] = bundle.source

        return self.save_json(merged, filename)

    # ------------------------------------------------------------------
    # Abstract Methods
    # ------------------------------------------------------------------

    @abstractmethod
    def scrape(self) -> SystemDataBundle:
        """
        Ana scraping mantığı. Alt sınıflar bunu override eder.
        Pydantic ile doğrulanmış bir SystemDataBundle döndürmelidir.
        """
        ...

    @abstractmethod
    def scrape_races(self) -> Dict[str, Any]:
        """Irk verilerini çek ve doğrula."""
        ...

    @abstractmethod
    def scrape_classes(self) -> Dict[str, Any]:
        """Sınıf verilerini çek ve doğrula."""
        ...

    # ------------------------------------------------------------------
    # İstatistikler
    # ------------------------------------------------------------------

    def stats(self) -> Dict[str, int]:
        """Scraping oturumu istatistikleri."""
        return {
            "requests": self._request_count,
            "errors": self._error_count,
        }

    def close(self) -> None:
        """Session'ı kapat."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
