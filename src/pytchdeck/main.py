"""pytchdeck REST API."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pytchdeck.config.settings import settings
from pytchdeck.dependencies.lifespan import lifespan
from pytchdeck.routes.api.v1 import api

config = settings()
logging.basicConfig(level=config.LOG_LEVEL)


app = FastAPI(
    lifespan=lifespan, title=config.PROJECT_NAME, description=config.API_DESCRIPTION, version=config.VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    **config.cors_config,
)

# Register routers
app.include_router(api.router)
