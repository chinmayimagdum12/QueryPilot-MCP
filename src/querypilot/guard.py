import re

import sqlglot
from sqlglot import exp

from .config import settings


class GuardError(ValueError):
    """Raised when a query is not allowed. Message is safe to show to the user."""


BLOCKED_FUNCS = {
    "pg_sleep",
    "pg_sleep_for",
    "pg_sleep_until",
    "pg_read_file",
    "pg_read_binary_file",
    "pg_ls_dir",
    "pg_stat_file",
    "lo_import",
    "lo_export",
    "lo_get",
    "lo_put",
    "dblink",
    "dblink_exec",
    "dblink_connect",
    "set_config",
    "nextval",
    "setval",
    "pg_advisory_lock",
    "pg_advisory_xact_lock",
    "pg_try_advisory_lock",
    "pg_notify",
    "pg_terminate_backend",
    "pg_cancel_backend",
    "pg_reload_conf",
    "pg_switch_wal",
    "pg_create_restore_point",
}

# Belt and braces: scan raw text for blocked functions
RAW_DENY = re.compile(r"\b(" + "|".join(sorted(BLOCKED_FUNCS)) + r")\b", re.IGNORECASE)


def _types(names: list[str]) -> tuple:
    """Version-safe: collect node types available in this sqlglot version."""
    return tuple(getattr(exp, n) for n in names if hasattr(exp, n))


ALLOWED_TOP = _types(["Select", "Union", "Intersect", "Except", "SetOperation", "Subquery"])
BLOCKED_NODES = _types([
    "Insert",
    "Update",
    "Delete",
    "Drop",
    "Create",
    "Alter",
    "AlterTable",
    "Command",
    "Set",
    "Merge",
    "Copy",
    "Truncate",
    "TruncateTable",
    "Grant",
    "Transaction",
    "Commit",
    "Rollback",
    "Into",
    "Lock",
])


def validate_sql(sql: str) -> str:
    """Return a validated single read-only SELECT statement or raise GuardError."""
    if not sql or not sql.strip():
        raise GuardError("Empty query.")
    if len(sql) > settings.max_sql_chars:
        raise GuardError("Query is too long.")
    if "\x00" in sql:
        raise GuardError("Invalid characters in query.")

    # Remove any trailing semicolon and surrounding whitespace
    sql = sql.strip().rstrip(";").strip()

    # Fast raw text check for blocked dangerous functions
    if RAW_DENY.search(sql):
        raise GuardError("Query uses a blocked function.")

    try:
        statements = [s for s in sqlglot.parse(sql, read="postgres") if s is not None]
    except sqlglot.errors.SqlglotError as e:
        raise GuardError("SQL could not be parsed. Check the syntax.") from e

    if len(statements) != 1:
        raise GuardError("Only one statement is allowed.")

    tree = statements[0]

    if not isinstance(tree, ALLOWED_TOP):
        raise GuardError("Only SELECT queries are allowed.")

    # Reject data-changing statements, locks, or SELECT INTO anywhere in the AST
    if tree.find(*BLOCKED_NODES):
        raise GuardError("Data-changing, locking, or SELECT INTO statements are not allowed.")

    # Explicit check for SELECT INTO
    if tree.args.get("into"):
        raise GuardError("SELECT INTO is not allowed.")

    # Explicit check for locking clauses (e.g. FOR UPDATE)
    lock_type = getattr(exp, "Lock", None)
    if (lock_type and tree.find(lock_type)) or tree.args.get("locks"):
        raise GuardError("Locking clauses (FOR UPDATE) are not allowed.")

    # AST check for blocked functions
    for fn in tree.find_all(exp.Func):
        name = (fn.name if isinstance(fn, exp.Anonymous) else fn.sql_name()).lower()
        if name.split(".")[-1] in BLOCKED_FUNCS:
            raise GuardError(f"Function '{name}' is not allowed.")

    # Schema and system catalog checks
    for t in tree.find_all(exp.Table):
        schema = (t.db or "").lower()
        name = (t.name or "").lower()
        if schema and schema not in settings.allowed_schemas:
            raise GuardError(f"Schema '{schema}' is not allowed.")
        if name.startswith("pg_") or schema in ("pg_catalog", "information_schema"):
            raise GuardError("System catalogs are not allowed. Use list_tables or describe_table.")

    return sql
