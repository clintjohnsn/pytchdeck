"""Setup FastAPI application."""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import ell
from fastapi import FastAPI
from langfuse import get_client
from llama_index.core import Document

from pytchdeck.clients.llm import llm
from pytchdeck.config.settings import settings
from pytchdeck.models.exceptions import InitializationError
from pytchdeck.workflows.nodes.readers import read_files

config = settings()
langfuse = get_client()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Handle FastAPI startup and shutdown events."""
    # Startup Events
    logger.info("Starting FastAPI application")
    # initialize ell store for local prompt management
    ell.init(
        store="./.logdir",
        autocommit=False,
        verbose=config.ENV == "dev",
        default_client=llm(),
    )
    await setup_directories()  # Setup required directories
    await setup_candidate_context(app)  # Ingest candidate context
    logger.info("Started FastAPI application")
    yield
    # Shutdown events
    langfuse.shutdown()
    logger.info("Shut down complete")


async def setup_directories():
    """Create required directories if they don't exist."""
    dirs: list[Path] = [config.CANDIDATE_DIR, config.GENERATED_DIR]
    for d in dirs:
        if not d.exists():
            d.mkdir(parents=True)
            logger.info("Created required directories: %s", str(d))


async def setup_candidate_context(app: FastAPI):
    """Set up candidate context."""
    logger.info("Loading candidate context...")
    app.state.candidate_context = await ingest_candidate_context()
    logger.info("Successfully loaded candidate context into app state")


async def ingest_candidate_context() -> str:
    """Ingest candidate context."""
    path: Path = settings().CANDIDATE_DIR
    if not path.exists() or not os.listdir(path):
        raise InitializationError("Candidate directory not setup or empty.")
    docs: list[Document] = await read_files(path)
    return "\n".join([doc.text for doc in docs])
