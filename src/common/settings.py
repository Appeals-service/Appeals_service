import sys
from pathlib import Path
from uuid import uuid4

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    SERVICE_NAME: str = "Appeals service"

    DB_USER: str = "POSTGRES"
    DB_PASSWORD: str = "POSTGRES"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "POSTGRES"
    DB_SCHEMA: str = "appeals_service"

    TEST_DB_SCHEMA_PREFIX: str = "test_"
    IS_TESTING: bool = False

    DEBUG: bool = True
    RELOAD: bool = True
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    CORS_ORIGINS: str = "*"

    SECRET_KEY: str = ""
    ALGORITHM: str = ""

    MAX_PHOTO_SIZE_IN_BYTES: int = 5 * 1024 * 1024

    S3_URL: str = ""
    S3_BUCKET_NAME: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    SELECTEL_STORAGE_DOMAIN: str = ""

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_DEFAULT_USER: str = ""
    RABBITMQ_DEFAULT_PASS: str = ""
    RABBITMQ_EXCHANGE_NAME: str = ""
    RABBITMQ_NOTIFICATION_QUEUE_NAME: str = ""
    RABBITMQ_NOTIFICATION_ROUTING_KEY: str = ""
    RABBITMQ_LOGS_QUEUE_NAME: str = ""
    RABBITMQ_LOGS_ROUTING_KEY: str = ""

    LOGGING_LEVEL: str = "DEBUG"
    LOGGING_JSON: bool = True
    LOGGING_FORMAT: str = "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"

    AUTHORIZATION_SERVICE_URL: str = "http://localhost:8001"
    AUTHORIZATION_SERVICE_TIMEOUT: int = 5

    ECHO: bool = False

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", env_file_encoding="utf-8", extra="allow")

    @property
    def log_config(self) -> dict:
        return {
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": self.LOGGING_LEVEL, "propagate": False},
                "sqlalchemy": {"handlers": ["default"], "level": self.LOGGING_LEVEL, "propagate": False},
            }
        }

    def get_db_url(self, async_mode: bool = True) -> str:
        return (f"{'postgresql+asyncpg' if async_mode else 'postgresql'}://"
                f"{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


    def get_rmq_url(self) -> str:
        return (f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@"
                f"{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/")


settings = Settings()


if "pytest" in sys.modules:  # pragma: no cover
    settings.DB_SCHEMA = settings.TEST_DB_SCHEMA_PREFIX + uuid4().hex + "_" + settings.DB_SCHEMA
    settings.SECRET_KEY = "test_secret_key_lksdf3"
    settings.ALGORITHM = "HS256"
    settings.IS_TESTING = True

    settings.DB_USER = "postgres"
    settings.DB_PASSWORD = "postgres"
    settings.DB_HOST = "localhost"
    settings.DB_PORT = 5432
    settings.DB_NAME = "postgres"
