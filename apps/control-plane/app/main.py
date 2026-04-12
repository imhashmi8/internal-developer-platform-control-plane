import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from app.core import settings
from app.api.v1.router import api_router
from app.db.session import init_db

# IMPORTANT: import models so SQLAlchemy knows about them
from app.models.service import Service
from app.models.job import Job

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_ready = False

    try:
        init_db()
        app.state.database_ready = True
    except SQLAlchemyError as exc:
        logger.warning(
            "Database initialization failed for %s: %s",
            settings.database_url,
            exc,
        )
        if settings.db_required:
            raise

    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/")
    def root():
        return {
            "message": "Internal Developer Platform Control Plane",
            "version": "0.1.0"
        }

    return app


app = create_app()
