from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "infra_insight"
    POSTGRES_USER: str = "infra"
    POSTGRES_PASSWORD: str = "infra"

    class Config:
        env_file = ".env"

settings = Settings()
