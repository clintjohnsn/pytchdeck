"""LLM Client."""

from functools import lru_cache

from langchain_openai import ChatOpenAI
from openai import OpenAI

from pytchdeck.config.settings import settings

MAX_RETRIES = settings().LLM_MAX_RETRIES
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.0
SUPPORTED_PROVIDERS = ["openai"]

@lru_cache
def llm(config: dict | None = None, native: bool = False) -> OpenAI | ChatOpenAI:
    """Get the LLM client.

    Args:
        config: Dictionary containing model parameters (provider, temperature, top_p, model, top_k).
        native: Whether to return the native LLM client or LangChain wrapper.

    Returns
    -------
        OpenAI client instance (native) or ChatOpenAI instance (LangChain wrapper).
    """
    if config is None:
        config = {}
    provider: str = config.pop("provider", "openai")
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider}")
    if native:
        return OpenAI(api_key=settings().OPENAI_API_KEY, max_retries=MAX_RETRIES)
    model: str = config.pop("model", DEFAULT_MODEL)
    temperature: float = config.pop("temperature", DEFAULT_TEMPERATURE)
    top_p: float | None = config.pop("top_p", None)
    top_k: int | None = config.pop("top_k", None)  # not used by OpenAI models

    langchain_kwargs = {
        "model": model,
        "temperature": temperature,
        "api_key": settings().OPENAI_API_KEY,
        "max_retries": MAX_RETRIES,
    }
    if top_k is not None:
        langchain_kwargs["top_k"] = top_k
    if top_p is not None:
        langchain_kwargs["top_p"] = top_p

    return ChatOpenAI(**langchain_kwargs)
