"""pytchdeck REST API."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import pytchdeck.workflows.pitch as workflow
from pytchdeck.models.dto import PitchOutput

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Handle FastAPI startup and shutdown events."""
    logger.info("Started FastAPI application")
    yield
    logger.info("Shutting down FastAPI application")


app = FastAPI(lifespan=lifespan, title="Pytchdeck API", description="API for Pytchdeck", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["Authorization"],
    allow_credentials=True,
)

@app.get("/pitch", response_model=PitchOutput)
async def pitch(job_description: str) -> PitchOutput:
    """Create a pitch deck for a given job description."""
    logger.info(f"Pitch request received for job description: {job_description}")
    return await workflow.run(job_description)

