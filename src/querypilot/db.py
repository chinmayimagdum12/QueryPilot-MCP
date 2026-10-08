import time

import psycopg
from psycopg.rows import dict_row

from .config import settings


def _connect() -> psycopg.Connection:
    """Establish a connection to PostgreSQL with read-only and strict timeout settings."""
    return psycopg.connect(
        settings.database_url,
        row_factory=dict_row,
        connect_timeout=5,
        options=(
            f"-c statement_timeout={settings.query_timeout_ms} "
            "-c default_transaction_read_only=on "
            "-c idle_in_transaction_session_timeout=10000 "
            "-c lock_timeout=2000"
        ),
    )


def fetch(query, params=None, max_rows: int | None = None) -> dict:
    """Run one query in a read-only transaction. Cap rows. Never returns more than hard_max_rows."""
    limit = max(1, min(max_rows or settings.default_max_rows, settings.hard_max_rows))
    start = time.perf_counter()
    with _connect() as conn:
        conn.read_only = True
        with conn.cursor() as cur:
            cur.execute(query, params)  # params=None means no % parsing of user SQL
            rows = cur.fetchmany(limit + 1)
            cols = [d.name for d in cur.description] if cur.description else []
    return {
        "columns": cols,
        "rows": rows[:limit],
        "row_count": min(len(rows), limit),
        "truncated": len(rows) > limit,
        "elapsed_ms": round((time.perf_counter() - start) * 1000, 1),
    }
