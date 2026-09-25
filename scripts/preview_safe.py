"""Loopback preview using a SQLite backup, never the user's live database."""
import os
from pathlib import Path
import sqlite3
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
target = Path(tempfile.mkdtemp(prefix='diyargezen-preview-')) / 'preview.db'
source = root / 'data/characters.db'
with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as original, sqlite3.connect(target) as copied:
    original.backup(copied)
os.environ['DIYARGEZEN_DB_PATH'] = str(target)
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / 'web/backend'))
print('PREVIEW_DB=' + str(target), flush=True)
import uvicorn
uvicorn.run('app.main:app', host='127.0.0.1', port=8011)
