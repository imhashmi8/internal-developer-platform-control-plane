from pydantic import BaseModel


class ServiceCreate(BaseModel):
    service_name: str
    team: str
    environment: str


class ServiceResponse(BaseModel):
    id: int
    service_name: str
    team: str
    environment: str
    lifecycle_state: str

    class Config:
        from_attributes = True