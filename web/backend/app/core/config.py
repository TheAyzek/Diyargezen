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
import shutil

DB_PATH = WORKSPACE_ROOT / "data" / "characters.db"
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

        import sqlite3
        try:
            from db.entity_store import init_game_schema
            init_game_schema(DB_PATH)
        except Exception as schema_exc:
            print(f"⚠️ Could not pre-initialize game schema: {schema_exc}")

        def get_entity_count(target_p: Path) -> int:
            if not target_p.exists():
                return 0
            try:
                with sqlite3.connect(str(target_p), timeout=5) as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM entities")
                    return cur.fetchone()[0]
            except Exception:
                return 0

        target_count = get_entity_count(DB_PATH)
        bundled_count = get_entity_count(bundled_db)

        if target_count < 10000 or (bundled_count > 0 and target_count < (bundled_count - 500)):
            print(f"📦 Pre-populating database (Target entities: {target_count}, Bundled entities: {bundled_count})...")
            copied = False
            # Attempt 1: Direct file copy if target has fewer entities
            try:
                if DB_PATH.exists():
                    try: os.chmod(DB_PATH, stat.S_IWRITE | stat.S_IREAD)
                    except Exception: pass
                shutil.copyfile(bundled_db, DB_PATH)
                try: os.chmod(DB_PATH, stat.S_IWRITE | stat.S_IREAD)
                except Exception: pass
                print(f"✅ Bundled database copied directly to LocalAppData: {DB_PATH}")
                copied = True
            except Exception as copy_exc:
                print(f"⚠️ Direct file copy failed ({copy_exc}). Falling back to SQLite ATTACH merge...")

            # Attempt 2: SQLite ATTACH database merge if direct file copy failed or file was in use
            if not copied:
                try:
                    from db.entity_store import init_game_schema
                    init_game_schema(DB_PATH)
                    with sqlite3.connect(str(DB_PATH), timeout=30) as conn:
                        conn.execute(f"ATTACH DATABASE '{bundled_db}' AS bundled_src")
                        conn.execute("""
                        INSERT OR REPLACE INTO entities (isim, sistem, kategori, aciklama, sistem_verisi)
                        SELECT isim, sistem, kategori, aciklama, sistem_verisi FROM bundled_src.entities
                        """)
                        conn.execute("DETACH DATABASE bundled_src")
                        conn.commit()
                    print(f"✅ SQLite ATTACH merge completed successfully. Entities in DB_PATH: {get_entity_count(DB_PATH)}")
                except Exception as attach_exc:
                    print(f"❌ Error during SQLite ATTACH merge: {attach_exc}")

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
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("DIYARGEZEN_JWT_EXPIRE_MINUTES", "1440"))

# System code translation
SYSTEM_MAPPING = {
    "pf1e": "pathfinder1e",
    "pathfinder1e": "pathfinder1e",
}
