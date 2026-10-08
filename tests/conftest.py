import os

import psycopg
import pytest


@pytest.fixture(scope="session", autouse=True)
def _env():
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql://querypilot_ro:change_me_local_only@localhost:5432/pagila",
    )


@pytest.fixture(scope="session")
def db_available(_env):
    """Skip integration tests cleanly if PostgreSQL is not reachable."""
    try:
        psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=3).close()
    except (psycopg.Error, OSError):
        pytest.skip("Postgres not available")
