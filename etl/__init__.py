"""ETL pipeline — yerel JSON → SQLite."""

from .pipeline import run_etl, run_etl_if_needed

__all__ = ["run_etl", "run_etl_if_needed"]
