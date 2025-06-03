"""Pitch workflow."""

import logging

from langgraph.checkpoint.memory import MemorySaver
from langgraph.func import entrypoint, task
from langgraph.types import interrupt

from pytchdeck.models.dto import PitchOutput

logger = logging.getLogger(__name__)


@task
async def write_essay(topic: str) -> str:
    """Write an essay about the given topic."""
    return f"An essay about topic: {topic}"


@entrypoint(checkpointer=MemorySaver())
async def pitch_workflow(topic: str) -> dict:
    """Pitch workflow."""
    essay = write_essay("cat").result()
    is_approved = interrupt(
        {
            "essay": essay,
            "action": "Please approve/reject the essay",
        }
    )
    return {
        "essay": essay,  # The essay that was generated
        "is_approved": is_approved,  # Response from HIL
    }


async def run(job_description: str) -> PitchOutput:
    """Create a pitch deck for a given job description."""
    config = {"configurable": {"thread_id": "some_thread_id"}}
    result = await pitch_workflow.ainvoke(job_description, config)
    logger.info(f"Pitch workflow result: {result}")
    return PitchOutput(link="https://www.google.com", title="Pitch Deck")
