"""
Masaüstü Arka Plan Senkronizasyon Motoru (Background Sync Engine)
================================================================
PySide6 QThread tabanlı servis. Arka planda periodik olarak internet
bağlantısını ve FastAPI sunucusunu kontrol eder; `is_dirty=1` olan
karakterleri sunucuya iletip buluttaki güncellemeleri yerel SQLite'a çeker.
"""

from __future__ import annotations

import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtCore import QThread, Signal, QObject

from desktop.api_client import api_client
from desktop import local_db

logger = logging.getLogger(__name__)


class SyncWorker(QObject):
    """Arka planda senkronizasyon mantığını çalıştıran worker objesi."""

    sync_finished = Signal(int, str)  # (synced_count, status_message)
    sync_failed = Signal(str)

    def __init__(self, db_path: Path):
        super().__init__()
        self.db_path = db_path
        self._last_sync_timestamp: Optional[str] = local_db.get_sync_checkpoint(db_path)

    def perform_sync(self) -> None:
        """Çevrimdışı öncelikli senkronizasyon adımını tetikler."""
        if not api_client.is_authenticated():
            auth_info = local_db.get_local_auth(self.db_path)
            if auth_info:
                api_client.set_token(auth_info[1], auth_info[0])

        if not api_client.is_authenticated():
            return

        try:
            # 1. Yereldeki dirty karakterleri çek
            dirty_records = [
                record for record in local_db.get_dirty_characters(self.db_path)
                if record.system.lower() in {"pf1e", "pathfinder1e"}
            ]
            dirty_payload = [
                {
                    "server_id": r.server_id,
                    "system": r.system,
                    "name": r.name,
                    "data": r.data,
                    "updated_at": r.updated_at,
                    "is_deleted": r.is_deleted,
                    "created_at": getattr(r, "created_at", None)
                }
                for r in dirty_records
            ]

            # 2. api_client üzerinden /api/sync endpoint'ini çağır
            data = api_client.sync_characters(
                dirty_characters=dirty_payload,
                last_sync_timestamp=self._last_sync_timestamp
            )

            synced_at = data.get("synced_at")
            updated_chars = data.get("updated_characters", [])
            deleted_ids = data.get("deleted_server_ids", [])

            # 3. Yerel SQLite veritabanına yanıtı uygula
            local_db.apply_sync_response(self.db_path, updated_chars, deleted_ids)
            self._last_sync_timestamp = synced_at
            if synced_at:
                local_db.set_sync_checkpoint(self.db_path, synced_at)

            count = len(updated_chars) + len(dirty_payload)
            self.sync_finished.emit(count, f"Senkronize edildi ({count} kayıt)")

        except Exception as exc:
            logger.debug("Senkronizasyon pas geçildi (Çevrimdışı mod): %s", exc)
            self.sync_failed.emit("Çevrimdışı mod (Sunucuya ulaşılamadı)")



class BackgroundSyncThread(QThread):
    """Her 15 saniyede bir otomatik senkronizasyon yapan PySide6 Thread."""

    sync_completed = Signal(int, str)
    status_changed = Signal(str)

    def __init__(self, db_path: Path, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.db_path = db_path
        self._running = True
        self._interval = 15

    def run(self) -> None:
        logger.info("Masaüstü Arka Plan Senkronizasyon Motoru başlatıldı.")
        worker = SyncWorker(self.db_path)

        while self._running:
            try:
                worker.perform_sync()
            except Exception as exc:
                logger.debug("Sync döngüsü hatası: %s", exc)

            # 15 saniye bekle
            for _ in range(self._interval * 2):
                if not self._running:
                    break
                time.sleep(0.5)

    def stop(self) -> None:
        self._running = False
        self.wait()
