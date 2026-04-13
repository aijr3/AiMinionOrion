"""Loads LLM prompt templates from the prompts/ directory."""
from pathlib import Path
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
_cache: dict[str, str] = {}


def load_prompt(name: str, **kwargs) -> str:
    """Load a prompt template by filename (without .txt) and interpolate kwargs."""
    if name not in _cache:
        path = settings.prompts_dir / f"{name}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")
        _cache[name] = path.read_text(encoding="utf-8")
        logger.info("Loaded prompt template: %s", name)
    template = _cache[name]
    if kwargs:
        try:
            return template.format_map(kwargs)
        except KeyError as e:
            logger.warning("Prompt %s missing variable: %s", name, e)
            return template
    return template
