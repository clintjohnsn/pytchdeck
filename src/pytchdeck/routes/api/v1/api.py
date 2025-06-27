"""API endpoints for the Pytchdeck application."""

from fastapi import APIRouter, HTTPException, Request, status

import pytchdeck.workflows.pitch as workflow
from pytchdeck.dependencies.workflow import CandidateContext, WorkflowConfig
from pytchdeck.models.dto import PitchOutput, PitchRequest
from pytchdeck.models.exceptions import (
    InvalidJobDescriptionError,
    InvalidUrlSchemeError,
    NoContentError,
    StructureParsingError,
)

router = APIRouter(prefix="/api/v1", tags=["pitch"])


@router.post(
    "/generate",
    response_model=PitchOutput,
    summary="Generate a pitch deck",
    description="""
    Generate a pitch deck based on the provided job description.
    Job description can be provided as a string or a link to a job description.
    - **job_description (optional)**: A detailed job description to base the pitch deck on
    - **job_description_link (optional)**: A link to the job description
    """,
    response_description="The generated pitch deck details",
)
async def pitch(
    request: Request, body: PitchRequest, config: WorkflowConfig, context: CandidateContext
) -> PitchOutput:
    """Generate a pitch deck for a given job description."""
    if not body.job_description and not body.job_description_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of job_description or job_description_link must be provided",
        )
    try:
        return await workflow.run(req=body, config=config, candidate_context=context)
    except (
        InvalidJobDescriptionError,
        NoContentError,
        InvalidUrlSchemeError,
        StructureParsingError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An error occurred while generating the pitch deck",
        ) from e
