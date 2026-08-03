"""
Desktop Login & Register Dialog (PySide6)
=========================================
Kullanıcının FastAPI backend sunucusuna JWT auth ile giriş yapmasını
veya yeni hesap oluşturmasını sağlar.
"""

from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTabWidget,
)

from desktop.api_client import api_client

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """Masaüstü için bulut senkronizasyonu giriş diyalog penceresi."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Diyargezen — Bulut Girişi")
        self.resize(380, 260)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("Diyargezen Bulut Senkronizasyonu")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #c9a84c;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.tabs = QTabWidget()

        # Tab 1: Login
        login_tab = QWidget()
        login_lay = QVBoxLayout(login_tab)

        self.login_user = QLineEdit()
        self.login_user.setPlaceholderText("Kullanıcı Adı")
        self.login_user.setText("ayzek")

        self.login_pass = QLineEdit()
        self.login_pass.setPlaceholderText("Şifre")
        self.login_pass.setEchoMode(QLineEdit.Password)
        self.login_pass.setText("ayzek1234")

        login_btn = QPushButton("Giriş Yap")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self._handle_login)

        login_lay.addWidget(QLabel("Kullanıcı Adı:"))
        login_lay.addWidget(self.login_user)
        login_lay.addWidget(QLabel("Şifre:"))
        login_lay.addWidget(self.login_pass)
        login_lay.addSpacing(10)
        login_lay.addWidget(login_btn)

        # Tab 2: Register
        reg_tab = QWidget()
        reg_lay = QVBoxLayout(reg_tab)

        self.reg_user = QLineEdit()
        self.reg_user.setPlaceholderText("Kullanıcı Adı")

        self.reg_pass = QLineEdit()
        self.reg_pass.setPlaceholderText("Şifre")
        self.reg_pass.setEchoMode(QLineEdit.Password)

        reg_btn = QPushButton("Yeni Kayıt Oluştur")
        reg_btn.setCursor(Qt.PointingHandCursor)
        reg_btn.clicked.connect(self._handle_register)

        reg_lay.addWidget(QLabel("Kullanıcı Adı:"))
        reg_lay.addWidget(self.reg_user)
        reg_lay.addWidget(QLabel("Şifre:"))
        reg_lay.addWidget(self.reg_pass)
        reg_lay.addSpacing(10)
        reg_lay.addWidget(reg_btn)

        self.tabs.addTab(login_tab, "Giriş Yap")
        self.tabs.addTab(reg_tab, "Kayıt Ol")
        layout.addWidget(self.tabs)

    def _handle_login(self) -> None:
        user = self.login_user.text().strip()
        pwd = self.login_pass.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Hata", "Lütfen kullanıcı adı ve şifre girin.")
            return

        try:
            from desktop.gui.main_window import ensure_local_server_running
            ensure_local_server_running()
            api_client.login(user, pwd)
            QMessageBox.information(self, "Başarılı", f"Hoş geldin {user}! Bulut senkronizasyonu aktif.")
            self.accept()
        except Exception as exc:
            msg = str(exc)
            if "Max retries exceeded" in msg or "Connection refused" in msg or "10061" in msg:
                msg = "Gömülü sunucu henüz başlatılıyor veya port 8000 bağlantısı reddedildi. Lütfen 2 saniye bekleyip tekrar deneyin."
            QMessageBox.critical(self, "Giriş Hatası", f"{msg}")

    def _handle_register(self) -> None:
        user = self.reg_user.text().strip()
        pwd = self.reg_pass.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Hata", "Lütfen kullanıcı adı ve şifre girin.")
            return

        if len(user) < 3 or len(pwd) < 4:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı en az 3, şifre en az 4 karakter olmalıdır.")
            return

        try:
            from desktop.gui.main_window import ensure_local_server_running
            ensure_local_server_running()
            api_client.register(user, pwd)
            QMessageBox.information(self, "Başarılı", f"Hesap oluşturuldu! Hoş geldin {user}.")
            self.accept()
        except Exception as exc:
            msg = str(exc)
            if "Max retries exceeded" in msg or "Connection refused" in msg or "10061" in msg:
                msg = "Gömülü sunucu henüz başlatılıyor veya port 8000 bağlantısı reddedildi. Lütfen 2 saniye bekleyip tekrar deneyin."
            QMessageBox.critical(self, "Kayıt Hatası", f"{msg}")
