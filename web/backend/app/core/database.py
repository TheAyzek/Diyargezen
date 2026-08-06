import sqlite3
from contextlib import contextmanager
from typing import Iterator
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DB_PATH

# Create SQLAlchemy Engine
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Iterator:
    """FastAPI dependency to yield database sessions."""
    db = SessionLocal()
    try:
        # Enable foreign keys for the session
        db.execute(text("PRAGMA foreign_keys=ON"))
        yield db
    finally:
        db.close()

@contextmanager
def get_db_connection() -> Iterator[sqlite3.Connection]:
    """Provide a thread-safe connection to the SQLite characters database (backward-compatibility)."""
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def check_db_exists() -> bool:
    """Verify that the database file exists and contains the expected tables.
    Decompresses pre-populated seed_characters.db.gz on cloud deployment if DB is missing or empty.
    """
    import gzip
    import shutil
    import logging
    logger = logging.getLogger(__name__)

    seed_gz = DB_PATH.parent / "seed_characters.db.gz"

    need_unpack = False
    if not DB_PATH.exists() or DB_PATH.stat().st_size < 100000:
        need_unpack = True
    else:
        try:
            with sqlite3.connect(str(DB_PATH), timeout=5) as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM entities")
                count = cur.fetchone()[0]
                if count < 1000:
                    need_unpack = True
        except Exception:
            need_unpack = True

    if need_unpack and seed_gz.exists():
        logger.info("📦 Unpacking pre-populated seed database (%s) -> (%s)...", seed_gz, DB_PATH)
        try:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            with gzip.open(seed_gz, 'rb') as f_in, open(DB_PATH, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            logger.info("✅ Pre-populated seed database unpacked successfully (%d bytes).", DB_PATH.stat().st_size)
        except Exception as e:
            logger.error("❌ Failed to unpack seed database: %s", e)

    if not DB_PATH.exists():
        return False
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('entities', 'characters')")
            tables = [r[0] for r in cursor.fetchall()]
            return len(tables) == 2
    except Exception:
        return False

def initialize_orm_schemas() -> None:
    """Create new ORM tables and alter existing tables to match ORM schemas."""
    import logging
    # Import models locally to avoid circular imports during startup
    from app.models import User, Character, LevelProgression
    
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logging.getLogger(__name__).error(f"Error creating ORM tables: {e}")
        
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(characters)")
            columns = [col[1] for col in cursor.fetchall()]
            if "user_id" not in columns:
                cursor.execute("ALTER TABLE characters ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
            if "server_id" not in columns:
                cursor.execute("ALTER TABLE characters ADD COLUMN server_id TEXT")
            if "is_deleted" not in columns:
                cursor.execute("ALTER TABLE characters ADD COLUMN is_deleted INTEGER DEFAULT 0")
            conn.commit()
    except Exception as e:
        logging.getLogger(__name__).error(f"Error altering characters table schema: {e}")


