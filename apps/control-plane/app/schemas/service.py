from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    service_name: str
    team: str
    environment: str


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_name: str
    team: str
    environment: str
    lifecycle_state: str


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: str
    service_id: int | None = None
    operation_type: str
    state: str
    message: str | None = None
    artifact_path: str | None = None


class ServiceCreateResponse(BaseModel):
    service: ServiceResponse
    job: JobResponse
