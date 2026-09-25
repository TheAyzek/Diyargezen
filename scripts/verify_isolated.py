"""Run the full Python suite in a disposable workspace, never on user data.

Usage: python scripts/verify_isolated.py [pytest arguments...]
The copy is retained for inspection; its absolute path is printed. It contains
a SQLite backup, not a raw copy of an open/WAL database.
"""
from pathlib import Path
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile


def main():
    source = Path(__file__).resolve().parents[1]
    target = Path(tempfile.mkdtemp(prefix='diyargezen-verification-'))
    ignore = shutil.ignore_patterns('__pycache__', '.pytest_cache', 'node_modules', '*.db-wal', '*.db-shm',
                                    'characters.db', 'backups', '.git', '.venv')
    folders = ['core', 'rules', 'creators', 'etl', 'db', 'models', 'parsers', 'utils', 'scraper', 'scraping',
               'desktop', 'tests', 'tools', 'templates', 'assets', 'data', 'web/backend', 'web/frontend/src',
               'web/frontend/public', 'web/frontend/dist']
    for name in folders:
        if (source / name).exists():
            shutil.copytree(source / name, target / name, ignore=ignore, dirs_exist_ok=True)
    for pattern in ('*.py', '*.toml', '*.ini', '*.txt'):
        for file in source.glob(pattern):
            shutil.copy2(file, target / file.name)
    for file in (source / 'web/frontend').iterdir():
        if file.is_file():
            shutil.copy2(file, target / 'web/frontend' / file.name)
    db = source / 'data' / 'characters.db'
    if db.exists():
        with sqlite3.connect(db.as_uri() + '?mode=ro', uri=True) as original, sqlite3.connect(target / 'data' / 'characters.db') as copied:
            original.backup(copied)
    print('ISOLATED_WORKSPACE=' + str(target), flush=True)
    env = {**os.environ, 'PYTHONPATH': str(target), 'DIYARGEZEN_DB_PATH': str(target / 'data' / 'characters.db')}
    # Each test run owns an entirely new temp root (no cross-sandbox ACL reuse).
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests', 'web/backend/tests',
                             '--import-mode=importlib', '-p', 'no:cacheprovider',
                             '--basetemp', str(target / 'pytest-temp'), *sys.argv[1:]], cwd=target, env=env)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
