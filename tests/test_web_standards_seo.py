import re
import pytest
from pathlib import Path

def test_index_html_seo_and_metadata_compliance():
    """Verify index.html has canonical tags, Open Graph, Twitter Cards, and JSON-LD structured data."""
    html_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "index.html"
    assert html_path.exists()
    content = html_path.read_text(encoding="utf-8")

    # 1. Lang attribute
    assert '<html lang="tr">' in content or '<html lang="tr-TR">' in content

    # 2. Canonical URL
    assert '<link rel="canonical"' in content

    # 3. Open Graph meta tags
    assert 'property="og:title"' in content
    assert 'property="og:description"' in content
    assert 'property="og:image"' in content
    assert 'property="og:url"' in content

    # 4. Twitter Cards
    assert 'name="twitter:card"' in content
    assert 'name="twitter:title"' in content

    # 5. Schema.org JSON-LD Structured Data
    assert 'application/ld+json' in content
    assert 'WebApplication' in content or 'SoftwareApplication' in content

    # 6. Fallback <noscript> content
    assert '<noscript>' in content


def test_vite_config_production_optimization():
    """Verify vite.config.js disables sourcemaps and defines manualChunks code-splitting."""
    config_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "vite.config.js"
    assert config_path.exists()
    content = config_path.read_text(encoding="utf-8")

    assert "sourcemap: false" in content
    assert "manualChunks" in content
    assert "pdf-lib" in content or "pdf" in content


def test_public_meta_files_exist():
    """Verify llms.txt, robots.txt, and sitemap.xml exist in public directory."""
    pub_dir = Path(__file__).resolve().parent.parent / "web" / "frontend" / "public"
    assert (pub_dir / "llms.txt").exists()
    assert (pub_dir / "robots.txt").exists()
    assert (pub_dir / "sitemap.xml").exists()
