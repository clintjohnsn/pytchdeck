"""State Models."""

from pydantic import BaseModel


class State(BaseModel):
    """Workflow state."""

    jd: str | None = None
    jd_link: str | None = None
    keywords: str | None = None

class PitchGenerationResult(BaseModel):
    """Pitch generation result.

    Attributes
    ----------
    link: str
        The URL to the generated pitch deck.
    title: str
        The title of the generated pitch deck.
    """

    link: str
    title: str
