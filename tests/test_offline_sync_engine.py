import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web" / "backend"))

import pytest
from datetime import datetime, timezone
from app.routers.sync import parse_iso_timestamp

def test_parse_iso_timestamp_utc_conversion():
    """Test parse_iso_timestamp safely converts ISO strings and timezone variations."""
    ts_z = "2026-08-13T10:00:00Z"
    dt_z = parse_iso_timestamp(ts_z)
    assert dt_z.year == 2026
    assert dt_z.month == 8
    assert dt_z.day == 13
    assert dt_z.tzinfo == timezone.utc

    ts_naive = "2026-08-13T12:00:00"
    dt_naive = parse_iso_timestamp(ts_naive)
    assert dt_naive.tzinfo == timezone.utc

    # Test invalid string fallback
    assert parse_iso_timestamp("invalid-date") == datetime.min.replace(tzinfo=timezone.utc)
    assert parse_iso_timestamp(None) == datetime.min.replace(tzinfo=timezone.utc)

def test_last_write_wins_timestamp_comparison():
    """Test Last-Write-Wins (LWW) timestamp logic."""
    client_ts = "2026-08-13T12:05:00Z"
    server_ts = "2026-08-13T12:00:00Z"

    client_dt = parse_iso_timestamp(client_ts)
    server_dt = parse_iso_timestamp(server_ts)

    # Client is newer -> Should update cloud record
    assert client_dt >= server_dt

    older_client_ts = "2026-08-13T11:55:00Z"
    older_client_dt = parse_iso_timestamp(older_client_ts)

    # Client is older -> Cloud record should be retained
    assert not (older_client_dt >= server_dt)
