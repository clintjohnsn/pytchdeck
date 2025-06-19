"""Workflow middleware."""

import hashlib
import json
import uuid
from typing import Annotated

from fastapi import Depends, Request
from pydantic import BaseModel

from pytchdeck.clients.langfuse import trace_callback


async def hash_object(obj: BaseModel) -> str:
    """Generate a deterministic ID from the entire pydantic object using MD5."""
    # Convert the request to a dictionary sorted by keys for consistent hashing
    json_str = json.dumps(obj.model_dump(mode="json"), sort_keys=True)
    return hashlib.md5(json_str.encode()).hexdigest()

async def thread_id(request: Request) -> str:
    """Get the thread id from the request."""
    # First try to get from headers
    if thread := request.headers.get("X-Thread-Id"):
        return thread
    # If no header, try to get from request body
    try:
        body = await request.json()
        if body:
            return await hash_object(body) # TODO: buggy, investigate
    except Exception:
        pass
    # If all else fails, generate a random UUID
    return str(uuid.uuid4())

async def current_host(request: Request) -> str:
    """Return the scheme://host of the incoming request (no trailing slash)."""
    return str(request.base_url).rstrip("/")

async def workflow_config(thread: str = Depends(thread_id), host: str = Depends(current_host)) -> dict:
    """Get the workflow config."""
    return {
        "configurable": {
            "thread_id": thread,  # Unique identifier to track workflow execution
            "host": host,
        },
        "callbacks": [trace_callback()],
    }

WorkflowConfig = Annotated[dict, Depends(workflow_config)]

async def candidate_context(request: Request) -> str:
    """Get the candidate context from FastAPI state."""
    return request.app.state.candidate_context

CandidateContext = Annotated[str, Depends(candidate_context)]
