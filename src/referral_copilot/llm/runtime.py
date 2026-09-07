"""Runtime helpers for live structured LLM calls with explicit fallback behavior."""

from typing import Any, Optional, Type
import logging

from pydantic import BaseModel

from referral_copilot.config import settings
from referral_copilot.llm.factory import get_llm


def configured_provider() -> Optional[str]:
    """Return the configured provider only when a usable API key is present."""
    candidates = {"gemini": settings.gemini_api_key, "groq": settings.groq_api_key}
    requested = settings.llm_provider.lower()
    if requested in candidates and candidates[requested] and not candidates[requested].startswith("<YOUR_"):
        return requested
    for provider, key in candidates.items():
        if key and not key.startswith("<YOUR_"):
            return provider
    return None


def invoke_structured(
    schema: Type[BaseModel],
    system_prompt: str,
    user_prompt: str,
    *,
    fallback: BaseModel,
) -> tuple[BaseModel, bool, Optional[str]]:
    """Call the configured provider and return a validated result.

    The boolean indicates whether a live provider was used. If no key exists, or a
    live call fails, the caller receives its deterministic fallback plus the error.
    """
    provider = configured_provider()
    if provider is None:
        return fallback, False, "No configured LLM API key"

    try:
        # The Google SDK emits a one-time advisory when structured output is used.
        # It is informational; API failures still propagate through this call.
        logging.getLogger("google_genai.models").setLevel(logging.ERROR)
        model = get_llm(provider_override=provider)
        structured_model = model.with_structured_output(schema)
        result = structured_model.invoke([
            ("system", system_prompt),
            ("human", user_prompt),
        ])
        return result, True, None
    except Exception as exc:
        return fallback, False, f"{type(exc).__name__}: {exc}"


def live_status_log(provider_used: bool, error: Optional[str]) -> dict[str, Any]:
    """Create a safe trace entry without recording prompts or secrets."""
    result: dict[str, Any] = {"llm_mode": "live" if provider_used else "fallback"}
    if error:
        result["llm_error"] = error[:300]
    if provider_used:
        result["llm_provider"] = configured_provider()
    return result