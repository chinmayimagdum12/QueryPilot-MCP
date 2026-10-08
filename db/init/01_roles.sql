-- QueryPilot MCP: Read-Only Role Hardening
-- Runs after Pagila schema & data have been initialized.

-- 1. Role: login only, no powers
CREATE ROLE querypilot_ro
  LOGIN PASSWORD 'change_me_local_only'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS
  CONNECTION LIMIT 5;

-- 2. Minimum access
GRANT CONNECT ON DATABASE pagila TO querypilot_ro;
GRANT USAGE ON SCHEMA public TO querypilot_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO querypilot_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO querypilot_ro;

-- 3. Session safety defaults (applied on every login)
ALTER ROLE querypilot_ro SET default_transaction_read_only = on;
ALTER ROLE querypilot_ro SET statement_timeout = '5s';
ALTER ROLE querypilot_ro SET idle_in_transaction_session_timeout = '10s';
ALTER ROLE querypilot_ro SET lock_timeout = '2s';
ALTER ROLE querypilot_ro SET work_mem = '16MB';
ALTER ROLE querypilot_ro SET temp_file_limit = '256MB';
ALTER ROLE querypilot_ro SET search_path = public;
