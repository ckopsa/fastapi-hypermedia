from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./domestic.db"

    class Config:
        env_file = ".env"


settings = Settings()

# Backward compatibility
DATABASE_URL = settings.database_url
