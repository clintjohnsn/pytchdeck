"""Pitch Deck Creation Workflow."""

import logging
from pathlib import Path

# Standard library
# Third-party
try:
    from importlib import resources  # Python 3.9+
except ImportError:  # pragma: no cover - fallback for older Python
    import importlib_resources as resources  # type: ignore


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

# ---------------------------------------------------------------------------
# Load template helpers
# ---------------------------------------------------------------------------
TEMPLATES_PACKAGE = "pytchdeck.templates"
LLMS_TXT = resources.files(TEMPLATES_PACKAGE).joinpath("revealjs", "llms.txt").read_text(encoding="utf-8")
HTML_TEMPLATE = resources.files(TEMPLATES_PACKAGE).joinpath("basic_template.html").read_text(encoding="utf-8")



async def run(req: PitchRequest, config: dict, candidate_context: str) -> PitchOutput:
    """Create a pitch deck for a given job description."""
    state = State(
        id=config["configurable"]["thread_id"],
        jd=req.job_description,
        jd_link=req.job_description_link.unicode_string() if req.job_description_link else None,
        candidate_context=candidate_context,
        host=config["configurable"].get("host", "http://localhost:3000"),
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
    fit_assessment: str = await assess_fit(jd=jd, candidate_context=candidate_context)
    pitch_content: str = await write_pitch(jd=jd, candidate_context=candidate_context, fit_assessment=fit_assessment)
    deck_content: str = await generate_deck(pitch_content)
    # Save generated HTML to file
    output_path = settings().GENERATED_DIR / f"pitch_{state.id}.html"
    Path(output_path).write_text(deck_content, encoding="utf-8")

    return PitchGenerationResult(
        link=f"{state.host}/pitch/pitch_{state.id}.html",
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
@ell.simple(model="gpt-4o-mini", temperature=0.4, client=llm())
def assess_fit(jd: str, candidate_context: str) -> str:
    """
    Given the following job description and information about a candidate,
    assess the candidate's fit for the role.
    Highlight what makes the candidate a good fit for the role, and what makes them not a good fit.
    """  # System prompt
    logger.info("Assessing candidate fit")
    return f"""
    \n Job Description: \n {jd} \n\n Candidate Context: \n {candidate_context}
    """  # User prompt

@task()
@ell.simple(model="gpt-4o-mini", temperature=0.6, client=llm())
def write_pitch(jd: str, candidate_context: str, fit_assessment: str) -> str:
    """
    Make a Pitch deck on behalf of the candidate.
    The deck should be concise, engaging, and tailored to the job description.
    Make upto 7 slides max.
    You must be creative with the content.
    The writing style should be high energy, direct, straight shooting. 
    You need to sell the recruiter on why the candidate is the best fit for the role.
    Feel free to use emojis, exclamation marks, and other elements to make the deck more engaging.
    For the areas where the candidate is not a good fit, mention transferable skills or possible potential, and invite them to contact you for further discussion.
    """
    logger.info("Making deck content")
    return f"\n **Job Description:** \n {jd}\n\n **Candidate Context:** \n {candidate_context}\n\n **Fit Assessment:** \n {fit_assessment}"


@task()
@ell.simple(model="gpt-4o-mini", temperature=0.3, client=llm())
def generate_deck(pitch_content: str) -> str:
    """Generate a pitch deck from the given content."""
    logger.info("Generating deck")

    return [
        ell.system(f"""
            Generate a reveal.js presentation from the given deck content.
            Make it visually appealing, with a clear structure and flow.
            Add animations, transitions, and other elements to make the deck more engaging.
            Use scroll view to make the deck more interactive.
            Remember to adjust the font size of the content to fit the slide.
            Use different backgrounds, colors, and themes to make the deck more engaging.
            Use transitions and auto-animate between slides to make the deck more engaging.

            Return only the HTML content of the presentation.
            --------------------------------
            Some documentation for Reveal.js:
            {LLMS_TXT}

            Template for the html. Use the cdn links for reveal.js and theme.
            {HTML_TEMPLATE}
            --------------------------------
            """),
        ell.user(f"Content: {pitch_content}"),
    ]
