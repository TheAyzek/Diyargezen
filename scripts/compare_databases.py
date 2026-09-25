"""Read-only table checksum comparison; never prints private row contents."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

def snapshot(path):
    with sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True) as db:
        result = {}
        for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
            table = '"' + name.replace('"', '""') + '"'
            columns = [row[1] for row in db.execute('PRAGMA table_info(' + table + ')')]
            # Compare mappings, not column order (migrations may rebuild a table).
            rows = [dict(zip(columns, row)) for row in db.execute('SELECT * FROM ' + table)]
            rows = [{key: row[key] for key in sorted(row)} for row in rows]
            hashes = sorted(hashlib.sha256(json.dumps(row, default=str, ensure_ascii=False).encode()).hexdigest() for row in rows)
            result[name] = (len(rows), hashlib.sha256(''.join(hashes).encode()).hexdigest())
        return result

if __name__ == '__main__':
    before, after = snapshot(sys.argv[1]), snapshot(sys.argv[2])
    for name in sorted(before.keys() | after.keys()):
        print(name, 'UNCHANGED' if before.get(name) == after.get(name) else 'CHANGED',
              'rows', before.get(name, (0,))[0], '->', after.get(name, (0,))[0])
