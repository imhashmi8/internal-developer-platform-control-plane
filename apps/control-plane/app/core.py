from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "internal-developer-platform-control-plane"
    environment: str = "local"
    api_prefix: str = "/api/v1"


settings = Settings()