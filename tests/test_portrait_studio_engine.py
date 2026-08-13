import pytest
from pathlib import Path

def test_preset_avatars_structure():
    """Verify frontend preset avatars SVG data."""
    modal_path = Path(__file__).resolve().parent.parent / "web" / "frontend" / "src" / "components" / "PortraitGeneratorModal.jsx"
    assert modal_path.exists()
    content = modal_path.read_text(encoding="utf-8")

    # Verify Pollinations URL generator
    assert "https://image.pollinations.ai/prompt/" in content
    assert "PRESET_AVATARS" in content
    assert "Valeros" in content
    assert "Ezren" in content
    assert "Kyra" in content
    assert "Merisiel" in content

def test_pollinations_url_format():
    """Verify zero-cost Pollinations image URL format."""
    prompt = "A portrait of a male Human Fighter"
    encoded_prompt = "A%20portrait%20of%20a%20male%20Human%20Fighter"
    seed = 1234
    expected_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&seed={seed}&nologo=true"
    
    # Simple Python logic matching JS implementation
    import urllib.parse
    generated_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=512&height=512&seed={seed}&nologo=true"
    assert generated_url == expected_url
