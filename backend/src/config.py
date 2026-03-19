from pathlib import Path

from pydantic_settings import BaseSettings


def _read_secret(name: str) -> str | None:
    path = Path(f"/run/secrets/{name}")
    if path.exists():
        return path.read_text().strip()
    return None


class Settings(BaseSettings):
    notion_api_key: str = ""
    notion_database_id: str = ""
    notion_data_source_id: str = ""
    notion_api_version: str = "2025-09-03"
    redis_url: str = "redis://redis:6379/0"
    cache_ttl_seconds: int = 300
    cache_invalidate_secret: str = ""
    notion_pages_data_source_id: str = ""
    sync_interval_minutes: int = 5
    backend_port: int = 8000
    supported_locales: str = "it,en"
    default_locale: str = "it"

    @property
    def parsed_locales(self) -> list[str]:
        return [loc.strip() for loc in self.supported_locales.split(",") if loc.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    def model_post_init(self, __context):
        for field in [
            "notion_api_key",
            "notion_database_id",
            "notion_data_source_id",
            "cache_invalidate_secret",
            "notion_pages_data_source_id",
        ]:
            secret = _read_secret(field)
            if secret:
                object.__setattr__(self, field, secret)


settings = Settings()
