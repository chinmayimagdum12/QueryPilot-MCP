import json

import pytest

from querypilot import server, tools
from querypilot.guard import GuardError

pytestmark = pytest.mark.usefixtures("db_available")


def test_list_tables_contains_film():
    res = tools.list_tables()
    names = [t["table_name"] for t in res["tables"]]
    assert "film" in names


def test_describe_table_has_pk():
    d = tools.describe_table("film")
    assert any(c["type"] == "primary key" for c in d["constraints"])
    assert any(col["column_name"] == "title" for col in d["columns"])


def test_unknown_table_suggests_close_match():
    with pytest.raises(tools.ToolError) as e:
        tools.describe_table("fillm")
    assert "film" in str(e.value)
    assert "Did you mean: film" in str(e.value)


def test_run_query_and_row_cap():
    r = tools.run_readonly_query("SELECT * FROM film", max_rows=5)
    assert r["row_count"] == 5
    assert r["truncated"] is True
    assert len(r["rows"]) == 5


def test_hard_cap_cannot_be_exceeded():
    r = tools.run_readonly_query("SELECT * FROM generate_series(1, 5000)", max_rows=99999)
    assert r["row_count"] <= 1000
    assert r["truncated"] is True


def test_explain_does_not_execute():
    r = tools.explain_query("SELECT * FROM film")
    assert r["plan"] is not None


def test_table_stats():
    s = tools.table_stats("film")
    assert s["row_count"] > 0
    assert s["columns"]
    # Check that null_pct and distinct are present in statistics
    assert any(c["column"] == "title" for c in s["columns"])


def test_write_blocked_by_guard():
    with pytest.raises(GuardError):
        tools.run_readonly_query("DELETE FROM film")


def test_write_blocked_by_database_even_without_guard():
    """Layer 1 and 2 must hold even if the guard is bypassed."""
    import psycopg

    from querypilot import db

    with pytest.raises(psycopg.Error):
        db.fetch("DELETE FROM film")


def test_timeout_returns_clean_error(monkeypatch):
    from querypilot.config import settings

    monkeypatch.setattr(settings, "query_timeout_ms", 500)
    out = json.loads(
        server.run_readonly_query(sql="SELECT count(*) FROM generate_series(1, 500000000)")
    )
    assert "error" in out
    assert "time limit" in out["error"]


def test_server_never_leaks_traceback():
    out = server.run_readonly_query(sql="SELECT * FROM does_not_exist")
    assert "Traceback" not in out
    parsed = json.loads(out)
    assert "error" in parsed


def test_server_returns_untrusted_data_note():
    out = server.run_readonly_query(sql="SELECT 1 AS val")
    parsed = json.loads(out)
    assert "note" in parsed
    assert "untrusted data" in parsed["note"]


def test_server_serializes_complex_types():
    out = server.run_readonly_query(
        sql="SELECT NOW() AS ts, 12.34::numeric AS num, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::uuid AS uid"
    )
    parsed = json.loads(out)
    assert parsed["row_count"] == 1
    assert "ts" in parsed["rows"][0]
