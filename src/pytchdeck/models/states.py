"""State Models."""

from typing import Literal

from pydantic import BaseModel, Field


class State(BaseModel):
    """Workflow state."""

    id: str = Field(..., description="Pitch generation ID")
    host: str = Field(..., description="Host")
    jd: str | None = Field(None, description="Job description")
    jd_link: str | None = Field(None, description="Job description link")
    candidate_context: str = Field(..., description="Candidate context")


class IsValidJD(BaseModel):
    """Job description validation result."""

    is_valid: bool = Field(description="Is this a valid job description post?")
    reason: Literal["NO_CONTENT", "IRRELEVANT", "NO_MATCH", "VALID_JD"] = Field(description="Reason for validation result")


class PitchGenerationResult(BaseModel):
    """Pitch generation result."""

    link: str | None = Field(None, description="Link to the generated pitch deck")
    title: str | None = Field(None, description="Title of the generated pitch deck")
    message: str | None = Field(None, description="Message accompanying the generated pitch deck")
