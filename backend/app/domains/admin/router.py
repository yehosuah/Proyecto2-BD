from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
def admin_health() -> dict[str, str]:
    return {"status": "ok", "domain": "admin"}

