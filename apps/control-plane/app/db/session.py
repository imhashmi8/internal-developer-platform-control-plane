from sqlalchemy import create_engine, inspect, text
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
    _ensure_job_columns()


def _ensure_job_columns():
    inspector = inspect(engine)

    if "jobs" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("jobs")}
    column_definitions = {
        "service_id": "INTEGER",
        "message": "VARCHAR(1000)",
        "artifact_path": "VARCHAR(1000)",
    }

    with engine.begin() as connection:
        for column_name, column_type in column_definitions.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE jobs ADD COLUMN {column_name} {column_type}"))
