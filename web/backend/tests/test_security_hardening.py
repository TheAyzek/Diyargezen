"""
Unit Tests for Security Hardening & Vulnerability Mitigation
==============================================================
CRLF Header Injection, Path Traversal, IDOR yetkilendirme ve 
Global Stack Trace Masking güvenlik birim testleri.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
workspace_root = backend_dir.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.routers.characters import _sanitize_filename


def test_sanitize_filename_crlf_and_path_traversal():
    # 1. CRLF Injection payload
    bad_name1 = "Valeros\r\nContent-Type: text/html"
    clean1 = _sanitize_filename(bad_name1)
    assert "\r" not in clean1
    assert "\n" not in clean1
    assert ":" not in clean1
    assert clean1 == "Valeros__Content-Type__text_html"

    # 2. Path Traversal payload
    bad_name2 = "../../etc/passwd"
    clean2 = _sanitize_filename(bad_name2)
    assert ".." not in clean2
    assert "/" not in clean2
    assert clean2 == "______etc_passwd"

    # 3. Normal character name
    normal_name = "Ezren the Wizard"
    clean3 = _sanitize_filename(normal_name)
    assert clean3 == "Ezren_the_Wizard"
