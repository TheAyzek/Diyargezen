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

DB_PATH = WORKSPACE_ROOT / "data" / "characters.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

if getattr(sys, 'frozen', False):
    bundled_db = MEIPASS_DIR / "data" / "characters.db"
    if not bundled_db.exists():
        bundled_db = EXEC_DIR / "data" / "characters.db"

    if bundled_db.exists() and (not DB_PATH.exists() or DB_PATH.stat().st_size < 1000000):
        import shutil
        try:
            shutil.copy2(bundled_db, DB_PATH)
        except Exception as exc:
            print(f"Error copying pre-populated database to LocalAppData: {exc}")

# These values must be supplied by the deployment environment.  The fallback is
# deliberately only suitable for local development, so an accidental production
# deployment is visible in logs/tests rather than silently sharing a key.
JWT_SECRET_KEY = os.getenv("DIYARGEZEN_JWT_SECRET", "development-only-change-me-please-set-a-real-secret")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("DIYARGEZEN_JWT_EXPIRE_MINUTES", "1440"))

# System code translation
SYSTEM_MAPPING = {
    "pf1e": "pathfinder1e",
    "pathfinder1e": "pathfinder1e",
}
