from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core import settings
from app.db.base import Base

engine_kwargs = {"echo": settings.db_echo}

if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
