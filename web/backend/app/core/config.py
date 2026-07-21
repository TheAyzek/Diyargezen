import sys
from pathlib import Path

# Resolve workspace root
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_ROOT = BACKEND_DIR.parent.parent

# Add workspace root to sys.path to allow importing existing modules (rules, db, utils, models)
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

DB_PATH = WORKSPACE_ROOT / "data" / "characters.db"

# System code translation
SYSTEM_MAPPING = {
    "pf1e": "pathfinder1e",
    "dnd5e": "dnd5e",
    "mnm": "mm3e",
    "mnm3e": "mm3e"
}
