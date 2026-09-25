import os
from pathlib import Path
import subprocess
import sys


def test_production_rejects_default_secret_and_wildcard_cors(tmp_path):
    config = Path(__file__).resolve().parents[1] / 'web/backend/app/core/config.py'
    env = {**os.environ, 'DIYARGEZEN_ENV': 'production', 'DIYARGEZEN_DB_PATH': str(tmp_path / 'safe.db')}
    env.pop('DIYARGEZEN_JWT_SECRET', None)
    result = subprocess.run([sys.executable, str(config)], env=env, capture_output=True, text=True)
    assert result.returncode != 0 and 'requires a unique' in result.stderr
    env['DIYARGEZEN_JWT_SECRET'] = 'test-only-random-looking-production-key-123456'
    env['DIYARGEZEN_CORS_ORIGINS'] = '*'
    result = subprocess.run([sys.executable, str(config)], env=env, capture_output=True, text=True)
    assert result.returncode != 0 and 'wildcard' in result.stderr
    env['DIYARGEZEN_CORS_ORIGINS'] = 'https://example.test'
    result = subprocess.run([sys.executable, str(config)], env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
