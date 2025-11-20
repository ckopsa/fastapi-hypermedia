from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./domestic.db"
    keycloak_api_client_id: str = ""
    keycloak_api_client_secret: str = ""
    keycloak_realm: str = ""
    keycloak_redirect_uri: str = ""
    keycloak_server_url: str = ""

    class Config:
        env_file = ".env"


settings = Settings()

# Backward compatibility
DATABASE_URL = settings.database_url
KEYCLOAK_API_CLIENT_ID = settings.keycloak_api_client_id
KEYCLOAK_API_CLIENT_SECRET = settings.keycloak_api_client_secret
KEYCLOAK_REALM = settings.keycloak_realm
KEYCLOAK_REDIRECT_URI = settings.keycloak_redirect_uri
KEYCLOAK_SERVER_URL = settings.keycloak_server_url
