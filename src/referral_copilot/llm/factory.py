"""Centralized LLM Factory Module.

Provides a unified interface `get_llm()` for instantiating the configured model
provider (Google Gemini or Groq) without hardcoding model names or providers in individual nodes/agents.
"""

import os
from typing import Any, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from referral_copilot.config import settings


def get_llm(
    provider_override: Optional[str] = None,
    temperature_override: Optional[float] = None,
    **kwargs: Any
) -> BaseChatModel:
    """Obtains a configured LangChain BaseChatModel based on central settings.

    Args:
        provider_override: Optional provider override ('gemini' or 'groq').
        temperature_override: Optional temperature override.
        **kwargs: Additional kwargs passed to the chat model constructor.

    Returns:
        BaseChatModel: Initialized LangChain chat model instance.

    Raises:
        ValueError: If provider is unsupported or required API key is missing.
    """
    provider = (provider_override or settings.llm_provider).lower()
    temp = temperature_override if temperature_override is not None else settings.temperature

    if provider == "gemini":
        api_key = settings.gemini_api_key
        # Check environment variable if settings placeholder
        if not api_key or api_key.startswith("<YOUR_"):
            api_key = os.getenv("GEMINI_API_KEY", "")

        if not api_key or api_key.startswith("<YOUR_"):
            raise ValueError(
                "LIVE API VERIFICATION BLOCKED: Gemini API key is missing or unconfigured. "
                "Set GEMINI_API_KEY in .env or environment."
            )

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=api_key,
                temperature=temp,
                timeout=settings.timeout,
                max_retries=settings.llm_api_retries,
                **kwargs
            )
        except ImportError:
            raise ImportError(
                "langchain-google-genai package is required for Gemini provider. "
                "Install via: pip install langchain-google-genai"
            )

    elif provider == "groq":
        api_key = settings.groq_api_key
        if not api_key or api_key.startswith("<YOUR_"):
            api_key = os.getenv("GROQ_API_KEY", "")

        if not api_key or api_key.startswith("<YOUR_"):
            raise ValueError(
                "LIVE API VERIFICATION BLOCKED: Groq API key is missing or unconfigured. "
                "Set GROQ_API_KEY in .env or environment."
            )

        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=settings.groq_model,
                groq_api_key=api_key,
                temperature=temp,
                timeout=settings.timeout,
                max_retries=settings.llm_api_retries,
                **kwargs
            )
        except ImportError:
            raise ImportError(
                "langchain-groq package is required for Groq provider. "
                "Install via: pip install langchain-groq"
            )

    else:
        raise ValueError(
            f"Unsupported LLM provider '{provider}'. Approved providers are 'gemini' or 'groq'."
        )
