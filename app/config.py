from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_PORT: int = 8000
    DATABASE_URL: str
    REDIS_URL: str
    EXTERNAL_API_URL: str = "https://api.open-meteo.com/v1/forecast"

    class Config:
        env_file = ".env"

settings = Settings()