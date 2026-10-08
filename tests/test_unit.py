import datetime
import json
import uuid
from decimal import Decimal

import pytest

from querypilot import audit, server, tools
from querypilot.config import settings


def test_server_json_serialization_handles_complex_types():
    data = {
        "decimal_val": Decimal("49.99"),
        "datetime_val": datetime.datetime(2026, 10, 8, 12, 0, 0, tzinfo=datetime.UTC),
        "date_val": datetime.date(2026, 10, 8),
        "uuid_val": uuid.UUID("12345678-1234-5678-1234-567812345678"),
        "bytes_val": b"binary_data",
    }
    serialized = server._out(data)
    deserialized = json.loads(serialized)
    assert deserialized["decimal_val"] == "49.99"
    assert "2026-10-08" in deserialized["datetime_val"]
    assert deserialized["date_val"] == "2026-10-08"
    assert deserialized["uuid_val"] == "12345678-1234-5678-1234-567812345678"


def test_audit_logging_format_and_safety(tmp_path, monkeypatch):
    test_audit_path = tmp_path / "test_audit.jsonl"
    monkeypatch.setattr(settings, "audit_log_path", str(test_audit_path))

    audit.log("run_readonly_query", "SELECT 1 AS safe_test", "ok", 3.5)
    audit.log("run_readonly_query", "DROP TABLE film", "blocked", 0.0)

    assert test_audit_path.exists()
    lines = test_audit_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2

    entry1 = json.loads(lines[0])
    assert entry1["tool"] == "run_readonly_query"
    assert entry1["detail"] == "SELECT 1 AS safe_test"
    assert entry1["status"] == "ok"
    assert entry1["elapsed_ms"] == 3.5
    assert "ts" in entry1

    entry2 = json.loads(lines[1])
    assert entry2["status"] == "blocked"
    assert "DROP TABLE" in entry2["detail"]

    # Verify no credentials or internal rows leaked
    for line in lines:
        assert "password" not in line.lower()
        assert "postgres://" not in line.lower()


def test_fuzzy_table_matching_suggestion(monkeypatch):
    # Mock _tables to return sample table names without needing DB
    monkeypatch.setattr(tools, "_tables", lambda schema: ["film", "customer", "rental"])

    with pytest.raises(tools.ToolError) as exc:
        tools._require_table("public", "filmm")
    assert "Did you mean: film?" in str(exc.value)

    with pytest.raises(tools.ToolError) as exc:
        tools._require_table("public", "costomer")
    assert "Did you mean: customer?" in str(exc.value)

    # When no close matches exist
    with pytest.raises(tools.ToolError) as exc:
        tools._require_table("public", "completely_unrelated")
    assert "Table 'public.completely_unrelated' not found." in str(exc.value)
    assert "Did you mean" not in str(exc.value)


def test_audit_report_script_execution(tmp_path, monkeypatch, capsys):
    from scripts import audit_report

    test_audit_path = tmp_path / "audit.jsonl"
    entries = [
        {"ts": "2026-10-08T12:00:00+0000", "tool": "list_tables", "detail": "public", "status": "ok", "elapsed_ms": 2.1},
        {"ts": "2026-10-08T12:00:01+0000", "tool": "run_readonly_query", "detail": "SELECT 1", "status": "ok", "elapsed_ms": 5.4},
        {"ts": "2026-10-08T12:00:02+0000", "tool": "run_readonly_query", "detail": "DELETE", "status": "blocked", "elapsed_ms": 0.0},
    ]
    with open(test_audit_path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(e) + "\n" for e in entries)

    # Change working directory in test so script finds audit.jsonl
    monkeypatch.chdir(tmp_path)
    audit_report.main()
    captured = capsys.readouterr().out
    assert "Total queries logged: 3" in captured
    assert "list_tables" in captured
    assert "blocked" in captured
