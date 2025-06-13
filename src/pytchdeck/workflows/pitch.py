"""Pitch Deck Creation Workflow."""

import logging

import ell
from langgraph.checkpoint.memory import MemorySaver
from langgraph.func import entrypoint, task

from pytchdeck.clients.llm import llm
from pytchdeck.config.settings import settings
from pytchdeck.models.dto import PitchOutput, PitchRequest
from pytchdeck.models.exceptions import InvalidJobDescriptionError
from pytchdeck.models.states import PitchGenerationResult, State
from pytchdeck.workflows.nodes.readers import fetch_content

logger = logging.getLogger(__name__)
config = settings()


async def run(req: PitchRequest, config: dict, candidate_context: str) -> PitchOutput:
    """Create a pitch deck for a given job description."""
    state = State(
        id=config["configurable"]["thread_id"],
        jd=req.job_description,
        jd_link=req.job_description_link.unicode_string() if req.job_description_link else None,
        candidate_context=candidate_context,
    )
    result: PitchGenerationResult = await pitch_workflow.ainvoke(state, config)
    logger.info(f"Pitch workflow result: {result}")
    return PitchOutput(link=result.link, title=result.title)


@entrypoint(checkpointer=MemorySaver())
async def pitch_workflow(state: State) -> PitchGenerationResult:
    """Pitch Generation Workflow."""
    jd: str = state.jd if state.jd else await fetch_content(state.jd_link)
    candidate_context: str = state.candidate_context
    is_valid = bool(await is_valid_jd(jd))
    if not is_valid:
        raise InvalidJobDescriptionError("That does not seem like a job description.")
    keywords: str = await extract_keywords(jd)
    fit_assessment: str = await assess_fit(jd=jd, candidate_context=candidate_context)
    pitch_content: str = await write_pitch(jd=jd, candidate_context=candidate_context, fit_assessment=fit_assessment)
    deck_content: str = await generate_deck(pitch_content)
    print(deck_content)
    return PitchGenerationResult(
        link=f"http://localhost:3000/pitch/pitch_{state.id}.html",
        title="Pitch Deck",
    )


@task()
@ell.simple(model="gpt-4o-mini", temperature=0.1, client=llm())
def is_valid_jd(jd: str) -> str:
    """Validate if the content is a job description for target roles."""
    logger.info("Validating job description")
    return [
        ell.system(f"""
            Determine if the content contains a valid job description.
            The job description should be for a {config.TARGET_ROLES} or related position.
            It needs to include title, role, and skills requirements.
            Output only True or False.
            """),
        ell.user(f"Content: {jd}"),
    ]
@task()
@ell.simple(model="gpt-4o-mini", temperature=0.2, client=llm())
def extract_keywords(jd: str) -> str:
    """
    Extract a list of relevant keywords from the job description provided.

    The keywords should be skills (technical or soft), core competencies,
    values, experience, and other relevant requirements of the job.
    """  # System prompt
    logger.info("Extracting keywords")
    return f"\n Job Description: \n {jd}"  # User prompt


@task()
@ell.simple(model="gpt-4o-mini", temperature=0.5, client=llm())
def assess_fit(jd: str, candidate_context: str) -> str:
    """
    Given the following job description and information about a candidate,
    assess and highlight the candidate's fit for the role.
    """  # System prompt
    logger.info("Assessing candidate fit")
    return f"""
    \n Job Description: \n {jd} \n\n Candidate Context: \n {candidate_context}
    """  # User prompt


@task()
@ell.simple(model="gpt-4o-mini", client=llm())
def write_pitch(jd: str, candidate_context: str, fit_assessment: str) -> str:
    """
    Write a pitch based on the job description and candidate context on behalf of the candidate.
    The pitch should be a short, concise, and engaging pitch that highlights the candidate's relevant experience and skills.
    Keep the company context and values in mind.

    When the candidate is a good fit, the pitch should be positive and enthusiastic.
    When the candidate is not a good fit, the pitch should be neutral and factual, talk about any transferable skills, mentioning any potential concerns.
    If the candidate is not a good fit, mention transferable skills or possible potential, but be honest. Keep the pitch concise, and avoid unnecessary details.
    """
    logger.info("Writing pitch content")
    return f"\n **Job Description:** \n {jd}\n\n **Candidate Context:** \n {candidate_context}\n\n **Fit Assessment:** \n {fit_assessment}"


@task()
@ell.simple(model="gpt-4o-mini", client=llm())
def generate_deck(content: str) -> str:
    """
    Make a deck based on the content provided.
    Make 10-15 slides, each with a title and content.
    """
    logger.info("Making deck content")
    return f"\n **Content:** \n {content}"
