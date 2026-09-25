import os
import sys
from pathlib import Path

# Resolve workspace root (Diyargezenweb)
CONFIG_FILE = Path(__file__).resolve()
if getattr(sys, 'frozen', False):
    MEIPASS_DIR = Path(getattr(sys, '_MEIPASS', ''))
    EXEC_DIR = Path(sys.executable).parent
    if str(MEIPASS_DIR) not in sys.path:
        sys.path.insert(0, str(MEIPASS_DIR))
    
    # In frozen desktop app mode, store user database and runtime files in %LOCALAPPDATA%/Diyargezen/ (always writable by user)
    local_appdata = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    WORKSPACE_ROOT = local_appdata / "Diyargezen"
else:
    WORKSPACE_ROOT = CONFIG_FILE.parents[4]  # .../Diyargezenweb

# Add workspace root to sys.path to allow importing existing modules (rules, db, utils, models)
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import stat

DB_PATH = Path(os.getenv('DIYARGEZEN_DB_PATH', str(WORKSPACE_ROOT / 'data' / 'characters.db'))).resolve()
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _ensure_database_populated():
    if getattr(sys, 'frozen', False):
        possible_bundled_paths = [
            MEIPASS_DIR / "data" / "characters.db",
            MEIPASS_DIR / "_internal" / "data" / "characters.db",
            EXEC_DIR / "data" / "characters.db",
            EXEC_DIR / "_internal" / "data" / "characters.db",
        ]
        bundled_db = None
        for p in possible_bundled_paths:
            if p.exists() and p.stat().st_size > 100000:
                bundled_db = p
                break

        if not bundled_db:
            print("⚠️ Bundled pre-populated database not found in MEIPASS or EXEC_DIR.")
            return

        try:
            from db.bundled_catalog import import_missing_catalog
            added = import_missing_catalog(DB_PATH, bundled_db)
            print(f"Bundled PF1e catalog: {added} missing records added; user data preserved.")
        except Exception as exc:
            # Failure must never fall back to overwriting the user's database.
            print(f"Bundled catalog import skipped; user database retained: {exc}")

_ensure_database_populated()

if DB_PATH.exists():
    try:
        os.chmod(DB_PATH, stat.S_IWRITE | stat.S_IREAD)
    except Exception:
        pass

# These values must be supplied by the deployment environment.  The fallback is
# deliberately only suitable for local development, so an accidental production
# deployment is visible in logs/tests rather than silently sharing a key.
JWT_SECRET_KEY = os.getenv("DIYARGEZEN_JWT_SECRET", "development-only-change-me-please-set-a-real-secret")
ENVIRONMENT = os.getenv('DIYARGEZEN_ENV', 'development').lower()
if ENVIRONMENT == 'production' and (len(JWT_SECRET_KEY) < 32 or JWT_SECRET_KEY.startswith('development-only')):
    raise RuntimeError('Production requires a unique DIYARGEZEN_JWT_SECRET of at least 32 characters.')
CORS_ORIGINS = [origin.strip() for origin in os.getenv(
    'DIYARGEZEN_CORS_ORIGINS', 'http://127.0.0.1:5173,http://localhost:5173'
).split(',') if origin.strip()]
if ENVIRONMENT == 'production' and '*' in CORS_ORIGINS:
    raise RuntimeError('Production CORS origins must be explicit, not a wildcard.')
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("DIYARGEZEN_JWT_EXPIRE_MINUTES", "1440"))

# System code translation
SYSTEM_MAPPING = {
    "pf1e": "pathfinder1e",
    "pathfinder1e": "pathfinder1e",
}
