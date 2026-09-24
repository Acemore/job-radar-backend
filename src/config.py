from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    EXTERNAL_CORE_GATEWAY: str | None = None

    NETWORK_MAX_DIRECT_ATTEMPTS: int = 2
    NETWORK_BACKOFF_FACTOR: float = 0.5
    NETWORK_NODES_FILE: str = "nodes.txt"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
