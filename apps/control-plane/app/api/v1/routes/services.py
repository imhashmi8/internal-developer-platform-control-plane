from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceResponse

router = APIRouter()


@router.post("/", response_model=ServiceResponse)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    service = Service(
        service_name=payload.service_name,
        team=payload.team,
        environment=payload.environment,
        lifecycle_state="PENDING"
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return service