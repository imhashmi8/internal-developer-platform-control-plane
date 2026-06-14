import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from dotenv import load_dotenv

    load_dotenv("../../.env")
except ImportError:
    # python-dotenv is a convenience for local runs; env vars may also be
    # supplied directly (e.g. via `uv run --env-file` or the process env).
    pass

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../../apps/control-plane/control-plane.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
