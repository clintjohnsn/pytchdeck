"""Data Transfer Objects."""

from pydantic import BaseModel, Field, HttpUrl, field_validator

from pytchdeck.models.exceptions import InvalidUrlSchemeError


class PitchRequest(BaseModel):
    """Request model for pitch generation.

    Attributes
    ----------
    job_description: str | None
        Optional detailed job description used to generate the pitch deck.
    job_description_link: HttpUrl | None
        Optional URL to the full job description if available.
    """

    job_description: str | None = Field(
        None,
        min_length=20,
        description="Detailed job description to base the pitch deck on.",
        example="We are looking for a Senior Python Developer with 5+ years of experience...",
    )
    job_description_link: HttpUrl | None = Field(
        None,
        description="Optional URL to the full job description if available. Must be a valid HTTP or HTTPS URL.",
        example="https://example.com/jobs/senior-python-developer",
    )

    @field_validator("job_description_link")
    @classmethod
    def validate_url_scheme(cls, v):
        """Validate that the URL uses http or https scheme.

        Raises
        ------
        ValueError
            If the URL scheme is not http or https
        """
        if v is not None and v.scheme not in ("http", "https"):
            raise InvalidUrlSchemeError("URL must use http or https scheme")
        return v


class PitchOutput(BaseModel):
    """Pitch output."""

    link: str
    title: str
