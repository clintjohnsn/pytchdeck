"""LLM Client."""

from functools import lru_cache

from openai import OpenAI

from pytchdeck.config.settings import settings


@lru_cache
def llm() -> OpenAI:
    """Get the  LLM client."""
    return OpenAI(api_key=settings().OPENAI_API_KEY)
