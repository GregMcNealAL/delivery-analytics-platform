from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Settings defines all environment-based configuration for the analytics service.
    Using pydantic-settings means all values are validated, typed, and automatically
    loaded from environment variables or a .env file.
    """

    ORDERS_API_URL: str = "http://127.0.0.1:8000/orders"
    REQUEST_TIMEOUT: float = 5.0
    MAX_RETRIES: int = 3
    INITIAL_BACKOFF: float = 0.5

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

settings = Settings()