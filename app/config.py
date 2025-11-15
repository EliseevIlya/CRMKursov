import os
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
if not os.path.exists(env_path):
    env_path = None


class Settings(BaseSettings):
    # Postgres/Citus
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "fitness_crm"

    # Mongo
    MONGO_USER: str = "root"
    MONGO_PASSWORD: str = "example"
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_DB: str = "fitness_crm"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Other
    TOKEN: str = "supersecrettoken"
    ADMINS: str = "admin@example.com"

    model_config = SettingsConfigDict(env_file=env_path, extra="ignore", env_file_encoding="utf-8", env_prefix="")


settings = Settings()

# Async SQLAlchemy URL helper
def get_postgres_async_url() -> str:
    return f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"


def get_mongo_url() -> str:
    return f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}/?authSource=admin"

def get_redis_url() -> str:
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"