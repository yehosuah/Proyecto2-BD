from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
def auth_health() -> dict[str, str]:
    return {"status": "ok", "domain": "auth"}

