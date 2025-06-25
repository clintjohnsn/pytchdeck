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
from pytchdeck.models.states import IsValidJD, PitchGenerationResult, State
from pytchdeck.workflows.nodes.guardrails import jd_guardrails
from pytchdeck.workflows.nodes.readers import fetch_content

logger = logging.getLogger(__name__)
config = settings()

LLMS_TXT = (
    resources.files("pytchdeck.templates")
    .joinpath("revealjs", "llms.txt")
    .read_text(encoding="utf-8")
)


async def run(req: PitchRequest, config: dict, candidate_context: str) -> PitchOutput:
    """Create a pitch deck for a given job description."""
    state = State(
        id=config["configurable"]["thread_id"],
        jd=req.job_description,
        jd_link=req.job_description_link.unicode_string() if req.job_description_link else None,
        candidate_context=candidate_context,
        host=config["configurable"].get("host", ""),
    )
    result: PitchGenerationResult = await pitch_workflow.ainvoke(state, config)
    logger.info(f"Pitch workflow result: {result}")
    return PitchOutput(link=result.link, title=result.title)


@entrypoint(checkpointer=MemorySaver())
async def pitch_workflow(state: State) -> PitchGenerationResult:
    """Pitch Generation Workflow."""
    jd: str = state.jd if state.jd else await fetch_content(state.jd_link)
    guardrails: IsValidJD = await jd_guardrails(jd)
    if not guardrails.is_valid:
        raise InvalidJobDescriptionError(f"{guardrails.reason or 'No reason provided'}")
    fit_assessment: str = await assess_fit(jd=jd, candidate_context=state.candidate_context)
    deck_content: str = await generate_deck(context=f"{fit_assessment}\n\n{state.candidate_context}")
    output_path = settings().GENERATED_DIR / f"pitch_{state.id}.html"  # Save generated HTML to file
    Path(output_path).write_text(deck_content, encoding="utf-8")
    return PitchGenerationResult(
        link=f"{state.host}/pitch/pitch_{state.id}.html",
        title="Pitch Deck",
    )

@task()
@ell.simple(model="gpt-4.1-mini", temperature=0.4, client=llm())
def assess_fit(jd: str, candidate_context: str) -> str:
    """
    Given the following job description and information about a candidate,
    assess the candidate's fit for the role.
    Highlight what makes the candidate a good fit for the role, and what makes them not a good fit.
    Pay attention to not only the requirements, but also the domain, culture, and other aspects of the company and what they do.
    Return a concise JSON object
    """  # System prompt
    logger.info("Assessing candidate fit")
    return f"""
    \n Job Description: \n {jd} \n\n Candidate Context: \n {candidate_context}
    """  # User prompt


@task()
@ell.simple(model="gpt-4.1-nano", temperature=0.4, client=llm())
def company_context(jd: str) -> str:
    """
    
    """  # System prompt
    logger.info("Assessing candidate fit")
    return f"""
    \n Job Description: \n {jd}
    """  # User prompt

@task()
@ell.simple(model="gpt-4.1", temperature=0.7, client=llm())
def generate_deck(context: str) -> str:
    """Generate a pitch deck from the given content."""
    logger.info("Generating deck")

    return [
        ell.system(f"""
            <documentation>
                Refer to the following documentation on using revealjs. Make sure to use standalone mode for your output.
                {LLMS_TXT}
            </documentation>
            """),
        ell.user(f"""
            <task>
                Generate a Pitch deck on behalf of the candidate, as a stand alone reveal.js presentation.
                You need to sell the recruiter on why the candidate is the best fit for the role.
                Feel free to use emojis, exclamation marks, and other elements to make the deck more engaging.
                Disregard any areas of the job description that are not relevant to the candidate's profile.
                The deck should be structured in a way that highlights the candidate's strengths and how they align.
                The deck should be concise, engaging, and tailored to the job description.
                Make it visually appealing, with a clear structure and flow.
                You must be creative with the content.
                Add animations, transitions, and other elements to make the deck more engaging.
                Use scroll view to make the deck more interactive.
                Remember to adjust the font size of the content to fit the slide.
                Pick a a cool color scheme and font for the deck and stick with it. Make sure that the colors make the text readable.
                Use transitions and auto-animate between slides to make the deck more engaging.
                Return only the HTML content of the presentation.
                You can use the candidate profile picture and the company logo in the deck.
                You can use https://cdn.jsdelivr.net/gh/devicons/devicon/icons to include icons in the deck.
                IT IS CRUICIAL THAT YOU KEEP THE FONT SIZE SMALL ENOUGH TO FIT THE CONTENT ON THE SLIDE.
                Think carefully about the structure of the deck, and how to best present the information.
                Think about the design and how to make the deck visually appealing.
            </task>
            <content>
            {context}
            </content>
        """),
    ]
