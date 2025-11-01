from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Delivery Service"
    ENV: str = "development"
    DATABASE_URL: str
    RABBITMQ_URL: str

    class Config:
        env_file = ".env"

settings = Settings()