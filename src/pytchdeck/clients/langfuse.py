"""Langfuse Client."""

from functools import lru_cache

from langfuse.langchain import CallbackHandler


@lru_cache
def trace_callback() -> CallbackHandler:
    """Get the Langfuse callback handler."""
    return CallbackHandler()
