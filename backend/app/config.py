"""Application configuration loaded from environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root: two levels up from this file (backend/app/config.py → project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Settings loaded from .env file at project root."""

    anthropic_api_key: str = ""
    backend_port: int = 8000
    backend_host: str = "0.0.0.0"
    log_level: str = "INFO"

    # Directories (resolved to absolute from project root)
    upload_dir: Path = Path("backend/data/uploads")
    processed_dir: Path = Path("backend/data/processed")
    synthetic_dir: Path = Path("backend/data/synthetic")
    fallback_dir: Path = Path("backend/data/fallbacks")
    sample_data_dir: Path = Path("sample-data")

    def model_post_init(self, __context: object) -> None:
        """Resolve relative directory paths against project root."""
        for field in (
            "upload_dir",
            "processed_dir",
            "synthetic_dir",
            "fallback_dir",
            "sample_data_dir",
        ):
            p = getattr(self, field)
            if not p.is_absolute():
                object.__setattr__(self, field, _PROJECT_ROOT / p)

    # Feature flags
    demo_mode: bool = True
    fallback_enabled: bool = True
    pipeline_timeout_seconds: int = 300

    # CORS
    cors_origins: str = "http://localhost,http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE), env_file_encoding="utf-8", extra="ignore",
    )
