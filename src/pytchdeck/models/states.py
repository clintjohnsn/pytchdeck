"""State Models."""

from pydantic import BaseModel, Field
from typing import Literal

class State(BaseModel):
    """Workflow state."""

    id: str = Field(..., description="Pitch generation ID")
    host: str = Field(..., description="Host")
    jd: str | None = Field(None, description="Job description")
    jd_link: str | None = Field(None, description="Job description link")
    candidate_context: str = Field(..., description="Candidate context")

class IsValidJD(BaseModel):
    is_valid: bool = Field(..., description="Is the job description valid?")
    reason: Literal['BrokenLink','NoContent','NotAJD','NotRelevant','ValidJD'] = Field(..., description="Details about the job description validation")


class PitchGenerationResult(BaseModel):
    """Pitch generation result."""

    link: str | None = Field(None, description="Link to the generated pitch deck")
    title: str | None = Field(None, description="Title of the generated pitch deck")
    message: str | None = Field(None, description="Message accompanying the generated pitch deck")

