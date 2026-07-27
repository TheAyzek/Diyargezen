import os
import sys
from pathlib import Path

# Resolve workspace root (Diyargezenweb)
CONFIG_FILE = Path(__file__).resolve()
WORKSPACE_ROOT = CONFIG_FILE.parents[4]  # .../Diyargezenweb

# Add workspace root to sys.path to allow importing existing modules (rules, db, utils, models)
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

DB_PATH = WORKSPACE_ROOT / "data" / "characters.db"

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
