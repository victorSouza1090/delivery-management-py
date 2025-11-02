from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default="Delivery Service", alias="APP_NAME")
    env: str = Field(default="development", alias="ENV")
    app_port: int = Field(default=8000, alias="APP_PORT")

    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")
    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(alias="DB_PORT")
    db_name: str = Field(alias="DB_NAME")
    database_url: str = Field(alias="DATABASE_URL")

    rabbitmq_user: str = Field(alias="RABBITMQ_USER")
    rabbitmq_password: str = Field(alias="RABBITMQ_PASSWORD")
    rabbitmq_host: str = Field(alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(alias="RABBITMQ_PORT")
    rabbitmq_vhost: str = Field(alias="RABBITMQ_VHOST")
    rabbitmq_url: str = Field(alias="RABBITMQ_URL")

    log_level: str = Field(alias="LOG_LEVEL")
    enable_structured_logs: str = Field(alias="ENABLE_STRUCTURED_LOGS")

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()