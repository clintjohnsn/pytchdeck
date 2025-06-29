"""Guardrails for validating job descriptions using a language model."""

import logging

import ell
from langgraph.func import task
from pydantic import ValidationError

from pytchdeck.clients.llm import llm
from pytchdeck.config.settings import settings
from pytchdeck.models.exceptions import StructureParsingError
from pytchdeck.models.states import IsValidJD

logger = logging.getLogger(__name__)
config = settings()


@task()
def jd_guardrails(jd: str) -> IsValidJD:
    """GUARDRAIL: Validate job description for target roles."""
    logger.info("Running job description guardrails")
    result = validate_jd(jd)
    try:
        parsed = IsValidJD.model_validate_json(result)
        return parsed
    except ValidationError as e:
        raise StructureParsingError("Error parsing job description guardrail response") from e


@ell.simple(model="gpt-4.1-nano", temperature=0.0, client=llm())
def validate_jd(jd: str) -> str:
    """Use a language model to check if the job description is valid."""
    logger.info("Validating job description")
    return [
        ell.system(f"""
            Determine if the content contains a valid job description.
            The job description should be for a {config.TARGET_ROLES} or related position.
            It needs to include title, role, and skills requirements.
            Return whether the job description is valid or not, and provide a reason.
            The response should be a JSON object with the following fields:
            is_valid: True/False indicating if the job description is valid.
            reason: string providing the reason for the validation result. Reason can be one of the following:
            - NO_CONTENT: No content found at the link,
            - IRRELEVANT: Content is not a job description,
            - NO_MATCH: No match found for the target roles,
            - VALID_JD: Valid job description post
            You must absolutely respond in this format with no exceptions.

           {IsValidJD.model_json_schema()}
            """),
        ell.user(f"\n Job description: <Job Description> \n\n{jd} \n\n </Job Description>"),
    ]
