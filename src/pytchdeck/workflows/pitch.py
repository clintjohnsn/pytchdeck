import json
import os

from jinja2 import Environment, FileSystemLoader
from llama_index.core.ingestion import IngestionPipeline
from rich import print as rprint

from pytchdeck.workflows.ingestion import ingest

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


class PitchWorkflow:

    def pitch(
        self, problem_file: str, deck_id: str, curr_path: str, source: str | None = None
    ) -> None:
        problem_context: dict = ingest("problem")(curr_path, problem_file)
        slides = [
            {"title": "Introduction", "content": "This is an AI-generated presentation."},
            {"title": "Data", "content": "Here we explore the dataset."},
            {"title": "Conclusion", "content": "The end."},
        ]
        data = {
            "title": "Your Pitch",
            "slides": slides,
        }
        self.process_template(
            template_file="basic_template.html",
            curr_path=curr_path,
            deck_id=deck_id,
            slides_data=data,
        )


    def process_template(self, template_file: str, curr_path: str, deck_id: str, slides_data: dict) -> str:
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(template_file)
        html_content = template.render(title=slides_data["title"], slides=slides_data["slides"])
        output_path = os.path.join(curr_path, f"{deck_id}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        rprint(f"[bold green] Done! [/bold green] Slide Deck saved to '{output_path}'")
        return output_path