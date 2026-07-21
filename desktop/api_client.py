"""
Diyargezen Desktop API Client
==============================
Masaüstü (PySide6 / CLI) uygulamasının FastAPI web backend'i ile
senkronize (JWT Auth + Cloud Sync) iletişim kurmasını sağlar.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests

logger = logging.getLogger(__name__)

DEFAULT_API_URL = "http://127.0.0.1:8000/api"


class ApiClient:
    """FastAPI Web Sunucusuyla iletişim kuran istemci sınıfı."""

    def __init__(self, base_url: str = DEFAULT_API_URL):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.username: Optional[str] = None

    def set_token(self, token: str, username: str = ""):
        self.token = token
        self.username = username

    def is_authenticated(self) -> bool:
        return bool(self.token)

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def register(self, username: str, password: str) -> Dict[str, Any]:
        """Yeni kullanıcı kaydı oluşturur."""
        url = f"{self.base_url}/auth/register"
        resp = requests.post(url, json={"username": username, "password": password}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "access_token" in data:
            self.set_token(data["access_token"], username)
        return data

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Kullanıcı girişi yapar ve JWT token alır."""
        url = f"{self.base_url}/auth/token"
        resp = requests.post(url, data={"username": username, "password": password}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "access_token" in data:
            self.set_token(data["access_token"], username)
        return data

    def list_characters(self, system: Optional[str] = None) -> List[Dict[str, Any]]:
        """Sunucudaki kayıtlı karakterleri çeker."""
        url = f"{self.base_url}/characters"
        params = {"system": system} if system else {}
        resp = requests.get(url, headers=self._headers(), params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_character(self, character_id: int) -> Dict[str, Any]:
        """ID'ye göre karakter detayını çeker."""
        url = f"{self.base_url}/characters/{character_id}"
        resp = requests.get(url, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def save_character(self, character_data: Dict[str, Any], character_id: Optional[int] = None) -> Dict[str, Any]:
        """Karakteri sunucuda yeni oluşturur veya günceller."""
        name = character_data.get("name", "İsimsiz Kahraman")
        system = character_data.get("system", "pathfinder1e")

        payload = {
            "system": system,
            "name": name,
            "data": character_data
        }

        if character_id:
            url = f"{self.base_url}/characters/{character_id}"
            resp = requests.put(url, json=payload, headers=self._headers(), timeout=10)
        else:
            url = f"{self.base_url}/characters"
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=10)

        resp.raise_for_status()
        return resp.json()

    def delete_character(self, character_id: int) -> bool:
        """Karakteri sunucudan siler."""
        url = f"{self.base_url}/characters/{character_id}"
        resp = requests.delete(url, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return True

    def recalculate(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stat değişikliklerini canlı hesaplamak için backend'e gönderir."""
        url = f"{self.base_url}/characters/recalculate"
        resp = requests.post(url, json={"data": character_data}, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def export_pdf(self, character_id: int, save_path: Path) -> bool:
        """Karakterin PDF belgesini indirir."""
        url = f"{self.base_url}/characters/{character_id}/pdf"
        resp = requests.get(url, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(resp.content)
        return True


# Global singleton instance for desktop application
api_client = ApiClient()
