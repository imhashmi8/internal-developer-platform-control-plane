from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base

DATABASE_URL = "postgresql://idp:idp@localhost:5432/idp"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)