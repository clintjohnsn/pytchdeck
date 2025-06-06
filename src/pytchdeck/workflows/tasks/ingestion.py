"""Ingestion tasks."""
import logging
import os
from pathlib import Path

from langgraph.func import task
from llama_index.core import Document

from pytchdeck.config.settings import settings
from pytchdeck.models.exceptions import InitializationError
from pytchdeck.workflows.tasks.readers import local_reader

logger = logging.getLogger(__name__)


async def ingest_source_context() -> str:
    """Ingest source context."""
    path: Path = settings().SOURCE_DIR
    if not path.exists() or not os.listdir(path):
        raise InitializationError("Source directory not setup or empty.")
    docs = await _read_files(path)
    return "\n".join([doc.text for doc in docs])

async def _read_files(path: Path) -> list[Document]:
    """Read files from a directory."""
    read = local_reader(path)
    docs = await read(os.listdir(path))
    return docs



@task()
async def fetch_content(url: str) -> str:
    """Fetch content from a URL."""
    logger.info(f"Fetching job description from url {url}")
    return url
