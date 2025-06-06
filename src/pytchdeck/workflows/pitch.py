"""Pitch Deck Creation Workflow."""

import logging
from functools import lru_cache
from uuid import uuid4

import ell
from langgraph.checkpoint.memory import MemorySaver
from langgraph.func import entrypoint, task
from openai import OpenAI

from pytchdeck.config.settings import settings
from pytchdeck.models.dto import PitchOutput, PitchRequest
from pytchdeck.models.exceptions import InvalidJobDescriptionError
from pytchdeck.models.states import PitchGenerationResult, State
from pytchdeck.utils.utils import hash_object
from pytchdeck.workflows.tasks.ingestion import fetch_content, ingest_source_context

logger = logging.getLogger(__name__)

@lru_cache
def llm():
    """Get the OpenAI LLM client."""
    return OpenAI(api_key=settings().OPENAI_API_KEY)

async def run(request: PitchRequest) -> PitchOutput:
    """Create a pitch deck for a given job description."""
    state = State(jd=request.job_description, jd_link=request.job_description_link)
    thread_id = hash_object(state)
    config = {
        "configurable": {
            "thread_id": thread_id  # Unique identifier to track workflow execution
        }
    }
    result: PitchGenerationResult = await pitch_workflow.ainvoke(state, config)
    logger.info(f"Pitch workflow result: {result}")
    return PitchOutput(link=result.link, title=result.title)


@entrypoint(checkpointer=MemorySaver())
async def pitch_workflow(state: State) -> PitchGenerationResult:
    """Pitch Generation Workflow."""
    link = state.jd_link
    jd: str = state.jd if state.jd else await fetch_content(link)
    is_valid = bool(await is_valid_jd(jd))
    if not is_valid:
        raise InvalidJobDescriptionError("That does not seem like a job description.")
    state.keywords = await extract_keywords(jd)
    source_context: str = await ingest_source_context()
    logger.info(f"Source context: {source_context}")
    pitch_content: str = await write_pitch(jd=jd, source_context=source_context)
    deck_content: str = await generate_deck(pitch_content)
    return PitchGenerationResult(
        link=f"http://localhost:3000/pitch/pitch_{uuid4()}.html",
        title="Pitch Deck",
    )

@task()
@ell.simple(model="gpt-4o-mini", client=llm())
def is_valid_jd(input: str) -> str:
    """
    Determine if the content contains a valid job description.

    The job description should be for a software engineer, AI engineer, engineering manager, or related position.
    It needs to include title, role, and skills requirements.
    Output only True or False.
    """
    logger.info("Validating job description")
    return f"\n Content: \n {input}"

@task()
@ell.simple(model="gpt-4o-mini", client=llm())
def extract_keywords(jd: str) -> str:
    """
    Extract a list of relevant keywords from the job description provided.

    The keywords should be skills, values, experience, and other relevant requirements of the job.
    """
    logger.info("Extracting keywords")
    return f"\n Job Description: \n {jd}"

@task()
@ell.simple(model="gpt-4o-mini", client=llm())
def write_pitch(jd: str, source_context: str) -> str:
    """
    Write a pitch based on the job description and candidate context.

    The pitch should be a short, concise, and engaging pitch that highlights the candidate's relevant experience and skills.
    Keep the company context and values in mind.
    """
    logger.info("Writing pitch content")
    return f"\n **Job Description:** \n {jd}\n\n **Candidate Context:** \n {source_context}"

@task()
@ell.simple(model="gpt-4o-mini", client=llm())
def generate_deck(content:str) -> str:
    """
    Make a deck based on the content provided.
    """
    logger.info("Making deck")
    return f"\n **Content:** \n {content}"