from pydantic import BaseModel

class PitchOutput(BaseModel):
    link: str
    title: str