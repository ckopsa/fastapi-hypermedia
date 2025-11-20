from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./domestic.db"
    use_dominate: bool = True

    class Config:
        env_file = ".env"


settings = Settings()

# Backward compatibility
DATABASE_URL = settings.database_url
USE_DOMINATE = settings.use_dominate
