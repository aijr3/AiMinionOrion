"""LLM client — wraps OpenAI-compatible API. Falls back to direct openai SDK if MiroFish unavailable.

API key is read dynamically from app_settings (UI-configured) on every request,
so users can update their key through the settings UI without restarting the server.
"""
import json
import sys
from typing import AsyncGenerator

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Try to import MiroFish's LLMClient first
_mirofish_client = None
try:
    if settings.mirofish_backend_path not in sys.path:
        sys.path.insert(0, settings.mirofish_backend_path)
    from app.utils.llm_client import LLMClient as _MiroFishLLMClient  # type: ignore
    _mirofish_client = _MiroFishLLMClient
    logger.info("Using MiroFish LLMClient")
except ImportError:
    logger.info("MiroFish LLMClient not available — using direct OpenAI SDK")


def _get_openai_client():
    """Build a fresh AsyncOpenAI client using the current effective settings."""
    from openai import AsyncOpenAI
    from app.utils.app_settings import get_llm_settings
    s = get_llm_settings()
    return AsyncOpenAI(
        api_key=s["llm_api_key"] or "no-key-set",
        base_url=s["llm_base_url"],
    )


def _get_model_name() -> str:
    from app.utils.app_settings import get_llm_settings
    return get_llm_settings()["llm_model_name"]


class LLMClient:
    """Unified LLM client for the Strategy App.

    Reads API key from app_settings on every call so UI changes take effect
    immediately — no restart required.
    """

    async def chat(self, system: str, user: str, temperature: float = 0.7) -> str:
        """Send a chat completion and return the text response."""
        client = _get_openai_client()
        response = await client.chat.completions.create(
            model=_get_model_name(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    async def chat_json(self, system: str, user: str, temperature: float = 0.3) -> dict | list:
        """Send a chat completion expecting JSON. Parses and returns parsed object."""
        raw = await self.chat(system, user, temperature)
        # Strip markdown code fences if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON substring
            start = text.find("{") if "{" in text else text.find("[")
            end = text.rfind("}") + 1 if "}" in text else text.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            logger.warning("LLM returned non-JSON: %s", text[:200])
            return {}

    async def stream(self, system: str, user: str) -> AsyncGenerator[str, None]:
        """Stream a chat completion token by token."""
        client = _get_openai_client()
        async for chunk in await client.chat.completions.create(
            model=_get_model_name(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            stream=True,
        ):
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
