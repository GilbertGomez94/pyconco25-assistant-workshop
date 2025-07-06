from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings, Field


class Settings(BaseSettings):
    """Centraliza las variables de entorno."""
    # LLM
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    # External APIs
    news_api_key: str = Field(..., env="NEWS_API_KEY")

    # Email
    email_host: str = Field(..., env="EMAIL_HOST")
    email_port: int = Field(..., env="EMAIL_PORT")
    email_user: str = Field(..., env="EMAIL_USER")
    email_password: str = Field(..., env="EMAIL_PASSWORD")
    tavily_api_key: str = Field(..., env="TAVILY_API_KEY")
    postgres_database_url: str = Field(..., env="POSTGRES_DATABASE_URL")
    embedding_dim: int = 1536

    class Config:
        extra = "ignore"
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings()
