"""Workflow middleware."""

import functools
import uuid
from typing import Annotated, Any

from fastapi import Depends, Request
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from pytchdeck.clients.langfuse import load_prompt, trace_callback
from pytchdeck.clients.llm import llm


async def thread_id(request: Request) -> str:
    """Get the thread id from the request."""
    # First try to get from headers
    if thread := request.headers.get("X-Thread-Id"):
        return thread
    return str(uuid.uuid4())


async def current_host(request: Request) -> str:
    """Return the scheme://host of the incoming request (no trailing slash)."""
    return str(request.base_url).rstrip("/")


async def workflow_config(
    thread: str = Depends(thread_id), host: str = Depends(current_host)
) -> dict:
    """Get the workflow config."""
    return {
        "configurable": {
            "thread_id": thread,  # Unique identifier to track workflow execution
            "host": host,
        },
        "callbacks": [trace_callback()],
        "metadata": {
            "langfuse_session_id": thread,
        },
    }


WorkflowConfig = Annotated[dict, Depends(workflow_config)]


async def candidate_context(request: Request) -> str:
    """Get the candidate context from FastAPI state."""
    return request.app.state.candidate_context


CandidateContext = Annotated[str, Depends(candidate_context)]


def lmp(
    name: str,
    label: str | None = None,
    prompt_type: str = "chat",
    fallback: str | list[str] | None = None,
    response_model: Any | None = None,
    **fallback_model_kwargs: dict[str, Any]
) -> PromptTemplate | ChatPromptTemplate:
    """
    Call an LLM with a prompt template. Models a LMP (Language Model Program).
    An LMP treats prompts as functions, encapsulating the prompt template,
    the LLM configuration (like model name and temperature), and the function logic.

    This decorator loads the prompt template from Langfuse, extracts the LLM config,
    and calls the LLM.
    Wrap a function to  invoke the LLM with the prompt template AFTER executing the function logic.
    The function could either return a new set of input parameters (after some transformation)
    or return None (which maps to no transformations).

    Fallbacks: Specify fallback prompts to use if the given prompt template is not found.
    You can also specify fallback model config to use if the primary model config is not found.

    Args:
        name (str): Name of the prompt template to load from Langfuse.
        label (optional, str): Label for the prompt version,
                defaults to "latest" in development environment
                and "production" in production environment.
        prompt_type (str): Type of the prompt, either "chat" or "text", defaults to "chat".
        fallback (str | list[str] | None): Fallback prompt (chat or text) if the template not found.
        response_model (Optional, Any): Provide a model for LLM calls with structured output.
        **fallback_model_kwargs (dict[str, Any]): Additional model parameters to use as fallback model config.
    """

    def decorator(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            """Wrapper function to call the LLM with the prompt template."""
            new_params : dict[str, Any] | None  = await func(*args, **kwargs)
            prompt = await load_prompt(
                name=name,
                label=label,
                prompt_type=prompt_type,
                fallback=fallback,
            )
            # Build LLM config from prompt metadata with kwargs fallback
            llm_config = {}
            config_keys = ["provider", "model", "temperature", "top_p", "top_k"]
            for key in config_keys:
                if prompt.metadata and key in prompt.metadata and prompt.metadata[key] is not None:
                    llm_config[key] = prompt.metadata[key]
                elif key in fallback_model_kwargs and fallback_model_kwargs[key] is not None:
                    llm_config[key] = fallback_model_kwargs[key]
            model = llm(**llm_config)
            if response_model:
                model = model.with_structured_output(response_model)
            chain = prompt | model
            payload = new_params if new_params else kwargs
            response = await chain.ainvoke(
                payload
            )
            response = response if response_model else response.content
            return response

        return wrapper

    return decorator
