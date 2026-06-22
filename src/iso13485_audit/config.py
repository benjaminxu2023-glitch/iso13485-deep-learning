"""Central application configuration loaded from environment / .env file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Values are read from environment variables prefixed with ``ISO13485_`` or
    from a ``.env`` file in the working directory. Every field has a default so
    the system runs out of the box with zero configuration.
    """

    model_config = SettingsConfigDict(
        env_prefix="ISO13485_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite:///./audit.db"

    # NLP
    nlp_backend: str = "tfidf"  # "tfidf" | "transformer"
    nlp_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Gap detection thresholds (cosine similarity in [0, 1])
    gap_similarity_threshold: float = 0.12
    gap_high_confidence_threshold: float = 0.30

    # File system
    upload_dir: Path = Path("./uploads")
    report_output_dir: Path = Path("./reports_output")

    # API
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"

    def ensure_dirs(self) -> None:
        """Create runtime directories if they do not already exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.report_output_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
