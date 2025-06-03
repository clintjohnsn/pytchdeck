from pytchdeck.workflows.components.readers import local_reader
from pydantic import BaseModel
from typing import Literal

def ingest(type: Literal["problem", "source"]) -> Context:
    if type == "problem":
        return ingest_problem
    elif type == "source":
        return ingest_source
    else:
        raise ValueError(f"Invalid type: {type}")

def ingest_problem(path: str, file: str) -> Context:
    if not path:
        raise ValueError("Input path cannot be empty.")
    reader = local_reader(path)
    docs = reader(file)
    return Context(text="\n".join([doc.text for doc in docs]))

def ingest_source(path: str, file: str) -> Context:
    if not path:
        raise ValueError("Input path cannot be empty.")
    reader = local_reader(path)
    docs = reader(file)
    return Context(text="\n".join([doc.text for doc in docs]))
