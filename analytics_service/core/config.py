from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    ORDERS_API_URL: str = "http://127.0.0.1:8000/orders"
    ORDERS_API_KEY: str
    REQUEST_TIMEOUT: float = 5.0
    MAX_RETRIES: int = 3
    INITIAL_BACKOFF: float = 0.5

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

settings = Settings()