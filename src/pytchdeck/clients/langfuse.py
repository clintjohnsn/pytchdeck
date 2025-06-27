"""Langfuse Client."""

import logging
from functools import lru_cache
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from pytchdeck.config.settings import settings
from pytchdeck.models.exceptions import PromptNotFoundError

# Initialize Langfuse client
client = Langfuse()
config = settings()
DEFAULT_LABEL = "latest" if config.ENV == "dev" else "production"

logger = logging.getLogger(__name__)


@lru_cache
def trace_callback() -> CallbackHandler:
    """Get the Langfuse callback handler."""
    return CallbackHandler()


@lru_cache
def get_client() -> Langfuse:
    """Get the Langfuse client."""
    return client


async def load_prompt(
    name: str,
    label: str = DEFAULT_LABEL,
    prompt_type: Literal["text", "chat"] = "text",
    fallback: str | list[dict] | None = None,
) -> ChatPromptTemplate | PromptTemplate:
    """Load a prompt from Langfuse.

    Args:
        name: The name of the prompt to load.
        label: The label of the prompt version to load. Defaults to "latest" in dev and "production"
        in other environments.
        prompt_type: The type of prompt to load, either "text" or "chat". Defaults to "text".
        fallback: Optional fallback prompt in case the prompt cannot be found. This can be a string
            or a list of dictionaries representing the messages for a chat prompt.

    Returns
    -------
        The loaded prompt as either a ChatPromptTemplate or a PromptTemplate.

    Raises
    ------
        PromptNotFoundError: If the prompt cannot be found or loaded.
    """
    try:
        langfuse_prmpt = await get_client().get_prompt(
            name=name,
            type=prompt_type,
            label=label,
            cache_ttl_seconds=config.PROMPT_CACHE_TTL,
            fallback=fallback,
        )
    except Exception as e:
        logger.error(f"Error getting prompt {name}, type = {prompt_type} from langfuse client")
        raise PromptNotFoundError(message=f"Prompt {name}, type = {prompt_type} not found") from e
    metadata = {
        "langfuse_prompt": langfuse_prmpt,
        "provider": str(langfuse_prmpt.config["provider"])
        if "provider" in langfuse_prmpt.config
        else None,
        "model": str(langfuse_prmpt.config["model"]) if "model" in langfuse_prmpt.config else None,
        "temperature": float(langfuse_prmpt.config["temperature"])
        if "temperature" in langfuse_prmpt.config
        else None,
        "top_p": float(langfuse_prmpt.config["top_p"])
        if "top_p" in langfuse_prmpt.config
        else None,
        "top_k": int(langfuse_prmpt.config["top_k"]) if "top_k" in langfuse_prmpt.config else None,
    }
    if prompt_type == "chat":
        prompt = ChatPromptTemplate.from_messages(
            langfuse_prmpt.get_langchain_prompt(), metadata=metadata
        )
    else:
        prompt = PromptTemplate.from_template(
            langfuse_prmpt.get_langchain_prompt(), metadata=metadata
        )
    return prompt


async def prefetch_at_startup(prompts: list[dict]) -> None:
    """Prefetch prompts at startup. Provide a list of prompts with their parameters."""
    for prompt in prompts:
        await load_prompt(**prompt)
