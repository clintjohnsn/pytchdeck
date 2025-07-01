"""LLM Client."""

from langchain_openai import ChatOpenAI
from openai import OpenAI

from pytchdeck.config.settings import settings

MAX_RETRIES = settings().LLM_MAX_RETRIES
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.0
SUPPORTED_PROVIDERS = ["openai"]


def llm(
    *,
    model: str = DEFAULT_MODEL,
    provider: str = "openai",
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float | None = None,
    top_k: int | None = None,
    native: bool = False
) -> OpenAI | ChatOpenAI:
    """Get the LLM client.

    Args:
        model: The model name to use.
        provider: The LLM provider to use.
        temperature: The temperature for sampling.
        top_p: The top_p parameter for nucleus sampling.
        top_k: The top_k parameter for top-k sampling (not used by OpenAI models).
        native: Whether to return the native LLM client or LangChain wrapper.

    Returns
    -------
        OpenAI client instance (native) or ChatOpenAI instance (LangChain wrapper).
    """
    provider = provider.lower() if provider else "openai"
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider}")
    if native:
        return OpenAI(api_key=settings().OPENAI_API_KEY, max_retries=MAX_RETRIES)

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
