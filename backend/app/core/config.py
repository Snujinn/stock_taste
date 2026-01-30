from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV_NAME: str = "dev"
    DATABASE_URL: str = "postgresql+psycopg://user:password@db:5432/stock_game"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "filesecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FINNHUB_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
