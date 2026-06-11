from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv("../../.env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../../apps/control-plane/control-plane.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
