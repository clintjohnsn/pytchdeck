"""pytchdeck CLI."""

import os
import uuid

import typer
from rich import print as rprint

from pytchdeck.workflows.pitch import PitchWorkflow

app = typer.Typer()

@app.command()
def config(GOOGLE_API_KEY: str) -> None:
    """Configure API keys"""
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    # TODO save keys to config file for laters


@app.command()
def pitch(problem_file: str, source: str, deck_name: str | None = None, pdf: bool = False) -> None:
    """Create a new deck."""
    deck_id = "deck_" + uuid.uuid4().hex[:8] if deck_name is None else deck_name

    if not os.path.exists(problem_file):
        raise FileNotFoundError(f"Problem file '{problem_file}' not found")
    
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source file '{source}' not found")

    curr_path = os.getcwd()

    rprint(f"[bold green] Initiating[/bold green] deck creation pipeline. Deck '#{deck_id}' for '{problem_file}' from source(s) in '{source}'")
    workflow = PitchWorkflow()
    workflow.pitch(problem_file=problem_file, source=source, curr_path=curr_path, deck_id=deck_id)
