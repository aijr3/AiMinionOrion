"""Application configuration — all settings sourced from environment variables."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    environment: str = "development"
    strategy_port: int = 8000

    # Database
    database_url: str = "sqlite:///./uploads/strategy.db"

    # LLM (OpenAI-compatible; also read by MiroFish submodule)
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model_name: str = "gpt-4o"

    # Zep Cloud
    zep_api_key: str = ""

    # Pipeline tuning
    strategy_min_win_probability_for_graceful_exit: float = 0.40
    strategy_max_competitors_to_analyze: int = 10
    strategy_max_personas_to_generate: int = 8
    mirofish_simulation_enabled: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def mirofish_backend_path(self) -> str:
        """Absolute path to MiroFish's backend package, for sys.path injection."""
        root = Path(__file__).resolve().parents[3]
        return str(root / "mirofish" / "backend")

    @property
    def uploads_dir(self) -> Path:
        return Path(__file__).resolve().parents[2] / "uploads"

    @property
    def exports_dir(self) -> Path:
        return self.uploads_dir / "exports"

    @property
    def prompts_dir(self) -> Path:
        return Path(__file__).resolve().parent / "prompts"


settings = Settings()

# Ensure upload dirs exist
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.exports_dir.mkdir(parents=True, exist_ok=True)
