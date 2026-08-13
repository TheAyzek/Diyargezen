import pytest
from pathlib import Path

def test_point_buy_cost_matrix():
    """Verify PF1e CRB Table 1-1 Point Buy cost values."""
    costs = {
        7: -4, 8: -2, 9: -1, 10: 0, 11: 1, 12: 2,
        13: 3, 14: 5, 15: 7, 16: 10, 17: 13, 18: 17
    }

    studio_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "src" / "components" / "PointBuyStudio.jsx"
    assert studio_path.exists()
    content = studio_path.read_text(encoding="utf-8")

    for score, cost in costs.items():
        assert f"{score}: {cost}" in content

def test_point_buy_presets_defined():
    """Verify standard PF1e campaign fantasy level presets."""
    studio_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "src" / "components" / "PointBuyStudio.jsx"
    content = studio_path.read_text(encoding="utf-8")

    assert "Low Fantasy" in content
    assert "Standard Fantasy" in content
    assert "High Fantasy" in content
    assert "Epic Fantasy" in content
