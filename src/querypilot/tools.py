import difflib

from psycopg import sql as psql

from . import db
from .guard import validate_sql


class ToolError(Exception):
    """User-facing error with a helpful message."""


def _tables(schema: str) -> list[str]:
    """Fetch existing table/view names for a schema from information_schema."""
    return [
        r["table_name"]
        for r in db.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY 1",
            (schema,),
            max_rows=1000,
        )["rows"]
    ]


def _require_table(schema: str, table: str) -> None:
    """Ensure table exists; suggest close matches if typo is detected."""
    names = _tables(schema)
    if table not in names:
        close = difflib.get_close_matches(table, names, n=3)
        hint = f" Did you mean: {', '.join(close)}?" if close else ""
        raise ToolError(f"Table '{schema}.{table}' not found.{hint}")


def list_tables(schema: str = "public") -> dict:
    """List tables and views in a schema with estimated row counts."""
    rows = db.fetch(
        """SELECT c.relname AS table_name,
                  CASE c.relkind
                       WHEN 'r' THEN 'table'
                       WHEN 'v' THEN 'view'
                       WHEN 'm' THEN 'materialized view'
                       WHEN 'p' THEN 'partitioned table'
                  END AS type,
                  c.reltuples::bigint AS estimated_rows
           FROM pg_class c
           JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = %s AND c.relkind IN ('r','v','m','p')
           ORDER BY c.relname""",
        (schema,),
        max_rows=1000,
    )["rows"]
    return {"schema": schema, "tables": rows}


def describe_table(table: str, schema: str = "public") -> dict:
    """Show columns, types, primary and foreign keys, and indexes for a table."""
    _require_table(schema, table)
    cols = db.fetch(
        """SELECT column_name, data_type, is_nullable, column_default
           FROM information_schema.columns
           WHERE table_schema = %s AND table_name = %s
           ORDER BY ordinal_position""",
        (schema, table),
        max_rows=1000,
    )["rows"]
    cons = db.fetch(
        """SELECT conname AS name,
                  CASE contype
                       WHEN 'p' THEN 'primary key'
                       WHEN 'f' THEN 'foreign key'
                       WHEN 'u' THEN 'unique'
                       WHEN 'c' THEN 'check'
                  END AS type,
                  pg_get_constraintdef(oid) AS definition
           FROM pg_constraint
           WHERE conrelid = to_regclass(quote_ident(%s) || '.' || quote_ident(%s))""",
        (schema, table),
        max_rows=200,
    )["rows"]
    idx = db.fetch(
        """SELECT indexname, indexdef
           FROM pg_indexes
           WHERE schemaname = %s AND tablename = %s""",
        (schema, table),
        max_rows=200,
    )["rows"]
    return {
        "table": f"{schema}.{table}",
        "columns": cols,
        "constraints": cons,
        "indexes": idx,
    }


def run_readonly_query(sql: str, max_rows: int = 100) -> dict:
    """Validate and run a read-only SQL query."""
    return db.fetch(validate_sql(sql), max_rows=max_rows)


def explain_query(sql: str) -> dict:
    """Generate the query plan using EXPLAIN (FORMAT JSON). Never executes the query."""
    safe = validate_sql(sql)
    res = db.fetch("EXPLAIN (FORMAT JSON) " + safe, max_rows=1)
    return {"plan": res["rows"][0]["QUERY PLAN"] if res["rows"] else None}


def table_stats(table: str, schema: str = "public") -> dict:
    """Calculate row count, null percentages, and distinct counts using safe identifier quoting."""
    _require_table(schema, table)
    cols = db.fetch(
        """SELECT column_name, data_type
           FROM information_schema.columns
           WHERE table_schema = %s AND table_name = %s
           ORDER BY ordinal_position""",
        (schema, table),
        max_rows=30,  # limit to first 30 columns for performance
    )["rows"]
    parts = [psql.SQL("count(*) AS total")]
    for i, c in enumerate(cols):
        ident = psql.Identifier(c["column_name"])
        parts.append(psql.SQL("count({}) AS {}").format(ident, psql.Identifier(f"nn_{i}")))
        if c["data_type"] not in ("json", "jsonb", "xml", "point"):
            parts.append(psql.SQL("count(DISTINCT {}) AS {}").format(ident, psql.Identifier(f"d_{i}")))
    q = psql.SQL("SELECT {} FROM {}.{}").format(
        psql.SQL(", ").join(parts), psql.Identifier(schema), psql.Identifier(table)
    )
    row = db.fetch(q, max_rows=1)["rows"][0]
    total = row["total"]
    out = []
    for i, c in enumerate(cols):
        nn = row.get(f"nn_{i}", 0)
        out.append({
            "column": c["column_name"],
            "type": c["data_type"],
            "null_pct": round(100 * (total - nn) / total, 2) if total else 0.0,
            "distinct": row.get(f"d_{i}"),
        })
    return {"table": f"{schema}.{table}", "row_count": total, "columns": out}
