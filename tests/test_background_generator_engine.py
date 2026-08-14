"""
Unit Tests for PF1e Ultimate Campaign Background & Story Feat Engine
===================================================================
Verifies:
- Background table selections (Homeland, Family, Childhood, Motivation)
- Coherent narrative biography generation
- Story Feats prerequisites, goals, and completion benefits
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.background_generator import (
    generate_random_background,
    compile_background_narrative,
    get_background_tables_catalog
)
from fastapi.testclient import TestClient
from app.main import app


def test_background_generation_and_narrative():
    """Verify random background generation returns complete structured components."""
    bg = generate_random_background(race="Elf", char_class="Ranger", alignment="CG")

    assert bg["race"] == "Elf"
    assert bg["class"] == "Ranger"
    assert "name_tr" in bg["homeland"]
    assert "name_tr" in bg["family"]
    assert "name_tr" in bg["childhood_event"]
    assert "name_tr" in bg["motivation"]
    assert len(bg["recommended_story_feats"]) == 2
    assert "narrative_biography" in bg
    assert len(bg["narrative_biography"]) > 50


def test_compile_background_narrative():
    """Verify compile_background_narrative formats clean string."""
    bg_data = {
        "homeland": {"name_tr": "Kadim Ormanlar"},
        "family": {"name_tr": "Manastır Yetimi", "desc": "Rahiplerin himayesinde eğitildi."},
        "childhood_event": {"name_tr": "Gizemli Yadigar", "desc": "Harabelerde kadim bir tılsım buldu."},
        "motivation": {"name_tr": "Vatan Görevi", "desc": "Topraklarını karanlık tehditlere karşı korumak."}
    }

    text = compile_background_narrative(bg_data)
    assert "Vatanı: Kadim Ormanlar" in text
    assert "Gizemli Yadigar" in text
    assert "Vatan Görevi" in text


def test_story_feats_registry_completion_goals():
    """Verify Paizo Story Feats have goals and completion benefits."""
    catalog = get_background_tables_catalog()
    story_feats = catalog["story_feats"]

    assert "arisen" in story_feats
    assert "champion" in story_feats
    assert "fearless" in story_feats

    champ = story_feats["champion"]
    assert "goal" in champ
    assert "completion_benefit" in champ
    assert "düelloda" in champ["goal"]


def test_background_backend_api():
    """Verify /api/rules/background-catalog, /generate-background and /compile-background."""
    client = TestClient(app)

    # 1. Catalog
    res_cat = client.get("/api/rules/background-catalog")
    assert res_cat.status_code == 200
    data_c = res_cat.json()
    assert len(data_c["homelands"]) >= 8

    # 2. Generate
    res_gen = client.post("/api/rules/generate-background", json={
        "race": "Dwarf",
        "char_class": "Cleric",
        "alignment": "LG"
    })
    assert res_gen.status_code == 200
    data_g = res_gen.json()
    assert "narrative_biography" in data_g

    # 3. Compile
    res_comp = client.post("/api/rules/compile-background", json={
        "background_data": {
            "homeland": {"name_tr": "Yüksek Dağlar"},
            "family": {"name_tr": "Gazi Ailesi", "desc": "Kılıç sesleriyle büyüdü."}
        }
    })
    assert res_comp.status_code == 200
    assert "Yüksek Dağlar" in res_comp.json()["narrative_biography"]
