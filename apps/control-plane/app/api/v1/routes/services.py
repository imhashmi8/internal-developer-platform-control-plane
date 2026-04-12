import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.db.session import get_db
from app.models.job import Job
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[ServiceResponse])
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).order_by(Service.id.asc()).all()


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    service = Service(
        service_name=payload.service_name,
        team=payload.team,
        environment=payload.environment,
        lifecycle_state="PENDING",
    )

    job = Job(
        job_id=f"job-{uuid.uuid4()}",
        operation_type="CREATE_SERVICE",
        state="PENDING",
    )

    db.add(service)
    db.add(job)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        logger.warning("Failed to create service '%s': %s", payload.service_name, exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Service '{payload.service_name}' already exists",
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error while creating service '%s'", payload.service_name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist service",
        ) from exc

    db.refresh(service)
    db.refresh(job)

    celery_app.send_task("process_create_service_job", kwargs={"job_id": job.job_id})

    logger.info("Created service '%s', dispatched job '%s'", service.service_name, job.job_id)

    return service
