"""Narrow Qt channel: verified identity + fixed SQLite command set, no paths/SQL."""
import hashlib
import json
import secrets

from PySide6.QtCore import QObject, Slot
from desktop.local_db import _connect
from desktop.local_server import allows_navigation
from desktop.web_storage import WebStorage


class BridgeService:
    def __init__(self, path, verify_token):
        self.path = path
        self.verify_token = verify_token
        self.storage = WebStorage(path)
        with _connect(path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS web_verified_sessions (token_hash TEXT PRIMARY KEY, username TEXT NOT NULL)')

    def dispatch(self, session, method, args):
        token = session.get('token', '')
        # Recompute identity fields rather than trusting the browser owner label.
        if session.get('authenticated'):
            digest = hashlib.sha256(token.encode()).hexdigest()
            with _connect(self.path) as db:
                row = db.execute('SELECT username FROM web_verified_sessions WHERE token_hash=?', (digest,)).fetchone()
                username = row[0] if row else self.verify_token(token)
                if not username or username.strip().casefold() == 'yerel gezgin':
                    raise ValueError('Geçerli kişisel oturum gerekli')
                owner = 'account:' + username
                if session.get('owner') != owner:
                    raise ValueError('Oturum sahibi uyuşmuyor')
                if not row:
                    db.execute('INSERT INTO web_verified_sessions VALUES(?,?)', (digest, username))
        else:
            if token or session.get('owner') != 'guest':
                raise ValueError('Geçersiz misafir oturumu')
            owner = 'guest'
        return self.storage.execute(owner, method, args)


def verify_local_token(token):
    from app.core.database import SessionLocal
    from app.services.auth_service import get_current_user
    with SessionLocal() as db:
        return get_current_user(token, db).username


class StorageBridge(QObject):
    def __init__(self, page, server, path):
        super().__init__(page)
        self.page = page
        self.server = server
        self.secret = secrets.token_urlsafe(32)
        self.service = BridgeService(path, verify_local_token)

    @Slot(str, result=str)
    def dispatch(self, envelope):
        try:
            if len(envelope) > 8_000_000:
                raise ValueError('Yerel işlem çok büyük')
            request = json.loads(envelope)
            if not secrets.compare_digest(request.get('secret', ''), self.secret):
                raise ValueError('Köprü erişimi reddedildi')
            if not self.server.is_running() or not allows_navigation(
                self.page.url().toString(), self.server.origin, main_frame=True,
            ) or self.page.url().scheme() != 'http':
                raise ValueError('Güvenilmeyen sayfa')
            result = self.service.dispatch(request['session'], request['method'], request.get('args', {}))
            return json.dumps({'ok': True, 'value': result}, ensure_ascii=False, allow_nan=False)
        except Exception:
            # Never expose SQL paths, JWTs or backend error internals to content.
            return json.dumps({'ok': False, 'error': 'Yerel işlem uygulanamadı. Oturumu veya çakışma durumunu kontrol edin; kayıtlar korunuyor.'})
