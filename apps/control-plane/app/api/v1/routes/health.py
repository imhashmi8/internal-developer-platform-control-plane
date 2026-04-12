from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
def health_check(request: Request):
    database_ready = getattr(request.app.state, "database_ready", False)

    return {
        "status": "healthy" if database_ready else "degraded",
        "service": "idp-control-plane",
        "component": "api",
        "database": "ready" if database_ready else "unavailable",
    }
