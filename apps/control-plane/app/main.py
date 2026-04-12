from fastapi import FastAPI
from app.core import settings
from app.api.v1.router import api_router
from app.db.session import init_db

# IMPORTANT: import models so SQLAlchemy knows about them
from app.models.service import Service
from app.models.job import Job


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0"
    )

    init_db()

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/")
    def root():
        return {
            "message": "Internal Developer Platform Control Plane",
            "version": "0.1.0"
        }

    return app


app = create_app()