"""Server settings."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Server settings."""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PytchDeck API"
    API_DESCRIPTION: str = "API for Pytchdeck"
    VERSION: str = "0.1.0"

    # Environment
    ENV: str = "dev"
    # Logging
    LOG_LEVEL: str = "INFO"
    # API Keys
    OPENAI_API_KEY: str
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # Data Directory
    DATA_DIR: Path = Path("data")
    CANDIDATE_DIR: Path = DATA_DIR / "candidate"
    PUBLIC_DIR: Path = DATA_DIR / "public"
    # Directory for generated HTML decks
    GENERATED_DIR: Path = PUBLIC_DIR / "generated"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    # Target Role
    TARGET_ROLES: str = "Software Engineer, AI Engineer"

    @property
    def cors_origins(self) -> list[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def cors_config(self) -> dict:
        """Return CORS configuration dictionary."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set environment variables
        os.environ["USER_AGENT"] = f"pytchdeck/{self.VERSION}"  # Ell user agent
        os.environ["LANGFUSE_TRACING_ENVIRONMENT"] = self.ENV  # Langfuse env
        # Ensure required directories exist
        self.PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        self.GENERATED_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache
def settings() -> Settings:
    """Get the settings."""
    return Settings()
