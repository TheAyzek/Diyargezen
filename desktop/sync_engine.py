"""
Diyargezen Desktop Background Synchronization Engine

Architecture & Threading Model:
-------------------------------
Implements an asynchronous, non-blocking background synchronization engine using PySide6 (`QThread` & `QObject`).
The thread operates independently of the main PySide6 GUI thread to ensure zero UI freezes during network operations.

Threading Architecture:
1. `BackgroundSyncThread`: Periodically executes an asynchronous loop (default 15-second interval).
2. `SyncWorker`: Executes local SQLite query for `is_dirty=True` records, invokes REST API `POST /api/sync`,
   and applies atomic local updates upon successful cloud handshake.
3. Network Failure Fallback: Catches network disconnects gracefully, maintaining dirty state flags in local SQLite
   until internet connectivity is restored.
"""

from __future__ import annotations

import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtCore import QThread, Signal, QObject

from desktop.api_client import api_client, ApiClient
from desktop import local_db

logger = logging.getLogger(__name__)


class SyncWorker(QObject):
    """
    Masaüstü istemcisinde arka planda çevrimdışı senkronizasyon mantığını yürüten iş parçacığı bileşeni.
    
    PySide6 Signal/Slot mimarisini kullanarak ana kullanıcı arayüzü (UI) iş parçacığını
    bloklamadan (non-blocking) ağ isteklerini ve yerel veritabanı güncellemelerini yönetir.
    
    Signals:
        sync_finished (Signal[int, str]): Senkronize edilen kayıt sayısı ve durum mesajı.
        sync_failed (Signal[str]): Ağ hatası veya yetkilendirme başarısızlık mesajı.
    """

    sync_finished = Signal(int, str)  # (synced_count, status_message)
    sync_failed = Signal(str)

    def __init__(self, db_path: Path):
        super().__init__()
        self.db_path = db_path
        self._last_sync_timestamp: Optional[str] = local_db.get_sync_checkpoint(db_path)

    def perform_sync(self) -> None:
        """
        Çevrimdışı öncelikli senkronizasyon adımını tetikler.
        
        Adımlar:
        1. Oturum durumunu denetler; geçerli JWT token varsa `api_client` yetkilendirilir.
        2. Yerel veritabanından `is_dirty=1` bayrağı taşıyan PF1e karakterlerini sorgular.
        3. Kalıcı işlem kuyruğunu `POST /api/sync/v2` uç noktasına gönderir.
        4. İşlem onaylarını, revizyonları ve çakışmaları atomik olarak saklar.
        """
        session = local_db.get_sync_session(self.db_path)
        if not session:
            return

        try:
            # Never share a mutable login token with the UI while a request runs.
            client = ApiClient(base_url=api_client.base_url)
            client.set_token(session[1], session[0])
            from desktop import sync_v2_store
            operations = sync_v2_store.prepare_operations(self.db_path, session)
            data = client.sync_v2(operations)
            sync_v2_store.apply_response(self.db_path, operations, data, session)
            conflicts = sync_v2_store.list_conflicts(self.db_path)
            pending = local_db.get_dirty_characters(self.db_path, expected_session=session)
            accepted = sum(item['status'] == 'accepted' for item in data['results'])
            message = f"{accepted} işlem onaylandı; {len(pending)} bekleyen kayıt, {len(conflicts)} çakışma"
            self.sync_finished.emit(accepted, message)

        except Exception as exc:
            logger.debug("Senkronizasyon pas geçildi (Çevrimdışı mod): %s", exc)
            self.sync_failed.emit("Senkronizasyon tamamlanamadı; yerel kayıtlar korundu.")


class BackgroundSyncThread(QThread):
    """
    Belirli periyotlarla (varsayılan 15 sn) otomatik senkronizasyon yürüten PySide6 QThread bileşeni.
    
    Uygulama yaşam döngüsü boyunca arka planda çalışarak ağ bağlantısı sağlandığında
    kullanıcı müdahalesi gerektirmeden verileri eşzamanlar.
    """

    sync_completed = Signal(int, str)
    status_changed = Signal(str)

    def __init__(self, db_path: Path, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.db_path = db_path
        self._running = True
        self._interval = 15

    def run(self) -> None:
        """İş parçacığının ana çalıştırma döngüsü."""
        logger.info("Masaüstü Arka Plan Senkronizasyon Motoru başlatıldı.")
        worker = SyncWorker(self.db_path)
        worker.sync_finished.connect(self.sync_completed.emit)
        worker.sync_failed.connect(self.status_changed.emit)

        while self._running:
            try:
                worker.perform_sync()
            except Exception as exc:
                logger.debug("Sync döngüsü hatası: %s", exc)

            # 15 saniye bekle (güvenli durdurma kontrolü ile)
            for _ in range(self._interval * 2):
                if not self._running:
                    break
                time.sleep(0.5)

    def stop(self) -> None:
        """İş parçacığını güvenli bir şekilde sonlandırır."""
        self._running = False
        self.wait()
