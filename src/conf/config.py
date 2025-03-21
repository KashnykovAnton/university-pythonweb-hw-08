import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # DB_URL: str = "postgresql+asyncpg://postgres:hw-08-container@localhost:5432/contacts"
    DB_URL: str = os.getenv("DB_URL")

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
