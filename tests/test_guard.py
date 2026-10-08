import pytest

from querypilot.guard import GuardError, validate_sql

ALLOWED = [
    "SELECT * FROM film",
    "SELECT * FROM film;",
    "  select title from film where length > 100 limit 5  ",
    "SELECT a FROM t1 UNION SELECT b FROM t2",
    "WITH x AS (SELECT 1 AS n) SELECT * FROM x",
    "SELECT f.title, count(*) FROM film f JOIN inventory i USING (film_id) GROUP BY f.title",
    "SELECT * FROM public.film",
    "SELECT 'DELETE FROM film' AS text_value",  # keyword inside a string is fine
    "SELECT 1 AS col WHERE 1=1",
    "SELECT a FROM t INTERSECT SELECT b FROM u",
    "SELECT a FROM t EXCEPT SELECT b FROM u",
]

BLOCKED = [
    "",
    "   ",
    "not sql at all",
    "DELETE FROM film",
    "dElEtE FROM film",
    "UPDATE film SET title='x'",
    "INSERT INTO film(title) VALUES ('x')",
    "DROP TABLE film",
    "TRUNCATE film",
    "CREATE TABLE x(a int)",
    "ALTER TABLE film ADD c int",
    "GRANT ALL ON film TO public",
    "SELECT 1; DROP TABLE film",
    "SELECT 1; SELECT 2",
    "/* hi */ DROP TABLE film",
    "-- c\nDROP TABLE film",
    "WITH d AS (DELETE FROM film RETURNING *) SELECT * FROM d",
    "WITH u AS (UPDATE film SET title='x' RETURNING *) SELECT * FROM u",
    "SELECT * INTO newt FROM film",
    "SELECT * FROM film FOR UPDATE",
    "SELECT pg_sleep(100)",
    "SELECT PG_SLEEP(1)",
    "SELECT pg_catalog.pg_sleep(1)",
    "SELECT pg_read_file('/etc/passwd')",
    "SELECT lo_import('/etc/passwd')",
    "SELECT nextval('film_film_id_seq')",
    "SELECT set_config('role','postgres',false)",
    "SELECT pg_advisory_lock(1)",
    "SELECT pg_terminate_backend(1)",
    "SELECT * FROM dblink('host=x','select 1') AS t(a int)",
    "SET ROLE postgres",
    "COPY film TO '/tmp/x'",
    "COPY film FROM PROGRAM 'id'",
    "BEGIN; SELECT 1; COMMIT",
    "SELECT * FROM pg_user",
    "SELECT * FROM pg_catalog.pg_shadow",
    "SELECT * FROM information_schema.tables",
    "SELECT * FROM secret_schema.users",
    "SELECT 1" + " " * 20000,
    "SELECT 1\x00 WHERE 1=1",
]


@pytest.mark.parametrize("q", ALLOWED)
def test_allowed(q):
    assert validate_sql(q)


@pytest.mark.parametrize("q", BLOCKED)
def test_blocked(q):
    with pytest.raises(GuardError):
        validate_sql(q)


def test_trailing_semicolon_removed():
    assert validate_sql("SELECT 1;") == "SELECT 1"


def test_empty_sql_variations():
    with pytest.raises(GuardError, match="Empty query"):
        validate_sql("")
    with pytest.raises(GuardError, match="Empty query"):
        validate_sql("   ")
    with pytest.raises(GuardError, match="Empty query"):
        validate_sql(None)


def test_null_byte():
    with pytest.raises(GuardError, match="Invalid characters in query"):
        validate_sql("SELECT 1\x00")


def test_query_too_long():
    with pytest.raises(GuardError, match="Query is too long"):
        validate_sql("SELECT " + "a" * 15000)
