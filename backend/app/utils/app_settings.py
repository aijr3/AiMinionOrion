"""Persistent app settings stored as JSON in uploads/app_settings.json.

This lets users configure the LLM API key through the UI without needing
to edit environment variables or restart the server.

Priority order for each setting:
  1. Value saved in app_settings.json  (set via UI)
  2. Value from environment variable   (set in .env or shell)
  3. Hard-coded default
"""
import json
import threading
from pathlib import Path
from typing import Optional

from app.config import settings as env_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_SETTINGS_FILE = Path(__file__).resolve().parents[3] / "uploads" / "app_settings.json"
_lock = threading.Lock()


def _load_file() -> dict:
    try:
        if _SETTINGS_FILE.exists():
            return json.loads(_SETTINGS_FILE.read_text())
    except Exception as e:
        logger.warning("Could not read app_settings.json: %s", e)
    return {}


def _save_file(data: dict) -> None:
    _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SETTINGS_FILE.write_text(json.dumps(data, indent=2))


def get_llm_settings() -> dict:
    """Return the effective LLM settings, merging file → env → defaults."""
    with _lock:
        stored = _load_file()
    return {
        "llm_api_key": stored.get("llm_api_key") or env_settings.llm_api_key or "",
        "llm_base_url": stored.get("llm_base_url") or env_settings.llm_base_url or "https://api.openai.com/v1",
        "llm_model_name": stored.get("llm_model_name") or env_settings.llm_model_name or "gpt-4o",
    }


def save_llm_settings(api_key: Optional[str], base_url: Optional[str], model_name: Optional[str]) -> None:
    """Persist user-supplied LLM settings to disk."""
    with _lock:
        stored = _load_file()
        if api_key is not None:
            stored["llm_api_key"] = api_key.strip()
        if base_url is not None:
            stored["llm_base_url"] = base_url.strip()
        if model_name is not None:
            stored["llm_model_name"] = model_name.strip()
        _save_file(stored)
    logger.info("LLM settings saved to %s", _SETTINGS_FILE)


def has_api_key() -> bool:
    """Return True if an API key is configured (file or env)."""
    s = get_llm_settings()
    return bool(s.get("llm_api_key"))
