# core/db.py
import sqlite3
from pathlib import Path
from contextlib import contextmanager

DEFAULT_DB_PATH = Path(".") / "inquisitor_net.db"

def _resolve_db_path(db_path: str | None) -> Path:
    return Path(db_path) if db_path else DEFAULT_DB_PATH

@contextmanager
def get_conn(db_path: str | None = None):
    """Context manager yielding a SQLite connection with row factory."""
    path = _resolve_db_path(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db(db_path: str | None = None):
    path = _resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with get_conn(db_path) as conn:
        # Phase-1/2 tables assumed created via migrations; keep helper for tests/tools.
        conn.execute('PRAGMA journal_mode=WAL')
        return True
