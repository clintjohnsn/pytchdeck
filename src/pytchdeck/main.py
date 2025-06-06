"""pytchdeck REST API."""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import ell
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pytchdeck.config.settings import settings
from pytchdeck.routes import api

config = settings()
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

def setup_directories():
    """Create required directories if they don't exist."""
    data_dir = config.DATA_DIR
    source_dir = config.SOURCE_DIR
    data_dir.mkdir(exist_ok=True)
    source_dir.mkdir(exist_ok=True)
    logger.info("Setup directories: %s, %s", str(data_dir), str(source_dir))

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Handle FastAPI startup and shutdown events."""
    verbose = config.ENV == "dev"
    ell.init(store="./.logdir", autocommit=True, verbose=verbose)
    # Setup required directories
    setup_directories()
    logger.info("Started FastAPI application")
    yield
    logger.info("Shutting down FastAPI application")


app = FastAPI(
    lifespan=lifespan,
    title=config.PROJECT_NAME,
    description="API for Pytchdeck",
    version=config.VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    **config.cors_config,
)

app.include_router(api.router)
