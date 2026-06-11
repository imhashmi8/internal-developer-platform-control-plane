from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(255), unique=True)
    service_id: Mapped[int | None] = mapped_column(default=None)
    operation_type: Mapped[str] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(50), default="PENDING")
    message: Mapped[str | None] = mapped_column(String(1000), default=None)
    artifact_path: Mapped[str | None] = mapped_column(String(1000), default=None)
