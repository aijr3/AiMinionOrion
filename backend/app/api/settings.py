"""Settings endpoints — let users configure API keys through the UI."""
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.utils.app_settings import get_llm_settings, save_llm_settings, has_api_key
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["settings"])


class LlmSettingsUpdate(BaseModel):
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model_name: Optional[str] = None


def _masked(key: str) -> str:
    """Return a masked version of the API key for display (sk-...xxxx)."""
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return key[:7] + "..." + key[-4:]


@router.get("/settings")
def get_settings():
    """Return current effective settings (key is masked for security)."""
    s = get_llm_settings()
    return {
        "success": True,
        "data": {
            "llm_api_key_masked": _masked(s["llm_api_key"]),
            "llm_api_key_set": bool(s["llm_api_key"]),
            "llm_base_url": s["llm_base_url"],
            "llm_model_name": s["llm_model_name"],
        },
    }


@router.put("/settings")
def update_settings(payload: LlmSettingsUpdate):
    """Save user-supplied LLM settings. Pass null to leave a field unchanged."""
    save_llm_settings(
        api_key=payload.llm_api_key,
        base_url=payload.llm_base_url,
        model_name=payload.llm_model_name,
    )
    s = get_llm_settings()
    return {
        "success": True,
        "data": {
            "llm_api_key_masked": _masked(s["llm_api_key"]),
            "llm_api_key_set": bool(s["llm_api_key"]),
            "llm_base_url": s["llm_base_url"],
            "llm_model_name": s["llm_model_name"],
        },
    }


@router.post("/settings/test")
async def test_connection():
    """Send a minimal LLM request to verify the API key works."""
    if not has_api_key():
        return {"success": False, "error": "No API key configured. Add your key in Settings first."}
    try:
        from app.utils.llm_client import LLMClient
        client = LLMClient()
        reply = await client.chat(
            system="You are a test assistant.",
            user='Reply with exactly: {"ok": true}',
            temperature=0,
        )
        return {"success": True, "data": {"response": reply.strip()}}
    except Exception as e:
        logger.warning("LLM test failed: %s", e)
        return {"success": False, "error": str(e)}
