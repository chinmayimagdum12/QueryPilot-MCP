from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql://querypilot_ro:change_me_local_only@localhost:5432/pagila"
    )
    query_timeout_ms: int = 5000
    default_max_rows: int = 100
    hard_max_rows: int = 1000
    max_sql_chars: int = 10_000
    allowed_schemas: list[str] = ["public"]
    audit_log_path: str = "audit.jsonl"


settings = Settings()
